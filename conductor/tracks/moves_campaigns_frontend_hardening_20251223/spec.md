# Specification: End-to-End Moves & Campaigns Frontend Hardening

## 1. Overview
This track focuses on the comprehensive analysis, integration, and hardening of the 'Moves' and 'Campaigns' frontend modules. The goal is to ensure a 100% functional, end-to-end experience where the UI is perfectly synchronized with the backend agentic spine, specifically leveraging Google Vertex AI via a simplified "inference_simple" configuration.

## 2. Functional Requirements
### 2.1 Code Integrity & Connectivity
- **File Audit:** Analyze every file in `raptorflow-app/src/app/(moves|campaigns)` and related components.
- **Link Verification:** Ensure all imports, API endpoints, and Supabase hooks are correctly mapped and functional.
- **State Management:** Standardize React state and hooks to handle asynchronous agent responses without UI flickering.

### 2.2 Inference Integration ("inference_simple")
- **Centralized Config:** Implement `inference_simple` support in `.env.example` and a centralized config utility (e.g., `src/lib/inference-config.ts`).
- **Vertex AI Path:** Establish the Google Vertex API key as the singular, mandatory basis for all inference flows in these modules.
- **Backend Proxying:** Ensure the frontend interacts with backend inference nodes securely.

### 2.3 UI Feature Integration
- **Campaign Strategy:** Enable 90-day arc generation directly from UI triggers.
- **Move Generation:** Implement interactive decomposition of milestones into weekly moves.
- **Refinement Loops:** Integrate "Move Refiner" and "Campaign Auditor" feedback displays within the UI.
- **Strategic Pivots:** Build interactive "Pivot Cards" that allow users to apply recommended strategic shifts.

## 3. Acceptance Criteria
- [ ] Successfully generate a Campaign and its Moves from the UI with real data flowing to Supabase.
- [ ] Browser console is 100% clean (zero errors/warnings) during the entire user flow.
- [ ] Automated smoke test confirms UI-to-Backend-to-Vertex-to-Supabase connectivity.
- [ ] Zero build errors in the Next.js frontend related to these modules.
- [ ] Manual side-by-side walkthrough confirms UI state matches database state exactly.

## 4. Out of Scope
- Modifications to core LangGraph logic (unless required for connectivity fixes).
- Changes to the "Blackbox" or "Matrix" modules unless they overlap with shared components.
