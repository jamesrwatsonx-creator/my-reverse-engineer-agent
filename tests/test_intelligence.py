import argparse, copy, json, pathlib, sys, tempfile, unittest
P=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(P/"scripts"))
import workbench as w
import intelligence as i
def comparison():
    a={"id":"old","context_id":"ctx","fixture_id":"fixture","gates":{k:"PASS" for k in i.GATES},"metrics":{"latency":{"value":100,"unit":"ms","direction":"min","tolerance":5,"n":10},"cost":{"value":2,"unit":"USD","direction":"min","tolerance":0.1,"n":10}}}
    b=copy.deepcopy(a); b["id"]="new"; b["metrics"]["latency"]["value"]=80
    return {"context_id":"ctx","fixture_id":"fixture","baseline":a,"challenger":b}
class IntelligenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup); self.root=pathlib.Path(self.tmp.name)
        for n in ("registry","templates","knowledge"): (self.root/n).mkdir()
        for n in ("registry/tools.json","templates/LAUNCH.md","knowledge/index.json"): (self.root/n).write_bytes((P/n).read_bytes())
        w.dump(self.root/"registry/index.json",{"investigations":[]})
        self.f=w.prepare(argparse.Namespace(slug="demo",name="Demo",target="https://example.com",kind="web",mode="research",goal="Test"),self.root)
    def r(self,p): return {"path":str(p.relative_to(self.root)),"sha256":i.sha(p)}
    def ready(self):
        ctx=w.load(self.f/"CONTEXT.json")
        for k in ("instruction_revision","tool_registry_revision","knowledge_revision"): ctx[k]="a"*40
        w.dump(self.f/"CONTEXT.json",ctx)
    def test_pending_and_no_change(self):
        self.assertFalse(i.audit("demo",self.root)["valid"]); self.ready()
        d=w.load(self.f/"LEARNING_DELTA.json"); d.update(assessment="NO_CHANGE",no_change_reason="No verified transferable evidence")
        w.dump(self.f/"LEARNING_DELTA.json",d); self.assertTrue(i.audit("demo",self.root)["valid"])
    def test_comparisons(self):
        c=comparison(); self.assertEqual(i.compare(c)["result"],"DOMINATES")
        c["challenger"]["metrics"]["cost"]["value"]=3; self.assertEqual(i.compare(c)["result"],"TRADEOFF")
        c["challenger"]["fixture_id"]="different"; self.assertEqual(i.compare(c)["result"],"INCOMPARABLE")
        c=comparison(); c["challenger"]["gates"]["security"]="FAIL"; self.assertEqual(i.compare(c)["result"],"INCOMPARABLE")
        c=comparison(); c["challenger"]["metrics"]["latency"]["value"]=98; self.assertEqual(i.compare(c)["result"],"TIE")
    def test_review_requires_receipts_and_independence(self):
        self.ready()
        f=self.f/"fixture.txt"; f.write_text("Synthetic test receipt")
        rev=self.f/"review.txt"; rev.write_text("Synthetic independent review")
        comp=self.f/"compare.json"; w.dump(comp,comparison())
        x={"id":"retry-variant","capability_id":"webhook-retry","kind":"VARIANT","proposer":"agent-a","summary":"Webhook retry pattern","context":"synthetic fixture","limitations":"not production","evidence":[self.r(f)],"fixture_receipt":self.r(f),"fixture_result":"PASS","license_review":"PASS","privacy_review":"PASS","comparison":self.r(comp),"claims_improvement":True}
        d=w.load(self.f/"LEARNING_DELTA.json"); d.update(assessment="ASSESSED",items=[x]); w.dump(self.f/"LEARNING_DELTA.json",d)
        self.assertTrue(i.audit("demo",self.root)["valid"])
        with self.assertRaises(ValueError): i.review("demo",x["id"],"agent-a","validated","test",str(rev.relative_to(self.root)),self.root)
        row=i.review("demo",x["id"],"agent-b","validated","test",str(rev.relative_to(self.root)),self.root)
        self.assertEqual(row["status"],"validated"); self.assertEqual(len(i.search("webhook retry",self.root)),1)
        f.write_text("changed")
        self.assertFalse(i.audit("demo",self.root)["valid"])
    def test_package_integrity(self):
        for n in i.PACKAGE: (self.f/"handoff"/n).write_text("Synthetic fixture "+n)
        self.assertTrue(i.make_package("demo","owner/research","b"*40,"owner/product","1","PARTIAL","test approval",self.root)["valid"])
        (self.f/"handoff"/"GAPS.md").write_text("changed")
        with self.assertRaises(ValueError): i.verify_package("demo",self.root)
    def test_path_escape(self):
        with self.assertRaises(ValueError): i.safe_file(self.root,"../outside")
