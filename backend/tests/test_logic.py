from typing import List, TypedDict
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from backend.agents.supervisor import (
    HierarchicalSupervisor,
    RouterOutput,
    create_team_supervisor,
)


class TestState(TypedDict):
    next_steps: List[str]
    signals: List[str]
    results: List[str]
    messages: List[any]


async def planning_node(state: TestState):
    """
    SOTA Planning node that can dynamically re-plan based on signals.
    """
    signals = state.get("signals", [])
    results = state.get("results", [])

    # If we have a 'need_research' signal and haven't done 'step_a' yet
    if "need_research" in signals and "A" not in results:
        return {"next_steps": ["step_a"]}

    # If 'step_a' is done but 'step_b' isn't
    if "A" in results and "B" not in results:
        return {"next_steps": ["step_b"]}

    return {"next_steps": ["final_step"]}


def router(state: TestState):
    next_step = state.get("next_steps", [])
    if not next_step or next_step[0] == "final_step":
        return END
    return next_step[0]


from backend.agents.classifier import (
    Intent,
    create_ambiguity_resolver,
    create_intent_classifier,
)
from backend.agents.planner import Plan, create_task_decomposer
from backend.models.fortress import FortressTask


@pytest.mark.asyncio
async def test_workspace_thread_isolation():
    """Verify that different thread IDs do not leak state."""
    checkpointer = MemorySaver()
    workflow = StateGraph(TestState)
    workflow.add_node("step", lambda x: {"results": x.get("results", []) + ["Done"]})
    workflow.add_edge(START, "step")
    workflow.add_edge("step", END)
    app = workflow.compile(checkpointer=checkpointer)

    config_1 = {"configurable": {"thread_id": "thread_1"}}
    config_2 = {"configurable": {"thread_id": "thread_2"}}

    await app.ainvoke({"results": []}, config=config_1)
    state_2 = await app.aget_state(config_2)

    # State 2 should be empty because it's a different thread
    assert state_2.values == {}


@pytest.mark.asyncio
async def test_ambiguity_resolution_logic():
    """Verify that the resolver generates questions for vague input."""
    mock_llm = AsyncMock()
    mock_llm.ainvoke.return_value = MagicMock(
        content="Question 1? Question 2? Question 3?"
    )

    resolver = create_ambiguity_resolver(mock_llm)
    state = {"raw_prompt": "do marketing"}
    result = await resolver(state)

    assert "Question 1?" in result["final_output"]
    assert result["status"] == "awaiting_clarification"


@pytest.mark.asyncio
async def test_intent_classification_logic():
    """Verify that the classifier correctly identifies intent."""
    mock_llm = MagicMock()
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = Intent(
        classification="campaign", confidence=0.99, reasoning="SOTA check"
    )

    with patch(
        "backend.agents.classifier.IntentClassifier.__init__", return_value=None
    ):
        classifier = create_intent_classifier(mock_llm)
        classifier.chain = mock_chain

        state = {"raw_prompt": "Plan a 3-month launch"}
        result = await classifier(state)

        assert result["next_node"] == "campaign"
        assert result["context_brief"]["intent"]["confidence"] == 0.99


@pytest.mark.asyncio
async def test_task_decomposition_logic():
    """Verify that the decomposer creates a structured plan."""
    mock_llm = MagicMock()
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = Plan(
        tasks=[
            FortressTask(crew="research", description="Analyze niche"),
            FortressTask(crew="strategy", description="Define UVP"),
        ]
    )

    with patch("backend.agents.planner.TaskDecomposer.__init__", return_value=None):
        decomposer = create_task_decomposer(mock_llm)
        decomposer.chain = mock_chain

        state = {"raw_prompt": "Launch a new SaaS"}
        result = await decomposer(state)

        assert len(result["task_queue"]) == 2
        assert result["task_queue"][0].crew == "research"


@pytest.mark.asyncio
async def test_hierarchical_supervisor_delegation():
    """Verify that the supervisor delegates correctly using a direct chain mock."""
    mock_llm = MagicMock()
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = RouterOutput(
        next_node="research", instructions="Find competitors"
    )

    # We mock the initialization of HierarchicalSupervisor to inject our mock_chain
    with patch(
        "backend.agents.supervisor.HierarchicalSupervisor.__init__", return_value=None
    ) as mock_init:
        supervisor = HierarchicalSupervisor(mock_llm, ["research"], "System prompt")
        supervisor.chain = mock_chain

        state = {"messages": [MagicMock(content="Build me a brand")]}
        result = await supervisor(state)

        assert result["next"] == "research"
        assert result["instructions"] == "Find competitors"


@pytest.mark.asyncio
async def test_hitl_interrupt_logic():
    """Test that the graph interrupts before a specific node."""
    workflow = StateGraph(TestState)
    workflow.add_node("step_a", lambda x: {"results": ["A"]})
    workflow.add_node(
        "approval_node", lambda x: {"results": x.get("results", []) + ["Approved"]}
    )

    workflow.add_edge(START, "step_a")
    workflow.add_edge("step_a", "approval_node")
    workflow.add_edge("approval_node", END)

    # Use MemorySaver for checkpointing in the test
    checkpointer = MemorySaver()
    app = workflow.compile(
        checkpointer=checkpointer, interrupt_before=["approval_node"]
    )

    config = {"configurable": {"thread_id": "test-thread"}}

    # Initial run - should stop before approval_node
    await app.ainvoke({"signals": [], "next_steps": [], "results": []}, config=config)

    snapshot = await app.aget_state(config)
    assert snapshot.next == ("approval_node",)
    assert "A" in snapshot.values["results"]
    assert "Approved" not in snapshot.values["results"]

    # Resume
    await app.ainvoke(None, config=config)

    final_snapshot = await app.aget_state(config)
    assert "Approved" in final_snapshot.values["results"]


@pytest.mark.asyncio
async def test_dynamic_replanning_signal():
    """Test that the graph can pivot based on a 'pivot' signal."""
    workflow = StateGraph(TestState)
    workflow.add_node("planner", planning_node)
    workflow.add_node("step_a", lambda x: {"results": x.get("results", []) + ["A"]})
    workflow.add_node("step_b", lambda x: {"results": x.get("results", []) + ["B"]})

    workflow.add_edge(START, "planner")
    workflow.add_conditional_edges(
        "planner", router, {"step_a": "step_a", "step_b": "step_b", END: END}
    )
    workflow.add_edge("step_a", "planner")
    workflow.add_edge("step_b", "planner")

    app = workflow.compile()

    # Case 1: Initial signal 'need_research'
    state = await app.ainvoke(
        {"signals": ["need_research"], "next_steps": [], "results": []}
    )

    assert "A" in state["results"]
    assert "B" in state["results"]
    assert state["next_steps"] == ["final_step"]
