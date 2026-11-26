import json,tempfile,unittest
from pathlib import Path
from datetime import datetime,timezone
from src.orchestrator.contracts import *
from src.orchestrator.evidence_store import EvidenceStore,digest
from src.orchestrator.dag_engine import DagEngine,StageStatus,load_graphs
from src.providers.browser_research_provider import BrowserResearchProvider
from src.providers.knowledge_retrieval_provider import KnowledgeRetrievalProvider
F=json.loads((Path(__file__).parent/"fixtures/phase3.json").read_text())
NOW=datetime(2026,1,1,tzinfo=timezone.utc)
FP=TargetFingerprint(Archetype.CLOUD_API,"fixture",None,None,(),(),None,1,False,True)
class Matrix:
    def is_available(self,n):return True
    def why_unavailable(self,n):return ""
class Fake:
    def __init__(self,name,fail=False,body="pseudocode"):self.name=name;self.fail=fail;self.body=body;self.calls=0
    def invoke(self,inp):
        self.calls+=1
        payload={"body_kind":self.body,"body":"fixture"}
        a=Artifact("function","fixture",digest(payload),"fixture-source",self.name,Derivation.OBSERVED,(),payload)
        return ProviderResult(ResultStatus.FAIL if self.fail else ResultStatus.PASS,FailureSignature.UNKNOWN_PROTOCOL if self.fail else FailureSignature.NONE,() if self.fail else (a,),(),Derivation.OBSERVED,("fixture",),(),None,None)
def stage(i,pre=(),kind="analysis",providers=None,contract=None,on_fail=()):
    return {"id":i,"layer":"static","preconditions":list(pre),"providers":providers or [i],"input_contract":contract or [],"output_contract":[{"artifact_type":"function","required_fields":{"body":None}}] if kind=="analysis" else [{"artifact_type":"discovery-candidates","required_fields":{"candidates":None}}],"gate":"fixture-contract","kind":kind,"on_fail":list(on_fail),"capability":"rate limiting middleware"}
class DagTests(unittest.TestCase):
    def run_graph(self,stages,providers,unresolved=None):
        with tempfile.TemporaryDirectory() as d,EvidenceStore(Path(d)/"e.db") as s:
            discovery={"browser_research":BrowserResearchProvider(capture=lambda q:F["har"]),"knowledge_retrieval":KnowledgeRetrievalProvider(s,web_search=lambda q:F["web"])}
            graph={"cloud-api":stages}
            return DagEngine(graph,providers,Matrix(),s,discovery).run(FP,input_hash="a"*64,execution_id="fixture",timestamp=NOW,allowed_providers=frozenset((*providers,*discovery)),unresolved=unresolved or {})
    def test_independent_stage_continues(self):
        a,b,c=Fake("A",True),Fake("B"),Fake("C")
        r=self.run_graph([stage("B",("A",)),stage("C"),stage("A")],{"A":a,"B":b,"C":c})
        self.assertEqual(r.stages["A"].status,StageStatus.EXHAUSTED)
        self.assertEqual(r.stages["B"].status,StageStatus.NOT_READY)
        self.assertEqual(r.stages["C"].status,StageStatus.PASS)
        self.assertEqual(b.calls,0);self.assertEqual(c.calls,1)
        self.assertEqual(set(r.trace),{"A","B","C"})
        self.assertTrue(r.stages["A"].exhaustion_receipts)
    def test_wrong_body_contract(self):
        a,b=Fake("A"),Fake("B")
        r=self.run_graph([stage("A"),stage("B",("A",),contract=[{"artifact_type":"function","required_fields":{"body_kind":"assembly","body":None}}])],{"A":a,"B":b})
        self.assertEqual(r.stages["B"].status,StageStatus.UNSATISFIED_INPUT)
        self.assertEqual(b.calls,0)
        self.assertIn("body_kind",str(r.stages["B"].unsatisfied))
    def test_discovery_triggers(self):
        alt=stage("discover-alternative-providers",kind="discovery",providers=["knowledge_retrieval"])
        alt["trigger"]="EXHAUSTED"
        brief=stage("discover-construction-brief",kind="discovery",providers=["browser_research","knowledge_retrieval"])
        brief["trigger"]="UNRESOLVED"
        a=stage("A",on_fail=["discover-alternative-providers","discover-construction-brief"])
        r=self.run_graph([a,alt,brief],{"A":Fake("A",True)},{"A":{"observable_behavior":"rate limiting response","undetermined_mechanism":"server policy","evidence_ids":["fixture-observation"]}})
        for name in ("discover-alternative-providers@A","discover-construction-brief@A"):
            x=r.stages[name]
            self.assertEqual(x.status,StageStatus.PASS)
            self.assertTrue(x.candidates)
            self.assertTrue(x.trigger_receipts)
            self.assertTrue(x.candidates[0].verification_required)
    def test_graphs_and_cycle(self):
        graphs=load_graphs(Path(__file__).resolve().parents[1]/"routes/stages.json")
        self.assertEqual(set(graphs),{"cloud-api","packed-binary"})
        with self.assertRaises(ValueError):self.run_graph([stage("A",("B",)),stage("B",("A",))],{})
