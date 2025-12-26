-- RaptorFlow Complete Database Schema (v2.0) - Part 1: Core Infrastructure
-- Comprehensive rebuild covering all application modules
-- Target: Production-ready with full workspace isolation

-- =====================================
-- 1. EXTENSIONS & CONFIGURATION
-- =====================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- =====================================
-- 2. WORKSPACE & TENANT MANAGEMENT
-- =====================================

-- Workspaces (Multi-tenant core)
CREATE TABLE IF NOT EXISTS workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    description TEXT,
    logo_url TEXT,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Workspace members with role-based access
CREATE TABLE IF NOT EXISTS workspace_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    role TEXT NOT NULL DEFAULT 'member' CHECK (role IN ('owner', 'admin', 'member', 'viewer')),
    permissions JSONB DEFAULT '{}',
    invited_by UUID REFERENCES auth.users(id),
    joined_at TIMESTAMPTZ DEFAULT now(),
    last_active_at TIMESTAMPTZ,
    UNIQUE(workspace_id, user_id)
);

-- =====================================
-- 3. FOUNDATION MODULE
-- =====================================

-- Brand Kit (Foundation branding)
CREATE TABLE IF NOT EXISTS foundation_brand_kits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,

    -- Visual identity
    logo_url TEXT,
    logo_storage_path TEXT,
    primary_color TEXT,
    secondary_color TEXT,
    accent_color TEXT,
    neutral_colors TEXT[], -- Array of neutral color hexes

    -- Typography
    typography_config JSONB DEFAULT '{}',

    -- Brand guidelines
    voice_tone TEXT,
    messaging_guidelines TEXT,
    competitive_positioning TEXT,

    -- Asset storage paths
    asset_folder_path TEXT,

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Positioning statements
CREATE TABLE IF NOT EXISTS foundation_positioning (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_kit_id UUID NOT NULL REFERENCES foundation_brand_kits(id) ON DELETE CASCADE,

    uvp TEXT NOT NULL,
    target_market TEXT NOT NULL,
    competitive_advantage TEXT,
    elevator_pitch TEXT,
    tagline TEXT,

    -- ICP definitions
    ideal_customer_profile JSONB DEFAULT '{}',
    pain_points TEXT[],
    gain_creators TEXT[],

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Voice & Tone variations
CREATE TABLE IF NOT EXISTS foundation_voice_tones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_kit_id UUID NOT NULL REFERENCES foundation_brand_kits(id) ON DELETE CASCADE,

    tone_name TEXT NOT NULL,
    description TEXT,
    keywords TEXT[],
    examples JSONB DEFAULT '[]'::jsonb,

    -- Usage guidelines
    use_cases TEXT[],
    avoid_situations TEXT[],

    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Foundation state (progress tracking)
CREATE TABLE IF NOT EXISTS foundation_state (
    tenant_id UUID PRIMARY KEY REFERENCES workspaces(id) ON DELETE CASCADE,
    current_phase TEXT DEFAULT 'brand_kit',
    phase_progress JSONB DEFAULT '{}',
    completed_steps TEXT[] DEFAULT '{}',
    current_step TEXT,

    -- Phase-specific data
    brand_kit_id UUID REFERENCES foundation_brand_kits(id),
    positioning_id UUID REFERENCES foundation_positioning(id),

    updated_at TIMESTAMPTZ DEFAULT now()
);

-- =====================================
-- 4. CAMPAIGNS & MOVES (v2.0)
-- =====================================

-- Campaigns (Multi-phase war plans)
CREATE TABLE IF NOT EXISTS campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Basic info
    title TEXT NOT NULL,
    description TEXT,
    objective TEXT NOT NULL CHECK (objective IN ('acquire', 'convert', 'launch', 'proof', 'retain', 'reposition')),

    -- Strategy context
    strategy_version TEXT DEFAULT 'v1.0',
    strategy_context_id UUID, -- Links to strategy version

    -- Timeline & sequencing
    status TEXT DEFAULT 'planned' CHECK (status IN ('planned', 'active', 'paused', 'wrapup', 'archived')),
    start_date TIMESTAMPTZ,
    end_date TIMESTAMPTZ,
    duration_days INTEGER DEFAULT 90,

    -- KPI tree
    primary_kpi TEXT,
    kpi_targets JSONB DEFAULT '{}',
    kpi_current JSONB DEFAULT '{}',

    -- Campaign arc data
    arc_data JSONB DEFAULT '{}',
    sequencing_plan JSONB DEFAULT '{}',

    -- Budget & resources
    budget_allocated NUMERIC DEFAULT 0,
    budget_spent NUMERIC DEFAULT 0,

    -- Quality & audit
    quality_score NUMERIC CHECK (quality_score >= 0 AND quality_score <= 1),
    audit_data JSONB DEFAULT '{}',
    rag_status TEXT DEFAULT 'green' CHECK (rag_status IN ('green', 'amber', 'red')),

    -- Wrapup data
    wrapup_data JSONB DEFAULT '{}',

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Moves (Execution units)
CREATE TABLE IF NOT EXISTS moves (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    campaign_id UUID REFERENCES campaigns(id) ON DELETE CASCADE, -- Can be NULL for standalone moves

    -- Basic info
    title TEXT NOT NULL,
    description TEXT,
    goal TEXT NOT NULL CHECK (goal IN ('leads', 'calls', 'sales', 'proof', 'distribution', 'activation')),

    -- Channel & execution
    channel TEXT NOT NULL CHECK (channel IN ('linkedin', 'email', 'instagram', 'whatsapp', 'cold_dms', 'partnerships', 'twitter')),
    secondary_channel TEXT CHECK (secondary_channel IN ('linkedin', 'email', 'instagram', 'whatsapp', 'cold_dms', 'partnerships', 'twitter')),

    -- Timeline
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'queued', 'active', 'completed', 'abandoned')),
    priority INTEGER DEFAULT 3 CHECK (priority >= 1 AND priority <= 5),
    duration_days INTEGER DEFAULT 7,
    daily_effort_minutes INTEGER DEFAULT 30,

    start_date TIMESTAMPTZ,
    due_date TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,

    -- Experiment details (Blackbox integration)
    hypothesis TEXT,
    control TEXT,
    variant TEXT,
    success_metric TEXT,
    sample_size TEXT,
    action_steps TEXT[] DEFAULT '{}',

    -- Assets & resources
    asset_ids UUID[] DEFAULT '{}',
    checklist JSONB DEFAULT '{}',

    -- Agent & execution
    agent_id TEXT,
    thread_id TEXT,
    tool_requirements JSONB DEFAULT '{}',

    -- Results & learnings
    execution_result JSONB DEFAULT '{}',
    self_report JSONB DEFAULT '{}',
    refinement_data JSONB DEFAULT '{}',

    -- Override tracking
    override_reason TEXT CHECK (override_reason IN ('experiment', 'temporary_pivot', 'special_case')),
    override_data JSONB DEFAULT '{}',

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Campaign KPIs (Time-series tracking)
CREATE TABLE IF NOT EXISTS campaign_kpis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,

    metric_name TEXT NOT NULL,
    current_value NUMERIC DEFAULT 0,
    target_value NUMERIC,
    unit TEXT,

    -- Tracking
    last_updated TIMESTAMPTZ DEFAULT now(),
    trend_direction TEXT CHECK (trend_direction IN ('up', 'down', 'stable')),

    created_at TIMESTAMPTZ DEFAULT now()
);

-- Move approvals workflow
CREATE TABLE IF NOT EXISTS move_approvals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    move_id UUID NOT NULL REFERENCES moves(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id),

    status TEXT NOT NULL CHECK (status IN ('pending', 'approved', 'rejected')),
    comment TEXT,

    created_at TIMESTAMPTZ DEFAULT now()
);
