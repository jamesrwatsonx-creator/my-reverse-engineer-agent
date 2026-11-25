# Route by target type
| Kind | Inspect/observe | Independent reconstruction and tests |
|---|---|---|
| web | public docs, Playwright/Obscura, REA passive CDP/JS/HAR, accessibility/style snapshots | screen/route map, motion tokens, contracts, viewport/workflow replay |
| desktop | authorized artifact path/hash, runtime detection, REA Electron/ASAR or native Ghidra conditional | IPC/file formats/local state, independent shell and smoke tests |
| mobile | official approved artifact/emulator, Appium, REA/JADX/Apktool when allowed | navigation, permission, offline and device tests |
| extension | approved manifest/permission declarations, owned browser profile | popup/background/content lifecycle, messaging, MV3 fixture tests |
| api | official OpenAPI/GraphQL/MCP docs, authorized samples, sandbox | schemas, pagination, errors, contracts, mocks, auth scopes |
| agent | public docs/tool declarations, permitted conversations/own fixtures | memory, tools, policy, schedules, approval and stochastic outcome eval |
| repository | pinned commit, license, manifests, source/tests, isolated safe build | capability graph, reproducible tests, integration compatibility |
| game | authorized offline build/docs, controls, mechanics | independent scene/state/input tests; no cheating or protection bypass |
| data | licensed schema/model card/sample | statistical validation, independent synthetic/consented dataset |
| other | determine format, actors, constraints, interface | choose closest lanes and disclose unknowns |
Mixed targets may combine lanes. Feature atlas dynamically covers onboarding/auth/roles, navigation, interactions/motion, CRUD/search/filter, import/export, collaboration, billing, messaging, integration, automation, realtime/offline, AI, analytics, notifications, accessibility, localization, security/privacy and admin when relevant. Capture primary and cross-feature journeys, empty/error/permission states, lifecycle and retries. Do not impose irrelevant features or fixed dossier count.


After reconnaissance and owner scope, follow docs/GAP_ENGINE.md and GAP_TOOL_RECIPES.md. Populate GAP_REGISTER.json with scoped obligations and explicit gap classes; run gap_engine.py plan --slug <target>, choose verified tools by evidence and gap, record attempts/fixtures/results/residuals, run audit at handoff and route reusable lessons through LEARNING_DELTA. Do not use irrelevant or unauthorized tools. No arbitrary fidelity percentage.

## Mixed and specialized targets
For authorized native, firmware, graphics, model and streaming surfaces, select advanced gap routes after classification. Use upstream built-in inventory before optional specialist tools. Dedicated approved fixtures and isolation gates precede dynamic analysis. See ADVANCED_ANALYSIS.md.
