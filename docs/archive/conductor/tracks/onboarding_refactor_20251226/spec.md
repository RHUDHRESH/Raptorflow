# Track Spec: Refactor Onboarding & Implement Precision Soundbite Framework 3.0

## 1. Overview
This track aims to fix the current onboarding "onboarding was supposed to be this" redundancy (where ICPs are shown twice) and replace the existing logic with a high-fidelity implementation of the **Precision Soundbite Framework 3.0**. The onboarding will be structured into four distinct, high-detail phases (Phases 3–6) following the "Quiet Luxury" design system.

## 2. Functional Requirements

### 2.1 UI/UX Refactoring (The Fix)
- **Eliminate Redundancy:** Remove the duplicate ICP/Onboarding step identified by the user.
- **Visual Style:** Adhere strictly to the "Quiet Luxury" identity (Canvas: `#F3F4EE`, Ink: `#2D3538`, Playfair Display for page titles, Inter for UI).
- **Progressive Disclosure:** Use a sequential, phase-by-base approach where each phase builds on the previous one's data.

### 2.2 Phase 3: Foundation & Jobs to Be Done (JTBD)
- **JTBD Canvas:** Interactive interface to capture Functional, Emotional, and Social jobs (Christensen model).
- **Message Hierarchy Pyramid:** UI to define Brand Essence, Core Message, and Messaging Pillars.
- **Customer Awareness Matrix:** Mapping user segments to the 5 awareness tiers (Unaware to Most Aware).
- **Backend:** Logic to synthesize JTBD inputs into a cohesive brand hierarchy.

### 2.3 Phase 4: Agitation & Identity Research
- **Interactive Research Boards:** Digital "Whiteboard" to aggregate customer pain points, emotional consequences, and voice-of-customer snippets.
- **Validation:** Identify the "Identity/Validation" soundbite (Soundbite #2) based on research.

### 2.4 Phase 5: Mechanism & Differentiation
- **Technical Differentiation Auditor:** Side-by-side comparison tool to define the "Unique Mechanism" (Soundbite #3) vs. competitors.
- **Evidence & Proof Vault:** A centralized modal/sidebar to store stats, testimonials, and guarantees used as mandatory proof for all claims.

### 2.5 Phase 6: Precision Soundbite Studio
- **Hybrid Builder:** A "Draft & Refine" studio that generates high-fidelity drafts based on Phases 3–5.
- **Sequential Flow:** Users unlock and finalize all 7 soundbites (Problem, Agitation, Mechanism, Objection Handling, Transformation, Positioning, Urgency) in sequence.
- **Clarity & Proof Audit:** Every soundbite must pass a validation check against the "Proof Vault" before finalization.

## 3. Technical Requirements
- **Frontend:** Next.js (App Router), TypeScript, Framer Motion for phase transitions.
- **Backend:** Vertex AI (Gemini) for soundbite generation, Supabase for storing framework data, Upstash for caching intermediate drafts.
- **State Management:** Universal State Sync to ensure the "Foundation" module is updated as the user completes onboarding.

## 4. Acceptance Criteria
- [ ] Onboarding no longer shows ICP questions/results twice.
- [ ] Phase 3 successfully generates a JTBD and Message Hierarchy.
- [ ] Phase 5 contains a functional "Proof Vault" with at least 3 linked evidence items.
- [ ] Phase 6 outputs exactly 7 soundbites, each validated against a specific job or proof point.
- [ ] UI matches the RaptorFlow design system (Playfair headings, minimalist borders, generous whitespace).

## 5. Out of Scope
- Integration with the "Moves" or "Campaigns" modules (those use the output of this track).
- Billing or Subscription logic.
