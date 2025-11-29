-- Migration 024: Campaigns & Moves Schema Update
-- Purpose: Align schema with the new Campaign/Move/Asset architecture

-- ============================================================================
-- 1. Update positioning table
-- ============================================================================
ALTER TABLE positioning ADD COLUMN IF NOT EXISTS problem_statement text;
ALTER TABLE positioning ADD COLUMN IF NOT EXISTS category_frame text;
ALTER TABLE positioning ADD COLUMN IF NOT EXISTS reason_to_believe text;
ALTER TABLE positioning ADD COLUMN IF NOT EXISTS competitive_alternative text;
ALTER TABLE positioning ADD COLUMN IF NOT EXISTS is_active boolean DEFAULT true;

-- ============================================================================
-- 2. Update message_architecture table
-- ============================================================================
ALTER TABLE message_architecture ADD COLUMN IF NOT EXISTS primary_claim text;
ALTER TABLE message_architecture ADD COLUMN IF NOT EXISTS proof_points jsonb DEFAULT '[]'::jsonb;

-- ============================================================================
-- 3. Update campaigns table
-- ============================================================================
ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS objective_type text; -- awareness, consideration, conversion, retention, advocacy
ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS target_metric text;
ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS target_value numeric;

-- ============================================================================
-- 4. Create campaign_channels table
-- ============================================================================
CREATE TABLE IF NOT EXISTS campaign_channels (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    channel text NOT NULL, -- linkedin, email, youtube, etc.
    role text NOT NULL, -- reach, engage, convert, retain
    budget_allocation numeric,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    CONSTRAINT campaign_channels_workspace_check CHECK (workspace_id IS NOT NULL)
);

CREATE INDEX IF NOT EXISTS idx_campaign_channels_campaign ON campaign_channels(campaign_id);

ALTER TABLE campaign_channels ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS campaign_channels_workspace_isolation ON campaign_channels;
CREATE POLICY campaign_channels_workspace_isolation ON campaign_channels
    USING (workspace_id = current_setting('app.current_workspace_id')::uuid)
    WITH CHECK (workspace_id = current_setting('app.current_workspace_id')::uuid);

-- ============================================================================
-- 5. Update cohorts table (Ensure strategy columns exist)
-- ============================================================================
-- Assuming cohorts table exists from previous migrations. 
-- If not, these will fail, but based on 013 it should exist.
DO $$ 
BEGIN
    BEGIN
        ALTER TABLE cohorts ADD COLUMN IF NOT EXISTS buying_triggers text[];
        ALTER TABLE cohorts ADD COLUMN IF NOT EXISTS decision_criteria text[];
        ALTER TABLE cohorts ADD COLUMN IF NOT EXISTS objection_map jsonb;
        ALTER TABLE cohorts ADD COLUMN IF NOT EXISTS attention_windows text[];
        ALTER TABLE cohorts ADD COLUMN IF NOT EXISTS journey_stage_distribution jsonb;
    EXCEPTION
        WHEN undefined_table THEN
            RAISE NOTICE 'Table cohorts does not exist, skipping column additions.';
    END;
END $$;

-- ============================================================================
-- 6. Create moves table
-- ============================================================================
CREATE TABLE IF NOT EXISTS moves (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    
    name text NOT NULL,
    move_type text NOT NULL, -- authority, consideration, objection, conversion, retention
    
    -- Targeting
    cohort_id uuid REFERENCES cohorts(id) ON DELETE SET NULL,
    journey_stage_from text,
    journey_stage_to text,
    
    -- Messaging
    message_variant_id uuid, -- Can reference message_architecture or specific variant
    
    -- Timeline
    start_date date,
    end_date date,
    
    -- Status
    status text DEFAULT 'planned', -- planned, preflight_failed, ready, in_progress, completed
    
    -- Success Metrics
    success_metric text,
    success_target numeric,
    
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    
    CONSTRAINT moves_workspace_check CHECK (workspace_id IS NOT NULL)
);

CREATE INDEX IF NOT EXISTS idx_moves_campaign ON moves(campaign_id);
CREATE INDEX IF NOT EXISTS idx_moves_workspace ON moves(workspace_id);

ALTER TABLE moves ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS moves_workspace_isolation ON moves;
CREATE POLICY moves_workspace_isolation ON moves
    USING (workspace_id = current_setting('app.current_workspace_id')::uuid)
    WITH CHECK (workspace_id = current_setting('app.current_workspace_id')::uuid);

-- ============================================================================
-- 7. Create assets table
-- ============================================================================
CREATE TABLE IF NOT EXISTS assets (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    move_id uuid NOT NULL REFERENCES moves(id) ON DELETE CASCADE,
    
    name text,
    format text NOT NULL, -- post, email, landing_page, ad, etc.
    channel text NOT NULL, -- linkedin, email, ...
    
    -- Creative Content
    creative_brief jsonb,
    single_minded_proposition text,
    content_body text,
    
    -- Status
    status text DEFAULT 'draft', -- draft, generating, ready, published
    external_url text,
    
    -- Metrics
    performance_metrics jsonb DEFAULT '{}'::jsonb,

    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),

    CONSTRAINT assets_workspace_check CHECK (workspace_id IS NOT NULL)
);

CREATE INDEX IF NOT EXISTS idx_assets_move ON assets(move_id);
CREATE INDEX IF NOT EXISTS idx_assets_workspace ON assets(workspace_id);

ALTER TABLE assets ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS assets_workspace_isolation ON assets;
CREATE POLICY assets_workspace_isolation ON assets
    USING (workspace_id = current_setting('app.current_workspace_id')::uuid)
    WITH CHECK (workspace_id = current_setting('app.current_workspace_id')::uuid);

-- ============================================================================
-- 8. Triggers
-- ============================================================================

-- Function to update updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply to new tables
DROP TRIGGER IF EXISTS update_campaign_channels_modtime ON campaign_channels;
CREATE TRIGGER update_campaign_channels_modtime BEFORE UPDATE ON campaign_channels FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

DROP TRIGGER IF EXISTS update_moves_modtime ON moves;
CREATE TRIGGER update_moves_modtime BEFORE UPDATE ON moves FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

DROP TRIGGER IF EXISTS update_assets_modtime ON assets;
CREATE TRIGGER update_assets_modtime BEFORE UPDATE ON assets FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

-- Trigger to update parent campaign timestamp when moves change
-- Assumes update_campaign_timestamp function exists (from mig 013)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'update_campaign_timestamp') THEN
        DROP TRIGGER IF EXISTS moves_update_campaign_trigger ON moves;
        CREATE TRIGGER moves_update_campaign_trigger AFTER INSERT OR UPDATE ON moves FOR EACH ROW EXECUTE FUNCTION update_campaign_timestamp();
    END IF;
END $$;
