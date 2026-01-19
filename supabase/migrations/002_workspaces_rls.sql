-- supabase/migrations/002_workspaces_rls.sql
-- Create workspaces table with Row-Level Security

-- Drop existing if exists (for clean migration)
DROP TABLE IF EXISTS public.workspace_members CASCADE;
DROP TABLE IF EXISTS public.workspaces CASCADE;
DROP FUNCTION IF EXISTS public.is_workspace_member(UUID) CASCADE;
DROP FUNCTION IF EXISTS public.is_workspace_admin(UUID) CASCADE;
DROP FUNCTION IF EXISTS public.get_user_workspace() CASCADE;
DROP FUNCTION IF EXISTS public.is_admin() CASCADE;

-- Create workspaces table
CREATE TABLE IF NOT EXISTS public.workspaces (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  slug TEXT UNIQUE NOT NULL,
  owner_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  settings JSONB DEFAULT '{}',
  plan TEXT NOT NULL DEFAULT 'free' CHECK (plan IN ('free', 'ascent', 'glide', 'soar')),
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

-- Create indexes for performance
CREATE INDEX idx_workspaces_owner ON public.workspaces(owner_id);
CREATE INDEX idx_workspaces_plan ON public.workspaces(plan);
CREATE INDEX idx_workspaces_slug ON public.workspaces(slug);

CREATE INDEX idx_workspace_members_workspace ON public.workspace_members(workspace_id);
CREATE INDEX idx_workspace_members_user ON public.workspace_members(user_id);
CREATE INDEX idx_workspace_members_role ON public.workspace_members(role);

-- Enable RLS
ALTER TABLE public.workspaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workspace_members ENABLE ROW LEVEL SECURITY;

-- Workspace RLS Policies
-- Users can view workspaces they are members of
CREATE POLICY "workspaces_select_member" ON public.workspaces
  FOR SELECT
  USING (
    id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid()
    )
  );

-- Users can create workspaces (they become owner)
CREATE POLICY "workspaces_insert_authenticated" ON public.workspaces
  FOR INSERT
  WITH CHECK (auth.uid() = owner_id);

-- Workspace admins and owners can update
CREATE POLICY "workspaces_update_admin" ON public.workspaces
  FOR UPDATE
  USING (
    id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
    )
  );

-- Only owners can delete workspaces
CREATE POLICY "workspaces_delete_owner" ON public.workspaces
  FOR DELETE
  USING (owner_id = auth.uid());

-- Workspace members RLS Policies
-- Users can view memberships for their workspaces
CREATE POLICY "workspace_members_select" ON public.workspace_members
  FOR SELECT
  USING (
    workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid()
    )
  );

-- Workspace admins can add members
CREATE POLICY "workspace_members_insert_admin" ON public.workspace_members
  FOR INSERT
  WITH CHECK (
    workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
    )
  );

-- Workspace admins can update member roles
CREATE POLICY "workspace_members_update_admin" ON public.workspace_members
  FOR UPDATE
  USING (
    workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
    )
  );

-- Workspace admins can remove members (and users can remove themselves)
CREATE POLICY "workspace_members_delete_admin" ON public.workspace_members
  FOR DELETE
  USING (
    workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
    )
    OR user_id = auth.uid() -- Users can remove themselves
  );

-- Updated_at trigger for workspaces
CREATE OR REPLACE FUNCTION public.update_workspace_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER workspaces_updated_at
  BEFORE UPDATE ON public.workspaces
  FOR EACH ROW EXECUTE FUNCTION public.update_workspace_updated_at();
