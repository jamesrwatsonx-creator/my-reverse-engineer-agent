# Dossier contract — authoritative Phase 4 rules

Status: enforced by `src/orchestrator/dossier_writer.py` and the supervisor. Supersedes the documentary-only portion of Phase 3. Phase 5 may extend the verified-result type only with independent verification.

## Separate persistence boundaries

DossierWriter and LearningWriter use distinct SQLite database paths and a persisted partition marker; attempting to reopen a marked database under the wrong partition fails. Records are append-only and identity-deduplicated. The evidence/WAL store is internal operational state, not a build-repo export. The build handoff receives only explicitly projected dossier records, not the evidence DB, raw DAG trace, learning database or runtime logs. Export/permissions infrastructure is not implemented by this phase; do not transfer those internal files.

Dossier writer accepts strict top-level and nested fields, rejects foreign record types and unsupported provenance. Learning writer accepts operational record types (failure_receipt, contradiction, discovery_query, strategy_outcome, abstention, transition) and rejects dossier types or nested dossier-specific content keys. It can retain evidence/brief IDs without brief bodies. Raw fixture provider receipts are observations, not independently verified results. This is schema/partition enforcement at the API boundary, not a semantic content filter for arbitrary free-text strings or an OS sandbox.

## Unresolved record (required)

```json
{
  "kind": "unresolved",
  "gap_id": "example",
  "status": "ABSTAINED",
  "construction_brief": {
    "observable_behavior": "A fixture exhibits a measured response",
    "undetermined_mechanism": "The original internal mechanism is unknown",
    "approximation": {"description": "Independent implementation path", "provenance_tier": 4},
    "supporting_evidence": ["persisted-evidence-id"],
    "implementation_path": [
      {"candidate_id": "content-derived-id", "canonical_path": "owner/repo", "verification_required": "Run held-out fixture", "license": "MIT"}
    ],
    "acceptance_test": {"input": "held-out fixture", "expected": "expected observable outcome", "method": "behavioral_equivalence"}
  },
  "no_brief_reason": null
}
```

Exactly one of construction_brief and no_brief_reason is required. Reason must be nonempty and name the limiting condition; a missing brief is not a silent omission. In the supervisor, supporting observation IDs must refer to persisted, noncontradicted observed/derived PASS entries. Discovery results are not Tier 1/2 evidence. High-license-risk candidates excluded; remaining candidates still require qualification. Candidate ID is canonical content digest, not proof of eligibility. Acceptance method is a specification, not a result. Supported named future methods: byte_match, oracle_harness, behavioral_equivalence.

Writer rejects incomplete/unexpected fields and invalid provenance or method; supervisor routes writer rejection to ESCALATED, with no invalid dossier entry. A blocking abstention escalates after recording ABSTAINED. Non-blocking abstention stays ABSTAINED.

## Synthetic fixture results

Allowed only `kind: fixture_result`, gap_id, status YELLOW, verification_method synthetic, residual_uncertainty (nonempty named list), evidence_ids (nonempty references). There is no independent GREEN result type in Phase 4. CLOSED is limited to synthetic scoped objectives, with explicitly named residual, not a certification of original functionality. Phase 5 must replace this with actual scoped gate receipts and enforce the earlier feasibility condition for production YELLOW closure.

## Learning store

Failure attempts and status, discovery queries and results, contradiction links, strategy outcomes, and supervisor transition history stay internal. AbstentionRecord in the learning store contains attempt/query receipts, stage/rung history, brief ID or no_brief_reason and what is required to proceed. Verified results and construction brief bodies are not accepted by LearningWriter. The dossier excludes raw receipts, contradiction records, discovery history, strategy outcomes and raw provider traces. No search candidate can authorize installation, access or copying.

## Tests

`tests/test_dossier_writer.py`: invalid unresolved record rejected, valid brief accepted and retrieved, failure receipt refused in dossier and accepted in learning, brief rejected by learning, unexpected dossier keys rejected, mandatory contracts and exclusive brief/reason.
`tests/test_supervisor.py`: discovery-driven brief, no-candidate reason, invalid brief rejected with ESCALATED, blocking abstention, prior strategy and all-rung exhaustion.
`tests/test_durability.py`: actual process death after dossier/abstention persistence and terminal checkpoint, then restart without duplicate dossier rows.

An unknown with a construction brief is a deliverable, not a silently dropped gap. An unknown with neither a brief nor a reason is a defect. A brief is still an approximation until independent acceptance is verified.
