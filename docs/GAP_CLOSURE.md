# Replace speculation with observable evidence and tested alternatives
Goal: maximize observable equivalence without claiming inaccessible originals.
| Surface | Stronger method | Candidate IDs | Acceptance and residual limit |
|---|---|---|---|
| Frontend / motion | viewport/style/DOM/a11y/timed screenshots | playwright, rea, obscura, axe, craft | visual and behavior comparison, licensed assets |
| Client JS | allowed shipped bundle graph and syntax analysis | rea, tree-sitter, semgrep | trace documented behavior, no hidden source |
| API | official specs + sanitized permitted samples, type inference and mocks | rea, mitmproxy, quicktype, openapi-generator, schemathesis, wiremock, pact | independent contract tests on own/sandbox APIs; private server unknown |
| Data structures | lawful exports, types/nulls/enums, keys and cardinality | quicktype, sqlglot, prisma, hypothesis, dbt | held-out validation and round-trip constraints |
| Authentication | published OAuth scopes, test roles, connect/revoke/expiry | nango, keycloak, authlib, playwright | independent tenant isolation, revocation and lifecycle |
| Business logic | state machines, decision tables, invariants and counterexamples on permitted fixtures | aalpy, learnlib, hypothesis, temporal, craft | held-out input/state/output; unseen rules remain unknown |
| Third-party integrations | provider docs, per-action/trigger/scope mapping, permitted connector sandbox | composio, nango, activepieces, airbyte, mcp-registry, n8n, treg | verify each action, webhook, retry, disconnect; catalog count not proof |
| Database schema | derive entities/relationships/lifecycle from lawful samples and workflows | prisma, sqlglot, dbt, postgres, sdv | independent schema satisfies constraints; exact remote tables/indexes unknown |
| Private server source | public interfaces and independent architecture | craft, openapi-generator, temporal, opentelemetry | source inaccessible; no attempts to obtain it |
| Proprietary algorithms | define task/objective, representative lawful fixtures, independent alternative methods | hypothesis, scikit-learn, optuna, promptfoo | held-out quality/latency; no guarantee of original, no extraction/model stealing |
| Private training data | task-specific licensed/open/consented + synthetic data, dedupe/curate, split by entity/time | distilabel, argilla, sdv, promptfoo, deepeval, ragas | data card, consent/license, contamination and privacy checks, human review, held-out eval; original dataset unavailable |
| Existing network / relationships | opt-in network, lawful seed data, synthetic graph | networkx, neo4j, sdv | independent matching quality/cold start; existing users/history unrecoverable |
Each gap gets ID, feature/obligation, current status, evidence, competing explanations, discriminating test, allowed scope, target tolerance, result, residual uncertainty, cost and owner disposition. Prioritize critical obligations and highest evidence gain. Active testing only on owned or explicitly permitted fixtures; prohibited lanes stay blocked. Production readiness separate from fidelity.
