import base64,json,tempfile,unittest
from datetime import datetime,timezone
from pathlib import Path
from subprocess import CompletedProcess
from src.orchestrator.contracts import *
from src.orchestrator.evidence_store import EvidenceStore
from src.providers.github_search_provider import GitHubSearchProvider
from src.providers.browser_research_provider import BrowserResearchProvider
from src.providers.knowledge_retrieval_provider import KnowledgeRetrievalProvider

F=json.loads((Path(__file__).parent/"fixtures/phase3.json").read_text())
NOW=datetime(2026,1,2,tzinfo=timezone.utc)
Q=DiscoveryQuery("rate limiting middleware","Python",Archetype.CLOUD_API,FailureSignature.UNKNOWN_PROTOCOL,("MIT",),"synthetic-fixture","rate limiting response","server policy",())
def gh(args):
    d=F["github"]
    if args[1:3]==["auth","status"]: data="authenticated"
    elif args[1:3]==["search","repos"]: data=d["search"]
    elif args[1:3]==["repo","view"]: data=d["details"][args[3]]
    elif args[1]=="api": data={"content":base64.b64encode(d["readme"].encode()).decode()}
    elif args[1:3]==["issue","list"]: data=d["issues"]
    else: raise AssertionError(args)
    return CompletedProcess(args,0,json.dumps(data),"")
class DiscoveryTests(unittest.TestCase):
    def test_github_license_archive_ranking(self):
        p=GitHubSearchProvider(run=gh,clock=lambda:NOW)
        self.assertTrue(p.health_check())
        r=p.invoke(Q)
        self.assertEqual(r.status,ResultStatus.PASS)
        self.assertEqual([c.canonical_path for c in r.candidates],["fixture/also","fixture/fit","fixture/copyleft"])
        self.assertEqual(r.candidates[0].license,"MIT")
        self.assertEqual(r.candidates[-1].license_risk,"high")
        self.assertFalse(r.candidates[-1].eligible)
        self.assertTrue(all(c.capability_match==Q.capability for c in r.candidates))
        self.assertTrue(r.rejections)
    def test_browser_inferred(self):
        p=BrowserResearchProvider(capture=lambda q:F["har"])
        self.assertTrue(p.health_check())
        r=p.invoke(Q)
        self.assertEqual(r.status,ResultStatus.PASS)
        self.assertTrue(r.candidates)
        self.assertTrue(all(c.derivation is Derivation.INFERRED and c.verification_required for c in r.candidates))
    def test_knowledge_prior_before_web(self):
        with tempfile.TemporaryDirectory() as d,EvidenceStore(Path(d)/"e.db") as s:
            calls=[]
            p=KnowledgeRetrievalProvider(s,web_search=lambda q:calls.append(q) or F["web"])
            first=p.invoke(Q)
            self.assertEqual(first.status,ResultStatus.PASS)
            s.record_discovery("learn-1",p.name,NOW,Q,first)
            second=p.invoke(Q)
            self.assertEqual(len(calls),1)
            self.assertEqual(second.candidates[0].derivation,Derivation.INFERRED)
            self.assertTrue(second.evidence_ids)
