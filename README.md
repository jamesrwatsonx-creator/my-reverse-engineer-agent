# My Reverse Engineer Agent — universal investigation and reconstruction workbench
One cumulative evidence-grounded system for applications, websites, APIs, extensions, desktop/mobile software, agents, repositories and other software. Claude Code and Codex use the same contract. REA is one provider, not the entire system.

## Start here
1. [AGENTS.md](AGENTS.md) — authoritative instructions; first perform the [upstream freshness review](docs/UPSTREAM_REVIEW.md) and [Replit assessment](docs/REPLIT.md).
2. [Workflow](docs/WORKFLOW.md), [intake](docs/INTAKE.md), [target playbooks](docs/TARGET_PLAYBOOKS.md).
3. [Gap closure](docs/GAP_CLOSURE.md), [toolchain](docs/TOOLCHAIN.md), [searchable candidate catalog](registry/tools.json).
4. [Fidelity and handoff](docs/FIDELITY_AND_HANDOFF.md), [cumulative learning](docs/LEARNING.md), [reference projects](docs/REFERENCE_PROJECTS.md), [status](docs/STATUS.md).

## ChatGPT → coding agent
Tell ChatGPT: "Go to my reverse engineer agent repo and prepare to investigate [target]." It reads the universal contract, assesses the public target, asks only missing essentials (0–3 questions), prepares/updates the canonical investigation folder, records owner scope and generates LAUNCH.md. Open this repo in Claude Code or Codex and paste the target launch prompt. The agent executes the appropriate gated workflow. Build independently only when authorized.

Python 3.10+ (stdlib):
```sh
python scripts/workbench.py prepare --slug example --name Example --target https://example.com --kind web --mode selected --goal "Reproduce selected workflow"
python scripts/workbench.py plan --kind web
python scripts/workbench.py preflight --kind web
python scripts/workbench.py validate --slug example
python -m unittest discover -s tests -v
```
Preparation does not access target or install/run external providers. Existing investigations remain intact. This is an execution scaffold, not a completed integrated runtime; selected providers require real host verification.

## Developmental learning and production transfer
Read [comparative evaluation](docs/COMPARATIVE_EVALUATION.md), [learning lifecycle](docs/LEARNING.md), [two-repository transfer](docs/TRANSFER_PROTOCOL.md), [ChatGPT project workflow](docs/CHATGPT_PROJECT.md). Every target retains interview, baseline context, decisions, receipts, learning deltas and handoff manifest. The shared knowledge index stores reviewed capability variants, methods, compatibility and negative results; never treats folder count as intelligence.

```sh
python scripts/intelligence.py search --query "webhook retry"
python scripts/intelligence.py audit --slug example
python scripts/intelligence.py compare --file path/to/comparison.json
python scripts/intelligence.py review --slug example --id candidate-id --reviewer reviewer-id --decision validated --reason "Independent fixture reproduced" --receipt investigations/example/review.md
python scripts/intelligence.py verify-package --slug example
```
Review is an explicit local index update, not autonomous certification. Run it only after an actual separate review; the script checks record shape, local artifact references and comparison eligibility, not truth or human identity. No global default is changed by the CLI.

## Resource coverage and challenge principle
[Resource audit](docs/RESOURCE_AUDIT.md) tracks prior-project sources, fork/upstream relationships, benchmark challengers and reference case discovery. [Tool registry](registry/tools.json) distinguishes candidates from verified runtime providers. The central learning principle is to challenge existing knowledge with new evidence, preserve conditional alternatives and change defaults only after review and regression.

[All-resource freshness protocol](docs/RESOURCE_FRESHNESS.md) and [initial source baseline](registry/source_baseline.json): refresh entire catalog, original upstreams and useful owner repositories at each investigation, review deltas and keep installed pins separate. Use `python scripts/resource_refresh.py --output report.json` with authenticated GitHub CLI; read-only metadata/release/compare collection, not automatic installation.

[Universal Gap Closure Engine](docs/GAP_ENGINE.md), [tool recipes](docs/GAP_TOOL_RECIPES.md), and [gap routing registry](registry/gap_routes.json) connect target observations to testable evidence and independent reconstruction. `python scripts/gap_engine.py plan --slug <target>` and `python scripts/gap_engine.py audit --slug <target>` operate on target GAP_REGISTER.json. Explicitly classify gaps before planning; no tool installs or target access by this utility.

## Advanced fallback architecture
[Advanced analysis](docs/ADVANCED_ANALYSIS.md) records upstream compatibility, specialized routes and provider acceptance. Catalog 152 entries (including reference-only leads); 33 gap routes. Planner emits limitation-sensitive fallback steps; external provider execution and verification remain separate.
