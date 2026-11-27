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

    def test_completed_supervisor_replay_no_extra_invocations(self):
        order=[]
        with tempfile.TemporaryDirectory() as d,EvidenceStore(Path(d)/"e.db") as s,DossierWriter(Path(d)/"d.db") as w,LearningWriter(Path(d)/"l.db") as l:
            class Adapter(Fake):
                def invoke(self,inp):
                    order.append("analysis");return super().invoke(inp)
            graph={"cloud-api":[stage("A",providers=["a"])]}
            discovery={n:Discovery(n,False,order) for n in ("knowledge_retrieval","github_search","browser_research")}
            sup=Supervisor(DagEngine(graph,{"a":Adapter("a",True)},Matrix(),s,discovery),s,w,l)
            args=dict(input_hash="a"*64,execution_id="resume",timestamp=NOW,allowed_providers=frozenset({"a",*discovery}),objectives={"A":F})
            first=sup.run(FP,**args)
            count=len(order)
            again=sup.run(FP,**args)
            self.assertEqual(first.state,again.state)
            self.assertEqual(first.transitions,again.transitions)
            self.assertEqual(len(order),count)
    def test_transient_retry_does_not_repeat_independent_failure(self):
        from dataclasses import replace
        order=[]
        with tempfile.TemporaryDirectory() as d,EvidenceStore(Path(d)/"e.db") as s,DossierWriter(Path(d)/"d.db") as w,LearningWriter(Path(d)/"l.db") as l:
            class Retry(Fake):
                def invoke(self,inp):
                    order.append(self.name)
                    r=super().invoke(inp)
                    if self.name=="a" and order.count("a")==1:
                        return replace(r,status=ResultStatus.TIMEOUT,failure_signature=FailureSignature.NONE)
                    return r
            a,b=Retry("a",True),Retry("b",True)
            graph={"cloud-api":[stage("A",providers=["a"]),stage("B",providers=["b"])]}
            sup=Supervisor(DagEngine(graph,{"a":a,"b":b},Matrix(),s,{}),s,w,l)
            sup.run(FP,input_hash="a"*64,execution_id="retry",timestamp=NOW,allowed_providers=frozenset({"a","b"}),objectives={"A":F})
            self.assertEqual(order.count("a"),2)
            self.assertEqual(order.count("b"),1)

    def test_all_four_rungs_exhaust_before_discovery(self):
        order=[]
        with tempfile.TemporaryDirectory() as d,EvidenceStore(Path(d)/"e.db") as s,DossierWriter(Path(d)/"d.db") as w,LearningWriter(Path(d)/"l.db") as l:
            class Adapter(Fake):
                def invoke(self,inp):
                    order.append(self.name);return super().invoke(inp)
            names=["static","symbolic","live","blackbox"]
            row=stage("A")
            row.pop("providers")
            row["ladder"]=[{"rung":i+1,"paradigm":p,"providers":[names[i]],"trigger_signatures":[] if i==0 else ["UNKNOWN_PROTOCOL"]} for i,p in enumerate(("static","symbolic-emulation","live-instrumentation","black-box-discovery"))]
            discovery={n:Discovery(n,True,order) for n in ("knowledge_retrieval","github_search","browser_research")}
            obs=s.append(EvidenceEntry("","fixture",Derivation.OBSERVED,NOW,"a"*64,"b"*64,(),(),"synthetic",FailureSignature.NONE,ResultStatus.PASS,ObservationScope("behavior","a"*64)))
            sup=Supervisor(DagEngine({"cloud-api":[row]},{n:Adapter(n,True) for n in names},Matrix(),s,discovery),s,w,l)
            result=sup.run(FP,input_hash="a"*64,execution_id="ladder",timestamp=NOW,allowed_providers=frozenset((*names,*discovery)),objectives={"A":{**F,"evidence_ids":[obs]}})
            self.assertEqual(result.state,SupervisorState.ABSTAINED)
            self.assertEqual(result.abstentions[0].rungs_attempted,(1,2,3,4))
            self.assertEqual(order[:4],names)
            self.assertEqual(order[4:],["knowledge_retrieval","github_search","browser_research"])
            self.assertTrue(w.read("ladder:A")["construction_brief"])
    def test_bad_brief_escalates_without_write(self):
        order=[]
        with tempfile.TemporaryDirectory() as d,EvidenceStore(Path(d)/"e.db") as s,DossierWriter(Path(d)/"d.db") as w,LearningWriter(Path(d)/"l.db") as l:
            discovery={n:Discovery(n,True,order) for n in ("knowledge_retrieval","github_search","browser_research")}
            obs=s.append(EvidenceEntry("","fixture",Derivation.OBSERVED,NOW,"a"*64,"b"*64,(),(),"synthetic",FailureSignature.NONE,ResultStatus.PASS,ObservationScope("behavior","a"*64)))
            sup=Supervisor(DagEngine({"cloud-api":[stage("A",providers=["a"])]},{"a":Fake("a",True)},Matrix(),s,discovery),s,w,l)
            r=sup.run(FP,input_hash="a"*64,execution_id="bad",timestamp=NOW,allowed_providers=frozenset(("a",*discovery)),objectives={"A":{**F,"evidence_ids":[obs],"acceptance_test":{"method":"fake"}}})
            self.assertEqual(r.state,SupervisorState.ESCALATED)
            self.assertIsNone(w.read("bad:A"))
