# RAPTORFLOW LANGGRAPH SWARM BACKEND

> **Complete Implementation Plan for Agent-to-Agent Swarm Architecture**

---

## 📋 DOCUMENTS

| Document | Description |
|----------|-------------|
| [01_LANGGRAPH_ARCHITECTURE.md](./01_LANGGRAPH_ARCHITECTURE.md) | Core LangGraph state machine and orchestrator |
| [02_SPECIALIST_AGENTS.md](./02_SPECIALIST_AGENTS.md) | All specialist agents with prompts and code |
| [03_TOOLS_AND_INFRASTRUCTURE.md](./03_TOOLS_AND_INFRASTRUCTURE.md) | Tools, FastAPI, Redis, Vertex AI config |
| [04_DATABASE_SCHEMA.md](./04_DATABASE_SCHEMA.md) | Complete Supabase PostgreSQL schema |

---

## 🏗️ ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Vercel)                       │
│                    Next.js + React + TypeScript                 │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND (GCP Cloud Run)                    │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    LANGGRAPH SWARM                        │  │
│  │                                                           │  │
│  │  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐     │  │
│  │  │ ORCHESTRATOR│──▶│  ONBOARDING │   │  PRODUCT    │     │  │
│  │  │  (Router)   │   │    SWARM    │   │   SWARM     │     │  │
│  │  └─────────────┘   │             │   │             │     │  │
│  │         │          │ -Vault      │   │ -Moves      │     │  │
│  │         │          │ -Extractor  │   │ -Campaigns  │     │  │
│  │         │          │ -Researcher │   │ -Muse       │     │  │
│  │         │          │ -ICP        │   │ -BlackBox   │     │  │
│  │         │          │ -Position   │   │ -DailyWins  │     │  │
│  │         │          └─────────────┘   └─────────────┘     │  │
│  │         │                                                 │  │
│  │         ▼                                                 │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │                    TOOLS                            │  │  │
│  │  │ web_search | scraper | OCR | GST | DB | export     │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│  Vertex AI  │      │  Supabase   │      │   Upstash   │
│  (Gemini)   │      │ (Postgres)  │      │   (Redis)   │
└─────────────┘      └─────────────┘      └─────────────┘
```

---

## 🤖 AGENT INVENTORY

### Onboarding Swarm (Steps 1-25)
| Agent | Steps | Purpose |
|-------|-------|---------|
| `VaultProcessor` | 1 | Process file uploads and URLs |
| `TruthExtractor` | 2, 4, 6 | Extract facts from evidence |
| `ContradictionDetector` | 3 | Find conflicts in data |
| `MarketResearcher` | 7, 10, 21, 22 | Web research, competitors |
| `CompetitorAnalyzer` | 8, 9 | Competitor analysis & ranking |
| `DifferentiationAnalyzer` | 11 | USP extraction |
| `PositioningMapper` | 12, 14 | Perceptual maps, strategy |
| `PositioningWriter` | 13 | Positioning statements |
| `ICPArchitect` | 15, 16 | Generate detailed ICPs |
| `MessagingGuardian` | 17 | Messaging guardrails |
| `SoundbiteGenerator` | 18, 19 | Soundbites, hierarchy |
| `SynthesisEngine` | 23-25 | Final synthesis |

### Product Swarm
| Agent | Feature | Purpose |
|-------|---------|---------|
| `MoveGenerator` | Moves | 7-day battle plans |
| `CampaignPlanner` | Campaigns | Multi-move initiatives |
| `MuseEngine` | Muse | Copywriting |
| `BlackBoxEngine` | BlackBox | High-risk strategies |
| `DailyWinsEngine` | Daily Wins | Quick content from trends |

---

## 💰 COST MODEL

### Vertex AI Pricing (Gemini 2.0)
| Model | Input ($/1K) | Output ($/1K) | Use Case |
|-------|-------------|---------------|----------|
| Flash-Lite | $0.000075 | $0.0003 | Routing |
| Flash | $0.00015 | $0.0006 | Standard ops |
| Pro | $0.00125 | $0.005 | Complex reasoning |

### Estimated Per-User Costs
| Operation | Tokens | Est. Cost |
|-----------|--------|-----------|
| Onboarding (full) | ~50K | ~$0.05 |
| Move generation | ~10K | ~$0.01 |
| Campaign planning | ~15K | ~$0.015 |
| Muse content | ~5K | ~$0.005 |
| BlackBox strategy | ~8K | ~$0.008 |
| Daily Wins | ~3K | ~$0.003 |

### Monthly Budget Tiers
| Tier | Budget | Price (INR) |
|------|--------|-------------|
| Free | $1 | ₹0 |
| Starter | $10 | ₹799 |
| Growth | $50 | ₹2,999 |
| Enterprise | Custom | Contact |

---

## 🚀 IMPLEMENTATION PHASES

### Phase 1: Core Infrastructure (Week 1-2)
- [ ] FastAPI project setup
- [ ] Supabase schema deployment
- [ ] Upstash Redis configuration
- [ ] Vertex AI authentication
- [ ] Basic LangGraph skeleton

### Phase 2: Orchestrator + Tools (Week 2-3)
- [ ] Orchestrator agent with routing
- [ ] Web search tool
- [ ] Scraping tools
- [ ] File processing (PDF, OCR)
- [ ] Budget enforcement

### Phase 3: Onboarding Swarm (Week 3-5)
- [ ] VaultProcessor
- [ ] TruthExtractor
- [ ] MarketResearcher
- [ ] CompetitorAnalyzer
- [ ] ICPArchitect
- [ ] PositioningMapper
- [ ] SynthesisEngine

### Phase 4: Product Swarm (Week 5-7)
- [ ] MoveGenerator
- [ ] CampaignPlanner
- [ ] MuseEngine
- [ ] BlackBoxEngine
- [ ] DailyWinsEngine

### Phase 5: Integration & Polish (Week 7-8)
- [ ] Frontend integration
- [ ] Semantic caching
- [ ] Error handling
- [ ] Monitoring setup
- [ ] Load testing

---

## 📁 PROJECT STRUCTURE

```
backend/
├── main.py                 # FastAPI app
├── requirements.txt
├── Dockerfile
│
├── agents/
│   ├── graph.py           # Main LangGraph
│   ├── orchestrator.py    # Supervisor
│   │
│   ├── onboarding/
│   │   ├── swarm.py       # Onboarding sub-graph
│   │   ├── vault.py
│   │   ├── extractor.py
│   │   ├── researcher.py
│   │   ├── icp_architect.py
│   │   └── synthesis.py
│   │
│   └── product/
│       ├── moves.py
│       ├── campaigns.py
│       ├── muse.py
│       ├── blackbox.py
│       └── daily_wins.py
│
├── tools/
│   ├── registry.py        # Tool registry
│   ├── search.py          # Web search
│   ├── scraper.py         # Web scraping
│   ├── files.py           # PDF, OCR
│   ├── indian_market.py   # JustDial, IndiaMART, GST
│   └── database.py        # Supabase tools
│
├── core/
│   ├── config.py          # Settings
│   ├── database.py        # Supabase client
│   ├── redis.py           # Upstash client
│   └── vertex.py          # Vertex AI config
│
├── economics/
│   ├── budget.py          # Budget enforcement
│   └── cache.py           # Semantic cache
│
└── api/
    └── v1/
        ├── agents.py      # /api/v1/agents/execute
        ├── onboarding.py  # /api/v1/onboarding/*
        ├── moves.py       # /api/v1/moves/*
        ├── campaigns.py   # /api/v1/campaigns/*
        ├── muse.py        # /api/v1/muse/*
        └── blackbox.py    # /api/v1/blackbox/*
```

---

## 🔧 QUICK START

```bash
# Clone and setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your credentials

# Run locally
uvicorn main:app --reload --port 8000

# Deploy to Cloud Run
gcloud builds submit --config=cloudbuild.yaml
```

---

## 📊 KEY METRICS

| Metric | Target |
|--------|--------|
| API Response Time (P95) | < 5s |
| Move Generation Time | < 10s |
| Onboarding Completion | < 30 min |
| Cost per Onboarding | < $0.10 |
| Cost per Move | < $0.02 |
| Agent Success Rate | > 95% |

---

## 🔐 SECURITY

- All API endpoints require Supabase JWT auth
- Row-Level Security on all database tables
- Service account keys stored in Secret Manager
- Rate limiting via Upstash Redis
- Budget enforcement prevents cost overruns

---

## 📈 MONITORING

- Cloud Run metrics (latency, errors, instances)
- Custom metrics for agent executions
- Cost tracking per user/operation
- Error alerting via Cloud Monitoring
