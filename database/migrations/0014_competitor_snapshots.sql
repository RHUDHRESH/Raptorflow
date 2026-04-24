-- Competitor snapshots upgrade
-- Migration 0006 already creates competitor_snapshots with an older schema.
-- This migration normalizes it to the URL-based shape used by the live code.

ALTER TABLE competitor_snapshots
    ADD COLUMN IF NOT EXISTS competitor_url text,
    ADD COLUMN IF NOT EXISTS hash text,
    ADD COLUMN IF NOT EXISTS status text NOT NULL DEFAULT 'pending',
    ADD COLUMN IF NOT EXISTS scrape_data jsonb NOT NULL DEFAULT '{}'::jsonb,
    ADD COLUMN IF NOT EXISTS created_at timestamptz NOT NULL DEFAULT now(),
    ADD COLUMN IF NOT EXISTS updated_at timestamptz NOT NULL DEFAULT now();

UPDATE competitor_snapshots
SET competitor_url = COALESCE(competitor_url, competitor_name)
WHERE competitor_url IS NULL;

ALTER TABLE competitor_snapshots
    ALTER COLUMN competitor_url SET NOT NULL;

ALTER TABLE competitor_snapshots ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_policies
        WHERE schemaname = 'public'
          AND tablename = 'competitor_snapshots'
          AND policyname = 'competitor_snapshots_tenant'
    ) THEN
        CREATE POLICY competitor_snapshots_tenant ON competitor_snapshots
            USING (org_id = app.current_org_id())
            WITH CHECK (org_id = app.current_org_id());
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_competitor_snapshots_org_url ON competitor_snapshots (org_id, competitor_url);
CREATE INDEX IF NOT EXISTS idx_competitor_snapshots_created_at ON competitor_snapshots (org_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_competitor_snapshots_status ON competitor_snapshots (org_id, status);
