-- Absolute Infinity Strategic Engine Consolidation
-- Migration: 20260119_absolute_infinity_consolidation.sql
-- Description: Unified schema for strategic orchestration, including relational arcs and job queue.

-- 1. Campaign Arcs (The Relational Graph)
CREATE TABLE IF NOT EXISTS public.campaign_arcs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES public.workspaces(id) ON DELETE CASCADE,
    campaign_id UUID NOT NULL REFERENCES public.campaigns(id) ON DELETE CASCADE,

    -- Strategic Graph Structure
    name TEXT NOT NULL,
    description TEXT,
    nodes JSONB DEFAULT '[]', -- Nodes in the strategic arc (moves, milestones)
    edges JSONB DEFAULT '[]', -- Relationships between nodes (dependencies)

    -- State Management
    status TEXT DEFAULT 'draft', -- draft, active, completed, archived
    current_pulse JSONB DEFAULT '{}', -- Current real-time intelligence state

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- 2. Move Instances (The Unified Move Table)
-- We extend the existing moves table with relational and state machine capabilities
ALTER TABLE public.moves ADD COLUMN IF NOT EXISTS parent_move_id UUID REFERENCES public.moves(id) ON DELETE SET NULL;
ALTER TABLE public.moves ADD COLUMN IF NOT EXISTS arc_id UUID REFERENCES public.campaign_arcs(id) ON DELETE SET NULL;
ALTER TABLE public.moves ADD COLUMN IF NOT EXISTS relation_type TEXT; -- concurrent, subsequent
ALTER TABLE public.moves ADD COLUMN IF NOT EXISTS strategic_index INTEGER DEFAULT 0;
ALTER TABLE public.moves ADD COLUMN IF NOT EXISTS reasoning_trace JSONB DEFAULT '[]'; -- Full expert thought logs
ALTER TABLE public.moves ADD COLUMN IF NOT EXISTS intelligence_map JSONB DEFAULT '{}'; -- Titan research data

-- 3. Scheduled Tasks (Global Job Queue)
CREATE TABLE IF NOT EXISTS public.scheduled_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES public.workspaces(id) ON DELETE CASCADE,
    move_id UUID REFERENCES public.moves(id) ON DELETE CASCADE,
    campaign_id UUID REFERENCES public.campaigns(id) ON DELETE CASCADE,

    -- Task Details
    task_type TEXT NOT NULL, -- move_execution, research, content_gen, health_check
    payload JSONB DEFAULT '{}',

    -- Scheduling
    scheduled_for TIMESTAMPTZ NOT NULL,
    priority INTEGER DEFAULT 3,
    status TEXT DEFAULT 'pending', -- pending, processing, completed, failed, pushed_back

    -- Execution Tracking
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    last_error TEXT,
    executed_at TIMESTAMPTZ,
    execution_duration_ms INTEGER,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Agent Reasoning Logs (Dedicated Deep Storage)
CREATE TABLE IF NOT EXISTS public.agent_thought_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES public.workspaces(id) ON DELETE CASCADE,
    entity_id UUID NOT NULL, -- UUID of move or campaign
    entity_type TEXT NOT NULL, -- 'move' or 'campaign'

    agent_name TEXT NOT NULL,
    thought_process TEXT,
    inputs JSONB DEFAULT '{}',
    outputs JSONB DEFAULT '{}',

    -- Telemetry
    tokens_used INTEGER DEFAULT 0,
    latency_ms INTEGER DEFAULT 0,
    model_tier TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. LangGraph Checkpoints (Industrial state persistence)
CREATE TABLE IF NOT EXISTS public.agent_checkpoints (
    thread_id TEXT NOT NULL,
    checkpoint_ns TEXT NOT NULL DEFAULT '',
    workspace_id UUID NOT NULL REFERENCES public.workspaces(id) ON DELETE CASCADE,
    checkpoint JSONB NOT NULL,
    metadata JSONB DEFAULT '{}',
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (thread_id, checkpoint_ns)
);

-- 6. RLS Policies
ALTER TABLE public.campaign_arcs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.scheduled_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.agent_thought_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.agent_checkpoints ENABLE ROW LEVEL SECURITY;

-- Campaign Arcs Policies
CREATE POLICY "Users can view their own workspace campaign arcs"
    ON public.campaign_arcs FOR SELECT
    USING (workspace_id IN (SELECT workspace_id FROM public.users_workspaces WHERE user_id = auth.uid()));

CREATE POLICY "Users can manage their own workspace campaign arcs"
    ON public.campaign_arcs FOR ALL
    USING (workspace_id IN (SELECT workspace_id FROM public.users_workspaces WHERE user_id = auth.uid()));

-- Scheduled Tasks Policies (Internal usually, but for visibility)
CREATE POLICY "Users can view their own workspace scheduled tasks"
    ON public.scheduled_tasks FOR SELECT
    USING (workspace_id IN (SELECT workspace_id FROM public.users_workspaces WHERE user_id = auth.uid()));

-- Agent Thought Logs Policies
CREATE POLICY "Users can view their own workspace agent thought logs"
    ON public.agent_thought_logs FOR SELECT
    USING (workspace_id IN (SELECT workspace_id FROM public.users_workspaces WHERE user_id = auth.uid()));

-- Agent Checkpoints Policies
CREATE POLICY "Users can manage their own workspace checkpoints"
    ON public.agent_checkpoints FOR ALL
    USING (workspace_id IN (SELECT workspace_id FROM public.users_workspaces WHERE user_id = auth.uid()));

-- 7. Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_campaign_arcs_workspace_id ON public.campaign_arcs(workspace_id);
CREATE INDEX IF NOT EXISTS idx_scheduled_tasks_scheduled_for ON public.scheduled_tasks(scheduled_for) WHERE status = 'pending';
CREATE INDEX IF NOT EXISTS idx_agent_thought_logs_entity_id ON public.agent_thought_logs(entity_id);
CREATE INDEX IF NOT EXISTS idx_agent_checkpoints_workspace_id ON public.agent_checkpoints(workspace_id);

-- 7. Trigger for updated_at
CREATE TRIGGER campaign_arcs_updated_at
    BEFORE UPDATE ON public.campaign_arcs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER scheduled_tasks_updated_at
    BEFORE UPDATE ON public.scheduled_tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();
