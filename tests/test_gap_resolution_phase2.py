import pathlib,sys,tempfile,unittest
from datetime import datetime,timezone
P=pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0,str(P/"scripts"))
import gap_engine as g
from src.orchestrator.contracts import *
from src.orchestrator.evidence_store import EvidenceStore

def sample():
    return {"schema_version":1,"target_slug":"demo","assessment":"ASSESSED","items":[{"id":"g","feature_id":"f","obligation_id":"o","route_id":"business-logic","priority":"normal","limitation":"missing-evidence","allowed_scope":"synthetic","knowledge_status":"DOCUMENTED","functional_status":"NOT_RUN","evidence":["old"],"hypotheses":[],"attempts":[],"acceptance":"fixture","residual":"unverified response","disposition":"RESOLVED","reason":"documented"}]}
class ResolutionTests(unittest.TestCase):
    def test_provenance_not_closure(self):
        a=g.audit(sample(),g.load_routes()[0])
        self.assertFalse(a["valid"])
        self.assertEqual(a["unresolved"][0]["knowledge_status"],"DOCUMENTED")
        self.assertEqual(a["unresolved"][0]["disposition"],"OPEN")
        self.assertTrue(a["unresolved"][0]["reason"])
    def test_verified_or_yellow(self):
        with tempfile.TemporaryDirectory() as d,EvidenceStore(pathlib.Path(d)/"e.sqlite") as s:
            x=sample(); item=x["items"][0]
            eid=s.append(EvidenceEntry("","fixture",Derivation.OBSERVED,datetime(2026,1,1,tzinfo=timezone.utc),"a"*64,"b"*64,(),(), "byte_match",FailureSignature.NONE,ResultStatus.PASS))
            item.update(evidence=[eid],functional_status="PASS",attempts=[{"result":"PASS","receipt":eid}])
            self.assertTrue(g.audit(x,g.load_routes()[0],evidence_store=s)["valid"])
            item.update(functional_status="NOT_RUN",attempts=[],verification={"color":"YELLOW","evidence_ids":[eid],"residual_uncertainty":["response timing interface"]})
            a=g.audit(x,g.load_routes()[0],evidence_store=s)
            self.assertTrue(a["valid"]);self.assertTrue(a["unresolved"])
            item["verification"]["residual_uncertainty"]=[]
            item["evidence"]=["missing"]
            self.assertFalse(g.audit(x,g.load_routes()[0],evidence_store=s)["valid"])

    def test_contradicted_receipt_does_not_close(self):
        with tempfile.TemporaryDirectory() as d,EvidenceStore(pathlib.Path(d)/"e.sqlite") as s:
            x=sample(); item=x["items"][0]
            now=datetime(2026,1,1,tzinfo=timezone.utc)
            eid=s.append(EvidenceEntry("","fixture",Derivation.OBSERVED,now,"a"*64,"b"*64,(),(),"byte_match",FailureSignature.NONE,ResultStatus.PASS))
            s.append(EvidenceEntry("","fixture",Derivation.OBSERVED,now,"a"*64,"c"*64,(),(),None,FailureSignature.NONE,ResultStatus.PASS))
            item.update(evidence=[eid],functional_status="PASS",attempts=[{"result":"PASS","receipt":eid}])
            a=g.audit(x,g.load_routes()[0],evidence_store=s)
            self.assertFalse(a["valid"])
            self.assertEqual(a["unresolved"][0]["disposition"],"OPEN")
