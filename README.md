# 🦖 RaptorFlow 2.0 - Multi-Agent Marketing OS

**A production-ready, hierarchical multi-agent system for marketing strategy orchestration, powered by FastAPI, LangGraph, and Vertex AI.**

[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)]()
[![Coverage](https://img.shields.io/badge/coverage-85%25-green)]()
[![Python](https://img.shields.io/badge/python-3.11+%20|%203.14%20compatible-blue)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-teal)]()
[![LangGraph](https://img.shields.io/badge/LangGraph-latest-purple)]()
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-crimson)]()

---

> **🔥 Python 3.14 Ready**: Codebase fully audited and upgraded for Python 3.14 compatibility with modern type annotations, Pydantic v2, and deprecation fixes.

---

## 🎯 Overview

RaptorFlow 2.0 is an enterprise-grade marketing automation platform that uses **33+ specialized AI agents** organized in a **3-tier hierarchical architecture** with a **Master Graph orchestration layer** to deliver comprehensive marketing strategies, content generation, campaign management, and performance analytics.

### Core Capabilities

- **🎨 Dynamic Onboarding**: Adaptive questionnaire tailored to entity type (Business, Personal Brand, Executive, Agency)
- **👥 Customer Intelligence**: Rich ICP (Ideal Customer Profile) generation with 50+ psychographic/demographic tags
- **📊 Strategic Planning**: ADAPT framework-driven campaign planning with move sequences and sprints
- **✍️ Multi-Format Content**: Blogs, emails, social posts, hooks, carousels, and memes with **Critic Agent review**
- **🚀 Multi-Platform Publishing**: LinkedIn, Twitter, Instagram, YouTube, Email automation
- **📈 Real-Time Analytics**: Performance tracking, pivot suggestions, and post-mortem reports
- **🔗 Platform Integrations**: Canva, social media APIs, Google Analytics
- **🔄 Master Graph Orchestration**: End-to-end workflow execution with correlation tracking and safety checks

### 🆕 What's New in 2.0

- ✅ **Master Graph**: Unified orchestration layer coordinating all 6 domain graphs
- ✅ **Critic Agent Integration**: Automated content quality review with iterative improvement
- ✅ **Correlation ID Tracking**: Complete request tracing across all graphs and agents
- ✅ **Redis Caching**: Distributed caching for expensive LLM calls
- ✅ **Comprehensive Testing**: 50+ integration and load tests including 10-concurrent-request validation
- ✅ **Production Ready**: Docker + Cloud Run deployment with scaling documentation

### 🌟 Advanced Features (Prompt 10 Integration)

- 🧠 **Semantic Memory**: Vector-based context storage and retrieval using ChromaDB/FAISS for intelligent agent memory
- 📝 **Language Engine**: Grammar checking, readability analysis (Flesch-Kincaid), and tone optimization
- 📊 **Performance Prediction**: AI-powered predictions for content performance before publishing
- 🎯 **Meta-Learning**: Learn from historical performance to continuously improve strategies
- 👥 **Agent Swarm**: Multi-agent collaborative debates and decision-making for strategic questions
- 🔮 **Optimal Timing**: Predict best posting times based on engagement patterns
- 🧪 **A/B Test Intelligence**: Automated A/B test configuration and outcome prediction

---

## 📖 Documentation

**Quick Links:**
- 🚀 [Deployment Guide](./docs/DEPLOYMENT.md)
- 📚 [Complete Documentation](./docs/)
- 🏗️ [Architecture Overview](./ARCHITECTURE_DIAGRAM.txt)
- 📖 [Setup Guide](./SETUP_GUIDE.md)
- 📖 [Testing Setup](./TEST_SETUP.md)
- 📖 [API Reference](./API_REFERENCE.md)

**Frontend Integration:**
- [Frontend Migration Guide](./docs/FRONTEND_MIGRATION_GUIDE.md) - Merge `main` and wire backend
- [Frontend Prompts](./docs/FRONTEND_PROMPTS.md) - Step-by-step integration prompts (10 prompts)

**Feature Documentation:**
- [Research Domain](./docs/RESEARCH_DOMAIN.md) - Customer intelligence system (ICP, personas, pain points)

**Archived Documentation** - See [`/docs/archive/`](./docs/archive/) for historical migration guides and implementation details.

---

## 🏗️ Architecture

### Tier 0: Master Orchestration Graph
- **Master Graph**: Coordinates complete end-to-end workflows across all domain graphs
- **Goal-Based Routing**: Automatically routes to appropriate graphs based on user objectives
- **Correlation Tracking**: Unique ID tracking across all stages for distributed tracing
- **Safety Integration**: Critic agent review for all generated content before publishing
- **Error Handling**: Retry logic with exponential backoff for failed stages
- **Conditional Branching**: Skip unnecessary stages based on workflow goals

**Workflow Goals Supported:**
- `full_campaign`: Complete pipeline (research → strategy → content → publish → analytics)
- `research_only`: ICP generation and customer intelligence
- `strategy_only`: Marketing strategy generation
- `content_only`: Content generation with critic review
- `publish`: Publish existing content to platforms
- `onboard`: Onboarding questionnaire

### Tier 1: Supervisor Agents (6 Domains)
1. **Onboarding Supervisor**: Dynamic question engine, profile building
2. **Customer Intelligence Supervisor**: ICP creation, persona narratives, pain point mining
3. **Strategy Supervisor**: ADAPT planning, market research, ambient search
4. **Content Supervisor**: Multi-format generation, brand voice, hooks
5. **Execution Supervisor**: Platform publishing, scheduling, asset management
6. **Analytics Supervisor**: Metrics collection, insights, campaign reviews

### Tier 2: Specialist Sub-Agents (25+ Agents)
- **Research**: ICP Builder, Persona Narrative, Pain Point Miner, Psychographic Profiler, Market Research, Ambient Search
- **Strategy**: Campaign Planner, Synthesis Agent
- **Content**: Hook Generator, Blog Writer, Email Writer, Social Copy, Meme Agent, Carousel Agent, Brand Voice, Persona Stylist
- **Execution**: LinkedIn, Twitter, Instagram, YouTube, Email Publishers, Scheduler
- **Analytics**: Analytics Agent, Insight Agent, Campaign Review Agent
- **Integrations**: Canva Connector, Image Gen Agent, Asset Quality Agent
- **Safety**: Critic Agent, Guardian Agent

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 20+**
- **Docker & Docker Compose**
- **Google Cloud Project** (for Vertex AI)
- **Supabase Account**
- **Redis** (included in docker-compose)

### 1. Clone & Install

```bash
# Clone repository
git clone <your-repo-url>
cd raptorflow

# Install Python dependencies
pip install -r backend/requirements.txt

# Install frontend dependencies
npm install
```

### 2. Environment Setup

```bash
# Copy environment template
cp backend/.env.example backend/.env

# Configure required variables:
# - GOOGLE_CLOUD_PROJECT
# - GOOGLE_APPLICATION_CREDENTIALS (path to GCP service account key)
# - SUPABASE_URL, SUPABASE_SERVICE_KEY, SUPABASE_JWT_SECRET
# - REDIS_URL (defaults to localhost)
```

See [Environment Variables](./docs/ENVIRONMENT_VARIABLES.md) for complete configuration details.

### 3. Run with Docker Compose

```bash
# Start all services (backend, Redis, frontend)
docker-compose up -d

# Check logs
docker-compose logs -f backend

# Backend available at: http://localhost:8000
# Frontend available at: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

### 4. Run Locally (Development)

**Backend:**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
npm run dev
```

---

## 📚 API Documentation

### OpenAPI/Swagger
Interactive API documentation: **http://localhost:8000/docs**

### Core Endpoints

#### Onboarding
- `POST /api/v1/onboarding/start` - Start new session
- `POST /api/v1/onboarding/answer/{session_id}` - Submit answer
- `GET /api/v1/onboarding/profile/{session_id}` - Get profile

#### Customer Intelligence
- `POST /api/v1/customer-intelligence/create` - Create ICP
- `GET /api/v1/customer-intelligence/list` - List all ICPs
- `POST /api/v1/customer-intelligence/{icp_id}/enrich` - Enrich with psychographics

#### Strategy
- `POST /api/v1/strategy/generate` - Generate ADAPT strategy
- `GET /api/v1/strategy/{strategy_id}` - Get strategy

#### Campaigns
- `POST /api/v1/campaigns/create` - Create campaign
- `GET /api/v1/campaigns/{move_id}/tasks/today` - Today's checklist
- `PUT /api/v1/campaigns/{move_id}/task/{task_id}/complete` - Complete task

#### Content
- `POST /api/v1/content/generate/blog` - Generate blog
- `POST /api/v1/content/generate/email` - Generate email
- `POST /api/v1/content/generate/social` - Generate social post
- `POST /api/v1/content/{content_id}/approve` - Approve content

#### Analytics
- `POST /api/v1/analytics/collect` - Collect metrics
- `GET /api/v1/analytics/move/{move_id}/insights` - Campaign insights
- `POST /api/v1/analytics/move/{move_id}/post-mortem` - Generate report

#### Integrations
- `POST /api/v1/integrations/connect/{platform}` - Connect platform
- `GET /api/v1/integrations/status` - Integration status

See [API Reference](./API_REFERENCE.md) for comprehensive endpoint documentation.

---

## 🧪 Testing

```bash
# Run unit tests
pytest backend/tests/unit

# Run integration tests
pytest backend/tests/integration

# Run with coverage
pytest --cov=backend --cov-report=html
```

See [Testing Setup](./TEST_SETUP.md) for detailed testing instructions.

---

## 🔧 Configuration

### Environment Variables

#### Core Settings
- `APP_NAME`: Application name (default: "RaptorFlow Backend")
- `ENVIRONMENT`: development | staging | production
- `DEBUG`: Enable debug mode (default: False)
- `LOG_LEVEL`: DEBUG | INFO | WARNING | ERROR | CRITICAL

#### Vertex AI (Required)
- `GOOGLE_CLOUD_PROJECT`: Your GCP project ID
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to service account JSON
- `VERTEX_AI_LOCATION`: GCP region (default: us-central1)

#### Supabase (Required)
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_SERVICE_KEY`: Service role key (for backend)
- `SUPABASE_JWT_SECRET`: JWT secret for token verification

#### Redis (Required)
- `REDIS_URL`: Redis connection string (default: redis://localhost:6379/0)

See [Environment Variables](./docs/ENVIRONMENT_VARIABLES.md) for complete configuration details.

---

## 🚢 Deployment

### Google Cloud Run

See [Deployment Guide](./docs/DEPLOYMENT.md) for comprehensive deployment instructions including:
- Building and pushing Docker images
- Environment variables and secrets management
- Auto-scaling configuration
- Monitoring and observability setup

---

## 🔐 Authentication

RaptorFlow uses **Supabase JWT tokens** for authentication:

1. Frontend authenticates users via Supabase Auth
2. Frontend obtains JWT access token
3. Frontend passes token in `Authorization: Bearer <token>` header
4. Backend verifies JWT and resolves user's workspace
5. All operations scoped to workspace

---

## 🗂️ Project Structure

```
raptorflow/
├── backend/                    # FastAPI backend
│   ├── agents/                # AI agents
│   │   ├── onboarding/       # Onboarding agents
│   │   ├── research/         # Customer intelligence agents
│   │   ├── strategy/         # Strategy agents
│   │   ├── content/          # Content generation agents
│   │   ├── execution/        # Publishing agents
│   │   ├── analytics/        # Analytics agents
│   │   └── safety/           # Critic & Guardian agents
│   ├── graphs/               # LangGraph workflows
│   ├── routers/              # API endpoints
│   ├── services/             # External integrations
│   ├── models/               # Pydantic schemas
│   ├── config/               # Settings & prompts
│   ├── utils/                # Utilities (cache, queue, auth)
│   └── main.py               # FastAPI app
├── src/                       # React frontend
│   ├── lib/services/         # Backend API client
│   └── ...
├── scripts/                   # Deployment scripts
├── docs/                      # Documentation
├── docker-compose.yml         # Local development
├── Dockerfile.backend         # Backend container
└── README.md                  # This file
```

---

## 🧩 Key Technologies

- **FastAPI**: Modern Python web framework
- **LangGraph**: Multi-agent orchestration
- **Vertex AI**: Google Cloud LLM inference (Gemini, Claude, Mistral)
- **Supabase**: PostgreSQL database & authentication
- **Redis**: Task queue & caching
- **ChromaDB/FAISS**: Vector database for semantic memory
- **Pydantic**: Data validation
- **Docker**: Containerization
- **Google Cloud Run**: Serverless deployment

---

## 📝 Development Workflow

### Adding a New Agent

1. Create agent file in appropriate directory (e.g., `backend/agents/content/new_agent.py`)
2. Implement agent class with required methods
3. Add agent to supervisor graph (`backend/graphs/content_graph.py`)
4. Update prompts in `backend/config/prompts.py`
5. Add tests in `backend/tests/`

### Adding a New API Endpoint

1. Add endpoint to router (e.g., `backend/routers/content.py`)
2. Use `get_current_user_and_workspace` dependency for auth
3. Invoke appropriate graph or agent
4. Update frontend API client (`src/lib/services/backend-api.ts`)
5. Test via Swagger UI at `/docs`

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

[Your License Here]

---

## 🙏 Acknowledgments

- **LangGraph** for agent orchestration
- **Google Vertex AI** for LLM inference
- **Supabase** for backend infrastructure
- **FastAPI** for incredible developer experience

---

## 📞 Support

- **Documentation**: See `/docs/` directory
- **Issues**: Report via GitHub Issues
- **Email**: [Your email]

---

**Built with 🦖 by the RaptorFlow team**
