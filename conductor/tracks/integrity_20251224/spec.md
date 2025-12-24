# Spec: End-to-End System Integrity Restoration

## Overview
This track is a high-priority, comprehensive audit and restoration of the entire RaptorFlow ecosystem. The goal is to eliminate all environment misconfigurations, linting errors, type-safety warnings, and runtime console noise, ensuring every module (Foundation, Cohorts, Moves, Campaigns, Muse, Matrix, Blackbox) is fully functional and production-ready.

## Functional Requirements
- **Environment Parity:** Audit and synchronize all environment variables across `.env.local`, GCP Secret Manager, and Supabase.
- **Zero-Warning Startup:** Eliminate all startup warnings in `raptorflow-app` (specifically Supabase errors in `middleware.ts`) and the Python `backend`.
- **Full Module Verification:** Perform end-to-end functional tests for all core modules:
    - Foundation (Brand Kit/Positioning)
    - Cohorts (ICP/Segmentation)
    - Moves & Campaigns (Execution Engines)
    - Muse (Asset Factory)
    - Blackbox (Cognitive Spine/Telemetry)
- **Cross-Service Integrity:** Verify that the Next.js frontend, Python backend, LangGraph orchestrators, and Supabase/Redis/GCP infrastructure communicate without failures.

## Non-Functional Requirements
- **Zero Technical Debt:** No linting errors (`eslint`, `flake8`), no TypeScript errors (`tsc`), and no console logs in production builds.
- **RaptorFlow Aesthetic:** Ensure all UI components adhere strictly to the "Quiet Luxury" design system (borders > shadows, editorial typography).

## Acceptance Criteria
- [ ] `npm run dev` and `npm run build` execute in the frontend with zero errors or warnings.
- [ ] The Python backend starts and passes all internal health checks and existing tests.
- [ ] All environment variables are documented and verified as present in the local environment.
- [ ] A full "smoke test" of a user journey (Foundation -> Cohorts -> Moves) completes without a single console error or rendering glitch.
- [ ] All components in `raptorflow-app/src/components` are verified for correct rendering and interaction.

## Out of Scope
- Adding new features or modules not mentioned in the current `product.md`.
- Refactoring the core architectural choice of LangGraph or Supabase.
