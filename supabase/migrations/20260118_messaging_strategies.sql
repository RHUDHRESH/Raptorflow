-- Migration: 20260118_messaging_strategies.sql
-- Create table for comprehensive brand messaging and StoryBrand framework

CREATE TABLE IF NOT EXISTS public.messaging_strategies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    
    one_liner TEXT,
    positioning_statement JSONB DEFAULT '{}',
    brand_voice JSONB DEFAULT '{}',
    core_messages JSONB DEFAULT '{}',
    framework JSONB DEFAULT '{}',
    story_brand JSONB DEFAULT '{}',
    channel_messaging JSONB DEFAULT '{}',
    objection_responses JSONB DEFAULT '{}',
    social_proof JSONB DEFAULT '{}',
    ctas JSONB DEFAULT '{}',
    
    confidence INTEGER DEFAULT 0,
    source TEXT DEFAULT 'vertex_ai',
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(workspace_id)
);

-- Enable RLS
ALTER TABLE public.messaging_strategies ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view own messaging strategy" ON public.messaging_strategies
    FOR SELECT USING (EXISTS (
        SELECT 1 FROM workspaces WHERE workspaces.id = messaging_strategies.workspace_id AND workspaces.user_id = auth.uid()
    ));

CREATE POLICY "Users can manage own messaging strategy" ON public.messaging_strategies
    FOR ALL USING (EXISTS (
        SELECT 1 FROM workspaces WHERE workspaces.id = messaging_strategies.workspace_id AND workspaces.user_id = auth.uid()
    ));

-- Trigger for updated_at
CREATE TRIGGER messaging_strategies_updated_at
    BEFORE UPDATE ON public.messaging_strategies
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();
