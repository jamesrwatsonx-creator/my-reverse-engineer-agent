import pathlib,sys,unittest,json
P=pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0,str(P/"scripts"))
import resource_refresh as r
class RefreshTests(unittest.TestCase):
    def test_baseline_coverage(self):
        c=r.load(P/"registry/tools.json"); b=r.load(P/"registry/source_baseline.json")
        ids=[x["repository"].lower() for x in b["records"]]
        self.assertEqual(len(ids),len(set(ids)))
        self.assertTrue(set(r.sources(c)).issubset(set(ids)))
        self.assertEqual(b["counts"]["tracked"],len(ids))
    def test_fork_discovery_and_review_baseline(self):
        cat={"entries":[{"url":"https://github.com/owner/fork","related_sources":[]},{"url":"https://replit.com/"}]}
        previous={"records":[{"repository":"owner/fork","head_sha":"a"*40,"reviewed_sha":"b"*40}]}
        calls=[]
        def api(path):
            calls.append(path)
            if path=="repos/owner/fork": return {"full_name":"owner/fork","parent":{"full_name":"upstream/source"}},None
            if path=="repos/upstream/source": return {"full_name":"upstream/source"},None
            if "/commits?" in path: return [{"sha":"c"*40,"commit":{"message":"change"}}],None
            if "/releases/" in path: return {"tag_name":"v2"},None
            if "/compare/" in path: return {"status":"ahead","files":[{"filename":"README.md"}]},None
            return None,"BLOCKED"
        report=r.scan(cat,previous,api); self.assertEqual(report["counts"]["tracked"],2)
        row=report["records"][0]
        self.assertEqual(row["reviewed_sha"],"b"*40); self.assertTrue(row["head_changed"])
        self.assertIn("reviewed_comparison",row); self.assertEqual(row["runtime_status"],"NOT_RUN")
        self.assertIn("repos/owner/fork/compare/"+"b"*40+"..."+"c"*40,calls)
    def test_blocked_preserves_previous(self):
        cat={"entries":[{"url":"https://github.com/owner/fork"}]}
        prior={"records":[{"repository":"owner/fork","head_sha":"a"*40,"reviewed_sha":"b"*40}]}
        row=r.scan(cat,prior,lambda path:(None,"ACCESS"))["records"][0]
        self.assertEqual(row["head_status"],"BLOCKED")
        self.assertEqual(row["previous_observed_sha"],"a"*40)
        self.assertEqual(row["reviewed_sha"],"b"*40)
    def test_urls(self):
        self.assertIsNone(r.github_name("https://github.com/a/b/blob/main/README.md"))
        self.assertIsNone(r.github_name("https://example.com/a/b"))
