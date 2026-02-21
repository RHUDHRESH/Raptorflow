# RAPTORFLOW — EXHAUSTIVE TECHNICAL CONTEXT DOCUMENT

## PART 1: PRODUCT PHILOSOPHY & ARCHITECTURE OVERVIEW

**File:** `.sisyphus/docs/PART_1_Philosophy_Architecture.md`
**Lines:** ~750

---

## 1.1 WHAT RAPTORFLOW IS

RaptorFlow is an AI-powered "Marketing Employee" SaaS platform that represents a fundamental shift in how marketing work gets done. Rather than being a tool that requires constant configuration and manual operation, RaptorFlow functions as a delegation interface where users hire an AI "employee" to handle the day-to-day marketing work autonomously. The core philosophy is that marketing should scale through delegation rather than configuration.

When users first sign up for RaptorFlow, they go through a comprehensive 21-step onboarding process that teaches the AI everything about their business: who they are, what they sell, who their customers are, what makes them different, and what rules they need to follow. This onboarding data feeds into the Business Context Manifest (BCM), which serves as the AI's "brain" - everything it needs to make intelligent marketing decisions without asking the user for guidance on every single piece of content.

Once onboarding is complete, the platform operates autonomously indefinitely. The AI creates marketing content (called "Moves"), organizes them into strategic initiatives (called "Campaigns"), schedules them for optimal publishing times, tracks their performance, and continuously optimizes based on results. The user provides high-level direction and strategic goals, but the day-to-day execution happens automatically.

This is fundamentally different from traditional marketing tools. Buffer, Hootsuite, and similar scheduling tools require users to manually create every piece of content and decide when to publish. Marketing automation platforms like HubSpot require users to build complex workflows with triggers and conditions. Even AI content generators like Jasper or Copy.ai produce content on-demand but don't actually do the ongoing work of marketing. RaptorFlow is the first platform that actually does the marketing job - not just helps humans do it faster.

The platform generates millions of dollars in value for users by eliminating the need for dedicated marketing operations staff. A single marketing employee costs $60,000-$150,000 annually plus benefits and overhead. RaptorFlow costs a fraction of that while working 24/7/365 without vacation, sick days, or turnover. The ROI calculation is straightforward: one employee or contractor can be replaced or augmented by RaptorFlow's autonomous marketing capabilities.

---

## 1.2 WHAT RAPTORFLOW IS NOT

Understanding what RaptorFlow is not helps clarify its unique position in the market. RaptorFlow is explicitly not any of the following categories of tools:

**Not a Social Media Scheduler:** Tools like Buffer, Hootsuite, Sprout Social, and Later are essentially calendars for manually-created posts. They help users organize content but don't create it. Users still need to write every caption, design every graphic, and decide what to post when. RaptorFlow does all of this automatically.

**Not a Content Template System:** Many marketing tools offer templates for common content types - email templates, social post templates, blog outlines. These reduce some friction but still require humans to fill in the blanks with original content. RaptorFlow generates completely original content tailored to the business.

**Not a Campaign Management Dashboard:** Platforms like Marketo, Pardot, or Salesforce Marketing Cloud help humans manage complex marketing workflows with lead scoring, drip campaigns, and analytics. They are configuration-heavy and require expert setup. RaptorFlow's Campaigns are AI-generated strategic initiatives, not human-configured workflows.

**Not an Analytics Dashboard:** Tools like Google Analytics, Mixpanel, or Amplitude show what happened in the past. They're useful for reporting but don't take action. RaptorFlow both acts (creates and publishes content) and reports (tracks performance).

**Not a Content Repurposing Tool:** Some AI tools take one piece of content and adapt it for different platforms. This is useful but limited. RaptorFlow creates content from scratch based on strategy, not just repurposes existing content.

**Not a Simple Chatbot:** While some platforms offer "AI marketing assistants" that respond to prompts, these are tools that wait to be used. RaptorFlow is proactive - it generates content on its own based on goals and strategy, without waiting for user commands.

---

## 1.3 THE DELEGATION MODEL VS CONFIGURATION MODEL

The fundamental architectural choice that drives RaptorFlow is the delegation model versus the configuration model. Understanding this distinction explains why the platform works the way it does.

**The Configuration Model** is how virtually all marketing software works today. Users configure every detail of their marketing:

- Every social post needs written copy
- Every email needs a subject line and body
- Every blog post needs an outline and content
- Every ad needs creative and targeting
- Every campaign needs timing and sequencing
- Every workflow needs triggers and conditions

This creates massive friction. The more marketing you do, the more configuration is required. Marketing teams scale by adding more humans to do more configuration. This is why marketing budgets are dominated by headcount - the work is inherently manual.

**The Delegation Model** inverts this relationship. Instead of configuring every piece of marketing, users delegate outcomes to the AI:

- "Drive more leads this month" - the AI decides what content to create
- "Build thought leadership" - the AI determines topics and publishes
- "Launch our new product" - the AI coordinates the entire campaign
- "Improve engagement" - the AI tests and optimizes

The AI doesn't wait to be told what to do. It has the context (BCM) to make decisions and the capability (Muse) to execute. The human's role shifts from content creator to strategic director - setting goals, reviewing results, providing feedback that improves the AI over time.

This model requires more upfront investment - the 21-step onboarding takes 30-60 minutes to complete. But the payoff is massive: once the AI understands the business, it can produce unlimited marketing without further human effort. The ROI compounds over time as the AI learns and improves.

The configuration model hits a ceiling at the limits of human bandwidth. The delegation model scales infinitely because the AI can work continuously in parallel. A marketing team of one person plus RaptorFlow can outperform teams of ten using traditional tools.

---

## 1.4 THE "MARKETING EMPLOYEE" METAPHOR

RaptorFlow is architected around treating the AI as a literal employee. This isn't just marketing speak - it drives actual technical decisions. Every component of the system has a corresponding real-world employee analogy:

**Onboarding as Job Training:** When a company hires a new marketing employee, they spend weeks or months learning the business: products, customers, competitors, messaging, processes. The 21-step onboarding in RaptorFlow serves exactly this purpose. Each question teaches the AI about a different aspect of the business. Skip onboarding and the AI is useless - just like hiring an employee and never training them.

**BCM as Institutional Memory:** When employees join a company, they learn from documentation, mentors, and experience. This knowledge lives in their heads and gets lost when they leave. The Business Context Manifest is the AI's permanent memory - everything it needs to do its job effectively, always available, never forgotten. When the BCM is updated, it's like the employee going through additional training.

**Moves as Daily Work:** Marketing employees produce tangible work products - social posts, emails, blog articles, ad campaigns. These are their "deliverables." Moves are exactly this - the discrete units of work the AI produces. Each Move has a purpose, goes through creation and review, gets scheduled, gets published, and gets measured.

**Campaigns as Projects:** Employees don't just produce random work - they work on projects with defined objectives, timelines, and stakeholders. Campaigns are these projects in RaptorFlow. A product launch is a campaign. A thought leadership initiative is a campaign. A lead nurture sequence is a campaign. Each campaign has a goal, a timeline, and multiple individual work products (Moves) that contribute to it.

**Daily Wins as Daily Standups:** In agile teams, daily standups answer "what should I work on today?" Daily Wins answers the same question for the AI marketing employee. Every morning, the system recommends the highest-impact actions for that specific day based on current context. The user can approve, skip, or modify - just like a manager directing priorities.

**Muse as The Employee:** Muse is the AI orchestration engine that actually does the work. It's not a single AI call - it's a complex system with multiple agents (strategist, copywriter, editor), quality gates, and learning mechanisms. This complexity is necessary because marketing is genuinely complex. Just as a human employee has multiple skills and workflows, Muse has multiple AI agents working together.

**Performance Reviews as Analytics:** Human employees get performance reviews - periodic assessments of how well they're doing. Analytics in RaptorFlow serve exactly this purpose. Every Move tracks impressions, clicks, engagements, conversions. Every Campaign tracks progress toward goals. The AI gets "reviewed" continuously and adjusts behavior based on what performs well.

**Feedback as Learning:** When humans make mistakes, they receive feedback and improve. The Reflection Engine captures feedback from users on Move quality and feeds it back into the BCM to improve future output. This is continuous learning - the AI gets better at marketing for that specific business over time.

---

## 1.5 THE BUSINESS CONTEXT MANIFEST (BCM) - THE NERVOUS SYSTEM

The Business Context Manifest is the most important data structure in RaptorFlow. It is the single source of truth about a business that enables AI to generate relevant, personalized marketing content. Without the BCM, the system cannot function - this is enforced by the `ENFORCE_BCM_READY_GATE` setting.

The BCM contains all information needed for marketing decision-making:

**Company Foundation:** Basic identifying information - company name, website URL, industry classification, business stage (pre-seed through enterprise), and a detailed description of what the company does and why it exists. This establishes the entity being marketed.

**Ideal Customer Profiles (ICPs):** Detailed personas describing target customers. Each ICP includes demographics (role, seniority, company size), psychographics (motivations, fears, values), specific pain points they experience, goals they're trying to achieve, and triggers that cause them to take action. Multiple ICPs can be defined to target different segments.

**Competitive Positioning:** Who the competitors are (both direct and indirect), what makes this company different (unique differentiators), and what category the company occupies in the market. This enables the AI to write competitive positioning content.

**Messaging Framework:** The brand voice (how the company sounds), specific tone descriptors, the main value proposition, proof points that establish credibility, guardrails (what not to say), and specific phrases to use or avoid. This ensures all content maintains brand consistency.

**Channel Strategy:** Which marketing channels are priorities (primary, secondary, experimental), what content formats work best on each, and posting frequency preferences. This guides channel selection for different types of content.

**Market Context:** Geographic focus (which regions to target), pricing model (affects how marketing talks about value), and acquisition goals (what the business is trying to achieve). This aligns content with business objectives.

The BCM is not static. It evolves through several mechanisms:

**Onboarding Creation:** Initially built from the 21-step onboarding process where users provide all foundational information.

**AI Synthesis:** The raw onboarding data is processed by Muse to create enriched, structured content - voice archetypes, ICP voice adaptations, content templates, guardrail patterns.

**User Feedback Loop:** When users provide feedback on Moves (ratings, comments, edits), the Reflection Engine analyzes patterns and proposes BCM refinements.

**Manual Updates:** Users can directly edit foundation information, add new competitors, adjust messaging, or modify guardrails through the settings interface.

Every piece of content generated by RaptorFlow flows through the BCM. The generation prompt includes relevant BCM sections as context. Without this context, the AI would produce generic, meaningless content. With it, the AI writes as if it deeply understands the business - because it does.

---

## 1.6 HOW MOVES AND CAMPAIGNS DIFFER FROM TRADITIONAL MARKETING TOOLS

The concepts of Moves and Campaigns are unique to RaptorFlow and represent a fundamentally different approach to marketing execution.

**Moves vs Traditional Content:**

Traditional marketing tools treat "content" as a standalone artifact - a social post exists in isolation, an email is its own entity, a blog article is separate from everything else. There's no inherent connection between pieces of content. Users must manually track what they've posted, when, and how it performed.

Moves in RaptorFlow are fundamentally different:

Every Move is created with strategic intent. When generating a Move, users specify a category (ignite, capture, authority, repair, rally) that maps to a strategic purpose. A "capture" Move is explicitly designed for lead generation. An "authority" Move is designed for thought leadership. The AI tailors content accordingly.

Every Move is connected to the BCM. The content isn't just created in a vacuum - it's informed by the company's positioning, written in the brand voice, targeted to specific ICPs, and follows all guardrails. It's like having the marketing team's institutional knowledge built into every piece of content.

Every Move is measurable. Each Move tracks engagement metrics (impressions, clicks, engagements) and can be linked to business outcomes (leads, conversions, revenue). Performance data flows back to inform future Move generation.

Every Move can exist independently or as part of a Campaign. A single Move might be a tactical response to something in the market. Multiple Moves organized together form a Campaign with shared goals and timeline.

**Campaigns vs Traditional Campaign Management:**

Traditional campaign tools (Marketo, Salesforce Campaigns, Pardot) treat campaigns as containers for manually-configured workflows. Users define segments, build email sequences, set up lead scoring rules, create landing pages - all through configuration. The "campaign" is essentially a label that groups these configurations together.

RaptorFlow Campaigns are fundamentally different:

Campaigns are AI-generated execution plans. Users define strategic parameters (goal, audience, timeline, channels) but don't manually build workflows. Muse analyzes the requirements and proposes a complete Move calendar - what to create, when to publish, on which channels, targeting which audiences.

Campaigns adapt dynamically. Traditional campaigns are static once launched - the same sequence runs until manually changed. RaptorFlow Campaigns continuously optimize based on performance. If certain Moves aren't performing, the AI adjusts the approach.

Campaigns have built-in intelligence. Rather than relying on humans to optimize, Campaigns track progress toward goals and automatically adjust content strategy. A Campaign with a lead generation goal tracks SQLs generated and shifts content toward higher-converting approaches.

Campaigns cascade status changes. When a Campaign is paused, all its scheduled Moves pause. When resumed, they resume. When completed, the Campaign closes out with full analytics. This organizational hierarchy provides management without manual intervention.

---

## 1.7 FULL SYSTEM ARCHITECTURE DIAGRAM

The RaptorFlow system consists of multiple layers working together to deliver autonomous marketing:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CLIENT LAYER (Next.js 14)                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌────────────────────────────────────────────────────────────────────┐   │
│   │                    FRONTEND COMPONENTS                              │   │
│   ├────────────────────────────────────────────────────────────────────┤   │
│   │  Pages: Dashboard | Moves | Campaigns | Settings | Onboarding      │   │
│   │  Components: MoveEditor | CampaignBuilder | Calendar | DailyWins   │   │
│   │  UI Library: Button | Card | Input | Modal | Calendar | Charts     │   │
│   └────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   ┌────────────────────────────────────────────────────────────────────┐   │
│   │                    STATE MANAGEMENT (Zustand)                     │   │
│   ├────────────────────────────────────────────────────────────────────┤   │
│   │  foundationStore | movesStore | campaignStore | bcmStore          │   │
│   │  workspaceStore | uiStore | dailyWinsStore                        │   │
│   └────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   ┌────────────────────────────────────────────────────────────────────┐   │
│   │                    SERVICES LAYER                                   │   │
│   ├────────────────────────────────────────────────────────────────────┤   │
│   │  movesService | campaignsService | bcmService | foundationService │   │
│   └────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                         HTTPS / WebSocket
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         API GATEWAY (Nginx)                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌────────────────────────────────────────────────────────────────────┐   │
│   │                    REVERSE PROXY & SSL                              │   │
│   ├────────────────────────────────────────────────────────────────────┤   │
│   │  - SSL/TLS Termination                                             │   │
│   │  - Request Routing (Frontend → Vercel, API → Backend)             │   │
│   │  - Rate Limiting (60 req/min per workspace)                       │   │
│   │  - Static Asset Caching                                           │   │
│   │  - Load Balancing                                                 │   │
│   └────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                         Internal API Calls
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      BACKEND SERVICES (FastAPI)                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌────────────────────────────────────────────────────────────────────┐   │
│   │                    API ROUTES (v1)                                │   │
│   ├────────────────────────────────────────────────────────────────────┤   │
│   │  /api/v1/workspaces/*    - Workspace CRUD, onboarding            │   │
│   │  /api/v1/moves/*         - Move CRUD, generation, scheduling     │   │
│   │  /api/v1/campaigns/*    - Campaign CRUD, move generation        │   │
│   │  /api/v1/context/*      - BCM operations, synthesis              │   │
│   │  /api/v1/ai/*           - AI generation endpoints                │   │
│   │  /api/v1/foundation/*   - Foundation data management             │   │
│   │  /api/v1/daily-wins/*   - Daily recommendations                  │   │
│   │  /api/v1/analytics/*   - Metrics and reporting                   │   │
│   └────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   ┌────────────────────────────────────────────────────────────────────┐   │
│   │                    SERVICE LAYER                                   │   │
│   ├────────────────────────────────────────────────────────────────────┤   │
│   │  MoveService        - Move CRUD, versioning, feedback             │   │
│   │  CampaignService    - Campaign CRUD, move calendar                 │   │
│   │  BCMService         - BCM CRUD, synthesis, versioning              │   │
│   │  MuseService        - AI content generation orchestration           │   │
│   │  FoundationService  - Company data management                     │   │
│   │  AnalyticsService   - Metrics aggregation and reporting            │   │
│   │  DailyWinsService   - Recommendation generation                    │   │
│   └────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   ┌────────────────────────────────────────────────────────────────────┐   │
│   │                    AI ORCHESTRATION (LangGraph)                    │   │
│   ├────────────────────────────────────────────────────────────────────┤   │
│   │                                                                       │   │
│   │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │   │
│   │   │   Single    │  │   Council   │  │   Swarm    │                 │   │
│   │   │    Agent    │  │    Mode    │  │    Mode    │                 │   │
│   │   │   Mode      │  │ (3 agents) │  │  (parallel)│                 │   │
│   │   └─────────────┘  └─────────────┘  └─────────────┘                 │   │
│   │                                                                       │   │
│   │   ┌─────────────────────────────────────────────────────────────┐    │   │
│   │   │              LangGraph State Machine                       │    │   │
│   │   │  fetch_bcm → select_mode → build_prompt → generate →     │    │   │
│   │   │  score → store_result                                      │    │   │
│   │   └─────────────────────────────────────────────────────────────┘    │   │
│   │                                                                       │   │
│   └────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
           ┌──────────────────────────┼──────────────────────────┐
           ▼                          ▼                          ▼
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│   SUPABASE          │  │   UPSTASH REDIS    │  │   VERTEX AI        │
│   (PostgreSQL)      │  │   (Cache/Queue)   │  │   (Gemini Pro)     │
├─────────────────────┤  ├─────────────────────┤  ├─────────────────────┤
│                     │  │                     │  │                     │
│  Tables:            │  │  Keys:              │  │  Models:            │
│  - workspaces       │  │  - bcm:{workspace} │  │  - gemini-2.0-flash│
│  - workspace_members│  │  - moves:list:{id} │  │  - gemini-1.5-pro  │
│  - users            │  │  - daily_wins:{id} │  │                     │
│  - foundations      │  │  - rate_limit:{w}  │  │  Used for:         │
│  - bcm_versions     │  │                     │  │  - Content gen      │
│  - moves            │  │  TTLs:              │  │  - Reasoning        │
│  - move_versions   │  │  - 24h (BCM)        │  │  - Synthesis       │
│  - move_feedback   │  │  - 5min (lists)     │  │                     │
│  - move_schedule   │  │  - 1min (ratelimit) │  │                     │
│  - move_analytics  │  │                     │  │                     │
│  - campaigns       │  │                     │  │                     │
│  - campaign_moves  │  │                     │  │                     │
│  - daily_wins      │  │                     │  │                     │
│  - integrations    │  │                     │  │                     │
│                     │  │                     │  │                     │
│  Features:         │  │                     │  │                     │
│  - Row Level Sec  │  │                     │  │                     │
│  - Realtime Sub   │  │                     │  │                     │
│  - Auth           │  │                     │  │                     │
│  - Storage (files)│  │                     │  │                     │
└─────────────────────┘  └─────────────────────┘  └─────────────────────┘

                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      INFRASTRUCTURE LAYER                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌────────────────────────────────────────────────────────────────────┐   │
│   │                    DEPLOYMENT PLATFORMS                            │   │
│   ├────────────────────────────────────────────────────────────────────┤   │
│   │  Frontend:    Vercel (automatic deployments, edge network)        │   │
│   │  Backend:     Docker on cloud host (AWS/GCP/Custom)              │   │
│   │  Database:    Supabase (managed PostgreSQL)                      │   │
│   │  Cache:       Upstash (serverless Redis)                          │   │
│   │  AI:          Google Cloud Vertex AI                              │   │
│   └────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   ┌────────────────────────────────────────────────────────────────────┐   │
│   │                    MONITORING & LOGGING                            │   │
│   ├────────────────────────────────────────────────────────────────────┤   │
│   │  Metrics:   Prometheus + Grafana dashboards                        │   │
│   │  Errors:    Sentry real-time error tracking                       │   │
│   │  Logging:   Structured JSON logs (production)                    │   │
│   │  Alerts:    PagerDuty integration for critical issues              │   │
│   └────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   ┌────────────────────────────────────────────────────────────────────┐   │
│   │                    CI/CD PIPELINE                                  │   │
│   ├────────────────────────────────────────────────────────────────────┤   │
│   │  GitHub Actions:                                                   │   │
│   │  - Lint (ESLint, Flake8)                                        │   │
│   │  - Type Check (TypeScript, mypy)                                 │   │
│   │  - Unit Tests (Vitest, Pytest)                                   │   │
│   │  - Build (Docker, Next.js)                                       │   │
│   │  - Deploy (Vercel, cloud host)                                   │   │
│   └────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 1.8 TECHNOLOGY STACK - COMPLETE INVENTORY

### Frontend Technologies

| Component | Version | Role | Why Chosen |
|-----------|---------|------|------------|
| Next.js | 14.x | React Framework | App Router enables server components for performance, API routes for backend functionality, automatic code splitting for fast loads |
| TypeScript | 5.x | Type System | Catches errors at compile time, enables confident refactoring, self-documenting code through types |
| Tailwind CSS | 3.x | Styling | Utility-first approach speeds development, ensures design consistency, reduces CSS bundle size |
| Framer Motion | 11.x | Animations | Declarative animation API integrates cleanly with React, smooth 60fps transitions |
| GSAP | 3.x | Complex Animations | Timeline control for choreographed sequences, scroll-triggered animations, morphing effects |
| Zustand | 4.x | State Management | Minimal boilerplate compared to Redux, TypeScript-native with great inference, atomic updates |
| React | 18.x | UI Library | Concurrent features enable smooth rendering, Suspense for data loading, hooks for logic reuse |
| Lucide React | Latest | Icons | Clean, consistent icon set, tree-shakeable for small bundles, easy customization |

### Backend Technologies

| Component | Version | Role | Why Chosen |
|-----------|---------|------|------------|
| Python | 3.11 | Runtime | Strong AI/ML ecosystem, type hints improve maintainability, async support for high concurrency |
| FastAPI | 0.100+ | API Framework | Native async support, Pydantic for validation, automatic OpenAPI docs, dependency injection |
| Pydantic | 2.x | Data Validation | Type coercion, field validation, serialization - essential for reliable API contracts |
| LangGraph | 0.0.x | AI Orchestration | State machine patterns for multi-agent workflows, checkpointing for long-running tasks |
| LangChain | 0.1.x | LLM Integration | Unified interface to multiple LLM providers, chains for complex operations |
| Uvicorn | Latest | ASGI Server | High-performance async server, standard Python ASGI implementation |

### AI/ML Stack

| Component | Version | Role | Why Chosen |
|-----------|---------|------|------------|
| Google Vertex AI | Latest | LLM Provider | Enterprise-grade AI platform, Gemini models for reasoning, cost-effective pricing |
| Gemini Pro | 1.5 | Foundation Model | Best-in-class reasoning capabilities, long context window for complex prompts |
| Gemini Flash | 2.0 | Fast Model | Sub-second latency for simple content, cost-effective for bulk generation |
| LangGraph | Latest | Agent Orchestration | Complex workflow orchestration, state management for multi-turn generation |

### Database & Cache

| Component | Version | Role | Why Chosen |
|-----------|---------|------|------------|
| Supabase | Latest | PostgreSQL + Auth | Managed database eliminates ops burden, Row Level Security for multi-tenancy, built-in auth |
| PostgreSQL | 15+ | Primary Database | ACID compliance, JSON support for flexible schemas, excellent performance |
| Upstash Redis | Latest | Cache + Queue | Serverless Redis with REST API, pay-per-request pricing, global replication |
| Redis | 7.x | Caching | Sub-millisecond access for frequently-used data, pub/sub for real-time features |

### Infrastructure

| Component | Version | Role | Why Chosen |
|-----------|---------|------|------------|
| Vercel | Latest | Frontend Hosting | Zero-config deployments, edge network for global performance, preview deployments |
| Docker | Latest | Containerization | Consistent environments across dev/staging/production, easy horizontal scaling |
| Nginx | Latest | Reverse Proxy | SSL termination, request routing, rate limiting, static asset serving |
| Prometheus | Latest | Metrics | Industry-standard metrics collection, powerful query language, Grafana integration |
| Sentry | Latest | Error Tracking | Real-time error monitoring, detailed stack traces, release tracking |

---

## 1.9 DATA FLOW EXAMPLES

### Example 1: Creating a Move

1. User clicks "New Move" on Dashboard
2. Frontend opens Move creation modal
3. User selects category ("capture" for lead generation), enters strategic context ("announce new feature"), selects target ICP
4. Frontend calls `POST /api/ai/generate` with request body containing task, category, context, ICP
5. Backend validates workspace membership via Workspace Guard
6. Backend retrieves BCM from Redis cache (or DB if cache miss)
7. Backend compiles system prompt from BCM using `compile_system_prompt()`
8. Backend invokes Muse orchestrator in Council mode (3 agents: analyst, creative, editor)
9. LangGraph executes: fetch_bcm → select_agent_mode → build_system_prompt → generate_draft → score_output → store_result
10. Generated content returned to frontend via streaming response
11. Frontend renders content in Move Editor with character-by-character animation
12. User can edit, regenerate with different tone, or publish directly
13. On publish, content is scheduled via move_schedule table

### Example 2: Daily Wins Generation

1. Cron job triggers at 6 AM UTC
2. System queries all workspaces with BCM ready
3. For each workspace:
   a. Fetch BCM from cache
   b. Get active campaigns
   c. Calculate recent performance metrics
   d. Apply scoring algorithm (goal alignment, timing, audience relevance)
   e. Generate top 5 recommendations
   f. Cache results in Redis with daily TTL
4. User logs in and sees Daily Wins card on Dashboard
5. User clicks "Use This" on a recommendation
6. System creates Move from recommendation
7. User can edit, schedule, or publish immediately

### Example 3: Campaign Creation

1. User clicks "New Campaign" in Campaigns
2. Campaign Builder wizard opens at step 1
3. Steps: Name/Type → Goal → Timeline → Audience → Channels → Theme → AI Generate → Review
4. At Step 7 ("AI Generate"), user clicks "Generate Move Calendar"
5. Backend receives campaign config (type, goal, audience, channels, timeline)
6. Backend invokes Muse in Swarm mode
7. Muse generates complete Move calendar (10-20 Moves) in parallel
8. Results displayed as draggable cards on calendar UI
9. User can adjust, remove, or add Moves
10. User clicks "Launch Campaign"
11. Campaign status set to "active", Moves scheduled per calendar
12. Scheduler picks up scheduled Moves and executes at designated times
