# COMPLETE DATABASE SCHEMA

---

## Core Tables

```sql
-- ============================================
-- USERS & AUTHENTICATION
-- ============================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),

    -- Profile
    full_name VARCHAR(255),
    avatar_url TEXT,
    phone VARCHAR(20),

    -- Subscription
    subscription_tier VARCHAR(50) DEFAULT 'free',  -- free, starter, growth, agency, enterprise
    subscription_status VARCHAR(50) DEFAULT 'active',  -- active, cancelled, past_due
    subscription_started_at TIMESTAMP,
    subscription_ends_at TIMESTAMP,

    -- Indian Market
    gst_number VARCHAR(20),
    pan_number VARCHAR(15),
    state VARCHAR(100),
    preferred_language VARCHAR(10) DEFAULT 'en',

    -- Settings
    constitution JSONB DEFAULT '{}',  -- User preferences
    notification_settings JSONB DEFAULT '{}',

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login_at TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_subscription ON users(subscription_tier, subscription_status);

-- ============================================
-- WORKSPACES (Multi-tenant)
-- ============================================

CREATE TABLE workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    owner_id UUID REFERENCES users(id) ON DELETE CASCADE,

    -- Settings
    settings JSONB DEFAULT '{}',

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE workspace_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'member',  -- owner, admin, member, viewer
    joined_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(workspace_id, user_id)
);

-- ============================================
-- FOUNDATIONS (User Business Context)
-- ============================================

CREATE TABLE foundations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Company Info
    company_name VARCHAR(255),
    business_description TEXT,
    industry VARCHAR(100),
    location VARCHAR(255),
    website VARCHAR(500),

    -- Positioning
    positioning TEXT,
    unique_value_proposition TEXT,
    key_differentiators JSONB DEFAULT '[]',

    -- Brand
    brand_voice VARCHAR(100),
    tone_keywords JSONB DEFAULT '[]',
    messaging_pillars JSONB DEFAULT '[]',

    -- Products
    products JSONB DEFAULT '[]',
    pricing_info TEXT,

    -- Competitors
    competitors JSONB DEFAULT '[]',

    -- Full data blob
    data JSONB DEFAULT '{}',

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(user_id, workspace_id)
);

CREATE INDEX idx_foundations_user ON foundations(user_id);

-- ============================================
-- ICP PROFILES
-- ============================================

CREATE TABLE icp_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Basic Info
    name VARCHAR(255) NOT NULL,
    title VARCHAR(255),
    industry VARCHAR(100),
    company_size VARCHAR(50),

    -- Psychographics
    pain_points JSONB DEFAULT '[]',
    goals JSONB DEFAULT '[]',
    objections JSONB DEFAULT '[]',

    -- Communication
    preferred_channels JSONB DEFAULT '[]',
    psychographics JSONB DEFAULT '{}',

    -- Firmographics
    firmographics JSONB DEFAULT '{}',

    -- Full data
    data JSONB DEFAULT '{}',

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_icp_user ON icp_profiles(user_id);
CREATE INDEX idx_icp_workspace ON icp_profiles(workspace_id);

-- ============================================
-- CAMPAIGNS
-- ============================================

CREATE TABLE campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Basic Info
    name VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(100),  -- product_launch, diwali, leadgen, awareness
    status VARCHAR(50) DEFAULT 'draft',  -- draft, active, paused, completed

    -- Dates
    start_date DATE,
    end_date DATE,

    -- Configuration
    target_icps JSONB DEFAULT '[]',  -- ICP IDs this campaign targets
    focus_areas JSONB DEFAULT '[]',
    risk_level INTEGER DEFAULT 5,

    -- Generated Content
    strategy JSONB DEFAULT '{}',
    phases JSONB DEFAULT '[]',

    -- Metrics
    metrics JSONB DEFAULT '{}',

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_campaigns_user ON campaigns(user_id);
CREATE INDEX idx_campaigns_status ON campaigns(status);

-- ============================================
-- MOVES (Executable Tasks)
-- ============================================

CREATE TABLE moves (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    campaign_id UUID REFERENCES campaigns(id) ON DELETE SET NULL,

    -- Basic Info
    title VARCHAR(500) NOT NULL,
    description TEXT,
    type VARCHAR(100),  -- content, outreach, research, admin

    -- Status
    status VARCHAR(50) DEFAULT 'pending',  -- pending, in_progress, completed, failed
    priority VARCHAR(20) DEFAULT 'medium',  -- low, medium, high, urgent

    -- Assignment
    due_date TIMESTAMP,
    assigned_to UUID REFERENCES users(id),

    -- Generated Content
    content JSONB DEFAULT '{}',

    -- Execution
    execution_id VARCHAR(255),  -- Link to agent execution

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

CREATE INDEX idx_moves_user ON moves(user_id);
CREATE INDEX idx_moves_status ON moves(status);
CREATE INDEX idx_moves_campaign ON moves(campaign_id);

-- ============================================
-- AGENT EXECUTIONS
-- ============================================

CREATE TABLE executions (
    id VARCHAR(255) PRIMARY KEY,  -- exec_20250110_123456_skill_id
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,

    -- Skill Info
    skill_id VARCHAR(255) NOT NULL,
    skill_version VARCHAR(50),

    -- Input/Output
    inputs JSONB,
    output JSONB,

    -- Status
    status VARCHAR(50) DEFAULT 'pending',  -- pending, running, completed, failed
    error_message TEXT,
    error_code VARCHAR(100),

    -- Metrics
    tokens_used INTEGER DEFAULT 0,
    cost DECIMAL(10, 6) DEFAULT 0,
    execution_time_ms INTEGER,
    tool_calls INTEGER DEFAULT 0,

    -- Quality
    quality_score INTEGER,
    critique JSONB,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

CREATE INDEX idx_executions_user ON executions(user_id);
CREATE INDEX idx_executions_skill ON executions(skill_id);
CREATE INDEX idx_executions_status ON executions(status);
CREATE INDEX idx_executions_created ON executions(created_at);

-- ============================================
-- EVENT SOURCING
-- ============================================

CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    event_id VARCHAR(255) UNIQUE NOT NULL,
    aggregate_id VARCHAR(255) NOT NULL,  -- e.g., exec_123, campaign_456
    event_type VARCHAR(100) NOT NULL,

    -- Data
    data JSONB NOT NULL,

    -- Versioning
    version INTEGER NOT NULL,

    -- Context
    user_id UUID REFERENCES users(id),

    -- Timing
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_events_aggregate ON events(aggregate_id);
CREATE INDEX idx_events_type ON events(event_type);
CREATE INDEX idx_events_timestamp ON events(timestamp);
CREATE INDEX idx_events_aggregate_version ON events(aggregate_id, version);

-- ============================================
-- MEMORY - CONVERSATIONS
-- ============================================

CREATE TABLE conversations (
    id VARCHAR(255) PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,

    title VARCHAR(500),

    -- Full conversation data
    data JSONB NOT NULL,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_conversations_user ON conversations(user_id);
CREATE INDEX idx_conversations_updated ON conversations(updated_at DESC);

-- ============================================
-- MEMORY - KNOWLEDGE GRAPH
-- ============================================

CREATE TABLE graph_entities (
    id VARCHAR(255) PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,

    entity_type VARCHAR(100) NOT NULL,  -- COMPANY, PERSON, PRODUCT, CONCEPT
    name VARCHAR(500) NOT NULL,
    properties JSONB DEFAULT '{}',

    -- Embedding for hybrid search
    embedding vector(768),

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_entities_user ON graph_entities(user_id);
CREATE INDEX idx_entities_type ON graph_entities(entity_type);
CREATE INDEX idx_entities_embedding ON graph_entities USING ivfflat (embedding vector_cosine_ops);

CREATE TABLE graph_relationships (
    id VARCHAR(255) PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,

    source_id VARCHAR(255) REFERENCES graph_entities(id) ON DELETE CASCADE,
    target_id VARCHAR(255) REFERENCES graph_entities(id) ON DELETE CASCADE,
    relationship_type VARCHAR(100) NOT NULL,  -- COMPETES_WITH, TARGETS, etc.

    properties JSONB DEFAULT '{}',
    strength DECIMAL(3, 2) DEFAULT 1.0,

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_relationships_source ON graph_relationships(source_id);
CREATE INDEX idx_relationships_target ON graph_relationships(target_id);
CREATE INDEX idx_relationships_type ON graph_relationships(relationship_type);

-- ============================================
-- MEMORY - VECTOR STORE
-- ============================================

CREATE TABLE memory_chunks (
    id VARCHAR(255) PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,

    content TEXT NOT NULL,
    embedding vector(768) NOT NULL,

    memory_type VARCHAR(100),  -- conversation, fact, research, campaign
    source VARCHAR(500),
    metadata JSONB DEFAULT '{}',

    -- Decay
    decay_weight DECIMAL(5, 4) DEFAULT 1.0,
    access_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP DEFAULT NOW(),

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_memory_user ON memory_chunks(user_id);
CREATE INDEX idx_memory_type ON memory_chunks(memory_type);
CREATE INDEX idx_memory_embedding ON memory_chunks USING ivfflat (embedding vector_cosine_ops);

-- ============================================
-- BILLING & PAYMENTS
-- ============================================

CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,

    plan_id VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'active',

    -- Pricing (in INR)
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'INR',

    -- Billing
    billing_cycle VARCHAR(20) DEFAULT 'monthly',
    current_period_start TIMESTAMP,
    current_period_end TIMESTAMP,

    -- PhonePe
    phonepe_subscription_id VARCHAR(255),

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    subscription_id UUID REFERENCES subscriptions(id),

    -- Transaction
    transaction_id VARCHAR(255) UNIQUE,
    merchant_transaction_id VARCHAR(255),

    -- Amount
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'INR',

    -- GST
    gst_amount DECIMAL(10, 2),
    cgst DECIMAL(10, 2),
    sgst DECIMAL(10, 2),
    igst DECIMAL(10, 2),

    -- Status
    status VARCHAR(50) DEFAULT 'pending',  -- pending, success, failed, refunded
    payment_method VARCHAR(100),

    -- Metadata
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

CREATE INDEX idx_payments_user ON payments(user_id);
CREATE INDEX idx_payments_status ON payments(status);

CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    payment_id UUID REFERENCES payments(id),

    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    invoice_date TIMESTAMP NOT NULL,

    -- Buyer
    buyer_name VARCHAR(255),
    buyer_gstin VARCHAR(20),
    buyer_address TEXT,
    buyer_state VARCHAR(100),

    -- Amounts
    subtotal DECIMAL(10, 2),
    total_gst DECIMAL(10, 2),
    grand_total DECIMAL(10, 2),

    -- Full invoice data
    data JSONB NOT NULL,

    -- PDF
    pdf_url TEXT,

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_invoices_user ON invoices(user_id);
CREATE INDEX idx_invoices_number ON invoices(invoice_number);

-- ============================================
-- USAGE TRACKING
-- ============================================

CREATE TABLE usage_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,

    execution_id VARCHAR(255),
    skill_id VARCHAR(255),

    -- Costs
    amount DECIMAL(10, 6) NOT NULL,
    tokens INTEGER,

    -- Timing
    recorded_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_usage_user ON usage_records(user_id);
CREATE INDEX idx_usage_date ON usage_records(recorded_at);

-- Materialized view for monthly usage
CREATE MATERIALIZED VIEW monthly_usage AS
SELECT
    user_id,
    DATE_TRUNC('month', recorded_at) as month,
    SUM(amount) as total_cost,
    SUM(tokens) as total_tokens,
    COUNT(*) as execution_count
FROM usage_records
GROUP BY user_id, DATE_TRUNC('month', recorded_at);

CREATE UNIQUE INDEX idx_monthly_usage ON monthly_usage(user_id, month);

-- ============================================
-- AUDIT LOG
-- ============================================

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),

    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id VARCHAR(255),

    -- Details
    old_value JSONB,
    new_value JSONB,
    metadata JSONB DEFAULT '{}',

    -- Context
    ip_address INET,
    user_agent TEXT,

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_created ON audit_logs(created_at);

-- ============================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================

-- Enable RLS on all tables
ALTER TABLE foundations ENABLE ROW LEVEL SECURITY;
ALTER TABLE icp_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE moves ENABLE ROW LEVEL SECURITY;
ALTER TABLE executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE memory_chunks ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own data
CREATE POLICY user_isolation_policy ON foundations
    FOR ALL USING (user_id = current_setting('app.user_id')::uuid);

CREATE POLICY user_isolation_policy ON icp_profiles
    FOR ALL USING (user_id = current_setting('app.user_id')::uuid);

CREATE POLICY user_isolation_policy ON campaigns
    FOR ALL USING (user_id = current_setting('app.user_id')::uuid);

CREATE POLICY user_isolation_policy ON moves
    FOR ALL USING (user_id = current_setting('app.user_id')::uuid);

CREATE POLICY user_isolation_policy ON executions
    FOR ALL USING (user_id = current_setting('app.user_id')::uuid);

CREATE POLICY user_isolation_policy ON conversations
    FOR ALL USING (user_id = current_setting('app.user_id')::uuid);

CREATE POLICY user_isolation_policy ON memory_chunks
    FOR ALL USING (user_id = current_setting('app.user_id')::uuid);
```

---

## Redis Key Patterns

```
# ============================================
# SESSION & AUTH
# ============================================
session:{session_id}           -> JSON (user session data)
refresh_token:{user_id}        -> string (refresh token)

# ============================================
# RATE LIMITING
# ============================================
rate:{user_id}:{endpoint}      -> integer (request count)
rate:global:{service}          -> integer (global rate limit)

# ============================================
# CACHING
# ============================================
foundation:{user_id}           -> JSON (foundation data, TTL: 1h)
icp:{icp_id}                   -> JSON (ICP data, TTL: 1h)
conv:{conversation_id}         -> JSON (conversation, TTL: 1h)

# ============================================
# SEMANTIC CACHE
# ============================================
semantic_cache:{user_id}:{skill_id} -> JSON array (cached results)

# ============================================
# BUDGET & USAGE
# ============================================
usage:{user_id}:{YYYY-MM}      -> float (monthly usage in USD)
usage:{user_id}:{YYYY-MM-DD}   -> float (daily usage)
budget_reserve:{user_id}:{exec_id} -> float (reserved budget)
budget_reserved:{user_id}      -> float (total reserved)
budget_alert:{user_id}:{threshold} -> "1" (alert sent flag)

# ============================================
# DISTRIBUTED LOCKING
# ============================================
lock:{resource_type}:{resource_id} -> "locked" (TTL: 30s)

# ============================================
# EVENT VERSIONING
# ============================================
event_version:{aggregate_id}   -> integer (current version)

# ============================================
# SKILL REGISTRY
# ============================================
skill_hash:{skill_id}          -> string (content hash for hot-reload)

# ============================================
# QUEUE (Streams)
# ============================================
events:{aggregate_id}          -> Stream (event stream)
queue:agent_tasks              -> Stream (task queue)
queue:campaign_tasks           -> Stream (campaign processing)

# ============================================
# PUBSUB CHANNELS
# ============================================
updates:{user_id}              -> Channel (real-time updates)
execution:{execution_id}       -> Channel (execution progress)

# ============================================
# CIRCUIT BREAKERS
# ============================================
circuit:{service_name}:failures -> integer (failure count)
circuit:{service_name}:state    -> string (CLOSED/OPEN/HALF_OPEN)

# ============================================
# INVOICE SEQUENCING
# ============================================
invoice_seq:{fiscal_year}      -> integer (next invoice number)
```
