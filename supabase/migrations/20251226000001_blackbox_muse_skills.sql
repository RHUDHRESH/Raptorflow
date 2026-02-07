-- RaptorFlow Complete Database Schema (v2.0) - Part 2: Blackbox & Experiments
-- Blackbox Industrial Engine and Experiment Management

-- =====================================
-- 5. BLACKBOX INDUSTRIAL ENGINE
-- =====================================

-- Blackbox Experiments (Hypothesis-driven)
CREATE TABLE IF NOT EXISTS blackbox_experiments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Core inputs
    goal TEXT NOT NULL CHECK (goal IN ('replies', 'leads', 'calls', 'clicks', 'sales', 'followers')),
    risk_level TEXT NOT NULL CHECK (risk_level IN ('safe', 'spicy', 'unreasonable')),
    channel TEXT NOT NULL CHECK (channel IN ('email', 'linkedin', 'twitter', 'instagram', 'tiktok', 'youtube', 'facebook', 'google_ads', 'website', 'blog', 'podcast', 'other')),

    -- Content
    title TEXT NOT NULL, -- 6-10 words
    bet TEXT NOT NULL, -- One sentence
    why TEXT, -- One sentence explanation
    principle TEXT CHECK (principle IN ('friction', 'identity', 'loss_aversion', 'social_proof', 'pattern_interrupt', 'commitment', 'pricing_psych')),

    -- Actionable experiment details
    hypothesis TEXT, -- "If we do X, then Y will happen"
    control TEXT, -- Current state / what we're testing against
    variant TEXT, -- The specific change we're making
    success_metric TEXT, -- What number to track
    sample_size TEXT, -- e.g., "500 emails", "1000 impressions"
    duration_days INTEGER DEFAULT 7,
    action_steps TEXT[] DEFAULT '{}',

    -- Execution details
    effort TEXT CHECK (effort IN ('10m', '30m', '2h')),
    time_to_signal TEXT CHECK (time_to_signal IN ('24h', '48h', '7d')),

    -- Skill stack
    skill_stack JSONB DEFAULT '{}',
    asset_plan JSONB DEFAULT '{}',
    asset_ids UUID[] DEFAULT '{}',

    -- Lifecycle
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'generated', 'launched', 'checked_in', 'expired')),
    created_at TIMESTAMPTZ DEFAULT now(),
    launched_at TIMESTAMPTZ,
    checkin_due_at TIMESTAMPTZ,
    checkin_remind_at TIMESTAMPTZ,
    checkin_expire_at TIMESTAMPTZ,

    -- Results
    self_report JSONB DEFAULT '{}',
    learning JSONB DEFAULT '{}',
    confidence NUMERIC CHECK (confidence >= 0 AND confidence <= 1)
);

-- Blackbox Telemetry (Performance tracking)
CREATE TABLE IF NOT EXISTS blackbox_telemetry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    experiment_id UUID REFERENCES blackbox_experiments(id) ON DELETE CASCADE,
    move_id UUID REFERENCES moves(id) ON DELETE CASCADE,

    agent_id TEXT NOT NULL,
    trace JSONB NOT NULL DEFAULT '{}',
    tokens INTEGER DEFAULT 0,
    latency_ms DOUBLE PRECISION DEFAULT 0.0,
    cost_estimate NUMERIC DEFAULT 0.0,

    timestamp TIMESTAMPTZ DEFAULT now()
);

-- Blackbox Outcomes (Results tracking)
CREATE TABLE IF NOT EXISTS blackbox_outcomes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    experiment_id UUID REFERENCES blackbox_experiments(id) ON DELETE SET NULL,
    move_id UUID REFERENCES moves(id) ON DELETE SET NULL,

    source TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    value NUMERIC NOT NULL,
    confidence DOUBLE PRECISION DEFAULT 1.0,

    timestamp TIMESTAMPTZ DEFAULT now()
);

-- Blackbox Learnings (Knowledge extraction)
CREATE TABLE IF NOT EXISTS blackbox_learnings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    content TEXT NOT NULL,
    learning_type TEXT NOT NULL CHECK (learning_type IN ('tactical', 'strategic', 'content')),
    source_ids UUID[] DEFAULT '{}',

    -- Vector embedding for similarity search
    embedding VECTOR(768),

    confidence NUMERIC DEFAULT 1.0,
    is_validated BOOLEAN DEFAULT FALSE,

    timestamp TIMESTAMPTZ DEFAULT now()
);

-- Agent Decision Audit
CREATE TABLE IF NOT EXISTS agent_decision_audit (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    agent_id TEXT NOT NULL,
    decision_type TEXT NOT NULL,
    input_state JSONB DEFAULT '{}',
    output_decision JSONB DEFAULT '{}',
    rationale TEXT,

    cost_estimate NUMERIC DEFAULT 0.0,
    accuracy_validated BOOLEAN DEFAULT FALSE,
    is_accurate BOOLEAN,
    feedback_notes TEXT,

    created_at TIMESTAMPTZ DEFAULT now()
);

-- =====================================
-- 6. MUSE MODULE (Asset Management)
-- =====================================

-- Muse Assets (Creative content generation)
CREATE TABLE IF NOT EXISTS muse_assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    content TEXT NOT NULL,
    asset_type TEXT CHECK (asset_type IN ('email', 'social_post', 'meme', 'text', 'image', 'video', 'document')),

    -- Generation metadata
    generation_prompt TEXT,
    generation_model TEXT,
    generation_tokens INTEGER,

    -- Asset metadata
    metadata JSONB DEFAULT '{}',
    tags TEXT[],

    -- Status & workflow
    status TEXT DEFAULT 'draft' CHECK (status IN ('generating', 'ready', 'blocked', 'archived')),
    quality_score NUMERIC CHECK (quality_score >= 0 AND quality_score <= 1),

    -- Usage tracking
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMPTZ,

    -- Vector embedding for search
    embedding VECTOR(768),

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Muse Asset Versions (Iteration tracking)
CREATE TABLE IF NOT EXISTS muse_asset_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id UUID NOT NULL REFERENCES muse_assets(id) ON DELETE CASCADE,

    version_number INTEGER NOT NULL,
    content TEXT NOT NULL,

    -- Version metadata
    change_description TEXT,
    generation_prompt TEXT,
    metadata JSONB DEFAULT '{}',

    created_at TIMESTAMPTZ DEFAULT now(),

    UNIQUE(asset_id, version_number)
);

-- Muse Collections (Asset organization)
CREATE TABLE IF NOT EXISTS muse_collections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    name TEXT NOT NULL,
    description TEXT,
    collection_type TEXT CHECK (collection_type IN ('campaign', 'experiment', 'template', 'favorite')),

    -- Collection metadata
    asset_ids UUID[] DEFAULT '{}',
    tags TEXT[],
    is_public BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- =====================================
-- 7. SKILLS & TOOLS REGISTRY
-- =====================================

-- Skills (AI capabilities)
CREATE TABLE IF NOT EXISTS skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    instructions TEXT NOT NULL,

    type TEXT NOT NULL CHECK (type IN ('system', 'custom')),
    category TEXT, -- hook, structure, tone, cta, proof, edit_polish

    -- Skill metadata
    input_schema JSONB,
    output_schema JSONB,
    examples JSONB DEFAULT '[]',

    -- Performance tracking
    usage_count INTEGER DEFAULT 0,
    success_rate NUMERIC DEFAULT 0.0,

    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Skill Registry (Available skills for experiments)
CREATE TABLE IF NOT EXISTS skill_registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT UNIQUE NOT NULL,
    description TEXT,

    input_schema JSONB,
    output_schema JSONB,

    -- Registry metadata
    category TEXT,
    tags TEXT[],
    version TEXT DEFAULT '1.0',

    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Skill Presets (Curated skill combinations)
CREATE TABLE IF NOT EXISTS skill_presets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,

    intent TEXT CHECK (intent IN ('replies', 'leads', 'calls', 'clicks', 'sales', 'followers')),
    channel TEXT CHECK (channel IN ('email', 'linkedin', 'twitter', 'instagram', 'tiktok', 'youtube', 'facebook', 'google_ads', 'website', 'blog', 'podcast', 'other')),

    skill_stack JSONB DEFAULT '{}',

    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now()
);
