# Provisioning manifest — Phase 3

Run `bash scripts/provision-check.sh` from any shell with Bash and Python 3.11+; `--manifest-only` performs no probes. The script reads registry/tools.json and routes/provisioning.json and validates graph coverage. It does not install, authenticate or execute any target. Commands are candidate setup instructions, not tested pins. All real analysis versions remain NOT_TESTED; resolve latest source/license/host and run approved fixtures before promotion. For Python packages use an isolated virtual environment; no automatic installation. REA stays a separate MCP/CLI process. Discovery adapters require configured authorization/backend; a successful gh version is not a valid token.

| Provider | Install instruction | Host requirements | Tested analysis version |
|---|---|---|---|
| rea | npm install --global rea-agents | Node.js/npm; provider-specific dependencies; CLI/MCP health | NOT_TESTED |
| mitmproxy | python -m pip install mitmproxy | supported Python; local authorized capture only | NOT_TESTED |
| wireshark | Install Wireshark/TShark via official OS package manager (e.g. apt install tshark on Debian/Ubuntu) | OS package; authorized capture permissions | NOT_TESTED |
| blackboxprotobuf | python -m pip install blackboxprotobuf | supported Python; reviewed dependency/license | NOT_TESTED |
| aalpy | python -m pip install aalpy | supported Python; controlled oracle fixture | NOT_TESTED |
| learnlib | Use Maven dependency de.learnlib:learnlib-distribution after reviewing official release | matching JDK/Maven; fixture | NOT_TESTED |
| hypothesis | python -m pip install hypothesis | supported Python | NOT_TESTED |
| ghidra | Download official Ghidra release and extract; use documented analyzeHeadless launcher | supported OS and matching full JDK | NOT_TESTED |
| qiling | python -m pip install qiling | supported host/arch and reviewed fixture runtime | NOT_TESTED |
| unicorn | python -m pip install unicorn | supported host/arch | NOT_TESTED |
| angr | python -m pip install angr | supported Python/architecture | NOT_TESTED |
| triton | python -m pip install triton-library | supported Python/architecture; distinguish from GPU Triton | NOT_TESTED |
| github_search | Install GitHub CLI via official OS package manager (e.g. apt install gh); gh auth login | gh executable; explicit public-research authorization and token; rate budget | NOT_TESTED |
| browser_research | python -m pip install playwright; python -m playwright install chromium (optional capture backend) | authorized capture callback; browser dependencies if used; HAR fixture needs only Python | NOT_TESTED |
| knowledge_retrieval | Included Python module; no package installation required | SQLite ledger; optional approved web callback | NOT_TESTED |

Only synthetic stage graphs are authored. Do not invoke any real analysis stage or use discovery to bypass access restrictions. No auto-copy, auto-install or provider promotion. For browser research use sanitized permitted evidence; capture backend must independently establish authorization. Source freshness rules remain applicable.

## Ladder and streaming addendum

Manifest covers providers across all four rungs of schema v2. Empty rungs declare no capability. Circuit breakers and content-addressed IO.read capture are standard-library fixture components; no additional installation. Live CDP/REA capture adapter and credentials are not provisioned here. Temporal/LangGraph are future durable-execution candidates; no framework installed or selected. See the Phase 3 report for fixture limits and CI evidence.
