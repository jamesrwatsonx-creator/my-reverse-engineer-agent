import json, unittest
from pathlib import Path
from src.orchestrator.artifact_normalizer import normalize_fixture
from src.orchestrator.contracts import Derivation

RAW=json.loads((Path(__file__).parent/"fixtures/phase2.json").read_text())["raw"]
class NormalizerTests(unittest.TestCase):
    def test_all_shapes_and_raw(self):
        required={"function":("name","address","signature","body","body_kind"),"call_graph":("nodes","edges","unknown_edges"),"strings":("strings",),"network":("requests","responses","protocol","decoded"),"schema":("fields",)}
        for kind,raw in RAW.items():
            a=normalize_fixture(kind,raw,"fixture-evidence",Derivation.OBSERVED)
            self.assertEqual(json.loads(a.raw_blob),raw)
            self.assertEqual(a.provenance.evidence_id,"fixture-evidence")
            self.assertTrue(all(hasattr(a,x) for x in required[kind]))
            self.assertTrue(a.unrepresented_fields,kind)
        self.assertEqual(normalize_fixture("function",RAW["function"],"e",Derivation.OBSERVED).name,"example")
        self.assertEqual(normalize_fixture("schema",RAW["schema"],"e",Derivation.OBSERVED).fields[0].confidence,0.8)
