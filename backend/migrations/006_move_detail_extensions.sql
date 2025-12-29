-- Move detail enhancements for checklist, assets, metrics, and status tracking

ALTER TABLE moves
ADD COLUMN IF NOT EXISTS checklist JSONB DEFAULT '[]'::JSONB,
ADD COLUMN IF NOT EXISTS assets JSONB DEFAULT '[]'::JSONB,
ADD COLUMN IF NOT EXISTS daily_metrics JSONB DEFAULT '[]'::JSONB,
ADD COLUMN IF NOT EXISTS confidence INTEGER,
ADD COLUMN IF NOT EXISTS started_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS completed_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS paused_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS rag_status VARCHAR(20),
ADD COLUMN IF NOT EXISTS rag_reason TEXT;

CREATE INDEX IF NOT EXISTS idx_moves_checklist ON moves USING GIN (checklist);
CREATE INDEX IF NOT EXISTS idx_moves_assets ON moves USING GIN (assets);
CREATE INDEX IF NOT EXISTS idx_moves_daily_metrics ON moves USING GIN (daily_metrics);
