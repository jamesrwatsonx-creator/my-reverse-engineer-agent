"""Append-only local evidence and attempt ledger for synthetic Phase 2 runs."""
from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .contracts import EvidenceEntry, Derivation, FailureSignature, ProviderResult, ResultStatus, ObservationScope, DiscoveryQuery, DiscoveryResult, DiscoveryCandidate, MaintenanceSignal


def canonical(value: Any) -> str:
    """Canonical local JSON; evidence ID itself is excluded from its preimage."""
    def default(obj):
        if isinstance(obj, datetime):
            if obj.tzinfo is None or obj.utcoffset() is None:
                raise ValueError("Naive timestamp")
            return obj.astimezone(timezone.utc).isoformat()
        raise TypeError(type(obj).__name__)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False, default=default)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class AttemptReceipt:
    attempt_id: str
    evidence_id: str
    provider: str
    timestamp: datetime
    input_hash: str | None
    status: ResultStatus
    failure_signature: FailureSignature
    result: dict


class EvidenceStore:
    def __init__(self, path: str | Path):
        self.db = sqlite3.connect(str(path))
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS evidence (
          id TEXT PRIMARY KEY, payload TEXT NOT NULL,
          input_hash TEXT, output_hash TEXT
        );
        CREATE INDEX IF NOT EXISTS evidence_input ON evidence(input_hash);
        CREATE TABLE IF NOT EXISTS conflicts (
          first_id TEXT NOT NULL REFERENCES evidence(id),
          second_id TEXT NOT NULL REFERENCES evidence(id),
          PRIMARY KEY(first_id,second_id), CHECK(first_id < second_id)
        );
        CREATE TABLE IF NOT EXISTS attempts (
          seq INTEGER PRIMARY KEY, attempt_id TEXT UNIQUE NOT NULL,
          evidence_id TEXT NOT NULL REFERENCES evidence(id),
          provider TEXT NOT NULL, timestamp TEXT NOT NULL,
          input_hash TEXT, status TEXT NOT NULL, signature TEXT NOT NULL,
          result TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS attempt_signature ON attempts(signature,input_hash);
        """)
        for table in ("evidence", "conflicts", "attempts"):
            for operation in ("UPDATE", "DELETE"):
                self.db.execute(f"CREATE TRIGGER IF NOT EXISTS immutable_{table}_{operation.lower()} "
                                f"BEFORE {operation} ON {table} BEGIN "
                                "SELECT RAISE(ABORT,'append-only ledger'); END;")
        self.db.execute("""CREATE TABLE IF NOT EXISTS discovery (
          seq INTEGER PRIMARY KEY, attempt_id TEXT UNIQUE NOT NULL,
          evidence_id TEXT NOT NULL REFERENCES evidence(id), provider TEXT NOT NULL,
          query TEXT NOT NULL, result TEXT NOT NULL
        )""")
        for op in ("UPDATE","DELETE"):
            self.db.execute(f"CREATE TRIGGER IF NOT EXISTS immutable_discovery_{op.lower()} BEFORE {op} ON discovery BEGIN SELECT RAISE(ABORT,'append-only ledger'); END;")
        self.db.execute("""CREATE TABLE IF NOT EXISTS dag_runs (
          execution_id TEXT PRIMARY KEY, payload TEXT NOT NULL
        )""")
        for op in ("UPDATE","DELETE"):
            self.db.execute(f"CREATE TRIGGER IF NOT EXISTS immutable_dag_runs_{op.lower()} BEFORE {op} ON dag_runs BEGIN SELECT RAISE(ABORT,'append-only ledger'); END;")
        self.db.commit()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def close(self):
        self.db.close()

    def _link(self, a: str, b: str):
        if a != b:
            self.db.execute("INSERT OR IGNORE INTO conflicts VALUES (?,?)", tuple(sorted((a,b))))

    def _append(self, entry: EvidenceEntry) -> str:
        payload = asdict(entry)
        supplied = payload.pop("evidence_id")
        ident = digest(payload)
        if supplied and supplied != ident:
            raise ValueError("Evidence ID does not match content")
        data = canonical(payload)
        self.db.execute("INSERT OR IGNORE INTO evidence VALUES (?,?,?,?)",
                        (ident,data,entry.input_artifact_hash,entry.output_artifact_hash))
        if self.db.execute("SELECT payload FROM evidence WHERE id=?", (ident,)).fetchone()[0] != data:
            raise ValueError("Evidence identity collision")
        if entry.output_artifact_hash is not None:
            # Explicit scope defines comparable observations. Legacy rows remain
            # comparable only to legacy rows sharing the old input hash.
            for other,raw in self.db.execute(
                    "SELECT id,payload FROM evidence WHERE output_hash IS NOT NULL AND output_hash<>?",
                    (entry.output_artifact_hash,)).fetchall():
                old=json.loads(raw)
                scope=old.get("observation_scope")
                if entry.observation_scope is not None:
                    comparable=scope==asdict(entry.observation_scope)
                else:
                    comparable=scope is None and entry.input_artifact_hash is not None and old.get("input_artifact_hash")==entry.input_artifact_hash
                if comparable:
                    self._link(ident,other)
        for other in entry.contradicts:
            if self.db.execute("SELECT 1 FROM evidence WHERE id=?",(other,)).fetchone() is None:
                raise ValueError("Explicit contradiction refers to missing evidence")
            self._link(ident,other)
        return ident

    def append(self, entry: EvidenceEntry) -> str:
        with self.db:
            return self._append(entry)

    def get(self, evidence_id: str) -> EvidenceEntry | None:
        row = self.db.execute("SELECT payload FROM evidence WHERE id=?",(evidence_id,)).fetchone()
        if row is None:
            return None
        data=json.loads(row[0])
        data.update(evidence_id=evidence_id, derivation=Derivation(data["derivation"]),
                    timestamp=datetime.fromisoformat(data["timestamp"]),
                    failure_signature=FailureSignature(data["failure_signature"]),
                    status=ResultStatus(data["status"]), limitations=tuple(data["limitations"]),
                    contradicts=tuple(data["contradicts"]))
        scope=data.get('observation_scope')
        data['observation_scope']=ObservationScope(**scope) if scope else None
        return EvidenceEntry(**data)

    def contradictions(self, evidence_id: str) -> tuple[str,...]:
        """Symmetric append-only index; do not mutate immutable original entries."""
        return tuple(r[0] for r in self.db.execute(
            "SELECT second_id FROM conflicts WHERE first_id=? UNION "
            "SELECT first_id FROM conflicts WHERE second_id=? ORDER BY 1",
            (evidence_id,evidence_id)))

    def record_attempt(self, attempt_id: str, provider: str, timestamp: datetime,
                       input_hash: str | None, result: ProviderResult, observation_scope: ObservationScope | None=None) -> AttemptReceipt:
        if not attempt_id or not provider:
            raise ValueError("Attempt identity and provider required")
        outputs=tuple(a.sha256 for a in result.artifacts)
        output_hash=outputs[0] if len(outputs)==1 else digest(outputs) if outputs else None
        limits=result.limitations
        if len(outputs)>1:
            limits+=("output hash is canonical ordered artifact-digest manifest",)
        if not outputs or input_hash is None:
            limits+=("attempt has no corresponding input or output artifact",)
        entry=EvidenceEntry("",provider,result.derivation,timestamp,input_hash,output_hash,
                            limits,(),result.verification_method,result.failure_signature,result.status,observation_scope)
        payload=canonical(asdict(result))
        stamp=timestamp.astimezone(timezone.utc).isoformat()
        with self.db:
            eid=self._append(entry)
            values=(attempt_id,eid,provider,stamp,input_hash,result.status.value,
                    result.failure_signature.value,payload)
            self.db.execute("INSERT OR IGNORE INTO attempts(attempt_id,evidence_id,provider,timestamp,input_hash,status,signature,result) VALUES(?,?,?,?,?,?,?,?)",values)
            actual=self.db.execute("SELECT attempt_id,evidence_id,provider,timestamp,input_hash,status,signature,result FROM attempts WHERE attempt_id=?",(attempt_id,)).fetchone()
            if actual!=values:
                raise ValueError("Attempt ID reused with different content")
        return self._receipt(actual)

    @staticmethod
    def _receipt(row) -> AttemptReceipt:
        a,e,p,t,h,s,g,r=row
        return AttemptReceipt(a,e,p,datetime.fromisoformat(t),h,ResultStatus(s),FailureSignature(g),json.loads(r))

    def get_attempt(self, attempt_id: str) -> AttemptReceipt | None:
        row=self.db.execute('SELECT attempt_id,evidence_id,provider,timestamp,input_hash,status,signature,result FROM attempts WHERE attempt_id=?',(attempt_id,)).fetchone()
        return self._receipt(row) if row else None

    def failures(self, signature: FailureSignature | None=None, input_hash: str | None=None) -> tuple[AttemptReceipt,...]:
        sql="SELECT attempt_id,evidence_id,provider,timestamp,input_hash,status,signature,result FROM attempts WHERE status<>'PASS'"
        args=[]
        if signature is not None:
            sql+=" AND signature=?"; args.append(signature.value)
        if input_hash is not None:
            sql+=" AND input_hash=?"; args.append(input_hash)
        return tuple(self._receipt(row) for row in self.db.execute(sql+" ORDER BY seq",args))

    def record_discovery(self, attempt_id: str, provider: str, timestamp: datetime,
                         query: DiscoveryQuery, result: DiscoveryResult) -> str:
        q=canonical(asdict(query)); r=canonical(asdict(result))
        qhash=digest(asdict(query))
        # Discovery outputs are source observations, not competing answers to a
        # target's verified mechanism; each provider/query has its own scope.
        entry=EvidenceEntry("",provider,result.derivation,timestamp,qhash,digest(asdict(result)),
            result.limitations,(),None,result.failure_signature,result.status,
            ObservationScope("discovery:"+provider,qhash))
        with self.db:
            eid=self._append(entry)
            values=(attempt_id,eid,provider,q,r)
            self.db.execute("INSERT OR IGNORE INTO discovery(attempt_id,evidence_id,provider,query,result) VALUES(?,?,?,?,?)",values)
            actual=self.db.execute("SELECT attempt_id,evidence_id,provider,query,result FROM discovery WHERE attempt_id=?",(attempt_id,)).fetchone()
            if actual!=values: raise ValueError("Discovery attempt identity reused")
        return eid

    def discovery_history(self, query: DiscoveryQuery) -> tuple[dict,...]:
        matches=[]
        for eid,provider,q,r in self.db.execute("SELECT evidence_id,provider,query,result FROM discovery ORDER BY seq"):
            prior=json.loads(q)
            if (prior["archetype"],prior["failure_signature"],prior["capability"].casefold())==(query.archetype.value,query.failure_signature.value,query.capability.casefold()):
                if not self.contradictions(eid):
                    matches.append({"evidence_id":eid,"provider":provider,"query":prior,"result":json.loads(r)})
        return tuple(matches)

    def record_dag_run(self, execution_id: str, payload: dict) -> None:
        data=canonical(payload)
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO dag_runs VALUES (?,?)",(execution_id,data))
            actual=self.db.execute("SELECT payload FROM dag_runs WHERE execution_id=?",(execution_id,)).fetchone()[0]
            if actual!=data: raise ValueError("DAG execution ID reused with different trace")

    def get_dag_run(self, execution_id: str) -> dict | None:
        row=self.db.execute("SELECT payload FROM dag_runs WHERE execution_id=?",(execution_id,)).fetchone()
        return json.loads(row[0]) if row else None
