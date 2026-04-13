# Local Mode

**Local mode** means running the RaptorFlow frontend without any backend, cloud services, or external credentials. The frontend uses mock data, a mock WebSocket server for the Office canvas, and a local AI provider instead of GCP Gemini.

It is designed for:

- Frontend-only developers who don't need to work on the Rust backend
- Iterating on UI when the backend is unavailable or you're rate-limited on GCP
- Demos that don't require real data
- Testing pages in isolation

One environment variable activates it: `NEXT_PUBLIC_OFFLINE_MODE=true`.

---

## Activate Local Mode

### Step 1: Add the flag

```bash
echo "NEXT_PUBLIC_OFFLINE_MODE=true" >> apps/web/.env.local
```

Your `apps/web/.env.local` should now contain:

```bash
NEXT_PUBLIC_OFFLINE_MODE=true
```

That's the only change required. The rest of your existing config stays intact — you can still point `NEXT_PUBLIC_API_BASE_URL` at a staging API if you want partial real data.

### Step 2: Start the frontend

```bash
pnpm dev
```

Open **http://localhost:3000**. Everything is live and interactive — pages render, navigation works, the Office canvas shows animated events, forms accept input. The difference is the data is mock data, not your real backend.

### Step 3 (optional): Start the mock WebSocket server

The Office canvas at `/office` connects to a mock server that replays a sequence of 12 office events on a timer. Start it with:

```bash
npx tsx scripts/mock-office-server.ts
```

Or include it in the offline Docker stack (see below).

---

## What Works in Local Mode

| Feature                    | Status | Notes                                            |
| -------------------------- | ------ | ------------------------------------------------ |
| All pages render           | ✅     | Dashboard, Campaigns, Council, Muse, Intel, etc. |
| Navigation                 | ✅     | Sidebar and all links work                       |
| Forms                      | ✅     | Accept input, validate, submit (no-op)           |
| Office canvas              | ✅     | Shows animated agents and zones                  |
| Office WebSocket           | ✅     | Mock server replays events                       |
| Dashboard tiles            | ✅     | Show mock campaigns, sessions, foundation        |
| Task board (drag-and-drop) | ✅     | Fully functional Kanban board                    |
| Performance charts         | ✅     | SVG charts with realistic data                   |
| Replanning page            | ✅     | Accept/reject decisions                          |
| Uploads page               | ✅     | Simulated upload with progress bars              |
| Clerk auth                 | ⚠️     | Redirects work but real JWTs not issued          |

---

## What Does NOT Work in Local Mode

| Feature                  | Status | Notes                                                           |
| ------------------------ | ------ | --------------------------------------------------------------- |
| Real AI inference        | ❌     | Calls go to GROQ/Ollama instead of GCP Gemini                   |
| Real database writes     | ❌     | Mock data only — nothing persists                               |
| Real file uploads        | ❌     | S3 presigned URLs don't work                                    |
| Real email (Resend)      | ❌     | Emails not sent                                                 |
| Real payments (Razorpay) | ❌     | Webhook verification uses mock                                  |
| Clerk JWT validation     | ❌     | The dev bypass (`ALLOW_INSECURE_DEV_AUTH=true`) is backend-only |
| Real WebSocket           | ❌     | Office uses the mock server at `ws://localhost:3001`            |

---

## The Mock Stack — What Runs Where

```
Your machine (localhost)

Browser → Next.js (localhost:3000)
           ↓ NEXT_PUBLIC_OFFLINE_MODE=true
           ↓ NEXT_PUBLIC_API_BASE_URL (ignored for mock data)
           API client returns mock data from apps/web/src/mocks/data.ts

Browser → Mock Office WS (localhost:3001)         ← scripts/mock-office-server.ts
           Replays 12 events on a 3.5s timer

(Optional) → GROQ or Ollama (localhost:8081 or :11434)  ← for AI calls
```

When `NEXT_PUBLIC_OFFLINE_MODE=true`, the API client (`apps/web/src/lib/api.ts`) checks the flag before every request. If it's true and the method is GET, it returns mock data from `apps/web/src/mocks/data.ts`. If it's POST/PUT/DELETE, it simulates success and returns `{ success: true }`.

---

## Swapping the Local AI Provider

By default, local AI calls go to GROQ at `http://localhost:8081`. You can change the provider by editing one file.

### GROQ (GPU recommended, free tier available)

Sign up at [console.groq.com](https://console.groq.com) and get a free API key.

```bash
# Start GROQ
docker run --gpus all -p 8081:8000 \
  ghcr.io/groq/groq-api:latest

# Set your key
export GROQ_API_KEY=sk-...
```

Then in `apps/web/src/lib/ai.ts`:

```typescript
const GROQ_BASE_URL = "http://localhost:8081/v1";
const DEFAULT_MODEL = "mixtral-8x7b-32768";
```

### Ollama (CPU, no API key needed)

Install from [ollama.com](https://ollama.com). No GPU required.

```bash
# Install and start
ollama pull llama3
ollama serve

# Verify it's running
curl http://localhost:11434/v1/models
```

Then in `apps/web/src/lib/ai.ts`:

```typescript
const GROQ_BASE_URL = "http://localhost:11434/v1/api";
const DEFAULT_MODEL = "llama3";
```

### Any OpenAI-compatible API

```typescript
// Together AI, Perplexity, etc.
const GROQ_BASE_URL = "https://api.groq.com/openai/v1";
const DEFAULT_MODEL = "mixtral-8x7b-32768"; // or their model
```

---

## Full Offline Docker Stack

Instead of starting services individually, use the offline compose file:

```bash
docker compose -f docker-compose.offline.yml up -d
```

This starts:

| Service      | Port      | What it is                        |
| ------------ | --------- | --------------------------------- |
| `postgres`   | 5432      | PostgreSQL 16                     |
| `dragonfly`  | 6379      | Redis-compatible cache            |
| `qdrant`     | 6333/6334 | Vector database                   |
| `localstack` | 4566      | SQS + S3 emulators                |
| `groq`       | 8081      | Local AI inference (GPU required) |

Then:

```bash
pnpm dev
```

---

## Script: `scripts/dev-offline.sh`

The fastest way to start everything:

```bash
./scripts/dev-offline.sh
```

This:

1. Copies `apps/web/.env.offline` → `apps/web/.env.local`
2. Copies `crates/.env.offline` → `.env`
3. Starts `docker-compose.offline.yml`
4. Starts the mock office WebSocket server in the background
5. Runs `pnpm dev`

Press `Ctrl+C` to stop everything cleanly.

---

## Mixing Real and Mock

You don't have to go all-in on local mode. You can mix:

### Frontend-only with real API

```bash
# .env.local
NEXT_PUBLIC_OFFLINE_MODE=false
NEXT_PUBLIC_API_BASE_URL=https://api.staging.raptorflow.io
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_your_real_key
```

The frontend calls the real staging API but you skip running the backend locally. Clerk auth works. Data is real. No Rust binary needed.

### Local backend with cloud AI

```bash
# .env (root)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/gcp-creds.json
GCP_PROJECT_ID=your-project
# Don't set ALLOW_INSECURE_DEV_AUTH=false
```

Run `cargo run --bin api` locally. The backend connects to GCP Gemini for real AI. Database is your local Postgres.

### Local backend with local AI

```bash
# .env
AI_PROVIDER=groq
GROQ_API_URL=http://localhost:8081/v1
GROQ_API_KEY=sk-...
```

Run the Rust backend locally, but AI inference goes to your local GROQ container instead of GCP.

---

## Environment Variable Reference

| Variable                   | File                  | Online default          | Offline value              |
| -------------------------- | --------------------- | ----------------------- | -------------------------- |
| `NEXT_PUBLIC_OFFLINE_MODE` | `apps/web/.env.local` | `false`                 | `true`                     |
| `NEXT_PUBLIC_API_BASE_URL` | `apps/web/.env.local` | `http://localhost:8080` | any or unchanged           |
| `GROQ_API_KEY`             | `.env.local` (root)   | —                       | your GROQ key              |
| `GROQ_API_URL`             | `crates/.env.offline` | —                       | `http://localhost:8081/v1` |
| `AI_PROVIDER`              | `crates/.env.offline` | `gemini`                | `groq`                     |

---

## Switching Back to Online

Remove the offline flag:

```bash
# Edit apps/web/.env.local and remove this line:
NEXT_PUBLIC_OFFLINE_MODE=true

# Or on macOS/Linux:
sed -i '/NEXT_PUBLIC_OFFLINE_MODE/d' apps/web/.env.local

# Or on Windows (PowerShell):
(Get-Content apps/web/.env.local) | Where-Object { $_ -notmatch 'OFFLINE' } | Set-Content apps/web/.env.local

# Restart the frontend
pnpm dev
```

The API client immediately starts calling `NEXT_PUBLIC_API_BASE_URL` again.

---

## CI/CD and Production — Local Mode Is Never Deployed

`NEXT_PUBLIC_OFFLINE_MODE` is read at **build time** by Next.js. The Vercel build always has `NEXT_PUBLIC_OFFLINE_MODE=false` set in the Vercel dashboard environment variables. Even if someone accidentally sets it in `.env.local`, it is overridden by the Vercel dashboard.

```bash
# Vercel dashboard — environment variables for production
NEXT_PUBLIC_OFFLINE_MODE = false   # ← enforced, always
```
