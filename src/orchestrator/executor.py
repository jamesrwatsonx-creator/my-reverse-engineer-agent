"""One-stage deterministic synthetic execution; no DAG or supervisor."""
from __future__ import annotations
from dataclasses import dataclass, replace
from datetime import datetime
from typing import Mapping
from .contracts import (Stage,TargetFingerprint,ProviderInput,ProviderResult,Provider,
                        ResultStatus,FailureSignature,Derivation)
from .evidence_store import EvidenceStore


@dataclass(frozen=True)
class Attempt:
    stage_id: str
    provider: str
    status: ResultStatus | None
    failure_signature: FailureSignature
    receipt_id: str | None
    reason: str


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
                  passed_preconditions: frozenset[str]=frozenset()) -> ExecutionPass | ExhaustedResult:
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
    trace=[]
    def run_once(current: Stage, inp: ProviderInput, round_id: str):
        if not set(current.preconditions)<=passed_preconditions:
            return None,None
        for i,name in enumerate(current.providers):
            if name not in allowed_providers or name not in providers:
                trace.append(Attempt(current.id,name,None,FailureSignature.NONE,None,"Not authorized or no fixture adapter"))
                continue
            if not matrix.is_available(name):
                trace.append(Attempt(current.id,name,None,FailureSignature.HOST_UNSUPPORTED,None,matrix.why_unavailable(name)))
                continue
            try:
                result=providers[name].invoke(inp)
                if not isinstance(result,ProviderResult):
                    raise TypeError("Adapter did not return ProviderResult")
                if result.status is ResultStatus.PASS and not result.artifacts:
                    result=replace(result,status=ResultStatus.EMPTY,
                                   limitations=result.limitations+("PASS contained no artifact",),verification_method=None)
                gate=None
                if result.status is ResultStatus.PASS and current.gate is not None:
                    try:
                        gate=current.gate(result) is True
                    except Exception as exc:
                        gate=False
                        result=replace(result,limitations=result.limitations+("Gate raised "+type(exc).__name__,))
                    if not gate:
                        result=replace(result,status=ResultStatus.CONTRADICTED,
                                       limitations=result.limitations+("Supplied stage predicate did not pass",),verification_method=None)
            except Exception as exc:
                gate=None
                result=ProviderResult(ResultStatus.FAIL,FailureSignature.NONE,(),(),Derivation.UNKNOWN,
                                      ("Adapter exception: "+type(exc).__name__,),(),None,None)
            receipt=store.record_attempt(f"{execution_id}:{current.id}:{round_id}:{i}",name,timestamp,input_hash,result)
            trace.append(Attempt(current.id,name,result.status,result.failure_signature,receipt.attempt_id,
                                 "provider result; not global verification"))
            if result.status is ResultStatus.PASS:
                return result,gate
        return None,None
    result,gate=run_once(stage,input,"initial")
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
        repaired,_=run_once(selected,replace(input,stage_id=selected.id),"repair")
        if repaired is not None:
            result,gate=run_once(stage,input,"reentry")
            if result is not None:
                return ExecutionPass(result,tuple(trace),gate)
    return ExhaustedResult(stage.id,tuple(trace),"Provider list exhausted; supervisor decision required")
