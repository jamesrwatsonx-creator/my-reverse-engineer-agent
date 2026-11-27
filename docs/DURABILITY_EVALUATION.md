# Durability evaluation — Phase 4

Decision: Option B, custom local SQLite WAL + append-only operation journal, cooperative completion outbox, stable idempotency identities, stage checkpoints and receipt/circuit reconciliation. Python standard library only. This is a single-worker fixture foundation, not a distributed workflow service or a universal exactly-once guarantee.

## Evidence

[Final implementation CI](https://github.com/jamesrwatsonx-creator/my-reverse-engineer-agent/actions/runs/45996938751), commit 07ba7d8963240c7edf13bf9d7183d513afc33006: 67 tests passed on Linux, including eight subprocess fault tests. Every fault test starts a separate process, uses SIGKILL at a controlled boundary (asserts return code -9), starts a new process against the same on-disk databases, and asserts the resulting state. No mocked exception is substituted for process death.

| Required scenario | Fault test | Actual assertion (passed) |
|---|---|---|
| 1a: completed invocation before evidence receipt | test_completed_outbox_before_evidence | Provider called once; one receipt, PASS recovered from committed outbox. |
| 1b: during invocation, completion uncertain | test_mid_invocation_incomplete | Provider called once; INCOMPLETE receipt and stable attempt hash; no blind re-invocation. |
| 2: evidence persisted before circuit transition | test_evidence_before_circuit | One invocation, one receipt; circuit failure count reconciled to one. |
| 3: stage checkpoint before dependent scheduling | test_stage_before_downstream | Exactly two total invocations (A and B); A not repeated, B executes. |
| 4: interrupted discovery invocation | test_discovery_mid_invocation | Two discovery calls, same key, INCOMPLETE event, one final receipt. |
| Additional: committed supervisor transition | test_supervisor_transition_restart | One analysis, one discovery, one dossier record; final ABSTAINED. |
| Additional: abstention/dossier writes persisted before terminal state | test_supervisor_abstention_write_restart | Same counts and final ABSTAINED; no duplicate dossier row. |
| Additional: terminal committed before return | test_supervisor_terminal_restart | Same counts and terminal result recovered. |

The separate terminal replay and scoped transient retry tests pass. These are observations of specific fault boundaries, not exhaustive interleaving exploration.

## Alternatives (documented capabilities, not executed head-to-head)

| Criterion | Temporal | LangGraph persistent checkpointer | Custom Phase 4 |
|---|---|---|---|
| Completion before receipt | Activity retries require application idempotency or provider completion reconciliation; replay of already recorded completion avoids another activity | Node/task checkpointing restores recorded work; side effects before a persisted result need application handling | Explicit completion outbox + attempt receipt, tested |
| Receipt before circuit event | Requires application-owned transactional reconciliation | Requires application-owned transactional reconciliation | Replay receipt, idempotent circuit event, tested |
| Completed stage before downstream | Workflow event history and replay designed for this | Persistent graph state checkpoint designed for this | Local stage checkpoint, tested |
| Discovery interrupted | Activity retry with stable logical identity; provider-specific idempotency | Re-execution/resume with stable application key | Read-only query reissued under original key, tested |
| Operations | Service/server or cloud, workers, SDK, deployment and schema/version discipline | Graph runtime, persistent checkpointer, thread IDs, DB configuration | Python/SQLite existing local stack; no server, but custom recovery logic to maintain |
| Multi-worker and scheduling | Mature workflow service; evaluate actual deployment | Runtime/checkpointer and deployment choices; evaluate concurrency | Not implemented; single-writer assumption |
| Fault tests in this repo | NOT_RUN | NOT_RUN | 8 passed |

Sources reviewed 2026-11-27: [Temporal Activity Definition](https://docs.temporal.io/activity-definition), [Temporal Activities](https://docs.temporal.io/activities), [Temporal durable execution](https://docs.temporal.io/durable-execution), [LangGraph Persistence](https://docs.langchain.com/oss/python/langgraph/persistence). These support the documented architecture comparison, not comparative benchmark results. No SDK installed, no license audit or release compatibility test performed here.

## Why custom now

The specific failure mode is the boundary between an opaque provider's completion, the REA evidence receipt, and the circuit transition. Neither general workflow engine automatically understands this repository's scoped evidence, circuit receipts, or distinction between unknown completion and a failed provider. Both can implement the same outbox/reconciliation pattern; this is not a claim of a capability unique to the custom engine. The small local layer implements the domain contract directly without replacing the existing scheduler or introducing a second workflow runtime.

A cooperative provider can invoke `invoke_durable(input,key,commit)` and commit the prepared result before acknowledging completion. If a provider has already completed externally but dies before a durable completion record, the system cannot know that fact. Non-cooperating analysis adapters are not re-invoked automatically; an INCOMPLETE receipt records the attempt hash. Read-only discovery can be retried under the same logical key; actual external request duplication remains possible and is not claimed away. Disk persistence uses WAL and synchronous FULL; not a cross-host or power-loss benchmark.

## Scope and next decision

Use this backend for fixture work until Phase 5 verifies the evidence contracts. Before real external side effects or multiple workers, require provider-level completion/idempotency, durable lease/fencing and recovery for interrupted writes, artifact storage integrity and retention, explicit per-operation policy and crash tests for additional interleavings. Cross-database dossier/learning writes are idempotent but not a single distributed transaction. A rerun requires the same plan, clock, configuration and execution identity. A changed plan is rejected; not all arbitrary crashes or disk corruptions have been simulated. Keep Temporal as a strong candidate for multi-worker orchestration, with the same domain outbox; compare a real prototype before migration. LangGraph remains an alternative if the agent graph becomes the main orchestration surface. No Phase 5 implementation authorized.
