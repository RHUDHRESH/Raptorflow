-- ============================================================
-- RAPTORFLOW RLS POLICIES MIGRATION
-- ============================================================
-- This script adds user-specific Row Level Security policies
-- to ensure users can only access their own data.
--
-- IMPORTANT: Run this with service_role key in Supabase SQL editor
-- or using: supabase db push
-- ============================================================

-- ============================================================
-- PROFILES: Users can only read/update their own profile
-- ============================================================

-- Drop existing if needed (for re-running)
DROP POLICY IF EXISTS "Users can view own profile" ON profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON profiles;
DROP POLICY IF EXISTS "Users can insert own profile" ON profiles;

-- Create new policies
CREATE POLICY "Users can view own profile" ON profiles
    FOR SELECT USING (
        auth.uid() = user_id
        OR auth.role() = 'service_role'
    );

CREATE POLICY "Users can update own profile" ON profiles
    FOR UPDATE USING (
        auth.uid() = user_id
        OR auth.role() = 'service_role'
    );

CREATE POLICY "Users can insert own profile" ON profiles
    FOR INSERT WITH CHECK (
        auth.uid() = user_id
        OR auth.role() = 'service_role'
    );

-- ============================================================
-- WORKSPACES: Users can access their workspaces
-- ============================================================

DROP POLICY IF EXISTS "Users can view own workspaces" ON workspaces;
DROP POLICY IF EXISTS "Users can create workspaces" ON workspaces;
DROP POLICY IF EXISTS "Users can update own workspaces" ON workspaces;
DROP POLICY IF EXISTS "Users can delete own workspaces" ON workspaces;

CREATE POLICY "Users can view own workspaces" ON workspaces
    FOR SELECT USING (
        owner_id = auth.uid()
        OR EXISTS (
            SELECT 1 FROM workspace_members 
            WHERE workspace_members.workspace_id = workspaces.id 
            AND workspace_members.user_id = auth.uid()
        )
        OR auth.role() = 'service_role'
    );

CREATE POLICY "Users can create workspaces" ON workspaces
    FOR INSERT WITH CHECK (
        auth.uid() = owner_id
        OR auth.role() = 'service_role'
    );

CREATE POLICY "Users can update own workspaces" ON workspaces
    FOR UPDATE USING (
        owner_id = auth.uid()
        OR auth.role() = 'service_role'
    );

CREATE POLICY "Users can delete own workspaces" ON workspaces
    FOR DELETE USING (
        owner_id = auth.uid()
        OR auth.role() = 'service_role'
    );

-- ============================================================
-- WORKSPACE_MEMBERS: Users can see their memberships
-- ============================================================

DROP POLICY IF EXISTS "Users can view workspace memberships" ON workspace_members;
DROP POLICY IF EXISTS "Users can join workspaces" ON workspace_members;
DROP POLICY IF EXISTS "Users can leave workspaces" ON workspace_members;

CREATE POLICY "Users can view workspace memberships" ON workspace_members
    FOR SELECT USING (
        user_id = auth.uid()
        OR auth.role() = 'service_role'
    );

CREATE POLICY "Users can join workspaces" ON workspace_members
    FOR INSERT WITH CHECK (
        user_id = auth.uid()
        OR auth.role() = 'service_role'
    );

CREATE POLICY "Users can leave workspaces" ON workspace_members
    FOR DELETE USING (
        user_id = auth.uid()
        OR auth.role() = 'service_role'
    );

-- ============================================================
-- FOUNDATIONS: User can access workspace foundations
-- ============================================================

DROP POLICY IF EXISTS "Users can view workspace foundations" ON foundations;
DROP POLICY IF EXISTS "Users can create workspace foundations" ON foundations;
DROP POLICY IF EXISTS "Users can update workspace foundations" ON foundations;
DROP POLICY IF EXISTS "Users can delete workspace foundations" ON foundations;

CREATE POLICY "Users can view workspace foundations" ON foundations
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM workspace_members wm
            JOIN workspaces w ON w.id = wm.workspace_id
            WHERE wm.user_id = auth.uid()
            AND w.id = foundations.workspace_id
        )
        OR auth.role() = 'service_role'
    );

CREATE POLICY "Users can create workspace foundations" ON foundations
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM workspace_members wm
            JOIN workspaces w ON w.id = wm.workspace_id
            WHERE wm.user_id = auth.uid()
            AND w.id = foundations.workspace_id
        )
        OR auth.role() = 'service_role'
    );

CREATE POLICY "Users can update workspace foundations" ON foundations
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM workspace_members wm
            JOIN workspaces w ON w.id = wm.workspace_id
            WHERE wm.user_id = auth.uid()
            AND w.id = foundations.workspace_id
        )
        OR auth.role() = 'service_role'
    );

CREATE POLICY "Users can delete workspace foundations" ON foundations
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM workspace_members wm
            JOIN workspaces w ON w.id = wm.workspace_id
            WHERE wm.user_id = auth.uid()
            AND w.id = foundations.workspace_id
        )
        OR auth.role() = 'service_role'
    );

-- ============================================================
-- BUSINESS_CONTEXT_MANIFESTS: Workspace BCM access
-- ============================================================

DROP POLICY IF EXISTS "Users can view workspace BCM" ON business_context_manifests;
DROP POLICY IF EXISTS "Users can create workspace BCM" ON business_context_manifests;
DROP POLICY IF EXISTS "Users can update workspace BCM" ON business_context_manifests;
DROP POLICY IF EXISTS "Users can delete workspace BCM" ON business_context_manifests;

CREATE POLICY "Users can view workspace BCM" ON business_context_manifests
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM workspace_members wm
            WHERE wm.user_id = auth.uid()
            AND wm.workspace_id = business_context_manifests.workspace_id
        )
        OR auth.role() = 'service_role'
    );

CREATE POLICY "Users can create workspace BCM" ON business_context_manifests
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM workspace_members wm
            WHERE wm.user_id = auth.uid()
            AND wm.workspace_id = business_context_manifests.workspace_id
        )
        OR auth.role() = 'service_role'
    );

CREATE POLICY "Users can update workspace BCM" ON business_context_manifests
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM workspace_members wm
            WHERE wm.user_id = auth.uid()
            AND wm.workspace_id = business_context_manifests.workspace_id
        )
        OR auth.role() = 'service_role'
    );

CREATE POLICY "Users can delete workspace BCM" ON business_context_manifests
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM workspace_members wm
            WHERE wm.user_id = auth.uid()
            AND wm.workspace_id = business_context_manifests.workspace_id
        )
        OR auth.role() = 'service_role'
    );

-- ============================================================
-- CAMPAIGNS: Workspace campaign access
-- ============================================================

DROP POLICY IF EXISTS "Users can view workspace campaigns" ON campaigns;
DROP POLICY IF EXISTS "Users can create workspace campaigns" ON campaigns;
DROP POLICY IF EXISTS "Users can update workspace campaigns" ON campaigns;
DROP POLICY IF EXISTS "Users can delete workspace campaigns" ON campaigns;

CREATE POLICY "Users can view workspace campaigns" ON campaigns
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM workspace_members wm
            WHERE wm.user_id = auth.uid()
            AND wm.workspace_id = campaigns.workspace_id
        )
        OR auth.role() = 'service_role'
    );

CREATE POLICY "Users can create workspace campaigns" ON campaigns
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM workspace_members wm
            WHERE wm.user_id = auth.uid()
            AND wm.workspace_id = campaigns.workspace_id
        )
        OR auth.role() = 'service_role'
    );

CREATE POLICY "Users can update workspace campaigns" ON campaigns
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM workspace_members wm
            WHERE wm.user_id = auth.uid()
            AND wm.workspace_id = campaigns.workspace_id
        )
        OR auth.role() = 'service_role'
    );

CREATE POLICY "Users can delete workspace campaigns" ON campaigns
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM workspace_members wm
            WHERE wm.user_id = auth.uid()
            AND wm.workspace_id = campaigns.workspace_id
        )
        OR auth.role() = 'service_role'
    );

-- ============================================================
-- MOVES: Workspace moves access
-- ============================================================

DROP POLICY IF EXISTS "Users can view workspace moves" ON moves;
DROP POLICY IF EXISTS "Users can create workspace moves" ON moves;
DROP POLICY IF EXISTS "Users can update workspace moves" ON moves;
DROP POLICY IF EXISTS "Users can delete workspace moves" ON moves;

CREATE POLICY "Users can view workspace moves" ON moves
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM workspace_members wm
            WHERE wm.user_id = auth.uid()
            AND wm.workspace_id = moves.workspace_id
        )
        OR auth.role() = 'service_role'
    );

CREATE POLICY "Users can create workspace moves" ON moves
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM workspace_members wm
            WHERE wm.user_id = auth.uid()
            AND wm.workspace_id = moves.workspace_id
        )
        OR auth.role() = 'service_role'
    );

CREATE POLICY "Users can update workspace moves" ON moves
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM workspace_members wm
            WHERE wm.user_id = auth.uid()
            AND wm.workspace_id = moves.workspace_id
        )
        OR auth.role() = 'service_role'
    );

CREATE POLICY "Users can delete workspace moves" ON moves
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM workspace_members wm
            WHERE wm.user_id = auth.uid()
            AND wm.workspace_id = moves.workspace_id
        )
        OR auth.role() = 'service_role'
    );

-- ============================================================
-- ICP_PROFILES: Workspace ICP access
-- ============================================================

DROP POLICY IF EXISTS "Users can view workspace ICP profiles" ON icp_profiles;
DROP POLICY IF EXISTS "Users can create workspace ICP profiles" ON icp_profiles;
DROP POLICY IF EXISTS "Users can update workspace ICP profiles" ON icp_profiles;
DROP POLICY IF EXISTS "Users can delete workspace ICP profiles" ON icp_profiles;

CREATE POLICY "Users can view workspace ICP profiles" ON icp_profiles
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM workspace_members wm
            WHERE wm.user_id = auth.uid()
            AND wm.workspace_id = icp_profiles.workspace_id
        )
        OR auth.role() = 'service_role'
    );

CREATE POLICY "Users can create workspace ICP profiles" ON icp_profiles
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM workspace_members wm
            WHERE wm.user_id = auth.uid()
            AND wm.workspace_id = icp_profiles.workspace_id
        )
        OR auth.role() = 'service_role'
    );

CREATE POLICY "Users can update workspace ICP profiles" ON icp_profiles
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM workspace_members wm
            WHERE wm.user_id = auth.uid()
            AND wm.workspace_id = icp_profiles.workspace_id
        )
        OR auth.role() = 'service_role'
    );

CREATE POLICY "Users can delete workspace ICP profiles" ON icp_profiles
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM workspace_members wm
            WHERE wm.user_id = auth.uid()
            AND wm.workspace_id = icp_profiles.workspace_id
        )
        OR auth.role() = 'service_role'
    );

-- ============================================================
-- ASSETS: Workspace asset access
-- ============================================================

DROP POLICY IF EXISTS "Users can view workspace assets" ON assets;
DROP POLICY IF EXISTS "Users can upload workspace assets" ON assets;
DROP POLICY IF EXISTS "Users can delete workspace assets" ON assets;

CREATE POLICY "Users can view workspace assets" ON assets
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM workspace_members wm
            WHERE wm.user_id = auth.uid()
            AND wm.workspace_id = assets.workspace_id
        )
        OR auth.role() = 'service_role'
    );

CREATE POLICY "Users can upload workspace assets" ON assets
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM workspace_members wm
            WHERE wm.user_id = auth.uid()
            AND wm.workspace_id = assets.workspace_id
        )
        OR auth.role() = 'service_role'
    );

CREATE POLICY "Users can delete workspace assets" ON assets
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM workspace_members wm
            WHERE wm.user_id = auth.uid()
            AND wm.workspace_id = assets.workspace_id
        )
        OR auth.role() = 'service_role'
    );

-- ============================================================
-- AUDIT_LOGS: Users can only see their workspace logs
-- ============================================================

DROP POLICY IF EXISTS "Users can view workspace audit logs" ON audit_logs;

CREATE POLICY "Users can view workspace audit_logs" ON audit_logs
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM workspace_members wm
            WHERE wm.user_id = auth.uid()
            AND wm.workspace_id = audit_logs.workspace_id
        )
        OR auth.role() = 'service_role'
    );

-- ============================================================
-- BCM_MEMORIES: Workspace BCM memories
-- ============================================================

DROP POLICY IF EXISTS "Users can view workspace bcm memories" ON bcm_memories;

CREATE POLICY "Users can view workspace bcm memories" ON bcm_memories
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM workspace_members wm
            WHERE wm.user_id = auth.uid()
            AND wm.workspace_id = bcm_memories.workspace_id
        )
        OR auth.role() = 'service_role'
    );

-- ============================================================
-- BCM_GENERATION_LOG: Workspace BCM generation logs
-- ============================================================

DROP POLICY IF EXISTS "Users can view workspace bcm generation logs" ON bcm_generation_log;

CREATE POLICY "Users can view workspace bcm generation logs" ON bcm_generation_log
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM workspace_members wm
            WHERE wm.user_id = auth.uid()
            AND wm.workspace_id = bcm_generation_log.workspace_id
        )
        OR auth.role() = 'service_role'
    );

-- ============================================================
-- Verify policies created
-- ============================================================

SELECT 
    schemaname,
    tablename, 
    policyname, 
    cmd 
FROM pg_policies 
WHERE schemaname = 'public'
ORDER BY tablename, policyname;
