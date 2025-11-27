# PATH A: FULL CODEX DEPLOYMENT - 90-Day Execution Plan

**Commitment Level**: 🔴 MAXIMUM (2+ full-time engineers required)

**Timeline**: 90 days to production

**Target Launch**: 12 weeks from start

**Success Criteria**: All 70+ agents operational, Frontend integrated, $10/user/month cost target achieved

---

## Team Structure

### Minimum Required Team
- **2x Backend Engineers** (Python/FastAPI)
- **1x Frontend Engineer** (React/TypeScript)
- **0.5x DevOps Engineer** (infrastructure/deployments)
- **0.5x QA Engineer** (testing/validation)

### Ideal Team (Faster Delivery)
- **3x Backend Engineers** (split: agents, integrations, infrastructure)
- **2x Frontend Engineers** (dashboard, real-time layer)
- **1x DevOps Engineer** (full-time)
- **1x QA Engineer** (full-time)
- **1x Project Manager** (coordination, dependencies)

---

## Phase 1: FOUNDATION (Week 1-3) - Database & Schema

### Week 1: Database Cleanup & Migration

**Monday-Tuesday: Staging Validation**
- [ ] Run migrations 011 & 012 on staging database
- [ ] Execute VERIFICATION_QUERIES.sql
- [ ] Verify all 9 unused tables removed
- [ ] Confirm no foreign key violations
- [ ] Test application still works with cleaned schema
- [ ] Document any issues, create fixes

**Wednesday: Production Migration**
- [ ] Backup production database (snapshot)
- [ ] Run migration 011 (fix conflicts)
- [ ] Verify: agent_recommendations has correct schema
- [ ] Verify: agent_trust_scores has workspace_id
- [ ] Run migration 012 (remove tables)
- [ ] Final verification: 38 active tables remain
- [ ] Monitor application logs (30 min)

**Thursday-Friday: Verification & Testing**
- [ ] Run full test suite (move creation, campaign planning, content gen)
- [ ] Spot-check key endpoints
- [ ] Load test: simulate 100 concurrent users
- [ ] Validate no data loss occurred
- [ ] Update database documentation

**Deliverables**: ✅ Clean 38-table schema ready for Codex

---

### Week 2: Codex Schema Creation (Migrations 013-017)

**Migration 013: Positioning & Campaigns** (100 lines)
```sql
CREATE TABLE positioning (
  id uuid PRIMARY KEY,
  workspace_id uuid REFERENCES workspaces(id),
  for_cohort_id uuid REFERENCES cohorts(id),
  problem_statement text,
  category_frame text,
  differentiator text,
  reason_to_believe text,
  competitive_alternative text,
  is_active boolean DEFAULT false,
  created_at timestamp DEFAULT NOW()
);

CREATE TABLE message_architecture (
  id uuid PRIMARY KEY,
  positioning_id uuid REFERENCES positioning(id),
  primary_claim text NOT NULL,
  proof_points jsonb,
  created_at timestamp DEFAULT NOW()
);

CREATE TABLE campaigns (
  id uuid PRIMARY KEY,
  workspace_id uuid REFERENCES workspaces(id),
  name text NOT NULL,
  positioning_id uuid REFERENCES positioning(id),
  objective_type text CHECK (objective_type IN ('awareness', 'consideration', 'conversion')),
  budget numeric,
  start_date date,
  end_date date,
  status text DEFAULT 'planning',
  created_at timestamp DEFAULT NOW()
);

CREATE TABLE campaign_quests (
  id uuid PRIMARY KEY,
  campaign_id uuid REFERENCES campaigns(id),
  title text,
  chapters jsonb,
  estimated_conversion_rate numeric(5,4),
  estimated_roi numeric(6,2),
  created_at timestamp DEFAULT NOW()
);

CREATE TABLE campaign_cohorts (
  campaign_id uuid REFERENCES campaigns(id),
  cohort_id uuid REFERENCES cohorts(id),
  PRIMARY KEY (campaign_id, cohort_id)
);

-- Add foreign keys to existing tables
ALTER TABLE moves ADD COLUMN IF NOT EXISTS campaign_id uuid REFERENCES campaigns(id);
ALTER TABLE assets ADD COLUMN IF NOT EXISTS move_id uuid REFERENCES moves(id);
```

**Migration 014: Gamification & Achievements** (80 lines)
```sql
CREATE TABLE achievements (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid REFERENCES workspaces(id),
  code varchar(50) UNIQUE NOT NULL,
  name varchar(100),
  xp_value int DEFAULT 100,
  icon_url text
);

CREATE TABLE user_achievements (
  user_id uuid REFERENCES auth.users(id),
  achievement_id uuid REFERENCES achievements(id),
  unlocked_at timestamp DEFAULT NOW(),
  PRIMARY KEY (user_id, achievement_id)
);

CREATE TABLE user_stats (
  user_id uuid PRIMARY KEY REFERENCES auth.users(id),
  workspace_id uuid REFERENCES workspaces(id),
  current_streak int DEFAULT 0,
  total_xp int DEFAULT 0,
  level int DEFAULT 1,
  last_milestone_at timestamp
);
```

**Migration 015: Agent Registry & Memory** (90 lines)
```sql
CREATE TABLE agents (
  id varchar(20) PRIMARY KEY,
  name varchar(100),
  guild varchar(20),
  tier varchar(20),
  model varchar(100),
  status varchar(20) DEFAULT 'IDLE',
  last_heartbeat timestamp DEFAULT NOW(),
  write_access_tables text[],
  created_at timestamp DEFAULT NOW()
);

CREATE TABLE memories (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id varchar(20) REFERENCES agents(id),
  content text,
  embedding vector(1536),
  metadata jsonb,
  tags text[],
  created_at timestamp DEFAULT NOW()
);

-- Populate initial agent registry
INSERT INTO agents VALUES
  ('LORD-001', 'The Architect', 'COUNCIL', 'SUPERVISOR', NULL, 'ACTIVE', NOW(), ARRAY['agents', 'emergency_actions']),
  ('LORD-002', 'Cognition', 'COUNCIL', 'SUPERVISOR', 'o1-preview', 'ACTIVE', NOW(), ARRAY['war_briefs', 'research_vectors']),
  ('LORD-003', 'Strategos', 'COUNCIL', 'SUPERVISOR', 'o1-preview', 'ACTIVE', NOW(), ARRAY['campaign_quests', 'strategy_simulations']),
  -- ... etc for all 70+ agents
;
```

**Migration 016: Intelligence & Alerts** (110 lines)
```sql
CREATE TABLE war_briefs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  campaign_id uuid REFERENCES campaigns(id),
  content jsonb,
  generated_by varchar(20),
  confidence_score numeric(3,2),
  token_cost int,
  created_at timestamp DEFAULT NOW()
);

CREATE TABLE intelligence_logs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid REFERENCES workspaces(id),
  signal_type varchar(50),
  source varchar(50),
  content jsonb,
  relevance_score numeric(3,2),
  sentiment numeric(4,2),
  severity varchar(20),
  created_at timestamp DEFAULT NOW()
);

CREATE TABLE alerts_log (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid REFERENCES workspaces(id),
  alert_type varchar(50),
  severity varchar(20),
  content jsonb,
  action_required boolean DEFAULT false,
  created_at timestamp DEFAULT NOW()
);

CREATE TABLE trend_velocity_metrics (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid REFERENCES workspaces(id),
  trend_name varchar(200),
  velocity numeric(10,2),
  acceleration numeric(10,2),
  newsjack_opportunity_score numeric(3,2),
  created_at timestamp DEFAULT NOW()
);
```

**Migration 017: RLS Policies & Indexes** (150 lines)
```sql
-- Row-Level Security Policies

-- positioning - workspace isolation
ALTER TABLE positioning ENABLE ROW LEVEL SECURITY;
CREATE POLICY positioning_workspace_isolation
  ON positioning USING (workspace_id = get_user_workspace_id());

-- campaigns - workspace isolation
ALTER TABLE campaigns ENABLE ROW LEVEL SECURITY;
CREATE POLICY campaigns_workspace_isolation
  ON campaigns USING (workspace_id = get_user_workspace_id());

-- war_briefs - workspace isolation
ALTER TABLE war_briefs ENABLE ROW LEVEL SECURITY;
CREATE POLICY war_briefs_workspace_isolation
  ON war_briefs USING (
    campaign_id IN (
      SELECT id FROM campaigns WHERE workspace_id = get_user_workspace_id()
    )
  );

-- intelligence_logs - workspace isolation
ALTER TABLE intelligence_logs ENABLE ROW LEVEL SECURITY;
CREATE POLICY intelligence_logs_workspace_isolation
  ON intelligence_logs USING (workspace_id = get_user_workspace_id());

-- Indexes for Performance

-- Positioning queries
CREATE INDEX idx_positioning_workspace ON positioning(workspace_id);
CREATE INDEX idx_positioning_cohort ON positioning(for_cohort_id);

-- Campaign queries
CREATE INDEX idx_campaigns_workspace ON campaigns(workspace_id);
CREATE INDEX idx_campaigns_positioning ON campaigns(positioning_id);
CREATE INDEX idx_campaigns_status ON campaigns(status);

-- Intelligence queries
CREATE INDEX idx_intelligence_workspace_type ON intelligence_logs(workspace_id, signal_type);
CREATE INDEX idx_intelligence_created ON intelligence_logs(created_at DESC);

-- Agent queries
CREATE INDEX idx_agents_guild ON agents(guild);
CREATE INDEX idx_memories_agent ON memories(agent_id);
CREATE INDEX idx_memories_embedding ON memories USING ivfflat(embedding vector_cosine_ops);
```

**Execution** (Thursday-Friday)
- [ ] Run migrations 013-017 on staging
- [ ] Verify all tables created successfully
- [ ] Test RLS policies (query from different users)
- [ ] Verify indexes created
- [ ] Run staging application with new schema
- [ ] Run migrations 013-017 on production
- [ ] Monitor migration logs

**Deliverables**: ✅ 68-table schema with all Codex tables + RLS policies + indexes

---

### Week 3: Initialize Agent Registry & RAG System

**Agent Registry Population**
- [ ] Create `backend/agents/registry.py` - populate 70+ agent definitions
- [ ] Load into agents table (name, guild, model, write_access)
- [ ] Initialize heartbeat expectation (all agents should ping within 30s)
- [ ] Create admin dashboard to view agent status

**RAG System Initialization**
- [ ] Set up ChromaDB instance
- [ ] Embed Codex specification (70 pages)
- [ ] Embed initial message architecture library
- [ ] Create RAG retrieval service (`backend/services/rag_manager.py`)
- [ ] Test retrieval: "positioning for SaaS" → returns similar positioning statements

**Data Validation**
- [ ] Run full data integrity checks
- [ ] Verify all foreign key relationships
- [ ] Backup final schema state
- [ ] Document schema version (v1.0)

**Deliverables**: ✅ Agent registry initialized, RAG system ready

---

## Phase 2A: COUNCIL OF LORDS (Week 4-7)

### Week 4: Base Classes & LORD-001 (The Architect)

**Monday-Tuesday: Base Classes**
```python
# backend/agents/lords/base_lord.py
class BaseLord(BaseAgent):
  - lord_id: str
  - guild_id: Optional[str]
  - write_access_tables: List[str]
  - budget_tokens_remaining: int
  - async publish_heartbeat()
  - async command_guild(guild_name, task)
  - async emergency_stop_guild(guild_name)
```

**Wednesday-Friday: LORD-001 Implementation**
```python
# backend/agents/lords/architect.py
class TheArchitect(BaseLord):
  - Monitor sys.global.heartbeat (all agents)
  - Detect frozen/crashed agents (3+ missed beats)
  - Auto-restart hung agents
  - Maintain agent registry
  - Emergency resource cleanup

Tools:
  - manage_graph_state()
  - restart_guild(guild_id)
  - emergency_flush_memory()
```

**Testing**:
- [ ] Unit tests: heartbeat monitoring
- [ ] Integration test: detect missed heartbeats, auto-restart
- [ ] Load test: 70 agents sending heartbeats simultaneously

**Deliverables**: ✅ BASE_LORD class, LORD-001 Architect operational

---

### Week 5: LORD-002 (Cognition) & LORD-003 (Strategos)

**LORD-002: Cognition** (Research aggregator)
```python
class Cognition(BaseLord):
  - Command Research Guild (RES-001 to RES-020)
  - Aggregate "War Briefs" from research data
  - Enforce token budgets
  - Model: o1-preview
  - Write access: war_briefs, research_vectors

Main method:
  - async synthesize_war_brief(campaign_id) → JSONB
```

**LORD-003: Strategos** (Strategy & simulation)
```python
class Strategos(BaseLord):
  - Generate Quests from War Briefs
  - Run Monte Carlo simulations
  - Predict conversion rates
  - Model: o1-preview
  - Write access: campaign_quests, strategy_simulations

Main method:
  - async generate_campaign_quest(war_brief) → quest_structure
```

**Testing**:
- [ ] Unit: War Brief synthesis
- [ ] Unit: Quest generation from War Brief
- [ ] Integration: Research Guild → Cognition → Strategos pipeline
- [ ] End-to-end: Campaign created → Research triggered → War Brief generated → Quest created

**Deliverables**: ✅ LORD-002 & LORD-003 operational, full campaign pipeline

---

### Week 6: LORD-004 (Aesthete) & LORD-005 (Seer)

**LORD-004: Aesthete** (Creative Director)
```python
class Aesthete(BaseLord):
  - Command Muse Guild (MUS-001 to MUS-030)
  - Orchestrate asset generation (text, visual, video)
  - Enforce brand consistency
  - Validate images against brand guidelines
  - Model: gemini-1.5-pro
  - Write access: creative_assets, canva_designs

Main method:
  - async orchestrate_asset_generation(war_brief) → List[Asset]
```

**LORD-005: Seer** (Intelligence Chief)
```python
class Seer(BaseLord):
  - Command Matrix Guild (MAT-001 to MAT-020)
  - Detect newsjacking opportunities
  - Trigger alerts on sentiment shifts
  - Monitor competitor activities
  - Model: gemini-1.5-flash
  - Write access: alerts_log, trend_velocity_metrics

Main method:
  - async monitor_signals() → listens to Matrix broadcasts
```

**Testing**:
- [ ] Aesthete: asset generation with creative brief
- [ ] Seer: signal processing and alert routing
- [ ] Integration: Newsjack opportunity detection

**Deliverables**: ✅ LORD-004 & LORD-005 operational

---

### Week 7: LORD-006 (Arbiter) & LORD-007 (Herald)

**LORD-006: Arbiter** (Compliance Officer)
```python
class Arbiter(BaseLord):
  - Command Guardian Agents (GRD-001 to GRD-010)
  - Enforce platform limits
  - Validate content (no hallucinations, banned terms)
  - Write access: approval_flags, content_audit_log

Main method:
  - async validate_content_for_platform(content, platform) → approval_status
```

**LORD-007: Herald** (Gamification Bridge)
```python
class Herald(BaseLord):
  - Monitor campaign completions
  - Trigger achievement unlocks
  - Award XP and level-ups
  - Generate narrative updates
  - Model: llama-3.1-70b (via Groq)
  - Write access: user_achievements, notifications, user_stats

Main method:
  - async monitor_completions() → listens to completion events
```

**Testing**:
- [ ] Arbiter: content validation gates
- [ ] Herald: achievement unlocks, XP awards
- [ ] Integration: Campaign completion → Achievement → WebSocket notification

**Deliverables**: ✅ All 7 Lords operational

---

## Phase 2B: RESEARCH GUILD (Week 8-11)

### Week 8: RES-001 to RES-007 (Research Foundation)

Implement first 7 research agents in parallel:

```python
# backend/agents/research/

RES-001: Competitor Spy
  - Monitor competitor pricing pages
  - Detect changes via hash comparison
  - Input: competitor domains
  - Output: price_change_alerts
  - Tools: SerperDev, SHA-256

RES-002: SEO Archaeologist
  - Find zero-volume, high-intent keywords
  - Input: industry keywords
  - Output: keyword_opportunities JSONB
  - Tools: Ahrefs/SEMrush API, keyword_clustering

RES-003: Trend Surfer
  - Correlate Google Trends with events
  - Input: trend keywords
  - Output: timing_recommendations
  - Tools: Google Trends API

RES-004: Voice of Customer
  - Scrape G2/Capterra reviews
  - Extract pain points
  - Input: product category
  - Output: customer_pain_points_analysis
  - Tools: G2 Scraper, sentiment_analysis

RES-005: Shadow Cartographer
  - CRM email analysis for decision influencers
  - Input: email inbox (if available)
  - Output: influencer_map
  - Tools: Email API, NER

RES-006: Tech Stack Detective
  - BuiltWith API for competitor tech
  - Input: competitor domains
  - Output: tech_stack_analysis
  - Tools: BuiltWith API

RES-007: Influencer Scout
  - Find micro-influencers in niche
  - Input: industry keywords
  - Output: influencer_profiles
  - Tools: Social Graph API, follower_analytics
```

**Testing**:
- [ ] Unit: Each agent processes sample input correctly
- [ ] Integration: All 7 agents publish results to research guild channel
- [ ] Load: All 7 running simultaneously without blocking

**Deliverables**: ✅ RES-001 to RES-007 operational (7/20 agents)

---

### Week 9: RES-008 to RES-015 (Expansion)

Continue with next 8 agents:

```python
RES-008: Content Auditor (site crawling, content calendar)
RES-009: Sentiment Miner (social sentiment analysis)
RES-010: Backlink Hunter (high-authority backlinks)
RES-011: UX Critiquer (Selenium + vision model for UX)
RES-012: News Junkie (NewsAPI for trends)
RES-013: Forum Lurker (Discourse/Reddit for Q&A)
RES-014: Patent Watcher (USPTO API)
RES-015: Pricing Analyst (pricing page scraper)
```

**Parallel Work**: Start RES-020 (Synthesis Engine)
- Receives outputs from all 15+ agents
- Calls o1-preview to synthesize
- Generates structured War Brief
- Stores to war_briefs table

**Testing**:
- [ ] All 15 agents operational
- [ ] RES-020 synthesis aggregates correctly
- [ ] War Brief generation tested with sample data

**Deliverables**: ✅ RES-001 to RES-020 operational (20/20 agents)

---

### Week 10: RES-016 to RES-020 (Completion)

Complete final 5 agents:

```python
RES-016: Ad Creative Spy (FB Ad Library + Vision)
RES-017: Persona Simulator (simulated buyer interactions)
RES-018: Keyword Clusterer (Pandas/SciKit clustering)
RES-019: Offer Deconstructor (funnel reverse engineering)
RES-020: Synthesis Engine (already started in Week 9)
```

**Maniacal Onboarding Graph**
- Implement 12-step deterministic workflow:
  1. DNS verification (RES-006)
  2. Brand voice calibration (RES-008)
  3. Competitor identification (RES-002)
  4. Technographic profiling (RES-006)
  5. Social footprint mapping (RES-001)
  6. Review ingestion (RES-004)
  7. Pain point extraction (RES-020)
  8. Keyword gap analysis (RES-002)
  9. ICP hypothesis (RES-005)
  10. Content audit (RES-008)
  11. Visual baseline (RES-011)
  12. War brief generation (LORD-002)

**Testing**:
- [ ] Onboarding graph completes all 12 steps
- [ ] Resume capability from any step
- [ ] War Brief generated at end

**Deliverables**: ✅ Research Guild complete, Maniacal Onboarding operational

---

### Week 11: Integration & Testing

**Research Guild Integration Tests**
- [ ] Test full pipeline: New campaign → trigger onboarding → generate war brief
- [ ] Test parallelization: 20 agents running simultaneously
- [ ] Test cost tracking: tokens logged per agent
- [ ] Test error handling: agent crash doesn't cascade

**Performance Optimization**
- [ ] Profile agent execution times
- [ ] Identify bottlenecks
- [ ] Cache frequently-used data (competitor profiles, keyword lists)
- [ ] Optimize API calls (batch where possible)

**Documentation**
- [ ] Document each RES agent's purpose, tools, inputs, outputs
- [ ] Create troubleshooting guide
- [ ] Document cost per research cycle

**Deliverables**: ✅ Research Guild production-ready

---

## Phase 2C: MUSE & MATRIX GUILDS (Week 12-15)

### Week 12: Muse Guild Foundation (MUS-001 to MUS-010)

**Text-Based Agents** (in parallel):
```python
MUS-001: Headline Smith (viral hooks, model: claude-haiku)
MUS-002: Long-Form Weaver (SEO articles, model: claude-sonnet)
MUS-003: Micro-Copy Poet (UI text, model: claude-haiku)
MUS-004: Email Persuader (email sequences, model: claude-sonnet)
MUS-005: Thread Spinner (Twitter threads, model: claude-haiku)
MUS-006: Script Wright (video scripts, model: claude-sonnet)
MUS-007: Case Study Historian (success stories, model: claude-sonnet)
MUS-008: Press Release Scribe (AP style, model: claude-haiku)
MUS-009: Technical Writer (documentation, model: claude-haiku)
MUS-010: Sloganist (taglines, model: claude-haiku)
```

**Debate Orchestrator**
```python
# backend/workflows/debate_orchestrator.py
1. MUS-002 generates Draft_V1
2. Panel critique: [MUS-026 Editor, RES-002 SEO, LORD-006 Arbiter]
3. Aggregate feedback (scored 1-10)
4. If score < 8: MUS-002 revises
5. Loop max 3 iterations
6. Output approved asset
```

**Testing**:
- [ ] Each text agent generates quality output
- [ ] Debate orchestrator improves draft quality
- [ ] Iteration limit prevents infinite loops

**Deliverables**: ✅ MUS-001 to MUS-010 + debate orchestrator

---

### Week 13: Muse Guild Expansion (MUS-011 to MUS-030)

**Visual Agents** (MUS-011 to MUS-020):
```python
MUS-011: Prompt Engineer (Midjourney prompts)
MUS-012: Prompt Engineer (DALL-E prompts)
MUS-013: SVG Architect (vector icons)
MUS-014: Layout Master (CSS/HTML layouts)
MUS-015: Color Theorist (color palette generation)
MUS-016: Infographic Designer (chart structures)
MUS-017: Thumbnail Artist (YouTube thumbnails)
MUS-018: Meme Lord (viral memes)
MUS-019: Brand Guardian (visual consistency check)
MUS-020: Slide Deck Designer (presentation outlines)
```

**Video/Audio Agents** (MUS-021 to MUS-025):
```python
MUS-021: Storyboarder (shot lists)
MUS-022: Audio Director (music selection)
MUS-023: Voiceover Caster (TTS configuration)
MUS-024: Clip Cutter (viral moment extraction)
MUS-025: B-Roll Hunter (stock footage search)
```

**Strategy Agents** (MUS-026 to MUS-030):
```python
MUS-026: The Editor (grammar, flow)
MUS-027: The Optimizer (SEO tweaks)
MUS-028: The Localizer (translations)
MUS-029: A/B Tester (variant generation)
MUS-030: The Archivist (asset tagging)
```

**Repurpose Engine**
```python
# backend/workflows/repurpose_engine.py
Video → Text (Whisper → Blog)
Video → Social (Clip Cutter → TikTok)
Text → Visual (Pull Quote → Instagram Card)
Tracks derived_assets with parent_id lineage
```

**Canva Integration**
```python
# backend/services/canva_service.py
- trigger_autofill(brand_template_id, dataset)
- poll_job_status(job_id)
- export_design(design_id, format)
```

**Testing**:
- [ ] All 30 Muse agents operational
- [ ] Repurpose engine transforms assets correctly
- [ ] Canva integration creates designs

**Deliverables**: ✅ Muse Guild complete (30/30 agents)

---

### Week 14: Matrix Guild (MAT-001 to MAT-020)

**Real-Time Agents** (running 24/7):
```python
MAT-001: Google News Watcher (NewsAPI, 15min interval)
MAT-002: Twitter Streamer (real-time streaming)
MAT-003: Reddit Monitor (PRAW, 1hr interval)
MAT-004: Competitor Site Tracker (ChangeDetection.io, 6hr)
```

**Signal Processing Pipeline**
```
Raw Signal (Tweet/News)
  ↓
Relevance Filter (verified user? followers > 500?)
  ↓
Enrichment (is user a customer?)
  ↓
Sentiment Analysis (VADER, TextBlob)
  ↓
Routing:
  - Crisis (sentiment < -0.8) → sys.alert.critical
  - Opportunity (sentiment > 0.8, followers > 10k) → LORD-005
  - Standard → intelligence_logs
```

**Batch Agents** (nightly runs):
```python
MAT-009: Keyword Volatility (SEMrush, daily)
MAT-013: Podcast Transcriber (Whisper, weekly)
MAT-014-020: Various batch intelligence jobs
```

**Testing**:
- [ ] Real-time agents streaming correctly
- [ ] Signal processing routes correctly
- [ ] Batch jobs complete nightly

**Deliverables**: ✅ Matrix Guild complete (20/20 agents)

---

### Week 15: Guardian Guild (GRD-001 to GRD-010)

**Platform-Specific Enforcers**:
```python
GRD-TW: Twitter (280 char, banned terms)
GRD-LI: LinkedIn (3000 char, "See More" optimization)
GRD-IG: Instagram (aspect ratio, 30 hashtag limit)
GRD-FB: Facebook (link preview validation)
GRD-YT: YouTube (title/desc length)
GRD-TT: TikTok (music licensing)
GRD-PIN: Pinterest (2:3 aspect ratio)
GRD-MED: Medium (canonical links)
GRD-RED: Reddit (subreddit rules)
GRD-THR: Threads (500 char limit)
```

**Validation Pipeline**:
```python
class Arbiter:
  1. Guardian validates format
  2. Check hallucinations
  3. Verify URLs
  4. Audit logging
  5. Approval gate (manual if high-risk)
```

**Testing**:
- [ ] All 10 Guardians validate correctly
- [ ] Content rejected for format violations
- [ ] Approval workflow functional

**Deliverables**: ✅ All 70+ agents operational + RaptorBus communication

---

## Phase 3: FRONTEND INTEGRATION (Week 16-18)

### Week 16: Real-Time Layer & Kingdom Dashboard

**WebSocket Real-Time Layer**
```python
# backend/routers/websocket.py
@app.websocket("/ws/dashboard/{user_id}")
async def websocket_endpoint(websocket):
  - Connect user
  - Subscribe to state updates
  - Broadcast events: campaign_created, asset_generated, alert_newsjack, achievement_unlocked
  - Monitor agent heartbeats
```

**Kingdom Dashboard** (redesign)
```
Sections:
├─ Kingdom Wealth (revenue, traffic, leads - metrics)
├─ The Barracks (agent status widget)
│  ├─ 7 Lords heartbeat
│  ├─ Guild status (research/muse/matrix/guardians)
│  └─ Failed agents alerting
├─ Quests in Progress (active campaigns)
├─ Recent Achievements (XP gains, level-ups)
└─ Alerts from Matrix Guild
```

**Frontend Components**:
```jsx
// React components (TypeScript)
<KingdomThrone /> - Main dashboard layout
<AgentStatusWidget /> - Real-time lord/guild status
<QuestProgressBar /> - Campaign progress
<AchievementToast /> - XP/achievement notifications
<MatrixAlertsPanel /> - Crisis/opportunity alerts
```

**Testing**:
- [ ] WebSocket connects and receives events
- [ ] Real-time updates show immediately
- [ ] Agent status updates every 30s
- [ ] No memory leaks on long-lived connections

**Deliverables**: ✅ Real-time Kingdom Dashboard

---

### Week 17: Campaign & Content Workflow UIs

**Positioning Workshop** (5-step wizard)
```
Step 1: For Whom? (target cohort, decision makers)
Step 2: What Problem? (core pain point)
Step 3: Why Us? (unique capability)
Step 4: Proof? (evidence, testimonials)
Step 5: Message Architecture (tagline, elevator pitch, narrative)
```

**Campaign Builder** (5-step wizard)
```
Step 1: Strategic Foundation (select positioning)
Step 2: Campaign Definition (objective, timeline)
Step 3: Channel Strategy (channel roles, budget)
Step 4: Move Planning (auto-suggested moves)
Step 5: Asset Requirements (creative briefs)
```

**Muse Studio** (asset creation interface)
```
Features:
├─ Asset gallery with filters
├─ Version history per asset
├─ Debate/revision comments
├─ Live Canva template preview
├─ Bulk export to social platforms
```

**Enhanced Cohorts UI**
```
New Fields:
├─ Buying Triggers (timed events)
├─ Decision Criteria (weighted factors)
├─ Objection Map (objection → response)
├─ Attention Windows (best contact times)
├─ Competitive Frame (who they compare to)
├─ Journey Distribution (% at each stage)
```

**Testing**:
- [ ] All wizards complete 5 steps
- [ ] Data saved to Supabase correctly
- [ ] Workflows trigger agent execution
- [ ] Assets display correctly

**Deliverables**: ✅ All UI workflows functional

---

### Week 18: Radar Module & Final Integration

**Radar Module** (live 2D intelligence dashboard)
```
Features:
├─ Competitive positioning map (D3.js)
├─ Real-time alert notifications
├─ Trend velocity visualizations
├─ Newsjack opportunity banners
└─ Live sentiment gauge
```

**WebSocket Integration**:
```
Events:
├─ campaign:created - highlight in sidebar
├─ asset:generated - notify in Muse
├─ alert:newsjack - critical banner
├─ achievement:unlocked - overlay + XP animation
├─ agent:status_changed - update Barracks widget
```

**Gamification Frontend**:
```
Components:
├─ XP Progress Bar
├─ Level Badge
├─ Achievement Showcase
├─ Streak Counter
├─ Milestone Notifications
```

**Final Integration Testing**:
- [ ] End-to-end: Create campaign → Research → War Brief → Assets → Publish
- [ ] Real-time: All WebSocket events propagate correctly
- [ ] Performance: Dashboard loads in < 2s, WebSocket latency < 100ms
- [ ] Mobile: Responsive design on all screens

**Deliverables**: ✅ Complete frontend integrated with all backend systems

---

## Phase 4: TESTING & LAUNCH (Week 19-22)

### Week 19: Comprehensive Testing

**Unit Tests**:
- [ ] All 70+ agents have unit tests
- [ ] Core services tested
- [ ] Utility functions covered
- Target: 85%+ code coverage

**Integration Tests**:
- [ ] Full campaign pipeline: create → research → quest → assets
- [ ] Onboarding workflow: all 12 steps complete
- [ ] Real-time layer: WebSocket events fire correctly
- [ ] Database: RLS policies enforce workspace isolation

**Load Tests**:
- [ ] 100 concurrent users on dashboard
- [ ] 50 simultaneous campaigns being created
- [ ] 1000 agents sending heartbeats
- [ ] Real-time WebSocket with 500 connected clients

**End-to-End Tests** (Selenium/Cypress):
- [ ] User signs up → Onboarding → Creates campaign → Sees results
- [ ] Real-time alerts trigger and display
- [ ] Gamification: achievements unlock with XP
- [ ] Mobile: responsive layouts work correctly

**Deliverables**: ✅ All test suites passing, 85%+ coverage

---

### Week 20: Performance Optimization

**Profiling & Optimization**:
- [ ] Profile agent execution times
- [ ] Identify slow database queries
- [ ] Optimize N+1 queries
- [ ] Add strategic caching

**Token Cost Analysis**:
- [ ] Simulate 1000 campaigns
- [ ] Measure total token consumption
- [ ] Verify < $10/user/month target
- [ ] Adjust models if needed

**Database Performance**:
- [ ] Verify indexes are used
- [ ] Check query plans
- [ ] Optimize hot paths
- [ ] Validate RLS policy performance

**Frontend Optimization**:
- [ ] Bundle size analysis
- [ ] Lazy loading components
- [ ] Image optimization
- [ ] Target Lighthouse 90+

**Deliverables**: ✅ Production-optimized system

---

### Week 21: Security & Compliance Audit

**Security Review**:
- [ ] RLS policies enforce workspace isolation (test bypasses)
- [ ] API authentication/authorization working
- [ ] No SQL injection vulnerabilities
- [ ] Sensitive data encrypted at rest
- [ ] Environment variables secure

**Compliance Checks**:
- [ ] GDPR: data deletion possible
- [ ] Data retention policies enforced
- [ ] Audit logging comprehensive
- [ ] Terms of Service updated

**Infrastructure Security**:
- [ ] Network isolation (VPC)
- [ ] SSL/TLS for all connections
- [ ] Rate limiting configured
- [ ] DDoS protection enabled

**Deliverables**: ✅ Security audit passed

---

### Week 22: Documentation & Launch Prep

**User Documentation**:
- [ ] Getting started guide
- [ ] Campaign workflow tutorial
- [ ] Positioning workshop guide
- [ ] Video walkthroughs

**Developer Documentation**:
- [ ] API documentation (Swagger)
- [ ] Agent architecture guide
- [ ] Database schema documentation
- [ ] Deployment runbook

**Operational Runbooks**:
- [ ] Incident response procedures
- [ ] Agent monitoring/alerts
- [ ] Cost tracking dashboard
- [ ] Performance monitoring

**Launch Checklist**:
- [ ] DNS configured
- [ ] SSL certificates installed
- [ ] Analytics tracking enabled
- [ ] Error monitoring (Sentry) configured
- [ ] Backup procedures in place
- [ ] Team trained on operations
- [ ] Customer support ready
- [ ] Marketing collateral prepared

**Deliverables**: ✅ All documentation complete, ready for launch

---

## Post-Launch (Week 23+)

### Week 23-26: Monitoring & Iteration

**Monitoring**:
- [ ] Agent execution metrics
- [ ] User engagement metrics
- [ ] Token cost tracking
- [ ] Error rate monitoring

**Iteration**:
- [ ] Bug fixes from production
- [ ] User feedback integration
- [ ] Performance tuning
- [ ] New feature requests

---

## Success Metrics (At Launch)

### Technical
- ✅ All 70+ agents operational
- ✅ < 30s campaign creation to war brief
- ✅ < 100ms WebSocket latency
- ✅ 99.9% uptime target
- ✅ < 1s frontend page load

### Business
- ✅ $10/user/month cost target achieved
- ✅ 50+ campaigns created (beta testing)
- ✅ 100% user retention (no bugs)
- ✅ Positive customer feedback

### Quality
- ✅ 85%+ test coverage
- ✅ Security audit passed
- ✅ Performance optimized
- ✅ Full documentation

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| External API failures (SEMrush, Ahrefs) | Medium | High | Mock APIs in dev, fallback strategies |
| Token cost overrun | Medium | Medium | Aggressive caching, model optimization |
| Agent coordination issues | Low | Medium | Extensive testing, RaptorBus stress tests |
| Database scaling issues | Low | High | Index optimization, query profiling |
| Real-time WebSocket issues | Low | Medium | Load testing, connection pooling |

---

## Team Accountability

### Backend Lead
- Owns: Agent implementation, RaptorBus integration, database schema
- Weekly: Report agent completion %, token usage, issues

### Frontend Lead
- Owns: UI workflows, WebSocket integration, real-time updates
- Weekly: Report UI completion %, performance metrics, UX feedback

### Infrastructure Lead
- Owns: Database, Redis, deployment pipeline, monitoring
- Weekly: Report uptime %, cost tracking, performance

### QA Lead
- Owns: Testing, security audit, performance profiling
- Weekly: Report test coverage %, critical issues, optimization wins

---

## Weekly Standup Cadence

**Monday 9 AM**: Weekly planning
- Review previous week progress
- Identify blockers
- Adjust priorities

**Wednesday 2 PM**: Mid-week sync
- Quick status update
- Address blockers

**Friday 4 PM**: Week wrap-up
- Celebrate wins
- Plan next week
- Update metrics

---

## This Week (Week 1) - Database Cleanup

**Your Immediate Tasks**:

1. **Monday**: Understand cleanup migrations (011 & 012)
2. **Tuesday**: Run on staging, verify, test application
3. **Wednesday**: Run on production, monitor
4. **Thursday-Friday**: Run full test suite, validate data integrity

**Success Criteria**:
- ✅ 9 unused tables removed
- ✅ 3 schema conflicts resolved
- ✅ 38 active tables remain
- ✅ All application endpoints working
- ✅ Zero data loss

**Next Week**: Start Week 2 (Codex Schema Creation)

---

## Go Live Timeline

```
Week 1: Database ready ✓
Week 2: Schema ready ✓
Week 3: Agent registry initialized ✓
Week 4-7: Lords operational ✓
Week 8-11: Research Guild 100% ✓
Week 12-15: Muse, Matrix, Guardians 100% ✓
Week 16-18: Frontend integrated ✓
Week 19-22: Testing, optimization, launch prep ✓
Week 23: PRODUCTION LAUNCH 🚀
```

**Launch Date**: ~6 months from start

**Post-Launch**: Continuous iteration, scale to 1000+ users

---

**You've got this. Let's build the future of marketing automation. 🚀**
