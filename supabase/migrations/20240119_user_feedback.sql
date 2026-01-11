-- User feedback table
-- Migration: 20240119_user_feedback.sql

CREATE TABLE IF NOT EXISTS public.user_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    output_type TEXT,
    output_id UUID,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comments TEXT,
    corrections TEXT,
    applied BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_feedback_workspace_id ON public.user_feedback(workspace_id);
CREATE INDEX IF NOT EXISTS idx_user_feedback_user_id ON public.user_feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_user_feedback_output_type ON public.user_feedback(output_type);
CREATE INDEX IF NOT EXISTS idx_user_feedback_rating ON public.user_feedback(rating);
CREATE INDEX IF NOT EXISTS idx_user_feedback_applied ON public.user_feedback(applied);
CREATE INDEX IF NOT EXISTS idx_user_feedback_created_at ON public.user_feedback(created_at);

-- Enable RLS
ALTER TABLE public.user_feedback ENABLE ROW LEVEL SECURITY;

-- RLS policies
CREATE POLICY "Users can view own feedback" ON public.user_feedback
    FOR SELECT USING (
        workspace_id IN (
            SELECT id FROM public.workspaces
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can create own feedback" ON public.user_feedback
    FOR INSERT WITH CHECK (
        workspace_id IN (
            SELECT id FROM public.workspaces
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update own feedback" ON public.user_feedback
    FOR UPDATE USING (
        workspace_id IN (
            SELECT id FROM public.workspaces
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete own feedback" ON public.user_feedback
    FOR DELETE USING (
        workspace_id IN (
            SELECT id FROM public.workspaces
            WHERE user_id = auth.uid()
        )
    );
