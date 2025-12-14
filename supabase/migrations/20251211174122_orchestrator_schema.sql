-- =====================================================
-- MIGRATION: Orchestrator Schema for Muse AI Agents
-- Adds brand_profiles, projects, and orchestrator_jobs tables
-- =====================================================

-- Brand profiles table
CREATE TABLE public.brand_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
  created_by UUID NOT NULL REFERENCES auth.users(id),

  -- Brand identity
  brand_name VARCHAR(255) NOT NULL,
  tagline VARCHAR(500),
  description TEXT,

  -- Brand attributes
  industry VARCHAR(100),
  target_audience TEXT,
  brand_values TEXT[],
  brand_personality JSONB DEFAULT '{}',
  brand_voice_tones TEXT[],

  -- Visual identity
  primary_colors JSONB DEFAULT '[]',
  secondary_colors JSONB DEFAULT '[]',
  brand_fonts JSONB DEFAULT '{}',
  logo_description TEXT,

  -- Content preferences
  content_themes TEXT[],
  communication_style VARCHAR(50),
  key_messaging TEXT,

  -- Social media handles (optional)
  social_handles JSONB DEFAULT '{}',

  -- Metadata
  is_active BOOLEAN DEFAULT true,
  version INTEGER DEFAULT 1,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Projects table (groups related assets/requests)
CREATE TABLE public.projects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
  brand_profile_id UUID REFERENCES public.brand_profiles(id) ON DELETE SET NULL,
  created_by UUID NOT NULL REFERENCES auth.users(id),

  -- Project details
  name VARCHAR(255) NOT NULL,
  description TEXT,
  project_type VARCHAR(50) DEFAULT 'muse' CHECK (project_type IN ('muse', 'campaign', 'content', 'other')),

  -- Status and workflow
  status VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'completed', 'archived')),
  priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),

  -- Settings
  settings JSONB DEFAULT '{}',
  tags TEXT[],

  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Orchestrator jobs table (tracks agent executions)
CREATE TABLE public.orchestrator_jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
  project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
  brand_profile_id UUID REFERENCES public.brand_profiles(id) ON DELETE SET NULL,
  created_by UUID NOT NULL REFERENCES auth.users(id),

  -- Job specification
  job_type VARCHAR(100) NOT NULL, -- e.g., 'generate_brand_script', 'social_media_ideas'
  agent_name VARCHAR(100) NOT NULL, -- e.g., 'BrandScript', 'SocialMediaIdeas'
  status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'queued', 'running', 'completed', 'failed', 'cancelled')),

  -- Input parameters
  input_params JSONB DEFAULT '{}',
  context_snapshot JSONB DEFAULT '{}', -- brand profile + project context at time of request

  -- Execution details
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  duration_ms INTEGER,
  attempt_count INTEGER DEFAULT 0,
  max_attempts INTEGER DEFAULT 3,

  -- Results and provenance
  output JSONB,
  provenance JSONB DEFAULT '{}', -- {model, prompt_version, tokens, cost}

  -- Error handling
  error_message TEXT,
  error_details JSONB,

  -- Metadata
  priority INTEGER DEFAULT 0,
  tags TEXT[],
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add indexes for performance
CREATE INDEX idx_brand_profiles_org ON public.brand_profiles(organization_id);
CREATE INDEX idx_brand_profiles_active ON public.brand_profiles(organization_id) WHERE is_active = true;

CREATE INDEX idx_projects_org ON public.projects(organization_id);
CREATE INDEX idx_projects_brand ON public.projects(brand_profile_id);
CREATE INDEX idx_projects_status ON public.projects(status);

CREATE INDEX idx_orchestrator_jobs_org ON public.orchestrator_jobs(organization_id);
CREATE INDEX idx_orchestrator_jobs_project ON public.orchestrator_jobs(project_id);
CREATE INDEX idx_orchestrator_jobs_brand ON public.orchestrator_jobs(brand_profile_id);
CREATE INDEX idx_orchestrator_jobs_status ON public.orchestrator_jobs(status);
CREATE INDEX idx_orchestrator_jobs_type ON public.orchestrator_jobs(job_type);
CREATE INDEX idx_orchestrator_jobs_created ON public.orchestrator_jobs(created_at DESC);

-- Update triggers for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_brand_profiles_updated_at
    BEFORE UPDATE ON public.brand_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at
    BEFORE UPDATE ON public.projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_orchestrator_jobs_updated_at
    BEFORE UPDATE ON public.orchestrator_jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

