# Specification: AI-Powered Onboarding Backend (22+ Steps)

## Overview
This track involves building the backend infrastructure for a comprehensive, 22-step "Onboarding" process for RaptorFlow. The system will be powered by a single **Universal Agent** architecture using **LangChain** (not LangGraph), utilizing a dynamic **Skills System** where each step's logic and AI prompts are defined in loadable YAML files with frontmatter.

## Functional Requirements

### 1. Universal Agent Core
- Implement a `UniversalAgent` class that serves as the single entry point for all onboarding tasks.
- The agent must be capable of loading "Skills" dynamically based on the current onboarding step.
- Architecture: LangChain-based (avoiding LangGraph complexity).

### 2. Dynamic Skill System
- Each onboarding step (up to 24) will have a corresponding "Skill" definition.
- **Skill Format:** YAML files with frontmatter.
  - **Frontmatter:** Contains metadata (`description`, `required_tools`, `output_format`), prompt templates, and tunable parameters.
  - **Content:** The core instruction set or logic for the AI.
- **Skills Registry:** A mechanism to discover and load these YAML-based skills at runtime.

### 3. Immaculate API Layer
- **Framework:** FastAPI for performance and developer experience.
- **Validation:** Pydantic models for strict request/response validation.
- **Documentation:** Auto-generated Swagger/OpenAPI documentation.
- **Endpoints:**
  - `POST /onboarding/{session_id}/steps/{step_id}`: Process data for a specific step.
  - `GET /onboarding/{session_id}/steps/{step_id}`: Retrieve results for a step.
  - `GET /onboarding/{session_id}/status`: Track overall progress.

### 4. Tool Integration
- The system must support a "Tool Registry" where Search, Scraping, and OCR tools (being developed in parallel) can be registered as callable LangChain tools.
- Initial implementation should use interfaces or mocks for these tools to allow development of the core flow.

### 5. Data Persistence (Supabase)
- Store onboarding sessions, step results, extracted facts, and detected issues (contradictions/unproven claims).
- Schema should follow the established patterns in `ONBOARDING_BACKEND_PLAN.md`.

## Non-Functional Requirements
- **Simplicity:** The system must be extremely easy to set up and work with.
- **Performance:** API response times should be optimized (< 2s where feasible, excluding heavy AI processing).
- **Scalability:** The single-agent architecture must handle multiple concurrent onboarding sessions efficiently.

## Acceptance Criteria
- [ ] Universal Agent can successfully load a YAML-defined skill and execute a LangChain call.
- [ ] API endpoints are functional and validated via Pydantic.
- [ ] Data for all 22+ steps can be saved and retrieved from Supabase.
- [ ] The "Skills" are tunable via YAML without changing the core backend code.

## Out of Scope
- User account creation and authentication (handled by another team).
- Frontend implementation (UI/UX).
- Actual development of the Search, Scrape, and OCR tools (only integration is required).
