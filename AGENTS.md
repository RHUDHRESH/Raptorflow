<!-- GSD:project-start source:PROJECT.md -->
## Project

**RaptorFlow**

RaptorFlow is a marketing intelligence and campaign orchestration platform that combines AI agents, real-time collaboration features, and automated content generation. The system enables marketing teams to create campaigns through multi-agent council debates, manage foundation data, track competitor intelligence, and collaborate in real-time through an AI avatar-powered office canvas.

**Core Value:** Organizations can launch data-driven marketing campaigns faster by leveraging AI agent councils that debate and synthesize strategy, with real-time visualization through an interactive office canvas where AI avatars represent different strategic perspectives.

### Constraints

- **Tech**: Rust 1.94+ required for backend — why: Type safety, performance
- **Multi-tenancy**: All data must be filtered by org_id via RLS — why: Tenant isolation is non-negotiable
- **AI Provider**: Vertex AI only — why: Context caching for cost optimization
- **Payments**: PhonePe only (India market) — why: Local payment provider
<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->
## Technology Stack

## Overview
## Frontend Stack
### Core Framework
| Technology     | Version | Purpose                                                  |
| -------------- | ------- | -------------------------------------------------------- |
| **Next.js**    | 15.5.7  | React framework with App Router, React Server Components |
| **React**      | 19.0.0  | UI library                                               |
| **TypeScript** | 6.0.2   | Type safety throughout                                   |
### State Management
| Technology         | Version | Purpose                                |
| ------------------ | ------- | -------------------------------------- |
| **Zustand**        | 5.0.0   | Lightweight client-side state          |
| **TanStack Query** | 5.66.0  | Server state, caching, synchronization |
### Authentication
| Technology        | Version | Purpose                                 |
| ----------------- | ------- | --------------------------------------- |
| **@clerk/nextjs** | 6.0.0   | JWT validation, middleware, SSR support |
### UI Components
| Technology                   | Version | Purpose                         |
| ---------------------------- | ------- | ------------------------------- |
| **Tailwind CSS**             | 4.1.18  | Utility-first styling           |
| **shadcn/ui**                | (Radix) | Accessible component primitives |
| **@radix-ui/react-slot**     | 1.1.0   | Headless component composition  |
| **class-variance-authority** | 0.7.1   | Component variant management    |
| **clsx**                     | 2.1.1   | Class name utility              |
| **tailwind-merge**           | 3.3.0   | Tailwind class merging          |
### Animation
| Technology        | Version | Purpose                                       |
| ----------------- | ------- | --------------------------------------------- |
| **Framer Motion** | 12.0.0  | General animations and transitions            |
| **PixiJS**        | 8.0.0   | High-performance 2D rendering (Office canvas) |
| **pixi-viewport** | 6.0.0   | Panning/zooming for Office canvas             |
### Icons & Media
| Technology       | Version | Purpose             |
| ---------------- | ------- | ------------------- |
| **lucide-react** | 0.511.0 | Consistent icon set |
## Backend Stack
### Runtime & Compiler
| Technology | Version   | Purpose                        |
| ---------- | --------- | ------------------------------ |
| **Rust**   | 1.94.0    | Systems programming language   |
| **cargo**  | (bundled) | Package manager and build tool |
### Web Framework
| Technology     | Version | Purpose                            |
| -------------- | ------- | ---------------------------------- |
| **Axum**       | 0.8     | HTTP server with WebSocket support |
| **tower**      | 0.5     | Modular middleware                 |
| **tower-http** | 0.6     | HTTP middleware (CORS, tracing)    |
### Async Runtime
| Technology | Version | Purpose                          |
| ---------- | ------- | -------------------------------- |
| **Tokio**  | 1.48    | Async runtime with full features |
### Serialization
| Technology     | Version | Purpose                 |
| -------------- | ------- | ----------------------- |
| **serde**      | 1.0     | Serialization framework |
| **serde_json** | 1.0     | JSON support            |
### Database
| Technology | Version | Purpose                                                  |
| ---------- | ------- | -------------------------------------------------------- |
| **sqlx**   | 0.8     | Async PostgreSQL driver with compile-time query checking |
### Authentication
| Technology       | Version | Purpose                       |
| ---------------- | ------- | ----------------------------- |
| **jsonwebtoken** | 10.1    | JWT parsing and validation    |
| **reqwest**      | 0.12    | HTTP client for JWKS fetching |
### Cryptography
| Technology | Version | Purpose                        |
| ---------- | ------- | ------------------------------ |
| **hmac**   | 0.12    | Webhook signature verification |
| **sha2**   | 0.10    | Hashing                        |
| **base64** | 0.22    | Encoding/decoding              |
| **hex**    | 0.4     | Hex encoding                   |
### Utilities
| Technology      | Version | Purpose                     |
| --------------- | ------- | --------------------------- |
| **anyhow**      | 1.0     | Error handling              |
| **thiserror**   | 2.0     | Custom error types          |
| **uuid**        | 1.18    | UUID generation and parsing |
| **ulid**        | 1.2     | Sortable unique IDs         |
| **chrono**      | 0.4     | Date/time handling          |
| **url**         | 2.5     | URL parsing                 |
| **futures**     | 0.3     | Async abstractions          |
| **async-trait** | 0.1     | Async method traits         |
### Caching & Messaging
| Technology | Version | Purpose                                    |
| ---------- | ------- | ------------------------------------------ |
| **redis**  | 0.32    | DragonflyDB client with connection pooling |
### Configuration
| Technology  | Version | Purpose                      |
| ----------- | ------- | ---------------------------- |
| **config**  | 0.15    | Configuration management     |
| **dotenvy** | 0.15    | Environment variable loading |
### Observability
| Technology             | Version | Purpose                            |
| ---------------------- | ------- | ---------------------------------- |
| **tracing**            | 0.1     | Structured logging and diagnostics |
| **tracing-subscriber** | 0.3     | Log formatting and filtering       |
## Data Infrastructure
### Primary Database
| Technology                             | Purpose                                 |
| -------------------------------------- | --------------------------------------- |
| **Aurora PostgreSQL 16 Serverless v2** | Primary data store                      |
| **pgvector**                           | Vector embeddings (installed extension) |
| **PgBouncer 1.24.1**                   | Connection pooling (transaction mode)   |
### Vector Search
| Technology | Version | Purpose                  |
| ---------- | ------- | ------------------------ |
| **Qdrant** | 1.13.6  | Vector similarity search |
### Cache & Pub/Sub
| Technology      | Version | Purpose                                |
| --------------- | ------- | -------------------------------------- |
| **DragonflyDB** | 1.31.0  | Redis-compatible cache, pub/sub, locks |
### Object Storage
| Technology | Purpose                                     |
| ---------- | ------------------------------------------- |
| **S3**     | File uploads, screenshots, exports, backups |
### Message Queues
| Technology  | Purpose                                                   |
| ----------- | --------------------------------------------------------- |
| **AWS SQS** | Background job processing (embedding, content generation) |
## AI/Inference
| Technology          | Purpose                 | Tier/Model                                               |
| ------------------- | ----------------------- | -------------------------------------------------------- |
| **Vertex AI**       | AI inference            | Gemini Pro (strategist), Flash-Lite (council/generation) |
| **Context Caching** | Foundation JSON caching | Reduces inference cost                                   |
## Monorepo Tooling
### Build System
| Technology    | Version | Purpose                        |
| ------------- | ------- | ------------------------------ |
| **pnpm**      | 10.33.0 | Package manager for workspaces |
| **Turborepo** | 2.5.0   | Build orchestrator, caching    |
### Code Quality
| Technology     | Version | Purpose         |
| -------------- | ------- | --------------- |
| **Prettier**   | 3.5.0   | Code formatting |
| **TypeScript** | 6.0.2   | Type checking   |
### Development Tools
| Technology    | Purpose                       |
| ------------- | ----------------------------- |
| **Git hooks** | Pre-commit validation         |
| **Docker**    | Local development environment |
## Infrastructure as Code
| Technology                   | Purpose                                       |
| ---------------------------- | --------------------------------------------- |
| **OpenTofu**                 | Cloud infrastructure definition (AWS, Vercel) |
| **Terraform-compatible HCL** | Infrastructure configuration                  |
## External Services
| Service                 | Purpose                     |
| ----------------------- | --------------------------- |
| **Clerk**               | Identity and authentication |
| **PhonePe**             | Payment processing          |
| **Vercel**              | Frontend deployment         |
| **Sentry**              | Error tracking              |
| **CloudWatch**          | Monitoring and logging      |
| **AWS Secrets Manager** | Secret storage              |
## Local Development
### Docker Services
| Service       | Image                         | Ports      |
| ------------- | ----------------------------- | ---------- |
| **web**       | node:22-alpine                | 3000       |
| **api**       | rust:1.94-bookworm            | 8080       |
| **postgres**  | pgvector/pg16                 | 5432       |
| **pgbouncer** | edoburu/pgbouncer:1.24.1      | 6432       |
| **dragonfly** | dragonflydb/dragonfly:v1.31.0 | 6379       |
| **qdrant**    | qdrant/qdrant:v1.13.6         | 6333, 6334 |
## Summary Table
| Layer              | Technology        | Key Version |
| ------------------ | ----------------- | ----------- |
| Frontend Framework | Next.js           | 15.5.7      |
| Frontend Language  | React             | 19.0.0      |
| Frontend Language  | TypeScript        | 6.0.2       |
| Package Manager    | pnpm              | 10.33.0     |
| Build Tool         | Turborepo         | 2.5.0       |
| Backend Language   | Rust              | 1.94.0      |
| HTTP Framework     | Axum              | 0.8         |
| Async Runtime      | Tokio             | 1.48        |
| Database Driver    | SQLx              | 0.8         |
| Primary DB         | Aurora PostgreSQL | 16          |
| Vector DB          | Qdrant            | 1.13.6      |
| Cache              | DragonflyDB       | 1.31.0      |
| Connection Pooler  | PgBouncer         | 1.24.1      |
| AI Provider        | Vertex AI         | -           |
| Payments           | PhonePe           | -           |
| Auth               | Clerk             | 6.0.0       |
| Hosting            | Vercel / AWS      | -           |
| IaC                | OpenTofu          | -           |
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

## Overview
## High-Level Architecture
```
```
## Directory Structure
```
```
## Core Components
### 1. Frontend (Next.js 15)
- Marketing site with React Server Components
- Authenticated app shell (client-rendered)
- Office canvas using PixiJS for real-time collaboration
- Route groups: `(app)`, `(auth)`, `(marketing)`
- **Client State**: Zustand
- **Server State**: TanStack Query
- **Auth**: Clerk middleware
### 2. Backend (Rust)
| Crate                     | Purpose                                     |
| ------------------------- | ------------------------------------------- |
| `raptorflow-api`          | Main entry point, HTTP server setup         |
| `raptorflow-http`         | Route definitions, middleware orchestration |
| `raptorflow-auth`         | Clerk JWT validation, middleware            |
| `raptorflow-db`           | SQLx-based database access                  |
| `raptorflow-config`       | Environment configuration                   |
| `raptorflow-jobs`         | Background job registry                     |
| `raptorflow-telemetry`    | Tracing/subscriber setup                    |
| `raptorflow-foundation`   | Foundation data management                  |
| `raptorflow-campaigns`    | Campaign CRUD and orchestration             |
| `raptorflow-council`      | Multi-agent council sessions                |
| `raptorflow-muse`         | Conversational AI interface                 |
| `raptorflow-intel`        | Intelligence and competitor analysis        |
| `raptorflow-office`       | Office canvas coordination                  |
| `raptorflow-prl`          | Predictive ripple memory                    |
| `raptorflow-billing`      | PhonePe payment processing                  |
| `raptorflow-integrations` | External service integrations               |
| `raptorflow-eel`          | Entity Essence Language                     |
| `raptorflow-contracts`    | Shared domain types                         |
### 3. Shared Contracts
- `domain.ts` - Domain types (Campaigns, Council, Muse, Intel, PRL)
- `rest.ts` - REST API namespace definitions
- `ws.ts` - WebSocket event type definitions
- `queues.ts` - SQS queue definitions
- `env.ts` - Environment variable interfaces
### 4. Data Layer
#### PostgreSQL (Aurora Serverless v2)
- Primary source of truth
- Row-Level Security (RLS) for tenant isolation
- pgvector extension for embeddings
- PgBouncer connection pooling
- `organizations` - Tenant management
- `org_users` - User-organization relationship
- `audit_logs` - Action auditing
- `foundation_snapshots` - Versioned foundation data
- `campaigns`, `campaign_moves`, `campaign_tasks` - Campaign management
- `council_sessions`, `council_agent_positions` - Multi-agent sessions
- `ripples`, `ripple_edges`, `agent_essences` - PRL data
- `muse_conversations`, `muse_messages` - Chat history
- `intel_*` tables - Competitor intelligence
- `subscriptions`, `payment_events` - Billing
#### Qdrant (Vector Search)
- Filtered vector collections for semantic search
- Used for foundation section embeddings
#### DragonflyDB (Redis-compatible)
- Session caching
- Pub/sub for real-time events
- Distributed locks
#### S3
- File uploads
- Screenshots
- Exports
- Backups
#### SQS Queues
- `raptorflow-{env}-embedding` - Embedding jobs
- `raptorflow-{env}-content-pregeneration` - Content generation
## Data Flow
### 1. Tenant Isolation Flow
```
```
### 2. Campaign Creation Flow
```
```
### 3. Real-time Communication
```
```
## API Boundaries
### REST API Namespaces
| Namespace                  | Description                  |
| -------------------------- | ---------------------------- |
| `/api/v1/foundation`       | Foundation data and scanning |
| `/api/v1/campaigns`        | Campaign management          |
| `/api/v1/council`          | Council sessions             |
| `/api/v1/muse`             | Conversational interface     |
| `/api/v1/intel`            | Intelligence artifacts       |
| `/api/v1/daily-wins`       | Daily briefings              |
| `/api/v1/nudges`           | User notifications           |
| `/api/v1/billing`          | Subscription management      |
| `/api/v1/office`           | Office canvas state          |
| `/api/v1/uploads`          | File uploads                 |
| `/api/v1/webhooks/clerk`   | Auth webhooks                |
| `/api/v1/webhooks/phonepe` | Payment webhooks             |
| `/api/v1/internal/jobs/*`  | Internal job triggers        |
### WebSocket Event Types
## Security Boundaries
## Infrastructure Boundaries
- **Public**: ALB, Vercel CDN
- **Private**: ECS tasks, PgBouncer, DragonflyDB, Qdrant
- **Isolated**: Aurora PostgreSQL, S3
## External Dependencies
| Service   | Purpose                     |
| --------- | --------------------------- |
| Clerk     | Identity and authentication |
| Vertex AI | AI inference (Gemini)       |
| PhonePe   | Payment processing          |
| Vercel    | Frontend hosting            |
| AWS       | Compute, databases, storage |
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->
## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, or `.github/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
