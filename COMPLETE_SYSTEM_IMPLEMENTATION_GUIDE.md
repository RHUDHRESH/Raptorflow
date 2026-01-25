# COMPLETE SYSTEM IMPLEMENTATION GUIDE
## RaptorFlow Production Hardening & Authentication Overhaul

**Version:** 1.0.0  
**Last Updated:** January 2026  
**Status:** Production Implementation Guide

---

## Table of Contents

1. [Phase 1: Authentication Foundation](#phase-1-authentication-foundation)
2. [Phase 2: Remove All Authentication Bypasses](#phase-2-remove-all-authentication-bypasses)
3. [Phase 3: Row-Level Security (RLS) Implementation](#phase-3-row-level-security-rls-implementation)
4. [Phase 4: Workspace Isolation](#phase-4-workspace-isolation)
5. [Phase 5: Session Management & Token Security](#phase-5-session-management--token-security)
6. [Phase 6: Payment Integration (PhonePe)](#phase-6-payment-integration-phonepe)
7. [Phase 7: Subscription Management](#phase-7-subscription-management)
8. [Phase 8: Customer ID & Billing](#phase-8-customer-id--billing)
9. [Phase 9: User Management](#phase-9-user-management)
10. [Phase 10: Admin Panel](#phase-10-admin-panel)
11. [Phase 11: Plan Upgrades & Downgrades](#phase-11-plan-upgrades--downgrades)
12. [Phase 12: Deployment Pipeline](#phase-12-deployment-pipeline)
13. [Phase 13: Infrastructure Hardening](#phase-13-infrastructure-hardening)
14. [Phase 14: Monitoring & Alerting](#phase-14-monitoring--alerting)
15. [Phase 15: Red-Team Verification & Final Checklist](#phase-15-red-team-verification--final-checklist)

---

## Executive Summary

This guide provides a comprehensive, step-by-step implementation plan for hardening RaptorFlow's production environment. It covers authentication, authorization, payment processing, user management, and infrastructure security.

**Key Objectives:**
- Implement bulletproof authentication with no bypasses
- Enforce Row-Level Security (RLS) across all tables
- Integrate PhonePe payment gateway
- Build scalable subscription management
- Deploy production-grade monitoring

---

# PHASE 1: AUTHENTICATION FOUNDATION

## 1.1 Overview

The authentication system is the first line of defense. This phase establishes a rock-solid authentication foundation using Supabase Auth with proper session handling.

## 1.2 Supabase Auth Configuration

### 1.2.1 Enable Email Authentication

```sql
-- In Supabase Dashboard > Authentication > Providers
-- Enable Email provider with the following settings:
-- - Confirm email: ENABLED
-- - Secure email change: ENABLED
-- - Double confirm changes: ENABLED
```

### 1.2.2 Configure Auth Settings

```sql
-- Authentication > Settings
-- JWT expiry: 3600 (1 hour)
-- Enable refresh token rotation: YES
-- Reuse interval: 10 seconds
```

### 1.2.3 Email Templates Setup

```sql
-- Authentication > Email Templates

-- Confirmation Email
-- Subject: Confirm your RaptorFlow account
-- Body: Use the default Supabase template with custom branding
```

## 1.3 Frontend Auth Implementation

### 1.3.1 Auth Context Setup

```typescript
// src/contexts/AuthContext.tsx
'use client';

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { createClient } from '@/lib/supabase/client';
import { User, Session, AuthError } from '@supabase/supabase-js';
import { useRouter } from 'next/navigation';

interface AuthState {
  user: User | null;
  session: Session | null;
  loading: boolean;
  error: AuthError | null;
}

interface AuthContextType extends AuthState {
  signIn: (email: string, password: string) => Promise<{ error: AuthError | null }>;
  signUp: (email: string, password: string, metadata?: object) => Promise<{ error: AuthError | null }>;
  signOut: () => Promise<void>;
  resetPassword: (email: string) => Promise<{ error: AuthError | null }>;
  updatePassword: (password: string) => Promise<{ error: AuthError | null }>;
  refreshSession: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    session: null,
    loading: true,
    error: null,
  });
  
  const router = useRouter();
  const supabase = createClient();

  // Initialize auth state
  useEffect(() => {
    const initAuth = async () => {
      try {
        const { data: { session }, error } = await supabase.auth.getSession();
        
        if (error) throw error;
        
        setState({
          user: session?.user ?? null,
          session,
          loading: false,
          error: null,
        });
      } catch (error) {
        setState(prev => ({
          ...prev,
          loading: false,
          error: error as AuthError,
        }));
      }
    };

    initAuth();

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        setState(prev => ({
          ...prev,
          user: session?.user ?? null,
          session,
          loading: false,
        }));

        if (event === 'SIGNED_OUT') {
          router.push('/login');
        }
        
        if (event === 'TOKEN_REFRESHED') {
          console.log('Token refreshed successfully');
        }
      }
    );

    return () => {
      subscription.unsubscribe();
    };
  }, [supabase, router]);

  const signIn = useCallback(async (email: string, password: string) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    const { error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    setState(prev => ({ ...prev, loading: false, error }));
    return { error };
  }, [supabase]);

  const signUp = useCallback(async (email: string, password: string, metadata?: object) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    const { error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: metadata,
        emailRedirectTo: `${window.location.origin}/auth/callback`,
      },
    });

    setState(prev => ({ ...prev, loading: false, error }));
    return { error };
  }, [supabase]);

  const signOut = useCallback(async () => {
    setState(prev => ({ ...prev, loading: true }));
    await supabase.auth.signOut();
    setState({
      user: null,
      session: null,
      loading: false,
      error: null,
    });
  }, [supabase]);

  const resetPassword = useCallback(async (email: string) => {
    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/auth/reset-password`,
    });
    return { error };
  }, [supabase]);

  const updatePassword = useCallback(async (password: string) => {
    const { error } = await supabase.auth.updateUser({ password });
    return { error };
  }, [supabase]);

  const refreshSession = useCallback(async () => {
    const { data: { session }, error } = await supabase.auth.refreshSession();
    if (!error && session) {
      setState(prev => ({
        ...prev,
        user: session.user,
        session,
      }));
    }
  }, [supabase]);

  const value: AuthContextType = {
    ...state,
    signIn,
    signUp,
    signOut,
    resetPassword,
    updatePassword,
    refreshSession,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
```

### 1.3.2 Supabase Client Configuration

```typescript
// src/lib/supabase/client.ts
import { createBrowserClient } from '@supabase/ssr';

export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );
}
```

### 1.3.3 Server-Side Supabase Client

```typescript
// src/lib/supabase/server.ts
import { createServerClient, type CookieOptions } from '@supabase/ssr';
import { cookies } from 'next/headers';

export async function createServerSupabaseClient() {
  const cookieStore = await cookies();

  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        get(name: string) {
          return cookieStore.get(name)?.value;
        },
        set(name: string, value: string, options: CookieOptions) {
          try {
            cookieStore.set({ name, value, ...options });
          } catch (error) {
            // Handle cookie setting in Server Components
          }
        },
        remove(name: string, options: CookieOptions) {
          try {
            cookieStore.set({ name, value: '', ...options });
          } catch (error) {
            // Handle cookie removal in Server Components
          }
        },
      },
    }
  );
}
```

## 1.4 Middleware Protection

### 1.4.1 Next.js Middleware

```typescript
// src/middleware.ts
import { createServerClient, type CookieOptions } from '@supabase/ssr';
import { NextResponse, type NextRequest } from 'next/server';

// Routes that don't require authentication
const publicRoutes = [
  '/login',
  '/signup',
  '/forgot-password',
  '/auth/callback',
  '/auth/reset-password',
  '/api/webhooks',
];

// Routes that require admin role
const adminRoutes = [
  '/admin',
  '/api/admin',
];

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  
  // Skip public routes
  if (publicRoutes.some(route => pathname.startsWith(route))) {
    return NextResponse.next();
  }

  // Skip static files
  if (pathname.startsWith('/_next') || pathname.includes('.')) {
    return NextResponse.next();
  }

  let response = NextResponse.next({
    request: {
      headers: request.headers,
    },
  });

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        get(name: string) {
          return request.cookies.get(name)?.value;
        },
        set(name: string, value: string, options: CookieOptions) {
          request.cookies.set({ name, value, ...options });
          response = NextResponse.next({
            request: { headers: request.headers },
          });
          response.cookies.set({ name, value, ...options });
        },
        remove(name: string, options: CookieOptions) {
          request.cookies.set({ name, value: '', ...options });
          response = NextResponse.next({
            request: { headers: request.headers },
          });
          response.cookies.set({ name, value: '', ...options });
        },
      },
    }
  );

  const { data: { user }, error } = await supabase.auth.getUser();

  // No user - redirect to login
  if (!user || error) {
    const redirectUrl = new URL('/login', request.url);
    redirectUrl.searchParams.set('redirect', pathname);
    return NextResponse.redirect(redirectUrl);
  }

  // Check admin routes
  if (adminRoutes.some(route => pathname.startsWith(route))) {
    const { data: profile } = await supabase
      .from('profiles')
      .select('role')
      .eq('id', user.id)
      .single();

    if (profile?.role !== 'admin') {
      return NextResponse.redirect(new URL('/dashboard', request.url));
    }
  }

  return response;
}

export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
};
```

## 1.5 Database Schema for Auth

### 1.5.1 Profiles Table

```sql
-- supabase/migrations/001_profiles.sql
CREATE TABLE IF NOT EXISTS public.profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT NOT NULL,
  full_name TEXT,
  avatar_url TEXT,
  role TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin', 'superadmin')),
  workspace_id UUID,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create index for faster lookups
CREATE INDEX idx_profiles_email ON public.profiles(email);
CREATE INDEX idx_profiles_workspace ON public.profiles(workspace_id);

-- Enable RLS
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Trigger to auto-create profile on signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, email, full_name)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'full_name', '')
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Updated_at trigger
CREATE OR REPLACE FUNCTION public.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER profiles_updated_at
  BEFORE UPDATE ON public.profiles
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();
```

## 1.6 Verification Checklist - Phase 1

- [ ] Email authentication enabled in Supabase Dashboard
- [ ] Auth context properly initializes session
- [ ] Login/signup forms work correctly
- [ ] Middleware blocks unauthenticated access
- [ ] Profiles table created with proper triggers
- [ ] Session refresh works automatically
- [ ] Logout clears all session data

---

# PHASE 2: REMOVE ALL AUTHENTICATION BYPASSES

## 2.1 Overview

This phase systematically identifies and removes ALL authentication bypasses, mock users, and development shortcuts that could compromise production security.

## 2.2 Identify Bypass Patterns

### 2.2.1 Common Bypass Patterns to Search

```bash
# Search for these patterns in your codebase
grep -r "SKIP_AUTH" --include="*.ts" --include="*.tsx" --include="*.py"
grep -r "mockUser" --include="*.ts" --include="*.tsx"
grep -r "isAuthenticated = true" --include="*.ts" --include="*.tsx"
grep -r "bypassAuth" --include="*.ts" --include="*.tsx"
grep -r "devMode" --include="*.ts" --include="*.tsx"
grep -r "NODE_ENV.*development.*auth" --include="*.ts" --include="*.tsx"
grep -r "demo.*user" --include="*.ts" --include="*.tsx"
grep -r "test.*token" --include="*.ts" --include="*.tsx"
```

## 2.3 Backend Bypass Removal

### 2.3.1 Remove Python Auth Bypasses

```python
# backend/core/auth.py - SECURE VERSION

from functools import wraps
from typing import Optional, Callable
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
import os

security = HTTPBearer()

class AuthenticationError(Exception):
    """Raised when authentication fails"""
    pass

def get_supabase_client() -> Client:
    """Get authenticated Supabase client"""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")
    
    if not url or not key:
        raise AuthenticationError("Missing Supabase credentials")
    
    return create_client(url, key)

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Verify JWT token and return user data.
    NO BYPASSES - ALWAYS VALIDATES TOKEN.
    """
    token = credentials.credentials
    
    if not token:
        raise HTTPException(status_code=401, detail="No token provided")
    
    try:
        supabase = get_supabase_client()
        
        # Verify the token with Supabase
        response = supabase.auth.get_user(token)
        
        if not response.user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return {
            "id": response.user.id,
            "email": response.user.email,
            "role": response.user.user_metadata.get("role", "user"),
        }
        
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

def require_auth(func: Callable):
    """
    Decorator to require authentication for routes.
    NO DEVELOPMENT BYPASSES.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request: Request = kwargs.get('request')
        if not request:
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
        
        if not request:
            raise HTTPException(status_code=500, detail="Request object not found")
        
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing authorization header")
        
        token = auth_header.split(" ")[1]
        
        # Verify token - NO BYPASSES
        try:
            supabase = get_supabase_client()
            response = supabase.auth.get_user(token)
            
            if not response.user:
                raise HTTPException(status_code=401, detail="Invalid token")
            
            # Attach user to request state
            request.state.user = response.user
            
        except Exception as e:
            raise HTTPException(status_code=401, detail=str(e))
        
        return await func(*args, **kwargs)
    
    return wrapper

def require_admin(func: Callable):
    """
    Decorator to require admin role.
    ALWAYS checks role - NO BYPASSES.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request: Request = kwargs.get('request')
        if not request:
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
        
        user = getattr(request.state, 'user', None)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Check role in database - NOT just token claims
        supabase = get_supabase_client()
        result = supabase.table('profiles').select('role').eq('id', user.id).single().execute()
        
        if not result.data or result.data.get('role') not in ['admin', 'superadmin']:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        return await func(*args, **kwargs)
    
    return wrapper
```

### 2.3.2 Secure FastAPI Routes

```python
# backend/api/v1/routes.py - SECURE VERSION

from fastapi import APIRouter, Depends, HTTPException, Request
from core.auth import verify_token, require_auth, require_admin

router = APIRouter()

@router.get("/protected")
async def protected_route(user: dict = Depends(verify_token)):
    """
    Protected route - requires valid JWT token.
    """
    return {"message": f"Hello {user['email']}", "user_id": user['id']}

@router.get("/admin/users")
@require_auth
@require_admin
async def list_users(request: Request):
    """
    Admin-only route - requires admin role.
    """
    # User is attached to request.state by decorators
    return {"users": []}

@router.post("/data")
async def create_data(request: Request, user: dict = Depends(verify_token)):
    """
    Create data - authenticated users only.
    Data is automatically scoped to user's workspace.
    """
    workspace_id = user.get('workspace_id')
    if not workspace_id:
        raise HTTPException(status_code=400, detail="No workspace assigned")
    
    # Process with workspace isolation
    return {"success": True, "workspace_id": workspace_id}
```

## 2.4 Frontend Bypass Removal

### 2.4.1 Remove Mock User Patterns

```typescript
// BEFORE (INSECURE - REMOVE THIS):
// const user = process.env.NODE_ENV === 'development' 
//   ? { id: 'mock-user', email: 'dev@test.com' }
//   : await getUser();

// AFTER (SECURE):
// src/lib/auth/getUser.ts
import { createServerSupabaseClient } from '@/lib/supabase/server';
import { redirect } from 'next/navigation';

export async function getAuthenticatedUser() {
  const supabase = await createServerSupabaseClient();
  
  const { data: { user }, error } = await supabase.auth.getUser();
  
  if (error || !user) {
    redirect('/login');
  }
  
  return user;
}

export async function getUserWithProfile() {
  const supabase = await createServerSupabaseClient();
  
  const { data: { user }, error: authError } = await supabase.auth.getUser();
  
  if (authError || !user) {
    redirect('/login');
  }
  
  const { data: profile, error: profileError } = await supabase
    .from('profiles')
    .select('*')
    .eq('id', user.id)
    .single();
  
  if (profileError) {
    console.error('Failed to fetch profile:', profileError);
    redirect('/onboarding');
  }
  
  return { user, profile };
}
```

### 2.4.2 Secure API Client

```typescript
// src/lib/api/client.ts - SECURE VERSION

import { createClient } from '@/lib/supabase/client';

class SecureAPIClient {
  private baseUrl: string;
  
  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || '';
  }
  
  private async getAuthHeaders(): Promise<Headers> {
    const supabase = createClient();
    const { data: { session } } = await supabase.auth.getSession();
    
    if (!session?.access_token) {
      throw new Error('Not authenticated');
    }
    
    return new Headers({
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${session.access_token}`,
    });
  }
  
  async get<T>(endpoint: string): Promise<T> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'GET',
      headers,
    });
    
    if (response.status === 401) {
      // Token expired - trigger refresh
      window.location.href = '/login?expired=true';
      throw new Error('Session expired');
    }
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }
    
    return response.json();
  }
  
  async post<T>(endpoint: string, data: unknown): Promise<T> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers,
      body: JSON.stringify(data),
    });
    
    if (response.status === 401) {
      window.location.href = '/login?expired=true';
      throw new Error('Session expired');
    }
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }
    
    return response.json();
  }
  
  // Similar for PUT, DELETE, PATCH...
}

export const api = new SecureAPIClient();
```

## 2.5 Environment Variable Audit

### 2.5.1 Remove Development Bypasses from .env

```bash
# .env.production - SECURE VERSION
# DO NOT include any of these bypass variables:
# - SKIP_AUTH=true (REMOVE)
# - DEV_MODE=true (REMOVE)
# - BYPASS_RLS=true (REMOVE)
# - MOCK_USER_ID=xxx (REMOVE)
# - TEST_TOKEN=xxx (REMOVE)

# Only include production values:
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key
NEXT_PUBLIC_API_URL=https://api.yourapp.com
```

## 2.6 Verification Checklist - Phase 2

- [ ] Searched codebase for all bypass patterns
- [ ] Removed all mock user logic
- [ ] Removed all `SKIP_AUTH` checks
- [ ] Removed all development-only auth bypasses
- [ ] Updated all API routes to require authentication
- [ ] Verified middleware blocks all protected routes
- [ ] Removed bypass environment variables
- [ ] Tested that unauthenticated requests fail with 401

---

# PHASE 3: ROW-LEVEL SECURITY (RLS) IMPLEMENTATION

## 3.1 Overview

Row-Level Security ensures users can only access their own data at the database level, providing defense-in-depth even if application-level checks fail.

## 3.2 RLS Policies for Core Tables

### 3.2.1 Profiles Table RLS

```sql
-- supabase/migrations/002_profiles_rls.sql

-- Enable RLS (if not already enabled)
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Drop existing policies to start fresh
DROP POLICY IF EXISTS "profiles_select_own" ON public.profiles;
DROP POLICY IF EXISTS "profiles_update_own" ON public.profiles;
DROP POLICY IF EXISTS "profiles_insert_own" ON public.profiles;
DROP POLICY IF EXISTS "profiles_admin_all" ON public.profiles;

-- Users can view their own profile
CREATE POLICY "profiles_select_own" ON public.profiles
  FOR SELECT
  USING (auth.uid() = id);

-- Users can update their own profile
CREATE POLICY "profiles_update_own" ON public.profiles
  FOR UPDATE
  USING (auth.uid() = id)
  WITH CHECK (auth.uid() = id);

-- Only system can insert (via trigger)
CREATE POLICY "profiles_insert_system" ON public.profiles
  FOR INSERT
  WITH CHECK (auth.uid() = id);

-- Admins can view all profiles
CREATE POLICY "profiles_admin_select" ON public.profiles
  FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM public.profiles
      WHERE id = auth.uid() AND role IN ('admin', 'superadmin')
    )
  );
```

### 3.2.2 Workspaces Table RLS

```sql
-- supabase/migrations/003_workspaces_rls.sql

-- Create workspaces table if not exists
CREATE TABLE IF NOT EXISTS public.workspaces (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  slug TEXT UNIQUE NOT NULL,
  owner_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  settings JSONB DEFAULT '{}',
  plan TEXT NOT NULL DEFAULT 'free' CHECK (plan IN ('free', 'starter', 'pro', 'enterprise')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create workspace members junction table
CREATE TABLE IF NOT EXISTS public.workspace_members (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES public.workspaces(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  role TEXT NOT NULL DEFAULT 'member' CHECK (role IN ('owner', 'admin', 'member', 'viewer')),
  invited_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(workspace_id, user_id)
);

-- Enable RLS
ALTER TABLE public.workspaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workspace_members ENABLE ROW LEVEL SECURITY;

-- Workspace policies
CREATE POLICY "workspaces_select_member" ON public.workspaces
  FOR SELECT
  USING (
    id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "workspaces_insert_authenticated" ON public.workspaces
  FOR INSERT
  WITH CHECK (auth.uid() = owner_id);

CREATE POLICY "workspaces_update_admin" ON public.workspaces
  FOR UPDATE
  USING (
    id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
    )
  );

CREATE POLICY "workspaces_delete_owner" ON public.workspaces
  FOR DELETE
  USING (owner_id = auth.uid());

-- Workspace members policies
CREATE POLICY "workspace_members_select" ON public.workspace_members
  FOR SELECT
  USING (
    workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "workspace_members_insert_admin" ON public.workspace_members
  FOR INSERT
  WITH CHECK (
    workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
    )
  );

CREATE POLICY "workspace_members_delete_admin" ON public.workspace_members
  FOR DELETE
  USING (
    workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
    )
    OR user_id = auth.uid() -- Users can remove themselves
  );
```

### 3.2.3 Campaigns Table RLS

```sql
-- supabase/migrations/004_campaigns_rls.sql

CREATE TABLE IF NOT EXISTS public.campaigns (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES public.workspaces(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'paused', 'completed', 'archived')),
  settings JSONB DEFAULT '{}',
  created_by UUID NOT NULL REFERENCES auth.users(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_campaigns_workspace ON public.campaigns(workspace_id);
CREATE INDEX idx_campaigns_status ON public.campaigns(status);

ALTER TABLE public.campaigns ENABLE ROW LEVEL SECURITY;

-- Users can view campaigns in their workspaces
CREATE POLICY "campaigns_select_workspace" ON public.campaigns
  FOR SELECT
  USING (
    workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid()
    )
  );

-- Members can create campaigns
CREATE POLICY "campaigns_insert_member" ON public.campaigns
  FOR INSERT
  WITH CHECK (
    workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid() AND role IN ('owner', 'admin', 'member')
    )
    AND created_by = auth.uid()
  );

-- Admins and creators can update campaigns
CREATE POLICY "campaigns_update" ON public.campaigns
  FOR UPDATE
  USING (
    workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
    )
    OR created_by = auth.uid()
  );

-- Only admins can delete campaigns
CREATE POLICY "campaigns_delete_admin" ON public.campaigns
  FOR DELETE
  USING (
    workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
    )
  );
```

### 3.2.4 Generic Data Table RLS Pattern

```sql
-- supabase/migrations/005_data_tables_rls.sql

-- Template for any workspace-scoped data table
-- Replace 'your_table' with actual table name

CREATE TABLE IF NOT EXISTS public.your_table (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES public.workspaces(id) ON DELETE CASCADE,
  -- Add your columns here
  data JSONB DEFAULT '{}',
  created_by UUID NOT NULL REFERENCES auth.users(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE public.your_table ENABLE ROW LEVEL SECURITY;

-- Standard workspace-scoped policies
CREATE POLICY "your_table_select" ON public.your_table
  FOR SELECT
  USING (
    workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "your_table_insert" ON public.your_table
  FOR INSERT
  WITH CHECK (
    workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid() AND role IN ('owner', 'admin', 'member')
    )
    AND created_by = auth.uid()
  );

CREATE POLICY "your_table_update" ON public.your_table
  FOR UPDATE
  USING (
    workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
    )
    OR created_by = auth.uid()
  );

CREATE POLICY "your_table_delete" ON public.your_table
  FOR DELETE
  USING (
    workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
    )
  );
```

## 3.3 RLS Helper Functions

### 3.3.1 Common Security Functions

```sql
-- supabase/migrations/006_security_functions.sql

-- Check if user is member of workspace
CREATE OR REPLACE FUNCTION public.is_workspace_member(ws_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM public.workspace_members
    WHERE workspace_id = ws_id AND user_id = auth.uid()
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Check if user is admin of workspace
CREATE OR REPLACE FUNCTION public.is_workspace_admin(ws_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM public.workspace_members
    WHERE workspace_id = ws_id 
    AND user_id = auth.uid()
    AND role IN ('owner', 'admin')
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Get current user's primary workspace
CREATE OR REPLACE FUNCTION public.get_user_workspace()
RETURNS UUID AS $$
DECLARE
  ws_id UUID;
BEGIN
  SELECT workspace_id INTO ws_id
  FROM public.profiles
  WHERE id = auth.uid();
  
  RETURN ws_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Check if user is system admin
CREATE OR REPLACE FUNCTION public.is_admin()
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM public.profiles
    WHERE id = auth.uid() AND role IN ('admin', 'superadmin')
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

## 3.4 Verification Checklist - Phase 3

- [ ] All tables have RLS enabled
- [ ] All tables have appropriate policies
- [ ] Tested SELECT only returns user's data
- [ ] Tested INSERT requires proper workspace membership
- [ ] Tested UPDATE respects role-based permissions
- [ ] Tested DELETE is properly restricted
- [ ] Verified cross-workspace data is isolated
- [ ] Helper functions work correctly

---

# PHASE 4: WORKSPACE ISOLATION

## 4.1 Overview

Workspace isolation ensures complete data separation between organizations/teams. Every piece of data must belong to exactly one workspace.

## 4.2 Workspace Creation Flow

### 4.2.1 Backend Workspace Service

```python
# backend/services/workspace_service.py

from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
import uuid

@dataclass
class Workspace:
    id: str
    name: str
    slug: str
    owner_id: str
    plan: str
    settings: Dict[str, Any]
    created_at: datetime

@dataclass
class WorkspaceMember:
    id: str
    workspace_id: str
    user_id: str
    role: str
    created_at: datetime

class WorkspaceService:
    def __init__(self, supabase_client):
        self.supabase = supabase_client
    
    async def create_workspace(
        self,
        owner_id: str,
        name: str,
        slug: Optional[str] = None
    ) -> Workspace:
        """
        Create a new workspace with the user as owner.
        """
        if not slug:
            slug = self._generate_slug(name)
        
        # Create workspace
        workspace_data = {
            'name': name,
            'slug': slug,
            'owner_id': owner_id,
            'plan': 'free',
            'settings': {},
        }
        
        result = self.supabase.table('workspaces').insert(workspace_data).execute()
        workspace = result.data[0]
        
        # Add owner as workspace member
        member_data = {
            'workspace_id': workspace['id'],
            'user_id': owner_id,
            'role': 'owner',
        }
        self.supabase.table('workspace_members').insert(member_data).execute()
        
        # Update user's profile with workspace
        self.supabase.table('profiles').update({
            'workspace_id': workspace['id']
        }).eq('id', owner_id).execute()
        
        return Workspace(**workspace)
    
    async def get_user_workspaces(self, user_id: str) -> List[Workspace]:
        """
        Get all workspaces a user is a member of.
        """
        result = self.supabase.table('workspace_members') \
            .select('workspace_id, workspaces(*)') \
            .eq('user_id', user_id) \
            .execute()
        
        return [
            Workspace(**item['workspaces'])
            for item in result.data
        ]
    
    async def add_member(
        self,
        workspace_id: str,
        user_email: str,
        role: str,
        invited_by: str
    ) -> WorkspaceMember:
        """
        Add a member to workspace by email.
        """
        # Find user by email
        user_result = self.supabase.table('profiles') \
            .select('id') \
            .eq('email', user_email) \
            .single() \
            .execute()
        
        if not user_result.data:
            raise ValueError(f"User with email {user_email} not found")
        
        user_id = user_result.data['id']
        
        # Check if already a member
        existing = self.supabase.table('workspace_members') \
            .select('id') \
            .eq('workspace_id', workspace_id) \
            .eq('user_id', user_id) \
            .execute()
        
        if existing.data:
            raise ValueError("User is already a member of this workspace")
        
        # Add member
        member_data = {
            'workspace_id': workspace_id,
            'user_id': user_id,
            'role': role,
            'invited_by': invited_by,
        }
        
        result = self.supabase.table('workspace_members').insert(member_data).execute()
        return WorkspaceMember(**result.data[0])
    
    async def remove_member(self, workspace_id: str, user_id: str) -> bool:
        """
        Remove a member from workspace.
        """
        self.supabase.table('workspace_members') \
            .delete() \
            .eq('workspace_id', workspace_id) \
            .eq('user_id', user_id) \
            .execute()
        
        return True
    
    async def update_member_role(
        self,
        workspace_id: str,
        user_id: str,
        new_role: str
    ) -> WorkspaceMember:
        """
        Update a member's role in the workspace.
        """
        result = self.supabase.table('workspace_members') \
            .update({'role': new_role}) \
            .eq('workspace_id', workspace_id) \
            .eq('user_id', user_id) \
            .execute()
        
        return WorkspaceMember(**result.data[0])
    
    def _generate_slug(self, name: str) -> str:
        """Generate URL-safe slug from name."""
        import re
        slug = name.lower()
        slug = re.sub(r'[^a-z0-9]+', '-', slug)
        slug = slug.strip('-')
        slug = f"{slug}-{uuid.uuid4().hex[:6]}"
        return slug
```

### 4.2.2 Frontend Workspace Context

```typescript
// src/contexts/WorkspaceContext.tsx
'use client';

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { createClient } from '@/lib/supabase/client';
import { useAuth } from './AuthContext';

interface Workspace {
  id: string;
  name: string;
  slug: string;
  owner_id: string;
  plan: 'free' | 'starter' | 'pro' | 'enterprise';
  settings: Record<string, unknown>;
  created_at: string;
}

interface WorkspaceMember {
  id: string;
  workspace_id: string;
  user_id: string;
  role: 'owner' | 'admin' | 'member' | 'viewer';
  created_at: string;
}

interface WorkspaceContextType {
  currentWorkspace: Workspace | null;
  workspaces: Workspace[];
  members: WorkspaceMember[];
  loading: boolean;
  error: string | null;
  switchWorkspace: (workspaceId: string) => Promise<void>;
  createWorkspace: (name: string) => Promise<Workspace>;
  inviteMember: (email: string, role: string) => Promise<void>;
  removeMember: (userId: string) => Promise<void>;
  updateMemberRole: (userId: string, role: string) => Promise<void>;
}

const WorkspaceContext = createContext<WorkspaceContextType | undefined>(undefined);

export function WorkspaceProvider({ children }: { children: React.ReactNode }) {
  const { user } = useAuth();
  const [currentWorkspace, setCurrentWorkspace] = useState<Workspace | null>(null);
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [members, setMembers] = useState<WorkspaceMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const supabase = createClient();

  // Load user's workspaces
  useEffect(() => {
    if (!user) {
      setCurrentWorkspace(null);
      setWorkspaces([]);
      setLoading(false);
      return;
    }

    const loadWorkspaces = async () => {
      try {
        setLoading(true);
        
        // Get user's profile to find current workspace
        const { data: profile } = await supabase
          .from('profiles')
          .select('workspace_id')
          .eq('id', user.id)
          .single();

        // Get all workspaces user is a member of
        const { data: memberData } = await supabase
          .from('workspace_members')
          .select(`
            workspace_id,
            workspaces (*)
          `)
          .eq('user_id', user.id);

        const userWorkspaces = memberData?.map(m => m.workspaces as Workspace) || [];
        setWorkspaces(userWorkspaces);

        // Set current workspace
        if (profile?.workspace_id) {
          const current = userWorkspaces.find(w => w.id === profile.workspace_id);
          setCurrentWorkspace(current || userWorkspaces[0] || null);
        } else if (userWorkspaces.length > 0) {
          setCurrentWorkspace(userWorkspaces[0]);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load workspaces');
      } finally {
        setLoading(false);
      }
    };

    loadWorkspaces();
  }, [user, supabase]);

  // Load workspace members when current workspace changes
  useEffect(() => {
    if (!currentWorkspace) {
      setMembers([]);
      return;
    }

    const loadMembers = async () => {
      const { data } = await supabase
        .from('workspace_members')
        .select('*')
        .eq('workspace_id', currentWorkspace.id);

      setMembers(data || []);
    };

    loadMembers();
  }, [currentWorkspace, supabase]);

  const switchWorkspace = useCallback(async (workspaceId: string) => {
    const workspace = workspaces.find(w => w.id === workspaceId);
    if (!workspace) throw new Error('Workspace not found');

    // Update user's profile
    await supabase
      .from('profiles')
      .update({ workspace_id: workspaceId })
      .eq('id', user?.id);

    setCurrentWorkspace(workspace);
  }, [workspaces, user, supabase]);

  const createWorkspace = useCallback(async (name: string): Promise<Workspace> => {
    if (!user) throw new Error('Not authenticated');

    const { data, error } = await supabase
      .from('workspaces')
      .insert({
        name,
        slug: name.toLowerCase().replace(/\s+/g, '-') + '-' + Date.now(),
        owner_id: user.id,
      })
      .select()
      .single();

    if (error) throw error;

    // Add owner as member
    await supabase
      .from('workspace_members')
      .insert({
        workspace_id: data.id,
        user_id: user.id,
        role: 'owner',
      });

    setWorkspaces(prev => [...prev, data]);
    return data;
  }, [user, supabase]);

  const inviteMember = useCallback(async (email: string, role: string) => {
    if (!currentWorkspace) throw new Error('No workspace selected');

    // Find user by email
    const { data: profile } = await supabase
      .from('profiles')
      .select('id')
      .eq('email', email)
      .single();

    if (!profile) throw new Error('User not found');

    await supabase
      .from('workspace_members')
      .insert({
        workspace_id: currentWorkspace.id,
        user_id: profile.id,
        role,
        invited_by: user?.id,
      });

    // Refresh members
    const { data } = await supabase
      .from('workspace_members')
      .select('*')
      .eq('workspace_id', currentWorkspace.id);

    setMembers(data || []);
  }, [currentWorkspace, user, supabase]);

  const removeMember = useCallback(async (userId: string) => {
    if (!currentWorkspace) throw new Error('No workspace selected');

    await supabase
      .from('workspace_members')
      .delete()
      .eq('workspace_id', currentWorkspace.id)
      .eq('user_id', userId);

    setMembers(prev => prev.filter(m => m.user_id !== userId));
  }, [currentWorkspace, supabase]);

  const updateMemberRole = useCallback(async (userId: string, role: string) => {
    if (!currentWorkspace) throw new Error('No workspace selected');

    await supabase
      .from('workspace_members')
      .update({ role })
      .eq('workspace_id', currentWorkspace.id)
      .eq('user_id', userId);

    setMembers(prev =>
      prev.map(m =>
        m.user_id === userId ? { ...m, role: role as WorkspaceMember['role'] } : m
      )
    );
  }, [currentWorkspace, supabase]);

  return (
    <WorkspaceContext.Provider
      value={{
        currentWorkspace,
        workspaces,
        members,
        loading,
        error,
        switchWorkspace,
        createWorkspace,
        inviteMember,
        removeMember,
        updateMemberRole,
      }}
    >
      {children}
    </WorkspaceContext.Provider>
  );
}

export function useWorkspace() {
  const context = useContext(WorkspaceContext);
  if (context === undefined) {
    throw new Error('useWorkspace must be used within a WorkspaceProvider');
  }
  return context;
}
```

## 4.3 Verification Checklist - Phase 4

- [ ] Workspace creation flow works correctly
- [ ] Users auto-become owners of created workspaces
- [ ] Workspace switching updates user profile
- [ ] Member invitation works
- [ ] Role updates work correctly
- [ ] Member removal works
- [ ] Data is properly isolated between workspaces

---

# PHASE 5: SESSION MANAGEMENT & TOKEN SECURITY

## 5.1 Overview

Proper session management prevents session hijacking, ensures token freshness, and handles edge cases like concurrent sessions.

## 5.2 Token Refresh Strategy

### 5.2.1 Automatic Token Refresh

```typescript
// src/lib/auth/tokenRefresh.ts

import { createClient } from '@/lib/supabase/client';

const TOKEN_REFRESH_MARGIN = 60 * 5; // 5 minutes before expiry

export class TokenManager {
  private refreshTimer: NodeJS.Timeout | null = null;
  private supabase = createClient();

  async initialize() {
    const { data: { session } } = await this.supabase.auth.getSession();
    
    if (session) {
      this.scheduleRefresh(session.expires_at!);
    }

    // Listen for auth changes
    this.supabase.auth.onAuthStateChange((event, session) => {
      if (event === 'TOKEN_REFRESHED' && session) {
        this.scheduleRefresh(session.expires_at!);
      }
      
      if (event === 'SIGNED_OUT') {
        this.clearRefreshTimer();
      }
    });
  }

  private scheduleRefresh(expiresAt: number) {
    this.clearRefreshTimer();

    const now = Math.floor(Date.now() / 1000);
    const timeUntilExpiry = expiresAt - now;
    const refreshIn = Math.max(0, timeUntilExpiry - TOKEN_REFRESH_MARGIN) * 1000;

    this.refreshTimer = setTimeout(async () => {
      try {
        const { error } = await this.supabase.auth.refreshSession();
        if (error) {
          console.error('Token refresh failed:', error);
          // Force re-login
          window.location.href = '/login?expired=true';
        }
      } catch (err) {
        console.error('Token refresh error:', err);
      }
    }, refreshIn);
  }

  private clearRefreshTimer() {
    if (this.refreshTimer) {
      clearTimeout(this.refreshTimer);
      this.refreshTimer = null;
    }
  }

  destroy() {
    this.clearRefreshTimer();
  }
}

export const tokenManager = new TokenManager();
```

### 5.2.2 Session Validation Hook

```typescript
// src/hooks/useSessionValidation.ts

import { useEffect, useCallback } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { createClient } from '@/lib/supabase/client';

export function useSessionValidation() {
  const { user, signOut } = useAuth();
  const supabase = createClient();

  const validateSession = useCallback(async () => {
    if (!user) return;

    try {
      // Verify session is still valid on server
      const { data: { user: currentUser }, error } = await supabase.auth.getUser();

      if (error || !currentUser) {
        console.warn('Session invalid, signing out');
        await signOut();
      }
    } catch (err) {
      console.error('Session validation failed:', err);
    }
  }, [user, supabase, signOut]);

  // Validate on focus (when user returns to tab)
  useEffect(() => {
    const handleFocus = () => {
      validateSession();
    };

    window.addEventListener('focus', handleFocus);
    return () => window.removeEventListener('focus', handleFocus);
  }, [validateSession]);

  // Validate periodically (every 5 minutes)
  useEffect(() => {
    const interval = setInterval(validateSession, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [validateSession]);

  return { validateSession };
}
```

## 5.3 Secure Cookie Configuration

### 5.3.1 Cookie Settings

```typescript
// src/lib/supabase/cookieOptions.ts

import { type CookieOptions } from '@supabase/ssr';

export const secureCookieOptions: CookieOptions = {
  path: '/',
  sameSite: 'lax',
  secure: process.env.NODE_ENV === 'production',
  httpOnly: true,
  maxAge: 60 * 60 * 24 * 7, // 7 days
};

// For access tokens (shorter lived)
export const accessTokenCookieOptions: CookieOptions = {
  ...secureCookieOptions,
  maxAge: 60 * 60, // 1 hour
};

// For refresh tokens (longer lived)
export const refreshTokenCookieOptions: CookieOptions = {
  ...secureCookieOptions,
  maxAge: 60 * 60 * 24 * 30, // 30 days
};
```

## 5.4 Concurrent Session Handling

### 5.4.1 Session Tracking Table

```sql
-- supabase/migrations/007_session_tracking.sql

CREATE TABLE IF NOT EXISTS public.user_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  session_token TEXT NOT NULL,
  device_info JSONB DEFAULT '{}',
  ip_address INET,
  last_active TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  expires_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX idx_user_sessions_user ON public.user_sessions(user_id);
CREATE INDEX idx_user_sessions_token ON public.user_sessions(session_token);
CREATE INDEX idx_user_sessions_expires ON public.user_sessions(expires_at);

ALTER TABLE public.user_sessions ENABLE ROW LEVEL SECURITY;

-- Users can only see their own sessions
CREATE POLICY "user_sessions_select_own" ON public.user_sessions
  FOR SELECT
  USING (user_id = auth.uid());

-- Users can delete their own sessions (logout from devices)
CREATE POLICY "user_sessions_delete_own" ON public.user_sessions
  FOR DELETE
  USING (user_id = auth.uid());

-- Cleanup function for expired sessions
CREATE OR REPLACE FUNCTION public.cleanup_expired_sessions()
RETURNS void AS $$
BEGIN
  DELETE FROM public.user_sessions
  WHERE expires_at < NOW();
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

## 5.5 Verification Checklist - Phase 5

- [ ] Tokens refresh automatically before expiry
- [ ] Session validation runs on tab focus
- [ ] Cookies are properly secured (httpOnly, secure, sameSite)
- [ ] Concurrent sessions are tracked
- [ ] Users can view/revoke their sessions
- [ ] Expired sessions are cleaned up
- [ ] Token refresh failures trigger re-login

---

# PHASE 6: PAYMENT INTEGRATION (PHONEPE)

## 6.1 Overview

PhonePe integration enables seamless payment collection for subscriptions. This phase covers the complete payment flow from initiation to webhook handling.

## 6.2 PhonePe Configuration

### 6.2.1 Environment Variables

```bash
# .env.production
PHONEPE_MERCHANT_ID=your_merchant_id
PHONEPE_SALT_KEY=your_salt_key
PHONEPE_SALT_INDEX=1
PHONEPE_ENV=PRODUCTION  # or UAT for testing
PHONEPE_CALLBACK_URL=https://your-domain.com/api/webhooks/phonepe
```

### 6.2.2 PhonePe Client Setup

```python
# backend/services/phonepe_client.py

import hashlib
import base64
import json
import uuid
import requests
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import os

class PhonePeEnv(Enum):
    UAT = "https://api-preprod.phonepe.com/apis/pg-sandbox"
    PRODUCTION = "https://api.phonepe.com/apis/hermes"

@dataclass
class PaymentRequest:
    merchant_id: str
    merchant_transaction_id: str
    amount: int  # Amount in paise
    redirect_url: str
    callback_url: str
    user_id: str
    mobile_number: Optional[str] = None

@dataclass
class PaymentResponse:
    success: bool
    code: str
    message: str
    transaction_id: Optional[str] = None
    redirect_url: Optional[str] = None
    data: Optional[Dict] = None

class PhonePeClient:
    def __init__(self):
        self.merchant_id = os.environ.get("PHONEPE_MERCHANT_ID")
        self.salt_key = os.environ.get("PHONEPE_SALT_KEY")
        self.salt_index = os.environ.get("PHONEPE_SALT_INDEX", "1")
        env = os.environ.get("PHONEPE_ENV", "UAT")
        self.base_url = PhonePeEnv[env].value
        
        if not all([self.merchant_id, self.salt_key]):
            raise ValueError("PhonePe credentials not configured")
    
    def _generate_checksum(self, payload: str, endpoint: str) -> str:
        """Generate X-VERIFY checksum for PhonePe API."""
        data_to_hash = payload + endpoint + self.salt_key
        sha256_hash = hashlib.sha256(data_to_hash.encode()).hexdigest()
        return f"{sha256_hash}###{self.salt_index}"
    
    def _encode_payload(self, data: Dict) -> str:
        """Base64 encode the payload."""
        json_str = json.dumps(data)
        return base64.b64encode(json_str.encode()).decode()
    
    def initiate_payment(self, request: PaymentRequest) -> PaymentResponse:
        """
        Initiate a payment request to PhonePe.
        """
        endpoint = "/pg/v1/pay"
        
        payload_data = {
            "merchantId": self.merchant_id,
            "merchantTransactionId": request.merchant_transaction_id,
            "merchantUserId": request.user_id,
            "amount": request.amount,
            "redirectUrl": request.redirect_url,
            "redirectMode": "POST",
            "callbackUrl": request.callback_url,
            "paymentInstrument": {
                "type": "PAY_PAGE"
            }
        }
        
        if request.mobile_number:
            payload_data["mobileNumber"] = request.mobile_number
        
        encoded_payload = self._encode_payload(payload_data)
        checksum = self._generate_checksum(encoded_payload, endpoint)
        
        headers = {
            "Content-Type": "application/json",
            "X-VERIFY": checksum
        }
        
        body = {
            "request": encoded_payload
        }
        
        try:
            response = requests.post(
                f"{self.base_url}{endpoint}",
                json=body,
                headers=headers,
                timeout=30
            )
            
            result = response.json()
            
            if result.get("success"):
                redirect_url = result.get("data", {}).get("instrumentResponse", {}).get("redirectInfo", {}).get("url")
                return PaymentResponse(
                    success=True,
                    code=result.get("code", "SUCCESS"),
                    message=result.get("message", "Payment initiated"),
                    transaction_id=request.merchant_transaction_id,
                    redirect_url=redirect_url,
                    data=result.get("data")
                )
            else:
                return PaymentResponse(
                    success=False,
                    code=result.get("code", "FAILURE"),
                    message=result.get("message", "Payment initiation failed"),
                    data=result
                )
                
        except requests.RequestException as e:
            return PaymentResponse(
                success=False,
                code="NETWORK_ERROR",
                message=str(e)
            )
    
    def check_payment_status(self, merchant_transaction_id: str) -> PaymentResponse:
        """
        Check the status of a payment.
        """
        endpoint = f"/pg/v1/status/{self.merchant_id}/{merchant_transaction_id}"
        
        checksum = self._generate_checksum("", endpoint)
        
        headers = {
            "Content-Type": "application/json",
            "X-VERIFY": checksum,
            "X-MERCHANT-ID": self.merchant_id
        }
        
        try:
            response = requests.get(
                f"{self.base_url}{endpoint}",
                headers=headers,
                timeout=30
            )
            
            result = response.json()
            
            return PaymentResponse(
                success=result.get("success", False),
                code=result.get("code", "UNKNOWN"),
                message=result.get("message", ""),
                transaction_id=merchant_transaction_id,
                data=result.get("data")
            )
            
        except requests.RequestException as e:
            return PaymentResponse(
                success=False,
                code="NETWORK_ERROR",
                message=str(e)
            )
    
    def verify_webhook_signature(self, payload: str, received_checksum: str) -> bool:
        """
        Verify the webhook callback signature.
        """
        expected_checksum = self._generate_checksum(payload, "/pg/v1/pay")
        return expected_checksum == received_checksum

# Singleton instance
phonepe_client = PhonePeClient()
```

## 6.3 Payment Database Schema

### 6.3.1 Payments Table

```sql
-- supabase/migrations/008_payments.sql

CREATE TABLE IF NOT EXISTS public.payments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES public.workspaces(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES auth.users(id),
  
  -- Transaction details
  merchant_transaction_id TEXT UNIQUE NOT NULL,
  phonepe_transaction_id TEXT,
  amount INTEGER NOT NULL,  -- Amount in paise
  currency TEXT NOT NULL DEFAULT 'INR',
  
  -- Status tracking
  status TEXT NOT NULL DEFAULT 'initiated' 
    CHECK (status IN ('initiated', 'pending', 'success', 'failed', 'refunded')),
  payment_method TEXT,
  
  -- Subscription linkage
  subscription_id UUID REFERENCES public.subscriptions(id),
  plan_id TEXT,
  
  -- Metadata
  metadata JSONB DEFAULT '{}',
  error_code TEXT,
  error_message TEXT,
  
  -- Timestamps
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  completed_at TIMESTAMPTZ
);

CREATE INDEX idx_payments_workspace ON public.payments(workspace_id);
CREATE INDEX idx_payments_user ON public.payments(user_id);
CREATE INDEX idx_payments_status ON public.payments(status);
CREATE INDEX idx_payments_merchant_txn ON public.payments(merchant_transaction_id);

ALTER TABLE public.payments ENABLE ROW LEVEL SECURITY;

-- Users can view their workspace payments
CREATE POLICY "payments_select_workspace" ON public.payments
  FOR SELECT
  USING (
    workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid()
    )
  );

-- Only system can insert/update payments (via service role)
CREATE POLICY "payments_insert_system" ON public.payments
  FOR INSERT
  WITH CHECK (false);  -- Disabled for anon, use service role

CREATE POLICY "payments_update_system" ON public.payments
  FOR UPDATE
  USING (false);  -- Disabled for anon, use service role
```

## 6.4 Payment API Endpoints

### 6.4.1 Payment Routes

```python
# backend/api/v1/payments.py

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
import uuid

from core.auth import verify_token
from services.phonepe_client import phonepe_client, PaymentRequest
from services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])

class InitiatePaymentRequest(BaseModel):
    plan_id: str
    amount: int  # Amount in rupees
    redirect_url: str

class PaymentStatusResponse(BaseModel):
    transaction_id: str
    status: str
    amount: int
    created_at: str
    completed_at: Optional[str]

@router.post("/initiate")
async def initiate_payment(
    request: InitiatePaymentRequest,
    user: dict = Depends(verify_token)
):
    """
    Initiate a new payment for subscription.
    """
    payment_service = PaymentService()
    
    # Generate unique transaction ID
    merchant_transaction_id = f"TXN_{uuid.uuid4().hex[:16].upper()}"
    
    # Amount in paise (multiply by 100)
    amount_paise = request.amount * 100
    
    # Create payment record
    payment = await payment_service.create_payment(
        workspace_id=user['workspace_id'],
        user_id=user['id'],
        merchant_transaction_id=merchant_transaction_id,
        amount=amount_paise,
        plan_id=request.plan_id
    )
    
    # Initiate PhonePe payment
    phonepe_request = PaymentRequest(
        merchant_id=phonepe_client.merchant_id,
        merchant_transaction_id=merchant_transaction_id,
        amount=amount_paise,
        redirect_url=request.redirect_url,
        callback_url=f"{os.environ.get('API_URL')}/api/webhooks/phonepe",
        user_id=user['id']
    )
    
    response = phonepe_client.initiate_payment(phonepe_request)
    
    if not response.success:
        await payment_service.update_payment_status(
            merchant_transaction_id,
            status='failed',
            error_code=response.code,
            error_message=response.message
        )
        raise HTTPException(status_code=400, detail=response.message)
    
    return {
        "transaction_id": merchant_transaction_id,
        "redirect_url": response.redirect_url
    }

@router.get("/status/{transaction_id}")
async def get_payment_status(
    transaction_id: str,
    user: dict = Depends(verify_token)
):
    """
    Get payment status.
    """
    payment_service = PaymentService()
    
    payment = await payment_service.get_payment(transaction_id)
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Verify user has access
    if payment['user_id'] != user['id']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return PaymentStatusResponse(
        transaction_id=payment['merchant_transaction_id'],
        status=payment['status'],
        amount=payment['amount'] // 100,  # Convert back to rupees
        created_at=payment['created_at'].isoformat(),
        completed_at=payment.get('completed_at', '').isoformat() if payment.get('completed_at') else None
    )

@router.get("/history")
async def get_payment_history(
    user: dict = Depends(verify_token),
    limit: int = 20,
    offset: int = 0
):
    """
    Get payment history for workspace.
    """
    payment_service = PaymentService()
    
    payments = await payment_service.get_workspace_payments(
        workspace_id=user['workspace_id'],
        limit=limit,
        offset=offset
    )
    
    return {
        "payments": [
            {
                "transaction_id": p['merchant_transaction_id'],
                "amount": p['amount'] // 100,
                "status": p['status'],
                "plan_id": p['plan_id'],
                "created_at": p['created_at'].isoformat()
            }
            for p in payments
        ]
    }
```

### 6.4.2 Webhook Handler

```python
# backend/api/webhooks/phonepe.py

from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
import base64
import json

from services.phonepe_client import phonepe_client
from services.payment_service import PaymentService
from services.subscription_service import SubscriptionService

router = APIRouter()

@router.post("/api/webhooks/phonepe")
async def phonepe_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Handle PhonePe payment callbacks.
    """
    try:
        body = await request.json()
        
        # Verify signature
        x_verify = request.headers.get("X-VERIFY", "")
        encoded_response = body.get("response", "")
        
        if not phonepe_client.verify_webhook_signature(encoded_response, x_verify):
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        # Decode response
        decoded = base64.b64decode(encoded_response).decode()
        payment_data = json.loads(decoded)
        
        merchant_transaction_id = payment_data.get("merchantTransactionId")
        status_code = payment_data.get("code")
        
        payment_service = PaymentService()
        subscription_service = SubscriptionService()
        
        if status_code == "PAYMENT_SUCCESS":
            # Update payment status
            await payment_service.update_payment_status(
                merchant_transaction_id,
                status='success',
                phonepe_transaction_id=payment_data.get("transactionId"),
                completed_at=True
            )
            
            # Get payment details
            payment = await payment_service.get_payment(merchant_transaction_id)
            
            if payment and payment.get('plan_id'):
                # Activate subscription
                background_tasks.add_task(
                    subscription_service.activate_subscription,
                    workspace_id=payment['workspace_id'],
                    plan_id=payment['plan_id'],
                    payment_id=payment['id']
                )
        
        elif status_code in ["PAYMENT_ERROR", "PAYMENT_DECLINED"]:
            await payment_service.update_payment_status(
                merchant_transaction_id,
                status='failed',
                error_code=status_code,
                error_message=payment_data.get("message", "Payment failed")
            )
        
        return {"status": "received"}
        
    except Exception as e:
        print(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

## 6.5 Verification Checklist - Phase 6

- [ ] PhonePe credentials configured
- [ ] Payment initiation works in UAT
- [ ] Redirect to PhonePe payment page works
- [ ] Webhook receives callbacks
- [ ] Signature verification works
- [ ] Payment status updates correctly
- [ ] Failed payments handled properly
- [ ] Payment history displays correctly

---

# PHASE 7: SUBSCRIPTION MANAGEMENT

## 7.1 Overview

Subscription management handles plan tiers, billing cycles, feature access, and usage tracking.

## 7.2 Subscription Database Schema

### 7.2.1 Plans and Subscriptions Tables

```sql
-- supabase/migrations/009_subscriptions.sql

-- Plans table (static plan definitions)
CREATE TABLE IF NOT EXISTS public.plans (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  
  -- Pricing
  price_monthly INTEGER NOT NULL,  -- Price in paise
  price_yearly INTEGER,
  
  -- Limits
  max_users INTEGER NOT NULL DEFAULT 1,
  max_campaigns INTEGER NOT NULL DEFAULT 5,
  max_api_calls INTEGER NOT NULL DEFAULT 1000,
  max_storage_mb INTEGER NOT NULL DEFAULT 100,
  
  -- Features (JSON array of feature keys)
  features JSONB NOT NULL DEFAULT '[]',
  
  -- Display
  is_public BOOLEAN NOT NULL DEFAULT true,
  sort_order INTEGER NOT NULL DEFAULT 0,
  
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Insert default plans
INSERT INTO public.plans (id, name, description, price_monthly, price_yearly, max_users, max_campaigns, max_api_calls, max_storage_mb, features, sort_order) VALUES
  ('free', 'Free', 'Get started for free', 0, 0, 1, 3, 500, 50, '["basic_analytics", "email_support"]', 0),
  ('starter', 'Starter', 'Perfect for small teams', 99900, 999000, 5, 10, 5000, 500, '["basic_analytics", "priority_support", "api_access"]', 1),
  ('pro', 'Pro', 'For growing businesses', 299900, 2999000, 20, 50, 50000, 5000, '["advanced_analytics", "priority_support", "api_access", "custom_branding", "webhooks"]', 2),
  ('enterprise', 'Enterprise', 'Custom solutions', 0, 0, -1, -1, -1, -1, '["all_features", "dedicated_support", "sla", "custom_integrations"]', 3)
ON CONFLICT (id) DO NOTHING;

-- Subscriptions table
CREATE TABLE IF NOT EXISTS public.subscriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES public.workspaces(id) ON DELETE CASCADE,
  plan_id TEXT NOT NULL REFERENCES public.plans(id),
  
  -- Status
  status TEXT NOT NULL DEFAULT 'active' 
    CHECK (status IN ('active', 'past_due', 'cancelled', 'expired', 'trialing')),
  
  -- Billing cycle
  billing_cycle TEXT NOT NULL DEFAULT 'monthly' CHECK (billing_cycle IN ('monthly', 'yearly')),
  current_period_start TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  current_period_end TIMESTAMPTZ NOT NULL,
  
  -- Trial
  trial_start TIMESTAMPTZ,
  trial_end TIMESTAMPTZ,
  
  -- Cancellation
  cancel_at_period_end BOOLEAN NOT NULL DEFAULT false,
  cancelled_at TIMESTAMPTZ,
  
  -- Payment
  last_payment_id UUID REFERENCES public.payments(id),
  
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  
  UNIQUE(workspace_id)
);

CREATE INDEX idx_subscriptions_workspace ON public.subscriptions(workspace_id);
CREATE INDEX idx_subscriptions_status ON public.subscriptions(status);
CREATE INDEX idx_subscriptions_period_end ON public.subscriptions(current_period_end);

ALTER TABLE public.subscriptions ENABLE ROW LEVEL SECURITY;

-- Users can view their workspace subscription
CREATE POLICY "subscriptions_select_workspace" ON public.subscriptions
  FOR SELECT
  USING (
    workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid()
    )
  );

-- Usage tracking table
CREATE TABLE IF NOT EXISTS public.usage_records (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES public.workspaces(id) ON DELETE CASCADE,
  
  -- Usage metrics
  metric_name TEXT NOT NULL,
  usage_count INTEGER NOT NULL DEFAULT 0,
  
  -- Period
  period_start TIMESTAMPTZ NOT NULL,
  period_end TIMESTAMPTZ NOT NULL,
  
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  
  UNIQUE(workspace_id, metric_name, period_start)
);

CREATE INDEX idx_usage_workspace ON public.usage_records(workspace_id);
CREATE INDEX idx_usage_period ON public.usage_records(period_start, period_end);

ALTER TABLE public.usage_records ENABLE ROW LEVEL SECURITY;

CREATE POLICY "usage_select_workspace" ON public.usage_records
  FOR SELECT
  USING (
    workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid()
    )
  );
```

## 7.3 Subscription Service

### 7.3.1 Backend Subscription Logic

```python
# backend/services/subscription_service.py

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass
import os

from supabase import create_client

@dataclass
class Subscription:
    id: str
    workspace_id: str
    plan_id: str
    status: str
    billing_cycle: str
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool

@dataclass
class Plan:
    id: str
    name: str
    price_monthly: int
    price_yearly: int
    max_users: int
    max_campaigns: int
    max_api_calls: int
    max_storage_mb: int
    features: List[str]

class SubscriptionService:
    def __init__(self):
        self.supabase = create_client(
            os.environ.get("SUPABASE_URL"),
            os.environ.get("SUPABASE_SERVICE_KEY")  # Use service key for admin operations
        )
    
    async def get_plan(self, plan_id: str) -> Optional[Plan]:
        """Get plan details by ID."""
        result = self.supabase.table('plans').select('*').eq('id', plan_id).single().execute()
        
        if not result.data:
            return None
        
        return Plan(**result.data)
    
    async def get_all_plans(self, public_only: bool = True) -> List[Plan]:
        """Get all available plans."""
        query = self.supabase.table('plans').select('*').order('sort_order')
        
        if public_only:
            query = query.eq('is_public', True)
        
        result = query.execute()
        return [Plan(**p) for p in result.data]
    
    async def get_subscription(self, workspace_id: str) -> Optional[Subscription]:
        """Get current subscription for workspace."""
        result = self.supabase.table('subscriptions') \
            .select('*') \
            .eq('workspace_id', workspace_id) \
            .single() \
            .execute()
        
        if not result.data:
            return None
        
        return Subscription(**result.data)
    
    async def create_subscription(
        self,
        workspace_id: str,
        plan_id: str,
        billing_cycle: str = 'monthly',
        trial_days: int = 0
    ) -> Subscription:
        """Create a new subscription."""
        now = datetime.utcnow()
        
        if billing_cycle == 'monthly':
            period_end = now + timedelta(days=30)
        else:
            period_end = now + timedelta(days=365)
        
        data = {
            'workspace_id': workspace_id,
            'plan_id': plan_id,
            'billing_cycle': billing_cycle,
            'status': 'trialing' if trial_days > 0 else 'active',
            'current_period_start': now.isoformat(),
            'current_period_end': period_end.isoformat(),
        }
        
        if trial_days > 0:
            data['trial_start'] = now.isoformat()
            data['trial_end'] = (now + timedelta(days=trial_days)).isoformat()
        
        result = self.supabase.table('subscriptions').insert(data).execute()
        
        # Update workspace plan
        self.supabase.table('workspaces').update({
            'plan': plan_id
        }).eq('id', workspace_id).execute()
        
        return Subscription(**result.data[0])
    
    async def activate_subscription(
        self,
        workspace_id: str,
        plan_id: str,
        payment_id: str
    ) -> Subscription:
        """Activate subscription after successful payment."""
        now = datetime.utcnow()
        
        # Get billing cycle from existing subscription or default to monthly
        existing = await self.get_subscription(workspace_id)
        billing_cycle = existing.billing_cycle if existing else 'monthly'
        
        if billing_cycle == 'monthly':
            period_end = now + timedelta(days=30)
        else:
            period_end = now + timedelta(days=365)
        
        data = {
            'plan_id': plan_id,
            'status': 'active',
            'current_period_start': now.isoformat(),
            'current_period_end': period_end.isoformat(),
            'last_payment_id': payment_id,
            'cancel_at_period_end': False,
            'trial_end': None,
        }
        
        if existing:
            result = self.supabase.table('subscriptions') \
                .update(data) \
                .eq('workspace_id', workspace_id) \
                .execute()
        else:
            data['workspace_id'] = workspace_id
            data['billing_cycle'] = billing_cycle
            result = self.supabase.table('subscriptions').insert(data).execute()
        
        # Update workspace plan
        self.supabase.table('workspaces').update({
            'plan': plan_id
        }).eq('id', workspace_id).execute()
        
        return Subscription(**result.data[0])
    
    async def cancel_subscription(
        self,
        workspace_id: str,
        immediate: bool = False
    ) -> Subscription:
        """Cancel subscription."""
        now = datetime.utcnow()
        
        if immediate:
            data = {
                'status': 'cancelled',
                'cancelled_at': now.isoformat(),
            }
        else:
            data = {
                'cancel_at_period_end': True,
                'cancelled_at': now.isoformat(),
            }
        
        result = self.supabase.table('subscriptions') \
            .update(data) \
            .eq('workspace_id', workspace_id) \
            .execute()
        
        if immediate:
            # Downgrade to free plan
            self.supabase.table('workspaces').update({
                'plan': 'free'
            }).eq('id', workspace_id).execute()
        
        return Subscription(**result.data[0])
    
    async def check_feature_access(
        self,
        workspace_id: str,
        feature: str
    ) -> bool:
        """Check if workspace has access to a feature."""
        subscription = await self.get_subscription(workspace_id)
        
        if not subscription or subscription.status not in ['active', 'trialing']:
            # Default to free plan features
            plan = await self.get_plan('free')
        else:
            plan = await self.get_plan(subscription.plan_id)
        
        if not plan:
            return False
        
        return feature in plan.features or 'all_features' in plan.features
    
    async def check_usage_limit(
        self,
        workspace_id: str,
        metric: str,
        increment: int = 1
    ) -> Dict[str, Any]:
        """Check if workspace is within usage limits."""
        subscription = await self.get_subscription(workspace_id)
        
        if not subscription:
            plan = await self.get_plan('free')
        else:
            plan = await self.get_plan(subscription.plan_id)
        
        # Get limit for metric
        limit_map = {
            'users': plan.max_users,
            'campaigns': plan.max_campaigns,
            'api_calls': plan.max_api_calls,
            'storage_mb': plan.max_storage_mb,
        }
        
        limit = limit_map.get(metric, 0)
        
        # -1 means unlimited
        if limit == -1:
            return {'allowed': True, 'current': 0, 'limit': -1}
        
        # Get current usage
        now = datetime.utcnow()
        period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        usage_result = self.supabase.table('usage_records') \
            .select('usage_count') \
            .eq('workspace_id', workspace_id) \
            .eq('metric_name', metric) \
            .gte('period_start', period_start.isoformat()) \
            .execute()
        
        current_usage = sum(u['usage_count'] for u in usage_result.data) if usage_result.data else 0
        
        return {
            'allowed': (current_usage + increment) <= limit,
            'current': current_usage,
            'limit': limit,
            'remaining': max(0, limit - current_usage)
        }
    
    async def record_usage(
        self,
        workspace_id: str,
        metric: str,
        count: int = 1
    ):
        """Record usage for a metric."""
        now = datetime.utcnow()
        period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        period_end = (period_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
        
        # Upsert usage record
        self.supabase.rpc('increment_usage', {
            'p_workspace_id': workspace_id,
            'p_metric_name': metric,
            'p_count': count,
            'p_period_start': period_start.isoformat(),
            'p_period_end': period_end.isoformat()
        }).execute()
```

## 7.4 Verification Checklist - Phase 7

- [ ] Plans table populated with tiers
- [ ] Subscription creation works
- [ ] Trial periods work correctly
- [ ] Feature access checks work
- [ ] Usage limits enforced
- [ ] Subscription cancellation works
- [ ] Period renewal logic correct
- [ ] Downgrade to free works

---

# PHASE 8: CUSTOMER ID & BILLING

## 8.1 Overview

Customer ID management links users to their billing entities, enabling proper invoice generation and customer support.

## 8.2 Customer Management Schema

```sql
-- supabase/migrations/010_customers.sql

CREATE TABLE IF NOT EXISTS public.customers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES public.workspaces(id) ON DELETE CASCADE,
  
  -- Customer identification
  customer_id TEXT UNIQUE NOT NULL,  -- Formatted customer ID
  
  -- Billing information
  billing_name TEXT,
  billing_email TEXT NOT NULL,
  billing_phone TEXT,
  billing_address JSONB DEFAULT '{}',
  
  -- Tax information
  gstin TEXT,  -- GST Number for India
  pan TEXT,    -- PAN for India
  
  -- Preferences
  currency TEXT NOT NULL DEFAULT 'INR',
  invoice_prefix TEXT,
  
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  
  UNIQUE(workspace_id)
);

CREATE INDEX idx_customers_workspace ON public.customers(workspace_id);
CREATE INDEX idx_customers_customer_id ON public.customers(customer_id);

-- Customer ID sequence
CREATE SEQUENCE IF NOT EXISTS customer_id_seq START 10000;

-- Function to generate customer ID
CREATE OR REPLACE FUNCTION public.generate_customer_id()
RETURNS TEXT AS $$
BEGIN
  RETURN 'RF-' || LPAD(nextval('customer_id_seq')::TEXT, 6, '0');
END;
$$ LANGUAGE plpgsql;

-- Invoices table
CREATE TABLE IF NOT EXISTS public.invoices (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL REFERENCES public.customers(id),
  workspace_id UUID NOT NULL REFERENCES public.workspaces(id),
  payment_id UUID REFERENCES public.payments(id),
  
  -- Invoice details
  invoice_number TEXT UNIQUE NOT NULL,
  invoice_date DATE NOT NULL DEFAULT CURRENT_DATE,
  due_date DATE,
  
  -- Amounts (all in paise)
  subtotal INTEGER NOT NULL,
  tax_amount INTEGER NOT NULL DEFAULT 0,
  discount_amount INTEGER NOT NULL DEFAULT 0,
  total_amount INTEGER NOT NULL,
  
  -- Tax breakdown
  cgst_amount INTEGER DEFAULT 0,
  sgst_amount INTEGER DEFAULT 0,
  igst_amount INTEGER DEFAULT 0,
  
  -- Status
  status TEXT NOT NULL DEFAULT 'draft' 
    CHECK (status IN ('draft', 'sent', 'paid', 'cancelled', 'refunded')),
  
  -- Line items
  line_items JSONB NOT NULL DEFAULT '[]',
  
  -- PDF storage
  pdf_url TEXT,
  
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_invoices_customer ON public.invoices(customer_id);
CREATE INDEX idx_invoices_workspace ON public.invoices(workspace_id);
CREATE INDEX idx_invoices_date ON public.invoices(invoice_date);

-- Invoice number sequence
CREATE SEQUENCE IF NOT EXISTS invoice_number_seq START 1;

-- Function to generate invoice number
CREATE OR REPLACE FUNCTION public.generate_invoice_number()
RETURNS TEXT AS $$
BEGIN
  RETURN 'INV-' || TO_CHAR(CURRENT_DATE, 'YYYYMM') || '-' || 
         LPAD(nextval('invoice_number_seq')::TEXT, 5, '0');
END;
$$ LANGUAGE plpgsql;

ALTER TABLE public.customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.invoices ENABLE ROW LEVEL SECURITY;

-- RLS policies
CREATE POLICY "customers_select_workspace" ON public.customers
  FOR SELECT USING (
    workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
    )
  );

CREATE POLICY "invoices_select_workspace" ON public.invoices
  FOR SELECT USING (
    workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid()
    )
  );
```

## 8.3 Customer Service

```python
# backend/services/customer_service.py

from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import os

from supabase import create_client

@dataclass
class Customer:
    id: str
    workspace_id: str
    customer_id: str
    billing_name: Optional[str]
    billing_email: str
    billing_phone: Optional[str]
    billing_address: Dict
    gstin: Optional[str]
    pan: Optional[str]
    currency: str

@dataclass
class Invoice:
    id: str
    invoice_number: str
    customer_id: str
    total_amount: int
    status: str
    invoice_date: str
    pdf_url: Optional[str]

class CustomerService:
    def __init__(self):
        self.supabase = create_client(
            os.environ.get("SUPABASE_URL"),
            os.environ.get("SUPABASE_SERVICE_KEY")
        )
    
    async def get_or_create_customer(
        self,
        workspace_id: str,
        billing_email: str,
        billing_name: Optional[str] = None
    ) -> Customer:
        """Get existing customer or create new one."""
        # Check for existing customer
        result = self.supabase.table('customers') \
            .select('*') \
            .eq('workspace_id', workspace_id) \
            .single() \
            .execute()
        
        if result.data:
            return Customer(**result.data)
        
        # Generate customer ID
        customer_id_result = self.supabase.rpc('generate_customer_id').execute()
        customer_id = customer_id_result.data
        
        # Create new customer
        data = {
            'workspace_id': workspace_id,
            'customer_id': customer_id,
            'billing_email': billing_email,
            'billing_name': billing_name,
        }
        
        result = self.supabase.table('customers').insert(data).execute()
        return Customer(**result.data[0])
    
    async def update_billing_info(
        self,
        workspace_id: str,
        billing_info: Dict[str, Any]
    ) -> Customer:
        """Update customer billing information."""
        allowed_fields = [
            'billing_name', 'billing_email', 'billing_phone',
            'billing_address', 'gstin', 'pan'
        ]
        
        update_data = {k: v for k, v in billing_info.items() if k in allowed_fields}
        
        result = self.supabase.table('customers') \
            .update(update_data) \
            .eq('workspace_id', workspace_id) \
            .execute()
        
        return Customer(**result.data[0])
    
    async def create_invoice(
        self,
        customer_id: str,
        workspace_id: str,
        payment_id: str,
        line_items: list,
        tax_rate: float = 0.18  # 18% GST
    ) -> Invoice:
        """Create invoice after successful payment."""
        # Calculate totals
        subtotal = sum(item['amount'] for item in line_items)
        tax_amount = int(subtotal * tax_rate)
        total_amount = subtotal + tax_amount
        
        # Generate invoice number
        invoice_number_result = self.supabase.rpc('generate_invoice_number').execute()
        invoice_number = invoice_number_result.data
        
        data = {
            'customer_id': customer_id,
            'workspace_id': workspace_id,
            'payment_id': payment_id,
            'invoice_number': invoice_number,
            'subtotal': subtotal,
            'tax_amount': tax_amount,
            'total_amount': total_amount,
            'cgst_amount': tax_amount // 2,
            'sgst_amount': tax_amount // 2,
            'line_items': line_items,
            'status': 'paid',
        }
        
        result = self.supabase.table('invoices').insert(data).execute()
        return Invoice(**result.data[0])
    
    async def get_invoices(
        self,
        workspace_id: str,
        limit: int = 20
    ) -> list:
        """Get invoices for workspace."""
        result = self.supabase.table('invoices') \
            .select('*') \
            .eq('workspace_id', workspace_id) \
            .order('invoice_date', desc=True) \
            .limit(limit) \
            .execute()
        
        return [Invoice(**inv) for inv in result.data]
```

## 8.4 Verification Checklist - Phase 8

- [ ] Customer ID generation works
- [ ] Billing info can be updated
- [ ] Invoices are auto-generated after payment
- [ ] Invoice numbers are sequential
- [ ] Tax calculations are correct
- [ ] Invoice history displays properly

---

# PHASE 9: USER MANAGEMENT

## 9.1 Overview

User management enables workspace admins to invite, manage, and remove team members with role-based access.

## 9.2 User Management API

```python
# backend/api/v1/users.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List, Optional

from core.auth import verify_token, require_admin
from services.workspace_service import WorkspaceService
from services.subscription_service import SubscriptionService

router = APIRouter(prefix="/users", tags=["Users"])

class InviteUserRequest(BaseModel):
    email: EmailStr
    role: str = "member"

class UpdateUserRoleRequest(BaseModel):
    role: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    role: str
    created_at: str

@router.get("/")
async def list_workspace_users(user: dict = Depends(verify_token)):
    """List all users in the current workspace."""
    workspace_service = WorkspaceService()
    
    members = await workspace_service.get_workspace_members(user['workspace_id'])
    
    return {
        "users": [
            UserResponse(
                id=m['user_id'],
                email=m['profiles']['email'],
                full_name=m['profiles'].get('full_name'),
                role=m['role'],
                created_at=m['created_at']
            )
            for m in members
        ]
    }

@router.post("/invite")
async def invite_user(
    request: InviteUserRequest,
    user: dict = Depends(verify_token)
):
    """Invite a user to the workspace."""
    workspace_service = WorkspaceService()
    subscription_service = SubscriptionService()
    
    # Check user limit
    usage = await subscription_service.check_usage_limit(
        user['workspace_id'],
        'users'
    )
    
    if not usage['allowed']:
        raise HTTPException(
            status_code=403,
            detail=f"User limit reached ({usage['limit']}). Upgrade your plan."
        )
    
    # Validate role
    valid_roles = ['admin', 'member', 'viewer']
    if request.role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Invalid role. Use: {valid_roles}")
    
    try:
        member = await workspace_service.add_member(
            workspace_id=user['workspace_id'],
            user_email=request.email,
            role=request.role,
            invited_by=user['id']
        )
        
        # Record usage
        await subscription_service.record_usage(user['workspace_id'], 'users', 1)
        
        return {"success": True, "member_id": member.id}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{user_id}/role")
async def update_user_role(
    user_id: str,
    request: UpdateUserRoleRequest,
    user: dict = Depends(verify_token)
):
    """Update a user's role in the workspace."""
    workspace_service = WorkspaceService()
    
    # Check if current user is admin
    current_member = await workspace_service.get_member(
        user['workspace_id'],
        user['id']
    )
    
    if current_member.role not in ['owner', 'admin']:
        raise HTTPException(status_code=403, detail="Only admins can change roles")
    
    # Cannot change owner role
    target_member = await workspace_service.get_member(
        user['workspace_id'],
        user_id
    )
    
    if target_member.role == 'owner':
        raise HTTPException(status_code=403, detail="Cannot change owner role")
    
    valid_roles = ['admin', 'member', 'viewer']
    if request.role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Invalid role. Use: {valid_roles}")
    
    await workspace_service.update_member_role(
        user['workspace_id'],
        user_id,
        request.role
    )
    
    return {"success": True}

@router.delete("/{user_id}")
async def remove_user(
    user_id: str,
    user: dict = Depends(verify_token)
):
    """Remove a user from the workspace."""
    workspace_service = WorkspaceService()
    
    # Check permissions
    current_member = await workspace_service.get_member(
        user['workspace_id'],
        user['id']
    )
    
    if current_member.role not in ['owner', 'admin']:
        raise HTTPException(status_code=403, detail="Only admins can remove users")
    
    # Cannot remove owner
    target_member = await workspace_service.get_member(
        user['workspace_id'],
        user_id
    )
    
    if target_member.role == 'owner':
        raise HTTPException(status_code=403, detail="Cannot remove workspace owner")
    
    await workspace_service.remove_member(user['workspace_id'], user_id)
    
    return {"success": True}
```

## 9.3 Verification Checklist - Phase 9

- [ ] User listing works
- [ ] User invitation works
- [ ] Role updates work
- [ ] User removal works
- [ ] Permission checks enforced
- [ ] User limits enforced
- [ ] Owner cannot be removed

---

# PHASE 10: ADMIN PANEL

## 10.1 Overview

The admin panel provides system administrators with oversight and management capabilities across all workspaces.

## 10.2 Admin API Endpoints

```python
# backend/api/v1/admin.py

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from datetime import datetime, timedelta

from core.auth import verify_token, require_admin
from services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/dashboard")
@require_admin
async def admin_dashboard(request):
    """Get admin dashboard statistics."""
    admin_service = AdminService()
    
    stats = await admin_service.get_dashboard_stats()
    
    return {
        "total_users": stats['total_users'],
        "total_workspaces": stats['total_workspaces'],
        "active_subscriptions": stats['active_subscriptions'],
        "revenue_this_month": stats['revenue_this_month'],
        "new_users_today": stats['new_users_today'],
        "new_users_this_week": stats['new_users_this_week'],
    }

@router.get("/users")
@require_admin
async def list_all_users(
    request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None
):
    """List all users in the system."""
    admin_service = AdminService()
    
    users, total = await admin_service.list_users(
        page=page,
        limit=limit,
        search=search
    )
    
    return {
        "users": users,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }

@router.get("/workspaces")
@require_admin
async def list_all_workspaces(
    request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    plan: Optional[str] = None
):
    """List all workspaces."""
    admin_service = AdminService()
    
    workspaces, total = await admin_service.list_workspaces(
        page=page,
        limit=limit,
        plan_filter=plan
    )
    
    return {
        "workspaces": workspaces,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }

@router.get("/payments")
@require_admin
async def list_all_payments(
    request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
):
    """List all payments."""
    admin_service = AdminService()
    
    payments, total = await admin_service.list_payments(
        page=page,
        limit=limit,
        status=status,
        from_date=from_date,
        to_date=to_date
    )
    
    return {
        "payments": payments,
        "total": total,
        "total_amount": sum(p['amount'] for p in payments) // 100,
        "page": page
    }

@router.post("/users/{user_id}/suspend")
@require_admin
async def suspend_user(request, user_id: str):
    """Suspend a user account."""
    admin_service = AdminService()
    
    await admin_service.suspend_user(user_id)
    
    return {"success": True, "message": "User suspended"}

@router.post("/users/{user_id}/activate")
@require_admin
async def activate_user(request, user_id: str):
    """Activate a suspended user account."""
    admin_service = AdminService()
    
    await admin_service.activate_user(user_id)
    
    return {"success": True, "message": "User activated"}

@router.post("/workspaces/{workspace_id}/plan")
@require_admin
async def change_workspace_plan(
    request,
    workspace_id: str,
    plan_id: str
):
    """Manually change a workspace's plan (admin override)."""
    admin_service = AdminService()
    
    await admin_service.change_plan(workspace_id, plan_id)
    
    return {"success": True, "message": f"Plan changed to {plan_id}"}
```

## 10.3 Admin Service

```python
# backend/services/admin_service.py

from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta
import os

from supabase import create_client

class AdminService:
    def __init__(self):
        self.supabase = create_client(
            os.environ.get("SUPABASE_URL"),
            os.environ.get("SUPABASE_SERVICE_KEY")
        )
    
    async def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get admin dashboard statistics."""
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=7)
        month_start = today_start.replace(day=1)
        
        # Total users
        users_result = self.supabase.table('profiles').select('id', count='exact').execute()
        
        # Total workspaces
        workspaces_result = self.supabase.table('workspaces').select('id', count='exact').execute()
        
        # Active subscriptions
        subs_result = self.supabase.table('subscriptions') \
            .select('id', count='exact') \
            .eq('status', 'active') \
            .execute()
        
        # Revenue this month
        revenue_result = self.supabase.table('payments') \
            .select('amount') \
            .eq('status', 'success') \
            .gte('created_at', month_start.isoformat()) \
            .execute()
        
        revenue = sum(p['amount'] for p in revenue_result.data) if revenue_result.data else 0
        
        # New users today
        new_today = self.supabase.table('profiles') \
            .select('id', count='exact') \
            .gte('created_at', today_start.isoformat()) \
            .execute()
        
        # New users this week
        new_week = self.supabase.table('profiles') \
            .select('id', count='exact') \
            .gte('created_at', week_start.isoformat()) \
            .execute()
        
        return {
            'total_users': users_result.count or 0,
            'total_workspaces': workspaces_result.count or 0,
            'active_subscriptions': subs_result.count or 0,
            'revenue_this_month': revenue // 100,  # Convert to rupees
            'new_users_today': new_today.count or 0,
            'new_users_this_week': new_week.count or 0,
        }
    
    async def list_users(
        self,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None
    ) -> Tuple[List[Dict], int]:
        """List all users with pagination."""
        offset = (page - 1) * limit
        
        query = self.supabase.table('profiles').select('*', count='exact')
        
        if search:
            query = query.or_(f"email.ilike.%{search}%,full_name.ilike.%{search}%")
        
        result = query.order('created_at', desc=True) \
            .range(offset, offset + limit - 1) \
            .execute()
        
        return result.data, result.count or 0
    
    async def list_workspaces(
        self,
        page: int = 1,
        limit: int = 20,
        plan_filter: Optional[str] = None
    ) -> Tuple[List[Dict], int]:
        """List all workspaces with pagination."""
        offset = (page - 1) * limit
        
        query = self.supabase.table('workspaces') \
            .select('*, profiles!workspaces_owner_id_fkey(email)', count='exact')
        
        if plan_filter:
            query = query.eq('plan', plan_filter)
        
        result = query.order('created_at', desc=True) \
            .range(offset, offset + limit - 1) \
            .execute()
        
        return result.data, result.count or 0
    
    async def list_payments(
        self,
        page: int = 1,
        limit: int = 20,
        status: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None
    ) -> Tuple[List[Dict], int]:
        """List all payments with filters."""
        offset = (page - 1) * limit
        
        query = self.supabase.table('payments').select('*', count='exact')
        
        if status:
            query = query.eq('status', status)
        if from_date:
            query = query.gte('created_at', from_date)
        if to_date:
            query = query.lte('created_at', to_date)
        
        result = query.order('created_at', desc=True) \
            .range(offset, offset + limit - 1) \
            .execute()
        
        return result.data, result.count or 0
    
    async def suspend_user(self, user_id: str):
        """Suspend a user account."""
        # Update profile
        self.supabase.table('profiles').update({
            'status': 'suspended'
        }).eq('id', user_id).execute()
        
        # Revoke sessions (would need Supabase admin API)
        # For now, the user's role check will fail
    
    async def activate_user(self, user_id: str):
        """Activate a suspended user."""
        self.supabase.table('profiles').update({
            'status': 'active'
        }).eq('id', user_id).execute()
    
    async def change_plan(self, workspace_id: str, plan_id: str):
        """Admin override to change workspace plan."""
        # Update workspace
        self.supabase.table('workspaces').update({
            'plan': plan_id
        }).eq('id', workspace_id).execute()
        
        # Update subscription
        now = datetime.utcnow()
        self.supabase.table('subscriptions').update({
            'plan_id': plan_id,
            'status': 'active',
            'updated_at': now.isoformat()
        }).eq('workspace_id', workspace_id).execute()
```

## 10.4 Verification Checklist - Phase 10

- [ ] Admin dashboard loads statistics
- [ ] User listing with search works
- [ ] Workspace listing with filters works
- [ ] Payment listing with date filters works
- [ ] User suspension works
- [ ] Plan override works
- [ ] Admin-only routes protected

---

*End of Chunk 2 - Phases 6-10*
*Continue to Chunk 3 for Phases 11-15*
