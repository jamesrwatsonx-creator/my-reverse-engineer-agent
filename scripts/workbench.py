#!/usr/bin/env python3
"""Local scaffold and diagnostics only. No external network or install."""
import argparse, datetime, json, pathlib, re, shutil, subprocess, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
KINDS=("web","desktop","mobile","extension","api","agent","repository","game","data","other")
MODES=("research","selected","fidelity","improve")
FILES=("README.md","features.md","experience.md","architecture.md","evidence.md","capabilities.md","opportunities.md","STATUS.md","GAP_MATRIX.md","SCENARIOS.md","TOOL_PLAN.md","HANDOFF.md","LAUNCH.md","BRIEF.json","INTERVIEW.md","CONTEXT.json","DECISIONS.md","REUSE_LOG.md","LEARNING_DELTA.json","TRANSFERS.md","FEEDBACK.md","UPSTREAM_REVIEW.md")
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def dump(p,v):
    tmp=p.with_suffix(p.suffix+".tmp")
    tmp.write_text(json.dumps(v,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    tmp.replace(p)
def slug(s):
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*",s): raise ValueError("Invalid lowercase kebab-case slug")
    return s
def plan(kind,root=ROOT):
    if kind not in KINDS: raise ValueError("Unknown kind")
    return [e for e in load(root/"registry/tools.json")["entries"] if kind in e["kinds"] or "all" in e["kinds"]]
def prepare(a,root=ROOT):
    s=slug(a.slug); folder=root/"investigations"/s
    if folder.exists(): raise ValueError("Target exists; update manually without overwriting")
    index_path=root/"registry/index.json"; index=load(index_path); records=index["investigations"]
    if any(e["slug"]==s for e in records): raise ValueError("Already registered")
    selected=plan(a.kind,root); now=datetime.datetime.now(datetime.timezone.utc).isoformat()
    folder.mkdir(parents=True)
    dump(folder/"BRIEF.json",{"slug":s,"name":a.name,"target":a.target,"kind":a.kind,"mode":a.mode,"goal":a.goal,"created_at":now,"authorization":"UNCONFIRMED; permitted public research only until scoped","build_authorized":False,"destination":None,"acceptance":[],"constraints":[],"owner_questions":[]})
    dump(folder/"CONTEXT.json",{"instruction_revision":None,"tool_registry_revision":None,"knowledge_revision":None,"retrieved_ids":[],"planned_tools":[x["id"] for x in selected],"upstream_review":"UPSTREAM_REVIEW.md","note":"Fill actual commit references and upstream review before launch; scaffold only"})
    dump(folder/"LEARNING_DELTA.json",{"schema_version":1,"target_slug":s,"assessment":"PENDING","no_change_reason":None,"items":[]})
    content={"UPSTREAM_REVIEW.md":"# Upstream freshness review\nPENDING. Before launch or REA execution, follow docs/UPSTREAM_REVIEW.md and docs/REPLIT.md. Record actual dated sources, changes, scope, decision and blockers; no review performed by scaffold.",
    "INTERVIEW.md":"# Owner interview\nOriginal goal recorded in BRIEF.json. Add dated exact non-sensitive Q&A and changes; no answers inferred.",
    "DECISIONS.md":"# Decisions\nPending owner decisions; record alternatives, rationale and consequences.",
    "REUSE_LOG.md":"# Prior knowledge reuse\nPending retrieval. Record IDs, adaptations, outcomes and evidence.",
    "TRANSFERS.md":"# Transfer history\nNo production repo transfer recorded.",
    "FEEDBACK.md":"# Production feedback\nNo production results recorded.",
    "README.md":"# "+a.name+"\nPLANNED; see BRIEF.json and LAUNCH.md.",
    "features.md":"# Feature atlas\nUNKNOWN; source-backed IDs pending.",
    "experience.md":"# UX, states and motion\nUNKNOWN.",
    "architecture.md":"# Architecture\nUNKNOWN; separate observation from hypothesis.",
    "evidence.md":"# Evidence ledger\nNo observations yet.",
    "capabilities.md":"# Candidate capabilities\nNo verified alternatives yet.",
    "opportunities.md":"# Owner-aligned opportunities\nPending research.",
    "STATUS.md":"# Status\nPLANNED; no tools or target tests run. Confirm scope and preflight.",
    "GAP_MATRIX.md":"# Gap matrix\nFeature ID, evidence, test, residual unknown, result and disposition.",
    "SCENARIOS.md":"# Scenarios\nSeed normal/failure/roles/held-out cases after reconnaissance.",
    "TOOL_PLAN.md":"# Candidate tool plan\n"+"\n".join("- "+x["id"]+": "+x["purpose"]+" — NOT_RUN" for x in selected),
    "HANDOFF.md":"# Handoff\nPending contracts, evidence, coverage, decision and plan.",
    "LAUNCH.md":(root/"templates/LAUNCH.md").read_text(encoding="utf-8")+"\nSelected folder: investigations/"+s+"/. BRIEF.json contains exact owner goal."}
    for n,c in content.items(): (folder/n).write_text(c+"\n",encoding="utf-8")
    (folder/"handoff").mkdir()
    (folder/"handoff/README.md").write_text("# Handoff package\nNot prepared. See docs/TRANSFER_PROTOCOL.md.\n",encoding="utf-8")
    (folder/"features").mkdir()
    (folder/"features/README.md").write_text("# Feature dossiers\nUse templates/FEATURE-DOSSIER.md.\n",encoding="utf-8")
    records.append({"slug":s,"name":a.name,"type":a.kind,"url":a.target,"status":"PLANNED","last_reviewed":now[:10],"summary":"Prepared; no target evidence yet.","tags":[a.kind,a.mode]})
    dump(index_path,index); return folder
def validate(s,root=ROOT):
    f=root/"investigations"/slug(s); missing=[n for n in FILES if not (f/n).is_file()]
    if missing: return {"valid":False,"missing":missing,"note":"Legacy folders may need migration"}
    b=load(f/"BRIEF.json")
    return {"valid":b.get("slug")==s and b.get("kind") in KINDS and b.get("mode") in MODES,"structural_only":True,"target_verified":False}
def preflight(kind):
    names=["git","python","node","npm","rea"]+(["java"] if kind in ("desktop","mobile","game") else [])
    out={}
    for n in names:
        exe=shutil.which(n)
        if not exe: out[n]={"status":"MISSING"}; continue
        try:
            p=subprocess.run([exe,"-version" if n=="java" else "--version"],capture_output=True,text=True,timeout=10)
            out[n]={"status":"FOUND" if p.returncode==0 else "CHECK_FAILED","version":(p.stdout or p.stderr).splitlines()[:2]}
        except (OSError,subprocess.TimeoutExpired): out[n]={"status":"CHECK_FAILED"}
    return {"kind":kind,"diagnostic_only":True,"tools":out,"note":"No provider fixture tested; follow TOOLCHAIN.md."}
def main():
    p=argparse.ArgumentParser(description=__doc__); sub=p.add_subparsers(dest="cmd",required=True)
    q=sub.add_parser("prepare")
    for k in ("slug","name","target","goal"): q.add_argument("--"+k,required=True)
    q.add_argument("--kind",choices=KINDS,required=True); q.add_argument("--mode",choices=MODES,default="research")
    for cmd in ("plan","preflight"): sub.add_parser(cmd).add_argument("--kind",choices=KINDS,required=True)
    sub.add_parser("validate").add_argument("--slug",required=True)
    a=p.parse_args()
    try:
        if a.cmd=="prepare": print(prepare(a))
        elif a.cmd=="plan": print(json.dumps(plan(a.kind),indent=2))
        elif a.cmd=="preflight": print(json.dumps(preflight(a.kind),indent=2))
        else:
            r=validate(a.slug); print(json.dumps(r,indent=2)); return 0 if r["valid"] else 1
    except (ValueError,OSError,KeyError) as e: print(str(e),file=sys.stderr); return 1
    return 0
if __name__=="__main__": raise SystemExit(main())
