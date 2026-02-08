# Specification: Onboarding Master System (25-Phase Architecture)

## 1. Overview
The Onboarding Master System is a high-precision backend implementation for the 23-step RaptorFlow onboarding flow. It leverages a SOTA Cognitive Intelligence Engine to convert raw user input and evidence into a structured `business_context.json`, which is then transformed into a Business Context Map (BCM). The system is built for concurrency, data integrity, and autonomous research capability.

## 2. Functional Requirements

### 2.1 State & Context Management
- **LangGraph Orchestration**: Use a stateful graph to manage the 23-step flow, ensuring each step has access to the full accumulated context.
- **Universal State (`business_context.json`)**: Every user interaction and AI insight must update a single source of truth.
- **BCM Conversion**: Real-time recalculation of the Business Context Map (BCM) as the context evolves.
- **UCID Integration**: Every session is mapped to a Unique Customer ID (RF-YYYY-XXXX).

### 2.2 Intelligence & Research
- **Evidence Classifier**: Auto-recognition of uploaded documents (screenshots, decks, manifestos) and URLs.
- **Extraction Engine**: Deep fact extraction from multi-source evidence with source citations.
- **Titan Sorter Integration**: Autonomous web research (Reddit, G2, etc.) to verify claims and extract market intelligence.
- **Neuroscience Copywriter**: 6-principle copywriting engine for positioning statements and manifestos.
- **Red Team Auditor**: An adversarial agent that identifies contradictions, hallucinations, and strategic gaps in the onboarding state.

### 2.3 Security & Privacy
- **Data Purge Protocol**: Automatic deletion of uploaded source files (GCS blobs) once extraction is verified and committed to the JSON state.
- **Conflict Resolution**: Compulsory resolution of "Critical" contradictions before proceeding past Step 4.

## 3. Technical Architecture
- **Framework**: LangGraph with Supabase Checkpointing.
- **LLM**: Google Vertex AI (Gemini 1.5 Pro/Flash).
- **Search**: Titan Sorter (Search Multiplexer + Stealth Scraper Pool).
- **Storage**: Supabase (PostgreSQL + JSONB) for state, temporary GCS for evidence.
- **Verification**: TDD-based implementation with automated logic audits.

## 4. Acceptance Criteria
- [ ] Successful completion of all 23 onboarding steps with 100% data persistence.
- [ ] `business_context.json` correctly reflects all extracted and verified facts.
- [ ] Final Step 23 successfully converts context into a functional BCM.
- [ ] Uploaded files are deleted from GCS after extraction (Step 2).
- [ ] Titan Sorter successfully retrieves real-time market data during Step 7.
- [ ] Red Team agent successfully identifies logical conflicts.

## 5. Out of Scope
- Frontend component redesign (this track focuses on backend logic and data flow).
- CRM/Marketing automation tool integrations.
