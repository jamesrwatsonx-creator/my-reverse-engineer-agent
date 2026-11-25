# REA — Shared Agent Operating Contract

Applies to Codex, Claude Code, and any other coding agent operating in this repository.

## Mandatory upstream freshness gate — before target planning or REA use
At initialization of EVERY new investigation and on resumption before using REA, inspect the original upstream https://github.com/morluto/rea, not just the owner's fork or our cached catalog. Read docs/UPSTREAM_REVIEW.md and review upstream main, releases, changed docs/tool schemas and relevant fixes since last recorded review. Compare source HEAD, stable npm release, fork and installed runtime. Record a dated receipt in target UPSTREAM_REVIEW.md, with baseline references, meaningful changes, implications for evidence, coverage, efficiency, compatibility and migration, and explicit adopt/test/defer decisions. If no changes, record that; if inaccessible, record BLOCKED and do not claim freshness. Use verified pinned stable version or documented fallback, never blindly install newest source. Before launch ChatGPT reviews upstream; before execution Claude/Codex rechecks and verifies actual installed tools. Record new portable findings in LEARNING_DELTA, retaining old evidence and independent review/regression gates. Review Replit's current official docs/changelog at initialization and assess whether it can assist development, testing or reconstruction; reassess before choosing build environment. Replit is a hosted candidate, not mandatory runtime, not automatically authorized to receive private research.

## Mandatory all-resource freshness and opportunity review
At every new investigation, refresh source metadata for EVERY catalog entry and every tracked upstream/mirror, regardless of target kind. Use docs/RESOURCE_FRESHNESS.md and scripts/resource_refresh.py (or authorized GitHub connector equivalent). Re-scan the owner's accessible GitHub profile for useful newly discovered or recently changed repositories, skills, APIs and linked resource indexes; register useful candidates and actual upstream lineage, then check their current versions. Before tool selection inspect changes since last reviewed baseline, including releases, docs, source, tests and migration/security implications. Deep-review changed sources for reusable capability gains and selected resources for target compatibility. Record coverage, explicit blockers, change range, citations, opportunity/gap affected, proposed fixture and disposition. Recheck selected tools before use; no automatic dependency or fork mutation. Preserve snapshots and last reviewed revision separately from last observed HEAD, maintain unresolved review backlog, and feed supported discoveries through developmental learning.

## Invariants

- One canonical target = one stable folder under `investigations/<slug>/`; never mix unrelated targets.
- Update the existing folder for follow-ups; don't create a duplicate just because the session or agent changed.
- Prioritize a high-level functional and competitive overview, then drill into demonstrable behavior and architecture.
- Use the exact labels **OBSERVED**, **DOCUMENTED**, **INFERRED**, and **UNKNOWN** for significant claims. Add source, date, method and confidence.
- A frontend observation cannot prove which backend, model, framework, database, algorithm or prompt is used.
- Do not invent feature behavior, architecture, API contracts, prices, screenshots or test results.
- Compare observed capability with proposed clean-room implementation, not copied proprietary artifacts.
- Protect secrets and personal information. Do not bypass authorization, paywalls or security controls.
- Do not run destructive commands or modify target services. Request authorization for consequential changes.
- Every investigation is resumable: keep the executive summary, unresolved questions and evidence log current.
- Preserve original evidence provenance and capture conditions; sanitized assets only.
- Update `registry/index.json` as part of every investigation commit, retaining valid JSON.

## Required target files

`README.md`: target URL, goal, status (PLANNED/ACTIVE/PARTIAL/BLOCKED/COMPLETE), last reviewed, executive overview, findings, uncertainty, next actions.

`features.md`: inventory of features; observed or documented behavior; user value; constraints.

`experience.md`: branding, palette, typography, imagery, layouts, microinteractions, navigation, primary workflows; indicate whether specifics were measured or estimated.

`architecture.md`: known interfaces, possible components and boundaries, data flows, integrations, security assumptions, technical unknowns. Separate verified from conjectural.

`evidence.md`: every substantial observation with URL/path, UTC date, environment, reproducible steps, asset path, confidence and authorization basis.

`capabilities.md`: individually named capabilities, inputs/outputs, dependencies, reuse potential, provenance, confidence, build-vs-integrate recommendation.

`opportunities.md`: what to copy conceptually vs avoid, user pain, distribution, differentiation, feasibility, risks, proposed smallest test.

`assets/`: optional authorized sanitized screenshots, diagrams, HAR summaries or notes; no secrets.

## Process

1. Inspect repository status and existing registry before writing; avoid clobbering parallel agents.
2. Establish a unique lowercase kebab-case slug. If target already exists, use its existing slug.
3. Create files from `templates/investigation.md`. Never prefill claims as fact.
4. Capture and cite real evidence. Review limits of available tools; explicitly mark inaccessible screens.
5. Produce a concise executive summary first; then structured observations, hypotheses, reverse-engineered workflows and gaps.
6. Prefer portable capabilities and decision logic over pixel-perfect cloning.
7. Add/update registry record `{slug,name,type,url,status,last_reviewed,summary,tags}`; preserve unrelated records.
8. Validate JSON and local consistency. Commit scoped changes; report exact commit or clearly say commit failed.
9. At handoff report completed work, evidence gaps, untested assumptions, and one next action.

## Multi-agent coordination

Never overwrite another agent's uncommitted changes. If there is concurrent work, use a target-specific branch and reconcile before merging. Claude Code and Codex share identical standards; this file is authoritative. Do not turn an investigation into a full product build unless explicitly asked.

## Universal workbench extension (2026-11-25)
Before action read README, docs/WORKFLOW.md, INTAKE.md, TARGET_PLAYBOOKS.md, GAP_CLOSURE.md, TOOLCHAIN.md, FIDELITY_AND_HANDOFF.md, LEARNING.md and registry/tools.json. Read target BRIEF.json, LAUNCH.md, STATUS and evidence. Existing folders migrate when revisited; do not overwrite them. Owner modes research, selected, fidelity, improve. Research never authorizes implementation; fidelity means independently implemented observable behavior. Record explicit scope, allowed accounts, budget, destination and acceptance before building. Only permitted public/authorized observation; do not bypass access controls, prohibited terms, extract secrets or private data, or attempt to recover private server code. Active probing, instrumentation, load, contract and model-learning tests only in owned/explicitly authorized fixtures. Pin and license-review tools, verify live capabilities, smoke-test on a harmless fixture and preserve receipt before use. One browser driver per scenario; REA is passive observer. Correlate IDs, preserve sanitized evidence, maintain feature dependencies and coverage. Failed and blocked obligations remain in denominator. Verified alternative is not verified target architecture. No silent scope changes or unsupported production-ready claims.

## Developmental intelligence and transfer contract (mandatory)
Before target intake, initialize from current main/branch revision, universal instructions, tool registry, knowledge/index.json and docs/LEARNING.md, docs/COMPARATIVE_EVALUATION.md, docs/TRANSFER_PROTOCOL.md. Search relevant knowledge once goals are known; store the exact baseline revision, selected knowledge IDs and rationale in CONTEXT.json. Record owner questions and exact non-sensitive answers in INTERVIEW.md (append dated changes; redact secrets explicitly), requirements in BRIEF.json, decisions in DECISIONS.md. All investigation output, hypotheses including rejected ones, receipts, comparison results, learning deltas, raw-safe evidence, and handoff artifacts stay inside canonical target folder. Preserve history, no chat-only findings. Research phase never writes product code into this repo beyond bounded independent fixtures.
At every checkpoint and before research closeout, extract discoveries into LEARNING_DELTA.json (including no transferable finding with reason), compare overlapping capabilities with the existing knowledge index, record reuse outcomes and counterexamples. Run structural validation and learning audit. New findings are candidates until evidence and separate review; a repeated observation is corroboration, not automatic promotion. Compare implementations on equivalent fixtures and constraints; retain conditional alternatives and negative results. A single agent may propose but not silently approve its own global policy/default changes. A reviewed card is still scoped, not proof of universal truth. Use a separate reviewer/owner for promotion; record identity/decision and artifact references. Policy/route changes require review and regression. An investigation can close with no promotions or blocked research but cannot omit the learning assessment. Do not claim learning improved performance until measured on comparable held-out tasks.
For independent reconstruction use a distinct owner-approved production repository. Generate and verify an immutable, sanitized handoff package from the investigation; include source commit, manifest hashes, evidence limits, dependency pins/license/test receipts and unresolved obligations. Do not transfer private data, credentials or unauthorized artifacts. Prepare destination with its own AGENTS/CLAUDE instructions, original source link, snapshot manifest and development plan. Keep product source/code in destination; retain research, transfer history and reviewed implementation feedback in target folder. Changes to research or production are proposals until reviewed, not blind two-way sync. Same ChatGPT chat may coordinate, but Git is authoritative. Follow docs/TRANSFER_PROTOCOL.md.

## Preserve developmental intelligence
New knowledge challenges existing intelligence; it never automatically overwrites it. Apply the permanent principle in docs/LEARNING.md. Retrieve relevant variants and counterevidence before selecting a method; benchmark lightweight/direct CLI, REA or Craft Anything as appropriate rather than mandating the heaviest stack. A failed search result is not proof a feature is absent. Use docs/RESOURCE_AUDIT.md and registry/tools.json as discovery inputs; preserve forks/upstreams, review exact versions and license, verify local fixtures and keep external reports separate from local validated knowledge. When discovering a new relevant resource, record its provenance and role before closeout; do not inflate the runtime catalog with unrelated examples or duplicate aliases.