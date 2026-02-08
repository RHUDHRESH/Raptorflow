# DATABASE SCHEMA

> Complete Supabase PostgreSQL Schema with Multi-tenancy

---

## 1. SCHEMA OVERVIEW

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATABASE SCHEMA                                   │
│                                                                             │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐       │
│  │     USERS       │────▶│   WORKSPACES    │────▶│   FOUNDATIONS   │       │
│  └─────────────────┘     └─────────────────┘     └─────────────────┘       │
│                                   │                       │                 │
│                    ┌──────────────┼──────────────┐       │                 │
│                    │              │              │       │                 │
│                    ▼              ▼              ▼       ▼                 │
│              ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│              │  MOVES   │  │CAMPAIGNS │  │   ICP    │  │  MUSE    │       │
│              │          │  │          │  │ PROFILES │  │  ASSETS  │       │
│              └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│                    │              │                                        │
│                    ▼              ▼                                        │
│              ┌──────────┐  ┌──────────┐                                   │
│              │  TASKS   │  │ MOVE_    │                                   │
│              │          │  │ CAMPAIGNS│                                   │
│              └──────────┘  └──────────┘                                   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    AGENT & MEMORY TABLES                            │   │
│  │  agent_executions | memory_vectors | graph_entities | episodic      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    BILLING TABLES                                   │   │
│  │  subscriptions | payments | invoices | usage_records                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. CORE TABLES

### 2.1 Users

```sql
-- Users table (extends Supabase auth.users)
CREATE TABLE public.users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    full_name TEXT,
    avatar_url TEXT,

    -- Subscription
    subscription_tier TEXT DEFAULT 'free' CHECK (
        subscription_tier IN ('free', 'starter', 'growth', 'enterprise')
    ),

    -- Budget
    budget_limit_monthly DECIMAL(10,4) DEFAULT 1.00,

    -- Onboarding
    onboarding_completed_at TIMESTAMPTZ,

    -- Preferences
    preferences JSONB DEFAULT '{}',

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Trigger to update updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Auto-create user profile on signup
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.users (id, email)
    VALUES (NEW.id, NEW.email);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION handle_new_user();
```

### 2.2 Workspaces

```sql
-- Workspaces (multi-tenant isolation)
CREATE TABLE workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    name TEXT NOT NULL,
    slug TEXT UNIQUE,

    -- Settings
    settings JSONB DEFAULT '{
        "timezone": "Asia/Kolkata",
        "currency": "INR",
        "language": "en"
    }',

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_workspaces_user ON workspaces(user_id);
CREATE INDEX idx_workspaces_slug ON workspaces(slug);

CREATE TRIGGER workspaces_updated_at
    BEFORE UPDATE ON workspaces
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Auto-create workspace for new user
CREATE OR REPLACE FUNCTION handle_new_user_workspace()
RETURNS TRIGGER AS $$
DECLARE
    workspace_uuid UUID;
BEGIN
    workspace_uuid := gen_random_uuid();

    INSERT INTO workspaces (id, user_id, name, slug)
    VALUES (
        workspace_uuid,
        NEW.id,
        CONCAT(SPLIT_PART(NEW.email, '@', 1), '''s Workspace'),
        CONCAT('ws-', LEFT(workspace_uuid::TEXT, 8))
    );

    -- Also create foundation
    INSERT INTO foundations (workspace_id)
    VALUES (workspace_uuid);

    -- And onboarding session
    INSERT INTO onboarding_sessions (workspace_id, current_step)
    VALUES (workspace_uuid, 1);

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_user_created_workspace
    AFTER INSERT ON users
    FOR EACH ROW
    EXECUTE FUNCTION handle_new_user_workspace();
```

### 2.3 Foundations

```sql
-- Foundation (business context from onboarding)
CREATE TABLE foundations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Company Info
    company_name TEXT,
    industry TEXT,
    company_stage TEXT CHECK (
        company_stage IN ('idea', 'mvp', 'growth', 'scale', 'enterprise')
    ),
    website_url TEXT,

    -- Truth Sheet (extracted facts)
    truth_sheet JSONB DEFAULT '{}',

    -- Market Research Results
    market_research JSONB DEFAULT '{
        "customer_insights": [],
        "competitor_analysis": [],
        "market_trends": []
    }',

    -- Competitors
    competitors JSONB DEFAULT '[]',

    -- Positioning
    positioning JSONB DEFAULT '{
        "category": null,
        "positioning_statement": null,
        "usps": [],
        "differentiators": []
    }',

    -- Brand Voice
    brand_voice TEXT DEFAULT 'professional',
    brand_voice_examples JSONB DEFAULT '[]',

    -- Messaging
    messaging_guardrails JSONB DEFAULT '[]',
    soundbite_library JSONB DEFAULT '{}',
    message_hierarchy JSONB DEFAULT '{}',

    -- AI Context (compressed summary for agents)
    summary TEXT,
    summary_embedding vector(384),  -- For semantic search

    -- Status
    onboarding_completed BOOLEAN DEFAULT FALSE,
    last_updated_by TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(workspace_id)
);

CREATE INDEX idx_foundations_workspace ON foundations(workspace_id);
CREATE INDEX idx_foundations_embedding ON foundations
    USING ivfflat (summary_embedding vector_cosine_ops) WITH (lists = 100);
```

### 2.4 ICP Profiles

```sql
-- ICP Profiles (Ideal Customer Profiles)
CREATE TABLE icp_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Basic Info
    name TEXT NOT NULL,  -- "Scaling SaaS Founder at $1M-$5M ARR"
    tagline TEXT,
    code TEXT,  -- "ICP-001"

    -- Status
    is_primary BOOLEAN DEFAULT FALSE,
    is_secondary BOOLEAN DEFAULT FALSE,

    -- Demographics
    demographics JSONB DEFAULT '{
        "age_range": null,
        "income_range": null,
        "location": [],
        "role": null,
        "company_size": null,
        "industry": []
    }',

    -- Psychographics
    psychographics JSONB DEFAULT '{
        "beliefs": [],
        "identity": null,
        "becoming": null,
        "fears": [],
        "values": []
    }',

    -- Behaviors
    behaviors JSONB DEFAULT '{
        "hangouts": [],
        "consumption": [],
        "follows": [],
        "language_patterns": [],
        "buying_triggers": [],
        "objections": []
    }',

    -- Market Sophistication (Eugene Schwartz stages)
    market_sophistication JSONB DEFAULT '{
        "stage": 3,
        "stage_name": "Solution Aware",
        "reasoning": null
    }',

    -- Fit Scores (0-100)
    scores JSONB DEFAULT '{
        "pain_intensity": 0,
        "willingness_to_pay": 0,
        "accessibility": 0,
        "product_fit": 0
    }',

    -- AI Context
    summary TEXT,
    summary_embedding vector(384),

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_icp_profiles_workspace ON icp_profiles(workspace_id);
CREATE INDEX idx_icp_profiles_primary ON icp_profiles(workspace_id, is_primary);
CREATE INDEX idx_icp_profiles_embedding ON icp_profiles
    USING ivfflat (summary_embedding vector_cosine_ops) WITH (lists = 100);

-- Ensure only one primary ICP per workspace
CREATE UNIQUE INDEX idx_icp_profiles_unique_primary
    ON icp_profiles(workspace_id) WHERE is_primary = TRUE;
```

---

## 3. PRODUCT TABLES

### 3.1 Moves

```sql
-- Moves (marketing execution plans)
CREATE TABLE moves (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    campaign_id UUID REFERENCES campaigns(id) ON DELETE SET NULL,

    -- Basic Info
    name TEXT NOT NULL,
    category TEXT NOT NULL CHECK (
        category IN ('ignite', 'capture', 'authority', 'repair', 'rally')
    ),
    status TEXT DEFAULT 'draft' CHECK (
        status IN ('draft', 'scheduled', 'active', 'paused', 'completed', 'cancelled')
    ),

    -- Goal & Context
    goal TEXT,
    context TEXT,  -- User-provided context

    -- Targeting
    target_icp_id UUID REFERENCES icp_profiles(id) ON DELETE SET NULL,
    channels TEXT[] DEFAULT '{}',

    -- Duration
    duration_days INT DEFAULT 7,
    start_date DATE,
    end_date DATE,

    -- Execution Plan (generated by AI)
    execution JSONB DEFAULT '[]',  -- Array of ExecutionDay

    -- Progress Tracking
    progress INT DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    current_day INT DEFAULT 0,

    -- Source
    source TEXT DEFAULT 'manual' CHECK (
        source IN ('manual', 'blackbox', 'campaign', 'daily_wins')
    ),
    source_id UUID,  -- Reference to blackbox_strategy or campaign

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_moves_workspace ON moves(workspace_id);
CREATE INDEX idx_moves_campaign ON moves(campaign_id);
CREATE INDEX idx_moves_status ON moves(workspace_id, status);
CREATE INDEX idx_moves_dates ON moves(workspace_id, start_date, end_date);
```

### 3.2 Move Tasks

```sql
-- Individual tasks within moves
CREATE TABLE move_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    move_id UUID NOT NULL REFERENCES moves(id) ON DELETE CASCADE,
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Task Info
    title TEXT NOT NULL,
    description TEXT,
    type TEXT CHECK (type IN ('pillar', 'story', 'engagement', 'outreach', 'admin')),

    -- Scheduling
    day_number INT NOT NULL,
    scheduled_date DATE,

    -- Platform
    platform TEXT,

    -- Time
    estimated_minutes INT DEFAULT 30,
    actual_minutes INT,

    -- Priority
    priority TEXT DEFAULT 'should-do' CHECK (
        priority IN ('must-do', 'should-do', 'nice-to-have')
    ),

    -- Status
    status TEXT DEFAULT 'pending' CHECK (
        status IN ('pending', 'in_progress', 'completed', 'skipped')
    ),
    completed_at TIMESTAMPTZ,

    -- Deliverable
    deliverable TEXT,
    deliverable_url TEXT,

    -- Output (generated content)
    generated_content JSONB,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_move_tasks_move ON move_tasks(move_id);
CREATE INDEX idx_move_tasks_workspace ON move_tasks(workspace_id);
CREATE INDEX idx_move_tasks_date ON move_tasks(workspace_id, scheduled_date);
```

### 3.3 Campaigns

```sql
-- Campaigns (collections of moves)
CREATE TABLE campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Basic Info
    name TEXT NOT NULL,
    description TEXT,
    objective TEXT CHECK (
        objective IN (
            'market_entry', 'revenue_scaling', 'brand_pivot',
            'product_launch', 'awareness', 'lead_gen', 'retention'
        )
    ),

    -- Status
    status TEXT DEFAULT 'planning' CHECK (
        status IN ('planning', 'scheduled', 'active', 'paused', 'completed', 'cancelled')
    ),

    -- Goal
    goal TEXT,
    success_criteria JSONB DEFAULT '[]',

    -- Targeting
    target_icp_id UUID REFERENCES icp_profiles(id) ON DELETE SET NULL,
    channels TEXT[] DEFAULT '{}',

    -- Duration
    duration_days INT,
    intensity TEXT CHECK (intensity IN ('sprint', 'marathon')),
    start_date DATE,
    end_date DATE,

    -- Phases
    phases JSONB DEFAULT '[]',  -- Array of CampaignPhase

    -- Progress
    progress INT DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),

    -- Budget
    budget_inr DECIMAL(10,2),
    spent_inr DECIMAL(10,2) DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_campaigns_workspace ON campaigns(workspace_id);
CREATE INDEX idx_campaigns_status ON campaigns(workspace_id, status);
CREATE INDEX idx_campaigns_dates ON campaigns(workspace_id, start_date, end_date);
```

### 3.4 Muse Assets

```sql
-- Muse Assets (generated content)
CREATE TABLE muse_assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Basic Info
    title TEXT NOT NULL,
    type TEXT NOT NULL CHECK (
        type IN ('email', 'social', 'blog', 'ad', 'script', 'carousel', 'landing', 'other')
    ),

    -- Content
    content TEXT NOT NULL,
    content_html TEXT,  -- Formatted version

    -- Metadata
    tone TEXT,
    word_count INT,
    platform TEXT,
    tags TEXT[] DEFAULT '{}',

    -- Versioning
    version INT DEFAULT 1,
    parent_id UUID REFERENCES muse_assets(id) ON DELETE SET NULL,

    -- Context
    move_id UUID REFERENCES moves(id) ON DELETE SET NULL,
    campaign_id UUID REFERENCES campaigns(id) ON DELETE SET NULL,
    icp_id UUID REFERENCES icp_profiles(id) ON DELETE SET NULL,

    -- Source
    source TEXT DEFAULT 'muse' CHECK (source IN ('muse', 'template', 'import', 'move')),
    prompt_used TEXT,

    -- Status
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'approved', 'published', 'archived')),

    -- Feedback
    rating INT CHECK (rating >= 1 AND rating <= 5),
    feedback JSONB,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_muse_assets_workspace ON muse_assets(workspace_id);
CREATE INDEX idx_muse_assets_type ON muse_assets(workspace_id, type);
CREATE INDEX idx_muse_assets_move ON muse_assets(move_id);
```

### 3.5 BlackBox Strategies

```sql
-- BlackBox Strategies (high-risk plays)
CREATE TABLE blackbox_strategies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Basic Info
    name TEXT NOT NULL,
    focus_area TEXT NOT NULL CHECK (
        focus_area IN ('acquisition', 'retention', 'revenue', 'brand_equity', 'virality')
    ),
    outcome TEXT,

    -- Risk
    risk_level INT CHECK (risk_level >= 1 AND risk_level <= 10),
    risk_reasons TEXT[] DEFAULT '{}',

    -- Strategy Details
    phases JSONB DEFAULT '[]',  -- Hook, Pivot, Close
    execution_steps TEXT[] DEFAULT '{}',

    -- Analysis
    expected_upside TEXT,
    potential_downside TEXT,
    time_to_result TEXT,

    -- Status
    status TEXT DEFAULT 'generated' CHECK (
        status IN ('generated', 'reviewing', 'accepted', 'executing', 'completed', 'discarded')
    ),

    -- Linked Move (if converted)
    move_id UUID REFERENCES moves(id) ON DELETE SET NULL,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_blackbox_workspace ON blackbox_strategies(workspace_id);
CREATE INDEX idx_blackbox_focus ON blackbox_strategies(workspace_id, focus_area);
```

### 3.6 Daily Wins

```sql
-- Daily Wins (quick content ideas)
CREATE TABLE daily_wins (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Content
    topic TEXT NOT NULL,
    angle TEXT,
    hook TEXT NOT NULL,
    outline TEXT[] DEFAULT '{}',

    -- Platform
    platform TEXT,
    estimated_time TEXT,  -- e.g., "~10 min"

    -- Trend Source
    trend_source TEXT,
    trend_url TEXT,
    relevance_score DECIMAL(3,2),

    -- Status
    status TEXT DEFAULT 'generated' CHECK (
        status IN ('generated', 'saved', 'posted', 'skipped')
    ),
    posted_at TIMESTAMPTZ,
    posted_url TEXT,

    -- Generated content (if expanded)
    generated_content TEXT,
    muse_asset_id UUID REFERENCES muse_assets(id) ON DELETE SET NULL,

    -- Timestamps
    generated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_daily_wins_workspace ON daily_wins(workspace_id);
CREATE INDEX idx_daily_wins_date ON daily_wins(workspace_id, generated_at);
```

---

## 4. AGENT & MEMORY TABLES

### 4.1 Agent Executions

```sql
-- Agent execution logs
CREATE TABLE agent_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    session_id UUID,

    -- Request
    request_type TEXT NOT NULL,
    request_data JSONB,

    -- Routing
    routing_path TEXT[] DEFAULT '{}',
    agents_invoked TEXT[] DEFAULT '{}',
    skills_used TEXT[] DEFAULT '{}',
    tools_used TEXT[] DEFAULT '{}',

    -- Output
    output JSONB,
    success BOOLEAN,
    error TEXT,

    -- Quality
    quality_score INT,
    corrections_made INT DEFAULT 0,

    -- Cost
    tokens_input INT DEFAULT 0,
    tokens_output INT DEFAULT 0,
    total_cost DECIMAL(10,6) DEFAULT 0,

    -- Timing
    latency_ms INT,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX idx_agent_executions_workspace ON agent_executions(workspace_id);
CREATE INDEX idx_agent_executions_type ON agent_executions(workspace_id, request_type);
CREATE INDEX idx_agent_executions_date ON agent_executions(workspace_id, started_at);
```

### 4.2 Memory Vectors

```sql
-- Vector memory for semantic search
CREATE TABLE memory_vectors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Type
    memory_type TEXT NOT NULL CHECK (
        memory_type IN ('foundation', 'icp', 'move', 'campaign', 'research', 'conversation', 'feedback')
    ),

    -- Content
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',

    -- Embedding
    embedding vector(384) NOT NULL,

    -- Reference
    reference_id UUID,  -- ID of the source record
    reference_table TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_memory_vectors_workspace ON memory_vectors(workspace_id);
CREATE INDEX idx_memory_vectors_type ON memory_vectors(workspace_id, memory_type);
CREATE INDEX idx_memory_vectors_embedding ON memory_vectors
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

### 4.3 Graph Entities

```sql
-- Knowledge graph entities
CREATE TABLE graph_entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Entity
    entity_type TEXT NOT NULL CHECK (
        entity_type IN (
            'company', 'icp', 'competitor', 'channel',
            'pain_point', 'usp', 'feature', 'move', 'campaign', 'content'
        )
    ),
    name TEXT NOT NULL,
    properties JSONB DEFAULT '{}',

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_graph_entities_workspace ON graph_entities(workspace_id);
CREATE INDEX idx_graph_entities_type ON graph_entities(workspace_id, entity_type);
CREATE INDEX idx_graph_entities_name ON graph_entities(workspace_id, name);

-- Knowledge graph relationships
CREATE TABLE graph_relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Relationship
    source_id UUID NOT NULL REFERENCES graph_entities(id) ON DELETE CASCADE,
    target_id UUID NOT NULL REFERENCES graph_entities(id) ON DELETE CASCADE,
    relation_type TEXT NOT NULL,

    -- Properties
    properties JSONB DEFAULT '{}',
    weight DECIMAL(3,2) DEFAULT 1.0,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_graph_relationships_workspace ON graph_relationships(workspace_id);
CREATE INDEX idx_graph_relationships_source ON graph_relationships(source_id);
CREATE INDEX idx_graph_relationships_target ON graph_relationships(target_id);
CREATE INDEX idx_graph_relationships_type ON graph_relationships(workspace_id, relation_type);
```

### 4.4 Episodic Memory

```sql
-- Episodic memory (conversations, feedback)
CREATE TABLE episodic_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    session_id UUID,

    -- Episode
    episode_type TEXT NOT NULL CHECK (
        episode_type IN ('conversation', 'execution', 'feedback', 'preference')
    ),
    content JSONB NOT NULL,

    -- Importance (for decay calculation)
    importance DECIMAL(3,2) DEFAULT 1.0,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_episodic_memory_workspace ON episodic_memory(workspace_id);
CREATE INDEX idx_episodic_memory_session ON episodic_memory(workspace_id, session_id);
CREATE INDEX idx_episodic_memory_type ON episodic_memory(workspace_id, episode_type);
CREATE INDEX idx_episodic_memory_date ON episodic_memory(workspace_id, created_at);
```

### 4.5 Onboarding Sessions

```sql
-- Onboarding session state
CREATE TABLE onboarding_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Progress
    current_step INT DEFAULT 1,
    completed_steps INT[] DEFAULT '{}',

    -- Evidence Vault
    evidence JSONB DEFAULT '[]',

    -- Step Data (accumulated through onboarding)
    step_data JSONB DEFAULT '{}',

    -- Status
    status TEXT DEFAULT 'in_progress' CHECK (
        status IN ('in_progress', 'completed', 'abandoned')
    ),

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,

    UNIQUE(workspace_id)
);

CREATE INDEX idx_onboarding_sessions_workspace ON onboarding_sessions(workspace_id);
```

---

## 5. BILLING TABLES

### 5.1 Subscriptions

```sql
-- Subscriptions
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Plan
    plan TEXT NOT NULL CHECK (plan IN ('free', 'starter', 'growth', 'enterprise')),
    status TEXT DEFAULT 'active' CHECK (
        status IN ('active', 'cancelled', 'past_due', 'trialing')
    ),

    -- Pricing
    price_inr DECIMAL(10,2),
    billing_cycle TEXT CHECK (billing_cycle IN ('monthly', 'annual')),

    -- Period
    current_period_start TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,
    trial_end TIMESTAMPTZ,

    -- PhonePe
    phonepe_subscription_id TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    cancelled_at TIMESTAMPTZ,

    UNIQUE(user_id)
);

CREATE INDEX idx_subscriptions_user ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
```

### 5.2 Payments

```sql
-- Payment transactions
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subscription_id UUID REFERENCES subscriptions(id) ON DELETE SET NULL,

    -- Amount
    amount_inr DECIMAL(10,2) NOT NULL,
    gst_amount DECIMAL(10,2),
    total_amount DECIMAL(10,2) NOT NULL,

    -- Status
    status TEXT DEFAULT 'pending' CHECK (
        status IN ('pending', 'processing', 'completed', 'failed', 'refunded')
    ),

    -- PhonePe
    phonepe_transaction_id TEXT,
    phonepe_merchant_transaction_id TEXT UNIQUE,

    -- Payment Method
    payment_method TEXT,
    payment_instrument JSONB,  -- UPI, Card details (masked)

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,

    -- Metadata
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_payments_user ON payments(user_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_phonepe ON payments(phonepe_merchant_transaction_id);
```

### 5.3 Usage Records

```sql
-- Daily usage tracking
CREATE TABLE usage_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Date
    date DATE NOT NULL,

    -- Token Usage
    tokens_input INT DEFAULT 0,
    tokens_output INT DEFAULT 0,

    -- Cost
    cost_usd DECIMAL(10,6) DEFAULT 0,

    -- Breakdown by Agent
    agent_usage JSONB DEFAULT '{}',

    -- Request Count
    request_count INT DEFAULT 0,

    UNIQUE(user_id, date)
);

CREATE INDEX idx_usage_records_user ON usage_records(user_id);
CREATE INDEX idx_usage_records_date ON usage_records(user_id, date);
CREATE INDEX idx_usage_records_workspace ON usage_records(workspace_id, date);
```

---

## 6. APPROVAL & FEEDBACK TABLES

```sql
-- Human approval gates
CREATE TABLE approval_gates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    session_id UUID,

    -- Gate
    gate_type TEXT NOT NULL CHECK (
        gate_type IN ('content', 'strategy', 'payment', 'deletion', 'external_action')
    ),
    description TEXT,

    -- Pending Output
    pending_output JSONB NOT NULL,

    -- Risk
    risk_level TEXT CHECK (risk_level IN ('low', 'medium', 'high', 'critical')),
    risk_reasons TEXT[] DEFAULT '{}',

    -- Status
    status TEXT DEFAULT 'pending' CHECK (
        status IN ('pending', 'approved', 'rejected', 'modified', 'expired')
    ),

    -- Resolution
    resolved_by UUID REFERENCES users(id),
    modifications JSONB,
    rejection_reason TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ
);

CREATE INDEX idx_approval_gates_workspace ON approval_gates(workspace_id);
CREATE INDEX idx_approval_gates_status ON approval_gates(workspace_id, status);

-- User feedback
CREATE TABLE feedback_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Output Reference
    output_type TEXT NOT NULL,
    output_id UUID,

    -- Rating
    rating INT CHECK (rating >= 1 AND rating <= 5),
    feedback_type TEXT CHECK (
        feedback_type IN ('helpful', 'not_helpful', 'wrong', 'good', 'needs_improvement')
    ),

    -- Details
    what_was_good TEXT[] DEFAULT '{}',
    what_needs_improvement TEXT[] DEFAULT '{}',
    free_text TEXT,

    -- Preferences
    tone_preference TEXT,
    length_preference TEXT CHECK (length_preference IN ('shorter', 'just_right', 'longer')),
    detail_preference TEXT CHECK (detail_preference IN ('less_detail', 'just_right', 'more_detail')),

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_feedback_records_workspace ON feedback_records(workspace_id);
CREATE INDEX idx_feedback_records_output ON feedback_records(workspace_id, output_type, output_id);
```

---

## 7. RLS POLICIES (SUMMARY)

```sql
-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE workspaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE foundations ENABLE ROW LEVEL SECURITY;
ALTER TABLE icp_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE moves ENABLE ROW LEVEL SECURITY;
ALTER TABLE move_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE muse_assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE blackbox_strategies ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_wins ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE memory_vectors ENABLE ROW LEVEL SECURITY;
ALTER TABLE graph_entities ENABLE ROW LEVEL SECURITY;
ALTER TABLE graph_relationships ENABLE ROW LEVEL SECURITY;
ALTER TABLE episodic_memory ENABLE ROW LEVEL SECURITY;
ALTER TABLE onboarding_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE usage_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE approval_gates ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedback_records ENABLE ROW LEVEL SECURITY;

-- Helper function
CREATE OR REPLACE FUNCTION user_owns_workspace(workspace_uuid UUID)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM workspaces
        WHERE id = workspace_uuid AND user_id = auth.uid()
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Apply policies to all workspace-scoped tables
DO $$
DECLARE
    tbl TEXT;
BEGIN
    FOR tbl IN
        SELECT unnest(ARRAY[
            'foundations', 'icp_profiles', 'moves', 'move_tasks',
            'campaigns', 'muse_assets', 'blackbox_strategies', 'daily_wins',
            'agent_executions', 'memory_vectors', 'graph_entities', 'graph_relationships',
            'episodic_memory', 'onboarding_sessions', 'usage_records', 'approval_gates', 'feedback_records'
        ])
    LOOP
        EXECUTE format('
            CREATE POLICY "Workspace isolation for %I" ON %I
            FOR ALL USING (user_owns_workspace(workspace_id))
        ', tbl, tbl);
    END LOOP;
END $$;

-- User-specific policies
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can view own workspaces" ON workspaces
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own workspaces" ON workspaces
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view own subscription" ON subscriptions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can view own payments" ON payments
    FOR SELECT USING (auth.uid() = user_id);
```
