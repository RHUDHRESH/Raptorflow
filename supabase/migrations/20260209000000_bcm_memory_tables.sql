-- =====================================
-- BCM MEMORY & FEEDBACK TABLES
-- ADR-0005: BCM Cognitive Identity
-- =====================================

-- BCM interaction memories (accumulated learning)
CREATE TABLE IF NOT EXISTS bcm_memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    memory_type TEXT NOT NULL,       -- 'correction', 'preference', 'pattern', 'insight'
    content JSONB NOT NULL,
    source TEXT NOT NULL,            -- 'user_feedback', 'generation_analysis', 'reflection'
    confidence FLOAT DEFAULT 0.5,
    created_at TIMESTAMPTZ DEFAULT now(),
    expires_at TIMESTAMPTZ           -- NULL = never expires
);

CREATE INDEX IF NOT EXISTS idx_bcm_memories_workspace ON bcm_memories(workspace_id, memory_type);
CREATE INDEX IF NOT EXISTS idx_bcm_memories_created ON bcm_memories(workspace_id, created_at DESC);

-- Generation log for learning from outputs
CREATE TABLE IF NOT EXISTS bcm_generation_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    content_type TEXT NOT NULL,      -- 'email', 'blog', 'social', 'general', etc.
    prompt_used TEXT NOT NULL,
    output TEXT NOT NULL,
    bcm_version INTEGER NOT NULL,
    feedback_score INTEGER CHECK (feedback_score BETWEEN 1 AND 5),
    user_edits TEXT,                 -- what the user changed (diff)
    tokens_used INTEGER,
    cost_usd FLOAT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_bcm_genlog_workspace ON bcm_generation_log(workspace_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_bcm_genlog_feedback ON bcm_generation_log(workspace_id, feedback_score)
    WHERE feedback_score IS NOT NULL;

-- RLS — scoped to service_role only
ALTER TABLE bcm_memories ENABLE ROW LEVEL SECURITY;
ALTER TABLE bcm_generation_log ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Allow all for service role" ON bcm_memories;
DROP POLICY IF EXISTS "Allow all for service role" ON bcm_generation_log;

CREATE POLICY "service_role_bcm_memories" ON bcm_memories
    FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "service_role_bcm_generation_log" ON bcm_generation_log
    FOR ALL USING (auth.role() = 'service_role');
