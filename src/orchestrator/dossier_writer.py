"""Separate, typed dossier and learning destinations; no raw trace export."""
from __future__ import annotations
import json,sqlite3
from pathlib import Path
from .evidence_store import canonical

class DossierError(ValueError):pass

def _keys(value,keys):
    if not isinstance(value,dict) or set(value)!=set(keys.split()):
        raise DossierError("Unexpected or missing fields: "+keys)
def _str(value):
    if not isinstance(value,str) or not value.strip():raise DossierError("Nonempty text required")
def _refs(value):
    if not isinstance(value,list) or not value:raise DossierError("Evidence references required")
    for x in value:_str(x)
def _brief(b):
    _keys(b,"observable_behavior undetermined_mechanism approximation supporting_evidence implementation_path acceptance_test")
    _str(b["observable_behavior"]);_str(b["undetermined_mechanism"]);_refs(b["supporting_evidence"])
    a=b["approximation"];_keys(a,"description provenance_tier");_str(a["description"])
    if type(a["provenance_tier"]) is not int or a["provenance_tier"] not in {3,4}:raise DossierError("Approximation must be Tier 3/4")
    paths=b["implementation_path"]
    if not isinstance(paths,list) or not paths:raise DossierError("Implementation candidates required")
    for p in paths:
        _keys(p,"candidate_id canonical_path verification_required license")
        for v in p.values():_str(v)
    t=b["acceptance_test"];_keys(t,"input expected method")
    for v in t.values():_str(v)
    if t["method"] not in {"byte_match","oracle_harness","behavioral_equivalence"}:raise DossierError("Named future verification method required")

class _Partition:
    partition=None
    def __init__(self,path):
        self.path=Path(path).resolve()
        self.db=sqlite3.connect(str(self.path))
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS partition_identity (kind TEXT PRIMARY KEY);
        CREATE TABLE IF NOT EXISTS records (id TEXT PRIMARY KEY,payload TEXT NOT NULL);
        CREATE TRIGGER IF NOT EXISTS immutable_records_update BEFORE UPDATE ON records BEGIN SELECT RAISE(ABORT,'append-only'); END;
        CREATE TRIGGER IF NOT EXISTS immutable_records_delete BEFORE DELETE ON records BEGIN SELECT RAISE(ABORT,'append-only'); END;
        """)
        with self.db:
            row=self.db.execute("SELECT kind FROM partition_identity").fetchone()
            if row and row[0]!=self.partition:
                self.db.close();raise DossierError("Partition mismatch")
            self.db.execute("INSERT OR IGNORE INTO partition_identity VALUES (?)",(self.partition,))
    def __enter__(self):return self
    def __exit__(self,*_):self.db.close()
    def read(self,ident):
        r=self.db.execute("SELECT payload FROM records WHERE id=?",(ident,)).fetchone()
        return json.loads(r[0]) if r else None
    def records(self):
        return tuple((k,json.loads(v)) for k,v in self.db.execute("SELECT id,payload FROM records ORDER BY id"))
    def _write(self,ident,entry):
        _str(ident);data=canonical(entry)
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO records VALUES (?,?)",(ident,data))
            if self.db.execute("SELECT payload FROM records WHERE id=?",(ident,)).fetchone()[0]!=data:
                raise DossierError("Record identity reused with different content")
        return True

class DossierWriter(_Partition):
    partition="dossier"
    def write(self,ident,entry):
        if not isinstance(entry,dict):raise DossierError("Dossier entry required")
        kind=entry.get("kind")
        if kind=="unresolved":
            _keys(entry,"kind gap_id status construction_brief no_brief_reason")
            _str(entry["gap_id"])
            if entry["status"]!="ABSTAINED":raise DossierError("Unresolved entry must be ABSTAINED")
            brief,reason=entry["construction_brief"],entry["no_brief_reason"]
            if (brief is None)==(reason is None):raise DossierError("Exactly one construction brief or no_brief_reason required")
            if brief is not None:_brief(brief)
            else:_str(reason)
        elif kind=="fixture_result":
            _keys(entry,"kind gap_id status verification_method residual_uncertainty evidence_ids")
            _str(entry["gap_id"]);_refs(entry["evidence_ids"]);_refs(entry["residual_uncertainty"])
            if entry["status"]!="YELLOW" or entry["verification_method"]!="synthetic":raise DossierError("Only conditional synthetic fixture results supported")
        else:raise DossierError("Not a dossier record type")
        return self._write(ident,entry)

class LearningWriter(_Partition):
    partition="learning"
    def write(self,ident,entry):
        _keys(entry,"kind data")
        if entry["kind"] not in {"failure_receipt","contradiction","discovery_query","strategy_outcome","abstention","transition"}:
            raise DossierError("Not a learning record type")
        data=entry["data"]
        if not isinstance(data,dict):raise DossierError("Learning data must be object")
        forbidden={"construction_brief","verified_result","verified_results","implementation_path","acceptance_test"}
        def inspect(value):
            if isinstance(value,dict):
                if forbidden.intersection(value):raise DossierError("Dossier contents cannot enter learning partition")
                for x in value.values():inspect(x)
            elif isinstance(value,(list,tuple)):
                for x in value:inspect(x)
        inspect(data)
        return self._write(ident,entry)
    def strategies(self,archetype,signature,capability,stage_id):
        out=[]
        for ident,entry in self.records():
            d=entry["data"]
            if entry["kind"]=="strategy_outcome" and all(d.get(k)==v for k,v in {
                "archetype":archetype,"failure_signature":signature,"capability":capability,"stage_id":stage_id,"outcome":"PASS"}.items()):
                out.append((ident,d))
        return tuple(out)
