import argparse, importlib.util, json, pathlib, tempfile, unittest
P=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("workbench",P/"scripts/workbench.py")
w=importlib.util.module_from_spec(spec); spec.loader.exec_module(w)
class Tests(unittest.TestCase):
    def test_routing(self):
        ids={x["id"] for x in w.plan("web")}
        self.assertIn("playwright",ids); self.assertIn("rea",ids); self.assertNotIn("ghidra",ids)
        self.assertIn("ghidra",{x["id"] for x in w.plan("desktop")})
    def test_prepare(self):
        with tempfile.TemporaryDirectory() as d:
            r=pathlib.Path(d)
            for n in ("registry","templates"): (r/n).mkdir()
            for n in ("registry/tools.json","templates/LAUNCH.md"): (r/n).write_bytes((P/n).read_bytes())
            (r/"registry/index.json").write_text(json.dumps({"investigations":[{"slug":"existing"}]}))
            a=argparse.Namespace(slug="demo",name="Demo",target="https://example.com",kind="web",mode="research",goal="Understand")
            f=w.prepare(a,r); self.assertTrue(w.validate("demo",r)["valid"])
            self.assertFalse(w.load(f/"BRIEF.json")["build_authorized"])
            self.assertIn("PENDING",(f/"UPSTREAM_REVIEW.md").read_text())
            self.assertEqual(w.load(f/"GAP_REGISTER.json")["assessment"],"PENDING")
            self.assertEqual(w.load(f/"GAP_REGISTER.json")["target_slug"],"demo")
            self.assertEqual(w.load(f/"CONTEXT.json")["upstream_review"],"UPSTREAM_REVIEW.md")
            self.assertEqual(w.load(r/"registry/index.json")["investigations"][0]["slug"],"existing")
            with self.assertRaises(ValueError): w.prepare(a,r)
    def test_slug(self):
        for s in ("../escape","bad/name","UPPER",""):
            with self.assertRaises(ValueError): w.slug(s)
