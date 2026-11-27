"""Bounded supervisor policy over the fixture DAG; no real verification."""
from __future__ import annotations
from dataclasses import asdict,dataclass
from enum import Enum
from types import SimpleNamespace
from .contracts import (SupervisorAction,SupervisorDecision,AbstentionRecord,ResultStatus,
    FailureSignature,Derivation,DiscoveryQuery,DiscoveryResult,Archetype)
from .dag_engine import StageStatus,provider_ladder
from .durability import DurableExecution,discovery_from
from .circuit_breaker import CircuitBreaker
from .dossier_writer import DossierError
from .evidence_store import digest,canonical

class SupervisorState(str,Enum):
    PLANNING="PLANNING"
    EXECUTING="EXECUTING"
    REPAIRING="REPAIRING"
    DISCOVERING="DISCOVERING"
    VERIFYING="VERIFYING"
    CLOSED="CLOSED"
    ABSTAINED="ABSTAINED"
    ESCALATED="ESCALATED"

@dataclass(frozen=True)
class SupervisorResult:
    state:SupervisorState
    transitions:tuple[SupervisorState,...]
    decisions:tuple[SupervisorDecision,...]
    abstentions:tuple[AbstentionRecord,...]
    verification_method:str | None

class Supervisor:
    def __init__(self,engine,store,dossier,learning,*,durable=None,retries_per_provider=1):
        if type(retries_per_provider) is not int or not 0<=retries_per_provider<=3:raise ValueError("Bounded retries required")
        if dossier.path==learning.path:raise ValueError("Separate partitions required")
        self.engine=engine;self.store=store;self.dossier=dossier;self.learning=learning
        self.durable=durable or engine.durable or DurableExecution(store)
        self.engine.durable=self.durable
        self.retries=retries_per_provider

    def run(self,fingerprint,*,input_hash,execution_id,timestamp,allowed_providers,objectives):
        objectives=dict(objectives)
        if any(s["id"]=="verify" and s["kind"]=="analysis" for s in self.engine.graphs[fingerprint.archetype.value]):
            objectives.setdefault("verify",{"required_to_proceed":"Successful synthetic verification stage and independent Phase 5 verification","blocks_downstream":True})
        if not objectives:raise ValueError("At least one scoped objective required")
        self.durable.emit(execution_id+":supervisor","PLAN",{"fingerprint":asdict(fingerprint),"input_hash":input_hash,
            "objectives":objectives,"timestamp":timestamp,"allowed":sorted(allowed_providers),"retries":self.retries})
        terminal=self.durable.get(execution_id+":supervisor","TERMINAL")
        if terminal is not None:
            return supervisor_result_from(terminal)
        states=[];decisions=[];abstentions=[];rounds=[];verification=None
        graph={s["id"]:s for s in self.engine.graphs[fingerprint.archetype.value] if s["kind"]=="analysis"}
        def transition(state,action,reason,target="",refs=()):
            decision=SupervisorDecision(action,reason,target,tuple(refs))
            step=execution_id+":transition:"+str(len(states))
            payload={"state":state.value,"decision":asdict(decision)}
            self.durable.emit(step,"TRANSITION",payload)
            self.learning.write(step,{"kind":"transition","data":payload})
            self.durable.hook("after_supervisor_transition")
            states.append(state);decisions.append(decision)
        def run_dag(suffix,seed=None,override=None,retry_stage=None):
            r=self.engine.run(fingerprint,input_hash=input_hash,execution_id=execution_id+":"+suffix,
                timestamp=timestamp,allowed_providers=allowed_providers,unresolved={},seed_passes=seed or {},stage_overrides=override or {},retry_stage=retry_stage)
            rounds.append(r);return r
        def available_observations(ids):
            return bool(ids) and all((e:=self.store.get(i)) is not None and e.status is ResultStatus.PASS
                and e.derivation in {Derivation.OBSERVED,Derivation.DERIVED} and not self.store.contradictions(i) for i in ids)
        def discover(stage,name,query):
            attempt_id=execution_id+":abstention:"+stage+":"+name
            provider=self.engine.discovery.get(name)
            if self.durable.get(attempt_id,"SKIPPED") is not None:return None,None
            def skip(reason):
                self.durable.emit(attempt_id,"SKIPPED",{"provider":name,"query":asdict(query),"reason":reason})
                return None,None
            if name not in allowed_providers or provider is None or getattr(provider,"name",None)!=name:
                return skip("Not authorized or no provider")
            circuit=CircuitBreaker(self.store,self.engine.circuit_threshold,self.engine.circuit_cooldown_seconds)
            previous=self.store.discovery_receipt(attempt_id)
            started=self.durable.get(attempt_id,"STARTED") is not None
            if not previous and not started:
                if not circuit.admit(name,attempt_id,timestamp):return skip("Circuit open")
                try:healthy=provider.health_check()
                except Exception:healthy=False
                if not healthy:
                    circuit.cancel_probe(name,attempt_id,timestamp);return skip("Health unavailable")
            def invoke(commit):
                try:
                    if callable(getattr(provider,"invoke_durable",None)):
                        r=provider.invoke_durable(query,attempt_id,commit)
                    else:r=provider.invoke(query)
                    if not isinstance(r,DiscoveryResult) or any(c.capability_match!=query.capability or not c.verification_required for c in r.candidates):
                        raise ValueError("Invalid discovery response")
                    canonical(asdict(r));return commit(r)
                except Exception as exc:
                    return commit(DiscoveryResult(ResultStatus.TIMEOUT if isinstance(exc,TimeoutError) else ResultStatus.FAIL,FailureSignature.NONE,(),(),Derivation.UNKNOWN,("Discovery error: "+type(exc).__name__,),()))
            if previous:r=discovery_from(previous["result"]);eid=previous["evidence_id"]
            else:
                r=self.durable.run_operation(attempt_id,{"provider":name,"query":asdict(query),"timestamp":timestamp},invoke,discovery_from,discovery=True)
                eid=self.store.record_discovery(attempt_id,name,timestamp,query,r)
            circuit.complete(name,SimpleNamespace(attempt_id=attempt_id,provider=name,status=r.status,timestamp=timestamp))
            self.learning.write(attempt_id,{"kind":"discovery_query","data":{"provider":name,"query":asdict(query),"result":asdict(r),"evidence_id":eid}})
            return r,eid
        def attempts_for(stage):
            out=[];seen=set()
            for r in rounds:
                for key,s in r.stages.items():
                    if key!=stage:continue
                    for a in s.attempts:
                        if not hasattr(a,"provider"):continue
                        receipt=self.store.get_attempt(a.receipt_id) if a.receipt_id else None
                        ident=a.receipt_id or digest(asdict(a))
                        if ident in seen:continue
                        seen.add(ident)
                        row={"stage":key,"provider":a.provider,"rung":a.rung,"failure_signature":a.failure_signature.value,
                             "attempt_id":a.receipt_id,"result":receipt.result if receipt else None,"reason":a.reason}
                        out.append(row)
                        if receipt and receipt.status is not ResultStatus.PASS:
                            self.learning.write("failure:"+receipt.attempt_id,{"kind":"failure_receipt","data":row})
            return out
        def accepted(s):
            return s.status is StageStatus.PASS and bool(s.evidence_ids) and not any(self.store.contradictions(i) for i in s.evidence_ids if self.store.get(i))
        def seed(r):
            return {k:v for k,v in r.stages.items() if k in graph}
        def has_incomplete(rows):
            return any(a["result"] and a["result"]["status"]=="INCOMPLETE" for a in rows)
        def can_retry(stage,provider):
            return provider in allowed_providers and provider in self.engine.providers and any(provider in rung["providers"] for rung in provider_ladder(graph[stage]))
        transition(SupervisorState.PLANNING,SupervisorAction.CONTINUE,"Plan bounded fixture execution")
        transition(SupervisorState.EXECUTING,SupervisorAction.CONTINUE,"Run deterministic DAG")
        current=run_dag("initial")
        transition(SupervisorState.PLANNING,SupervisorAction.CONTINUE,"Inspect DAG terminal dispositions")
        blocked=False;invalid=False
        for stage_id in sorted(objectives):
            objective=objectives[stage_id]
            if stage_id not in graph:raise ValueError("Objective stage missing")
            s=current.stages[stage_id]
            if accepted(s):
                continue
            rows=attempts_for(stage_id)
            # Only transient failures are eligible for a bounded retry. Missing
            # auth requires already authorized provider; no credential changes.
            transient=[a for a in rows if not has_incomplete(rows) and a["result"] and ((a["result"]["status"]=="TIMEOUT" and a["failure_signature"]=="NONE") or a["failure_signature"] in {"RATE_LIMITED","AUTH_MISSING"})]
            for provider in sorted({a["provider"] for a in transient}):
                if not can_retry(stage_id,provider):continue
                for i in range(self.retries):
                    transition(SupervisorState.REPAIRING,SupervisorAction.REPAIR,"Bounded transient retry",stage_id)
                    current=run_dag("retry:"+stage_id+":"+provider+":"+str(i),seed(current),{stage_id:{"provider":provider,"configuration":{}}},retry_stage=stage_id)
                    if accepted(current.stages[stage_id]):break
                if current.stages[stage_id].status is StageStatus.PASS:break
            if current.stages[stage_id].status is StageStatus.PASS:continue
            rows=attempts_for(stage_id);s=current.stages[stage_id]
            signatures=tuple(dict.fromkeys(a["failure_signature"] for a in rows))
            sig=next((FailureSignature(x) for x in signatures if x!="NONE"),FailureSignature.NONE)
            refs=tuple(dict.fromkeys((*s.evidence_ids,*objective.get("evidence_ids",[]))))
            query=DiscoveryQuery(objective.get("capability",graph[stage_id]["capability"]),None,fingerprint.archetype,sig,
                ("MIT","Apache-2.0","BSD-2-Clause","BSD-3-Clause","ISC"),"synthetic-fixture",
                objective.get("observable_behavior",""),objective.get("undetermined_mechanism",""),s.exhaustion_receipts,
                tuple(c["artifact_type"] for c in graph[stage_id]["output_contract"]),signatures)
            transition(SupervisorState.DISCOVERING,SupervisorAction.DISCOVER,"Consult prior knowledge before abstention",stage_id,refs)
            found=[];discovery_refs=[]
            r,eid=discover(stage_id,"knowledge_retrieval",query)
            if r and r.status is ResultStatus.PASS:found.extend(r.candidates);discovery_refs.append(eid)
            # Only explicitly recorded prior successful fixture configurations,
            # not arbitrary search candidates, can be replayed.
            strategy_key=execution_id+":strategies:"+stage_id
            chosen=self.durable.get(strategy_key,"SELECTED")
            if chosen is None:
                strategies=[(i,s) for i,s in self.learning.strategies(fingerprint.archetype.value,sig.value,query.capability,stage_id)
                            if not i.startswith(execution_id+":")]
                chosen={"rows":strategies[:1] if not has_incomplete(rows) and sig not in {FailureSignature.PINNED,FailureSignature.TIMEOUT_ADVERSARIAL} else []}
                self.durable.emit(strategy_key,"SELECTED",chosen)
            for strategy_id,strategy in chosen["rows"]:
                provider=strategy.get("provider");config=strategy.get("configuration")
                if not can_retry(stage_id,provider) or not isinstance(config,dict) or not available_observations(strategy.get("evidence_ids",[])):
                    continue
                transition(SupervisorState.REPAIRING,SupervisorAction.REPAIR,"Replay prior successful authorized fixture strategy",stage_id,strategy["evidence_ids"])
                current=run_dag("prior:"+stage_id+":"+digest(strategy_id),seed(current),{stage_id:{"provider":provider,"configuration":config}},retry_stage=stage_id)
                self.learning.write(execution_id+":strategy:"+stage_id,{"kind":"strategy_outcome","data":{"archetype":fingerprint.archetype.value,"failure_signature":sig.value,"capability":query.capability,"stage_id":stage_id,"provider":provider,"configuration":config,"outcome":"PASS" if current.stages[stage_id].status is StageStatus.PASS else "FAIL","evidence_ids":list(current.stages[stage_id].evidence_ids)}})
            if current.stages[stage_id].status is StageStatus.PASS:continue
            transition(SupervisorState.DISCOVERING,SupervisorAction.DISCOVER,"Research alternative providers and independent construction paths",stage_id)
            for name in ("github_search","browser_research"):
                r,eid=discover(stage_id,name,query)
                if r and r.status is ResultStatus.PASS:found.extend(r.candidates);discovery_refs.append(eid)
            obs=objective.get("evidence_ids",[])
            candidates=[c for c in found if c.license_risk!="high" and c.provenance_tier in {3,4} and c.derivation is Derivation.INFERRED]
            brief=None;reason=None;brief_id=None
            if candidates and available_observations(obs) and objective.get("observable_behavior") and objective.get("undetermined_mechanism") and objective.get("acceptance_test"):
                paths=[{"candidate_id":digest(asdict(c)),"canonical_path":c.canonical_path,"verification_required":c.verification_required,"license":c.license} for c in candidates]
                brief={"observable_behavior":objective["observable_behavior"],"undetermined_mechanism":objective["undetermined_mechanism"],
                    "approximation":{"description":"Independent candidate implementation; original mechanism remains unknown","provenance_tier":max(c.provenance_tier for c in candidates)},
                    "supporting_evidence":list(dict.fromkeys((*obs,*discovery_refs))),"implementation_path":paths,"acceptance_test":objective["acceptance_test"]}
                brief_id=execution_id+":"+stage_id
            else:reason="No qualified construction path with persisted observation and acceptance specification" if candidates else "No eligible discovery candidate; additional authorized evidence or host capability required"
            try:
                self.dossier.write(execution_id+":"+stage_id,{"kind":"unresolved","gap_id":stage_id,"status":"ABSTAINED","construction_brief":brief,"no_brief_reason":reason})
            except DossierError as exc:
                transition(SupervisorState.ESCALATED,SupervisorAction.ESCALATE,"Dossier rejected: "+str(exc),stage_id)
                invalid=True;break
            rows=attempts_for(stage_id)
            issued=self.store.discoveries_for_run(execution_id)
            for item in issued:
                self.learning.write(item["attempt_id"],{"kind":"discovery_query","data":{k:v for k,v in item.items() if k!="attempt_id"}})
            for ref in refs:
                for other in self.store.contradictions(ref):
                    ids=sorted((ref,other))
                    self.learning.write("contradiction:"+digest(ids),{"kind":"contradiction","data":{"evidence_ids":ids}})
            all_rows=[a for k in sorted(graph) for a in attempts_for(k)]
            record=AbstentionRecord(fingerprint.archetype,tuple(dict.fromkeys(a["failure_signature"] for a in all_rows)),
                tuple(dict.fromkeys(k for r in rounds for k in r.trace if r.stages[k].attempts)),tuple(sorted({a["rung"] for a in all_rows if a["rung"] is not None})),
                tuple(all_rows),issued,brief_id,reason,(objective.get("required_to_proceed") or "Authorized fixture observation and independent verification",))
            self.learning.write(execution_id+":abstain:"+stage_id,{"kind":"abstention","data":asdict(record)})
            abstentions.append(record)
            self.durable.hook("after_abstention_write")
            blocked|=bool(objective.get("blocks_downstream"))
        if invalid:state=SupervisorState.ESCALATED
        elif abstentions:
            transition(SupervisorState.ABSTAINED,SupervisorAction.ABSTAIN,"Structured unresolved findings persisted")
            state=SupervisorState.ABSTAINED
            if blocked:
                transition(SupervisorState.ESCALATED,SupervisorAction.ESCALATE,"Abstention blocks downstream work");state=SupervisorState.ESCALATED
        else:
            transition(SupervisorState.VERIFYING,SupervisorAction.VERIFY,"Fixture gate only; independent verification deferred")
            verification="synthetic"
            for stage_id in sorted(objectives):
                evidence=[i for i in current.stages[stage_id].evidence_ids if self.store.get(i) and self.store.get(i).status is ResultStatus.PASS and not self.store.contradictions(i)]
                try:self.dossier.write(execution_id+":"+stage_id,{"kind":"fixture_result","gap_id":stage_id,"status":"YELLOW","verification_method":"synthetic","residual_uncertainty":["Independent functional equivalence of "+stage_id+" not verified"],"evidence_ids":evidence})
                except DossierError as exc:
                    transition(SupervisorState.ESCALATED,SupervisorAction.ESCALATE,"Dossier rejected: "+str(exc),stage_id)
                    result=SupervisorResult(SupervisorState.ESCALATED,tuple(states),tuple(decisions),tuple(abstentions),verification)
                    self.durable.emit(execution_id+":supervisor","TERMINAL",asdict(result))
                    return result
            transition(SupervisorState.CLOSED,SupervisorAction.CONTINUE,"Synthetic objectives met; YELLOW named residual, not GREEN")
            state=SupervisorState.CLOSED
        result=SupervisorResult(state,tuple(states),tuple(decisions),tuple(abstentions),verification)
        self.durable.emit(execution_id+":supervisor","TERMINAL",asdict(result))
        self.durable.hook("after_supervisor_terminal")
        return result


def supervisor_result_from(row):
    return SupervisorResult(SupervisorState(row["state"]),tuple(SupervisorState(x) for x in row["transitions"]),
        tuple(SupervisorDecision(SupervisorAction(x["action"]),x["reason"],x["target"],tuple(x["evidence_ids"])) for x in row["decisions"]),
        tuple(AbstentionRecord(Archetype(x["archetype"]),tuple(x["failure_signatures"]),tuple(x["stages_attempted"]),
            tuple(x["rungs_attempted"]),tuple(x["providers_attempted"]),tuple(x["discovery_queries_issued"]),
            x["construction_brief_id"],x["no_brief_reason"],tuple(x["required_to_proceed"])) for x in row["abstentions"]),row["verification_method"])
