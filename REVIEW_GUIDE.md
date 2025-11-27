# RaptorFlow Codex Implementation - Complete Review Guide

**Purpose**: Understand the full 90-yard Codex integration before proceeding to Phase 2+

**Reading Time**: 30-45 minutes

---

## Navigation Guide

### 🎯 Start Here (Quick Overview - 5 min)
1. Read this section
2. Check Phase 1 Summary below

### 📚 Architecture & Design (15 min)
1. `CODEX_BLUEPRINT.md` - Sections I, II, III (Overview, Data Architecture, RaptorBus)
2. `RAPTORBUS_IMPLEMENTATION.md` - Architecture section

### 🏗️ System Components (20 min)
1. `CODEX_BLUEPRINT.md` - Sections IV, V, VI (Lords, RAG, Guilds)
2. Understand what each Lord does
3. Understand what each Guild does

### 💾 Database Cleanup (10 min)
1. `DATABASE_CLEANUP_STRATEGY.md` - Cleanup Opportunities section
2. `DATABASE_CLEANUP_COMPLETE.md` - What Gets Cleaned Up section

### 🔧 Implementation Readiness (10 min)
1. This Review Guide → Sections below
2. Assess feasibility for your team

---

## Phase 1 Summary (COMPLETED)

### What RaptorBus Does

**RaptorBus is the nervous system of the Codex.**

It enables 70+ agents to communicate without blocking each other:

```
Agent A publishes event → Redis channel
                       ↓
                 (stored for replay)
                       ↓
Agent B, C, D listen on channel
Agent E listens with pattern matching
       ↓
     (2 agents handle in parallel, 1 fails)
       ↓
Failed message → Dead Letter Queue
Success messages → Stored for audit
       ↓
Frontend WebSocket gets real-time update
       ↓
Dashboard shows: "Campaign created", "Alert: Crisis detected", "Achievement: +100 XP"
```

**Why it matters**:
- Non-blocking (agents don't wait for responses)
- Message persistence (replay capability)
- Fault isolation (one agent failure doesn't cascade)
- Real-time updates (frontend knows immediately)
- Cost-efficient (lightweight pub/sub vs request/response)

### 8 Channel Types

| Channel | Purpose | TTL | Subscribers |
|---------|---------|-----|-------------|
| `sys.global.heartbeat` | Agent health monitoring | 1 min | LORD-001 (Architect) |
| `sys.guild.research.*` | Research agent coordination | 1 hour | RES agents, LORD-002 |
| `sys.guild.muse.*` | Creative asset generation | 24 hours | MUS agents, LORD-004 |
| `sys.guild.matrix.*` | Intelligence gathering | 7 days | MAT agents, LORD-005 |
| `sys.guild.guardians.*` | Platform compliance | 7 days | GRD agents, LORD-006 |
| `sys.alert.critical` | Crisis/emergency | 24 hours | All Lords, dashboard |
| `sys.alert.warning` | Important notifications | 24 hours | Dashboard, alerts |
| `sys.state.update` | Frontend WebSocket events | 1 hour | Frontend subscribers |

### Real-World Flow Example

**User creates campaign:**
```
1. Frontend: POST /api/v1/campaigns
2. Backend validates, calls Master Orchestrator
3. MO publishes: "campaign.create_requested"
   → Channel: sys.guild.research.broadcast
   → Source: LORD-002
   → Payload: positioning, personas, budget
4. RES-001 (Competitor Spy) subscribes, starts research
5. RES-002 (SEO Archaeologist) subscribes, starts keyword analysis
6. RES-003, RES-004... all run in parallel
7. Each publishes back: "research.competitive_complete"
8. LORD-002 (Cognition) aggregates when all done
9. Calls o1-preview to synthesize "War Brief"
10. Stores War Brief to Supabase
11. Publishes: "state.campaign_created"
    → Channel: sys.state.update
12. Frontend WebSocket receives update
13. Dashboard shows new campaign + "Research phase: 89% complete"
```

**Total time**: ~30 seconds (vs sequential: ~5 minutes)

---

## The Seven Lords (Leadership Layer)

### Organizational Structure

```
The Council of Lords (7 high-level supervisors)
├─ LORD-001: The Architect
│   └─ Supervises: System health, agent lifecycle, emergency stops
├─ LORD-002: Cognition
│   └─ Commands: Research Guild (RES-001 to RES-020)
├─ LORD-003: Strategos
│   └─ Specializes in: Game theory, campaign simulation, strategic planning
├─ LORD-004: Aesthete
│   └─ Commands: Muse Guild (MUS-001 to MUS-030)
├─ LORD-005: Seer
│   └─ Commands: Matrix Guild (MAT-001 to MAT-020)
├─ LORD-006: Arbiter
│   └─ Commands: Guardian Guild (GRD-001 to GRD-010)
└─ LORD-007: Herald
    └─ Manages: Gamification, WebSocket events, achievements
```

### Key Concept: Write Access

**Lords have database write permissions**. Others don't.

This is critical for security:
- All agents PRODUCE data (events, messages)
- Only Lords PERSIST data (write to Supabase)
- All writes pass through RLS policies (row-level security)

**Example**:
- RES-001 finds competitor price change
- Publishes: "competitor.price_changed"
- LORD-002 receives, approves
- LORD-002 writes to `competitor_profiles` table
- RLS policy: ensures workspace isolation

---

## Four Guilds (Specialist Layers)

### Guild 1: Research (RES-001 to RES-020)

**Purpose**: Gather market intelligence

```
Data Sources:
├─ Ahrefs / SEMrush (keywords, backlinks)
├─ SerperDev (competitor monitoring)
├─ G2 / Capterra (customer reviews)
├─ NewsAPI (market trends)
├─ Twitter API (sentiment)
├─ Google Trends (search trends)
├─ USPTO (patents)
├─ Facebook Ad Library (competitor ads)
└─ Custom scrapers (websites, forums, patents)

Processing:
├─ RES-002: SEO Archaeologist → High-intent keywords
├─ RES-004: Voice of Customer → Pain points
├─ RES-006: Tech Stack Detective → Competitive tech
├─ RES-009: Sentiment Miner → Emotional intelligence
├─ RES-020: Synthesis Engine → Aggregate to "War Brief"

Output:
└─ War Brief: Structured intelligence for campaign planning
```

**Output Example**:
```json
{
  "market_analysis": {
    "tam": "$5.2B enterprise data management",
    "trends": ["AI-powered", "no-code", "real-time"],
    "competitive_landscape": {
      "direct": ["Palantir", "Databricks"],
      "indirect": ["Notion", "Airtable"]
    }
  },
  "persona_deep_dive": {
    "CTO_Enterprise": {
      "biggest_pain": "data silos",
      "decision_criteria": ["ease_of_use", "scalability", "security"],
      "objections": ["too complex", "expensive", "vendor lock-in"]
    }
  },
  "messaging_insights": {
    "top_value_props": ["unified data layer", "no-code pipelines"],
    "proof_points": ["used by Fortune 500", "3x faster than competitors"]
  }
}
```

### Guild 2: Muse (MUS-001 to MUS-030)

**Purpose**: Generate creative assets

```
Text Agents (MUS-001 to MUS-010):
├─ MUS-002: Long-Form Weaver (blog articles)
├─ MUS-004: Email Persuader (email sequences)
├─ MUS-005: Thread Spinner (Twitter threads)
└─ MUS-009: Technical Writer (documentation)

Visual Agents (MUS-011 to MUS-020):
├─ MUS-011: Prompt Engineer (Midjourney)
├─ MUS-016: Infographic Designer (data viz)
├─ MUS-017: Thumbnail Artist (YouTube)
└─ MUS-019: Brand Guardian (consistency check)

Strategy Agents (MUS-026 to MUS-030):
├─ MUS-026: The Editor (grammar, flow)
├─ MUS-027: The Optimizer (SEO tweaks)
└─ MUS-029: A/B Tester (variant generation)

Workflow:
1. MUS-002 generates blog draft
2. Panel critique: MUS-026 (grammar), RES-002 (SEO), LORD-006 (brand)
3. Feedback aggregated
4. MUS-002 revises (chain-of-thought)
5. Consensus gate (score > 8/10)
6. Output: Approved blog post
```

**Output**: Creative assets ready for publishing

### Guild 3: Matrix (MAT-001 to MAT-020)

**Purpose**: Real-time market signal detection

```
Real-Time Agents:
├─ MAT-001: Google News Watcher (NewsAPI, 15min)
├─ MAT-002: Twitter Streamer (real-time)
├─ MAT-003: Reddit Monitor (1 hour)
└─ MAT-004: Competitor Site Tracker (6 hours)

Processing:
├─ Relevance filter (verified users, followers > 500?)
├─ Enrichment (is user a customer?)
├─ Sentiment analysis (VADER + TextBlob)
└─ Routing decision:
    ├─ sentiment < -0.8 → sys.alert.critical (CRISIS)
    ├─ sentiment > 0.8 & followers > 10k → LORD-005 (OPPORTUNITY)
    └─ else → intelligence_logs (standard archival)

Output:
├─ Newsjack Opportunity: "AI for healthcare trending - respond within 60 min"
├─ Crisis Alert: "Customer complaint - sentiment -0.92"
└─ Competitor Move: "Competitor launched new feature"
```

**Key Feature**: Newsjacking
When trending topic detected:
1. MAT analyzes relevance
2. If applicable, alerts with suggested response
3. Team can approve/reject in < 5 minutes
4. LORD-004 (Aesthete) generates rapid-response assets
5. LORD-006 (Arbiter) validates compliance
6. Published within 30 minutes of trend start

### Guild 4: Guardians (GRD-001 to GRD-010)

**Purpose**: Platform compliance enforcement

```
Per-Platform Enforcers:
├─ GRD-TW: Twitter (280 char limit, banned terms)
├─ GRD-IG: Instagram (aspect ratio, 30 hashtag limit)
├─ GRD-LI: LinkedIn (3000 char, "See More" optimization)
├─ GRD-YT: YouTube (title/desc length)
├─ GRD-FB: Facebook (link preview validation)
├─ GRD-TT: TikTok (music licensing)
├─ GRD-PIN: Pinterest (2:3 aspect ratio)
├─ GRD-RED: Reddit (subreddit rules)
└─ GRD-MED: Medium (canonical links)

Validation Gates:
1. Character limits (hard cap, soft warning)
2. Banned terms (brand safety)
3. URL validation (no broken links)
4. Hallucination detection (fact check)
5. Media specs (aspect ratios, file sizes)
```

**Example Flow**:
```
MUS-004 generates email: "Click here for exclusive offer"
→ Passes to GRD-EMAIL
→ Guardian checks: URL valid? No tracking pixels? Compliant?
→ If issues: flag for manual review
→ If OK: publish
```

---

## RAG System (Context Injection)

**Why RAG?** 70+ agents need context without exceeding token limits.

```
Vector Database (ChromaDB):
├─ Codex specification (70 pages) - embedded
├─ Historical campaigns (success factors, ROI)
├─ Competitive intelligence (positioning patterns)
├─ Research artifacts (previous market analyses)
└─ Message library (proven positioning statements)

Agent Usage:
├─ RES-020 (Synthesis): "Similar campaigns in my niche?" → retrieves relevant past campaigns
├─ MUS-002 (Writer): "Positioning for SaaS CTOs?" → retrieves proven positioning statements
├─ LORD-004 (Aesthete): "Brand guidelines?" → retrieves visual brand codex
└─ LORD-003 (Strategos): "Game theory for pricing?" → retrieves competitive analysis patterns

Cost Benefit:
├─ Without RAG: 40K tokens per campaign
├─ With RAG: 15K tokens (60% reduction)
├─ Monthly savings: $3-5 per user
```

---

## Database Evolution

### Current (After Cleanup)
- 38 active tables
- 0 conflicts
- 0 unused tables

### After Phase 3 (Codex Schema)
- 68 tables (38 existing + 30 new Codex)
- Multi-tenant isolation via workspace_id
- RLS policies on all sensitive tables

### Key New Tables

**Positioning & Strategy**:
- `positioning` - Strategic positioning statements
- `message_architecture` - Messaging hierarchy
- `campaigns` - Strategic campaigns
- `campaign_quests` - Gamified campaign steps
- `campaign_cohorts` - Campaign-to-cohort targeting

**Gamification**:
- `achievements` - Achievement definitions
- `user_achievements` - User progress
- `user_stats` - XP, level, streak tracking

**Agent System**:
- `agents` - Agent registry (70+ agents)
- `memories` - Vector embeddings for RAG

**Intelligence**:
- `war_briefs` - Aggregated research outputs
- `intelligence_logs` - Market signals
- `alerts_log` - Crisis management

---

## Cost Model ($10/user/month target)

### Token Breakdown (assuming 20 campaigns/user/month)

| Phase | Cost/Campaign | Token Count | Notes |
|-------|---------------|-------------|-------|
| Research | $0.30 | 40K tokens | 20 agents × 2K each |
| Strategy | $0.15 | 20K tokens | Game theory simulation |
| Creative | $0.40 | 30K tokens | Multiple iterations |
| Overhead | $0.05 | 5K tokens | Caching, validation |
| **Total/month** | **$2.00** | **190K tokens** | **$200 cost, $10 user price** |

### Optimization Tactics

1. **Model Selection** (40% savings)
   - Use cheapest model that works
   - o1-preview only for synthesis (1-2 calls)
   - gemini-flash for high-volume

2. **Aggressive Caching** (35% savings)
   - Persona data: 30-day TTL
   - Competitor profiles: 7-day TTL
   - Message library: 30-day TTL

3. **Batch Processing** (15% savings)
   - Research in batches, not real-time
   - Nightly intelligence aggregation
   - Weekly report generation

4. **Approximation** (10% savings)
   - URL validation: regex instead of LLM
   - Template selection: similarity matching
   - Formatting checks: logic-based Guardian agents

---

## Feasibility Assessment

### Team Requirements

**To build Phase 2-3 (Codex full deployment)**:

| Role | Effort | Duration |
|------|--------|----------|
| Python Backend Dev | Full-time | 8-10 weeks |
| React Frontend Dev | Part-time (50%) | 8-10 weeks |
| DevOps/Infrastructure | Part-time (30%) | 4-6 weeks |
| QA/Testing | Part-time (40%) | 6-8 weeks |
| Project Manager | Part-time (20%) | 10-12 weeks |

**Option 1: Full team** → 10-12 weeks to production
**Option 2: Lean team** → 16-20 weeks to production
**Option 3: Phased approach** →
- Phase 2A (Database + Lords): 2-3 weeks
- Phase 2B (Guilds 1-2): 4-5 weeks
- Phase 3 (Guilds 3-4 + Frontend): 4-6 weeks

### Risk Factors

**Low Risk ✅**:
- RaptorBus already built & tested
- Database cleanup planned & safe
- Agent patterns established in existing codebase
- Clear separation of concerns

**Medium Risk ⚠️**:
- 70 agents to coordinate (complexity)
- Real-time streaming (Matrix guild)
- Third-party API reliability (SEMrush, Ahrefs)
- Token cost optimization (needs monitoring)

**Mitigations**:
- Start with 30 agents (skip optional research agents)
- Mock external APIs in development
- Implement cost tracking from day 1
- Weekly review of agent performance

---

## Next Steps Decision Tree

### Path A: Full Codex Deployment (90 days)
- ✅ Run database cleanup (3 days)
- ✅ Create Codex schema (4 days)
- ✅ Build Council of Lords (10 days)
- ✅ Build Research Guild (14 days)
- ✅ Build Muse Guild (14 days)
- ✅ Build Matrix Guild (14 days)
- ✅ Build Guardian Guild (5 days)
- ✅ Frontend integration (10 days)
- ✅ Testing & optimization (8 days)

**Best for**: Teams with 2+ dedicated engineers, clear deadline

### Path B: Phased Deployment (120+ days)
- Week 1-2: Database cleanup
- Week 3-4: Codex schema + basic gamification
- Week 5-8: Council of Lords + Research Guild (partial: 10 agents)
- Week 9-12: Muse Guild + basic creative
- Week 13+: Matrix & Guardian guilds, advanced features

**Best for**: Lean teams, want to release incrementally, learn as you go

### Path C: Minimal MVP (30 days)
- Week 1: Database cleanup
- Week 2: Codex schema (positioning, campaigns only)
- Week 3-4: Campaign Builder UI + basic workflow
- Launch: Simple campaign flow without full agent system

**Best for**: MVP validation, then scale agents later

---

## Questions to Answer Before Proceeding

1. **Team**: How many full-time engineers can dedicate to Codex?
   - 2+ → Path A (full deployment)
   - 1 + part-time → Path B (phased)
   - 0 → Path C (MVP only)

2. **Timeline**: When do you need this in production?
   - < 3 months → Path A (full resources)
   - 3-6 months → Path B (phased)
   - Flexible → Path C (start small, iterate)

3. **Budget**: Can you afford external APIs?
   - Yes: SEMrush ($449/mo), Ahrefs ($999/mo) → Full intelligence
   - No: Use mock data, implement later → Start with messaging focus

4. **Priority**: What's most important?
   - Research quality → Invest in Research Guild
   - Creative excellence → Invest in Muse Guild
   - Real-time responsiveness → Invest in Matrix Guild

---

## Review Checklist

After reading this guide, you should understand:

- [ ] What RaptorBus is and why it matters
- [ ] How the 7 Lords coordinate
- [ ] What each Guild does
- [ ] The complete data flow (campaign creation → execution)
- [ ] RAG system and cost optimization
- [ ] Database schema (before & after cleanup)
- [ ] Feasibility for your team
- [ ] Deployment options (Path A, B, or C)

---

## Ready to Decide?

Once you've reviewed these materials:

1. **Choose your path** (A, B, or C)
2. **Assess team capacity**
3. **Set timeline**
4. **Move to Phase 2**:
   - Run database migrations (011 & 012)
   - Create Codex schema (013+)
   - Start building Lords/Guilds

---

**Questions?** Review the specific section above, or ask for clarification on any component.

**Ready to proceed?** Let me know your chosen path, and we'll start Phase 2! 🚀
