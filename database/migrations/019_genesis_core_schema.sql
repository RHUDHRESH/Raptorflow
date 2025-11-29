-- ============================================
-- RAPTORFLOW GENESIS CORE SCHEMA MIGRATION
-- Date: 2025-11-28
-- Description: Canonical Phase 1 Genesis schema freeze
-- ============================================

-- This migration establishes the canonical core ("kernel") tables
-- These are the OS kernel for RaptorFlow - do not conceptually duplicate them
-- All business data must link back to workspaces.workspace_id

-- ============================================
-- 1. CORE DATA TYPES
-- ============================================

-- Workspace role enum
CREATE TYPE IF NOT EXISTS workspace_role AS ENUM ('owner', 'admin', 'member', 'viewer');

-- ============================================
-- 2. NORMALIZE EXISTING CORE TABLES
-- ============================================

-- 2.1 Profiles table (ensure it exists with correct structure)
-- If it exists as user_profiles, we add columns but don't drop
-- Standardize on: profiles (not user_profiles) going forward
CREATE TABLE IF NOT EXISTS profiles (
  id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  full_name text,
  avatar_url text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

-- Add missing columns to profiles if they exist as user_profiles or profiles
DO $$
BEGIN
  -- If user_profiles exists, ensure it has required columns
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'user_profiles' AND table_schema = 'public') THEN
    ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS updated_at timestamptz DEFAULT now();
  END IF;
END $$;

-- 2.2 Workspaces table (ensure owner_id exists)
-- Add owner_id if missing (it might not exist in older migrations)
ALTER TABLE workspaces ADD COLUMN IF NOT EXISTS owner_id uuid REFERENCES auth.users(id) ON DELETE CASCADE;
ALTER TABLE workspaces ADD COLUMN IF NOT EXISTS plan text NOT NULL DEFAULT 'free';
ALTER TABLE workspaces ADD COLUMN IF NOT EXISTS is_active boolean NOT NULL DEFAULT true;
ALTER TABLE workspaces ADD COLUMN IF NOT EXISTS updated_at timestamptz NOT NULL DEFAULT now();

-- 2.3 Workspace members table
-- Normalize from user_workspaces to workspace_members if user_workspaces exists
-- Otherwise create workspace_members
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'user_workspaces' AND table_schema = 'public')
  AND NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'workspace_members' AND table_schema = 'public') THEN
    -- Rename user_workspaces to workspace_members
    ALTER TABLE user_workspaces RENAME TO workspace_members;
    ALTER TABLE workspace_members RENAME COLUMN user_id TO user_id;
    ALTER TABLE workspace_members RENAME COLUMN workspace_id TO workspace_id;
    -- Convert role from string to our enum if needed
  END IF;
END $$;

-- Create workspace_members if it doesn't exist
CREATE TABLE IF NOT EXISTS workspace_members (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  role workspace_role NOT NULL DEFAULT 'member',
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (workspace_id, user_id)
);

-- Add missing columns if table existed in different form
ALTER TABLE workspace_members ADD COLUMN IF NOT EXISTS created_at timestamptz NOT NULL DEFAULT now();
-- Ensure unique constraint
ALTER TABLE workspace_members DROP CONSTRAINT IF EXISTS unique_workspace_user;
ALTER TABLE workspace_members ADD CONSTRAINT unique_workspace_user UNIQUE (workspace_id, user_id);

-- 2.4 Workspace invites table
CREATE TABLE IF NOT EXISTS workspace_invites (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  email text NOT NULL,
  role workspace_role NOT NULL DEFAULT 'member',
  status text NOT NULL DEFAULT 'pending',
  created_at timestamptz NOT NULL DEFAULT now()
);

-- Add token, accepted, expires_at if they exist in other databases (for compatibility)
ALTER TABLE workspace_invites ADD COLUMN IF NOT EXISTS token text;
ALTER TABLE workspace_invites ADD COLUMN IF NOT EXISTS accepted boolean DEFAULT false;
ALTER TABLE workspace_invites ADD COLUMN IF NOT EXISTS expires_at timestamptz;

-- ============================================
-- 3. CREATE MISSING CORE INFRA TABLES
-- ============================================

-- 3.1 Agents table
CREATE TABLE IF NOT EXISTS agents (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  name text NOT NULL,
  slug text NOT NULL UNIQUE,
  guild text NOT NULL,
  kind text NOT NULL,
  config jsonb NOT NULL DEFAULT '{}'::jsonb,
  status text NOT NULL DEFAULT 'active',
  created_at timestamptz NOT NULL DEFAULT now()
);

-- 3.2 Agent runs table
CREATE TABLE IF NOT EXISTS agent_runs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  agent_id uuid REFERENCES agents(id) ON DELETE SET NULL,
  input_summary text,
  result_summary text,
  status text NOT NULL DEFAULT 'pending',
  error_message text,
  started_at timestamptz NOT NULL DEFAULT now(),
  completed_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now()
);

-- 3.3 Cost logs table (standardize on cost_logs, not llm_calls)
-- If llm_calls exists, ensure it has required columns
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'llm_calls' AND table_schema = 'public')
  AND NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'cost_logs' AND table_schema = 'public') THEN
    ALTER TABLE llm_calls RENAME TO cost_logs;
  END IF;
END $$;

-- Ensure cost_logs has all required columns
CREATE TABLE IF NOT EXISTS cost_logs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  agent_id uuid REFERENCES agents(id),
  agent_run_id uuid REFERENCES agent_runs(id),
  model text NOT NULL,
  prompt_tokens integer NOT NULL DEFAULT 0,
  completion_tokens integer NOT NULL DEFAULT 0,
  total_tokens integer NOT NULL DEFAULT 0,
  estimated_cost_usd numeric(12, 6) NOT NULL DEFAULT 0,
  created_at timestamptz NOT NULL DEFAULT now()
);

-- Add missing columns to cost_logs if it existed with fewer columns
ALTER TABLE cost_logs ADD COLUMN IF NOT EXISTS agent_id uuid REFERENCES agents(id);
ALTER TABLE cost_logs ADD COLUMN IF NOT EXISTS agent_run_id uuid REFERENCES agent_runs(id);
ALTER TABLE cost_logs ADD COLUMN IF NOT EXISTS prompt_tokens integer NOT NULL DEFAULT 0;
ALTER TABLE cost_logs ADD COLUMN IF NOT EXISTS completion_tokens integer NOT NULL DEFAULT 0;
ALTER TABLE cost_logs ADD COLUMN IF NOT EXISTS total_tokens integer NOT NULL DEFAULT 0;

-- 3.4 Audit logs table
CREATE TABLE IF NOT EXISTS audit_logs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  actor_user_id uuid REFERENCES auth.users(id),
  event_type text NOT NULL,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
);

-- ============================================
-- 4. ENABLE ROW LEVEL SECURITY ON ALL TABLES
-- ============================================

ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE workspaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE workspace_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE workspace_invites ENABLE ROW LEVEL SECURITY;
ALTER TABLE agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE cost_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- ============================================
-- 5. ROW LEVEL SECURITY POLICIES
-- ============================================

-- 5.1 Profiles RLS policies (self-access only)
DROP POLICY IF EXISTS "Users can view own profile" ON profiles;
CREATE POLICY "Users can view own profile"
ON profiles FOR SELECT
USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users can update own profile" ON profiles;
CREATE POLICY "Users can update own profile"
ON profiles FOR UPDATE
USING (auth.uid() = id)
WITH CHECK (auth.uid() = id);

DROP POLICY IF EXISTS "Users can insert own profile" ON profiles;
CREATE POLICY "Users can insert own profile"
ON profiles FOR INSERT
WITH CHECK (auth.uid() = id);

-- 5.2 Workspaces RLS policies
DROP POLICY IF EXISTS "Members can view workspaces they belong to" ON workspaces;
CREATE POLICY "Members can view workspaces they belong to"
ON workspaces FOR SELECT
USING (
  exists (
    select 1 from workspace_members wm
    where wm.workspace_id = workspaces.id
      and wm.user_id = auth.uid()
  )
);

DROP POLICY IF EXISTS "Users can create workspaces" ON workspaces;
CREATE POLICY "Users can create workspaces"
ON workspaces FOR INSERT
WITH CHECK (owner_id = auth.uid());

DROP POLICY IF EXISTS "Owners can update workspace" ON workspaces;
CREATE POLICY "Owners can update workspace"
ON workspaces FOR UPDATE
USING (owner_id = auth.uid())
WITH CHECK (owner_id = auth.uid());

DROP POLICY IF EXISTS "Owners can delete workspace" ON workspaces;
CREATE POLICY "Owners can delete workspace"
ON workspaces FOR DELETE
USING (owner_id = auth.uid());

-- 5.3 Workspace_members RLS policies
DROP POLICY IF EXISTS "Users can view membership rows for their workspaces" ON workspace_members;
CREATE POLICY "Users can view membership rows for their workspaces"
ON workspace_members FOR SELECT
USING (
  user_id = auth.uid()
  or exists (
    select 1 from workspace_members wm2
    where wm2.workspace_id = workspace_members.workspace_id
      and wm2.user_id = auth.uid()
  )
);

DROP POLICY IF EXISTS "Owners can add members" ON workspace_members;
CREATE POLICY "Owners can add members"
ON workspace_members FOR INSERT
WITH CHECK (
  exists (
    select 1 from workspaces w
    where w.id = workspace_members.workspace_id
      and w.owner_id = auth.uid()
  )
);

DROP POLICY IF EXISTS "Owners can update member roles" ON workspace_members;
CREATE POLICY "Owners can update member roles"
ON workspace_members FOR UPDATE
USING (
  exists (
    select 1 from workspaces w
    where w.id = workspace_members.workspace_id
      and w.owner_id = auth.uid()
  )
)
WITH CHECK (
  exists (
    select 1 from workspaces w
    where w.id = workspace_members.workspace_id
      and w.owner_id = auth.uid()
  )
);

DROP POLICY IF EXISTS "Owners can remove members" ON workspace_members;
CREATE POLICY "Owners can remove members"
ON workspace_members FOR DELETE
USING (
  exists (
    select 1 from workspaces w
    where w.id = workspace_members.workspace_id
      and w.owner_id = auth.uid()
  )
);

-- 5.4 Workspace_invites RLS policies
DROP POLICY IF EXISTS "Members can view workspace invites" ON workspace_invites;
CREATE POLICY "Members can view workspace invites"
ON workspace_invites FOR SELECT
USING (
  exists (
    select 1 from workspace_members wm
    where wm.workspace_id = workspace_invites.workspace_id
      and wm.user_id = auth.uid()
  )
);

DROP POLICY IF EXISTS "Owners can create invites" ON workspace_invites;
CREATE POLICY "Owners can create invites"
ON workspace_invites FOR INSERT
WITH CHECK (
  exists (
    select 1 from workspaces w
    where w.id = workspace_invites.workspace_id
      and w.owner_id = auth.uid()
  )
);

DROP POLICY IF EXISTS "Owners can delete invites" ON workspace_invites;
CREATE POLICY "Owners can delete invites"
ON workspace_invites FOR DELETE
USING (
  exists (
    select 1 from workspaces w
    where w.id = workspace_invites.workspace_id
      and w.owner_id = auth.uid()
  )
);

-- 5.5 Workspace-scoped tables RLS policies (agents, agent_runs, cost_logs, audit_logs)
-- Use the standard membership check pattern

DROP POLICY IF EXISTS "Members can view agents in workspace" ON agents;
CREATE POLICY "Members can view agents in workspace"
ON agents FOR SELECT
USING (
  exists (
    select 1 from workspace_members wm
    where wm.workspace_id = agents.workspace_id
      and wm.user_id = auth.uid()
  )
);

DROP POLICY IF EXISTS "Members can manage agents in workspace" ON agents;
CREATE POLICY "Members can manage agents in workspace"
ON agents FOR ALL
USING (
  exists (
    select 1 from workspace_members wm
    where wm.workspace_id = agents.workspace_id
      and wm.user_id = auth.uid()
  )
)
WITH CHECK (
  exists (
    select 1 from workspace_members wm
    where wm.workspace_id = agents.workspace_id
      and wm.user_id = auth.uid()
  )
);

DROP POLICY IF EXISTS "Members can view agent runs in workspace" ON agent_runs;
CREATE POLICY "Members can view agent runs in workspace"
ON agent_runs FOR SELECT
USING (
  exists (
    select 1 from workspace_members wm
    where wm.workspace_id = agent_runs.workspace_id
      and wm.user_id = auth.uid()
  )
);

DROP POLICY IF EXISTS "Members can manage agent runs in workspace" ON agent_runs;
CREATE POLICY "Members can manage agent runs in workspace"
ON agent_runs FOR ALL
USING (
  exists (
    select 1 from workspace_members wm
    where wm.workspace_id = agent_runs.workspace_id
      and wm.user_id = auth.uid()
  )
)
WITH CHECK (
  exists (
    select 1 from workspace_members wm
    where wm.workspace_id = agent_runs.workspace_id
      and wm.user_id = auth.uid()
  )
);

DROP POLICY IF EXISTS "Members can view cost logs in workspace" ON cost_logs;
CREATE POLICY "Members can view cost logs in workspace"
ON cost_logs FOR SELECT
USING (
  exists (
    select 1 from workspace_members wm
    where wm.workspace_id = cost_logs.workspace_id
      and wm.user_id = auth.uid()
  )
);

DROP POLICY IF EXISTS "Members can insert cost logs in workspace" ON cost_logs;
CREATE POLICY "Members can insert cost logs in workspace"
ON cost_logs FOR INSERT
WITH CHECK (
  exists (
    select 1 from workspace_members wm
    where wm.workspace_id = cost_logs.workspace_id
      and wm.user_id = auth.uid()
  )
);

DROP POLICY IF EXISTS "Members can view audit logs in workspace" ON audit_logs;
CREATE POLICY "Members can view audit logs in workspace"
ON audit_logs FOR SELECT
USING (
  exists (
    select 1 from workspace_members wm
    where wm.workspace_id = audit_logs.workspace_id
      and wm.user_id = auth.uid()
  )
);

DROP POLICY IF EXISTS "Members can insert audit logs in workspace" ON audit_logs;
CREATE POLICY "Members can insert audit logs in workspace"
ON audit_logs FOR INSERT
WITH CHECK (
  exists (
    select 1 from workspace_members wm
    where wm.workspace_id = audit_logs.workspace_id
      and wm.user_id = auth.uid()
  )
);

-- ============================================
-- 6. INDEXES FOR PERFORMANCE
-- ============================================

-- Profiles indexes
CREATE INDEX IF NOT EXISTS idx_profiles_id ON profiles(id);

-- Workspaces indexes
CREATE INDEX IF NOT EXISTS idx_workspaces_owner_id ON workspaces(owner_id);
CREATE INDEX IF NOT EXISTS idx_workspaces_slug ON workspaces(slug);

-- Workspace members indexes
CREATE INDEX IF NOT EXISTS idx_workspace_members_workspace_id ON workspace_members(workspace_id);
CREATE INDEX IF NOT EXISTS idx_workspace_members_user_id ON workspace_members(user_id);

-- Workspace invites indexes
CREATE INDEX IF NOT EXISTS idx_workspace_invites_workspace_id ON workspace_invites(workspace_id);
CREATE INDEX IF NOT EXISTS idx_workspace_invites_email ON workspace_invites(email);

-- Agents indexes
CREATE INDEX IF NOT EXISTS idx_agents_workspace_id ON agents(workspace_id);
CREATE INDEX IF NOT EXISTS idx_agents_slug ON agents(slug);
CREATE INDEX IF NOT EXISTS idx_agents_guild ON agents(guild);

-- Agent runs indexes
CREATE INDEX IF NOT EXISTS idx_agent_runs_workspace_id ON agent_runs(workspace_id);
CREATE INDEX IF NOT EXISTS idx_agent_runs_agent_id ON agent_runs(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_runs_status ON agent_runs(status);
CREATE INDEX IF NOT EXISTS idx_agent_runs_started_at ON agent_runs(started_at);

-- Cost logs indexes
CREATE INDEX IF NOT EXISTS idx_cost_logs_workspace_id ON cost_logs(workspace_id);
CREATE INDEX IF NOT EXISTS idx_cost_logs_agent_id ON cost_logs(agent_id);
CREATE INDEX IF NOT EXISTS idx_cost_logs_agent_run_id ON cost_logs(agent_run_id);
CREATE INDEX IF NOT EXISTS idx_cost_logs_created_at ON cost_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_cost_logs_model ON cost_logs(model);

-- Audit logs indexes
CREATE INDEX IF NOT EXISTS idx_audit_logs_workspace_id ON audit_logs(workspace_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_actor_user_id ON audit_logs(actor_user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_event_type ON audit_logs(event_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);

-- ============================================
-- 7. TRIGGERS FOR UPDATED_AT
-- ============================================

-- Function to update updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers to tables with updated_at
CREATE TRIGGER update_profiles_updated_at
  BEFORE UPDATE ON profiles
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workspaces_updated_at
  BEFORE UPDATE ON workspaces
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- MIGRATION COMPLETE
-- ============================================

-- PHASE 1 GENESIS CORE SCHEMA IS NOW READY
-- These 8 tables are the RaptorFlow OS kernel.
-- DO NOT conceptually duplicate them.
-- All future business tables must reference workspace_id and use the standard RLS pattern.
