"""Read-only research projection from an explicitly authorized, supplied capture source.

No target access is performed by this adapter. Capture backends may be attached
by the host after permission review; Phase 3 tests use a sanitized HAR fixture.
"""
from __future__ import annotations
import re
from urllib.parse import urlsplit,urlunsplit
from src.orchestrator.contracts import (DiscoveryKind,DiscoveryCandidate,DiscoveryResult,
    MaintenanceSignal,ResultStatus,FailureSignature,Derivation)

class BrowserResearchProvider:
    name="browser_research"
    kind=DiscoveryKind.BROWSER_RESEARCH
    capture_methods=("network-capture","graphql-introspect","openapi-import","bundle-analysis","browser-automation")

    def __init__(self, *, capture=None):
        self.capture=capture

    def health_check(self):
        return callable(self.capture)

    def invoke(self,query):
        if not self.health_check():
            return DiscoveryResult(ResultStatus.FAIL,FailureSignature.HOST_UNSUPPORTED,(),(),Derivation.UNKNOWN,("No authorized capture backend",),())
        try:
            raw=self.capture(query)
            entries=raw["log"]["entries"]
            if not isinstance(entries,list):raise ValueError("Invalid HAR")
            candidates={}
            for row in entries[:250]:
                req=row["request"];response=row["response"]
                url=urlsplit(req["url"])
                if url.scheme not in {"http","https"} or not url.hostname or url.username or url.password:
                    continue
                # Do not preserve query, fragment, credentials, headers, or bodies.
                public=urlunsplit((url.scheme,url.netloc,url.path,"",""))
                method=req["method"];status=response["status"]
                if not re.fullmatch(r"[A-Z]{1,12}",method) or not isinstance(status,int):continue
                words={w for w in re.findall(r"[a-z0-9]+",query.capability.lower()) if len(w)>2}
                pathwords=set(re.findall(r"[a-z0-9]+",url.path.lower()))
                if not words.intersection(pathwords):continue
                candidate=DiscoveryCandidate(public,query.capability,"UNKNOWN",MaintenanceSignal(None,None,None),None,
                    "Replay an authorized local response fixture; confirm observable status, response schema and state transition",
                    Derivation.INFERRED,"unknown",False,f"{method} recorded with HTTP {status}; mechanism unknown",4)
                candidates[(public,method,status)]=candidate
            result=tuple(candidates[k] for k in sorted(candidates))
            return DiscoveryResult(ResultStatus.PASS if result else ResultStatus.EMPTY,FailureSignature.NONE,
                result,(),Derivation.INFERRED,
                ("HAR feature survey and operation hypotheses only; network-capture selected. Other capture methods require explicit supported authorized backend. Tier 4, never overrides observed binary evidence.",),())
        except TimeoutError:
            return DiscoveryResult(ResultStatus.TIMEOUT,FailureSignature.NONE,(),(),Derivation.UNKNOWN,("Capture source timeout",),())
        except (ValueError,KeyError,TypeError,OSError) as exc:
            return DiscoveryResult(ResultStatus.FAIL,FailureSignature.NONE,(),(),Derivation.UNKNOWN,("Capture invalid: "+type(exc).__name__,),())
