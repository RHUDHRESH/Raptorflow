# API SPECIFICATION & INITIALIZATION

> Complete API Layer + User Initialization Sequences

---

## 1. API STRUCTURE

```
/api/v1/
├── auth/
│   ├── POST /initialize          # Initialize new user
│   └── POST /webhook             # Supabase auth webhook
│
├── agents/
│   ├── POST /execute             # Execute agent request
│   └── POST /execute/stream      # Stream agent response
│
├── onboarding/
│   ├── GET  /session             # Get onboarding session
│   ├── POST /session             # Create onboarding session
│   ├── POST /{sessionId}/vault/upload    # Upload evidence
│   ├── POST /{sessionId}/vault/url       # Process URL
│   ├── POST /{sessionId}/steps/{step}/run    # Run step
│   ├── GET  /{sessionId}/steps/{step}        # Get step data
│   └── POST /{sessionId}/complete            # Complete onboarding
│
├── foundation/
│   ├── GET  /                    # Get foundation
│   ├── PUT  /                    # Update foundation
│   └── GET  /summary             # Get compressed summary
│
├── icps/
│   ├── GET  /                    # List ICPs
│   ├── POST /                    # Create ICP
│   ├── GET  /{id}                # Get ICP
│   ├── PUT  /{id}                # Update ICP
│   ├── DELETE /{id}              # Delete ICP
│   └── POST /{id}/set-primary    # Set as primary
│
├── moves/
│   ├── GET  /                    # List moves
│   ├── POST /                    # Create move
│   ├── GET  /{id}                # Get move
│   ├── PUT  /{id}                # Update move
│   ├── DELETE /{id}              # Delete move
│   ├── POST /{id}/start          # Start move
│   ├── POST /{id}/pause          # Pause move
│   └── POST /{id}/complete       # Complete move
│
├── campaigns/
│   ├── GET  /                    # List campaigns
│   ├── POST /                    # Create campaign
│   ├── GET  /{id}                # Get campaign
│   ├── PUT  /{id}                # Update campaign
│   ├── DELETE /{id}              # Delete campaign
│   └── GET  /{id}/moves          # Get campaign moves
│
├── muse/
│   ├── POST /generate            # Generate content
│   ├── GET  /assets              # List assets
│   ├── GET  /assets/{id}         # Get asset
│   ├── PUT  /assets/{id}         # Update asset
│   ├── DELETE /assets/{id}       # Delete asset
│   └── GET  /templates           # Get templates
│
├── blackbox/
│   ├── POST /generate            # Generate strategy
│   ├── GET  /strategies          # List strategies
│   ├── GET  /strategies/{id}     # Get strategy
│   └── POST /strategies/{id}/accept  # Accept strategy
│
├── daily-wins/
│   ├── POST /generate            # Generate wins
│   ├── GET  /                    # List today's wins
│   └── POST /{id}/mark-posted    # Mark as posted
│
├── billing/
│   ├── GET  /plans               # Get plans
│   ├── GET  /subscription        # Get subscription
│   ├── POST /subscription        # Subscribe
│   ├── GET  /usage               # Get usage
│   └── GET  /invoices            # Get invoices
│
└── webhooks/
    └── POST /phonepe             # PhonePe callback
```

---

## 2. CORE API IMPLEMENTATION

### 2.1 Main FastAPI App

```python
# backend/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from core.config import settings
from core.database import init_database
from core.redis import get_redis
from agents.graph import create_raptorflow_graph

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global graph instance
raptorflow_graph = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    global raptorflow_graph

    logger.info("Starting Raptorflow Backend...")

    # Initialize database
    await init_database()
    logger.info("✓ Database initialized")

    # Verify Redis
    redis = get_redis()
    await redis.set("health:startup", "ok", ex=60)
    logger.info("✓ Redis connected")

    # Compile LangGraph
    raptorflow_graph = create_raptorflow_graph()
    logger.info("✓ LangGraph compiled")

    yield

    # Cleanup
    logger.info("Shutting down...")

app = FastAPI(
    title="Raptorflow API",
    version="6.0.0",
    description="AI-powered marketing automation backend",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://app.raptorflow.com",
        "https://raptorflow.com",
        "http://localhost:3000",
        "http://localhost:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth context middleware
from core.middleware import AuthContextMiddleware
app.add_middleware(AuthContextMiddleware)

# Import routers
from api.v1 import (
    auth, agents, onboarding, foundation, icps,
    moves, campaigns, muse, blackbox, daily_wins, billing
)

# Register routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["Agents"])
app.include_router(onboarding.router, prefix="/api/v1/onboarding", tags=["Onboarding"])
app.include_router(foundation.router, prefix="/api/v1/foundation", tags=["Foundation"])
app.include_router(icps.router, prefix="/api/v1/icps", tags=["ICPs"])
app.include_router(moves.router, prefix="/api/v1/moves", tags=["Moves"])
app.include_router(campaigns.router, prefix="/api/v1/campaigns", tags=["Campaigns"])
app.include_router(muse.router, prefix="/api/v1/muse", tags=["Muse"])
app.include_router(blackbox.router, prefix="/api/v1/blackbox", tags=["BlackBox"])
app.include_router(daily_wins.router, prefix="/api/v1/daily-wins", tags=["Daily Wins"])
app.include_router(billing.router, prefix="/api/v1/billing", tags=["Billing"])

# Health check
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": "6.0.0",
        "graph_ready": raptorflow_graph is not None
    }

# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
```

### 2.2 Auth Middleware

```python
# backend/core/middleware.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt, JWTError
import os

class AuthContextMiddleware(BaseHTTPMiddleware):
    """Inject auth context into all requests."""

    async def dispatch(self, request: Request, call_next):
        # Initialize empty auth state
        request.state.user = None
        request.state.user_id = None
        request.state.workspace_id = None

        # Extract auth header
        auth_header = request.headers.get("Authorization")

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]

            try:
                # Decode JWT
                payload = jwt.decode(
                    token,
                    os.getenv("SUPABASE_JWT_SECRET"),
                    algorithms=["HS256"],
                    audience="authenticated"
                )

                user_id = payload.get("sub")

                if user_id:
                    request.state.user_id = user_id

                    # Get workspace
                    from core.database import get_supabase_client
                    supabase = get_supabase_client()

                    result = supabase.table("workspaces").select("id").eq(
                        "user_id", user_id
                    ).limit(1).execute()

                    if result.data:
                        request.state.workspace_id = result.data[0]["id"]

            except JWTError:
                pass  # Continue without auth

        response = await call_next(request)
        return response
```

### 2.3 Agent Execution Endpoint

```python
# backend/api/v1/agents.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Any, Literal
import json

from core.auth import get_current_user, AuthenticatedUser
from cognitive.engine import CognitiveEngine
from services.cache_manager import CacheManager
from services.usage_tracker import UsageTracker

router = APIRouter()

class AgentRequest(BaseModel):
    request_type: Literal[
        "onboarding", "moves", "campaigns", "muse",
        "blackbox", "daily_wins", "analytics", "foundation"
    ]
    request_data: dict[str, Any]
    stream: bool = False

class AgentResponse(BaseModel):
    success: bool
    output: Any | None = None
    error: str | None = None
    tokens_used: int = 0
    cost: float = 0.0
    requires_approval: bool = False
    approval_gate_id: str | None = None

@router.post("/execute", response_model=AgentResponse)
async def execute_agent(
    request: AgentRequest,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """Execute an agent request."""

    # Check budget
    usage_tracker = UsageTracker()
    estimated_cost = 0.01  # Conservative estimate

    budget = await usage_tracker.check_budget(user.id, estimated_cost)
    if not budget["can_afford"]:
        raise HTTPException(
            status_code=402,
            detail=f"Insufficient budget. Remaining: ${budget['remaining']:.4f}"
        )

    # Get cached context
    cache = CacheManager()
    foundation = await cache.get_foundation(user.workspace_id)
    icps = await cache.get_icps(user.workspace_id)

    # Build user context
    user_context = {
        "user_id": user.id,
        "workspace_id": user.workspace_id,
        "foundation_summary": foundation.get("summary", "") if foundation else "",
        "brand_voice": foundation.get("brand_voice", "professional") if foundation else "professional",
        "icps": icps,
        "has_foundation": foundation is not None,
        "num_icps": len(icps),
        "budget_remaining": budget["remaining"]
    }

    # Execute through cognitive engine
    from core.database import get_supabase_client
    from core.redis import get_redis

    engine = CognitiveEngine(get_supabase_client(), get_redis())

    import uuid
    session_id = str(uuid.uuid4())

    trace = await engine.process(
        raw_input=json.dumps(request.request_data),
        workspace_id=user.workspace_id,
        session_id=session_id,
        user_context=user_context
    )

    # Record usage
    await usage_tracker.record_usage(
        user_id=user.id,
        workspace_id=user.workspace_id,
        tokens_input=trace.total_tokens // 2,
        tokens_output=trace.total_tokens // 2,
        cost_usd=trace.total_cost,
        agent_type=request.request_type
    )

    # Check if approval needed
    if trace.final_output and isinstance(trace.final_output, dict):
        if trace.final_output.get("type") == "approval_required":
            return AgentResponse(
                success=True,
                output=trace.final_output.get("output") or trace.final_output.get("plan"),
                requires_approval=True,
                approval_gate_id=trace.final_output.get("gate_id"),
                tokens_used=trace.total_tokens,
                cost=trace.total_cost
            )

    return AgentResponse(
        success=trace.final_output is not None,
        output=trace.final_output,
        tokens_used=trace.total_tokens,
        cost=trace.total_cost
    )

@router.post("/execute/stream")
async def execute_agent_stream(
    request: AgentRequest,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """Execute agent with streaming response."""

    async def generate():
        # Similar to above but yield chunks
        yield json.dumps({"status": "started"}) + "\n"

        # ... execution logic ...

        yield json.dumps({"status": "complete", "output": {}}) + "\n"

    return StreamingResponse(
        generate(),
        media_type="application/x-ndjson"
    )
```

---

## 3. USER INITIALIZATION SEQUENCE

### 3.1 Complete Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    USER INITIALIZATION SEQUENCE                             │
│                                                                             │
│  1. USER SIGNS UP (Supabase Auth)                                          │
│     │                                                                       │
│     ▼                                                                       │
│  2. SUPABASE TRIGGER fires (on auth.users INSERT)                          │
│     │                                                                       │
│     ▼                                                                       │
│  3. CREATE USER PROFILE (public.users)                                     │
│     │                                                                       │
│     ▼                                                                       │
│  4. CREATE WORKSPACE (workspaces)                                          │
│     │                                                                       │
│     ▼                                                                       │
│  5. CREATE EMPTY FOUNDATION (foundations)                                  │
│     │                                                                       │
│     ▼                                                                       │
│  6. CREATE ONBOARDING SESSION (onboarding_sessions)                        │
│     │                                                                       │
│     ▼                                                                       │
│  7. CREATE FREE SUBSCRIPTION (subscriptions)                               │
│     │                                                                       │
│     ▼                                                                       │
│  8. REDIRECT TO ONBOARDING (frontend)                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Database Triggers

```sql
-- Trigger 1: Create user profile
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.users (id, email, full_name)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', SPLIT_PART(NEW.email, '@', 1))
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();


-- Trigger 2: Create workspace and related entities
CREATE OR REPLACE FUNCTION public.handle_new_user_workspace()
RETURNS TRIGGER AS $$
DECLARE
    v_workspace_id UUID;
BEGIN
    -- Create workspace
    v_workspace_id := gen_random_uuid();

    INSERT INTO workspaces (id, user_id, name, slug)
    VALUES (
        v_workspace_id,
        NEW.id,
        CONCAT(SPLIT_PART(NEW.email, '@', 1), '''s Workspace'),
        CONCAT('ws-', LEFT(v_workspace_id::TEXT, 8))
    );

    -- Create empty foundation
    INSERT INTO foundations (workspace_id, summary, onboarding_completed)
    VALUES (v_workspace_id, '', FALSE);

    -- Create onboarding session
    INSERT INTO onboarding_sessions (workspace_id, current_step, status)
    VALUES (v_workspace_id, 1, 'in_progress');

    -- Create free subscription
    INSERT INTO subscriptions (user_id, plan, status, price_inr)
    VALUES (NEW.id, 'free', 'active', 0);

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_user_profile_created
    AFTER INSERT ON public.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user_workspace();
```

### 3.3 Backend Initialization Endpoint

```python
# backend/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException
from core.auth import get_current_user, AuthenticatedUser
from core.database import get_supabase_client

router = APIRouter()

@router.post("/initialize")
async def initialize_user(user: AuthenticatedUser = Depends(get_current_user)):
    """Initialize user if not already done (fallback for trigger failures)."""

    supabase = get_supabase_client()

    # Check if workspace exists
    workspace = supabase.table("workspaces").select("id").eq(
        "user_id", user.id
    ).execute()

    if workspace.data:
        return {"status": "already_initialized", "workspace_id": workspace.data[0]["id"]}

    # Create workspace
    import uuid
    workspace_id = str(uuid.uuid4())

    supabase.table("workspaces").insert({
        "id": workspace_id,
        "user_id": user.id,
        "name": f"My Workspace",
        "slug": f"ws-{workspace_id[:8]}"
    }).execute()

    # Create foundation
    supabase.table("foundations").insert({
        "workspace_id": workspace_id,
        "summary": "",
        "onboarding_completed": False
    }).execute()

    # Create onboarding session
    supabase.table("onboarding_sessions").insert({
        "workspace_id": workspace_id,
        "current_step": 1,
        "status": "in_progress"
    }).execute()

    # Create free subscription
    existing_sub = supabase.table("subscriptions").select("id").eq(
        "user_id", user.id
    ).execute()

    if not existing_sub.data:
        supabase.table("subscriptions").insert({
            "user_id": user.id,
            "plan": "free",
            "status": "active",
            "price_inr": 0
        }).execute()

    return {"status": "initialized", "workspace_id": workspace_id}

@router.get("/me")
async def get_me(user: AuthenticatedUser = Depends(get_current_user)):
    """Get current user with workspace info."""

    supabase = get_supabase_client()

    # Get user profile
    user_data = supabase.table("users").select("*").eq("id", user.id).single().execute()

    # Get workspace
    workspace = supabase.table("workspaces").select("*").eq(
        "user_id", user.id
    ).single().execute()

    # Get subscription
    subscription = supabase.table("subscriptions").select("*").eq(
        "user_id", user.id
    ).single().execute()

    # Get onboarding status
    onboarding = None
    if workspace.data:
        onboarding = supabase.table("onboarding_sessions").select(
            "current_step, status"
        ).eq("workspace_id", workspace.data["id"]).single().execute()

    return {
        "user": user_data.data,
        "workspace": workspace.data,
        "subscription": subscription.data,
        "onboarding": onboarding.data if onboarding else None
    }
```

### 3.4 Frontend Auth Flow

```typescript
// frontend/src/app/auth/callback/route.ts
import { createRouteHandlerClient } from '@supabase/auth-helpers-nextjs'
import { cookies } from 'next/headers'
import { NextResponse } from 'next/server'

export async function GET(request: Request) {
  const requestUrl = new URL(request.url)
  const code = requestUrl.searchParams.get('code')

  if (code) {
    const supabase = createRouteHandlerClient({ cookies })

    // Exchange code for session
    const { data: { session }, error } = await supabase.auth.exchangeCodeForSession(code)

    if (!error && session) {
      // Initialize user on backend (in case triggers failed)
      try {
        await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/initialize`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${session.access_token}`
          }
        })
      } catch (e) {
        console.error('Failed to initialize user:', e)
      }

      // Check onboarding status
      const { data: onboarding } = await supabase
        .from('onboarding_sessions')
        .select('status')
        .single()

      if (onboarding?.status === 'in_progress') {
        return NextResponse.redirect(new URL('/onboarding', request.url))
      }
    }
  }

  return NextResponse.redirect(new URL('/app', request.url))
}
```

---

## 4. SESSION DATA FLOW

### 4.1 How User Gets Their Own Data

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         DATA ISOLATION FLOW                                  │
│                                                                              │
│  1. FRONTEND makes request with JWT token                                    │
│     │                                                                        │
│     │  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...        │
│     │                                                                        │
│     ▼                                                                        │
│  2. AUTH MIDDLEWARE extracts user_id from JWT                                │
│     │                                                                        │
│     │  jwt.decode(token) → { sub: "user-uuid-123" }                         │
│     │                                                                        │
│     ▼                                                                        │
│  3. MIDDLEWARE looks up workspace_id for user                                │
│     │                                                                        │
│     │  SELECT id FROM workspaces WHERE user_id = 'user-uuid-123'            │
│     │  → workspace_id = "workspace-uuid-456"                                 │
│     │                                                                        │
│     ▼                                                                        │
│  4. MIDDLEWARE injects into request.state                                    │
│     │                                                                        │
│     │  request.state.user_id = "user-uuid-123"                              │
│     │  request.state.workspace_id = "workspace-uuid-456"                     │
│     │                                                                        │
│     ▼                                                                        │
│  5. API ENDPOINT uses workspace_id in ALL queries                            │
│     │                                                                        │
│     │  SELECT * FROM moves WHERE workspace_id = 'workspace-uuid-456'        │
│     │                                                                        │
│     ▼                                                                        │
│  6. RLS POLICY enforces isolation at database level                          │
│     │                                                                        │
│     │  Policy: user_owns_workspace(workspace_id) must be TRUE               │
│     │                                                                        │
│     ▼                                                                        │
│  7. USER receives ONLY their own data                                        │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Example: Get Moves Endpoint

```python
# backend/api/v1/moves.py
from fastapi import APIRouter, Depends, HTTPException, Query
from core.auth import get_current_user, AuthenticatedUser
from core.database import get_supabase_client
from pydantic import BaseModel
from typing import Literal

router = APIRouter()

class MoveCreate(BaseModel):
    category: Literal["ignite", "capture", "authority", "repair", "rally"]
    goal: str
    duration_days: int = 7
    target_icp_id: str | None = None

@router.get("/")
async def list_moves(
    status: str | None = Query(None),
    limit: int = Query(20, le=100),
    offset: int = Query(0),
    user: AuthenticatedUser = Depends(get_current_user)
):
    """List moves for current user's workspace."""

    supabase = get_supabase_client()

    # Build query - ALWAYS filter by workspace_id
    query = supabase.table("moves").select(
        "*, target_icp:icp_profiles(id, name)"
    ).eq(
        "workspace_id", user.workspace_id  # ← CRITICAL
    ).order("created_at", desc=True)

    if status:
        query = query.eq("status", status)

    query = query.range(offset, offset + limit - 1)

    result = query.execute()

    return {
        "moves": result.data,
        "total": len(result.data),
        "limit": limit,
        "offset": offset
    }

@router.post("/")
async def create_move(
    move: MoveCreate,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """Create a new move."""

    supabase = get_supabase_client()

    # ALWAYS include workspace_id
    result = supabase.table("moves").insert({
        "workspace_id": user.workspace_id,  # ← CRITICAL
        "category": move.category,
        "name": f"New {move.category.capitalize()} Move",
        "goal": move.goal,
        "duration_days": move.duration_days,
        "target_icp_id": move.target_icp_id,
        "status": "draft"
    }).execute()

    return {"move": result.data[0]}

@router.get("/{move_id}")
async def get_move(
    move_id: str,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """Get a specific move."""

    supabase = get_supabase_client()

    # Filter by BOTH id AND workspace_id
    result = supabase.table("moves").select(
        "*, target_icp:icp_profiles(*), tasks:move_tasks(*)"
    ).eq(
        "id", move_id
    ).eq(
        "workspace_id", user.workspace_id  # ← PREVENTS accessing other users' moves
    ).single().execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Move not found")

    return {"move": result.data}

@router.put("/{move_id}")
async def update_move(
    move_id: str,
    updates: dict,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """Update a move."""

    supabase = get_supabase_client()

    # Verify ownership first
    existing = supabase.table("moves").select("id").eq(
        "id", move_id
    ).eq(
        "workspace_id", user.workspace_id
    ).single().execute()

    if not existing.data:
        raise HTTPException(status_code=404, detail="Move not found")

    # Remove protected fields
    updates.pop("id", None)
    updates.pop("workspace_id", None)
    updates.pop("created_at", None)

    result = supabase.table("moves").update(updates).eq(
        "id", move_id
    ).execute()

    return {"move": result.data[0]}

@router.delete("/{move_id}")
async def delete_move(
    move_id: str,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """Delete a move."""

    supabase = get_supabase_client()

    # Delete with workspace check
    result = supabase.table("moves").delete().eq(
        "id", move_id
    ).eq(
        "workspace_id", user.workspace_id
    ).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Move not found")

    return {"deleted": True}
```

---

## 5. CHECKLIST: COMPLETE BACKEND

### Infrastructure
- [ ] FastAPI app with lifespan management
- [ ] Supabase PostgreSQL with all tables
- [ ] pgvector extension enabled
- [ ] All RLS policies applied
- [ ] Upstash Redis configured
- [ ] Vertex AI credentials set
- [ ] PhonePe credentials set
- [ ] Environment variables configured

### Authentication
- [ ] JWT verification middleware
- [ ] Workspace lookup per request
- [ ] User initialization triggers
- [ ] Protected routes enforced

### Data Isolation
- [ ] ALL queries filter by workspace_id
- [ ] ALL inserts include workspace_id
- [ ] RLS policies active on all tables
- [ ] No data leaks in responses

### Agents
- [ ] LangGraph compiled at startup
- [ ] Routing pipeline (Semantic → HLK → Intent)
- [ ] All specialist agents implemented
- [ ] Skill system with registry and executor
- [ ] Tool integrations working

### Memory
- [ ] Vector store (pgvector) operational
- [ ] Graph store implemented
- [ ] Episodic memory storing conversations
- [ ] Working memory in Redis
- [ ] Context compression working

### Payments
- [ ] PhonePe integration complete
- [ ] Subscription management working
- [ ] Usage tracking per user
- [ ] Budget enforcement active
- [ ] GST invoice generation

### Testing
- [ ] Unit tests for core modules
- [ ] Integration tests for API endpoints
- [ ] Multi-user isolation tests
- [ ] Load testing completed
- [ ] Security audit passed
