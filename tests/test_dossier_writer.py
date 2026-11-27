import tempfile,unittest
from pathlib import Path
from src.orchestrator.dossier_writer import DossierWriter,LearningWriter,DossierError
from src.orchestrator.contracts import AbstentionRecord,SupervisorDecision,SupervisorAction,Archetype
from dataclasses import fields,MISSING

class DossierTests(unittest.TestCase):
    def test_partition_and_validation(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            with DossierWriter(p/"dossier.db") as w, LearningWriter(p/"learning.db") as l:
                entry={"kind":"unresolved","gap_id":"g","status":"ABSTAINED","construction_brief":None,"no_brief_reason":None}
                with self.assertRaises(DossierError):w.write("g",entry)
                with self.assertRaises(DossierError):w.write("f",{"kind":"failure_receipt","data":{}})
                l.write("f",{"kind":"failure_receipt","data":{"signature":"PACKED"}})
                brief={"observable_behavior":"fixture behavior","undetermined_mechanism":"unknown policy","approximation":{"description":"independent approach","provenance_tier":4},"supporting_evidence":["e1"],"implementation_path":[{"candidate_id":"c1","canonical_path":"fixture/repo","verification_required":"held-out fixture","license":"MIT"}],"acceptance_test":{"input":"fixture","expected":"status","method":"behavioral_equivalence"}}
                entry["construction_brief"]=brief
                self.assertTrue(w.write("g",entry))
                self.assertEqual(w.read("g"),entry)
                with self.assertRaises(DossierError):l.write("brief",entry)
                with self.assertRaises(DossierError):w.write("leak",{**entry,"failure_receipts":[]})
    def test_abstention_contract(self):
        for cls in (AbstentionRecord,SupervisorDecision):
            self.assertTrue(all(f.default is MISSING and f.default_factory is MISSING for f in fields(cls)))
        args=(Archetype.CLOUD_API,(),(),(),(),())
        with self.assertRaises(ValueError):AbstentionRecord(*args,None,None,("evidence",))
        with self.assertRaises(ValueError):AbstentionRecord(*args,"brief","reason",("evidence",))
        self.assertEqual(AbstentionRecord(*args,None,"reason",("evidence",)).no_brief_reason,"reason")
