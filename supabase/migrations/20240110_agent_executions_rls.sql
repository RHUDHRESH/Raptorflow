-- RLS policies for agent_executions table
-- Migration: 20240110_agent_executions_rls.sql
-- Description: Row Level Security policies for agent_executions table

-- Users can view agent executions in their workspace
CREATE POLICY "Users can view agent executions" ON public.agent_executions
    FOR SELECT USING (
        user_owns_workspace(workspace_id)
    );

-- Users can create agent executions in their workspace
CREATE POLICY "Users can create agent executions" ON public.agent_executions
    FOR INSERT WITH CHECK (
        user_owns_workspace(workspace_id)
    );

-- Users can update agent executions in their workspace
CREATE POLICY "Users can update agent executions" ON public.agent_executions
    FOR UPDATE USING (
        user_owns_workspace(workspace_id)
    );

-- Users can delete agent executions in their workspace
CREATE POLICY "Users can delete agent executions" ON public.agent_executions
    FOR DELETE USING (
        user_owns_workspace(workspace_id)
    );
