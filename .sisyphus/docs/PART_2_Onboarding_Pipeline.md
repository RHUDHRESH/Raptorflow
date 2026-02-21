# RAPTORFLOW — EXHAUSTIVE TECHNICAL CONTEXT DOCUMENT

## PART 2: THE 21-STEP ONBOARDING PIPELINE

**File:** `.sisyphus/docs/PART_2_Onboarding_Pipeline.md`
**Lines:** ~800

---

## 2.1 ONBOARDING ARCHITECTURE OVERVIEW

The onboarding pipeline is the critical first experience for RaptorFlow users. It transforms a new signup into a fully-configured marketing machine by collecting comprehensive business context through 21 structured steps. This section documents every aspect of the onboarding system.

### Architectural Components

The onboarding system consists of several interconnected components:

**Frontend Components:**
- `src/app/(shell)/onboarding/page.tsx` - Main onboarding page container
- `src/components/onboarding/pages/*.tsx` - Individual step components (21 pages)
- `src/components/onboarding/steps/*.tsx` - Shared step components
- `src/stores/foundationStore.ts` - Zustand store for onboarding state

**Backend Components:**
- `backend/api/v1/workspaces/routes.py` - Onboarding API endpoints (lines 41-208 define schema)
- `backend/api/v1/workspaces/routes.py` - `_build_business_context()` function for data transformation
- `backend/services/bcm/synthesizer.py` - AI synthesis of BCM from onboarding data

**State Management:**
The foundationStore persists all answers to localStorage during onboarding to prevent data loss on page refresh. Upon completion, all data is sent to the backend where it transforms into the Business Context Manifest.

---

## 2.2 STATE MANAGEMENT DURING ONBOARDING

**File:** `src/stores/foundationStore.ts`

The foundationStore is a Zustand store that manages all onboarding state:

```typescript
interface FoundationState {
  // Session state
  currentStep: number;
  isLoading: boolean;
  error: string | null;
  
  // All collected answers (keyed by field ID from backend schema)
  answers: Record<string, string | string[]>;
  
  // Actions
  setAnswer: (fieldId: string, value: string | string[]) => void;
  setAnswers: (answers: Record<string, string | string[]>) => void;
  nextStep: () => void;
  prevStep: () => void;
  goToStep: (step: number) => void;
  reset: () => void;
  
  // Async actions
  loadFromBackend: (workspaceId: string) => Promise<void>;
  saveToBackend: (workspaceId: string) => Promise<void>;
  completeOnboarding: (workspaceId: string) => Promise<OnboardingCompleteResponse>;
  
  // Persistence
  _hasHydrated: boolean;
  setHasHydrated: (state: boolean) => void;
}
```

The store uses Zustand's persist middleware to save to localStorage:

```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const useFoundationStore = create<FoundationState>()(
  persist(
    (set, get) => ({
      currentStep: 1,
      isLoading: false,
      error: null,
      answers: {},
      _hasHydrated: false,
      
      setAnswer: (fieldId, value) => set((state) => ({
        answers: { ...state.answers, [fieldId]: value }
      })),
      
      setAnswers: (answers) => set({ answers }),
      
      nextStep: () => set((state) => ({
        currentStep: Math.min(state.currentStep + 1, 21)
      })),
      
      prevStep: () => set((state) => ({
        currentStep: Math.max(state.currentStep - 1, 1)
      })),
      
      goToStep: (step) => set({ currentStep: step }),
      
      reset: () => set({
        currentStep: 1,
        answers: {},
        error: null
      }),
      
      setHasHydrated: (state) => set({ _hasHydrated: state }),
      
      // Async methods would call API endpoints
    }),
    {
      name: 'raptorflow-onboarding', // localStorage key
      partialize: (state) => ({ 
        // Only persist answers, not loading states
        answers: state.answers 
      }),
      onRehydrateStorage: () => (state) => {
        state?.setHasHydrated(true);
      }
    }
  )
);
```

The persistence layer ensures users can close their browser mid-onboarding and resume without losing progress. When they return, the store rehydrates from localStorage and they continue where they left off.

---

## 2.3 BACKEND ONBOARDING SCHEMA

**File:** `backend/api/v1/workspaces/routes.py`

The canonical onboarding schema is defined as a Python constant:

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
    {
        "id": "company_website",
        "title": "Company Website",
        "description": "Primary website URL for the business.",
        "fields": [
            {
                "id": "company_website",
                "label": "Company Website",
                "kind": "url",
                "required": False,
                "placeholder": "https://acme.com",
            }
        ],
    },
    {
        "id": "industry",
        "title": "Industry",
        "description": "Market category the company operates in.",
        "fields": [
            {
                "id": "industry",
                "label": "Industry",
                "kind": "short_text",
                "required": True,
                "placeholder": "SaaS / FinTech / E-commerce",
            }
        ],
    },
    {
        "id": "business_stage",
        "title": "Business Stage",
        "description": "Current maturity stage (pre-seed, seed, growth, etc.).",
        "fields": [
            {
                "id": "business_stage",
                "label": "Business Stage",
                "kind": "short_text",
                "required": True,
                "placeholder": "Seed",
            }
        ],
    },
    {
        "id": "company_description",
        "title": "Company Description",
        "description": "What the company does and why it exists.",
        "fields": [
            {
                "id": "company_description",
                "label": "Company Description",
                "kind": "long_text",
                "required": True,
                "placeholder": "Two to five sentence company description.",
            }
        ],
    },
    {
        "id": "primary_offer",
        "title": "Primary Offer",
        "description": "Main product/service sold to customers.",
        "fields": [
            {
                "id": "primary_offer",
                "label": "Primary Offer",
                "kind": "short_text",
                "required": True,
                "placeholder": "AI-powered project management platform"
            }
        ],
    },
    {
        "id": "core_problem",
        "title": "Core Problem Solved",
        "description": "Most painful problem solved for customers.",
        "fields": [
            {
                "id": "core_problem",
                "label": "Core Problem Solved",
                "kind": "long_text",
                "required": True,
                "placeholder": "What painful outcome is prevented?"
            }
        ],
    },
    {
        "id": "ideal_customer_title",
        "title": "Ideal Customer Title",
        "description": "Role or persona of the primary buyer/user.",
        "fields": [
            {
                "id": "ideal_customer_title",
                "label": "Ideal Customer Title",
                "kind": "short_text",
                "required": True,
                "placeholder": "VP Engineering"
            }
        ],
    },
    {
        "id": "ideal_customer_profile",
        "title": "Ideal Customer Profile",
        "description": "Demographic and firmographic description of the ICP.",
        "fields": [
            {
                "id": "ideal_customer_profile",
                "label": "Ideal Customer Profile",
                "kind": "long_text",
                "required": True,
                "placeholder": "B2B SaaS companies, 20-200 employees, remote teams."
            }
        ],
    },
    {
        "id": "top_pain_points",
        "title": "Top Pain Points",
        "description": "Top customer pains (comma-separated or newline-separated).",
        "fields": [
            {
                "id": "top_pain_points",
                "label": "Top Pain Points",
                "kind": "list",
                "required": True,
                "placeholder": "Low conversion rates, poor retention, unclear attribution"
            }
        ],
    },
    {
        "id": "top_goals",
        "title": "Top Customer Goals",
        "description": "Goals customers want to achieve (list).",
        "fields": [
            {
                "id": "top_goals",
                "label": "Top Customer Goals",
                "kind": "list",
                "required": True,
                "placeholder": "Increase pipeline velocity, reduce churn"
            }
        ],
    },
    {
        "id": "key_differentiator",
        "title": "Key Differentiator",
        "description": "What makes this solution different and defensible.",
        "fields": [
            {
                "id": "key_differentiator",
                "label": "Key Differentiator",
                "kind": "long_text",
                "required": True,
                "placeholder": "Our mechanism competitors cannot replicate easily."
            }
        ],
    },
    {
        "id": "competitors",
        "title": "Competitors",
        "description": "Direct and indirect competitors (list).",
        "fields": [
            {
                "id": "competitors",
                "label": "Competitors",
                "kind": "list",
                "required": True,
                "placeholder": "Competitor A, Competitor B"
            }
        ],
    },
    {
        "id": "brand_tone",
        "title": "Brand Tone",
        "description": "How the brand should sound (list of tone descriptors).",
        "fields": [
            {
                "id": "brand_tone",
                "label": "Brand Tone",
                "kind": "list",
                "required": True,
                "placeholder": "Direct, confident, practical"
            }
        ],
    },
    {
        "id": "banned_phrases",
        "title": "Banned Words/Phrases",
        "description": "Words and phrases the brand should avoid.",
        "fields": [
            {
                "id": "banned_phrases",
                "label": "Banned Words/Phrases",
                "kind": "list",
                "required": False,
                "placeholder": "Revolutionary, game-changing, synergy"
            }
        ],
    },
    {
        "id": "channel_priorities",
        "title": "Channel Priorities",
        "description": "Primary go-to-market channels in priority order (list).",
        "fields": [
            {
                "id": "channel_priorities",
                "label": "Channel Priorities",
                "kind": "list",
                "required": True,
                "placeholder": "LinkedIn, Email, YouTube"
            }
        ],
    },
    {
        "id": "geographic_focus",
        "title": "Geographic Focus",
        "description": "Primary markets or geographies served.",
        "fields": [
            {
                "id": "geographic_focus",
                "label": "Geographic Focus",
                "kind": "short_text",
                "required": False,
                "placeholder": "United States and EU"
            }
        ],
    },
    {
        "id": "pricing_model",
        "title": "Pricing Model",
        "description": "How the product is priced and sold.",
        "fields": [
            {
                "id": "pricing_model",
                "label": "Pricing Model",
                "kind": "short_text",
                "required": False,
                "placeholder": "Per-seat monthly SaaS"
            }
        ],
    },
    {
        "id": "proof_points",
        "title": "Proof Points",
        "description": "Evidence, traction, metrics, or testimonials (list).",
        "fields": [
            {
                "id": "proof_points",
                "label": "Proof Points",
                "kind": "list",
                "required": False,
                "placeholder": "2.1M ARR, 40% MoM growth, NPS 62"
            }
        ],
    },
    {
        "id": "acquisition_goal",
        "title": "Primary Acquisition Goal",
        "description": "Short-term growth objective for the system to optimize.",
        "fields": [
            {
                "id": "acquisition_goal",
                "label": "Primary Acquisition Goal",
                "kind": "short_text",
                "required": True,
                "placeholder": "Generate 60 SQLs per month"
            }
        ],
    },
    {
        "id": "constraints_and_guardrails",
        "title": "Constraints and Guardrails",
        "description": "Hard constraints for messaging and execution (list).",
        "fields": [
            {
                "id": "constraints_and_guardrails",
                "label": "Constraints and Guardrails",
                "kind": "list",
                "required": True,
                "placeholder": "No legal claims without proof, no competitor bashing"
            }
        ],
    },
]
```

This schema is the single source of truth. Both frontend (for rendering) and backend (for validation) use this definition.

---

## 2.4 THE 21 STEPS - DETAILED DOCUMENTATION

### STEP 1: Company Name

**Component:** `src/components/onboarding/pages/PageCompanyName.tsx`

This is the first impression of the onboarding experience. The component uses GSAP animations to create an immersive, high-end feel.

**User Interface:**
- Full-screen dark background with subtle grain texture overlay
- Animated compass logo that drops from top with rotation on entrance
- Progress indicator showing "Step 01 / 21" at top
- Massive typography for the question: "What is your company name?"
- Single text input with placeholder cycling through examples
- Character counter "X / 50"
- Navigation: Back button (disabled), Continue button (appears when valid)

**Input Specifications:**
- Type: Single-line text input
- Max length: 50 characters
- Validation: Minimum 2 characters required
- Auto-complete: organization (browser autocomplete for company names)
- Spellcheck: disabled

**Frontend State Mapping:**
```typescript
// In foundationStore
answers: {
  company_name: "Acme Labs"  // string, stored directly
}
```

**Backend Pydantic Schema:**
```python
class CompanyNameField(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=50)
```

**BCM Synthesis Usage:**
This field populates the foundational company identity:
- `foundation.company.name` - The primary company identifier
- Used in every generated piece of content as the subject
- Referenced in brand voice training prompts
- Displayed throughout the dashboard and analytics

**GSAP Animations:**

Entrance Timeline (2.2 seconds):
```javascript
// Grain texture fades in
gsap.fromTo(".grain", { opacity: 0 }, { opacity: 0.03, duration: 2.5 });

// Compass logo animates in with bounce
gsap.fromTo(".compass",
  { y: -160, opacity: 0, rotation: -40, scale: 0.7 },
  { y: 0, opacity: 1, rotation: 0, scale: 1, duration: 2.2, ease: "back.out(1.02)" }
);

// Step indicator slides in
gsap.fromTo(".step", { opacity: 0, x: -50 }, { opacity: 1, x: 0, duration: 1.2 });

// Progress bar grows
gsap.fromTo(".progress", 
  { scaleX: 0 }, 
  { scaleX: currentPage / totalPages, duration: 3, ease: "power2.inOut" }
);

// Question number letter-spacing animation
gsap.fromTo(".qnum",
  { opacity: 0, letterSpacing: "1.2em" },
  { opacity: 1, letterSpacing: "0.5em", duration: 2 }
);

// Headline words animate with 3D rotation
gsap.fromTo(".hword",
  { opacity: 0, y: 100, rotateX: -60 },
  { opacity: 1, y: 0, rotateX: 0, duration: 1.6, stagger: 0.25, ease: "power3.out" }
);

// Input wrapper rises up
gsap.fromTo(".inputwrap",
  { opacity: 0, y: 140, scale: 0.85 },
  { opacity: 1, y: 0, scale: 1, duration: 1.8, ease: "power3.out" }
);

// Helper text fades in
gsap.fromTo(".helper", { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 1.2 });

// Navigation rises up
gsap.fromTo(".nav", { opacity: 0, y: 80 }, { opacity: 1, y: 0, duration: 1.4 });
```

Idle Animations (continuous):
```javascript
// Compass gently floats
gsap.to(".compass", {
  y: "-=12",
  duration: 10,
  repeat: -1,
  yoyo: true,
  ease: "sine.inOut",
  delay: 3,
});

// Grain texture moves subtly
gsap.to(".grain", {
  x: "+=100",
  y: "+=100",
  duration: 50,
  repeat: -1,
  ease: "none",
});
```

Focus State Animation:
```javascript
// When user clicks into input
gsap.to(inputWrapRef.current, {
  y: -16,
  boxShadow: "0 100px 280px rgba(42, 37, 41, 0.18)",
  duration: 0.8,
  ease: "power2.out",
});

gsap.to(".glow", { opacity: 1, duration: 0.7 });
gsap.to(".line", { scaleX: 1, duration: 0.8, ease: "power2.out" });
gsap.to(".dim", { opacity: 0.4, duration: 0.7 });
gsap.to(".compass", { scale: 1.15, duration: 0.6, ease: "power2.out" });
```

Valid State Animation (2+ characters entered):
```javascript
// Green checkmark appears
gsap.to(".dot", { scale: 1, opacity: 1, duration: 0.7, ease: "back.out(3)" });

// Continue button slides in
gsap.to(".btn", { opacity: 1, y: 0, duration: 1, ease: "power3.out" });

// Counter turns green
gsap.to(".count", { color: "#16a34a", scale: 1.15, duration: 0.5, ease: "back.out(2)" });
```

Error Shake Animation:
```javascript
// When validation fails
const tl = gsap.timeline();
tl.to(inputWrapRef.current, { x: 18, duration: 0.08, ease: "power2.in" })
  .to(inputWrapRef.current, { x: -36, duration: 0.12, yoyo: true, repeat: 3, ease: "power2.inOut" })
  .to(inputWrapRef.current, { x: 0, duration: 1, ease: "elastic.out(1, 0.2)" });
```

Exit Animation:
```javascript
// When clicking Continue
gsap.to(inputWrapRef.current, {
  scale: 0.92,
  duration: 0.25,
  ease: "power2.in",
  onComplete: () => {
    gsap.to(".page", {
      opacity: 0,
      x: -150,
      filter: "blur(12px)",
      duration: 0.8,
      ease: "power3.in",
      onComplete: onNext,
    });
  },
});
```

**Why This Data Is Critical:**
The company name is the most fundamental piece of information. It appears in:
- Every generated piece of content
- The dashboard header
- Analytics reports
- Email sender names
- Social media profiles
- All API responses and database records

Without this, the system cannot produce any meaningful marketing content.

---

### STEP 2: Company Website

**Component:** `src/components/onboarding/pages/PageCompanyWebsite.tsx`

**User Interface:**
- Similar layout to Step 1 with updated headline
- URL input field with automatic protocol validation
- Optional helper text explaining the use case

**Input Specifications:**
- Type: URL input
- Validation: Must start with http:// or https://
- Required: No (optional field)
- Placeholder: "https://acme.com"

**Frontend State:**
```typescript
answers: {
  company_website: "https://acme.com"  // URL string
}
```

**Backend Pydantic Schema:**
```python
class CompanyWebsiteField(BaseModel):
    company_website: Optional[str] = Field(None, pattern=r"^https?://")
```

**BCM Synthesis Usage:**
- `foundation.company.website` - Primary website URL
- Used as default CTA destination in all generated content
- Scraped for additional brand intelligence (optional feature)
- Referenced in analytics attribution

**Why This Data Is Critical:**
The website URL enables:
- Automatic link insertion in all content
- Brand analysis and competitive research
- Landing page recommendations
- Attribution tracking in analytics

---

### STEP 3: Industry / Vertical Selection

**Component:** `src/components/onboarding/pages/PageIndustry.tsx`

**User Interface:**
- Headline: "What industry do you operate in?"
- Free-form text input with industry suggestions/autocomplete
- Visual icons for common industries (optional)

**Input Specifications:**
- Type: Short text with autocomplete
- Required: Yes
- Max length: 100 characters
- Placeholder: "SaaS / FinTech / E-commerce"

**Frontend State:**
```typescript
answers: {
  industry: "SaaS"
}
```

**Backend Pydantic Schema:**
```python
class IndustryField(BaseModel):
    industry: str = Field(..., min_length=1, max_length=100)
```

**BCM Synthesis Usage:**
- `foundation.company.industry` - Industry classification
- Drives ICP template selection
- Enables competitive benchmarking within vertical
- Influences messaging style (B2B vs B2C, technical depth)

**Industry Suggestions (autocomplete):**
The frontend may provide suggestions from a predefined list:
- SaaS (Software as a Service)
- FinTech (Financial Technology)
- E-commerce / Retail
- Healthcare / HealthTech
- EdTech (Education Technology)
- Real Estate
- Manufacturing
- Professional Services
- Media / Entertainment
- Non-profit

---

### STEP 4: Business Stage

**Component:** `src/components/onboarding/pages/PageBusinessStage.tsx`

**User Interface:**
- Headline: "What stage is your business at?"
- Selection cards for each stage with descriptions

**Input Specifications:**
- Type: Single select from predefined options
- Required: Yes
- Options: ["Pre-seed", "Seed", "Series A", "Series B", "Growth", "Enterprise"]

**Frontend State:**
```typescript
answers: {
  business_stage: "Seed"  // One of predefined options
}
```

**Backend Pydantic Schema:**
```python
class BusinessStageField(BaseModel):
    business_stage: str = Field(..., pattern=r"^(Pre-seed|Seed|Series A|Series B|Growth|Enterprise)$")
```

**BCM Synthesis Usage:**
- `foundation.company.stage` - Maturity stage
- Influences messaging sophistication
- Affects competitive positioning strategy
- Guides goal-setting realism (early stage = awareness, late stage = conversion)

**Business Stage Descriptions:**
- **Pre-seed:** Idea/concept stage, no revenue yet
- **Seed:** Early product, some early users, pre-revenue or early revenue
- **Series A:** Product-market fit, scaling initial customer base
- **Series B:** Proven model, scaling operations
- **Growth:** Established market position, maximizing efficiency
- **Enterprise:** Market leader, brand-driven growth

---

### STEP 5: Company Description

**Component:** `src/components/onboarding/pages/PageCompanyDescription.tsx`

**User Interface:**
- Headline: "Describe what your company does"
- Multi-line textarea for detailed description
- Character counter
- Helper text: "Be specific about your core offering and target customers"

**Input Specifications:**
- Type: Long text (textarea)
- Required: Yes
- Min length: 50 characters
- Max length: 1000 characters
- Placeholder: "Two to five sentence company description."

**Frontend State:**
```typescript
answers: {
  company_description: "Acme Labs is a B2B SaaS platform that helps sales teams..."  // Multi-line string
}
```

**Backend Pydantic Schema:**
```python
class CompanyDescriptionField(BaseModel):
    company_description: str = Field(..., min_length=50, max_length=1000)
```

**BCM Synthesis Usage:**
- `foundation.company.description` - Full company narrative
- Primary training material for AI context
- Source for value proposition extraction
- Used in About pages, bio sections, press releases

**Content Guidance:**
The placeholder provides guidance on what to include:
- What the product/service does
- Who it's for (target customer)
- What problem it solves
- What makes it different

---

### STEP 6: Primary Offer

**Component:** `src/components/onboarding/pages/PagePrimaryOffer.tsx`

**User Interface:**
- Headline: "What is your primary offer?"
- Single-line input
- Helper text distinguishing "offer" from "product"

**Input Specifications:**
- Type: Short text
- Required: Yes
- Max length: 200 characters
- Placeholder: "AI-powered project management platform"

**Frontend State:**
```typescript
answers: {
  primary_offer: "AI-powered project management platform"
}
```

**Backend Pydantic Schema:**
```python
class PrimaryOfferField(BaseModel):
    primary_offer: str = Field(..., min_length=1, max_length=200)
```

**BCM Synthesis Usage:**
- `intelligence.positioning.category` - Core offering category
- Primary element of positioning statement
- Subject of most marketing content
- Used in headlines, value propositions, CTAs

---

### STEP 7: Core Problem Solved

**Component:** `src/components/onboarding/pages/PageCoreProblem.tsx`

**User Interface:**
- Headline: "What painful problem do you solve?"
- Multi-line textarea
- Emphasis on "painful" - the cost of not solving

**Input Specifications:**
- Type: Long text
- Required: Yes
- Min length: 20 characters
- Placeholder: "What painful outcome is prevented?"

**Frontend State:**
```typescript
answers: {
  core_problem: "Sales teams lose deals because they can't identify which prospects are most likely to buy"
}
```

**Backend Pydantic Schema:**
```python
class CoreProblemField(BaseModel):
    core_problem: str = Field(..., min_length=20)
```

**BCM Synthesis Usage:**
- Fills ICP pain points by default
- Used in problem-agitation content
- Drives objection-handling copy
- Core element of "before/after" positioning

---

### STEP 8: Ideal Customer Title

**Component:** `src/components/onboarding/pages/PageIdealCustomerTitle.tsx`

**User Interface:**
- Headline: "Who is your primary buyer?"
- Role/title input field with examples

**Input Specifications:**
- Type: Short text
- Required: Yes
- Placeholder: "VP Engineering"

**Frontend State:**
```typescript
answers: {
  ideal_customer_title: "VP Engineering"
}
```

**Backend Pydantic Schema:**
```python
class IdealCustomerTitleField(BaseModel):
    ideal_customer_title: str = Field(..., min_length=1)
```

**BCM Synthesis Usage:**
- Creates primary ICP with this as the ICP name
- Default target for all content generation
- Drives messaging tone and channel selection

---

### STEP 9: Ideal Customer Profile

**Component:** `src/components/onboarding/pages/PageIdealCustomerProfile.tsx`

**User Interface:**
- Headline: "Describe your ideal customer"
- Multi-line textarea
- Prompts for firmographics and demographics

**Input Specifications:**
- Type: Long text
- Required: Yes
- Placeholder: "B2B SaaS companies, 20-200 employees, remote teams"

**Frontend State:**
```typescript
answers: {
  ideal_customer_profile: "Mid-market B2B SaaS companies, 50-200 employees, Series A-B funding..."
}
```

**Backend Pydantic Schema:**
```python
class IdealCustomerProfileField(BaseModel):
    ideal_customer_profile: str = Field(..., min_length=1)
```

**BCM Synthesis Usage:**
- Populates ICP demographics and psychographics
- Used for audience targeting in ads
- Informs channel selection (where does this persona spend time?)
- Enables personalization in email and content

---

### STEP 10: Top Pain Points

**Component:** `src/components/onboarding/pages/PageTopPainPoints.tsx`

**User Interface:**
- Headline: "What are your customers' top pain points?"
- List input - accepts comma-separated or newline-separated values
- Tag-based UI for entered pain points

**Input Specifications:**
- Type: List (array of strings)
- Required: Yes
- Backend normalizes: splits on commas, newlines, semicolons
- Placeholder: "Low conversion rates, poor retention, unclear attribution"

**Frontend State:**
```typescript
answers: {
  top_pain_points: ["Low conversion rates", "Poor retention", "Unclear attribution"]
}
```

**Backend Normalization:**
```python
def _normalize_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    if isinstance(value, str):
        # Split on common delimiters
        items = re.split(r'[\n,;]+', value)
        return [i.strip() for i in items if i.strip()]
    return []
```

**BCM Synthesis Usage:**
- `icps[].painPoints` - List of customer problems
- Used in problem-agitation content
- Drives solution messaging
- Enables empathy in copy

---

### STEP 11: Top Customer Goals

**Component:** `src/components/onboarding/pages/PageTopGoals.tsx`

**User Interface:**
- Headline: "What goals do your customers want to achieve?"
- Similar list input to pain points

**Input Specifications:**
- Type: List
- Required: Yes
- Placeholder: "Increase pipeline velocity, reduce churn"

**Frontend State:**
```typescript
answers: {
  top_goals: ["Increase pipeline velocity", "Reduce churn", "Improve forecast accuracy"]
}
```

**BCM Synthesis Usage:**
- `icps[].goals` - What customers want to achieve
- Used in aspiration-focused content
- Enables outcome-based messaging
- Drives value proposition framing

---

### STEP 12: Key Differentiator

**Component:** `src/components/onboarding/pages/PageKeyDifferentiator.tsx`

**User Interface:**
- Headline: "What makes you different?"
- Multi-line textarea
- Emphasis on defensibility and uniqueness

**Input Specifications:**
- Type: Long text
- Required: Yes
- Placeholder: "Our mechanism competitors cannot replicate easily"

**Frontend State:**
```typescript
answers: {
  key_differentiator: "Our AI predicts deal closure with 92% accuracy using proprietary signal analysis"
}
```

**BCM Synthesis Usage:**
- `intelligence.positioning.differentiators` - Competitive edge
- Core element of positioning vs competitors
- Used in comparison content
- Enables "why us" messaging

---

### STEP 13: Competitors

**Component:** `src/components/onboarding/pages/PageCompetitors.tsx`

**User Interface:**
- Headline: "Who are your main competitors?"
- List input
- Helper explaining direct vs indirect competitors

**Input Specifications:**
- Type: List
- Required: Yes
- Max items: 8 (backend limit)
- Placeholder: "Competitor A, Competitor B"

**Frontend State:**
```typescript
answers: {
  competitors: ["Salesforce", "HubSpot", "Gong"]
}
```

**Backend Processing:**
```python
# Transforms to structured objects
competitor_objects = [
    {"name": name, "type": "direct"} 
    for name in competitor_names[:8]
]
```

**BCM Synthesis Usage:**
- `intelligence.positioning.competitors` - Competitive landscape
- Enables competitive positioning content
- Used in "why not them" messaging
- Tracks competitive mentions

---

### STEP 14: Brand Tone

**Component:** `src/components/onboarding/pages/PageBrandTone.tsx`

**User Interface:**
- Headline: "How should your brand sound?"
- Multi-select tone descriptors with examples

**Input Specifications:**
- Type: List
- Required: Yes
- Options: ["Direct", "Confident", "Practical", "Playful", "Authoritative", "Empathetic", "Professional", "Casual"]

**Frontend State:**
```typescript
answers: {
  brand_tone: ["Direct", "Confident", "Practical"]
}
```

**BCM Synthesis Usage:**
- `messaging.brandVoice.tone` - Voice characteristics
- Drives AI prompt construction
- Used in tone consistency enforcement
- Affects all generated content

---

### STEP 15: Banned Phrases

**Component:** `src/components/onboarding/pages/PageBannedPhrases.tsx`

**User Interface:**
- Headline: "What words should your brand never use?"
- List input
- Common buzzword warnings

**Input Specifications:**
- Type: List
- Required: No
- Placeholder: "Revolutionary, game-changing, synergy"

**Frontend State:**
```typescript
answers: {
  banned_phrases: ["revolutionary", "game-changing", "synergy", "leverage"]
}
```

**BCM Synthesis Usage:**
- `messaging.brandVoice.dontList` - Prohibited vocabulary
- Used as hard guardrails in content generation
- Flagged in content review
- Prevents generic marketing speak

---

### STEP 16: Channel Priorities

**Component:** `src/components/onboarding/pages/PageChannelPriorities.tsx`

**User Interface:**
- Headline: "What are your primary channels?"
- Ranked list input with channel icons

**Input Specifications:**
- Type: List (ordered by priority)
- Required: Yes
- Max items: 8
- Placeholder: "LinkedIn, Email, YouTube"

**Frontend State:**
```typescript
answers: {
  channel_priorities: ["LinkedIn", "Email", "YouTube", "Twitter"]
}
```

**Backend Processing:**
```python
# Creates channel objects with priority levels
channel_objects = []
for index, channel in enumerate(channels[:8]):
    priority = "primary" if index == 0 else "secondary" if index <= 2 else "experimental"
    channel_objects.append({"name": channel, "priority": priority})
```

**BCM Synthesis Usage:**
- `intelligence.channels` - Channel strategy
- Drives channel-specific content generation
- Influences resource allocation recommendations
- Sets posting frequency by channel

---

### STEP 17: Geographic Focus

**Component:** `src/components/onboarding/pages/PageGeographicFocus.tsx`

**User Interface:**
- Headline: "What markets do you serve?"
- Geographic selector or text input

**Input Specifications:**
- Type: Short text
- Required: No
- Placeholder: "United States and EU"

**Frontend State:**
```typescript
answers: {
  geographic_focus: "United States, Canada, UK"
}
```

**BCM Synthesis Usage:**
- `market.geo` - Geographic targeting
- Drives timezone-aware scheduling
- Influences cultural messaging adaptation
- Enables local market content

---

### STEP 18: Pricing Model

**Component:** `src/components/onboarding/pages/PagePricingModel.tsx`

**User Interface:**
- Headline: "How do you price your product?"
- Single-line input with pricing examples

**Input Specifications:**
- Type: Short text
- Required: No
- Placeholder: "Per-seat monthly SaaS"

**Frontend State:**
```typescript
answers: {
  pricing_model: "$99/user/month, annual contract"
}
```

**BCM Synthesis Usage:**
- Creates fact object in `intelligence.facts`
- Used in objection handling around pricing
- Enables ROI calculations in content
- Informs "investment" vs "cost" framing

---

### STEP 19: Proof Points

**Component:** `src/components/onboarding/pages/PageProofPoints.tsx`

**User Interface:**
- Headline: "What evidence supports your claims?"
- List input for metrics, testimonials, traction

**Input Specifications:**
- Type: List
- Required: No
- Placeholder: "2.1M ARR, 40% MoM growth, NPS 62"

**Frontend State:**
```typescript
answers: {
  proof_points: ["2.1M ARR", "40% month-over-month growth", "NPS of 62", "200+ enterprise customers"]
}
```

**Backend Processing:**
```python
# Creates fact objects with high confidence
facts.append({
    "id": f"f-proof-{idx}",
    "category": "traction",
    "label": f"Proof Point {idx}",
    "value": item,
    "confidence": 0.86  # High confidence for user-provided facts
})
```

**BCM Synthesis Usage:**
- `intelligence.facts` - Credibility evidence
- Used as social proof in content
- Enables data-driven marketing
- Builds trust with prospects

---

### STEP 20: Acquisition Goal

**Component:** `src/components/onboarding/pages/PageAcquisitionGoal.tsx`

**User Interface:**
- Headline: "What is your primary growth objective?"
- Focus on measurable outcome

**Input Specifications:**
- Type: Short text
- Required: Yes
- Placeholder: "Generate 60 SQLs per month"

**Frontend State:**
```typescript
answers: {
  acquisition_goal: "Generate 60 SQLs per month"
}
```

**BCM Synthesis Usage:**
- `market.primary_goal` - North Star metric
- Drives goal-oriented content strategy
- Enables ROI-focused messaging
- Sets optimization targets for AI

---

### STEP 21: Constraints and Guardrails

**Component:** `src/components/onboarding/pages/PageConstraintsAndGuardrails.tsx`

**User Interface:**
- Headline: "What are your hard constraints?"
- Multi-line textarea for legal, regulatory, brand constraints
- Examples: "No health claims without FDA approval", "No competitor bashing"

**Input Specifications:**
- Type: List
- Required: Yes
- Placeholder: "No legal claims without proof, no competitor bashing"

**Frontend State:**
```typescript
answers: {
  constraints_and_guardrails: [
    "No health claims without FDA approval",
    "No competitor bashing",
    "Must include disclaimer on all financial content"
  ]
}
```

**BCM Synthesis Usage:**
- `messaging.guardrails` - Hard constraints
- Critical for compliance in regulated industries
- Used as mandatory rules in generation
- Legal protection for the business

---

## 2.5 ONBOARDING COMPLETION AND BCM GENERATION

When the user completes Step 21, the complete onboarding flow executes:

### Frontend API Call

```typescript
const response = await fetch(`/api/workspaces/${workspaceId}/onboarding/complete`, {
  method: 'POST',
  headers: { 
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    schema_version: "2026.03.0",
    answers: foundationStore.getState().answers
  })
});
```

### Backend Processing Pipeline

**1. Validation:**
```python
# _validate_and_normalize_answers()
def _validate_and_normalize_answers(raw_answers: Dict[str, Any]) -> Dict[str, Any]:
    # Check for unknown fields
    unknown_fields = [f for f in raw_answers if f not in _CANONICAL_FIELD_BY_ID]
    if unknown_fields:
        raise HTTPException(400, {"unknown_fields": unknown_fields})
    
    # Normalize each field by kind
    normalized = {}
    for field_id, field in _CANONICAL_FIELD_BY_ID.items():
        normalized[field_id] = _normalize_field_value(
            kind=str(field.get("kind")),
            raw_value=raw_answers.get(field_id)
        )
    return normalized
```

**2. Business Context Building:**
```python
# _build_business_context()
def _build_business_context(workspace_row, answers) -> Dict:
    # Extract and transform all onboarding data
    company_name = answers.get("company_name") or workspace_row.get("name")
    industry = answers.get("industry") or ""
    stage = answers.get("business_stage") or ""
    description = answers.get("company_description") or ""
    primary_offer = answers.get("primary_offer") or ""
    core_problem = answers.get("core_problem") or ""
    customer_title = answers.get("ideal_customer_title") or "Primary Buyer"
    customer_profile = answers.get("ideal_customer_profile") or ""
    pain_points = _normalize_list(answers.get("top_pain_points"))
    goals = _normalize_list(answers.get("top_goals"))
    differentiator = answers.get("key_differentiator") or ""
    competitor_names = _normalize_list(answers.get("competitors"))
    tone = _normalize_list(answers.get("brand_tone"))
    banned = _normalize_list(answers.get("banned_phrases"))
    channels = _normalize_list(answers.get("channel_priorities"))
    geography = answers.get("geographic_focus") or ""
    pricing_model = answers.get("pricing_model") or ""
    proof_points = _normalize_list(answers.get("proof_points"))
    acquisition_goal = answers.get("acquisition_goal") or ""
    constraints = _normalize_list(answers.get("constraints_and_guardrails"))
    
    # Build derived fields
    one_liner = f"{company_name}: {primary_offer} {differentiator}".strip()
    positioning_statement = (
        f"For {customer_title}, {company_name} solves {core_problem}. "
        f"We do this through {primary_offer}. "
        f"Our edge is {differentiator}."
    ).strip()
    
    # Build structured business context
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
            "evidence_count": len(proof_points) + (1 if pricing_model else 0),
            "facts": _build_facts(pricing_model, acquisition_goal, proof_points),
            "icps": [_build_icp(customer_title, customer_profile, pain_points, goals)],
            "positioning": {
                "category": primary_offer,
                "categoryPath": "bold",
                "uvp": differentiator or primary_offer,
                "differentiators": [differentiator] + proof_points[:3],
                "competitors": [{"name": c, "type": "direct"} for c in competitor_names[:8]],
            },
            "messaging": {
                "oneLiner": one_liner,
                "positioningStatement": positioning_statement,
                "valueProps": [{"title": "Primary Offer", "description": primary_offer}],
                "brandVoice": {
                    "tone": tone,
                    "doList": constraints[:5],
                    "dontList": banned[:5],
                },
                "soundbites": [one_liner],
                "guardrails": constraints + [f"Avoid phrase: {b}" for b in banned[:3]],
            },
            "channels": _build_channels(channels),
            "market": {
                "geo": geography,
                "primary_goal": acquisition_goal,
            },
        },
    }
    
    return business_context
```

**3. AI Synthesis:**
```python
# langgraph_context_orchestrator.seed()
bcm_row = await langgraph_context_orchestrator.seed(workspace_id, business_context)
```

This invokes the Muse AI to synthesize and enhance the basic business context into a full-featured BCM with AI-generated components like identity archetypes, prompt templates, and refined guardrails.

**4. Foundation Upsert:**
```python
# _upsert_foundation_from_business_context()
supabase.table("foundations").upsert({
    "workspace_id": workspace_id,
    "company_info": {
        "name": company.get("name", ""),
        "website": company.get("website", ""),
        "industry": company.get("industry", ""),
        "stage": company.get("stage", ""),
        "description": company.get("description", ""),
    },
    "mission": company.get("description", ""),
    "value_proposition": intel.get("positioning", {}).get("uvp", ""),
    "brand_voice": messaging.get("brandVoice", {}),
    "messaging": messaging,
    "status": "active",
}, on_conflict="workspace_id").execute()
```

**5. Workspace Settings Update:**
```python
# _mark_bcm_ready()
settings["onboarding"] = {
    "schema_version": ONBOARDING_SCHEMA_VERSION,
    "completed": True,
    "completed_at": now_iso,
    "updated_at": now_iso,
    "answers": normalized_answers,
    "total_steps": len(CANONICAL_ONBOARDING_STEPS),
    "required_steps": _REQUIRED_STEP_IDS,
}
settings["business_context"] = business_context
settings["bcm"] = {
    "ready": True,
    "version": bcm_payload.get("version"),
    "checksum": bcm_payload.get("checksum"),
    "completion_pct": bcm_payload.get("completion_pct", 0),
    "synthesized": bcm_payload.get("synthesized", False),
    "updated_at": now_iso,
}
settings["bcm_ready"] = True
settings["orchestrator"] = "langgraph"
```

### Response to Frontend

```json
{
  "workspace": {
    "id": "workspace-123",
    "name": "Acme Labs",
    "slug": "acme-labs",
    "settings": { "bcm_ready": true }
  },
  "onboarding": {
    "completed": true,
    "bcm_ready": true,
    "completion_pct": 100,
    "schema_version": "2026.03.0"
  },
  "bcm": {
    "version": "2.1",
    "checksum": "abc123",
    "synthesized": true,
    "completion_pct": 100
  },
  "business_context": { /* Full business context */ }
}
```

The user is now ready to use RaptorFlow for autonomous marketing generation.
