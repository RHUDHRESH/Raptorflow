# RaptorFlow Backend Audit Report - Phase 1 Baseline

## Executive Summary
Completed comprehensive audit of RaptorFlow's backend architecture. Identified key opportunities for the refactored agentic marketing OS with 36 specialized agents.

## 1. Repository Structure Analysis

### Backend Architecture
```
backend/
├── backend/backend/src/swarm/          # Nested swarm architecture (LangGraph-based)
├── src/                               # Main backend application
│   ├── agents/                        # 16 existing agents
│   ├── config/                        # Environment configuration
│   ├── lib/                           # Core libraries (DB, LLM, Orchestrator)
│   ├── middleware/                    # Request middleware
│   ├── routes/                        # 11 API route modules
│   ├── services/                      # 4 service modules
│   ├── swarm/                         # Swarm coordination
│   └── tools/                         # 3 tool modules
├── test/                              # Test infrastructure
└── supabase/                          # Database migrations & schema
```

### Key Findings
- **Nested Architecture**: Two backend directories suggest incomplete consolidation
- **Agent Count**: 16 agents currently vs. 36 planned
- **Missing Services**: No `services/` directory (mentioned in plan) - only 4 service files
- **Routes**: 11 route modules covering core platform features
- **Database**: Supabase-based with comprehensive migrations

## 2. API Endpoints Inventory

### Core Platform APIs
- `/api/onboarding` - User onboarding flow
- `/api/payments` - Payment processing (PhonePe integration)
- `/api/shared` - Shared utilities
- `/api/icps` - Ideal Customer Profile management
- `/api/campaigns` - Campaign orchestration
- `/api/moves` - Move execution and management
- `/api/protocols` - Protocol definitions
- `/api/metrics` - Analytics and KPIs
- `/api/spikes` - Spike detection and management
- `/api/assets` - Content asset management
- `/api/enrich` - Data enrichment services
- `/api/radar` - Trend monitoring
- `/api/cohorts` - Cohort analysis

### Missing Planned Endpoints
- `/v2/plan` - New workflow planning
- `/v2/execute` - Agent execution
- `/v2/feedback` - User feedback capture
- `/v2/status` - Orchestration status

## 3. Move Execution Flow Analysis

### Current Flow (MoveAssemblyAgent → Database → Routes)
```
User Request → MoveAssemblyAgent.assemble() → LLM Call → Structured Output → Database → API Response
```

### Data Flow Diagram
```
Input: Campaign Context + ICP + Barrier + Protocol
├── Campaign: {id, name, goal, demand_source, persuasion_axis}
├── ICP: {label, summary, firmographics, psychographics}
├── Barrier: OBSCURITY/RISK/INERTIA/FRICTION/CAPACITY/ATROPHY
└── Protocol: A_AUTHORITY_BLITZ through F_CHURN_INTERCEPT

Output: MoveAssemblyOutput
├── move: {name, description, channels, tasks[], kpis[], assets_needed[]}
├── execution_timeline: {setup_days, run_days, review_days}
└── budget_allocation: {content, paid_media, tools, other}
```

### Execution States
- `planned` → `generating_assets` → `ready` → `running` → `paused` → `completed`/`failed`

## 4. Token Usage Profile

### Current Model Configuration
```typescript
ModelTier = {
  REASONING_HEAVY: 'gemini-2.0-flash-thinking-exp-01-21',  // Complex analysis
  REASONING: 'gemini-2.5-pro-preview-06-05',               // Structured output
  GENERAL: 'gemini-2.5-flash-preview-05-20',               // Normal tasks
  SIMPLE: 'gemini-1.5-flash'                               // Parsing/simple
}
```

### Agent-to-Model Mapping (16 agents)
- **Heavy Reasoning (4)**: ICPBuildAgent, BarrierEngineAgent, StrategyProfileAgent, CohortBuilderAgent
- **Reasoning (8)**: MoveAssemblyAgent, MuseAgent, PositioningParseAgent, MonetizationAgent, etc.
- **General (4)**: CompanyEnrichAgent, CompetitorSurfaceAgent, TechStackSeedAgent, JTBDMapperAgent

### Token Limits per Tier
- Heavy: 16,384 tokens max
- Reasoning: 8,192 tokens
- General: 4,096 tokens
- Simple: 2,048 tokens

## 5. Performance Hotspots Identified

### Large Prompt Issues
- MoveAssemblyAgent: Complex multi-part prompts with extensive ICP/context data
- MuseAgent: Creative content generation with detailed style guides
- StrategyProfileAgent: Comprehensive business analysis prompts

### Redundant Calls
- Multiple agents querying same Supabase tables without caching
- ICP data fetched repeatedly across agents
- Competitor intelligence gathered independently

### Optimization Opportunities
- Implement prompt chunking for large inputs
- Add Redis caching layer for frequent queries
- Batch similar LLM calls
- Implement streaming responses for long outputs

## 6. Third-Party Integrations Catalog

### Payment Processing
- **PhonePe**: Payment gateway integration (`PHONEPE_MERCHANT_ID`, `PHONEPE_SALT_KEY`)
- Endpoints: `/apis/hermes/pg/v1/pay`, `/apis/hermes/pg/v1/status`

### Data Enrichment
- **BuiltWith API**: Technology stack detection (`BUILTWITH_API_URL`)
- **Clearbit**: Company data enrichment (currently stubbed)

### Infrastructure
- **Supabase**: Primary database and auth
- **Google Cloud Vertex AI**: LLM models and embeddings
- **Upstash Redis**: Caching (optional, `UPSTASH_REDIS_URL`)

### Missing Planned Integrations
- Scrapegraph/DuckDuckGo (Market Intel)
- Diffbot (Competitor analysis)
- SerpAPI/KeyBERT (Keyword mining)
- GoogleTrends/ExplodingTopics (Trend radar)
- Buffer API (Social posting)
- Mailchimp (Email automation)
- Twilio (WhatsApp)

## 7. Vector Store Evaluation

### Current State: NONE
- No vector database configured
- No embedding generation pipeline
- No RAG implementation
- No memory persistence layer

### Missing Components
- pgvector extension in Supabase
- Embedding generation for documents
- Vector similarity search
- RAG query utilities
- Memory chunking strategies

## 8. Memory & Learning Systems

### Current State
- **User Preferences**: Basic JSONB field in auth.users
- **Brand Memory**: Not implemented
- **Learning Loops**: Not implemented
- **Template Weighting**: Not implemented

### Migration Requirements
- Export existing user preferences
- Design memory schema (embeddings + metadata)
- Implement preference learning from UI interactions
- Create feedback capture endpoints

## 9. Test Infrastructure Assessment

### Existing Test Setup
- **Framework**: Vitest configuration
- **Mocks**: Basic mock utilities in `test/mocks/`
- **Environment**: Test-specific env configuration
- **Coverage**: Not configured

### Gaps
- No integration tests for agent workflows
- No load testing setup
- No API endpoint testing
- No LLM response mocking

## 10. Branch Strategy

### Recommended: Create `refactor-v1` Feature Branch
- Freeze current `main`/`prod` branch
- Create feature branch for 100-step refactor
- Implement incrementally with feature flags
- Maintain backward compatibility during transition

## Key Opportunities for Refactor

1. **LangGraph Orchestration**: Replace current orchestrator with DAG-based agent coordination
2. **Token Optimization**: Implement tiered model selection and prompt chunking
3. **Vector Memory**: Add pgvector for RAG and preference learning
4. **Agent Specialization**: Expand from 16 to 36 specialized agents
5. **Integration Layer**: Add comprehensive third-party tool integrations
6. **Safety & Quality**: Implement guardrails and quality rating systems

## Risk Assessment

### High Risk
- Model dependency on Gemini ecosystem
- Complex agent orchestration requiring careful state management
- Vector store migration and embedding quality

### Medium Risk
- Token cost optimization without sacrificing quality
- Third-party API rate limits and reliability
- Backward compatibility during transition

### Low Risk
- Database schema extensions
- API endpoint additions
- Test infrastructure improvements

---

**Audit Completed**: December 11, 2025
**Next Phase**: Core Architecture Redesign (LangGraph, I/O contracts, ToolBox)


