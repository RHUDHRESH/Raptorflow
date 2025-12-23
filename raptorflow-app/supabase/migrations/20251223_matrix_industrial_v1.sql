-- RaptorFlow Matrix — Industrial Migration v1.0
-- Block I: Cloud Infrastructure & Database Schema

-- 1. Enable Extensions
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Agent Decision Audit (Accuracy & ROI)
CREATE TABLE IF NOT EXISTS agent_decision_audit (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id TEXT NOT NULL,
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

-- 3. Model Lineage (MLOps)
CREATE TABLE IF NOT EXISTS model_lineage (
    model_id TEXT PRIMARY KEY,
    dataset_uri TEXT NOT NULL,
    artifact_uri TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Knowledge Graph (Conceptual Memory)
CREATE TABLE IF NOT EXISTS knowledge_concepts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(workspace_id, name)
);

CREATE TABLE IF NOT EXISTS knowledge_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id TEXT NOT NULL,
    source_id UUID REFERENCES knowledge_concepts(id) ON DELETE CASCADE,
    target_id UUID REFERENCES knowledge_concepts(id) ON DELETE CASCADE,
    relation TEXT NOT NULL,
    weight FLOAT DEFAULT 1.0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_id, target_id, relation)
);

-- 5. Indexes for Industrial Scale
CREATE INDEX IF NOT EXISTS idx_agent_decision_tenant ON agent_decision_audit(tenant_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_concepts_workspace ON knowledge_concepts(workspace_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_links_workspace ON knowledge_links(workspace_id);

-- 6. Realtime Enablement
ALTER PUBLICATION supabase_realtime ADD TABLE agent_decision_audit;
