-- Industrial Blackbox Tables
-- Refined schemas for high-scale MLOps and Agentic Intelligence

-- 1. Refined Telemetry (Execution Traces)
CREATE TABLE IF NOT EXISTS blackbox_telemetry_industrial (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    move_id UUID NOT NULL REFERENCES moves(id),
    agent_id TEXT NOT NULL,
    trace JSONB NOT NULL DEFAULT '{}'::jsonb,
    tokens INTEGER DEFAULT 0,
    latency DOUBLE PRECISION DEFAULT 0.0,
    timestamp TIMESTAMPTZ DEFAULT now()
);

-- 2. Refined Outcomes (Conversion/Engagement)
CREATE TABLE IF NOT EXISTS blackbox_outcomes_industrial (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source TEXT NOT NULL,
    value NUMERIC NOT NULL,
    confidence DOUBLE PRECISION DEFAULT 1.0,
    timestamp TIMESTAMPTZ DEFAULT now()
);

-- 3. Blackbox Learnings (Strategic Memory)
CREATE TABLE IF NOT EXISTS blackbox_learnings_industrial (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    embedding vector(1536), -- 1536 for OpenAI/standard embeddings
    source_ids UUID[] DEFAULT '{}'::uuid[],
    learning_type TEXT NOT NULL, -- tactical, strategic, content
    timestamp TIMESTAMPTZ DEFAULT now()
);

-- Enable RLS
ALTER TABLE blackbox_telemetry_industrial ENABLE ROW LEVEL SECURITY;
ALTER TABLE blackbox_outcomes_industrial ENABLE ROW LEVEL SECURITY;
ALTER TABLE blackbox_learnings_industrial ENABLE ROW LEVEL SECURITY;

-- Indexing for performance
CREATE INDEX IF NOT EXISTS idx_bb_telemetry_move_id ON blackbox_telemetry_industrial(move_id);
CREATE INDEX IF NOT EXISTS idx_bb_telemetry_agent_id ON blackbox_telemetry_industrial(agent_id);
CREATE INDEX IF NOT EXISTS idx_bb_outcomes_source ON blackbox_outcomes_industrial(source);
CREATE INDEX IF NOT EXISTS idx_bb_learnings_type ON blackbox_learnings_industrial(learning_type);
