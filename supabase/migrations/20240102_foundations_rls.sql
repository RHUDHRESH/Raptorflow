-- RLS policies for foundations table
-- Migration: 20240102_foundations_rls.sql

-- Helper function to check workspace ownership
CREATE OR REPLACE FUNCTION user_owns_workspace(workspace_uuid UUID)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM workspaces
        WHERE id = workspace_uuid AND user_id = auth.uid()
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Apply RLS policies to foundations
CREATE POLICY "Users can view own foundation" ON public.foundations
    FOR SELECT USING (user_owns_workspace(workspace_id));

CREATE POLICY "Users can create own foundation" ON public.foundations
    FOR INSERT WITH CHECK (user_owns_workspace(workspace_id));

CREATE POLICY "Users can update own foundation" ON public.foundations
    FOR UPDATE USING (user_owns_workspace(workspace_id));

CREATE POLICY "Users can delete own foundation" ON public.foundations
    FOR DELETE USING (user_owns_workspace(workspace_id));
