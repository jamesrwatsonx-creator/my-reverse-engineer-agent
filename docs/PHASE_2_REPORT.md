# Phase 2 — minimum execution foundation

Review branch: phase-2/minimum-execution-foundation, based on Phase 1 0b9e820216ea6e78a3be850195eee315748af1c7. Main intentionally unchanged. Synthetic fixtures only; no real target, provider analysis, REA internal changes, full DAG, supervisor or verification harness.

## What was built

| File | Behavior and test coverage |
|---|---|
| src/orchestrator/evidence_store.py | SQLite append-only evidence and attempt ledger; canonical SHA-256 content identity excludes the ID itself; deduplication; symmetric immutable conflict index for distinct outputs on a common input; queryable failure receipts with status, signature, provider, time and input digest. tests/test_evidence_store.py checks deduplication, restart, both conflict directions and failure query. |
| src/orchestrator/capability_matrix.py | Host snapshot, PATH discovery, explicit provider-specific read-only health probes, conservative availability states and immutable timestamped JSON snapshot. tests/test_capability_matrix.py tests missing binary, nonzero exit, wrong output, not checked and verified health. |
| src/orchestrator/artifact_normalizer.py | Fixture dialect projections: function, call graph with unknown edges, string table, network capture and inferred schema. Complete canonical raw JSON blob, provenance, nested/top-level unrepresented fields. tests/test_artifact_normalizer.py covers all five. No real-provider raw schema assumed. |
| src/orchestrator/executor.py | Ordered provider fallback, authorized fixture-only invocation, receipt persistence before advancing, skip trace without attempt receipt, structured exhaustion; one matching repair stage and one re-entry maximum. Repair artifacts augment re-entry input; augmented digest includes original input and repair hashes. tests/test_executor.py covers timeout/empty/pass, all fail, skip, bounded repair, repair output and exceptions. |
| scripts/gap_engine.py | Revised closure check; persisted verification receipt or explicit YELLOW linked residual required; no provenance-only resolution. tests/test_gap_resolution_phase2.py covers regression, verified/conditional closure, and contradiction rejection. Existing gap-engine test updated to use real persisted fixture receipt. |
| src/orchestrator/contracts.py | EvidenceEntry now includes mandatory ResultStatus and validates UTC-aware timestamp, digest format, PASS hashes; null hashes permitted with limitations on failures. GateAssessment.acceptable_for is an admissibility check, not a verifier. tests/test_contracts.py covers enum membership, mandatory fields and YELLOW policy. |
| tests/fixtures/phase2.json | Small checked-in synthetic input, fingerprint, stage and raw artifact fixture. |
| .github/workflows/workbench.yml | Existing unittest discovery automatically includes new tests; compile new modules, run web planning and generate capability snapshot artifact on push and PR. |

## RED/GREEN receipts

- Test-only commit [2917091](https://github.com/jamesrwatsonx-creator/my-reverse-engineer-agent/commit/2917091d6d157135c17698d5eb22302f56579193), [RED CI](https://github.com/jamesrwatsonx-creator/my-reverse-engineer-agent/actions/runs/45723833088): 28 tests discovered, seven expected errors (missing runtime modules and EvidenceEntry status contract).
- Initial implementation commit [ddafe37](https://github.com/jamesrwatsonx-creator/my-reverse-engineer-agent/commit/ddafe3752ec7c67593ca0180bb9d8618d633efed), [GREEN CI](https://github.com/jamesrwatsonx-creator/my-reverse-engineer-agent/actions/runs/45723961939): 30 tests passed, compilation and workbench planning succeeded, host snapshot uploaded. This receipt is for that exact commit.
- Final implementation commit [9928d61](https://github.com/jamesrwatsonx-creator/my-reverse-engineer-agent/commit/9928d61cdf86f32441406a5727d757782638db5f), [GREEN CI](https://github.com/jamesrwatsonx-creator/my-reverse-engineer-agent/actions/runs/45724129063): 33 tests passed (0.220 s), compilation, workbench planning, capability snapshot and artifact upload succeeded. No real target analysis. This final report-only commit records that observed receipt.

## Closure behavior change

Previously the gap auditor permitted RESOLVED with DOCUMENTED/OBSERVED and NOT_RUN if evidence was merely referenced. Now it rejects that disposition, retains the knowledge_status, reports effective OPEN plus an explicit reason and invalid audit, and does not silently rewrite the case file. A functional PASS must link a persisted, noncontradicted evidence entry with observed/derived provenance, status PASS, an allowed verification method (byte_match, oracle_harness, behavioral_equivalence) and a matching PASS attempt receipt ID. Alternatively an explicit YELLOW verification assessment must name residual_uncertainty and cite existing noncontradicted evidence; it remains unresolved for full equivalence. FAIL/BLOCKED/DEFERRED cannot be RESOLVED. A user-authored YELLOW assessment is a recorded conditional disposition, not proof of a verifier invocation. No global harness exists yet. Legacy gap register closure claims need review, not automatic migration. Use python scripts/gap_engine.py audit --slug SLUG --evidence-store PATH for persisted checks.

The test test_provenance_not_closure constructs DOCUMENTED/NOT_RUN/RESOLVED, which the old audit accepted; the new audit returns invalid, DOCUMENTED and effective OPEN. test_verified_or_yellow checks both approved paths and malformed residual rejection. test_contradicted_receipt_does_not_close checks a conflicting artifact prevents closure.

## Actual execution host snapshot

The actual execution host for the implementation and tests was the GitHub Actions Linux runner, not the user's workstation or the chat container. The chat container cannot resolve GitHub DNS and was not used to claim a local checkout or full-suite execution. Host probe from the successful run at 2026-11-25 23:48 UTC (final implementation commit):
- os: "Linux"
- architecture: "x86_64"
- jdk_version: "openjdk version \"25.0.5\" 2026-10-20 LTS"
- python_version: "3.11.18"
- ptrace_seize: true
- docker_reachable: true
- display_present: false
- kvm_accessible: false

| Status | Count |
|---|---:|
| UNAVAILABLE | 150 |
| AVAILABLE_UNVERIFIED | 0 |
| AVAILABLE_VERIFIED | 2 |

AVAILABLE_VERIFIED here means only the allowlisted read-only command exited successfully and matched an expected output shape, not functional analysis, provider integration or sandbox safety. Registry runtime statuses remain NOT_RUN. 24 reviewed provisional command shapes; remaining 128 catalog entries fail closed because no approved provider-specific executable/host probe exists. Many entries are libraries, skills, documentation, hosted APIs or reference-only sources, not executable binaries. The table below covers every one of the 152 entries. Reprobe on the actual deployment host before selecting a provider.

| Provider | Status | PATH observation | Reason |
|---|---|---|---|
| rea | UNAVAILABLE | not resolved | Binary not on PATH: rea |
| ghidra | UNAVAILABLE | not resolved | Binary not on PATH: analyzeHeadless |
| craft | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| playwright | UNAVAILABLE | not resolved | Binary not on PATH: playwright |
| playwright-mcp | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| obscura | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| treg | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| omniget | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| last30days | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| jev-guard | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| jev-ultrafast | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| github | AVAILABLE_VERIFIED | /usr/bin/gh | Version/help shape verified; analysis compatibility untested |
| rea-prompts | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| awesome-rea | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| mitmproxy | UNAVAILABLE | not resolved | Binary not on PATH: mitmdump |
| quicktype | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| openapi-generator | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| schemathesis | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| wiremock | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| pact | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| composio | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| nango | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| activepieces | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| airbyte | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| mcp-registry | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| n8n | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| keycloak | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| authlib | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| aalpy | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| learnlib | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| hypothesis | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| temporal | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| sqlglot | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| prisma | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| dbt | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| postgres | UNAVAILABLE | not resolved | Binary not on PATH: postgres |
| sdv | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| distilabel | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| argilla | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| promptfoo | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| deepeval | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| ragas | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| scikit-learn | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| optuna | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| networkx | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| neo4j | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| jadx | UNAVAILABLE | not resolved | Binary not on PATH: jadx |
| apktool | UNAVAILABLE | not resolved | Binary not on PATH: apktool |
| ilspy | UNAVAILABLE | not resolved | Binary not on PATH: ilspycmd |
| appium | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| axe | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| tree-sitter | UNAVAILABLE | not resolved | Binary not on PATH: tree-sitter |
| semgrep | UNAVAILABLE | not resolved | Binary not on PATH: semgrep |
| opentelemetry | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| browser-use | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| stagehand | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| livekit | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| pipecat | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| hermes | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| openviking | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| postiz | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| grill-with-docs | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| leanrea | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| rea-lab | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| rea-casebook | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| rea-groundtruth | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| dsh-rea | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| rea-video | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| automatisch | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| dograh | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| letta-code | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| ghidra-mcp | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| ida-pro-mcp | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| rea-reconstruction-companion | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| rea-python | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| rea-case-index | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| awesome-reverse-engineering | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| replit | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| blender-agent-sdk | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| daikon | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| kaitai | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| pm4py | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| fast-check | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| k6 | UNAVAILABLE | not resolved | Binary not on PATH: k6 |
| locust | UNAVAILABLE | not resolved | Binary not on PATH: locust |
| testcontainers | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| z3 | UNAVAILABLE | not resolved | Binary not on PATH: z3 |
| tlaplus | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| openrewrite | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| kaitai-compiler | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| kaitai-formats | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| angr | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| triton | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| qiling | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| unicorn | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| rz-ghidra | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| webcrack | UNAVAILABLE | not resolved | Binary not on PATH: webcrack |
| js-deobfuscator | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| blackboxprotobuf | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| pbtk | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| wireshark | UNAVAILABLE | not resolved | Binary not on PATH: tshark |
| ipsw | UNAVAILABLE | not resolved | Binary not on PATH: ipsw |
| ipsw-py | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| ipsw-skill | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| panda | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| rr | UNAVAILABLE | not resolved | Binary not on PATH: rr |
| qbdi | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| libvmi | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| hyperdbg | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| firecracker | UNAVAILABLE | not resolved | Binary not on PATH: firecracker |
| bubblewrap | AVAILABLE_VERIFIED | /usr/bin/bwrap | Version/help shape verified; analysis compatibility untested |
| nsjail | UNAVAILABLE | not resolved | Binary not on PATH: nsjail |
| qemu | UNAVAILABLE | not resolved | Binary not on PATH: qemu-system-x86_64 |
| d810-ng | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| renderdoc | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| spirv-tools | UNAVAILABLE | not resolved | Binary not on PATH: spirv-val |
| spirv-cross | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| directx-shader-compiler | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| netron | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| onnx | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| onnxruntime | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| litert | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| coremltools | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| aioquic | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| aiortc | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| eventsource-parser | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| automatalib | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| renode | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| littlefs | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| ollama | UNAVAILABLE | not resolved | Binary not on PATH: ollama |
| vllm | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| ghydramcp | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| pyghidra-mcp | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| jadx-mcp | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| awesome-ai-re | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| ecapture-reference | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| fritap-reference | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| scyllahide-reference | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| frida-dexdump-reference | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| drakvuf-reference | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| libmicrovmi-reference | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| hvmi-reference | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| vtil2-reference | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| triton-symbolic-reference | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| ghidra-alternative-reference | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| ghidra-headless-reference | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| mobile-skills-reference | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| x64dbg-mcp-reference | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| frida-mcp-reference | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| tenrec-reference | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| ida-instances-reference | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |
| agent-escape-bench-reference | UNAVAILABLE | not resolved | No approved provider-specific CLI/host probe; catalog entry only |

Full timestamped snapshot: [run artifact and logs](https://github.com/jamesrwatsonx-creator/my-reverse-engineer-agent/actions/runs/45724129063). This snapshot additionally records KVM accessibility; display detection is limited to observed display environment variables. No installations, real application or binary analysis ran. PTRACE_SEIZE probe uses only a disposable Python child. Docker reachability check is a local daemon version request; remote DOCKER_HOST values are skipped.

## Discrepancies and design decisions

- Phase 1 is not merged to main. Phase 2 is based on that branch so comparison to main includes Phase 1 as well. No prior runtime files or fixtures existed.
- Phase 1 EvidenceEntry lacked status; added mandatory field (schema change). Canonical ID excludes its own ID; append accepts blank for computed ID or validates supplied one. Explicit conflict links are stored separately so no mutation occurs. Distinct normalized outputs on same input can be complementary; the directive's automatic conflict rule is deliberately conservative until Phase 3 adds comparable observation scope.
- Failure receipts carry the original ProviderResult serialization and stable caller-supplied execution/stage/round/index identity. Multiple artifacts use the ordered digest manifest as the result's output hash. No artifact bytes are fabricated; raw normalized fixture output is retained as JSON, not original formatting or binary bytes. Provider provenance IDs are kept distinct from the local receipt ID.
- is_available means health-verified for this session, fail closed for unverified. No approved probe means UNAVAILABLE even if an unrelated similarly named executable resolves. Host probes are bounded; KVM path is a Linux capability check, not an install location. Provider-specific compatibility/licensing/authorization/fixture execution is still unverified. A health command is not an analysis invocation.
- Executor does not orchestrate dependencies; caller supplies previously passed preconditions and explicit provider allowlist. An optional stage predicate may reject a provider result; a PASS without gate remains unverified. Repair route is selected by observed failure signature, no NONE/PINNED/adversarial automatic retry, no nested repair, no actual real provider adapters. The target fingerprint is passed as fixture metadata. Database write failure aborts rather than continuing without a receipt.
- Current typed normalizers support only the fixture dialect. Unknown raw fields are retained; real provider format, artifact schema compatibility validation and content-addressed binary storage are later work.
- Existing tests are synthetic, not comprehensive proof of performance/concurrency/crash recovery or trust in a caller-supplied verification method. The gap auditor checks receipt structure and linkage; it cannot prove the verifier really ran or bind all evidence to a semantic obligation. The Phase 3/4 design must establish authority and scoped gate receipts; YELLOW remains partial.

## Recommended Phase 3 scope (not implemented)

Start the DAG engine only after review. Define per-archetype stage definitions, validated acyclic preconditions, evidence-scoped artifact compatibility and explicit signature routes. Implement deterministic bounded scheduling and checkpoint/restart on synthetic fixtures; preserve receipt identities and precondition gate status. Add cross-provider proof scope and explicit host/provider qualification before real adapter work. Keep supervisor state machine and independent verification harness as their own later milestones; do not treat health-only or provider PASS as verified closure. Test denial/contradiction/exhaustion/restart and cycle rejection before any real targets.

Stop after Phase 2.
