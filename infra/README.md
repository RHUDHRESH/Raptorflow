# Infrastructure

## Two kinds of infrastructure, one directory

`infra/` contains two completely separate infrastructure systems. They're in the same directory only because both describe how RaptorFlow runs — they never share code or configuration.

|                            | `docker/`                             | `tofu/`                                 |
| -------------------------- | ------------------------------------- | --------------------------------------- |
| **What it is**             | Docker Compose for your local machine | OpenTofu (Terraform) for production AWS |
| **Who uses it**            | Every developer                       | CI/CD pipelines and infra engineers     |
| **Runs where**             | Your laptop                           | AWS (ECS Fargate, Aurora, S3, VPC)      |
| **Changes deployed how**   | `docker compose up --build`           | `tofu apply` (gated by CI)              |
| **Version controlled how** | Yes — part of the repo                | Yes — part of the repo                  |

---

## The mental model

Think of it this way:

```
Your laptop                              Production AWS
───────────────────                      ────────────────────────────────────
docker compose                           tofu apply
   │                                         │
   ├── postgres (pgvector)                   ├── Aurora PostgreSQL 16
   │      └── stores all domain data              └── stores all domain data
   ├── pgbouncer
   │      └── connection pooling
   ├── dragonfly                              ├── ElastiCache Redis
   │      └── cache, pub/sub                      └── cache, pub/sub
   └── qdrant                                 ├── Qdrant (ECS or managed)
          └── vector search                        └── vector search
                                          ├── ECS Fargate
                                          │      └── runs the Rust API
                                          ├── S3
                                          │      └── file uploads, backups
                                          └── CloudWatch
                                                 └── logs and metrics
```

The Docker stack is a **local replica of the production data layer** — same images, same versions, same configuration patterns. The Rust API and Next.js frontend run differently locally (`pnpm dev`) than in production (ECS containers), but they connect to the same data infrastructure.

---

## `infra/docker/` — local development

### What it starts

| Service     | Image                                                 | Ports          | Role                                                                        |
| ----------- | ----------------------------------------------------- | -------------- | --------------------------------------------------------------------------- |
| `postgres`  | `pgvector/pgvector:pg16`                              | `5432`         | Primary database. `vector` extension installed on first boot.               |
| `pgbouncer` | `edoburu/pgbouncer:1.24.1`                            | `6432`         | Connection pooler in transaction mode. All app connections go through here. |
| `dragonfly` | `docker.dragonflydb.io/dragonflydb/dragonfly:v1.31.0` | `6379`         | Redis-compatible: cache, pub/sub, distributed locks.                        |
| `qdrant`    | `qdrant/qdrant:v1.13.6`                               | `6333`, `6334` | Vector similarity search for the PRL memory system.                         |
| `web`       | `node:22-alpine`                                      | `3000`         | Next.js frontend (volume-mounted — hot reload works).                       |
| `api`       | `rust:1.94-bookworm`                                  | `8080`         | Rust Axum server (volume-mounted — recompiles on save).                     |

### How to use it

```bash
# Start databases only (run API and frontend via pnpm dev instead)
docker compose up postgres pgbouncer dragonfly qdrant

# Start everything (API and frontend run in containers — not recommended for active development)
docker compose up

# Rebuild after changing a Dockerfile
docker compose up --build api
```

**The recommended workflow:** `docker compose up postgres pgbouncer dragonfly qdrant` in terminal 1, then `pnpm dev` in terminal 2 for the frontend and `cargo run -p raptorflow-api` (or IDE-run) for the backend. This gives you hot reload on both sides.

### The database connection rule

> ⚠️ **Migrations: connect directly to PostgreSQL (port 5432).**
> ⚠️ **App runtime: connect through PgBouncer (port 6432).**

PgBouncer is in **transaction mode**. It doesn't support `CREATE EXTENSION`, `CREATE DATABASE`, or most DDL commands. If you run migrations through PgBouncer, those commands silently fail and corrupt your schema.

```bash
# For migrations — DIRECT to PostgreSQL
RAPTORFLOW_DIRECT_DATABASE_URL=postgres://raptorflow:raptorflow@localhost:5432/raptorflow sqlx migrate run

# For the app runtime — through PgBouncer
RAPTORFLOW_DATABASE_URL=postgres://raptorflow:raptorflow@localhost:6432/raptorflow
```

Both are set correctly in your `.env` file. Just don't override them manually.

### Init script

`postgres/init/001-init.sql` runs once on container first boot. It creates the `vector` extension (idempotent — safe to re-run). All other schema (tables, indexes, RLS policies) is applied by `sqlx migrate run` from the `db` crate.

---

## `infra/tofu/` — production AWS infrastructure

### Structure

```
infra/tofu/
    ├── modules/              ← Reusable components (ECS, RDS, S3, VPC)
    │   ├── compute/          ← ECS cluster, services, task definitions
    │   ├── data/            ← Aurora, ElastiCache, S3
    │   └── network/         ← VPC, subnets, security groups, ALB
    │
    └── environments/
        ├── dev/             ← Dev overlay (ap-south-1)
        ├── staging/         ← Staging overlay
        └── prod/            ← Production overlay
```

Each environment overlay (`environments/dev/main.tf`, etc.) instantiates the modules with environment-specific variables.

### How to use it

```bash
cd infra/tofu/environments/dev

# See what would change (safe — reads only)
tofu plan

# Apply changes (requires AWS credentials)
tofu apply
```

In CI, `tofu plan` runs on every PR to show the diff. `tofu apply` runs on merge to `main` for dev, and is manually triggered for staging/prod.

---

## Where to make changes

| Scenario                                                | Where to edit                                                 |
| ------------------------------------------------------- | ------------------------------------------------------------- |
| Add a database service locally                          | `docker-compose.yml` + `infra/docker/`                        |
| Change how the Rust API container is built              | `infra/docker/api/Dockerfile`                                 |
| Add an AWS resource (S3 bucket, ECS task, Aurora table) | `infra/tofu/modules/` or `environments/<env>/`                |
| Change an environment variable in production            | `infra/tofu/environments/<env>/main.tf` + AWS Secrets Manager |
| Change an environment variable locally                  | `.env.example` + `crates/config/src/lib.rs`                   |
| Add a database migration                                | `database/migrations/` (not here)                             |

---

## A note on environment variables and secrets

**Local:** `.env` file → `Settings` in `crates/config/src/lib.rs` → all crates read from there.

**Production:** AWS Secrets Manager → injected into ECS task definition as environment variables → same `Settings` struct.

The Rust code doesn't know the difference. `Settings::from_env()` reads from the environment in both cases. This means code that works locally works in production — same types, same defaults, same validation.

---

## Design goals

The Docker setup is not just "whatever works." It is intentionally shaped like production:

| Goal                            | What it means                                                                  |
| ------------------------------- | ------------------------------------------------------------------------------ |
| **Service name alignment**      | Container service names match production concerns (`postgres`, not `local-db`) |
| **Port alignment**              | Local ports mirror production (5432 direct, 6432 via PgBouncer)                |
| **Tenant-aware paths testable** | `org_id` filtering works the same way locally as in production                 |
| **Smoke testable**              | Container health checks validate the stack without requiring feature logic     |

And explicitly what it does NOT try to replicate:

| Non-goal                            | Why                                                                                     |
| ----------------------------------- | --------------------------------------------------------------------------------------- |
| Exact Aurora Serverless v2 behavior | Aurora Serverless has auto-scaling, Data API, and IAM auth that Docker Postgres doesn't |
| ECS control plane parity            | Docker Compose is for running, not for simulating ECS task definitions                  |
| Real GCP API or Razorpay execution  | Use `replace-me` values in `.env`; integration tests use test/sandbox accounts          |
