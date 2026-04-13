# Schemas — the API contract source of truth

Every type that crosses the frontend↔backend boundary starts as a JSON schema here. The Rust types in `crates/contracts/` and the TypeScript types in `packages/contracts/` are both **generated from these files** — never written by hand.

This means:

- Frontend and backend always agree on exact type shapes
- A schema change fails fast (at generation time), not at runtime
- OpenAPI specs can be derived automatically
- Queue message formats are versioned alongside the code

If Rust and TypeScript ever disagree, the schema wins.

---

## The four schema categories

### `domain/` — Business entities

The things your users care about: campaigns, tasks, nudges, intelligence alerts, daily briefings.

```
schemas/domain/
    ├── campaign.json
    ├── nudge.json
    ├── daily-wins-brief.json
    ├── intel-alert.json
    └── tenant-contract.json     ← Every domain entity extends this
```

Every domain entity schema includes:

```json
{
  "required": ["org_id", "created_at", "updated_at"],
  "properties": {
    "org_id": { "type": "string", "format": "uuid" },
    "created_at": { "type": "string", "format": "date-time" },
    "updated_at": { "type": "string", "format": "date-time" }
  }
}
```

**Why `org_id` is required on every entity:** RaptorFlow is multi-tenant. Every row in every table is scoped to an organization. The schema enforces this at the type level — if you try to serialize a domain entity without an `org_id`, it fails validation.

### `queues/` — Background job messages

Job payloads for AWS SQS workers. These are what gets put on the queue when a background task is dispatched.

```
schemas/queues/
    ├── embedding-job.json       ← Ripple text → vector embedding
    ├── content-pregeneration-job.json  ← AI content generation
    ├── intern-task.json         ← Intern agent task dispatch
    ├── research-request.json    ← Competitive research task
    └── tool-gateway-request.json ← Tool invocation from AI agent
```

Queue schemas are versioned. When you change a job payload shape, create a new schema version and keep the old one until all workers have migrated.

### `ws/` — WebSocket events

Real-time events pushed to the frontend over WebSocket connections.

```
schemas/ws/
    ├── office-event.json        ← Office canvas: avatar movement, snark, zone changes
    ├── council-event.json       ← Council session: position taken, synthesis, vote
    └── session-event.json       ← Session: agent activity, memory updates, errors
```

Office events use dotted namespacing: `office.event.avatar.moved`, `office.event.snark.received`. This makes them easy to filter on the frontend.

### `openapi/` — REST API specification

`api-v1.yaml` is the OpenAPI v3 spec for the HTTP API. It's derived from the route definitions in `crates/http/src/lib.rs` and the domain schemas. You don't edit it directly.

---

## The sync process

```bash
pnpm contracts:sync
```

This runs `scripts/sync-contracts.mjs`, which:

1. Reads every `.json` file in `schemas/domain/`, `schemas/queues/`, and `schemas/ws/`
2. For each schema, generates a Rust struct in `crates/contracts/src/lib.rs` (using a codegen template)
3. Generates a TypeScript type in `packages/contracts/src/` (matching the JSON Schema type shape)
4. Writes both files

The generated files are committed to git. This means:

- A schema change appears as a diff in both `crates/` and `packages/` — easy to review
- CI validates that generated code matches schemas (`pnpm contracts:check`)

---

## Adding a new schema

### Step 1 — Choose the right directory

| Type                                    | Directory         |
| --------------------------------------- | ----------------- |
| Business entity (campaign, task, alert) | `schemas/domain/` |
| Background job payload                  | `schemas/queues/` |
| Real-time event                         | `schemas/ws/`     |

### Step 2 — Write the schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://raptorflow.dev/schemas/domain/my-entity.json",
  "title": "MyEntity",
  "type": "object",
  "required": ["org_id", "name", "created_at"],
  "properties": {
    "org_id": {
      "type": "string",
      "format": "uuid",
      "description": "Tenant — every entity is scoped to an org"
    },
    "name": {
      "type": "string",
      "minLength": 1,
      "maxLength": 255
    },
    "status": {
      "type": "string",
      "enum": ["draft", "active", "archived"],
      "default": "draft"
    },
    "metadata": {
      "type": "object",
      "additionalProperties": true,
      "description": "Extensible — allows forward compatibility"
    }
  }
}
```

### Rules for schema authors

**Naming:**

- `title` → `PascalCase` → becomes the type name in both Rust (`struct MyEntity`) and TypeScript (`type MyEntity = ...`)
- File name → `kebab-case` → `my-entity.json`
- Fields → `camelCase` → `campaignName`, not `campaign_name`

**Required fields — every entity must have:**

- `org_id: uuid` — tenant isolation at the type level
- `created_at: date-time` — audit trail
- `updated_at: date-time` — audit trail

**Use `additionalProperties: true` on object types.** This allows adding new fields without a breaking change, which is how the schema achieves forward compatibility.

**Prefer `enum` over `string` for status fields.** It generates a TypeScript union type and a Rust enum automatically.

### Step 3 — Generate code

```bash
pnpm contracts:sync
```

### Step 4 — Verify

```bash
pnpm contracts:check
```

This runs in CI on every PR. Running it locally first saves time.

---

## Updating an existing schema

**Adding an optional field** — Safe. Existing JSON will deserialize correctly (the new field just won't be present). Rust/TypeScript will have it as `Option<T>` / `T | undefined`.

**Adding a required field** — Breaking change. All existing JSON will fail validation. Only do this with a migration plan.

**Removing or renaming a field** — Breaking change. Don't do it. Instead, mark the field as deprecated in the schema and remove it in a future major version.

**Changing a type** — Depends. `string → string (format: uuid)` is safe. `string → integer` is breaking. `string + enum: [a, b] → string + enum: [a, b, c]` is safe (adding enum variants).

---

## When NOT to use a schema

Internal Rust-only types that never leave the Rust process don't need schemas:

- Error types (`MyServiceError`) — use `thiserror`
- Intermediate computation types used within a single function
- Configuration structs — those go in `crates/config/src/lib.rs`

The test for whether something needs a schema: **"Will the TypeScript frontend ever need to know about this type?"** If yes, schema. If no, Rust type directly.

---

## Schema validation in the pipeline

```
git commit
  └── pnpm lint-staged
        └── pnpm contracts:check     ← validates generated code matches schemas
```

If `contracts:check` fails, the commit is rejected. Run `pnpm contracts:sync` locally and commit the generated code alongside your schema change.
