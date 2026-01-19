# RAPTORFLOW ONBOARDING OVERHAUL: 15-PHASE IMPLEMENTATION PLAN

## EXECUTIVE SUMMARY

This document provides a comprehensive audit of the current onboarding system and a detailed 15-phase implementation plan to achieve the 23-step vision outlined by the product owner.

---

## PART 1: CURRENT STATE AUDIT

### Frontend Current State (27 Step Components)

| Current Step | Component File | Status | Gap vs Vision |
|--------------|---------------|--------|---------------|
| 1 | Step1EvidenceVault.tsx | Partial | ❌ Missing: Auto-recognition of uploaded content, recommended evidence lighting up |
| 2 | Step2AutoExtraction.tsx | Partial | ⚠️ Has extraction UI but uses mock data, no real AI extraction |
| 3 | Step3Contradictions.tsx | Exists | ⚠️ Needs inconsistency detection from internal docs |
| 4 | Step4ValidateTruthSheet.tsx | Exists | ✅ Confirmation step present |
| 5 | Step6OfferPricing.tsx | Exists | ⚠️ UI exists but needs polish per vision |
| 6 | Step7ResearchBrief.tsx | Partial | ❌ Mock data only, no real Reddit/web scraping |
| 7 | Step8CompetitiveAlternatives.tsx | Exists | ❌ DELETE ability to manually add competitors |
| 8 | Step9CompetitiveLadder.tsx | Exists | ⚠️ Needs competitive comparison view |
| 9 | Step10CategorySelection.tsx | Exists | ⚠️ Needs Safe/Clever/Bold path options |
| 10 | Step11DifferentiatedCapabilities.tsx | Exists | ⚠️ Needs Only You/Unique/Better Than/Table Stakes |
| 11 | Step12CapabilityMatrix.tsx | Partial | ❌ Has perceptual map but manual, not AI-generated 3 options |
| 12 | Step13PositioningStatements.tsx | Exists | ⚠️ Missing neuroscience-based copy generation |
| 13 | Step13StrategicGap.tsx | Exists | ⚠️ Gap analysis exists but needs full competitor detail |
| 14 | Step14FocusSacrifice.tsx | Exists | ⚠️ Focus/Sacrifice logic incomplete |
| 15 | Step15ICPProfiles.tsx | Good | ⚠️ Demographics/psychographics exist, needs more depth |
| 16 | Step16BuyingProcess.tsx | Exists | ✅ Educational step |
| 17 | Step17MessagingGuardrails.tsx | Exists | ⚠️ Needs "what to never follow" rules |
| 18 | Step18SoundbitesLibrary.tsx | Exists | ⚠️ Needs merge with positioning statements |
| 19 | Step19MessageHierarchy.tsx | Exists | ❌ DELETE per vision |
| 20 | Step20BrandAugmentation.tsx | Exists | ❌ DELETE per vision |
| 21 | Step21ChannelMapping.tsx | Exists | ⚠️ Needs AI-driven primary/secondary/tertiary |
| 22 | Step22TAMSAM.tsx | Exists | ⚠️ Needs better visual design (not grid) |
| 23 | Step23ValidationTodos.tsx | Exists | ⚠️ 5 non-content validation tasks |
| 24 | Step24FinalSynthesis.tsx | Exists | ⚠️ Should be step 23 completion |
| 25 | Step25Export.tsx | Exists | ❌ DELETE per vision |

### Backend Current State

| Component | File | Status | Gap |
|-----------|------|--------|-----|
| Onboarding API | api/v1/onboarding.py | ✅ Working | Basic CRUD, file upload, URL processing |
| OCR Service | services/ocr_service.py | ⚠️ Partial | Fallback mode active, needs real OCR |
| Web Scraper | tools/web_scraper.py | ⚠️ Framework | Selenium/HTTP scraping exists but not Reddit-specific |
| LangGraph Flow | agents/graphs/onboarding.py | ⚠️ Outdated | 13-step flow, not 23-step |
| Orchestrator | agents/specialists/onboarding_orchestrator.py | ⚠️ Basic | Generic guidance, not step-specific AI |
| Competitive Service | services/competitive_service.py | ⚠️ Partial | Basic competitor analysis |
| ICP Architect | agents/specialists/icp_architect.py | ✅ Exists | AI-powered ICP generation |

### Critical Missing Capabilities

1. **Evidence Vault Auto-Recognition (Step 1)**
   - No AI that identifies "product screenshot" vs "pitch deck" vs "manifesto"
   - No "recommended evidence" section that lights up automatically

2. **Real Web Scraping Intelligence (Step 6)**
   - No Reddit scraping capability
   - No pain point extraction from forums
   - Mock data used throughout

3. **AI-Driven Perceptual Map (Step 11)**
   - Current implementation is manual drag-and-drop
   - Need AI to suggest 3 unique quadrant positions
   - "Only You" positioning not automated

4. **Neuroscience Copywriting Engine (Step 12)**
   - 6 core principles not implemented
   - No limbic activation scoring
   - No pattern recognition analysis

5. **Position-Based Logic (Step 13)**
   - Focus/Sacrifice buttons not tied to positioning decisions
   - No lightbulb explanations for why something can't be chosen

6. **TAM/SAM/SOM Visualization (Step 21)**
   - Currently uses boring grid layout
   - Need "weirdly shaped, nice-looking, integrally designed" visualization

---

## PART 2: THE 23-STEP VISION (Mapped)

| Vision Step | Purpose | Current Gap Level |
|-------------|---------|-------------------|
| 1 | Evidence Vault: Upload + Auto-recognize + Light up recommendations | 🔴 HIGH |
| 2 | Extraction Summary: "Here's what we found" | 🟡 MEDIUM |
| 3 | Inconsistency Detection: Find contradictions in their docs | 🟡 MEDIUM |
| 4 | Truth Confirmation: "Are you sure this is right?" | 🟢 LOW |
| 5 | The Offer: Recurring vs One-time sales model | 🟡 MEDIUM |
| 6 | Market Intelligence: Reddit scraping, pain points, competitors | 🔴 HIGH |
| 7 | DELETE: Remove manual competitor adding | 🟢 EASY FIX |
| 8 | Comparative Angle: How you compare, where you beat them | 🟡 MEDIUM |
| 9 | Market Category: Safe/Clever/Bold paths with pros/cons | 🟡 MEDIUM |
| 10 | Product Capabilities: Only You/Unique/Better Than/Table Stakes | 🟡 MEDIUM |
| 11 | Perceptual Map + Position Grid + Gap Analysis | 🔴 HIGH |
| 12 | Positioning Statements: Neuroscience-based copywriting | 🔴 HIGH |
| 13 | Focus & Sacrifice: Position-driven constraints | 🟡 MEDIUM |
| 14 | ICP Personas: Full demographics + psychographics | 🟢 LOW |
| 15 | Market Education: Buying process info (read-only) | 🟢 LOW |
| 16 | Messaging Rules: What to follow / never follow | 🟡 MEDIUM |
| 17 | Soundbites Library: Merge with positioning statements | 🟡 MEDIUM |
| 18-19 | DELETE: Message Hierarchy and Brand Augmentation | 🟢 EASY FIX |
| 20 | Channel Mapping: AI-driven primary/secondary/tertiary | 🟡 MEDIUM |
| 21 | TAM/SAM/SOM: Beautiful non-grid visualization | 🟡 MEDIUM |
| 22 | Validation Tasks: 5 non-content tasks | 🟢 LOW |
| 23 | Completion: "Onboarding done, go to app" | 🟢 LOW |

---

## PART 3: 15-PHASE IMPLEMENTATION PLAN

### PHASE 1: Foundation & Cleanup (Week 1)
**Priority: Critical**

#### Tasks:
1. **Renumber step tokens** in `onboarding-tokens.ts` to match 23-step vision
2. **Delete deprecated steps**: Step19MessageHierarchy, Step20BrandAugmentation, Step25Export
3. **Update step component mapping** in `[stepId]/page.tsx`
4. **Update LangGraph flow** in `agents/graphs/onboarding.py` to 23 steps
5. **Create step ID migration** for existing sessions

#### Deliverables:
- Clean 23-step structure
- Aligned frontend/backend step IDs
- No orphaned components

---

### PHASE 2: Evidence Vault Intelligence (Week 1-2)
**Priority: Critical**

#### Backend Tasks:
1. **Create EvidenceClassifier agent** that auto-detects document type:
   - Product screenshots → "PRODUCT_VISUAL"
   - Pitch decks → "STRATEGY_DECK"
   - Brand manifesto → "BRAND_VOICE"
   - Competitor URLs → "COMPETITIVE_INTEL"
   - Testimonials → "SOCIAL_PROOF"

2. **Implement classification API endpoint**:
   ```python
   POST /api/v1/onboarding/{session_id}/vault/classify
   # Returns: { type: "PRODUCT_VISUAL", confidence: 0.92 }
   ```

3. **Enhance OCR service** for document understanding

#### Frontend Tasks:
1. **Add RECOMMENDED_EVIDENCE section** with automatic lighting:
   ```tsx
   const RECOMMENDED_EVIDENCE = [
     { id: "product_screenshots", label: "Product Screenshots", lit: false },
     { id: "pitch_deck", label: "Strategy/Pitch Deck", lit: false },
     { id: "manifesto", label: "Brand Manifesto", lit: false },
     // ... more
   ];
   ```

2. **Real-time classification** on upload that lights up matched recommendations
3. **Better file preview** with extracted content snippet

#### Deliverables:
- AI auto-recognizes uploaded content
- Recommended evidence lights up automatically
- Enhanced upload experience

---

### PHASE 3: Extraction Engine (Week 2)
**Priority: High**

#### Backend Tasks:
1. **Create ExtractionOrchestrator** that:
   - Processes all vault items
   - Extracts brand name, value props, audience signals
   - Returns structured facts with confidence scores
   - Cites sources (file/page, URL)

2. **Implement real extraction endpoint**:
   ```python
   POST /api/v1/onboarding/{session_id}/extract
   # Returns: { facts: [...], summary: "...", warnings: [...] }
   ```

3. **Integrate with Vertex AI** for intelligent extraction

#### Frontend Tasks:
1. **Show "Here's what we found"** summary prominently
2. **Display extracted facts** by category with source citations
3. **Allow editing/verification** of each fact

#### Deliverables:
- Real AI extraction from uploaded materials
- Clear summary of findings
- Editable facts with source tracking

---

### PHASE 4: Inconsistency Detection (Week 2-3)
**Priority: High**

#### Backend Tasks:
1. **Create ContradictionDetector agent** that:
   - Compares extracted facts against each other
   - Identifies mismatches (e.g., "premium" claim vs low price)
   - Generates clarification questions

2. **Contradiction API**:
   ```python
   POST /api/v1/onboarding/{session_id}/analyze/contradictions
   # Returns: { issues: [{ id, claim1, claim2, severity, question }] }
   ```

#### Frontend Tasks:
1. **Issue cards** with highlighted contradictions
2. **Clarification input** for user to explain/fix
3. **Resolution tracking** (resolved vs pending)

#### Deliverables:
- AI detects internal contradictions
- User can clarify/resolve issues
- Clean truth sheet emerges

---

### PHASE 5: Reddit Scraping & Market Intelligence (Week 3-4)
**Priority: Critical**

#### Backend Tasks:
1. **Create RedditScraper tool**:
   ```python
   class RedditScraper:
       async def search_subreddits(self, keywords: List[str]) -> List[Post]:
           # Uses Reddit API (free tier)
           # Extracts: title, body, comments, sentiment
       
       async def extract_pain_points(self, posts: List[Post]) -> List[PainPoint]:
           # AI-powered extraction of pain points, desires, objections
   ```

2. **Market Intelligence API**:
   ```python
   POST /api/v1/onboarding/{session_id}/research/market
   # Returns: { pain_points, desires, objections, competitor_mentions }
   ```

3. **Competitor Discovery** from market research data:
   - Direct competitors (same solution)
   - Indirect competitors (different approach, same problem)
   - Status quo (what they do now without any tool)

#### Frontend Tasks:
1. **Pain point display** with verbatim quotes
2. **Desire/objection categorization**
3. **Competitor cards** (3-5 max, auto-discovered)
4. **Remove manual "Add Competitor" button**

#### Deliverables:
- Real Reddit scraping capability
- AI-extracted customer insights
- Auto-discovered competitors (3-5)

---

### PHASE 6: Competitive Analysis Engine (Week 4)
**Priority: High**

#### Backend Tasks:
1. **CompetitorAnalyzer agent**:
   - Scrapes competitor websites
   - Extracts: core claim, target audience, pricing, features
   - Identifies strengths and weaknesses

2. **Comparative Advantage API**:
   ```python
   POST /api/v1/onboarding/{session_id}/analyze/competitive
   # Returns: { advantages, disadvantages, attack_vectors }
   ```

#### Frontend Tasks:
1. **Comparison matrix view**
2. **Attack vector recommendations** (speed, price, culture, etc.)
3. **"How you'll fare" assessments**

#### Deliverables:
- Automated competitor research
- Clear comparative advantages
- Attack strategy recommendations

---

### PHASE 7: Market Category Selection (Week 4-5)
**Priority: High**

#### Backend Tasks:
1. **CategoryAdvisor agent**:
   - Analyzes positioning context
   - Generates 3 paths: Safe, Clever, Bold
   - Calculates effort, education, pricing implications
   - Generates pros/cons

2. **Category API**:
   ```python
   POST /api/v1/onboarding/{session_id}/strategy/categories
   # Returns: { paths: [{ name, effort, pros, cons, competitors_in_space }] }
   ```

#### Frontend Tasks:
1. **Three-card selection UI** for Safe/Clever/Bold
2. **Expandable details**: why yes, why no, competitors, buyers
3. **Pricing and effort indicators**

#### Deliverables:
- AI-generated category recommendations
- Clear decision framework
- Informed category selection

---

### PHASE 8: Product Capability Rating (Week 5)
**Priority: Medium**

#### Backend Tasks:
1. **CapabilityAnalyzer**:
   - Cross-references capabilities with competitors
   - Classifies as: Only You / Unique / Better Than / Table Stakes
   - Provides verification data from scraping

#### Frontend Tasks:
1. **Capability list** with rating buttons
2. **AI suggestions** for each rating
3. **"Add capability"** functionality
4. **Summary view** without redundant "Better Than Table Stakes" labels

#### Deliverables:
- Capability differentiation mapping
- AI-assisted classification
- Clean summary output

---

### PHASE 9: AI-Powered Perceptual Map (Week 5-6)
**Priority: Critical**

#### Backend Tasks:
1. **PerceptualMapGenerator agent**:
   ```python
   async def generate_positioning_options(self, context: PositioningContext) -> List[PerceptualOption]:
       # Analyzes all competitor positions
       # Finds 3 unique quadrant opportunities
       # Ensures "Only You" in each option
       # Returns: x_axis, y_axis, your_position, competitor_positions
   ```

2. **Position Grid auto-generation**:
   - Market served: SMB, Mid-market, Enterprise, Startups
   - Category (from selected path)
   - Tribe: Growth teams, Founders, Marketing leaders
   - Story: David vs Goliath, Built by practitioners, Opinionated

#### Frontend Tasks:
1. **3 AI-generated perceptual map options**
2. **Interactive visualization** showing unique quadrant
3. **Position grid** with auto-filled selections
4. **Gap analysis view** with competitor cards

#### Deliverables:
- AI finds 3 unique positioning opportunities
- User is always "Only" in their quadrant
- Complete position grid

---

### PHASE 10: Neuroscience Copywriting Engine (Week 6-7)
**Priority: Critical**

#### Backend Tasks:
1. **NeuroscienceCopywriter agent** implementing 6 principles:
   - Limbic System Activation (emotional tagging)
   - Pattern Recognition (rhythm, rhyme, repetition)
   - Cognitive Load Reduction (simplicity)
   - Neural Coupling (storytelling)
   - Spacing Effect (repetition structure)
   - Multi-Sensory Encoding

2. **Copy generation endpoint**:
   ```python
   POST /api/v1/onboarding/{session_id}/copy/generate
   # Generates: positioning_statement, uvp, one_liner, tagline, body_copy
   ```

3. **Copy scoring** based on neuroscience principles

#### Frontend Tasks:
1. **Full messaging hierarchy** (5 levels from playbook)
2. **Principle compliance indicators**
3. **Edit with real-time scoring**
4. **Multiple variations** for A/B testing

#### Deliverables:
- Neuroscience-based copy generation
- Positioning statement, UVP, one-liner, tagline
- Compliance scoring with principles

---

### PHASE 11: Focus & Sacrifice Logic (Week 7)
**Priority: Medium**

#### Backend Tasks:
1. **PositionConstraintEngine**:
   - Based on selected position, determines:
     - What you MUST focus on (can't change)
     - What you CAN'T do (automatic sacrifice)
     - What's flexible

#### Frontend Tasks:
1. **Focus/Sacrifice toggle buttons**
2. **Disabled states** based on position
3. **Lightbulb explanation** popups
4. **"Not recommended" warnings**

#### Deliverables:
- Position-driven constraints
- Clear explanations for restrictions
- Logical focus/sacrifice flow

---

### PHASE 12: Deep ICP Generation (Week 7-8)
**Priority: Medium**

#### Backend Tasks:
1. **Enhanced ICP Architect**:
   - Demographics: age, income, location, role, stage
   - Psychographics: beliefs, identity, becoming, fears, values
   - Behaviors: hangouts, consumption, follows, language, timing, triggers
   - Market sophistication level (1-5)

#### Frontend Tasks:
1. **Complete ICP cards** with all dimensions
2. **Primary/Secondary ICP selection**
3. **Market sophistication visualization**

#### Deliverables:
- Rich ICP profiles
- All demographics/psychographics
- Purchase trigger identification

---

### PHASE 13: Messaging Rules & Soundbites (Week 8)
**Priority: Medium**

#### Tasks:
1. **Merge soundbites library with positioning**
2. **"What to follow" rules** (3 core principles)
3. **"What to NEVER follow"** rules (3 anti-patterns)
4. **Warning popups** for contradictory inputs
5. **Problem statement, agitation, unique mechanism, CTA generation**

#### Deliverables:
- Unified messaging system
- Clear guardrails
- Editable soundbites

---

### PHASE 14: Channel Strategy & TAM/SAM/SOM (Week 8-9)
**Priority: Medium**

#### Backend Tasks:
1. **ChannelRecommender**:
   - Based on ICP behaviors (where they hang out)
   - Suggests primary/secondary/tertiary channels
   - Considers brand preferences (e.g., "no newsletters")

2. **MarketSizeCalculator**:
   - TAM/SAM/SOM estimation
   - Industry data integration

#### Frontend Tasks:
1. **AI-driven channel recommendations**
2. **"Not recommended" warnings** for additions
3. **Beautiful TAM/SAM/SOM visualization** (NOT a grid)
   - Concentric circles or funnel
   - Interesting shapes
   - Key insights in cards

#### Deliverables:
- AI-recommended channels
- Beautiful market sizing visualization
- Clear channel prioritization

---

### PHASE 15: Validation & Completion (Week 9)
**Priority: Low**

#### Tasks:
1. **5 validation tasks** (non-content):
   - Interview 3 ICPs about pain points
   - Test elevator pitch with 5 prospects
   - Shadow a sales call
   - Review competitor positioning
   - Validate pricing with 3 prospects

2. **Skip option** with acknowledgment
3. **Completion screen** → redirect to dashboard
4. **Remove export step** (vision says no export)

#### Deliverables:
- Validation task checklist
- Clean completion flow
- Dashboard redirect

---

## PART 4: TECHNICAL REQUIREMENTS

### New Backend Services Needed

```
backend/
├── agents/
│   ├── specialists/
│   │   ├── evidence_classifier.py         # NEW: Auto-detect document type
│   │   ├── extraction_orchestrator.py     # NEW: Extract facts from evidence
│   │   ├── contradiction_detector.py      # NEW: Find inconsistencies
│   │   ├── reddit_researcher.py           # NEW: Reddit scraping
│   │   ├── competitor_analyzer.py         # NEW: Competitor deep analysis
│   │   ├── category_advisor.py            # NEW: Safe/Clever/Bold paths
│   │   ├── perceptual_map_generator.py    # NEW: AI positioning
│   │   ├── neuroscience_copywriter.py     # NEW: 6-principle copywriting
│   │   ├── channel_recommender.py         # NEW: AI channel strategy
│   │   └── market_size_calculator.py      # NEW: TAM/SAM/SOM
│   └── graphs/
│       └── onboarding.py                  # UPDATE: 23-step flow
├── tools/
│   └── reddit_scraper.py                  # NEW: Reddit API integration
└── services/
    └── positioning_service.py             # NEW: Positioning logic
```

### New Frontend Components Needed

```
frontend/src/components/onboarding/
├── steps/
│   ├── Step1EvidenceVault.tsx             # UPDATE: Auto-recognition
│   ├── Step2ExtractionSummary.tsx         # RENAME/UPDATE
│   ├── Step3InconsistencyResolution.tsx   # RENAME/UPDATE
│   └── ... (renumber all)
├── visualizations/
│   ├── PerceptualMapAI.tsx                # NEW: 3-option map
│   ├── TAMSAMSOMVisual.tsx                # NEW: Beautiful viz
│   └── PositionGrid.tsx                   # NEW: Auto-filled grid
└── messaging/
    ├── NeuroscienceScore.tsx              # NEW: Principle compliance
    └── SoundbitesEditor.tsx               # NEW: Merged soundbites
```

### Database Schema Updates

```sql
-- Evidence classification
ALTER TABLE onboarding_vault ADD COLUMN document_type VARCHAR(50);
ALTER TABLE onboarding_vault ADD COLUMN classification_confidence FLOAT;
ALTER TABLE onboarding_vault ADD COLUMN extracted_content JSONB;

-- Contradictions
CREATE TABLE onboarding_contradictions (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES onboarding_sessions(id),
    claim1 TEXT,
    claim2 TEXT,
    severity VARCHAR(20),
    resolution TEXT,
    resolved_at TIMESTAMP
);

-- Market research
CREATE TABLE onboarding_market_insights (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES onboarding_sessions(id),
    type VARCHAR(50), -- pain_point, desire, objection
    quote TEXT,
    source VARCHAR(255),
    frequency VARCHAR(20)
);

-- Competitors (auto-discovered)
CREATE TABLE onboarding_competitors (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES onboarding_sessions(id),
    name VARCHAR(255),
    type VARCHAR(50), -- direct, indirect, status_quo
    core_claim TEXT,
    strengths JSONB,
    weaknesses JSONB,
    discovered_by VARCHAR(50) -- ai, manual (should be ai only)
);

-- Positioning
CREATE TABLE onboarding_positioning (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES onboarding_sessions(id),
    perceptual_map_option INTEGER, -- 1, 2, or 3
    x_axis VARCHAR(100),
    y_axis VARCHAR(100),
    category_path VARCHAR(50), -- safe, clever, bold
    position_grid JSONB
);
```

---

## PART 5: TIMELINE SUMMARY

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| 1 | Week 1 | Clean 23-step structure |
| 2 | Week 1-2 | Evidence auto-recognition |
| 3 | Week 2 | Real AI extraction |
| 4 | Week 2-3 | Inconsistency detection |
| 5 | Week 3-4 | Reddit scraping + market intel |
| 6 | Week 4 | Competitive analysis engine |
| 7 | Week 4-5 | Market category selection |
| 8 | Week 5 | Product capability rating |
| 9 | Week 5-6 | AI perceptual map |
| 10 | Week 6-7 | Neuroscience copywriting |
| 11 | Week 7 | Focus/sacrifice logic |
| 12 | Week 7-8 | Deep ICP generation |
| 13 | Week 8 | Messaging rules & soundbites |
| 14 | Week 8-9 | Channel strategy + TAM/SAM/SOM |
| 15 | Week 9 | Validation & completion |

**Total Estimated Duration: 9 weeks**

---

## PART 6: RISK ASSESSMENT

### High Risk Items
1. **Reddit API limitations** - May need to use web scraping fallback
2. **AI extraction accuracy** - Requires extensive testing
3. **Perceptual map intelligence** - Complex positioning logic
4. **Neuroscience copywriting** - Needs domain expertise

### Mitigation Strategies
1. Build fallback scraping for Reddit if API insufficient
2. Implement confidence scoring with human review for low scores
3. Start with rule-based positioning, enhance with AI
4. Consult copywriting expertise for principle implementation

---

## PART 7: SUCCESS METRICS

1. **Step 1**: 90%+ accuracy in auto-classifying document types
2. **Step 2**: 80%+ of extracted facts marked "verified" by users
3. **Step 6**: Real customer insights sourced from Reddit (not mock)
4. **Step 11**: All 3 perceptual map options show unique quadrant position
5. **Step 12**: Copy scores 70%+ on neuroscience principle compliance
6. **Overall**: Onboarding completion rate > 60%

---

*Document created: January 2026*
*Author: Raptorflow Engineering*
