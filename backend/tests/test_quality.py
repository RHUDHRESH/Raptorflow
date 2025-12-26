from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.quality import (
    BrandAlignment,
    ComplianceResult,
    ContentStats,
    EditorialCritique,
    HypeLintResult,
    MemoryDecision,
    RedTeamAnalysis,
    StrategicRisk,
    create_brand_guardian,
    create_editor_node,
    create_feedback_integrator,
    create_hype_filter,
    create_legal_guard,
    create_memory_governor,
    create_quality_gate,
    create_red_team_agent,
    create_refiner_node,
    create_stats_scorer,
)


@pytest.mark.asyncio
async def test_memory_governor_logic():
    """Verify that the governor identifies insights correctly."""
    mock_llm = MagicMock()
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = MemoryDecision(
        should_remember=True,
        importance_score=0.9,
        extracted_fact="New tone rule",
        category="tone",
    )

    with patch("backend.agents.quality.MemoryGovernor.__init__", return_value=None):
        governor = create_memory_governor(mock_llm)
        governor.chain = mock_chain

        state = {"current_draft": "SOTA insights"}
        result = await governor(state)

        assert "Vaulted new insight" in result["messages"][0]


@pytest.mark.asyncio
async def test_ui_feedback_logic():
    """Verify that the integrator converts feedback to instructions."""
    mock_llm = MagicMock()
    mock_llm.ainvoke = AsyncMock(return_value=MagicMock(content="Technical fix"))

    integrator = create_feedback_integrator(mock_llm)
    state = {"user_feedback": "make it bolder", "current_draft": "soft"}
    result = await integrator(state)

    assert "Technical fix" in result["messages"][0]
    assert result["next_node"] == "refine"


@pytest.mark.asyncio
async def test_quality_gate_logic():
    """Verify that the gate routes to finalize or refine based on score."""
    gate = create_quality_gate()

    # Case 1: High Score -> Finalize
    state_pass = {"quality_score": 0.9, "brand_pass": True, "legal_pass": True}
    res_pass = await gate(state_pass)
    assert res_pass["next_node"] == "finalize"

    # Case 2: Low Score -> Refine
    state_fail = {"quality_score": 0.5, "brand_pass": True, "legal_pass": True}
    res_fail = await gate(state_fail)
    assert res_fail["next_node"] == "refine"


@pytest.mark.asyncio
async def test_legal_guard_logic():
    """Verify that the legal guard catches prohibited claims."""
    mock_llm = MagicMock()
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = ComplianceResult(
        is_compliant=False, issues=["Unsubstantiated claim"], risk_level="High"
    )

    with patch(
        "backend.agents.quality.LegalComplianceGuard.__init__", return_value=None
    ):
        guard = create_legal_guard(mock_llm)
        guard.chain = mock_chain

        state = {"current_draft": "We are 100% better than anyone."}
        result = await guard(state)

        assert result["legal_pass"] is False
        assert "Unsubstantiated claim" in result["messages"][0]


@pytest.mark.asyncio
async def test_red_team_logic():
    """Verify that the red team identifies strategic risks."""
    mock_llm = MagicMock()
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = RedTeamAnalysis(
        risks=[
            StrategicRisk(risk="Cannibalization", severity=0.7, impact="Revenue loss")
        ]
    )

    with patch("backend.agents.quality.RedTeamAgent.__init__", return_value=None):
        agent = create_red_team_agent(mock_llm)
        agent.chain = mock_chain

        state = {"context_brief": {"campaign_arc": {}}}
        result = await agent(state)

        assert result["telemetry"][0]["risks"][0]["risk"] == "Cannibalization"


@pytest.mark.asyncio
async def test_refiner_node_logic():
    """Verify that the refiner applies editorial changes."""
    mock_llm = MagicMock()
    mock_llm.ainvoke = AsyncMock(return_value=MagicMock(content="Refined SOTA draft."))

    refiner = create_refiner_node(mock_llm)
    state = {"current_draft": "Original draft.", "messages": ["Editor: Shorten hook"]}
    result = await refiner(state)

    assert result["current_draft"] == "Refined SOTA draft."
    assert result["iteration_count"] == 1


@pytest.mark.asyncio
async def test_editor_critique_logic():
    """Verify that the editor provides structured feedback."""
    mock_llm = MagicMock()
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = EditorialCritique(
        critique="Too wordy.",
        improvement_items=["Shorten hook"],
        ready_for_refiner=True,
    )

    with patch("backend.agents.quality.EditorNode.__init__", return_value=None):
        editor = create_editor_node(mock_llm)
        editor.chain = mock_chain

        state = {"current_draft": "Wordy draft."}
        result = await editor(state)

        assert "Shorten hook" in result["messages"][0]
        assert result["quality_score"] == 0.0  # Heuristic for skeletal state


@pytest.mark.asyncio
async def test_stats_scorer_logic():
    """Verify that the stats scorer calculates linguistic metrics."""
    mock_llm = MagicMock()
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = ContentStats(
        reading_level="10th Grade", word_count=50, flow_score=0.8
    )

    with patch("backend.agents.quality.StatsScorer.__init__", return_value=None):
        scorer = create_stats_scorer(mock_llm)
        scorer.chain = mock_chain

        state = {"current_draft": "Some draft content here."}
        result = await scorer(state)

        assert result["telemetry"][0]["word_count"] == 50
        assert result["telemetry"][0]["reading_level"] == "10th Grade"


@pytest.mark.asyncio
async def test_hype_filter_logic():
    """Verify that the hype filter catches banned marketing speak."""
    mock_llm = MagicMock()
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = HypeLintResult(
        clean_content="Our software is good.",
        banned_words_found=["revolutionary"],
        hype_score=0.5,
    )

    with patch("backend.agents.quality.HypeWordFilter.__init__", return_value=None):
        filter_node = create_hype_filter(mock_llm)
        filter_node.chain = mock_chain

        state = {"current_draft": "Our software is revolutionary."}
        result = await filter_node(state)

        assert "revolutionary" in result["telemetry"][0]["banned_words"]
        assert result["current_draft"] == "Our software is good."


@pytest.mark.asyncio
async def test_brand_guardian_tone_logic():
    """Verify that the brand guardian correctly evaluates tone."""
    # This will fail initially because quality.py does not exist
    mock_llm = MagicMock()
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = BrandAlignment(
        is_aligned=True, score=0.9, tone_feedback="Perfectly surgical.", violations=[]
    )

    with patch("backend.agents.quality.BrandGuardian.__init__", return_value=None):
        guardian = create_brand_guardian(mock_llm)
        guardian.chain = mock_chain

        state = {"current_draft": "We deliver SOTA results faster."}
        result = await guardian(state)

        assert result["quality_score"] == 0.9
        assert result["brand_pass"] is True
