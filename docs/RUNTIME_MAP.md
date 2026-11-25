# Repository runtime map

Immutable baseline [5d7119db5ea16d4466a9d80f13e6b274c6dfc6f7](https://github.com/jamesrwatsonx-creator/my-reverse-engineer-agent/tree/5d7119db5ea16d4466a9d80f13e6b274c6dfc6f7), tree c1cd8781ef71bff9c52ecf99ea95043cbfd1b17c. 57 tracked files; all source blobs fetched via GitHub during audit (some long documents reviewed by extracted sections; not a line-by-line semantic proof). No execution engine, provider adapter, evidence database or supervisor exists. No local checkout: container DNS cannot resolve GitHub. Existing Python consists of four utility scripts and four test modules. Line numbers refer to baseline, not this revision.

## File inventory and actual structure
| Path | Actual content / schema |
|---|---|
| .github/workflows/workbench.yml | GitHub Actions push/PR, ubuntu-latest, checkout@v4/setup-python@v5, Python 3.11, unittest discovery and web plan; structural only. |
| .gitignore | Patterns for env, keys, credential/session/token files, node_modules, venv, bytecode, OS artifacts; not complete secret policy. |
| AGENTS.md | Markdown operating contract: freshness, all-resource review, gap register, scoped permission, required target files, process, learning and transfer; statuses and evidence vocabulary. |
| CLAUDE.md | Agent entrypoint referencing AGENTS, scoped brief, preflight, upstream and catalog refresh. |
| README.md | Workbench overview, commands, research/build separation, learning and advanced routes. |
| docs/ADVANCED_ANALYSIS.md | Upstream reconciliation, provider cards, failure taxonomy, isolation and fallback proposals; already records CLI cache. |
| docs/CHATGPT_PROJECT.md | Target preparation and project instruction workflow; not executable. |
| docs/COMPARATIVE_EVALUATION.md | Comparison JSON: context_id, fixture_id, baseline/challenger {id, context_id, fixture_id, gates, metrics}; metrics {value,unit,direction,tolerance,n}; gates functional/security/license/authorization/fidelity. |
| docs/FIDELITY_AND_HANDOFF.md | Evidence ID/source/date/actor/tool/permission/steps/artifact/hash/result/confidence; fidelity obligations feature/priority/outcome/scenario/tolerance/source/fixture/result; native REA comparison and handoff. |
| docs/GAP_CLOSURE.md | Gap approach matrix with evidence and independent acceptance; residual uncertainty. |
| docs/GAP_ENGINE.md | Gap register v1 and planner/audit; documented/observed direct knowledge may resolve without functional pass (conflict). |
| docs/GAP_TOOL_RECIPES.md | Candidate tool recipes, fixture acceptance, proposed compositions; no adapters. |
| docs/INITIAL_RESOURCE_REVIEW.md | Dated resource evolution leads and candidate tests. |
| docs/INTAKE.md | Owner target intake, permanent interview/history and preparation. |
| docs/LEARNING.md | Capability, method, composition, negative knowledge and review lifecycle, comparison and governance. |
| docs/LEARNING_RECORD_FORMAT.md | LEARNING_DELTA v1: schema_version,target_slug,assessment,no_change_reason,items. Items id,capability_id,kind,proposer,summary,context,limitations,aliases,evidence [{path,sha256}],fixture_receipt,fixture_result,license_review,privacy_review,optional comparison and claims_improvement. |
| docs/REFERENCE_PROJECTS.md | REA-LINDY/Big_Idea lineage; source references not target findings. |
| docs/REPLIT.md | Optional hosted build/test candidate and selection checklist; no verified runtime. |
| docs/RESOURCE_AUDIT.md | Resource reconciliation, benchmark and challenge leads; not local results. |
| docs/RESOURCE_FRESHNESS.md | Full catalog, owner sources, source history and refresh receipts protocol. |
| docs/STATUS.md | Dated upgrade/structural status and advanced expansion notes. |
| docs/TARGET_PLAYBOOKS.md | Target-type routing table and mixed/specialized playbooks. |
| docs/TOOLCHAIN.md | Candidate selection, provider cards, versions, host checks and promotion sequence. |
| docs/TRANSFER_PROTOCOL.md | Nine-file handoff allowlist, manifest, approved destination, transfer receipts and feedback; no automatic build. |
| docs/UPSTREAM_REVIEW.md | Dated upstream/release/fork/installed schema review receipt and adoption/defer policy. |
| docs/WORKFLOW.md | Stage gates from initialize to handoff and optional build/feedback; no executable DAG. |
| investigations/README.md | Stable slug and case folder conventions. |
| investigations/livekit-cloud/README.md | Blocked authenticated project, partial documented findings; next authorized inspection. |
| investigations/livekit-cloud/architecture.md | Proposed flow, service ownership, entities, security/build gates; project config unknown. |
| investigations/livekit-cloud/capabilities.md | Portable capability and buy/integrate/build decisions. |
| investigations/livekit-cloud/evidence.md | Dated evidence log; public documentation, user requirements and unknown authenticated details. |
| investigations/livekit-cloud/experience.md | Proposed UX and testable flows; no observed console screens. |
| investigations/livekit-cloud/features.md | Documented LiveKit surfaces, proposed product features and unknowns. |
| investigations/livekit-cloud/opportunities.md | Inferred pilot, sequence, validation gates and next actions. |
| knowledge/capabilities/README.md | Empty scaffold for validated capability cards. |
| knowledge/compositions/README.md | Empty scaffold for tested chains. |
| knowledge/evaluations/README.md | Empty scaffold for held-out comparison receipts. |
| knowledge/index.json | schema_version:int=1, description:string, records:[], review_history:[]; no validated entries. |
| knowledge/methods/README.md | Empty scaffold for validated methods. |
| knowledge/negative/README.md | Empty scaffold for confirmed failures and reversal conditions. |
| registry/gap_routes.json | schema_version:int, description:string, routes:list[object]; id,description,input,method,acceptance,boundary strings; tools:list[str]. 33 routes, no trigger/signature/layer field. |
| registry/index.json | schema_version:int,repository:string,description:string,investigations:list[{slug,name,type,url,status,last_reviewed,summary:string,tags:list[str]}]; one LiveKit record BLOCKED. |
| registry/source_baseline.json | schema_version,review_date,scope,counts,records; 179 tracked, 113 heads observed, 5 blocked, 61 not checked, 20 releases observed. Records repository, head_status, head_sha,release_status,release_tag,reviewed_sha,capability_review,runtime_status; optional previous_observed_sha,observed_comparison,default_branch. Not health proof. |
| registry/tools.json | schema_version,reviewed,entries:list; id,url,kinds:list[str],purpose,source_status,runtime_status,pin,license_review; optional related_sources[{url,relationship}],notes,previous_url,resource_type,reported_license. 152 unique candidates/reference entries; all runtime NOT_RUN. |
| scripts/gap_engine.py | read,load_routes,case_path,fallback_policy,plan,audit,main; deterministic plan only. No execution or signature detection. |
| scripts/intelligence.py | Safe artifact refs/hash, search, compare, audit, independent review, package generation/verification; no automatic execution or promotion. |
| scripts/resource_refresh.py | Catalog and previous source records -> GitHub gh api metadata/head/release/compare, lineage and bounded results. Writes immutable report. Not deep/runtime review. |
| scripts/workbench.py | Scaffold, plan, validate, version-only preflight; no external network except installed command execution for version checks. |
| templates/FEATURE-DOSSIER.md | Feature ID/status, UX, I/O, dependencies, evidence, candidate receipts, held-out test, residual. |
| templates/HANDOFF-README.md | Manifest schema source_repo,source_commit,target_slug,destination,readiness,package_version,approval_ref,files[{path,sha256}]. |
| templates/LAUNCH.md | Agent launch prompt with upstream/fixture/scope gates. |
| templates/LEARNING-ITEM.md | Learning record fields, comparison, reviewer, limitations and next verification. |
| templates/investigation.md | Markdown sections for seven original case files, evidence table and proposed architecture. |
| tests/test_gap_engine.py | Route coverage, plan nonexecution, fallback, independent pass/unknown, missing receipt, blocked, critical/pending, no gaps rationale. |
| tests/test_intelligence.py | Learning pending/no-change, comparison, independent review and receipts, package integrity, path escape. |
| tests/test_resource_refresh.py | Source baseline coverage, fork discovery, blocked preservation, URL filtering with fake API. |
| tests/test_workbench.py | Routing, scaffold, invalid slug, no implicit authorization and preserved index. |

## Generated schemas and actual interfaces

- GAP_REGISTER v1: schema_version:int,target_slug:str,assessment:PENDING/ASSESSED/NO_GAPS,no_gaps_reason:null|string,items:list. Item strings id,feature_id,obligation_id,route_id,priority,limitation,allowed_scope,knowledge_status,functional_status,acceptance,residual,disposition,reason; lists evidence,hypotheses,attempts. Evidence item type not validated; attempt PASS needs result and nonempty receipt only. Knowledge DOCUMENTED/OBSERVED/INFERRED/UNKNOWN/BLOCKED; function NOT_RUN/PASS/FAIL/BLOCKED/DEFERRED; disposition OPEN/TEST/RESOLVED/BLOCKED/DEFERRED; limitation missing-evidence/tool-coverage/restricted/non-identifiable/budget/unavailable-data. Planner returns target_slug,assessment,plans,target_accessed=false,tools_executed=false; each plan gap/feature/obligation/route IDs,priority,limitation,allowed_scope,candidate_tools[{id,url,status}],required_input,method,acceptance,boundary,fallback_policy{steps,provider_execution_allowed:false},execution_note. Audit returns valid/errors/unresolved/gap_count/structural_only/functional_equivalence_certified=false (early malformed list lacks some fields).
- BRIEF: slug,name,target,kind,mode,goal,created_at,authorization strings; build_authorized=false,destination=null,acceptance/constraints/owner_questions arrays. CONTEXT: instruction_revision,tool_registry_revision,knowledge_revision initially null, retrieved_ids/planned_tools lists, upstream_review/gap_register/note strings. LEARNING_DELTA above. Legacy LiveKit folder lacks these newer generated records; do not silently migrate or invent evidence.
- intelligence.compare returns result/reason/metrics/structural_comparison_only. Learning review rows id,target_slug,capability_id,kind,summary,context,limitations,aliases,status,reviewer,reason,review_receipt,evidence,fixture_receipt,comparison,reviewed_at. Review decisions validated/rejected/needs-retest/deprecated. Manifest readiness PARTIAL/BUILD_READY is a claim, verification integrity only. No normalized ProviderResult or EvidenceEntry schema.
- Resource report includes counts tracked/head_observed/blocked/releases_observed; records also metadata_status, canonical_repository, default_branch, archived, license, lineage, commit_date/latest_commit_title, head_error, release_date/url/notes, head_changed and comparison objects where observed. Previous report preserves prior observed/reviewed heads, not actual runtime health.
- Workbench.validate returns valid/missing/note or valid/structural_only/target_verified=false. preflight returns kind,diagnostic_only,tools map of status/version,note; never fixture PASS.

## Terminal and interception points

No code currently transitions a gap to BLOCKED/FAIL/UNKNOWN during provider execution. Those states are input labels or scaffold text. A CLI exit is terminal for the command, not the analytical obligation. Distinguish correction, retry, alternate authorized evidence and true boundary abstention.

| Baseline call site | Trigger and actual outcome | Retry/terminal decision |
|---|---|---|
| scripts/gap_engine.py:16–17 load_routes | duplicate route / unknown tool raises ValueError | correct catalog; retry; no gap transition |
| :21 case_path | invalid slug | correct input; no retry unchanged |
| :23–34 fallback_policy | restricted lane stops; non-identifiable/unavailable data records unknown and independent model; budget recovery; all plans disallow execution | restricted original lane terminal while scope unchanged; non-identifiable original fact terminal under current evidence; alternate independent functionality separate; budget retry conditional |
| :40 plan | unknown route raises ValueError | correct explicit route; retry |
| :46–65 audit | schema/slug/assessment/item/field/enum errors; malformed list early return false :50 | input correction; no gap transition |
| :67–73 audit | wrong lists, missing direct evidence/PASS receipt, inconsistent RESOLVED; :72 permits direct knowledge without functional pass | retry with verified receipt or retain unresolved; migration required later |
| :74 audit | functional not PASS or knowledge UNKNOWN/BLOCKED/INFERRED appended to unresolved | reporting only; not terminal |
| :75–76 audit | critical OPEN/TEST invalid; BLOCKED/DEFERRED allowed with reason; structural-only outcome | handoff can remain partial; not proof of terminality |
| :84–88 main | slug mismatch; invalid audit exit 2; exception exit 1 | correction/retry; no failure ledger |
| scripts/workbench.py:14,17,21,23 | invalid slug/kind, existing folder/registered target | fix input; duplicate refuses overwrite, use explicit migration |
| :37–44 prepare | UNKNOWN scaffold, planned and gap instructions | not observations; pending |
| :58–60 validate | missing files or brief mismatch false | retry after migration |
| :66,69–71 preflight | missing executable, nonzero version, OSError or timeout CHECK_FAILED | host remediation or alternate; not fixture health |
| :85–88 main | invalid validation / caught errors exit 1 | retry only after correction |
| scripts/resource_refresh.py:22–29 request/call | API nonzero, malformed JSON, OSError/timeout | retry with permission/budget or abstain; no provider evidence ledger |
| :42–46 scan | defaults BLOCKED/NOT_CHECKED/NOT_RUN; bad metadata/invalid canonical skips | source access correction; preserve previous |
| :55–63 scan | no valid head / release -> head_error or release diagnostic | bounded retry; release absence not failure of capability |
| :67–76 scan | compare missing or inaccessible -> BLOCKED reason | retry if accessible; no update adoption |
| :84,89–91 main | refuse overwrite, blocked count exit 2, errors exit 1 | new report path, fix/retry; immutable old report |
| scripts/intelligence.py:13–21,26 safe_file/ref/search | unsafe/missing/hash mismatch or empty query raises | fix legitimate evidence/input, never bypass path boundary |
| :34–50 compare | context/fixture mismatch, hard gates fail, metric sets/definitions/values invalid -> INCOMPARABLE; DOMINATES etc not gate | re-evaluate on equivalent valid fixtures, never turn into PASS |
| :54–60 item_check | missing fields/kind/evidence or hash failure | repair evidence; no promotion |
| :64–81 audit | scaffold/assessment/context/retrieval/item/duplicate errors -> invalid; caught errors retained as issues | retry corrected record |
| :84–105 review | invalid decision, missing rationale, incomplete/audit failure, nonunique item, same reviewer/receipt, absent fixture, license/privacy/comparison fail -> ValueError | remediation or reject/defer; independent reviewer required |
| :107–112 review | explicit rejected/needs-retest/deprecated review row, not gap state | retain history; reevaluate only with new evidence |
| :115–119 verify_package | metadata/allowlist/hash errors; successful integrity only | correct/republish reviewed package |
| :122–125 make_package | invalid metadata/readiness or manifest already exists | explicit version, no overwrite |
| :144–146 main | invalid report or caught errors exit 1 | correct or record unresolved; no provider ledger |
| registry/index.json; investigations/livekit-cloud/README.md and evidence.md | BLOCKED authenticated scope / UNKNOWN project details | terminal for current authorization only; authorized new evidence can reopen |

## Host and version inventory

TOOLCHAIN.md requires live REA npm version, doctor, providers and MCP tools/list, separately installed Ghidra (historical >=12.2 lead with matching full JDK, not a universal pin), actual Windows P0 and X11 capture limitations, isolated allowed loopback CDP and one driver (Playwright/Obscura/manual), actual fixture interop. GitHub/Atlas source pins are per receipt, not hardcoded runtime defaults. Optional Replit needs hosted compatibility, costs, export and data boundary check; no assumed REA/Ghidra support. Container engine for Testcontainers, dedicated approved labs for advanced native/VM lanes, license, egress, cleanup and supported host. Workbench hardcoded executable names git/python/node/npm/rea plus java for desktop/mobile/game, PATH resolution, 10s version probe. resource_refresh uses gh api and 45s timeout. CI uses ubuntu-latest/Python 3.11 (CI only). Candidate registry pins not assumed. New capability matrix must check OS, architecture, privileges/ptrace, JDK, display, browser profile, virtualization/KVM/container access, provider version and permission before use; no availability claim from documentation.

## All provider references

Every route tool resolves to a catalog ID. All catalog entries runtime_status NOT_RUN; no executable adapters in baseline. Distinguish documentation source_status from integrated status. Reference-only resources are not executable candidates. Each row below lists all route associations; dash = no route, not absent.

| ID | Registry source status | Runtime status | Route IDs |
|---|---|---|---|
| rea | metadata-reviewed | NOT_RUN (not integrated) | feature-discovery, frontend-motion, client-code, api-contract, binary-format, native-symbolic-analysis, code-deobfuscation, cross-platform-emulation, runtime-instrumentation, deterministic-replay, binary-protocol-inference, apple-platform-analysis, gpu-shader-analysis, local-model-analysis, realtime-media-protocol, embedded-firmware, resource-recovery, system-runtime-analysis |
| ghidra | metadata-reviewed | NOT_RUN (not integrated) | client-code, binary-format, native-symbolic-analysis, cross-platform-emulation, apple-platform-analysis, embedded-firmware, resource-recovery |
| craft | readme-reviewed | NOT_RUN (not integrated) | frontend-motion, backend-architecture |
| playwright | candidate-unverified | NOT_RUN (not integrated) | feature-discovery, frontend-motion, auth-permissions, edge-cases, realtime-media-protocol |
| playwright-mcp | candidate-unverified | NOT_RUN (not integrated) | — |
| obscura | metadata-reviewed | NOT_RUN (not integrated) | feature-discovery, frontend-motion |
| treg | candidate-unverified | NOT_RUN (not integrated) | integrations |
| omniget | candidate-unverified | NOT_RUN (not integrated) | feature-discovery |
| last30days | candidate-unverified | NOT_RUN (not integrated) | feature-discovery |
| jev-guard | candidate-unverified | NOT_RUN (not integrated) | — |
| jev-ultrafast | candidate-unverified | NOT_RUN (not integrated) | — |
| github | candidate-unverified | NOT_RUN (not integrated) | feature-discovery |
| rea-prompts | candidate-unverified | NOT_RUN (not integrated) | — |
| awesome-rea | candidate-unverified | NOT_RUN (not integrated) | — |
| mitmproxy | metadata-reviewed | NOT_RUN (not integrated) | api-contract |
| quicktype | candidate-unverified | NOT_RUN (not integrated) | api-contract, data-schema |
| openapi-generator | candidate-unverified | NOT_RUN (not integrated) | api-contract, backend-architecture |
| schemathesis | metadata-reviewed | NOT_RUN (not integrated) | api-contract, edge-cases |
| wiremock | candidate-unverified | NOT_RUN (not integrated) | api-contract, integrations |
| pact | candidate-unverified | NOT_RUN (not integrated) | api-contract |
| composio | metadata-reviewed | NOT_RUN (not integrated) | integrations |
| nango | metadata-reviewed | NOT_RUN (not integrated) | auth-permissions, integrations |
| activepieces | public-source-reviewed | NOT_RUN (not integrated) | integrations |
| airbyte | candidate-unverified | NOT_RUN (not integrated) | integrations |
| mcp-registry | candidate-unverified | NOT_RUN (not integrated) | integrations |
| n8n | candidate-unverified | NOT_RUN (not integrated) | integrations |
| keycloak | candidate-unverified | NOT_RUN (not integrated) | auth-permissions |
| authlib | candidate-unverified | NOT_RUN (not integrated) | auth-permissions |
| aalpy | metadata-reviewed | NOT_RUN (not integrated) | business-logic, async-workflow |
| learnlib | public-source-reviewed | NOT_RUN (not integrated) | business-logic |
| hypothesis | candidate-unverified | NOT_RUN (not integrated) | data-schema, business-logic, algorithm, binary-format, edge-cases, migration, native-symbolic-analysis, binary-protocol-inference |
| temporal | candidate-unverified | NOT_RUN (not integrated) | backend-architecture, async-workflow, deployment |
| sqlglot | candidate-unverified | NOT_RUN (not integrated) | data-schema |
| prisma | candidate-unverified | NOT_RUN (not integrated) | data-schema |
| dbt | candidate-unverified | NOT_RUN (not integrated) | data-schema |
| postgres | candidate-unverified | NOT_RUN (not integrated) | data-schema, deployment |
| sdv | metadata-reviewed | NOT_RUN (not integrated) | training-data, network-data |
| distilabel | metadata-reviewed | NOT_RUN (not integrated) | training-data |
| argilla | candidate-unverified | NOT_RUN (not integrated) | training-data |
| promptfoo | metadata-reviewed | NOT_RUN (not integrated) | algorithm, training-data, agent-behavior, local-model-analysis |
| deepeval | candidate-unverified | NOT_RUN (not integrated) | training-data, agent-behavior |
| ragas | candidate-unverified | NOT_RUN (not integrated) | training-data, agent-behavior |
| scikit-learn | candidate-unverified | NOT_RUN (not integrated) | algorithm |
| optuna | candidate-unverified | NOT_RUN (not integrated) | algorithm |
| networkx | candidate-unverified | NOT_RUN (not integrated) | network-data |
| neo4j | candidate-unverified | NOT_RUN (not integrated) | network-data |
| jadx | release-and-head-reviewed | NOT_RUN (not integrated) | client-code |
| apktool | candidate-unverified | NOT_RUN (not integrated) | — |
| ilspy | candidate-unverified | NOT_RUN (not integrated) | client-code |
| appium | candidate-unverified | NOT_RUN (not integrated) | — |
| axe | candidate-unverified | NOT_RUN (not integrated) | frontend-motion |
| tree-sitter | candidate-unverified | NOT_RUN (not integrated) | client-code, migration, code-deobfuscation |
| semgrep | candidate-unverified | NOT_RUN (not integrated) | client-code |
| opentelemetry | candidate-unverified | NOT_RUN (not integrated) | backend-architecture, async-workflow, performance, deployment |
| browser-use | candidate-unverified | NOT_RUN (not integrated) | — |
| stagehand | candidate-unverified | NOT_RUN (not integrated) | — |
| livekit | candidate-unverified | NOT_RUN (not integrated) | — |
| pipecat | candidate-unverified | NOT_RUN (not integrated) | — |
| hermes | candidate-unverified | NOT_RUN (not integrated) | agent-behavior |
| openviking | candidate-unverified | NOT_RUN (not integrated) | agent-behavior |
| postiz | candidate-unverified | NOT_RUN (not integrated) | — |
| grill-with-docs | candidate-unverified | NOT_RUN (not integrated) | — |
| leanrea | readme-reviewed | NOT_RUN (not integrated) | — |
| rea-lab | readme-reviewed | NOT_RUN (not integrated) | — |
| rea-casebook | readme-reviewed | NOT_RUN (not integrated) | — |
| rea-groundtruth | readme-reviewed | NOT_RUN (not integrated) | — |
| dsh-rea | metadata-reviewed | NOT_RUN (not integrated) | — |
| rea-video | metadata-reviewed | NOT_RUN (not integrated) | frontend-motion |
| automatisch | metadata-reviewed | NOT_RUN (not integrated) | — |
| dograh | metadata-reviewed | NOT_RUN (not integrated) | — |
| letta-code | metadata-reviewed | NOT_RUN (not integrated) | — |
| ghidra-mcp | source-index-listed | NOT_RUN (not integrated) | — |
| ida-pro-mcp | source-index-listed | NOT_RUN (not integrated) | — |
| rea-reconstruction-companion | source-index-listed | NOT_RUN (not integrated) | — |
| rea-python | source-index-listed | NOT_RUN (not integrated) | — |
| rea-case-index | source-index-listed | NOT_RUN (not integrated) | — |
| awesome-reverse-engineering | source-index-listed | NOT_RUN (not integrated) | — |
| replit | official-docs-reviewed | NOT_RUN (not integrated) | deployment |
| blender-agent-sdk | head-reviewed | NOT_RUN (not integrated) | — |
| daikon | docs-and-metadata-reviewed | NOT_RUN (not integrated) | business-logic |
| kaitai | docs-and-metadata-reviewed | NOT_RUN (not integrated) | binary-format, binary-protocol-inference, embedded-firmware |
| pm4py | docs-and-metadata-reviewed | NOT_RUN (not integrated) | async-workflow |
| fast-check | docs-and-metadata-reviewed | NOT_RUN (not integrated) | api-contract, business-logic, agent-behavior, edge-cases, migration, deterministic-replay |
| k6 | docs-and-metadata-reviewed | NOT_RUN (not integrated) | performance |
| locust | docs-and-metadata-reviewed | NOT_RUN (not integrated) | performance |
| testcontainers | docs-and-metadata-reviewed | NOT_RUN (not integrated) | api-contract, data-schema, auth-permissions, integrations, backend-architecture, async-workflow, performance, deployment, migration, isolated-execution |
| z3 | docs-and-metadata-reviewed | NOT_RUN (not integrated) | data-schema, auth-permissions, business-logic, algorithm, edge-cases, native-symbolic-analysis |
| tlaplus | docs-and-metadata-reviewed | NOT_RUN (not integrated) | business-logic, async-workflow, deterministic-replay |
| openrewrite | docs-and-metadata-reviewed | NOT_RUN (not integrated) | migration |
| kaitai-compiler | docs-and-metadata-reviewed | NOT_RUN (not integrated) | binary-format |
| kaitai-formats | docs-and-metadata-reviewed | NOT_RUN (not integrated) | binary-format |
| angr | candidate-unverified | NOT_RUN (not integrated) | client-code, native-symbolic-analysis, code-deobfuscation, resource-recovery |
| triton | candidate-unverified | NOT_RUN (not integrated) | native-symbolic-analysis, code-deobfuscation |
| qiling | candidate-unverified | NOT_RUN (not integrated) | cross-platform-emulation, embedded-firmware |
| unicorn | candidate-unverified | NOT_RUN (not integrated) | cross-platform-emulation |
| rz-ghidra | candidate-unverified | NOT_RUN (not integrated) | client-code, native-symbolic-analysis, resource-recovery |
| webcrack | candidate-unverified | NOT_RUN (not integrated) | client-code, code-deobfuscation |
| js-deobfuscator | candidate-unverified | NOT_RUN (not integrated) | code-deobfuscation |
| blackboxprotobuf | candidate-unverified | NOT_RUN (not integrated) | api-contract, binary-protocol-inference |
| pbtk | candidate-unverified | NOT_RUN (not integrated) | binary-format, binary-protocol-inference |
| wireshark | candidate-unverified | NOT_RUN (not integrated) | api-contract, binary-protocol-inference, realtime-media-protocol |
| ipsw | candidate-unverified | NOT_RUN (not integrated) | binary-format, apple-platform-analysis |
| ipsw-py | candidate-unverified | NOT_RUN (not integrated) | apple-platform-analysis |
| ipsw-skill | candidate-unverified | NOT_RUN (not integrated) | — |
| panda | candidate-unverified | NOT_RUN (not integrated) | deterministic-replay, system-runtime-analysis |
| rr | candidate-unverified | NOT_RUN (not integrated) | runtime-instrumentation, deterministic-replay, system-runtime-analysis |
| qbdi | candidate-unverified | NOT_RUN (not integrated) | runtime-instrumentation |
| libvmi | candidate-unverified | NOT_RUN (not integrated) | system-runtime-analysis |
| hyperdbg | candidate-unverified | NOT_RUN (not integrated) | system-runtime-analysis |
| firecracker | candidate-unverified | NOT_RUN (not integrated) | isolated-execution |
| bubblewrap | candidate-unverified | NOT_RUN (not integrated) | isolated-execution |
| nsjail | candidate-unverified | NOT_RUN (not integrated) | isolated-execution |
| qemu | candidate-unverified | NOT_RUN (not integrated) | cross-platform-emulation, isolated-execution, embedded-firmware, system-runtime-analysis |
| d810-ng | candidate-unverified | NOT_RUN (not integrated) | code-deobfuscation |
| renderdoc | candidate-unverified | NOT_RUN (not integrated) | gpu-shader-analysis |
| spirv-tools | candidate-unverified | NOT_RUN (not integrated) | gpu-shader-analysis |
| spirv-cross | candidate-unverified | NOT_RUN (not integrated) | gpu-shader-analysis |
| directx-shader-compiler | candidate-unverified | NOT_RUN (not integrated) | gpu-shader-analysis |
| netron | candidate-unverified | NOT_RUN (not integrated) | local-model-analysis |
| onnx | candidate-unverified | NOT_RUN (not integrated) | local-model-analysis |
| onnxruntime | candidate-unverified | NOT_RUN (not integrated) | local-model-analysis |
| litert | candidate-unverified | NOT_RUN (not integrated) | local-model-analysis |
| coremltools | candidate-unverified | NOT_RUN (not integrated) | local-model-analysis |
| aioquic | candidate-unverified | NOT_RUN (not integrated) | realtime-media-protocol |
| aiortc | candidate-unverified | NOT_RUN (not integrated) | realtime-media-protocol |
| eventsource-parser | candidate-unverified | NOT_RUN (not integrated) | api-contract, realtime-media-protocol |
| automatalib | candidate-unverified | NOT_RUN (not integrated) | business-logic, async-workflow |
| renode | candidate-unverified | NOT_RUN (not integrated) | cross-platform-emulation, embedded-firmware |
| littlefs | candidate-unverified | NOT_RUN (not integrated) | embedded-firmware |
| ollama | candidate-unverified | NOT_RUN (not integrated) | — |
| vllm | candidate-unverified | NOT_RUN (not integrated) | — |
| ghydramcp | candidate-unverified | NOT_RUN (not integrated) | — |
| pyghidra-mcp | candidate-unverified | NOT_RUN (not integrated) | — |
| jadx-mcp | candidate-unverified | NOT_RUN (not integrated) | — |
| awesome-ai-re | candidate-unverified | NOT_RUN (not integrated) | — |
| ecapture-reference | candidate-unverified | NOT_RUN (not integrated) | — |
| fritap-reference | candidate-unverified | NOT_RUN (not integrated) | — |
| scyllahide-reference | candidate-unverified | NOT_RUN (not integrated) | — |
| frida-dexdump-reference | candidate-unverified | NOT_RUN (not integrated) | — |
| drakvuf-reference | candidate-unverified | NOT_RUN (not integrated) | — |
| libmicrovmi-reference | candidate-unverified | NOT_RUN (not integrated) | — |
| hvmi-reference | candidate-unverified | NOT_RUN (not integrated) | — |
| vtil2-reference | candidate-unverified | NOT_RUN (not integrated) | — |
| triton-symbolic-reference | candidate-unverified | NOT_RUN (not integrated) | — |
| ghidra-alternative-reference | candidate-unverified | NOT_RUN (not integrated) | — |
| ghidra-headless-reference | candidate-unverified | NOT_RUN (not integrated) | — |
| mobile-skills-reference | candidate-unverified | NOT_RUN (not integrated) | — |
| x64dbg-mcp-reference | candidate-unverified | NOT_RUN (not integrated) | — |
| frida-mcp-reference | candidate-unverified | NOT_RUN (not integrated) | — |
| tenrec-reference | candidate-unverified | NOT_RUN (not integrated) | — |
| ida-instances-reference | candidate-unverified | NOT_RUN (not integrated) | — |
| agent-escape-bench-reference | candidate-unverified | NOT_RUN (not integrated) | — |
