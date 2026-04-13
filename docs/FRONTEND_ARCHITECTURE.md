# RaptorFlow Frontend Architecture & Deployment Strategy

## What Exists vs. What Needs to Be Built

The frontend is a **Next.js 15 + React 19 + TypeScript + TailwindCSS 4** monorepo app with Pixi.js for the Office canvas. Most pages are scaffolded but lack real data connectivity. This document covers what to build, how to deploy it, and how to work offline.

---

## Part 1: The Frontend We Have (Inventory)

### Tech Stack

- **Framework**: Next.js 15.5.7 (App Router, Turbopack)
- **Language**: TypeScript 6
- **Styling**: TailwindCSS 4 + custom CSS variables
- **Auth**: Clerk (`@clerk/nextjs` 6.0.0)
- **Server state**: TanStack Query 5
- **Client state**: Zustand 5
- **Canvas**: Pixi.js 8 + pixi-viewport 6
- **Animations**: Framer Motion 12
- **Icons**: Lucide React

### Directory Structure

```
apps/web/src/
├── app/                          # Next.js App Router
│   ├── (app)/                   # Authenticated routes (has AppShell sidebar)
│   │   ├── app/page.tsx          # Dashboard — 6 placeholder tiles
│   │   ├── foundation/page.tsx    # 21-step onboarding flow
│   │   ├── campaigns/            # Campaign management
│   │   │   ├── page.tsx          # Campaign list (placeholder)
│   │   │   └── [campaignId]/
│   │   │       ├── moves/page.tsx    # Move sequence (placeholder)
│   │   │       ├── tasks/page.tsx     # Task board (MISSING)
│   │   │       ├── performance/page.tsx  # Analytics (MISSING)
│   │   │       └── replanning/page.tsx   # Replanning (MISSING)
│   │   ├── intel/page.tsx         # Intelligence alerts + feeds
│   │   ├── nudges/page.tsx        # In-app alert system
│   │   ├── uploads/               # Asset management (MISSING)
│   │   │   └── assets/[assetId]/
│   │   ├── office/page.tsx        # Pixi.js canvas shell
│   │   ├── muse/page.tsx           # Spatially-aware chat (placeholder)
│   │   ├── council/page.tsx        # Avatar deliberation (placeholder)
│   │   ├── daily-wins/page.tsx     # Briefing feed (placeholder)
│   │   ├── billing/page.tsx         # Razorpay integration (placeholder)
│   │   ├── settings/page.tsx        # Org settings (placeholder)
│   │   └── internal/debug/page.tsx  # Debug tools
│   ├── (auth)/                   # Clerk auth routes (sign-in, sign-up)
│   │   └── sign-in/[[...sign-in]]/
│   │   └── sign-up/[[...sign-up]]/
│   ├── (marketing)/              # Public landing page
│   │   └── page.tsx              # Full landing with CTA
│   ├── api/                     # Next.js API routes (edge)
│   │   ├── health/route.ts
│   │   └── internal/diagnostics/route.ts
│   ├── layout.tsx               # Root layout (ClerkProvider)
│   └── globals.css              # Design tokens + gradients
├── components/
│   ├── layout/
│   │   ├── app-shell.tsx         # Main shell (sidebar + main)
│   │   ├── route-shell.tsx       # Reusable page wrapper (eyebrow, title, rail)
│   │   └── shell-sidebar.tsx     # Left nav with 13 nav items
│   ├── office/                  # Pixi.js components
│   │   ├── office-canvas.tsx     # Main canvas (MISSING real Pixi integration)
│   │   ├── office-floor-plan.tsx # Zone rendering
│   │   ├── office-hud.tsx        # Heads-up display
│   │   ├── office-shell.tsx      # Shell wrapper
│   │   ├── office-roster.tsx     # Agent list
│   │   ├── office-snark-feed.tsx # Humorous commentary
│   │   ├── office-view-controls.tsx # Zoom/pan controls
│   │   └── office-debug-panel.tsx # Transport/cache/contract debug
│   ├── providers/
│   │   └── app-providers.tsx     # QueryClient provider only
│   └── ui/                      # Primitive components
│       ├── button.tsx
│       ├── badge.tsx
│       └── card.tsx
├── hooks/                       # Custom hooks (MISSING - needs building)
├── lib/
│   ├── routes.ts                # Route constants
│   ├── env.ts                   # Public env vars
│   ├── query-client.ts          # TanStack Query client
│   ├── api.ts                   # API client (MISSING)
│   ├── cn.ts                    # classname utility
│   └── cache.ts                 # Cache utilities (MISSING)
├── state/
│   ├── app-shell-store.ts       # Sidebar + command palette state
│   ├── session-store.ts         # Session state (MISSING)
│   ├── office-store.ts          # Office canvas state (Zustand)
│   └── office-types.ts          # Office type definitions
└── types/                       # Type declarations (MISSING - generate from contracts)
```

### Pages That Are Complete (Placeholder-only, need real UI)

- `/app` — Dashboard with 6 tiles
- `/foundation` — Grid of 21 screens with links
- `/campaigns` — List with demo links
- `/campaigns/[id]/moves` — Move type list
- `/intel` — Feed coverage + source links
- `/nudges` — Alert surface with type tags
- `/office` — Pixi canvas shell (Pixi.js not fully wired)
- `/muse` — Placeholder chat shell
- `/council` — Session config placeholder
- `/daily-wins` — Briefing feed placeholder
- `/billing` — Subscription state placeholder
- `/settings` — Org settings placeholder
- `/` — Full marketing landing page

### Pages That Are Missing (No File at All)

- `/campaigns/[campaignId]/tasks` → needs `tasks/page.tsx`
- `/campaigns/[campaignId]/performance` → needs `performance/page.tsx`
- `/campaigns/[campaignId]/replanning` → needs `replanning/page.tsx`
- `/uploads` → needs `uploads/page.tsx` + `assets/[assetId]/page.tsx`
- `/internal/debug` → needs `page.tsx`
- `/foundation/[slug]` → dynamic foundation screens (21 of them)
- `/intel/overview`, `/intel/alerts`, `/intel/diffs` → sub-routes
- Auth sign-in/sign-up route groups are empty — Clerk handles these via `[[...sign-in]]` slugs

---

## Part 2: What to Build — Feature-by-Feature

### 2.1 API Client Layer (`apps/web/src/lib/api.ts`)

**Purpose**: Typed wrapper around all backend REST endpoints. Replaces ad-hoc fetch calls.

```typescript
// What to build in apps/web/src/lib/api.ts

const BASE = publicEnv.apiBaseUrl;

async function request<T>(path: string, options?: RequestInit & { auth?: boolean }): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options?.auth ? { Authorization: `Bearer ${await getClerkToken()}` } : {}),
      ...options?.headers,
    },
  });
  if (!res.ok) throw new ApiError(res.status, await res.text());
  return res.json() as Promise<T>;
}

// Foundation
export const foundationApi = {
  get: () => request<Foundation>("/api/v1/foundation"),
  create: (body: CreateFoundationRequest) =>
    request<Foundation>("/api/v1/foundation", {
      method: "POST",
      body: JSON.stringify(body),
      auth: true,
    }),
  updateSection: (section: string, body: UpdateSectionRequest) =>
    request<void>(`/api/v1/foundation/sections/${section}`, {
      method: "PUT",
      body: JSON.stringify(body),
      auth: true,
    }),
  listSnapshots: () => request<Snapshot[]>("/api/v1/foundation/snapshots"),
  triggerScan: (type: "quick" | "deep") =>
    request<ScanJob>(`/api/v1/foundation/scan`, {
      method: "POST",
      body: JSON.stringify({ type }),
      auth: true,
    }),
};

// Campaigns
export const campaignsApi = {
  list: () => request<Campaign[]>("/api/v1/campaigns", { auth: true }),
  get: (id: string) => request<Campaign>(`/api/v1/campaigns/${id}`, { auth: true }),
  // ... etc
};

// Council
export const councilApi = {
  startSession: (campaignId: string) =>
    request<CouncilSession>("/api/v1/council", {
      method: "POST",
      body: JSON.stringify({ campaignId }),
      auth: true,
    }),
  listSessions: () => request<CouncilSession[]>("/api/v1/council/history", { auth: true }),
  getSession: (id: string) => request<CouncilSession>(`/api/v1/council/${id}`, { auth: true }),
  getMessages: (id: string) =>
    request<CouncilMessage[]>(`/api/v1/council/${id}/messages`, { auth: true }),
};

// Muse
export const museApi = {
  submitPrompt: (body: MusePromptRequest) =>
    request<MuseResponse>("/api/v1/muse", {
      method: "POST",
      body: JSON.stringify(body),
      auth: true,
    }),
  listConversations: () => request<Conversation[]>("/api/v1/muse/history", { auth: true }),
  getConversation: (id: string) => request<Conversation>(`/api/v1/muse/${id}`, { auth: true }),
  getMessages: (id: string) => request<Message[]>(`/api/v1/muse/${id}/messages`, { auth: true }),
};

// PRL (Ripples/Essences)
export const prlApi = {
  listRipples: () => request<Ripple[]>("/api/v1/ripples", { auth: true }),
  createRipple: (body: CreateRippleRequest) =>
    request<Ripple>("/api/v1/ripples", { method: "POST", body: JSON.stringify(body), auth: true }),
  getRipple: (id: string) => request<Ripple>(`/api/v1/ripples/${id}`, { auth: true }),
  updateRipple: (id: string, body: UpdateRippleRequest) =>
    request<Ripple>(`/api/v1/ripples/${id}`, {
      method: "PUT",
      body: JSON.stringify(body),
      auth: true,
    }),
  deleteRipple: (id: string) =>
    request<void>(`/api/v1/ripples/${id}`, { method: "DELETE", auth: true }),
  realizeRipple: (id: string) =>
    request<void>(`/api/v1/ripples/${id}/realize`, { method: "POST", auth: true }),
  getRippleEdges: (id: string) => request<Edge[]>(`/api/v1/ripples/${id}/edges`, { auth: true }),
  createRippleEdge: (id: string, body: CreateEdgeRequest) =>
    request<Edge>(`/api/v1/ripples/${id}/edges`, {
      method: "POST",
      body: JSON.stringify(body),
      auth: true,
    }),
  deleteRippleEdge: (edgeId: string) =>
    request<void>(`/api/v1/ripples/edges/${edgeId}`, { method: "DELETE", auth: true }),
  listEssences: () => request<Essence[]>("/api/v1/essences", { auth: true }),
  createEssence: (body: CreateEssenceRequest) =>
    request<Essence>("/api/v1/essences", {
      method: "POST",
      body: JSON.stringify(body),
      auth: true,
    }),
  getEssence: (id: string) => request<Essence>(`/api/v1/essences/${id}`, { auth: true }),
  updateEssence: (id: string, body: UpdateEssenceRequest) =>
    request<Essence>(`/api/v1/essences/${id}`, {
      method: "PUT",
      body: JSON.stringify(body),
      auth: true,
    }),
  runDecay: () => request<void>("/api/v1/prl/decay", { method: "POST", auth: true }),
};

// Uploads
export const uploadsApi = {
  generateUploadUrl: (filename: string, contentType: string) =>
    request<UploadUrlResponse>("/api/v1/uploads", {
      method: "POST",
      body: JSON.stringify({ filename, contentType }),
      auth: true,
    }),
  generateDownloadUrl: (key: string) =>
    request<DownloadUrlResponse>("/api/v1/uploads/download", {
      method: "POST",
      body: JSON.stringify({ key }),
      auth: true,
    }),
  deleteUpload: (key: string) =>
    request<void>(`/api/v1/uploads/${encodeURIComponent(key)}`, { method: "DELETE", auth: true }),
  generateScreenshotUploadUrl: (filename: string) =>
    request<UploadUrlResponse>("/api/v1/screenshots", {
      method: "POST",
      body: JSON.stringify({ filename }),
      auth: true,
    }),
  generateExportUrl: (exportId: string) =>
    request<ExportUrlResponse>("/api/v1/exports", {
      method: "POST",
      body: JSON.stringify({ exportId }),
      auth: true,
    }),
  generateExportDownloadUrl: (exportId: string) =>
    request<ExportUrlResponse>("/api/v1/exports/download", {
      method: "POST",
      body: JSON.stringify({ exportId }),
      auth: true,
    }),
};

// Billing
export const billingApi = {
  getStatus: () => request<BillingStatus>("/api/v1/billing", { auth: true }),
  createOrder: (campaignId: string, amount: number) =>
    request<Order>("/api/v1/billing/orders", {
      method: "POST",
      body: JSON.stringify({ campaignId, amount }),
      auth: true,
    }),
  getSubscription: (id: string) =>
    request<Subscription>(`/api/v1/billing/subscriptions/${id}`, { auth: true }),
  cancelSubscription: (id: string) =>
    request<void>(`/api/v1/billing/subscriptions/${id}/cancel`, { method: "POST", auth: true }),
};

// Foundation Snapshots
export const foundationSnapshotsApi = {
  list: () => request<Snapshot[]>("api/v1/foundation/snapshots", { auth: true }),
  create: () => request<Snapshot>("/api/v1/foundation/snapshots", { method: "POST", auth: true }),
  get: (id: string) => request<Snapshot>(`/api/v1/foundation/snapshots/${id}`, { auth: true }),
  restore: (id: string) =>
    request<void>(`/api/v1/foundation/snapshots/${id}/restore`, { method: "POST", auth: true }),
};

// Scan
export const scanApi = {
  trigger: (type: "quick" | "deep") =>
    request<ScanJob>("/api/v1/foundation/scan", {
      method: "POST",
      body: JSON.stringify({ type }),
      auth: true,
    }),
  getStatus: (jobId: string) =>
    request<ScanJob>(`/api/v1/foundation/scan/${jobId}`, { auth: true }),
};

// Webhooks (read-only — these are public, no auth)
export const webhooksApi = {
  clerk: {
    receive: (payload: ClerkWebhookEvent, signature: string) =>
      request<WebhookResponse>("/api/v1/webhooks/clerk", {
        method: "POST",
        body: JSON.stringify(payload),
        headers: { "Clerk-Webhook-Signature": signature },
      }),
  },
  razorpay: {
    receive: (payload: RazorpayWebhookEvent, signature: string) =>
      request<WebhookResponse>("/api/v1/webhooks/razorpay", {
        method: "POST",
        body: JSON.stringify(payload),
        headers: { "Razorpay-Webhook-Signature": signature },
      }),
  },
};
```

**Key insight**: Every API function is auth-aware. Auth tokens come from Clerk. The `auth: true` flag triggers token injection. This keeps fetch logic DRY.

### 2.2 TanStack Query Hooks (`apps/web/src/hooks/`)

**Purpose**: Replace ad-hoc `useEffect` + fetch with typed, cached, refetchable query hooks.

```typescript
// apps/web/src/hooks/useFoundation.ts
export function useFoundation() {
  return useQuery({
    queryKey: ["foundation"],
    queryFn: foundationApi.get,
  });
}

export function useFoundationSnapshots() {
  return useQuery({
    queryKey: ["foundation", "snapshots"],
    queryFn: foundationSnapshotsApi.list,
  });
}

export function useTriggerScan() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ type }: { type: "quick" | "deep" }) => scanApi.trigger(type),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["foundation"] });
    },
  });
}

// apps/web/src/hooks/useCampaigns.ts
export function useCampaigns() { ... }
export function useCampaign(id: string) { ... }

// apps/web/src/hooks/useCouncil.ts
export function useCouncilSessions() { ... }
export function useCouncilSession(id: string) { ... }
export function useStartCouncilSession() { ... }

// apps/web/src/hooks/useMuse.ts
export function useMuseConversations() { ... }
export function useSubmitPrompt() { ... }

// apps/web/src/hooks/usePRL.ts
export function useRipples() { ... }
export function useCreateRipple() { ... }
export function useEssences() { ... }

// apps/web/src/hooks/useBilling.ts
export function useBillingStatus() { ... }
export function useCreateOrder() { ... }

// apps/web/src/hooks/useUploads.ts
export function useUploadUrl() { ... }
export function useDownloadUrl(key: string) { ... }
```

### 2.3 Real Pages to Build

#### `/app` (Dashboard)

- Wire 6 tiles to real TanStack Query hooks
- Add "Foundation completeness" → progress bar from `useFoundation()`
- Add "Campaign execution state" → list from `useCampaigns()`
- Add "Council session queue" → list from `useCouncilSessions()`
- Add "Muse activity" → recent from `useMuseConversations()`
- Add "Daily Wins status" → check `useDailyWins()`
- Add "Infrastructure health" → poll `/health`

#### `/foundation/[slug]` (Dynamic screens)

- Build 21 individual route components for each onboarding step
- Each screen: form state, validation, autosave on blur
- URL param → fetch existing data → prefill
- On submit: PATCH to section API + navigate to next screen
- Add `useAutosave` hook that debounces 2s after last keystroke

#### `/campaigns/[campaignId]/tasks`

- Kanban board with columns: Backlog → In Progress → Review → Done
- Each card: task title, assignee, due date, priority badge
- Drag-and-drop between columns (use `@dnd-kit/core`)
- On drop: PATCH task status

#### `/campaigns/[campaignId]/performance`

- Charts: budget burn rate, task completion over time, council session count
- Use Recharts (lightweight, works with React 19)
- Date range picker for filtering

#### `/campaigns/[campaignId]/replanning`

- Side-by-side: original plan vs current state
- Diff highlighting of changed moves/tasks
- "Accept diff" or "Discard" actions per item

#### `/uploads`

- File uploader: drag-and-drop zone → presigned S3 URL → direct upload
- Progress bar per file
- Grid/list view toggle
- Filter by type (document, image, video)

#### `/intel/overview`, `/intel/alerts`, `/intel/diffs`

- Overview: aggregated feed from all intel sources
- Alerts: real-time list with severity badges + "Take action" buttons
- Diffs: side-by-side diff viewer for document changes

### 2.4 Office Canvas (Pixi.js — "Pixy")

The Office canvas (`/office`) is the real-time visualization layer. Pixi.js handles rendering; the frontend subscribes to WebSocket events.

**Architecture**:

```
OfficeCanvas (Pixi.js Application)
    ├── Viewport (pixi-viewport — pan + zoom)
    │   ├── FloorPlanLayer (rendered as PIXI Graphics)
    │   │   └── ZoneSprites (one per office zone)
    │   ├── AvatarLayer
    │   │   └── AgentSprites (one per council member)
    │   │       └── speechBubbleSprite (on speaking)
    │   └── EffectsLayer (animations, transitions)
    └── HUD Overlay (React DOM — HTML on top of canvas)
        ├── OfficeHud (zoom level, mode indicator)
        ├── OfficeRoster (agent list sidebar)
        ├── OfficeSnarkFeed (scrolling commentary)
        └── OfficeDebugPanel (transport state)
```

**WebSocket connection**:

```typescript
// apps/web/src/lib/socket.ts
export function createOfficeSocket(orgId: string) {
  const ws = new WebSocket(`wss://api.raptorflow.io/ws/office?org_id=${orgId}`);

  ws.onmessage = (event) => {
    const message: OfficeEventMessage = JSON.parse(event.data);
    useOfficeStore.getState().pushEvent(message);

    // Dispatch to appropriate handler
    switch (message.eventType) {
      case "agent_seated_conference":
        moveAgentSprite(message.payload.agent, message.payload.zone);
        break;
      case "speech_bubble":
        showSpeechBubble(message.payload.agent, message.payload.content);
        break;
      // ... etc
    }
  };

  return ws;
}
```

**Offline mode**: When `NEXT_PUBLIC_OFFLINE_MODE=true`, the socket connects to `ws://localhost:3001` (a local mock WebSocket server). The mock server replays canned event sequences.

---

## Part 3: Deployment Architecture

### Where Each Thing Lives

```
Internet
   │
   ├── Vercel (Frontend + Edge Functions)
   │   ├── Next.js app (SSR/SSG)
   │   ├── Static assets (CDN)
   │   └── API routes ( Next.js API route handlers — lightweight only)
   │
   └── AWS (Backend + Data)
       │
       ├── CloudFront (API CDN + TLS termination)
       │   └── ALB (Application Load Balancer)
       │       ├── ECS Fargate — api (Axum Rust binary)
       │       ├── ECS Fargate — jobs (SQS worker)
       │       ├── ECS Fargate — stream-coordinator
       │       └── ECS Fargate — event-harvester
       │
       ├── Aurora PostgreSQL 16 (with pgvector)
       │   └── Read replica for analytics queries
       ├── DragonflyDB (Redis-compatible) — cache + sessions
       ├── Qdrant — vector store for embeddings
       ├── S3 — static assets, uploads
       │   └── CloudFront CDN for uploads
       ├── SQS — job queues
       │   ├── embedding-job queue
       │   ├── content-pregeneration-job queue
       │   ├── intern-task queue
       │   └── tool-gateway-request queue
       ├── Secrets Manager — all secrets
       ├── EventBridge — cron triggers
       └── GCP (AI inference only)
           └── Gemini (via crates/gcp)
```

### Vercel Configuration

```typescript
// apps/web/vercel.json (or Vercel dashboard settings)
{
  "framework": "nextjs",
  "buildCommand": "pnpm --filter @raptorflow/web build",
  "installCommand": "pnpm install",
  "regions": ["sin1"],  // Singapore — closest to Mumbai region
  "env": {
    "NEXT_PUBLIC_APP_URL": "@rf_app_url",
    "NEXT_PUBLIC_API_BASE_URL": "@rf_api_base_url",
    "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY": "@rf_clerk_publishable_key",
    "NEXT_PUBLIC_OFFLINE_MODE": "false"
  },
  "regions": ["sin1"]
}
```

**Vercel environment variables** (set in Vercel dashboard):

- `NEXT_PUBLIC_APP_URL` = `https://app.raptorflow.io`
- `NEXT_PUBLIC_API_BASE_URL` = `https://api.raptorflow.io`
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` = from Clerk dashboard
- `NEXT_PUBLIC_OFFLINE_MODE` = `false` (always false in production)

### AWS Backend Deployment

The Rust binary is deployed as an ECS Fargate service:

```yaml
# infra/tofu/modules/api-service/main.tf
resource "aws_ecs_service" "api" {
name            = "raptorflow-api"
cluster         = aws_ecs_cluster.main.id
task_definition = aws_ecs_task_definition.api.arn
desired_count   = 2
min_percent     = 50
max_percent     = 200

load_balancer {
target_group_arn = aws_lb_target_group.api.arn
container_name   = "api"
container_port   = 8080
}

deployment_controller {
type = "ecs"
}
}

resource "aws_ecs_task_definition" "api" {
family = "raptorflow-api"
cpu    = "512"
memory = "1024"

container_definitions = [{
name      = "api"
image     = "${aws_ecr_repository.api.repository_url}:${var.image_tag}"
portMappings = [{ containerPort = 8080 }]
environment = [
{ name = "APP_ENV", value = "prod" },
{ name = "AWS_REGION", value = "ap-south-1" },
]
secrets = [
{ name = "DATABASE_URL", valueFrom = "${aws_secretsmanager_secret.database.arn}" },
{ name = "CLERK_SECRET_KEY", valueFrom = "${aws_secretsmanager_secret.clerk.arn}" },
{ name = "RAZORPAY_SECRET", valueFrom = "${aws_secretsmanager_secret.razorpay.arn}" },
]
}]
}
```

### Domain & TLS

```
Vercel → app.raptorflow.io (managed TLS)
AWS ALB → api.raptorflow.io (managed TLS via ACM)
         → assets.raptorflow.io → S3 + CloudFront
```

### Environment Variable Mapping

| Variable                            | Vercel (Frontend)           | AWS ECS (Backend)                      |
| ----------------------------------- | --------------------------- | -------------------------------------- |
| `NEXT_PUBLIC_APP_URL`               | `https://app.raptorflow.io` | —                                      |
| `NEXT_PUBLIC_API_BASE_URL`          | `https://api.raptorflow.io` | —                                      |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | from Clerk dashboard        | —                                      |
| `APP_ENV`                           | —                           | `prod`                                 |
| `RAPTORFLOW_FRONTEND_URL`           | —                           | `https://app.raptorflow.io`            |
| `DATABASE_URL`                      | —                           | from Secrets Manager                   |
| `DRAGONFLY_URL`                     | —                           | `redis://10.0.x.x:6379`                |
| `QDRANT_URL`                        | —                           | `http://10.0.x.x:6333`                 |
| `SQS_BASE_URL`                      | —                           | `https://sqs.ap-south-1.amazonaws.com` |
| `RAZORPAY_KEY_SECRET`               | —                           | from Secrets Manager                   |
| `CLERK_ISSUER`                      | —                           | `https://...clerk.accounts.dev`        |
| `CLERK_JWKS_URL`                    | —                           | from Clerk dashboard                   |
| `SENTRY_DSN`                        | —                           | from Secrets Manager                   |

### CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - run: pnpm install --frozen-lockfile
      - run: pnpm build
        env:
          NEXT_PUBLIC_API_BASE_URL: ${{ secrets.RF_API_BASE_URL }}
          NEXT_PUBLIC_APP_URL: ${{ secrets.RF_APP_URL }}
      - uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: "--prod"
          working-directory: ./apps/web

  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ap-south-1
      - run: |
          aws ecs update-service --cluster raptorflow --service raptorflow-api \
            --force-new-deployment
          aws ecs wait services-stable --cluster raptorflow \
            --services raptorflow-api
```

---

## Part 4: Offline Development Strategy

### The Problem

The backend uses:

- **GCP Gemini** for AI inference (requires Google Cloud credentials)
- **AWS SQS** for job queues
- **Aurora PostgreSQL** for data
- **DragonflyDB** for caching

During offline development, you can't reach any of these.

### The Solution: Offline Mode

Add a `NEXT_PUBLIC_OFFLINE_MODE=true` flag that switches the frontend to a fully mocked backend.

```typescript
// apps/web/src/lib/env.ts
export const publicEnv = {
  appUrl: process.env.NEXT_PUBLIC_APP_URL ?? "http://localhost:3000",
  apiBaseUrl: process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8080",
  offlineMode: process.env.NEXT_PUBLIC_OFFLINE_MODE === "true",
} as const;
```

### What Changes in Offline Mode

#### 1. API Client — Mock Adapter

```typescript
// apps/web/src/lib/api-offline.ts
// When offlineMode=true, this module intercepts all API calls
// and returns mock data instead of hitting the network.

import { mockFoundation, mockCampaigns, mockCouncilSessions } from "@/mocks/data";

export function isOffline() {
  return publicEnv.offlineMode;
}

export async function offlineGet<T>(resource: string): Promise<T> {
  // Simulate network delay
  await new Promise((r) => setTimeout(r, 200 + Math.random() * 300));

  switch (resource) {
    case "/api/v1/foundation":
      return mockFoundation as T;
    case "/api/v1/campaigns":
      return mockCampaigns as T;
    case "/api/v1/council/history":
      return mockCouncilSessions as T;
    default:
      throw new Error(`Offline mock not defined for: ${resource}`);
  }
}
```

Update `apps/web/src/lib/api.ts`:

```typescript
async function request<T>(path: string, options?: RequestInit & { auth?: boolean }): Promise<T> {
  if (isOffline()) {
    if (options?.method === "POST" || options?.method === "PUT" || options?.method === "DELETE") {
      // Simulate successful mutation
      await new Promise((r) => setTimeout(r, 100));
      return { success: true } as T;
    }
    return offlineGet<T>(path);
  }

  // ... real fetch logic
}
```

#### 2. Replace Gemini with GROQ (Offline AI)

GROQ (Graph Relational Object Queries) is a local inference engine. For offline development:

```bash
# Start a local GROQ inference server
docker run --gpus all -p 8081:8000 \
  ghcr.io/groq/groq-api:latest \
  --model mixtral-8x7b-32768
```

```typescript
// apps/web/src/lib/ai-offline.ts
// When offlineMode=true, this module handles AI calls
// using a local GROQ server instead of GCP Gemini.

const GROQ_BASE_URL = "http://localhost:8081/v1";
const GROQ_API_KEY = "lm-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX";

export async function completion(prompt: string, system: string): Promise<string> {
  if (!isOffline()) {
    throw new Error("AI offline adapter called in production mode");
  }

  const res = await fetch(`${GROQ_BASE_URL}/chat/completions`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${GROQ_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: "mixtral-8x7b-32768",
      messages: [
        { role: "system", content: system },
        { role: "user", content: prompt },
      ],
      temperature: 0.7,
    }),
  });

  const data = await res.json();
  return data.choices[0].message.content;
}
```

Wire this into the Muse and Council AI calls:

```typescript
// In museApi.submitPrompt or councilApi.startSession
if (isOffline()) {
  return completion(userPrompt, systemPrompt);
}
```

#### 3. Mock WebSocket Server (for Office Canvas)

```bash
# Start a mock WebSocket server that replays office events
npx tsx scripts/mock-office-server.ts
```

```typescript
// scripts/mock-office-server.ts
// A simple WebSocket server on port 3001 that:
// 1. Sends office events on a timer (simulating live office activity)
// 2. Responds to incoming events with appropriate echoes
// 3. Provides a REST endpoint to reset the event sequence

import { WebSocketServer } from "ws";

const wss = new WebSocketServer({ port: 3001 });

const eventSequence: OfficeEventMessage[] = [
  {
    orgId: "dev-org",
    type: "office.event",
    eventType: "morning_meeting_start",
    payload: { room: "conference-room", speaker: "Strategist" },
  },
  {
    orgId: "dev-org",
    type: "office.event",
    eventType: "speech_bubble",
    payload: { agent: "ogilvy", content: "The brief is not a suggestion." },
  },
  // ... more events
];

let eventIndex = 0;

wss.on("connection", (ws) => {
  const interval = setInterval(() => {
    if (eventIndex < eventSequence.length) {
      ws.send(JSON.stringify(eventSequence[eventIndex++]));
    } else {
      // Loop back for continuous demo
      eventIndex = 0;
    }
  }, 3000);

  ws.on("close", () => clearInterval(interval));
});

console.log("Mock office WebSocket server running on ws://localhost:3001");
```

#### 4. Local Database (PostgreSQL via Docker)

```bash
# docker-compose.offline.yml
# Use for offline development instead of the full compose stack
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: raptorflow_dev
      POSTGRES_USER: raptorflow
      POSTGRES_PASSWORD: raptorflow
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/migrations:/docker-entrypoint-initdb.d

  dragonfly:
    image: dragonflydb/dragonfly
    ports:
      - "6379:6379"

  # GROQ for offline AI (GPU recommended, CPU fallback works)
  groq:
    image: ghcr.io/groq/groq-api:latest
    ports:
      - "8081:8000"
    environment:
      # Optional: set API key for local auth
      GROQ_API_KEY: lm-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

#### 5. Environment for Offline Development

Create `apps/web/.env.local`:

```bash
# Offline mode — disables real API calls
NEXT_PUBLIC_OFFLINE_MODE=true

# Point to local backend (or use mocks)
NEXT_PUBLIC_API_BASE_URL=http://localhost:8080
NEXT_PUBLIC_APP_URL=http://localhost:3000

# Mock Clerk (dev JWT bypass — ONLY FOR OFFLINE)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_mock
```

Create `backend/.env.offline`:

```bash
APP_ENV=dev
DATABASE_URL=postgres://raptorflow:raptorflow@localhost:5432/raptorflow_dev
DRAGONFLY_URL=redis://localhost:6379
QDRANT_URL=http://localhost:6333
SQS_BASE_URL=http://localhost:4566  # LocalStack
ALLOW_INSECURE_DEV_AUTH=true
DEV_BEARER_TOKEN=dev-token-12345

# GROQ instead of Gemini
AI_PROVIDER=groq
GROQ_API_URL=http://localhost:8081/v1
GROQ_API_KEY=lm-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

#### 6. Switching Between Modes

```bash
# Production-like (real APIs)
pnpm dev

# Offline mode (mocked everything)
echo "NEXT_PUBLIC_OFFLINE_MODE=true" >> apps/web/.env.local
pnpm dev
```

Or use a startup script:

```bash
# scripts/dev-offline.sh
cp .env.offline backend/.env
echo "NEXT_PUBLIC_OFFLINE_MODE=true" > apps/web/.env.local
docker compose -f docker-compose.offline.yml up -d
pnpm dev
```

### Offline Mode Feature Matrix

| Feature            | Production                     | Offline Mode            |
| ------------------ | ------------------------------ | ----------------------- |
| API calls          | Real backend                   | Mocked (local data)     |
| AI inference       | GCP Gemini                     | Local GROQ              |
| WebSocket (Office) | Real `wss://api.raptorflow.io` | `ws://localhost:3001`   |
| Database           | Aurora PostgreSQL              | Local Postgres Docker   |
| Cache              | DragonflyDB (AWS)              | Local Dragonfly Docker  |
| Queues             | AWS SQS                        | LocalStack SQS          |
| Auth               | Clerk (real JWTs)              | Dev bypass token        |
| File uploads       | S3 + CloudFront                | Local MinIO or disabled |

---

## Part 5: Connecting Frontend to Backend (Wire Diagram)

```
Browser (Vercel CDN)
    │
    ├── Clerk JS SDK (loads from Clerk CDN)
    │   └── Gets JWT with org_id claim
    │
    └── Next.js App
        │
        ├── TanStack Query (caches all API responses)
        │   └── queryClient = new QueryClient({ staleTime: 30_000 })
        │
        ├── Zustand Stores
        │   ├── useAppShellStore (sidebar state)
        │   ├── useOfficeStore (Pixi canvas state + event log)
        │   └── useSessionStore (conversation history)
        │
        ├── API Client (fetch with auth header)
        │   ├── Clerk JWT → Authorization: Bearer <token>
        │   └── org_id from JWT → all requests scoped
        │
        ├── WebSocket (Office canvas only)
        │   └── Connects to wss://api.raptorflow.io/ws/office
        │   └── Message types: OfficeEventMessage (from schemas/ws/)
        │
        └── File Uploads (direct to S3)
            ├── GET /api/v1/uploads → presigned S3 PUT URL
            ├── PUT directly to S3 (browser → S3, bypasses backend)
            └── GET /api/v1/uploads/download → presigned S3 GET URL
```

### Clerk Integration Detail

Clerk handles auth at the Next.js layer. The JWT is available via `const { getToken } = useAuth()`.

```typescript
// apps/web/src/lib/get-clerk-token.ts
// Used by the API client to inject auth headers
export async function getClerkToken(): Promise<string> {
  const { getToken } = useAuth();
  const token = await getToken();
  if (!token) throw new Error("Not authenticated");
  return token;
}
```

For server components:

```typescript
// In a Server Component (app/(app)/campaigns/page.tsx)
import { auth } from "@clerk/nextjs/server";
const { getToken } = await auth();
const token = await getToken();
```

---

## Part 6: Testing Strategy

### 1. Unit Tests (Vitest)

```bash
pnpm test:unit --filter @raptorflow/web
```

- Test all hooks (`useFoundation`, `useCampaigns`, etc.)
- Test API client functions with MSW (Mock Service Worker)
- Test Zustand store reducers
- Test utility functions (`cn`, date formatting, etc.)

### 2. Component Tests (Playwright)

```bash
pnpm test:component --filter @raptorflow/web
```

- Test each page renders without crashing
- Test form submissions
- Test navigation flows

### 3. Integration Tests

- Test API client → actual backend (when online)
- Test offline mode → mock server

### 4. E2E Tests (Playwright)

```bash
pnpm test:e2e --filter @raptorflow/web
```

- Full user journeys (sign in → create foundation → start council session)
- Office canvas loads and shows sprites

### 5. Offline Testing Checklist

```bash
# Before shipping anything:
1. Set NEXT_PUBLIC_OFFLINE_MODE=true
2. Start docker-compose.offline.yml
3. Start mock-office-server.ts
4. Run: pnpm dev
5. Verify all pages render (even with mock data)
6. Verify Office canvas shows live events from mock WS
7. Run: pnpm build (must succeed in offline mode too)
```

---

## Part 7: File-by-File Frontend Roadmap

| File to Create                                               | Purpose                             | Priority                        |
| ------------------------------------------------------------ | ----------------------------------- | ------------------------------- |
| `apps/web/src/lib/api.ts`                                    | Typed API client (all 17 endpoints) | **P0 — blocks all data wiring** |
| `apps/web/src/hooks/useFoundation.ts`                        | TanStack Query hooks for Foundation | **P0**                          |
| `apps/web/src/hooks/useCampaigns.ts`                         | Campaign CRUD hooks                 | **P0**                          |
| `apps/web/src/hooks/useCouncil.ts`                           | Council session hooks               | **P0**                          |
| `apps/web/src/hooks/useMuse.ts`                              | Muse prompt hooks                   | **P0**                          |
| `apps/web/src/hooks/usePRL.ts`                               | Ripples/Essences hooks              | P1                              |
| `apps/web/src/hooks/useBilling.ts`                           | Billing hooks                       | P1                              |
| `apps/web/src/hooks/useUploads.ts`                           | Upload hooks                        | P1                              |
| `apps/web/src/mocks/data.ts`                                 | Offline mock data                   | P1                              |
| `apps/web/src/lib/socket.ts`                                 | WebSocket client                    | P1                              |
| `scripts/mock-office-server.ts`                              | Mock WS server for offline          | P1                              |
| `docker-compose.offline.yml`                                 | Offline dev stack                   | P1                              |
| `apps/web/.env.local`                                        | Offline env template                | P1                              |
| `apps/web/src/app/(app)/campaigns/[id]/tasks/page.tsx`       | Task board                          | P2                              |
| `apps/web/src/app/(app)/campaigns/[id]/performance/page.tsx` | Analytics                           | P2                              |
| `apps/web/src/app/(app)/campaigns/[id]/replanning/page.tsx`  | Replanning                          | P2                              |
| `apps/web/src/app/(app)/uploads/page.tsx`                    | Upload manager                      | P2                              |
| `apps/web/src/app/(app)/foundation/[slug]/page.tsx`          | Dynamic 21 screens                  | P2                              |
| `apps/web/src/components/office/office-canvas.tsx`           | Full Pixi.js integration            | P2                              |
| `apps/web/src/lib/ai-offline.ts`                             | GROQ adapter for offline AI         | P2                              |
| `apps/web/.env.offline`                                      | Backend offline env                 | P2                              |
| `apps/web/src/app/(app)/intel/overview/page.tsx`             | Intel overview                      | P3                              |
| `apps/web/src/app/(app)/intel/alerts/page.tsx`               | Alert stream                        | P3                              |
| `apps/web/src/app/(app)/intel/diffs/page.tsx`                | Diff archive                        | P3                              |
| `apps/web/src/app/(app)/internal/debug/page.tsx`             | Debug tools                         | P3                              |
| `apps/web/vercel.json`                                       | Vercel deployment config            | P3                              |

---

## Summary

1. **What to build**: An API client layer + TanStack Query hooks + 4 missing page components + full Pixi.js Office integration + GROQ offline adapter
2. **Deployment**: Vercel for Next.js (frontend + edge), AWS ECS Fargate for Rust API, Aurora PostgreSQL + DragonflyDB + Qdrant for data
3. **Modularization**: Frontend is a standalone Next.js app on Vercel. Backend is a single Rust binary on ECS. They communicate over HTTPS + WebSocket. S3 handles file storage directly (presigned URLs bypass the backend for uploads)
4. **Offline dev**: Set `NEXT_PUBLIC_OFFLINE_MODE=true`, run `docker-compose.offline.yml`, run `mock-office-server.ts`, use GROQ for AI instead of Gemini
5. **Testing offline**: The mock server replays office events, mock data covers all API responses, GROQ handles AI locally
