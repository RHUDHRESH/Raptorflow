-- RLS policies for blackbox_strategies table
-- Migration: 20240108_blackbox_strategies_rls.sql
-- Description: Row Level Security policies for blackbox_strategies table

-- Users can view blackbox strategies in their workspace
CREATE POLICY "Users can view blackbox strategies" ON public.blackbox_strategies
    FOR SELECT USING (
        user_owns_workspace(workspace_id)
    );

-- Users can create blackbox strategies in their workspace
CREATE POLICY "Users can create blackbox strategies" ON public.blackbox_strategies
    FOR INSERT WITH CHECK (
        user_owns_workspace(workspace_id)
    );

-- Users can update blackbox strategies in their workspace
CREATE POLICY "Users can update blackbox strategies" ON public.blackbox_strategies
    FOR UPDATE USING (
        user_owns_workspace(workspace_id)
    );

-- Users can delete blackbox strategies in their workspace
CREATE POLICY "Users can delete blackbox strategies" ON public.blackbox_strategies
    FOR DELETE USING (
        user_owns_workspace(workspace_id)
    );
