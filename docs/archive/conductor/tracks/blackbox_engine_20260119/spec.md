# Specification: Blackbox Strategy Engine Resurrection

## Overview
The "Blackbox" is the "Cognitive Spine" of RaptorFlow, designed to generate experimental, high-risk/high-reward marketing moves. This track aims to transition the Blackbox from a mock frontend experience to a fully functional, AI-driven engine integrated with the backend orchestration layer.

## Functional Requirements
1.  **Backend Integration:**
    *   Connect the frontend `handleGenerate` function to the backend `POST /api/v1/blackbox/generate` endpoint.
    *   Ensure the backend `BlackboxWorkflow` correctly utilizes the `BlackboxStrategist` agent.
2.  **Configurable Ambition:**
    *   Map the 4 "Ambitions" (Market Domination, Brand Immortality, Viral Spiral, Fortress Position) to specific prompts or strategies in the `BlackboxStrategist`.
    *   Implement the "Volatility" slider (1-10) as a parameter that influences the "riskiness" and "unconventionality" of the AI's output.
3.  **Context-Aware Generation:**
    *   The engine must pull current workspace context (Brand Foundation, RICP segments, and previous Moves) to ensure strategies are bold but relevant.
4.  **Actionable Moves:**
    *   Successfully convert a generated Blackbox strategy into a "Move" in the `moves` table, preserving the risk level and strategic intent.
5.  **UI/UX Improvements:**
    *   Replace mock data in the "Output" screen with real-time results from the AI.
    *   Add error handling for failed generation or database timeouts.

## Non-Functional Requirements
*   **Performance:** Strategy generation should complete within 30 seconds.
*   **Security:** Ensure RLS policies for `blackbox_strategies` and `moves` are strictly enforced.
*   **Reliability:** Implement a retry mechanism for AI generation if the LLM provider times out.

## Acceptance Criteria
*   User can select an ambition and volatility level.
*   Backend generates a unique, non-generic strategy based on the inputs.
*   Strategy is saved to the database.
*   User can click "Accept & Create Move" and see the new move in their dashboard.

## Out of Scope
*   Automated execution of moves (only generation and planning).
*   Integration with external marketing tools for direct deployment.
