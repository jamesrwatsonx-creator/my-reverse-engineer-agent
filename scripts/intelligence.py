#!/usr/bin/env python3
"""Local evidence bookkeeping. Does not certify truth, identity, permissions or runtime readiness."""
import argparse, datetime, hashlib, json, math, pathlib, re, sys
import workbench as w
ROOT=w.ROOT
KINDS={"NEW","CORROBORATION","VARIANT","COMPOSITION","METHOD","FAILURE","CONTRADICTION","RETRACTION","NO_CHANGE"}
NEGATIVE={"FAILURE","CONTRADICTION","RETRACTION"}
GATES={"functional","security","license","authorization","fidelity"}
PACKAGE={"PRODUCT_SPEC.md","ARCHITECTURE.md","UX_SPEC.md","CONTRACTS.md","DEPENDENCIES.json","ACCEPTANCE.md","BUILD_PLAN.md","GAPS.md","BUILD_AGENT.md"}
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def safe_file(base, rel):
    if not isinstance(rel,str) or not rel or "\\" in rel: raise ValueError("Invalid relative file reference")
    p=pathlib.PurePosixPath(rel)
    if p.is_absolute() or ".." in p.parts: raise ValueError("Unsafe file reference: "+rel)
    f=base.joinpath(*p.parts)
    if not f.is_file() or not f.resolve().is_relative_to(base.resolve()) or f.is_symlink(): raise ValueError("Missing or unsafe file: "+rel)
    return f
def ref(base,record):
    f=safe_file(base,record["path"])
    if sha(f)!=record["sha256"]: raise ValueError("Hash mismatch: "+record["path"])
    return f
def index(root): return w.load(root/"knowledge/index.json")
def search(query,root=ROOT):
    terms=set(re.findall(r"[a-z0-9]+",query.lower()))
    if not terms: raise ValueError("Search query required")
    hits=[]
    for row in index(root)["records"]:
        hay=set(re.findall(r"[a-z0-9]+", " ".join([row["capability_id"],row["summary"],row["kind"]," ".join(row.get("aliases",[])),row.get("context","")]).lower()))
        score=len(terms & hay)
        if score: hits.append({"score":score,**row})
    return sorted(hits,key=lambda x:(-x["score"],x["id"]))
def compare(d):
    def result(s,reason,metrics=None): return {"result":s,"reason":reason,"metrics":metrics or {},"structural_comparison_only":True}
    a,b=d["baseline"],d["challenger"]
    if not d.get("context_id") or not d.get("fixture_id") or any(x.get(k)!=d[k] for x in (a,b) for k in ("context_id","fixture_id")): return result("INCOMPARABLE","Context or fixture differs")
    if any(set(x.get("gates",{}))!=GATES or any(v!="PASS" for v in x["gates"].values()) for x in (a,b)): return result("INCOMPARABLE","Hard gates not all passed")
    am,bm=a["metrics"],b["metrics"]
    if not am or set(am)!=set(bm): return result("INCOMPARABLE","Metric sets differ")
    signs=[]; details={}
    for k,m in am.items():
        n=bm[k]
        if any(m.get(x)!=n.get(x) for x in ("unit","direction","tolerance","n")) or m.get("direction") not in ("min","max") or not m.get("unit") or not isinstance(m.get("n"),int) or m["n"]<1: return result("INCOMPARABLE","Metric definition or sample size differs: "+k)
        v,t,u=m.get("value"),m.get("tolerance"),n.get("value")
        if any(isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) for x in (v,t,u)) or t<0: return result("INCOMPARABLE","Invalid metric: "+k)
        delta=(u-v)*(1 if m["direction"]=="max" else -1)
        sign=1 if delta>t else -1 if delta< -t else 0
        signs.append(sign); details[k]={"baseline":v,"challenger":u,"unit":m["unit"],"advantage":delta,"tolerance":t}
    status="TRADEOFF" if 1 in signs and -1 in signs else "DOMINATES" if 1 in signs else "BASELINE_DOMINATES" if -1 in signs else "TIE"
    return result(status,"Numerical comparison within stated tolerances, not statistical significance",details)
def target(root,s): return root/"investigations"/w.slug(s)
def item_check(root,x):
    for k in ("id","capability_id","kind","proposer","summary","context","limitations"):
        if not isinstance(x.get(k),str) or not x[k].strip(): raise ValueError("Missing learning item field: "+k)
    w.slug(x["id"]); w.slug(x["capability_id"])
    if x["kind"] not in KINDS: raise ValueError("Unknown learning kind")
    evidence=x.get("evidence",[])
    if not isinstance(evidence,list) or not evidence: raise ValueError("Evidence references required")
    for e in evidence: ref(root,e)
    if "comparison" in x: ref(root,x["comparison"])
def audit(s,root=ROOT):
    f=target(root,s); issues=[]
    v=w.validate(s,root)
    if not v["valid"]: issues.append("Scaffold incomplete: "+str(v))
    if issues: return {"valid":False,"issues":issues,"structural_only":True}
    d=w.load(f/"LEARNING_DELTA.json"); ctx=w.load(f/"CONTEXT.json")
    if d.get("target_slug")!=s: issues.append("Wrong target slug")
    if d.get("assessment") not in ("ASSESSED","NO_CHANGE"): issues.append("Learning assessment pending")
    if not all(isinstance(ctx.get(k),str) and re.fullmatch(r"[0-9a-f]{40}",ctx[k]) for k in ("instruction_revision","tool_registry_revision","knowledge_revision")): issues.append("Actual baseline Git revisions required")
    if not isinstance(ctx.get("retrieved_ids"),list): issues.append("Missing retrieval record")
    items=d.get("items",[])
    if d.get("assessment")=="NO_CHANGE" and (items or not str(d.get("no_change_reason") or "").strip()): issues.append("NO_CHANGE requires empty items and explicit reason")
    if d.get("assessment")=="ASSESSED" and not items: issues.append("ASSESSED requires items; use NO_CHANGE otherwise")
    ids=set()
    for x in items:
        try:
            item_check(root,x)
            if x["id"] in ids: raise ValueError("Duplicate learning ID")
            ids.add(x["id"])
        except (ValueError,KeyError,TypeError) as e: issues.append(str(e))
    return {"valid":not issues,"issues":issues,"items":len(items),"structural_only":True,"note":"Audit does not promote or prove findings"}
def review(s,item_id,reviewer,decision,reason,receipt,root=ROOT):
    f=target(root,s); d=w.load(f/"LEARNING_DELTA.json"); ix=index(root)
    if decision not in ("validated","rejected","needs-retest","deprecated"): raise ValueError("Invalid review decision")
    if not reviewer.strip() or not reason.strip(): raise ValueError("Reviewer and rationale required")
    if d.get("target_slug")!=s or d.get("assessment")!="ASSESSED": raise ValueError("Completed assessment required")
    report=audit(s,root)
    if not report["valid"]: raise ValueError("Learning audit failed: "+str(report["issues"]))
    matches=[x for x in d["items"] if x["id"]==item_id]
    if len(matches)!=1: raise ValueError("Exactly one item required")
    x=matches[0]; item_check(root,x)
    if reviewer.strip().casefold()==x["proposer"].strip().casefold(): raise ValueError("Separate reviewer required")
    receipt_path=safe_file(root,receipt)
    receipt_ref={"path":receipt,"sha256":sha(receipt_path)}
    if receipt in [e["path"] for e in x["evidence"]]: raise ValueError("Separate review receipt required")
    if decision=="validated":
        if x.get("fixture_result") not in (("FAIL","PASS") if x["kind"] in NEGATIVE else ("PASS",)): raise ValueError("Actual fixture result required")
        if not x.get("fixture_receipt"): raise ValueError("Fixture receipt required")
        ref(root,x["fixture_receipt"])
        if x.get("license_review")!="PASS" or x.get("privacy_review")!="PASS": raise ValueError("License and privacy review required")
        if x.get("claims_improvement") or x["kind"]=="VARIANT":
            if "comparison" not in x: raise ValueError("Comparison required for variant or improvement")
            comparison=compare(w.load(ref(root,x["comparison"])))
            if comparison["result"]=="INCOMPARABLE": raise ValueError("Comparable measurement required")
            if x.get("claims_improvement") and comparison["result"]!="DOMINATES": raise ValueError("Unqualified improvement not supported")
    key=s+":"+item_id
    row={"id":key,"target_slug":s,"capability_id":x["capability_id"],"kind":x["kind"],"summary":x["summary"],"context":x["context"],"limitations":x["limitations"],"aliases":x.get("aliases",[]),"status":decision,"reviewer":reviewer,"reason":reason,"review_receipt":receipt_ref,"evidence":x["evidence"],"fixture_receipt":x.get("fixture_receipt"),"comparison":x.get("comparison"),"reviewed_at":now()}
    existing=next((r for r in ix["records"] if r["id"]==key),None)
    ix["review_history"].append({"previous":existing,"current":row})
    ix["records"]=[r for r in ix["records"] if r["id"]!=key]+[row]
    w.dump(root/"knowledge/index.json",ix)
    return row
def verify_package(s,root=ROOT):
    base=target(root,s)/"handoff"; m=w.load(base/"MANIFEST.json")
    if m.get("target_slug")!=s or not re.fullmatch(r"[0-9a-f]{40}",str(m.get("source_commit",""))) or m.get("readiness") not in ("PARTIAL","BUILD_READY") or not all(m.get(k) for k in ("source_repo","destination","package_version","approval_ref")): raise ValueError("Incomplete manifest metadata")
    records=m["files"]; paths=[x["path"] for x in records]
    if len(paths)!=len(set(paths)) or set(paths)!=PACKAGE: raise ValueError("Required allowlisted package files mismatch")
    for x in records: ref(base,x)
    return {"valid":True,"files":len(paths),"readiness_claim":m["readiness"],"integrity_only":True,"note":"Readiness and approval must be separately reviewed"}
def make_package(s,source_repo,source_commit,destination,version,readiness,approval,root=ROOT):
    base=target(root,s)/"handoff"
    if not re.fullmatch(r"[0-9a-f]{40}",source_commit) or not all(x.strip() for x in (source_repo,destination,version,approval)): raise ValueError("Manifest metadata required")
    if readiness not in ("PARTIAL","BUILD_READY"): raise ValueError("Invalid readiness")
    m={"source_repo":source_repo,"source_commit":source_commit,"target_slug":s,"destination":destination,"readiness":readiness,"package_version":version,"approval_ref":approval,"files":[{"path":p,"sha256":sha(safe_file(base,p))} for p in sorted(PACKAGE)]}
    if (base/"MANIFEST.json").exists(): raise ValueError("Manifest exists; preserve old package commit and explicitly version new package")
    w.dump(base/"MANIFEST.json",m); return verify_package(s,root)
def main():
    p=argparse.ArgumentParser(description=__doc__); sub=p.add_subparsers(dest="cmd",required=True)
    sub.add_parser("search").add_argument("--query",required=True)
    sub.add_parser("compare").add_argument("--file",required=True)
    for c in ("audit","verify-package"): sub.add_parser(c).add_argument("--slug",required=True)
    r=sub.add_parser("review")
    for k in ("slug","id","reviewer","decision","reason","receipt"): r.add_argument("--"+k,required=True)
    q=sub.add_parser("make-package")
    for k in ("slug","source-repo","source-commit","destination","version","readiness","approval"): q.add_argument("--"+k,required=True)
    a=p.parse_args()
    try:
        if a.cmd=="search": out=search(a.query)
        elif a.cmd=="compare": out=compare(w.load(pathlib.Path(a.file)))
        elif a.cmd=="audit": out=audit(a.slug)
        elif a.cmd=="review": out=review(a.slug,a.id,a.reviewer,a.decision,a.reason,a.receipt)
        elif a.cmd=="make-package": out=make_package(a.slug,a.source_repo,a.source_commit,a.destination,a.version,a.readiness,a.approval)
        else: out=verify_package(a.slug)
        print(json.dumps(out,indent=2)); return 1 if isinstance(out,dict) and out.get("valid") is False else 0
    except (ValueError,OSError,KeyError,TypeError) as e: print(str(e),file=sys.stderr); return 1
if __name__=="__main__": raise SystemExit(main())
