# DATABASE SCHEMA

> Supabase (PostgreSQL + pgvector)

---

## CORE TABLES

### users
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    subscription_tier TEXT DEFAULT 'free',
    budget_limit_monthly DECIMAL(10,4) DEFAULT 10.00,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### workspaces
```sql
CREATE TABLE workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    slug TEXT UNIQUE,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### foundations
```sql
CREATE TABLE foundations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Company Info
    company_name TEXT,
    industry TEXT,
    company_stage TEXT,

    -- Extracted Data
    truth_sheet JSONB DEFAULT '{}',
    market_research JSONB DEFAULT '{}',
    competitors JSONB DEFAULT '[]',
    positioning JSONB DEFAULT '{}',

    -- Generated Content
    brand_voice TEXT,
    messaging_guardrails JSONB DEFAULT '[]',
    soundbite_library JSONB DEFAULT '{}',
    message_hierarchy JSONB DEFAULT '{}',

    -- Summary for Agent Context
    summary TEXT,  -- Compressed context for agents
    summary_embedding vector(384),  -- For semantic search

    onboarding_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### icp_profiles
```sql
CREATE TABLE icp_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,

    name TEXT NOT NULL,  -- "Scaling SaaS Founder at $1M-$5M ARR"
    tagline TEXT,
    code TEXT,  -- "ICP-001"

    is_primary BOOLEAN DEFAULT FALSE,
    is_secondary BOOLEAN DEFAULT FALSE,

    demographics JSONB DEFAULT '{}',
    psychographics JSONB DEFAULT '{}',
    behaviors JSONB DEFAULT '{}',
    market_sophistication JSONB DEFAULT '{}',
    scores JSONB DEFAULT '{}',

    -- For agent context
    summary TEXT,
    summary_embedding vector(384),

    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## PRODUCT TABLES

### moves
```sql
CREATE TABLE moves (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    campaign_id UUID REFERENCES campaigns(id) ON DELETE SET NULL,

    name TEXT NOT NULL,
    category TEXT NOT NULL,  -- ignite, capture, authority, repair, rally
    status TEXT DEFAULT 'draft',  -- draft, active, paused, completed

    goal TEXT,
    target_icp_id UUID REFERENCES icp_profiles(id),
    channels TEXT[],
    duration_days INT,

    -- Execution Plan
    execution JSONB DEFAULT '[]',  -- Array of ExecutionDay

    -- Tracking
    progress INT DEFAULT 0,
    current_day INT DEFAULT 0,

    -- Meta
    source TEXT,  -- manual, blackbox, campaign
    context TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### campaigns
```sql
CREATE TABLE campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,

    name TEXT NOT NULL,
    objective TEXT,  -- Market Entry, Revenue Scaling, etc.
    status TEXT DEFAULT 'planning',  -- planning, active, completed

    goal TEXT,
    target_icp_id UUID REFERENCES icp_profiles(id),
    channels TEXT[],

    duration_days INT,
    intensity TEXT,  -- sprint, marathon

    -- Structure
    phases JSONB DEFAULT '[]',

    -- Tracking
    progress INT DEFAULT 0,

    start_date DATE,
    end_date DATE,

    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### muse_assets
```sql
CREATE TABLE muse_assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,

    title TEXT NOT NULL,
    type TEXT NOT NULL,  -- email, social, script, blog, ad, carousel
    content TEXT NOT NULL,

    tags TEXT[],
    tone TEXT,

    -- Versioning
    version INT DEFAULT 1,
    parent_id UUID REFERENCES muse_assets(id),

    -- Context
    move_id UUID REFERENCES moves(id),

    source TEXT DEFAULT 'muse',  -- muse, template, import

    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### blackbox_strategies
```sql
CREATE TABLE blackbox_strategies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,

    name TEXT NOT NULL,
    focus_area TEXT NOT NULL,  -- acquisition, retention, revenue, brand_equity, virality
    outcome TEXT,
    risk_level INT,

    phases JSONB DEFAULT '[]',
    execution_steps TEXT[],

    expected_upside TEXT,
    potential_downside TEXT,
    time_to_result TEXT,

    status TEXT DEFAULT 'generated',  -- generated, accepted, executed, discarded

    -- Link to resulting move
    move_id UUID REFERENCES moves(id),

    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### daily_wins
```sql
CREATE TABLE daily_wins (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,

    topic TEXT NOT NULL,
    angle TEXT,
    hook TEXT NOT NULL,
    outline TEXT[],
    platform TEXT,

    trend_source TEXT,
    relevance_score DECIMAL(3,2),

    status TEXT DEFAULT 'generated',  -- generated, posted, skipped
    posted_at TIMESTAMPTZ,

    generated_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## AGENT EXECUTION TABLES

### agent_executions
```sql
CREATE TABLE agent_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),

    request_type TEXT NOT NULL,
    request_data JSONB,

    -- Execution trace
    agents_invoked TEXT[],
    tools_used TEXT[],

    -- Output
    output JSONB,
    success BOOLEAN,
    error TEXT,

    -- Cost tracking
    tokens_input INT,
    tokens_output INT,
    total_cost DECIMAL(10,6),

    -- Timing
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    duration_ms INT
);
```

### onboarding_sessions
```sql
CREATE TABLE onboarding_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,

    current_step INT DEFAULT 1,
    completed_steps INT[] DEFAULT '{}',

    -- Evidence vault
    evidence JSONB DEFAULT '[]',

    -- Step data (accumulated)
    step_data JSONB DEFAULT '{}',

    status TEXT DEFAULT 'in_progress',  -- in_progress, completed, abandoned

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## BILLING TABLES

### subscriptions
```sql
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,

    plan TEXT NOT NULL,  -- free, starter, growth, enterprise
    status TEXT DEFAULT 'active',

    price_inr DECIMAL(10,2),
    billing_cycle TEXT,  -- monthly, annual

    current_period_start TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,

    -- PhonePe integration
    phonepe_subscription_id TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### usage_records
```sql
CREATE TABLE usage_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,

    date DATE NOT NULL,

    tokens_used INT DEFAULT 0,
    cost_usd DECIMAL(10,6) DEFAULT 0,

    -- Breakdown by agent
    agent_usage JSONB DEFAULT '{}',

    UNIQUE(user_id, date)
);
```

### payments
```sql
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,

    amount_inr DECIMAL(10,2) NOT NULL,
    gst_amount DECIMAL(10,2),
    total_amount DECIMAL(10,2),

    status TEXT DEFAULT 'pending',

    -- PhonePe
    phonepe_transaction_id TEXT,
    phonepe_merchant_transaction_id TEXT UNIQUE,

    payment_method TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);
```

---

## INDEXES

```sql
-- Performance indexes
CREATE INDEX idx_foundations_workspace ON foundations(workspace_id);
CREATE INDEX idx_icp_profiles_workspace ON icp_profiles(workspace_id);
CREATE INDEX idx_moves_workspace ON moves(workspace_id);
CREATE INDEX idx_moves_campaign ON moves(campaign_id);
CREATE INDEX idx_campaigns_workspace ON campaigns(workspace_id);
CREATE INDEX idx_muse_assets_workspace ON muse_assets(workspace_id);
CREATE INDEX idx_agent_executions_workspace ON agent_executions(workspace_id);
CREATE INDEX idx_usage_records_user_date ON usage_records(user_id, date);

-- Vector indexes for semantic search
CREATE INDEX idx_foundations_embedding ON foundations
    USING ivfflat (summary_embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_icp_profiles_embedding ON icp_profiles
    USING ivfflat (summary_embedding vector_cosine_ops) WITH (lists = 100);
```

---

## ROW LEVEL SECURITY

```sql
-- Enable RLS
ALTER TABLE foundations ENABLE ROW LEVEL SECURITY;
ALTER TABLE icp_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE moves ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaigns ENABLE ROW LEVEL SECURITY;

-- Policies
CREATE POLICY "Users can access own workspace data" ON foundations
    FOR ALL USING (
        workspace_id IN (
            SELECT id FROM workspaces WHERE user_id = auth.uid()
        )
    );

-- Similar policies for other tables
```

---

## REDIS KEY PATTERNS

```
# Session/Cache
session:{session_id}                    # Onboarding session state
cache:foundation:{workspace_id}         # Foundation context cache
cache:icps:{workspace_id}               # ICP profiles cache

# Usage/Budget
usage:{user_id}:{YYYY-MM}              # Monthly usage counter
usage:{user_id}:{YYYY-MM-DD}           # Daily usage counter
budget:{user_id}                        # Current budget limit

# Semantic Cache
semantic:{user_id}                      # Semantic query cache (hash)

# Rate Limiting
ratelimit:{user_id}:{endpoint}          # API rate limiting

# Queues
queue:agent_tasks                       # Agent execution queue
queue:webhooks                          # Webhook processing queue
```
