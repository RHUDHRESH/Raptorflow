-- RLS policies for memory_vectors table
-- Migration: 20240201_memory_vectors_rls.sql
-- Description: Row Level Security policies for memory_vectors table

-- Users can view memory vectors in their workspace
CREATE POLICY "Workspace isolation" ON public.memory_vectors
    FOR SELECT USING (
        workspace_id IN (
            SELECT id FROM workspaces
            WHERE user_id = auth.uid()
        )
    );

-- Users can create memory vectors in their workspace
CREATE POLICY "Users can create memory vectors" ON public.memory_vectors
    FOR INSERT WITH CHECK (
        workspace_id IN (
            SELECT id FROM workspaces
            WHERE user_id = auth.uid()
        )
    );

-- Users can update memory vectors in their workspace
CREATE POLICY "Users can update memory vectors" ON public.memory_vectors
    FOR UPDATE USING (
        workspace_id IN (
            SELECT id FROM workspaces
            WHERE user_id = auth.uid()
        )
    );

-- Users can delete memory vectors in their workspace
CREATE POLICY "Users can delete memory vectors" ON public.memory_vectors
    FOR DELETE USING (
        workspace_id IN (
            SELECT id FROM workspaces
            WHERE user_id = auth.uid()
        )
    );
