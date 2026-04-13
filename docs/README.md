# Documentation

Four layers of documentation, each answering a different question. Use the decision tree below to find what you need.

---

## The decision tree

```
I just cloned the repo
    └── docs/GETTING_STARTED.md

I understand the basics but want to know WHY it's designed this way
    ├── docs/canonical/repo-topology.md         ← Why the directories are this way
    └── docs/canonical/stack.md                 ← Why we chose each technology

I need to understand a specific crate or system
    ├── crates/<name>/src/lib.rs               ← Module docs (every crate has them)
    └── crates/README.md                       ← Overview of all 27 crates + dependency graph

I need to add a domain type (API contract)
    ├── schemas/README.md                       ← How schemas work
    └── docs/prompt-contracts/README.md         ← What prompt contracts are

I need to build a feature that calls the AI
    └── docs/prompt-contracts/<relevant-file>.md  ← The specific contract for your call

I need to deploy or debug in production
    ├── infra/README.md                        ← Docker vs tofu overview
    └── docs/runbooks/deployments.md           ← Step-by-step deploy + rollback

I need to operate the stack locally
    ├── docs/GETTING_STARTED.md               ← Quick start, clone + run
    └── docs/LOCAL_SETUP.md                  ← Detailed: env vars, infra, multi-dev, deployment

I want to run without any backend (mock data, local AI)
    └── docs/LOCAL_MODE.md                   ← NEXT_PUBLIC_OFFLINE_MODE=true — full frontend, no services needed

I need to add a background job
    └── docs/runbooks/jobs.md                  ← All 17 jobs + lock keys

I found something and want to trace where it came from
    └── docs/source-digests/                   ← Every design decision linked to its source doc

I need to add new infrastructure to AWS
    └── infra/tofu/README.md                   ← Modules, environments, tofu workflow

I found something that looks wrong and want to understand if it's a risk
    └── docs/threat-model/overview.md          ← 6 threats, 7 required controls
```

---

## What each subdirectory is for

| Directory           | What it contains                                                                               | Read it when...                                                    |
| ------------------- | ---------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| `canonical/`        | Design truth — repo structure, stack choices, deployment shape, avatar topology, data platform | You want to understand _why_ something is the way it is            |
| `adrs/`             | Architecture Decision Records — the reasoning behind 4 major choices                           | Same as above, but more detailed "picked this over alternatives"   |
| `source-digests/`   | Traceability links — digests of the 18 source documents that informed the scaffold             | You need to trace a design decision back to its document of origin |
| `prompt-contracts/` | Structured contracts for 17 AI inference calls                                                 | You're building a feature that calls Gemini via `crates/gcp/`      |
| `runbooks/`         | Operational guides — deployments, closed loops, jobs, local ops, hardening                     | You're deploying, debugging, or adding a background job            |
| `threat-model/`     | Security — attack surfaces, trust boundaries, mitigations                                      | You're doing a security review or adding an external integration   |

---

## The reading order (if you want to understand everything)

```
docs/GETTING_STARTED.md                ← Day 1 — setup + orientation
    ↓
canonical/repo-topology.md             ← Why the structure is this way
canonical/stack.md                     ← Why each technology
    ↓
canonical/deployment-topology.md       ← How production is wired
canonical/avatar-topology.md          ← How the 21 avatars work
canonical/data-platform.md             ← Qdrant, Dragonfly, S3 specifics
    ↓
scaffold-file-by-file.md              ← "What is this file?" — the exhaustive reference
    ↓
adrs/                                  ← Deep dives: monorepo, runtime, data, PixiJS
source-digests/                        ← Where each design came from
```

---

## Keeping docs accurate

Docs are part of the codebase. When you change something:

| What you changed                 | Update what                                               |
| -------------------------------- | --------------------------------------------------------- |
| A directory was added or removed | `scaffold-file-by-file.md` + `canonical/repo-topology.md` |
| A new crate was added            | `crates/README.md` + module docs in the crate itself      |
| A new schema was added           | `schemas/README.md`                                       |
| A new AI call was added          | Add a new prompt contract in `docs/prompt-contracts/`     |
| A deployment process changed     | `docs/runbooks/deployments.md`                            |
| A new background job was added   | `docs/runbooks/jobs.md`                                   |
| An ADR was made                  | Add it in `docs/adrs/` with the 000X-naming convention    |
| A design decision was made       | Create an ADR in `docs/adrs/`                             |

Run `pnpm docs:check` to validate the source corpus integrity. It runs in pre-commit automatically.
