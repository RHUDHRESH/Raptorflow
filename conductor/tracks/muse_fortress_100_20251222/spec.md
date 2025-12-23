# Track Spec: SOTA Muse Backend Overhaul (100-Phase "Fortress" Project)

## 1. Overview
Transform the Muse backend from a skeletal "shell" into a state-of-the-art (SOTA), production-grade autonomous agent system. This project implements a hierarchical multi-agent architecture (LangGraph Supervisor) with deep contextual memory, recursive quality loops, and an industrial-grade toolbelt.

## 2. Functional Requirements

### 2.1 Autonomous Orchestration (The Supervisor)
- **Hierarchical Supervisor Node:** A central brain that decomposes complex marketing requests into sub-tasks and delegates them to specialized crews.
- **Dynamic Task Routing:** The ability to add/remove tasks from the execution queue based on intermediate agent results.

### 2.2 Specialist Agent Crews
- **Research Crew:** Dedicated nodes for deep web search (Tavily/Perplexity), competitive intelligence, and trend extraction.
- **Strategy Crew:** Nodes for ICP profiling, brand positioning alignment, and strategic war-planning (Moves/Campaigns).
- **Creative Crew:** Nodes for surgical copywriting, social post architecture, and visual asset prompt engineering.
- **Operator Crew:** Deployment nodes for syncing data to Slack, Notion, and other CRM/Marketing APIs.

### 2.3 Quality Control & Reflection (The "Fortress")
- **Recursive Multi-Agent Critique:** A "Producer-Critique" loop where creatives generate work and specialists (like a Brand Guardian) recursively refine it.
- **Brand Guardian Node:** A dedicated agent that enforces the RaptorFlow Brand Kit (tone, voice, non-negotiables) on every output.
- **Automated Scoring:** Statistical checks for formatting, word count, and "hype-word" detection (removing "game-changer", "revolutionary").
- **HITL Checkpoints:** Mandatory user interrupts for high-stakes decisions (Budget, Final Copy, Strategic Pivots).

### 2.4 Deep Contextual Memory
- **Entity Memory:** Tracking specific brands, founders, and competitors across multiple threads.
- **Contextual Awareness:** Memory that informs agent "backstories" dynamically based on historical project success/failure.

### 2.5 Industrial Toolbelt
- **Code Interpreter Sandbox:** A secure environment for agents to perform data analysis or generate charts.
- **Advanced Search:** Multi-hop search queries to synthesize information from across the web.
- **CRM/API Connectors:** Standardized interfaces for Notion, Slack, and Supabase.

## 3. Tech Stack
- **Framework:** LangGraph (Supervisor Model)
- **Persistence:** Supabase (pgvector for Memory, Checkpointers for State)
- **Caching:** Upstash Redis
- **Search:** Tavily API / Perplexity
- **Observability:** LangSmith (with custom Evaluators)
- **Tools:** Python REPL (Sandboxed), Notion/Slack SDKs

## 4. Acceptance Criteria
1. The backend handles a "New Campaign" request from 0 to 100% autonomously, pausing only for HITL approval.
2. Every asset produced passes a "Brand Guardian" QA check with <5% rejection rate in final manual review.
3. Memory recall for "past campaigns" is utilized in 100% of new strategy sessions.
4. Latency for complex multi-agent flows is optimized via parallel node execution.
5. LangSmith traces show a clear "Inner Monologue" for every decision made by the Supervisor.

## 5. Out of Scope
- Consumer-facing landing page redesign (handled by Frontend tracks).
- Mobile application development.
