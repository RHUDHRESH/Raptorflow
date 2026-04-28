# Runtime Reality Smoke Tests

Runtime reality smoke tests verify that the application can connect to and interact with core infrastructure dependencies (Postgres/pgvector, Qdrant, AWS Bedrock) and that the API health endpoints respond correctly.

## Purpose

Before populating avatars and agents, we must prove:

1. The app can connect to Postgres with pgvector extension
2. Migrations apply cleanly
3. The app can connect to Qdrant vector store
4. The API health endpoints are functional
5. AWS Bedrock inference works (optional, manual trigger)

## Smoke Tests

### 1. DB Smoke (`crates/db/tests/runtime_reality_smoke.rs`)

Tests:

- Database connection via `TEST_DATABASE_URL`
- pgvector extension presence
- Required tables exist
- RLS policy presence

**Env vars:**

- `TEST_DATABASE_URL` (required) - Separate test database, never production URLs

### 2. Qdrant Smoke (`scripts/smoke/qdrant-smoke.mjs`)

Tests:

- Qdrant health endpoint
- Collection creation (random name)
- Document upsert
- Search
- Collection deletion

**Env vars:**

- `QDRANT_URL` (default: `http://localhost:6333`)

**Safety:** Collections use random UUID names and are deleted after test.

### 3. API Health Smoke (`scripts/smoke/api-health-smoke.mjs`)

Tests:

- `GET /health/live` - Liveness probe
- `GET /health/ready` - Readiness probe
- `GET /api/v1/health` - API health with status

**Env vars:**

- `API_BASE_URL` (default: `http://localhost:3000`)

### 4. Bedrock Smoke (`crates/aws/tests/bedrock_smoke.rs`)

Tests:

- AWS credentials validity
- Bedrock converse API invocation
- JSON response validation

**Env vars:**

- `AWS_ACCESS_KEY_ID` (required for Bedrock smoke)
- `AWS_SECRET_ACCESS_KEY` (required for Bedrock smoke)
- `AWS_REGION` (default: `us-east-1`)
- `BEDROCK_SMOKE_TEST=1` (required to enable)

**Note:** Bedrock smoke is NOT run by default. It requires explicit manual trigger via GitHub Actions `workflow_dispatch` with `run_bedrock: true`.

## Running Locally

### Prerequisites

1. Start required services:

```bash
docker compose up -d postgres qdrant
```

2. Set environment variables:

```bash
export TEST_DATABASE_URL="postgres://testuser:testpass@localhost:5432/raptorflow_test"
export QDRANT_URL="http://localhost:6333"
export API_BASE_URL="http://localhost:3000"
```

### Run All Smoke Tests

```bash
# Create test database
docker compose exec postgres psql -U testuser -d postgres -c "DROP DATABASE IF EXISTS raptorflow_test;"
docker compose exec postgres psql -U testuser -d postgres -c "CREATE DATABASE raptorflow_test;"

# DB smoke
cargo test -p raptorflow-db --test runtime_reality_smoke -- --nocapture

# Qdrant smoke
node scripts/smoke/qdrant-smoke.mjs

# API health smoke
node scripts/smoke/api-health-smoke.mjs

# Bedrock smoke (optional, requires AWS credentials)
export BEDROCK_SMOKE_TEST=1
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
export AWS_REGION="us-east-1"
cargo test -p raptorflow-aws --test bedrock_smoke -- --nocapture
```

### Orchestrator Script

A PowerShell orchestrator is available for local testing:

```powershell
./scripts/smoke/local-runtime-smoke.ps1 -WithApi -ResetVolumes
```

See `Get-Help ./scripts/smoke/local-runtime-smoke.ps1` for options.

## CI/CD

### GitHub Actions

The `runtime-reality.yml` workflow runs:

1. **DB & Qdrant Smoke** (automatic on PR to main):

   - Spins up Postgres (pgvector:pg16) and Qdrant (v1.17.1) services
   - Runs DB smoke test with `TEST_DATABASE_URL`
   - Runs Qdrant smoke script

2. **API Health Smoke** (automatic, depends on DB/Qdrant):

   - Runs API health smoke script

3. **Bedrock Smoke** (manual trigger only):
   - Requires `workflow_dispatch` with `run_bedrock: true`
   - Requires AWS secrets in GitHub repository

## Safety Rules

- **NEVER use production/staging database URLs** in smoke tests
- **ALWAYS use `TEST_DATABASE_URL`** for DB tests
- **ALWAYS use random collection names** in Qdrant tests
- **NEVER commit secrets** to the repository
- **NEVER run Bedrock smoke by default** - only via manual trigger
- If `TEST_DATABASE_URL` is present but connection fails = **FAIL** (do not skip)
- If `TEST_DATABASE_URL` is absent = **SKIP** DB tests gracefully

## Exit Codes

| Exit Code | Meaning                        |
| --------- | ------------------------------ |
| 0         | All smoke tests passed         |
| 1         | One or more smoke tests failed |

## Next Steps

After runtime reality smoke tests pass:

1. Proceed to avatar population
2. Add agent personalities
3. Enable external actions
