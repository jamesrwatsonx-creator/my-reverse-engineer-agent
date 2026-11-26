import base64,hashlib,json,tempfile,unittest
from datetime import timedelta
from pathlib import Path
from src.orchestrator.contracts import *
from src.orchestrator.evidence_store import EvidenceStore,digest
from src.orchestrator.executor import execute_stage,ExhaustedResult
from src.orchestrator.circuit_breaker import CircuitBreaker,CircuitState
from src.orchestrator.streaming_capture import capture_stream
from src.orchestrator.dag_engine import DagEngine,StageStatus,load_graphs
from test_dag_engine import FP,NOW,Matrix,Fake,stage

ROOT=Path(__file__).resolve().parents[1]
class AddendumTests(unittest.TestCase):
    def test_ladder_signature_and_no_escalation(self):
        for signature,expected in [(FailureSignature.UNKNOWN_PROTOCOL,True),(FailureSignature.PINNED,False)]:
            class First(Fake):
                def invoke(self,inp):
                    r=super().invoke(inp)
                    from dataclasses import replace
                    return replace(r,failure_signature=signature)
            a,b=First("a",True),Fake("b")
            row=stage("A")
            row.pop("providers")
            row["ladder"]=[{"rung":1,"paradigm":"static","providers":["a"],"trigger_signatures":[]},
                           {"rung":2,"paradigm":"symbolic-emulation","providers":["b"],"trigger_signatures":["UNKNOWN_PROTOCOL"]},
                           {"rung":3,"paradigm":"live-instrumentation","providers":[],"trigger_signatures":[]},
                           {"rung":4,"paradigm":"black-box-discovery","providers":[],"trigger_signatures":[]}]
            with tempfile.TemporaryDirectory() as d,EvidenceStore(Path(d)/"e.db") as s:
                r=DagEngine({"cloud-api":[row]},{"a":a,"b":b},Matrix(),s,{}).run(FP,input_hash="a"*64,execution_id="ladder",timestamp=NOW,allowed_providers=frozenset({"a","b"}))
                self.assertEqual(b.calls,int(expected))
                self.assertEqual(r.stages["A"].status,StageStatus.PASS if expected else StageStatus.EXHAUSTED)
                self.assertEqual([x.rung for x in r.stages["A"].attempts],[1,2] if expected else [1])
    def test_circuit_restart_and_half_open(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"e.db"
            a=Fake("a",True)
            st=Stage("A",Layer.STATIC,(),("a",),None,())
            def execute(s,n,ts):
                return execute_stage(st,FP,{"a":a},Matrix(),s,ProviderInput("A",(),{},"synthetic-fixture"),"a"*64,allowed_providers=frozenset({"a"}),execution_id=n,timestamp=ts,repair_stages={})
            with EvidenceStore(path) as s:
                for i in range(3):execute(s,str(i),NOW)
                self.assertEqual(CircuitBreaker(s).state("a").state,CircuitState.OPEN)
            with EvidenceStore(path) as s:
                r=execute(s,"skip",NOW)
                self.assertEqual(a.calls,3)
                self.assertIsNone(r.trace[0].receipt_id)
                self.assertEqual(len(s.failures()),3)
                a.fail=False
                execute(s,"probe",NOW+timedelta(seconds=61))
                self.assertEqual(a.calls,4)
                self.assertEqual(CircuitBreaker(s).state("a").state,CircuitState.CLOSED)
                self.assertIn("HALF_OPEN",[v["state"] for v in s.circuit_history("a")])
    def test_stream_large_payload_via_io_read(self):
        raw=(ROOT/"tests/fixtures/phase3-large-payload.txt").read_bytes()
        self.assertGreater(len(raw),4096)
        calls=[];offset=0
        def read(method,params):
            nonlocal offset
            calls.append(method)
            if method=="IO.close":return {}
            self.assertEqual(method,"IO.read")
            n=params["size"];chunk=raw[offset:offset+n];offset+=len(chunk)
            return {"data":base64.b64encode(chunk).decode(),"base64Encoded":True,"eof":offset==len(raw)}
        with tempfile.TemporaryDirectory() as d:
            ref=capture_stream(read,"fixture-stream",Path(d),chunk_bytes=1024,max_bytes=16384)
            self.assertEqual(ref.sha256,hashlib.sha256(raw).hexdigest())
            self.assertEqual(ref.size_bytes,len(raw))
            self.assertEqual((Path(d)/ref.relative_path).read_bytes(),raw)
            self.assertGreater(calls.count("IO.read"),1)
            self.assertEqual(calls[-1],"IO.close")
    def test_graph_streaming_path(self):
        graphs=load_graphs(ROOT/"routes/stages.json")
        row=next(x for x in graphs["cloud-api"] if x["id"]=="capture")
        self.assertEqual(row["streaming_capture"]["method"],"IO.read")
        self.assertTrue(all(len(s["ladder"])==4 and "providers" not in s for g in graphs.values() for s in g))
        raw=(ROOT/"tests/fixtures/phase3-large-payload.txt").read_bytes()
        offset=0
        def read(method,params):
            nonlocal offset
            if method=="IO.close":return {}
            chunk=raw[offset:offset+params["size"]];offset+=len(chunk)
            return {"data":chunk.decode(),"eof":offset==len(raw)}
        class Capture:
            name="rea"
            def invoke(self,inp):
                payload={"requests":[],"responses":[],"stream_handle":"fixture-stream","payload_size":len(raw)}
                a=Artifact("network-capture","fixture",digest(payload),"fixture-source",self.name,Derivation.OBSERVED,(),payload)
                return ProviderResult(ResultStatus.PASS,FailureSignature.NONE,(a,),(),Derivation.OBSERVED,(),(),None,None)
        with tempfile.TemporaryDirectory() as d,EvidenceStore(Path(d)/"e.db") as s:
            r=DagEngine({"cloud-api":[row,next(x for x in graphs["cloud-api"] if x["id"]=="discover-alternative-providers")]},{"rea":Capture()},Matrix(),s,{},stream_reader=read,artifact_directory=Path(d)/"blobs").run(FP,input_hash="a"*64,execution_id="stream",timestamp=NOW,allowed_providers=frozenset({"rea"}))
            self.assertEqual(r.stages["capture"].status,StageStatus.PASS)
            payload=r.stages["capture"].artifacts[0].payload
            self.assertNotIn("stream_handle",payload)
            self.assertEqual(payload["payload_ref"]["sha256"],hashlib.sha256(raw).hexdigest())
            self.assertNotIn(raw.decode(),json.dumps(s.get_dag_run("stream")))
