-- Content Strategy table for managing content territories, pillar pages, and editorial calendar
-- Used by foundation content strategy endpoints

CREATE TABLE IF NOT EXISTS content_strategy (
    strategy_id text PRIMARY KEY,
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    territories jsonb NOT NULL DEFAULT '[]'::jsonb,
    pillar_pages jsonb NOT NULL DEFAULT '[]'::jsonb,
    editorial_calendar jsonb NOT NULL DEFAULT '[]'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE content_strategy ENABLE ROW LEVEL SECURITY;

CREATE POLICY content_strategy_tenant ON content_strategy
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());

CREATE INDEX idx_content_strategy_org ON content_strategy (org_id);