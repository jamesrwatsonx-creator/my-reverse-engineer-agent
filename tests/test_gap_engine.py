import pathlib,sys,unittest
P=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/"scripts"))
import gap_engine as g
class GapEngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.routes,cls.tools=g.load_routes()
    def sample(self):
        return {"schema_version":1,"target_slug":"demo","assessment":"ASSESSED","items":[{"id":"gap-1","feature_id":"f1","obligation_id":"o1","route_id":"business-logic","priority":"critical","limitation":"non-identifiable","allowed_scope":"Owned fixture only","knowledge_status":"UNKNOWN","functional_status":"PASS","evidence":["e1"],"hypotheses":["candidate independent rule"],"attempts":[{"result":"PASS","receipt":"fixture-result.json"}],"acceptance":"Scoped rule matches held-out cases","residual":"Original mechanism unknown","disposition":"RESOLVED","reason":"Independent alternative passed"}]}
    def test_routes(self):
        self.assertEqual(len(self.routes),19)
        self.assertTrue({"daikon","z3","tlaplus"}.issubset(set(self.routes["business-logic"]["tools"])))
        self.assertTrue({"kaitai-compiler","kaitai-formats"}.issubset(set(self.routes["binary-format"]["tools"])))
        self.assertTrue({"k6","locust"}.issubset(set(self.routes["performance"]["tools"])))
    def test_plan_is_not_execution(self):
        p=g.plan(self.sample(),self.routes,self.tools)
        self.assertFalse(p["tools_executed"]);self.assertFalse(p["target_accessed"])
        self.assertEqual(p["plans"][0]["route_id"],"business-logic")
    def test_independent_pass_keeps_unknown(self):
        a=g.audit(self.sample(),self.routes,"demo")
        self.assertTrue(a["valid"]);self.assertFalse(a["functional_equivalence_certified"])
        self.assertEqual(a["unresolved"][0]["knowledge_status"],"UNKNOWN")
    def test_missing_receipt(self):
        x=self.sample();x["items"][0]["attempts"]=[]
        self.assertFalse(g.audit(x,self.routes)["valid"])
    def test_blocked_is_not_pass(self):
        x=self.sample();x["items"][0].update(functional_status="BLOCKED",knowledge_status="BLOCKED",disposition="BLOCKED")
        a=g.audit(x,self.routes);self.assertTrue(a["valid"]);self.assertEqual(len(a["unresolved"]),1)
    def test_unresolved_critical_and_pending(self):
        x=self.sample();x["items"][0].update(functional_status="NOT_RUN",disposition="OPEN")
        self.assertFalse(g.audit(x,self.routes)["valid"])
        self.assertFalse(g.audit({"schema_version":1,"assessment":"PENDING","items":[]},self.routes)["valid"])
    def test_no_gaps_requires_reason(self):
        x={"schema_version":1,"target_slug":"demo","assessment":"NO_GAPS","items":[]}
        self.assertFalse(g.audit(x,self.routes)["valid"])
        x["no_gaps_reason"]="Scope is limited to a documented interface; no open gaps identified after review."
        self.assertTrue(g.audit(x,self.routes)["valid"])
