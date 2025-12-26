import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
import uuid

from models.swarm import (
    SwarmState,
    CompetitorProfile,
    CompetitorGroup,
    CompetitorInsight,
    CompetitorAnalysis,
    CompetitorType,
    CompetitorThreatLevel,
    SwarmTask,
    SwarmTaskStatus,
)
from agents.specialists.swarm_competitor_intelligence import SwarmCompetitorIntelligenceAgent
from memory.swarm_l1 import SwarmL1MemoryManager
from services.competitor_monitoring import CompetitorMonitoringService, CompetitorAnalysisService, MonitoringFrequency
from nodes.competitor_intelligence import CompetitorIntelligenceNode
from agents.specialists.competitor_intelligence import (
    CompetitorIntelligenceAgent,
    CompetitorMapOutput,
    CompetitorProfile as OldCompetitorProfile,
)
from models.cognitive import AgentMessage




# Legacy test for backward compatibility
@pytest.mark.asyncio
async def test_competitor_intelligence_logic():
    """
    Phase 45: Verify that the CompetitorIntelligenceAgent maps competitors correctly.
    """
    expected_map = CompetitorMapOutput(
        competitors=[
            OldCompetitorProfile(
                brand_name="Comp A",
                landing_page_hooks=["Save time"],
                pricing_model="$99/mo",
                messaging_weakness="No AI support",
            )
        ],
        market_positioning_gap="Focus on AI-driven strategy.",
    )

    mock_runnable = AsyncMock()
    mock_runnable.ainvoke.return_value = expected_map

    with patch("backend.agents.base.InferenceProvider") as mock_inference:
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_runnable
        mock_inference.get_model.return_value = mock_llm

        agent = CompetitorIntelligenceAgent()
        state = {
            "tenant_id": "test-tenant",
            "messages": [],
            "raw_prompt": "Analyze our competitors.",
        }

        result = await agent(state)

        assert result["last_agent"] == "CompetitorIntelligence"
        assert "Focus on AI-driven strategy" in result["messages"][0].content


# New comprehensive test suite for swarm competitor intelligence
class TestCompetitorModels:
    """Test suite for competitor data models."""

    def test_competitor_profile_creation(self):
        """Test creating a competitor profile."""
        profile = CompetitorProfile(
            id="comp_1",
            name="Test Competitor",
            competitor_type=CompetitorType.DIRECT,
            threat_level=CompetitorThreatLevel.MEDIUM,
            website="https://example.com",
            description="A test competitor",
            market_share=15.5,
            target_audience=["enterprise", "startup"],
            key_features=["feature1", "feature2"],
            pricing_model="subscription",
            strengths=["strong brand", "good product"],
            weaknesses=["poor support", "high price"],
            confidence_score=0.8
        )
        
        assert profile.id == "comp_1"
        assert profile.name == "Test Competitor"
        assert profile.competitor_type == CompetitorType.DIRECT
        assert profile.threat_level == CompetitorThreatLevel.MEDIUM
        assert profile.market_share == 15.5
        assert len(profile.target_audience) == 2
        assert profile.confidence_score == 0.8

    def test_competitor_group_creation(self):
        """Test creating a competitor group."""
        group = CompetitorGroup(
            id="group_1",
            name="Direct Competitors",
            description="Group of direct competitors",
            competitor_ids=["comp_1", "comp_2"],
            common_characteristics=["similar pricing", "same market segment"],
            market_segment="enterprise"
        )
        
        assert group.id == "group_1"
        assert group.name == "Direct Competitors"
        assert len(group.competitor_ids) == 2
        assert group.market_segment == "enterprise"

    def test_competitor_insight_creation(self):
        """Test creating a competitor insight."""
        insight = CompetitorInsight(
            id="insight_1",
            competitor_id="comp_1",
            insight_type="pricing_change",
            title="Price Increase Detected",
            description="Competitor increased prices by 10%",
            impact_assessment="medium",
            confidence=0.9,
            source="web_scraping",
            tags=["pricing", "increase"]
        )
        
        assert insight.id == "insight_1"
        assert insight.competitor_id == "comp_1"
        assert insight.insight_type == "pricing_change"
        assert insight.confidence == 0.9

    def test_competitor_analysis_creation(self):
        """Test creating a competitor analysis."""
        analysis = CompetitorAnalysis(
            id="analysis_1",
            analysis_type="swot",
            competitor_ids=["comp_1", "comp_2"],
            summary="SWOT analysis of direct competitors",
            key_findings=["finding1", "finding2"],
            recommendations=["recommendation1"],
            threat_level=CompetitorThreatLevel.HIGH,
            confidence_score=0.85
        )
        
        assert analysis.id == "analysis_1"
        assert analysis.analysis_type == "swot"
        assert len(analysis.competitor_ids) == 2
        assert analysis.threat_level == CompetitorThreatLevel.HIGH
        assert analysis.confidence_score == 0.85

    def test_swarm_state_with_competitor_data(self):
        """Test swarm state with competitor tracking fields."""
        state = SwarmState(
            competitor_profiles={
                "comp_1": CompetitorProfile(
                    id="comp_1",
                    name="Test Competitor",
                    competitor_type=CompetitorType.DIRECT,
                    threat_level=CompetitorThreatLevel.MEDIUM
                )
            },
            competitor_groups={
                "group_1": CompetitorGroup(
                    id="group_1",
                    name="Test Group",
                    description="Test group description"
                )
            },
            competitor_insights=[
                CompetitorInsight(
                    id="insight_1",
                    competitor_id="comp_1",
                    insight_type="general",
                    title="Test Insight",
                    description="Test description"
                )
            ],
            active_competitor_watchlist=["comp_1"],
            competitive_landscape_summary="Test summary"
        )
        
        assert len(state.competitor_profiles) == 1
        assert len(state.competitor_groups) == 1
        assert len(state.competitor_insights) == 1
        assert len(state.active_competitor_watchlist) == 1
        assert state.competitive_landscape_summary == "Test summary"


class TestSwarmCompetitorIntelligenceAgent:
    """Test suite for swarm competitor intelligence agent."""

    @pytest.fixture
    def agent(self):
        """Create a competitor intelligence agent."""
        return SwarmCompetitorIntelligenceAgent()

    @pytest.fixture
    def sample_state(self):
        """Create a sample swarm state."""
        return SwarmState(
            shared_knowledge={"objective": "Analyze competitive landscape"},
            competitive_landscape_summary="Current market has 3 main competitors"
        )

    @pytest.mark.asyncio
    async def test_discover_competitors(self, agent, sample_state):
        """Test competitor discovery operation."""
        with patch.object(agent, '_call_llm') as mock_llm:
            # Mock LLM response
            from agents.specialists.swarm_competitor_intelligence import CompetitorResearchOutput
            mock_response = CompetitorResearchOutput(
                discovered_competitors=[],
                market_insights=["Market is growing", "Competition is intense"],
                competitive_gaps=["No AI features", "Poor mobile experience"],
                recommendations=["Focus on AI", "Improve mobile"],
                confidence_score=0.8,
                research_summary="Discovered 5 new competitors"
            )
            mock_llm.return_value = mock_response
            
            result = await agent.discover_competitors(sample_state)
            
            assert "discovered_competitors" in result
            assert "market_insights" in result
            assert "competitive_gaps" in result
            assert "recommendations" in result
            assert result["confidence_score"] == 0.8
            assert "updated_state" in result

    @pytest.mark.asyncio
    async def test_analyze_competitors(self, agent, sample_state):
        """Test competitor analysis operation."""
        # Add competitor profiles to state
        competitor = CompetitorProfile(
            id="comp_1",
            name="Test Competitor",
            competitor_type=CompetitorType.DIRECT,
            threat_level=CompetitorThreatLevel.MEDIUM
        )
        sample_state.competitor_profiles = {"comp_1": competitor}
        
        with patch.object(agent, '_call_llm') as mock_llm:
            # Mock LLM response
            from agents.specialists.swarm_competitor_intelligence import CompetitorAnalysisOutput
            mock_response = CompetitorAnalysisOutput(
                analysis_type="swot",
                swot_analysis={
                    "strengths": ["Strong brand"],
                    "weaknesses": ["High price"],
                    "opportunities": ["New markets"],
                    "threats": ["New competitors"]
                },
                competitive_positioning="Strong market position",
                threat_assessment=CompetitorThreatLevel.MEDIUM,
                strategic_recommendations=["Lower prices", "Expand to new markets"],
                market_opportunities=["Emerging markets"],
                confidence_score=0.75
            )
            mock_llm.return_value = mock_response
            
            result = await agent.analyze_competitors(sample_state, ["comp_1"])
            
            assert "analysis" in result
            assert "swot_analysis" in result
            assert "competitive_positioning" in result
            assert "threat_assessment" in result
            assert result["confidence_score"] == 0.75

    @pytest.mark.asyncio
    async def test_track_competitor_insights(self, agent, sample_state):
        """Test tracking competitor insights."""
        insight_data = {
            "competitor_id": "comp_1",
            "insight_type": "pricing_change",
            "title": "Price Increase",
            "description": "Competitor increased prices",
            "impact_assessment": "high",
            "confidence": 0.9,
            "source": "web_monitoring",
            "tags": ["pricing", "increase"]
        }
        
        result = await agent.track_competitor_insights(sample_state, insight_data)
        
        assert "insight" in result
        assert "updated_state" in result
        assert result["status"] == "tracked"
        assert result["insight"]["competitor_id"] == "comp_1"


class TestCompetitorIntelligenceNode:
    """Test suite for competitor intelligence node."""

    @pytest.fixture
    def node(self):
        """Create a competitor intelligence node."""
        return CompetitorIntelligenceNode("test_thread")

    @pytest.fixture
    def sample_state(self):
        """Create a sample swarm state."""
        return SwarmState(
            instructions="Discover new competitors in the market",
            shared_knowledge={"objective": "Competitive analysis"}
        )

    @pytest.mark.asyncio
    async def test_handle_discovery(self, node, sample_state):
        """Test handling competitor discovery."""
        with patch.object(node.agent, 'discover_competitors') as mock_discover:
            mock_discover.return_value = {
                "discovered_competitors": [],
                "market_insights": ["Market is growing"],
                "competitive_gaps": ["No AI features"],
                "recommendations": ["Add AI features"],
                "confidence_score": 0.8,
                "updated_state": sample_state
            }
            
            result = await node._handle_discovery(sample_state)
            
            assert "analysis_summary" in result
            assert "discovered_competitors" in result
            assert "market_insights" in result
            assert result["status"] == "completed"

    def test_extract_target_competitors(self, node):
        """Test extracting target competitors from state."""
        # Test with explicit target competitors
        state = SwarmState(target_competitors=["comp_1", "comp_2"])
        result = node._extract_target_competitors(state)
        assert result == ["comp_1", "comp_2"]
        
        # Test with @mentions in instructions
        state = SwarmState(instructions="Analyze @comp_1 and @comp_3")
        result = node._extract_target_competitors(state)
        assert "comp_1" in result
        assert "comp_3" in result
        
        # Test with both
        state = SwarmState(
            target_competitors=["comp_1"],
            instructions="Also analyze @comp_2"
        )
        result = node._extract_target_competitors(state)
        assert "comp_1" in result
        assert "comp_2" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
