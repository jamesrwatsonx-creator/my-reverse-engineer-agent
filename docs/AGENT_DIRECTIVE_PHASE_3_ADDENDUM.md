# AGENT_DIRECTIVE_PHASE_3.md — accepted addendum A–C

The original Phase 3 directive was provided in the review conversation, not stored as a tracked standalone file. This addendum records the additional requirements and applies alongside the original directive. No Phase 4 implementation is authorized.

## A — Four-rung recovery ladder

Replace flat provider arrays in routes/stages.json with an ordered ladder: R1 static, R2 symbolic/emulation, R3 live instrumentation, R4 black-box/discovery. Each rung declares trigger_signatures. Escalate only after current applicable rung exhaustion and a matching observed signature; stop on PASS. Empty/inapplicable rungs are explicit. Preserve receipts and rung trace. Discovery is a separate candidate-generation event, not verified closure or authorization.

## B — Persistent circuit breaker

Per-provider consecutive failure count, configurable threshold (default 3), OPEN/HALF_OPEN/CLOSED state persisted as append-only evidence-store transitions. OPEN skips invocation and must not fabricate a failed-attempt receipt. Use deterministic caller clock and a configurable cooldown (PoC default 60 seconds) before one half-open probe. Apply to analysis and discovery providers. Test persistence across restart, skip and recovery.

## C — Streaming capture

Cloud-api capture must specify streaming_capture: bounded IO.read to disk and hash reference rather than inline large payload. Use synthetic fixture above threshold and verify exact hash, disk content and absence of full inline payload in persisted trace. PoC threshold 4096 bytes, chunk 1024, cap 16384; not production quotas. Respect existing evidence, permission, retention and host checks.

## Architectural boundary

Durable execution (Temporal/LangGraph), the four-rung ladder, circuit breakers and reference-based handoff are complementary. The ladder, circuit and reference mechanism belong to Phase 3. Production durable execution selection, checkpoint/replay, transactional recovery and independent verification belong to later phases; do not claim crash-proof execution until tested. The supervisor remains separate. No real target or unauthorized access; no auto-install of research candidates.

See [PHASE_3_REPORT.md](PHASE_3_REPORT.md) for observed CI receipts, decisions and remaining limitations.
