# RaptorFlow Technical Overview

## 🏗️ **Executive Summary**

RaptorFlow is a **modern marketing operating system** built with a **serverless-first architecture** that combines cutting-edge frontend and backend technologies. The application leverages **Next.js 16** for the frontend, **FastAPI** for the backend, and integrates with **AI/ML services** to provide intelligent marketing automation and analytics.

---

## 📋 **Technology Stack Overview**

### **Frontend Stack (Vercel)**
- **Framework**: Next.js 16.1.1 with React 19.2.3
- **Language**: TypeScript 5.6.3
- **Deployment**: Vercel (serverless functions)
- **Styling**: Tailwind CSS v4.0
- **UI Components**: Radix UI primitives
- **State Management**: Zustand 5.0.9
- **Animations**: GSAP + Framer Motion 12.23.24
- **Testing**: Playwright + Vitest
- **Monitoring**: Sentry

### **Backend Stack (GCP/Serverless)**
- **Framework**: FastAPI (Python 3.11+)
- **Deployment**: Google Cloud Platform (Cloud Run/Container Engine)
- **Database**: Supabase (PostgreSQL)
- **Cache**: Upstash Redis
- **AI/ML**: Vertex AI (Google Cloud)
- **Storage**: Google Cloud Storage
- **Email**: Resend
- **Monitoring**: Sentry + Structlog

### **Infrastructure Services**
- **Frontend Hosting**: Vercel Edge Network
- **Backend Hosting**: Google Cloud Platform (Cloud Run)
- **Database**: Supabase (managed PostgreSQL)
- **Cache**: Upstash Redis (global edge)
- **File Storage**: Google Cloud Storage
- **AI/ML**: Vertex AI (Gemini models)
- **Email**: Resend (transactional)
- **Monitoring**: Sentry (error tracking)

---

## 🌐 **Architecture Patterns**

### **High-Level Architecture**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Proxy     │    │   Backend       │
│   (Next.js)     │───▶│   (Next.js)     │───▶│   (FastAPI)     │
│   Vercel        │    │   Serverless    │    │   GCP Cloud Run │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Browser       │    │   CORS/Security │    │   Supabase      │
│   Client        │    │   Layer         │    │   PostgreSQL    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Data Flow Architecture**
```
User Interaction → Frontend Component → API Proxy → Backend Service → External Service
     ↓                    ↓                    ↓              ↓              ↓
State Update → UI Re-render → HTTP Request → Business Logic → Database/AI
```

---

## 🎨 **Frontend Architecture Deep Dive**

### **Next.js App Router Structure**
```
src/
├── app/                    # App Router pages
│   ├── (shell)/           # Shell layout
│   ├── api/               # API routes (proxy)
│   │   └── [...path]/     # Dynamic proxy route
│   ├── auth/              # Authentication pages
│   ├── campaigns/         # Campaign management
│   └── dashboard/         # Main dashboard
├── components/            # Reusable React components
│   ├── ui/               # Base UI components
│   ├── forms/            # Form components
│   └── layout/           # Layout components
├── lib/                  # Utility functions
│   ├── utils.ts          # General utilities
│   ├── auth-service.ts   # Authentication logic
│   └── api-client.ts     # API client configuration
└── stores/               # Zustand state management
    ├── campaignStore.ts  # Campaign state
    └── authStore.ts      # Authentication state
```

### **State Management with Zustand**
```typescript
// Example campaign store
interface CampaignStore {
  campaigns: Campaign[]
  loading: boolean
  error: string | null
  
  // Actions
  fetchCampaigns: () => Promise<void>
  createCampaign: (data: CreateCampaignData) => Promise<void>
  updateCampaign: (id: string, data: UpdateCampaignData) => Promise<void>
}
```

### **API Proxy Pattern**
```typescript
// src/app/api/[...path]/route.ts
export async function GET(request: NextRequest, context: RouteContext) {
  const { path } = await context.params
  return proxyRequest(request, path)
}

// Proxy handles:
// - CORS headers
// - Authentication forwarding
// - Error handling
// - Backend URL resolution
```

### **Component Architecture**
- **Atomic Design**: Atoms → Molecules → Organisms → Templates → Pages
- **Composition over Inheritance**: Highly composable component patterns
- **TypeScript First**: Full type safety across all components
- **Responsive Design**: Mobile-first with Tailwind breakpoints

---

## ⚙️ **Backend Architecture Deep Dive**

### **FastAPI Application Structure**
```
backend/
├── main.py               # Application entry point
├── app_factory.py        # App configuration factory
├── api/                  # API routes
│   ├── registry.py       # Router registry
│   ├── system.py         # System endpoints
│   └── v1/               # API v1 routes
│       ├── campaigns.py   # Campaign management
│       ├── workspaces.py # Workspace management
│       ├── foundation.py # Marketing foundation
│       ├── muse.py       # AI content generation
│       └── context.py    # Business context
├── core/                 # Core functionality
│   ├── redis_mgr.py      # Redis management
│   └── storage_mgr.py    # Storage management
├── services/             # External services
│   ├── supabase_client.py
│   ├── vertex_ai_client.py
│   └── upstash_client.py
└── agents/               # AI agents
    └── specialists/      # Specialized AI agents
```

### **Router Registry Pattern**
```python
# backend/api/registry.py
UNIVERSAL_ROUTERS = [
    workspaces.router,
    campaigns.router,
    moves.router,
    foundation.router,
    muse.router,
    context.router,
    bcm_feedback.router,
    scraper.router,
    search.router,
]

def include_universal(app: FastAPI, prefix: str = "/api") -> None:
    for router in UNIVERSAL_ROUTERS:
        app.include_router(router, prefix=prefix)
```

### **Service Layer Architecture**
```python
# Example service pattern
class CampaignService:
    def __init__(self, db: Database, redis: Redis):
        self.db = db
        self.redis = redis
    
    async def create_campaign(self, data: CampaignCreate) -> Campaign:
        # Business logic
        campaign = await self.db.create_campaign(data)
        await self.redis.cache_campaign(campaign)
        return campaign
```

---

## 🗄️ **Database & Storage Architecture**

### **Supabase PostgreSQL Schema**
```sql
-- Core entities
workspaces               -- Multi-tenant workspaces
users                    -- User profiles and auth
campaigns               -- Marketing campaigns
moves                   -- Marketing tasks/activities
foundation              -- Marketing foundation data
icp_profiles            -- Ideal customer profiles
business_context        -- Business context data

-- Supporting entities
campaign_analytics      -- Campaign performance
move_completions        -- Task completion tracking
user_sessions           -- Session management
audit_logs             -- Audit trail
```

### **Row Level Security (RLS)**
```sql
-- Example RLS policy
CREATE POLICY workspace_isolation ON campaigns
  FOR ALL TO authenticated
  USING (workspace_id = current_setting('app.workspace_id')::uuid);
```

### **Upstash Redis Usage**
```python
# Redis patterns implemented
redis_client.set(f"session:{session_id}", user_data, ex=3600)  # Sessions
redis_client.set(f"campaign:{id}", campaign_data, ex=300)    # Cache
redis_client.incr(f"rate_limit:{user_id}", ex=60)           # Rate limiting
redis_client.publish(f"workspace:{id}", event_data)         # Real-time
```

---

## 🔌 **API Architecture**

### **Frontend API Routes**
```typescript
// API Proxy Routes
GET    /api/proxy/health
GET    /api/proxy/workspaces
POST   /api/proxy/workspaces
GET    /api/proxy/campaigns
POST   /api/proxy/campaigns
PATCH  /api/proxy/campaigns/:id
DELETE /api/proxy/campaigns/:id
```

### **Backend API Routes**
```python
# System Routes
GET    /health
GET    /api/health

# Workspace Routes (No Auth)
POST   /api/workspaces
GET    /api/workspaces/{id}
PATCH  /api/workspaces/{id}

# Tenant-Scoped Routes (requires x-workspace-id header)
GET    /api/campaigns
POST   /api/campaigns
GET    /api/campaigns/{id}
PATCH  /api/campaigns/{id}
DELETE /api/campaigns/{id}

# AI/ML Routes
POST   /api/muse/generate
GET    /api/muse/health
```

### **Authentication Flow**
```typescript
// Frontend auth flow
1. User signs in with Supabase Auth
2. JWT token stored in secure cookie
3. API proxy forwards auth header to backend
4. Backend validates token with Supabase
5. Workspace context extracted from token
6. Request processed with workspace isolation
```

---

## 🤖 **AI/ML Integration Architecture**

### **Vertex AI Integration**
```python
# Vertex AI client implementation
class VertexAIClient:
    def __init__(self, project_id: str, location: str):
        self.project_id = project_id
        self.location = location
        self.model = "gemini-2.0-flash-exp"
    
    async def generate_content(self, prompt: str) -> str:
        # AI content generation
        response = await self.model.generate_content(prompt)
        return response.text
```

### **AI-Powered Features**
1. **Content Generation (Muse)**
   - AI-powered marketing content
   - Multiple content types (posts, emails, blogs)
   - Brand voice consistency

2. **Business Context Analysis**
   - SWOT analysis generation
   - Competitive positioning
   - Market insights

3. **ICP Enhancement**
   - Psychographic profiling
   - Behavioral pattern analysis
   - Persona refinement

---

## 🔐 **Security Architecture**

### **Multi-Layer Security**
```
┌─────────────────┐
│   Network Layer  │  - HTTPS enforcement
│   (TLS/SSL)      │  - Vercel edge security
└─────────────────┘
┌─────────────────┐
│   Application   │  - CORS configuration
│   Security       │  - Rate limiting
│   Layer          │  - Input validation
└─────────────────┘
┌─────────────────┐
│   Data Layer     │  - Row Level Security
│   Security       │  - Encryption at rest
│   Layer          │  - Secure secrets
└─────────────────┘
```

### **Authentication & Authorization**
```typescript
// Supabase Auth integration
const { data: { user } } = await supabase.auth.getUser()
const workspaceId = user?.app_metadata?.workspace_id

// Backend validation
token = request.headers.get("Authorization")
user = await supabase.auth.getUser(token)
workspace_id = user.app_metadata.workspace_id
```

---

## 📊 **Monitoring & Observability**

### **Sentry Integration**
```typescript
// Frontend error tracking
Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: 1.0,
})
```

```python
# Backend error tracking
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    traces_sample_rate=1.0,
    environment=os.getenv("NODE_ENV")
)
```

### **Health Checks**
```python
# Comprehensive health monitoring
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": await check_database(),
        "redis": await check_redis(),
        "vertex_ai": await check_vertex_ai(),
        "timestamp": datetime.utcnow()
    }
```

---

## 🚀 **Deployment Architecture**

### **Frontend Deployment (Vercel)**
```json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/next"
    }
  ],
  "routes": [
    {
      "src": "/api/proxy/(.*)",
      "dest": "/api/proxy/$1"
    }
  ],
  "functions": {
    "src/app/api/**/*.ts": {
      "maxDuration": 30
    }
  }
}
```

### **Backend Deployment (Render)**
```dockerfile
# Backend Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### **CI/CD Pipeline**
```yaml
# Automated deployment on git push
Frontend: Git Push → Vercel Build → Deploy → Global CDN
Backend:  Git Push → GCP Cloud Build → Deploy → Cloud Run Container
```

---

## 🔧 **Development Workflow**

### **Local Development Setup**
```bash
# Frontend development
npm run dev                    # Next.js dev server on :3000
npm run test                   # Vitest unit tests
npm run test:e2e              # Playwright E2E tests

# Backend development
python -m backend.run_simple   # FastAPI dev server on :8000
pytest                         # Python tests

# Database
supabase start                 # Local Supabase instance
```

### **Code Quality Tools**
```json
{
  "scripts": {
    "lint": "eslint \"src/**/*.{js,jsx,ts,tsx}\"",
    "type-check": "tsc --noEmit",
    "format": "prettier --write .",
    "test": "vitest",
    "test:e2e": "playwright test"
  }
}
```

---

## 📈 **Performance Optimization**

### **Frontend Optimizations**
- **Code Splitting**: Automatic with Next.js App Router
- **Image Optimization**: Next.js Image component
- **Bundle Analysis**: Webpack bundle analyzer
- **Caching**: Browser and CDN caching strategies
- **Lazy Loading**: Component and route-level lazy loading

### **Backend Optimizations**
- **Database Pooling**: Connection pooling with Supabase
- **Redis Caching**: Multi-layer caching strategy
- **Async Operations**: Full async/await implementation
- **Rate Limiting**: Token bucket algorithm
- **Compression**: Gzip response compression

---

## 🎯 **Key Technical Features**

### **Real-Time Capabilities**
```typescript
// Real-time updates with Supabase
supabase
  .channel('campaign_updates')
  .on('postgres_changes', 
    { event: 'INSERT', schema: 'public', table: 'campaigns' },
    (payload) => updateCampaign(payload.new)
  )
  .subscribe()
```

### **Multi-Tenancy**
```sql
-- Workspace isolation at database level
CREATE POLICY workspace_isolation ON campaigns
  FOR ALL TO authenticated
  USING (workspace_id = current_setting('app.workspace_id')::uuid);
```

### **API Rate Limiting**
```python
# Redis-based rate limiting
async def check_rate_limit(user_id: str, limit: int = 100) -> bool:
    key = f"rate_limit:{user_id}"
    current = await redis.incr(key)
    if current == 1:
        await redis.expire(key, 60)  # 1 minute window
    return current <= limit
```

---

## 🔮 **Scalability Architecture**

### **Horizontal Scaling**
- **Frontend**: Vercel's global edge network
- **Backend**: Render's auto-scaling containers
- **Database**: Supabase's connection pooling
- **Cache**: Upstash's global Redis cluster

### **Performance Metrics**
```javascript
// Core performance targets
{
  "page_load_time": "< 2 seconds",
  "first_contentful_paint": "< 1.5 seconds",
  "api_response_time": "< 500ms",
  "database_query_time": "< 100ms",
  "cache_hit_rate": "> 90%"
}
```

---

## 📚 **API Documentation**

### **OpenAPI Specification**
```yaml
# Auto-generated OpenAPI docs
openapi: 3.0.0
info:
  title: RaptorFlow API
  version: 1.0.0
  description: Marketing Operating System API
```

### **Interactive Documentation**
- **Swagger UI**: Available at `/docs` endpoint
- **ReDoc**: Alternative documentation viewer
- **Postman Collection**: Exportable API collection

---

## 🛠️ **Configuration Management**

### **Environment Variables**
```bash
# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=your-supabase-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SENTRY_DSN=your-sentry-dsn

# Backend (.env)
DATABASE_URL=your-database-url
REDIS_URL=your-redis-url
VERTEX_AI_PROJECT_ID=your-project-id
RESEND_API_KEY=your-resend-key
```

---

## 🎉 **Summary**

RaptorFlow represents a **modern, scalable, and secure marketing operating system** built with:

### **Technical Excellence**
- **Modern Stack**: Next.js 16 + FastAPI + TypeScript
- **Serverless Architecture**: Vercel + Render + Supabase
- **AI Integration**: Vertex AI for intelligent features
- **Real-Time Capabilities**: WebSocket + Redis pub/sub
- **Enterprise Security**: Multi-layer security with RLS

### **Developer Experience**
- **Type Safety**: Full TypeScript coverage
- **Hot Reload**: Fast development cycles
- **Comprehensive Testing**: Unit + E2E test coverage
- **Modern Tooling**: ESLint, Prettier, Playwright
- **Clear Architecture**: Well-structured codebase

### **Production Readiness**
- **Global CDN**: Vercel edge network
- **Auto-Scaling**: Serverless containers
- **Monitoring**: Sentry error tracking
- **Performance**: Optimized for speed
- **Reliability**: 99.9% uptime target

This architecture provides **high performance**, **scalability**, **security**, and **excellent developer experience** while maintaining **cost-effectiveness** and **reliability** for production workloads.

---

## 📞 **Technical Support**

For technical questions or contributions:
- **Documentation**: Comprehensive API and component docs
- **GitHub**: Open source contributions and issues
- **Architecture Decisions**: See ADRs in `/ADRs/` directory
- **Development Guides**: Step-by-step setup instructions
