-- RaptorFlow Complete Database Schema (v2.0) - Part 5: Strategy, Matrix & Cohorts
-- Performance tracking and strategic management

-- =====================================
-- 14. COHORTS & AUDIENCE SEGMENTATION
-- =====================================

-- Cohorts (Audience segments)
CREATE TABLE IF NOT EXISTS cohorts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    name TEXT NOT NULL,
    description TEXT,
    cohort_type TEXT CHECK (cohort_type IN ('icp_based', 'behavioral', 'demographic', 'custom')),

    -- Segment criteria
    criteria JSONB DEFAULT '{}',
    filters JSONB DEFAULT '{}',

    -- Size and metrics
    estimated_size INTEGER,
    actual_size INTEGER,
    engagement_rate NUMERIC DEFAULT 0.0,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Cohort Members
CREATE TABLE IF NOT EXISTS cohort_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cohort_id UUID NOT NULL REFERENCES cohorts(id) ON DELETE CASCADE,

    member_identifier TEXT, -- Email, user_id, etc.
    member_data JSONB DEFAULT '{}',

    joined_at TIMESTAMPTZ DEFAULT now(),
    last_active_at TIMESTAMPTZ,

    UNIQUE(cohort_id, member_identifier)
);

-- =====================================
-- 15. STRATEGY & MATRIX MODULES
-- =====================================

-- Strategy Versions
CREATE TABLE IF NOT EXISTS strategy_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    name TEXT NOT NULL,
    version TEXT NOT NULL,
    description TEXT,

    -- Strategy content
    positioning JSONB DEFAULT '{}',
    messaging JSONB DEFAULT '{}',
    channels JSONB DEFAULT '{}',
    kpi_framework JSONB DEFAULT '{}',

    -- Status and adoption
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'archived')),
    adoption_rate NUMERIC DEFAULT 0.0,

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),

    UNIQUE(workspace_id, version)
);

-- Matrix Overview (Performance dashboard)
CREATE TABLE IF NOT EXISTS matrix_overview (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Period metrics
    period_start TIMESTAMPTZ NOT NULL,
    period_end TIMESTAMPTZ NOT NULL,

    -- Key metrics
    total_campaigns INTEGER DEFAULT 0,
    active_campaigns INTEGER DEFAULT 0,
    total_moves INTEGER DEFAULT 0,
    completed_moves INTEGER DEFAULT 0,

    -- Performance metrics
    total_leads INTEGER DEFAULT 0,
    total_conversions INTEGER DEFAULT 0,
    conversion_rate NUMERIC DEFAULT 0.0,
    total_revenue NUMERIC DEFAULT 0.0,

    -- Engagement metrics
    asset_generations INTEGER DEFAULT 0,
    experiment_launches INTEGER DEFAULT 0,

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Matrix KPI Tracking
CREATE TABLE IF NOT EXISTS matrix_kpis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    metric_name TEXT NOT NULL,
    metric_value NUMERIC NOT NULL,
    metric_unit TEXT,

    -- Time tracking
    period_start TIMESTAMPTZ NOT NULL,
    period_end TIMESTAMPTZ NOT NULL,

    -- Context
    campaign_id UUID REFERENCES campaigns(id),
    move_id UUID REFERENCES moves(id),

    created_at TIMESTAMPTZ DEFAULT now()
);

-- =====================================
-- 16. PAYMENTS & SUBSCRIPTIONS
-- =====================================

-- Subscriptions
CREATE TABLE IF NOT EXISTS subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Subscription details
    plan_type TEXT NOT NULL CHECK (plan_type IN ('starter', 'growth', 'enterprise')),
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'paused', 'cancelled', 'expired')),

    -- Billing
    billing_cycle TEXT DEFAULT 'monthly' CHECK (billing_cycle IN ('monthly', 'yearly')),
    price NUMERIC NOT NULL,
    currency TEXT DEFAULT 'USD',

    -- PhonePe integration
    phonepe_customer_id TEXT,
    phonepe_mandate_id TEXT,
    autopay_enabled BOOLEAN DEFAULT FALSE,

    -- Limits and usage
    limits JSONB DEFAULT '{}',
    current_usage JSONB DEFAULT '{}',

    -- Timeline
    trial_end_at TIMESTAMPTZ,
    current_period_end_at TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Invoices
CREATE TABLE IF NOT EXISTS invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subscription_id UUID NOT NULL REFERENCES subscriptions(id) ON DELETE CASCADE,

    -- Invoice details
    invoice_number TEXT UNIQUE NOT NULL,
    amount NUMERIC NOT NULL,
    currency TEXT DEFAULT 'USD',

    -- Status
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'paid', 'failed', 'cancelled', 'refunded')),

    -- PhonePe integration
    phonepe_transaction_id TEXT,
    payment_method TEXT,

    -- Dates
    due_date TIMESTAMPTZ NOT NULL,
    paid_at TIMESTAMPTZ,

    -- Line items
    line_items JSONB DEFAULT '[]',

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Payment Methods
CREATE TABLE IF NOT EXISTS payment_methods (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Payment method details
    method_type TEXT NOT NULL CHECK (method_type IN ('phonepe', 'card', 'bank_transfer')),
    provider TEXT NOT NULL,

    -- PhonePe specific
    phonepe_upi_id TEXT,
    phonepe_customer_id TEXT,

    -- Status
    is_default BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,

    -- Metadata
    metadata JSONB DEFAULT '{}',

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- =====================================
-- 17. USER PREFERENCES & SETTINGS
-- =====================================

-- User Preferences
CREATE TABLE IF NOT EXISTS user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- UI Preferences
    theme TEXT DEFAULT 'light' CHECK (theme IN ('light', 'dark', 'auto')),
    language TEXT DEFAULT 'en',
    timezone TEXT DEFAULT 'UTC',

    -- Notification preferences
    email_notifications BOOLEAN DEFAULT TRUE,
    push_notifications BOOLEAN DEFAULT TRUE,
    notification_types JSONB DEFAULT '{}',

    -- Feature preferences
    default_cohort_id UUID REFERENCES cohorts(id),
    default_workspace_id UUID REFERENCES workspaces(id),

    -- Custom preferences
    custom_preferences JSONB DEFAULT '{}',

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),

    UNIQUE(user_id, workspace_id)
);

-- Workspace Settings
CREATE TABLE IF NOT EXISTS workspace_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Feature flags
    features_enabled JSONB DEFAULT '{}',
    features_disabled JSONB DEFAULT '{}',

    -- Integration settings
    integrations JSONB DEFAULT '{}',
    api_keys JSONB DEFAULT '{}',

    -- Limits and quotas
    limits JSONB DEFAULT '{}',
    quotas JSONB DEFAULT '{}',

    -- Custom settings
    custom_settings JSONB DEFAULT '{}',

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);
