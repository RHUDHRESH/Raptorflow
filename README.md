# RaptorFlow

**Autonomous Marketing Strategy OS** - A virtual marketing agency in a box.

RaptorFlow analyzes your business (story, audience, goals) and delivers a ready-to-run marketing campaign. Instead of giving you tools, we give you a finished strategic plan to review and execute.

## 🏗️ Project Structure

```
Raptorflow/
├── raptorflow-www/          # Frontend (Next.js 15)
│   ├── src/
│   │   ├── app/
│   │   │   ├── (marketing)/  # Public marketing site
│   │   │   └── (app)/        # Authenticated app (dashboard, groundwork, etc.)
│   │   ├── components/       # React components
│   │   ├── lib/              # Utilities
│   │   └── styles/           # Global styles & tokens
│   └── public/                # Static assets
│
├── backend/                  # Backend (FastAPI + LangGraph)
│   ├── main.py              # FastAPI entry point
│   ├── routers/             # API routes
│   ├── agents/              # AI agents (LangGraph)
│   ├── services/            # External integrations
│   └── models/              # Pydantic models
│
└── shared/                   # Shared types & contracts
    └── types/               # TypeScript types (shared with backend)
```

## 🚀 Quick Start

### Frontend

```bash
cd raptorflow-www
pnpm install
pnpm dev
```

Visit http://localhost:3000

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

API docs: http://localhost:8000/docs

## 📋 Tech Stack

### Frontend
- **Next.js 15** (App Router) - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first styling
- **shadcn/ui** - Component library
- **Inter Font** - Typography (17-18px base, proper hierarchy)

### Backend
- **FastAPI** - Python web framework
- **LangGraph** - Multi-agent orchestration
- **Supabase** - PostgreSQL database + vector embeddings
- **OpenAI** - LLM for content generation
- **Redis** - Message bus for agent communication

### Design System
- **Monochrome base** (white/black/gray)
- **Accent colors**: Deep Indigo (#28295a), Sky Blue (#51baff), Emerald (#09be99)
- **Typography**: Inter for UI, JetBrains Mono for code
- **Spacing**: Generous whitespace, clean layout

## 🎯 Key Features

1. **Groundwork** - Strategic onboarding that captures business context, ICPs, goals
2. **ADAPT Framework** - Automated strategy generation (Audience, Design, Assemble, Promote, Track)
3. **Move System** - Campaign execution with daily tasks and AI automation
4. **Multi-Agent System** - Specialized AI agents for content, assets, publishing, analytics
5. **Ambient Search** - Proactive campaign ideation based on trends and user data

## 📁 Route Structure

### Marketing (Public)
- `/` - Homepage
- `/pricing` - Pricing page

### App (Authenticated)
- `/dashboard` - Strategy workspace
- `/groundwork` - Onboarding flow
- `/auth/signin` - Sign in
- `/auth/signup` - Sign up

## 🔧 Development

### Type Checking
```bash
# Frontend
cd raptorflow-www
pnpm typecheck

# Backend
cd backend
mypy .
```

### Linting
```bash
# Frontend
pnpm lint

# Backend
flake8 .
black .
```

## 📚 Documentation

- [Product Blueprint](./docs/blueprint.md) - Full product strategy
- [API Documentation](./backend/README.md) - Backend API docs
- [Design System](./raptorflow-www/src/styles/tokens.css) - Design tokens

## 🎨 Design Principles

- **Minimalist Elegance** - Monochrome base with strategic accents
- **Premium Feel** - Clean, spacious, professional
- **User-Centric** - Clear hierarchy, readable typography
- **Accessible** - High contrast, semantic HTML, ARIA labels

## 📝 Next Steps

1. ✅ Design tokens aligned with blueprint
2. ✅ App route structure created
3. ✅ Shared types defined
4. ⏳ Groundwork onboarding implementation
5. ⏳ Backend API implementation
6. ⏳ Authentication setup
7. ⏳ Database schema & migrations

---

Built with ❤️ for founders, marketers, and small teams.

