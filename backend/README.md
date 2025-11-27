# RaptorFlow 2.0 Backend - Complete AI Agent Platform

## 🚀 What This System Does

**RaptorFlow 2.0** is a production-ready FastAPI backend implementing a **comprehensive AI agent ecosystem** with a hierarchical multi-agent system. The platform provides intelligent automation across multiple business domains through specialized AI agents.

**Core Innovation**: Realizes the "Console of Loads" - providing complete visibility and control over AI agent operations across the entire system, with cost tracking, performance monitoring, and operational insights.

## 🎯 Key Features Implemented

- **🤖 Hierarchical Agent System**: 3-tier architecture with specialized agents across multiple guilds
- **💰 Cost Tracking System**: Real-time monitoring of AI operations and costs
- **📊 Console of Loads**: Complete system monitoring dashboard and operational visibility
- **🎨 Muse Guild**: Creative content generation (hooks, memes, copy optimization, long-form content)
- **🔬 Research Guild**: Intelligence gathering and customer research capabilities
- **🛡️ Safety Guild**: Content compliance and moderation agents
- **📈 Matrix Guild**: Analytics and performance tracking agents
- **💾 Persistent Storage**: Supabase integration with structured data models
- **⚡ Caching & Performance**: Redis-backed caching and queue system
- **🔒 Security**: JWT authentication with workspace isolation
- **📝 API Documentation**: Complete Swagger/OpenAPI documentation

## ⚙️ Key Technologies

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Framework** | FastAPI | High-performance async web framework |
| **Agent Orchestration** | LangGraph | Multi-agent workflows and state management |
| **AI Models** | Google Vertex AI (Gemini/Sonnet) | Primary LLM provider with cost-effective models |
| **Database** | Supabase (PostgreSQL) | Real-time database with RLS |
| **Cache & Queue** | Redis | High-performance caching and task queuing |
| **Authentication** | JWT + Supabase Auth | Secure workspace-based authentication |
| **Monitoring** | Structured Logging + Health Checks | "Console of Loads" system visibility |

## 📁 Project Structure

```
backend/
├── main.py              # FastAPI application entry point
├── requirements.txt     # Python dependencies
├── .env.example         # Environment configuration template
├── config/
│   ├── settings.py      # Centralized configuration with brand guidelines
│   └── __init__.py
├── models/
│   ├── safety.py        # Safety and compliance data models
│   ├── muse.py          # Creative content generation models
│   ├── research.py      # Research and intelligence models
│   ├── matrix.py        # Analytics and performance models
│   ├── cost.py          # Cost tracking data models
│   └── __init__.py
├── agents/
│   ├── supervisor.py    # Master orchestrator agent
│   ├── safety/
│   │   ├── guardian_agent.py     # Content safety orchestrator
│   │   ├── privacy_guardian.py   # PII detection and removal
│   │   ├── brand_guardian.py     # Brand compliance checker
│   │   └── critic_agent.py       # Critical analysis agent
│   ├── muse/
│   │   ├── ab_test_agent.py      # A/B testing for copy
│   │   ├── whitepaper_agent.py   # Long-form content creation
│   │   ├── hook_generator.py     # Viral hooks generator
│   │   └── meme_agent.py         # Meme ideas generator
│   ├── research/
│   │   ├── web_intelligence_agent.py  # Web content analysis
│   │   └── pain_point_miner.py         # Customer feedback analysis
│   └── matrix/
│       ├── analytics_agent.py    # Business analytics
│       └── trend_agent.py        # Trend analysis
├── services/
│   ├── vertex_ai_client.py       # Google Vertex AI integration
│   ├── supabase_client.py        # Database operations
│   ├── cost_tracker.py          # Cost monitoring service
│   ├── monitoring_service.py    # System monitoring ("Console of Loads")
│   ├── web_scraper.py           # Web content scraping
│   ├── memory_manager.py        # Memory and context management
│   └── __init__.py
├── routers/
│   ├── monitoring.py     # System monitoring and health endpoints
│   ├── muse.py          # Creative content API endpoints
│   ├── research.py      # Research and intelligence endpoints
│   ├── analytics.py     # Analytics and performance endpoints
│   ├── costs.py         # Cost tracking API endpoints
│   └── __init__.py
├── orchestration/
│   ├── swarm_orchestrator.py   # Multi-agent orchestration
│   └── __init__.py
├── memory/               # Memory and RAG systems
├── tests/               # Comprehensive test suite
│   ├── test_cost_tracker.py
│   ├── test_pain_point_miner.py
│   ├── test_hook_generator.py
│   ├── test_meme_agent.py
│   └── __init__.py
├── utils/
│   ├── auth.py          # Authentication and authorization
│   ├── cache.py         # Redis caching utilities
│   ├── correlation.py   # Request correlation tracking
│   ├── sanitize.py      # Content sanitization
│   └── __init__.py
└── __init__.py
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Supabase account and project
- Google Cloud project with Vertex AI enabled
- Redis (local or cloud)

### 1. Environment Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env
```

**Required Environment Variables:**
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_SERVICE_KEY` - Supabase service role key
- `SUPABASE_ANON_KEY` - Supabase anon key
- `SUPABASE_JWT_SECRET` - JWT secret for token verification
- `GOOGLE_CLOUD_PROJECT` - Google Cloud project ID
- `REDIS_URL` - Redis connection URL
- `SECRET_KEY` - JWT signing key (change in production)

### 3. Database Setup

```bash
# Run database migrations (cost tracking table)
psql $SUPABASE_URL -f database/migrations/018_create_cost_tracking.sql
```

### 4. Start the Application

```bash
# Development mode
python main.py

# Production with uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📡 API Endpoints

The API is organized around different agent guilds:

### 🏥 System Monitoring ("Console of Loads")
- `GET /monitoring/status` - Complete system snapshot with agent activity and health
- `GET /monitoring/health` - Quick health check for load balancers
- `GET /monitoring/agents/activity` - 24h agent activity summary
- `GET /monitoring/costs/week` - Weekly cost breakdown by agent

### 🎨 Muse Guild - Creative Content
- `POST /muse/generate_variants` - A/B test marketing copy variations
- `POST /muse/generate_variants_batch` - Batch copy variation generation
- `POST /muse/generate_variants_contextual` - Context-aware copy variations
- `POST /muse/create_whitepaper` - Generate technical whitepapers
- `POST /muse/generate_hooks` - Create viral content hooks
- `POST /muse/generate_meme_ideas` - Generate creative meme concepts
- `GET /muse/variant_focuses` - List available variation strategies

### 🔬 Research Guild - Intelligence Gathering
- `POST /research/analyze_url` - Web content analysis and insights
- `POST /research/find_pain_points` - Customer feedback pain point extraction

### 📈 Matrix Guild - Analytics
- `POST /matrix/analytics/performance` - Business performance analytics
- `POST /matrix/trends/analyze` - Market trend analysis and insights

### 💰 Cost Tracking
- `GET /costs/{workspace_id}` - Retrieve cost logs for workspace

## 🏗️ Agent Architecture

### Guild-Based Organization

```
🏛️ RaptorFlow Agent Ecosystem
├── 🎨 Muse Guild (Creative Generation)
│   ├── Hook Generator (viral content hooks)
│   ├── Meme Generator (creative meme ideas)
│   ├── A/B Test Agent (copy optimization)
│   └── Whitepaper Agent (long-form content)
├── 🔬 Research Guild (Intelligence & Research)
│   ├── Pain Point Miner (customer feedback analysis)
│   └── Web Intelligence Agent (content analysis)
├── 🛡️ Safety Guild (Compliance & Moderation)
│   ├── Brand Guardian (brand compliance)
│   ├── Privacy Guardian (PII detection)
│   ├── Critic Agent (critical analysis)
│   └── Guardian Agent (orchestrator)
├── 📈 Matrix Guild (Analytics & Tracking)
│   ├── Analytics Agent (business analytics)
│   └── Trend Agent (market analysis)
└── 📊 Monitoring Service ("Console of Loads")
    ├── Agent Activity Monitoring
    ├── System Health Checks
    └── Cost Tracking Integration
```

### Cost Tracking System

**Database Schema**: `cost_logs` table tracks all AI operations
- Agent name, action, input/output tokens
- Estimated cost calculation (configurable pricing)
- Workspace isolation and correlation IDs
- 24h activity summaries and trending

### Console of Loads

The monitoring system provides real-time visibility:
- **Agent Activity**: Total actions, costs, top performers (24h rolling)
- **System Health**: Database connectivity, LLM API status
- **Performance Metrics**: Response times, error tracking
- **Operational Dashboard**: Centralized management view

## 🧪 Testing

```bash
# Run full test suite
pytest backend/tests/

# Run specific test
pytest backend/tests/test_cost_tracker.py -v

# Run with coverage
pytest --cov=backend --cov-report=html
```

## 📊 Monitoring Dashboard

Access the "Console of Loads" at:
- **API Endpoint**: `GET /monitoring/status`
- **Response**: Complete system health and activity snapshot

Example monitoring output:
```json
{
  "timestamp": "2025-01-27T12:34:56Z",
  "overall_status": "HEALTHY",
  "agent_activity": {
    "total_actions": 245,
    "total_cost": 12.45,
    "period_start": "2025-01-26T12:34:56Z",
    "period_end": "2025-01-27T12:34:56Z"
  },
  "system_health": {
    "database_connection": "OK",
    "llm_api_status": "OK",
    "response_time_ms": 245
  }
}
```

## 🔧 Configuration

### Centralized Settings (`backend/config/settings.py`)
- Brand guidelines for content compliance
- AI model configurations and API keys
- Database and caching parameters
- Security and authentication settings

### Environment Variables
All configuration can be overridden via environment variables for different deployments (development, staging, production).

## 🚀 Deployment

### Docker
```bash
# Build
docker build -t raptorflow-backend .

# Run
docker run -p 8000:8000 raptorflow-backend
```

### Cloud Run
```bash
# Deploy to Google Cloud Run
gcloud run deploy raptorflow-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## 🤝 Development Guidelines

- **Agent-First Development**: Every feature starts with an agent
- **Test-Driven Development**: Comprehensive test coverage
- **Type Safety**: Pydantic models for all data structures
- **Observability**: Correlation IDs and structured logging
- **Security**: JWT authentication with workspace isolation
- **Performance**: Redis caching and async operations

## 📄 License

This project demonstrates production-quality AI agent system architecture.

---

**Built with ❤️ using FastAPI, LangGraph, Google Vertex AI, Supabase, and Redis**
