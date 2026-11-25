#!/usr/bin/env python3
"""Read-only GitHub freshness collector; requires authenticated gh. No installs or remote writes."""
import argparse, datetime, json, pathlib, re, subprocess, sys
from collections import deque
ROOT=pathlib.Path(__file__).resolve().parents[1]
NAME=re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
def load(path): return json.loads(path.read_text(encoding="utf-8"))
def github_name(url):
    p="https://github.com/"
    if not isinstance(url,str) or not url.startswith(p): return None
    n=url[len(p):].rstrip("/")
    return n if NAME.fullmatch(n) else None
def sources(catalog):
    result={}
    for e in catalog["entries"]:
        for url in [e["url"]]+[x["url"] for x in e.get("related_sources",[])]:
            n=github_name(url)
            if n: result[n.lower()]=n
    return result
def request(endpoint):
    p=subprocess.run(["gh","api","--method","GET",endpoint],capture_output=True,text=True,timeout=45)
    if p.returncode:
        # Avoid leaking raw stderr or headers to committed reports.
        return None,"HTTP_OR_ACCESS_ERROR"
    try: return json.loads(p.stdout),None
    except ValueError: return None,"INVALID_JSON"
def call(api,endpoint):
    try: return api(endpoint)
    except (OSError,subprocess.TimeoutExpired): return None,"CLI_OR_TIMEOUT"
def scan(catalog,previous,api=request):
    tracked=sources(catalog); old={x["repository"].lower():x for x in previous.get("records",[])}
    # Preserve prior useful resources, even if absent from a new catalog.
    for key,row in old.items():
        if NAME.fullmatch(row["repository"]): tracked.setdefault(key,row["repository"])
    pending=deque(tracked.values()); seen=set(); records=[]
    while pending:
        name=pending.popleft(); key=name.lower()
        if key in seen: continue
        seen.add(key); prior=old.get(key,{})
        base="repos/"+name
        meta,err=call(api,base)
        row={"repository":name,"head_status":"BLOCKED","head_sha":None,"release_status":"NOT_CHECKED","release_tag":None,"previous_observed_sha":prior.get("head_sha") or prior.get("previous_observed_sha"),"reviewed_sha":prior.get("reviewed_sha"),"capability_review":"PENDING_DEEP_REVIEW","runtime_status":"NOT_RUN"}
        if not isinstance(meta,dict) or not meta.get("full_name"):
            row["metadata_status"]=err or "UNUSABLE_RESPONSE"; records.append(row); continue
        canonical=meta["full_name"]
        if not NAME.fullmatch(canonical): row["metadata_status"]="INVALID_REPO_NAME"; records.append(row); continue
        row.update(metadata_status="OBSERVED",canonical_repository=canonical,default_branch=meta.get("default_branch"),archived=meta.get("archived"),license=(meta.get("license") or {}).get("spdx_id"),lineage=[])
        for field in ("parent","source"):
            n=(meta.get(field) or {}).get("full_name")
            if isinstance(n,str) and NAME.fullmatch(n):
                row["lineage"].append({"relationship":field,"repository":n})
                if n.lower() not in seen: pending.append(n)
        base="repos/"+canonical
        commits,err=call(api,base+"/commits?per_page=1")
        if isinstance(commits,list) and commits and isinstance(commits[0],dict):
            c=commits[0]; sha=c.get("sha")
            if isinstance(sha,str) and re.fullmatch(r"[a-f0-9]{40}",sha):
                co=c.get("commit",{}); row.update(head_status="OBSERVED",head_sha=sha,commit_date=(co.get("committer") or {}).get("date"),latest_commit_title=str(co.get("message","")).split("\n")[0][:300])
        if not row["head_sha"]: row["head_error"]=err or "UNUSABLE_RESPONSE"
        rel,err=call(api,base+"/releases/latest")
        if isinstance(rel,dict) and rel.get("tag_name"):
            row.update(release_status="OBSERVED",release_tag=rel["tag_name"],release_date=rel.get("published_at"),release_url=rel.get("html_url"),release_notes_excerpt=str(rel.get("body") or "")[:6000])
        else: row["release_status"]=err or "NO_VERIFIED_RELEASE"
        row["release_changed"]=row.get("release_tag")!=prior.get("release_tag")
        row["head_changed"]=bool(row["head_sha"] and row["head_sha"]!=row["previous_observed_sha"])
        for label,oldsha in (("observed",row["previous_observed_sha"]),("reviewed",row["reviewed_sha"])):
            if not row["head_sha"] or not isinstance(oldsha,str) or not re.fullmatch(r"[a-f0-9]{40}",oldsha): continue
            if oldsha==row["head_sha"]: row[label+"_comparison"]={"status":"identical"}; continue
            # Deduplicate matching comparisons.
            if label=="reviewed" and oldsha==row["previous_observed_sha"] and "observed_comparison" in row:
                row[label+"_comparison"]=row["observed_comparison"]; continue
            comp,err=call(api,base+"/compare/"+oldsha+"..."+row["head_sha"])
            if isinstance(comp,dict) and comp.get("status"):
                files=comp.get("files") or []; cs=comp.get("commits") or []
                row[label+"_comparison"]={"status":comp["status"],"ahead_by":comp.get("ahead_by"),"behind_by":comp.get("behind_by"),"total_commits":comp.get("total_commits"),"file_names":[f.get("filename") for f in files[:300]],"commit_titles":[str(x.get("commit",{}).get("message","")).split("\n")[0][:300] for x in cs[:250]],"note":"GitHub compare results may be truncated; inspect complete relevant change range independently."}
            else: row[label+"_comparison"]={"status":"BLOCKED","reason":err or "UNUSABLE_RESPONSE"}
        records.append(row)
    return {"schema_version":1,"review_date":datetime.datetime.now(datetime.timezone.utc).isoformat(),"scope":"Read-only metadata and bounded release/compare triage; not a deep or runtime review.","counts":{"tracked":len(records),"head_observed":sum(r["head_status"]=="OBSERVED" for r in records),"blocked":sum(r["head_status"]!="OBSERVED" for r in records),"releases_observed":sum(r["release_status"]=="OBSERVED" for r in records)},"records":records}
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output",type=pathlib.Path,required=True)
    p.add_argument("--previous",type=pathlib.Path,default=ROOT/"registry/source_baseline.json")
    a=p.parse_args()
    if a.output.exists(): p.error("Refusing to overwrite an existing report; use a new path")
    try:
        report=scan(load(ROOT/"registry/tools.json"),load(a.previous))
        a.output.parent.mkdir(parents=True,exist_ok=True)
        with a.output.open("x",encoding="utf-8") as f: json.dump(report,f,indent=2); f.write("\n")
        print(json.dumps(report["counts"])); return 0 if not report["counts"]["blocked"] else 2
    except (OSError,ValueError,KeyError) as e: print(str(e),file=sys.stderr); return 1
if __name__=="__main__": raise SystemExit(main())
