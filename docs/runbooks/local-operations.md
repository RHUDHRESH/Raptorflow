# Local Operations Runbook

How to run, debug, and fix the RaptorFlow stack on your machine.

---

## Starting the stack

### Databases only (recommended for most development)

```bash
docker compose up postgres pgbouncer qdrant
```

### Full stack (includes API and web containers — useful for CI-like environments)

```bash
docker compose up
```

### Rebuild after changing a Dockerfile

```bash
docker compose up --build api
docker compose up --build web
```

---

## Verifying health

```bash
# Check all containers are running
docker compose ps

# Check API is responding
curl http://localhost:8080/health

# Check PostgreSQL is up
docker compose exec postgres pg_isready -U raptorflow

# Check Qdrant is up
curl http://localhost:6333/collections
```

---

## Running migrations

Migrations run automatically on API startup via `sqlx migrate run`. To run them manually:

```bash
# Requires DIRECT database URL (port 5432, not PgBouncer port 6432)
export RAPTORFLOW_DIRECT_DATABASE_URL="postgres://raptorflow:raptorflow@localhost:5432/raptorflow"
sqlx migrate run
```

> ⚠️ **Never run migrations through PgBouncer.** PgBouncer is in transaction mode — it silently drops `CREATE EXTENSION` and DDL. Always connect directly to PostgreSQL on port 5432.

To roll back the last migration:

```bash
sqlx migrate revert
```

---

## Viewing logs

```bash
# All services
docker compose logs

# Specific service
docker compose logs api
docker compose logs postgres

# Follow in real time
docker compose logs -f api
```

---

## Connecting to services directly

```bash
# PostgreSQL (for migrations and direct debugging)
psql "postgres://raptorflow:raptorflow@localhost:5432/raptorflow"

# Qdrant (vector search)
# Open http://localhost:6333/dashboard in your browser
```

---

## Common failures

### API won't start — "database not found"

The database container started but the app connected before it was ready. Wait 5 seconds and retry `pnpm dev`.

### Migration fails — "relation does not exist"

You're connected through PgBouncer instead of directly to PostgreSQL. Use `RAPTORFLOW_DIRECT_DATABASE_URL` with port `5432`.

### `docker compose up` fails — "port already in use"

Something else is using the port. Find and stop it:

```bash
# Find what's using port 5432
netstat -ano | findstr :5432
```

Common culprits: another PostgreSQL install, Docker Desktop's built-in postgres.

### Frontend shows "Failed to fetch" errors

The Rust API isn't running. Start it with `cargo run -p raptorflow-api` in a separate terminal, or run `pnpm dev` (which starts both).

### Rust compilation is slow on first run

The `cargo-target/` volume isn't mounted in Docker. Either use `docker compose up --build api` once to warm the cache, or run Rust natively:

```bash
cargo run -p raptorflow-api
```

---

## Resetting the local database

Wipe all data and re-run migrations from scratch:

```bash
# Stop the stack
docker compose down

# Remove the data volume
docker compose volume rm raptorflow_postgres-data

# Restart — the init script will run again
docker compose up postgres

# Wait for init to complete (~10 seconds), then start everything
docker compose up
```

This also resets Qdrant data (`raptorflow_qdrant-data` volume).

---

## Environment variables quick reference

| Variable                         | Local default                                     | What it does                                   |
| -------------------------------- | ------------------------------------------------- | ---------------------------------------------- |
| `RAPTORFLOW_DATABASE_URL`        | `postgres://raptorflow@localhost:6432/raptorflow` | App DB connection (through PgBouncer)          |
| `RAPTORFLOW_DIRECT_DATABASE_URL` | `postgres://raptorflow@localhost:5432/raptorflow` | Migration connection (direct)                  |
| `RAPTORFLOW_QDRANT_URL`          | `http://localhost:6333`                           | Vector search                                  |
| `APP_ENV`                        | `dev`                                             | Controls logging level, stub vs real behaviour |
