-- RLS policies for moves table
-- Migration: 20240104_moves_rls.sql
-- Description: Row Level Security policies for moves table

-- Users can view moves in their workspace
CREATE POLICY "Users can view moves" ON public.moves
    FOR SELECT USING (
        user_owns_workspace(workspace_id)
    );

-- Users can create moves in their workspace
CREATE POLICY "Users can create moves" ON public.moves
    FOR INSERT WITH CHECK (
        user_owns_workspace(workspace_id)
    );

-- Users can update moves in their workspace
CREATE POLICY "Users can update moves" ON public.moves
    FOR UPDATE USING (
        user_owns_workspace(workspace_id)
    );

-- Users can delete moves in their workspace
CREATE POLICY "Users can delete moves" ON public.moves
    FOR DELETE USING (
        user_owns_workspace(workspace_id)
    );
