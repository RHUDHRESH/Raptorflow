# RAPTORFLOW COMPLETE BACKEND SPECIFICATION

> **Version 6.0** | **Production-Ready Implementation Plan**

---

## DOCUMENT INDEX

### PART I: AGENT INTELLIGENCE SYSTEM
| Doc | File | Description |
|-----|------|-------------|
| 01 | `01_ROUTING_ARCHITECTURE.md` | Semantic, HLK, Intent routing systems |
| 02 | `02_MEMORY_SYSTEMS.md` | Vector, Graph, Hybrid memory + compression |
| 03 | `03_COGNITIVE_ENGINE.md` | Planning, reflection, reasoning |
| 04 | `04_SKILL_SYSTEM.md` | Skill cards, execution, storage |
| 05 | `05_AGENT_DEFINITIONS.md` | Every agent with full specifications |

### PART II: CORE INFRASTRUCTURE
| Doc | File | Description |
|-----|------|-------------|
| 06 | `06_AUTHENTICATION.md` | Supabase Auth, JWT, session isolation |
| 07 | `07_DATABASE_SCHEMA.md` | PostgreSQL + RLS for multi-tenancy |
| 08 | `08_REDIS_ARCHITECTURE.md` | Sessions, cache, rate limiting, queues |
| 09 | `09_PAYMENTS.md` | PhonePe integration, GST, invoicing |

### PART III: API & INITIALIZATION
| Doc | File | Description |
|-----|------|-------------|
| 10 | `10_API_SPECIFICATION.md` | Complete REST API with auth flows |
| 11 | `11_INITIALIZATION_SEQUENCES.md` | User signup → first session flow |
| 12 | `12_DEPLOYMENT.md` | GCP, Docker, CI/CD |

---

## ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND (Vercel)                              │
│                         Next.js 14 + Supabase Auth                          │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │ JWT Token
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           API GATEWAY (FastAPI)                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Auth Guard  │  │ Rate Limit  │  │ Budget Check│  │ RLS Inject  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │
┌─────────────────────────────────────▼───────────────────────────────────────┐
│                          COGNITIVE CORE                                     │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      PERCEPTION MODULE                               │   │
│  │   Intent Classification → Entity Extraction → Context Assembly      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                      │                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      ROUTING ENGINE                                  │   │
│  │   Semantic Router → HLK Router → Intent Router → Skill Matcher      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                      │                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      PLANNING MODULE                                 │   │
│  │   Task Decomposition → Dependency Graph → Execution Plan            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                      │                                      │
│  ┌───────────────────────────────────▼─────────────────────────────────┐   │
│  │                      AGENT SWARM                                     │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │   │
│  │  │ Onboarding  │ │   Moves     │ │  Campaigns  │ │   BlackBox  │   │   │
│  │  │   Swarm     │ │   Agent     │ │   Agent     │ │   Agent     │   │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘   │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │   │
│  │  │    Muse     │ │ Daily Wins  │ │  Analytics  │ │  Foundation │   │   │
│  │  │   Agent     │ │   Agent     │ │   Agent     │ │   Agent     │   │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                      │                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      REFLECTION MODULE                               │   │
│  │   Output Validation → Quality Check → Self-Correction Loop          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                      │                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      HUMAN-IN-THE-LOOP                               │   │
│  │   Approval Gates → Feedback Collection → Preference Learning        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │
        ┌─────────────────────────────┼─────────────────────────────┐
        │                             │                             │
        ▼                             ▼                             ▼
┌───────────────┐          ┌───────────────┐          ┌───────────────┐
│   MEMORY      │          │    SKILLS     │          │    TOOLS      │
│   SYSTEM      │          │    SYSTEM     │          │    SYSTEM     │
│               │          │               │          │               │
│ ┌───────────┐ │          │ ┌───────────┐ │          │ ┌───────────┐ │
│ │  Vector   │ │          │ │  Skill    │ │          │ │  Search   │ │
│ │  Store    │ │          │ │  Cards    │ │          │ │  Tools    │ │
│ │ (pgvector)│ │          │ │ (YAML+MD) │ │          │ └───────────┘ │
│ └───────────┘ │          │ └───────────┘ │          │ ┌───────────┐ │
│ ┌───────────┐ │          │ ┌───────────┐ │          │ │  Scraper  │ │
│ │  Graph    │ │          │ │  Skill    │ │          │ │  Tools    │ │
│ │  Store    │ │          │ │ Executor  │ │          │ └───────────┘ │
│ │ (Neo4j/PG)│ │          │ └───────────┘ │          │ ┌───────────┐ │
│ └───────────┘ │          │ ┌───────────┐ │          │ │  Indian   │ │
│ ┌───────────┐ │          │ │  Skill    │ │          │ │  Market   │ │
│ │ Episodic  │ │          │ │ Registry  │ │          │ └───────────┘ │
│ │  Memory   │ │          │ └───────────┘ │          │ ┌───────────┐ │
│ └───────────┘ │          │               │          │ │  Database │ │
│ ┌───────────┐ │          │               │          │ │  Tools    │ │
│ │ Working   │ │          │               │          │ └───────────┘ │
│ │  Memory   │ │          │               │          │               │
│ └───────────┘ │          │               │          │               │
└───────────────┘          └───────────────┘          └───────────────┘
        │                             │                             │
        └─────────────────────────────┼─────────────────────────────┘
                                      │
┌─────────────────────────────────────▼───────────────────────────────────────┐
│                          DATA LAYER                                         │
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │    Supabase     │  │     Upstash     │  │   Vertex AI     │             │
│  │   PostgreSQL    │  │      Redis      │  │    Gemini       │             │
│  │   + pgvector    │  │                 │  │                 │             │
│  │   + RLS         │  │  - Sessions     │  │  - Flash-Lite   │             │
│  │                 │  │  - Cache        │  │  - Flash        │             │
│  │  - Users        │  │  - Rate Limit   │  │  - Pro          │             │
│  │  - Workspaces   │  │  - Queues       │  │                 │             │
│  │  - Foundations  │  │  - Pub/Sub      │  │                 │             │
│  │  - ICPs         │  │                 │  │                 │             │
│  │  - Moves        │  │                 │  │                 │             │
│  │  - Campaigns    │  │                 │  │                 │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐                                  │
│  │   GCS Storage   │  │    PhonePe      │                                  │
│  │                 │  │   Payments      │                                  │
│  │  - File uploads │  │                 │                                  │
│  │  - PDFs         │  │  - UPI          │                                  │
│  │  - Images       │  │  - Cards        │                                  │
│  │  - Exports      │  │  - Subscriptions│                                  │
│  └─────────────────┘  └─────────────────┘                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## CRITICAL USER ISOLATION PROBLEM

**Current Issue**: Users see everyone's data instead of their own.

**Root Cause**: Missing workspace-scoped queries + RLS not enforced.

**Solution** (covered in detail in docs 06, 07):
1. Every query MUST include `workspace_id` filter
2. RLS policies enforce isolation at DB level
3. JWT contains `user_id` which maps to `workspace_id`
4. Middleware injects workspace context into every request

```python
# EVERY database query must be scoped
# WRONG:
result = supabase.table("moves").select("*").execute()

# CORRECT:
result = supabase.table("moves").select("*").eq("workspace_id", user.workspace_id).execute()
```

---

## TECHNOLOGY STACK

| Layer | Technology | Purpose |
|-------|------------|---------|
| Frontend | Next.js 14 + Vercel | UI + SSR |
| Auth | Supabase Auth | JWT, OAuth, Magic Link |
| Database | Supabase PostgreSQL | Primary data store |
| Vector DB | pgvector extension | Embeddings |
| Graph DB | PostgreSQL (ltree/adjacency) | Knowledge graph |
| Cache | Upstash Redis | Sessions, cache, queues |
| LLM | Vertex AI (Gemini) | All inference |
| Payments | PhonePe | UPI, Cards, Subscriptions |
| Storage | GCP Cloud Storage | File uploads |
| Backend | FastAPI + Cloud Run | API layer |
| Agent Framework | LangGraph | Orchestration |
