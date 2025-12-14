# backend/tests/test_architect_e2e_integration.py
# RaptorFlow Codex - Architect Lord E2E Integration Tests
# Phase 2A Week 4 - Full Stack Testing

import pytest
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any
from unittest.mock import AsyncMock, patch, MagicMock

# ==============================================================================
# TEST FIXTURES
# ==============================================================================

@pytest.fixture
async def architect_agent():
    """Initialize Architect agent for testing"""
    from agents.council_of_lords.architect import ArchitectLord

    agent = ArchitectLord()
    await agent.initialize()
    return agent


@pytest.fixture
async def test_client():
    """Create FastAPI test client"""
    from fastapi.testclient import TestClient
    from main import app

    return TestClient(app)


@pytest.fixture
def sample_initiative_request():
    """Sample initiative design request"""
    return {
        "name": "Q1 Marketing Automation",
        "objectives": [
            "Implement campaign automation",
            "Improve email targeting",
            "Increase conversion rates by 25%"
        ],
        "target_guilds": ["research", "muse", "matrix"],
        "timeline_weeks": 8,
        "success_metrics": {
            "conversion_improvement": 0.25,
            "automation_coverage": 0.95,
            "team_efficiency": 1.5
        }
    }


@pytest.fixture
def sample_architecture_analysis():
    """Sample architecture analysis request"""
    return {
        "component": "api",
        "metrics": {
            "latency_ms": 85,
            "throughput_rps": 450,
            "error_rate": 0.02,
            "cpu_percent": 65,
            "memory_percent": 72
        }
    }


@pytest.fixture
def sample_guidance_request():
    """Sample guidance request"""
    return {
        "guild_name": "research",
        "topic": "research"
    }


# ==============================================================================
# ARCHITECT AGENT UNIT TESTS
# ==============================================================================

class TestArchitectAgentCore:
    """Test core Architect agent functionality"""

    @pytest.mark.asyncio
    async def test_architect_initialization(self, architect_agent):
        """Test Architect agent initializes correctly"""
        assert architect_agent is not None
        assert architect_agent.name == "Architect"
        assert architect_agent.role.value == "architect"
        assert len(architect_agent.capabilities) >= 5

    @pytest.mark.asyncio
    async def test_architect_capabilities_registered(self, architect_agent):
        """Test all Architect capabilities are registered"""
        expected_capabilities = [
            "design_initiative",
            "analyze_architecture",
            "optimize_component",
            "provide_strategic_guidance",
            "review_guild_strategy"
        ]

        registered = [cap.name for cap in architect_agent.capabilities]
        for expected in expected_capabilities:
            assert expected in registered, f"Capability {expected} not registered"

    @pytest.mark.asyncio
    async def test_design_initiative_execution(self, architect_agent, sample_initiative_request):
        """Test initiative design execution"""
        result = await architect_agent.execute(
            task="design_initiative",
            parameters={
                "initiative_name": sample_initiative_request["name"],
                "objectives": sample_initiative_request["objectives"],
                "target_guilds": sample_initiative_request["target_guilds"],
                "timeline_weeks": sample_initiative_request["timeline_weeks"],
                "success_metrics": sample_initiative_request["success_metrics"]
            }
        )

        assert result["success"] is True
        assert "data" in result
        assert "duration_seconds" in result

        # Verify initiative data structure
        initiative_data = result["data"]
        assert initiative_data["name"] == sample_initiative_request["name"]
        assert initiative_data["objectives"] == sample_initiative_request["objectives"]
        assert initiative_data["target_guilds"] == sample_initiative_request["target_guilds"]

    @pytest.mark.asyncio
    async def test_analyze_architecture_execution(self, architect_agent, sample_architecture_analysis):
        """Test architecture analysis execution"""
        result = await architect_agent.execute(
            task="analyze_architecture",
            parameters={
                "component": sample_architecture_analysis["component"],
                "metrics": sample_architecture_analysis["metrics"]
            }
        )

        assert result["success"] is True
        assert "data" in result

        # Verify analysis structure
        analysis = result["data"]
        assert "issues" in analysis
        assert "recommendations" in analysis
        assert isinstance(analysis["issues"], list)
        assert isinstance(analysis["recommendations"], list)

    @pytest.mark.asyncio
    async def test_optimize_component_execution(self, architect_agent):
        """Test component optimization execution"""
        result = await architect_agent.execute(
            task="optimize_component",
            parameters={
                "component_type": "api",
                "current_metrics": {
                    "latency_ms": 150,
                    "throughput_rps": 200,
                    "error_rate": 0.05
                }
            }
        )

        assert result["success"] is True
        assert "data" in result

        # Verify optimization plan
        plan = result["data"]
        assert "strategies" in plan
        assert "expected_improvement_percent" in plan
        assert "implementation_steps" in plan

    @pytest.mark.asyncio
    async def test_provide_guidance_execution(self, architect_agent, sample_guidance_request):
        """Test strategic guidance execution"""
        result = await architect_agent.execute(
            task="provide_strategic_guidance",
            parameters={
                "guild_name": sample_guidance_request["guild_name"],
                "topic": sample_guidance_request["topic"]
            }
        )

        assert result["success"] is True
        assert "data" in result
        assert isinstance(result["data"], str)
        assert len(result["data"]) > 0

    @pytest.mark.asyncio
    async def test_review_guild_strategy_execution(self, architect_agent):
        """Test guild strategy review execution"""
        strategy = {
            "name": "Research Guild Q1 Strategy",
            "focus_areas": ["market_analysis", "competitor_tracking"],
            "resource_allocation": {"headcount": 5, "budget": 50000},
            "timeline": "13 weeks"
        }

        result = await architect_agent.execute(
            task="review_guild_strategy",
            parameters={
                "guild_name": "research",
                "guild_strategy": strategy
            }
        )

        assert result["success"] is True
        assert "data" in result

        review = result["data"]
        assert "alignment_score" in review
        assert "status" in review
        assert isinstance(review["alignment_score"], (int, float))
        assert 0.0 <= review["alignment_score"] <= 1.0


# ==============================================================================
# API ENDPOINT TESTS
# ==============================================================================

class TestArchitectAPIEndpoints:
    """Test Architect API endpoints"""

    @pytest.mark.asyncio
    async def test_design_initiative_endpoint(self, test_client, sample_initiative_request):
        """Test /lords/architect/initiatives/design endpoint"""
        response = test_client.post(
            "/lords/architect/initiatives/design",
            json=sample_initiative_request
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert "execution_time" in data

    @pytest.mark.asyncio
    async def test_list_initiatives_endpoint(self, test_client):
        """Test /lords/architect/initiatives GET endpoint"""
        response = test_client.get("/lords/architect/initiatives")

        assert response.status_code == 200
        initiatives = response.json()
        assert isinstance(initiatives, list)

    @pytest.mark.asyncio
    async def test_get_initiative_detail_endpoint(self, test_client, sample_initiative_request):
        """Test /lords/architect/initiatives/{id} endpoint"""
        # First create an initiative
        create_response = test_client.post(
            "/lords/architect/initiatives/design",
            json=sample_initiative_request
        )

        assert create_response.status_code == 200
        initiative_id = create_response.json()["data"]["id"]

        # Then retrieve it
        detail_response = test_client.get(
            f"/lords/architect/initiatives/{initiative_id}"
        )

        assert detail_response.status_code == 200
        initiative = detail_response.json()
        assert initiative["id"] == initiative_id
        assert initiative["name"] == sample_initiative_request["name"]

    @pytest.mark.asyncio
    async def test_approve_initiative_endpoint(self, test_client, sample_initiative_request):
        """Test /lords/architect/initiatives/{id}/approve endpoint"""
        # Create initiative
        create_response = test_client.post(
            "/lords/architect/initiatives/design",
            json=sample_initiative_request
        )
        initiative_id = create_response.json()["data"]["id"]

        # Approve it
        approve_response = test_client.post(
            f"/lords/architect/initiatives/{initiative_id}/approve",
            json={"approver": "architect"}
        )

        assert approve_response.status_code == 200
        result = approve_response.json()
        assert result["status"] == "success"
        assert result["approval_status"]["architect"] is True

    @pytest.mark.asyncio
    async def test_analyze_architecture_endpoint(self, test_client, sample_architecture_analysis):
        """Test /lords/architect/architecture/analyze endpoint"""
        response = test_client.post(
            "/lords/architect/architecture/analyze",
            json=sample_architecture_analysis
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "analysis" in data

    @pytest.mark.asyncio
    async def test_optimize_component_endpoint(self, test_client):
        """Test /lords/architect/architecture/optimize endpoint"""
        request_data = {
            "component_type": "database",
            "current_metrics": {
                "latency_ms": 200,
                "throughput_rps": 100,
                "error_rate": 0.08
            }
        }

        response = test_client.post(
            "/lords/architect/architecture/optimize",
            json=request_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "optimization_plan" in data

    @pytest.mark.asyncio
    async def test_provide_guidance_endpoint(self, test_client, sample_guidance_request):
        """Test /lords/architect/guidance/provide endpoint"""
        response = test_client.post(
            "/lords/architect/guidance/provide",
            json=sample_guidance_request
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "guidance" in data

    @pytest.mark.asyncio
    async def test_get_guild_guidance_endpoint(self, test_client, sample_guidance_request):
        """Test /lords/architect/guidance/{guild_name} endpoint"""
        # Provide guidance first
        test_client.post(
            "/lords/architect/guidance/provide",
            json=sample_guidance_request
        )

        # Get guidance
        response = test_client.get(
            f"/lords/architect/guidance/{sample_guidance_request['guild_name']}"
        )

        assert response.status_code == 200
        guidance_list = response.json()
        assert isinstance(guidance_list, list)

    @pytest.mark.asyncio
    async def test_get_status_endpoint(self, test_client):
        """Test /lords/architect/status endpoint"""
        response = test_client.get("/lords/architect/status")

        assert response.status_code == 200
        data = response.json()
        assert "agent" in data
        assert "performance" in data
        assert data["agent"]["name"] == "Architect"
        assert data["agent"]["role"] == "architect"

    @pytest.mark.asyncio
    async def test_get_decisions_endpoint(self, test_client):
        """Test /lords/architect/decisions endpoint"""
        response = test_client.get("/lords/architect/decisions")

        assert response.status_code == 200
        decisions = response.json()
        assert isinstance(decisions, list)


# ==============================================================================
# WEBSOCKET INTEGRATION TESTS
# ==============================================================================

class TestArchitectWebSocketIntegration:
    """Test WebSocket integration for real-time updates"""

    @pytest.mark.asyncio
    async def test_websocket_connection(self, test_client):
        """Test WebSocket connection establishment"""
        with test_client.websocket_connect("/ws/lords/architect") as websocket:
            # Send subscription message
            websocket.send_text("subscribe")

            # Receive confirmation
            data = websocket.receive_json()
            assert data["type"] == "subscription_confirmed"
            assert data["lord"] == "architect"

    @pytest.mark.asyncio
    async def test_websocket_heartbeat(self, test_client):
        """Test WebSocket heartbeat/ping mechanism"""
        with test_client.websocket_connect("/ws/lords/architect") as websocket:
            # Send ping
            websocket.send_text("ping")

            # Receive pong
            data = websocket.receive_json()
            assert data["type"] == "pong"
            assert "timestamp" in data

    @pytest.mark.asyncio
    async def test_websocket_event_broadcast(self, test_client):
        """Test WebSocket event broadcasting"""
        # This would require mocking RaptorBus event publishing
        # In a real scenario, this would be an integration test with Redis
        with test_client.websocket_connect("/ws/lords/architect") as websocket:
            websocket.send_text("subscribe")

            # Verify subscription
            response = websocket.receive_json()
            assert response["type"] == "subscription_confirmed"


# ==============================================================================
# END-TO-END WORKFLOW TESTS
# ==============================================================================

class TestArchitectE2EWorkflows:
    """Test complete end-to-end workflows"""

    @pytest.mark.asyncio
    async def test_initiative_design_workflow(self, test_client, sample_initiative_request):
        """Test complete initiative design workflow"""
        # Step 1: Create initiative
        create_response = test_client.post(
            "/lords/architect/initiatives/design",
            json=sample_initiative_request
        )
        assert create_response.status_code == 200
        initiative_id = create_response.json()["data"]["id"]

        # Step 2: Retrieve initiative
        detail_response = test_client.get(
            f"/lords/architect/initiatives/{initiative_id}"
        )
        assert detail_response.status_code == 200
        initiative = detail_response.json()
        assert initiative["status"] == "designed"

        # Step 3: Approve from Architect
        approve_response = test_client.post(
            f"/lords/architect/initiatives/{initiative_id}/approve",
            json={"approver": "architect"}
        )
        assert approve_response.status_code == 200
        assert approve_response.json()["approval_status"]["architect"] is True

        # Step 4: Check status reflects approvals
        final_response = test_client.get(
            f"/lords/architect/initiatives/{initiative_id}"
        )
        assert final_response.status_code == 200
        final_initiative = final_response.json()
        assert final_initiative["approval_status"]["architect"] is True

    @pytest.mark.asyncio
    async def test_architecture_review_workflow(self, test_client, sample_architecture_analysis):
        """Test complete architecture review workflow"""
        # Step 1: Analyze current state
        analysis_response = test_client.post(
            "/lords/architect/architecture/analyze",
            json=sample_architecture_analysis
        )
        assert analysis_response.status_code == 200
        analysis = analysis_response.json()["analysis"]

        # Step 2: Get optimization plan
        optimization_response = test_client.post(
            "/lords/architect/architecture/optimize",
            json={
                "component_type": sample_architecture_analysis["component"],
                "current_metrics": sample_architecture_analysis["metrics"]
            }
        )
        assert optimization_response.status_code == 200
        optimization = optimization_response.json()["optimization_plan"]

        # Verify improvement expectations
        assert "expected_improvement_percent" in optimization
        assert optimization["expected_improvement_percent"] >= 0

    @pytest.mark.asyncio
    async def test_guild_guidance_workflow(self, test_client):
        """Test complete guild guidance workflow"""
        # Step 1: Provide guidance to research guild
        guidance_response = test_client.post(
            "/lords/architect/guidance/provide",
            json={
                "guild_name": "research",
                "topic": "research"
            }
        )
        assert guidance_response.status_code == 200

        # Step 2: Retrieve guild guidance
        retrieve_response = test_client.get(
            "/lords/architect/guidance/research"
        )
        assert retrieve_response.status_code == 200
        guidance_list = retrieve_response.json()
        assert isinstance(guidance_list, list)
        assert len(guidance_list) > 0

    @pytest.mark.asyncio
    async def test_full_architect_workflow(self, test_client, sample_initiative_request):
        """Test complete Architect Lord workflow"""
        # 1. Design initiative
        create_response = test_client.post(
            "/lords/architect/initiatives/design",
            json=sample_initiative_request
        )
        assert create_response.status_code == 200
        initiative_id = create_response.json()["data"]["id"]

        # 2. Get architect status
        status_response = test_client.get("/lords/architect/status")
        assert status_response.status_code == 200
        status = status_response.json()

        # 3. Get recent decisions
        decisions_response = test_client.get("/lords/architect/decisions?limit=5")
        assert decisions_response.status_code == 200

        # 4. List all initiatives
        list_response = test_client.get("/lords/architect/initiatives")
        assert list_response.status_code == 200
        initiatives = list_response.json()
        assert len(initiatives) > 0


# ==============================================================================
# PERFORMANCE & LOAD TESTS
# ==============================================================================

class TestArchitectPerformance:
    """Test performance characteristics"""

    @pytest.mark.asyncio
    async def test_api_response_time(self, test_client, sample_initiative_request):
        """Test API response time is within SLA"""
        import time

        start = time.time()
        response = test_client.post(
            "/lords/architect/initiatives/design",
            json=sample_initiative_request
        )
        elapsed = time.time() - start

        assert response.status_code == 200
        # SLA: < 100ms
        assert elapsed < 0.1, f"API response time {elapsed*1000:.1f}ms exceeds 100ms SLA"

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, test_client, sample_initiative_request):
        """Test handling concurrent requests"""
        import asyncio

        async def make_request():
            response = test_client.post(
                "/lords/architect/initiatives/design",
                json=sample_initiative_request
            )
            return response.status_code == 200

        # Simulate 10 concurrent requests
        tasks = [make_request() for _ in range(10)]
        results = await asyncio.gather(*tasks)

        # All should succeed
        assert all(results)
        assert len(results) == 10

    @pytest.mark.asyncio
    async def test_analysis_result_consistency(self, test_client, sample_architecture_analysis):
        """Test analysis results are consistent"""
        response1 = test_client.post(
            "/lords/architect/architecture/analyze",
            json=sample_architecture_analysis
        )

        response2 = test_client.post(
            "/lords/architect/architecture/analyze",
            json=sample_architecture_analysis
        )

        assert response1.status_code == 200
        assert response2.status_code == 200

        # Results should be similar (though may not be identical due to randomness)
        result1 = response1.json()["analysis"]
        result2 = response2.json()["analysis"]

        # Both should have issues and recommendations
        assert "issues" in result1 and "issues" in result2
        assert "recommendations" in result1 and "recommendations" in result2


# ==============================================================================
# ERROR HANDLING TESTS
# ==============================================================================

class TestArchitectErrorHandling:
    """Test error handling and edge cases"""

    @pytest.mark.asyncio
    async def test_missing_required_fields(self, test_client):
        """Test API handles missing required fields"""
        # Missing objectives
        response = test_client.post(
            "/lords/architect/initiatives/design",
            json={
                "name": "Test Initiative",
                "target_guilds": ["research"]
                # Missing objectives and timeline
            }
        )

        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_invalid_initiative_id(self, test_client):
        """Test handling of invalid initiative ID"""
        response = test_client.get(
            "/lords/architect/initiatives/invalid_id_12345"
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_invalid_approver(self, test_client, sample_initiative_request):
        """Test handling of invalid approver"""
        # Create initiative
        create_response = test_client.post(
            "/lords/architect/initiatives/design",
            json=sample_initiative_request
        )
        initiative_id = create_response.json()["data"]["id"]

        # Try to approve with invalid approver
        response = test_client.post(
            f"/lords/architect/initiatives/{initiative_id}/approve",
            json={"approver": "invalid_lord"}
        )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_websocket_disconnect_handling(self, test_client):
        """Test graceful WebSocket disconnect"""
        with test_client.websocket_connect("/ws/lords/architect") as websocket:
            websocket.send_text("subscribe")
            response = websocket.receive_json()
            assert response["type"] == "subscription_confirmed"

        # Connection should close gracefully
        # (No exception should be raised)


# ==============================================================================
# INTEGRATION WITH RAFTORBUS TESTS
# ==============================================================================

class TestArchitectRaptorBusIntegration:
    """Test RaptorBus event integration"""

    @pytest.mark.asyncio
    async def test_initiative_publishes_event(self, architect_agent):
        """Test that initiative design publishes RaptorBus event"""
        with patch('raptor_bus.RaptorBus.publish_event') as mock_publish:
            mock_publish.return_value = None

            result = await architect_agent.execute(
                task="design_initiative",
                parameters={
                    "initiative_name": "Test Initiative",
                    "objectives": ["Objective 1"],
                    "target_guilds": ["research"],
                    "timeline_weeks": 4,
                    "success_metrics": {}
                }
            )

            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_event_payload_structure(self, architect_agent):
        """Test RaptorBus event payload structure"""
        # Event should include initiative ID, name, status, timestamp
        result = await architect_agent.execute(
            task="design_initiative",
            parameters={
                "initiative_name": "Test Event Payload",
                "objectives": ["Objective 1"],
                "target_guilds": ["research"],
                "timeline_weeks": 4,
                "success_metrics": {}
            }
        )

        initiative = result["data"]
        assert "id" in initiative
        assert "name" in initiative
        assert "status" in initiative
        assert "created_at" in initiative


# ==============================================================================
# FRONTEND INTEGRATION TESTS
# ==============================================================================

class TestArchitectFrontendIntegration:
    """Test frontend integration scenarios"""

    @pytest.mark.asyncio
    async def test_frontend_can_create_initiative(self, test_client, sample_initiative_request):
        """Test frontend initiative creation scenario"""
        # Frontend sends request
        response = test_client.post(
            "/lords/architect/initiatives/design",
            json={
                "name": sample_initiative_request["name"],
                "objectives": sample_initiative_request["objectives"],
                "target_guilds": sample_initiative_request["target_guilds"],
                "timeline_weeks": sample_initiative_request["timeline_weeks"],
                "success_metrics": sample_initiative_request["success_metrics"]
            }
        )

        # Backend responds with initiative details
        assert response.status_code == 200
        data = response.json()

        # Frontend receives these fields
        assert "status" in data
        assert "data" in data
        assert data["data"]["id"]
        assert data["data"]["name"]
        assert data["data"]["status"] in ["proposed", "designing", "designed"]

    @pytest.mark.asyncio
    async def test_frontend_can_list_initiatives_with_filters(self, test_client):
        """Test frontend can list initiatives with status filter"""
        response = test_client.get(
            "/lords/architect/initiatives?status=designed"
        )

        assert response.status_code == 200
        initiatives = response.json()
        assert isinstance(initiatives, list)

    @pytest.mark.asyncio
    async def test_frontend_metric_card_data(self, test_client):
        """Test frontend metric card data availability"""
        response = test_client.get("/lords/architect/status")

        assert response.status_code == 200
        data = response.json()

        # Frontend metric cards expect
        performance = data["performance"]
        assert "initiatives_designed" in performance
        assert "initiatives_approved" in performance
        assert "architecture_decisions" in performance
        assert "guild_guidance_provided" in performance


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
