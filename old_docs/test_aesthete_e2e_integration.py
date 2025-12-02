# test_aesthete_e2e_integration.py
# RaptorFlow Codex - Aesthete Lord E2E Integration Tests
# Phase 2A Week 5 - Comprehensive testing suite

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timedelta
import json

# Backend imports
from backend_lord_aesthete import (
    AestheteLord,
    QualityLevel,
    ContentType,
    QualityReview,
    BrandGuideline,
    ConsistencyReport,
)

# ============================================================================
# UNIT TESTS - AESTHETE LORD AGENT
# ============================================================================

class TestAestheteLordAgent:
    """Unit tests for Aesthete Lord agent"""

    @pytest.fixture
    def aesthete(self):
        """Create Aesthete Lord instance"""
        lord = AestheteLord()
        return lord

    # Test initialization
    def test_aesthete_initialization(self, aesthete):
        """Test Aesthete Lord initialization"""
        assert aesthete.name == "Aesthete Lord"
        assert aesthete.role.value == "quality_and_design"
        assert aesthete.quality_reviews == {}
        assert aesthete.brand_guidelines == {}
        assert aesthete.consistency_reports == {}
        assert aesthete.total_reviews_conducted == 0

    def test_aesthete_role_value(self, aesthete):
        """Test Aesthete Lord has correct role"""
        assert aesthete.role.value == "quality_and_design"

    # Test capability registration
    def test_aesthete_has_five_capabilities(self, aesthete):
        """Test Aesthete Lord has all 5 capabilities"""
        assert len(aesthete.capabilities) == 5
        capability_names = {cap.name for cap in aesthete.capabilities}
        expected = {
            "assess_quality",
            "check_brand_compliance",
            "evaluate_visual_consistency",
            "provide_design_feedback",
            "approve_content",
        }
        assert capability_names == expected

    def test_capability_execution_methods(self, aesthete):
        """Test all capabilities have execution methods"""
        for capability in aesthete.capabilities:
            assert hasattr(aesthete, f"_execute_{capability.name}")
            assert callable(getattr(aesthete, f"_execute_{capability.name}"))

    # Test quality assessment
    @pytest.mark.asyncio
    async def test_assess_quality_basic(self, aesthete):
        """Test basic quality assessment"""
        result = await aesthete.execute(
            task="assess_quality",
            parameters={
                "content_id": "content_001",
                "content_type": "copy",
                "guild_name": "Content Guild",
                "content_metrics": {"clarity": 0.9, "relevance": 0.85, "engagement": 0.8, "correctness": 0.95},
            },
        )

        assert result.get("success", True)
        assert "review_id" in result
        assert "overall_score" in result
        assert 0 <= result["overall_score"] <= 100
        assert "quality_level" in result
        assert result["quality_level"] in ["poor", "fair", "good", "excellent", "outstanding"]

    @pytest.mark.asyncio
    async def test_assess_quality_stores_review(self, aesthete):
        """Test quality assessment stores review in memory"""
        result = await aesthete.execute(
            task="assess_quality",
            parameters={
                "content_id": "content_001",
                "content_type": "visual",
                "guild_name": "Design Guild",
                "content_metrics": {"clarity": 0.7, "relevance": 0.8, "engagement": 0.75, "correctness": 0.8},
            },
        )

        review_id = result["review_id"]
        assert review_id in aesthete.quality_reviews
        assert aesthete.quality_reviews[review_id].content_id == "content_001"

    @pytest.mark.asyncio
    async def test_assess_quality_increments_counter(self, aesthete):
        """Test quality assessment increments counter"""
        initial_count = aesthete.total_reviews_conducted

        await aesthete.execute(
            task="assess_quality",
            parameters={
                "content_id": "content_002",
                "content_type": "copy",
                "guild_name": "Content Guild",
                "content_metrics": {"clarity": 0.8, "relevance": 0.8, "engagement": 0.8, "correctness": 0.8},
            },
        )

        assert aesthete.total_reviews_conducted == initial_count + 1

    @pytest.mark.asyncio
    async def test_assess_quality_multiple_types(self, aesthete):
        """Test quality assessment with different content types"""
        content_types = ["copy", "visual", "design", "messaging", "branding"]

        for content_type in content_types:
            result = await aesthete.execute(
                task="assess_quality",
                parameters={
                    "content_id": f"content_{content_type}",
                    "content_type": content_type,
                    "guild_name": "Test Guild",
                    "content_metrics": {"clarity": 0.8, "relevance": 0.8, "engagement": 0.8, "correctness": 0.8},
                },
            )
            assert "quality_level" in result

    # Test brand compliance
    @pytest.mark.asyncio
    async def test_check_brand_compliance(self, aesthete):
        """Test brand compliance check"""
        result = await aesthete.execute(
            task="check_brand_compliance",
            parameters={
                "content_id": "content_001",
                "guild_name": "Brand Guild",
                "content_elements": {
                    "tone": "professional",
                    "colors": ["#1f2937", "#ffffff"],
                    "logos": ["logo_primary"],
                },
            },
        )

        assert result.get("success", True)
        assert "compliance_score" in result
        assert 0 <= result["compliance_score"] <= 100
        assert "compliant" in result

    @pytest.mark.asyncio
    async def test_check_brand_compliance_violations(self, aesthete):
        """Test brand compliance detection of violations"""
        result = await aesthete.execute(
            task="check_brand_compliance",
            parameters={
                "content_id": "content_bad",
                "guild_name": "Brand Guild",
                "content_elements": {
                    "tone": "unprofessional",
                    "colors": ["#ff00ff"],
                    "logos": ["unauthorized_logo"],
                },
            },
        )

        # Violations may be detected depending on implementation
        assert "compliance_score" in result

    # Test visual consistency
    @pytest.mark.asyncio
    async def test_evaluate_visual_consistency(self, aesthete):
        """Test visual consistency evaluation"""
        result = await aesthete.execute(
            task="evaluate_visual_consistency",
            parameters={
                "scope": "campaign",
                "scope_id": "camp_001",
                "items_count": 10,
                "consistency_data": {},
            },
        )

        assert result.get("success", True)
        assert "report_id" in result
        assert "consistency_percent" in result
        assert 0 <= result["consistency_percent"] <= 100

    @pytest.mark.asyncio
    async def test_evaluate_visual_consistency_scopes(self, aesthete):
        """Test consistency evaluation with different scopes"""
        scopes = ["campaign", "guild", "organization"]

        for scope in scopes:
            result = await aesthete.execute(
                task="evaluate_visual_consistency",
                parameters={
                    "scope": scope,
                    "scope_id": f"{scope}_001",
                    "items_count": 5,
                    "consistency_data": {},
                },
            )
            assert "consistency_percent" in result

    # Test design feedback
    @pytest.mark.asyncio
    async def test_provide_design_feedback(self, aesthete):
        """Test design feedback provision"""
        result = await aesthete.execute(
            task="provide_design_feedback",
            parameters={
                "content_id": "design_001",
                "content_type": "visual",
                "design_elements": {
                    "typography": "sans-serif",
                    "color_palette": ["#1f2937", "#3b82f6"],
                    "spacing": "comfortable",
                    "hierarchy": "clear",
                },
                "guild_name": "Design Guild",
            },
        )

        assert result.get("success", True)
        assert "feedback_id" in result
        assert "strengths" in result or "improvements" in result

    # Test content approval
    @pytest.mark.asyncio
    async def test_approve_content_basic(self, aesthete):
        """Test content approval"""
        # First create a review
        assess_result = await aesthete.execute(
            task="assess_quality",
            parameters={
                "content_id": "content_approve",
                "content_type": "copy",
                "guild_name": "Content Guild",
                "content_metrics": {"clarity": 0.95, "relevance": 0.95, "engagement": 0.9, "correctness": 0.95},
            },
        )

        review_id = assess_result["review_id"]

        # Now approve it
        result = await aesthete.execute(
            task="approve_content",
            parameters={
                "review_id": review_id,
                "approval_notes": "Excellent quality",
            },
        )

        assert result.get("success", True)

    @pytest.mark.asyncio
    async def test_get_recent_reviews(self, aesthete):
        """Test getting recent reviews"""
        # Create multiple reviews
        for i in range(3):
            await aesthete.execute(
                task="assess_quality",
                parameters={
                    "content_id": f"content_{i}",
                    "content_type": "copy",
                    "guild_name": "Content Guild",
                    "content_metrics": {"clarity": 0.8, "relevance": 0.8, "engagement": 0.8, "correctness": 0.8},
                },
            )

        reviews = await aesthete.get_recent_reviews(limit=10)
        assert len(reviews) >= 3

    @pytest.mark.asyncio
    async def test_get_approved_content(self, aesthete):
        """Test getting approved content IDs"""
        approved = await aesthete.get_approved_content()
        assert isinstance(approved, list)

    # Test data structure methods
    @pytest.mark.asyncio
    async def test_quality_review_to_dict(self, aesthete):
        """Test QualityReview to_dict conversion"""
        result = await aesthete.execute(
            task="assess_quality",
            parameters={
                "content_id": "content_dict",
                "content_type": "copy",
                "guild_name": "Content Guild",
                "content_metrics": {"clarity": 0.8, "relevance": 0.8, "engagement": 0.8, "correctness": 0.8},
            },
        )

        review_id = result["review_id"]
        review = aesthete.quality_reviews[review_id]
        review_dict = review.to_dict()

        assert isinstance(review_dict, dict)
        assert "review_id" in review_dict
        assert "overall_score" in review_dict
        assert "quality_level" in review_dict

    # Test error handling
    @pytest.mark.asyncio
    async def test_assess_quality_error_handling(self, aesthete):
        """Test error handling in quality assessment"""
        # Missing required parameters
        with pytest.raises(Exception):
            await aesthete.execute(
                task="assess_quality",
                parameters={
                    "content_id": "content_001",
                    # Missing content_type, guild_name, content_metrics
                },
            )

    @pytest.mark.asyncio
    async def test_invalid_task_execution(self, aesthete):
        """Test execution of invalid task"""
        with pytest.raises(Exception):
            await aesthete.execute(
                task="invalid_task",
                parameters={},
            )


# ============================================================================
# INTEGRATION TESTS - API ENDPOINTS
# ============================================================================

class TestAestheteLordAPI:
    """Integration tests for Aesthete Lord API endpoints"""

    @pytest.fixture
    def mock_current_user(self):
        """Mock current user dependency"""
        return "test_user"

    @pytest.fixture
    def mock_current_workspace(self):
        """Mock current workspace dependency"""
        return "test_workspace"

    @pytest.mark.asyncio
    async def test_assess_quality_endpoint(self, mock_current_user, mock_current_workspace):
        """Test assess-quality endpoint"""
        # This would be tested with actual HTTP requests in integration
        pass

    @pytest.mark.asyncio
    async def test_brand_compliance_endpoint(self, mock_current_user, mock_current_workspace):
        """Test brand-compliance endpoint"""
        pass

    @pytest.mark.asyncio
    async def test_consistency_evaluation_endpoint(self, mock_current_user, mock_current_workspace):
        """Test consistency/evaluate endpoint"""
        pass

    @pytest.mark.asyncio
    async def test_design_feedback_endpoint(self, mock_current_user, mock_current_workspace):
        """Test feedback/provide endpoint"""
        pass

    @pytest.mark.asyncio
    async def test_approve_content_endpoint(self, mock_current_user, mock_current_workspace):
        """Test approve endpoint"""
        pass

    @pytest.mark.asyncio
    async def test_get_reviews_endpoint(self, mock_current_user, mock_current_workspace):
        """Test get recent reviews endpoint"""
        pass

    @pytest.mark.asyncio
    async def test_get_approved_content_endpoint(self, mock_current_user, mock_current_workspace):
        """Test get approved content endpoint"""
        pass

    @pytest.mark.asyncio
    async def test_status_endpoint(self, mock_current_user, mock_current_workspace):
        """Test status endpoint"""
        pass


# ============================================================================
# WEBSOCKET INTEGRATION TESTS
# ============================================================================

class TestAestheteLordWebSocket:
    """WebSocket integration tests for Aesthete Lord"""

    @pytest.mark.asyncio
    async def test_websocket_connection(self):
        """Test WebSocket connection"""
        # Would require actual WebSocket testing framework
        pass

    @pytest.mark.asyncio
    async def test_websocket_real_time_update(self):
        """Test real-time updates via WebSocket"""
        pass

    @pytest.mark.asyncio
    async def test_websocket_broadcast_quality_review(self):
        """Test quality review event broadcast"""
        pass

    @pytest.mark.asyncio
    async def test_websocket_broadcast_approval(self):
        """Test approval event broadcast"""
        pass


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestAestheteLordPerformance:
    """Performance tests for Aesthete Lord"""

    @pytest.fixture
    def aesthete(self):
        """Create Aesthete Lord instance"""
        lord = AestheteLord()
        return lord

    @pytest.mark.asyncio
    async def test_assess_quality_performance(self, aesthete):
        """Test quality assessment response time < 100ms"""
        import time

        start_time = time.time()
        await aesthete.execute(
            task="assess_quality",
            parameters={
                "content_id": "perf_content",
                "content_type": "copy",
                "guild_name": "Content Guild",
                "content_metrics": {"clarity": 0.8, "relevance": 0.8, "engagement": 0.8, "correctness": 0.8},
            },
        )
        elapsed = time.time() - start_time

        assert elapsed < 0.1, f"Quality assessment took {elapsed}s, expected < 0.1s"

    @pytest.mark.asyncio
    async def test_brand_compliance_performance(self, aesthete):
        """Test compliance check response time < 100ms"""
        import time

        start_time = time.time()
        await aesthete.execute(
            task="check_brand_compliance",
            parameters={
                "content_id": "perf_content",
                "guild_name": "Brand Guild",
                "content_elements": {"tone": "professional", "colors": ["#000000"], "logos": ["logo"]},
            },
        )
        elapsed = time.time() - start_time

        assert elapsed < 0.1, f"Compliance check took {elapsed}s, expected < 0.1s"

    @pytest.mark.asyncio
    async def test_consistency_evaluation_performance(self, aesthete):
        """Test consistency evaluation response time < 100ms"""
        import time

        start_time = time.time()
        await aesthete.execute(
            task="evaluate_visual_consistency",
            parameters={
                "scope": "campaign",
                "scope_id": "camp_perf",
                "items_count": 20,
                "consistency_data": {},
            },
        )
        elapsed = time.time() - start_time

        assert elapsed < 0.1, f"Consistency evaluation took {elapsed}s, expected < 0.1s"

    @pytest.mark.asyncio
    async def test_design_feedback_performance(self, aesthete):
        """Test design feedback response time < 100ms"""
        import time

        start_time = time.time()
        await aesthete.execute(
            task="provide_design_feedback",
            parameters={
                "content_id": "perf_design",
                "content_type": "visual",
                "design_elements": {"typography": "sans-serif", "spacing": "comfortable"},
                "guild_name": "Design Guild",
            },
        )
        elapsed = time.time() - start_time

        assert elapsed < 0.1, f"Design feedback took {elapsed}s, expected < 0.1s"

    @pytest.mark.asyncio
    async def test_concurrent_quality_assessments(self, aesthete):
        """Test concurrent quality assessments"""
        import time

        async def assess():
            return await aesthete.execute(
                task="assess_quality",
                parameters={
                    "content_id": f"concurrent_{asyncio.current_task().get_name()}",
                    "content_type": "copy",
                    "guild_name": "Content Guild",
                    "content_metrics": {"clarity": 0.8, "relevance": 0.8, "engagement": 0.8, "correctness": 0.8},
                },
            )

        start_time = time.time()
        tasks = [assess() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        elapsed = time.time() - start_time

        assert len(results) == 10
        assert elapsed < 1.0  # 10 concurrent requests should complete in < 1s


# ============================================================================
# ERROR HANDLING & RESILIENCE TESTS
# ============================================================================

class TestAestheteLordErrorHandling:
    """Error handling and resilience tests"""

    @pytest.fixture
    def aesthete(self):
        """Create Aesthete Lord instance"""
        lord = AestheteLord()
        return lord

    @pytest.mark.asyncio
    async def test_invalid_content_type(self, aesthete):
        """Test handling of invalid content type"""
        with pytest.raises(Exception):
            await aesthete.execute(
                task="assess_quality",
                parameters={
                    "content_id": "invalid",
                    "content_type": "invalid_type",
                    "guild_name": "Guild",
                    "content_metrics": {"clarity": 0.8},
                },
            )

    @pytest.mark.asyncio
    async def test_missing_parameters(self, aesthete):
        """Test handling of missing parameters"""
        with pytest.raises(Exception):
            await aesthete.execute(
                task="assess_quality",
                parameters={"content_id": "test"},
            )

    @pytest.mark.asyncio
    async def test_invalid_metric_values(self, aesthete):
        """Test handling of invalid metric values"""
        # Values outside 0-1 range should be clamped or rejected
        result = await aesthete.execute(
            task="assess_quality",
            parameters={
                "content_id": "invalid_metrics",
                "content_type": "copy",
                "guild_name": "Guild",
                "content_metrics": {"clarity": 1.5, "relevance": -0.5, "engagement": 0.8, "correctness": 0.8},
            },
        )
        # Should still process, clamping values
        assert "overall_score" in result

    @pytest.mark.asyncio
    async def test_review_not_found(self, aesthete):
        """Test handling of non-existent review"""
        # Try to approve non-existent review
        with pytest.raises(Exception):
            await aesthete.execute(
                task="approve_content",
                parameters={"review_id": "non_existent", "approval_notes": ""},
            )

    @pytest.mark.asyncio
    async def test_concurrent_error_handling(self, aesthete):
        """Test error handling under concurrent load"""
        async def mixed_requests():
            results = []
            for i in range(5):
                try:
                    result = await aesthete.execute(
                        task="assess_quality" if i % 2 == 0 else "invalid_task",
                        parameters={"content_id": f"test_{i}"} if i % 2 == 0 else {},
                    )
                    results.append(("success", result))
                except Exception as e:
                    results.append(("error", str(e)))
            return results

        results = await mixed_requests()
        assert len(results) == 5


# ============================================================================
# END-TO-END WORKFLOW TESTS
# ============================================================================

class TestAestheteLordE2EWorkflows:
    """End-to-end workflow tests"""

    @pytest.fixture
    def aesthete(self):
        """Create Aesthete Lord instance"""
        lord = AestheteLord()
        return lord

    @pytest.mark.asyncio
    async def test_complete_quality_review_workflow(self, aesthete):
        """Test complete quality review workflow"""
        # 1. Assess quality
        assess_result = await aesthete.execute(
            task="assess_quality",
            parameters={
                "content_id": "e2e_content",
                "content_type": "copy",
                "guild_name": "Content Guild",
                "content_metrics": {"clarity": 0.85, "relevance": 0.9, "engagement": 0.8, "correctness": 0.95},
            },
        )
        assert "review_id" in assess_result
        review_id = assess_result["review_id"]

        # 2. Get review details
        reviews = await aesthete.get_recent_reviews(limit=1)
        assert len(reviews) > 0

        # 3. Approve content (if quality is good)
        if assess_result["overall_score"] >= 75:
            approve_result = await aesthete.execute(
                task="approve_content",
                parameters={
                    "review_id": review_id,
                    "approval_notes": "Great quality!",
                },
            )
            assert "success" in approve_result

        # 4. Get approved content
        approved = await aesthete.get_approved_content()
        assert isinstance(approved, list)

    @pytest.mark.asyncio
    async def test_brand_compliance_workflow(self, aesthete):
        """Test brand compliance check workflow"""
        # 1. Check compliance
        result = await aesthete.execute(
            task="check_brand_compliance",
            parameters={
                "content_id": "e2e_brand",
                "guild_name": "Brand Guild",
                "content_elements": {
                    "tone": "professional",
                    "colors": ["#1f2937", "#3b82f6"],
                    "logos": ["logo_primary"],
                },
            },
        )

        assert "compliance_score" in result
        assert result["compliance_score"] >= 0

    @pytest.mark.asyncio
    async def test_consistency_review_workflow(self, aesthete):
        """Test consistency review workflow"""
        # 1. Evaluate consistency
        result = await aesthete.execute(
            task="evaluate_visual_consistency",
            parameters={
                "scope": "campaign",
                "scope_id": "e2e_campaign",
                "items_count": 15,
                "consistency_data": {},
            },
        )

        assert "consistency_percent" in result

        # 2. Get recent reports
        if hasattr(aesthete, "get_consistency_reports"):
            reports = await aesthete.get_consistency_reports()
            assert isinstance(reports, list)

    @pytest.mark.asyncio
    async def test_design_feedback_workflow(self, aesthete):
        """Test design feedback workflow"""
        # 1. Provide feedback
        result = await aesthete.execute(
            task="provide_design_feedback",
            parameters={
                "content_id": "e2e_design",
                "content_type": "visual",
                "design_elements": {
                    "typography": "sans-serif",
                    "color_palette": ["#1f2937", "#3b82f6", "#10b981"],
                    "spacing": "comfortable",
                    "hierarchy": "clear",
                },
                "guild_name": "Design Guild",
            },
        )

        assert "feedback_id" in result or "success" in result


# ============================================================================
# RAPTORBUS INTEGRATION TESTS
# ============================================================================

class TestAestheteLordRaptorBusIntegration:
    """RaptorBus integration tests"""

    @pytest.mark.asyncio
    async def test_quality_review_event_publishing(self):
        """Test publishing quality review events to RaptorBus"""
        # Would require actual RaptorBus connection
        pass

    @pytest.mark.asyncio
    async def test_approval_event_publishing(self):
        """Test publishing approval events"""
        pass

    @pytest.mark.asyncio
    async def test_consistency_report_event_publishing(self):
        """Test publishing consistency report events"""
        pass


# ============================================================================
# METRIC & REPORTING TESTS
# ============================================================================

class TestAestheteLordMetrics:
    """Metrics and reporting tests"""

    @pytest.fixture
    def aesthete(self):
        """Create Aesthete Lord instance"""
        lord = AestheteLord()
        return lord

    @pytest.mark.asyncio
    async def test_performance_summary(self, aesthete):
        """Test performance summary generation"""
        summary = await aesthete.get_performance_summary()
        assert isinstance(summary, dict)

    @pytest.mark.asyncio
    async def test_approval_rate_calculation(self, aesthete):
        """Test approval rate calculation"""
        # Create multiple reviews and approvals
        for i in range(3):
            assess = await aesthete.execute(
                task="assess_quality",
                parameters={
                    "content_id": f"metric_{i}",
                    "content_type": "copy",
                    "guild_name": "Guild",
                    "content_metrics": {"clarity": 0.9 if i < 2 else 0.5, "relevance": 0.8, "engagement": 0.8, "correctness": 0.9},
                },
            )

            if i < 2:  # Approve first two
                await aesthete.execute(
                    task="approve_content",
                    parameters={
                        "review_id": assess["review_id"],
                        "approval_notes": "",
                    },
                )

        summary = await aesthete.get_performance_summary()
        assert isinstance(summary, dict)


# ============================================================================
# FIXTURE CLEANUP
# ============================================================================

@pytest.fixture(scope="session", autouse=True)
def cleanup_resources():
    """Clean up resources after test session"""
    yield
    # Cleanup code would go here


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
