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
            if unresolved:
                obs=s.append(EvidenceEntry("","fixture",Derivation.OBSERVED,NOW,"a"*64,"b"*64,(),(),"oracle_harness",FailureSignature.NONE,ResultStatus.PASS,ObservationScope("observable behavior","a"*64)))
                unresolved={k:{**v,"evidence_ids":[obs] if v.get("evidence_ids")==["fixture-observation"] else v.get("evidence_ids",[])} for k,v in unresolved.items()}
            result=DagEngine(graph,providers,Matrix(),s,discovery).run(FP,input_hash="a"*64,execution_id="fixture",timestamp=NOW,allowed_providers=frozenset((*providers,*discovery)),unresolved=unresolved or {})
            self.assertEqual(s.get_dag_run("fixture")["trace"],list(result.trace))
            return result
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

    def test_discovery_uses_sorted_ready_queue_and_rejects_missing_observation(self):
        alt=stage("discover-alternative-providers",kind="discovery",providers=["knowledge_retrieval"])
        alt["trigger"]="EXHAUSTED"
        brief=stage("discover-construction-brief",kind="discovery",providers=["browser_research"])
        brief["trigger"]="UNRESOLVED"
        a=stage("A",on_fail=["discover-alternative-providers","discover-construction-brief"])
        r=self.run_graph([a,stage("B"),alt,brief],{"A":Fake("A",True),"B":Fake("B")},{"A":{"observable_behavior":"rate limiting","undetermined_mechanism":"unknown","evidence_ids":["missing"]}})
        self.assertEqual(r.stages["discover-construction-brief@A"].status,StageStatus.UNSATISFIED_INPUT)
        self.assertLess(r.trace.index("B"),r.trace.index("discover-alternative-providers@A"))

    def test_authored_graphs_all_stages_with_synthetic_adapters(self):
        graphs=load_graphs(Path(__file__).resolve().parents[1]/"routes/stages.json")
        for archetype,rows in graphs.items():
            outputs={s["id"]:s["output_contract"] for s in rows if s["kind"]=="analysis"}
            class Adapter:
                def __init__(self,name): self.name=name
                def invoke(self,inp):
                    arts=[]
                    for spec in outputs[inp.stage_id]:
                        payload={k:("fixture" if v is None else v) for k,v in spec["required_fields"].items()}
                        arts.append(Artifact(spec["artifact_type"],"fixture",digest(payload),"fixture-source",self.name,Derivation.OBSERVED,(),payload))
                    return ProviderResult(ResultStatus.PASS,FailureSignature.NONE,tuple(arts),(),Derivation.OBSERVED,("synthetic shape only",),(),None,None)
            names={p for s in rows if s["kind"]=="analysis" for rung in s["ladder"] for p in rung["providers"]}
            providers={n:Adapter(n) for n in names}
            fp=TargetFingerprint(Archetype(archetype),"fixture",None,None,(),(),None,1,False,True)
            with tempfile.TemporaryDirectory() as d,EvidenceStore(Path(d)/"e.db") as s:
                r=DagEngine(graphs,providers,Matrix(),s,{}).run(fp,input_hash="a"*64,execution_id=archetype,timestamp=NOW,allowed_providers=frozenset(names))
                self.assertTrue(all(r.stages[k].status is StageStatus.PASS for k in outputs))
                self.assertTrue(all(r.stages[k].status is StageStatus.SKIPPED for k in r.stages if k not in outputs))
