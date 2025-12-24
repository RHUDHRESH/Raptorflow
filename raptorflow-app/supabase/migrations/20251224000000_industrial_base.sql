-- RaptorFlow Industrial Base Schema (Consolidated 2025-12-24)
-- Standardized on explicit workspace management

-- 1. EXTENSIONS
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. WORKSPACE MANAGEMENT
CREATE TABLE IF NOT EXISTS workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS workspace_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id UUID NOT NULL, -- References auth.users
    role TEXT NOT NULL DEFAULT 'member' CHECK (role IN ('owner', 'admin', 'member')),
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(workspace_id, user_id)
);

-- 3. FOUNDATION MODULE
CREATE TABLE IF NOT EXISTS foundation_brand_kit (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    logo_url TEXT,
    primary_color TEXT,
    secondary_color TEXT,
    accent_color TEXT,
    typography_config JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS foundation_positioning (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_kit_id UUID NOT NULL REFERENCES foundation_brand_kit(id) ON DELETE CASCADE,
    uvp TEXT NOT NULL,
    target_market TEXT NOT NULL,
    competitive_advantage TEXT,
    elevator_pitch TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS foundation_voice_tone (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_kit_id UUID NOT NULL REFERENCES foundation_brand_kit(id) ON DELETE CASCADE,
    tone_name TEXT NOT NULL,
    description TEXT,
    keywords TEXT[],
    examples JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS foundation_state (
    workspace_id UUID PRIMARY KEY REFERENCES workspaces(id) ON DELETE CASCADE,
    data JSONB NOT NULL DEFAULT '{}',
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 4. CAMPAIGNS & MOVES
CREATE TABLE IF NOT EXISTS campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    objective TEXT,
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'completed', 'archived', 'planned')),
    start_date TIMESTAMPTZ,
    end_date TIMESTAMPTZ,
    arc_data JSONB DEFAULT '{}'::jsonb,
    kpi_targets JSONB DEFAULT '{}'::jsonb,
    rag_status TEXT DEFAULT 'green',
    strategy_context_id UUID,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS moves (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'approved', 'rejected', 'executed', 'queued', 'active', 'completed', 'abandoned')),
    priority INTEGER DEFAULT 3, -- 1: High, 5: Low
    move_type TEXT, -- social, email, ad, research
    agent_id TEXT,
    thread_id TEXT,
    execution_result JSONB DEFAULT '{}'::jsonb,
    tool_requirements JSONB DEFAULT '[]'::jsonb,
    scheduled_at TIMESTAMPTZ,
    approval_comment TEXT,
    refinement_data JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS move_approvals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    move_id UUID NOT NULL REFERENCES moves(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    status TEXT NOT NULL,
    comment TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS campaign_kpis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    metric_name TEXT NOT NULL,
    current_value NUMERIC DEFAULT 0,
    target_value NUMERIC,
    unit TEXT,
    last_updated TIMESTAMPTZ DEFAULT now(),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 5. BLACKBOX & TELEMETRY
CREATE TABLE IF NOT EXISTS blackbox_telemetry_industrial (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    move_id UUID NOT NULL REFERENCES moves(id) ON DELETE CASCADE,
    agent_id TEXT NOT NULL,
    trace JSONB NOT NULL DEFAULT '{}'::jsonb,
    tokens INTEGER DEFAULT 0,
    latency DOUBLE PRECISION DEFAULT 0.0,
    timestamp TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS blackbox_outcomes_industrial (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    campaign_id UUID REFERENCES campaigns(id) ON DELETE SET NULL,
    move_id UUID REFERENCES moves(id) ON DELETE SET NULL,
    source TEXT NOT NULL,
    value NUMERIC NOT NULL,
    confidence DOUBLE PRECISION DEFAULT 1.0,
    timestamp TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS blackbox_learnings_industrial (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    embedding vector(768),
    source_ids UUID[] DEFAULT '{}'::uuid[],
    learning_type TEXT NOT NULL, -- tactical, strategic, content
    timestamp TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS agent_decision_audit (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    agent_id TEXT NOT NULL,
    decision_type TEXT NOT NULL,
    input_state JSONB DEFAULT '{}',
    output_decision JSONB DEFAULT '{}',
    rationale TEXT,
    cost_estimate DECIMAL(10, 5) DEFAULT 0.0,
    accuracy_validated BOOLEAN DEFAULT FALSE,
    is_accurate BOOLEAN,
    feedback_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 6. MEMORY & ML
CREATE TABLE IF NOT EXISTS agent_memory_episodic (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    thread_id TEXT NOT NULL,
    observation TEXT NOT NULL,
    embedding vector(768),
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS agent_memory_semantic (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    fact TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    embedding vector(768),
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS agent_memory_procedural (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    fact TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    embedding vector(768),
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS entity_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    entity_name TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    description TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    embedding VECTOR(768),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS fact_store (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    category TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    embedding VECTOR(768),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ml_feature_store (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    entity_id UUID NOT NULL,
    feature_name TEXT NOT NULL,
    feature_value NUMERIC NOT NULL,
    vector_value vector(768),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 7. KNOWLEDGE GRAPH
CREATE TABLE IF NOT EXISTS knowledge_concepts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(workspace_id, name)
);

CREATE TABLE IF NOT EXISTS knowledge_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    source_id UUID REFERENCES knowledge_concepts(id) ON DELETE CASCADE,
    target_id UUID REFERENCES knowledge_concepts(id) ON DELETE CASCADE,
    relation TEXT NOT NULL,
    weight FLOAT DEFAULT 1.0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_id, target_id, relation)
);

-- 8. EXPERIMENTS
CREATE TABLE IF NOT EXISTS experiments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    goal TEXT NOT NULL,
    risk_level TEXT NOT NULL,
    channel TEXT NOT NULL,
    title TEXT NOT NULL,
    bet TEXT NOT NULL,
    why TEXT,
    principle TEXT,
    effort TEXT,
    time_to_signal TEXT,
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'generated', 'launched', 'checked_in', 'expired')),
    created_at TIMESTAMPTZ DEFAULT now(),
    launched_at TIMESTAMPTZ,
    self_report JSONB DEFAULT '{}'::jsonb,
    asset_ids UUID[] DEFAULT '{}'::uuid[]
);

-- 9. MUSE MODULE
CREATE TABLE IF NOT EXISTS muse_assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    content text not null,
    metadata jsonb default '{}'::jsonb,
    embedding vector(768),
    created_at timestamptz default now()
);

-- 10. SKILLS REGISTRY
CREATE TABLE IF NOT EXISTS skills (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    description text,
    instructions text not null,
    type text not null check (type in ('system', 'custom')),
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

CREATE TABLE IF NOT EXISTS skill_registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    input_schema JSONB,
    output_schema JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 11. MLOPS
CREATE TABLE IF NOT EXISTS model_lineage (
    model_id TEXT PRIMARY KEY,
    dataset_uri TEXT NOT NULL,
    artifact_uri TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 12. LANGGRAPH CHECKPOINTING
CREATE TABLE IF NOT EXISTS checkpoints (
    thread_id TEXT NOT NULL,
    checkpoint_ns TEXT NOT NULL DEFAULT '',
    checkpoint_id TEXT NOT NULL,
    parent_checkpoint_id TEXT,
    type TEXT,
    checkpoint BYTEA,
    metadata BYTEA,
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id)
);

CREATE TABLE IF NOT EXISTS checkpoint_blobs (
    thread_id TEXT NOT NULL,
    checkpoint_ns TEXT NOT NULL DEFAULT '',
    channel TEXT NOT NULL,
    version TEXT NOT NULL,
    type TEXT,
    blob BYTEA,
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    PRIMARY KEY (thread_id, checkpoint_ns, channel, version)
);

CREATE TABLE IF NOT EXISTS checkpoint_writes (
    thread_id TEXT NOT NULL,
    checkpoint_ns TEXT NOT NULL DEFAULT '',
    checkpoint_id TEXT NOT NULL,
    task_id TEXT NOT NULL,
    idx INTEGER NOT NULL,
    channel TEXT NOT NULL,
    type TEXT,
    blob BYTEA,
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id, task_id, idx)
);

CREATE TABLE IF NOT EXISTS graph_threads (
    thread_id TEXT PRIMARY KEY,
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id UUID,
    status TEXT DEFAULT 'idle' CHECK (status IN ('idle', 'busy', 'interrupted', 'error', 'completed')),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS checkpoint_metadata (
    thread_id TEXT NOT NULL,
    checkpoint_id TEXT NOT NULL,
    step_name TEXT,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    latency_ms REAL DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (thread_id, checkpoint_id)
);

-- 13. SUBSCRIPTIONS & ENTITLEMENTS (₹ Rupees)
CREATE TABLE IF NOT EXISTS subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    plan_name TEXT NOT NULL CHECK (plan_name IN ('Ascent', 'Glide', 'Soar')),
    status TEXT NOT NULL DEFAULT 'inactive' CHECK (status IN ('active', 'inactive', 'past_due', 'canceled')),
    amount_rupees NUMERIC NOT NULL,
    currency TEXT DEFAULT 'INR',
    current_period_start TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,
    moves_count INTEGER DEFAULT 0,
    muse_generations_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    subscription_id UUID REFERENCES subscriptions(id) ON DELETE SET NULL,
    amount_rupees NUMERIC NOT NULL,
    transaction_id TEXT,
    provider TEXT, -- PhonePe, Razorpay, etc.
    status TEXT DEFAULT 'paid',
    pdf_url TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 14. FUNCTIONS (RPCs)
CREATE OR REPLACE FUNCTION match_muse_assets (
  query_embedding vector(768),
  match_threshold float,
  match_count int,
  p_workspace_id uuid
)
RETURNS TABLE (
  id uuid,
  content text,
  metadata jsonb,
  similarity float
)
LANGUAGE plpgsql
AS $$
begin
  return query
  select
    muse_assets.id,
    muse_assets.content,
    muse_assets.metadata,
    1 - (muse_assets.embedding <=> query_embedding) as similarity
  from muse_assets
  where muse_assets.workspace_id = p_workspace_id
    AND 1 - (muse_assets.embedding <=> query_embedding) > match_threshold
  order by muse_assets.embedding <=> query_embedding
  limit match_count;
end;
$$;

CREATE OR REPLACE FUNCTION match_episodic_memory (
  query_embedding vector(768),
  match_threshold float,
  match_count int,
  p_workspace_id uuid,
  p_thread_id text
)
RETURNS TABLE (
  id uuid,
  observation text,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    ame.id,
    ame.observation,
    1 - (ame.embedding <=> query_embedding) AS similarity
  FROM agent_memory_episodic ame
  WHERE ame.workspace_id = p_workspace_id
    AND ame.thread_id = p_thread_id
    AND 1 - (ame.embedding <=> query_embedding) > match_threshold
  ORDER BY similarity DESC
  LIMIT match_count;
END;
$$;

CREATE OR REPLACE FUNCTION match_semantic_memory (
  query_embedding vector(768),
  match_threshold float,
  match_count int,
  p_workspace_id uuid
)
RETURNS TABLE (
  id uuid,
  fact text,
  metadata jsonb,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    ams.id,
    ams.fact,
    ams.metadata,
    1 - (ams.embedding <=> query_embedding) AS similarity
  FROM agent_memory_semantic ams
  WHERE ams.workspace_id = p_workspace_id
    AND 1 - (ams.embedding <=> query_embedding) > match_threshold
  ORDER BY similarity DESC
  LIMIT match_count;
END;
$$;

CREATE OR REPLACE FUNCTION match_blackbox_learnings (
  query_embedding vector(768),
  match_threshold float DEFAULT 0.5,
  match_count int DEFAULT 10,
  p_workspace_id uuid DEFAULT NULL
)
RETURNS TABLE (
  id uuid,
  content text,
  learning_type text,
  source_ids uuid[],
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    bbl.id,
    bbl.content,
    bbl.learning_type,
    bbl.source_ids,
    1 - (bbl.embedding <=> query_embedding) AS similarity
  FROM blackbox_learnings_industrial bbl
  WHERE (p_workspace_id IS NULL OR bbl.workspace_id = p_workspace_id)
    AND 1 - (bbl.embedding <=> query_embedding) > match_threshold
  ORDER BY similarity DESC
  LIMIT match_count;
END;
$$;

-- 15. INDEXES
CREATE INDEX IF NOT EXISTS idx_muse_assets_vector ON muse_assets USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_semantic_memory_vector ON agent_memory_semantic USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_episodic_memory_vector ON agent_memory_episodic USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_procedural_memory_vector ON agent_memory_procedural USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_entity_vector ON entity_embeddings USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_fact_vector ON fact_store USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_experiments_workspace ON experiments(workspace_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_workspace ON campaigns(workspace_id);
CREATE INDEX IF NOT EXISTS idx_moves_campaign ON moves(campaign_id);
CREATE INDEX IF NOT EXISTS idx_bb_telemetry_workspace ON blackbox_telemetry_industrial(workspace_id);
CREATE INDEX IF NOT EXISTS idx_bb_outcomes_workspace ON blackbox_outcomes_industrial(workspace_id);
CREATE INDEX IF NOT EXISTS idx_bb_learnings_workspace ON blackbox_learnings_industrial(workspace_id);

-- 16. RLS POLICIES (Explicit Workspace Isolation)
ALTER TABLE workspaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE workspace_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE foundation_brand_kit ENABLE ROW LEVEL SECURITY;
ALTER TABLE foundation_positioning ENABLE ROW LEVEL SECURITY;
ALTER TABLE foundation_voice_tone ENABLE ROW LEVEL SECURITY;
ALTER TABLE foundation_state ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE moves ENABLE ROW LEVEL SECURITY;
ALTER TABLE move_approvals ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaign_kpis ENABLE ROW LEVEL SECURITY;
ALTER TABLE blackbox_telemetry_industrial ENABLE ROW LEVEL SECURITY;
ALTER TABLE blackbox_outcomes_industrial ENABLE ROW LEVEL SECURITY;
ALTER TABLE blackbox_learnings_industrial ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_decision_audit ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_memory_episodic ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_memory_semantic ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_memory_procedural ENABLE ROW LEVEL SECURITY;
ALTER TABLE entity_embeddings ENABLE ROW LEVEL SECURITY;
ALTER TABLE fact_store ENABLE ROW LEVEL SECURITY;
ALTER TABLE ml_feature_store ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge_concepts ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge_links ENABLE ROW LEVEL SECURITY;
ALTER TABLE experiments ENABLE ROW LEVEL SECURITY;
ALTER TABLE muse_assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE skill_registry ENABLE ROW LEVEL SECURITY;
ALTER TABLE model_lineage ENABLE ROW LEVEL SECURITY;
ALTER TABLE checkpoints ENABLE ROW LEVEL SECURITY;
ALTER TABLE checkpoint_blobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE checkpoint_writes ENABLE ROW LEVEL SECURITY;
ALTER TABLE graph_threads ENABLE ROW LEVEL SECURITY;
ALTER TABLE checkpoint_metadata ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;

-- Global Policy Helper: Check if user is member of workspace
CREATE OR REPLACE FUNCTION is_member_of(p_workspace_id uuid)
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM workspace_members
    WHERE workspace_id = p_workspace_id
    AND user_id = auth.uid()
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Policies for Workspaces (View if member)
CREATE POLICY view_workspaces ON workspaces FOR SELECT
    USING (EXISTS (SELECT 1 FROM workspace_members WHERE workspace_id = workspaces.id AND user_id = auth.uid()));

-- Policies for Workspace Members (View if member of same workspace)
CREATE POLICY view_members ON workspace_members FOR SELECT
    USING (is_member_of(workspace_id));

-- Generic Workspace Isolation Policies
DO $$
DECLARE
    t text;
BEGIN
    FOR t IN
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name NOT IN ('workspaces', 'workspace_members', 'skills', 'skill_registry', 'model_lineage')
        AND table_name IN (
            SELECT table_name FROM information_schema.columns WHERE column_name = 'workspace_id'
        )
    LOOP
        EXECUTE format('CREATE POLICY workspace_isolation_%I ON %I FOR ALL USING (is_member_of(workspace_id)) WITH CHECK (is_member_of(workspace_id))', t, t);
    END LOOP;
END $$;

-- Exceptions & Special Cases
CREATE POLICY skill_registry_read ON skill_registry FOR SELECT USING (true);
CREATE POLICY skills_read ON skills FOR SELECT USING (true);

-- 17. REALTIME
ALTER PUBLICATION supabase_realtime ADD TABLE agent_decision_audit;
ALTER PUBLICATION supabase_realtime ADD TABLE moves;
ALTER PUBLICATION supabase_realtime ADD TABLE campaigns;
