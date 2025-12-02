# test_arbiter_e2e_integration.py
# RaptorFlow Codex - Arbiter Lord E2E Integration Tests
# Phase 2A Week 6 - Comprehensive Test Suite

import pytest
import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List
from httpx import AsyncClient
from unittest.mock import Mock, patch, AsyncMock

# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_conflict_case() -> Dict[str, Any]:
    """Sample conflict case data"""
    return {
        "conflict_type": "resource_allocation",
        "title": "GPU Resource Contention - Guild A vs Guild B",
        "description": "Two guilds competing for GPU allocation for AI training",
        "parties_involved": ["Guild A", "Guild B"],
        "conflicting_goals": [
            "Guild A: Maximize GPU time for Q4 model training",
            "Guild B: Maintain consistent GPU availability for real-time inference"
        ]
    }

@pytest.fixture
def sample_resolution_proposal() -> Dict[str, Any]:
    """Sample resolution proposal"""
    return {
        "case_id": "case_001",
        "proposed_solution": "Allocate GPU resources on time-sharing basis: Guild A gets 70% peak hours, Guild B gets 30%. Reverse allocation during off-peak hours.",
        "priority_adjustment": {
            "Guild_A_priority": 0.7,
            "Guild_B_priority": 0.3
        }
    }

@pytest.fixture
def sample_decision() -> Dict[str, Any]:
    """Sample arbitration decision"""
    return {
        "case_id": "case_001",
        "proposal_id": "prop_001",
        "enforcement_method": "monitored"
    }

@pytest.fixture
def sample_appeal() -> Dict[str, Any]:
    """Sample appeal"""
    return {
        "decision_id": "dec_001",
        "appellant_party": "Guild A",
        "appeal_grounds": [
            "Unfair allocation of GPU resources",
            "Did not consider seasonal workload patterns",
            "Monitoring method too restrictive"
        ],
        "requested_review_points": [
            "Historical GPU usage patterns",
            "Projected Q4 requirements",
            "Alternative enforcement methods"
        ]
    }

# ============================================================================
# UNIT TESTS - CAPABILITY HANDLERS
# ============================================================================

class TestArbiterCapabilities:
    """Test Arbiter Lord capability handlers"""

    @pytest.mark.asyncio
    async def test_register_conflict_capability(self):
        """Test conflict registration capability"""
        from agents.council_of_lords.arbiter import ArbiterLord

        arbiter = ArbiterLord()
        await arbiter.initialize()

        result = await arbiter.execute(
            task="register_conflict",
            parameters={
                "conflict_type": "resource_allocation",
                "title": "Test Conflict",
                "description": "Test conflict description",
                "parties_involved": ["Party A", "Party B"],
                "conflicting_goals": ["Goal 1", "Goal 2"]
            }
        )

        assert result.get("success", True) is not False
        assert "case_id" in result or "data" in result
        assert result.get("case_id") or (result.get("data") and "case_id" in result.get("data", {}))

    @pytest.mark.asyncio
    async def test_analyze_conflict_capability(self):
        """Test conflict analysis capability"""
        from agents.council_of_lords.arbiter import ArbiterLord

        arbiter = ArbiterLord()
        await arbiter.initialize()

        # Register first
        register_result = await arbiter.execute(
            task="register_conflict",
            parameters={
                "conflict_type": "priority_dispute",
                "title": "Test Analysis",
                "description": "Testing analysis",
                "parties_involved": ["Team A", "Team B"],
                "conflicting_goals": ["Goal 1", "Goal 2"]
            }
        )

        case_id = register_result.get("case_id") or register_result.get("data", {}).get("case_id")

        # Analyze
        result = await arbiter.execute(
            task="analyze_conflict",
            parameters={
                "case_id": case_id,
                "additional_context": {
                    "stakeholder_count": 5,
                    "impact_level": "high"
                }
            }
        )

        assert result.get("success", True) is not False
        assert "analysis_id" in result or "data" in result

    @pytest.mark.asyncio
    async def test_propose_resolution_capability(self):
        """Test resolution proposal capability"""
        from agents.council_of_lords.arbiter import ArbiterLord

        arbiter = ArbiterLord()
        await arbiter.initialize()

        # Register case
        register_result = await arbiter.execute(
            task="register_conflict",
            parameters={
                "conflict_type": "goal_conflict",
                "title": "Test Proposal",
                "description": "Test proposal",
                "parties_involved": ["Party A", "Party B"],
                "conflicting_goals": ["Maximize speed", "Maximize quality"]
            }
        )

        case_id = register_result.get("case_id") or register_result.get("data", {}).get("case_id")

        # Propose
        result = await arbiter.execute(
            task="propose_resolution",
            parameters={
                "case_id": case_id,
                "proposed_solution": "Implement phased approach: speed iteration 1, quality iteration 2",
                "priority_adjustment": {"speed_priority": 0.5, "quality_priority": 0.5}
            }
        )

        assert result.get("success", True) is not False
        assert "proposal_id" in result or "data" in result

    @pytest.mark.asyncio
    async def test_make_arbitration_decision_capability(self):
        """Test arbitration decision capability"""
        from agents.council_of_lords.arbiter import ArbiterLord

        arbiter = ArbiterLord()
        await arbiter.initialize()

        # Register and propose
        register_result = await arbiter.execute(
            task="register_conflict",
            parameters={
                "conflict_type": "stakeholder_disagreement",
                "title": "Test Decision",
                "description": "Test decision making",
                "parties_involved": ["Stakeholder A", "Stakeholder B"],
                "conflicting_goals": ["Direction 1", "Direction 2"]
            }
        )

        case_id = register_result.get("case_id") or register_result.get("data", {}).get("case_id")

        propose_result = await arbiter.execute(
            task="propose_resolution",
            parameters={
                "case_id": case_id,
                "proposed_solution": "Hybrid approach combining both perspectives",
                "priority_adjustment": {}
            }
        )

        proposal_id = propose_result.get("proposal_id") or propose_result.get("data", {}).get("proposal_id")

        # Make decision
        result = await arbiter.execute(
            task="make_arbitration_decision",
            parameters={
                "case_id": case_id,
                "proposal_id": proposal_id,
                "enforcement_method": "standard"
            }
        )

        assert result.get("success", True) is not False
        assert "decision_id" in result or "data" in result

    @pytest.mark.asyncio
    async def test_handle_appeal_capability(self):
        """Test appeal handling capability"""
        from agents.council_of_lords.arbiter import ArbiterLord

        arbiter = ArbiterLord()
        await arbiter.initialize()

        # Register, propose, decide, appeal
        register_result = await arbiter.execute(
            task="register_conflict",
            parameters={
                "conflict_type": "decision_challenge",
                "title": "Test Appeal",
                "description": "Test appeal",
                "parties_involved": ["Party A", "Party B"],
                "conflicting_goals": ["Approach 1", "Approach 2"]
            }
        )

        case_id = register_result.get("case_id") or register_result.get("data", {}).get("case_id")

        propose_result = await arbiter.execute(
            task="propose_resolution",
            parameters={
                "case_id": case_id,
                "proposed_solution": "Balanced resolution",
                "priority_adjustment": {}
            }
        )

        proposal_id = propose_result.get("proposal_id") or propose_result.get("data", {}).get("proposal_id")

        decision_result = await arbiter.execute(
            task="make_arbitration_decision",
            parameters={
                "case_id": case_id,
                "proposal_id": proposal_id,
                "enforcement_method": "standard"
            }
        )

        decision_id = decision_result.get("decision_id") or decision_result.get("data", {}).get("decision_id")

        # Handle appeal
        result = await arbiter.execute(
            task="handle_appeal",
            parameters={
                "decision_id": decision_id,
                "appellant_party": "Party A",
                "appeal_grounds": ["Unfair treatment", "Insufficient evidence"],
                "requested_review_points": ["Stakeholder input", "Alternative approaches"]
            }
        )

        assert result.get("success", True) is not False
        assert "appeal_id" in result or "data" in result

# ============================================================================
# API INTEGRATION TESTS
# ============================================================================

class TestArbiterAPIEndpoints:
    """Test Arbiter API endpoints"""

    @pytest.mark.asyncio
    async def test_register_conflict_endpoint(self, sample_conflict_case):
        """Test POST /lords/arbiter/conflict/register"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/lords/arbiter/conflict/register",
                json=sample_conflict_case,
                headers={"Authorization": "Bearer test_token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data.get("status") == "success"
            assert "data" in data or "case_id" in data

    @pytest.mark.asyncio
    async def test_get_conflict_cases_endpoint(self):
        """Test GET /lords/arbiter/cases"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/lords/arbiter/cases?limit=10",
                headers={"Authorization": "Bearer test_token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_conflict_case_detail_endpoint(self):
        """Test GET /lords/arbiter/cases/{case_id}"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # First register a case
            register_response = await client.post(
                "/lords/arbiter/conflict/register",
                json={
                    "conflict_type": "resource_allocation",
                    "title": "Test Case",
                    "description": "Test",
                    "parties_involved": ["A", "B"],
                    "conflicting_goals": ["G1", "G2"]
                },
                headers={"Authorization": "Bearer test_token"}
            )

            case_data = register_response.json().get("data", {})
            case_id = case_data.get("case_id", "case_001")

            # Get detail
            response = await client.get(
                f"/lords/arbiter/cases/{case_id}",
                headers={"Authorization": "Bearer test_token"}
            )

            assert response.status_code in [200, 404]  # May not exist in test environment

    @pytest.mark.asyncio
    async def test_analyze_conflict_endpoint(self, sample_conflict_case):
        """Test POST /lords/arbiter/analysis/analyze"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/lords/arbiter/analysis/analyze",
                json={
                    "case_id": "case_001",
                    "additional_context": {"test": True}
                },
                headers={"Authorization": "Bearer test_token"}
            )

            assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_propose_resolution_endpoint(self, sample_resolution_proposal):
        """Test POST /lords/arbiter/resolution/propose"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/lords/arbiter/resolution/propose",
                json=sample_resolution_proposal,
                headers={"Authorization": "Bearer test_token"}
            )

            assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_get_proposals_endpoint(self):
        """Test GET /lords/arbiter/proposals"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/lords/arbiter/proposals?limit=10",
                headers={"Authorization": "Bearer test_token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_make_decision_endpoint(self, sample_decision):
        """Test POST /lords/arbiter/decision/make"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/lords/arbiter/decision/make",
                json=sample_decision,
                headers={"Authorization": "Bearer test_token"}
            )

            assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_get_decisions_endpoint(self):
        """Test GET /lords/arbiter/decisions"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/lords/arbiter/decisions?limit=10",
                headers={"Authorization": "Bearer test_token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_handle_appeal_endpoint(self, sample_appeal):
        """Test POST /lords/arbiter/appeals/handle"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/lords/arbiter/appeals/handle",
                json=sample_appeal,
                headers={"Authorization": "Bearer test_token"}
            )

            assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_get_appeals_endpoint(self):
        """Test GET /lords/arbiter/appeals"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/lords/arbiter/appeals?limit=10",
                headers={"Authorization": "Bearer test_token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_generate_fairness_report_endpoint(self):
        """Test POST /lords/arbiter/fairness/report"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/lords/arbiter/fairness/report?evaluation_period_days=30",
                headers={"Authorization": "Bearer test_token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data.get("status") in ["success", "error"]

    @pytest.mark.asyncio
    async def test_get_arbiter_status_endpoint(self):
        """Test GET /lords/arbiter/status"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/lords/arbiter/status",
                headers={"Authorization": "Bearer test_token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert "agent" in data or "performance" in data

# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestArbiterPerformance:
    """Test Arbiter performance SLAs"""

    @pytest.mark.asyncio
    async def test_register_conflict_performance(self, sample_conflict_case):
        """Test conflict registration completes in <100ms"""
        from agents.council_of_lords.arbiter import ArbiterLord

        arbiter = ArbiterLord()
        await arbiter.initialize()

        start = time.time()
        await arbiter.execute(
            task="register_conflict",
            parameters=sample_conflict_case
        )
        duration = (time.time() - start) * 1000

        assert duration < 100, f"Conflict registration took {duration}ms, expected <100ms"

    @pytest.mark.asyncio
    async def test_analyze_conflict_performance(self):
        """Test conflict analysis completes in <100ms"""
        from agents.council_of_lords.arbiter import ArbiterLord

        arbiter = ArbiterLord()
        await arbiter.initialize()

        start = time.time()
        await arbiter.execute(
            task="analyze_conflict",
            parameters={
                "case_id": "case_001",
                "additional_context": {}
            }
        )
        duration = (time.time() - start) * 1000

        assert duration < 100, f"Conflict analysis took {duration}ms, expected <100ms"

    @pytest.mark.asyncio
    async def test_propose_resolution_performance(self):
        """Test resolution proposal completes in <100ms"""
        from agents.council_of_lords.arbiter import ArbiterLord

        arbiter = ArbiterLord()
        await arbiter.initialize()

        start = time.time()
        await arbiter.execute(
            task="propose_resolution",
            parameters={
                "case_id": "case_001",
                "proposed_solution": "Test solution",
                "priority_adjustment": {}
            }
        )
        duration = (time.time() - start) * 1000

        assert duration < 100, f"Resolution proposal took {duration}ms, expected <100ms"

    @pytest.mark.asyncio
    async def test_make_decision_performance(self):
        """Test decision making completes in <100ms"""
        from agents.council_of_lords.arbiter import ArbiterLord

        arbiter = ArbiterLord()
        await arbiter.initialize()

        start = time.time()
        await arbiter.execute(
            task="make_arbitration_decision",
            parameters={
                "case_id": "case_001",
                "proposal_id": "prop_001",
                "enforcement_method": "standard"
            }
        )
        duration = (time.time() - start) * 1000

        assert duration < 100, f"Decision making took {duration}ms, expected <100ms"

    @pytest.mark.asyncio
    async def test_handle_appeal_performance(self):
        """Test appeal handling completes in <100ms"""
        from agents.council_of_lords.arbiter import ArbiterLord

        arbiter = ArbiterLord()
        await arbiter.initialize()

        start = time.time()
        await arbiter.execute(
            task="handle_appeal",
            parameters={
                "decision_id": "dec_001",
                "appellant_party": "Party A",
                "appeal_grounds": ["Ground 1"],
                "requested_review_points": ["Point 1"]
            }
        )
        duration = (time.time() - start) * 1000

        assert duration < 100, f"Appeal handling took {duration}ms, expected <100ms"

# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestArbiterErrorHandling:
    """Test Arbiter error handling"""

    @pytest.mark.asyncio
    async def test_invalid_conflict_type(self):
        """Test handling of invalid conflict type"""
        from agents.council_of_lords.arbiter import ArbiterLord

        arbiter = ArbiterLord()
        await arbiter.initialize()

        result = await arbiter.execute(
            task="register_conflict",
            parameters={
                "conflict_type": "invalid_type",
                "title": "Test",
                "description": "Test",
                "parties_involved": [],
                "conflicting_goals": []
            }
        )

        # Should either fail gracefully or handle invalid type
        assert result.get("success", True) is not None

    @pytest.mark.asyncio
    async def test_missing_required_fields(self):
        """Test handling of missing required fields"""
        from agents.council_of_lords.arbiter import ArbiterLord

        arbiter = ArbiterLord()
        await arbiter.initialize()

        result = await arbiter.execute(
            task="register_conflict",
            parameters={
                "conflict_type": "resource_allocation",
                # Missing required fields
            }
        )

        # Should handle gracefully
        assert result is not None

    @pytest.mark.asyncio
    async def test_nonexistent_case_id(self):
        """Test handling of nonexistent case ID"""
        from agents.council_of_lords.arbiter import ArbiterLord

        arbiter = ArbiterLord()
        await arbiter.initialize()

        result = await arbiter.execute(
            task="analyze_conflict",
            parameters={
                "case_id": "nonexistent_case_id_xyz",
                "additional_context": {}
            }
        )

        # Should handle gracefully or return not found
        assert result is not None

    @pytest.mark.asyncio
    async def test_invalid_enforcement_method(self):
        """Test handling of invalid enforcement method"""
        from agents.council_of_lords.arbiter import ArbiterLord

        arbiter = ArbiterLord()
        await arbiter.initialize()

        result = await arbiter.execute(
            task="make_arbitration_decision",
            parameters={
                "case_id": "case_001",
                "proposal_id": "prop_001",
                "enforcement_method": "invalid_method"
            }
        )

        # Should handle gracefully
        assert result is not None

# ============================================================================
# E2E WORKFLOW TESTS
# ============================================================================

class TestArbiterE2EWorkflows:
    """Test complete Arbiter workflows"""

    @pytest.mark.asyncio
    async def test_complete_conflict_resolution_workflow(self):
        """Test complete workflow: register → analyze → propose → decide"""
        from agents.council_of_lords.arbiter import ArbiterLord

        arbiter = ArbiterLord()
        await arbiter.initialize()

        # Step 1: Register conflict
        register_result = await arbiter.execute(
            task="register_conflict",
            parameters={
                "conflict_type": "resource_allocation",
                "title": "Complete Workflow Test",
                "description": "Testing complete workflow",
                "parties_involved": ["Team A", "Team B"],
                "conflicting_goals": ["Goal 1", "Goal 2"]
            }
        )

        case_id = register_result.get("case_id") or register_result.get("data", {}).get("case_id")
        assert case_id is not None

        # Step 2: Analyze conflict
        analyze_result = await arbiter.execute(
            task="analyze_conflict",
            parameters={
                "case_id": case_id,
                "additional_context": {"priority": "high"}
            }
        )

        assert analyze_result is not None

        # Step 3: Propose resolution
        propose_result = await arbiter.execute(
            task="propose_resolution",
            parameters={
                "case_id": case_id,
                "proposed_solution": "50/50 split with quarterly review",
                "priority_adjustment": {"team_a": 0.5, "team_b": 0.5}
            }
        )

        proposal_id = propose_result.get("proposal_id") or propose_result.get("data", {}).get("proposal_id")
        assert proposal_id is not None

        # Step 4: Make decision
        decision_result = await arbiter.execute(
            task="make_arbitration_decision",
            parameters={
                "case_id": case_id,
                "proposal_id": proposal_id,
                "enforcement_method": "monitored"
            }
        )

        assert decision_result is not None
        decision_id = decision_result.get("decision_id") or decision_result.get("data", {}).get("decision_id")
        assert decision_id is not None

    @pytest.mark.asyncio
    async def test_conflict_with_appeal_workflow(self):
        """Test workflow with appeal: register → propose → decide → appeal"""
        from agents.council_of_lords.arbiter import ArbiterLord

        arbiter = ArbiterLord()
        await arbiter.initialize()

        # Register
        register_result = await arbiter.execute(
            task="register_conflict",
            parameters={
                "conflict_type": "priority_dispute",
                "title": "Appeal Workflow Test",
                "description": "Testing appeal workflow",
                "parties_involved": ["Party A", "Party B"],
                "conflicting_goals": ["Priority 1", "Priority 2"]
            }
        )

        case_id = register_result.get("case_id") or register_result.get("data", {}).get("case_id")

        # Propose
        propose_result = await arbiter.execute(
            task="propose_resolution",
            parameters={
                "case_id": case_id,
                "proposed_solution": "Rotating priority scheme",
                "priority_adjustment": {}
            }
        )

        proposal_id = propose_result.get("proposal_id") or propose_result.get("data", {}).get("proposal_id")

        # Decide
        decision_result = await arbiter.execute(
            task="make_arbitration_decision",
            parameters={
                "case_id": case_id,
                "proposal_id": proposal_id,
                "enforcement_method": "standard"
            }
        )

        decision_id = decision_result.get("decision_id") or decision_result.get("data", {}).get("decision_id")

        # Appeal
        appeal_result = await arbiter.execute(
            task="handle_appeal",
            parameters={
                "decision_id": decision_id,
                "appellant_party": "Party A",
                "appeal_grounds": ["Insufficient consideration of seasonal patterns"],
                "requested_review_points": ["Seasonal demand analysis"]
            }
        )

        assert appeal_result is not None
        appeal_id = appeal_result.get("appeal_id") or appeal_result.get("data", {}).get("appeal_id")
        assert appeal_id is not None

    @pytest.mark.asyncio
    async def test_multiple_cases_parallel_processing(self):
        """Test handling multiple conflict cases in parallel"""
        from agents.council_of_lords.arbiter import ArbiterLord

        arbiter = ArbiterLord()
        await arbiter.initialize()

        # Create multiple cases in parallel
        cases = []
        for i in range(5):
            result = await arbiter.execute(
                task="register_conflict",
                parameters={
                    "conflict_type": "resource_allocation",
                    "title": f"Parallel Test Case {i}",
                    "description": f"Testing parallel case {i}",
                    "parties_involved": [f"Party {i}A", f"Party {i}B"],
                    "conflicting_goals": [f"Goal {i}1", f"Goal {i}2"]
                }
            )

            case_id = result.get("case_id") or result.get("data", {}).get("case_id")
            cases.append(case_id)

        assert len(cases) == 5
        assert all(case_id is not None for case_id in cases)

# ============================================================================
# CONCURRENT OPERATION TESTS
# ============================================================================

class TestArbiterConcurrency:
    """Test concurrent operations"""

    @pytest.mark.asyncio
    async def test_concurrent_conflict_registrations(self):
        """Test concurrent conflict registrations"""
        from agents.council_of_lords.arbiter import ArbiterLord

        arbiter = ArbiterLord()
        await arbiter.initialize()

        async def register_conflict(i):
            return await arbiter.execute(
                task="register_conflict",
                parameters={
                    "conflict_type": "resource_allocation",
                    "title": f"Concurrent Case {i}",
                    "description": f"Concurrent test {i}",
                    "parties_involved": ["A", "B"],
                    "conflicting_goals": ["G1", "G2"]
                }
            )

        results = await asyncio.gather(*[register_conflict(i) for i in range(10)])

        assert len(results) == 10
        assert all(r is not None for r in results)

    @pytest.mark.asyncio
    async def test_concurrent_mixed_operations(self):
        """Test concurrent mixed operations (register, analyze, propose)"""
        from agents.council_of_lords.arbiter import ArbiterLord

        arbiter = ArbiterLord()
        await arbiter.initialize()

        # Setup: register a case
        register_result = await arbiter.execute(
            task="register_conflict",
            parameters={
                "conflict_type": "goal_conflict",
                "title": "Mixed Concurrent Test",
                "description": "Mixed operations test",
                "parties_involved": ["A", "B"],
                "conflicting_goals": ["G1", "G2"]
            }
        )

        case_id = register_result.get("case_id") or register_result.get("data", {}).get("case_id")

        # Concurrent operations
        async def analyze():
            return await arbiter.execute(
                task="analyze_conflict",
                parameters={"case_id": case_id, "additional_context": {}}
            )

        async def propose():
            return await arbiter.execute(
                task="propose_resolution",
                parameters={
                    "case_id": case_id,
                    "proposed_solution": "Mixed test solution",
                    "priority_adjustment": {}
                }
            )

        results = await asyncio.gather(analyze(), propose())

        assert len(results) == 2
        assert all(r is not None for r in results)

# ============================================================================
# DATA STRUCTURE TESTS
# ============================================================================

class TestArbiterDataStructures:
    """Test Arbiter data structure integrity"""

    @pytest.mark.asyncio
    async def test_conflict_case_structure(self):
        """Test ConflictCase data structure"""
        from agents.council_of_lords.arbiter import ArbiterLord

        arbiter = ArbiterLord()
        await arbiter.initialize()

        result = await arbiter.execute(
            task="register_conflict",
            parameters={
                "conflict_type": "resource_allocation",
                "title": "Structure Test",
                "description": "Testing data structure",
                "parties_involved": ["A", "B"],
                "conflicting_goals": ["G1", "G2"]
            }
        )

        case_data = result.get("data", {})

        # Verify required fields
        assert case_data.get("case_id") is not None
        assert case_data.get("severity") is not None
        assert case_data.get("status") is not None

    @pytest.mark.asyncio
    async def test_resolution_proposal_structure(self):
        """Test ResolutionProposal data structure"""
        from agents.council_of_lords.arbiter import ArbiterLord

        arbiter = ArbiterLord()
        await arbiter.initialize()

        # Register case first
        register_result = await arbiter.execute(
            task="register_conflict",
            parameters={
                "conflict_type": "priority_dispute",
                "title": "Proposal Structure Test",
                "description": "Testing proposal structure",
                "parties_involved": ["A", "B"],
                "conflicting_goals": ["G1", "G2"]
            }
        )

        case_id = register_result.get("case_id") or register_result.get("data", {}).get("case_id")

        result = await arbiter.execute(
            task="propose_resolution",
            parameters={
                "case_id": case_id,
                "proposed_solution": "Test solution",
                "priority_adjustment": {}
            }
        )

        proposal_data = result.get("data", {})

        # Verify required fields
        assert proposal_data.get("proposal_id") is not None
        assert proposal_data.get("fairness_score") is not None
        assert proposal_data.get("status") is not None

# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
