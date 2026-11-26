"""Read prior scoped discovery history first; optional authorized web research."""
from __future__ import annotations
import re
from urllib.parse import urlsplit,urlunsplit
from src.orchestrator.contracts import (DiscoveryKind,DiscoveryCandidate,DiscoveryResult,
    MaintenanceSignal,ResultStatus,FailureSignature,Derivation)

class KnowledgeRetrievalProvider:
    name="knowledge_retrieval"
    kind=DiscoveryKind.KNOWLEDGE_RETRIEVAL

    def __init__(self,store,*,web_search=None,learning_index=None):
        self.store=store
        self.web_search=web_search
        self.learning_index=learning_index or {"records":[]}

    def health_check(self):return self.store is not None

    def invoke(self,query):
        if not self.health_check():
            return DiscoveryResult(ResultStatus.FAIL,FailureSignature.HOST_UNSUPPORTED,(),(),Derivation.UNKNOWN,("Learning store missing",),())
        candidates={};refs=[]
        try:
            for item in self.store.discovery_history(query):
                if item["result"]["status"]!="PASS":continue
                for raw in item["result"]["candidates"]:
                    if not raw.get("verification_required"):continue
                    c=DiscoveryCandidate(raw["canonical_path"],query.capability,raw["license"],
                        MaintenanceSignal(**raw["maintenance_signal"]),raw["stars"],
                        "Revalidate freshness, authorization, and "+raw["verification_required"],
                        Derivation.INFERRED,raw["license_risk"],False,raw.get("source_quote",""),4)
                    candidates.setdefault(c.canonical_path,c)
                    refs.append(item["evidence_id"])
            # Reviewed portable knowledge may carry matching context; not all
            # legacy cards have these fields. Never infer a successful strategy.
            for row in self.learning_index.get("records",[]):
                if row.get("status")!="validated":continue
                if row.get("archetype")!=query.archetype.value or row.get("failure_signature")!=query.failure_signature.value:continue
                if row.get("capability_match")!=query.capability:continue
                if not row.get("id") or not row.get("verification_required"):continue
                c=DiscoveryCandidate("knowledge:"+row["id"],query.capability,"UNKNOWN",MaintenanceSignal(None,None,None),None,
                    row["verification_required"],Derivation.INFERRED,"unknown",False,"Prior reviewed card; revalidate in current scope",3)
                candidates.setdefault(c.canonical_path,c)
            if not candidates and self.web_search is not None:
                for row in self.web_search(query.capability)[:25]:
                    u=urlsplit(row["url"])
                    if u.scheme not in {"http","https"} or not u.hostname or u.username or u.password:continue
                    url=urlunsplit((u.scheme,u.netloc,u.path,"",""))
                    check=row.get("verification_required")
                    if not isinstance(check,str) or not check.strip():continue
                    c=DiscoveryCandidate(url,query.capability,"UNKNOWN",MaintenanceSignal(None,None,None),None,
                        check,Derivation.INFERRED,"unknown",False,str(row.get("quote",""))[:250],4)
                    candidates.setdefault(url,c)
            return DiscoveryResult(ResultStatus.PASS if candidates else ResultStatus.EMPTY,FailureSignature.NONE,
                tuple(candidates[k] for k in sorted(candidates)),tuple(dict.fromkeys(refs)),Derivation.INFERRED,
                ("History first; candidate claims require current fixture verification. No strategy success inferred from discovery PASS.",),())
        except TimeoutError:
            return DiscoveryResult(ResultStatus.TIMEOUT,FailureSignature.NONE,(),tuple(dict.fromkeys(refs)),Derivation.UNKNOWN,("Research timed out",),())
        except (OSError,ValueError,KeyError,TypeError) as exc:
            return DiscoveryResult(ResultStatus.FAIL,FailureSignature.NONE,(),tuple(dict.fromkeys(refs)),Derivation.UNKNOWN,("Research failed: "+type(exc).__name__,),())
