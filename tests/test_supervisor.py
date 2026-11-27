import json,tempfile,unittest
from pathlib import Path
from src.orchestrator.contracts import *
from src.orchestrator.dossier_writer import DossierWriter,LearningWriter
from src.orchestrator.supervisor import Supervisor,SupervisorState
from src.orchestrator.dag_engine import DagEngine
from src.orchestrator.evidence_store import EvidenceStore
from src.providers.knowledge_retrieval_provider import KnowledgeRetrievalProvider
from test_dag_engine import FP,NOW,Matrix,Fake,stage
F=json.loads((Path(__file__).parent/"fixtures/phase4.json").read_text())

class Discovery:
    def __init__(self,name,candidates,order):self.name=name;self.candidates=candidates;self.order=order
    def health_check(self):return True
    def invoke(self,q):
        self.order.append(self.name)
        c=DiscoveryCandidate("https://fixture.invalid/reference",q.capability,"UNKNOWN",MaintenanceSignal(None,None,None),None,"Controlled fixture replay",Derivation.INFERRED,"unknown",False,"fixture",4)
        return DiscoveryResult(ResultStatus.PASS if self.candidates else ResultStatus.EMPTY,FailureSignature.NONE,(c,) if self.candidates else (),(),Derivation.INFERRED,(),())

class SupervisorTests(unittest.TestCase):
    def scenario(self,candidates,prior=False,block=False):
        order=[]
        with tempfile.TemporaryDirectory() as d,EvidenceStore(Path(d)/"e.db") as s,DossierWriter(Path(d)/"d.db") as w,LearningWriter(Path(d)/"l.db") as l:
            class Adapter(Fake):
                def invoke(self,inp):
                    order.append("analysis:"+str(inp.parameters.get("mode","initial")))
                    self.fail=inp.parameters.get("mode")!="fixture-repair"
                    return super().invoke(inp)
            a=Adapter("a",True)
            graph={"cloud-api":[stage("A",providers=["a"])]}
            discovery={n:Discovery(n,candidates if n!="knowledge_retrieval" else False,order) for n in ("knowledge_retrieval","github_search","browser_research")}
            obs=s.append(EvidenceEntry("","fixture",Derivation.OBSERVED,NOW,"a"*64,"b"*64,(),(),"synthetic",FailureSignature.NONE,ResultStatus.PASS,ObservationScope("behavior","a"*64)))
            if prior:
                l.write("strategy",{"kind":"strategy_outcome","data":{"archetype":"cloud-api","failure_signature":"UNKNOWN_PROTOCOL","capability":F["capability"],"stage_id":"A","provider":"a","configuration":F["configuration"],"outcome":"PASS","evidence_ids":[obs]}})
            sup=Supervisor(DagEngine(graph,{"a":a},Matrix(),s,discovery),s,w,l)
            result=sup.run(FP,input_hash="a"*64,execution_id="sup",timestamp=NOW,allowed_providers=frozenset({"a",*discovery}),objectives={"A":{**F,"evidence_ids":[obs],"blocks_downstream":block}})
            return result,w.read("sup:A"),order
    def test_abstention_with_brief(self):
        r,d,order=self.scenario(True)
        self.assertEqual(r.state,SupervisorState.ABSTAINED)
        self.assertIn(SupervisorState.DISCOVERING,r.transitions)
        self.assertTrue(d["construction_brief"]["implementation_path"])
        self.assertTrue(r.abstentions[0].providers_attempted)
        self.assertTrue(r.abstentions[0].discovery_queries_issued)
        self.assertEqual(order,["analysis:initial","knowledge_retrieval","github_search","browser_research"])
    def test_empty_and_blocking(self):
        r,d,_=self.scenario(False)
        self.assertEqual(r.state,SupervisorState.ABSTAINED)
        self.assertTrue(d["no_brief_reason"])
        self.assertTrue(r.abstentions[0].required_to_proceed)
        self.assertEqual(self.scenario(False,block=True)[0].state,SupervisorState.ESCALATED)
    def test_prior_strategy_before_external(self):
        r,d,order=self.scenario(True,prior=True)
        self.assertEqual(order,["analysis:initial","knowledge_retrieval","analysis:fixture-repair"])
        self.assertIn(SupervisorState.REPAIRING,r.transitions)
        self.assertEqual(r.state,SupervisorState.CLOSED)
        self.assertEqual(r.verification_method,"synthetic")
