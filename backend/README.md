# RaptorFlow Backend

FastAPI + LangGraph backend for RaptorFlow marketing OS.

## Structure

```
backend/
├── main.py              # FastAPI app entry point
├── routers/              # API route handlers
│   ├── auth.py          # Authentication endpoints
│   ├── groundwork.py     # Groundwork onboarding
│   ├── strategy.py       # ADAPT strategy management
│   ├── moves.py          # Move (campaign) management
│   ├── content.py        # Content generation
│   └── analytics.py      # Analytics & insights
├── agents/               # AI agents (LangGraph)
│   ├── supervisor.py    # Strategy Supervisor
│   ├── persona.py        # ICP/Persona agents
│   ├── content/          # Content generation agents
│   ├── assets/           # Asset generation agents
│   ├── platform/         # Platform publishing agents
│   └── analytics/        # Analytics agents
├── services/             # External integrations
│   ├── supabase.py       # Database client
│   ├── canva.py          # Canva API
│   ├── social.py         # Social platform APIs
│   └── openai.py         # LLM service
├── models/               # Pydantic models & DB schemas
│   ├── user.py
│   ├── icp.py
│   ├── strategy.py
│   └── move.py
└── utils/                # Utilities
    ├── auth.py           # JWT, session management
    └── validators.py     # Input validation
```

## Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload --port 8000
```

## Environment Variables

Create a `.env` file:

```env
# Database
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# AI Services
OPENAI_API_KEY=your_openai_key

# External APIs
CANVA_API_KEY=your_canva_key

# Auth
JWT_SECRET=your_jwt_secret
JWT_ALGORITHM=HS256

# App
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

