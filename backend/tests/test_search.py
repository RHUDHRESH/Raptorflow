import pytest
from unittest.mock import patch, MagicMock
from backend.tools.search import TavilyMultiHopTool, PerplexitySearchTool
from unittest.mock import patch, MagicMock, AsyncMock

from backend.agents.researchers import (
    create_reddit_analyst, RedditAnalysis, RedditInsight, 
    create_linkedin_profiler, LinkedInAnalysis, LinkedInProfile, 
    create_competitor_mapper, CompetitorAnalysis, CompetitorPlan, 
    create_evidence_bundler, EvidenceBundle, 
    create_source_validator, ValidatorOutput, SourceValidation,
    create_trend_extractor, TrendAnalysis, MarketTrend,
    create_gap_finder, GapAnalysis, MarketGap,
    create_research_summarizer,
    create_brand_history_contextualizer,
    create_visual_trend_analyzer, VisualAnalysis, VisualStyle,
    create_positioning_mapper, PositioningMap,
    create_swot_analyzer, SWOTAnalysis,
    create_research_qa_guard, ResearchQAPass,
    create_competitor_tracker
)

@pytest.mark.asyncio
async def test_competitor_tracker_logic():
    """Verify that the tracker syncs competitor data correctly."""
    with patch("backend.agents.researchers.save_entity", new_callable=AsyncMock) as mock_save:
        tracker = create_competitor_tracker()
        state = {
            "workspace_id": "ws_1",
            "research_bundle": {"competitor_map": {"brand_name": "CompX"}}
        }
        result = await tracker(state)
        
        assert result["status"] == "competitor_sync_complete"
        mock_save.assert_called_once()

@pytest.mark.asyncio
async def test_research_qa_logic():
    """Verify that the QA node evaluates research quality correctly."""
    mock_llm = MagicMock()
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = ResearchQAPass(
        is_high_quality=True, score=0.9, issues=[], improvement_suggestions=[]
    )
    
    with patch("backend.agents.researchers.ResearchQAGuard.__init__", return_value=None):
        guard = create_research_qa_guard(mock_llm)
        guard.chain = mock_chain
        
        state = {"research_bundle": {"executive_brief": "SOTA Brief"}}
        result = await guard(state)
        
        assert result["research_bundle"]["qa_pass"]["is_high_quality"] is True

@pytest.mark.asyncio
async def test_swot_analyzer_logic():
    """Verify that the SWOT analyzer extracts 4 quadrants correctly."""
    mock_llm = MagicMock()
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = SWOTAnalysis(
        strengths=["S1"], weaknesses=["W1"], 
        opportunities=["O1"], threats=["T1"]
    )
    
    with patch("backend.agents.researchers.SWOTAnalyzer.__init__", return_value=None):
        analyzer = create_swot_analyzer(mock_llm)
        analyzer.chain = mock_chain
        
        state = {"research_bundle": {"final_evidence": {}}}
        result = await analyzer(state)
        
        assert "S1" in result["research_bundle"]["swot"]["strengths"]

@pytest.mark.asyncio
async def test_positioning_mapper_logic():
    """Verify that the mapper defines X/Y axes correctly."""
    mock_llm = MagicMock()
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = PositioningMap(
        x_axis="Price (Low -> High)",
        y_axis="Complexity (Simple -> Advanced)",
        competitor_coordinates={"CompCo": {"x": 0.8, "y": 0.9}}
    )
    
    with patch("backend.agents.researchers.PositioningMapper.__init__", return_value=None):
        mapper = create_positioning_mapper(mock_llm)
        mapper.chain = mock_chain
        
        state = {"research_bundle": {"competitor_map": {"plans": []}}}
        result = await mapper(state)
        
        assert result["research_bundle"]["positioning_map"]["x_axis"] == "Price (Low -> High)"

@pytest.mark.asyncio
async def test_visual_trend_analyzer_logic():
    """Verify that the multimodal analyzer extracts aesthetic themes."""
    mock_llm = MagicMock()
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = VisualAnalysis(styles=[
        VisualStyle(aesthetic="Minimalist", color_palette=["#000", "#FFF"], signal="Clean UI trend")
    ])
    
    with patch("backend.agents.researchers.VisualTrendAnalyzer.__init__", return_value=None):
        analyzer = create_visual_trend_analyzer(mock_llm)
        analyzer.chain = mock_chain
        
        state = {"research_bundle": {"raw_images": ["img_data"]}}
        result = await analyzer(state)
        
        assert result["research_bundle"]["visual_trends"]["styles"][0]["aesthetic"] == "Minimalist"

@pytest.mark.asyncio
async def test_brand_history_context_logic():
    """Verify that the contextualizer retrieves past project data."""
    with patch("backend.agents.researchers.get_memory", new_callable=AsyncMock) as mock_mem:
        mock_mem.return_value = [("id", "Past campaign: Launch 2024", {"type": "episodic"}, 0.9)]
        
        contextualizer = create_brand_history_contextualizer()
        state = {"workspace_id": "ws_1", "raw_prompt": "new campaign"}
        result = await contextualizer(state)
        
        assert "Past campaign" in result["research_bundle"]["historical_context"][0][1]

@pytest.mark.asyncio
async def test_research_summarizer_logic():
    """Verify that the summarizer node condenses research data."""
    mock_llm = MagicMock()
    with patch("backend.agents.researchers.summarize_recursively", new_callable=AsyncMock) as mock_sum:
        mock_sum.return_value = "Condensed Brief"
        
        summarizer = create_research_summarizer(mock_llm)
        state = {"research_bundle": {"final_evidence": "Lots of data"}}
        result = await summarizer(state)
        
        assert result["research_bundle"]["executive_brief"] == "Condensed Brief"

@pytest.mark.asyncio
async def test_gap_finder_logic():
    """Verify that the gap finder identifies differentiation opportunities."""
    mock_llm = MagicMock()
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = GapAnalysis(gaps=[
        MarketGap(description="Low focus on privacy", severity=0.8, opportunity="SOTA Privacy First Agent")
    ])
    
    with patch("backend.agents.researchers.GapFinder.__init__", return_value=None):
        finder = create_gap_finder(mock_llm)
        finder.chain = mock_chain
        
        state = {"research_bundle": {"competitor_map": {"plans": []}}}
        result = await finder(state)
        
        assert result["research_bundle"]["gaps"]["gaps"][0]["severity"] == 0.8

@pytest.mark.asyncio
async def test_trend_extractor_logic():
    """Verify that the trend extractor finds patterns in evidence."""
    mock_llm = MagicMock()
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = TrendAnalysis(trends=[
        MarketTrend(name="AI Native", strength=0.9, signal="High interest in local LLMs")
    ])
    
    with patch("backend.agents.researchers.TrendExtractor.__init__", return_value=None):
        extractor = create_trend_extractor(mock_llm)
        extractor.chain = mock_chain
        
        state = {"research_bundle": {"final_evidence": {"key_findings": ["AI is hot"]}}}
        result = await extractor(state)
        
        assert result["research_bundle"]["trends"]["trends"][0]["name"] == "AI Native"

@pytest.mark.asyncio
async def test_source_validator_logic():
    """Verify that the source validator scores URLs correctly."""
    mock_llm = MagicMock()
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = ValidatorOutput(validations=[
        SourceValidation(url="https://trusted.com", credibility_score=0.9, reasoning="SOTA Domain", is_trusted=True)
    ])
    
    with patch("backend.agents.researchers.SourceValidator.__init__", return_value=None):
        validator = create_source_validator(mock_llm)
        validator.chain = mock_chain
        
        state = {"research_bundle": {"raw_urls": ["https://trusted.com"]}}
        result = await validator(state)
        
        assert result["research_bundle"]["validations"]["validations"][0]["credibility_score"] == 0.9

@pytest.mark.asyncio
async def test_evidence_bundler_logic():
    """Verify that the evidence bundler consolidates research data."""
    mock_llm = MagicMock()
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = EvidenceBundle(
        topic="SaaS Growth",
        key_findings=["Finding 1"],
        raw_sources=["https://src.com"],
        confidence_score=0.95
    )
    
    with patch("backend.agents.researchers.EvidenceBundler.__init__", return_value=None):
        bundler = create_evidence_bundler(mock_llm)
        bundler.chain = mock_chain
        
        state = {"research_bundle": {"raw_search": "data"}}
        result = await bundler(state)
        
        assert result["research_bundle"]["final_evidence"]["topic"] == "SaaS Growth"
        assert result["research_bundle"]["final_evidence"]["confidence_score"] == 0.95

@pytest.mark.asyncio
async def test_competitor_mapper_logic():
    """Verify that the competitor mapper extracts data correctly."""
    mock_llm = MagicMock()
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = CompetitorAnalysis(
        brand_name="CompCo",
        plans=[CompetitorPlan(name="Pro", price="$99", features=["API", "Support"])],
        unique_selling_points=["Speed"]
    )
    
    with patch("backend.agents.researchers.CompetitorFeatureMapper.__init__", return_value=None):
        mapper = create_competitor_mapper(mock_llm)
        mapper.chain = mock_chain
        
        state = {"research_bundle": {"raw_competitor_data": "CompCo Pro is $99"}}
        result = await mapper(state)
        
        assert result["research_bundle"]["competitor_map"]["brand_name"] == "CompCo"
        assert result["research_bundle"]["competitor_map"]["plans"][0]["name"] == "Pro"

@pytest.mark.asyncio
async def test_linkedin_profiler_logic():
    """Verify that the linkedin profiler extracts profiles correctly."""
    mock_llm = MagicMock()
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = LinkedInAnalysis(profiles=[
        LinkedInProfile(name="John Doe", key_themes=["AI", "SaaS"], authority_score=0.9)
    ])
    
    with patch("backend.agents.researchers.LinkedInProfiler.__init__", return_value=None):
        profiler = create_linkedin_profiler(mock_llm)
        profiler.chain = mock_chain
        
        state = {"research_bundle": {"raw_linkedin_data": "John Doe is an AI expert"}}
        result = await profiler(state)
        
        assert len(result["research_bundle"]["linkedin_insights"]["profiles"]) == 1
        assert result["research_bundle"]["linkedin_insights"]["profiles"][0]["name"] == "John Doe"

@pytest.mark.asyncio
async def test_reddit_analyst_logic():
    """Verify that the reddit analyst extracts insights correctly."""
    mock_llm = MagicMock()
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = RedditAnalysis(insights=[
        RedditInsight(pain_point="Cost", sentiment="angry", evidence_quote="Too expensive!")
    ])
    
    with patch("backend.agents.researchers.RedditSentimentAnalyst.__init__", return_value=None):
        analyst = create_reddit_analyst(mock_llm)
        analyst.chain = mock_chain
        
        state = {"research_bundle": {"raw_social_data": "expensive software is bad"}}
        result = await analyst(state)
        
        assert len(result["research_bundle"]["social_insights"]["insights"]) == 1
        assert result["research_bundle"]["social_insights"]["insights"][0]["pain_point"] == "Cost"

@pytest.mark.asyncio
async def test_perplexity_search_logic():
    """Verify that the tool executes perplexity search correctly."""
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={
        "choices": [{"message": {"content": "SOTA Answer"}}]
    })
    
    mock_session = MagicMock()
    mock_session.post.return_value.__aenter__.return_value = mock_resp
    mock_session.__aenter__.return_value = mock_session

    with patch("aiohttp.ClientSession", return_value=mock_session):
        tool = PerplexitySearchTool()
        result = await tool.run(query="latest AI news")
        
        assert result["success"] is True
        assert result["data"] == "SOTA Answer"

@pytest.mark.asyncio
async def test_tavily_search_logic():
    """Verify that the tool executes tavily search correctly."""
    # This will fail if TavilyMultiHopTool is not correctly implemented
    mock_client_inst = MagicMock()
    mock_client_inst.search.return_value = {
        "results": [{"title": "SOTA AI", "content": "Evidence", "url": "https://test.com"}]
    }
    
    with patch("backend.tools.search.TavilyClient", return_value=mock_client_inst):
        tool = TavilyMultiHopTool()
        result = await tool.run(query="SOTA agent patterns 2025")
        
        assert result["success"] is True
        assert len(result["data"]) == 1
        assert result["data"][0]["title"] == "SOTA AI"
        mock_client_inst.search.assert_called_once()
