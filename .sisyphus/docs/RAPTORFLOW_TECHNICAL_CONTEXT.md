# RAPTORFLOW — EXHAUSTIVE TECHNICAL CONTEXT DOCUMENT

**Location:** `C:\Users\hp\OneDrive\Desktop\Raptorflow\.sisyphus\docs\RAPTORFLOW_TECHNICAL_CONTEXT.md`
**Version:** 1.0.0
**Purpose:** Comprehensive technical documentation for AI coding assistants working on the RaptorFlow codebase

---

## DOCUMENT OVERVIEW

This document provides exhaustive technical context for the RaptorFlow AI-powered marketing platform. It is designed to enable any developer who has never seen the codebase to understand, modify, and rebuild the entire system from scratch. Every field, every state, every UI interaction, every API call, every database column, and every edge case is documented explicitly.

---

## PART 1 — PRODUCT PHILOSOPHY & ARCHITECTURE OVERVIEW

### 1.1 What RaptorFlow Is

RaptorFlow is an AI-powered "Marketing Employee" SaaS platform. It is NOT merely a marketing tool or content generator — it is a **delegation interface** that functions as a virtual marketing team member. Users onboard once through a comprehensive 21-step pipeline, and the platform autonomously produces, schedules, and tracks marketing output indefinitely.

The core philosophy of RaptorFlow is that marketing should not require constant manual configuration. Instead, users provide deep business context during onboarding, and the AI (codenamed "Muse") uses this context to make intelligent decisions about what to create, when to publish, and how to optimize.

### 1.2 What RaptorFlow Is Not

RaptorFlow is explicitly NOT:
- A simple social media scheduling tool like Buffer or Hootsuite
- A templated content generator that produces generic marketing copy
- A campaign management tool that requires manual configuration for every piece of content
- An analytics dashboard that only reports on past performance
- A multi-tool suite requiring users to stitch together workflows

### 1.3 The Delegation Model vs Configuration Model

Traditional marketing tools follow a **configuration model**: users must specify every detail for every piece of content — the platform, the timing, the copy, the hashtags. This creates friction and prevents marketing from scaling.

RaptorFlow follows a **delegation model**: users delegate marketing decisions to the AI by providing rich business context. The AI then makes thousands of micro-decisions autonomously:
- What content to create
- Which platform to publish on
- What time to schedule
- What tone to use
- What hashtags to include
- How to adapt based on performance

The delegation model requires more upfront investment (the 21-step onboarding) but delivers compound returns through autonomous execution.

### 1.4 The "Marketing Employee" Metaphor

RaptorFlow is architected around the metaphor of hiring a marketing employee:

- **Onboarding as Job Training:** The 21-step onboarding is training the "employee" on the company's business context, competitive landscape, brand voice, and strategic objectives.

- **BCM as Institutional Memory:** The Business Context Manifest (BCM) serves as the employee's memory — everything they need to know to do their job effectively.

- **Moves as Daily Work:** Individual marketing actions are called "Moves" — the daily work product of the marketing employee.

- **Campaigns as Projects:** Campaigns are larger strategic initiatives composed of multiple Moves — equivalent to marketing projects the employee is executing.

- **Daily Wins as Daily Standups:** The Daily Wins feature provides a daily recommendation of the highest-impact marketing action — equivalent to a standup.

- **Muse as The Employee:** Muse is the AI orchestration engine that functions as the marketing employee.

### 1.5 The Business Context Manifest (BCM) — The Nervous System

The Business Context Manifest (BCM) is the central nervous system of RaptorFlow. It is a structured JSON document that captures everything the AI needs to know about a business to produce effective marketing.

The BCM contains:
- **Foundation:** Company identity, value proposition, mission
- **ICPs (Ideal Customer Profiles):** Detailed personas with demographics, psychographics, pain points, goals
- **Positioning:** Competitive differentiation, category, unique value proposition
- **Messaging:** Brand voice, tone, guardrails, soundbites
- **Channels:** Go-to-market channels with priorities
- **Market:** TAM/SAM/SOM, geographic focus, acquisition goals

The BCM is generated from onboarding data, synthesized and enhanced by AI, cached in Redis for fast access, versioned for change tracking, and injected into every LLM prompt. Every marketing decision flows through the BCM. Without a BCM, the system cannot function — this is enforced by the `ENFORCE_BCM_READY_GATE` setting.

### 1.6 How Moves and Campaigns Differ from Traditional Marketing Tools

**Traditional Content Tools:**
- User creates content manually or via templates
- User decides platform, timing, and format
- Content exists in isolation
- No strategic context

**RaptorFlow Moves:**
- AI generates content based on BCM + strategic intent
- AI recommends optimal platform and timing
- Moves exist within strategic context (Campaigns, Daily Wins)
- Every piece of content is aligned with business objectives

**Traditional Campaign Tools:**
- Campaign is a container for pre-planned content
- Manual scheduling of each piece
- Limited optimization

**RaptorFlow Campaigns:**
- Campaign is a strategic objective with AI-generated execution plan
- AI proposes optimal Move calendar
- Continuous optimization based on performance
- Dynamic adaptation to market conditions

### 1.7 Full System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  Next.js 14 (App Router)                                                    │
│  ├── TypeScript 5.x                                                          │
│  ├── Tailwind CSS 3.x                                                       │
│  ├── Framer Motion + GSAP                                                   │
│  ├── Zustand (State Management)                                             │
│  └── React Server Components                                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP/HTTPS + WebSocket
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              API GATEWAY                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  Nginx (Reverse Proxy + SSL)                                                │
│  ├── Rate Limiting                                                          │
│  ├── Request Routing                                                        │
│  └── Static Asset Serving                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            BACKEND SERVICES                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  FastAPI (Python 3.11)                                                      │
│  ├── API Routes (/api/v1/*)                                                │
│  │   ├── /workspaces/*     - Workspace management                           │
│  │   ├── /moves/*          - Move CRUD                                      │
│  │   ├── /campaigns/*      - Campaign management                            │
│  │   ├── /context/*        - BCM operations                                 │
│  │   ├── /ai/*             - AI generation endpoints                        │
│  │   └── /foundation/*     - Foundation data                                │
│  ├── Services Layer                                                          │
│  │   ├── MoveService                                                         │
│  │   ├── CampaignService                                                     │
│  │   ├── BCMService                                                          │
│  │   └── MuseService                                                         │
│  └── AI Orchestration (LangGraph)                                           │
│      ├── Single Agent Mode                                                   │
│      ├── Council Mode (Multi-Agent)                                          │
│      └── Swarm Mode (Parallel)                                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            DATA LAYER                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────┐    ┌─────────────────────┐    ┌──────────────────┐│
│  │  Supabase           │    │  Upstash Redis      │    │  Vertex AI       ││
│  │  (PostgreSQL)       │    │  (Cache + Queue)    │    │  (Gemini Pro)    ││
│  │  ├── workspaces     │    │  ├── bcm:{id}       │    │  Content Gen     ││
│  │  ├── moves          │    │  ├── moves:list     │    │  Reasoning       ││
│  │  ├── campaigns      │    │  ├── rate_limit     │    │  Synthesis       ││
│  │  ├── bcm_versions   │    │  └── daily_wins     │    │                  ││
│  │  └── foundations    │    │                     │    │                  ││
│  └─────────────────────┘    └─────────────────────┘    └──────────────────┘│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.8 Technology Stack — Complete Inventory

#### Frontend Stack

| Component | Version | Role | Why Chosen |
|-----------|---------|------|------------|
| Next.js | 14.x | React Framework | App Router for server components, API routes, optimal performance |
| TypeScript | 5.x | Type System | Type safety across the entire codebase |
| Tailwind CSS | 3.x | Styling | Utility-first CSS for rapid UI development |
| Framer Motion | 11.x | Animations | Declarative animations for onboarding flows |
| GSAP | 3.x | Complex Animations | Timeline control, scroll-triggered animations |
| Zustand | 4.x | State Management | Lightweight, TypeScript-native, no boilerplate |
| React | 18.x | UI Library | Concurrent features, Suspense |
| Lucide React | Latest | Icons | Consistent, customizable icon system |

#### Backend Stack

| Component | Version | Role | Why Chosen |
|-----------|---------|------|------------|
| Python | 3.11 | Runtime | Type hints, performance improvements |
| FastAPI | 0.100+ | API Framework | Async native, Pydantic validation, OpenAPI |
| Pydantic | 2.x | Data Validation | Type-safe request/response models |
| LangGraph | 0.0.x | AI Orchestration | State machine for multi-agent workflows |
| LangChain | 0.1.x | LLM Integration | Abstracted LLM provider interface |
| Uvicorn | Latest | ASGI Server | High-performance async server |

#### AI/ML Stack

| Component | Version | Role | Why Chosen |
|-----------|---------|------|------------|
| Google Vertex AI | Latest | LLM Provider | Gemini Pro for content generation |
| Gemini Pro | 1.5 | Foundation Model | Best-in-class reasoning, long context |
| Gemini Flash | 2.0 | Fast Model | Low-latency operations |
| LangGraph | Latest | Agent Orchestration | State machines, conditional routing |

#### Database & Cache

| Component | Version | Role | Why Chosen |
|-----------|---------|------|------------|
| Supabase | Latest | PostgreSQL + Auth | Managed Postgres, RLS, Realtime |
| PostgreSQL | 15+ | Primary Database | Relational data, JSONB for flexibility |
| Upstash Redis | Latest | Cache + Queue | Serverless Redis, REST API |
| Redis | 7.x | Caching | BCM cache, rate limiting, session store |

---

## PART 2 — THE 21-STEP ONBOARDING PIPELINE

The onboarding pipeline is the entry point to RaptorFlow. It collects comprehensive business context through 21 carefully designed steps.

### 2.1 Onboarding Architecture

**File:** `src/app/(shell)/onboarding/page.tsx`

The onboarding is implemented as a single-page application within the Next.js shell. Each step is a distinct page component that receives standardized props:

```typescript
interface OnboardingPageProps {
  value: string | string[];
  onChange: (value: string | string[]) => void;
  onNext: () => void;
  onBack?: () => void;
  totalPages: number;  // Always 21
  currentPage: number; // 1-indexed step number
}
```

### 2.2 State Management During Onboarding

**File:** `src/stores/foundationStore.ts`

Onboarding state is managed through the `foundationStore` Zustand store:

```typescript
interface FoundationState {
  currentStep: number;
  isLoading: boolean;
  error: string | null;
  answers: Record<string, string | string[]>;
  setAnswer: (fieldId: string, value: string | string[]) => void;
  nextStep: () => void;
  prevStep: () => void;
  completeOnboarding: () => Promise<void>;
  _hasHydrated: boolean;
  setHasHydrated: (state: boolean) => void;
}
```

The store persists to `localStorage` during onboarding to prevent data loss on page refresh.

### 2.3 Backend Schema for Onboarding

**File:** `backend/api/v1/workspaces/routes.py` (Lines 41-208)

The canonical onboarding schema is defined in the backend:

```python
ONBOARDING_SCHEMA_VERSION = "2026.03.0"

CANONICAL_ONBOARDING_STEPS: List[Dict[str, Any]] = [
    {
        "id": "company_name",
        "title": "Company Name",
        "description": "Legal or public-facing name of the business.",
        "fields": [
            {
                "id": "company_name",
                "label": "Company Name",
                "kind": "short_text",
                "required": True,
                "placeholder": "Acme Labs",
            }
        ],
    },
    # ... continues for all 21 steps
]
```

### 2.4 The 21 Steps — Detailed Documentation

#### STEP 1: Company Name

**Component:** `src/components/onboarding/pages/PageCompanyName.tsx`

The user sees a full-screen immersive experience with dark background, animated compass logo at top, large headline "What is your company name?", single text input field with massive typography, character counter showing "X / 50", progress bar showing "Step 01 / 21", navigation buttons.

**Input Specifications:**
- Type: Single-line text input
- Max length: 50 characters
- Validation: Minimum 2 characters required
- Placeholder: Cycles through examples ("Acme Inc", "Stripe", "Linear", etc.)

**Frontend State:**
```typescript
answers: {
  company_name: "Acme Labs"  // string
}
```

**Backend Pydantic Schema:**
```python
class CompanyNameField(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=50)
```

**BCM Synthesis Usage:**
- Populates `foundation.company.name`
- Used in every piece of generated content as the primary entity reference

**GSAP Animations:**
- Entrance Sequence includes compass drop animation, progress bar growth, headline word stagger animation
- Focus state includes input lift and glow effect
- Valid state shows green checkmark and enables continue button
- Exit animation includes page slide and blur transition

**Why This Data Is Critical:** The company name is the primary identifier used throughout the platform.

#### STEPS 2-21: Overview

The remaining steps follow a similar pattern:

| Step | Field ID | Type | Required | Purpose |
|------|----------|------|----------|---------|
| 2 | company_website | URL | No | Brand analysis, CTA destination |
| 3 | industry | short_text | Yes | ICP templates, messaging strategies |
| 4 | business_stage | short_text | Yes | Tone and messaging sophistication |
| 5 | company_description | long_text | Yes | Core training for AI context |
| 6 | primary_offer | short_text | Yes | Primary subject of marketing content |
| 7 | core_problem | long_text | Yes | Pain points for objection handling |
| 8 | ideal_customer_title | short_text | Yes | Creates primary ICP |
| 9 | ideal_customer_profile | long_text | Yes | ICP demographics and psychographics |
| 10 | top_pain_points | list | Yes | Problem-agitation content |
| 11 | top_goals | list | Yes | Aspiration-focused content |
| 12 | key_differentiator | long_text | Yes | Competitive differentiation |
| 13 | competitors | list | Yes | Competitive intelligence |
| 14 | brand_tone | list | Yes | AI prompt construction |
| 15 | banned_phrases | list | No | Guardrails for content generation |
| 16 | channel_priorities | list | Yes | Channel-specific content generation |
| 17 | geographic_focus | short_text | No | Timezone-aware scheduling |
| 18 | pricing_model | short_text | No | Objection handling around pricing |
| 19 | proof_points | list | No | Social proof in content |
| 20 | acquisition_goal | short_text | Yes | Goal-oriented content strategy |
| 21 | constraints_and_guardrails | list | Yes | Compliance in regulated industries |

### 2.5 Onboarding Completion and BCM Generation

When the user completes Step 21, the frontend calls:

```typescript
const response = await fetch(`/api/workspaces/${workspaceId}/onboarding/complete`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    schema_version: "2026.03.0",
    answers: foundationStore.getState().answers
  })
});
```

**Backend Processing Flow:**

1. **Validation:** Validates all required fields are present, normalizes list fields, checks schema version matches

2. **Business Context Building:** `_build_business_context()` transforms onboarding answers into structured business_context object

3. **BCM Seeding:** `langgraph_context_orchestrator.seed()` passes business_context to AI orchestration layer

4. **Foundation Upsert:** Creates/updates `foundations` table in Supabase

5. **Workspace Settings Update:** Sets workspace.settings.bcm_ready = true

---

## PART 3 — THE BUSINESS CONTEXT MANIFEST (BCM)

The Business Context Manifest (BCM) is the core data structure that enables RaptorFlow's AI to generate contextually appropriate marketing content.

### 3.1 BCM JSON Schema — Complete Structure

```python
from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime

class BCMCompanyProfile(TypedDict):
    name: str
    website: str
    industry: str
    stage: str
    description: str

class BCMFact(TypedDict):
    id: str
    category: str  # "traction", "pricing", "growth", etc.
    label: str
    value: str
    confidence: float  # 0.0 - 1.0

class BCMDemographics(TypedDict):
    role: str
    stage: str
    location: str
    ageRange: str
    income: str

class BCMPsychographics(TypedDict):
    beliefs: str
    identity: str
    fears: str
    values: List[str]
    hangouts: List[str]
    triggers: List[str]

class BCMICP(TypedDict):
    name: str
    demographics: BCMDemographics
    psychographics: BCMPsychographics
    painPoints: List[str]
    goals: List[str]
    objections: List[str]
    marketSophistication: int  # 1-5 scale

class BCMPositioning(TypedDict):
    category: str
    categoryPath: str
    uvp: str  # Unique Value Proposition
    differentiators: List[str]
    competitors: List[Dict[str, str]]

class BCMBrandVoice(TypedDict):
    tone: List[str]
    doList: List[str]
    dontList: List[str]

class BCMMessaging(TypedDict):
    oneLiner: str
    positioningStatement: str
    valueProps: List[Dict[str, str]]
    brandVoice: BCMBrandVoice
    soundbites: List[str]
    guardrails: List[str]

class BCMChannel(TypedDict):
    name: str
    priority: str  # "primary", "secondary", "experimental"

class BCMMarket(TypedDict):
    tam: str
    sam: str
    som: str
    geo: str
    primary_goal: str

class BCMIntelligence(TypedDict):
    evidence_count: int
    facts: List[BCMFact]
    icps: List[BCMICP]
    positioning: BCMPositioning
    messaging: BCMMessaging
    channels: List[BCMChannel]
    market: BCMMarket

class BCMMetadata(TypedDict):
    workspace_id: str
    version: str
    checksum: str
    created_at: str
    updated_at: str
    synthesized: bool
    completion_pct: int

class BusinessContextManifest(TypedDict):
    version: str
    generated_at: str
    session_id: str
    company_profile: BCMCompanyProfile
    intelligence: BCMIntelligence
    metadata: BCMMetadata
```

### 3.2 BCM Construction Pipeline

The BCM is constructed through a multi-stage pipeline:

**Stage 1: Data Collection (Onboarding)**
- User provides answers through 21-step wizard
- Answers stored in normalized format

**Stage 2: Business Context Generation**
- `_build_business_context()` transforms answers to structured format
- Generates derived fields (oneLiner, positioningStatement)

**Stage 3: AI Synthesis**
- `langgraph_context_orchestrator.seed()` invokes Muse
- AI enhances and validates the context

**Stage 4: Storage**
- BCM stored in Supabase `bcm_versions` table
- Latest version cached in Redis
- Foundation record created/updated

### 3.3 BCM Redis Cache

The BCM is cached in Redis for fast access during AI generation:

```python
# Cache key pattern
BCM_CACHE_KEY = "bcm:{workspace_id}"

# TTL: 24 hours (86400 seconds)
BCM_CACHE_TTL = 86400

# Invalidation triggers:
# - BCM is updated or re-synthesized
# - Foundation data is modified
# - Onboarding is re-completed
# - Manual cache refresh via API
```

### 3.4 BCM Injection into LLM Prompts

**File:** `backend/ai/prompts/__init__.py`

The BCM is compiled into system prompts for LLM generation:

```python
def compile_system_prompt(
    manifest: Dict[str, Any],
    content_type: str = "general",
    target_icp: Optional[str] = None,
    memories: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """Build a complete system prompt from a BCM manifest."""
    identity = manifest.get("identity")
    prompt_kit = manifest.get("prompt_kit")
    guardrails_v2 = manifest.get("guardrails_v2")

    if identity and prompt_kit and guardrails_v2:
        return _compile_from_synthesis(manifest, identity, prompt_kit, guardrails_v2, content_type, target_icp, memories)
    else:
        return _compile_from_foundation(manifest, content_type, target_icp, memories)
```

### 3.5 BCM Versioning

Every BCM update creates a new version in the `bcm_versions` table:

```sql
CREATE TABLE bcm_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id),
    version VARCHAR(10) NOT NULL,
    checksum VARCHAR(64) NOT NULL,
    data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    change_summary TEXT,
    completion_pct INTEGER DEFAULT 0
);

CREATE INDEX idx_bcm_versions_workspace ON bcm_versions(workspace_id, created_at DESC);
```

---

## PART 4 — MOVES (THE ATOMIC MARKETING UNIT)

### 4.1 What Is a Move?

A Move is the atomic unit of marketing execution in RaptorFlow. It represents a single marketing action — a social post, an email, a blog article, an ad — that is generated, scheduled, and tracked within the platform.

**Why "Move" and Not "Post" or "Content":**

- **Strategic Intent:** A Move has a strategic purpose tied to business objectives
- **Tactical Execution:** A Move includes the full execution context
- **Measurable Impact:** Every Move is tracked for performance
- **Composable:** Moves can be organized into Campaigns

### 4.2 Move Data Model

**Frontend TypeScript Interface:**

```typescript
export type MoveCategory = 'ignite' | 'capture' | 'authority' | 'repair' | 'rally';

export interface Move {
    id: string;
    name: string;
    category: MoveCategory;
    status: MoveStatus;
    duration: number;
    goal: string;
    tone: string;
    context: string;
    attachments?: string[];
    createdAt: string;
    startDate?: string;
    endDate?: string;
    execution: ExecutionDay[];
    progress?: number;
    icp?: string;
    campaignId?: string;
    metrics?: string[];
    workspaceId?: string;
    isLocked?: boolean;
}

export type MoveStatus = 'draft' | 'active' | 'completed' | 'paused';

export const MOVE_CATEGORIES: Record<MoveCategory, MoveCategoryInfo> = {
    ignite: {
        id: 'ignite',
        name: 'Ignite',
        tagline: 'Launch & Hype',
        description: 'Maximum noise in a short window',
        useFor: ['New product drops', 'Store openings', 'Feature releases', 'Major announcements'],
        goal: 'Maximum noise in a short window',
    },
    capture: {
        id: 'capture',
        name: 'Capture',
        tagline: 'Acquisition & Sales',
        description: 'Direct revenue or qualified leads',
        useFor: ['Increasing footfall', 'Getting B2B leads', 'Closing end-of-quarter sales'],
        goal: 'Direct revenue or qualified leads',
    },
    authority: {
        id: 'authority',
        name: 'Authority',
        tagline: 'Brand & Reputation',
        description: 'Mindshare and credibility',
        useFor: ['Thought leadership', 'Personal branding', 'Building trust'],
        goal: 'Mindshare and credibility',
    },
    repair: {
        id: 'repair',
        name: 'Repair',
        tagline: 'PR & Crisis',
        description: 'Damage control and sentiment shift',
        useFor: ['Handling bad reviews', 'Addressing controversy', 'Fixing public mistakes'],
        goal: 'Damage control and sentiment shift',
    },
    rally: {
        id: 'rally',
        name: 'Rally',
        tagline: 'Community & Loyalty',
        description: 'Deepen relationships with existing users',
        useFor: ['Reactivating old customers', 'Increasing LTV', 'Driving referrals/UGC'],
        goal: 'Deepening relationships with existing users',
    },
};
```

### 4.3 Move Creation Flow

**Entry Points:**
1. Dashboard "New Move" button
2. Campaign Builder "Add Move"
3. Quick-create modal from navigation
4. Daily Wins "Use This" button

**API Endpoint:** `POST /api/ai/generate`

```typescript
const response = await fetch('/api/ai/generate', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-Workspace-ID': workspaceId
    },
    body: JSON.stringify({
        intent: "muse.generate",
        inputs: {
            task: context,
            tone: tone,
            target_audience: icp,
            context: { category, goal, strategy }
        },
        constraints: { max_tokens: 900, temperature: 0.7 },
        mode: "council",
        intensity: "medium",
        content_type: "social_post"
    })
});
```

### 4.4 LangGraph State Machine for Move Generation

**File:** `backend/agents/muse/orchestrator.py`

```python
class MoveGenerationState(TypedDict):
    workspace_id: str
    bcm: Dict[str, Any]
    request: TaskRequestV1
    system_prompt: str
    selected_agents: List[str]
    generated_content: str
    scores: Dict[str, float]
    final_output: Dict[str, Any]

# Nodes
async def fetch_bcm_node(state):
    state["bcm"] = await bcm_cache.get_or_fetch(state["workspace_id"])
    return state

async def select_agent_mode_node(state):
    # single: strategist_copywriter
    # council: analyst, creative, editor
    # swarm: swarm_coordinator
    return state

async def build_system_prompt_node(state):
    state["system_prompt"] = compile_system_prompt(state["bcm"], state["request"].content_type)
    return state

async def generate_draft_node(state):
    # Multi-agent or single generation
    return state

async def score_output_node(state):
    scores = await score_content(state["generated_content"], state["bcm"])
    state["scores"] = scores
    return state
```

### 4.5 Move Editor

The Move Editor provides:
- **Title Bar:** Move name, Save, Publish buttons
- **Content Body:** Editable generated content
- **Toolbar:** Regenerate, Rewrite Tone, Shorten, Expand, Add Emoji, Add CTA, Copy, Download
- **Right Sidebar:**
  - Move Metadata panel
  - Publishing Settings panel
  - Version History panel
  - Feedback panel

### 4.6 Move Scheduling

**Table:** `move_schedule`

```sql
CREATE TABLE move_schedule (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    move_id UUID NOT NULL REFERENCES moves(id) ON DELETE CASCADE,
    workspace_id UUID NOT NULL REFERENCES workspaces(id),
    scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
    timezone VARCHAR(50) NOT NULL DEFAULT 'UTC',
    channel VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'scheduled',
    retry_count INTEGER DEFAULT 0,
    last_error TEXT,
    published_at TIMESTAMP WITH TIME ZONE,
    published_url TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 4.7 Move Analytics

```sql
CREATE TABLE move_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    move_id UUID NOT NULL REFERENCES moves(id) ON DELETE CASCADE,
    workspace_id UUID NOT NULL REFERENCES workspaces(id),
    impressions INTEGER DEFAULT 0,
    reach INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    engagements INTEGER DEFAULT 0,
    engagement_rate DECIMAL(5,4) DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    saves INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    conversion_rate DECIMAL(5,4) DEFAULT 0,
    revenue DECIMAL(12,2) DEFAULT 0,
    source VARCHAR(50) NOT NULL,
    source_data JSONB DEFAULT '{}',
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    fetched_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## PART 5 — CAMPAIGNS

### 5.1 What Is a Campaign?

A Campaign in RaptorFlow is a strategic marketing initiative composed of multiple Moves organized around a specific goal, theme, and timeline.

**Key Characteristics:**
- **Strategic Objective:** Each Campaign has a clear, measurable goal
- **Thematic Cohesion:** All Moves share a common theme or narrative
- **Timeline-Bound:** Defined start and end dates
- **Move Organization:** Moves work together toward the goal
- **Performance Tracking:** Campaign-level analytics

### 5.2 Campaign Data Model

```typescript
type CampaignStatus = 'draft' | 'active' | 'paused' | 'completed' | 'archived';
type CampaignType = 'launch' | 'nurture' | 'reengagement' | 'seasonal' | 'product_update' | 'brand_awareness' | 'lead_gen' | 'retention';
type GoalType = 'AWARENESS' | 'LEADS' | 'SALES' | 'ENGAGEMENT' | 'RETENTION' | 'REFERRALS';

interface Campaign {
    id: string;
    workspaceId: string;
    name: string;
    description: string;
    campaignType: CampaignType;
    status: CampaignStatus;
    goalType: GoalType;
    kpiTarget: number;
    kpiMetric: string;
    startDate: string;
    endDate: string;
    targetPersonaIds: string[];
    channels: string[];
    theme: string;
    creativeBrief: string;
    budget?: number;
    moveCount: number;
    publishedMoves: number;
    createdAt: string;
    updatedAt: string;
    createdBy: string;
    isArchived: boolean;
}
```

### 5.3 Campaign Builder Wizard

The Campaign Builder is an 8-step wizard:

1. **Campaign Name + Type Selection** - Choose campaign type (launch, nurture, reengagement, seasonal, product_update, brand_awareness, lead_gen, retention)

2. **Goal Setting** - Select goal type (AWARENESS, LEADS, SALES, ENGAGEMENT, RETENTION, REFERRALS), set KPI target and metric

3. **Timeline** - Set start date, end date, duration

4. **Audience** - Select target personas from BCM or define custom segment

5. **Channels Selection** - Multi-select channels with per-channel frequency settings

6. **Theme / Creative Brief** - Freeform input with AI theme suggestion button

7. **Move Generation** - AI proposes Move calendar based on campaign config

8. **Review + Launch** - Final review and campaign activation

### 5.4 Campaign Calendar View

The Campaign Calendar provides:
- Month, week, day views
- Move cards on calendar dates with channel icon, status badge, preview
- Drag-and-drop to reschedule
- Click-to-expand Move detail panel
- Color coding by channel, status, or campaign
- Filtering controls

### 5.5 Campaign ↔ Move Relationship

```sql
CREATE TABLE campaign_moves (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    move_id UUID NOT NULL REFERENCES moves(id) ON DELETE CASCADE,
    workspace_id UUID NOT NULL REFERENCES workspaces(id),
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    added_by UUID REFERENCES auth.users(id),
    order_index INTEGER,
    campaign_goal_override TEXT,
    campaign_theme_override TEXT,
    UNIQUE(campaign_id, move_id)
);
```

**Status Propagation:**
- Campaign PAUSED → All scheduled moves PAUSED
- Campaign RESUMED → All paused moves SCHEDULED
- Campaign ARCHIVED → All draft moves archived, moves become standalone

### 5.6 Campaign Templates

Pre-built campaign templates include:

- **Product Launch:** 30 days, 15 moves, focus on awareness
- **Lead Nurture:** 60 days, 12 moves, focus on conversions
- **Thought Leadership:** 90 days, 20 moves, focus on engagement
- **Brand Awareness:** 45 days, 18 moves, multi-channel
- **Seasonal Campaign:** Variable, tied to holidays/events

---

## PART 6 — MUSE AI ORCHESTRATION ENGINE

### 6.1 Architecture Overview

Muse is not a single LLM call — it is a multi-agent orchestration layer that coordinates AI workers to produce high-quality marketing content. The architecture is built on LangGraph for state machine management.

**Core Design Principles:**
1. **Context-Driven:** Every decision is grounded in the BCM
2. **Quality-First:** Multiple agents review and refine output
3. **Scalable:** Can operate in single, council, or swarm modes
4. **Observable:** Full traceability of all decisions

### 6.2 Single Agent Mode

**Use Case:** Fast, low-complexity Moves (social posts, short emails)

**Configuration:**
```python
SINGLE_AGENT_CONFIG = {
    "agent_role": "strategist_copywriter",
    "temperature": 0.7,
    "max_tokens": 900,
    "model": "gemini-2.0-flash",
    "timeout_seconds": 15,
}
```

**Latency:** 2.5-5.5 seconds total

### 6.3 Council Mode (Multi-Agent)

**Use Case:** High-quality, long-form content (blog articles, email newsletters, LinkedIn articles)

**Three Agents:**

1. **Analyst** - Analyzes BCM, extracts key insights
2. **Creative** - Drafts content based on analyst's insights
3. **Editor** - Refines content for quality and brand alignment

**Latency:** 13-21 seconds (single pass), up to 35s with retry

### 6.4 Swarm Mode

**Use Case:** Campaign-level bulk generation (generating all Moves for a Campaign at once)

**Features:**
- Parallel generation with concurrency limit (5)
- Rate limit management against Vertex AI
- Task distribution across agents
- Result aggregation with error handling

### 6.5 Prompt Engineering

The system prompt includes:
- Identity section with voice archetype
- Business context from BCM
- Target audience (ICP) details
- Competitive positioning
- Guardrails (positive and negative patterns)
- Content type instructions
- Few-shot examples

### 6.6 Vertex AI Integration

**File:** `backend/ai/backends/vertex_ai.py`

**Service Class:**

```python
class VertexAIService:
    MODELS = {
        "gemini-2.0-flash": {"model_id": "gemini-2.0-flash-001", "max_tokens": 8192},
        "gemini-2.0-flash-lite": {"model_id": "gemini-2.0-flash-lite-001", "max_tokens": 8192},
        "gemini-1.5-pro": {"model_id": "gemini-1.5-pro-001", "max_tokens": 8192},
    }

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = "gemini-2.0-flash",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        streaming: bool = False,
    ) -> GenerationResult:
        # Implementation
```

**Authentication:** Uses Google service account with credentials loaded from `GOOGLE_APPLICATION_CREDENTIALS` environment variable.

**Rate Limits:**
- gemini-2.0-flash: 60 RPM, 100K tokens/minute
- gemini-2.0-flash-lite: 120 RPM, 200K tokens/minute
- gemini-1.5-pro: 30 RPM, 50K tokens/minute

**Fallback Behavior:** If primary model fails, tries fallback chain: flash → flash-lite → pro

---

## PART 7 — DAILY WINS

### 7.1 What Is Daily Wins?

Daily Wins is RaptorFlow's "morning newspaper" — a curated daily digest of recommended Moves that the AI determines will have the highest impact for that specific day.

**Key Characteristics:**
- **Daily Generated:** New recommendations every day
- **Context-Aware:** Considers BCM, current campaigns, performance history, day of week
- **High-Impact Focus:** Prioritizes moves that will drive business goals
- **Actionable:** One-click promotion to scheduled Move

### 7.2 Daily Wins Generation

**Schedule:** Cron job runs at 6 AM local time for each workspace

**Algorithm:**
1. Gather inputs (BCM, campaigns, recent performance, preferences)
2. Score potential moves by impact
3. Select top recommendations
4. Store in cache

**Scoring Signals:**
- Goal alignment (25%)
- Audience relevance (20%)
- Timing (20%)
- Performance prediction (15%)
- Strategic gaps (10%)
- Channel health (10%)

### 7.3 Daily Wins UI

```typescript
interface Win {
    id: string;
    title: string;
    description: string;
    impact: "high" | "medium" | "low";
    completed: boolean;
    category: "foundation" | "move" | "campaign" | "analysis";
    suggestedContent?: string;
    channel?: string;
    strategicRationale?: string;
}
```

**Actions:**
- "Use This" - Promotes recommendation to real scheduled Move
- "Skip" - Marks as skipped, signals to recommendation engine
- "Edit" - Opens editor with pre-filled content

---

## PART 8 — DATABASE ARCHITECTURE (SUPABASE)

### 8.1 Complete Table List

| Table | Purpose |
|-------|---------|
| `workspaces` | Multi-tenant workspace records |
| `workspace_members` | User-workspace relationships with roles |
| `users` | Extended user profiles (links to Supabase auth) |
| `foundations` | Company info, brand voice, messaging |
| `bcm_versions` | Versioned BCM snapshots |
| `moves` | Individual marketing content pieces |
| `move_versions` | Version history for moves |
| `move_feedback` | User ratings and comments on moves |
| `move_schedule` | Scheduled publishing queue |
| `move_analytics` | Performance metrics per move |
| `campaigns` | Strategic marketing initiatives |
| `campaign_moves` | Campaign-Move relationships |
| `campaign_analytics` | Campaign-level metrics |
| `campaign_templates` | Pre-built campaign templates |
| `daily_wins` | Daily AI recommendations |
| `ai_usage_logs` | Token usage tracking |

### 8.2 Row Level Security (RLS)

All tables have RLS enabled with workspace-based isolation:

```sql
-- Example: Moves table policy
CREATE POLICY moves_select_policy ON moves
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM workspace_members wm
            WHERE wm.workspace_id = moves.workspace_id
            AND wm.user_id = auth.uid()
        )
    );
```

### 8.3 Supabase Realtime

Enabled on tables that need real-time updates:
- `moves` - Content changes
- `campaigns` - Status updates
- `daily_wins` - New recommendations

```typescript
// Subscription pattern
const channel = supabase
    .channel('moves-changes')
    .on('postgres_changes', { event: '*', schema: 'public', table: 'moves' }, (payload) => {
        console.log('Change received!', payload);
    })
    .subscribe();
```

---

## PART 9 — REDIS CACHING LAYER

### 9.1 Cache Keys

| Key Pattern | TTL | Purpose |
|-------------|-----|---------|
| `bcm:{workspace_id}` | 24h | Business Context Manifest |
| `moves:list:{workspace_id}` | 5min | Move list cache |
| `campaigns:list:{workspace_id}` | 5min | Campaign list cache |
| `daily_wins:{workspace_id}:{date}` | Until midnight | Daily recommendations |
| `rate_limit:{workspace_id}:vertex_ai` | Sliding 60s | API rate limiting |

### 9.2 Cache Operations

```python
class BCMCache:
    async def get(self, workspace_id: str) -> Optional[Dict]:
        key = f"bcm:{workspace_id}"
        data = await redis.get(key)
        return json.loads(data) if data else None

    async def set(self, workspace_id: str, bcm: Dict, ttl: int = 86400) -> None:
        key = f"bcm:{workspace_id}"
        await redis.setex(key, ttl, json.dumps(bcm))

    async def invalidate(self, workspace_id: str) -> None:
        key = f"bcm:{workspace_id}"
        await redis.delete(key)
```

---

## PART 10 — BACKEND API ROUTES

### 10.1 Core Routes

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/workspaces/` | Create workspace |
| GET | `/api/workspaces/me/default` | Get default workspace |
| POST | `/api/workspaces/me/select` | Switch workspace |
| GET | `/api/workspaces/{id}/onboarding/status` | Get onboarding progress |
| PUT | `/api/workspaces/{id}/onboarding/answers` | Save onboarding answers |
| POST | `/api/workspaces/{id}/onboarding/complete` | Complete onboarding |
| GET | `/api/context/` | Get BCM |
| POST | `/api/context/rebuild` | Rebuild BCM |
| POST | `/api/ai/generate` | Generate content |
| GET | `/api/moves` | List moves |
| POST | `/api/moves` | Create move |
| GET | `/api/moves/{id}` | Get move |
| PATCH | `/api/moves/{id}` | Update move |
| DELETE | `/api/moves/{id}` | Delete move |
| POST | `/api/moves/{id}/feedback` | Submit feedback |
| GET | `/api/campaigns` | List campaigns |
| POST | `/api/campaigns` | Create campaign |
| GET | `/api/campaigns/{id}` | Get campaign |
| PATCH | `/api/campaigns/{id}` | Update campaign |
| DELETE | `/api/campaigns/{id}` | Delete campaign |
| POST | `/api/campaigns/{id}/generate-moves` | AI generate moves |
| GET | `/api/daily-wins` | Get daily recommendations |
| POST | `/api/daily-wins/{id}/use` | Use recommendation |

---

## PART 11 — FRONTEND ARCHITECTURE

### 11.1 Directory Structure

```
src/
├── app/                    # Next.js App Router pages
│   ├── (shell)/           # Authenticated app routes
│   │   ├── onboarding/    # Onboarding flow
│   │   ├── dashboard/    # Main dashboard
│   │   ├── moves/        # Move management
│   │   ├── campaigns/    # Campaign management
│   │   └── settings/     # User settings
│   └── api/              # API routes
├── components/
│   ├── onboarding/        # Onboarding step components
│   │   └── pages/       # Individual step pages
│   ├── moves/           # Move-related components
│   ├── campaigns/        # Campaign components
│   ├── dashboard/        # Dashboard widgets
│   ├── ui/              # Base UI primitives
│   └── raptor/          # Core app components
├── stores/               # Zustand stores
│   ├── foundationStore.ts
│   ├── movesStore.ts
│   ├── campaignStore.ts
│   ├── bcmStore.ts
│   └── workspaceStore.ts
├── services/             # API client services
│   ├── moves.service.ts
│   ├── campaigns.service.ts
│   ├── bcm.service.ts
│   └── foundation.service.ts
├── hooks/               # Custom React hooks
├── lib/                 # Utilities
└── types/               # TypeScript interfaces
```

### 11.2 Zustand Stores

**foundationStore:**
```typescript
interface FoundationState {
    currentStep: number;
    isLoading: boolean;
    error: string | null;
    answers: Record<string, string | string[]>;
    setAnswer: (fieldId: string, value: string | string[]) => void;
    nextStep: () => void;
    prevStep: () => void;
    completeOnboarding: () => Promise<void>;
}
```

**movesStore:**
```typescript
interface MovesState {
    moves: Move[];
    currentMove: Move | null;
    isLoading: boolean;
    error: string | null;
    list: (workspaceId: string) => Promise<void>;
    create: (workspaceId: string, move: Move) => Promise<void>;
    update: (workspaceId: string, moveId: string, patch: Partial<Move>) => Promise<void>;
    delete: (workspaceId: string, moveId: string) => Promise<void>;
}
```

**campaignStore:**
```typescript
interface CampaignState {
    campaigns: Campaign[];
    currentCampaign: Campaign | null;
    wizardState: CampaignWizardState;
    isLoading: boolean;
    list: (workspaceId: string) => Promise<void>;
    create: (workspaceId: string, config: CampaignConfig) => Promise<void>;
}
```

---

## PART 12 — AUTHENTICATION & MULTI-TENANCY

### 12.1 Auth Modes

RaptorFlow supports multiple authentication modes:

- **demo:** Demo user mode with preset workspace
- **supabase:** Full Supabase Auth integration
- **disabled:** No authentication (development only)

### 12.2 Auth Configuration

**Environment Variables:**
```
AUTH_MODE=demo|supabase|disabled
DEMO_USER_ID=demo-user-001
DEMO_WORKSPACE_ID=demo-workspace-001
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=xxx
SUPABASE_SERVICE_ROLE_KEY=xxx
```

### 12.3 Workspace Membership

```sql
CREATE TABLE workspace_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id),
    workspace_id UUID NOT NULL REFERENCES workspaces(id),
    role VARCHAR(20) NOT NULL DEFAULT 'member',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, workspace_id)
);

-- Roles: owner, admin, member, viewer
```

### 12.4 Workspace Guard Middleware

```python
async def workspace_guard(request: Request, call_next):
    workspace_id = request.headers.get("X-Workspace-ID")
    user_id = request.state.user_id
    
    # Verify membership
    membership = await supabase.table("workspace_members").select("*").eq("workspace_id", workspace_id).eq("user_id", user_id).execute()
    
    if not membership.data:
        raise HTTPException(403, "Access denied")
    
    request.state.workspace_id = workspace_id
    return await call_next(request)
```

---

## PART 13 — INTEGRATIONS

### 13.1 Supported Integrations

| Provider | Status | Purpose |
|----------|--------|---------|
| LinkedIn | Planned | Social publishing, analytics |
| Twitter/X | Planned | Social publishing, analytics |
| Instagram | Planned | Social publishing |
| Mailchimp | Planned | Email newsletter delivery |
| ConvertKit | Planned | Email automation |
| HubSpot | Planned | CRM sync |
| Google Analytics | Planned | Web analytics |

### 13.2 Integration Schema

```sql
CREATE TABLE integrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id),
    provider VARCHAR(50) NOT NULL,
    connected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    access_token TEXT,
    refresh_token TEXT,
    expires_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',
    UNIQUE(workspace_id, provider)
);
```

---

## PART 14 — INFRASTRUCTURE & DEVOPS

### 14.1 Environment Variables

```
# Application
APP_NAME=RaptorFlow
ENVIRONMENT=development|production
DEBUG=false

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=xxx

# Redis (Upstash)
UPSTASH_REDIS_REST_URL=https://xxx.upstash.io
UPSTASH_REDIS_REST_TOKEN=xxx

# Vertex AI
VERTEX_AI_PROJECT_ID=xxx
VERTEX_AI_LOCATION=us-central1
VERTEX_AI_MODEL=gemini-2.0-flash
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# AI Configuration
AI_EXECUTION_MODE=council|single|swarm
AI_DEFAULT_INTENSITY=medium|low|high

# Email
RESEND_API_KEY=xxx
EMAIL_FROM=noreply@raptorflow.app

# Monitoring
SENTRY_DSN=https://xxx@sentry.io
LOG_LEVEL=INFO
```

### 14.2 Docker Services

```yaml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - SUPABASE_URL
      - VERTEX_AI_PROJECT_ID
    depends_on:
      - redis

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_SUPABASE_URL

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  nginx:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
      - frontend
```

---

## PART 15 — TESTING ARCHITECTURE

### 15.1 Test Types

- **Unit Tests:** Vitest for frontend, Pytest for backend
- **Integration Tests:** API endpoint testing with test databases
- **E2E Tests:** Playwright for critical user flows

### 15.2 Backend Testing

```python
import pytest
from httpx import AsyncClient
from backend.main import app

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_create_workspace(client):
    response = await client.post("/api/workspaces/", json={"name": "Test"})
    assert response.status_code == 201
    assert response.json()["name"] == "Test"
```

### 15.3 Frontend Testing

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { MoveEditor } from './MoveEditor';

test('renders move content', () => {
  render(<MoveEditor move={mockMove} />);
  expect(screen.getByText(mockMove.name)).toBeInTheDocument();
});
```

---

## PART 16 — GLOSSARY OF ALL DOMAIN TERMS

### Core Terms

**BCM (Business Context Manifest):** The central JSON document containing all business context needed for AI content generation. Includes company profile, ICPs, positioning, messaging, channels, and market data.

**Move:** The atomic unit of marketing execution in RaptorFlow. A single piece of content (social post, email, blog article) that is generated, scheduled, and tracked.

**Campaign:** A strategic marketing initiative composed of multiple Moves organized around a specific goal, theme, and timeline.

**Muse:** The AI orchestration engine that generates content using the BCM as context. Supports single, council, and swarm execution modes.

**Foundation:** The company-level data including brand voice, positioning, and messaging configuration.

### Execution Modes

**Single Agent Mode:** Fast, single-pass content generation using one AI agent. Used for simple content like social posts.

**Council Mode:** Multi-agent content generation with Analyst, Creative, and Editor agents. Used for high-quality long-form content.

**Swarm Mode:** Parallel generation of multiple content pieces for bulk campaign creation.

### Move-Related Terms

**Move Category:** Strategic bucket for Moves: ignite (launch), capture (acquisition), authority (thought leadership), repair (crisis), rally (retention).

**Move Status:** State of a Move: draft, active, completed, paused.

**Move Version:** Historical snapshots of move content for tracking changes.

**Move Feedback:** User ratings and comments on generated content that feed back into BCM refinement.

### Campaign-Related Terms

**Campaign Type:** Category of campaign: launch, nurture, reengagement, seasonal, product_update, brand_awareness, lead_gen, retention.

**Campaign Status:** State of campaign: draft, active, paused, completed, archived.

**Goal Type:** Marketing objective: AWARENESS, LEADS, SALES, ENGAGEMENT, RETENTION, REFERRALS.

### Context Terms

**ICP (Ideal Customer Profile):** Detailed description of the target customer including demographics, psychographics, pain points, and goals.

**BCM Cache:** Redis-cached copy of the BCM for fast access during AI generation.

**Brand Voice:** The personality and tone that should be used in marketing content.

**Guardrails:** Constraints on content generation including banned phrases and mandatory compliance rules.

### Feature Terms

**Daily Wins:** Daily AI-generated recommendations for high-impact marketing actions.

**Reflection Engine:** System that captures user feedback on moves and uses it to refine the BCM.

**Tone Dial:** Feature that allows users to change the tone of generated content (direct, professional, casual, etc.).

### Technical Terms

**Workspace:** The multi-tenant container that isolates data between organizations.

**Workspace Guard:** Middleware that enforces workspace-based access control.

**RLS (Row Level Security):** PostgreSQL feature that enforces row-level access control based on user identity.

**Supabase Realtime:** Real-time subscription system for live data updates.

---

## COMPLETION SUMMARY

This document has covered:

1. **Product Philosophy & Architecture** - The delegation model, Marketing Employee metaphor, BCM as nervous system
2. **21-Step Onboarding Pipeline** - All steps with UI details, state management, and backend processing
3. **Business Context Manifest (BCM)** - Complete JSON schema, construction pipeline, Redis caching, injection patterns
4. **Moves** - Data model, creation flow, LangGraph orchestration, editor UI, scheduling, analytics
5. **Campaigns** - Data model, builder wizard, calendar view, templates
6. **Muse AI Engine** - Single/Council/Swarm modes, prompt engineering, Vertex AI integration
7. **Daily Wins** - Generation algorithm, scoring signals, UI
8. **Database Architecture** - All tables, RLS policies, realtime subscriptions
9. **Redis Caching** - All cache keys, TTLs, operations
10. **API Routes** - Complete route documentation
11. **Frontend Architecture** - Directory structure, Zustand stores
12. **Authentication & Multi-Tenancy** - Auth modes, workspace membership, guard middleware
13. **Integrations** - Provider list, schema
14. **Infrastructure** - Environment variables, Docker, monitoring
15. **Testing** - Test types and patterns
16. **Glossary** - All domain terms defined

This document is designed to enable any developer to understand, modify, and rebuild the RaptorFlow platform from scratch.
