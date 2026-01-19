-- Backend Infrastructure Hardening: Optimized RLS and Performance Indexes
-- Migration: 20260119_harden_rls_and_performance.sql

-- 1. Optimized Membership Helper Functions (SECURITY DEFINER to bypass RLS internally)
CREATE OR REPLACE FUNCTION public.check_membership(p_workspace_id UUID, p_user_id UUID DEFAULT auth.uid())
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM public.workspace_members
        WHERE workspace_id = p_workspace_id
        AND user_id = p_user_id
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION public.check_admin(p_workspace_id UUID, p_user_id UUID DEFAULT auth.uid())
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM public.workspace_members
        WHERE workspace_id = p_workspace_id
        AND user_id = p_user_id
        AND role IN ('owner', 'admin')
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 2. Standardize RLS Policies for Core Tables
-- Moves
DROP POLICY IF EXISTS "Users can view moves" ON public.moves;
CREATE POLICY "moves_select_isolation" ON public.moves
    FOR SELECT USING (check_membership(workspace_id));

DROP POLICY IF EXISTS "Users can create moves" ON public.moves;
CREATE POLICY "moves_insert_isolation" ON public.moves
    FOR INSERT WITH CHECK (check_membership(workspace_id));

DROP POLICY IF EXISTS "Users can update moves" ON public.moves;
CREATE POLICY "moves_update_isolation" ON public.moves
    FOR UPDATE USING (check_membership(workspace_id));

-- Campaigns
DROP POLICY IF EXISTS "Users can view their campaigns" ON public.campaigns;
CREATE POLICY "campaigns_select_isolation" ON public.campaigns
    FOR SELECT USING (check_membership(workspace_id));

DROP POLICY IF EXISTS "Users can manage their campaigns" ON public.campaigns;
CREATE POLICY "campaigns_all_isolation" ON public.campaigns
    FOR ALL USING (check_admin(workspace_id));

-- Business Context Manifests
DROP POLICY IF EXISTS "Users can access their workspace's manifests" ON public.business_context_manifests;
CREATE POLICY "bcm_select_isolation" ON public.business_context_manifests
    FOR SELECT USING (check_membership(workspace_id));

DROP POLICY IF EXISTS "Workspace admins can manage manifests" ON public.business_context_manifests;
CREATE POLICY "bcm_admin_isolation" ON public.business_context_manifests
    FOR ALL USING (check_admin(workspace_id));

-- 3. Performance Indexing
-- Standard B-Tree for foreign keys
CREATE INDEX IF NOT EXISTS idx_moves_workspace_perf ON public.moves(workspace_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_workspace_perf ON public.campaigns(workspace_id);
CREATE INDEX IF NOT EXISTS idx_foundations_workspace_perf ON public.foundations(workspace_id);

-- GIN Indexes for JSONB fields frequently queried
CREATE INDEX IF NOT EXISTS idx_moves_success_metrics_gin ON public.moves USING GIN (success_metrics);
CREATE INDEX IF NOT EXISTS idx_foundations_positioning_gin ON public.foundations USING GIN (positioning);
CREATE INDEX IF NOT EXISTS idx_bcm_content_gin ON public.business_context_manifests USING GIN (content);

-- 4. Transaction Integrity (Server-side Helpers)
-- Function to create a move with associated tasks in a single transaction
CREATE OR REPLACE FUNCTION public.create_move_with_tasks(
    p_move_data JSONB,
    p_tasks_data JSONB[]
) RETURNS UUID AS $$
DECLARE
    v_move_id UUID;
    v_task_data JSONB;
BEGIN
    -- Verify workspace access from data
    IF NOT check_membership((p_move_data->>'workspace_id')::UUID) THEN
        RAISE EXCEPTION 'Unauthorized workspace access';
    END IF;

    -- Insert Move
    INSERT INTO public.moves (
        workspace_id, title, description, category, objective, status
    ) VALUES (
        (p_move_data->>'workspace_id')::UUID,
        p_move_data->>'title',
        p_move_data->>'description',
        p_move_data->>'category',
        p_move_data->>'objective',
        COALESCE(p_move_data->>'status', 'draft')
    ) RETURNING id INTO v_move_id;

    -- Insert Tasks
    FOREACH v_task_data IN ARRAY p_tasks_data LOOP
        INSERT INTO public.move_tasks (
            move_id, workspace_id, title, description, status
        ) VALUES (
            v_move_id,
            (p_move_data->>'workspace_id')::UUID,
            v_task_data->>'title',
            v_task_data->>'description',
            COALESCE(v_task_data->>'status', 'pending')
        );
    END LOOP;

    RETURN v_move_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant permissions
GRANT EXECUTE ON FUNCTION public.check_membership TO authenticated;
GRANT EXECUTE ON FUNCTION public.check_admin TO authenticated;
GRANT EXECUTE ON FUNCTION public.create_move_with_tasks TO authenticated;
