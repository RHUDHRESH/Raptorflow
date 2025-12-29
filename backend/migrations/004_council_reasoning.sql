-- Council reasoning updates

CREATE TABLE IF NOT EXISTS reasoning_chains (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL,
    debate_history JSONB DEFAULT '[]'::JSONB,
    final_synthesis TEXT,
    metrics JSONB DEFAULT '{}'::JSONB,
    metadata JSONB DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS rejected_paths (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL,
    reasoning_chain_id UUID REFERENCES reasoning_chains(id) ON DELETE CASCADE,
    path_name TEXT NOT NULL,
    reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_reasoning_chains_workspace ON reasoning_chains(workspace_id);
CREATE INDEX IF NOT EXISTS idx_rejected_paths_reasoning_chain ON rejected_paths(reasoning_chain_id);

CREATE TRIGGER IF NOT EXISTS update_reasoning_chains_updated_at
    BEFORE UPDATE ON reasoning_chains FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'moves' AND column_name = 'consensus_metrics'
    ) THEN
        ALTER TABLE moves
        ADD COLUMN consensus_metrics JSONB DEFAULT '{}'::JSONB;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'moves' AND column_name = 'decree'
    ) THEN
        ALTER TABLE moves ADD COLUMN decree TEXT;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'moves' AND column_name = 'reasoning_chain_id'
    ) THEN
        ALTER TABLE moves
        ADD COLUMN reasoning_chain_id UUID REFERENCES reasoning_chains(id);
    END IF;
END;
$$;
