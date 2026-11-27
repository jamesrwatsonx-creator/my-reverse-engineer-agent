"""Deterministic, fixture-only DAG scheduler. No policy loop or real-target adapter."""
from __future__ import annotations
from dataclasses import asdict, dataclass, replace
from enum import Enum
import json
from pathlib import Path
from .contracts import (Artifact,ArtifactContract,Stage,Layer,ProviderInput,TargetFingerprint,
    DiscoveryQuery,DiscoveryResult,DiscoveryCandidate,DiscoveryKind,EvidenceEntry,ObservationScope,
    ResultStatus,FailureSignature,Derivation)
from .evidence_store import digest
from .executor import execute_stage,ExecutionPass,ExhaustedResult,Attempt
from .streaming_capture import normalize_capture_result
from .circuit_breaker import CircuitBreaker
from types import SimpleNamespace
from .durability import artifact_from,candidate_from,discovery_from

class StageStatus(str,Enum):
    PASS="PASS"
    EXHAUSTED="EXHAUSTED"
    UNSATISFIED_INPUT="UNSATISFIED_INPUT"
    NOT_READY="NOT_READY"
    SKIPPED="SKIPPED"

@dataclass(frozen=True)
class UnsatisfiedInput:
    artifact_type:str
    field:str
    expected:object
    available:tuple[object,...]

@dataclass(frozen=True)
class StageResult:
    status:StageStatus
    evidence_ids:tuple[str,...]=()
    exhaustion_receipts:tuple[str,...]=()
    attempts:tuple=()
    artifacts:tuple[Artifact,...]=()
    unsatisfied:tuple[UnsatisfiedInput,...]=()
    reason:str=""
    candidates:tuple[DiscoveryCandidate,...]=()
    trigger_receipts:tuple[str,...]=()

@dataclass(frozen=True)
class DagResult:
    archetype:str
    stages:dict[str,StageResult]
    trace:tuple[str,...]


def load_graphs(path):
    data=json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("schema_version") not in {1,2}:raise ValueError("Unsupported stage schema")
    graphs=data["graphs"]
    for graph in graphs.values():_validate(graph)
    return graphs


def _contracts(rows):
    out=[]
    for row in rows:
        if not isinstance(row.get("artifact_type"),str) or not isinstance(row.get("required_fields"),dict):
            raise ValueError("Invalid artifact contract")
        out.append(ArtifactContract(row["artifact_type"],row["required_fields"]))
    return tuple(out)


PARADIGMS=("static","symbolic-emulation","live-instrumentation","black-box-discovery")

def provider_ladder(row):
    # Legacy in-memory Phase 3 fixture rows retain their original single rung.
    if "ladder" not in row:
        return ({"rung":1,"paradigm":"static","providers":row["providers"],"trigger_signatures":[]},)
    return tuple(row["ladder"])

def _validate(rows):
    stages={}
    for row in rows:
        ident=row["id"]
        if not isinstance(ident,str) or not ident or "@" in ident or ident in stages:
            raise ValueError("Invalid or duplicate stage ID")
        if row["kind"] not in {"analysis","discovery"} or row["gate"]!="fixture-contract":
            raise ValueError("Unknown stage kind or gate")
        Layer(row["layer"])
        ladder=provider_ladder(row)
        if "ladder" in row:
            if "providers" in row or [(r["rung"],r["paradigm"]) for r in ladder]!=list(enumerate(PARADIGMS,1)):
                raise ValueError("Exactly four ordered paradigms required")
            for rung in ladder:
                for sig in rung["trigger_signatures"]:
                    if FailureSignature(sig) in {FailureSignature.PINNED,FailureSignature.TIMEOUT_ADVERSARIAL,FailureSignature.NONE}:
                        raise ValueError("Unsafe or ambiguous automatic escalation signature")
            if set(ladder[3].get("discovery_stages",[]))!=set(row["on_fail"]):
                raise ValueError("Rung four discovery routes must match on_fail")
        names=[p for rung in ladder for p in rung["providers"]]
        if not names or len(set(names))!=len(names):
            raise ValueError("Providers must be ordered and unique within stage")
        if "streaming_capture" in row:
            spec=row["streaming_capture"]
            if spec["method"]!="IO.read" or not 0<spec["chunk_bytes"]<=spec["threshold_bytes"]<=spec["max_bytes"]:
                raise ValueError("Invalid streaming capture spec")
        _contracts(row["input_contract"]);_contracts(row["output_contract"])
        stages[ident]=row
    for ident,row in stages.items():
        for pre in row["preconditions"]:
            if pre not in stages or stages[pre]["kind"]!="analysis":
                raise ValueError("Unknown/non-analysis prerequisite: "+pre)
        for dest in row["on_fail"]:
            if dest not in stages or stages[dest]["kind"]!="discovery":
                raise ValueError("Unknown discovery route "+dest)
        if row["kind"]=="discovery" and (row.get("trigger") not in {"EXHAUSTED","UNRESOLVED"} or row["preconditions"] or row["on_fail"]):
            raise ValueError("Discovery templates require a terminal event, no recursive routes")
    pending={k:set(v["preconditions"]) for k,v in stages.items() if v["kind"]=="analysis"}
    while pending:
        ready=sorted(k for k,v in pending.items() if not v)
        if not ready:raise ValueError("Dependency cycle")
        for k in ready:del pending[k]
        for deps in pending.values():deps.difference_update(ready)
    return stages


def _value(payload,path):
    for p in path.split("."):
        if not isinstance(payload,dict) or p not in payload:return None
        payload=payload[p]
    return payload


def check_contract(contracts,artifacts):
    failures=[]
    for rule in contracts:
        candidates=[a for a in artifacts if a.artifact_type==rule.artifact_type and
                    isinstance(a.payload,dict) and digest(a.payload)==a.sha256]
        if not candidates:
            failures.append(UnsatisfiedInput(rule.artifact_type,"<artifact>",rule.artifact_type,tuple(a.artifact_type for a in artifacts)))
            continue
        def matches(a,path,expected):
            value=_value(a.payload,path)
            return value is not None if expected is None else type(value) is type(expected) and value==expected
        if any(all(matches(a,k,v) for k,v in rule.required_fields.items()) for a in candidates):continue
        for k,v in rule.required_fields.items():
            failures.append(UnsatisfiedInput(rule.artifact_type,k,v,tuple(_value(a.payload,k) for a in candidates)))
    return tuple(failures)


class DagEngine:
    def __init__(self,graphs,providers,matrix,store,discovery,*,stream_reader=None,artifact_directory=None,circuit_threshold=3,circuit_cooldown_seconds=60,durable=None):
        self.graphs=graphs;self.providers=providers;self.matrix=matrix;self.store=store;self.discovery=discovery
        self.stream_reader=stream_reader;self.artifact_directory=artifact_directory;self.durable=durable
        self.circuit_threshold=circuit_threshold;self.circuit_cooldown_seconds=circuit_cooldown_seconds
        for rows in graphs.values():_validate(rows)

    def run(self,fingerprint:TargetFingerprint,*,input_hash:str,execution_id:str,timestamp,
            allowed_providers:frozenset[str],unresolved=None,initial_artifacts=(),seed_passes=None,stage_overrides=None,retry_stage=None):
        """Only explicit fixture inputs; caller classifies unresolved gaps, not this scheduler."""
        graph=_validate(self.graphs.get(fingerprint.archetype.value,[]))
        if not graph:raise ValueError("Archetype graph not authored")
        unresolved=unresolved or {};seed_passes=seed_passes or {};stage_overrides=stage_overrides or {}
        if retry_stage is not None and retry_stage not in graph:raise ValueError('Unknown retry stage')
        affected={retry_stage} if retry_stage else set()
        while retry_stage:
            more={k for k,v in graph.items() if set(v['preconditions'])&affected}
            if more<=affected:break
            affected|=more
        if self.durable:
            self.durable.emit(execution_id+':dag','PLAN',{'graph':list(graph.values()),'fingerprint':asdict(fingerprint),'input_hash':input_hash,'timestamp':timestamp,'allowed':sorted(allowed_providers),'unresolved':unresolved,'initial_artifacts':[asdict(a) for a in initial_artifacts],'seed_passes':{k:asdict(v) for k,v in seed_passes.items()},'overrides':stage_overrides,'retry_stage':retry_stage})
        results={};trace=[];fired=set();events={}
        discovery_circuit=CircuitBreaker(self.store,self.circuit_threshold,self.circuit_cooldown_seconds)
        pending={k for k,v in graph.items() if v["kind"]=="analysis"}
        def save(ident,result):
            results[ident]=result;trace.append(ident)
            if self.durable:
                self.durable.checkpoint(execution_id+':stage:'+ident,asdict(result))
                self.durable.hook('after_stage')

        def event_artifact(kind,payload,eid):
            return Artifact(kind,"ledger:"+eid,digest(payload),eid,"dag-engine",Derivation.DERIVED,("synthetic event",),payload)

        def discover(template,parent,trigger,receipt_ids,signature,available):
            row=graph[template];ident=template+"@"+parent
            fired.add(template)
            missing=check_contract(_contracts(row["input_contract"]),available)
            if missing:
                save(ident,StageResult(StageStatus.UNSATISFIED_INPUT,unsatisfied=missing,trigger_receipts=receipt_ids));return
            gap=unresolved.get(parent,{})
            query=DiscoveryQuery(graph[parent]["capability"],graph[parent].get("language"),fingerprint.archetype,signature,
                ("MIT","Apache-2.0","BSD-2-Clause","BSD-3-Clause","ISC"),"synthetic-fixture",
                gap.get("observable_behavior",""),gap.get("undetermined_mechanism",""),receipt_ids,
                tuple(c.artifact_type for c in _contracts(graph[parent]["output_contract"])),
                tuple(a.failure_signature.value for a in results[parent].attempts))
            candidates=[];refs=[];attempts=[];exhaustion=[]
            for name in (p for rung in provider_ladder(row) for p in rung["providers"]):
                provider=self.discovery.get(name)
                if name not in allowed_providers or provider is None or getattr(provider,"name",None)!=name:
                    attempts.append((name,"SKIPPED","not authorized or no discovery adapter"));continue
                attempt_id=execution_id+":"+ident+":"+name
                # OPEN must skip even the provider health invocation.
                prior=self.store.discovery_receipt(attempt_id) if self.durable else None
                started=self.durable is not None and self.durable.get(attempt_id,'STARTED') is not None
                if not prior and not started and not discovery_circuit.admit(name,attempt_id,timestamp):
                    attempts.append((name,"SKIPPED",FailureSignature.CIRCUIT_OPEN.value));continue
                try: healthy=bool(prior or started) or provider.health_check()
                except Exception:healthy=False
                if not healthy:
                    discovery_circuit.cancel_probe(name,attempt_id,timestamp)
                    attempts.append((name,"SKIPPED","health unavailable"));continue
                def invoke(commit):
                    try:
                        r=provider.invoke_durable(query,attempt_id,commit) if self.durable and callable(getattr(provider,"invoke_durable",None)) else provider.invoke(query)
                        if not isinstance(r,DiscoveryResult):raise TypeError("Invalid discovery result")
                        if r.status is ResultStatus.PASS and any(not c.verification_required or c.capability_match!=query.capability for c in r.candidates):
                            raise ValueError("Unscoped discovery candidate")
                        digest(asdict(r))
                    except Exception as exc:
                        r=DiscoveryResult(ResultStatus.TIMEOUT if isinstance(exc,TimeoutError) else ResultStatus.FAIL,FailureSignature.NONE,(),(),Derivation.UNKNOWN,("Discovery adapter error: "+type(exc).__name__,),())
                    return commit(r)
                if prior:
                    r=discovery_from(prior["result"]);eid=prior["evidence_id"]
                else:
                    r=self.durable.run_operation(attempt_id,{"provider":name,"query":asdict(query),"timestamp":timestamp},invoke,discovery_from,discovery=True) if self.durable else invoke(lambda x:x)
                    eid=self.store.record_discovery(attempt_id,name,timestamp,query,r)
                    if self.durable:self.durable.hook("after_discovery_evidence")
                discovery_circuit.complete(name,SimpleNamespace(attempt_id=attempt_id,provider=name,status=r.status,timestamp=timestamp))
                refs.append(eid);attempts.append((name,r.status.value,r.failure_signature.value,eid))
                if r.status is ResultStatus.PASS:candidates.extend(r.candidates)
                else:exhaustion.append(eid)
            # Preserve all candidate observations, even duplicate paths with
            # differing provenance. No auto-install or automatic re-entry.
            if candidates:
                payload={"candidates":[asdict(c) for c in candidates],"trigger_receipts":list(receipt_ids)}
                art=event_artifact("discovery-candidates",payload,refs[0])
                missing=check_contract(_contracts(row["output_contract"]),(art,))
                status=StageStatus.UNSATISFIED_INPUT if missing else StageStatus.PASS
                save(ident,StageResult(status,tuple(refs),tuple(exhaustion),tuple(attempts),(art,),missing,
                    "Discovery candidate list only; not target verification",tuple(candidates),receipt_ids))
            else:
                save(ident,StageResult(StageStatus.EXHAUSTED,tuple(refs),tuple(exhaustion),tuple(attempts),
                    reason="No discovery candidate; no automatic integration",trigger_receipts=receipt_ids))

        while pending or events:
            # A stage becomes decidable once all dependencies are terminal.
            ready=sorted(k for k in pending if set(graph[k]["preconditions"])<=results.keys())
            ready=sorted((*ready,*events))
            if not ready:raise RuntimeError("Validated graph cannot progress")
            ident=ready[0]
            if ident in events:
                args=events.pop(ident)
                discover(*args)
                continue
            pending.remove(ident);row=graph[ident]
            pre=row["preconditions"]
            if retry_stage is not None and ident not in affected and ident in seed_passes:
                save(ident,seed_passes[ident]);continue
            if any(results[k].status is not StageStatus.PASS for k in pre):
                save(ident,StageResult(StageStatus.NOT_READY,reason="Prerequisite not PASS: "+", ".join(k for k in pre if results[k].status is not StageStatus.PASS)));continue
            artifacts=tuple(a for k in pre for a in results[k].artifacts) if pre else tuple(initial_artifacts)
            input_contract=_contracts(row["input_contract"]);output_contract=_contracts(row["output_contract"])
            missing=check_contract(input_contract,artifacts)
            if missing:
                save(ident,StageResult(StageStatus.UNSATISFIED_INPUT,unsatisfied=missing,reason="Input contract not satisfied"));continue
            cached=self.durable.get(execution_id+":stage:"+ident,"CHECKPOINT") if self.durable else None
            if cached and cached["status"]=="PASS":
                save(ident,stage_result_from(cached));continue
            seeded=seed_passes.get(ident)
            if seeded is not None and ident not in affected and seeded.status is StageStatus.PASS and not check_contract(output_contract,seeded.artifacts):
                save(ident,seeded);continue
            override=stage_overrides.get(ident,{})
            stage_hash=digest({"root":input_hash,"stage":ident,"inputs":[a.sha256 for a in artifacts],**({"configuration":override} if override else {})})
            spec=row.get("streaming_capture")
            inp=ProviderInput(ident,artifacts,{**override.get("configuration",{}),**({"streaming_capture":spec} if spec else {})},"synthetic-fixture")
            transform=(lambda result:normalize_capture_result(result,spec,self.stream_reader,self.artifact_directory)) if spec else None
            combined=[];prior_signatures=set();started=False;discovery_allowed="ladder" not in row
            r=ExhaustedResult(ident,(),"No eligible rung")
            for rung in provider_ladder(row):
                names=[n for n in rung["providers"] if not override.get("provider") or n==override["provider"]]; destinations=rung.get("discovery_stages",[])
                if not names and not destinations:continue  # inapplicable paradigm, not an attempt
                triggers={FailureSignature(s) for s in rung["trigger_signatures"]}
                if started and (not prior_signatures.intersection(triggers) or prior_signatures.intersection({FailureSignature.PINNED,FailureSignature.TIMEOUT_ADVERSARIAL})):
                    # Stop the ladder on a nonmatching structural outcome.
                    break
                if destinations:discovery_allowed=True
                if not names:continue
                started=True
                stage=Stage(ident,Layer(row["layer"]),tuple(pre),tuple(names),
                    lambda result:not check_contract(output_contract,result.artifacts),(),input_contract,output_contract)
                r=execute_stage(stage,fingerprint,self.providers,self.matrix,self.store,inp,stage_hash,
                    allowed_providers=allowed_providers,execution_id=execution_id+":rung-"+str(rung["rung"]),timestamp=timestamp,repair_stages={},
                    passed_preconditions=frozenset(k for k in pre if results[k].status is StageStatus.PASS),
                    circuit_threshold=self.circuit_threshold,circuit_cooldown_seconds=self.circuit_cooldown_seconds,
                    transform_result=transform,durable=self.durable)
                combined.extend(replace(a,rung=rung["rung"]) for a in r.trace)
                prior_signatures={a.failure_signature for a in r.trace}
                if isinstance(r,ExecutionPass) or any(a.status is ResultStatus.INCOMPLETE for a in r.trace):break
            r=replace(r,trace=tuple(combined))
            attempt_receipts=tuple(a.receipt_id for a in r.trace if a.receipt_id)
            evidence=tuple(self.store.get_attempt(a).evidence_id for a in attempt_receipts)
            if isinstance(r,ExecutionPass):
                save(ident,StageResult(StageStatus.PASS,tuple(dict.fromkeys((*evidence,*r.result.evidence_ids))),
                    attempts=r.trace,artifacts=r.result.artifacts,reason="Fixture contract passed; not global verification"))
                continue
            signatures=tuple(a.failure_signature.value for a in r.trace)
            payload={"stage_id":ident,"attempt_receipts":list(attempt_receipts),"failure_signatures":list(signatures),
                     "artifact_types_attempted":[c.artifact_type for c in output_contract],"reason":r.reason}
            eid=self.store.append(EvidenceEntry("","dag-engine",Derivation.DERIVED,timestamp,stage_hash,digest(payload),
                ("Exhaustion is a scheduler event, not a terminal gap",),(),None,FailureSignature.NONE,ResultStatus.FAIL,
                ObservationScope("exhaustion:"+ident,stage_hash)))
            linked=(*attempt_receipts,eid)
            save(ident,StageResult(StageStatus.EXHAUSTED,(*evidence,eid),linked,r.trace,reason=r.reason))
            signature=next((a.failure_signature for a in r.trace if a.status is not None and a.failure_signature is not FailureSignature.NONE),FailureSignature.NONE)
            for template in sorted(row["on_fail"] if discovery_allowed else []):
                tr=graph[template]["trigger"]
                if tr=="EXHAUSTED":
                    events[template+"@"+ident]=(template,ident,tr,linked,signature,(event_artifact("exhaustion-receipt",payload,eid),))
                elif tr=="UNRESOLVED" and ident in unresolved:
                    gap=unresolved[ident]
                    if not all(isinstance(gap.get(k),str) and gap[k].strip() for k in ("observable_behavior","undetermined_mechanism")):
                        save(template+"@"+ident,StageResult(StageStatus.UNSATISFIED_INPUT,reason="Missing named unresolved behavior/mechanism",trigger_receipts=linked));fired.add(template);continue
                    observation_ids=gap.get("evidence_ids",[])
                    observations=[self.store.get(i) for i in observation_ids if isinstance(i,str)]
                    if not observations or len(observations)!=len(observation_ids) or any(
                            o is None or o.status is not ResultStatus.PASS or o.derivation not in {Derivation.OBSERVED,Derivation.DERIVED}
                            or self.store.contradictions(o.evidence_id) for o in observations):
                        save(template+"@"+ident,StageResult(StageStatus.UNSATISFIED_INPUT,reason="Unresolved behavior needs persisted noncontradicted fixture observation",trigger_receipts=linked));fired.add(template);continue
                    gap_payload={"observable_behavior":gap["observable_behavior"],"undetermined_mechanism":gap["undetermined_mechanism"],
                                 "evidence_ids":observation_ids,"exhaustion_receipts":list(linked)}
                    brief_links=(*linked,*observation_ids)
                    events[template+"@"+ident]=(template,ident,tr,brief_links,signature,(event_artifact("unresolved-gap",gap_payload,eid),))
        for name,row in sorted(graph.items()):
            if row["kind"]=="discovery" and name not in fired:
                save(name,StageResult(StageStatus.SKIPPED,reason="No matching terminal event"))
        result=DagResult(fingerprint.archetype.value,results,tuple(trace))
        self.store.record_dag_run(execution_id,{**asdict(result),"candidate_integrations":[],"timestamp":timestamp})
        return result


def stage_result_from(row):
    attempts=tuple(Attempt(**{**a,"status":ResultStatus(a["status"]) if a["status"] is not None else None,
        "failure_signature":FailureSignature(a["failure_signature"])}) if isinstance(a,dict) else tuple(a) for a in row["attempts"])
    return StageResult(StageStatus(row["status"]),tuple(row["evidence_ids"]),tuple(row["exhaustion_receipts"]),attempts,
        tuple(artifact_from(a) for a in row["artifacts"]),tuple(UnsatisfiedInput(**{**a,"available":tuple(a["available"])}) for a in row["unsatisfied"]),
        row["reason"],tuple(candidate_from(a) for a in row["candidates"]),tuple(row["trigger_receipts"]))
