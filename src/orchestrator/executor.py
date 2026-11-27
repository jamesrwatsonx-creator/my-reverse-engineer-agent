"""One-stage deterministic synthetic execution; no DAG or supervisor."""
from __future__ import annotations
from dataclasses import asdict, dataclass, replace
import re
import subprocess
from datetime import datetime
from typing import Mapping
from .contracts import (Stage,TargetFingerprint,ProviderInput,ProviderResult,Provider,
                        ResultStatus,FailureSignature,Derivation,ObservationScope)
from .evidence_store import EvidenceStore, canonical, digest
from .circuit_breaker import CircuitBreaker
from .durability import result_from


@dataclass(frozen=True)
class Attempt:
    stage_id: str
    provider: str
    status: ResultStatus | None
    failure_signature: FailureSignature
    receipt_id: str | None
    reason: str
    rung: int | None = None


@dataclass(frozen=True)
class ExecutionPass:
    result: ProviderResult
    trace: tuple[Attempt,...]
    gate_passed: bool | None


@dataclass(frozen=True)
class ExhaustedResult:
    stage_id: str
    trace: tuple[Attempt,...]
    reason: str


def execute_stage(stage: Stage, fingerprint: TargetFingerprint,
                  providers: Mapping[str,Provider], matrix, store: EvidenceStore,
                  input: ProviderInput, input_hash: str, *, allowed_providers: frozenset[str],
                  execution_id: str, timestamp: datetime, repair_stages: Mapping[str,Stage],
                  passed_preconditions: frozenset[str]=frozenset(),
                  circuit_threshold: int=3,circuit_cooldown_seconds: float=60,
                  transform_result=None,durable=None) -> ExecutionPass | ExhaustedResult:
    """Call only explicitly authorized fixture adapters; receipt before advancing.

    Provider PASS is not verified closure. Optional supplied stage predicate is
    evaluated but no verification harness is constructed. Repair is one stage
    maximum, no nested repair; original stage can re-enter at most once.
    """
    if input.authorization_ref!="synthetic-fixture" or input.stage_id!=stage.id:
        raise ValueError("Phase 2 execution accepts scoped synthetic fixtures only")
    if not execution_id:
        raise ValueError("Execution identity required")
    if not set(stage.preconditions)<=passed_preconditions:
        return ExhaustedResult(stage.id,(),"Prerequisites not verified; no provider attempted")
    if not re.fullmatch(r"[0-9a-f]{64}", input_hash):
        raise ValueError("Input hash must be SHA-256")
    input=replace(input,parameters={**input.parameters,"target_fingerprint":asdict(fingerprint)})
    trace=[]
    circuit=CircuitBreaker(store,circuit_threshold,circuit_cooldown_seconds)
    def run_once(current: Stage, inp: ProviderInput, round_id: str, attempt_input_hash: str):
        if not set(current.preconditions)<=passed_preconditions:
            return None,None
        for i,name in enumerate(current.providers):
            attempt_id=f"{execution_id}:{current.id}:{round_id}:{i}"
            prior=store.get_attempt(attempt_id)
            started=durable is not None and durable.get(attempt_id,"STARTED") is not None
            if name not in allowed_providers:
                trace.append(Attempt(current.id,name,None,FailureSignature.NONE,None,"Not authorized"))
                continue
            if not started and prior is None and (name not in providers or providers[name].name!=name):
                trace.append(Attempt(current.id,name,None,FailureSignature.NONE,None,"No fixture adapter"))
                continue
            if not started and prior is None and not matrix.is_available(name):
                trace.append(Attempt(current.id,name,None,FailureSignature.HOST_UNSUPPORTED,None,matrix.why_unavailable(name)))
                continue
            if prior is not None and durable is None:
                raise ValueError("Attempt already persisted; explicit replay/resume is required")
            if prior is None and not started and not circuit.admit(name,attempt_id,timestamp):
                trace.append(Attempt(current.id,name,None,FailureSignature.CIRCUIT_OPEN,None,"Circuit open; no invocation"))
                continue
            def prepare(result):
                if not isinstance(result,ProviderResult):
                    raise TypeError("Adapter did not return ProviderResult")
                if not isinstance(result.status,ResultStatus) or not isinstance(result.failure_signature,FailureSignature) or not isinstance(result.derivation,Derivation):
                    raise ValueError("Invalid provider status, signature or derivation")
                if any(not re.fullmatch(r"[0-9a-f]{64}",a.sha256) for a in result.artifacts):
                    raise ValueError("Invalid provider artifact hash")
                if transform_result is not None and result.status is ResultStatus.PASS:
                    result=transform_result(result)
                canonical(asdict(result))
                if result.status is ResultStatus.PASS and not result.artifacts:
                    result=replace(result,status=ResultStatus.EMPTY,limitations=result.limitations+("PASS contained no artifact",),verification_method=None)
                if result.status is ResultStatus.PASS and current.gate is not None:
                    try: gate=current.gate(result) is True
                    except Exception as exc:
                        gate=False
                        result=replace(result,limitations=result.limitations+("Gate raised "+type(exc).__name__,))
                    if not gate:
                        result=replace(result,status=ResultStatus.CONTRADICTED,
                                       limitations=result.limitations+("Supplied stage predicate did not pass",),verification_method=None)
                if current.id=="verify":
                    result=replace(result,verification_method="synthetic")
                elif result.verification_method is not None:
                    # Phase 4 cannot certify even if a fixture adapter claims a method.
                    result=replace(result,verification_method="synthetic")
                return result
            def invoke(commit):
                try:
                    adapter=providers[name]
                    if durable is not None and callable(getattr(adapter,"invoke_durable",None)):
                        # Cooperating adapter commits at its own completion boundary.
                        return adapter.invoke_durable(inp,attempt_id,lambda raw:commit(prepare(raw)))
                    return commit(prepare(adapter.invoke(inp)))
                except Exception as exc:
                    if durable is not None and durable.get(attempt_id,"COMPLETED") is not None:
                        return result_from(durable.get(attempt_id,"COMPLETED"))
                    status=ResultStatus.TIMEOUT if isinstance(exc,(TimeoutError,subprocess.TimeoutExpired)) else ResultStatus.FAIL
                    return commit(ProviderResult(status,FailureSignature.NONE,(),(),Derivation.UNKNOWN,
                                      ("Adapter exception or invalid response: "+type(exc).__name__,),(),None,None))
            if prior is not None:
                if prior.provider!=name or prior.input_hash!=attempt_input_hash:
                    raise ValueError("Persisted attempt identity differs")
                result=result_from(prior.result)
                receipt=prior
            else:
                if durable is not None:
                    request={"provider":name,"input_hash":attempt_input_hash,"input":asdict(inp),"timestamp":timestamp}
                    result=durable.run_operation(attempt_id,request,invoke,result_from)
                    if result is None:
                        result=ProviderResult(ResultStatus.INCOMPLETE,FailureSignature.NONE,(),(),Derivation.UNKNOWN,
                            ("Unknown completion; no automatic reinvocation; attempt hash "+durable.get(attempt_id,"STARTED")["attempt_hash"],),(),None,None)
                else:
                    result=invoke(lambda x:x)
                receipt=store.record_attempt(attempt_id,name,timestamp,attempt_input_hash,result,ObservationScope(current.id,attempt_input_hash))
                if durable is not None:durable.hook("after_evidence")
            if result.status is not ResultStatus.INCOMPLETE:
                circuit.complete(name,receipt)
            else:
                circuit.cancel_probe(name,attempt_id,timestamp)
            gate=True if result.status is ResultStatus.PASS and current.gate is not None else None
            trace.append(Attempt(current.id,name,result.status,result.failure_signature,receipt.attempt_id,
                                 "provider result; not global verification"))
            if result.status is ResultStatus.PASS:
                return replace(result,evidence_ids=tuple(dict.fromkeys((*result.evidence_ids,receipt.evidence_id)))),gate
        return None,None
    result,gate=run_once(stage,input,"initial",input_hash)
    if result is not None:
        return ExecutionPass(result,tuple(trace),gate)
    seen={x.failure_signature for x in trace if x.status is not None}
    # Select first matching explicit route, then first registered repair stage;
    # no NONE retry, no recursion, no permission escalation, no adversarial loop.
    selected=None
    for route in stage.on_fail:
        if route.failure_signature in seen and route.failure_signature not in {
                FailureSignature.NONE,FailureSignature.PINNED,FailureSignature.TIMEOUT_ADVERSARIAL}:
            selected=next((repair_stages[s] for s in route.stage_ids
                           if s in repair_stages and s!=stage.id),None)
            if selected is not None:
                break
    if selected is not None:
        repaired,_=run_once(selected,replace(input,stage_id=selected.id),"repair",input_hash)
        if repaired is not None:
            augmented=replace(input,artifacts=(*input.artifacts,*repaired.artifacts))
            # Augmented input is a distinct, deterministic manifest; do not claim
            # a modified input was the exact same artifact as the original.
            augmented_hash=digest({"original_input_hash":input_hash,
                                   "repair_artifact_hashes":[a.sha256 for a in repaired.artifacts]})
            result,gate=run_once(stage,augmented,"reentry",augmented_hash)
            if result is not None:
                return ExecutionPass(result,tuple(trace),gate)
    return ExhaustedResult(stage.id,tuple(trace),"Provider list exhausted; supervisor decision required")
