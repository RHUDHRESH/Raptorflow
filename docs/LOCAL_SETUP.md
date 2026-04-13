# Local Development Setup

This guide covers everything you need to run RaptorFlow on your own machine.

---

## Quick Start

### 1. Clone and install

```bash
git clone <repo-url>
cd Raptorflow
corepack enable
pnpm install --frozen-lockfile
```

### 2. Copy environment files

```bash
cp .env.example .env                    # Backend env (committed, shared defaults)
cp apps/web/.env.example apps/web/.env.local   # Frontend env (NOT committed — yours alone)
```

### 3. Start the infrastructure

```bash
docker compose up postgres pgbouncer dragonfly qdrant -d
```

### 4. Run the frontend

```bash
pnpm dev
```

Open **http://localhost:3000**. The API runs at **http://localhost:8080**.

---

## The Two `.env` Files

RaptorFlow has **two separate environments** — one for the frontend (Next.js) and one for the backend (Rust). They are configured independently.

### Frontend — `apps/web/.env.local`

This file is **never committed**. It is your local override file. Create it if it doesn't exist:

```bash
cp apps/web/.env.example apps/web/.env.local
```

**What it controls:**

| Variable                            | Default                 | What it does                                       |
| ----------------------------------- | ----------------------- | -------------------------------------------------- |
| `NEXT_PUBLIC_APP_URL`               | `http://localhost:3000` | Where the frontend thinks it lives                 |
| `NEXT_PUBLIC_API_BASE_URL`          | `http://localhost:8080` | Where the frontend calls the API                   |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | `pk_test_...`           | Clerk auth — get from Clerk dashboard              |
| `NEXT_PUBLIC_OFFLINE_MODE`          | `false`                 | Set to `true` to use mock data instead of real API |

**All `NEXT_PUBLIC_` variables are public.** They are embedded in the browser bundle. Never put secrets here.

### Backend — `.env` (root)

This file IS committed. It contains shared defaults. Override values locally using `.env.local` (which is gitignored) or by setting environment variables directly in your terminal.

```bash
# Override any value locally without editing .env
export DATABASE_URL=postgres://custom:pass@localhost:5432/mydb
cargo run --bin api
```

### Adding your own overrides (recommended pattern)

Create a `.env.local` in the **root** directory (it is gitignored):

```bash
# .env.local (root — never committed)
DATABASE_URL=postgres://raptorflow:custom@localhost:5432/raptorflow_dev
DRAGONFLY_URL=redis://localhost:6379
ALLOW_INSECURE_DEV_AUTH=true
```

This way `.env` stays clean and shared, but your machine uses its own values.

---

## Offline Mode — `NEXT_PUBLIC_OFFLINE_MODE=true`

When `NEXT_PUBLIC_OFFLINE_MODE=true`, the frontend:

- **API calls** → return mock data (no real backend needed)
- **AI inference** → calls your local GROQ container instead of GCP Gemini
- **Office WebSocket** → connects to a mock server that replays canned events

### When to use offline mode

- You want to work on UI without running the full Rust backend
- You don't have GCP credentials to run AI inference locally
- You're iterating on pages that don't need real data

### Setting up offline mode

**Step 1: Set the flag**

```bash
echo "NEXT_PUBLIC_OFFLINE_MODE=true" >> apps/web/.env.local
```

**Step 2: Start the offline infrastructure**

```bash
docker compose -f docker-compose.offline.yml up -d
```

This starts: Postgres 16, DragonflyDB, Qdrant, LocalStack (S3 + SQS), GROQ (GPU), and the mock WebSocket server.

**Step 3: Start the frontend**

```bash
pnpm dev
```

Open http://localhost:3000. You'll see mock campaigns, council sessions, and a live Office canvas replaying events from the mock WebSocket server.

**Step 4: Stop offline mode**

```bash
# Remove the flag
# Edit apps/web/.env.local and remove the NEXT_PUBLIC_OFFLINE_MODE line, or:
sed -i '/NEXT_PUBLIC_OFFLINE_MODE/d' apps/web/.env.local

# Or restart the frontend without the flag
pnpm dev
```

---

## Full Stack (Online) Mode

When you want to run the real backend with real AI:

### Prerequisites

1. **GCP credentials** — Download your service account JSON from Google Cloud Console. Set:

   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
   export GCP_PROJECT_ID=your-project-id
   ```

2. **AWS credentials** — For SQS and S3:

   ```bash
   export AWS_ACCESS_KEY_ID=your-key
   export AWS_SECRET_ACCESS_KEY=your-secret
   export AWS_REGION=ap-south-1
   ```

3. **Clerk** — Create a Clerk application. Get your publishable key and API URL. Set:

   ```bash
   # apps/web/.env.local
   NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_...
   ```

   ```bash
   # .env or .env.local
   CLERK_ISSUER=https://your-org.clerk.accounts.dev
   CLERK_JWKS_URL=https://your-org.clerk.accounts.dev/.well-known/jwks.json
   CLERK_SECRET_KEY=sk_test_...
   CLERK_WEBHOOK_SECRET=whsec_...
   ```

### Running the full stack

```bash
# Terminal 1 — Infrastructure
docker compose up postgres pgbouncer dragonfly qdrant -d

# Terminal 2 — Backend
cargo run --bin api

# Terminal 3 — Frontend
pnpm dev
```

### Run migrations

```bash
# Direct to Postgres (NOT through PgBouncer — it breaks DDL)
RAPTORFLOW_DIRECT_DATABASE_URL=postgres://raptorflow:raptorflow@localhost:5432/raptorflow_dev \
  cargo run --bin api -- migrate
```

---

## Swapping AI Providers

The AI adapter is in `apps/web/src/lib/ai.ts`. By default:

- **Online** → calls GCP Gemini
- **Offline (`NEXT_PUBLIC_OFFLINE_MODE=true`)** → calls local GROQ at `http://localhost:8081`

### To use a different local model

Edit `apps/web/src/lib/ai.ts`:

```typescript
// Change this line to use any OpenAI-compatible endpoint:
const GROQ_BASE_URL = "http://localhost:8081/v1";
// OR for Ollama:
const GROQ_BASE_URL = "http://localhost:11434/v1/api";

// Change the model:
const DEFAULT_MODEL = "mixtral-8x7b-32768"; // GROQ
// OR for Ollama:
const DEFAULT_MODEL = "llama3"; // Ollama
```

### For Ollama (CPU-only, no GPU needed)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull llama3

# Start the server (Ollama runs on port 11434 by default)
ollama serve
```

Then update `apps/web/src/lib/ai.ts`:

```typescript
const GROQ_BASE_URL = "http://localhost:11434/v1/api";
const DEFAULT_MODEL = "llama3";
```

### For OpenAI-compatible APIs (Groq, Together, Perplexity, etc.)

```bash
# Set your API key
export OPENAI_API_KEY=sk-...

# Update the base URL
# groq: https://groq.com (has free tier)
# together: https://together.ai
# perplexity: https://api.perplexity.ai
```

---

## Multiple Developers — How It Works

**`.env.local` files are gitignored.** This means every developer can configure their own environment without affecting anyone else.

```
# .gitignore already includes:
apps/web/.env.local
.env.local
.env.offline
```

### Each developer can have a completely different setup:

| Developer | Setup                                                           |
| --------- | --------------------------------------------------------------- |
| **Alice** | Full stack with GCP + AWS, offline mode OFF                     |
| **Bob**   | Frontend-only, `NEXT_PUBLIC_OFFLINE_MODE=true`, mock everything |
| **Carol** | Full stack but uses Ollama on CPU instead of GROQ on GPU        |
| **Dan**   | Frontend-only, uses real backend at `api.staging.raptorflow.io` |

### Sharing environment requirements

When you add a new environment variable, document it in the relevant `.env.example` file. Other developers will see it when they run `cp .env.example .env`.

### Recommended `.env.local` for a frontend-only dev

```bash
# apps/web/.env.local
NEXT_PUBLIC_OFFLINE_MODE=true
NEXT_PUBLIC_API_BASE_URL=https://api.staging.raptorflow.io
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_clerk_key
```

That's it. No backend, no Docker infra, just the frontend and the staging API.

### Recommended `.env.local` for a full-stack dev

```bash
# .env.local (root — your machine only)
DATABASE_URL=postgres://raptorflow:raptorflow@localhost:5432/raptorflow_dev
DRAGONFLY_URL=redis://localhost:6379
QDRANT_URL=http://localhost:6333
GOOGLE_APPLICATION_CREDENTIALS=/Users/you/.gcp/raptorflow-dev.json
ALLOW_INSECURE_DEV_AUTH=true
CLERK_SECRET_KEY=sk_test_...
RAZORPAY_KEY_SECRET=...
RESEND_API_KEY=re_...
SENTRY_DSN=https://...@sentry.io/...
```

---

## Deployment Environments

### Frontend — Vercel

The Next.js app deploys to **Vercel** in the `sin1` region (Singapore, closest to the Mumbai AWS region).

**Environment variables set in Vercel dashboard:**

| Variable                            | Value                       |
| ----------------------------------- | --------------------------- |
| `NEXT_PUBLIC_APP_URL`               | `https://app.raptorflow.io` |
| `NEXT_PUBLIC_API_BASE_URL`          | `https://api.raptorflow.io` |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | From Clerk dashboard        |
| `NEXT_PUBLIC_OFFLINE_MODE`          | `false`                     |

The `vercel.json` in `apps/web/` configures security headers and the `sin1` region.

**To deploy:**

```bash
# Preview
vercel

# Production
vercel --prod
```

Or connect the repo to Vercel and it deploys automatically on push to `main`.

### Backend — AWS ECS Fargate

The Rust binary deploys to **AWS ECS Fargate** in `ap-south-1` (Mumbai).

**Environment variables set in ECS task definition (via AWS Secrets Manager):**

| Variable                  | Source                      |
| ------------------------- | --------------------------- |
| `APP_ENV`                 | `prod`                      |
| `DATABASE_URL`            | Secrets Manager             |
| `DRAGONFLY_URL`           | Secrets Manager             |
| `QDRANT_URL`              | Secrets Manager             |
| `SQS_BASE_URL`            | Secrets Manager             |
| `CLERK_SECRET_KEY`        | Secrets Manager             |
| `CLERK_ISSUER`            | Secrets Manager             |
| `RAZORPAY_KEY_SECRET`     | Secrets Manager             |
| `RESEND_API_KEY`          | Secrets Manager             |
| `SENTRY_DSN`              | Secrets Manager             |
| `RAPTORFLOW_FRONTEND_URL` | `https://app.raptorflow.io` |

**To deploy a new backend version:**

```bash
# Build and push new Docker image
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin $ECR_URL
docker build -f infra/docker/api/Dockerfile -t $ECR_URL:$COMMIT_SHA .
docker push $ECR_URL:$COMMIT_SHA

# Update the ECS service (zero-downtime deploy)
aws ecs update-service \
  --cluster raptorflow \
  --service raptorflow-api \
  --task-definition raptorflow-api:$COMMIT_SHA \
  --force-new-deployment

# Wait for stability
aws ecs wait services-stable \
  --cluster raptorflow \
  --services raptorflow-api
```

### Domains

```
https://app.raptorflow.io      → Vercel (Next.js frontend)
https://api.raptorflow.io       → AWS ALB → ECS Fargate (Rust API)
https://assets.raptorflow.io    → CloudFront → S3 (uploaded files)
```

---

## Troubleshooting

### Frontend won't start

```bash
# Clear Next.js cache
rm -rf apps/web/.next

# Reinstall dependencies
pnpm install --frozen-lockfile
```

### API returns 401

Clerk JWT has expired or is invalid. Make sure:

- `CLERK_SECRET_KEY` is set in your `.env`
- Clerk domain matches `CLERK_ISSUER`
- For local dev, `ALLOW_INSECURE_DEV_AUTH=true` is set

### Pixi.js canvas shows "Loading PixiJS..."

The canvas is SSR-safe — it only initializes on the client. If it shows nothing:

1. Check browser console for errors
2. Make sure `office-canvas.tsx` isn't throwing during dynamic import of `pixi.js`
3. The `data-pixi-status` div should disappear once PixiJS initializes

### Docker services won't start

```bash
# Check what ports are in use
lsof -i :5432   # Postgres
lsof -i :6379   # Dragonfly
lsof -i :6333   # Qdrant

# Or check Docker logs
docker compose logs postgres
docker compose logs dragonfly
```

### Offline mode still hitting the real API

Make sure `NEXT_PUBLIC_OFFLINE_MODE=true` is in `apps/web/.env.local` (not just `.env`). The `NEXT_PUBLIC_` prefix is required.

```bash
# Verify what's set
grep OFFLINE apps/web/.env.local
```

### GROQ API errors in offline mode

If you see `GROQ API error 401`:

```bash
# Get a free API key from https://console.groq.com
export GROQ_API_KEY=sk-...

# Or use Ollama instead (no API key needed)
# See "For Ollama" section above
```

---

## File Summary

| File                         | Purpose                   | Committed? |
| ---------------------------- | ------------------------- | ---------- |
| `.env`                       | Backend shared defaults   | ✅         |
| `.env.example`               | Backend template          | ✅         |
| `.env.local`                 | Backend local overrides   | ❌         |
| `apps/web/.env.local`        | Frontend local config     | ❌         |
| `apps/web/.env.example`      | Frontend template         | ✅         |
| `apps/web/.env.offline`      | Frontend offline defaults | ✅         |
| `docker-compose.yml`         | Full stack infra          | ✅         |
| `docker-compose.offline.yml` | Offline infra             | ✅         |
| `crates/.env.offline`        | Backend offline defaults  | ✅         |
| `scripts/dev-offline.sh`     | Start offline environment | ✅         |
| `scripts/deploy-frontend.sh` | Deploy to Vercel          | ✅         |
