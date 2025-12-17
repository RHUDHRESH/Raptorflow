-- =====================================================
-- MIGRATION: Campaign Orchestration v2
-- Campaigns become real orchestration layer (objective + KPI contract + constraints)
-- Adds move linking + move slots + campaign events (telemetry)
-- Also adds minimal Moves + Templates tables if missing (required for linking)
-- =====================================================

DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'campaign_status') THEN
    IF NOT EXISTS (
      SELECT 1
      FROM pg_enum e
      JOIN pg_type t ON t.oid = e.enumtypid
      WHERE t.typname = 'campaign_status'
        AND e.enumlabel = 'archived'
    ) THEN
      ALTER TYPE public.campaign_status ADD VALUE 'archived';
    END IF;
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'move_status') THEN
    CREATE TYPE public.move_status AS ENUM (
      'planned',
      'generating_assets',
      'ready',
      'running',
      'paused',
      'completed',
      'failed'
    );
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'campaign_move_link_status') THEN
    CREATE TYPE public.campaign_move_link_status AS ENUM (
      'planned',
      'ready',
      'running',
      'done',
      'blocked'
    );
  END IF;
END
$$;

-- -----------------------------------------------------
-- Minimal protocol + move template + moves tables
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS public.protocols (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  metadata JSONB DEFAULT '{}'::jsonb,
  is_active BOOLEAN DEFAULT true,
  display_order INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.move_templates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  slug TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  protocol_type TEXT,
  barrier_type TEXT,
  channels TEXT[] DEFAULT '{}'::text[],
  required_inputs JSONB DEFAULT '[]'::jsonb,
  task_template JSONB DEFAULT '[]'::jsonb,
  asset_requirements JSONB DEFAULT '[]'::jsonb,
  automation_hooks JSONB DEFAULT '{}'::jsonb,
  success_metrics JSONB DEFAULT '[]'::jsonb,
  base_impact_score INTEGER DEFAULT 0,
  base_effort_score INTEGER DEFAULT 0,
  tags TEXT[] DEFAULT '{}'::text[],
  is_active BOOLEAN DEFAULT true,
  display_order INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.moves (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
  created_by UUID NOT NULL REFERENCES auth.users(id),

  campaign_id UUID REFERENCES public.campaigns(id) ON DELETE SET NULL,
  template_id UUID REFERENCES public.move_templates(id) ON DELETE SET NULL,

  name TEXT NOT NULL,
  description TEXT,

  protocol_type TEXT,
  channels TEXT[] DEFAULT '{}'::text[],

  status public.move_status NOT NULL DEFAULT 'planned',
  progress_percentage INTEGER NOT NULL DEFAULT 0,

  planned_start DATE,
  planned_end DATE,
  actual_start TIMESTAMPTZ,
  actual_end TIMESTAMPTZ,

  tasks JSONB DEFAULT '[]'::jsonb,
  kpis JSONB DEFAULT '{}'::jsonb,
  tracking_json JSONB DEFAULT '{}'::jsonb,
  metadata JSONB DEFAULT '{}'::jsonb,

  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_moves_org ON public.moves(organization_id);
CREATE INDEX IF NOT EXISTS idx_moves_campaign ON public.moves(campaign_id);
CREATE INDEX IF NOT EXISTS idx_moves_status ON public.moves(status);

-- -----------------------------------------------------
-- Upgrade campaigns table into orchestration model
-- -----------------------------------------------------

ALTER TABLE public.campaigns
  ADD COLUMN IF NOT EXISTS objective_text TEXT,
  ADD COLUMN IF NOT EXISTS primary_kpi_type TEXT,
  ADD COLUMN IF NOT EXISTS primary_kpi_baseline NUMERIC,
  ADD COLUMN IF NOT EXISTS primary_kpi_target NUMERIC,
  ADD COLUMN IF NOT EXISTS primary_kpi_window_start DATE,
  ADD COLUMN IF NOT EXISTS primary_kpi_window_end DATE,
  ADD COLUMN IF NOT EXISTS budget_amount NUMERIC,
  ADD COLUMN IF NOT EXISTS strategy_version_id UUID,
  ADD COLUMN IF NOT EXISTS primary_cohort_id UUID REFERENCES public.cohorts(id) ON DELETE SET NULL,
  ADD COLUMN IF NOT EXISTS secondary_cohort_ids UUID[] DEFAULT '{}'::uuid[],
  ADD COLUMN IF NOT EXISTS stage_model TEXT,
  ADD COLUMN IF NOT EXISTS stages_json JSONB DEFAULT '[]'::jsonb,
  ADD COLUMN IF NOT EXISTS channels_json JSONB DEFAULT '[]'::jsonb,
  ADD COLUMN IF NOT EXISTS measurement_json JSONB DEFAULT '{}'::jsonb,
  ADD COLUMN IF NOT EXISTS execution_capacity_json JSONB DEFAULT '{}'::jsonb,
  ADD COLUMN IF NOT EXISTS execution_override BOOLEAN DEFAULT false,
  ADD COLUMN IF NOT EXISTS health_score INTEGER,
  ADD COLUMN IF NOT EXISTS health_details JSONB DEFAULT '{}'::jsonb,
  ADD COLUMN IF NOT EXISTS last_preflight_at TIMESTAMPTZ;

CREATE INDEX IF NOT EXISTS idx_campaigns_org_window ON public.campaigns(organization_id, start_date, end_date);

-- -----------------------------------------------------
-- Linking table: campaigns <-> moves (ordering + stage)
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS public.campaign_move_links (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
  created_by UUID NOT NULL REFERENCES auth.users(id),

  campaign_id UUID NOT NULL REFERENCES public.campaigns(id) ON DELETE CASCADE,
  move_id UUID NOT NULL REFERENCES public.moves(id) ON DELETE CASCADE,

  slot_index INTEGER NOT NULL DEFAULT 0,
  stage_key TEXT,
  week_start DATE,
  week_end DATE,

  status public.campaign_move_link_status NOT NULL DEFAULT 'planned',

  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),

  CONSTRAINT unique_campaign_move UNIQUE (campaign_id, move_id)
);

CREATE INDEX IF NOT EXISTS idx_cml_campaign ON public.campaign_move_links(campaign_id, slot_index);
CREATE INDEX IF NOT EXISTS idx_cml_org ON public.campaign_move_links(organization_id);
CREATE INDEX IF NOT EXISTS idx_cml_move ON public.campaign_move_links(move_id);

-- -----------------------------------------------------
-- Move slots: planned slots before a move exists
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS public.campaign_move_slots (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
  created_by UUID NOT NULL REFERENCES auth.users(id),

  campaign_id UUID NOT NULL REFERENCES public.campaigns(id) ON DELETE CASCADE,
  slot_index INTEGER NOT NULL,
  stage_key TEXT,
  outcome_text TEXT,

  recommended_move_template_id UUID REFERENCES public.move_templates(id) ON DELETE SET NULL,
  created_move_id UUID REFERENCES public.moves(id) ON DELETE SET NULL,

  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cms_campaign ON public.campaign_move_slots(campaign_id, slot_index);
CREATE INDEX IF NOT EXISTS idx_cms_org ON public.campaign_move_slots(organization_id);

-- -----------------------------------------------------
-- Campaign events: telemetry boundary (Matrix/Lab feed later)
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS public.campaign_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
  user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,

  campaign_id UUID REFERENCES public.campaigns(id) ON DELETE CASCADE,
  move_id UUID REFERENCES public.moves(id) ON DELETE SET NULL,

  event_name TEXT NOT NULL,
  properties JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_campaign_events_org_time ON public.campaign_events(organization_id, occurred_at DESC);
CREATE INDEX IF NOT EXISTS idx_campaign_events_campaign_time ON public.campaign_events(campaign_id, occurred_at DESC);

-- -----------------------------------------------------
-- RLS policies
-- -----------------------------------------------------

ALTER TABLE public.protocols ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.move_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.moves ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.campaign_move_links ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.campaign_move_slots ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.campaign_events ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS protocols_select ON public.protocols;
CREATE POLICY protocols_select ON public.protocols
  FOR SELECT USING (is_active = true);

DROP POLICY IF EXISTS move_templates_select ON public.move_templates;
CREATE POLICY move_templates_select ON public.move_templates
  FOR SELECT USING (is_active = true);

DROP POLICY IF EXISTS moves_select ON public.moves;
CREATE POLICY moves_select ON public.moves
  FOR SELECT USING (public.is_org_member(organization_id));

DROP POLICY IF EXISTS moves_insert ON public.moves;
CREATE POLICY moves_insert ON public.moves
  FOR INSERT WITH CHECK (public.is_org_member(organization_id));

DROP POLICY IF EXISTS moves_update ON public.moves;
CREATE POLICY moves_update ON public.moves
  FOR UPDATE USING (public.is_org_member(organization_id));

DROP POLICY IF EXISTS moves_delete ON public.moves;
CREATE POLICY moves_delete ON public.moves
  FOR DELETE USING (public.is_org_admin(organization_id));

DROP POLICY IF EXISTS cml_select ON public.campaign_move_links;
CREATE POLICY cml_select ON public.campaign_move_links
  FOR SELECT USING (public.is_org_member(organization_id));

DROP POLICY IF EXISTS cml_insert ON public.campaign_move_links;
CREATE POLICY cml_insert ON public.campaign_move_links
  FOR INSERT WITH CHECK (public.is_org_member(organization_id));

DROP POLICY IF EXISTS cml_update ON public.campaign_move_links;
CREATE POLICY cml_update ON public.campaign_move_links
  FOR UPDATE USING (public.is_org_member(organization_id));

DROP POLICY IF EXISTS cml_delete ON public.campaign_move_links;
CREATE POLICY cml_delete ON public.campaign_move_links
  FOR DELETE USING (public.is_org_admin(organization_id));

DROP POLICY IF EXISTS cms_select ON public.campaign_move_slots;
CREATE POLICY cms_select ON public.campaign_move_slots
  FOR SELECT USING (public.is_org_member(organization_id));

DROP POLICY IF EXISTS cms_insert ON public.campaign_move_slots;
CREATE POLICY cms_insert ON public.campaign_move_slots
  FOR INSERT WITH CHECK (public.is_org_member(organization_id));

DROP POLICY IF EXISTS cms_update ON public.campaign_move_slots;
CREATE POLICY cms_update ON public.campaign_move_slots
  FOR UPDATE USING (public.is_org_member(organization_id));

DROP POLICY IF EXISTS cms_delete ON public.campaign_move_slots;
CREATE POLICY cms_delete ON public.campaign_move_slots
  FOR DELETE USING (public.is_org_admin(organization_id));

DROP POLICY IF EXISTS campaign_events_select ON public.campaign_events;
CREATE POLICY campaign_events_select ON public.campaign_events
  FOR SELECT USING (public.is_org_member(organization_id));

DROP POLICY IF EXISTS campaign_events_insert ON public.campaign_events;
CREATE POLICY campaign_events_insert ON public.campaign_events
  FOR INSERT WITH CHECK (public.is_org_member(organization_id));

-- updated_at triggers
DROP TRIGGER IF EXISTS trg_protocols_updated ON public.protocols;
CREATE TRIGGER trg_protocols_updated BEFORE UPDATE ON public.protocols
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

DROP TRIGGER IF EXISTS trg_move_templates_updated ON public.move_templates;
CREATE TRIGGER trg_move_templates_updated BEFORE UPDATE ON public.move_templates
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

DROP TRIGGER IF EXISTS trg_moves_updated ON public.moves;
CREATE TRIGGER trg_moves_updated BEFORE UPDATE ON public.moves
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

DROP TRIGGER IF EXISTS trg_cml_updated ON public.campaign_move_links;
CREATE TRIGGER trg_cml_updated BEFORE UPDATE ON public.campaign_move_links
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

DROP TRIGGER IF EXISTS trg_cms_updated ON public.campaign_move_slots;
CREATE TRIGGER trg_cms_updated BEFORE UPDATE ON public.campaign_move_slots
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();
