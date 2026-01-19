import pytest
from backend.schemas import (
    BusinessContextState, CompanyProfile, MarketAnalysis, 
    CompetitiveLandscape, EnhancedICP, MessagingStrategy,
    CustomerSegments, ValueProposition, BusinessModel,
    GrowthStrategy, RiskFactors, SWOTAnalysis,
    PESTELAnalysis, ValueChainAnalysis, BrandArchetypes,
    CompetitorMatrix
)

@pytest.mark.unit
def test_business_context_state_initialization():
    """Test that BusinessContextState can be initialized with default values."""
    state = BusinessContextState()
    assert state.company_profile is None
    assert state.icp_enhancements == {}
    assert "generated_at" in state.metadata

@pytest.mark.unit
def test_company_profile_defaults():
    profile = CompanyProfile()
    assert profile.name == "Unknown"
    assert profile.industry == "Unknown"

@pytest.mark.unit
def test_market_analysis_defaults():
    market = MarketAnalysis()
    assert market.size == "Unknown"
    assert isinstance(market.trends, list)

@pytest.mark.unit
def test_competitive_landscape_defaults():
    cl = CompetitiveLandscape()
    assert len(cl.competitors) == 0

@pytest.mark.unit
def test_customer_segments_defaults():
    cs = CustomerSegments()
    assert cs.primary == "Unknown"

@pytest.mark.unit
def test_value_proposition_defaults():
    vp = ValueProposition()
    assert vp.core == ""

@pytest.mark.unit
def test_business_model_defaults():
    bm = BusinessModel()
    assert bm.type == "Unknown"

@pytest.mark.unit
def test_growth_strategy_defaults():
    gs = GrowthStrategy()
    assert gs.overview == "Growth strategy not available"

@pytest.mark.unit
def test_risk_factors_defaults():
    rf = RiskFactors()
    assert rf.overview == "Risk analysis not available"

@pytest.mark.unit
def test_advanced_models_initialization():
    assert SWOTAnalysis().strengths == []
    assert PESTELAnalysis().political == []
    assert ValueChainAnalysis().primary_activities == {}
    assert BrandArchetypes().primary == "Unknown"
    assert CompetitorMatrix().comparison == {}

@pytest.mark.unit
def test_messaging_strategy_initialization():
    ms = MessagingStrategy()
    assert ms.brand_voice.tone == "Professional"
    assert ms.ctas.primary == "Learn More"
