import json,subprocess,sys,tempfile,unittest
from pathlib import Path
from src.orchestrator.evidence_store import EvidenceStore
from src.orchestrator.durability import DurableExecution
ROOT=Path(__file__).resolve().parents[1]
class FaultTests(unittest.TestCase):
    def fault(self,scenario):
        with tempfile.TemporaryDirectory() as d:
            args=[sys.executable,str(ROOT/"tests/fixtures/phase4_fault_worker.py"),d,scenario]
            first=subprocess.run(args+["kill"],cwd=ROOT,capture_output=True,text=True)
            self.assertEqual(first.returncode,-9,first.stdout+first.stderr)
            second=subprocess.run(args+["resume"],cwd=ROOT,capture_output=True,text=True)
            self.assertEqual(second.returncode,0,second.stdout+second.stderr)
            return json.loads(second.stdout)
    def test_completed_outbox_before_evidence(self):
        r=self.fault("completed")
        self.assertEqual(r["calls"],1);self.assertEqual(r["receipts"],1);self.assertEqual(r["status"],"PASS")
    def test_mid_invocation_incomplete(self):
        r=self.fault("incomplete")
        self.assertEqual(r["calls"],1);self.assertEqual(r["status"],"INCOMPLETE");self.assertTrue(r["attempt_hash"])
    def test_evidence_before_circuit(self):
        r=self.fault("circuit")
        self.assertEqual(r["calls"],1);self.assertEqual(r["receipts"],1);self.assertEqual(r["circuit_failures"],1)
    def test_stage_before_downstream(self):
        r=self.fault("stage")
        self.assertEqual(r["calls"],2);self.assertEqual(r["stages"],["A","B"])
    def test_discovery_mid_invocation(self):
        r=self.fault("discovery")
        self.assertEqual(r["calls"],2);self.assertEqual(len(set(r["keys"])),1);self.assertIn("INCOMPLETE",r["events"]);self.assertEqual(r["receipts"],1)
