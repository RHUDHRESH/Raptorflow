# RAPTORFLOW — EXHAUSTIVE TECHNICAL CONTEXT DOCUMENT

## PART 3: THE BUSINESS CONTEXT MANIFEST (BCM)

**File:** `.sisyphus/docs/PART_3_BCM.md`
**Lines:** ~800

---

## 3.1 BCM JSON SCHEMA - COMPLETE STRUCTURE

The Business Context Manifest is a comprehensive JSON document containing all information needed for AI-powered marketing generation. This section documents every field.

### Top-Level Structure

```python
from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime

class BusinessContextManifest(TypedDict):
    """Complete BCM structure."""
    version: str                    # Schema version (e.g., "2.1")
    generated_at: str               # ISO 8601 timestamp
    session_id: str                # Unique session identifier
    company_profile: BCMCompanyProfile
    intelligence: BCMIntelligence
    metadata: BCMMetadata
```

### Company Profile Section

```python
class BCMCompanyProfile(TypedDict):
    """Basic company identifying information."""
    name: str                      # Company legal or public name
    website: str                   # Primary website URL
    industry: str                  # Industry classification
    stage: str                     # Business stage (Pre-seed through Enterprise)
    description: str               # Detailed company description
```

**Example:**
```json
{
    "name": "Acme Labs",
    "website": "https://acmelabs.io",
    "industry": "SaaS",
    "stage": "Seed",
    "description": "Acme Labs provides AI-powered analytics for B2B sales teams."
}
```

This section is populated from onboarding Steps 1-5 (company name, website, industry, stage, description). It forms the foundational identity of the company throughout all marketing operations.

### Intelligence Section

The intelligence section contains the core business knowledge that drives content generation:

```python
class BCMIntelligence(TypedDict):
    """Business intelligence for content generation."""
    evidence_count: int           # Number of evidence/facts
    facts: List[BCMFact]          # Supporting evidence
    icps: List[BCMICP]           # Ideal customer profiles
    positioning: BCMPositioning    # Competitive positioning
    messaging: BCMMessaging       # Brand messaging framework
    channels: List[BCMChannel]   # Go-to-market channels
    market: BCMMarket            # Market context
```

#### Facts

Facts are pieces of evidence that support marketing claims:

```python
class BCMFact(TypedDict):
    """Evidence supporting marketing claims."""
    id: str                       # Unique identifier (e.g., "f-pricing-1")
    category: str                 # Category: pricing, traction, growth, etc.
    label: str                   # Human-readable label
    value: str                   # The fact value
    confidence: float             # Confidence score 0.0-1.0
```

**Categories:**
- **pricing:** Pricing information and models
- **traction:** Revenue, users, growth metrics
- **growth:** Growth rates, expansion metrics
- **recognition:** Awards, press, certifications
- **customer:** Success stories, NPS, satisfaction

**Example:**
```json
{
    "id": "f-traction-1",
    "category": "traction",
    "label": "Annual Recurring Revenue",
    "value": "$2.1M ARR",
    "confidence": 0.92
}
```

The confidence score reflects how certain the AI should be when using this fact. User-provided facts get high confidence (0.8+), inferred facts get medium confidence (0.5-0.7), and predicted metrics get lower confidence.

#### Ideal Customer Profiles (ICPs)

ICPs define who the marketing should target:

```python
class BCMICP(TypedDict):
    """Ideal customer profile."""
    name: str                     # ICP name (e.g., "VP Sales")
    demographics: BCMDemographics # Demographic info
    psychographics: BCMPsychographics  # Psychographic info
    painPoints: List[str]         # Problems this persona experiences
    goals: List[str]              # Goals this persona wants to achieve
    objections: List[str]         # Common objections to overcome
    marketSophistication: int    # 1-5 scale of market knowledge
```

**Demographics:**
```python
class BCMDemographics(TypedDict):
    """Demographic information."""
    role: str                    # Job title/role
    stage: str                   # Career stage
    location: str                # Geographic focus
    ageRange: str                # Age range (optional)
    income: str                  # Income level (optional)
```

**Psychographics:**
```python
class BCMPsychographics(TypedDict):
    """Psychographic information."""
    beliefs: str                  # What they believe about the problem
    identity: str                 # How they identify
    fears: str                   # Fears related to the problem
    values: List[str]            # Values that drive decisions
    hangouts: List[str]          # Where they spend time online
    triggers: List[str]          # Events that trigger action
```

**Example ICP:**
```json
{
    "name": "VP Sales",
    "demographics": {
        "role": "VP Sales",
        "stage": "Mid-career",
        "location": "United States",
        "ageRange": "35-50",
        "income": "$200K+"
    },
    "psychographics": {
        "beliefs": "Data-driven decisions are superior to intuition",
        "identity": "Revenue leader responsible for team success",
        "fears": "Missing quarterly targets, being surprised by deals",
        "values": ["Transparency", "Accountability", "Results"],
        "hangouts": ["LinkedIn", "Sales podcasts", "Conference"],
        "triggers": ["Q-end approaching", "Low pipeline coverage", "Competitive threat"]
    },
    "painPoints": [
        "Inaccurate sales forecasts",
        "Poor visibility into deal health",
        "Reps chasing wrong deals"
    ],
    "goals": [
        "Hit quota consistently",
        "Build predictable revenue",
        "Develop team skills"
    ],
    "objections": [
        "Too expensive",
        "Need executive buy-in",
        "Current process works"
    ],
    "marketSophistication": 4
}
```

ICPs are created from onboarding Steps 7-11 (core problem, ideal customer title/profile, pain points, goals). Multiple ICPs can be defined to target different segments.

#### Positioning

Positioning defines how the company differentiates in the market:

```python
class BCMPositioning(TypedDict):
    """Competitive positioning."""
    category: str                 # Product category
    categoryPath: str            # Category strategy: bold, differentiated, etc.
    uvp: str                     # Unique Value Proposition
    differentiators: List[str]   # Key differentiators
    competitors: List[Dict[str, str]]  # Competitive landscape
```

**Example:**
```json
{
    "category": "AI-powered sales analytics",
    "categoryPath": "bold",
    "uvp": "Predicts deal closure with 92% accuracy using proprietary signal analysis",
    "differentiators": [
        "Proprietary AI model trained on 10M+ deals",
        "Real-time signal detection",
        "Native Salesforce integration"
    ],
    "competitors": [
        {"name": "Salesforce Einstein", "type": "direct"},
        {"name": "Gong", "type": "direct"},
        {"name": "Clari", "type": "indirect"}
    ]
}
```

The category path indicates positioning strategy:
- **bold:** Creating a new category
- **differentiated:** Position within existing category but different
- **challenger:** Take on market leader

#### Messaging

Messaging defines how the brand communicates:

```python
class BCMMessaging(TypedDict):
    """Brand messaging framework."""
    oneLiner: str                 # Quick positioning statement
    positioningStatement: str      # Full positioning paragraph
    valueProps: List[Dict[str, str]]  # Value propositions
    brandVoice: BCMBrandVoice    # Voice characteristics
    soundbites: List[str]        # Quick quotes for social
    guardrails: List[str]       # Content constraints
```

**Brand Voice:**
```python
class BCMBrandVoice(TypedDict):
    """Voice characteristics."""
    tone: List[str]             # Tone descriptors
    doList: List[str]          # Things to do in content
    dontList: List[str]        # Things to avoid in content
```

**Example:**
```json
{
    "oneLiner": "Acme Labs: AI-powered analytics that predict which deals will close",
    "positioningStatement": "For VP Sales who need predictable revenue, Acme Labs is an AI analytics platform that predicts deal outcomes 3x more accurately than intuition. Unlike Salesforce, we use proprietary signals to forecast with 92% accuracy.",
    "valueProps": [
        {"title": "Accurate Forecasting", "description": "Predict deal closure with 92% accuracy"},
        {"title": "Early Warning", "description": "Identify at-risk deals weeks before they surface"}
    ],
    "brandVoice": {
        "tone": ["Direct", "Confident", "Data-driven"],
        "doList": [
            "Use specific numbers and metrics",
            "Address pain points directly",
            "Lead with outcomes"
        ],
        "dontList": [
            "Use generic buzzwords",
            "Make unsubstantiated claims",
            "Be vague about value"
        ]
    },
    "soundbites": [
        "Stop guessing. Start predicting.",
        "Your forecast is wrong. Here's why.",
        "92% accuracy. No crystal ball required."
    ],
    "guardrails": [
        "No legal claims without proof",
        "No competitor bashing",
        "Always include disclaimer on ROI claims"
    ]
}
```

The brand voice is constructed from onboarding Steps 12-15 (key differentiator, brand tone, banned phrases) and Step 21 (constraints/guardrails).

#### Channels

Channels define go-to-market priorities:

```python
class BCMChannel(TypedDict):
    """Marketing channel."""
    name: str                    # Channel name
    priority: str               # Priority: primary, secondary, experimental
```

**Example:**
```json
[
    {"name": "LinkedIn", "priority": "primary"},
    {"name": "Email", "priority": "primary"},
    {"name": "YouTube", "priority": "secondary"},
    {"name": "Twitter", "priority": "experimental"}
]
```

Channels are prioritized from onboarding Step 16. The priority influences content allocation - primary channels get the most content, experimental channels get tested.

#### Market

Market context provides business scope:

```python
class BCMMarket(TypedDict):
    """Market context."""
    tam: str                     # Total Addressable Market
    sam: str                     # Serviceable Addressable Market
    som: str                     # Serviceable Obtainable Market
    geo: str                     # Geographic focus
    primary_goal: str            # Primary acquisition goal
```

**Example:**
```json
{
    "tam": "$50B",
    "sam": "$10B",
    "som": "$500M",
    "geo": "United States, Canada, UK",
    "primary_goal": "Generate 60 SQLs per month"
}
```

### Metadata Section

Metadata tracks the BCM itself:

```python
class BCMMetadata(TypedDict):
    """BCM metadata."""
    workspace_id: str            # Associated workspace
    version: str                 # BCM version
    checksum: str                # Content hash for change detection
    created_at: str             # Creation timestamp
    updated_at: str              # Last update timestamp
    synthesized: bool            # Whether AI synthesis completed
    completion_pct: int          # Completeness percentage
```

---

## 3.2 EXAMPLE COMPLETE BCM

```json
{
  "version": "2.1",
  "generated_at": "2026-02-20T10:30:00Z",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "company_profile": {
    "name": "Acme Labs",
    "website": "https://acmelabs.io",
    "industry": "SaaS",
    "stage": "Seed",
    "description": "Acme Labs provides AI-powered analytics for B2B sales teams."
  },
  "intelligence": {
    "evidence_count": 4,
    "facts": [
      {
        "id": "f-pricing-1",
        "category": "pricing",
        "label": "Pricing Model",
        "value": "$99/seat/month",
        "confidence": 0.85
      },
      {
        "id": "f-traction-1",
        "category": "traction",
        "label": "Annual Recurring Revenue",
        "value": "$2.1M ARR",
        "confidence": 0.92
      },
      {
        "id": "f-traction-2",
        "category": "traction",
        "label": "Growth Rate",
        "value": "40% MoM",
        "confidence": 0.90
      },
      {
        "id": "f-traction-3",
        "category": "traction",
        "label": "Customer Count",
        "value": "200+ customers",
        "confidence": 0.88
      }
    ],
    "icps": [
      {
        "name": "VP Sales",
        "demographics": {
          "role": "VP Sales",
          "stage": "Mid-career",
          "location": "United States",
          "ageRange": "35-50",
          "income": "$200K+"
        },
        "psychographics": {
          "beliefs": "Data-driven decisions are superior to intuition",
          "identity": "Revenue leader responsible for team success",
          "fears": "Missing quarterly targets, being surprised by deals",
          "values": ["Transparency", "Accountability", "Results"],
          "hangouts": ["LinkedIn", "Sales podcasts", "Conference"],
          "triggers": ["Q-end approaching", "Low pipeline coverage", "Competitive threat"]
        },
        "painPoints": [
          "Inaccurate sales forecasts",
          "Poor visibility into deal health",
          "Reps chasing wrong deals"
        ],
        "goals": [
          "Hit quota consistently",
          "Build predictable revenue",
          "Develop team skills"
        ],
        "objections": [
          "Too expensive",
          "Need executive buy-in"
        ],
        "marketSophistication": 4
      },
      {
        "name": "Sales Manager",
        "demographics": {
          "role": "Sales Manager",
          "stage": "Early-career",
          "location": "United States",
          "ageRange": "28-40",
          "income": "$120K+"
        },
        "psychographics": {
          "beliefs": "Hard work beats talent when talent doesn't work hard",
          "identity": "Player-coach driving individual and team success",
          "fears": "Not being able to hit number, team member turnover",
          "values": ["Grind", "Team success", "Career growth"],
          "hangouts": ["LinkedIn", "Twitter", "Sales communities"],
          "triggers": ["New quarter starting", "Deal stuck", "Rep frustration"]
        },
        "painPoints": [
          "Can't see what reps are working on",
          "Don't know which deals need help",
          "Too many meetings, not enough selling"
        ],
        "goals": [
          "Promote to Director",
          "Hit team quota",
          "Build team reputation"
        ],
        "objections": [
          "Already have a CRM",
          "My team is too small"
        ],
        "marketSophistication": 3
      }
    ],
    "positioning": {
      "category": "AI-powered sales analytics",
      "categoryPath": "bold",
      "uvp": "Predicts deal closure with 92% accuracy using proprietary signal analysis",
      "differentiators": [
        "Proprietary AI model trained on 10M+ deals",
        "Real-time signal detection",
        "Native Salesforce integration",
        "$2.1M ARR traction proof"
      ],
      "competitors": [
        {"name": "Salesforce Einstein", "type": "direct"},
        {"name": "Gong", "type": "direct"},
        {"name": "Clari", "type": "indirect"},
        {"name": "HubSpot", "type": "indirect"}
      ]
    },
    "messaging": {
      "oneLiner": "Acme Labs: AI-powered analytics that predict which deals will close",
      "positioningStatement": "For VP Sales who need predictable revenue, Acme Labs is an AI analytics platform that predicts deal outcomes 3x more accurately than intuition. Unlike Salesforce, we use proprietary signals to forecast with 92% accuracy.",
      "valueProps": [
        {"title": "Accurate Forecasting", "description": "Predict deal closure with 92% accuracy"},
        {"title": "Early Warning", "description": "Identify at-risk deals weeks before they surface"},
        {"title": "Rep Coaching", "description": "Know exactly which deals need attention"}
      ],
      "brandVoice": {
        "tone": ["Direct", "Confident", "Data-driven"],
        "doList": [
          "Use specific numbers and metrics",
          "Address pain points directly",
          "Lead with outcomes",
          "Show don't tell"
        ],
        "dontList": [
          "Revolutionary",
          "Game-changing",
          "Synergy"
        ]
      },
      "soundbites": [
        "Stop guessing. Start predicting.",
        "Your forecast is wrong. Here's why.",
        "92% accuracy. No crystal ball required."
      ],
      "guardrails": [
        "No legal claims without proof",
        "No competitor bashing",
        "Always include disclaimer on ROI claims",
        "No medical/health claims",
        "Avoid unsubstantiated percentages"
      ]
    },
    "channels": [
      {"name": "LinkedIn", "priority": "primary"},
      {"name": "Email", "priority": "primary"},
      {"name": "YouTube", "priority": "secondary"},
      {"name": "Twitter", "priority": "experimental"},
      {"name": "Blog", "priority": "secondary"}
    ],
    "market": {
      "tam": "$50B",
      "sam": "$10B",
      "som": "$500M",
      "geo": "United States, Canada, UK",
      "primary_goal": "Generate 60 SQLs per month"
    }
  },
  "metadata": {
    "workspace_id": "ws-550e8400-e29b-41d4-a716-446655440000",
    "version": "2.1",
    "checksum": "a1b2c3d4e5f6",
    "created_at": "2026-02-20T10:30:00Z",
    "updated_at": "2026-02-20T10:30:00Z",
    "synthesized": true,
    "completion_pct": 100
  }
}
```

---

## 3.3 BCM CONSTRUCTION PIPELINE

The BCM is constructed through a multi-stage pipeline:

### Stage 1: Data Collection (Onboarding)

Users provide answers through the 21-step wizard. Each step maps to specific BCM fields:

| Onboarding Step | BCM Field |
|---------------|-----------|
| 1-2 | company_profile.name, company_profile.website |
| 3-4 | company_profile.industry, company_profile.stage |
| 5 | company_profile.description |
| 6-7 | positioning.category, icps[].painPoints |
| 8-9 | icps[].name, icps[].demographics |
| 10-11 | icps[].painPoints, icps[].goals |
| 12 | positioning.differentiators |
| 13 | positioning.competitors |
| 14 | messaging.brandVoice.tone |
| 15 | messaging.brandVoice.dontList |
| 16 | channels |
| 17 | market.geo |
| 18 | facts (pricing) |
| 19 | facts (traction) |
| 20 | market.primary_goal |
| 21 | messaging.guardrails |

### Stage 2: Business Context Generation

The `_build_business_context()` function transforms raw onboarding data into structured business context:

```python
def _build_business_context(workspace_row, answers) -> Dict:
    # Extract base fields
    company_name = answers.get("company_name") or workspace_row.get("name")
    industry = answers.get("industry") or ""
    stage = answers.get("business_stage") or ""
    description = answers.get("company_description") or ""
    
    # Normalize lists
    pain_points = _normalize_list(answers.get("top_pain_points"))
    goals = _normalize_list(answers.get("top_goals"))
    tone = _normalize_list(answers.get("brand_tone"))
    competitors = _normalize_list(answers.get("competitors"))
    channels = _normalize_list(answers.get("channel_priorities"))
    
    # Build derived fields
    one_liner = f"{company_name}: {answers.get('primary_offer')}".strip()
    
    positioning_statement = (
        f"For {answers.get('ideal_customer_title')}, {company_name} solves "
        f"{answers.get('core_problem')}. We do this through "
        f"{answers.get('primary_offer')}. Our edge is "
        f"{answers.get('key_differentiator')}."
    ).strip()
    
    # Create channel objects with priorities
    channel_objects = []
    for index, channel in enumerate(channels[:8]):
        if index == 0:
            priority = "primary"
        elif index <= 2:
            priority = "secondary"
        else:
            priority = "experimental"
        channel_objects.append({"name": channel, "priority": priority})
    
    # Build structured context
    business_context = {
        "version": "2.1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "session_id": str(uuid4()),
        "company_profile": {
            "name": company_name,
            "website": answers.get("company_website", ""),
            "industry": industry,
            "stage": stage,
            "description": description,
        },
        "intelligence": {
            "evidence_count": len(proof_points) + 1,
            "facts": _build_facts(answers),
            "icps": [_build_icp(answers)],
            "positioning": {
                "category": answers.get("primary_offer", ""),
                "categoryPath": "bold",
                "uvp": answers.get("key_differentiator", ""),
                "differentiators": [answers.get("key_differentiator", "")] + proof_points[:3],
                "competitors": [{"name": c, "type": "direct"} for c in competitors[:8]],
            },
            "messaging": {
                "oneLiner": one_liner,
                "positioningStatement": positioning_statement,
                "valueProps": [{"title": "Primary Offer", "description": answers.get("primary_offer", "")}],
                "brandVoice": {
                    "tone": tone,
                    "doList": [],
                    "dontList": _normalize_list(answers.get("banned_phrases")),
                },
                "soundbites": [one_liner],
                "guardrails": _normalize_list(answers.get("constraints_and_guardrails")),
            },
            "channels": channel_objects,
            "market": {
                "geo": answers.get("geographic_focus", ""),
                "primary_goal": answers.get("acquisition_goal", ""),
            },
        },
    }
    
    return business_context
```

### Stage 3: AI Synthesis

The LangGraph orchestrator enhances the basic business context:

```python
async def seed(workspace_id: str, business_context: Dict) -> Dict:
    """
    Synthesize BCM from business context using AI.
    
    This enriches the basic onboarding data with:
    - AI-generated identity archetypes
    - Content templates per channel/type
    - Refined guardrails
    - ICP voice adaptations
    """
    
    # Invoke synthesis graph
    result = await synthesis_graph.execute(
        business_context=business_context,
        workspace_id=workspace_id
    )
    
    # Return enhanced BCM
    return result["synthesized_bcm"]
```

The synthesis process adds:
- **identity:** Synthesized voice archetype with communication style, emotional register, vocabulary DNA
- **prompt_kit:** Content templates for each content type (social, email, blog, etc.)
- **guardrails_v2:** AI-refined positive and negative patterns

### Stage 4: Storage

BCM is stored in two places:

**Supabase (persistent):**
```sql
INSERT INTO bcm_versions (
    workspace_id, version, checksum, data, created_at, completion_pct
) VALUES (
    'workspace-123', '2.1', 'abc123', 
    '{...}', NOW(), 100
);
```

**Redis (cache):**
```
Key: bcm:workspace-123
TTL: 86400 (24 hours)
Value: Full BCM JSON
```

---

## 3.4 BCM REDIS CACHE

The BCM is cached in Redis for fast access during AI generation.

### Cache Key Pattern

```python
BCM_CACHE_PREFIX = "bcm:"
BCM_CACHE_TTL = 86400  # 24 hours

def get_cache_key(workspace_id: str) -> str:
    return f"{BCM_CACHE_PREFIX}{workspace_id}"
```

### Cache Operations

```python
class BCMCache:
    """Redis cache for Business Context Manifests."""
    
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def get(self, workspace_id: str) -> Optional[Dict]:
        """Get BCM from cache."""
        key = get_cache_key(workspace_id)
        data = await self.redis.get(key)
        if data:
            return json.loads(data)
        return None
    
    async def set(self, workspace_id: str, bcm: Dict, ttl: int = BCM_CACHE_TTL) -> None:
        """Set BCM in cache."""
        key = get_cache_key(workspace_id)
        await self.redis.setex(key, ttl, json.dumps(bcm))
    
    async def invalidate(self, workspace_id: str) -> None:
        """Invalidate BCM cache."""
        key = get_cache_key(workspace_id)
        await self.redis.delete(key)
    
    async def refresh(self, workspace_id: str) -> Dict:
        """Refresh BCM from database."""
        # Get latest version from Supabase
        result = await supabase.table("bcm_versions").select("*").eq("workspace_id", workspace_id).order("created_at", desc=True).limit(1).execute()
        
        if not result.data:
            raise ValueError(f"No BCM found for workspace {workspace_id}")
        
        bcm = result.data[0]["data"]
        
        # Update cache
        await self.set(workspace_id, bcm)
        
        return bcm
```

### Cache Hit/Miss Flow

```python
async def get_bcm(workspace_id: str) -> Dict:
    """Get BCM with cache-aside pattern."""
    
    # Try cache first
    cached = await cache.get(workspace_id)
    if cached:
        logger.debug(f"BCM cache hit for {workspace_id}")
        return cached
    
    # Cache miss - load from database
    logger.debug(f"BCM cache miss for {workspace_id}")
    bcm = await cache.refresh(workspace_id)
    
    return bcm
```

### Invalidation Triggers

The BCM cache is invalidated when:

1. **Onboarding completed:** New BCM generated
2. **BCM rebuilt manually:** User triggers rebuild
3. **Foundation updated:** Company info changed
4. **Feedback threshold reached:** Significant negative feedback triggers refinement
5. **Manual invalidation:** Admin clears cache

```python
async def on_bcm_updated(workspace_id: str) -> None:
    """Handle BCM update - invalidate cache."""
    await cache.invalidate(workspace_id)
    
    # Also notify any connected clients
    await publish_bcm_update(workspace_id)
```

---

## 3.5 BCM INJECTION INTO LLM PROMPTS

The BCM is compiled into system prompts for every LLM generation request.

### Prompt Compilation

**File:** `backend/ai/prompts/__init__.py`

```python
def compile_system_prompt(
    manifest: Dict[str, Any],
    content_type: str = "general",
    target_icp: Optional[str] = None,
    memories: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """
    Build complete system prompt from BCM manifest.
    
    If manifest has synthesized identity/prompt_kit/guardrails_v2,
    uses those directly. Otherwise builds from foundation data.
    """
    identity = manifest.get("identity")
    prompt_kit = manifest.get("prompt_kit")
    guardrails_v2 = manifest.get("guardrails_v2")
    
    if identity and prompt_kit and guardrails_v2:
        return _compile_from_synthesis(
            manifest, identity, prompt_kit, guardrails_v2,
            content_type, target_icp, memories
        )
    else:
        return _compile_from_foundation(
            manifest, content_type, target_icp, memories
        )
```

### Synthesis-Based Compilation

```python
def _compile_from_synthesis(
    manifest: Dict,
    identity: Dict,
    prompt_kit: Dict,
    guardrails_v2: Dict,
    content_type: str,
    target_icp: Optional[str],
    memories: Optional[List]
) -> str:
    """Build prompt from AI-synthesized BCM."""
    
    foundation = manifest.get("foundation", {})
    messaging = manifest.get("messaging", {})
    competitive = manifest.get("competitive", {})
    icps = manifest.get("icps", [])
    
    parts = []
    
    # Identity section
    parts.append(f"You are {identity.get('voice_archetype', 'a content specialist')} "
                f"for {foundation.get('company', 'the company')}.")
    
    parts.append("\n## YOUR IDENTITY")
    parts.append(f"- Communication style: {identity.get('communication_style', '')}")
    parts.append(f"- Emotional register: {identity.get('emotional_register', '')}")
    
    if identity.get("vocabulary_dna"):
        parts.append(f"- Power words to use: {', '.join(identity['vocabulary_dna'])}")
    
    if identity.get("anti_vocabulary"):
        parts.append(f"- Words to NEVER use: {', '.join(identity['anti_vocabulary'])}")
    
    if identity.get("sentence_patterns"):
        parts.append("- Writing patterns:")
        for p in identity["sentence_patterns"]:
            parts.append(f"  * {p}")
    
    parts.append(f"- Perspective: {identity.get('perspective', 'we')}")
    
    # Business context
    parts.append(f"\n## BUSINESS CONTEXT")
    parts.append(f"- Company: {foundation.get('company', '')} "
                f"({foundation.get('industry', '')}, {foundation.get('stage', '')})")
    parts.append(f"- Value proposition: {foundation.get('value_prop', '')}")
    parts.append(f"- One-liner: {messaging.get('one_liner', '')}")
    
    if messaging.get("positioning"):
        parts.append(f"- Positioning: {messaging['positioning'][:200]}")
    
    # Target audience
    selected_icp = None
    if target_icp and icps:
        selected_icp = next((i for i in icps if i.get("name") == target_icp), None)
    if not selected_icp and icps:
        selected_icp = icps[0]
    
    if selected_icp:
        parts.append(f"\n## TARGET AUDIENCE: {selected_icp.get('name', '')}")
        parts.append(f"- Role: {selected_icp.get('role', '')}")
        
        if selected_icp.get("pains"):
            parts.append(f"- Pain points: {', '.join(selected_icp['pains'][:3])}")
        
        if selected_icp.get("goals"):
            parts.append(f"- Goals: {', '.join(selected_icp['goals'][:3])}")
        
        if selected_icp.get("triggers"):
            parts.append(f"- Triggers: {', '.join(selected_icp['triggers'][:3])}")
        
        icp_voice = prompt_kit.get("icp_voice_map", {}).get(selected_icp.get("name", ""), "")
        if icp_voice:
            parts.append(f"- Voice adaptation: {icp_voice}")
    
    # Competitive positioning
    if competitive.get("category") or competitive.get("differentiation"):
        parts.append(f"\n## COMPETITIVE POSITIONING")
        if competitive.get("category"):
            parts.append(f"- Category: {competitive['category']}")
        if competitive.get("differentiation"):
            parts.append(f"- Key differentiator: {competitive['differentiation']}")
        if guardrails_v2.get("competitive_rules"):
            for rule in guardrails_v2["competitive_rules"]:
                parts.append(f"- {rule}")
    
    # Guardrails
    parts.append(f"\n## GUARDRAILS")
    if guardrails_v2.get("positive_patterns"):
        parts.append("DO:")
        for g in guardrails_v2["positive_patterns"][:5]:
            parts.append(f"  + {g}")
    
    if guardrails_v2.get("negative_patterns"):
        parts.append("DON'T:")
        for g in guardrails_v2["negative_patterns"][:5]:
            parts.append(f"  - {g}")
    
    # Content type instructions
    ct_template = prompt_kit.get("content_templates", {}).get(content_type, "")
    if ct_template:
        parts.append(f"\n## CONTENT TYPE INSTRUCTIONS ({content_type.upper()})")
        parts.append(ct_template)
    
    # Few-shot examples
    examples = prompt_kit.get("few_shot_examples", {}).get(content_type, [])
    if examples:
        parts.append(f"\n## EXAMPLES OF YOUR BEST WORK")
        for i, ex in enumerate(examples[:2], 1):
            parts.append(f"\nExample {i}:\n{ex}")
    
    # Learned preferences
    if memories:
        parts.append(f"\n## LEARNED PREFERENCES")
        for mem in memories[:5]:
            parts.append(f"- {mem.get('summary', str(mem))}")
    
    return "\n".join(parts)
```

### Example Compiled Prompt

```
You are a Data-Driven Storyteller for Acme Labs.

## YOUR IDENTITY
- Communication style: Direct, specific, outcome-focused
- Emotional register: Confident but not arrogant
- Power words to use: Predict, forecast, accuracy, signals, deal health
- Words to NEVER use: Revolutionary, game-changing, synergistic
- Writing patterns:
  * Lead with specific numbers
  * Use active voice
  * Show, don't tell
- Perspective: we

## BUSINESS CONTEXT
- Company: Acme Labs (SaaS, Seed)
- Value proposition: AI-powered analytics that predict deal outcomes
- One-liner: Acme Labs: AI-powered analytics that predict which deals will close

## TARGET AUDIENCE: VP Sales
- Role: VP Sales
- Pain points: Inaccurate forecasts, poor visibility, wrong deals
- Goals: Hit quota, predictable revenue, team skills
- Triggers: Q-end approaching, low pipeline coverage

## COMPETITIVE POSITIONING
- Category: AI-powered sales analytics
- Key differentiator: 92% accuracy vs 30% industry average

## GUARDRAILS
DO:
  + Use specific metrics and percentages
  + Lead with outcomes
  + Reference traction/proof
DON'T:
  - Make claims without evidence
  - Mention competitors by name negatively
  - Use hype language

## CONTENT TYPE INSTRUCTIONS (social_linkedin)
Write a LinkedIn post that:
- Hooks in the first line
- Addresses a specific pain point
- Includes concrete evidence
- Ends with soft CTA

## EXAMPLES OF YOUR BEST WORK

Example 1:
Your forecast is lying to you.

3 deals worth $500K just slipped through the cracks.

That's $500K you'll never recover this quarter.

The problem isn't your team. It's your signals.

We analyzed 10M+ deals and found that traditional CRM data only captures 30% of what actually predicts a close.

The other 70%? It's hidden in email patterns, meeting sentiment, and deal velocity changes.

92% of the time, we can spot a at-risk deal 3 weeks before it goes sideways.

Stop managing your pipeline by hope. Start managing it by signal.

→ Book a demo to see your at-risk deals

Example 2:
Sales forecasting is broken.

Your rep says "we'll hit number" and you want to believe them.

But how do they actually know?

The deals in your pipeline today will close at roughly the same rate as the deals that closed last quarter.

Unless you're tracking the signals that actually predict outcomes.

Not activity. Not stages. Signals.

What signals is your team tracking?

## LEARNED PREFERENCES
- Lead posts with contrarian statements
- Use specific dollar amounts
- End with soft CTAs asking questions
```

---

## 3.6 BCM VERSIONING

Every BCM update creates a new version stored in Supabase.

### Schema

```sql
CREATE TABLE bcm_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
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

### Version Creation

```python
async def create_version(workspace_id: str, bcm_data: Dict, user_id: str) -> Dict:
    """Create new BCM version."""
    
    checksum = hash_bcm(bcm_data)
    
    version = await supabase.table("bcm_versions").insert({
        "workspace_id": workspace_id,
        "version": bcm_data.get("metadata", {}).get("version", "2.1"),
        "checksum": checksum,
        "data": bcm_data,
        "created_by": user_id,
        "completion_pct": bcm_data.get("metadata", {}).get("completion_pct", 0)
    }).execute()
    
    return version.data[0]
```

### Version History

```python
async def get_versions(workspace_id: str, limit: int = 10) -> List[Dict]:
    """Get BCM version history."""
    
    result = await supabase.table("bcm_versions").select(
        "id, version, checksum, created_at, created_by, change_summary, completion_pct"
    ).eq("workspace_id", workspace_id).order("created_at", desc=True).limit(limit).execute()
    
    return result.data
```

---

## 3.7 BCM DIFF/DELTA DETECTION

Semantic changes are detected to avoid unnecessary re-synthesis:

```python
def compute_bcm_delta(old_bcm: Dict, new_bcm: Dict) -> Dict[str, Any]:
    """Compute semantic delta between BCM versions."""
    
    delta = {
        "changed_sections": [],
        "significance_score": 0.0,
        "requires_resynthesis": False,
        "affected_content_types": []
    }
    
    # Check company profile changes
    if old_bcm.get("company_profile") != new_bcm.get("company_profile"):
        delta["changed_sections"].append("company_profile")
        delta["significance_score"] += 0.3
    
    # Check positioning changes
    old_pos = old_bcm.get("intelligence", {}).get("positioning", {})
    new_pos = new_bcm.get("intelligence", {}).get("positioning", {})
    if old_pos != new_pos:
        delta["changed_sections"].append("positioning")
        delta["significance_score"] += 0.4
        delta["affected_content_types"].extend(["messaging", "ads", "landing_pages"])
    
    # Check ICP changes
    old_icps = old_bcm.get("intelligence", {}).get("icps", [])
    new_icps = new_bcm.get("intelligence", {}).get("icps", [])
    if old_icps != new_icps:
        delta["changed_sections"].append("icps")
        delta["significance_score"] += 0.5
        delta["affected_content_types"].append("all_content")
    
    # Check channel changes
    old_channels = old_bcm.get("intelligence", {}).get("channels", [])
    new_channels = new_bcm.get("intelligence", {}).get("channels", [])
    if old_channels != new_channels:
        delta["changed_sections"].append("channels")
        delta["significance_score"] += 0.2
    
    # Determine if re-synthesis needed
    if delta["significance_score"] > 0.3:
        delta["requires_resynthesis"] = True
    
    return delta
```

---

## 3.8 THE REFLECTION ENGINE

The Reflection Engine captures feedback on generated content and uses it to refine the BCM.

### Feedback Collection

```python
class MoveFeedback(TypedDict):
    """Feedback on a generated Move."""
    move_id: str
    rating: int                    # 1-5 stars
    category: str                  # tone, accuracy, relevance, quality
    comment: str                  # Free text
    content_version: str          # Which version was rated
    timestamp: str
```

### Feedback Processing

```python
class BCMReflector:
    """Analyzes feedback and proposes BCM refinements."""
    
    async def record_move_feedback(
        self,
        workspace_id: str,
        move_id: str,
        feedback: MoveFeedback
    ) -> None:
        """Store feedback and trigger analysis if needed."""
        
        # Store in database
        await self._store_feedback(workspace_id, move_id, feedback)
        
        # Analyze if rating is low
        if feedback["rating"] <= 2:
            await self._propose_bcm_update(workspace_id, move_id, feedback)
    
    async def _propose_bcm_update(
        self,
        workspace_id: str,
        move_id: str,
        feedback: MoveFeedback
    ) -> Optional[Dict]:
        """Analyze low-rated content and propose refinements."""
        
        # Get the Move content
        move = await move_service.get(move_id)
        
        # Analyze what went wrong
        proposal = await self._analyze_content_issues(
            content=move["content"],
            feedback_comment=feedback["comment"],
            feedback_category=feedback["category"]
        )
        
        # If confident, create proposal
        if proposal["confidence"] > 0.7:
            return await self._create_update_proposal(
                workspace_id=workspace_id,
                proposal=proposal
            )
        
        return None
    
    async def _analyze_content_issues(
        self,
        content: str,
        feedback_comment: str,
        feedback_category: str
    ) -> Dict:
        """AI analysis of content issues."""
        
        prompt = f"""
        Analyze this content that received negative feedback.
        
        Category: {feedback_category}
        Comment: {feedback_comment}
        
        Content:
        {content[:2000]}
        
        Identify:
        1. What specifically was wrong (tone, accuracy, relevance, etc.)
        2. What BCM changes would improve future content
        3. Confidence in the analysis (0.0-1.0)
        
        Return JSON with keys: issues[], recommendations[], confidence
        """
        
        result = await vertex_ai.generate(prompt=prompt)
        
        return json.loads(result.content)
```

The Reflection Engine enables continuous improvement - the BCM isn't static, it learns from user feedback to produce better content over time.
