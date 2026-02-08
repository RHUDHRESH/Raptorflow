# RaptorFlow SaaS Production Roadmap

> **Generated**: December 2024
> **Status**: Comprehensive audit of scalability, security, and production readiness
> **Goal**: Scale to thousands of concurrent users with enterprise-grade reliability

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [MUST FIX - Critical User Experience Issues](#must-fix---critical-user-experience-issues)
3. [MUST FIX - Critical Security Issues](#must-fix---critical-security-issues)
4. [MUST FIX - Scalability Blockers](#must-fix---scalability-blockers)
5. [MUST BUILD - Missing Infrastructure](#must-build---missing-infrastructure)
6. [MUST IMPROVE - Performance Optimization](#must-improve---performance-optimization)
7. [MUST ADD - Observability & Monitoring](#must-add---observability--monitoring)
8. [MUST CLEAN - Technical Debt](#must-clean---technical-debt)
9. [Architecture Strengths (Already Done)](#architecture-strengths-already-done)
10. [Implementation Priority Matrix](#implementation-priority-matrix)
11. [Estimated Timeline](#estimated-timeline)

---

## Executive Summary

RaptorFlow has a **solid foundation** with FastAPI, LangGraph, Supabase, Redis caching, rate limiting, and GCS storage. However, several **critical gaps** must be addressed before scaling to many users:

| Category | Critical (P0) | High (P1) | Medium (P2) |
|----------|---------------|-----------|-------------|
| **User Experience** | 4 | 4 | 3 |
| Security | 3 | 2 | 4 |
| Scalability | 2 | 3 | 2 |
| Infrastructure | 1 | 4 | 3 |
| Performance | 2 | 3 | 5 |
| **Total** | **12** | **16** | **17** |

### 🚨 Most Urgent Issues

1. **Auth is BYPASSED** - Anyone can access protected pages
2. **All users see SAME data** - Loading from static JSON, not user's workspace
3. **Login doesn't persist** - Users must re-login on every visit
4. **Multi-tenant data leakage** - DB queries missing workspace filters

---

## MUST FIX - Critical User Experience Issues

> **These issues directly impact user retention and satisfaction. Users will leave if login doesn't persist, data isn't theirs, or navigation is frustrating.**

### 🔴 P0-UX-1: Authentication Not Enforced (AuthGuard Bypassed)

**Current State**: Authentication is **completely disabled** for development
**Impact**: Anyone can access any page without logging in
**File**: `raptorflow-app/src/components/auth/AuthGuard.tsx`

```tsx
// CURRENT - LINE 15-17 (BYPASSED!)
export function AuthGuard({ children }: AuthGuardProps) {
  // BYPASS: Render children directly without auth check
  return <>{children}</>;
```

**Also bypassed in middleware**:
```typescript
// raptorflow-app/src/proxy.ts - LINE 88-91
if (isProtectedRoute && !user) {
  // BYPASS AUTH FOR LOCAL DEV
  // return NextResponse.redirect(new URL('/login', request.url))
}
```

#### Fix Required:

```tsx
// AuthGuard.tsx - UNCOMMENT AND ENABLE
export function AuthGuard({ children }: AuthGuardProps) {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);
  const router = useRouter();

  useEffect(() => {
    async function checkAuth() {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) {
        router.push('/login');
      } else {
        setIsAuthenticated(true);
      }
    }
    checkAuth();

    // Listen for auth state changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        if (!session) {
          router.push('/login');
        }
      }
    );

    return () => subscription.unsubscribe();
  }, [router]);

  if (isAuthenticated === null) {
    return <LoadingSpinner />;
  }

  return <>{children}</>;
}
```

```typescript
// proxy.ts - ENABLE REDIRECT
if (isProtectedRoute && !user) {
  return NextResponse.redirect(new URL('/login', request.url));
}
```

---

### 🔴 P0-UX-2: Session Not Persisted Across Browser Sessions

**Current State**: Supabase session stored in cookies, but not properly refreshed
**Impact**: User has to log in every time they close browser
**Cause**: Missing session refresh logic and proper cookie persistence

#### What's Missing:

1. **No automatic token refresh** when session expires
2. **No "remember me" functionality**
3. **Cookies may not persist** due to missing `maxAge` or `expires`

#### Fix Required:

```typescript
// Create: raptorflow-app/src/lib/auth-provider.tsx

'use client';
import { createContext, useContext, useEffect, useState } from 'react';
import { supabase } from './supabase';
import { User, Session } from '@supabase/supabase-js';

interface AuthContextType {
  user: User | null;
  session: Session | null;
  loading: boolean;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      setUser(session?.user ?? null);
      setLoading(false);
    });

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        setSession(session);
        setUser(session?.user ?? null);

        // Auto-refresh token before expiry
        if (event === 'TOKEN_REFRESHED') {
          console.log('Token refreshed successfully');
        }

        if (event === 'SIGNED_OUT') {
          // Clear all local state
          localStorage.removeItem('raptorflow-onboarding');
        }
      }
    );

    return () => subscription.unsubscribe();
  }, []);

  const signOut = async () => {
    await supabase.auth.signOut();
    setUser(null);
    setSession(null);
  };

  return (
    <AuthContext.Provider value={{ user, session, loading, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};
```

---

### 🔴 P0-UX-3: No User-Workspace Association

**Current State**: Onboarding data stored in localStorage without user ID
**Impact**:
- Different users on same computer see same data
- User's data not tied to their account
- Data lost when localStorage cleared

**File**: `raptorflow-app/src/stores/onboardingStore.ts`

```typescript
// CURRENT - LINE 618-630
persist(
  (set, get) => ({ ... }),
  {
    name: 'raptorflow-onboarding',  // NO USER ID! Same key for everyone
    partialize: (state) => ({ ... }),
  }
)
```

#### Fix Required:

```typescript
// onboardingStore.ts - User-scoped storage key

import { supabase } from '@/lib/supabase';

// Dynamic storage key based on user ID
const getStorageKey = async () => {
  const { data: { user } } = await supabase.auth.getUser();
  return user ? `raptorflow-onboarding-${user.id}` : 'raptorflow-onboarding-guest';
};

export const useOnboardingStore = create<OnboardingState>()(
  persist(
    (set, get) => ({
      // ... existing state

      // Add user context
      userId: null,
      workspaceId: null,

      initializeForUser: async () => {
        const { data: { user } } = await supabase.auth.getUser();
        if (user) {
          // Load user's data from backend
          const workspaceId = await getWorkspaceId();
          set({ userId: user.id, workspaceId });

          // Sync with backend
          await get().syncFromBackend();
        }
      },

      syncFromBackend: async () => {
        const state = get();
        if (!state.workspaceId) return;

        // Load saved foundation state from Supabase
        const { data } = await supabase
          .from('foundation_state')
          .select('*')
          .eq('tenant_id', state.workspaceId)
          .single();

        if (data?.phase_progress) {
          // Merge backend state with local state
          set({ ...data.phase_progress });
        }
      },

      syncToBackend: async () => {
        const state = get();
        if (!state.workspaceId) return;

        await supabase
          .from('foundation_state')
          .upsert({
            tenant_id: state.workspaceId,
            phase_progress: state.exportFoundationJSON(),
            updated_at: new Date().toISOString(),
          });
      },
    }),
    {
      name: 'raptorflow-onboarding',
      // Storage will be initialized after user auth
      storage: createJSONStorage(() => localStorage),
    }
  )
);
```

---

### 🔴 P0-UX-4: Foundation Data Loaded from Static JSON, Not User's Data

**Current State**: FoundationProvider loads from `/foundation_test.json`
**Impact**: All users see the SAME demo data, not their own
**File**: `raptorflow-app/src/context/FoundationProvider.tsx`

```typescript
// CURRENT - LINE 51-53
const FOUNDATION_METADATA_PATH =
  process.env.NEXT_PUBLIC_FOUNDATION_METADATA_PATH || '/foundation_test.json';
```

#### Fix Required:

```typescript
// FoundationProvider.tsx - Load user's data from backend

export function FoundationProvider({ children }: { children: ReactNode }) {
  const [foundation, setFoundation] = useState<FoundationData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadFoundation = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      // 1. Get authenticated user
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) {
        throw new Error('Not authenticated');
      }

      // 2. Get user's workspace
      const workspaceId = await getWorkspaceId();
      if (!workspaceId) {
        throw new Error('No workspace found');
      }

      // 3. Load foundation from backend API
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/foundation/${workspaceId}`,
        {
          headers: await getAuthHeaders(),
        }
      );

      if (!response.ok) {
        // If no data yet, return empty foundation
        if (response.status === 404) {
          setFoundation(null);
          return;
        }
        throw new Error('Failed to load foundation');
      }

      const data = await response.json();
      setFoundation(data);

    } catch (err) {
      console.error('Failed to load foundation:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadFoundation();
  }, [loadFoundation]);

  // ... rest of component
}
```

---

### 🟠 P1-UX-5: Scroll Position Lost on Navigation

**Current State**: When navigating between sections, page jumps to top
**Impact**: Frustrating UX when switching tabs or sections
**Cause**: No scroll position preservation

#### Fix Required:

```typescript
// Create: raptorflow-app/src/hooks/useScrollPosition.ts

import { useEffect, useRef } from 'react';
import { usePathname } from 'next/navigation';

const scrollPositions = new Map<string, number>();

export function useScrollPosition() {
  const pathname = usePathname();
  const scrollRef = useRef<HTMLDivElement>(null);

  // Restore scroll position when route changes
  useEffect(() => {
    const savedPosition = scrollPositions.get(pathname);
    if (savedPosition && scrollRef.current) {
      scrollRef.current.scrollTop = savedPosition;
    }
  }, [pathname]);

  // Save scroll position before leaving
  useEffect(() => {
    const element = scrollRef.current;
    if (!element) return;

    const handleScroll = () => {
      scrollPositions.set(pathname, element.scrollTop);
    };

    element.addEventListener('scroll', handleScroll);
    return () => element.removeEventListener('scroll', handleScroll);
  }, [pathname]);

  return scrollRef;
}
```

```tsx
// Usage in layout
export function DashboardLayout({ children }) {
  const scrollRef = useScrollPosition();

  return (
    <div ref={scrollRef} className="overflow-auto h-screen">
      {children}
    </div>
  );
}
```

---

### 🟠 P1-UX-6: Form State Lost on Tab Switch

**Current State**: In-progress form data lost when switching tabs
**Impact**: User loses work when navigating away
**Cause**: State not persisted mid-form

#### Fix Required:

```typescript
// Auto-save form state with debouncing

import { useEffect, useCallback } from 'react';
import { useDebouncedCallback } from 'use-debounce';

export function useFormPersistence(
  formId: string,
  formData: any,
  setFormData: (data: any) => void
) {
  // Save to sessionStorage on every change (debounced)
  const saveForm = useDebouncedCallback((data: any) => {
    sessionStorage.setItem(`form-${formId}`, JSON.stringify(data));
  }, 500);

  // Auto-save on changes
  useEffect(() => {
    saveForm(formData);
  }, [formData, saveForm]);

  // Restore on mount
  useEffect(() => {
    const saved = sessionStorage.getItem(`form-${formId}`);
    if (saved) {
      try {
        setFormData(JSON.parse(saved));
      } catch (e) {
        console.error('Failed to restore form state');
      }
    }
  }, [formId, setFormData]);

  // Clear on successful submit
  const clearSavedForm = useCallback(() => {
    sessionStorage.removeItem(`form-${formId}`);
  }, [formId]);

  return { clearSavedForm };
}
```

---

### 🟠 P1-UX-7: No Workspace Switcher for Multi-Workspace Users

**Current State**: User can only access one workspace
**Impact**: Agencies/consultants can't manage multiple clients
**Schema**: `workspace_members` table exists but no UI

#### Fix Required:

```tsx
// Create: raptorflow-app/src/components/WorkspaceSwitcher.tsx

'use client';
import { useState, useEffect } from 'react';
import { supabase } from '@/lib/supabase';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { ChevronDown, Building2, Plus } from 'lucide-react';

interface Workspace {
  id: string;
  name: string;
  role: string;
}

export function WorkspaceSwitcher() {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [currentWorkspace, setCurrentWorkspace] = useState<Workspace | null>(null);

  useEffect(() => {
    loadWorkspaces();
  }, []);

  const loadWorkspaces = async () => {
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) return;

    const { data } = await supabase
      .from('workspace_members')
      .select(`
        workspace_id,
        role,
        workspaces:workspace_id (
          id,
          name
        )
      `)
      .eq('user_id', user.id);

    if (data) {
      const ws = data.map((d: any) => ({
        id: d.workspace_id,
        name: d.workspaces?.name || 'Unnamed Workspace',
        role: d.role,
      }));
      setWorkspaces(ws);

      // Set current from localStorage or first
      const savedId = localStorage.getItem('currentWorkspaceId');
      const current = ws.find(w => w.id === savedId) || ws[0];
      setCurrentWorkspace(current);
    }
  };

  const switchWorkspace = (workspace: Workspace) => {
    setCurrentWorkspace(workspace);
    localStorage.setItem('currentWorkspaceId', workspace.id);
    // Reload data for new workspace
    window.location.reload();
  };

  if (!currentWorkspace) return null;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-accent">
        <Building2 className="w-4 h-4" />
        <span className="font-medium">{currentWorkspace.name}</span>
        <ChevronDown className="w-4 h-4 opacity-50" />
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" className="w-56">
        {workspaces.map((ws) => (
          <DropdownMenuItem
            key={ws.id}
            onClick={() => switchWorkspace(ws)}
            className={ws.id === currentWorkspace.id ? 'bg-accent' : ''}
          >
            <Building2 className="w-4 h-4 mr-2" />
            <span>{ws.name}</span>
            <span className="ml-auto text-xs text-muted-foreground">{ws.role}</span>
          </DropdownMenuItem>
        ))}
        <DropdownMenuItem className="text-primary">
          <Plus className="w-4 h-4 mr-2" />
          Create Workspace
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
```

---

### 🟠 P1-UX-8: No User Profile or Account Settings

**Current State**: No way for user to:
- See their email/profile
- Change account settings
- Manage team members
- View billing/subscription

#### Fix Required:

Create these pages:
- `/settings/profile` - User profile & preferences
- `/settings/team` - Invite/manage team members
- `/settings/billing` - Subscription & invoices
- `/settings/workspace` - Workspace settings

---

### 🟡 P2-UX-9: No Loading States During Data Fetch

**Current State**: Pages show blank or stale content during loading
**Impact**: User thinks app is broken

#### Fix Required:

```tsx
// Add skeleton loaders for all data-dependent components

export function CampaignsSkeleton() {
  return (
    <div className="space-y-4">
      {[1, 2, 3].map((i) => (
        <div key={i} className="h-24 rounded-xl bg-muted animate-pulse" />
      ))}
    </div>
  );
}

// Use in page:
export default function CampaignsPage() {
  const { data, isLoading } = useCampaigns();

  if (isLoading) return <CampaignsSkeleton />;

  return <CampaignsList campaigns={data} />;
}
```

---

### 🟡 P2-UX-10: No Optimistic Updates

**Current State**: User must wait for backend confirmation
**Impact**: App feels slow and unresponsive

#### Fix Required:

```typescript
// Use optimistic updates with rollback

async function createCampaign(campaign: NewCampaign) {
  // 1. Optimistically add to UI
  const tempId = `temp-${Date.now()}`;
  setCampaigns(prev => [...prev, { ...campaign, id: tempId }]);

  try {
    // 2. Send to backend
    const result = await api.createCampaign(campaign);

    // 3. Replace temp with real
    setCampaigns(prev =>
      prev.map(c => c.id === tempId ? result : c)
    );
  } catch (error) {
    // 4. Rollback on error
    setCampaigns(prev => prev.filter(c => c.id !== tempId));
    toast.error('Failed to create campaign');
  }
}
```

---

### 🟡 P2-UX-11: No Offline Support

**Current State**: App fails completely when offline
**Impact**: Users lose work in poor connectivity

#### Future Enhancement:

- Add service worker for offline caching
- Queue mutations when offline
- Sync when back online
- Show offline indicator

---

## User Experience Priority Summary

| Priority | Issue | Impact | Effort |
|----------|-------|--------|--------|
| **P0** | Auth bypassed | Anyone can access | 1h |
| **P0** | Session not persistent | Login every time | 2h |
| **P0** | No user-workspace link | Wrong data shown | 3h |
| **P0** | Static demo data | Same data for all | 2h |
| **P1** | Scroll position lost | Frustrating nav | 1h |
| **P1** | Form state lost | Lost work | 2h |
| **P1** | No workspace switcher | Can't multi-tenant | 3h |
| **P1** | No settings pages | Can't manage account | 4h |
| **P2** | No loading states | Looks broken | 2h |
| **P2** | No optimistic updates | Feels slow | 3h |
| **P2** | No offline support | Fails offline | 8h |

---

## MUST FIX - Critical Security Issues

### 🔴 P0-SEC-1: Multi-Tenant Data Leakage in Database Operations

**Risk**: Users can access/modify other tenants' data
**Impact**: Complete data breach, GDPR violation
**Effort**: 2-3 hours

#### Affected Files:

| File | Function | Issue |
|------|----------|-------|
| `backend/db.py#L1271-L1283` | `update_move_status()` | Filters only by `move_id`, no `workspace_id` |
| `backend/db.py#L1286-L1296` | `update_move_description()` | Filters only by `move_id`, no `workspace_id` |
| `backend/api/v1/campaigns.py#L226-L245` | `get_campaign_gantt()` | Missing workspace validation |
| `backend/api/v1/campaigns.py#L247-L274` | `generate_campaign_arc()` | Missing workspace validation |
| `backend/api/v1/campaigns.py#L276-L297` | `get_campaign_arc_status()` | Missing workspace validation |
| `backend/api/v1/blackbox_learning.py#L26` | `get_learning_feed()` | Called without tenant context |
| `backend/api/v1/foundation.py#L60` | `get_brand_kit()` | Called with only global ID |

#### Fix Required:

```python
# BEFORE (VULNERABLE)
async def update_move_status(move_id: str, status: str, result: dict = None):
    query = """
        UPDATE moves
        SET status = %s, execution_result = %s, updated_at = now()
        WHERE id = %s;
    """

# AFTER (SECURE)
async def update_move_status(move_id: str, workspace_id: str, status: str, result: dict = None):
    query = """
        UPDATE moves
        SET status = %s, execution_result = %s, updated_at = now()
        WHERE id = %s AND workspace_id = %s;
    """
```

---

### 🔴 P0-SEC-2: Missing RLS on Critical Tables

**Risk**: Database-level data leakage
**Impact**: Even if API is secure, direct DB access exposes all data
**Effort**: 1 hour

#### Tables Without RLS:

| Table | Contains | Risk Level |
|-------|----------|------------|
| `blackbox_telemetry_industrial` | Agent execution traces, tokens | HIGH |
| `blackbox_outcomes_industrial` | Business outcomes, ROI data | HIGH |
| `agent_decision_audit` | AI decision logs | MEDIUM |
| `agent_heuristics` | Never/Always rules | MEDIUM |
| `agent_exploits` | Proven strategies | MEDIUM |
| `entity_embeddings` | Research embeddings | MEDIUM |

#### Fix Required:

```sql
-- Add to new migration: 014_add_missing_rls.sql

ALTER TABLE blackbox_telemetry_industrial ENABLE ROW LEVEL SECURITY;
CREATE POLICY telemetry_workspace_policy ON blackbox_telemetry_industrial
    FOR ALL USING (workspace_id = current_setting('app.current_workspace_id', true)::UUID);

ALTER TABLE blackbox_outcomes_industrial ENABLE ROW LEVEL SECURITY;
CREATE POLICY outcomes_workspace_policy ON blackbox_outcomes_industrial
    FOR ALL USING (workspace_id = current_setting('app.current_workspace_id', true)::UUID);

ALTER TABLE agent_decision_audit ENABLE ROW LEVEL SECURITY;
CREATE POLICY audit_tenant_policy ON agent_decision_audit
    FOR ALL USING (tenant_id = current_setting('app.current_workspace_id', true)::UUID);

-- Repeat for other tables...
```

---

### 🔴 P0-SEC-3: Inconsistent Tenant ID Column Names

**Risk**: Query bypass due to wrong column name
**Impact**: Data leakage through column mismatch
**Effort**: 4 hours

#### Current State:

| Table | Column Used | Should Be |
|-------|-------------|-----------|
| campaigns | `tenant_id` | `workspace_id` (standardize) |
| moves | `tenant_id` | `workspace_id` (standardize) |
| subscriptions | `workspace_id` | ✅ Correct |
| blackbox_telemetry | Both used inconsistently | Standardize to `workspace_id` |

#### Fix Required:

1. Create migration to rename `tenant_id` → `workspace_id` across all tables
2. Update all service/API code to use `workspace_id` consistently
3. Use `resolve_tenant_column()` function in `db.py` during transition

---

## MUST FIX - Scalability Blockers

### 🔴 P0-SCALE-1: Synchronous Blocking in Async Context

**Risk**: Event loop blocked, all concurrent requests stall
**Impact**: App becomes unresponsive under load
**Effort**: 4-6 hours

#### Affected Code:

| File | Issue | Impact |
|------|-------|--------|
| `backend/services/blackbox_service.py` | **All 30+ methods are sync `def`** | Blocks event loop |
| `blackbox_service.py#L178-189` | `stream_to_bigquery()` - sync BigQuery call | 200-500ms blocking |
| `blackbox_service.py#L239-250` | `stream_outcome_to_bigquery()` - sync | 200-500ms blocking |
| `blackbox_service.py#L377-420` | `get_longitudinal_analysis()` - heavy BQ query | 2-10s blocking |

#### Fix Options:

**Option A: Convert to Async (Recommended)**
```python
# BEFORE
def log_telemetry(self, telemetry: BlackboxTelemetry, ...):
    session = self.vault.get_session()
    session.table("blackbox_telemetry_industrial").insert(data).execute()

# AFTER
async def log_telemetry(self, telemetry: BlackboxTelemetry, ...):
    session = self.vault.get_session()
    await asyncio.to_thread(
        lambda: session.table("blackbox_telemetry_industrial").insert(data).execute()
    )
```

**Option B: Run in Thread Pool**
```python
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=10)

async def log_telemetry_async(self, telemetry):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, self.log_telemetry, telemetry)
```

---

### 🔴 P0-SCALE-2: BigQuery Streaming in Request Path

**Risk**: 200-500ms added to every telemetry write
**Impact**: Slow API responses, poor UX
**Effort**: 3-4 hours

#### Current Flow:
```
Request → log_telemetry() → Supabase INSERT → BigQuery INSERT (BLOCKING) → Response
```

#### Required Flow:
```
Request → log_telemetry() → Supabase INSERT → Queue BQ Job → Response
                                                    ↓
                                            Background Worker → BigQuery INSERT
```

#### Fix Required:

```python
# Use FastAPI BackgroundTasks
from fastapi import BackgroundTasks

@router.post("/telemetry")
async def log_telemetry(data: TelemetryData, background_tasks: BackgroundTasks):
    # Sync write to Supabase (fast)
    await blackbox_service.log_telemetry_sync(data)

    # Async queue to BigQuery (non-blocking)
    background_tasks.add_task(blackbox_service.stream_to_bigquery, data)

    return {"status": "logged"}
```

---

## MUST BUILD - Missing Infrastructure

### 🟠 P1-BUILD-1: Storage Quota Enforcement

**Status**: Schema exists, not enforced
**Impact**: Users can exceed storage limits
**Effort**: 2-3 hours

#### Current State:

- ✅ `plans.storage_quota_gb` defined (10GB, 50GB, unlimited)
- ✅ `subscription_usage` table exists
- ❌ Quota NOT checked before upload
- ❌ Usage NOT incremented after upload

#### Implementation Required:

```python
# backend/services/storage_quota_service.py

class StorageQuotaService:
    async def check_quota(self, workspace_id: str, file_size_bytes: int) -> bool:
        """Check if workspace can upload file within quota."""
        current_usage = await self.get_current_usage(workspace_id)
        limit_bytes = await self.get_storage_limit(workspace_id)

        if limit_bytes == -1:  # Unlimited plan
            return True

        return (current_usage + file_size_bytes) <= limit_bytes

    async def increment_usage(self, workspace_id: str, bytes_added: int):
        """Increment storage usage after successful upload."""
        async with get_db_connection() as conn:
            await conn.execute("""
                UPDATE subscription_usage
                SET current_usage = current_usage + %s
                WHERE workspace_id = %s AND metric_name = 'storage_gb'
            """, (bytes_added / (1024**3), workspace_id))

    async def decrement_usage(self, workspace_id: str, bytes_removed: int):
        """Decrement storage usage after file deletion."""
        # Similar implementation
```

#### Integration Point:

```python
# backend/api/v1/upload.py

@router.post("/file")
async def upload_file(file: UploadFile, workspace_id: str, ...):
    # ADD THIS CHECK
    if not await storage_quota_service.check_quota(workspace_id, file.size):
        raise HTTPException(
            status_code=402,  # Payment Required
            detail="Storage quota exceeded. Please upgrade your plan."
        )

    # ... existing upload logic ...

    # ADD THIS AFTER SUCCESS
    await storage_quota_service.increment_usage(workspace_id, file.size)
```

---

### 🟠 P1-BUILD-2: API Rate Limit Quota Tracking

**Status**: Rate limiter exists, quota tracking incomplete
**Impact**: Can't enforce plan-based API limits
**Effort**: 2-3 hours

#### Current State:

- ✅ `RateLimiter` class with Redis backend
- ✅ `subscription_usage.api_calls_daily` in schema
- ❌ Daily reset not implemented
- ❌ Per-workspace limits not enforced (uses global limits)

#### Implementation Required:

```python
# Add to backend/services/rate_limiter.py

async def check_api_quota(self, workspace_id: str) -> Tuple[bool, int, int]:
    """
    Check if workspace has remaining API quota.
    Returns: (allowed, current_count, limit)
    """
    # Get plan limit
    limit = await self._get_workspace_api_limit(workspace_id)

    # Get today's usage
    key = f"api_quota:{workspace_id}:{date.today().isoformat()}"
    current = await self.redis_client.get(key) or 0

    return (int(current) < limit, int(current), limit)

async def increment_api_usage(self, workspace_id: str):
    """Increment API usage counter."""
    key = f"api_quota:{workspace_id}:{date.today().isoformat()}"
    await self.redis_client.incr(key)
    await self.redis_client.expire(key, 86400)  # 24 hour TTL
```

---

### 🟠 P1-BUILD-3: File Metadata Persistence

**Status**: Stored in Redis only (24h TTL)
**Impact**: File list lost after Redis flush or expiry
**Effort**: 3-4 hours

#### Current State:

```python
# upload.py - CURRENT (Redis only)
await redis_client.set_json(f"upload:{file_id}", metadata, ex=86400)
```

#### Required Change:

```sql
-- New migration: 015_file_uploads.sql
CREATE TABLE uploaded_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id),
    user_id UUID NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    storage_path TEXT NOT NULL,  -- GCS path or local path
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(100),
    checksum VARCHAR(64),
    processing_status VARCHAR(50) DEFAULT 'uploaded',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE  -- Soft delete
);

CREATE INDEX idx_uploaded_files_workspace ON uploaded_files(workspace_id);
ALTER TABLE uploaded_files ENABLE ROW LEVEL SECURITY;
```

---

### 🟠 P1-BUILD-4: Production Storage Backend

**Status**: Falls back to local disk
**Impact**: Files lost on container restart, not scalable
**Effort**: 2 hours

#### Current State:

```python
# upload.py#L154 - Uses local disk
file_path = os.path.join(settings.UPLOAD_DIR, workspace_id, safe_filename)
with open(file_path, 'wb') as f:
    f.write(content)
```

#### Required Change:

```python
# Use EnhancedStorageManager for production
from services.enhanced_storage_service import EnhancedStorageManager

async def save_uploaded_file(file: UploadFile, workspace_id: str, user_id: str):
    settings = get_settings()

    if settings.ENVIRONMENT == "production":
        storage = EnhancedStorageManager(settings.GCS_BUCKET)
        result = await storage.upload_intelligent(
            file_content=await file.read(),
            filename=file.filename,
            content_type=file.content_type,
            tenant_id=workspace_id,
            asset_type=AssetType.DOCUMENT
        )
        return {"file_path": result.blob_name, "public_url": result.public_url}
    else:
        # Keep local storage for development
        # ... existing code ...
```

---

## MUST IMPROVE - Performance Optimization

### 🟡 P1-PERF-1: Frontend Bundle Size

**Status**: 4 icon libs + 3 animation libs
**Impact**: Slow initial load, poor Lighthouse score
**Effort**: 30 minutes

#### Current Dependencies (package.json):

```json
// REDUNDANT - REMOVE THESE
"@hugeicons/core-free-icons": "^3.1.0",
"@hugeicons/react": "^1.1.4",
"@lineiconshq/free-icons": "^1.0.3",
"@lineiconshq/react-lineicons": "^1.0.5",
"@phosphor-icons/react": "^2.1.10",
"motion": "^12.23.26",  // Duplicate of framer-motion
"@studio-freight/lenis": "^1.0.42",  // Duplicate scroll lib

// SHOULD NOT BE IN FRONTEND
"pg": "^8.16.3",  // Postgres driver - backend only!
```

#### Fix Command:

```bash
cd raptorflow-app
npm uninstall @hugeicons/core-free-icons @hugeicons/react @lineiconshq/free-icons @lineiconshq/react-lineicons @phosphor-icons/react motion @studio-freight/lenis pg
```

#### Keep Only:

- `lucide-react` for icons
- `framer-motion` for animations
- `lenis` for smooth scroll (if needed)

---

### 🟡 P1-PERF-2: Replace Print Statements with Logging

**Status**: `print()` used in production code
**Impact**: No log levels, no structured logging
**Effort**: 30 minutes

#### Affected Files:

| File | Line | Current |
|------|------|---------|
| `blackbox_service.py` | 189 | `print(f"BigQuery insertion errors: {errors}")` |
| `blackbox_service.py` | 250 | `print(f"BigQuery outcome insertion errors: {errors}")` |
| `matrix_service.py` | 145 | `print(f"ERROR: Failed to initialize telemetry stream: {e}")` |
| `matrix_service.py` | 157 | `print(f"ERROR: Failed to emit telemetry event: {e}")` |
| `matrix_service.py` | 224 | `print(f"ERROR: Audit logging for kill-switch failed: {e}")` |

#### Fix:

```python
# Replace all print() with logger
import logging
logger = logging.getLogger(__name__)

# BEFORE
print(f"BigQuery insertion errors: {errors}")

# AFTER
logger.error(f"BigQuery insertion errors", extra={"errors": errors})
```

---

### 🟡 P2-PERF-3: Connection Pool Tuning

**Status**: Conservative settings, may need adjustment
**Current**: `min_size=2, max_size=20`
**Effort**: Testing required

#### Recommended for High Load:

```python
# db.py - Adjust based on Cloud Run instances
_pool = AsyncConnectionPool(
    DB_URI,
    min_size=5,       # Keep more warm connections
    max_size=50,      # Allow more concurrent queries
    max_lifetime=900, # 15 minutes (shorter for Cloud SQL)
    max_idle=180,     # 3 minutes
)
```

---

## MUST ADD - Observability & Monitoring

### 🟡 P1-OBS-1: Structured Logging Format

**Status**: Basic logging, not JSON
**Impact**: Hard to query in Cloud Logging
**Effort**: 1 hour

```python
# utils/logging_config.py - Add JSON formatter

import json
import logging

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "workspace_id": getattr(record, 'workspace_id', None),
            "request_id": getattr(record, 'request_id', None),
        }
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)
```

---

### 🟡 P1-OBS-2: Request Tracing Headers

**Status**: Correlation ID middleware exists
**Missing**: Propagation to downstream services
**Effort**: 1 hour

```python
# Ensure X-Request-ID flows to:
# - Supabase queries (add as metadata)
# - BigQuery jobs (add as label)
# - GCS uploads (add as custom metadata)
# - External API calls (forward header)
```

---

### 🟡 P2-OBS-3: Business Metrics Dashboard

**Status**: Internal metrics collected
**Missing**: Exposed metrics endpoint
**Effort**: 2 hours

```python
# Add /metrics endpoint for Prometheus scraping
@router.get("/metrics")
async def get_metrics():
    return {
        "active_workspaces": await get_active_workspace_count(),
        "total_moves_today": await get_moves_count_today(),
        "api_calls_per_minute": await get_api_rate(),
        "storage_used_gb": await get_total_storage(),
        "error_rate_5m": await get_error_rate(),
    }
```

---

## MUST CLEAN - Technical Debt

### 🟡 P2-DEBT-1: Remove Experimental Files

**Action**: Move or delete these from production paths

| File | Action |
|------|--------|
| `error_ridden_backend.py` | Move to `experiments/` |
| `error_ridden_api.py` | Move to `experiments/` |
| `error_ridden_config.py` | Move to `experiments/` |
| `error_ridden_database.py` | Move to `experiments/` |
| `verify_*.py` (root level) | Move to `scripts/diagnostics/` |

---

### 🟡 P2-DEBT-2: Consolidate Entry Points

**Current**: Multiple server entry points
**Target**: Single production entry

| File | Status |
|------|--------|
| `backend/main.py` | ✅ KEEP - Production entry |
| `backend_server.py` | Move to `scripts/` |
| `intelligent_backend.py` | Move to `scripts/` |
| `start_server.py` | Move to `scripts/` |
| `minimal_test.py` | Move to `scripts/` |

---

### 🟡 P2-DEBT-3: Standardize Service Patterns

**Issue**: Inconsistent async/sync patterns across services

| Service | Pattern | Should Be |
|---------|---------|-----------|
| `BlackboxService` | All sync | All async |
| `CampaignService` | Mixed | All async |
| `PaymentService` | All async | ✅ Correct |
| `StorageService` | All sync | All async |

---

## Architecture Strengths (Already Done)

### ✅ Security
- [x] JWT + Supabase auth middleware
- [x] API key authentication support
- [x] Rate limiting (Redis-backed)
- [x] Security headers middleware
- [x] PII masking in telemetry (`utils/pii_masking.py`)
- [x] RLS on core tables (campaigns, moves, subscriptions)

### ✅ Infrastructure
- [x] Connection pooling (psycopg AsyncConnectionPool)
- [x] Redis caching with fallback
- [x] Graceful degradation manager
- [x] Automated recovery system
- [x] Health check endpoints (deep + shallow)
- [x] GCS storage integration
- [x] BigQuery analytics pipeline

### ✅ Multi-Tenancy
- [x] Workspace-based isolation
- [x] Subscription plans with limits
- [x] Usage tracking schema
- [x] Tenant-isolated storage paths

### ✅ Developer Experience
- [x] Comprehensive test suite structure
- [x] Docker + docker-compose setup
- [x] Pre-commit hooks configured
- [x] CI/CD with GitHub Actions

---

## Implementation Priority Matrix

| Priority | Category | Items | Total Effort |
|----------|----------|-------|--------------|
| **P0** | Security | 3 | 8 hours |
| **P0** | Scalability | 2 | 10 hours |
| **P1** | Infrastructure | 4 | 12 hours |
| **P1** | Performance | 2 | 1 hour |
| **P1** | Observability | 2 | 2 hours |
| **P2** | Performance | 1 | 2 hours |
| **P2** | Observability | 1 | 2 hours |
| **P2** | Tech Debt | 3 | 4 hours |
| | **TOTAL** | **18 items** | **~41 hours** |

---

## Estimated Timeline

### Week 1: Critical Security & Scalability (P0)
- [ ] Day 1-2: Fix multi-tenant data leakage (all affected files)
- [ ] Day 2: Add missing RLS policies
- [ ] Day 3: Standardize tenant_id → workspace_id
- [ ] Day 4-5: Convert BlackboxService to async
- [ ] Day 5: Move BigQuery streaming to background tasks

### Week 2: User Experience & Infrastructure (P0-P1)
- [ ] Day 1: Enable AuthGuard + middleware auth enforcement
- [ ] Day 2: Create AuthProvider with session persistence
- [ ] Day 3: User-scoped storage keys in onboardingStore
- [ ] Day 4: Load foundation data from backend API (not static JSON)
- [ ] Day 5: Implement scroll position + form state persistence

### Week 3: Multi-Tenant Features (P1)
- [ ] Day 1: Create WorkspaceSwitcher component
- [ ] Day 2: Build /settings/profile page
- [ ] Day 3: Build /settings/team page (invite members)
- [ ] Day 4: Implement storage quota enforcement
- [ ] Day 5: Implement API quota tracking

### Week 4: Infrastructure & Performance (P1-P2)
- [ ] Day 1: Add file metadata persistence to Postgres
- [ ] Day 2: Switch to GCS in production
- [ ] Day 3: Remove redundant npm packages
- [ ] Day 4: Add skeleton loaders + optimistic updates
- [ ] Day 5: Structured logging + request tracing

---

## Quick Wins (Do Today)

1. **Enable authentication** (10 min):
   ```tsx
   // AuthGuard.tsx - Remove the bypass, uncomment the original auth logic
   // proxy.ts - Uncomment the redirect to /login
   ```

2. **Remove npm bloat** (5 min):
   ```bash
   cd raptorflow-app && npm uninstall @hugeicons/core-free-icons @hugeicons/react @lineiconshq/free-icons @lineiconshq/react-lineicons @phosphor-icons/react motion pg
   ```

3. **Replace print with logger** (30 min):
   - `blackbox_service.py` lines 189, 250
   - `matrix_service.py` lines 145, 157, 224

4. **Add workspace_id to update_move_status** (30 min):
   - `db.py` line 1271-1283

---

## Validation Checklist

Before going to production with many users:

### Authentication & Sessions
- [ ] AuthGuard enforcing login for protected routes
- [ ] Session persists across browser restarts
- [ ] Token refresh working automatically
- [ ] Users redirected to /login when session expires

### Multi-Tenancy & Data Isolation
- [ ] Each user sees ONLY their workspace data
- [ ] Onboarding data tied to user ID + workspace ID
- [ ] Foundation data loaded from backend, not static JSON
- [ ] All API endpoints validate workspace_id ownership
- [ ] All DB update/delete queries include workspace_id filter
- [ ] All tables have RLS enabled

### User Experience
- [ ] Scroll position preserved on navigation
- [ ] Form state saved automatically (no lost work)
- [ ] Workspace switcher for multi-workspace users
- [ ] Settings pages exist (profile, team, billing)
- [ ] Loading skeletons shown during data fetch

### Infrastructure
- [ ] Storage quota checked before upload
- [ ] API quota tracked per workspace per day
- [ ] No synchronous I/O in request handlers
- [ ] All file uploads go to GCS (not local disk)
- [ ] File metadata persisted to Postgres
- [ ] Structured JSON logging enabled
- [ ] Error monitoring configured (Sentry/similar)
- [ ] Load testing completed (target: 100 concurrent users)

---

*This document should be treated as a living roadmap. Update checkboxes as items are completed.*
