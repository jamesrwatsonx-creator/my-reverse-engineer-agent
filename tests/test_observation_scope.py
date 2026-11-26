import tempfile,unittest
from pathlib import Path
from datetime import datetime,timezone
from src.orchestrator.contracts import EvidenceEntry,ObservationScope,Derivation,ResultStatus,FailureSignature
from src.orchestrator.evidence_store import EvidenceStore

class ScopeTests(unittest.TestCase):
    def test_complementary_and_conflicting(self):
        with tempfile.TemporaryDirectory() as d,EvidenceStore(Path(d)/"e.db") as s:
            def entry(q,out):
                return EvidenceEntry("","fixture",Derivation.OBSERVED,datetime(2026,1,1,tzinfo=timezone.utc),"a"*64,out,(),(),None,FailureSignature.NONE,ResultStatus.PASS,ObservationScope(q,"a"*64))
            a=s.append(entry("function body","b"*64))
            b=s.append(entry("string table","c"*64))
            self.assertEqual(s.contradictions(a),())
            c=s.append(entry("function body","d"*64))
            self.assertEqual(s.contradictions(a),(c,))
            self.assertEqual(s.contradictions(c),(a,))
            self.assertEqual(s.contradictions(b),())
            self.assertEqual(a,s.append(entry("function body","b"*64)))
            self.assertEqual(s.get(a).observation_scope.question_asked,"function body")
