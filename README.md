# My Reverse Engineer Agent — universal investigation and reconstruction workbench
One cumulative evidence-grounded system for applications, websites, APIs, extensions, desktop/mobile software, agents, repositories and other software. Claude Code and Codex use the same contract. REA is one provider, not the entire system.

## Start here
1. [AGENTS.md](AGENTS.md) — authoritative instructions.
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
python scripts/intelligence.py review --slug example --id candidate-id --reviewer reviewer-id --decision validated --reason "Independent fixture reproduced"
python scripts/intelligence.py verify-package --slug example
```
Review is an explicit local index update, not autonomous certification. Run it only after an actual separate review; the script checks record shape, local artifact references and comparison eligibility, not truth or human identity. No global default is changed by the CLI.