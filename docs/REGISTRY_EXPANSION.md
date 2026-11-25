# Registry reconciliation — 22 requested candidates

Baseline 5d7119db5ea16d4466a9d80f13e6b274c6dfc6f7: 152 entries, all 22 already present, source_status=candidate-unverified, runtime_status=NOT_RUN, pin=null and license_review=PENDING. No duplicate additions; metadata-only enrichment using phase1_priority, phase1_capability, upstream_overlap. Repository paths are existing catalog URLs, not fresh independent canonical redirect or release checks. No provider invocation or installation attempted; availability UNAVAILABLE/unknown until local health and fixture pass. Preserve existing route references and other entries.

| Priority | ID | Repository path | Capability | REA overlap | Status |
|---|---|---|---|---|---|
| very-high | angr | https://github.com/angr/angr | Symbolic binary analysis; indirect-dispatch hypotheses | Partial: native Ghidra value flow; symbolic execution distinct | candidate-unverified / NOT_RUN |
| very-high | triton | https://github.com/JonathanSalwan/Triton | Dynamic symbolic execution and expression analysis | Partial: Ghidra/Frida observations; symbolic execution distinct | candidate-unverified / NOT_RUN |
| very-high | qiling | https://github.com/qilingframework/qiling | OS-aware binary and firmware emulation | Partial: native artifact inspection; execution emulation distinct; not full-system universally | candidate-unverified / NOT_RUN |
| very-high | webcrack | https://github.com/j4k0xb/webcrack | JavaScript normalization/deobfuscation | Partial: REA JavaScript graph and source analysis; compare transformations | candidate-unverified / NOT_RUN |
| high | unicorn | https://github.com/unicorn-engine/unicorn | CPU instruction emulation on controlled fixtures | Partial: native disassembly; CPU emulation distinct | candidate-unverified / NOT_RUN |
| high | blackboxprotobuf | https://github.com/nccgroup/blackboxprotobuf | Schema-less Protobuf interpretation and re-encoding | Substantial: REA wire fields, framing and candidate readings; re-encoding/inference needs fixture | candidate-unverified / NOT_RUN |
| high | pbtk | https://github.com/marin-m/pbtk | Descriptor recovery from authorized artifacts | Partial: REA supplied FileDescriptorSet interpretation; descriptor discovery distinct | candidate-unverified / NOT_RUN |
| high | wireshark | https://github.com/wireshark/wireshark | Packet and protocol inspection | Partial: native HAR/SAZ/mitmproxy/qlog and tested HTTP/3 profile; general packet capture distinct | candidate-unverified / NOT_RUN |
| high | ipsw | https://github.com/blacktop/ipsw | Apple firmware and binary artifact inspection | Partial: native artifact readers; specialized Apple coverage requires comparison | candidate-unverified / NOT_RUN |
| high | panda | https://github.com/panda-re/panda | Whole-system record/replay | Partial: browser scenario replay is not whole-system replay | candidate-unverified / NOT_RUN |
| high | rr | https://github.com/rr-debugger/rr | Deterministic Linux process replay | Partial: native debugger/Frida observations; deterministic replay distinct | candidate-unverified / NOT_RUN |
| high | qbdi | https://github.com/QBDI/QBDI | Dynamic binary instrumentation | Partial: Frida and debugger providers; instruction coverage compare | candidate-unverified / NOT_RUN |
| high | renderdoc | https://github.com/baldurk/renderdoc | Owned graphics-frame inspection | Partial: static GPU metadata, not graphics runtime | candidate-unverified / NOT_RUN |
| high | spirv-tools | https://github.com/KhronosGroup/SPIRV-Tools | SPIR-V IR validation and analysis | Partial: static CUDA/HIP/PTX inspection is not SPIR-V validation | candidate-unverified / NOT_RUN |
| high | netron | https://github.com/lutzroeder/netron | Local model graph visualization | Partial: GGUF/safetensors declarations, not executable graph | candidate-unverified / NOT_RUN |
| high | onnx | https://github.com/onnx/onnx | ONNX model structure and validation | Distinct: REA model artifact guide explicitly excludes ONNX | candidate-unverified / NOT_RUN |
| high | firecracker | https://github.com/firecracker-microvm/firecracker | MicroVM isolation component | Distinct: REA provider cleanup not a host isolation guarantee | candidate-unverified / NOT_RUN |
| high | bubblewrap | https://github.com/containers/bubblewrap | Linux namespace isolation component | Distinct: no comparable supervisor isolation contract established | candidate-unverified / NOT_RUN |
| high | nsjail | https://github.com/google/nsjail | Controlled process isolation component | Distinct: no comparable supervisor isolation contract established | candidate-unverified / NOT_RUN |
| specialized | libvmi | https://github.com/libvmi/libvmi | Approved guest introspection | Partial: process observation, not hypervisor guest introspection | candidate-unverified / NOT_RUN |
| specialized | hyperdbg | https://github.com/HyperDbg/HyperDbg | Dedicated approved hypervisor debugging lab | Partial: GDB/Rizin/Frida, not hypervisor-level observation | candidate-unverified / NOT_RUN |
| specialized | rz-ghidra | https://github.com/rizinorg/rz-ghidra | Alternative Rizin Ghidra decompilation backend | Substantial: REA Ghidra and Rizin interfaces; alternate backend only for measured delta | candidate-unverified / NOT_RUN |

Canonical paths and lineage need rechecking with source freshness protocol before selection; no fixed versions or paths introduced. Prefer REA where actual operation/fixture passes. Qiling is OS-aware emulation, not universal full-system emulation. Isolation components require host, privilege and confinement validation; no claim of a safe sandbox. No authorization/DRM/security bypass lane. Record exact source, license, host, live schemas, test receipt and restrictions before any promotion.
