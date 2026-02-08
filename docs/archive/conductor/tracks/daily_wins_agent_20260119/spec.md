# Specification: LangGraph Daily Wins Agent ("The Surprise Engine")

## Overview
This track implements a SOTA LangGraph-powered agent for the **Daily Wins** module. The goal is to replace static content ideas with high-quality, "surprisingly good" daily posts that leverage internal business context (BCM) and real-world market intelligence (SearXNG/Reddit). The agent acts as a daily strategic partner for the founder, delivering surgical insights with "MasterClass polish."

## 1. Functional Requirements

### 1.1 The 7 Core Agent Skills (LangGraph Nodes)
The agent will be orchestrated as a multi-node LangGraph workflow with the following specialized skills:
1.  **Context Miner (BCM Integration):** Extracts high-level "wins," completed moves, and active campaign data from the RaptorFlow backend.
2.  **Trend Mapper (Search Integration):** Uses SearXNG and Reddit to identify current cultural zeitgeist and industry shifts relevant to the founder's ICP.
3.  **Synthesizer:** Bridges the gap between internal activity (Proof of Work) and external trends to create a unique narrative arc.
4.  **Voice Architect:** Enforces the "Editorial Restraint" and "Quiet Luxury" tone, ensuring posts sound like a master practitioner, not an AI.
5.  **Hook Specialist:** Crafts 3-5 scroll-stopping headlines tailored for LinkedIn and X (Twitter).
6.  **Visualist:** Generates sophisticated editorial art direction prompts or layout mockups to accompany the text.
7.  **Skeptic/Editor (Reflection):** A final self-critique layer that rejects "AI-generic" outputs and ensures every post meets the "Surprise" threshold.

### 1.2 Surprise Content Angles
The engine will focus on three primary content types:
-   **Contrarian Takes:** Challenging industry "vibes" with data-backed, surgical logic.
-   **Proof of Work:** Showcasing sanitized business momentum (e.g., "We just analyzed 5,000 Reddit comments to find this one ICP gap").
-   **Market Intelligence:** Obscure but relevant market data that provides an unfair advantage to solo founders.

### 1.3 Trigger & UI Integration
-   **Surface:** The existing `DailyWinsPage` (`/daily-wins`).
-   **Mechanism:** The "Get Today's Win" button triggers the full LangGraph orchestration.
-   **Feel:** A clean, minimal "Intelligence Brief" reveal that emphasizes decision-ready clarity over "lottery" noise.

## 2. Technical Requirements
-   **Backend:** Python/FastAPI endpoint `/api/v1/daily_wins/generate-langgraph`.
-   **Orchestration:** LangGraph for stateful, multi-agent logic.
-   **Search:** Integration with the existing self-hosted SearXNG cluster.
-   **Context:** Direct read access to Supabase tables (`foundations`, `moves`, `campaigns`, `icp_profiles`).

## 3. Acceptance Criteria
- [ ] LangGraph agent successfully synthesizes 1 internal "win" with 1 external "trend."
- [ ] Posts are generated in under 15 seconds.
- [ ] Output includes: Hook, Body (Editorial structure), Visual Prompt, and Platform Recommendation.
- [ ] The "Skeptic" node can successfully reject and retry a post if it lacks "surprise."

## 4. Out of Scope
-   Automatic publishing to social media (Human-in-the-loop only).
-   Generation of actual image files (Prompts/mockups only).
