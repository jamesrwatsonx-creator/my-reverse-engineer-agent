"""Persisted deterministic, single-writer fixture circuit breaker."""
from __future__ import annotations
from dataclasses import asdict,dataclass
from datetime import datetime
from enum import Enum
from .contracts import ResultStatus

class CircuitState(str,Enum):
    CLOSED="CLOSED"
    OPEN="OPEN"
    HALF_OPEN="HALF_OPEN"

@dataclass(frozen=True)
class CircuitSnapshot:
    state:CircuitState
    failures:int
    timestamp:datetime | None
    reason:str
    receipt_id:str | None

class CircuitBreaker:
    """Consecutive failed attempts; explicit clock, no sleeps or hidden retries.

    OPEN is skipped until cooldown expires. Exactly one sequential half-open
    probe is permitted; an abandoned probe stays open to further calls until
    another cooldown passes. Multi-worker leasing is outside this phase.
    """
    def __init__(self,store,threshold:int=3,cooldown_seconds:float=60):
        if type(threshold) is not int or threshold<1 or cooldown_seconds<=0:
            raise ValueError("Invalid circuit configuration")
        self.store=store;self.threshold=threshold;self.cooldown_seconds=cooldown_seconds

    def state(self,provider):
        history=self.store.circuit_history(provider)
        if not history:return CircuitSnapshot(CircuitState.CLOSED,0,None,"initial",None)
        r=history[-1]
        return CircuitSnapshot(CircuitState(r["state"]),r["failures"],
            datetime.fromisoformat(r["timestamp"]),r["reason"],r["receipt_id"])

    def _append(self,provider,ident,state,failures,now,reason,receipt_id=None):
        if now.tzinfo is None or now.utcoffset() is None:raise ValueError("Clock must be aware")
        s=CircuitSnapshot(state,failures,now,reason,receipt_id)
        self.store.append_circuit_event(ident,provider,asdict(s))

    def admit(self,provider,attempt_id,now):
        s=self.state(provider)
        if s.state is CircuitState.CLOSED:return True
        if (now-s.timestamp).total_seconds()<self.cooldown_seconds:return False
        event="circuit:probe:"+attempt_id
        if self.store.circuit_event(event) is not None:return False
        self._append(provider,event,CircuitState.HALF_OPEN,s.failures,now,"one cooldown probe")
        return True

    def cancel_probe(self,provider,attempt_id,now):
        """A refused health check is not a provider analysis attempt."""
        if self.store.circuit_event("circuit:probe:"+attempt_id) is not None:
            s=self.state(provider)
            self._append(provider,"circuit:cancel:"+attempt_id,CircuitState.OPEN,s.failures,now,"health unavailable; no invocation")

    def complete(self,provider,receipt):
        ident="circuit:result:"+receipt.attempt_id
        if self.store.circuit_event(ident) is not None:return
        if receipt.provider!=provider:raise ValueError("Receipt/provider mismatch")
        s=self.state(provider)
        if receipt.status is ResultStatus.PASS:
            state=CircuitState.CLOSED;count=0
        else:
            count=s.failures+1
            state=CircuitState.OPEN if s.state is CircuitState.HALF_OPEN or count>=self.threshold else CircuitState.CLOSED
        self._append(provider,ident,state,count,receipt.timestamp,"attempt "+receipt.status.value,receipt.attempt_id)
