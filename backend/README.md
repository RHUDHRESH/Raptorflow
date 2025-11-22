# RaptorFlow 2.0 Backend - Quick Start

## 🚀 What's Built

A production-ready FastAPI backend with a **3-tier hierarchical multi-agent system** using LangGraph:

- **Tier 0**: Master Supervisor orchestrator
- **Tier 1**: Domain supervisors (Onboarding, Customer Intelligence, etc.)
- **Tier 2**: 10+ specialist agents

## 📁 Project Structure

```
backend/
├── main.py                    # FastAPI app (READY TO RUN)
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
├── agents/
│   ├── supervisor.py         # Master orchestrator
│   ├── onboarding/           # Onboarding agents ✅
│   │   ├── question_agent.py
│   │   └── profile_builder.py
│   └── research/             # ICP research agents ✅
│       ├── icp_builder.py
│       ├── persona_narrative.py
│       ├── pain_point_miner.py
│       └── psychographic_profiler.py
├── graphs/                   # LangGraph workflows ✅
│   ├── onboarding_graph.py
│   └── customer_intelligence_graph.py
├── routers/                  # API endpoints ✅
│   └── onboarding.py         # 8 REST endpoints
├── models/                   # Pydantic schemas ✅
│   ├── onboarding.py
│   ├── persona.py
│   ├── campaign.py
│   └── content.py
├── services/                 # External integrations ✅
│   ├── supabase_client.py
│   └── openai_client.py
├── utils/                    # Utilities ✅
│   ├── cache.py              # Redis caching
│   ├── queue.py              # Task queue
│   └── correlation.py        # Distributed tracing
└── config/                   # Configuration ✅
    ├── settings.py
    └── prompts.py
```

## ⚡ Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Environment Variables

Copy `.env.example` to `.env` and fill in:

```bash
cp .env.example .env
```

Required variables:
- `OPENAI_API_KEY` - Your OpenAI API key
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_SERVICE_KEY` - Supabase service role key
- `SUPABASE_JWT_SECRET` - JWT secret for token verification
- `REDIS_URL` - Redis connection URL (default: `redis://localhost:6379/0`)

### 3. Start Redis (Required)

```bash
# Using Docker
docker run -d -p 6379:6379 redis:7-alpine

# Or using Homebrew (Mac)
brew services start redis

# Or using apt (Linux)
sudo apt-get install redis-server
sudo systemctl start redis
```

### 4. Run the Backend

```bash
# Development mode (with auto-reload)
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## 📚 API Endpoints

### System
- `GET /` - API information
- `GET /health` - Health check

### Onboarding ✅
- `POST /api/v1/onboarding/start` - Start onboarding session
- `POST /api/v1/onboarding/answer` - Submit answer
- `GET /api/v1/onboarding/session/{id}` - Get session state
- `GET /api/v1/onboarding/profile` - Get completed profile
- `PUT /api/v1/onboarding/profile` - Update profile
- `POST /api/v1/onboarding/complete` - Complete onboarding
- `DELETE /api/v1/onboarding/session/{id}` - Cancel session

## 🔧 Testing the API

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# Start onboarding (requires auth token)
curl -X POST http://localhost:8000/api/v1/onboarding/start \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Using Swagger UI

1. Open http://localhost:8000/api/docs
2. Click "Authorize" and enter your JWT token
3. Try out the endpoints interactively

## 🎯 What's Implemented

### ✅ Completed
- **Master Supervisor**: Routes requests to appropriate agents
- **Onboarding System**: Dynamic questionnaire with LangGraph workflow
- **Customer Intelligence**: 4 agents for ICP building
  - ICP Builder: Tags and structures personas
  - Persona Narrative: Converts data to stories
  - Pain Point Miner: Discovers pain points from web
  - Psychographic Profiler: Applies B=MAP framework
- **Core Infrastructure**:
  - FastAPI app with middleware
  - CORS configuration
  - JWT authentication with Supabase ✅
  - Correlation ID tracking
  - Redis caching & task queue
  - Supabase integration
  - OpenAI client with retry logic
  - Comprehensive Pydantic models

### 🚧 TODO
- Strategy agents (campaign planning, market research)
- Content generation agents (blog, email, social)
- Execution agents (platform publishing)
- Analytics agents (metrics, insights)
- Safety agents (critic, guardian)
- Additional routers (strategy, campaigns, content, analytics)
- Social platform integrations
- Docker containerization
- Deployment scripts

## 🏗️ Architecture

### 3-Tier Agent System

```
Tier 0: Master Supervisor
    └── Routes to domain supervisors

Tier 1: Domain Supervisors
    ├── Onboarding Supervisor
    │   └── Question Agent, Profile Builder
    ├── Customer Intelligence Supervisor
    │   └── ICP Builder, Narrative, Pain Point Miner, Psychographics
    ├── Strategy Supervisor (TODO)
    ├── Content Supervisor (TODO)
    └── Execution Supervisor (TODO)

Tier 2: Specialist Agents
    └── Atomic tasks (research, generation, API calls)
```

### Inter-Agent Communication
- **Message Bus**: Redis Pub/Sub for async events
- **Shared State**: LangGraph state management
- **Correlation IDs**: Distributed tracing across all agents
- **Caching**: Redis with configurable TTL

## 🔍 Monitoring & Debugging

### Logs
The application uses structured logging with correlation IDs. All logs include:
- Timestamp
- Log level
- Correlation ID (for tracing requests)
- Message

### Health Check
Monitor service health:
```bash
curl http://localhost:8000/health
```

Returns:
```json
{
  "status": "healthy",
  "environment": "development",
  "version": "2.0.0",
  "services": {
    "redis": "healthy",
    "supabase": "connected"
  }
}
```

## 📖 Next Steps

1. **Complete Strategy Layer**: Build campaign planning and market research agents
2. **Add Content Generation**: Implement blog, email, and social copy agents
3. **Platform Integrations**: Connect LinkedIn, Twitter, Instagram APIs
4. **Testing**: Add unit and integration tests
5. **Deployment**: Create Docker images and Cloud Run deployment scripts

## 🤝 Contributing

This is a production system under active development. Key principles:
- **Agent-first**: Every feature is an agent with clear responsibilities
- **LangGraph**: All multi-step workflows use LangGraph for orchestration
- **Type safety**: Pydantic models for all data structures
- **Observability**: Correlation IDs and structured logging everywhere

## 📄 License

[Your License]

---

**Built with**: FastAPI, LangGraph, OpenAI, Supabase, Redis

