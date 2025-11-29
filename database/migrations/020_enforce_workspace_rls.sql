-- Migration 020: Enforce Core RLS Policies for Multi-Tenancy
-- This "locks the kernel" as per Phase 2.1 plan.

-- 1. Profiles (User Identity)
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own profile" ON public.profiles;
CREATE POLICY "Users can view own profile"
    ON public.profiles FOR SELECT
    USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users can update own profile" ON public.profiles;
CREATE POLICY "Users can update own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = id);

-- 2. Workspaces
ALTER TABLE public.workspaces ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Members can view workspaces" ON public.workspaces;
CREATE POLICY "Members can view workspaces"
    ON public.workspaces FOR SELECT
    USING (
        exists (
            select 1 from public.workspace_members wm
            where wm.workspace_id = workspaces.id
            and wm.user_id = auth.uid()
        )
    );

DROP POLICY IF EXISTS "Owners can update workspace" ON public.workspaces;
CREATE POLICY "Owners can update workspace"
    ON public.workspaces FOR UPDATE
    USING (owner_id = auth.uid());

DROP POLICY IF EXISTS "Users can create workspaces" ON public.workspaces;
CREATE POLICY "Users can create workspaces"
    ON public.workspaces FOR INSERT
    WITH CHECK (owner_id = auth.uid());

-- 3. Workspace Members
ALTER TABLE public.workspace_members ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Members can view workspace members" ON public.workspace_members;
CREATE POLICY "Members can view workspace members"
    ON public.workspace_members FOR SELECT
    USING (
        user_id = auth.uid() OR
        exists (
            select 1 from public.workspace_members wm
            where wm.workspace_id = workspace_members.workspace_id
            and wm.user_id = auth.uid()
        )
    );

DROP POLICY IF EXISTS "Owners can manage members" ON public.workspace_members;
CREATE POLICY "Owners can manage members"
    ON public.workspace_members FOR ALL
    USING (
        exists (
            select 1 from public.workspaces w
            where w.id = workspace_members.workspace_id
            and w.owner_id = auth.uid()
        )
    );

-- 4. Agents & System Tables (Member Access)
-- Standard pattern: Access allowed if user is a member of the referenced workspace

ALTER TABLE public.agents ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Workspace members can view agents" ON public.agents;
CREATE POLICY "Workspace members can view agents"
    ON public.agents FOR SELECT
    USING (
        exists (
            select 1 from public.workspace_members wm
            where wm.workspace_id = agents.workspace_id
            and wm.user_id = auth.uid()
        )
    );

ALTER TABLE public.agent_runs ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Workspace members can view runs" ON public.agent_runs;
CREATE POLICY "Workspace members can view runs"
    ON public.agent_runs FOR SELECT
    USING (
        exists (
            select 1 from public.workspace_members wm
            where wm.workspace_id = agent_runs.workspace_id
            and wm.user_id = auth.uid()
        )
    );

ALTER TABLE public.cost_logs ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Workspace members can view costs" ON public.cost_logs;
CREATE POLICY "Workspace members can view costs"
    ON public.cost_logs FOR SELECT
    USING (
        exists (
            select 1 from public.workspace_members wm
            where wm.workspace_id = cost_logs.workspace_id
            and wm.user_id = auth.uid()
        )
    );
