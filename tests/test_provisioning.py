import json,subprocess,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class ProvisionTests(unittest.TestCase):
    def test_manifest_covers_graph(self):
        graphs=json.loads((ROOT/"routes/stages.json").read_text())["graphs"]
        manifest=json.loads((ROOT/"routes/provisioning.json").read_text())
        expected={p for stages in graphs.values() for s in stages for rung in s["ladder"] for p in rung["providers"]}
        self.assertEqual(set(manifest),expected)
        self.assertTrue(all(v["install"] and v["host"] and v["tested_version"] for v in manifest.values()))
        p=subprocess.run(["bash",str(ROOT/"scripts/provision-check.sh"),"--manifest-only"],capture_output=True,text=True,check=True)
        self.assertIn("github_search",p.stdout)
