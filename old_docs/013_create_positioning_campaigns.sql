-- Migration 013: Create Positioning & Campaigns Core Tables
-- Phase: Week 2 - Codex Schema Creation
-- Purpose: Add positioning system and campaign architecture tables
-- New Tables: 5 (positioning, message_architecture, campaigns, campaign_quests, campaign_cohorts)
-- Scope: Expand from 43 → 48 tables

-- ============================================================================
-- TABLE 1: positioning
-- Purpose: Store positioning frameworks for different market segments
-- Workspace isolation: workspace_id + RLS policy
-- ============================================================================
CREATE TABLE IF NOT EXISTS positioning (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

  -- Core fields
  name text NOT NULL,
  description text,
  market_segment text NOT NULL, -- "B2B", "B2C", "SMB", "Enterprise", etc.
  target_persona text,

  -- Positioning elements
  key_message text,
  value_proposition text,
  differentiation text,
  target_pain_points text[],
  solution_benefits text[],

  -- Metadata
  created_by uuid NOT NULL REFERENCES auth.users(id) ON DELETE SET NULL,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),

  -- Constraints
  CONSTRAINT positioning_workspace_check CHECK (workspace_id IS NOT NULL)
);

CREATE INDEX idx_positioning_workspace ON positioning(workspace_id);
CREATE INDEX idx_positioning_segment ON positioning(workspace_id, market_segment);

-- Add RLS policy for positioning
ALTER TABLE positioning ENABLE ROW LEVEL SECURITY;

CREATE POLICY positioning_workspace_isolation ON positioning
  USING (workspace_id = current_setting('app.current_workspace_id')::uuid)
  WITH CHECK (workspace_id = current_setting('app.current_workspace_id')::uuid);

-- ============================================================================
-- TABLE 2: message_architecture
-- Purpose: Define messaging frameworks and content pillars
-- Workspace isolation: workspace_id + RLS policy
-- ============================================================================
CREATE TABLE IF NOT EXISTS message_architecture (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

  -- Core fields
  name text NOT NULL,
  description text,
  positioning_id uuid REFERENCES positioning(id) ON DELETE CASCADE,

  -- Message framework
  primary_message text NOT NULL,
  secondary_messages text[],
  content_pillars text[],
  brand_voice text,
  tone_guidelines text,

  -- Target context
  target_audience text,
  key_topics text[],
  content_themes text[],

  -- Metadata
  created_by uuid NOT NULL REFERENCES auth.users(id) ON DELETE SET NULL,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),

  CONSTRAINT message_arch_workspace_check CHECK (workspace_id IS NOT NULL)
);

CREATE INDEX idx_message_architecture_workspace ON message_architecture(workspace_id);
CREATE INDEX idx_message_architecture_positioning ON message_architecture(positioning_id);

ALTER TABLE message_architecture ENABLE ROW LEVEL SECURITY;

CREATE POLICY message_architecture_workspace_isolation ON message_architecture
  USING (workspace_id = current_setting('app.current_workspace_id')::uuid)
  WITH CHECK (workspace_id = current_setting('app.current_workspace_id')::uuid);

-- ============================================================================
-- TABLE 3: campaigns
-- Purpose: Core campaign records with positioning and messaging
-- Workspace isolation: workspace_id + RLS policy
-- ============================================================================
CREATE TABLE IF NOT EXISTS campaigns (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

  -- Core fields
  name text NOT NULL,
  description text,
  objective text,

  -- Campaign configuration
  status text NOT NULL DEFAULT 'draft',
  -- Status values: draft, planning, active, paused, completed, archived

  positioning_id uuid REFERENCES positioning(id) ON DELETE SET NULL,
  message_architecture_id uuid REFERENCES message_architecture(id) ON DELETE SET NULL,

  -- Scope
  target_segments text[],
  target_geographies text[],

  -- Timeline
  start_date date,
  end_date date,
  planned_duration_days integer,

  -- Budget & Resources
  budget_allocation numeric,
  allocated_budget_amount numeric,
  resource_allocation jsonb, -- {agents: [...], channels: [...]}

  -- Performance
  total_reach bigint DEFAULT 0,
  total_engagements bigint DEFAULT 0,
  conversion_count integer DEFAULT 0,
  roi_percentage numeric,

  -- Metadata
  created_by uuid NOT NULL REFERENCES auth.users(id) ON DELETE SET NULL,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),

  CONSTRAINT campaigns_workspace_check CHECK (workspace_id IS NOT NULL),
  CONSTRAINT campaigns_status_check CHECK (status IN ('draft', 'planning', 'active', 'paused', 'completed', 'archived'))
);

CREATE INDEX idx_campaigns_workspace ON campaigns(workspace_id);
CREATE INDEX idx_campaigns_status ON campaigns(workspace_id, status);
CREATE INDEX idx_campaigns_positioning ON campaigns(positioning_id);
CREATE INDEX idx_campaigns_dates ON campaigns(workspace_id, start_date, end_date);

ALTER TABLE campaigns ENABLE ROW LEVEL SECURITY;

CREATE POLICY campaigns_workspace_isolation ON campaigns
  USING (workspace_id = current_setting('app.current_workspace_id')::uuid)
  WITH CHECK (workspace_id = current_setting('app.current_workspace_id')::uuid);

-- ============================================================================
-- TABLE 4: campaign_quests
-- Purpose: Track quest/objective hierarchy within campaigns
-- Workspace isolation: workspace_id + RLS policy
-- ============================================================================
CREATE TABLE IF NOT EXISTS campaign_quests (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,

  -- Quest definition
  name text NOT NULL,
  description text,
  objective text,

  -- Hierarchy
  parent_quest_id uuid REFERENCES campaign_quests(id) ON DELETE CASCADE,
  quest_order integer,

  -- Status
  status text NOT NULL DEFAULT 'pending',
  -- Status: pending, in_progress, completed, blocked, on_hold

  -- Timeline
  start_date date,
  end_date date,
  due_date date,

  -- Execution
  assigned_to_agents text[], -- agent names/types
  expected_output text,
  actual_output text,

  -- Metadata
  created_by uuid NOT NULL REFERENCES auth.users(id) ON DELETE SET NULL,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),

  CONSTRAINT campaign_quests_workspace_check CHECK (workspace_id IS NOT NULL),
  CONSTRAINT campaign_quests_status_check CHECK (status IN ('pending', 'in_progress', 'completed', 'blocked', 'on_hold'))
);

CREATE INDEX idx_campaign_quests_workspace ON campaign_quests(workspace_id);
CREATE INDEX idx_campaign_quests_campaign ON campaign_quests(campaign_id);
CREATE INDEX idx_campaign_quests_status ON campaign_quests(campaign_id, status);
CREATE INDEX idx_campaign_quests_parent ON campaign_quests(parent_quest_id);

ALTER TABLE campaign_quests ENABLE ROW LEVEL SECURITY;

CREATE POLICY campaign_quests_workspace_isolation ON campaign_quests
  USING (workspace_id = current_setting('app.current_workspace_id')::uuid)
  WITH CHECK (workspace_id = current_setting('app.current_workspace_id')::uuid);

-- ============================================================================
-- TABLE 5: campaign_cohorts
-- Purpose: Association table linking campaigns to customer cohorts
-- Workspace isolation: workspace_id + RLS policy
-- ============================================================================
CREATE TABLE IF NOT EXISTS campaign_cohorts (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  cohort_id uuid NOT NULL REFERENCES cohorts(id) ON DELETE CASCADE,

  -- Allocation
  allocation_percentage numeric,
  target_count integer,
  reached_count integer DEFAULT 0,
  converted_count integer DEFAULT 0,

  -- Metadata
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),

  CONSTRAINT campaign_cohorts_workspace_check CHECK (workspace_id IS NOT NULL),
  CONSTRAINT campaign_cohorts_unique UNIQUE(campaign_id, cohort_id)
);

CREATE INDEX idx_campaign_cohorts_workspace ON campaign_cohorts(workspace_id);
CREATE INDEX idx_campaign_cohorts_campaign ON campaign_cohorts(campaign_id);
CREATE INDEX idx_campaign_cohorts_cohort ON campaign_cohorts(cohort_id);

ALTER TABLE campaign_cohorts ENABLE ROW LEVEL SECURITY;

CREATE POLICY campaign_cohorts_workspace_isolation ON campaign_cohorts
  USING (workspace_id = current_setting('app.current_workspace_id')::uuid)
  WITH CHECK (workspace_id = current_setting('app.current_workspace_id')::uuid);

-- ============================================================================
-- VERIFICATION TRIGGERS
-- ============================================================================

-- Update campaigns.updated_at on related table changes
CREATE OR REPLACE FUNCTION update_campaign_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE campaigns SET updated_at = now() WHERE id = NEW.campaign_id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER campaign_quests_update_trigger
AFTER INSERT OR UPDATE ON campaign_quests
FOR EACH ROW
EXECUTE FUNCTION update_campaign_timestamp();

CREATE TRIGGER campaign_cohorts_update_trigger
AFTER INSERT OR UPDATE ON campaign_cohorts
FOR EACH ROW
EXECUTE FUNCTION update_campaign_timestamp();

-- ============================================================================
-- MIGRATION VERIFICATION BLOCK
-- ============================================================================

/*
POST-MIGRATION VERIFICATION:

1. Table creation:
   SELECT COUNT(*) FROM information_schema.tables
   WHERE table_schema = 'public' AND table_name IN
   ('positioning', 'message_architecture', 'campaigns', 'campaign_quests', 'campaign_cohorts');
   -- Expected: 5

2. RLS policies:
   SELECT COUNT(*) FROM pg_policies
   WHERE tablename IN ('positioning', 'message_architecture', 'campaigns', 'campaign_quests', 'campaign_cohorts');
   -- Expected: 5

3. Indexes created:
   SELECT COUNT(*) FROM pg_indexes
   WHERE tablename IN ('positioning', 'message_architecture', 'campaigns', 'campaign_quests', 'campaign_cohorts')
   AND schemaname = 'public';
   -- Expected: 12+ indexes

4. Triggers:
   SELECT COUNT(*) FROM pg_trigger
   WHERE tgrelname IN ('campaign_quests', 'campaign_cohorts');
   -- Expected: 2

5. Foreign key constraints:
   SELECT COUNT(*) FROM information_schema.table_constraints
   WHERE constraint_type = 'FOREIGN KEY'
   AND (table_name IN ('positioning', 'message_architecture', 'campaigns', 'campaign_quests', 'campaign_cohorts'));
   -- Expected: 12+ FKs
*/
