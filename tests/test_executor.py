import hashlib,json,tempfile,unittest
from pathlib import Path
from datetime import datetime,timezone
from src.orchestrator.contracts import *
from src.orchestrator.evidence_store import EvidenceStore
from src.orchestrator.executor import execute_stage, ExhaustedResult, ExecutionPass

F=json.loads((Path(__file__).parent/"fixtures/phase2.json").read_text())
NOW=datetime(2026,1,1,tzinfo=timezone.utc)
H=hashlib.sha256(F["input"].encode()).hexdigest()
FP=TargetFingerprint(Archetype(F["fingerprint"]["archetype"]),"synthetic","fixture",None,(),(),"fixture",1,False,True)
STAGE=Stage(F["stage"]["id"],Layer.STATIC,(),tuple(F["stage"]["providers"]),None,())
class Matrix:
    def __init__(self,skip=()): self.skip=skip
    def is_available(self,name): return name not in self.skip
    def why_unavailable(self,name): return "synthetic host unsupported"
class Fake:
    def __init__(self,name,status,signature):
        self.name=name; self.status=status; self.signature=signature
    def invoke(self,inp):
        artifacts=(Artifact("function","fixture","b"*64,"raw-id",self.name,Derivation.OBSERVED,()),) if self.status==ResultStatus.PASS else ()
        schemas=(ArtifactSchema("function","1",{}),) if artifacts else ()
        return ProviderResult(self.status,self.signature,artifacts,(),Derivation.OBSERVED,("fixture",),schemas,None,None)

class ExecutorTests(unittest.TestCase):
    def execute(self,statuses,stage=STAGE,skip=(),repairs=None):
        providers={n:Fake(n,s,g) for n,s,g in statuses}
        with tempfile.TemporaryDirectory() as d, EvidenceStore(Path(d)/"e.sqlite") as store:
            result=execute_stage(stage,FP,providers,Matrix(skip),store,ProviderInput(stage.id,(),{},"synthetic-fixture"),H,allowed_providers=frozenset(providers),execution_id="fixture-run",timestamp=NOW,repair_stages=repairs or {})
            return result,store.failures()
    def test_fallback_and_exhaustion(self):
        seq=[("first",ResultStatus.TIMEOUT,FailureSignature.DISPATCHER_LOOP),("second",ResultStatus.EMPTY,FailureSignature.UNKNOWN_PROTOCOL),("third",ResultStatus.PASS,FailureSignature.NONE)]
        r,failures=self.execute(seq)
        self.assertIsInstance(r,ExecutionPass); self.assertEqual([a.provider for a in r.trace],["first","second","third"])
        self.assertEqual([x.failure_signature for x in failures],[FailureSignature.DISPATCHER_LOOP,FailureSignature.UNKNOWN_PROTOCOL])
        self.assertIsNone(r.gate_passed)
        again,_=self.execute(seq); self.assertEqual(r,again)
        r,failures=self.execute(seq[:2]+[("third",ResultStatus.FAIL,FailureSignature.NONE)])
        self.assertIsInstance(r,ExhaustedResult); self.assertEqual(len(failures),3)
    def test_skipped_and_one_reentry(self):
        seq=[("first",ResultStatus.FAIL,FailureSignature.PACKED),("second",ResultStatus.EMPTY,FailureSignature.NONE),("third",ResultStatus.FAIL,FailureSignature.NONE),("repair",ResultStatus.PASS,FailureSignature.NONE)]
        stage=Stage("sample",Layer.STATIC,(),STAGE.providers,None,(RepairRoute(FailureSignature.PACKED,("repair-stage",)),))
        repair=Stage("repair-stage",Layer.STATIC,(),("repair",),None,(RepairRoute(FailureSignature.NONE,("repair-stage",)),))
        r,failures=self.execute(seq,stage,("second",),{"repair-stage":repair})
        self.assertIsInstance(r,ExhaustedResult)
        self.assertEqual([a.provider for a in r.trace],["first","second","third","repair","first","second","third"])
        self.assertEqual(len(failures),4)

    def test_repair_output_is_used_and_receipts_linked(self):
        class NeedsRepair(Fake):
            def invoke(self, inp):
                if inp.artifacts:
                    self.status=ResultStatus.PASS
                    self.signature=FailureSignature.NONE
                else:
                    self.status=ResultStatus.FAIL
                    self.signature=FailureSignature.PACKED
                return super().invoke(inp)
        a=NeedsRepair("first",ResultStatus.FAIL,FailureSignature.PACKED)
        b=Fake("repair",ResultStatus.PASS,FailureSignature.NONE)
        stage=Stage("sample",Layer.STATIC,(),("first",),None,(RepairRoute(FailureSignature.PACKED,("repair-stage",)),))
        repair=Stage("repair-stage",Layer.STATIC,(),("repair",),None,())
        with tempfile.TemporaryDirectory() as d, EvidenceStore(Path(d)/"e.sqlite") as store:
            result=execute_stage(stage,FP,{"first":a,"repair":b},Matrix(),store,ProviderInput(stage.id,(),{},"synthetic-fixture"),H,allowed_providers=frozenset({"first","repair"}),execution_id="repair-run",timestamp=NOW,repair_stages={"repair-stage":repair})
            self.assertIsInstance(result,ExecutionPass)
            self.assertEqual([x.provider for x in result.trace],["first","repair","first"])
            receipt=store.get_attempt(result.trace[-1].receipt_id)
            self.assertNotEqual(receipt.input_hash,H)
            self.assertIn(receipt.evidence_id,result.result.evidence_ids)
            self.assertEqual(len(store.failures()),1)

    def test_unauthorized_and_exception_are_distinct(self):
        class Raises(Fake):
            def invoke(self,inp): raise TimeoutError()
        a=Raises("first",ResultStatus.FAIL,FailureSignature.NONE)
        b=Fake("second",ResultStatus.PASS,FailureSignature.NONE)
        stage=Stage("sample",Layer.STATIC,(),("second","first"),None,())
        with tempfile.TemporaryDirectory() as d, EvidenceStore(Path(d)/"e.sqlite") as store:
            result=execute_stage(stage,FP,{"first":a,"second":b},Matrix(),store,ProviderInput(stage.id,(),{},"synthetic-fixture"),H,allowed_providers=frozenset({"first"}),execution_id="exception-run",timestamp=NOW,repair_stages={})
            self.assertIsInstance(result,ExhaustedResult)
            self.assertIsNone(result.trace[0].receipt_id)
            self.assertEqual(store.failures()[0].status,ResultStatus.TIMEOUT)
