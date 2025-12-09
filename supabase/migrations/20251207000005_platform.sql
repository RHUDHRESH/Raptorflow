-- =====================================================
-- MIGRATION 005: Platform Core (Cohorts, Campaigns, Assets)
-- =====================================================

-- Cohorts
CREATE TABLE public.cohorts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
  created_by UUID NOT NULL REFERENCES auth.users(id),
  name VARCHAR(255) NOT NULL,
  description TEXT,
  rules JSONB NOT NULL DEFAULT '[]',
  member_count INTEGER DEFAULT 0,
  is_active BOOLEAN DEFAULT true,
  deleted_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Cohort memberships
CREATE TABLE public.cohort_memberships (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  cohort_id UUID NOT NULL REFERENCES public.cohorts(id) ON DELETE CASCADE,
  member_type VARCHAR(50) NOT NULL CHECK (member_type IN ('user', 'lead', 'contact')),
  member_id TEXT NOT NULL,
  added_via VARCHAR(50) DEFAULT 'rule' CHECK (added_via IN ('rule', 'manual', 'import')),
  added_at TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT unique_cohort_member UNIQUE (cohort_id, member_type, member_id)
);

-- Campaigns
CREATE TABLE public.campaigns (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
  created_by UUID NOT NULL REFERENCES auth.users(id),
  name VARCHAR(255) NOT NULL,
  description TEXT,
  cohort_ids UUID[] DEFAULT '{}',
  start_date DATE,
  end_date DATE,
  status campaign_status DEFAULT 'draft',
  config JSONB DEFAULT '{}',
  deleted_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Assets / Files
CREATE TABLE public.assets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
  uploaded_by UUID NOT NULL REFERENCES auth.users(id),
  filename VARCHAR(500) NOT NULL,
  original_filename VARCHAR(500) NOT NULL,
  file_path TEXT NOT NULL,
  file_size BIGINT NOT NULL,
  mime_type VARCHAR(200) NOT NULL,
  bucket_name VARCHAR(200) NOT NULL,
  entity_type VARCHAR(100),
  entity_id UUID,
  deleted_at TIMESTAMPTZ,
  deleted_by UUID,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Storage quotas
CREATE TABLE public.storage_quotas (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE UNIQUE,
  total_quota_bytes BIGINT NOT NULL DEFAULT 5368709120,
  used_bytes BIGINT DEFAULT 0,
  last_calculated_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_cohorts_org ON public.cohorts(organization_id);
CREATE INDEX idx_cohorts_active ON public.cohorts(organization_id) WHERE is_active = true AND deleted_at IS NULL;
CREATE INDEX idx_cohort_members_cohort ON public.cohort_memberships(cohort_id);
CREATE INDEX idx_campaigns_org ON public.campaigns(organization_id);
CREATE INDEX idx_campaigns_status ON public.campaigns(status);
CREATE INDEX idx_campaigns_active ON public.campaigns(organization_id, status) WHERE deleted_at IS NULL;
CREATE INDEX idx_assets_org ON public.assets(organization_id);
CREATE INDEX idx_assets_entity ON public.assets(entity_type, entity_id);
