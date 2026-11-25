#!/usr/bin/env python3
"""Deterministic local gap planner and structural handoff audit. No external tool execution."""
import argparse, json, pathlib, re, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
KNOWLEDGE={"DOCUMENTED","OBSERVED","INFERRED","UNKNOWN","BLOCKED"}
FUNCTION={"NOT_RUN","PASS","FAIL","BLOCKED","DEFERRED"}
DISPOSITION={"OPEN","TEST","RESOLVED","BLOCKED","DEFERRED"}
LIMITS={"missing-evidence","tool-coverage","restricted","non-identifiable","budget","unavailable-data"}
def read(p): return json.loads(p.read_text(encoding="utf-8"))
def load_routes(root=ROOT):
    data=read(root/"registry/gap_routes.json")
    catalog=read(root/"registry/tools.json")
    tools={x["id"]:x for x in catalog["entries"]}
    routes={}
    for r in data["routes"]:
        if r["id"] in routes: raise ValueError("Duplicate route "+r["id"])
        if any(t not in tools for t in r["tools"]): raise ValueError("Unknown candidate in "+r["id"])
        routes[r["id"]]=r
    return routes,tools
def case_path(root,slug):
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*",slug): raise ValueError("Invalid target slug")
    return root/"investigations"/slug
def plan(register,routes,tools):
    out=[]
    for x in register.get("items",[]):
        r=routes.get(x.get("route_id"))
        if not r: raise ValueError("Unknown gap route for "+str(x.get("id")))
        out.append({"gap_id":x.get("id"),"feature_id":x.get("feature_id"),"obligation_id":x.get("obligation_id"),"route_id":r["id"],"priority":x.get("priority"),"limitation":x.get("limitation"),"allowed_scope":x.get("allowed_scope"),"candidate_tools":[{"id":t,"url":tools[t]["url"],"status":tools[t]["runtime_status"]} for t in r["tools"]],"required_input":r["input"],"method":r["method"],"acceptance":r["acceptance"],"boundary":r["boundary"],"execution_note":"Candidate plan only. Verify scope, version, license, fixture and target compatibility before use. If restricted, no probing; use permitted evidence or independent alternatives."})
    return {"target_slug":register.get("target_slug"),"assessment":register.get("assessment"),"plans":out,"target_accessed":False,"tools_executed":False}
def nonempty(x): return isinstance(x,str) and bool(x.strip())
def audit(register,routes,slug=None):
    errors=[]; unresolved=[]; seen=set()
    if register.get("schema_version")!=1: errors.append("Unsupported schema")
    if slug and register.get("target_slug")!=slug: errors.append("Target slug mismatch")
    assessment=register.get("assessment")
    items=register.get("items")
    if not isinstance(items,list): return {"valid":False,"errors":["items must be a list"],"unresolved":[],"structural_only":True}
    if assessment=="PENDING": errors.append("Gap assessment pending")
    elif assessment=="NO_GAPS":
        if items or not nonempty(register.get("no_gaps_reason")): errors.append("NO_GAPS requires empty register and scoped rationale")
    elif assessment=="ASSESSED":
        if not items: errors.append("ASSESSED requires at least one gap")
    else: errors.append("Invalid assessment")
    for x in items:
        if not isinstance(x,dict): errors.append("Invalid gap object"); continue
        i=x.get("id"); prefix=str(i)+": "
        if not nonempty(i) or i in seen: errors.append(prefix+"Missing or duplicate ID")
        if isinstance(i,str): seen.add(i)
        for k in ("feature_id","obligation_id","allowed_scope","acceptance","residual","reason"):
            if not nonempty(x.get(k)): errors.append(prefix+"Missing "+k)
        for k,allowed in (("route_id",routes),("priority",{"critical","high","normal"}),("limitation",LIMITS),("knowledge_status",KNOWLEDGE),("functional_status",FUNCTION),("disposition",DISPOSITION)):
            if x.get(k) not in allowed: errors.append(prefix+"Invalid "+k)
        for k in ("evidence","hypotheses","attempts"):
            if not isinstance(x.get(k),list): errors.append(prefix+k+" must be a list")
        e=x.get("evidence") or []; a=x.get("attempts") or []
        f=x.get("functional_status"); k=x.get("knowledge_status"); d=x.get("disposition")
        if k in {"DOCUMENTED","OBSERVED"} and not e: errors.append(prefix+"Direct knowledge requires evidence references")
        if f=="PASS" and (not e or not any(isinstance(v,dict) and v.get("result")=="PASS" and nonempty(v.get("receipt")) for v in a)): errors.append(prefix+"Functional PASS requires evidence and pass receipt")
        if d=="RESOLVED" and f!="PASS" and k not in {"DOCUMENTED","OBSERVED"}: errors.append(prefix+"Resolved requires scoped functional pass or direct knowledge")
        if d=="RESOLVED" and f in {"FAIL","BLOCKED","DEFERRED"}: errors.append(prefix+"Failed or blocked functionality cannot be resolved")
        if f!="PASS" or k in {"UNKNOWN","BLOCKED","INFERRED"}: unresolved.append({"id":i,"priority":x.get("priority"),"knowledge_status":k,"functional_status":f,"disposition":d})
        if x.get("priority")=="critical" and d in {"OPEN","TEST"}: errors.append(prefix+"Critical gap requires explicit handoff disposition")
    return {"valid":not errors,"errors":errors,"unresolved":unresolved,"gap_count":len(items),"structural_only":True,"functional_equivalence_certified":False}
def main():
    p=argparse.ArgumentParser(description=__doc__); sub=p.add_subparsers(dest="command",required=True)
    for name in ("plan","audit"): sub.add_parser(name).add_argument("--slug",required=True)
    a=p.parse_args()
    try:
        routes,tools=load_routes()
        g=read(case_path(ROOT,a.slug)/"GAP_REGISTER.json")
        if g.get("target_slug")!=a.slug: raise ValueError("Target slug mismatch")
        result=plan(g,routes,tools) if a.command=="plan" else audit(g,routes,a.slug)
        print(json.dumps(result,indent=2));return 2 if result.get("valid") is False else 0
    except (OSError,ValueError,KeyError,TypeError) as e: print(str(e),file=sys.stderr);return 1
if __name__=="__main__": raise SystemExit(main())
