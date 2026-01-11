# RAPTORFLOW LANGGRAPH AGENT SWARM ARCHITECTURE

> **Version**: 5.0 | **Framework**: LangGraph + Vertex AI

---

## EXECUTIVE SUMMARY

This document defines the complete backend architecture using **LangGraph** for agent-to-agent swarm orchestration.

### Technology Stack
| Component | Technology |
|-----------|------------|
| **Agent Framework** | LangGraph (LangChain) |
| **LLM Inference** | Vertex AI (Gemini 2.0 Flash) |
| **Database** | Supabase (PostgreSQL + pgvector) |
| **Cache/Queue** | Upstash Redis |
| **Backend** | FastAPI on GCP Cloud Run |
| **Frontend** | Vercel |

---

## CORE ARCHITECTURE: SUPERVISOR + SPECIALIST SWARM

```
                    ┌─────────────────────────┐
                    │    ORCHESTRATOR         │
                    │   (Supervisor Agent)    │
                    │   - Routes requests     │
                    │   - Manages state       │
                    │   - Controls budget     │
                    └──────────┬──────────────┘
                               │
           ┌───────────────────┼───────────────────┐
           │                   │                   │
           ▼                   ▼                   ▼
    ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
    │  ONBOARDING  │   │   PRODUCT    │   │   UTILITY    │
    │    SWARM     │   │    SWARM     │   │    SWARM     │
    │              │   │              │   │              │
    │ - Vault      │   │ - Moves      │   │ - Search     │
    │ - Extractor  │   │ - Campaigns  │   │ - Scraper    │
    │ - Researcher │   │ - Muse       │   │ - OCR        │
    │ - ICP        │   │ - BlackBox   │   │ - Export     │
    │ - Position   │   │ - DailyWins  │   │ - GST        │
    └──────────────┘   └──────────────┘   └──────────────┘
```

---

## LANGGRAPH STATE MACHINE

```python
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END
import operator

class AgentState(TypedDict):
    """Shared state across all agents in the swarm."""
    # Request context
    user_id: str
    workspace_id: str
    request_type: str  # onboarding, moves, campaigns, muse, blackbox, daily_wins
    request_data: dict

    # Foundation context (injected for personalization)
    foundation_summary: str
    icps: list[dict]
    brand_voice: str

    # Execution tracking
    messages: Annotated[list, operator.add]
    current_agent: str
    agent_outputs: dict

    # Cost control
    tokens_used: int
    estimated_cost: float
    budget_remaining: float

    # Flow control
    next_step: str
    requires_human_approval: bool
    final_output: dict | None


def create_raptorflow_graph():
    """Create the main LangGraph workflow."""
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("orchestrator", orchestrator_node)
    workflow.add_node("onboarding_swarm", onboarding_swarm_node)
    workflow.add_node("moves_agent", moves_agent_node)
    workflow.add_node("campaigns_agent", campaigns_agent_node)
    workflow.add_node("muse_agent", muse_agent_node)
    workflow.add_node("blackbox_agent", blackbox_agent_node)
    workflow.add_node("daily_wins_agent", daily_wins_agent_node)
    workflow.add_node("tools", tool_node)
    workflow.add_node("human_approval", human_approval_node)
    workflow.add_node("output_formatter", output_formatter_node)

    workflow.set_entry_point("orchestrator")

    # Routing from orchestrator
    workflow.add_conditional_edges(
        "orchestrator",
        route_request,
        {
            "onboarding": "onboarding_swarm",
            "moves": "moves_agent",
            "campaigns": "campaigns_agent",
            "muse": "muse_agent",
            "blackbox": "blackbox_agent",
            "daily_wins": "daily_wins_agent",
            "end": END
        }
    )

    # Each agent can route to tools, human approval, or output
    for agent in ["onboarding_swarm", "moves_agent", "campaigns_agent",
                  "muse_agent", "blackbox_agent", "daily_wins_agent"]:
        workflow.add_conditional_edges(
            agent,
            should_continue,
            {
                "continue": "orchestrator",
                "tools": "tools",
                "human": "human_approval",
                "output": "output_formatter",
                "end": END
            }
        )

    workflow.add_edge("tools", "orchestrator")
    workflow.add_edge("human_approval", "orchestrator")
    workflow.add_edge("output_formatter", END)

    return workflow.compile()
```

---

## ORCHESTRATOR (SUPERVISOR)

```python
from langchain_google_vertexai import ChatVertexAI
from langchain_core.prompts import ChatPromptTemplate

ORCHESTRATOR_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are the Raptorflow Orchestrator. Route requests to specialist agents.

Available agents:
- onboarding_swarm: Onboarding steps 1-25
- moves_agent: Marketing moves (7-day battle plans)
- campaigns_agent: Campaign planning
- muse_agent: Copywriting/content
- blackbox_agent: Strategic plays (acquisition, retention, virality)
- daily_wins_agent: Quick content based on current events

User Foundation: {foundation_summary}
User ICPs: {icps}
Budget: ${budget_remaining:.4f}
"""),
    ("human", "{request}")
])

async def orchestrator_node(state: AgentState) -> AgentState:
    """Route requests using cheap model (Gemini Flash Lite)."""
    llm = ChatVertexAI(
        model_name="gemini-2.0-flash-lite",
        project="your-gcp-project",
        temperature=0.1,
        max_tokens=500
    )

    chain = ORCHESTRATOR_PROMPT | llm
    decision = await chain.ainvoke({
        "foundation_summary": state["foundation_summary"],
        "icps": state["icps"],
        "budget_remaining": state["budget_remaining"],
        "request": state["request_data"]
    })

    # Parse decision and update state
    state["current_agent"] = decision["target_agent"]
    state["tokens_used"] += 500

    return state
```

---

## AGENT INVENTORY

| Agent | Purpose | Model | Max Tokens |
|-------|---------|-------|------------|
| **Orchestrator** | Route requests | Flash-Lite | 500 |
| **VaultProcessor** | Process uploads | Flash | 2000 |
| **TruthExtractor** | Extract facts | Flash | 4000 |
| **MarketResearcher** | Web research | Flash | 8000 |
| **ICPArchitect** | Generate ICPs | Flash | 4000 |
| **PositioningMapper** | Perceptual maps | Flash | 6000 |
| **MoveGenerator** | Create moves | Flash | 8000 |
| **CampaignPlanner** | Plan campaigns | Flash | 8000 |
| **MuseEngine** | Write copy | Flash | 4000 |
| **BlackBoxEngine** | Strategic plays | Flash | 6000 |
| **DailyWinsEngine** | Quick wins | Flash | 3000 |
