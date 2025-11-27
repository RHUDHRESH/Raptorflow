# test_seer_e2e_integration.py
# RaptorFlow Codex - Seer Lord E2E Integration Tests
# Phase 2A Week 6 - Comprehensive testing suite

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timedelta
import json

# Backend imports
from backend_lord_seer import (
    SeerLord,
    ForecastType,
    TrendDirection,
    ConfidenceLevel,
    TrendPrediction,
    MarketIntelligence,
    PerformanceAnalysis,
    StrategicRecommendation,
    ForecastReport,
)

# ============================================================================
# UNIT TESTS - SEER LORD AGENT
# ============================================================================

class TestSeerLordAgent:
    """Unit tests for Seer Lord agent"""

    @pytest.fixture
    def seer(self):
        """Create Seer Lord instance"""
        lord = SeerLord()
        return lord

    # Test initialization
    def test_seer_initialization(self, seer):
        """Test Seer Lord initialization"""
        assert seer.name == "Seer Lord"
        assert seer.role.value == "seer"
        assert seer.trend_predictions == {}
        assert seer.market_intelligence == {}
        assert seer.performance_analyses == {}
        assert seer.strategic_recommendations == {}
        assert seer.forecast_reports == {}

    def test_seer_role_value(self, seer):
        """Test Seer Lord has correct role"""
        assert seer.role.value == "seer"

    # Test capability registration
    def test_seer_has_five_capabilities(self, seer):
        """Test Seer Lord has all 5 capabilities"""
        assert len(seer.capabilities) == 5
        capability_names = {cap.name for cap in seer.capabilities}
        expected = {
            "predict_trend",
            "gather_intelligence",
            "analyze_performance",
            "generate_recommendation",
            "get_forecast_report",
        }
        assert capability_names == expected

    # Test trend prediction
    @pytest.mark.asyncio
    async def test_predict_trend_basic(self, seer):
        """Test basic trend prediction"""
        result = await seer.execute(
            task="predict_trend",
            parameters={
                "metric_name": "market_growth",
                "historical_values": [50, 55, 60, 65, 70],
                "forecast_period_days": 30,
                "forecast_type": "linear",
            },
        )

        assert result.get("success", True)
        assert "prediction_id" in result
        assert "trend_direction" in result
        assert "confidence" in result
        assert "predicted_values" in result
        assert 0 <= result["confidence"] <= 100

    @pytest.mark.asyncio
    async def test_predict_trend_stores_prediction(self, seer):
        """Test prediction is stored"""
        result = await seer.execute(
            task="predict_trend",
            parameters={
                "metric_name": "engagement",
                "historical_values": [40, 42, 44, 46, 48],
                "forecast_period_days": 30,
                "forecast_type": "exponential",
            },
        )

        prediction_id = result["prediction_id"]
        assert prediction_id in seer.trend_predictions
        assert seer.trend_predictions[prediction_id].metric_name == "engagement"

    @pytest.mark.asyncio
    async def test_predict_trend_increments_counter(self, seer):
        """Test prediction counter increments"""
        initial_count = seer.total_predictions_made

        await seer.execute(
            task="predict_trend",
            parameters={
                "metric_name": "sales",
                "historical_values": [100, 105, 110, 115, 120],
                "forecast_period_days": 30,
                "forecast_type": "linear",
            },
        )

        assert seer.total_predictions_made == initial_count + 1

    @pytest.mark.asyncio
    async def test_predict_trend_different_types(self, seer):
        """Test different forecast types"""
        forecast_types = ["linear", "exponential", "polynomial", "seasonal", "cyclical"]

        for ftype in forecast_types:
            result = await seer.execute(
                task="predict_trend",
                parameters={
                    "metric_name": f"metric_{ftype}",
                    "historical_values": [50, 55, 60, 65, 70],
                    "forecast_period_days": 30,
                    "forecast_type": ftype,
                },
            )
            assert "prediction_id" in result
            assert result["forecast_type"] == ftype

    @pytest.mark.asyncio
    async def test_predict_trend_with_minimal_data(self, seer):
        """Test prediction with minimal historical data"""
        result = await seer.execute(
            task="predict_trend",
            parameters={
                "metric_name": "minimal",
                "historical_values": [50, 55],
                "forecast_period_days": 30,
                "forecast_type": "linear",
            },
        )

        assert "prediction_id" in result
        assert len(result["predicted_values"]) == 30

    # Test market intelligence
    @pytest.mark.asyncio
    async def test_gather_intelligence_basic(self, seer):
        """Test gathering market intelligence"""
        result = await seer.execute(
            task="gather_intelligence",
            parameters={
                "intelligence_type": "market_trend",
                "title": "Market Analysis",
                "summary": "Growing market trends",
                "source": "internal_analysis",
                "key_insights": ["Insight 1", "Insight 2"],
            },
        )

        assert result.get("success", True)
        assert "intelligence_id" in result
        assert "impact_score" in result
        assert "threat_level" in result

    @pytest.mark.asyncio
    async def test_gather_intelligence_increments_counter(self, seer):
        """Test intelligence counter increments"""
        initial_count = seer.total_intelligence_gathered

        await seer.execute(
            task="gather_intelligence",
            parameters={
                "intelligence_type": "competitive",
                "title": "Competitor Analysis",
                "summary": "Competitor strategy",
                "source": "market_research",
                "key_insights": ["Key insight"],
            },
        )

        assert seer.total_intelligence_gathered == initial_count + 1

    @pytest.mark.asyncio
    async def test_gather_intelligence_threat_levels(self, seer):
        """Test threat level determination"""
        # Low threat (few insights)
        result_low = await seer.execute(
            task="gather_intelligence",
            parameters={
                "intelligence_type": "economic",
                "title": "Low Threat",
                "summary": "Minor economic changes",
                "source": "public",
                "key_insights": ["Minor insight"],
            },
        )

        # High threat (many insights)
        result_high = await seer.execute(
            task="gather_intelligence",
            parameters={
                "intelligence_type": "regulatory",
                "title": "High Threat",
                "summary": "Major regulatory changes",
                "source": "regulatory_body",
                "key_insights": ["Insight 1", "Insight 2", "Insight 3", "Insight 4", "Insight 5"],
            },
        )

        assert result_low.get("threat_level") in ["low", "medium"]
        assert result_high.get("threat_level") in ["medium", "high", "critical"]

    # Test performance analysis
    @pytest.mark.asyncio
    async def test_analyze_performance_basic(self, seer):
        """Test performance analysis"""
        result = await seer.execute(
            task="analyze_performance",
            parameters={
                "scope": "campaign",
                "scope_id": "camp_001",
                "metrics": {"engagement": 80, "reach": 75, "conversion": 70},
            },
        )

        assert result.get("success", True)
        assert "analysis_id" in result
        assert "performance_score" in result
        assert "trend_analysis" in result
        assert "strengths" in result
        assert "weaknesses" in result

    @pytest.mark.asyncio
    async def test_analyze_performance_scopes(self, seer):
        """Test analysis with different scopes"""
        scopes = ["campaign", "guild", "organization"]

        for scope in scopes:
            result = await seer.execute(
                task="analyze_performance",
                parameters={
                    "scope": scope,
                    "scope_id": f"{scope}_001",
                    "metrics": {"metric1": 75, "metric2": 80},
                },
            )
            assert result["scope"] == scope

    # Test recommendation generation
    @pytest.mark.asyncio
    async def test_generate_recommendation_basic(self, seer):
        """Test recommendation generation"""
        result = await seer.execute(
            task="generate_recommendation",
            parameters={
                "title": "Growth Strategy",
                "description": "Scale operations",
                "priority": "high",
                "supporting_insights": ["Insight 1", "Insight 2"],
                "required_resources": {"budget": 10000, "team_size": 5},
            },
        )

        assert result.get("success", True)
        assert "recommendation_id" in result
        assert "expected_impact" in result
        assert "implementation_effort" in result
        assert "success_probability" in result

    @pytest.mark.asyncio
    async def test_generate_recommendation_increments_counter(self, seer):
        """Test recommendation counter increments"""
        initial_count = seer.total_recommendations_generated

        await seer.execute(
            task="generate_recommendation",
            parameters={
                "title": "Cost Reduction",
                "description": "Reduce expenses",
                "priority": "normal",
                "supporting_insights": [],
                "required_resources": {},
            },
        )

        assert seer.total_recommendations_generated == initial_count + 1

    # Test forecast report
    @pytest.mark.asyncio
    async def test_get_forecast_report_basic(self, seer):
        """Test forecast report generation"""
        # Create some predictions and intelligence first
        await seer.execute(
            task="predict_trend",
            parameters={
                "metric_name": "market_size",
                "historical_values": [100, 110, 120, 130, 140],
                "forecast_period_days": 30,
                "forecast_type": "linear",
            },
        )

        await seer.execute(
            task="gather_intelligence",
            parameters={
                "intelligence_type": "market_trend",
                "title": "Market Report",
                "summary": "Positive trends",
                "source": "analysis",
                "key_insights": ["Growing market"],
            },
        )

        # Generate report
        result = await seer.execute(
            task="get_forecast_report",
            parameters={
                "title": "Q1 Forecast",
                "forecast_period_days": 90,
                "include_predictions": True,
                "include_intelligence": True,
            },
        )

        assert result.get("success", True)
        assert "report_id" in result
        assert "overall_confidence" in result
        assert "key_insights" in result
        assert "risk_factors" in result
        assert "opportunities" in result

    # Test helper methods
    @pytest.mark.asyncio
    async def test_get_recent_predictions(self, seer):
        """Test getting recent predictions"""
        for i in range(3):
            await seer.execute(
                task="predict_trend",
                parameters={
                    "metric_name": f"metric_{i}",
                    "historical_values": [50 + i * 5, 55 + i * 5, 60 + i * 5],
                    "forecast_period_days": 30,
                    "forecast_type": "linear",
                },
            )

        predictions = await seer.get_recent_predictions(limit=10)
        assert len(predictions) >= 3

    @pytest.mark.asyncio
    async def test_get_recent_intelligence(self, seer):
        """Test getting recent intelligence"""
        for i in range(3):
            await seer.execute(
                task="gather_intelligence",
                parameters={
                    "intelligence_type": "market_trend",
                    "title": f"Intelligence {i}",
                    "summary": f"Summary {i}",
                    "source": "analysis",
                    "key_insights": [f"Insight {i}"],
                },
            )

        intel = await seer.get_recent_intelligence(limit=10)
        assert len(intel) >= 3

    @pytest.mark.asyncio
    async def test_performance_summary(self, seer):
        """Test performance summary generation"""
        summary = await seer.get_performance_summary()
        assert isinstance(summary, dict)
        assert "predictions_made" in summary
        assert "intelligence_gathered" in summary
        assert "recommendations_generated" in summary


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestSeerLordPerformance:
    """Performance tests for Seer Lord"""

    @pytest.fixture
    def seer(self):
        """Create Seer Lord instance"""
        lord = SeerLord()
        return lord

    @pytest.mark.asyncio
    async def test_predict_trend_performance(self, seer):
        """Test trend prediction response time < 100ms"""
        import time

        start_time = time.time()
        await seer.execute(
            task="predict_trend",
            parameters={
                "metric_name": "perf_metric",
                "historical_values": [50, 55, 60, 65, 70],
                "forecast_period_days": 30,
                "forecast_type": "linear",
            },
        )
        elapsed = time.time() - start_time

        assert elapsed < 0.1, f"Trend prediction took {elapsed}s, expected < 0.1s"

    @pytest.mark.asyncio
    async def test_gather_intelligence_performance(self, seer):
        """Test intelligence gathering response time < 100ms"""
        import time

        start_time = time.time()
        await seer.execute(
            task="gather_intelligence",
            parameters={
                "intelligence_type": "market_trend",
                "title": "Performance Test",
                "summary": "Testing",
                "source": "test",
                "key_insights": ["Test"],
            },
        )
        elapsed = time.time() - start_time

        assert elapsed < 0.1, f"Intelligence gathering took {elapsed}s, expected < 0.1s"

    @pytest.mark.asyncio
    async def test_analyze_performance_performance(self, seer):
        """Test performance analysis response time < 100ms"""
        import time

        start_time = time.time()
        await seer.execute(
            task="analyze_performance",
            parameters={
                "scope": "campaign",
                "scope_id": "perf_001",
                "metrics": {"m1": 75, "m2": 80},
            },
        )
        elapsed = time.time() - start_time

        assert elapsed < 0.1, f"Performance analysis took {elapsed}s, expected < 0.1s"

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, seer):
        """Test concurrent operations"""
        import time

        async def mixed_operations():
            tasks = [
                seer.execute(
                    task="predict_trend",
                    parameters={
                        "metric_name": f"m_{i}",
                        "historical_values": [50 + i, 55 + i, 60 + i],
                        "forecast_period_days": 30,
                        "forecast_type": "linear",
                    },
                )
                for i in range(5)
            ]
            return await asyncio.gather(*tasks)

        start_time = time.time()
        results = await mixed_operations()
        elapsed = time.time() - start_time

        assert len(results) == 5
        assert elapsed < 1.0  # 5 concurrent should complete in < 1s


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestSeerLordErrorHandling:
    """Error handling tests"""

    @pytest.fixture
    def seer(self):
        """Create Seer Lord instance"""
        lord = SeerLord()
        return lord

    @pytest.mark.asyncio
    async def test_invalid_task(self, seer):
        """Test handling of invalid task"""
        with pytest.raises(ValueError):
            await seer.execute(
                task="invalid_task",
                parameters={},
            )

    @pytest.mark.asyncio
    async def test_missing_parameters(self, seer):
        """Test handling of missing parameters"""
        with pytest.raises(Exception):
            await seer.execute(
                task="predict_trend",
                parameters={"metric_name": "test"},
            )

    @pytest.mark.asyncio
    async def test_invalid_forecast_type(self, seer):
        """Test handling of invalid forecast type"""
        # Should handle gracefully, falling back to default
        result = await seer.execute(
            task="predict_trend",
            parameters={
                "metric_name": "test",
                "historical_values": [50, 55, 60],
                "forecast_period_days": 30,
                "forecast_type": "invalid_type",
            },
        )
        # Should still succeed, using a default type
        assert "prediction_id" in result


# ============================================================================
# E2E WORKFLOW TESTS
# ============================================================================

class TestSeerLordE2EWorkflows:
    """End-to-end workflow tests"""

    @pytest.fixture
    def seer(self):
        """Create Seer Lord instance"""
        lord = SeerLord()
        return lord

    @pytest.mark.asyncio
    async def test_complete_forecast_workflow(self, seer):
        """Test complete forecasting workflow"""
        # 1. Gather intelligence
        intel_result = await seer.execute(
            task="gather_intelligence",
            parameters={
                "intelligence_type": "market_trend",
                "title": "Market Analysis",
                "summary": "Growing market",
                "source": "analysis",
                "key_insights": ["Growing market", "New opportunities"],
            },
        )
        assert "intelligence_id" in intel_result

        # 2. Predict trends
        trend_result = await seer.execute(
            task="predict_trend",
            parameters={
                "metric_name": "market_size",
                "historical_values": [100, 110, 120, 130, 140, 150],
                "forecast_period_days": 30,
                "forecast_type": "linear",
            },
        )
        assert "prediction_id" in trend_result

        # 3. Analyze performance
        perf_result = await seer.execute(
            task="analyze_performance",
            parameters={
                "scope": "campaign",
                "scope_id": "camp_001",
                "metrics": {"engagement": 85, "reach": 90, "conversion": 80},
            },
        )
        assert "analysis_id" in perf_result

        # 4. Generate recommendation
        rec_result = await seer.execute(
            task="generate_recommendation",
            parameters={
                "title": "Scale Investment",
                "description": "Based on positive market trends",
                "priority": "high",
                "supporting_insights": ["Growing market", "High engagement"],
                "required_resources": {"budget": 50000},
            },
        )
        assert "recommendation_id" in rec_result

        # 5. Generate forecast report
        report_result = await seer.execute(
            task="get_forecast_report",
            parameters={
                "title": "Q1 Market Forecast",
                "forecast_period_days": 90,
                "include_predictions": True,
                "include_intelligence": True,
            },
        )
        assert "report_id" in report_result

    @pytest.mark.asyncio
    async def test_trend_analysis_workflow(self, seer):
        """Test trend analysis workflow"""
        # Create multiple trend predictions
        metrics = ["sales", "growth", "engagement"]
        prediction_ids = []

        for metric in metrics:
            result = await seer.execute(
                task="predict_trend",
                parameters={
                    "metric_name": metric,
                    "historical_values": [100 + i * 10 for i in range(5)],
                    "forecast_period_days": 30,
                    "forecast_type": "linear",
                },
            )
            prediction_ids.append(result["prediction_id"])

        # Get all predictions
        predictions = await seer.get_recent_predictions(limit=10)
        assert len(predictions) >= len(metrics)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
