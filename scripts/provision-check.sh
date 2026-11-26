#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
"${PYTHON:-python3}" - "$@" <<'PY'
import json,sys
from pathlib import Path
from src.orchestrator.capability_matrix import CapabilityMatrix
catalog=json.loads(Path("registry/tools.json").read_text())
manifest=json.loads(Path("routes/provisioning.json").read_text())
graphs=json.loads(Path("routes/stages.json").read_text())["graphs"]
ids={e["id"] for e in catalog["entries"]}
assert set(manifest)=={p for g in graphs.values() for s in g for rung in s["ladder"] for p in rung["providers"]}
assert all(v["registry_id"] is None or v["registry_id"] in ids for v in manifest.values())
matrix=None if "--manifest-only" in sys.argv else CapabilityMatrix.discover(catalog)
if matrix:
    print("HOST "+json.dumps(matrix.host.__dict__,sort_keys=True))
for name,item in sorted(manifest.items()):
    key=item["registry_id"]
    if matrix is None: status,reason="NOT_CHECKED","manifest-only"
    elif name in ("github_search","browser_research","knowledge_retrieval"):
        status,reason="UNAVAILABLE","discovery adapter runtime authorization/backend not configured; fixture tests separate"
    elif key in matrix.records:
        r=matrix.records[key];status,reason=r.status.value,r.reason
    else:status,reason="UNAVAILABLE","no reviewed runtime probe"
    print(f"{name} | {status} | {reason} | {item['install']} | {item['tested_version']} | {item['host']}")
print("No installation performed; version/health is not analysis verification.")
PY
