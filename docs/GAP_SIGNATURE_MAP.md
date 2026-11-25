# Gap signature map

Baseline 5d7119db5ea16d4466a9d80f13e6b274c6dfc6f7. All 33 existing route IDs mapped below. A dash means no defensible single recovery layer; NONE means no specific supplied signature or intake-driven route. Do not automatically dispatch NONE. Signatures are observations, not causes guessed from route names; alternate signatures require recorded evidence. All listed local catalog tools are NOT_RUN; cataloged-only, not integrated or healthy. REA is a documented upstream boundary, not a verified local adapter. No absent candidate referenced by route IDs.

| Route | Primary layer | Conditional signature(s) | Candidate provider IDs (existing order) | Qualification |
|---|---|---|---|---|
| feature-discovery | — | NONE | rea, playwright, obscura, omniget, last30days, github | Product scope discovery is orthogonal to five technical layers; manual obligation intake. |
| frontend-motion | — | NONE | playwright, rea, obscura, axe, craft, rea-video | Visual interaction is cross-layer; needs screen/scenario coverage, not a binary failure signature. |
| client-code | static | PACKED / ENCRYPTED_STRINGS | rea, tree-sitter, semgrep, ghidra, jadx, ilspy, webcrack, rz-ghidra, angr | Only when observed; ordinary source inventory needs explicit intake. |
| api-contract | transport | UNKNOWN_PROTOCOL | rea, mitmproxy, quicktype, openapi-generator, schemathesis, wiremock, pact, fast-check, testcontainers, wireshark, blackboxprotobuf, eventsource-parser | Also missing schema may be ordinary incomplete evidence. |
| data-schema | persistent-state | NONE | quicktype, sqlglot, prisma, dbt, postgres, hypothesis, testcontainers, z3 | No supplied signature denotes semantic schema absence; explicit gap. |
| auth-permissions | cross-boundary | NONE | nango, keycloak, authlib, playwright, z3, testcontainers | Authorization semantics are not PINNED; record scope and denial. |
| business-logic | persistent-state | NONE | aalpy, learnlib, daikon, z3, hypothesis, fast-check, tlaplus, automatalib | State rules may span dynamic dispatch; missing semantics not a binary signature. |
| integrations | cross-boundary | NONE | composio, nango, activepieces, airbyte, mcp-registry, n8n, treg, wiremock, testcontainers | Manual boundary inventory or observed interface failure. |
| backend-architecture | — | NONE | craft, openapi-generator, temporal, opentelemetry, testcontainers | Remote architecture not identifiable from interface alone; manual review. |
| algorithm | dynamic-dispatch | NONE | scikit-learn, optuna, z3, hypothesis, promptfoo | Opaque behavior alone is not evidence of dispatcher loop. |
| training-data | — | NONE | distilabel, argilla, sdv, promptfoo, deepeval, ragas | Not one of five runtime layers; unavailable original data is a residual. |
| agent-behavior | dynamic-dispatch | NONE | promptfoo, deepeval, ragas, hermes, openviking, fast-check | Behavioral evaluation, not native branch failure. |
| async-workflow | dynamic-dispatch | NONE | pm4py, temporal, tlaplus, opentelemetry, aalpy, testcontainers, automatalib | State/workflow ordering requires scenario evidence. |
| binary-format | static | PACKED / UNKNOWN_PROTOCOL | kaitai, kaitai-compiler, kaitai-formats, rea, ghidra, hypothesis, pbtk, ipsw | Unknown container is not necessarily packing; signature conditional. |
| performance | — | NONE | k6, locust, opentelemetry, testcontainers | Cross-cutting; timeout alone is not adversarial. |
| deployment | — | HOST_UNSUPPORTED | testcontainers, postgres, temporal, replit, opentelemetry | Only observed host incompatibility; ordinary deployment is cross-cutting. |
| edge-cases | — | NONE | hypothesis, fast-check, schemathesis, playwright, z3 | Cross-cutting acceptance test obligation. |
| network-data | persistent-state | NONE | networkx, neo4j, sdv | Graph/relationship data; not network transport. |
| migration | persistent-state | NONE | openrewrite, tree-sitter, fast-check, hypothesis, testcontainers | Schema migration semantics; general code migration cross-cutting. |
| native-symbolic-analysis | dynamic-dispatch | UNRESOLVED_INDIRECT / DISPATCHER_LOOP | rea, ghidra, rz-ghidra, angr, triton, z3, hypothesis | Require concrete failure observation. |
| code-deobfuscation | static | ENCRYPTED_STRINGS / PACKED / DISPATCHER_LOOP | rea, tree-sitter, webcrack, js-deobfuscator, angr, triton, d810-ng | Dispatcher loop may require dynamic layer; authorized artifact only. |
| cross-platform-emulation | dynamic-dispatch | HOST_UNSUPPORTED / DISPATCHER_LOOP | rea, ghidra, unicorn, qiling, qemu, renode | Only on supported, permitted fixture. |
| runtime-instrumentation | dynamic-dispatch | UNRESOLVED_INDIRECT | rea, qbdi, rr | Host unsupported is distinct; instrumentation does not authorize access. |
| deterministic-replay | dynamic-dispatch | NONE | rea, rr, panda, tlaplus, fast-check | No nondeterminism signature supplied; explicit replay obligation. |
| binary-protocol-inference | transport | UNKNOWN_PROTOCOL | rea, wireshark, blackboxprotobuf, pbtk, kaitai, hypothesis | Preserve wire bytes and ambiguity. |
| apple-platform-analysis | static | HOST_UNSUPPORTED | rea, ghidra, ipsw, ipsw-py | Format/host capability; protected data remains out of scope. |
| gpu-shader-analysis | static | SHADER_OPAQUE | rea, renderdoc, spirv-tools, spirv-cross, directx-shader-compiler | Static shader unknown; runtime frames require separate obligation. |
| local-model-analysis | static | MODEL_GRAPH_UNKNOWN | rea, netron, onnx, onnxruntime, litert, coremltools, promptfoo | Header/graph distinction; model behavior independent. |
| isolated-execution | — | HOST_UNSUPPORTED | bubblewrap, nsjail, firecracker, qemu, testcontainers | Cross-cutting precondition, not analysis layer. |
| realtime-media-protocol | transport | UNKNOWN_PROTOCOL | rea, wireshark, aioquic, aiortc, eventsource-parser, playwright | PINNED is a transport observation, not permission to circumvent. |
| embedded-firmware | static | PACKED / HOST_UNSUPPORTED | rea, ghidra, kaitai, qiling, renode, qemu, littlefs | Dynamic/persistent sub-obligations separate. |
| resource-recovery | — | TIMEOUT_ADVERSARIAL / HOST_UNSUPPORTED | rea, rz-ghidra, ghidra, angr | Only when supported by observed signature; ordinary budget exhaustion has no proposed specific enum. |
| system-runtime-analysis | dynamic-dispatch | UNRESOLVED_INDIRECT / HOST_UNSUPPORTED | rea, panda, rr, libvmi, hyperdbg, qemu | Cross-system boundary can require separate stage. |

## Signature dispatch semantics
PACKED: supported format inspection first; ENCRYPTED_STRINGS: observed opaque string representation on authorized artifact; DISPATCHER_LOOP: observed flattened/looping control flow; UNRESOLVED_INDIRECT: unresolved target set; PINNED: confirmed trust constraint, stop restricted lane and use authorized evidence; UNKNOWN_PROTOCOL: actual undecoded framing; HOST_UNSUPPORTED: capability or host refusal; TIMEOUT_ADVERSARIAL: positive evidence of time-sensitive/adversarial behavior, not ordinary slowness; SHADER_OPAQUE: unresolved shader representation; MODEL_GRAPH_UNKNOWN: absent/unsupported graph; NONE: no specific signature. A route may require multiple stage layers; cross-cutting rows must be explicitly planned. Failure signatures do not override permissions. No unbounded retry. For ordinary resource limits, first recover and configure REA; Phase 2 review may propose additional signatures for budget, nondeterminism, contradiction, permission, schema missing and state semantics instead of forcing false matches.
