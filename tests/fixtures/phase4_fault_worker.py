"""Subprocess worker: SIGKILL at actual persisted boundaries, then reopen DB."""
import json,os,signal,sys
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from src.orchestrator.contracts import *
from src.orchestrator.evidence_store import EvidenceStore,digest
from src.orchestrator.durability import DurableExecution
from src.orchestrator.executor import execute_stage
from src.orchestrator.circuit_breaker import CircuitBreaker
from src.orchestrator.dag_engine import DagEngine
from src.orchestrator.supervisor import Supervisor
from src.orchestrator.dossier_writer import DossierWriter,LearningWriter

root=Path(sys.argv[1]);scenario=sys.argv[2];kill=sys.argv[3]=="kill"
NOW=datetime(2026,1,1,tzinfo=timezone.utc)
FP=TargetFingerprint(Archetype.CLOUD_API,"fixture",None,None,(),(),None,1,False,True)
def die():os.kill(os.getpid(),signal.SIGKILL)
def hook(point):
    if kill and {"completed":"after_provider_outbox","circuit":"after_evidence","stage":"after_stage"}.get(scenario)==point:die()
def log(key):
    with (root/"calls").open("a") as f:
        f.write(key+"\n");f.flush();os.fsync(f.fileno())
class Matrix:
    def is_available(self,n):return True
    def why_unavailable(self,n):return ""
class Provider:
    def __init__(self,name):self.name=name
    def invoke_durable(self,inp,key,commit):
        log(key)
        if scenario=="incomplete" and kill:die()
        payload={"body":"fixture"}
        a=Artifact("function","fixture",digest(payload),"fixture",self.name,Derivation.OBSERVED,(),payload)
        fail=scenario=="circuit" or scenario=="discovery"
        r=ProviderResult(ResultStatus.FAIL if fail else ResultStatus.PASS,FailureSignature.UNKNOWN_PROTOCOL if fail else FailureSignature.NONE,() if fail else (a,),(),Derivation.OBSERVED,(),(),None,None)
        return commit(r)
class Research:
    name="knowledge_retrieval"
    def health_check(self):return True
    def invoke_durable(self,q,key,commit):
        log(key)
        if kill:die()
        return commit(DiscoveryResult(ResultStatus.EMPTY,FailureSignature.NONE,(),(),Derivation.INFERRED,(),()))
def stage(i,pre=()):
    return {"id":i,"kind":"analysis","layer":"static","providers":[i],"preconditions":list(pre),"input_contract":[],"output_contract":[{"artifact_type":"function","required_fields":{"body":None}}],"on_fail":[],"gate":"fixture-contract","capability":"rate limiting middleware"}
with EvidenceStore(root/"e.db") as s:
    durable=DurableExecution(s,hook)
    if scenario=="stage":
        engine=DagEngine({"cloud-api":[stage("A"),stage("B",("A",))]},{"A":Provider("A"),"B":Provider("B")},Matrix(),s,{},durable=durable)
        r=engine.run(FP,input_hash="a"*64,execution_id="fault",timestamp=NOW,allowed_providers=frozenset({"A","B"}))
        print(json.dumps({"calls":len((root/"calls").read_text().splitlines()),"stages":list(r.trace)}))
    elif scenario=="discovery":
        # Exercise actual supervisor abstention path. Exclude initial analysis call
        # from discovery count; its stable key is still independently persisted.
        with DossierWriter(root/"d.db") as w,LearningWriter(root/"l.db") as l:
            engine=DagEngine({"cloud-api":[stage("A")]},{"A":Provider("A")},Matrix(),s,{"knowledge_retrieval":Research()},durable=durable)
            result=Supervisor(engine,s,w,l,durable=durable).run(FP,input_hash="a"*64,execution_id="fault",timestamp=NOW,allowed_providers=frozenset({"A","knowledge_retrieval"}),objectives={"A":{"required_to_proceed":"fixture"}})
            key="fault:abstention:A:knowledge_retrieval"
            keys=[x for x in (root/"calls").read_text().splitlines() if x==key]
            print(json.dumps({"calls":len(keys),"keys":keys,"events":[e["state"] for e in durable.events(key)],"receipts":len(s.discoveries_for_run("fault"))}))
    else:
        st=Stage("A",Layer.STATIC,(),("A",),None,())
        r=execute_stage(st,FP,{"A":Provider("A")},Matrix(),s,ProviderInput("A",(),{},"synthetic-fixture"),"a"*64,allowed_providers=frozenset({"A"}),execution_id="fault",timestamp=NOW,repair_stages={},durable=durable)
        key="fault:A:initial:0";receipt=s.get_attempt(key)
        print(json.dumps({"calls":len((root/"calls").read_text().splitlines()),"receipts":s.db.execute("SELECT count(*) FROM attempts").fetchone()[0],"status":receipt.status.value,"attempt_hash":durable.get(key,"STARTED")["attempt_hash"],"circuit_failures":CircuitBreaker(s).state("A").failures}))
