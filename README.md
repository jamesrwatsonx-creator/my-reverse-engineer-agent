# My Reverse Engineer Agent (REA)

**Private reverse-engineering research repository for Claude Code and Codex.**

Every application, website, repository, product, agent, API or system gets **one permanent investigation folder**. This is a cumulative, evidence-grounded knowledge base for understanding existing systems and identifying reusable ideas, patterns, capabilities and opportunities.

## Quick start

Tell Claude Code or Codex:

> Reverse engineer [TARGET / URL] and save the investigation to my private GitHub repository `jamesrwatsonx-creator/my-reverse-engineer-agent`. Follow `AGENTS.md`. Reuse the target folder if it already exists; otherwise create `investigations/<target-slug>/`. Begin with a high-level analysis, then inspect features, UX, branding, architecture hypotheses, evidence and reusable capabilities. Update `registry/index.json` and commit resumable checkpoints. Never confuse inference with verified facts.

## Repository

```text
my-reverse-engineer-agent/
├── README.md                   # Introduction and quick start
├── AGENTS.md                   # Shared rules for Codex + Claude Code
├── CLAUDE.md                   # Claude Code entrypoint
├── investigations/
│   ├── README.md
│   └── <target-slug>/
│       ├── README.md           # Target overview, status, verdict
│       ├── features.md         # Feature inventory and user value
│       ├── experience.md       # Branding, visual system, UX and motion
│       ├── architecture.md     # Known behavior versus hypotheses
│       ├── evidence.md         # Sources, dates and reproducible steps
│       ├── capabilities.md     # Portable implementation patterns
│       ├── opportunities.md    # Differentiation and build options
│       └── assets/             # Authorized sanitized captures
├── templates/
│   └── investigation.md        # Canonical investigation template
└── registry/
    └── index.json              # Searchable investigation catalog
```

## Research principles

- **OBSERVED** means directly witnessed and recorded.
- **DOCUMENTED** means a cited first-party specification or other identified source.
- **INFERRED** means a plausible explanation that still requires validation.
- **UNKNOWN** means not established.

Do not present inferred internal architecture as confirmed. Preserve provenance, confidence, capture method, and limitations. Only inspect authorized or publicly accessible resources. Never store secrets, account data or copyrighted third-party source code without permission. Independently implement reusable patterns rather than copying proprietary software.

## Integration with Maliky Repository Intelligence

REA discovers and explains **external systems and patterns**. Maliky Repository Intelligence catalogs **owned repositories and reusable assets**. Later, verified REA capability records can be exported with provenance into Repository Intelligence without contaminating its owned-source evidence.

## Completion criteria

Each investigation has a uniquely named target folder, evidence, high-level summary, feature inventory, UX notes, architecture uncertainty, reusable capability records, next actions, a current registry entry and a commit. Mark work `PARTIAL` or `BLOCKED` when evidence or access is insufficient.
