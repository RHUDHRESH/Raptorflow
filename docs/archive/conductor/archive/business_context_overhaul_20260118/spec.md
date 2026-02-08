# Specification: Business Context Generator Overhaul

## 1. Overview
This track involves a complete re-architecture of the `BusinessContextGenerator` service (`backend/services/business_context_generator.py`). The goal is to transform the current fragile, monolithic class into a robust, stateful **LangGraph** application. This new engine will produce deep, structured business insights, enhanced ICPs, and messaging strategies using `gemini-1.5-pro` (via Vertex AI) with strict Pydantic validation.

## 2. Functional Requirements

### 2.1 Core Architecture (LangGraph)
*   **State Management:** Implement a `BusinessContextState` (TypedDict/Pydantic) to hold the accumulating context.
*   **Graph Workflow:**
    *   **Input:** Raw Foundation Data.
    *   **Nodes:**
        1.  `generate_profile`: Core identity & positioning.
        2.  `analyze_market`: Market size & trends.
        3.  `analyze_competitors`: Competitor Deep Dive (Feature matrices).
        4.  `generate_swot`: SWOT Analysis.
        5.  `generate_pestel`: PESTEL Analysis.
        6.  `analyze_value_chain`: Value Chain Analysis.
        7.  `generate_personas`: Detailed Marketing Personas & Brand Archetypes.
        8.  `enhance_icp`: **Enhance ICP data with deep insights (Psychographics, Buying Triggers).** (Replaces `enhance_icp_context`)
        9.  `generate_messaging`: **Generate comprehensive messaging strategy (Brand Voice, Core Messages, Handling Objections).** (Replaces `generate_messaging_strategy`)
        10. `synthesize_strategy`: Final synthesis.
    *   **Edges:** Sequential execution or parallel branches for independent analysis modules.

### 2.2 New Capabilities
The generator must produce the following structured outputs (replacing/augmenting current fallbacks) with strict schemas:
*   **Business Context:** SWOT, PESTEL, Value Chain, Brand Archetypes, Competitor Matrix.
*   **ICP Enhancement:** Psychographics, Behavioral Patterns, Pain Point Severity (1-10), Buying Triggers, Messaging Angles.
*   **Messaging Strategy:** Brand Voice, Core Message Pillars, Channel-specific messaging, Objection Handling.

### 2.3 Quality & Robustness
*   **Structured Output:** ALL LLM outputs must be validated against strict Pydantic models.
*   **Prompt Engineering:** Use advanced prompting techniques (Chain-of-Thought, System Instructions).
*   **Error Handling:** Graph-level error handling with retries on validation failure.
*   **Removal of "Fallbacks":** The aggressive use of generic fallbacks in the success path must be removed. The system should either succeed with valid data or raise a clear, handled error.

## 3. Non-Functional Requirements
*   **Tech Stack:** LangGraph, Vertex AI (Gemini 1.5 Pro), Pydantic.
*   **Testing:** Unit tests for each node, integration tests for the graph, and mocked Vertex AI calls.
*   **Code Quality:** >80% Test Coverage, fully typed.

## 4. Acceptance Criteria
*   [ ] `BusinessContextGenerator` is refactored to use `LangGraph`.
*   [ ] Pydantic models exist for ALL analysis types (Context, ICP, Messaging).
*   [ ] `enhance_icp_context` and `generate_messaging_strategy` are integrated into the graph or capable of using the graph's tools.
*   [ ] Test suite passes with >80% coverage.
*   [ ] No "hardcoded fallback" strings in the success path.
