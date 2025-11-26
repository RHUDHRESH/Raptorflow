-- ============================================
-- RAPTORFLOW STRATEGIC SYSTEM ENHANCEMENTS
-- Migration 010: Enhance Existing Tables
-- Run after 009_strategic_system_foundation.sql
-- ============================================

-- ============================================
-- 1. ENHANCE COHORTS TABLE
-- ============================================

-- Add strategic attributes to cohorts
ALTER TABLE public.cohorts ADD COLUMN IF NOT EXISTS buying_triggers JSONB DEFAULT '[]'::jsonb;
ALTER TABLE public.cohorts ADD COLUMN IF NOT EXISTS decision_criteria JSONB DEFAULT '[]'::jsonb;
ALTER TABLE public.cohorts ADD COLUMN IF NOT EXISTS objection_map JSONB DEFAULT '[]'::jsonb;
ALTER TABLE public.cohorts ADD COLUMN IF NOT EXISTS attention_windows JSONB DEFAULT '{}'::jsonb;
ALTER TABLE public.cohorts ADD COLUMN IF NOT EXISTS journey_distribution JSONB DEFAULT '{}'::jsonb;
ALTER TABLE public.cohorts ADD COLUMN IF NOT EXISTS competitive_frame JSONB DEFAULT '{}'::jsonb;
ALTER TABLE public.cohorts ADD COLUMN IF NOT EXISTS decision_making_unit JSONB DEFAULT '{}'::jsonb;
ALTER TABLE public.cohorts ADD COLUMN IF NOT EXISTS health_score INTEGER CHECK (health_score BETWEEN 0 AND 100);
ALTER TABLE public.cohorts ADD COLUMN IF NOT EXISTS last_validated TIMESTAMP WITH TIME ZONE;

-- Add indexes for new JSONB columns
CREATE INDEX IF NOT EXISTS idx_cohorts_buying_triggers ON public.cohorts USING GIN(buying_triggers);
CREATE INDEX IF NOT EXISTS idx_cohorts_decision_criteria ON public.cohorts USING GIN(decision_criteria);
CREATE INDEX IF NOT EXISTS idx_cohorts_objection_map ON public.cohorts USING GIN(objection_map);
CREATE INDEX IF NOT EXISTS idx_cohorts_health_score ON public.cohorts(health_score);

-- Add comments to document the JSONB structure
COMMENT ON COLUMN public.cohorts.buying_triggers IS 'Array of {trigger, strength, timing, signal}';
COMMENT ON COLUMN public.cohorts.decision_criteria IS 'Array of {criterion, weight, description}. Weights must sum to 1.0';
COMMENT ON COLUMN public.cohorts.objection_map IS 'Array of {objection, frequency, stage, response, linked_asset_ids[]}';
COMMENT ON COLUMN public.cohorts.attention_windows IS 'Object with channel keys: {channel: {best_times[], receptivity, preferred_formats[]}}';
COMMENT ON COLUMN public.cohorts.journey_distribution IS 'Object: {unaware, problem_aware, solution_aware, product_aware, most_aware}. Must sum to 1.0';
COMMENT ON COLUMN public.cohorts.competitive_frame IS 'Object: {direct_competitors[], category_alternatives[], switching_triggers[]}';
COMMENT ON COLUMN public.cohorts.decision_making_unit IS 'Object: {roles[], influencers[], decision_maker, approval_chain[]}';

-- ============================================
-- 2. ENHANCE MOVES TABLE
-- ============================================

-- Add campaign linkage and strategic context
ALTER TABLE public.moves ADD COLUMN IF NOT EXISTS campaign_id UUID REFERENCES public.campaigns(id) ON DELETE SET NULL;
ALTER TABLE public.moves ADD COLUMN IF NOT EXISTS journey_stage_from VARCHAR(50);
ALTER TABLE public.moves ADD COLUMN IF NOT EXISTS journey_stage_to VARCHAR(50);
ALTER TABLE public.moves ADD COLUMN IF NOT EXISTS message_variant JSONB DEFAULT '{}'::jsonb;
ALTER TABLE public.moves ADD COLUMN IF NOT EXISTS asset_requirements JSONB DEFAULT '[]'::jsonb;
ALTER TABLE public.moves ADD COLUMN IF NOT EXISTS intensity VARCHAR(20) CHECK (intensity IN ('light', 'standard', 'aggressive'));

-- Add indexes for new columns
CREATE INDEX IF NOT EXISTS idx_moves_campaign ON public.moves(campaign_id);
CREATE INDEX IF NOT EXISTS idx_moves_journey_stages ON public.moves(journey_stage_from, journey_stage_to);
CREATE INDEX IF NOT EXISTS idx_moves_intensity ON public.moves(intensity);

-- Add comments to document the JSONB structure
COMMENT ON COLUMN public.moves.message_variant IS 'Object: {proof_point_id, angle, tone, emphasis[]}';
COMMENT ON COLUMN public.moves.asset_requirements IS 'Array of {channel, format, quantity, brief_data}';

-- ============================================
-- 3. ADD JOURNEY STAGE ENUM (for reference)
-- ============================================

-- Create a reference table for journey stages (optional, for validation)
CREATE TABLE IF NOT EXISTS public.journey_stages (
  id VARCHAR(50) PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  sort_order INTEGER NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insert journey stages
INSERT INTO public.journey_stages (id, name, description, sort_order) VALUES
  ('unaware', 'Unaware', 'Don''t know they have a problem', 1),
  ('problem_aware', 'Problem Aware', 'Know the problem, don''t know solutions exist', 2),
  ('solution_aware', 'Solution Aware', 'Know solutions exist, don''t know your product', 3),
  ('product_aware', 'Product Aware', 'Know your product, not yet convinced', 4),
  ('most_aware', 'Most Aware', 'Ready to buy, need final push', 5)
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- 4. ADD CHANNEL ROLES ENUM (for reference)
-- ============================================

-- Create a reference table for channel roles (optional, for validation)
CREATE TABLE IF NOT EXISTS public.channel_roles (
  id VARCHAR(50) PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insert channel roles
INSERT INTO public.channel_roles (id, name, description) VALUES
  ('reach', 'Reach', 'Get attention (LinkedIn, Instagram, ads)'),
  ('engage', 'Engage', 'Build interest (Email, content marketing)'),
  ('convert', 'Convert', 'Drive action (Landing pages, sales calls)'),
  ('retain', 'Retain', 'Keep engaged (Email, community, support)')
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- 5. ADD VALIDATION FUNCTIONS
-- ============================================

-- Function to validate decision criteria weights sum to 1.0
CREATE OR REPLACE FUNCTION validate_decision_criteria_weights(criteria JSONB)
RETURNS BOOLEAN AS $$
DECLARE
  total_weight NUMERIC := 0;
  criterion JSONB;
BEGIN
  -- If empty array, return true
  IF jsonb_array_length(criteria) = 0 THEN
    RETURN true;
  END IF;
  
  -- Sum all weights
  FOR criterion IN SELECT * FROM jsonb_array_elements(criteria)
  LOOP
    total_weight := total_weight + (criterion->>'weight')::NUMERIC;
  END LOOP;
  
  -- Check if sum is approximately 1.0 (allow small floating point errors)
  RETURN ABS(total_weight - 1.0) < 0.01;
END;
$$ LANGUAGE plpgsql;

-- Function to validate journey distribution sums to 1.0
CREATE OR REPLACE FUNCTION validate_journey_distribution(distribution JSONB)
RETURNS BOOLEAN AS $$
DECLARE
  total NUMERIC := 0;
BEGIN
  -- If empty object, return true
  IF distribution = '{}'::jsonb THEN
    RETURN true;
  END IF;
  
  -- Sum all percentages
  total := COALESCE((distribution->>'unaware')::NUMERIC, 0) +
           COALESCE((distribution->>'problem_aware')::NUMERIC, 0) +
           COALESCE((distribution->>'solution_aware')::NUMERIC, 0) +
           COALESCE((distribution->>'product_aware')::NUMERIC, 0) +
           COALESCE((distribution->>'most_aware')::NUMERIC, 0);
  
  -- Check if sum is approximately 1.0 (allow small floating point errors)
  RETURN ABS(total - 1.0) < 0.01;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 6. ADD CHECK CONSTRAINTS (optional, can be enforced in app layer)
-- ============================================

-- Note: These are commented out as they might be too strict for initial data entry
-- Uncomment if you want database-level validation

-- ALTER TABLE public.cohorts ADD CONSTRAINT check_decision_criteria_weights
--   CHECK (validate_decision_criteria_weights(decision_criteria));

-- ALTER TABLE public.cohorts ADD CONSTRAINT check_journey_distribution_sum
--   CHECK (validate_journey_distribution(journey_distribution));

-- ============================================
-- 7. UPDATE RLS POLICIES FOR MOVES
-- ============================================

-- The moves table should already have RLS enabled from previous migrations
-- We just need to ensure campaign-linked moves are accessible

-- Drop existing policies if they need updating
-- (This assumes moves table already has basic RLS policies)

-- Add policy for viewing moves by campaign
DROP POLICY IF EXISTS "Users can view moves by campaign" ON public.moves;
CREATE POLICY "Users can view moves by campaign"
  ON public.moves FOR SELECT
  USING (
    workspace_id = get_user_workspace_id() OR
    campaign_id IN (
      SELECT id FROM public.campaigns WHERE workspace_id = get_user_workspace_id()
    )
  );

-- ============================================
-- 8. CREATE HELPER VIEWS
-- ============================================

-- View for campaign health summary
CREATE OR REPLACE VIEW public.campaign_health_summary AS
SELECT 
  c.id,
  c.name,
  c.status,
  c.health_score,
  c.objective,
  c.start_date,
  c.end_date,
  COUNT(DISTINCT m.id) as total_moves,
  COUNT(DISTINCT cc.cohort_id) as total_cohorts,
  CASE 
    WHEN c.end_date < CURRENT_DATE THEN 'completed'
    WHEN c.start_date > CURRENT_DATE THEN 'upcoming'
    WHEN c.health_score >= 80 THEN 'healthy'
    WHEN c.health_score >= 60 THEN 'on_track'
    WHEN c.health_score >= 40 THEN 'at_risk'
    ELSE 'critical'
  END as health_status
FROM public.campaigns c
LEFT JOIN public.moves m ON m.campaign_id = c.id
LEFT JOIN public.campaign_cohorts cc ON cc.campaign_id = c.id
GROUP BY c.id, c.name, c.status, c.health_score, c.objective, c.start_date, c.end_date;

-- View for cohort journey distribution
CREATE OR REPLACE VIEW public.cohort_journey_summary AS
SELECT 
  c.id,
  c.name,
  c.workspace_id,
  COALESCE((c.journey_distribution->>'unaware')::NUMERIC, 0) as pct_unaware,
  COALESCE((c.journey_distribution->>'problem_aware')::NUMERIC, 0) as pct_problem_aware,
  COALESCE((c.journey_distribution->>'solution_aware')::NUMERIC, 0) as pct_solution_aware,
  COALESCE((c.journey_distribution->>'product_aware')::NUMERIC, 0) as pct_product_aware,
  COALESCE((c.journey_distribution->>'most_aware')::NUMERIC, 0) as pct_most_aware,
  c.health_score
FROM public.cohorts c;

-- ============================================
-- 9. GRANT PERMISSIONS ON NEW OBJECTS
-- ============================================

-- Grant permissions on reference tables
GRANT SELECT ON public.journey_stages TO authenticated;
GRANT SELECT ON public.channel_roles TO authenticated;

-- Grant permissions on views
GRANT SELECT ON public.campaign_health_summary TO authenticated;
GRANT SELECT ON public.cohort_journey_summary TO authenticated;

-- ============================================
-- MIGRATION COMPLETE
-- ============================================

-- Verification queries (run these to verify the migration)
-- SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'cohorts' AND column_name LIKE '%trigger%';
-- SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'moves' AND column_name = 'campaign_id';
-- SELECT * FROM public.journey_stages;
-- SELECT * FROM public.channel_roles;
