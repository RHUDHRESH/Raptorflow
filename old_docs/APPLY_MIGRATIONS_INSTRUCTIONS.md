# Manual Database Migration Instructions

Since automatic migration application requires a database password which is not available in the environment, please follow these steps to apply the migrations manually.

## 1. Get Your Database Password
Retrieve your Supabase database password. You will need this to update the `.env` file or to connect via a SQL client.

## 2. Update Environment Variables
Open `backend/.env` and update the `DATABASE_URL` with your actual password:
```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.vpwwzsanuyhpkvgorcnc.supabase.co:5432/postgres
```

## 3. Apply Migrations
You can apply the migrations using the Supabase Dashboard (SQL Editor) or a local SQL client.

### Critical Migration: Onboarding Requests
This migration creates the `onboarding_requests` table required for the new feature.

**File:** `database/migrations/027_create_onboarding_requests.sql`

**SQL Content:**
```sql
-- ============================================
-- MIGRATION 027: Create Onboarding Requests Table
-- Purpose: Track onboarding requests manually
-- ============================================

CREATE TABLE IF NOT EXISTS public.onboarding_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    workspace_id UUID REFERENCES public.workspaces(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL DEFAULT 'pending', -- pending, approved, rejected
    reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    handled_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    handled_at TIMESTAMP WITH TIME ZONE
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_onboarding_requests_user_id ON public.onboarding_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_onboarding_requests_workspace_id ON public.onboarding_requests(workspace_id);
CREATE INDEX IF NOT EXISTS idx_onboarding_requests_status ON public.onboarding_requests(status);

-- RLS
ALTER TABLE public.onboarding_requests ENABLE ROW LEVEL SECURITY;

-- Policies
DROP POLICY IF EXISTS "Users can view own onboarding requests" ON public.onboarding_requests;
CREATE POLICY "Users can view own onboarding requests"
    ON public.onboarding_requests FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can create onboarding requests" ON public.onboarding_requests;
CREATE POLICY "Users can create onboarding requests"
    ON public.onboarding_requests FOR INSERT
    WITH CHECK (auth.uid() = user_id);
```

### Other Migrations
Please ensure all other migrations in `database/migrations/` are applied if they haven't been already.
