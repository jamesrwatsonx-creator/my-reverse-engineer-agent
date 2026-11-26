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
    if not re.fullmatch(r"[0-9a-f]{64}", input_hash):
        raise ValueError("Input hash must be SHA-256")
    input=replace(input,parameters={**input.parameters,"target_fingerprint":asdict(fingerprint)})
    trace=[]
    def run_once(current: Stage, inp: ProviderInput, round_id: str, attempt_input_hash: str):
        if not set(current.preconditions)<=passed_preconditions:
            return None,None
        for i,name in enumerate(current.providers):
            if name not in allowed_providers or name not in providers or providers[name].name!=name:
                trace.append(Attempt(current.id,name,None,FailureSignature.NONE,None,"Not authorized or no fixture adapter"))
                continue
            if not matrix.is_available(name):
                trace.append(Attempt(current.id,name,None,FailureSignature.HOST_UNSUPPORTED,None,matrix.why_unavailable(name)))
                continue
            try:
                result=providers[name].invoke(inp)
                if not isinstance(result,ProviderResult):
                    raise TypeError("Adapter did not return ProviderResult")
                if not isinstance(result.status,ResultStatus) or not isinstance(result.failure_signature,FailureSignature) or not isinstance(result.derivation,Derivation):
                    raise ValueError("Invalid provider status, signature or derivation")
                if any(not re.fullmatch(r"[0-9a-f]{64}",a.sha256) for a in result.artifacts):
                    raise ValueError("Invalid provider artifact hash")
                canonical(asdict(result))  # reject nonserializable results before ledger write
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
                status=ResultStatus.TIMEOUT if isinstance(exc,(TimeoutError,subprocess.TimeoutExpired)) else ResultStatus.FAIL
                result=ProviderResult(status,FailureSignature.NONE,(),(),Derivation.UNKNOWN,
                                      ("Adapter exception or invalid response: "+type(exc).__name__,),(),None,None)
            receipt=store.record_attempt(f"{execution_id}:{current.id}:{round_id}:{i}",name,timestamp,attempt_input_hash,result,ObservationScope(current.id,attempt_input_hash))
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
