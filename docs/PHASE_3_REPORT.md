# Phase 3 — deterministic DAG engine and backend discovery

**Review checkpoint:** branch `phase-3/dag-engine`, based on Phase 2 `c5290df969ec12edfe9bf17ae86fcdff78ff064f`. Main and Phase 2 are not modified. Synthetic target fixtures only. No supervisor, independent verification harness, real target analysis or other thirteen graphs implemented.

- [Compare against Phase 2](https://github.com/jamesrwatsonx-creator/my-reverse-engineer-agent/compare/phase-2/minimum-execution-foundation...phase-3/dag-engine)
- [Compare against main](https://github.com/jamesrwatsonx-creator/my-reverse-engineer-agent/compare/main...phase-3/dag-engine)

## 1. Implementation and coverage

| File | Implementation / test coverage |
|---|---|
| src/orchestrator/contracts.py | ObservationScope, ArtifactContract, payload references for fixture validation, typed discovery queries/results/candidates, DiscoveryKind, RATE_LIMITED/AUTH_MISSING. Existing constructor compatibility is retained through default fields. |
| src/orchestrator/evidence_store.py | Scoped conflict comparisons; legacy unscoped records retain prior semantics, never silently relabeled. Append-only discovery queries/results and DAG run trace, with stable receipt identifiers. Tests: test_observation_scope and test_discovery_providers; DAG trace readback. |
| src/orchestrator/executor.py | Pass explicit stage/question and input hash to attempt receipts. Prior bounded execution preserved. |
| src/orchestrator/dag_engine.py | Validate graph, reject cycles and duplicate IDs, check artifact payload digest and input/output field contracts, sorted ready queue, independent progress on exhaustion, terminal statuses, explicit conditional discovery event instances, exhaustion receipt linkage and persisted complete trace. Tests: test_dag_engine, including wrong body kind, independent stage, cycle, triggered discovery, missing observation, queue order and full two-graph synthetic smoke test. |
| src/providers/github_search_provider.py | Bounded GitHub CLI research with explicit opt-in live execution, injectable mocked runner, in-memory command cache and paced live calls. Metadata, README and issue sample, maintenance and license filtering, deterministic ordering independent of stars. Tests: archive rejection, copyleft risk, maintenance and star invariance. |
| src/providers/browser_research_provider.py | Authorized capture callback; sanitized HAR fixture projection into feature/capability-matched candidate endpoints and behavioral hypotheses; Tier 4 inferred, no target requests or browser automation implemented here. Test: cached HAR. |
| src/providers/knowledge_retrieval_provider.py | Prior matching discovery results and optionally validated learning cards first; optional injected web callback when no candidates match. Test: previous result reused, web callback not repeated. |
| routes/stages.json | Two proof-of-concept graphs in schema v2; four explicit paradigms per stage, ordered providers and signature-gated escalation. |
| routes/provisioning.json; docs/PROVISIONING.md; scripts/provision-check.sh | Manifest and read-only checks, graph coverage validation; no installation. test_provisioning. |
| tests/fixtures/phase3.json | Deterministic mocked GitHub, sanitized HAR and web search fixture. |
| src/orchestrator/circuit_breaker.py | Append-only per-provider circuit transitions; configurable failure threshold/cooldown; OPEN skip, bounded HALF_OPEN probe, CLOSED reset; analysis and discovery admission. |
| src/orchestrator/streaming_capture.py | Bounded fixture CDP IO.read/IO.close streaming to SHA-256-addressed files; capture-stage reference projection before evidence persistence. |
| tests/test_phase3_addendum.py; tests/fixtures/phase3-large-payload.txt | Five regression tests for ladder matching, circuit restart, half-open recovery, discovery admission, and 9,300-byte streaming fixture. |
| .github/workflows/workbench.yml | Existing suite plus provider compilation and uploaded provisioning output. |

### RED/GREEN evidence

- [RED commit](https://github.com/jamesrwatsonx-creator/my-reverse-engineer-agent/commit/782f150febcf72811593c92ccf1d3867a745bca7), [CI 45727640341](https://github.com/jamesrwatsonx-creator/my-reverse-engineer-agent/actions/runs/45727640341): 37 tests discovered, four expected errors (missing DAG module, missing discovery provider modules, missing ObservationScope, missing graph/manifest).
- [First implementation](https://github.com/jamesrwatsonx-creator/my-reverse-engineer-agent/commit/5352a1d5b736f79abb56a30da23f149e375726d7), [CI 45727856817](https://github.com/jamesrwatsonx-creator/my-reverse-engineer-agent/actions/runs/45727856817): 42 tests passed; compilation, planning, capability snapshot and provisioning succeeded.
- [Final implementation](https://github.com/jamesrwatsonx-creator/my-reverse-engineer-agent/commit/0e27ececc28a60a17b0e5904d0d49922dc19548d), [CI 45727952827](https://github.com/jamesrwatsonx-creator/my-reverse-engineer-agent/actions/runs/45727952827): 45 tests passed (0.511 s); compilation, workbench planning, capability snapshot, provisioning and upload succeeded. Test logs are direct observations. This was the pre-addendum baseline.
- [Addendum RED](https://github.com/jamesrwatsonx-creator/my-reverse-engineer-agent/actions/runs/45728124748): 46 tests discovered; expected import failure for missing circuit breaker in the addendum test module (streaming module also absent).
- [Addendum GREEN](https://github.com/jamesrwatsonx-creator/my-reverse-engineer-agent/actions/runs/45728226168): 49 tests passed.
- [Final implementation commit](https://github.com/jamesrwatsonx-creator/my-reverse-engineer-agent/commit/e36a5f734ecdd7ea75aabc32696098b89a7d4ac3), [CI 45728304206](https://github.com/jamesrwatsonx-creator/my-reverse-engineer-agent/actions/runs/45728304206): 50 tests passed (1.089 s), compilation, workbench planning, capability snapshot, provisioning and artifact upload succeeded. This report-only commit records that observed result.

## 2. Archetype graphs — ladder schema v2

### cloud-api

| Stage | Layer | Preconditions / trigger | Ordered ladder (nonempty rungs) | Input → output contract | Discovery event | Gate |
|---|---|---|---|---|---|---|
| capture | transport | root | R1: rea; R3: mitmproxy; R4:  → discover-alternative-providers | none → network-capture {"requests":null,"responses":null} | discover-alternative-providers | fixture-contract |
| protocol-classify | transport | capture | R1: rea, wireshark | network-capture {"requests":null,"responses":null} → protocol {"identifier":null} | — | fixture-contract |
| schema-infer | transport | protocol-classify, capture | R1: rea, blackboxprotobuf; R4:  → discover-alternative-providers | protocol {"identifier":null}; network-capture {"requests":null} → schema {"fields":null} | discover-alternative-providers | fixture-contract |
| state-machine | persistent-state | schema-infer | R4: aalpy, learnlib | schema {"fields":null} → state-machine {"states":null,"transitions":null} | — | fixture-contract |
| verify | persistent-state | state-machine | R1: rea; R4: hypothesis | state-machine {"states":null,"transitions":null} → verification {"fixture_result":"PASS"} | — | fixture-contract |
| discover-alternative-providers | static | EXHAUSTED | R4: github_search, knowledge_retrieval | exhaustion-receipt {"failure_signatures":null,"artifact_types_attempted":null} → discovery-candidates {"candidates":null} | — | fixture-contract |

### packed-binary

| Stage | Layer | Preconditions / trigger | Ordered ladder (nonempty rungs) | Input → output contract | Discovery event | Gate |
|---|---|---|---|---|---|---|
| fingerprint | static | root | R1: rea, ghidra | none → fingerprint {"format":null} | — | fixture-contract |
| unpack | static | fingerprint | R1: rea; R2: qiling; R4:  → discover-alternative-providers | fingerprint {"format":null} → binary {"artifact_id":null} | discover-alternative-providers | fixture-contract |
| emulation-decrypt | dynamic-dispatch | unpack | R2: qiling, unicorn; R4:  → discover-alternative-providers | binary {"artifact_id":null} → binary {"artifact_id":null} | discover-alternative-providers | fixture-contract |
| re-static | static | emulation-decrypt | R1: rea, ghidra | binary {"artifact_id":null} → function {"body_kind":"assembly","body":null} | — | fixture-contract |
| symbolic-resolve | dynamic-dispatch | re-static | R2: angr, triton; R4:  → discover-construction-brief | function {"body_kind":"assembly","body":null} → call-graph {"nodes":null,"edges":null,"unknown_edges":null} | discover-construction-brief | fixture-contract |
| verify | dynamic-dispatch | symbolic-resolve | R1: rea; R4: hypothesis | call-graph {"nodes":null,"edges":null} → verification {"fixture_result":"PASS"} | — | fixture-contract |
| discover-alternative-providers | static | EXHAUSTED | R4: github_search, knowledge_retrieval | exhaustion-receipt {"failure_signatures":null,"artifact_types_attempted":null} → discovery-candidates {"candidates":null} | — | fixture-contract |
| discover-construction-brief | persistent-state | UNRESOLVED | R4: browser_research, github_search, knowledge_retrieval | unresolved-gap {"observable_behavior":null,"undetermined_mechanism":null} → discovery-candidates {"candidates":null} | — | fixture-contract |

All stages declare four rungs: static, symbolic/emulation, live instrumentation, black-box/discovery. Empty rungs are explicitly inapplicable and bypassed, not fabricated provider attempts. The first applicable rung starts; subsequent applicable rungs require exhaustion plus intersection with that rung's trigger_signatures. PINNED, TIMEOUT_ADVERSARIAL and NONE are not automatic escalation triggers. The rung is recorded on each analysis attempt. Rung-four discovery remains a conditional DAG event, not an analytical PASS or automatic installation. The cloud capture stage declares IO.read, threshold 4096 bytes, chunks 1024 bytes, maximum 16384 bytes, and content-addressed disk storage for this PoC.

An input requirement of null means present and non-null; literal values must match exactly, including representation kind. The current contract checks fixture shape and content hash, not full JSON Schema, semantic verification or source authority. Graph PASS means local fixture contract passed; it does not mean functional equivalence. Discovery instances are keyed by template@origin stage. An untriggered template is SKIPPED. A failed prerequisite produces NOT_READY; a mismatched field produces UNSATISFIED_INPUT. Independent stages continue.

## 3. Discovery provider specifications

| Provider | Interface and guardrails | Verified test / remaining boundary |
|---|---|---|
| github_search | Capability + language query, gh auth status, search limited to 50, default deep-inspection cap 10, per-command timeout, bounded output, paced live invocations and in-memory cache. gh repo view, repository metadata, latest commit, README, issue sample. SPDX allowlist enforced locally; GPL/AGPL retained as ineligible high-risk records. Archived, stale, low-term-match, broad or service-coupled candidates rejected heuristically. No stars in ranking, no code execution. | Mocked fixtures pass; real authentication, API compatibility and current CLI flags NOT_RUN. GitHub open_issues_count can include pull requests; it is not a pure issue-only count. |
| browser_research | Capture callback; network-capture method selected from sanitized HAR. Feature matches based on capability tokens, method/status and endpoint URL stripped of query/fragment; unknown backend mechanisms remain unknown. Other named methods (GraphQL introspection, OpenAPI import, bundle analysis, browser automation) are method descriptors, not implemented capture adapters. Tier 4 inferred. | Cached HAR fixture passes. Live Playwright/network-capture plumbing not connected. Never overrides Tier 1 observation; Phase 4 must adjudicate and record discrepancies. |
| knowledge_retrieval | Consult prior noncontradicted discovery history by archetype + failure signature + capability, then compatible validated knowledge cards; if no candidates, invoke injected authorized web search callback. Return inferred research with named verification required. | Fixture proves reuse before web. No live general-web adapter configured. Existing legacy learning cards lack some context fields; only compatible cards accepted. |

The directive's OSS Bootstrap and api-anything patterns were followed as described in the directive; their full external skill/source files were not independently reviewed. Capability query validation rejects clone phrasing, URLs and repository selectors but is not a semantic classifier of every app-name query. Licensing and relevance checks are conservative screening, not legal or implementation proof. No provider is auto-integrated, and the ledger explicitly records no integrations.

Exhaustion is a scheduler event rather than a gap policy decision. Alternative discovery runs on matching exhausted stages and links actual attempts plus the exhaustion evidence ID. Construction discovery requires caller-provided UNRESOLVED classification and existing noncontradicted fixture observations. It produces candidate paths with verification requirements, not final verified briefs. No unbounded retry or autonomous candidate installation. A discovery health refusal is a skipped provider, not a fabricated invocation.

## 4. Provisioning

See [PROVISIONING.md](PROVISIONING.md), [manifest](../routes/provisioning.json), and [script](../scripts/provision-check.sh). The registry retains its 152 catalog entries. All 15 graph-referenced provider IDs have manifest records (three internal discovery adapter names map to registry entries or local code). No real analysis version was tested; instructions are candidate install paths, not version pins. Health is not analysis readiness. No installation was performed. The final implementation's GitHub Actions runner output follows (actual execution host, not the user's computer):

```text
HOST {"architecture": "x86_64", "display_present": false, "docker_reachable": true, "jdk_version": "openjdk version \"25.0.5\" 2026-10-20 LTS", "kvm_accessible": false, "os": "Linux", "ptrace_seize": true, "python_version": "3.11.18"}
aalpy | UNAVAILABLE | No approved provider-specific CLI/host probe; catalog entry only | python -m pip install aalpy | NOT_TESTED (provider analysis); fixture adapter tests only | supported Python; controlled oracle fixture
angr | UNAVAILABLE | No approved provider-specific CLI/host probe; catalog entry only | python -m pip install angr | NOT_TESTED (provider analysis); fixture adapter tests only | supported Python/architecture
blackboxprotobuf | UNAVAILABLE | No approved provider-specific CLI/host probe; catalog entry only | python -m pip install blackboxprotobuf | NOT_TESTED (provider analysis); fixture adapter tests only | supported Python; reviewed dependency/license
browser_research | UNAVAILABLE | discovery adapter runtime authorization/backend not configured; fixture tests separate | python -m pip install playwright; python -m playwright install chromium (optional capture backend) | NOT_TESTED (provider analysis); fixture adapter tests only | authorized capture callback; browser dependencies if used; HAR fixture needs only Python
ghidra | UNAVAILABLE | Binary not on PATH: analyzeHeadless | Download official Ghidra release and extract; use documented analyzeHeadless launcher | NOT_TESTED (provider analysis); fixture adapter tests only | supported OS and matching full JDK
github_search | UNAVAILABLE | discovery adapter runtime authorization/backend not configured; fixture tests separate | Install GitHub CLI via official OS package manager (e.g. apt install gh); gh auth login | NOT_TESTED (provider analysis); fixture adapter tests only | gh executable; explicit public-research authorization and token; rate budget
hypothesis | UNAVAILABLE | No approved provider-specific CLI/host probe; catalog entry only | python -m pip install hypothesis | NOT_TESTED (provider analysis); fixture adapter tests only | supported Python
knowledge_retrieval | UNAVAILABLE | discovery adapter runtime authorization/backend not configured; fixture tests separate | Included Python module; no package installation required | NOT_TESTED (provider analysis); fixture adapter tests only | SQLite ledger; optional approved web callback
learnlib | UNAVAILABLE | No approved provider-specific CLI/host probe; catalog entry only | Use Maven dependency de.learnlib:learnlib-distribution after reviewing official release | NOT_TESTED (provider analysis); fixture adapter tests only | matching JDK/Maven; fixture
mitmproxy | UNAVAILABLE | Binary not on PATH: mitmdump | python -m pip install mitmproxy | NOT_TESTED (provider analysis); fixture adapter tests only | supported Python; local authorized capture only
qiling | UNAVAILABLE | No approved provider-specific CLI/host probe; catalog entry only | python -m pip install qiling | NOT_TESTED (provider analysis); fixture adapter tests only | supported host/arch and reviewed fixture runtime
rea | UNAVAILABLE | Binary not on PATH: rea | npm install --global rea-agents | NOT_TESTED (provider analysis); fixture adapter tests only | Node.js/npm; provider-specific dependencies; CLI/MCP health
triton | UNAVAILABLE | No approved provider-specific CLI/host probe; catalog entry only | python -m pip install triton-library | NOT_TESTED (provider analysis); fixture adapter tests only | supported Python/architecture; distinguish from GPU Triton
unicorn | UNAVAILABLE | No approved provider-specific CLI/host probe; catalog entry only | python -m pip install unicorn | NOT_TESTED (provider analysis); fixture adapter tests only | supported host/arch
wireshark | UNAVAILABLE | Binary not on PATH: tshark | Install Wireshark/TShark via official OS package manager (e.g. apt install tshark on Debian/Ubuntu) | NOT_TESTED (provider analysis); fixture adapter tests only | OS package; authorized capture permissions
No installation performed; version/health is not analysis verification.
```

The runner can reach Docker and permit PTRACE_SEIZE on a disposable child; no display or KVM. All 15 graph providers were reported unavailable for real execution (missing CLI, unapproved probe, or unconfigured discovery backend/authorization). Fixture adapters were exercised independently. See [CI output and artifact](https://github.com/jamesrwatsonx-creator/my-reverse-engineer-agent/actions/runs/45728304206). A setup command is not a receipt. Resolve license, version, host compatibility and fixture before promotion.

## 5. Dossier contract and learning-store separation

The dossier is an approved, bounded build handoff. It contains verified results, honest unknowns, and construction briefs. The learning store contains raw failure receipts, contradiction records, discovery query/results, trace, strategy outcomes and reusable lessons. The build repository **never receives the learning store**; only sanitized evidence references and approved acceptance material cross the boundary. The final verification authority is a later harness, not discovery or scheduler PASS.

Each unknown dossier entry must contain:

1. Observable behavior and supporting fixture verification references.
2. Precisely named undetermined mechanism.
3. Approximation with provenance tier and explicit limitations.
4. Supporting evidence IDs and contradictions/residual uncertainty where applicable.
5. Independent implementation path naming candidate tools/repos and license/eligibility review.
6. Acceptance test (inputs, expected observable outcome, tolerance and authorized held-out fixture); execution and result remain separate.
7. If no defensible independent path exists, named reason for abstention.

An unknown with a construction brief is a deliverable, not a gap. An unknown with neither a construction brief nor a reason it cannot be built is a dossier defect. A discovered candidate is not yet a verified brief. Phase 4 should assemble conditional briefs with explicit status; Phase 5 should independently verify acceptance before promoting them. External claims never silently supersede stronger direct observations.

## 6. Discrepancies and limitations

- Phase 2 already had append-only evidence with conservative same-input conflicts, but no explicit question/artifact scope and no normalized payload field on Artifact. Added fields with backward-compatible defaults. Legacy unscoped records are not silently rewritten or conflated with new scoped evidence. Exact identical canonical records deduplicate; different providers/timestamps remain distinct provenance even if output agrees. Scoped comparisons use question and artifact identity; they do not require equal input hashes. Historical explicit contradiction links remain visible.
- The Phase 2 Stage contract used signature-specific repair lists. Phase 3 graph JSON uses explicit terminal-event discovery template references; the scheduler delegates each analysis stage to the existing executor with no internal repair routes, leaving supervisor repair policy separate. Exhaustion does not by itself prove an unresolved mechanism.
- Artifact payloads in these fixtures are canonical hashed mappings. Existing provider-specific Phase 2 fixture normalizers do not yet bind every new graph artifact schema. Fixture field checks are not real normalized interoperability tests, and full schema typing/authority must be added later.
- Backend discovery integration is fixture-proven; browser and general-web transports are injected callbacks, not production implementations. GitHub CLI can be opted into for direct authorized public research, but scheduler passes synthetic authorization in this phase. No live search or app access was used. Provision check correctly reports real discovery adapters unconfigured.
- The simple lexical relevance, recency and service-coupling filters are heuristics; no semantic guarantee of technical fit or license compatibility. Rate limit classification is based on command failure diagnostics; no live rate-limit behavior tested. Candidate metadata is retained, not a byte-for-byte archive of all provider CLI responses.
- DAG trace persistence is at run completion; crash-resume and transactional stage checkpoints are not implemented. Automatic contradiction detection scans stored entries and is not a production-scale indexing benchmark. Scope equality does not establish semantic contradiction of differing representations; callers must normalize the question and artifact identity.
- Conditional discovery attempts are recorded with links; no candidate selection, integration, or learning success policy is implemented. The caller supplies unresolved observations; the scheduler does not decide a gap is unfillable.
- Provisioned versions, operating-system support and command flags are unverified for real analytical execution. Existing health coverage remains incomplete for catalog libraries and hosted capabilities. Main and Phase 2 branches remain unchanged; comparison to main includes earlier phases.

## 7. Directive addendum A–C

See [AGENT_DIRECTIVE_PHASE_3_ADDENDUM.md](AGENT_DIRECTIVE_PHASE_3_ADDENDUM.md).

- A: v2 graph ladder replaces flat provider arrays on disk. Each of the four rungs has explicit trigger_signatures. The scheduler executes only the current applicable rung, matches observed exhaustion signatures before advancement, preserves ordered attempts with rung numbers, and conditionally releases discovery events. Legacy in-memory fixture definitions are accepted for regression compatibility only. A nonmatching signature stops escalation; the supervisor decides what next. A prior PASS stops the ladder. No auto-install, provider promotion or access escalation.
- B: the executor and discovery event path use the persistent CircuitBreaker. Default threshold is three consecutive unsuccessful attempts; configurable threshold and 60-second default cooldown. Caller-supplied timestamp makes test behavior deterministic. CLOSED success resets the count; OPEN skips without invocation or failed-attempt receipt; one HALF_OPEN probe after cooldown closes on success or opens on failure. Health refusal in a half-open discovery probe reopens without inventing an invocation. Circuit transitions are append-only with receipt IDs; the current state is derived from the latest event. This is a single-writer PoC. Receipt insertion and circuit transition are separate transactions, so crash-atomic recovery and distributed leases remain Phase 4 work. No claim of resume-after-any-failure.
- C: cloud-api capture has a streaming_capture spec. The synthetic provider supplies a stream handle and declared size; the injected IO.read/IO.close transport reads bounded chunks into a temporary disk file, checks the byte count, hashes captured bytes, and publishes the file by digest. Oversized inline metadata or a large declared size without a handle is rejected before evidence persistence. The artifact contains the reference metadata and its own metadata hash; payload_ref.sha256 identifies the bytes. The 9,300-byte fixture crosses the 4,096-byte threshold; both direct stream and DAG integration tests confirm multiple reads, exact content hash, disk reference, and no full body in the persisted DAG trace. No real CDP session was used. The cap is deliberately small for synthetic testing; production capture quotas, verified native REA retention/recovery, authorization and streaming transport wiring require qualification. The store and content files are not a distributed durable artifact store.

Temporal and LangGraph are candidate durable execution backends, not dependencies installed by this phase. Temporal is already cataloged. Their production capabilities and comparative fit have not been tested in this phase; evaluate against replay, deterministic checkpoints, human authorization boundaries, idempotent receipt/circuit updates and restart fault injection in Phase 4 rather than introducing both frameworks or claiming crash-proof execution.

## 8. Recommended Phase 4 scope (not implemented)

Build a bounded supervisor state machine around the DAG, not inside it. It should classify exhaustion vs evidence contradiction vs policy denial, choose scoped authorized recovery or abstention, decide when discovery candidates warrant a separately approved provider qualification, and write explicit unresolved construction briefs. Add persistent per-stage checkpoints, idempotent attempt replay/resume and transactional circuit reconciliation; evaluate Temporal and LangGraph against a minimal local baseline before choosing one, add policy budgets, per-obligation evidence authority and conflict adjudication, candidate-use receipts and verified learning promotion. Establish the verification gate interface now; keep the independent verification harness and remaining thirteen archetype graphs for their own phase. Test that Tier 3/4 discovery never replaces Tier 1 evidence, no discovery PASS closes an unknown, and authorization cannot be escalated through a graph edge. Real provider onboarding must have a separate permission and fixture qualification milestone.

**Stop here for review.**
