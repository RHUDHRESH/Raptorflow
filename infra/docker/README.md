# Local Docker Setup

**What this is:** A Docker Compose stack that replicates the production data layer on your machine. PostgreSQL, PgBouncer, DragonflyDB, and Qdrant — same images as production, same configuration patterns.

**What this is NOT:** A deployment target. The `api` and `web` containers are for local development convenience only. Production runs on AWS ECS Fargate.

---

## Services

| Service     | Image                                                 | Ports          | What it does                                                                                                     |
| ----------- | ----------------------------------------------------- | -------------- | ---------------------------------------------------------------------------------------------------------------- |
| `postgres`  | `pgvector/pgvector:pg16`                              | `5432`         | Primary database. pgvector extension installed on first boot via `001-init.sql`.                                 |
| `pgbouncer` | `edoburu/pgbouncer:1.24.1`                            | `6432`         | Connection pooler in transaction mode. Rails all app connections through a small pool of PostgreSQL connections. |
| `dragonfly` | `docker.dragonflydb.io/dragonflydb/dragonfly:v1.31.0` | `6379`         | Redis-compatible cache, pub/sub, and distributed locks.                                                          |
| `qdrant`    | `qdrant/qdrant:v1.13.6`                               | `6333`, `6334` | Vector similarity search. Stores embedding vectors for the PRL memory system.                                    |
| `web`       | `node:22-alpine`                                      | `3000`         | Next.js frontend. Mounts `apps/web/` as a volume — code changes hot-reload without rebuilding.                   |
| `api`       | `rust:1.94-bookworm`                                  | `8080`         | Rust Axum server. Mounts the workspace as a volume and runs `cargo watch` — code changes recompile on save.      |

---

## Quick start

```bash
# Start databases only (most common — API runs locally via pnpm dev)
docker compose up postgres pgbouncer dragonfly qdrant

# Start everything including API and web containers
docker compose up

# Rebuild after changing a Dockerfile
docker compose up --build api
```

The `web` and `api` services mount the project root, so you don't need to rebuild containers during active development. `pnpm dev` runs the frontend locally (hot reload), and `cargo run -p raptorflow-api` runs the backend locally (with `cargo watch`).

---

## Database connection map

| Who needs to connect        | Connects to                             | Why                                                                                                          |
| --------------------------- | --------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| Your Rust app (`pnpm dev`)  | PgBouncer on `localhost:6432`           | Connection pooling — handles many concurrent requests with a small PostgreSQL connection pool                |
| `sqlx migrate run` (manual) | PostgreSQL directly on `localhost:5432` | Migrations cannot run through PgBouncer — it doesn't support `CREATE EXTENSION` and other superuser commands |
| Next.js (Prisma)            | PgBouncer on `localhost:6432`           | Same pooling rationale as above                                                                              |

> ⚠️ **Critical: Always run migrations against PostgreSQL directly (port 5432), not PgBouncer (port 6432).** PgBouncer is in transaction mode. It silently swallows `CREATE EXTENSION` and DDL statements, corrupting your schema.

Set `RAPTORFLOW_DIRECT_DATABASE_URL` for migrations and `RAPTORFLOW_DATABASE_URL` for the app. Both are in `.env`.

---

## Init script

`postgres/init/001-init.sql` runs once when the container first starts (it checks for the `vector` extension before creating it — idempotent). It creates:

- The `vector` extension (for pgvector similarity search)

All schema (tables, indexes, RLS policies) is applied by `sqlx migrate run` from the Rust `db` crate on application startup.

---

## Environment variables

All `RAPTORFLOW_*` variables are documented in [`crates/config/src/lib.rs`](../../crates/config/src/lib.rs).

The `docker-compose.yml` sets infrastructure service URLs. Your `.env` file (gitignored) overrides them for local development:

```bash
RAPTORFLOW_DATABASE_URL=postgres://raptorflow:raptorflow@localhost:6432/raptorflow
RAPTORFLOW_DIRECT_DATABASE_URL=postgres://raptorflow:raptorflow@localhost:5432/raptorflow
RAPTORFLOW_REDIS_URL=redis://localhost:6379
RAPTORFLOW_QDRANT_URL=http://localhost:6333
```

---

## PgBouncer configuration

Key settings in `pgbouncer.ini`:

| Setting               | Value         | What it means                                                                                         |
| --------------------- | ------------- | ----------------------------------------------------------------------------------------------------- |
| `pool_mode`           | `transaction` | Connections returned to pool after each transaction. Required for RLS to work correctly with pooling. |
| `max_client_conn`     | `250`         | Max concurrent client connections                                                                     |
| `default_pool_size`   | `30`          | PostgreSQL connections per user/database pair                                                         |
| `server_idle_timeout` | `600`         | Seconds before an idle server connection is closed                                                    |

Auth is plain text in development only (`userlist.txt`). Production uses proper secrets.

---

## Volumes

| Volume             | Mount                      | Purpose                                                                                                      |
| ------------------ | -------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `postgres-data`    | `/var/lib/postgresql/data` | PostgreSQL data directory — survives container restarts                                                      |
| `qdrant-data`      | `/qdrant/storage`          | Qdrant vector storage — survives restarts                                                                    |
| `cargo-target`     | `/workspace/target`        | Rust build cache in the API container — avoids rebuilding Rust deps on every `docker compose up --build api` |
| `web-node-modules` | `/workspace/node_modules`  | Node dependencies in the web container — survives rebuilds                                                   |
| `pnpm-store`       | `/pnpm/store`              | pnpm content-addressable store — shared across web container rebuilds                                        |

---

## Adding a new local service

If you need a local-only service (e.g. a mock SMTP server for testing emails):

1. Add the service to `docker-compose.yml` following the same pattern as existing services
2. Add the image or `build:` block with the correct port mappings
3. Add environment variables to `docker-compose.yml` with sensible local defaults
4. Document the service in the table at the top of this file

Do NOT add development-only services to the production `infra/tofu/` infrastructure.
