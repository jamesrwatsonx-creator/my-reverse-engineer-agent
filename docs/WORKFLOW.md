# Universal stage gates
INTAKE → PREFLIGHT → RECON → OBSERVE → MODEL → MATCH → VERIFY → HANDOFF → BUILD (only authorized) → COMPARE → LEARN. Iterate when evidence contradicts hypotheses.
| Stage | Required artifacts | Acceptance |
|---|---|---|
| Intake | brief, scope, obligations | goal and authorization explicit |
| Preflight | tool plan and receipts | pinned version, live capability list, safe fixture |
| Recon | source/version map, feature atlas, actors | citations and blocked surfaces |
| Observe | scenarios, sanitized traces, states | reproducible steps and evidence IDs |
| Model | dossiers, contracts, data/state/dependency graph | alternative hypotheses and discriminating tests |
| Match | component cards, architecture options | license, pin, fixture result or blocker |
| Verify | comparative held-out tests | normal, failure, roles, gaps retained |
| Handoff | contracts, coverage, decisions, plan | owner scope approved before build |
| Build/compare | independent code, tests, deploy receipts | authorized destination and acceptance |
| Learn | capability cards, index | safe reusable evidence |
Coordination: assign run_id/target_slug/scenario_id/step_id, UTC, source version and artifact hash. One action driver (Playwright/Obscura/Appium/manual) per scenario, REA observer armed before action; pass sanitized artifacts to offline analyzers, then schema/model and comparator. Independent read-only tasks may run concurrently; serialize shared account/profile/database/rate budget. Store receipts and STATUS after gates, checkpoint with scoped commits, reconcile concurrent work. If tool missing or permission blocked, choose permitted fallback or ask only smallest owner action. Never silently claim synchronized operation; prove with correlated fixture trace.

## Mandatory learning and separate build stages
Refine the stage sequence: INITIALIZE → UPSTREAM REVIEW → INTAKE → RETRIEVE → PREFLIGHT → RECON → OBSERVE → MODEL → MATCH → VERIFY → LEARNING REVIEW → HANDOFF → optional separate BUILD → COMPARE → FEEDBACK. Retrieval happens before expensive work and again when a capability is identified. During each checkpoint record what was reused, what failed, new alternatives and evidence. Research handoff requires INTERVIEW, CONTEXT, DECISIONS, LEARNING_DELTA, REUSE_LOG and a learning audit; no finding is also a valid disposition. A blocked investigation remains blocked, even when its learning record is complete. A separate production repository receives reviewed handoff snapshot; implementation feedback triggers a new comparative review. Do not require a full production build to learn from a research investigation.

UPSTREAM REVIEW precedes target planning; refresh immediately before REA execution when resuming or starting a new agent session. Record actual sources/version and scope in UPSTREAM_REVIEW.md, compare with prior review, and assess Replit; use documented fallback if blocked. New external features are candidate learning, not automatic policy changes.

Mandatory all-resource refresh: follow docs/RESOURCE_FRESHNESS.md at every investigation (full catalog and tracked owner sources, current upstreams, owner-profile discovery, change assessment and per-target relevance), record receipt in UPSTREAM_REVIEW.md and reference immutable report. Recheck selected versions before execution. Never silently auto-update or mark unreviewed changes as adopted.

After reconnaissance and owner scope, follow docs/GAP_ENGINE.md and GAP_TOOL_RECIPES.md. Populate GAP_REGISTER.json with scoped obligations and explicit gap classes; run gap_engine.py plan --slug <target>, choose verified tools by evidence and gap, record attempts/fixtures/results/residuals, run audit at handoff and route reusable lessons through LEARNING_DELTA. Do not use irrelevant or unauthorized tools. No arbitrary fidelity percentage.