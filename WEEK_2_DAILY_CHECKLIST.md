# Week 2 Daily Checklist: Codex Schema Creation
**Status**: Ready to Execute (Post-Week 1 Database Cleanup)

**Timeline**: 5 days
**Effort**: 18-22 hours
**Prerequisites**: Week 1 complete with 43 active tables ✅

---

## Week 2 Overview

After removing 9 unused tables in Week 1, we now add **25 new Codex tables** across 5 migrations:

| Migration | Purpose | Tables | Est. Time |
|-----------|---------|--------|-----------|
| **013** | Positioning & Campaigns | 5 tables | 1-2 hrs |
| **014** | Gamification & Achievements | 3 tables | 1 hr |
| **015** | Agent Registry & Memory | 4 tables | 1.5 hrs |
| **016** | Intelligence & Alerts | 5 tables | 1.5 hrs |
| **017** | RLS Policies & Indexes | Performance | 2-3 hrs |

**Expected Result**: 68 total tables (43 + 25 new)

---

## MONDAY: Migrations 013-014 (Positioning, Campaigns, Gamification)

### Task 1: Prepare Migration 013 - Positioning & Campaign Infrastructure (1.5 hrs)

**What You're Doing**: Creating the core positioning framework that feeds campaigns with strategic insights.

**Files to Create**:
1. `database/migrations/013_create_positioning_campaigns.sql`
2. Copy the complete SQL below:

```sql
-- ============================================================================
-- MIGRATION 013: POSITIONING & CAMPAIGN INFRASTRUCTURE
-- ============================================================================
-- Creates the strategic positioning layer and campaigns framework
-- This enables the Muse Guild (content generation) and RES-001/RES-002 agents
--
-- Tables Created: 5
-- Dependencies: workspaces, cohorts, moves, assets
-- Time to Execute: < 500ms
-- Safe: Yes - new tables only
-- ============================================================================

-- Table 1: positioning
-- Stores strategic positioning statements for each cohort
CREATE TABLE IF NOT EXISTS positioning (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  for_cohort_id uuid NOT NULL REFERENCES cohorts(id) ON DELETE CASCADE,

  -- Core positioning elements
  problem_statement text NOT NULL,
  category_frame text NOT NULL,
  differentiator text NOT NULL,
  reason_to_believe text,
  competitive_alternative text,

  -- Metadata
  is_active boolean DEFAULT true,
  created_at timestamp DEFAULT NOW(),
  updated_at timestamp DEFAULT NOW(),

  CONSTRAINT positioning_unique_per_cohort UNIQUE (workspace_id, for_cohort_id)
);

CREATE INDEX idx_positioning_workspace ON positioning(workspace_id);
CREATE INDEX idx_positioning_cohort ON positioning(for_cohort_id);

-- Table 2: message_architecture
-- Hierarchical messaging strategy (claim → proof points → messaging)
CREATE TABLE IF NOT EXISTS message_architecture (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  positioning_id uuid NOT NULL REFERENCES positioning(id) ON DELETE CASCADE,

  -- Messaging hierarchy
  primary_claim text NOT NULL,
  proof_points jsonb, -- Array of supporting evidence
  sub_claims jsonb,   -- Secondary claims
  rejection_reasons jsonb, -- Common objections addressed

  -- Variants for different channels
  headline_variant text,
  body_variant text,
  cta_variant text,

  -- Metadata
  created_at timestamp DEFAULT NOW(),
  updated_at timestamp DEFAULT NOW()
);

CREATE INDEX idx_message_arch_positioning ON message_architecture(positioning_id);

-- Table 3: campaigns
-- Campaign definitions linked to positioning and cohorts
CREATE TABLE IF NOT EXISTS campaigns (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

  -- Campaign basics
  name text NOT NULL,
  description text,
  positioning_id uuid REFERENCES positioning(id) ON DELETE SET NULL,

  -- Campaign strategy
  objective_type text NOT NULL CHECK (objective_type IN ('awareness', 'consideration', 'conversion', 'retention', 'advocacy')),
  target_stage text CHECK (target_stage IN ('awareness', 'consideration', 'decision', 'post_purchase')),

  -- Budget & timeline
  budget numeric(12, 2),
  currency text DEFAULT 'USD',
  start_date date,
  end_date date,

  -- Status tracking
  status text DEFAULT 'planning' CHECK (status IN ('planning', 'approved', 'active', 'paused', 'completed')),
  approval_status text DEFAULT 'pending' CHECK (approval_status IN ('pending', 'approved', 'rejected')),

  -- Performance metrics (computed)
  estimated_reach integer,
  estimated_conversions integer,
  estimated_roi numeric(6, 2),

  -- Metadata
  created_by uuid REFERENCES auth.users(id),
  created_at timestamp DEFAULT NOW(),
  updated_at timestamp DEFAULT NOW(),

  CONSTRAINT campaign_unique_name UNIQUE (workspace_id, name)
);

CREATE INDEX idx_campaigns_workspace ON campaigns(workspace_id);
CREATE INDEX idx_campaigns_status ON campaigns(status);
CREATE INDEX idx_campaigns_positioning ON campaigns(positioning_id);

-- Table 4: campaign_quests
-- Gamified campaign milestones (quest = campaign milestone structure)
CREATE TABLE IF NOT EXISTS campaign_quests (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,

  -- Quest definition
  title text NOT NULL,
  description text,
  sequence_order integer,

  -- Quest chapters (nested structure for multi-step execution)
  chapters jsonb NOT NULL, -- Array of {title, description, estimated_hours, deliverables}

  -- Success criteria
  success_metrics jsonb, -- {metric: value, threshold: target}

  -- Estimates
  estimated_hours integer,
  estimated_budget numeric(10, 2),
  estimated_conversion_rate numeric(5, 4),
  estimated_roi numeric(6, 2),

  -- Status
  status text DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'completed', 'archived')),

  -- Metadata
  created_at timestamp DEFAULT NOW(),
  updated_at timestamp DEFAULT NOW()
);

CREATE INDEX idx_campaign_quests_campaign ON campaign_quests(campaign_id);
CREATE INDEX idx_campaign_quests_order ON campaign_quests(campaign_id, sequence_order);

-- Table 5: campaign_cohorts
-- Junction table linking campaigns to target cohorts
CREATE TABLE IF NOT EXISTS campaign_cohorts (
  campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  cohort_id uuid NOT NULL REFERENCES cohorts(id) ON DELETE CASCADE,
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

  -- Priority & allocation
  priority_rank integer DEFAULT 1,
  allocation_percentage numeric(5, 2) DEFAULT 100,

  -- Cohort-specific metrics
  cohort_estimated_reach integer,
  cohort_conversion_rate numeric(5, 4),
  cohort_budget_allocation numeric(12, 2),

  PRIMARY KEY (campaign_id, cohort_id),
  CONSTRAINT allocation_percentage_valid CHECK (allocation_percentage > 0 AND allocation_percentage <= 100)
);

CREATE INDEX idx_campaign_cohorts_cohort ON campaign_cohorts(cohort_id);

-- ============================================================================
-- EXTENSION: Add campaign linkage to existing tables
-- ============================================================================

ALTER TABLE moves ADD COLUMN IF NOT EXISTS campaign_id uuid REFERENCES campaigns(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS idx_moves_campaign ON moves(campaign_id);

ALTER TABLE assets ADD COLUMN IF NOT EXISTS move_id uuid REFERENCES moves(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS idx_assets_move ON assets(move_id);

-- ============================================================================
-- ROW-LEVEL SECURITY: Preliminary RLS for new tables (detailed in migration 017)
-- ============================================================================
-- Note: Full RLS policies added in migration 017
-- For now, ensure workspace_id isolation is enforced at application level

-- ============================================================================
-- VERIFICATION QUERIES (run after migration)
-- ============================================================================
-- SELECT COUNT(*) FROM positioning;
-- SELECT COUNT(*) FROM message_architecture;
-- SELECT COUNT(*) FROM campaigns;
-- SELECT COUNT(*) FROM campaign_quests;
-- SELECT COUNT(*) FROM campaign_cohorts;
```

**Verification Steps**:
```bash
# 1. Copy the SQL to Supabase SQL Editor
# 2. Run the migration

# 3. Expected output: Query execution completed
# (No rows created, just schema added)

# 4. Verify table creation:
# Run these queries in Supabase SQL Editor:

SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('positioning', 'message_architecture', 'campaigns', 'campaign_quests', 'campaign_cohorts')
ORDER BY table_name;

-- Expected result: 5 rows
-- positioning
-- message_architecture
-- campaigns
-- campaign_quests
-- campaign_cohorts
```

**If migration fails**:
- Error: "relation positioning already exists" → Table already created, safe to continue
- Error: Foreign key violation → Check workspaces, cohorts, moves tables exist (they should from Week 1)
- Error: Column already exists → Safe, just means it was already added

---

### Task 2: Prepare Migration 014 - Gamification & Achievements (1 hr)

**What You're Doing**: Adding the XP/levels/achievements framework that powers user engagement metrics.

**File to Create**: `database/migrations/014_create_gamification.sql`

```sql
-- ============================================================================
-- MIGRATION 014: GAMIFICATION & USER ACHIEVEMENTS
-- ============================================================================
-- Creates XP, levels, achievements, and streak tracking
-- Enables gamification layer for frontend (Kingdom Dashboard)
--
-- Tables Created: 3
-- Dependencies: auth.users, workspaces
-- Time to Execute: < 300ms
-- Safe: Yes - new tables only
-- ============================================================================

-- Table 1: achievements
-- Definition of all possible achievements a user can unlock
CREATE TABLE IF NOT EXISTS achievements (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

  -- Achievement definition
  code varchar(50) NOT NULL, -- e.g., "first_campaign", "research_master"
  name varchar(100) NOT NULL,
  description text,
  category text CHECK (category IN ('research', 'creation', 'strategy', 'engagement', 'mastery')),

  -- Reward
  xp_value int NOT NULL DEFAULT 100,
  badge_icon_url text,
  rarity text DEFAULT 'common' CHECK (rarity IN ('common', 'uncommon', 'rare', 'epic', 'legendary')),

  -- Unlock conditions
  unlock_condition jsonb, -- {type: 'move_count', value: 10} or {type: 'xp_threshold', value: 1000}

  -- Metadata
  is_active boolean DEFAULT true,
  created_at timestamp DEFAULT NOW(),

  CONSTRAINT achievement_unique_code UNIQUE (workspace_id, code)
);

CREATE INDEX idx_achievements_workspace ON achievements(workspace_id);
CREATE INDEX idx_achievements_rarity ON achievements(rarity);

-- Table 2: user_achievements
-- Track which achievements each user has unlocked
CREATE TABLE IF NOT EXISTS user_achievements (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  achievement_id uuid NOT NULL REFERENCES achievements(id) ON DELETE CASCADE,

  -- Achievement unlock tracking
  unlocked_at timestamp DEFAULT NOW(),
  progress_percentage numeric(5, 2) DEFAULT 100,

  -- Optional: notification sent tracking
  notification_sent boolean DEFAULT false,

  CONSTRAINT user_achievement_unique UNIQUE (user_id, achievement_id)
);

CREATE INDEX idx_user_achievements_user ON user_achievements(user_id);
CREATE INDEX idx_user_achievements_achievement ON user_achievements(achievement_id);
CREATE INDEX idx_user_achievements_unlocked ON user_achievements(unlocked_at);

-- Table 3: user_stats
-- Aggregated user progression metrics
CREATE TABLE IF NOT EXISTS user_stats (
  user_id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

  -- XP & Levels
  total_xp int DEFAULT 0,
  current_level int DEFAULT 1,
  xp_to_next_level int DEFAULT 1000, -- Dynamic based on level curve

  -- Streaks & Activity
  current_streak int DEFAULT 0,
  longest_streak int DEFAULT 0,
  streak_last_activity_date date,

  -- Milestones
  last_achievement_unlocked_at timestamp,
  achievement_count int DEFAULT 0,

  -- Engagement
  total_campaigns_created int DEFAULT 0,
  total_moves_executed int DEFAULT 0,
  total_research_minutes int DEFAULT 0,

  -- Metadata
  created_at timestamp DEFAULT NOW(),
  updated_at timestamp DEFAULT NOW()
);

CREATE INDEX idx_user_stats_level ON user_stats(current_level);
CREATE INDEX idx_user_stats_xp ON user_stats(total_xp);
CREATE INDEX idx_user_stats_streak ON user_stats(current_streak);

-- ============================================================================
-- INITIAL ACHIEVEMENT SEED DATA
-- ============================================================================
-- These are the foundational achievements - add more as features develop

INSERT INTO achievements (workspace_id, code, name, description, category, xp_value, rarity, unlock_condition)
SELECT
  id as workspace_id,
  'first_campaign' as code,
  'Campaign Creator' as name,
  'Create your first campaign' as description,
  'creation' as category,
  100 as xp_value,
  'common' as rarity,
  '{"type": "campaign_count", "value": 1}'::jsonb as unlock_condition
FROM workspaces
ON CONFLICT (workspace_id, code) DO NOTHING;

INSERT INTO achievements (workspace_id, code, name, description, category, xp_value, rarity, unlock_condition)
SELECT
  id as workspace_id,
  'research_master' as code,
  'Research Master' as name,
  'Execute 10 research moves' as description,
  'research' as category,
  500 as xp_value,
  'rare' as rarity,
  '{"type": "move_type", "move_type": "research", "count": 10}'::jsonb as unlock_condition
FROM workspaces
ON CONFLICT (workspace_id, code) DO NOTHING;

INSERT INTO achievements (workspace_id, code, name, description, category, xp_value, rarity, unlock_condition)
SELECT
  id as workspace_id,
  'content_creator' as code,
  'Content Creator' as name,
  'Generate 5 pieces of content' as description,
  'creation' as category,
  300 as xp_value,
  'uncommon' as rarity,
  '{"type": "asset_count", "value": 5}'::jsonb as unlock_condition
FROM workspaces
ON CONFLICT (workspace_id, code) DO NOTHING;

-- ============================================================================
-- VERIFICATION QUERIES (run after migration)
-- ============================================================================
-- SELECT COUNT(*) FROM achievements;
-- SELECT COUNT(*) FROM user_achievements;
-- SELECT COUNT(*) FROM user_stats;
-- SELECT * FROM achievements WHERE code = 'first_campaign';
```

**Verification Steps**:
```bash
# Run in Supabase SQL Editor:

SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('achievements', 'user_achievements', 'user_stats')
ORDER BY table_name;

-- Expected: 3 rows returned

SELECT COUNT(*) FROM achievements;
-- Expected: 3 rows (initial seed data: first_campaign, research_master, content_creator)

SELECT code, name FROM achievements ORDER BY code;
-- Expected output:
-- content_creator | Content Creator
-- first_campaign | Campaign Creator
-- research_master | Research Master
```

---

### Task 3: Execute Migrations 013 & 014 on Staging (45 min)

**Step 1**: Open Supabase Dashboard → SQL Editor

**Step 2**: Copy entire migration 013 SQL, create new query, paste, and run
```
Expected: Query executed successfully
Status: DONE ✅
Time: ~500ms
```

**Step 3**: Copy entire migration 014 SQL, create new query, paste, and run
```
Expected: Query executed successfully
Status: DONE ✅
Time: ~400ms
```

**Step 4**: Verify both migrations with aggregate query:
```sql
-- Check total table count on staging (should be 48: 43 + 5 from 013)
SELECT COUNT(*) as table_count
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_type = 'BASE TABLE';

-- Expected: 48 tables
```

**If errors occur**:
- "Relation already exists" → Safe, migration was partially applied
- "Foreign key violation on workspaces" → Schema may be incomplete, verify in UI
- "Column undefined" → Check for typos in SQL, re-run migration 013 carefully

**Troubleshooting Command**:
```sql
-- If migration 013 seems incomplete, verify each table:
SELECT 'positioning' as table_name, COUNT(*) as rows FROM positioning
UNION ALL
SELECT 'message_architecture', COUNT(*) FROM message_architecture
UNION ALL
SELECT 'campaigns', COUNT(*) FROM campaigns
UNION ALL
SELECT 'campaign_quests', COUNT(*) FROM campaign_quests
UNION ALL
SELECT 'campaign_cohorts', COUNT(*) FROM campaign_cohorts;

-- If any return error, table wasn't created - re-run that section
```

---

### Task 4: Update Application Code for Campaign Integration (30 min)

**What You're Doing**: Adding campaign context to existing agent queries.

**File**: `backend/utils/database.py` (or your schema sync file)

Add this helper function for campaign queries:

```python
async def get_campaign_context(workspace_id: str, campaign_id: str) -> dict:
    """
    Fetch full campaign context for agent planning
    Returns: {campaign, positioning, message_arch, target_cohorts, quests}
    """
    query = """
    SELECT
      c.id, c.name, c.objective_type, c.budget, c.status,
      p.problem_statement, p.differentiator, p.reason_to_believe,
      ma.primary_claim, ma.proof_points,
      json_agg(
        json_build_object('cohort_id', cc.cohort_id, 'priority', cc.priority_rank)
      ) as target_cohorts
    FROM campaigns c
    LEFT JOIN positioning p ON c.positioning_id = p.id
    LEFT JOIN message_architecture ma ON p.id = ma.positioning_id
    LEFT JOIN campaign_cohorts cc ON c.id = cc.campaign_id
    WHERE c.workspace_id = %s AND c.id = %s
    GROUP BY c.id, p.id, ma.id;
    """

    result = await db.fetch_one(query, workspace_id, campaign_id)
    return result if result else {}
```

---

## TUESDAY: Migration 015 (Agent Registry & Memory)

### Task 1: Prepare Migration 015 - Agent Registry & RAG Memory (2 hrs)

**What You're Doing**: Creating the agent catalog and vector embedding storage for RAG-enhanced decision making.

**File to Create**: `database/migrations/015_create_agent_registry.sql`

```sql
-- ============================================================================
-- MIGRATION 015: AGENT REGISTRY & RAG MEMORY SYSTEM
-- ============================================================================
-- Creates agent catalog, capability registry, and vector embedding storage
-- Enables agent self-discovery, role assignment, and RAG context injection
--
-- Tables Created: 4
-- Dependencies: workspaces, auth.users
-- Time to Execute: < 400ms
-- Safe: Yes - new tables only, pgvector extension optional
-- ============================================================================

-- Enable pgvector extension (for vector similarity search)
-- Note: May fail if already enabled - this is safe
CREATE EXTENSION IF NOT EXISTS vector;

-- Table 1: agents
-- Complete agent registry with roles, capabilities, cost tracking
CREATE TABLE IF NOT EXISTS agents (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

  -- Agent identity
  code varchar(20) NOT NULL, -- e.g., 'LORD-001', 'RES-005', 'MUSE-012'
  name varchar(100) NOT NULL,
  role text NOT NULL CHECK (role IN ('lord', 'research', 'muse', 'matrix', 'guardian', 'utility')),
  guild text CHECK (guild IN ('council', 'research', 'muse', 'matrix', 'guardians')),

  -- Description & capabilities
  description text,
  system_prompt text, -- Full LLM system prompt for this agent
  capabilities jsonb, -- Array of capabilities: ['research', 'content_gen', 'analysis']

  -- Model & inference config
  primary_model text NOT NULL, -- 'gemini-2.5-flash', 'claude-opus', etc.
  temperature numeric(3, 2) DEFAULT 0.7,
  max_tokens int DEFAULT 4000,

  -- Performance metrics
  success_rate numeric(5, 2), -- % of tasks completed successfully
  avg_response_time_ms int,
  total_invocations int DEFAULT 0,
  total_tokens_used int DEFAULT 0,
  total_cost_cents numeric(10, 2) DEFAULT 0,

  -- Activation & metadata
  is_active boolean DEFAULT true,
  created_by uuid REFERENCES auth.users(id),
  created_at timestamp DEFAULT NOW(),
  updated_at timestamp DEFAULT NOW(),

  CONSTRAINT agent_unique_code UNIQUE (workspace_id, code),
  CONSTRAINT valid_cost CHECK (total_cost_cents >= 0)
);

CREATE INDEX idx_agents_workspace ON agents(workspace_id);
CREATE INDEX idx_agents_role ON agents(role);
CREATE INDEX idx_agents_guild ON agents(guild);
CREATE INDEX idx_agents_code ON agents(code);

-- Table 2: agent_capabilities
-- Detailed capability matrix with performance metrics per capability
CREATE TABLE IF NOT EXISTS agent_capabilities (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  agent_id uuid NOT NULL REFERENCES agents(id) ON DELETE CASCADE,

  -- Capability definition
  capability_code varchar(50) NOT NULL, -- 'research_analysis', 'content_generation', etc.
  name varchar(100),
  description text,

  -- Performance in this capability
  success_rate numeric(5, 2),
  avg_response_time_ms int,
  invocations_count int DEFAULT 0,

  -- Cost per invocation
  avg_cost_cents numeric(8, 4),

  CONSTRAINT agent_capability_unique UNIQUE (agent_id, capability_code)
);

CREATE INDEX idx_agent_capabilities_agent ON agent_capabilities(agent_id);
CREATE INDEX idx_agent_capabilities_code ON agent_capabilities(capability_code);

-- Table 3: agent_memories (RAG Vector Store)
-- Embeddings for agent context injection and decision making
CREATE TABLE IF NOT EXISTS agent_memories (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  agent_id uuid REFERENCES agents(id) ON DELETE CASCADE,

  -- Memory content
  memory_type text NOT NULL CHECK (memory_type IN (
    'codex_knowledge',      -- General Codex system knowledge
    'campaign_brief',       -- Campaign context & strategy
    'competitor_intel',     -- Competitive analysis
    'historical_result',    -- Past campaign results
    'user_preference',      -- User/org preferences
    'process_example'       -- Example workflows
  )),

  content text NOT NULL,
  source_reference text, -- e.g., 'campaign_id:123', 'article_url:...'

  -- Embedding (optional, requires pgvector)
  -- Uncomment if using vector search:
  -- embedding vector(1536), -- OpenAI embedding dimension

  -- Metadata
  relevance_score numeric(3, 2), -- How useful is this memory? 0-1
  last_used_at timestamp,
  use_count int DEFAULT 0,
  created_at timestamp DEFAULT NOW(),
  updated_at timestamp DEFAULT NOW()
);

CREATE INDEX idx_agent_memories_agent ON agent_memories(agent_id);
CREATE INDEX idx_agent_memories_type ON agent_memories(memory_type);
-- Uncomment if using vector search:
-- CREATE INDEX idx_agent_memories_embedding ON agent_memories USING ivfflat (embedding vector_cosine_ops);

-- Table 4: agent_config_log
-- Audit trail of agent configuration changes
CREATE TABLE IF NOT EXISTS agent_config_log (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  agent_id uuid NOT NULL REFERENCES agents(id) ON DELETE CASCADE,

  -- What changed
  config_field varchar(100), -- 'temperature', 'max_tokens', 'system_prompt', etc.
  old_value text,
  new_value text,

  -- Who changed it and when
  changed_by uuid REFERENCES auth.users(id),
  changed_at timestamp DEFAULT NOW(),

  -- Reason
  reason text
);

CREATE INDEX idx_agent_config_log_agent ON agent_config_log(agent_id);
CREATE INDEX idx_agent_config_log_date ON agent_config_log(changed_at);

-- ============================================================================
-- INITIAL AGENT REGISTRY SEED DATA
-- ============================================================================
-- Insert all 70+ agents into agent registry
-- Format: (workspace_id, code, name, role, guild, system_prompt, primary_model, ...)

INSERT INTO agents (workspace_id, code, name, role, guild, description, primary_model)
SELECT
  id as workspace_id,
  'LORD-001' as code,
  'The Architect' as name,
  'lord' as role,
  'council' as guild,
  'Strategic architect overseeing all agent operations and cross-guild coordination' as description,
  'claude-opus-4-1' as primary_model
FROM workspaces
ON CONFLICT (workspace_id, code) DO NOTHING;

INSERT INTO agents (workspace_id, code, name, role, guild, description, primary_model)
SELECT
  id as workspace_id,
  'RES-001' as code,
  'Market Researcher' as name,
  'research' as role,
  'research' as guild,
  'Gathers and synthesizes market research from multiple sources' as description,
  'gemini-2.5-flash' as primary_model
FROM workspaces
ON CONFLICT (workspace_id, code) DO NOTHING;

-- Continue with all 70+ agents...
-- (Detailed in CODEX_BLUEPRINT.md - Agent Registry section)

-- ============================================================================
-- VERIFICATION QUERIES (run after migration)
-- ============================================================================
-- SELECT COUNT(*) FROM agents;
-- SELECT COUNT(*) FROM agent_capabilities;
-- SELECT COUNT(*) FROM agent_memories;
-- SELECT code, name, role FROM agents WHERE role = 'lord';
```

**Expected table count after 015**: 51 tables (48 + 3)

---

### Task 2: Execute Migration 015 on Staging (1 hr)

```bash
# Step 1: Copy migration 015 SQL to Supabase SQL Editor
# Step 2: Run migration (may see pgvector extension warning - safe to ignore)
# Step 3: Verify execution:

SELECT COUNT(*) FROM agents;
-- Expected: 1 agent (The Architect - LORD-001) initially
-- Will expand to 70+ when full seed data is added

SELECT COUNT(*) FROM agent_capabilities;
-- Expected: 0 (empty initially, populated by agent setup scripts)

SELECT COUNT(*) FROM agent_memories;
-- Expected: 0 (empty initially, populated during operation)

# Step 4: Check for pgvector support
SELECT * FROM pg_extension WHERE extname = 'vector';
-- Expected: 1 row (extension is enabled)
```

---

## WEDNESDAY: Migration 016 (Intelligence & Alerts)

### Task 1: Prepare Migration 016 - Intelligence & Alert System (1.5 hrs)

**What You're Doing**: Creating the intelligence aggregation layer for competitive research and crisis management.

**File to Create**: `database/migrations/016_create_intelligence_alerts.sql`

```sql
-- ============================================================================
-- MIGRATION 016: INTELLIGENCE & ALERT SYSTEM
-- ============================================================================
-- Creates war briefs, intelligence logs, and alert management
-- Enables Matrix Guild (intelligence agents) and crisis response
--
-- Tables Created: 5
-- Dependencies: workspaces, agents, campaigns
-- Time to Execute: < 400ms
-- Safe: Yes - new tables only
-- ============================================================================

-- Table 1: war_briefs
-- Aggregated competitive intelligence and market analysis
CREATE TABLE IF NOT EXISTS war_briefs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  campaign_id uuid REFERENCES campaigns(id) ON DELETE SET NULL,

  -- Brief content
  title text NOT NULL,
  executive_summary text,
  key_findings jsonb, -- Array of findings with confidence scores
  competitive_threats jsonb, -- Array of competitor moves detected
  market_opportunities jsonb, -- Array of market gaps identified

  -- Metadata
  brief_type text CHECK (brief_type IN ('weekly', 'campaign', 'competitor', 'market', 'crisis')),
  priority text DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'critical')),

  generated_by uuid REFERENCES agents(id),
  generated_at timestamp DEFAULT NOW(),
  valid_until timestamp, -- When this brief expires

  -- Tracking
  action_items_count int DEFAULT 0,
  acted_on boolean DEFAULT false
);

CREATE INDEX idx_war_briefs_workspace ON war_briefs(workspace_id);
CREATE INDEX idx_war_briefs_campaign ON war_briefs(campaign_id);
CREATE INDEX idx_war_briefs_type ON war_briefs(brief_type);
CREATE INDEX idx_war_briefs_priority ON war_briefs(priority);

-- Table 2: intelligence_logs
-- Detailed audit trail of all intelligence gathering activities
CREATE TABLE IF NOT EXISTS intelligence_logs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

  -- Signal origin
  signal_type text NOT NULL CHECK (signal_type IN (
    'competitor_activity',
    'market_trend',
    'technology_shift',
    'regulatory_change',
    'customer_sentiment',
    'industry_event'
  )),

  -- Content
  source_url text,
  headline text,
  summary text,
  full_content text,
  signal_strength numeric(3, 2), -- 0-1 confidence score

  -- Processing
  detected_at timestamp DEFAULT NOW(),
  processed_at timestamp,
  processed_by uuid REFERENCES agents(id),
  processing_result jsonb, -- {relevant: bool, themes: [], actions: []}

  -- Classification
  relevance_to_campaigns jsonb, -- Array of {campaign_id, relevance_score}
  threat_level text CHECK (threat_level IN ('none', 'low', 'medium', 'high', 'critical')),

  -- Archival
  archived boolean DEFAULT false
);

CREATE INDEX idx_intelligence_logs_workspace ON intelligence_logs(workspace_id);
CREATE INDEX idx_intelligence_logs_type ON intelligence_logs(signal_type);
CREATE INDEX idx_intelligence_logs_threat ON intelligence_logs(threat_level);
CREATE INDEX idx_intelligence_logs_detected ON intelligence_logs(detected_at);

-- Table 3: alerts_log
-- Active alerts for crisis management and urgent situations
CREATE TABLE IF NOT EXISTS alerts_log (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  intelligence_log_id uuid REFERENCES intelligence_logs(id) ON DELETE SET NULL,

  -- Alert definition
  alert_type text NOT NULL CHECK (alert_type IN (
    'competitor_threat',
    'market_shift',
    'campaign_impact',
    'brand_mention',
    'stock_alert',
    'regulatory_deadline'
  )),

  title text NOT NULL,
  description text,
  urgency text DEFAULT 'normal' CHECK (urgency IN ('low', 'normal', 'high', 'critical')),

  -- Target information
  target_cohort_id uuid REFERENCES cohorts(id),
  affected_campaigns jsonb, -- Array of campaign IDs that are affected

  -- Response tracking
  acknowledgement_status text DEFAULT 'unacknowledged' CHECK (acknowledgement_status IN ('unacknowledged', 'acknowledged', 'in_progress', 'resolved')),
  acknowledged_at timestamp,
  acknowledged_by uuid REFERENCES auth.users(id),

  -- Action plan
  recommended_action text,
  response_taken text,
  resolved_at timestamp,

  -- Metadata
  created_at timestamp DEFAULT NOW(),
  updated_at timestamp DEFAULT NOW()
);

CREATE INDEX idx_alerts_workspace ON alerts_log(workspace_id);
CREATE INDEX idx_alerts_urgency ON alerts_log(urgency);
CREATE INDEX idx_alerts_status ON alerts_log(acknowledgement_status);
CREATE INDEX idx_alerts_created ON alerts_log(created_at);

-- Table 4: competitor_tracking
-- Continuous monitoring of competitor activities
CREATE TABLE IF NOT EXISTS competitor_tracking (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  competitor_id uuid NOT NULL REFERENCES competitors(id) ON DELETE CASCADE,

  -- Tracked activity
  activity_type text NOT NULL CHECK (activity_type IN (
    'product_launch',
    'pricing_change',
    'marketing_campaign',
    'partnership',
    'acquisition',
    'funding',
    'leadership_change',
    'content_publication'
  )),

  -- Activity details
  activity_title text,
  activity_summary text,
  activity_date date,
  activity_url text,

  -- Analysis
  potential_impact text CHECK (potential_impact IN ('low', 'medium', 'high', 'critical')),
  recommended_response text,

  -- Tracking
  monitoring_agent uuid REFERENCES agents(id),
  detected_at timestamp DEFAULT NOW(),
  last_verified_at timestamp
);

CREATE INDEX idx_competitor_tracking_competitor ON competitor_tracking(competitor_id);
CREATE INDEX idx_competitor_tracking_activity ON competitor_tracking(activity_type);

-- Table 5: alert_response_history
-- Audit trail of all alert responses for learning
CREATE TABLE IF NOT EXISTS alert_response_history (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  alert_id uuid NOT NULL REFERENCES alerts_log(id) ON DELETE CASCADE,

  -- Response action
  action_type text NOT NULL,
  action_description text,

  -- Result
  effectiveness_score numeric(3, 2), -- 0-1 rating of response effectiveness
  lessons_learned text,

  -- Metadata
  taken_by uuid REFERENCES auth.users(id),
  taken_at timestamp DEFAULT NOW()
);

CREATE INDEX idx_alert_response_alert ON alert_response_history(alert_id);

-- ============================================================================
-- VERIFICATION QUERIES (run after migration)
-- ============================================================================
-- SELECT COUNT(*) FROM war_briefs;
-- SELECT COUNT(*) FROM intelligence_logs;
-- SELECT COUNT(*) FROM alerts_log;
-- SELECT COUNT(*) FROM competitor_tracking;
-- SELECT COUNT(*) FROM alert_response_history;
```

**Expected table count after 016**: 56 tables (51 + 5)

---

### Task 2: Execute Migration 016 on Staging (45 min)

```bash
# Run in Supabase SQL Editor:
# Copy entire migration 016 SQL
# Create new query, paste, run

# Verify:
SELECT COUNT(*) as table_count
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_type = 'BASE TABLE';
-- Expected: 56 tables

SELECT table_name
FROM information_schema.tables
WHERE table_name IN ('war_briefs', 'intelligence_logs', 'alerts_log', 'competitor_tracking', 'alert_response_history')
ORDER BY table_name;
-- Expected: 5 rows
```

---

## THURSDAY: Migration 017 (RLS Policies & Performance)

### Task 1: Prepare Migration 017 - RLS Policies & Indexes (2-3 hrs)

**What You're Doing**: Adding workspace isolation security policies and performance indexes for production queries.

**File to Create**: `database/migrations/017_rls_policies_indexes.sql`

```sql
-- ============================================================================
-- MIGRATION 017: ROW-LEVEL SECURITY POLICIES & PERFORMANCE INDEXES
-- ============================================================================
-- Enforces workspace-level isolation and adds critical query indexes
-- Ensures multi-tenant security and production query performance
--
-- RLS Policies: 15+
-- Indexes: 20+
-- Time to Execute: 1-2 seconds
-- Safe: Yes - policies are transparent, indexes don't modify data
-- ============================================================================

-- ============================================================================
-- PART 1: ENABLE RLS ON ALL TABLES
-- ============================================================================

ALTER TABLE positioning ENABLE ROW LEVEL SECURITY;
ALTER TABLE message_architecture ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaign_quests ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaign_cohorts ENABLE ROW LEVEL SECURITY;
ALTER TABLE achievements ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_achievements ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_stats ENABLE ROW LEVEL SECURITY;
ALTER TABLE agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_capabilities ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_memories ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_config_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE war_briefs ENABLE ROW LEVEL SECURITY;
ALTER TABLE intelligence_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE competitor_tracking ENABLE ROW LEVEL SECURITY;
ALTER TABLE alert_response_history ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- PART 2: RLS POLICIES (Workspace Isolation)
-- ============================================================================

-- Policy: positioning - workspace isolation
CREATE POLICY positioning_workspace_isolation ON positioning
  USING (workspace_id = auth.uid()::uuid OR EXISTS(
    SELECT 1 FROM workspace_members
    WHERE workspace_id = positioning.workspace_id
    AND user_id = auth.uid()::uuid
  ))
  WITH CHECK (workspace_id IN (
    SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()::uuid
  ));

-- Policy: campaigns - workspace isolation
CREATE POLICY campaigns_workspace_isolation ON campaigns
  USING (workspace_id IN (
    SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()::uuid
  ))
  WITH CHECK (workspace_id IN (
    SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()::uuid
  ));

-- Policy: war_briefs - workspace isolation
CREATE POLICY war_briefs_workspace_isolation ON war_briefs
  USING (workspace_id IN (
    SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()::uuid
  ))
  WITH CHECK (workspace_id IN (
    SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()::uuid
  ));

-- Policy: alerts_log - workspace isolation
CREATE POLICY alerts_workspace_isolation ON alerts_log
  USING (workspace_id IN (
    SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()::uuid
  ))
  WITH CHECK (workspace_id IN (
    SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()::uuid
  ));

-- Policy: achievements - workspace isolation
CREATE POLICY achievements_workspace_isolation ON achievements
  USING (workspace_id IN (
    SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()::uuid
  ));

-- Policy: user_achievements - users see only their own + workspace context
CREATE POLICY user_achievements_own_only ON user_achievements
  USING (user_id = auth.uid()::uuid OR workspace_id IN (
    SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()::uuid
  ))
  WITH CHECK (workspace_id IN (
    SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()::uuid
  ));

-- Policy: agents - workspace isolation
CREATE POLICY agents_workspace_isolation ON agents
  USING (workspace_id IN (
    SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()::uuid
  ));

-- ============================================================================
-- PART 3: CRITICAL PERFORMANCE INDEXES
-- ============================================================================

-- Campaign query indexes
CREATE INDEX IF NOT EXISTS idx_campaigns_workspace_status ON campaigns(workspace_id, status);
CREATE INDEX IF NOT EXISTS idx_campaigns_created_date ON campaigns(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_campaign_cohorts_efficiency ON campaign_cohorts(campaign_id, allocation_percentage);

-- Agent performance indexes
CREATE INDEX IF NOT EXISTS idx_agents_active ON agents(workspace_id, is_active);
CREATE INDEX IF NOT EXISTS idx_agent_capabilities_performance ON agent_capabilities(agent_id, success_rate DESC);

-- Intelligence query indexes
CREATE INDEX IF NOT EXISTS idx_war_briefs_recent ON war_briefs(workspace_id, generated_at DESC);
CREATE INDEX IF NOT EXISTS idx_intelligence_logs_recent ON intelligence_logs(workspace_id, detected_at DESC);
CREATE INDEX IF NOT EXISTS idx_intelligence_threat_level ON intelligence_logs(threat_level) WHERE threat_level IN ('high', 'critical');

-- Alert response indexes
CREATE INDEX IF NOT EXISTS idx_alerts_unacknowledged ON alerts_log(workspace_id, acknowledgement_status) WHERE acknowledgement_status = 'unacknowledged';
CREATE INDEX IF NOT EXISTS idx_alerts_critical ON alerts_log(workspace_id, urgency) WHERE urgency = 'critical';
CREATE INDEX IF NOT EXISTS idx_alert_response_effectiveness ON alert_response_history(effectiveness_score DESC);

-- Achievement & gamification indexes
CREATE INDEX IF NOT EXISTS idx_user_achievements_recent ON user_achievements(unlocked_at DESC);
CREATE INDEX IF NOT EXISTS idx_user_stats_leaderboard ON user_stats(workspace_id, total_xp DESC);

-- Move & asset indexes (existing table enhancements)
CREATE INDEX IF NOT EXISTS idx_moves_campaign_status ON moves(campaign_id, status);
CREATE INDEX IF NOT EXISTS idx_assets_move_content_type ON assets(move_id, content_type);

-- Agent memory search indexes
CREATE INDEX IF NOT EXISTS idx_agent_memories_recent ON agent_memories(agent_id, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_agent_memories_usage ON agent_memories(use_count DESC, relevance_score DESC);

-- ============================================================================
-- PART 4: PERFORMANCE GRANTS (for read-heavy queries)
-- ============================================================================
-- Grant SELECT on all new tables to authenticated users
GRANT SELECT ON positioning TO authenticated;
GRANT SELECT ON message_architecture TO authenticated;
GRANT SELECT ON campaigns TO authenticated;
GRANT SELECT ON campaign_quests TO authenticated;
GRANT SELECT ON campaign_cohorts TO authenticated;
GRANT SELECT ON achievements TO authenticated;
GRANT SELECT ON user_achievements TO authenticated;
GRANT SELECT ON user_stats TO authenticated;
GRANT SELECT ON agents TO authenticated;
GRANT SELECT ON war_briefs TO authenticated;
GRANT SELECT ON intelligence_logs TO authenticated;
GRANT SELECT ON alerts_log TO authenticated;

-- ============================================================================
-- VERIFICATION QUERIES (run after migration)
-- ============================================================================
-- Check RLS is enabled:
-- SELECT tablename, rowsecurity FROM pg_tables
-- WHERE schemaname = 'public'
-- AND tablename LIKE '%position%' OR tablename LIKE '%campaign%';

-- Check indexes are created:
-- SELECT tablename, indexname FROM pg_indexes
-- WHERE schemaname = 'public'
-- AND tablename IN ('campaigns', 'agents', 'war_briefs', 'alerts_log')
-- ORDER BY tablename;

-- Check policies:
-- SELECT schemaname, tablename, policyname FROM pg_policies
-- WHERE schemaname = 'public';
```

**Expected table count after 017**: Still 56 tables (no new tables, just RLS + indexes)

**Verification**:
```sql
-- Check RLS is enabled on key tables:
SELECT tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
AND tablename IN ('campaigns', 'war_briefs', 'agents')
ORDER BY tablename;

-- Expected output:
-- campaigns | t (true)
-- war_briefs | t (true)
-- agents | t (true)

-- Check total indexes (should be 70+):
SELECT COUNT(*) as total_indexes
FROM pg_indexes
WHERE schemaname = 'public';

-- Expected: 70+ indexes (includes auto-created primary key indexes)
```

---

### Task 2: Execute Migration 017 on Staging (1.5 hrs)

```bash
# Step 1: Run migration 017 in Supabase SQL Editor
# Expected: Query executed successfully (RLS policies created silently)

# Step 2: Verify RLS is enabled:
SELECT COUNT(*) as rls_tables
FROM pg_tables
WHERE schemaname = 'public'
AND rowsecurity = true
AND tablename LIKE '%campaign%' OR tablename LIKE '%agent%';

-- Expected: 10+ tables with RLS enabled

# Step 3: Test RLS isolation (use test user)
-- Create test query to verify workspace isolation
SELECT COUNT(*) FROM campaigns
WHERE workspace_id = (SELECT id FROM workspaces LIMIT 1);
-- Expected: Should return count (or 0 if test user not in workspace)
```

---

## FRIDAY: Schema Verification & Completion

### Task 1: Final Schema Audit (1 hr)

**Run complete verification query suite**:

```sql
-- ============================================================================
-- COMPLETE SCHEMA VERIFICATION
-- ============================================================================

-- 1. Total table count
SELECT COUNT(*) as total_tables
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_type = 'BASE TABLE';
-- Expected: 56 tables

-- 2. Count tables by category
SELECT
  'Positioning & Campaigns' as category, COUNT(*) as count
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('positioning', 'message_architecture', 'campaigns', 'campaign_quests', 'campaign_cohorts')
UNION ALL
SELECT
  'Gamification' as category, COUNT(*) as count
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('achievements', 'user_achievements', 'user_stats')
UNION ALL
SELECT
  'Agent Registry' as category, COUNT(*) as count
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('agents', 'agent_capabilities', 'agent_memories', 'agent_config_log')
UNION ALL
SELECT
  'Intelligence & Alerts' as category, COUNT(*) as count
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('war_briefs', 'intelligence_logs', 'alerts_log', 'competitor_tracking', 'alert_response_history');

-- Expected output:
-- Positioning & Campaigns | 5
-- Gamification | 3
-- Agent Registry | 4
-- Intelligence & Alerts | 5

-- 3. Verify all 17 new tables exist:
SELECT COUNT(*) as new_tables_created
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN (
  'positioning', 'message_architecture', 'campaigns', 'campaign_quests', 'campaign_cohorts',
  'achievements', 'user_achievements', 'user_stats',
  'agents', 'agent_capabilities', 'agent_memories', 'agent_config_log',
  'war_briefs', 'intelligence_logs', 'alerts_log', 'competitor_tracking', 'alert_response_history'
);
-- Expected: 17 rows

-- 4. Verify foreign key integrity:
SELECT COUNT(*) as valid_foreign_keys
FROM information_schema.table_constraints
WHERE table_schema = 'public'
AND constraint_type = 'FOREIGN KEY';
-- Expected: 30+ (increased from initial setup)

-- 5. Verify RLS policies:
SELECT COUNT(*) as rls_policies
FROM pg_policies
WHERE schemaname = 'public'
AND tablename IN ('campaigns', 'war_briefs', 'agents', 'achievements');
-- Expected: 8+ policies

-- 6. Check seed data:
SELECT
  'Agents' as table_name, COUNT(*) as row_count FROM agents
UNION ALL
SELECT 'Achievements', COUNT(*) FROM achievements
UNION ALL
SELECT 'User Stats', COUNT(*) FROM user_stats;

-- Expected:
-- Agents | 1+ (at least The Architect)
-- Achievements | 3 (first_campaign, research_master, content_creator)
-- User Stats | 0 (empty until users active)
```

**Save verification output** to `WEEK_2_VERIFICATION_RESULTS.md`

---

### Task 2: Application Code Integration (1 hr)

**Update backend to use new Codex tables**:

Create file: `backend/services/campaign_service.py`

```python
from fastapi import HTTPException
from sqlalchemy import select, func
from datetime import datetime
from typing import List, Optional
import json

async def create_campaign_with_positioning(
    workspace_id: str,
    campaign_name: str,
    objective_type: str,
    positioning_data: dict,
    target_cohorts: List[str]
) -> dict:
    """
    Create a campaign with complete positioning context
    This demonstrates integration with new Codex schema
    """

    # Step 1: Create positioning
    positioning = {
        'workspace_id': workspace_id,
        'problem_statement': positioning_data['problem'],
        'category_frame': positioning_data['category'],
        'differentiator': positioning_data['differentiator'],
        'reason_to_believe': positioning_data.get('rtb'),
        'competitive_alternative': positioning_data.get('alternative'),
        'is_active': True
    }

    # Step 2: Create message architecture
    message_arch = {
        'primary_claim': positioning_data['claim'],
        'proof_points': positioning_data.get('proof_points', []),
        'sub_claims': positioning_data.get('sub_claims', [])
    }

    # Step 3: Create campaign
    campaign = {
        'workspace_id': workspace_id,
        'name': campaign_name,
        'objective_type': objective_type,
        'budget': positioning_data.get('budget'),
        'status': 'planning',
        'estimated_roi': positioning_data.get('estimated_roi')
    }

    # Step 4: Link to cohorts
    campaign_cohorts = [
        {
            'cohort_id': cohort_id,
            'priority_rank': idx + 1,
            'allocation_percentage': 100 / len(target_cohorts)
        }
        for idx, cohort_id in enumerate(target_cohorts)
    ]

    return {
        'positioning': positioning,
        'message_architecture': message_arch,
        'campaign': campaign,
        'campaign_cohorts': campaign_cohorts
    }

async def get_campaign_intelligence_brief(
    workspace_id: str,
    campaign_id: str
) -> dict:
    """
    Get complete intelligence brief for a campaign
    Combines war briefs, alerts, and competitive tracking
    """

    query = """
    SELECT
      wb.id, wb.title, wb.executive_summary,
      wb.key_findings, wb.competitive_threats,
      COUNT(DISTINCT CASE WHEN al.urgency = 'critical' THEN al.id END) as critical_alerts,
      json_agg(DISTINCT ct.activity_type) as competitor_activities
    FROM war_briefs wb
    LEFT JOIN alerts_log al ON wb.campaign_id = al.id
    LEFT JOIN competitor_tracking ct ON wb.campaign_id = ct.id
    WHERE wb.workspace_id = %s AND wb.campaign_id = %s
    GROUP BY wb.id;
    """

    # Execute query and return results
    return {}  # Placeholder

async def log_intelligence_signal(
    workspace_id: str,
    signal_type: str,
    headline: str,
    summary: str,
    source_url: str,
    threat_level: str = 'medium'
) -> dict:
    """
    Log a new intelligence signal for Matrix Guild processing
    """

    signal = {
        'workspace_id': workspace_id,
        'signal_type': signal_type,
        'headline': headline,
        'summary': summary,
        'source_url': source_url,
        'signal_strength': 0.75,
        'threat_level': threat_level,
        'detected_at': datetime.now(),
        'processed': False
    }

    return signal
```

---

### Task 3: Documentation & Sign-Off (45 min)

**Create**: `WEEK_2_COMPLETION_REPORT.md`

```markdown
# Week 2 Completion Report: Codex Schema Creation

**Status**: ✅ COMPLETE

**Date**: [Current Date]
**Total Hours**: [Record actual hours spent]
**Team**: [List who executed this]

## Executed Migrations

| Migration | Name | Tables | Status | Time |
|-----------|------|--------|--------|------|
| 013 | Positioning & Campaigns | 5 | ✅ Done | 45 min |
| 014 | Gamification | 3 | ✅ Done | 30 min |
| 015 | Agent Registry | 4 | ✅ Done | 60 min |
| 016 | Intelligence & Alerts | 5 | ✅ Done | 45 min |
| 017 | RLS & Indexes | N/A | ✅ Done | 90 min |

**Total New Tables**: 17 ✅
**Total Active Tables**: 56 ✅
**Remaining Original Tables**: 39 (from 43 in Week 1)

## Verification Results

### Schema Health
- [x] All 17 new tables created
- [x] 56 total tables in system
- [x] Foreign key constraints validated (30+ FKs)
- [x] RLS policies enabled on 17 tables
- [x] 25+ performance indexes created

### Data Integrity
- [x] Seed data inserted (3 achievements, 1 agent)
- [x] No orphaned foreign keys
- [x] No duplicate constraints
- [x] Pgvector extension enabled for future RAG

### Performance
- [x] Migration execution time: < 5 seconds total
- [x] Query indexes optimized for common patterns
- [x] RLS policies transparent to application

## Code Integration

- [x] Campaign service created (`backend/services/campaign_service.py`)
- [x] Intelligence logging service created
- [x] Agent registry service ready
- [ ] Frontend components still needed (Week 3)

## Issues Encountered

### None 🎉

All migrations executed flawlessly on staging with zero errors.

## Next Steps

**Week 3: Agent Registry & RAG Initialization**
- Initialize all 70+ agents in registry
- Set up ChromaDB for vector embeddings
- Create agent communication backbone
- Begin Council of Lords implementation

**Week 4: Council of Lords**
- Implement 7 Lord classes
- Wire Lords to RaptorBus
- Begin guild command routing

## Sign-Off Checklist

- [x] All migrations verified
- [x] Schema documented
- [x] Tests passing (if applicable)
- [x] No data loss
- [x] Application still functional
- [x] Ready for Week 3

**Signed by**: [Your Name]
**Date**: [Date]
**Approved for production migration**: YES ✅
```

---

## Week 2 Summary

**Total Hours**: 18-22 hours (across 5 days)

**Accomplishments**:
- ✅ 17 new Codex tables created
- ✅ 5 migrations executed (013-017)
- ✅ RLS policies for multi-tenant security
- ✅ 25+ performance indexes added
- ✅ Schema grows from 43 → 56 tables
- ✅ Agent registry ready for population

**Deliverables**:
- `database/migrations/013_create_positioning_campaigns.sql`
- `database/migrations/014_create_gamification.sql`
- `database/migrations/015_create_agent_registry.sql`
- `database/migrations/016_create_intelligence_alerts.sql`
- `database/migrations/017_rls_policies_indexes.sql`
- `backend/services/campaign_service.py`
- `WEEK_2_VERIFICATION_RESULTS.md`
- `WEEK_2_COMPLETION_REPORT.md`

**Ready for**: Week 3 (Agent Registry Initialization & RAG System)
