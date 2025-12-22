# Specification: Muse V2 Shared Agent Spine

## 1. Overview
Implementation of the "Shared Agent Platform" using a dedicated Python service (FastAPI) orchestrated by **LangGraph**. This service serves as the "Creative Brain" for RaptorFlow, providing shared agents (A00-A16) and a deterministic toolbelt (T01-T44).

## 2. Infrastructure
- **Brain:** Python 3.11+, FastAPI, LangGraph, LangChain.
- **Inference:** Vertex AI (Gemini 1.5 Flash for routing, 1.5 Pro for research/quality).
- **Memory:** LangGraph `PostgresSaver` connecting directly to Supabase.
- **Search:** `pgvector` for RAG and asset retrieval.
- **Visuals:** Konva-based canvas state (JSON) managed by MemeDirector.

## 3. The "Spine" Contracts (Internal API)

### 3.1 Ambiguity Ladder (A00-A02)
The endpoint `/muse/create` must implement the following logic:
1. **Confidence High:** Execute `A03 (Skill Planner)` -> `A04 (Executor)` immediately.
2. **Confidence Medium:** Return `clarify_chips` card payload.
3. **Confidence Low:** Return `clarify_questions` (max 3) and `interrupt()`.

### 3.2 Human-in-the-Loop (HITL)
Graphs for **Publishing** or **External Actions** must use `interrupt()`. 
- Graph state is saved to Supabase via `thread_id`.
- UI polls or receives a "Pending Approval" state.

### 3.3 Card Payload Schema
Every graph response returns a JSON list of cards:
- `suggestion_grid`: Initial UI state.
- `generation_card`: Shows current phase (Drafting/Polishing/Packaging).
- `result_card`: Final asset preview + actionable tools.

## 4. Shared Toolbelt (Core Tools)
- `GetWorkspaceContext`: Pulls brand/plan data.
- `RetrieveAssets`: Vector-based RAG.
- `BrandLint`: Compliance check using A07.
- `CostGovernor`: Enforces per-org token limits.

## 5. Acceptance Criteria
- [ ] **Python Service Live:** Responds to health checks on Cloud Run.
- [ ] **Resumable State:** A graph can be interrupted for a question and resumed via the same `thread_id`.
- [ ] **Direct DB Retrieval:** Agents can find "Brand Guidelines" stored in Supabase without Next.js proxying.
- [ ] **Premium Output:** Skills chain (Subject -> Hook -> Draft -> QA) produces "Surgical" quality assets.
- [ ] **Konva Integration:** Meme concept generates valid JSON for the React-Konva editor.
