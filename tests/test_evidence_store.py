import tempfile, unittest
from pathlib import Path
from datetime import datetime, timezone
from src.orchestrator.contracts import *
from src.orchestrator.evidence_store import EvidenceStore

NOW = datetime(2026,1,1,tzinfo=timezone.utc)
class EvidenceTests(unittest.TestCase):
    def test_restart_dedup_contradiction_and_failure(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/"evidence.sqlite"
            with EvidenceStore(path) as s:
                def entry(out):
                    return EvidenceEntry("", "fixture", Derivation.OBSERVED, NOW, "a"*64, out, (), (), None, FailureSignature.NONE, ResultStatus.PASS)
                a=s.append(entry("b"*64)); b=s.append(entry("c"*64))
                self.assertEqual(a,s.append(entry("b"*64)))
                r=ProviderResult(ResultStatus.TIMEOUT, FailureSignature.DISPATCHER_LOOP, (), (), Derivation.UNKNOWN, ("fixture timeout",), (), None, None)
                s.record_attempt("run:s:0:0", "fixture", NOW, "a"*64, r)
            with EvidenceStore(path) as s:
                self.assertEqual(s.get(a).output_artifact_hash,"b"*64)
                self.assertEqual(s.get(b).output_artifact_hash,"c"*64)
                self.assertEqual(s.contradictions(a),(b,))
                self.assertEqual(s.contradictions(b),(a,))
                self.assertEqual(len(s.failures(FailureSignature.DISPATCHER_LOOP,"a"*64)),1)
                self.assertEqual(s.failures(FailureSignature.DISPATCHER_LOOP)[0].status,ResultStatus.TIMEOUT)
