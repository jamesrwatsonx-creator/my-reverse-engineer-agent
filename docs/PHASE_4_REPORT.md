# Phase 4 — supervisor, durable execution and dossier enforcement

Review branch: phase-4/supervisor-durability, based on Phase 3 28f90f3d75f76a355208698289a6b6dd05764803. No changes to main, Phase 2, or Phase 3. Synthetic target fixtures only. No verification harness, remaining thirteen archetype graphs, real provider onboarding or Phase 5 code.

- [Compare Phase 3](https://github.com/jamesrwatsonx-creator/my-reverse-engineer-agent/compare/phase-3/dag-engine...phase-4/supervisor-durability)
- [Compare Phase 2](https://github.com/jamesrwatsonx-creator/my-reverse-engineer-agent/compare/phase-2/minimum-execution-foundation...phase-4/supervisor-durability)
- [Compare main](https://github.com/jamesrwatsonx-creator/my-reverse-engineer-agent/compare/main...phase-4/supervisor-durability)

## 1. Built and tested

| File | Implementation / coverage |
|---|---|
| src/orchestrator/supervisor.py | Bounded policy on top of DAG, scoped retry, discovery-on-abstention, prior strategy replay, durable decisions and terminal return, structured abstention and blocking escalation. tests/test_supervisor.py (7 tests). |
| src/orchestrator/durability.py | Append-only WAL journal, operation envelope/hash, completion outbox, INCOMPLETE, stable identities, typed decoding, stage and decision checkpoint/replay. tests/test_durability.py (8 process-kill tests). |
| src/orchestrator/dossier_writer.py | Distinct marked SQLite partitions, strict dossier record schema, idempotent append, learning partition guard, strategy lookup. tests/test_dossier_writer.py (2 tests). |
| src/orchestrator/contracts.py | SupervisorAction, mandatory SupervisorDecision and AbstentionRecord, INCOMPLETE provider status for unknown completion. Brief ID/reason exclusive and required evidence named. |
| src/orchestrator/executor.py | Durable invocation/receipt replay, circuit reconciliation, persisted skip outcomes, unknown analysis completion stops automatic fallback within the stage. All claimed verification methods from fixture adapters restricted to synthetic. |
| src/orchestrator/dag_engine.py | Durable plan validation, stage snapshots, cached PASS stages, discovery replay, persisted skips, scoped retry/affected descendant scheduling with unchanged independent stages reused. |
| src/orchestrator/evidence_store.py | WAL + synchronous FULL, discovery receipt retrieval by logical key, run-scoped discovery history; preserves existing append-only evidence and circuit rules. |
| tests/fixtures/phase4.json; tests/fixtures/phase4_fault_worker.py | Deterministic fixture objective and real SIGKILL subprocess worker. No real binary, app, or API target. |
| docs/DURABILITY_EVALUATION.md; docs/DOSSIER_CONTRACT.md | Compared choices and enforced handoff rules. |

### CI receipts

- [RED](https://github.com/jamesrwatsonx-creator/my-reverse-engineer-agent/actions/runs/45996435695), commit 201e6fe7da2d5e06c9328fae7857668668ff7f33: 53 discovered, three expected missing-module errors. Test-first baseline.
- [Initial GREEN](https://github.com/jamesrwatsonx-creator/my-reverse-engineer-agent/actions/runs/45996676538), commit 23586e269daef876d6d18a6a949c22615f52eede: 60 passed, including five SIGKILL/restart cases.
- [Hardened GREEN](https://github.com/jamesrwatsonx-creator/my-reverse-engineer-agent/actions/runs/45996799555), commit 2508ba5432dd4541939d527b8a4d03058031d682: 62 passed.
- [Final implementation GREEN](https://github.com/jamesrwatsonx-creator/my-reverse-engineer-agent/actions/runs/45996938751), commit 07ba7d8963240c7edf13bf9d7183d513afc33006: 67 tests passed in 2.424 seconds; compilation, workbench planning, host capability snapshot, provisioning review and artifact upload all succeeded. Eight process-kill tests, seven supervisor tests, two dossier/contract tests. This report-only commit records the exact implementation receipt. No live target verification.

## 2. Supervisor transition policy

| From | Event/condition | To | Action |
|---|---|---|---|
| PLANNING | Valid scoped run | EXECUTING | CONTINUE with deterministic DAG |
| EXECUTING | DAG returns | PLANNING | Review dispositions, evidence and objective scope |
| PLANNING | Transient TIMEOUT/NONE, RATE_LIMITED, AUTH_MISSING | REPAIRING | Bounded per-provider retry; already authorized and declared only |
| REPAIRING | Retry/prior strategy run | PLANNING (logical inspection) / DISCOVERING / VERIFYING | Reinspect returned result; affected descendants only, unrelated stages reused |
| DAG execution | Structural failure, matching next rung | EXECUTING | Existing DAG ladder controls escalation; no supervisor bypass |
| PLANNING | Exhaustion, contradiction or unsatisfied objective | DISCOVERING | Knowledge retrieval first, prior successful eligible configuration once |
| DISCOVERING | Prior success qualifies | REPAIRING | Explicit fixture provider/configuration replay |
| DISCOVERING | No successful recovery | DISCOVERING | GitHub and browser research for candidate paths; no automatic install |
| DISCOVERING | Brief or named no-brief reason accepted | ABSTAINED | Persist dossier and structured internal record |
| ABSTAINED | Blocks downstream work | ESCALATED | Human review |
| Any dossier write | Schema rejection | ESCALATED | Do not persist invalid entry |
| PLANNING / REPAIRING | All requested fixture objectives accepted | VERIFYING | Synthetic gate bookkeeping; authored verify stage included in objectives |
| VERIFYING | Conditional fixture outcome with named residual | CLOSED | YELLOW synthetic only, never production GREEN |

The implementation emits transitions for actual policy steps, not a redundant PLANNING event after every single retry. Default one retry per provider (configurable 0–3); circuit state and original allowed-provider set remain authoritative. Structural escalation remains DAG-owned. Phase 2 separate repair-stage machinery is not newly wired into Phase 3 graph definitions; Phase 4 replays a qualified provider configuration within the declared stage and DAG ladder. Unknown completion is never treated as a transient failure. No unauthorized credential acquisition or access escalation.

## 3. Durability

See [DURABILITY_EVALUATION.md](DURABILITY_EVALUATION.md) for approach comparison and exact fault-test matrix. Option B selected. Persist STARTED envelope and input hash, cooperative COMPLETED outbox, then evidence receipt and circuit transition; resume via recorded result and reconcile idempotently. An unacknowledged analysis invocation yields INCOMPLETE; read-only discovery reissues the original key. A completed stage snapshot releases descendants after restart. Plan identities and payloads cannot be reused with changed content. Terminal supervisor decision is returned without replaying provider work.

All four requested fault scenarios passed, with scenario 1 split into completed versus incomplete (five required tests), and three additional subprocess kill tests at committed supervisor transition, abstention write and terminal checkpoint. Every test actually kills a subprocess and starts another on the same DB. No assertion of universal exactly-once semantics: an external provider can finish before durably acknowledging, and cannot be reliably distinguished from an interrupted invocation without cooperation. The general orchestration frameworks would need the same domain-specific integration.

## 4. Dossier and learning boundaries

See [DOSSIER_CONTRACT.md](DOSSIER_CONTRACT.md). Strict schema and persisted partition identity enforce separate destinations. A missing brief AND missing no-brief reason rejects; invalid brief field or method rejects; failure receipt rejected in dossier, accepted in learning; construction brief rejected in learning. Supervisor escalates on invalid dossier entry. Candidate and evidence IDs remain traceable; full query/attempt history and strategy records stay internal. No build repo export performed. The internal evidence store contains raw observations and operation receipts, not verified production result artifacts. Verified production result type deferred to Phase 5; only explicitly marked synthetic YELLOW fixture results can be written by this phase.

## 5. Discovery and compounding

At abstention, the supervisor invokes knowledge retrieval first. It matches explicitly recorded successful fixture strategies by archetype, failure signature, capability and stage, validates allowed provider and persisted noncontradicted observation references, freezes the selected prior strategy in the journal, and replays its configuration once. It stores the strategy outcome. If recovery succeeds, no GitHub/browser call is needed. If no prior strategy qualifies or works, GitHub and browser candidates are requested (unless unavailable or disallowed); Tier 3/4 inferred candidates are screened, with high license risk excluded. A candidate plus supporting observation and acceptance specification becomes a conditional brief; otherwise a reason is written. Raw discovery results do not become verified findings. Interrupted queries are recorded in the operation journal and reissued under their original key. Phase 3 may already have run event-triggered discovery before the supervisor begins its abstention-specific flow.

Tests prove prior strategy before external discovery, all four rungs exhausted before knowledge/GitHub/browser, candidates yield brief, empty discovery yields named reason, malformed brief escalates, blocking abstention escalates, and unrelated failed stages are not repeated on transient retry. Live discovery backends remain unconfigured; no external search was run by these tests.

## 6. Discrepancies, limitations and decisions

- Phase 3 had completion-only DAG persistence, no supervisor, no dossier writer, no explicit INCOMPLETE status. Added new status and typed contracts rather than silently labeling unknown completion FAIL.
- The directive asks for crash between any two operations; the implementation proves the eight named controlled fault boundaries, not every possible interruption, power-loss, storage corruption or concurrent worker interleaving. Unknown provider completion cannot be made exactly-once by an orchestration engine alone. Cooperative provider callback or provider-side idempotency/result lookup is required for real operations. Single writer and deterministic plan/clock are required; no distributed leases, heartbeats or transactional cross-database writes.
- The required evidence-write/circuit split is reconciled on replay; stage PASS snapshots avoid duplicate analysis. Failed stages replay their existing receipts/skips and reconstruct routing. Artifact streaming checkpoint/crash windows and arbitrary mid-write faults remain untested. Dossier and learning writes are separate idempotent transactions, not atomic cross-store commits.
- Retry configuration is bounded and fixture-only; no actual rate-limit backoff scheduler, credential refresh or host repair. Circuit cooldown uses supplied timestamp. Unknown completion stops stage fallback; human input may be necessary.
- Synthetic gate: authored verify stage is treated as an objective, outputs tagged synthetic, and no independent harness is run. The fixture CLOSED label represents scoped synthetic YELLOW completion with named residual; it is not production closure and does not replace Phase 1 feasibility and authority rules. Phase 5 must enforce those rules when introducing real verification. Fixture graph tests without a verify node use the local contract PASS as their synthetic outcome.
- LearningWriter guards record type and nested dossier-specific keys; it cannot semantically inspect arbitrary free text. Separate database markers and schema validation are not OS-level permissions, export tooling or proof of information-flow isolation. No raw database is supplied to a build repo. Strategy success is explicitly a prior fixture outcome, not a production verified mechanism.
- Knowledge retrieval's existing provider returns candidate history; the supervisor separately queries the learning partition for explicit successful configurations. No candidate-derived executable or configuration is automatically installed or invoked. Discovery without evidence/acceptance fields writes a named no-brief reason. Current brief schema requires a named input, expected observation and verification method; tolerances can be described in expected text, not a separate structured numeric tolerance field yet.
- Supervisor currently records scoped abstentions in deterministic objective order, not a general objective dependency/priority planner. External candidate integration and strategy admission beyond fixture controls, independent verification, production recovery, and broader provider qualification remain outstanding. The full Phase 3 report remains historical, with authoritative dossier contract now separate.
- Tests executed on GitHub Actions Linux, not user's machine. Phase 3 host qualification gaps remain. No REA internals modified, no new live provider tests or dependencies installed. Temporal/LangGraph comparison is documentation-based; neither tested or ruled out for distributed production.

## 7. Phase 5 recommendation (not implemented)

First implement independent verification harness and authority-scoped receipt validation on the two existing graphs. Enforce GREEN only with actual verified evidence and YELLOW only when allowed with named residual. Validate construction-brief acceptance independently and reject incompatible provider artifacts. Add production-grade evidence/operation idempotency and crash recovery qualification for any real provider onboarding; ensure artifact refs, host scope and permissions remain valid. Then extend remaining thirteen archetype graphs in batches only when tests and provider qualifications can support them. Do not build them all before verification is stable. Evaluate Temporal for distributed execution when multi-worker reliability becomes an actual requirement, carrying the local evidence/outbox semantics forward. Stop at Phase 4 review.
