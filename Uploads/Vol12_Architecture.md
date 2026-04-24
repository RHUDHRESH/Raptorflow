# RAPTORFLOW MASTER DOCUMENT SERIES

## Volume 12: Architecture, Infrastructure, Deployment, and Economics

---

# Opening: The Machine Behind the Magic

Every design principle in the previous eleven volumes — the personality stability, the memory persistence, the real-time streaming, the autonomous intelligence — depends on an infrastructure that can deliver it reliably at scale, at cost. This volume documents that infrastructure completely. Every service, every configuration decision, every cost component, every scaling consideration.

The goal of the architecture is not elegance for its own sake. It is the specific capability profile that RaptorFlow requires: millisecond-latency memory retrieval, concurrent multi-agent inference, real-time token streaming, always-on monitoring, and economics that make ₹5,000/month viable with strong margins.

---

# Part One: The Technology Stack — Complete Specification

## Chapter 1.1 — Backend: Rust and Axum

**Why Rust:** Three reasons that are not interchangeable with other languages.

First, **predictable latency**. Rust compiles to native code with no garbage collector. There are no GC pause events — the 50-200ms pauses that JVM and .NET languages produce when memory pressure triggers collection. For RaptorFlow, which is running WebSocket streams of AI-generated tokens where any latency spike is visible to the user, GC pauses are unacceptable. Rust's deterministic memory management means P99 latency is close to P50 latency.

Second, **cost efficiency**. A Rust service handling a given workload consumes 3-5x less CPU and memory than an equivalent Python/FastAPI service. At scale, this translates directly to EC2 instance savings. The economics of ₹5,000/month pricing depend on keeping infrastructure costs low, and the Rust choice is a significant contributor.

Third, **the type system for correctness**. The borrow checker prevents entire categories of concurrency bugs — data races, use-after-free, null pointer dereferences — at compile time. For a system that runs concurrent agent inference with complex shared state, the type system is a correctness guarantee that cannot be achieved through code review or testing alone.

**The Axum framework:** Built on Tokio (Rust's async runtime) and Tower (composable middleware). Axum provides: native WebSocket upgrade support, typed extractor pattern for request parsing, layer-based middleware composition, and compile-time verified routing. All WebSocket handling, REST API routing, and middleware (authentication, rate limiting, request tracing) are implemented in Axum.

**The Tokio runtime:** The async executor for all concurrent operations. Key usage patterns in RaptorFlow:

- `tokio::spawn` for independent background tasks (intelligence scans, SWR consolidation)
- `tokio::task::JoinSet` for fan-out Council sessions (all agents start simultaneously)
- `tokio::time::timeout` for inference call timeouts (30s limit per agent)
- `tokio::sync::mpsc` for the PRL ingest event channel (fire-and-forget ripple creation)
- `tokio::sync::Mutex` and `RwLock` for shared mutable state (session context, working memory cache)

**Key crates:**

```toml
[dependencies]
axum = { version = "0.7", features = ["ws", "macros"] }
tokio = { version = "1", features = ["full"] }
sqlx = { version = "0.7", features = ["postgres", "runtime-tokio-rustls", "uuid", "chrono"] }
redis = { version = "0.24", features = ["tokio-comp"] }  # DragonflyDB is Redis-compatible
reqwest = { version = "0.11", features = ["json", "stream"] }
chromiumoxide = "0.5"
serde = { version = "1", features = ["derive"] }
serde_json = "1"
uuid = { version = "1", features = ["v4", "serde"] }
ulid = "1"
governor = "0.6"  # Rate limiting
scraper = "0.18"  # HTML parsing
tokio-cron-scheduler = "0.10"
tracing = "0.1"
tracing-subscriber = "0.3"
sentry = "0.32"
```

## Chapter 1.2 — Frontend: Next.js 15 on Vercel

**Why Next.js 15:** App Router architecture with React Server Components for fast initial loads. Server-side rendering for SEO-sensitive pages (the landing page). Client-side rendering for the application shell. TypeScript throughout.

**Why Vercel:** Edge deployment closest to the user. Automatic preview deployments on every branch. Built-in performance monitoring. Zero configuration for Next.js deployment. The alternative (self-hosting Next.js on ECS) adds operational complexity for minimal cost savings at current scale.

**Frontend architecture decisions:**

- WebSocket connection managed as a singleton in a React context, shared across all components
- Zustand for application state (lighter than Redux for the data model complexity required)
- TanStack Query for server state (campaign data, foundation data, intel data) with optimistic updates
- Framer Motion for The Office animations (declarative animation system that handles the complex character animation states)
- Tailwind CSS for styling
- shadcn/ui for UI components (accessible, composable, zero runtime JavaScript overhead)

**The WebSocket client:** The WebSocket connection is established when the user authenticates. A custom hook `useRaptorSocket()` provides the connection state and message sending function. Incoming messages from the server are dispatched through a message router that updates the relevant Zustand store slices. The Office animation events arrive through this same WebSocket connection and are handled by the animation state manager.

## Chapter 1.3 — Primary Database: Aurora Serverless v2 (PostgreSQL 16)

**Why Aurora Serverless v2:** Three properties that match RaptorFlow's requirements exactly.

**Automatic scaling:** Aurora Serverless v2 scales Aurora Capacity Units (ACUs) automatically based on load. At 2 AM IST with no active users, it scales down to 0.5 ACUs (minimum). At 9 AM IST with 200 users simultaneously in active sessions, it scales up to handle the load. The scaling happens in milliseconds and is transparent to the application. For a product whose load is highly time-of-day dependent (Indian SMBs log in in the morning, not 24/7), serverless scaling eliminates the cost of paying for peak capacity during off-peak hours.

**PostgreSQL compatibility:** Full PostgreSQL 16 compatibility including pgvector for vector operations, row-level security for tenant isolation, tsvector for full-text search, JSONB for flexible document storage, and the full PostgreSQL extension ecosystem.

**Multi-AZ by default:** Aurora automatically replicates across multiple availability zones. Failover to a replica happens in under 30 seconds. For a product whose users depend on it for their morning briefing, the availability guarantee matters.

**Connection pooling:** Aurora Serverless v2 has a maximum connection limit (varies with ACU count). PgBouncer is deployed as a connection pooler in transaction pooling mode. The Rust application connects to PgBouncer, which manages a pool of connections to Aurora. This allows the application to handle many concurrent requests without exhausting the Aurora connection limit.

**Database configuration:**

```
Instance: Aurora PostgreSQL 16 Serverless v2
Min ACUs: 0.5 (scales down to this during off-peak)
Max ACUs: 16 (sufficient for ~2,000 concurrent users before needing to increase)
Region: ap-south-1 (Mumbai — closest to Indian user base)
Multi-AZ: enabled
Backup retention: 7 days
Performance Insights: enabled
```

## Chapter 1.4 — Vector Database: Qdrant

**Why a separate vector database:** At small scale, pgvector with IVFFlat index provides acceptable vector search performance. The limitation appears when applying filters before ANN search — pgvector's performance degrades significantly when the filter reduces the candidate set before the ANN traversal. Qdrant's HNSW implementation handles pre-filtered search efficiently through payload indexing, maintaining millisecond-range search latency regardless of filter selectivity.

**Qdrant configuration:**

- Self-hosted on ECS Fargate (same cluster as the main application) — not using Qdrant Cloud at launch to control costs
- Single collection: `ripples` with 64-dimensional vectors and payload filtering by {org_id, agent_id, scope, retention_band}
- HNSW parameters: m=16, ef_construction=128 (good balance of index quality and build time)
- Scalar quantization enabled (INT8) — reduces memory footprint by 4x with ~1% precision loss
- ef_search=128 for query time (high recall while maintaining <5ms latency)
- Persistent storage to an EFS volume mounted on the Fargate task

**Collection schema:**

```json
{
  "name": "ripples",
  "vectors": { "size": 64, "distance": "Cosine" },
  "payload_schema": {
    "org_id": "keyword",
    "agent_id": "keyword",
    "scope": "keyword",
    "hierarchy_level": "integer",
    "retention_band": "keyword",
    "salience": "float",
    "created_at": "datetime"
  }
}
```

## Chapter 1.5 — Cache and Pub/Sub: DragonflyDB

**Why DragonflyDB over Redis:** DragonflyDB is a Redis-compatible in-memory data store built from scratch for modern multi-core hardware. It uses a shared-nothing architecture that avoids the single-threaded bottleneck of Redis. At the throughput RaptorFlow requires — concurrent pub/sub from multiple agent streams, working memory cache reads for every inference call, Foundation cache lookups — DragonflyDB's multi-core utilisation produces materially lower latency than Redis at the same instance size.

The Redis compatibility means all existing Redis clients (including the Rust `redis` crate) work with DragonflyDB without modification.

**DragonflyDB usage patterns:**

Working memory cache (ZSET + HASH):

```
Key pattern: wm:{org_id}:{agent_id}
Type: Sorted Set (score = activation timestamp, member = ripple_id)
Size: Up to 50 members per set
Companion: hash ripple:{ripple_id} containing summary_text, emotion_vector, salience
TTL on companion hashes: 1 hour (refreshed on access)
```

Pub/sub channels for streaming:

```
council:{session_id}:{agent_id}     — individual agent streams
council:{session_id}:synthesis      — synthesis stream
muse:{session_id}                   — Muse response streams
office:{org_id}                     — office animation events
intel:{org_id}                      — intelligence alerts
nudge:{user_id}                     — user-specific nudges
```

Foundation cache:

```
Key: foundation:{org_id}
Type: Hash (field = section name, value = JSON content)
TTL: 1 hour (refreshed on Foundation update)
```

Distributed locks (for SWR consolidation):

```
Key: lock:consolidation:{org_id}
Type: String (value = lock holder identifier)
TTL: 35 minutes (auto-release if job crashes)
SET NX EX command
```

**DragonflyDB configuration:**

```
Instance: m5.large on EC2 in same VPC as ECS cluster
Memory: 8GB (sufficient for ~2,000 concurrent users' working memory caches)
Persistence: RDB snapshots every 5 minutes to S3 (for recovery from crash)
Multi-threading: enabled (uses all available cores)
```

## Chapter 1.6 — AI Inference: GCP API (Google Cloud)

**Why GCP API over OpenAI API:** Three reasons.

First, **the model portfolio**. Gemini 3.1 Pro and Flash-Lite provide the right capability tiers for RaptorFlow's 20/80 split. There is no comparable Flash-Lite equivalent in the OpenAI portfolio — the GPT-4o mini is capable but priced higher and without the reasoning variant required for Council sessions.

Second, **context caching**. GCP API's explicit context caching API allows Foundation content to be cached at the model level, reducing input token costs by 90% for repeated calls. No equivalent exists in the OpenAI API at launch.

Third, **regional availability**. GCP API has inference endpoints in the `asia-south1` region (Mumbai). Running inference close to the application server (also in Mumbai) reduces latency compared to routing all inference traffic through US-based OpenAI endpoints.

**GCP API integration:**
The GCP API authentication uses an API key stored in AWS Secrets Manager. The application authenticates using the API key at startup.

API endpoints:

- Streaming generation: `POST https://asia-south1-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/asia-south1/publishers/google/models/{MODEL_ID}:streamGenerateContent`
- Batch generation: `POST https://asia-south1-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/asia-south1/batchPredictionJobs`
- Context caching: `POST https://asia-south1-aiplatform.googleapis.com/v1beta1/projects/{PROJECT_ID}/locations/asia-south1/cachedContents`

**Model identifiers:**

```
Pro:                 gemini-2.0-pro-002
Flash-Lite Reasoning: gemini-2.0-flash-thinking-exp-01-21
Flash-Lite Normal:   gemini-2.0-flash-exp
```

(Use current stable model identifiers at build time — these change as Gemini versions update)

## Chapter 1.7 — Authentication: Clerk

Clerk handles all user authentication. The Axum backend validates Clerk JWTs on every request using the JWKS endpoint that Clerk provides. The validation is cached — the JWKS is fetched once and cached in DragonflyDB, refreshed every hour.

Clerk configuration:

- Email + password and Google OAuth enabled
- Organisation-level accounts (one org per business, multiple users per org supported post-v1)
- JWT template configured to include: org_id, user_id, email, display_name
- Webhook for user creation events (to trigger initial agent setup)

## Chapter 1.8 — Payments: Razorpay

Razorpay handles all Indian payment processing. The subscription model:

- Monthly billing at ₹5,000/month
- Razorpay subscription API for recurring payments
- 2-day grace period on payment failure before account suspension
- Webhook for payment success/failure events to update subscription_status in the users table

## Chapter 1.9 — Object Storage: AWS S3

Used for: competitor ad screenshots, user-uploaded assets from Foundation Screen 17, generated content exports, SWR overflow logs, and application backups.

Bucket structure:

```
raptorflow-prod/
  ├── intelligence/{org_id}/{competitor_id}/ads/{date}/
  ├── uploads/{org_id}/{foundation|assets}/
  ├── exports/{org_id}/{date}/
  └── backups/aurora/{date}/
```

## Chapter 1.10 — Queue: AWS SQS

Used for: PRL embedding queue (ripple_ids queued for async embedding generation), content pre-generation queue (scheduled content generation jobs), and intelligence pipeline job queue (each monitoring scan is a queued job).

Queue configuration:

- Standard queue (not FIFO — order does not matter for these use cases)
- Message retention: 4 days
- Visibility timeout: 5 minutes (time allowed for processing before message becomes visible again for retry)
- Dead letter queue: messages that fail processing 5 times go to the DLQ for manual inspection

## Chapter 1.11 — Monitoring: Sentry

Sentry provides:

- Error tracking for both Rust backend (using `sentry-rust`) and Next.js frontend (using `@sentry/nextjs`)
- Performance monitoring (distributed traces across Rust + Next.js)
- Session replay for frontend debugging

Custom Sentry context added to every error: org_id, session_id, agent_id (where applicable), inference_model, operation type. This context makes every error immediately actionable — the engineer looking at the Sentry dashboard can see exactly which org encountered the error and in which system context.

---

# Part Two: The Deployment Architecture

## Chapter 2.1 — AWS ECS Fargate

The Rust backend runs on AWS ECS Fargate in the ap-south-1 (Mumbai) region. Fargate is chosen over EC2 because: no server management required, per-task billing (pay only for what the application actually uses), automatic security patching of the underlying compute layer.

**Task definition:**

```json
{
  "family": "raptorflow-api",
  "cpu": "2048",
  "memory": "4096",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "containerDefinitions": [
    {
      "name": "api",
      "image": "YOUR_ECR_REPO/raptorflow-api:latest",
      "portMappings": [{ "containerPort": 8080, "protocol": "tcp" }],
      "environment": [
        { "name": "DATABASE_URL", "value": "FROM_SECRETS_MANAGER" },
        { "name": "DRAGONFLY_URL", "value": "FROM_SECRETS_MANAGER" },
        { "name": "QDRANT_URL", "value": "FROM_ENV" },
        { "name": "AWS_REGION", "value": "ap-south-1" }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/raptorflow-api",
          "awslogs-region": "ap-south-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

**Service configuration:**

- Desired count: 2 tasks (minimum 2 for high availability — if one task fails, the other serves traffic)
- Auto-scaling: based on CPU utilisation (scale up at 70%, scale down at 40%), minimum 2 tasks, maximum 10 tasks
- Load balancer: Application Load Balancer with sticky sessions (WebSocket connections need to route to the same task throughout the session)
- Health check: GET /health returning 200 within 5 seconds

**The Qdrant task:** Qdrant runs as a separate ECS Fargate service (not mixed into the API service). It uses an EFS volume mounted at /qdrant/storage for persistence. The API service communicates with Qdrant through the private VPC network.

## Chapter 2.2 — The Deployment Pipeline

```
Developer pushes to main branch
→ GitHub Actions workflow triggers
→ Runs: cargo test (unit tests), cargo clippy (linting)
→ If tests pass: builds Docker image
→ Pushes image to Amazon ECR
→ Updates ECS service with new task definition
→ ECS performs rolling deployment (new task starts, health check passes, old task stops)
→ Vercel automatically deploys frontend from same git push
→ Total deployment time: 4-8 minutes
```

**Environment strategy:**

- `main` branch → Production (ap-south-1)
- `develop` branch → Staging (same region, separate cluster and database)
- Feature branches → Preview deployments on Vercel only (no backend preview deployments)

**Database migrations:** Managed with `sqlx migrate`. Migrations run as a separate ECS task that runs before the API service update. If migration fails, the deployment is halted and the previous API version continues serving. Migration files are stored in `migrations/` directory in the repository.

## Chapter 2.3 — VPC and Network Architecture

All services run inside a single VPC in ap-south-1 with three availability zones.

**Subnet structure:**

```
Public subnets (one per AZ): ALB, NAT Gateways
Private subnets (one per AZ): ECS tasks, DragonflyDB, Qdrant, PgBouncer
Database subnets (one per AZ): Aurora instances
```

**Security groups:**

- ALB: inbound 443 from internet, outbound 8080 to ECS tasks
- ECS tasks: inbound 8080 from ALB only, outbound to Aurora (5432), DragonflyDB (6379), Qdrant (6333), internet (for Vertex AI API, PhonePe API, Clerk API, external URLs)
- Aurora: inbound 5432 from ECS tasks and PgBouncer only
- DragonflyDB: inbound 6379 from ECS tasks only
- Qdrant: inbound 6333 from ECS tasks only

**Internet access for ECS tasks:** ECS tasks in private subnets access the internet through NAT Gateways in the public subnets. This allows Vertex AI API calls, PhonePe webhooks, and web scraping (intelligence pipeline) without exposing the ECS tasks directly to the internet.

---

# Part Three: The Complete Economics

## Chapter 3.1 — Revenue Model

**Price:** ₹5,000/month per organisation (flat rate, no per-seat pricing at launch)

**Target market:** Indian SMBs with marketing budget and operational need for marketing intelligence

**Projected user cohort (Month 12):** 500 paying organisations

**Monthly revenue at 500 orgs:** ₹25,000,000 (~$300,000)

## Chapter 3.2 — Infrastructure Cost Per User Per Month

Breaking down every cost component at 500 users, in USD:

**Vertex AI Inference:**

| Operation                                            | Calls/user/month | Input tokens | Output tokens | Cost/user                   |
| ---------------------------------------------------- | ---------------- | ------------ | ------------- | --------------------------- |
| Foundation caching                                   | 1                | 4,000        | 0             | $0.0004 (10% cached rate)   |
| Council sessions                                     | ~30 total        | ~800 avg     | ~1,000 avg    | $0.024                      |
| Muse responses                                       | ~50              | ~2,000 avg   | ~800 avg      | $0.015                      |
| Content generation                                   | ~80              | ~1,500 avg   | ~1,200 avg    | $0.024                      |
| Daily Wins batch                                     | 30               | ~3,000       | ~500          | $0.003 (50% batch discount) |
| Background ops (ripple summaries, reflections, etc.) | ~500             | ~400 avg     | ~150 avg      | $0.013                      |
| **Total Vertex AI**                                  |                  |              |               | **~$0.079/user/month**      |

**Aurora Serverless v2:**
At 500 users, Aurora scales to approximately 1-2 ACUs during peak, 0.5 ACU off-peak. Estimated ACU-hours: 400/month × $0.12/ACU-hour = $48/month across all users = **$0.096/user/month**

**DragonflyDB (m5.large):**
$0.096/hour × 730 hours = $70/month ÷ 500 users = **$0.14/user/month**

**ECS Fargate (2 tasks baseline):**
2 tasks × 2 vCPU × 4GB × 730 hours: CPU cost = 2 × $0.04048 × 730 = $59, Memory = 2 × $0.004445 × 4 × 730 = $26. Total = $85/month ÷ 500 users = **$0.17/user/month**

**Qdrant ECS Fargate:**
1 task × 1 vCPU × 2GB × 730 hours = ~$40/month ÷ 500 users = **$0.08/user/month**

**S3:**
~10GB storage across all orgs + transfer = ~$5/month ÷ 500 = **$0.01/user/month**

**SQS:**
Approximately 2,000 messages/user/month × 500 users = 1M messages × $0.0000004 = $0.40/month total = **<$0.001/user/month**

**Data Transfer:**
ECS to internet (Vertex AI calls): ~2GB/user/month × 500 = 1,000GB × $0.085/GB = $85 ÷ 500 = **$0.17/user/month**

**Vercel (Pro plan):**
$20/month for Pro plan (adequate for <500 users) ÷ 500 = **$0.04/user/month**

**Clerk:**
$0.02/user/month at current pricing = **$0.02/user/month**

**Sentry (Team plan):**
$26/month ÷ 500 = **$0.05/user/month**

**Total infrastructure cost per user per month:**

| Component     | Cost (USD) | Cost (INR at 83x) |
| ------------- | ---------- | ----------------- |
| Vertex AI     | $0.079     | ₹6.56             |
| Aurora        | $0.096     | ₹7.97             |
| DragonflyDB   | $0.140     | ₹11.62            |
| ECS API       | $0.170     | ₹14.11            |
| ECS Qdrant    | $0.080     | ₹6.64             |
| S3            | $0.010     | ₹0.83             |
| Data Transfer | $0.170     | ₹14.11            |
| Vercel        | $0.040     | ₹3.32             |
| Clerk         | $0.020     | ₹1.66             |
| Sentry        | $0.050     | ₹4.15             |
| **Total**     | **$0.855** | **₹71**           |

**Revenue per user: ₹5,000**
**Infrastructure cost per user: ₹71**
**Infrastructure margin: 98.6%**

Even accounting for other operational costs (human support, payment processing fees, domain, tooling, contingency buffer), gross margin stays well above 80%.

## Chapter 3.3 — Unit Economics at Scale

The infrastructure cost per user decreases as scale increases:

- Aurora: serverless pricing means cost per user decreases as more users share the fixed ACU overhead at peak
- ECS: more users per task before auto-scaling triggers; each new task serves more users
- DragonflyDB: same instance serves more users as they are unlikely all active simultaneously
- Fixed costs (Vercel base, Sentry base, tooling) dilute across more users

Estimated infrastructure cost per user at 2,000 users: ~₹45 (marginal improvements as fixed costs dilute)
Estimated infrastructure cost per user at 10,000 users: ~₹30 (further improvements; may require Vertex AI committed use discounts)

The pricing headroom for growth investment, marketing, and team is substantial. At 500 users:

- Gross revenue: ₹25,000,000/month
- Infrastructure cost: ₹35,500/month (~₹71 × 500)
- Revenue after infrastructure: ₹24,964,500/month

---

# Part Four: Scaling Plan

## Chapter 4.1 — Current Architecture Limits

The current architecture handles approximately 2,000 concurrent users before any component reaches capacity constraints.

**The first bottleneck at scale: ECS task count.** At 2,000 concurrent users with active sessions, the 2-10 task auto-scaling range may be insufficient. The response: increase max_count to 20 tasks and monitor CPU utilisation. Rust's efficiency means each task handles significantly more concurrent users than a Python equivalent would.

**The second bottleneck: Aurora connections.** PgBouncer's transaction pooling allows many application connections to share a smaller pool of Aurora connections. At 2,000 users, verify PgBouncer pool_size is sufficient. Aurora Serverless scaling handles the compute side; connections are the constraint.

**The third bottleneck: DragonflyDB memory.** At 2,000 users, working memory cache (50 ripples × ~2KB × 21 agents × 2,000 users) = ~4.2GB. The m5.large instance has 8GB, so 2,000 users is near the limit. Response: upgrade to m5.xlarge (16GB) or implement working memory eviction more aggressively.

## Chapter 4.2 — The Path to 10,000 Users

Architectural changes required to serve 10,000 users:

**Multi-region deployment:** Indian users in tier-2 and tier-3 cities may experience higher latency to the Mumbai region. A second ECS cluster in a second Indian region (ap-south-2 when available, or ap-southeast-1 Singapore as a proxy) would reduce latency for these users.

**Aurora read replicas:** At high read load (analytics queries, Daily Wins generation, reporting), adding Aurora read replicas and routing read-heavy queries to replicas reduces load on the primary instance.

**DragonflyDB cluster mode:** At 10,000 users, DragonflyDB's single-instance configuration becomes a bottleneck. DragonflyDB's cluster mode shards data across multiple instances, allowing linear horizontal scaling.

**Qdrant scaling:** At 10,000 users with 6 months of average usage, the ripples collection contains approximately 600 million vectors (10,000 users × 60,000 ripples/user). Qdrant's horizontal scaling (multiple nodes with sharding) is required at this point.

**Vertex AI committed use:** At 10,000 users, monthly Vertex AI spend reaches the threshold where committed use discounts become significant. Negotiating a committed use agreement with Google Cloud would reduce per-token costs by 10-25%.

**Intelligence pipeline scaling:** At 10,000 users with average 5 competitors per user = 50,000 competitor entities to monitor. The scraping infrastructure needs to scale: more chromiumoxide instances, more IP rotation capacity, potentially distributed scraping across multiple ECS services.

## Chapter 4.3 — Multi-Tenancy Evolution (Adding org_id Layer)

The current architecture is single-user-to-org. The Foundation is one per org. The agents are one set per org. This works for the solo founder or small team where everyone shares the same marketing intelligence.

When organisational features are required — multiple users per org with different roles, different agents for different departments, department-specific foundations — the architecture evolves:

**What changes:** The org_id layer, which is already present in all tables as a column, becomes more meaningful. Role-based access control is added (using the Clerk organisation membership model). The Foundation becomes hierarchical: org-level Foundation that all agents share, plus department-level Foundations that specific agents and specific campaigns reference.

**What does not change:** The fundamental architecture. The PRL, EEL, Harness, and all feature logic are unchanged. The org_id already provides the tenant isolation. The new org features are additions to the existing structure, not restructuring of it.

**The middleware approach:** Rather than building multi-tenancy features into the core agent architecture, add an org middleware layer that runs before every inference call. The middleware assembles the org-level context (which Foundation variant applies to this user, which agents this user has access to, what campaigns are visible to this user) and injects it into the existing Harness pipeline. The Harness does not need to know about org structure.

---

# Part Five: Security

## Chapter 5.1 — Data Security Architecture

**Data in transit:** All traffic encrypted with TLS 1.3. The ALB terminates TLS from the internet. All inter-service communication within the VPC uses TLS (Aurora SSL, DragonflyDB TLS, Qdrant TLS over the VPC network).

**Data at rest:** Aurora encryption using AWS KMS (enabled by default). S3 server-side encryption with AWS KMS. DragonflyDB RDB snapshots stored in S3 with the same encryption.

**Tenant isolation:** Row Level Security in Aurora ensures that even application-level bugs cannot return data from one org to another. The RLS policy is enforced at the database level, not the application level. This is a defence-in-depth measure — application-level filtering is also applied, but RLS is the backstop.

**Secrets management:** All secrets (database credentials, Vertex AI service account key, PhonePe API key, Clerk JWT secret) stored in AWS Secrets Manager. The ECS task IAM role has permissions to read specific secrets. No secrets in environment variables, Git repositories, or application logs.

**Foundation data:** The Foundation is the most sensitive data in the system — it contains detailed competitive strategy and business positioning. It is stored in Aurora with RLS protection and is never logged to CloudWatch, Sentry, or any external system.

**PRL data:** Ripple content — which includes competitive intelligence, user conversation content, and business performance data — is stored in Aurora with RLS and in Qdrant with per-org payload filtering. It is not shared across org boundaries under any circumstances.

## Chapter 5.2 — The Scraping Legal Posture

The intelligence pipeline's web scraping activity raises legal and terms-of-service questions that must be addressed proactively.

**Public data principle:** All scraped data is publicly accessible without authentication. The intelligence pipeline does not scrape content behind login walls, does not extract private data, and does not access content that requires a user account to view. Competitor websites, public social media posts, and public ad libraries are all public data.

**Robots.txt compliance:** The scraping infrastructure checks and respects robots.txt for non-critical URLs. For competitor website monitoring (the core competitive intelligence function), the decision is made to proceed despite robots.txt restrictions, based on the established legal principle in multiple jurisdictions that publicly accessible data collection for business analysis is generally permissible regardless of robots.txt.

**Rate limiting and server respect:** The governor crate enforces rate limits that prevent the scraping from placing meaningful load on any competitor's servers. Maximum 1 request per 5 minutes per domain for the monitoring functions. This is consistent with the rate of a human researcher checking a website periodically.

**Data use:** The scraped data is used exclusively within the org that generated it. Competitor intelligence gathered for Org A is not shared with Org B, not used for any system-level training, and not visible outside the specific org context.

---

# Part Six: Operational Runbook

## Chapter 6.1 — The Monitoring Dashboard

CloudWatch dashboard components:

**Application health:** ECS task count and health, ALB request count and latency (P50/P99), ECS task CPU and memory utilisation, error rate from Sentry integration.

**Database health:** Aurora ACU utilisation, connection count, query latency (P99), replication lag.

**Cache health:** DragonflyDB memory utilisation, hit rate for working memory cache lookups, pub/sub message delivery rate.

**Inference health:** Vertex AI API call success rate, latency by model tier, token usage by model tier, daily cost tracking (alert if daily spend exceeds budget).

**Intelligence pipeline health:** Monitoring job completion rate by job type, scraping success rate, competitor update frequency, embedding queue depth.

**Business metrics:** Active users (daily/weekly/monthly), Council sessions per day, content pieces generated per day, Daily Wins briefings generated successfully, Nudges delivered.

## Chapter 6.2 — Key Alerts

**P1 Alerts (immediate response required):**

- ECS task count drops below 1 (complete service outage)
- Aurora connection to primary fails
- DragonflyDB OOM (out of memory)
- Vertex AI API returning 5xx errors (inference unavailable)
- Daily Wins generation job fails for more than 20% of orgs

**P2 Alerts (response within 1 hour):**

- ECS CPU utilisation above 80% for more than 10 minutes
- Aurora ACU at maximum for more than 30 minutes
- Embedding queue depth above 1,000
- Sentry error rate above 1% of requests
- Qdrant storage utilisation above 80%

**P3 Alerts (response within 24 hours):**

- Intelligence pipeline job completion rate below 90%
- Daily Wins action rate (users clicking recommended actions) drops significantly below baseline
- Council session P99 latency above 15 seconds

## Chapter 6.3 — Common Operational Procedures

**Deploy a backend update:**

```bash
# Build and push the Docker image
docker build -t raptorflow-api .
docker tag raptorflow-api:latest YOUR_ECR_REPO/raptorflow-api:latest
docker push YOUR_ECR_REPO/raptorflow-api:latest

# Update the ECS service (runs migration first via ECS one-off task)
aws ecs run-task --cluster raptorflow-prod --task-definition raptorflow-migrate
aws ecs update-service --cluster raptorflow-prod --service raptorflow-api --force-new-deployment
```

**Roll back a backend update:**

```bash
# Update service to use the previous task definition revision
aws ecs update-service --cluster raptorflow-prod --service raptorflow-api \
  --task-definition raptorflow-api:PREVIOUS_REVISION
```

**Manually trigger Daily Wins for a specific org:**

```bash
# Run the Daily Wins job for a specific org via one-off ECS task
aws ecs run-task --cluster raptorflow-prod \
  --task-definition raptorflow-jobs \
  --overrides '{"containerOverrides":[{"name":"jobs","command":["daily-wins","--org-id","ORG_ID"]}]}'
```

**Check SWR consolidation status:**

```bash
# Query Aurora for consolidation status
psql $DATABASE_URL -c "SELECT org_id, last_consolidation_at, next_consolidation_at FROM orgs ORDER BY last_consolidation_at ASC LIMIT 20;"
```

**Clear DragonflyDB working memory for an org (after EEL reset):**

```bash
redis-cli -u $DRAGONFLY_URL --scan --pattern "wm:ORG_ID:*" | xargs redis-cli -u $DRAGONFLY_URL DEL
```

---

# Closing: The Machine Serves the Mission

The architecture described in this volume is not the most sophisticated architecture that could be built. It is the most appropriate architecture for the mission: delivering enterprise-grade marketing intelligence to Indian SMBs at ₹5,000/month with strong unit economics and a clear path to scale.

Every technology choice — Rust for latency and cost, Aurora Serverless for flexible scaling, Qdrant for vector search quality, DragonflyDB for pub/sub throughput, Vertex AI for model quality and context caching — is justified not by technical trend but by specific product requirements.

The product is designed to get better over time. So is the infrastructure. The architecture that serves 500 users well today is designed to evolve naturally to serve 10,000 users with identifiable, incremental changes rather than a complete rebuild.

Build the machine. Run the machine. Let the machine prove the value. Then scale the machine to serve everyone who deserves it.

---

_End of Volume 12. End of the RaptorFlow Master Document Series._

_Volumes 1-12 constitute the complete specification for RaptorFlow v1.0. The system described herein is sufficient to build a production-ready product that delivers genuine enterprise-grade marketing intelligence to Indian SMBs at ₹5,000/month. Build it._
