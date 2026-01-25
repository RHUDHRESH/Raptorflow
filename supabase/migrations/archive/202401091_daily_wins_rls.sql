-- RLS policies for daily_wins table
-- Migration: 20240109_daily_wins_rls.sql
-- Description: Row Level Security policies for daily_wins table

-- Users can view daily wins in their workspace
CREATE POLICY "Users can view daily wins" ON public.daily_wins
    FOR SELECT USING (
        user_owns_workspace(workspace_id)
    );

-- Users can create daily wins in their workspace
CREATE POLICY "Users can create daily wins" ON public.daily_wins
    FOR INSERT WITH CHECK (
        user_owns_workspace(workspace_id)
    );

-- Users can update daily wins in their workspace
CREATE POLICY "Users can update daily wins" ON public.daily_wins
    FOR UPDATE USING (
        user_owns_workspace(workspace_id)
    );

-- Users can delete daily wins in their workspace
CREATE POLICY "Users can delete daily wins" ON public.daily_wins
    FOR DELETE USING (
        user_owns_workspace(workspace_id)
    );
