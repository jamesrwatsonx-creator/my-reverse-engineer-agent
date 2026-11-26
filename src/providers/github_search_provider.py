"""Capability-indexed public GitHub research; never installs or executes candidates."""
from __future__ import annotations
import base64
import json
import re
import shutil
import subprocess
import time
from datetime import datetime,timezone
from src.orchestrator.contracts import (DiscoveryKind, DiscoveryCandidate, DiscoveryResult,
    MaintenanceSignal, ResultStatus, FailureSignature, Derivation)

class GitHubSearchProvider:
    name="github_search"
    kind=DiscoveryKind.GITHUB_SEARCH

    def __init__(self, *, run=None, clock=lambda:datetime.now(timezone.utc), allow_live=False,
                 inspect_limit=10, max_age_days=730, min_interval=1.0):
        if not 1<=inspect_limit<=50 or max_age_days<1 or min_interval<0:
            raise ValueError("Invalid discovery budget")
        self.run=run
        self.clock=clock
        self.allow_live=allow_live
        self.inspect_limit=inspect_limit
        self.max_age_days=max_age_days
        self.min_interval=min_interval
        self.cache={}
        self._last=None
        self._error=FailureSignature.AUTH_MISSING

    def _command(self,args):
        key=tuple(args)
        if key in self.cache: return self.cache[key]
        if self.run is not None:
            result=self.run(args)
        else:
            if not self.allow_live or not shutil.which("gh"):
                raise OSError("GitHub CLI live research unavailable")
            if self._last is not None:
                time.sleep(max(0,self.min_interval-(time.monotonic()-self._last)))
            self._last=time.monotonic()
            result=subprocess.run(args,capture_output=True,text=True,timeout=15,check=False)
        if result.returncode!=0:
            msg=(result.stderr or "").lower()
            self._error=FailureSignature.RATE_LIMITED if ("rate limit" in msg or "429" in msg) else FailureSignature.AUTH_MISSING if ("auth" in msg or "401" in msg) else FailureSignature.NONE
            raise RuntimeError("GitHub command failed; diagnostics redacted")
        if len(result.stdout or "")>2_000_000:
            raise ValueError("GitHub response exceeds bounded input")
        self.cache[key]=result.stdout
        return result.stdout

    def health_check(self):
        try:
            self._command(["gh","auth","status","--hostname","github.com"])
            return True
        except (OSError,RuntimeError,ValueError,subprocess.TimeoutExpired):
            return False

    def invoke(self,query):
        rejects=[]; candidates=[]
        if self.run is None and (not self.allow_live or query.authorization_ref!="public-research"):
            return DiscoveryResult(ResultStatus.FAIL,FailureSignature.AUTH_MISSING,(),(),Derivation.UNKNOWN,("Live public discovery not enabled",),())
        if not self.health_check():
            return DiscoveryResult(ResultStatus.FAIL,self._error,(),(),Derivation.UNKNOWN,("GitHub health check failed",),())
        try:
            # No shell, no target name; inspect a bounded subset by recency/path.
            # Apply allowlist after search so copyleft results remain recorded.
            terms=query.capability+((" language:"+query.language) if query.language else "")
            rows=json.loads(self._command(["gh","search","repos",terms,"--limit","50","--sort","updated","--json","fullName,description,url,language,license,updatedAt,stargazersCount"]))
            if not isinstance(rows,list): raise ValueError("Invalid search response")
            rows=sorted(rows[:50],key=lambda x:(str(x.get("fullName","")).casefold()))
            rows.sort(key=lambda x:str(x.get("updatedAt") or ""),reverse=True)
            allow={v.casefold() for v in query.license_allowlist}
            def permitted(lic):
                return lic.casefold() in allow
            words={w for w in re.findall(r"[a-z0-9]+",query.capability.lower()) if len(w)>2}
            for row in rows[self.inspect_limit:]:
                rejects.append(str(row.get("fullName","unknown"))+": inspection budget; unreviewed")
            for row in rows[:self.inspect_limit]:
                name=row.get("fullName","")
                if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+",name) or any(p in {".",".."} for p in name.split("/")):
                    rejects.append("invalid repository identity");continue
                details=json.loads(self._command(["gh","repo","view",name,"--json","nameWithOwner,licenseInfo,primaryLanguage,pushedAt,isArchived,latestRelease"]))
                canonical=details.get("nameWithOwner",name)
                if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+",canonical):
                    rejects.append(name+": invalid canonical path");continue
                if details.get("isArchived") is not False:
                    rejects.append(canonical+": archived or unknown archive status");continue
                pushed=details.get("pushedAt")
                meta=json.loads(self._command(["gh","api","repos/"+canonical]))
                commits=json.loads(self._command(["gh","api","repos/"+canonical+"/commits?per_page=1"]))
                date=(commits[0].get("commit",{}).get("committer") or {}).get("date") if isinstance(commits,list) and commits else None
                count=meta.get("open_issues_count") if isinstance(meta,dict) else None
                if not isinstance(count,int) or isinstance(count,bool) or count<0: count=None
                try:
                    when=datetime.fromisoformat((date or pushed).replace("Z","+00:00"))
                    age=(self.clock()-when).days
                except (AttributeError,TypeError,ValueError):
                    rejects.append(canonical+": unknown maintenance date");continue
                if age>self.max_age_days:
                    rejects.append(canonical+": stale maintenance");continue
                lic=(details.get("licenseInfo") or {}).get("spdxId") or "UNKNOWN"
                if lic in {"NOASSERTION","OTHER"}:lic="UNKNOWN"
                copyleft=bool(re.match(r"(?i)(?:A?GPL)(?:-|$)",lic))
                if not copyleft and not permitted(lic):
                    rejects.append(canonical+": license outside allowlist ("+lic+")");continue
                read=json.loads(self._command(["gh","api","repos/"+canonical+"/readme"]))
                raw=base64.b64decode(read.get("content",""),validate=False)
                excerpt=raw[:16000].decode("utf-8",errors="replace")
                issues=json.loads(self._command(["gh","issue","list","--repo",canonical,"--state","open","--limit","10","--json","number,title,labels"]))
                text=((row.get("description") or "")+" "+excerpt).lower()
                matched=words.intersection(re.findall(r"[a-z0-9]+",text))
                if not words or len(matched)<max(1,(len(words)+1)//2):
                    rejects.append(canonical+": insufficient capability terms; broad or unrelated");continue
                if re.search(r"(?i)requires (?:our|a paid|the hosted) (?:cloud|service|subscription|account)|hosted[- ]only|saas[- ]only",text):
                    rejects.append(canonical+": service-coupled candidate");continue
                candidates.append(DiscoveryCandidate(canonical,query.capability,lic,
                    MaintenanceSignal(date,count,False),row.get("stargazersCount"),
                    "Review exact license and dependencies; inspect implementation and run authorized held-out capability fixture; issue sample="+str(len(issues)),
                    Derivation.INFERRED,"high" if copyleft else "review-required",not copyleft,
                    "Bounded README and metadata reviewed; not implementation proof",4))
            # Stars never enter selection or order. Stable tie break; eligible before risks.
            candidates.sort(key=lambda c:(not c.eligible,c.canonical_path.casefold()))
            return DiscoveryResult(ResultStatus.PASS if candidates else ResultStatus.EMPTY,FailureSignature.NONE,
                tuple(candidates),(),Derivation.OBSERVED,
                ("API metadata observed; capability fit inferred. GitHub open_issues_count can include pull requests; issue sample is not total. No copying or auto-integration.",),tuple(rejects))
        except subprocess.TimeoutExpired:
            return DiscoveryResult(ResultStatus.TIMEOUT,FailureSignature.NONE,tuple(candidates),(),Derivation.UNKNOWN,("Bounded command timeout",),tuple(rejects))
        except (OSError,RuntimeError,ValueError,TypeError,KeyError) as exc:
            return DiscoveryResult(ResultStatus.FAIL,self._error if isinstance(exc,RuntimeError) else FailureSignature.NONE,
                tuple(candidates),(),Derivation.UNKNOWN,("Discovery interrupted: "+type(exc).__name__,),tuple(rejects))
