# Track Spec: SOTA Muse Backend (Production Grade)

## 1. Overview
This track focuses on upgrading the Muse backend from a prototype to a "State-of-the-Art" (SOTA) production-grade Marketing Operating System. Inspired by "Building Generative AI Agents" (2025), the focus is on resilience, speed, and surgical precision using the LangGraph framework.

## 2. Functional Requirements

### 2.1 Cognitive Spine & Logic (Resilience)
- **Dynamic Re-planning:** Implement graphs that can modify their own execution path based on intermediate tool outputs or research findings.
- **Human-in-the-loop (HITL):** Integrate strategic "Interrupt" points for user approval on high-stakes tasks (e.g., final brand positioning, campaign budget).
- **Self-Correction Loops:** Agents must verify their own output against the RaptorFlow Brand Kit before proceeding.

### 2.2 Memory & Context (Intelligence)
- **Vectorized Knowledge (Supabase):** Implement RAG using Supabase pgvector for brand context and historical campaign retrieval.
- **Episodic & Semantic Memory:** Distinguish between specific past interactions (Episodic) and evergreen brand facts (Semantic).
- **Recursive Summarization:** Automatic condensing of long research data and chat histories to maintain context window efficiency.
- **Persistence:** Use LangGraph checkpointers to ensure every "Move" or "Campaign" can be resumed if the process is interrupted.

### 2.3 Operational Efficiency (Speed/Cost)
- **Intelligent Caching:** Integrate Upstash Redis to cache redundant tool calls and common research queries.
- **Model Routing (SLMs):** Use Gemini Flash for summarization and classification; reserve Gemini Pro/o1 for complex reasoning.
- **Parallel Execution:** Refactor nodes to execute independent specialists (Research, Strategy) concurrently.
- **Observability:** Full integration with LangSmith for real-time cost, latency, and trace monitoring.

### 2.4 Specialist Collaboration (Scale)
- **Quality Gates:** Dedicated QA nodes that must "pass" a creative asset before it reaches the user.
- **Standardized Toolbelt:** A unified, validated tool-calling layer for all specialists.

### 2.5 Payments & Billing (Production)
- **PhonePe Integration:** Implement secure checkout flows and webhook handlers for Campaign/Move funding.
- **Payment Lifecycle:** Link payment success to the "Execution" phase of a Campaign or Move.

## 3. Tech Stack
- **Framework:** LangGraph (Python)
- **Database:** Supabase (PostgreSQL + pgvector)
- **Cache:** Upstash Redis
- **Monitoring:** LangSmith
- **Payments:** PhonePe Gateway
- **Models:** Gemini 1.5 Pro/Flash, OpenAI o1/GPT-4o

## 4. Acceptance Criteria
1. Backend can persist state across sessions (Checkpointing).
2. The UI can approve/reject steps via HITL interrupts.
3. Latency for redundant tasks is reduced by >40% via Upstash caching.
4. LangSmith shows a clear "trace" for every major Move execution.
5. Research documents >10k words are successfully processed via Recursive Summarization.
6. PhonePe webhook successfully triggers the next phase of a Campaign upon payment confirmation.

## 5. Out of Scope
- Native mobile app development.
