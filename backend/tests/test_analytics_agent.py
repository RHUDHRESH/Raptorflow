"""
Test suite for Analytics Agent (MAT-004)

Tests KPI calculation accuracy with various input scenarios,
including edge cases with zero denominators and data validation.
"""

import pytest
from unittest.mock import MagicMock

from backend.agents.matrix.analytics_agent import AnalyticsAgent
from backend.models.matrix import (
    CampaignPerformanceData,
    CampaignKPIs,
    KPIBatchRequest,
    KPIBatchResponse
)


class TestAnalyticsAgent:
    """Test AnalyticsAgent core functionality"""

    @pytest.fixture
    def agent(self):
        """Create a fresh agent instance for each test"""
        return AnalyticsAgent()

    def test_agent_initialization(self, agent):
        """Test agent initializes correctly"""
        assert isinstance(agent, AnalyticsAgent)
        assert hasattr(agent, 'calculate_kpis')
        assert hasattr(agent, 'calculate_kpi_batch')

    def test_calculate_kpis_full_data(self, agent):
        """Test KPI calculation with complete, realistic campaign data"""
        data = CampaignPerformanceData(
            impressions=20000,
            clicks=800,
            cost_usd=400.00,
            conversions=40,
            revenue_usd=2000.00
        )

        kpis = agent.calculate_kpis(data)

        assert isinstance(kpis, CampaignKPIs)

        # Verify calculated values (manual calculation for validation)
        # CTR: 800 / 20000 = 0.04
        assert kpis.click_through_rate_ctr == 0.040000

        # CPC: 400.00 / 800 = 0.5
        assert kpis.cost_per_click_cpc == 0.5000

        # CVR: 40 / 800 = 0.05
        assert kpis.conversion_rate_cvr == 0.050000

        # CPA: 400.00 / 40 = 10.00
        assert kpis.cost_per_acquisition_cpa == 10.0000

        # ROAS: 2000.00 / 400.00 = 5.0
        assert kpis.return_on_ad_spend_roas == 5.0

    def test_calculate_kpis_all_zeroes(self, agent):
        """Test KPI calculation when all inputs are zero"""
        data = CampaignPerformanceData(
            impressions=0,
            clicks=0,
            cost_usd=0.0,
            conversions=0,
            revenue_usd=0.0
        )

        kpis = agent.calculate_kpis(data)

        assert isinstance(kpis, CampaignKPIs)
        assert kpis.click_through_rate_ctr == 0.0
        assert kpis.cost_per_click_cpc == 0.0
        assert kpis.conversion_rate_cvr == 0.0
        assert kpis.cost_per_acquisition_cpa == 0.0
        assert kpis.return_on_ad_spend_roas == 0.0

    def test_calculate_ctr_zero_impressions(self, agent):
        """Test CTR calculation with zero impressions"""
        # CTR should return 0.0 when impressions = 0
        assert agent._calculate_ctr(100, 0) == 0.0

    def test_calculate_ctr_normal_case(self, agent):
        """Test CTR calculation with normal inputs"""
        # CTR: 250 / 5000 = 0.05
        assert agent._calculate_ctr(250, 5000) == 0.050000

    def test_calculate_cpc_zero_clicks(self, agent):
        """Test CPC calculation with zero clicks"""
        # CPC should return 0.0 when clicks = 0
        assert agent._calculate_cpc(100.0, 0) == 0.0

    def test_calculate_cpc_normal_case(self, agent):
        """Test CPC calculation with normal inputs"""
        # CPC: 250.50 / 125 = 2.004 (rounded to 2.0040)
        assert agent._calculate_cpc(250.50, 125) == 2.0040

    def test_calculate_cvr_zero_clicks(self, agent):
        """Test CVR calculation with zero clicks"""
        # CVR should return 0.0 when clicks = 0
        assert agent._calculate_cvr(20, 0) == 0.0

    def test_calculate_cvr_normal_case(self, agent):
        """Test CVR calculation with normal inputs"""
        # CVR: 30 / 600 = 0.05
        assert agent._calculate_cvr(30, 600) == 0.050000

    def test_calculate_cpa_zero_conversions(self, agent):
        """Test CPA calculation with zero conversions"""
        # CPA should return 0.0 when conversions = 0
        assert agent._calculate_cpa(500.0, 0) == 0.0

    def test_calculate_cpa_normal_case(self, agent):
        """Test CPA calculation with normal inputs"""
        # CPA: 750.25 / 25 = 30.01
        assert agent._calculate_cpa(750.25, 25) == 30.0100

    def test_calculate_roas_zero_cost(self, agent):
        """Test ROAS calculation with zero cost"""
        # ROAS should return 0.0 when cost_usd = 0
        assert agent._calculate_roas(1000.0, 0.0) == 0.0

    def test_calculate_roas_normal_case(self, agent):
        """Test ROAS calculation with normal inputs"""
        # ROAS: 1500.00 / 300.00 = 5.0
        assert agent._calculate_roas(1500.00, 300.00) == 5.0

    def test_calculate_roas_loss_scenario(self, agent):
        """Test ROAS calculation with loss (revenue < cost)"""
        # ROAS: 200.00 / 500.00 = 0.4 (loss scenario)
        assert agent._calculate_roas(200.00, 500.00) == 0.4

    def test_calculate_roas_high_multiplier(self, agent):
        """Test ROAS calculation with high return multiplier"""
        # ROAS: 10000.00 / 250.00 = 40.0
        assert agent._calculate_roas(10000.00, 250.00) == 40.0

    def test_calculate_kpis_edge_cases(self, agent):
        """Test KPI calculations with various edge cases"""
        test_cases = [
            # (data, expected_kpis)
            (
                CampaignPerformanceData(impressions=0, clicks=0, cost_usd=0.0, conversions=0, revenue_usd=0.0),
                CampaignKPIs(click_through_rate_ctr=0.0, cost_per_click_cpc=0.0, conversion_rate_cvr=0.0,
                            cost_per_acquisition_cpa=0.0, return_on_ad_spend_roas=0.0)
            ),
            (
                CampaignPerformanceData(impressions=1000, clicks=0, cost_usd=0.0, conversions=0, revenue_usd=0.0),
                CampaignKPIs(click_through_rate_ctr=0.0, cost_per_click_cpc=0.0, conversion_rate_cvr=0.0,
                            cost_per_acquisition_cpa=0.0, return_on_ad_spend_roas=0.0)
            ),
            (
                CampaignPerformanceData(impressions=1000, clicks=50, cost_usd=0.0, conversions=0, revenue_usd=0.0),
                CampaignKPIs(click_through_rate_ctr=0.050000, cost_per_click_cpc=0.0, conversion_rate_cvr=0.0,
                            cost_per_acquisition_cpa=0.0, return_on_ad_spend_roas=0.0)
            ),
            (
                CampaignPerformanceData(impressions=1000, clicks=50, cost_usd=25.0, conversions=0, revenue_usd=0.0),
                CampaignKPIs(click_through_rate_ctr=0.050000, cost_per_click_cpc=0.5, conversion_rate_cvr=0.0,
                            cost_per_acquisition_cpa=0.0, return_on_ad_spend_roas=0.0)
            ),
            (
                CampaignPerformanceData(impressions=1000, clicks=50, cost_usd=25.0, conversions=5, revenue_usd=0.0),
                CampaignKPIs(click_through_rate_ctr=0.050000, cost_per_click_cpc=0.5, conversion_rate_cvr=0.1,
                            cost_per_acquisition_cpa=5.0, return_on_ad_spend_roas=0.0)
            ),
        ]

        for data, expected in test_cases:
            kpis = agent.calculate_kpis(data)
            assert kpis.click_through_rate_ctr == expected.click_through_rate_ctr
            assert kpis.cost_per_click_cpc == expected.cost_per_click_cpc
            assert kpis.conversion_rate_cvr == expected.conversion_rate_cvr
            assert kpis.cost_per_acquisition_cpa == expected.cost_per_acquisition_cpa
            assert kpis.return_on_ad_spend_roas == expected.return_on_ad_spend_roas

    def test_calculate_kpi_batch_single_campaign(self, agent):
        """Test batch calculation with single campaign"""
        data = CampaignPerformanceData(
            impressions=5000,
            clicks=250,
            cost_usd=125.0,
            conversions=12,
            revenue_usd=600.0
        )

        request = KPIBatchRequest(campaigns=[data])
        response = agent.calculate_kpi_batch(request)

        assert isinstance(response, KPIBatchResponse)
        assert response.total_campaigns == 1
        assert len(response.kpis) == 1

        kpi = response.kpis[0]
        assert kpi.click_through_rate_ctr == 0.050000  # 250/5000
        assert kpi.cost_per_click_cpc == 0.5000      # 125.0/250
        assert kpi.conversion_rate_cvr == 0.048000    # 12/250
        assert kpi.cost_per_acquisition_cpa == 10.4167 # 125.0/12 ≈ 10.4167

    def test_calculate_kpi_batch_multiple_campaigns(self, agent):
        """Test batch calculation with multiple campaigns"""
        campaigns = [
            CampaignPerformanceData(impressions=10000, clicks=500, cost_usd=250.0, conversions=25, revenue_usd=1250.0),
            CampaignPerformanceData(impressions=20000, clicks=800, cost_usd=400.0, conversions=40, revenue_usd=2000.0),
        ]

        request = KPIBatchRequest(campaigns=campaigns)
        response = agent.calculate_kpi_batch(request)

        assert response.total_campaigns == 2
        assert len(response.kpis) == 2

        # Check first campaign
        kpi1 = response.kpis[0]
        assert kpi1.click_through_rate_ctr == 0.050000
        assert kpi1.return_on_ad_spend_roas == 5.0

        # Check second campaign
        kpi2 = response.kpis[1]
        assert kpi2.click_through_rate_ctr == 0.040000
        assert kpi2.return_on_ad_spend_roas == 5.0

    def test_validate_performance_data_no_warnings(self, agent):
        """Test validation with clean data returns no warnings"""
        data = CampaignPerformanceData(
            impressions=10000,
            clicks=500,  # Reasonable CTR (<50%)
            cost_usd=250.0,
            conversions=50,  # Reasonable conversion count
            revenue_usd=1250.0  # Reasonable ROAS (5x)
        )

        warnings = agent.validate_performance_data(data)
        assert warnings == []

    def test_validate_performance_data_clicks_exceed_impressions(self, agent):
        """Test validation detects clicks > impressions"""
        data = CampaignPerformanceData(
            impressions=1000,
            clicks=1500,  # Invalid: more clicks than impressions
            cost_usd=100.0,
            conversions=50,
            revenue_usd=500.0
        )

        warnings = agent.validate_performance_data(data)
        assert "Clicks cannot exceed impressions" in warnings

    def test_validate_performance_data_conversions_exceed_clicks(self, agent):
        """Test validation detects conversions > clicks"""
        data = CampaignPerformanceData(
            impressions=5000,
            clicks=250,
            cost_usd=125.0,
            conversions=300,  # Invalid: more conversions than clicks
            revenue_usd=1500.0
        )

        warnings = agent.validate_performance_data(data)
        assert "Conversions cannot exceed clicks" in warnings

    def test_validate_performance_data_suspicious_ctr(self, agent):
        """Test validation detects suspiciously high CTR"""
        data = CampaignPerformanceData(
            impressions=1000,
            clicks=600,  # CTR = 0.6 (>50% is suspicious)
            cost_usd=300.0,
            conversions=30,
            revenue_usd=1500.0
        )

        warnings = agent.validate_performance_data(data)
        assert "CTR above 50%" in warnings

    def test_validate_performance_data_suspicious_roas(self, agent):
        """Test validation detects suspiciously high ROAS"""
        data = CampaignPerformanceData(
            impressions=10000,
            clicks=500,
            cost_usd=1.0,    # Very small cost
            conversions=25,
            revenue_usd=110.0  # ROAS = 110x (suspiciously high)
        )

        warnings = agent.validate_performance_data(data)
        assert "ROAS above 100x" in warnings

    def test_validate_performance_data_zero_warnings(self, agent):
        """Test validation provides helpful warnings for zero values"""
        test_cases = [
            (CampaignPerformanceData(impressions=0, clicks=0, cost_usd=0.0, conversions=0, revenue_usd=0.0),
             ["Zero impressions prevent CTR calculation"]),
            (CampaignPerformanceData(impressions=1000, clicks=0, cost_usd=0.0, conversions=0, revenue_usd=0.0),
             ["Zero clicks prevent CPC and CVR calculations"]),
            (CampaignPerformanceData(impressions=1000, clicks=100, cost_usd=0.0, conversions=0, revenue_usd=0.0),
             ["Zero conversions prevent CPA calculation", "Zero cost prevents CPC, CPA, and ROAS calculations"]),
        ]

        for data, expected_warnings in test_cases:
            warnings = agent.validate_performance_data(data)
            for warning in expected_warnings:
                assert warning in warnings

    def test_calculate_kpi_breakdown(self, agent):
        """Test detailed KPI breakdown calculation"""
        data = CampaignPerformanceData(
            impressions=10000,
            clicks=400,
            cost_usd=200.0,
            conversions=16,
            revenue_usd=1600.0
        )

        result = agent.calculate_kpi_breakdown(data)

        # Check structure
        assert "kpis" in result
        assert "validation_warnings" in result
        assert "input_summary" in result

        # Check KPI calculations
        kpis = result["kpis"]
        assert kpis.click_through_rate_ctr == 0.040000
        assert kpis.cost_per_click_cpc == 0.5000
        assert kpis.conversion_rate_cvr == 0.040000
        assert kpis.cost_per_acquisition_cpa == 12.5000
        assert kpis.return_on_ad_spend_roas == 8.0

        # Check input summary
        summary = result["input_summary"]
        assert summary["impressions"] == 10000
        assert summary["clicks"] == 400
        assert summary["cost_usd"] == 200.0
        assert summary["conversions"] == 16
        assert summary["revenue_usd"] == 1600.0

    def test_calculate_kpi_breakdown_with_warnings(self, agent):
        """Test detailed breakdown includes validation warnings"""
        data = CampaignPerformanceData(
            impressions=500,
            clicks=600,  # Invalid: clicks > impressions
            cost_usd=1.0,
            conversions=30,
            revenue_usd=150.0  # ROAS = 150x (suspicious)
        )

        result = agent.calculate_kpi_breakdown(data)

        warnings = result["validation_warnings"]
        assert "Clicks cannot exceed impressions" in warnings
        assert "ROAS above 100x" in warnings

    def test_precision_handling(self, agent):
        """Test that calculations handle precision correctly"""
        data = CampaignPerformanceData(
            impressions=1000000,
            clicks=12345,
            cost_usd=999.99,
            conversions=678,
            revenue_usd=12345.67
        )

        kpis = agent.calculate_kpis(data)

        # Verify precision is maintained for different KPI types
        assert kpis.click_through_rate_ctr == 0.012345  # 6 decimal places
        assert kpis.cost_per_click_cpc == 0.0810       # 4 decimal places
        assert kpis.conversion_rate_cvr == 0.054896    # 6 decimal places
        assert kpis.cost_per_acquisition_cpa == 1.4752  # 4 decimal places
        assert kpis.return_on_ad_spend_roas == 12.35   # 2 decimal places

    def test_large_number_handling(self, agent):
        """Test calculations work with large numbers"""
        data = CampaignPerformanceData(
            impressions=50000000,  # 50M impressions
            clicks=1500000,        # 1.5M clicks
            cost_usd=750000.0,     # $750K cost
            conversions=45000,     # 45K conversions
            revenue_usd=2250000.0  # $2.25M revenue
        )

        kpis = agent.calculate_kpis(data)

        # Manual verification
        assert kpis.click_through_rate_ctr == 0.030000  # 1.5M/50M
        assert kpis.cost_per_click_cpc == 0.5000       # 750K/1.5M
        assert kpis.conversion_rate_cvr == 0.030000    # 45K/1.5M
        assert kpis.cost_per_acquisition_cpa == 16.6667 # 750K/45K ≈ 16.6667
        assert kpis.return_on_ad_spend_roas == 3.0     # 2.25M/750K


class TestModelValidation:
    """Test Pydantic model validation"""

    def test_campaign_performance_data_validation(self):
        """Test CampaignPerformanceData model validation"""
        # Valid data
        data = CampaignPerformanceData(
            impressions=10000,
            clicks=500,
            cost_usd=250.50,
            conversions=25,
            revenue_usd=1250.75
        )
        assert data.impressions == 10000
        assert data.clicks == 500
        assert data.cost_usd == 250.50

    def test_campaign_performance_data_negative_values(self):
        """Test that negative values are not allowed"""
        try:
            CampaignPerformanceData(
                impressions=-100,  # Invalid
                clicks=500,
                cost_usd=250.50,
                conversions=25,
                revenue_usd=1250.75
            )
            assert False, "Should have raised validation error"
        except Exception:
            # Expected validation error
            pass

    def test_campaign_kpis_validation(self):
        """Test CampaignKPIs model validation"""
        kpis = CampaignKPIs(
            click_through_rate_ctr=0.025,
            cost_per_click_cpc=0.50,
            conversion_rate_cvr=0.05,
            cost_per_acquisition_cpa=10.00,
            return_on_ad_spend_roas=5.0
        )

        assert kpis.click_through_rate_ctr == 0.025
        assert kpis.cost_per_click_cpc == 0.50
        assert kpis.conversion_rate_cvr == 0.05
        assert kpis.cost_per_acquisition_cpa == 10.00
        assert kpis.return_on_ad_spend_roas == 5.0


class TestIntegrationScenarios:
    """Test complete workflows and integration scenarios"""

    def test_real_world_campaign_optimization_scenario(self):
        """Test realistic campaign optimization workflow"""
        agent = AnalyticsAgent()

        # Simulate A/B test results
        campaign_a = CampaignPerformanceData(
            impressions=25000,
            clicks=1250,
            cost_usd=750.0,
            conversions=75,
            revenue_usd=2250.0
        )

        campaign_b = CampaignPerformanceData(
            impressions=25000,
            clicks=1000,
            cost_usd=500.0,
            conversions=70,
            revenue_usd=2800.0
        )

        kpis_a = agent.calculate_kpis(campaign_a)
        kpis_b = agent.calculate_kpis(campaign_b)

        # Campaign A: CTR=5%, CPC=$0.60, CVR=6%, CPA=$10, ROAS=3x
        # Campaign B: CTR=4%, CPC=$0.50, CVR=7%, CPA≈$7.14, ROAS=5.6x

        assert kpis_a.click_through_rate_ctr == 0.050000
        assert kpis_a.cost_per_click_cpc == 0.6000
        assert kpis_a.return_on_ad_spend_roas == 3.0

        assert kpis_b.click_through_rate_ctr == 0.040000
        assert kpis_b.cost_per_click_cpc == 0.5000
        assert round(kpis_b.return_on_ad_spend_roas, 1) == 5.6

        # Campaign B has better ROAS despite lower CTR
        assert kpis_b.return_on_ad_spend_roas > kpis_a.return_on_ad_spend_roas

    def test_data_quality_audit_scenario(self):
        """Test scenario where we audit data quality issues"""
        agent = AnalyticsAgent()

        problematic_data = CampaignPerformanceData(
            impressions=1000,
            clicks=1001,    # Invalid: clicks > impressions
            cost_usd=0.01,  # Very low cost
            conversions=100, # High conversions
            revenue_usd=500.0 # ROAS = 50,000x (impossible)
        )

        warnings = agent.validate_performance_data(problematic_data)

        # Should identify multiple data quality issues
        assert len(warnings) >= 3  # Multiple validation issues expected
        assert any("exceed" in w for w in warnings)  # Logical inconsistencies
        assert any("ROAS" in w for w in warnings)    # Quality issue

    def test_seasonal_campaign_analysis(self):
        """Test analyzing seasonal campaign performance"""
        agent = AnalyticsAgent()

        # Holiday campaign (high spending, high returns)
        holiday_campaign = CampaignPerformanceData(
            impressions=100000,
            clicks=10000,
            cost_usd=10000.0,
            conversions=500,
            revenue_usd=75000.0
        )

        # Regular campaign (lower spending, moderate returns)
        regular_campaign = CampaignPerformanceData(
            impressions=50000,
            clicks=2500,
            cost_usd=1250.0,
            conversions=125,
            revenue_usd=6250.0
        )

        holiday_kpis = agent.calculate_kpis(holiday_campaign)
        regular_kpis = agent.calculate_kpis(regular_campaign)

        # Holiday campaign should show higher ROAS
        assert holiday_kpis.return_on_ad_spend_roas == 7.5
        assert regular_kpis.return_on_ad_spend_roas == 5.0
        assert holiday_kpis.return_on_ad_spend_roas > regular_kpis.return_on_ad_spend_roas
