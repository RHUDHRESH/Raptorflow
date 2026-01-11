-- RLS policies for move_tasks table
-- Migration: 20240105_move_tasks_rls.sql
-- Description: Row Level Security policies for move_tasks table

-- Users can view move tasks in their workspace
CREATE POLICY "Users can view move tasks" ON public.move_tasks
    FOR SELECT USING (
        user_owns_workspace(workspace_id)
    );

-- Users can create move tasks in their workspace
CREATE POLICY "Users can create move tasks" ON public.move_tasks
    FOR INSERT WITH CHECK (
        user_owns_workspace(workspace_id)
    );

-- Users can update move tasks in their workspace
CREATE POLICY "Users can update move tasks" ON public.move_tasks
    FOR UPDATE USING (
        user_owns_workspace(workspace_id)
    );

-- Users can delete move tasks in their workspace
CREATE POLICY "Users can delete move tasks" ON public.move_tasks
    FOR DELETE USING (
        user_owns_workspace(workspace_id)
    );
