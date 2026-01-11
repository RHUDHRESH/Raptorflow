# AUTHENTICATION & SESSION ISOLATION

> Solving "Users see everyone's data" problem

---

## 1. THE PROBLEM

**Current Issue**: Users log in and see everyone's data instead of their own.

**Root Causes**:
1. Database queries not scoped to user's workspace
2. Missing Row-Level Security (RLS) policies
3. No workspace context injection in API middleware
4. Frontend not passing workspace context correctly

---

## 2. AUTHENTICATION ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND (Next.js)                                │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Supabase Auth Client                             │   │
│  │                                                                     │   │
│  │  Sign up → Sign in → Session management → Token refresh            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    │ JWT Token (in Authorization header)   │
│                                    ▼                                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           BACKEND (FastAPI)                                 │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Auth Middleware                                  │   │
│  │                                                                     │   │
│  │  1. Extract JWT from Authorization header                          │   │
│  │  2. Verify JWT with Supabase                                       │   │
│  │  3. Extract user_id from JWT claims                                │   │
│  │  4. Lookup workspace_id for user                                   │   │
│  │  5. Inject user + workspace into request state                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Request Context                                  │   │
│  │                                                                     │   │
│  │  request.state.user = {                                            │   │
│  │      id: "user-uuid",                                              │   │
│  │      email: "user@example.com",                                    │   │
│  │      workspace_id: "workspace-uuid"  ← CRITICAL                    │   │
│  │  }                                                                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Database Queries                                 │   │
│  │                                                                     │   │
│  │  ALWAYS filter by workspace_id:                                    │   │
│  │                                                                     │   │
│  │  ✗ WRONG: SELECT * FROM moves                                      │   │
│  │  ✓ RIGHT: SELECT * FROM moves WHERE workspace_id = $1              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. SUPABASE AUTH SETUP

### 3.1 Frontend Auth Configuration

```typescript
// frontend/src/lib/supabase.ts
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true
  }
})

// Auth helper functions
export async function signUp(email: string, password: string) {
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
    options: {
      emailRedirectTo: `${window.location.origin}/auth/callback`
    }
  })

  if (error) throw error
  return data
}

export async function signIn(email: string, password: string) {
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password
  })

  if (error) throw error
  return data
}

export async function signInWithGoogle() {
  const { data, error } = await supabase.auth.signInWithOAuth({
    provider: 'google',
    options: {
      redirectTo: `${window.location.origin}/auth/callback`
    }
  })

  if (error) throw error
  return data
}

export async function signOut() {
  const { error } = await supabase.auth.signOut()
  if (error) throw error
}

export async function getSession() {
  const { data: { session }, error } = await supabase.auth.getSession()
  if (error) throw error
  return session
}

export async function getUser() {
  const { data: { user }, error } = await supabase.auth.getUser()
  if (error) throw error
  return user
}
```

### 3.2 Auth Context Provider

```typescript
// frontend/src/contexts/AuthContext.tsx
'use client'

import { createContext, useContext, useEffect, useState } from 'react'
import { User, Session } from '@supabase/supabase-js'
import { supabase } from '@/lib/supabase'

interface AuthContextType {
  user: User | null
  session: Session | null
  workspaceId: string | null
  loading: boolean
  signIn: (email: string, password: string) => Promise<void>
  signUp: (email: string, password: string) => Promise<void>
  signOut: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [session, setSession] = useState<Session | null>(null)
  const [workspaceId, setWorkspaceId] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session)
      setUser(session?.user ?? null)
      if (session?.user) {
        loadWorkspace(session.user.id)
      }
      setLoading(false)
    })

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        setSession(session)
        setUser(session?.user ?? null)

        if (session?.user) {
          await loadWorkspace(session.user.id)
        } else {
          setWorkspaceId(null)
        }

        setLoading(false)
      }
    )

    return () => subscription.unsubscribe()
  }, [])

  async function loadWorkspace(userId: string) {
    // Get user's primary workspace
    const { data, error } = await supabase
      .from('workspaces')
      .select('id')
      .eq('user_id', userId)
      .single()

    if (data && !error) {
      setWorkspaceId(data.id)
    }
  }

  async function handleSignIn(email: string, password: string) {
    const { error } = await supabase.auth.signInWithPassword({ email, password })
    if (error) throw error
  }

  async function handleSignUp(email: string, password: string) {
    const { error } = await supabase.auth.signUp({ email, password })
    if (error) throw error
  }

  async function handleSignOut() {
    const { error } = await supabase.auth.signOut()
    if (error) throw error
    setWorkspaceId(null)
  }

  return (
    <AuthContext.Provider value={{
      user,
      session,
      workspaceId,
      loading,
      signIn: handleSignIn,
      signUp: handleSignUp,
      signOut: handleSignOut
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
```

### 3.3 Protected Route Middleware

```typescript
// frontend/src/middleware.ts
import { createMiddlewareClient } from '@supabase/auth-helpers-nextjs'
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export async function middleware(req: NextRequest) {
  const res = NextResponse.next()
  const supabase = createMiddlewareClient({ req, res })

  const { data: { session } } = await supabase.auth.getSession()

  // Protect app routes
  if (req.nextUrl.pathname.startsWith('/app') ||
      req.nextUrl.pathname.startsWith('/moves') ||
      req.nextUrl.pathname.startsWith('/campaigns') ||
      req.nextUrl.pathname.startsWith('/muse') ||
      req.nextUrl.pathname.startsWith('/blackbox')) {

    if (!session) {
      const redirectUrl = new URL('/login', req.url)
      redirectUrl.searchParams.set('redirect', req.nextUrl.pathname)
      return NextResponse.redirect(redirectUrl)
    }
  }

  // Redirect logged-in users from auth pages
  if (session && (req.nextUrl.pathname === '/login' || req.nextUrl.pathname === '/signup')) {
    return NextResponse.redirect(new URL('/app', req.url))
  }

  return res
}

export const config = {
  matcher: [
    '/app/:path*',
    '/moves/:path*',
    '/campaigns/:path*',
    '/muse/:path*',
    '/blackbox/:path*',
    '/login',
    '/signup'
  ]
}
```

---

## 4. BACKEND AUTH MIDDLEWARE

### 4.1 JWT Verification

```python
# backend/core/auth.py
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pydantic import BaseModel
import httpx
import os

class AuthenticatedUser(BaseModel):
    """Authenticated user with workspace context."""
    id: str
    email: str
    workspace_id: str
    role: str = "user"

class JWTBearer(HTTPBearer):
    """Custom JWT bearer authentication."""

    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_jwt_secret = os.getenv("SUPABASE_JWT_SECRET")

    async def __call__(self, request: Request) -> AuthenticatedUser:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)

        if not credentials:
            raise HTTPException(status_code=401, detail="Invalid authorization")

        if credentials.scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")

        # Verify JWT
        user = await self.verify_jwt(credentials.credentials)

        # Store in request state for easy access
        request.state.user = user

        return user

    async def verify_jwt(self, token: str) -> AuthenticatedUser:
        """Verify Supabase JWT and extract user info."""
        try:
            # Decode JWT
            payload = jwt.decode(
                token,
                self.supabase_jwt_secret,
                algorithms=["HS256"],
                audience="authenticated"
            )

            user_id = payload.get("sub")
            email = payload.get("email")

            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid token: missing user ID")

            # Get workspace for user
            workspace_id = await self.get_user_workspace(user_id)

            return AuthenticatedUser(
                id=user_id,
                email=email,
                workspace_id=workspace_id
            )

        except JWTError as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    async def get_user_workspace(self, user_id: str) -> str:
        """Get user's primary workspace ID."""
        from .database import get_supabase_client

        supabase = get_supabase_client()

        result = supabase.table("workspaces").select("id").eq(
            "user_id", user_id
        ).single().execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Workspace not found")

        return result.data["id"]


# Dependency for protected routes
auth_required = JWTBearer()

async def get_current_user(
    user: AuthenticatedUser = Depends(auth_required)
) -> AuthenticatedUser:
    """Dependency to get current authenticated user."""
    return user
```

### 4.2 Auth Middleware Integration

```python
# backend/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

class AuthContextMiddleware(BaseHTTPMiddleware):
    """Middleware to inject auth context into all requests."""

    async def dispatch(self, request: Request, call_next):
        # Initialize empty user state
        request.state.user = None
        request.state.workspace_id = None

        # Try to extract auth from header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                from core.auth import JWTBearer
                bearer = JWTBearer(auto_error=False)
                user = await bearer.verify_jwt(auth_header[7:])
                request.state.user = user
                request.state.workspace_id = user.workspace_id
            except:
                pass  # Continue without auth for public routes

        response = await call_next(request)
        return response


app = FastAPI(title="Raptorflow Backend")

# Add middlewares in correct order
app.add_middleware(AuthContextMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.raptorflow.com", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4.3 Protected Endpoint Example

```python
# backend/api/v1/moves.py
from fastapi import APIRouter, Depends, HTTPException
from core.auth import get_current_user, AuthenticatedUser
from core.database import get_supabase_client

router = APIRouter()

@router.get("/")
async def list_moves(
    user: AuthenticatedUser = Depends(get_current_user)
):
    """List moves for the authenticated user's workspace."""

    supabase = get_supabase_client()

    # CRITICAL: Always filter by workspace_id
    result = supabase.table("moves").select("*").eq(
        "workspace_id", user.workspace_id  # ← THIS IS KEY
    ).order("created_at", desc=True).execute()

    return {"moves": result.data}


@router.post("/")
async def create_move(
    move_data: dict,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """Create a new move in user's workspace."""

    supabase = get_supabase_client()

    # CRITICAL: Always set workspace_id on insert
    result = supabase.table("moves").insert({
        **move_data,
        "workspace_id": user.workspace_id  # ← THIS IS KEY
    }).execute()

    return {"move": result.data[0]}


@router.get("/{move_id}")
async def get_move(
    move_id: str,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """Get a specific move, ensuring workspace isolation."""

    supabase = get_supabase_client()

    # CRITICAL: Filter by BOTH move_id AND workspace_id
    result = supabase.table("moves").select("*").eq(
        "id", move_id
    ).eq(
        "workspace_id", user.workspace_id  # ← Prevents accessing other users' moves
    ).single().execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Move not found")

    return {"move": result.data}
```

---

## 5. DATABASE ROW-LEVEL SECURITY (RLS)

### 5.1 Enable RLS on All Tables

```sql
-- Enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE workspaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE foundations ENABLE ROW LEVEL SECURITY;
ALTER TABLE icp_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE moves ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE muse_assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE blackbox_strategies ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_wins ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE onboarding_sessions ENABLE ROW LEVEL SECURITY;
```

### 5.2 RLS Policies

```sql
-- ═══════════════════════════════════════════════════════════════════════════
-- USERS TABLE
-- ═══════════════════════════════════════════════════════════════════════════

-- Users can only see their own profile
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid() = id);

-- Users can only update their own profile
CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid() = id);


-- ═══════════════════════════════════════════════════════════════════════════
-- WORKSPACES TABLE
-- ═══════════════════════════════════════════════════════════════════════════

-- Users can only see their own workspaces
CREATE POLICY "Users can view own workspaces" ON workspaces
    FOR SELECT USING (auth.uid() = user_id);

-- Users can create workspaces for themselves
CREATE POLICY "Users can create own workspaces" ON workspaces
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Users can update their own workspaces
CREATE POLICY "Users can update own workspaces" ON workspaces
    FOR UPDATE USING (auth.uid() = user_id);


-- ═══════════════════════════════════════════════════════════════════════════
-- FOUNDATIONS TABLE
-- ═══════════════════════════════════════════════════════════════════════════

-- Users can only access foundations in their workspaces
CREATE POLICY "Workspace isolation for foundations" ON foundations
    FOR ALL USING (
        workspace_id IN (
            SELECT id FROM workspaces WHERE user_id = auth.uid()
        )
    );


-- ═══════════════════════════════════════════════════════════════════════════
-- ICP PROFILES TABLE
-- ═══════════════════════════════════════════════════════════════════════════

CREATE POLICY "Workspace isolation for icp_profiles" ON icp_profiles
    FOR ALL USING (
        workspace_id IN (
            SELECT id FROM workspaces WHERE user_id = auth.uid()
        )
    );


-- ═══════════════════════════════════════════════════════════════════════════
-- MOVES TABLE
-- ═══════════════════════════════════════════════════════════════════════════

CREATE POLICY "Workspace isolation for moves" ON moves
    FOR ALL USING (
        workspace_id IN (
            SELECT id FROM workspaces WHERE user_id = auth.uid()
        )
    );


-- ═══════════════════════════════════════════════════════════════════════════
-- CAMPAIGNS TABLE
-- ═══════════════════════════════════════════════════════════════════════════

CREATE POLICY "Workspace isolation for campaigns" ON campaigns
    FOR ALL USING (
        workspace_id IN (
            SELECT id FROM workspaces WHERE user_id = auth.uid()
        )
    );


-- ═══════════════════════════════════════════════════════════════════════════
-- MUSE ASSETS TABLE
-- ═══════════════════════════════════════════════════════════════════════════

CREATE POLICY "Workspace isolation for muse_assets" ON muse_assets
    FOR ALL USING (
        workspace_id IN (
            SELECT id FROM workspaces WHERE user_id = auth.uid()
        )
    );


-- ═══════════════════════════════════════════════════════════════════════════
-- BLACKBOX STRATEGIES TABLE
-- ═══════════════════════════════════════════════════════════════════════════

CREATE POLICY "Workspace isolation for blackbox_strategies" ON blackbox_strategies
    FOR ALL USING (
        workspace_id IN (
            SELECT id FROM workspaces WHERE user_id = auth.uid()
        )
    );


-- ═══════════════════════════════════════════════════════════════════════════
-- SERVICE ROLE BYPASS
-- ═══════════════════════════════════════════════════════════════════════════

-- For backend service operations, use service_role key which bypasses RLS
-- This is handled automatically by Supabase when using SUPABASE_SERVICE_KEY
```

### 5.3 Helper Function for Workspace Check

```sql
-- Function to check workspace ownership
CREATE OR REPLACE FUNCTION user_owns_workspace(workspace_uuid UUID)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM workspaces
        WHERE id = workspace_uuid AND user_id = auth.uid()
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Simplified policies using the function
CREATE POLICY "Workspace isolation" ON moves
    FOR ALL USING (user_owns_workspace(workspace_id));
```

---

## 6. USER INITIALIZATION SEQUENCE

### 6.1 New User Signup Flow

```python
# backend/api/v1/auth.py
from fastapi import APIRouter, HTTPException
from core.database import get_supabase_client
import uuid

router = APIRouter()

async def initialize_new_user(user_id: str, email: str):
    """Initialize a new user with workspace and default data."""

    supabase = get_supabase_client()

    # 1. Create user profile
    supabase.table("users").insert({
        "id": user_id,
        "email": email,
        "subscription_tier": "free",
        "budget_limit_monthly": 1.00  # $1 free tier
    }).execute()

    # 2. Create default workspace
    workspace_id = str(uuid.uuid4())
    supabase.table("workspaces").insert({
        "id": workspace_id,
        "user_id": user_id,
        "name": f"{email.split('@')[0]}'s Workspace",
        "slug": f"ws-{workspace_id[:8]}",
        "settings": {}
    }).execute()

    # 3. Create empty foundation
    supabase.table("foundations").insert({
        "workspace_id": workspace_id,
        "onboarding_completed": False,
        "summary": ""
    }).execute()

    # 4. Create onboarding session
    supabase.table("onboarding_sessions").insert({
        "workspace_id": workspace_id,
        "current_step": 1,
        "status": "in_progress"
    }).execute()

    return workspace_id


# Webhook handler for Supabase auth events
@router.post("/webhook/auth")
async def auth_webhook(payload: dict):
    """Handle Supabase auth events."""

    event_type = payload.get("type")

    if event_type == "INSERT" and payload.get("table") == "users":
        # New user signed up via Supabase Auth
        record = payload.get("record", {})
        user_id = record.get("id")
        email = record.get("email")

        if user_id and email:
            await initialize_new_user(user_id, email)

    return {"status": "ok"}
```

### 6.2 Login Flow - Ensuring Correct Data

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

    if (session && !error) {
      // Verify user has a workspace
      const { data: workspace } = await supabase
        .from('workspaces')
        .select('id')
        .eq('user_id', session.user.id)
        .single()

      if (!workspace) {
        // Initialize user if no workspace exists
        await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/initialize`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${session.access_token}`,
            'Content-Type': 'application/json'
          }
        })
      }
    }
  }

  // Redirect to app
  return NextResponse.redirect(new URL('/app', request.url))
}
```

---

## 7. API REQUEST PATTERN

### Every API Call Must Include Auth Token

```typescript
// frontend/src/lib/api.ts
import { supabase } from './supabase'

class ApiClient {
  private baseUrl: string

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  }

  private async getAuthHeaders(): Promise<HeadersInit> {
    const { data: { session } } = await supabase.auth.getSession()

    if (!session?.access_token) {
      throw new Error('Not authenticated')
    }

    return {
      'Authorization': `Bearer ${session.access_token}`,
      'Content-Type': 'application/json'
    }
  }

  async get<T>(endpoint: string): Promise<T> {
    const headers = await this.getAuthHeaders()

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'GET',
      headers
    })

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`)
    }

    return response.json()
  }

  async post<T>(endpoint: string, data: any): Promise<T> {
    const headers = await this.getAuthHeaders()

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers,
      body: JSON.stringify(data)
    })

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`)
    }

    return response.json()
  }

  // ... put, delete, etc.
}

export const api = new ApiClient()

// Usage
const moves = await api.get('/api/v1/moves')
const newMove = await api.post('/api/v1/moves', { category: 'ignite', goal: '...' })
```

---

## 8. CHECKLIST: FIXING USER ISOLATION

```markdown
### Database Level
- [ ] Enable RLS on ALL tables
- [ ] Create workspace isolation policies for ALL tables
- [ ] Verify policies work with test queries

### Backend Level
- [ ] Auth middleware extracts user_id from JWT
- [ ] Auth middleware resolves workspace_id from user_id
- [ ] workspace_id injected into request.state
- [ ] ALL queries filter by workspace_id
- [ ] ALL inserts include workspace_id

### Frontend Level
- [ ] Auth context provides workspaceId
- [ ] All API calls include Authorization header
- [ ] Protected routes redirect to login
- [ ] Session refresh handled automatically

### Testing
- [ ] Create test with two users
- [ ] Verify User A cannot see User B's data
- [ ] Verify User A cannot access User B's endpoints
- [ ] Test RLS policies directly in Supabase SQL Editor
```
