import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from backend.agents.strategists import (
    create_icp_demographer, ICPDemographics, 
    create_icp_psychographer, ICPPsychographics, 
    create_pain_point_mapper, PainPointAnalysis, PainPoint, 
    create_uvp_architect, UVPAnalysis, UVP,
    create_brand_voice_aligner, BrandVoiceAnalysis, AlignmentResult,
    create_anti_persona_profiler, AntiPersonaAnalysis, AntiPersona,
    create_category_architect, CategoryAnalysis, CategoryProposal,
    create_tagline_generator, TaglineAnalysis, Tagline,
    create_strategy_replanner,
    create_campaign_designer, CampaignArc, MonthPlan,
    create_move_sequencer, MoveSequence, ExecutionMove,
    create_budget_allocator, BudgetAnalysis, ChannelBudget,
    create_channel_selector, ChannelSelection, SelectedChannel,
    create_kpi_definer, KPIAnalysis, Metric,
    create_funnel_designer, FunnelAnalysis, FunnelStage,
    create_conflict_resolver, ConflictAnalysis, StrategicConflict,
    create_strategy_refresh_hook,
    create_founder_profiler, FounderProfile
)

@pytest.mark.asyncio
async def test_founder_profiler_logic():
    """Verify that the founder profiler extracts and syncs data."""
    mock_llm = MagicMock()
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = FounderProfile(
        personality_traits=["Bold"], strategic_goals=["Scale"], preferred_communication_style="Direct"
    )
    
    with patch("backend.agents.strategists.FounderArchetypeProfiler.__init__", return_value=None), \
         patch("backend.agents.strategists.save_entity", new_callable=AsyncMock) as mock_save:
        
        profiler = create_founder_profiler(mock_llm)
        profiler.chain = mock_chain
        
        state = {"workspace_id": "ws_1", "research_bundle": {}}
        result = await profiler(state)
        
        assert result["context_brief"]["founder_profile"]["personality_traits"] == ["Bold"]
        mock_save.assert_called_once()

@pytest.mark.asyncio
async def test_strategy_refresh_hook_logic():
    """Verify that the hook requests refresh on thin data."""
    mock_llm = AsyncMock()
    mock_llm.ainvoke.return_value = MagicMock(content="Find more SaaS data")
    
    hook = create_strategy_refresh_hook(mock_llm)
    state = {"research_bundle": {"final_evidence": {"key_findings": ["Only one"]}}}
    result = await hook(state)
    
    assert result["next_node"] == "research_refresh"
    assert "Find more SaaS" in result["context_brief"]["refresh_instruction"]

@pytest.mark.asyncio
async def test_conflict_resolution_logic():
    """Verify that the resolver identifies contradictions."""
    mock_llm = MagicMock()
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = ConflictAnalysis(
        conflicts=[StrategicConflict(description="Theme mismatch", severity=0.5, resolution_suggestion="Fix theme")],
        is_safe_to_proceed=False
    )
    
    with patch("backend.agents.strategists.StrategicConflictResolver.__init__", return_value=None):
        resolver = create_conflict_resolver(mock_llm)
        resolver.chain = mock_chain
        
        state = {"context_brief": {"campaign_arc": {}}, "research_bundle": {"historical_context": []}}
        result = await resolver(state)
        
        assert result["context_brief"]["conflicts"]["is_safe_to_proceed"] is False

@pytest.mark.asyncio
async def test_funnel_design_logic():
    """Verify that the designer architects a funnel correctly."""
    mock_llm = MagicMock()
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = FunnelAnalysis(stages=[
        FunnelStage(stage_name="TOFU", content_type="Blog", conversion_goal="Awareness")
    ])
    
    with patch("backend.agents.strategists.FunnelDesigner.__init__", return_value=None):
        designer = create_funnel_designer(mock_llm)
        designer.chain = mock_chain
        
        state = {"context_brief": {"campaign_arc": {}, "channels": {}}}
        result = await designer(state)
        
        assert result["context_brief"]["funnel"]["stages"][0]["stage_name"] == "TOFU"

@pytest.mark.asyncio
async def test_kpi_definition_logic():
    """Verify that the definer creates surgical KPIs."""
    mock_llm = MagicMock()
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = KPIAnalysis(kpis=[
        Metric(name="Conversion", target_value="5%", measurement_method="GA4")
    ])
    
    with patch("backend.agents.strategists.KPIDefiner.__init__", return_value=None):
        definer = create_kpi_definer(mock_llm)
        definer.chain = mock_chain
        
        state = {"context_brief": {"channels": {}, "campaign_arc": {}}}
        result = await definer(state)
        
        assert result["context_brief"]["kpis"]["kpis"][0]["name"] == "Conversion"

@pytest.mark.asyncio
async def test_channel_selection_logic():
    """Verify that the selector chooses primary channels correctly."""
    mock_llm = MagicMock()
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = ChannelSelection(selected_channels=[
        SelectedChannel(channel_name="LinkedIn", priority="primary", relevance_score=0.9)
    ])
    
    with patch("backend.agents.strategists.ChannelSelector.__init__", return_value=None):
        selector = create_channel_selector(mock_llm)
        selector.chain = mock_chain
        
        state = {"context_brief": {"icp_demographics": {}}, "research_bundle": {}}
        result = await selector(state)
        
        assert result["context_brief"]["channels"]["selected_channels"][0]["channel_name"] == "LinkedIn"

@pytest.mark.asyncio
async def test_budget_allocation_logic():
    """Verify that the allocator suggests spend correctly."""
    mock_llm = MagicMock()
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = BudgetAnalysis(
        suggested_total="$5000",
        distribution=[ChannelBudget(channel="LinkedIn", allocation_percentage=0.6, reasoning="SOTA B2B")]
    )
    
    with patch("backend.agents.strategists.BudgetAllocator.__init__", return_value=None):
        allocator = create_budget_allocator(mock_llm)
        allocator.chain = mock_chain
        
        state = {"research_bundle": {}, "context_brief": {}}
        result = await allocator(state)
        
        assert result["context_brief"]["budget_plan"]["suggested_total"] == "$5000"
        assert result["context_brief"]["budget_plan"]["distribution"][0]["channel"] == "LinkedIn"

@pytest.mark.asyncio
async def test_move_sequencing_logic():
    """Verify that the sequencer breaks an arc into weekly moves."""
    mock_llm = MagicMock()
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = MoveSequence(moves=[
        ExecutionMove(week_number=1, title="Warmup", action_items=["Post 1"], desired_outcome="Awareness")
    ])
    
    with patch("backend.agents.strategists.MoveSequencer.__init__", return_value=None):
        sequencer = create_move_sequencer(mock_llm)
        sequencer.chain = mock_chain
        
        state = {"context_brief": {"campaign_arc": {}}}
        result = await sequencer(state)
        
        assert len(result["context_brief"]["move_sequence"]["moves"]) == 1
        assert result["context_brief"]["move_sequence"]["moves"][0]["title"] == "Warmup"

@pytest.mark.asyncio
async def test_campaign_arc_logic():
    """Verify that the designer architects a 3-month plan correctly."""
    mock_llm = MagicMock()
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = CampaignArc(
        campaign_title="SOTA Launch",
        monthly_plans=[
            MonthPlan(month_number=1, theme="Awareness", key_objective="Reach 10k")
        ]
    )
    
    with patch("backend.agents.strategists.CampaignArcDesigner.__init__", return_value=None):
        designer = create_campaign_designer(mock_llm)
        designer.chain = mock_chain
        
        state = {"context_brief": {"uvps": {}}, "research_bundle": {}}
        result = await designer(state)
        
        assert result["context_brief"]["campaign_arc"]["campaign_title"] == "SOTA Launch"
        assert len(result["context_brief"]["campaign_arc"]["monthly_plans"]) == 1

@pytest.mark.asyncio
async def test_strategy_replanner_logic():
    """Verify that the replanner triggers pivot on low scores."""
    mock_llm = AsyncMock()
    mock_llm.ainvoke.return_value = MagicMock(content="Pivot: Focus on speed")
    
    replanner = create_strategy_replanner(mock_llm)
    state = {
        "context_brief": {
            "brand_alignment": {"alignments": [{"score": 0.5}]} # Low score
        }
    }
    result = await replanner(state)
    
    assert result["next_node"] == "pivot"
    assert "Focus on speed" in result["context_brief"]["pivot_instruction"]

@pytest.mark.asyncio
async def test_tagline_generator_logic():
    """Verify that the generator creates taglines correctly."""
    mock_llm = MagicMock()
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = TaglineAnalysis(taglines=[
        Tagline(text="Marketing. Finally under control.", vibe="Expensive")
    ])
    
    with patch("backend.agents.strategists.TaglineGenerator.__init__", return_value=None):
        generator = create_tagline_generator(mock_llm)
        generator.chain = mock_chain
        
        state = {"context_brief": {"uvps": {}}}
        result = await generator(state)
        
        assert "Finally under control" in result["context_brief"]["taglines"]["taglines"][0]["text"]

@pytest.mark.asyncio
async def test_category_architect_logic():
    """Verify that the architect proposes categories correctly."""
    mock_llm = MagicMock()
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = CategoryAnalysis(proposals=[
        CategoryProposal(category_name="MOS", rationale="SOTA OS", market_potential=0.9)
    ])
    
    with patch("backend.agents.strategists.CategoryArchitect.__init__", return_value=None):
        architect = create_category_architect(mock_llm)
        architect.chain = mock_chain
        
        state = {"context_brief": {"uvps": {}}}
        result = await architect(state)
        
        assert result["context_brief"]["categories"]["proposals"][0]["category_name"] == "MOS"

@pytest.mark.asyncio
async def test_anti_persona_logic():
    """Verify that the anti-persona node defines segments to avoid."""
    mock_llm = MagicMock()
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = AntiPersonaAnalysis(anti_personas=[
        AntiPersona(persona_name="Hobbyist", why_to_avoid="Low budget", common_signals=["No LLC"])
    ])
    
    with patch("backend.agents.strategists.AntiPersonaProfiler.__init__", return_value=None):
        profiler = create_anti_persona_profiler(mock_llm)
        profiler.chain = mock_chain
        
        state = {"research_bundle": {}, "context_brief": {}}
        result = await profiler(state)
        
        assert result["context_brief"]["anti_personas"]["anti_personas"][0]["persona_name"] == "Hobbyist"

@pytest.mark.asyncio
async def test_brand_voice_alignment_logic():
    """Verify that the aligner scores UVP consistency correctly."""
    mock_llm = MagicMock()
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = BrandVoiceAnalysis(alignments=[
        AlignmentResult(uvp_title="SOTA", is_aligned=True, score=0.95, feedback="Perfect")
    ])
    
    with patch("backend.agents.strategists.BrandVoiceAligner.__init__", return_value=None):
        aligner = create_brand_voice_aligner(mock_llm)
        aligner.chain = mock_chain
        
        state = {"context_brief": {"uvps": {}}}
        result = await aligner(state)
        
        assert result["context_brief"]["brand_alignment"]["alignments"][0]["score"] == 0.95

@pytest.mark.asyncio
async def test_uvp_architect_logic():
    """Verify that the architect drafts UVPs correctly."""
    mock_llm = MagicMock()
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = UVPAnalysis(winning_positions=[
        UVP(title="Fast Move", description="Speed is key", why_it_wins="SOTA Speed")
    ])
    
    with patch("backend.agents.strategists.UVPArchitect.__init__", return_value=None):
        architect = create_uvp_architect(mock_llm)
        architect.chain = mock_chain
        
        state = {"context_brief": {"pain_points": {}}, "research_bundle": {}}
        result = await architect(state)
        
        assert result["context_brief"]["uvps"]["winning_positions"][0]["title"] == "Fast Move"

@pytest.mark.asyncio
async def test_pain_point_mapper_logic():
    """Verify that the mapper extracts burning problems correctly."""
    mock_llm = MagicMock()
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = PainPointAnalysis(burning_problems=[
        PainPoint(problem="Scaling", severity=0.9, quote_or_signal="Hard to scale")
    ])
    
    with patch("backend.agents.strategists.PainPointMapper.__init__", return_value=None):
        mapper = create_pain_point_mapper(mock_llm)
        mapper.chain = mock_chain
        
        state = {"research_bundle": {"final_evidence": "Lots of research"}}
        result = await mapper(state)
        
        assert result["context_brief"]["pain_points"]["burning_problems"][0]["severity"] == 0.9

@pytest.mark.asyncio
async def test_icp_psychographic_logic():
    """Verify that the psychographer extracts motivation data correctly."""
    mock_llm = MagicMock()
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = ICPPsychographics(
        core_motivations=["Speed", "Control"],
        perceived_risks=["Hallucination"],
        values_alignment=["Transparency"],
        buying_triggers=["Product launch"]
    )
    
    with patch("backend.agents.strategists.ICPPsychographicProfiler.__init__", return_value=None):
        profiler = create_icp_psychographer(mock_llm)
        profiler.chain = mock_chain
        
        state = {"research_bundle": {"final_evidence": "Lots of research"}}
        result = await profiler(state)
        
        assert "Speed" in result["context_brief"]["icp_psychographics"]["core_motivations"]

@pytest.mark.asyncio
async def test_icp_demographic_logic():
    """Verify that the demographer extracts target data correctly."""
    mock_llm = MagicMock()
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = ICPDemographics(
        target_role="Founder",
        company_size="1-10",
        industry_niche="Fintech",
        geographic_focus=["India"],
        tech_stack_affinity=["Stripe", "Next.js"]
    )
    
    with patch("backend.agents.strategists.ICPDemographicProfiler.__init__", return_value=None):
        profiler = create_icp_demographer(mock_llm)
        profiler.chain = mock_chain
        
        state = {"research_bundle": {"final_evidence": "Lots of fintech research"}}
        result = await profiler(state)
        
        assert result["context_brief"]["icp_demographics"]["target_role"] == "Founder"
        assert "India" in result["context_brief"]["icp_demographics"]["geographic_focus"]
