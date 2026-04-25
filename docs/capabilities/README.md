# Capabilities Documentation

## Overview

The Capability Harness Cortex layer provides a structured execution framework for AI-powered avatar capabilities. It consists of:

- **Capability Registry** — Define, query, and manage available capabilities
- **Avatar Grants** — Per-avatar permission model controlling which avatars can execute which capabilities
- **Cortex Context Pack Builder** — Assembles bounded context from Foundation, Intel, Campaign, Office, and Ripple data
- **Capability Execution Engine** — Executes capabilities via AWS Bedrock with draft/dry-run modes
- **Ripple Harvester** — Extracts learning atoms from capability outputs for future context enrichment
- **Artifact Versioning** — Tracks and versions capability output artifacts

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     HTTP API (axum)                         │
│  capabilities | avatar-capabilities | context-packs        │
│  capability-runs | artifacts                                │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              raptorflow-harness crate                       │
│  ┌─────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │   Cortex    │  │ ExecutionEngine  │  │ RippleHarv.. │  │
│  │ (context    │  │ (Bedrock calls,  │  │ (extract     │  │
│  │  assembly)  │  │  guardrails)     │  │  candidates) │  │
│  └─────────────┘  └──────────────────┘  └──────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           CapabilitySeeder (5 safe defaults)        │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              raptorflow-db (SQLx)                           │
│  capability_definitions | avatar_capability_grants          │
│  harness_context_packs | capability_runs                   │
│  capability_artifacts | artifact_versions                  │
│  artifact_ripple_links                                     │
└─────────────────────────────────────────────────────────────┘
```

## API Endpoints

| Method | Path                                                | Description                        |
| ------ | --------------------------------------------------- | ---------------------------------- |
| GET    | `/api/v1/capabilities`                              | List all capabilities              |
| POST   | `/api/v1/capabilities/defaults`                     | Ensure default capabilities seeded |
| GET    | `/api/v1/capabilities/{id}`                         | Get capability by ID               |
| GET    | `/api/v1/capabilities/key/{key}`                    | Get capability by key              |
| GET    | `/api/v1/avatars/{id}/capabilities`                 | List capabilities for an avatar    |
| POST   | `/api/v1/avatars/{id}/capabilities`                 | Grant capability to avatar         |
| DELETE | `/api/v1/avatars/{id}/capabilities/{capability_id}` | Revoke capability from avatar      |
| POST   | `/api/v1/harness/context-packs`                     | Build and store context pack       |
| GET    | `/api/v1/harness/context-packs/{id}`                | Get context pack by ID             |
| GET    | `/api/v1/capability-runs`                           | List capability runs               |
| POST   | `/api/v1/capability-runs`                           | Create and execute capability run  |
| GET    | `/api/v1/capability-runs/{id}`                      | Get capability run by ID           |
| GET    | `/api/v1/artifacts`                                 | List artifacts                     |
| GET    | `/api/v1/artifacts/{id}`                            | Get artifact by ID                 |
| POST   | `/api/v1/artifacts/{id}/versions`                   | Create new artifact version        |

## Seeded Capabilities

| Key                               | Name                             | Domain     | Risk   |
| --------------------------------- | -------------------------------- | ---------- | ------ |
| `foundation.icp.refine`           | ICP Refinement                   | Foundation | Low    |
| `foundation.positioning.generate` | Positioning Statement Generation | Foundation | Low    |
| `offer.core.design`               | Core Offer Design                | Offer      | Medium |
| `copy.hooks.generate`             | Hook Copy Generation             | Copy       | Low    |
| `content.calendar.plan`           | Content Calendar Planning        | Content    | Low    |

## Guardrails

- Avatar capability grants are validated before every execution
- Execution modes: `draft` (requires Bedrock) and `dry_run` (no Bedrock required)
- Draft mode returns 503 if Bedrock is unavailable
- All org-scoped queries include `org_id` from TenantContext
- No Prisma access in any capability harness code
- No bypass of TenantContext isolation
