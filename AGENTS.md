# REA — Shared Agent Operating Contract

Applies to Codex, Claude Code, and any other coding agent operating in this repository.

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
