"""Local single-writer WAL, cooperative completion outbox, stable invocation keys.
Unknown completion is never guessed. Discovery is read-only and replayable.
"""
from __future__ import annotations
import json
from dataclasses import asdict
from .contracts import (Artifact,ArtifactSchema,ProviderResult,DiscoveryResult,DiscoveryCandidate,
    MaintenanceSignal,Derivation,ResultStatus,FailureSignature)
from .evidence_store import canonical,digest

def artifact_from(row):
    return Artifact(**{**row,"derivation":Derivation(row["derivation"]),"limitations":tuple(row["limitations"])})
def result_from(row):
    return ProviderResult(ResultStatus(row["status"]),FailureSignature(row["failure_signature"]),
        tuple(artifact_from(x) for x in row["artifacts"]),tuple(row["evidence_ids"]),Derivation(row["derivation"]),
        tuple(row["limitations"]),tuple(ArtifactSchema(**x) for x in row["normalized_artifact_schema"]),
        row["satisfies_upstream_requirement"],row["verification_method"])
def candidate_from(row):
    return DiscoveryCandidate(**{**row,"maintenance_signal":MaintenanceSignal(**row["maintenance_signal"]),"derivation":Derivation(row["derivation"])})
def discovery_from(row):
    return DiscoveryResult(ResultStatus(row["status"]),FailureSignature(row["failure_signature"]),
        tuple(candidate_from(x) for x in row["candidates"]),tuple(row["evidence_ids"]),Derivation(row["derivation"]),
        tuple(row["limitations"]),tuple(row["rejections"]))

class DurableExecution:
    def __init__(self,store,hook=None):
        self.store=store;self.hook=hook or (lambda point:None)
        store.db.executescript("""
        CREATE TABLE IF NOT EXISTS durable_events (
          seq INTEGER PRIMARY KEY, event_id TEXT UNIQUE NOT NULL,
          operation TEXT NOT NULL, state TEXT NOT NULL, payload TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS durable_op ON durable_events(operation,seq);
        CREATE TRIGGER IF NOT EXISTS immutable_durable_update BEFORE UPDATE ON durable_events BEGIN SELECT RAISE(ABORT,'append-only'); END;
        CREATE TRIGGER IF NOT EXISTS immutable_durable_delete BEFORE DELETE ON durable_events BEGIN SELECT RAISE(ABORT,'append-only'); END;
        """)
    def emit(self,key,state,payload,*,event=None):
        ident=event or key+":"+state
        data=canonical(payload)
        with self.store.db:
            self.store.db.execute("INSERT OR IGNORE INTO durable_events(event_id,operation,state,payload) VALUES (?,?,?,?)",(ident,key,state,data))
            actual=self.store.db.execute("SELECT operation,state,payload FROM durable_events WHERE event_id=?",(ident,)).fetchone()
            if actual!=(key,state,data):raise ValueError("Durable key reused with different content: "+ident)
    def events(self,key):
        return tuple({"state":s,"payload":json.loads(p)} for s,p in self.store.db.execute("SELECT state,payload FROM durable_events WHERE operation=? ORDER BY seq",(key,)))
    def get(self,key,state):
        rows=[x["payload"] for x in self.events(key) if x["state"]==state]
        return rows[-1] if rows else None
    def checkpoint(self,key,payload):
        self.emit(key,"CHECKPOINT",payload)
    def run_operation(self,key,request,invoke,decode,*,discovery=False):
        """invoke(commit) must commit its completion before returning to the caller.

        Cooperative adapters may commit from inside invoke_durable. Ordinary
        adapters are wrapped; interruption before the outbox commit is unknown.
        Discovery can safely retry with the same key; analysis cannot.
        """
        existing=self.get(key,"STARTED")
        envelope={"request":request,"attempt_hash":digest(request),"kind":"discovery" if discovery else "analysis"}
        if existing is not None and canonical(existing)!=canonical(envelope):
            raise ValueError("Invocation key reused with different request")
        completed=self.get(key,"COMPLETED")
        if completed is not None:return decode(completed)
        if existing is not None:
            self.emit(key,"INCOMPLETE",envelope)
            if not discovery:return None
        else:self.emit(key,"STARTED",envelope)
        def commit(result):
            self.emit(key,"COMPLETED",asdict(result))
            return result
        result=invoke(commit)
        if self.get(key,"COMPLETED") is None:commit(result)
        self.hook("after_discovery_outbox" if discovery else "after_provider_outbox")
        return decode(self.get(key,"COMPLETED"))
