from unittest.mock import AsyncMock, Mock, patch

import pytest
from schemas.bcm_evolution import EventType

from .services.bcm_projector import BCMProjector
from .services.icp import ICPService
from .services.move import MoveService
from .services.onboarding import OnboardingService


@pytest.mark.asyncio
@patch("backend.services.onboarding.OnboardingRepository")
@patch("backend.services.onboarding.get_supabase_client")
@patch("backend.services.bcm_integration.bcm_evolution.recorder.record_event")
async def test_onboarding_to_ledger_integration(
    MockRecordEvent, MockSupabase, MockRepo
):
    """Test that completing onboarding records a STRATEGIC_SHIFT in the ledger"""
    mock_db = Mock()
    MockSupabase.return_value = mock_db

    mock_repo = MockRepo.return_value
    mock_repo.get_by_workspace = AsyncMock(
        return_value={"id": "session-1", "step_data": {"step_1": {"name": "Test"}}}
    )
    mock_repo.update_step = AsyncMock(return_value={"status": "completed"})

    service = OnboardingService()
    workspace_id = "ws-integration-test"

    await service.complete_onboarding(workspace_id)

    # Verify ledger was called
    MockRecordEvent.assert_called_once()
    args, kwargs = MockRecordEvent.call_args
    assert kwargs["event_type"] == EventType.STRATEGIC_SHIFT
    assert kwargs["workspace_id"] == workspace_id
    assert "Initial Onboarding" in kwargs["payload"]["reason"]


@pytest.mark.asyncio
@patch("backend.services.icp.ICPRepository")
@patch("backend.services.icp.FoundationRepository")
@patch("backend.services.icp.get_supabase_client")
@patch("backend.services.icp.get_business_context_graph")
@patch("backend.services.bcm_integration.bcm_evolution.recorder.record_event")
async def test_icp_derivation_to_ledger_integration(
    MockRecordEvent, MockGraph, MockSupabase, MockFoundationRepo, MockICPRepo
):
    """Test that deriving an ICP trinity records a USER_INTERACTION in the ledger"""
    mock_db = Mock()
    MockSupabase.return_value = mock_db

    # Mock foundation check
    mock_foundation = MockFoundationRepo.return_value
    mock_foundation.get_by_workspace = AsyncMock(
        return_value={"company_name": "Test Corp"}
    )

    # Mock graph node
    mock_graph = MockGraph.return_value
    mock_ricp = Mock(id="icp-123", name="Test Cohort", confidence=90)
    mock_ricp.demographics.model_dump.return_value = {}
    mock_ricp.psychographics.model_dump.return_value = {"identity": "test"}
    mock_graph.enhance_icp_node = AsyncMock(
        return_value={"context_data": Mock(ricps=[mock_ricp])}
    )

    # Mock repo creation
    mock_icp_repo = MockICPRepo.return_value
    mock_icp_repo.create = AsyncMock(return_value={"id": "icp-db-id"})

    service = ICPService()
    workspace_id = "ws-icp-test"

    await service.derive_trinity(workspace_id, "Test Cohort")

    # Verify ledger interaction
    MockRecordEvent.assert_called_once()
    _, kwargs = MockRecordEvent.call_args
    assert kwargs["event_type"] == EventType.USER_INTERACTION
    assert kwargs["payload"]["interaction_type"] == "ICP_DERIVATION"
    assert kwargs["payload"]["cohort_name"] == "Test Cohort"


@pytest.mark.asyncio
@patch("backend.services.bcm_projector.get_supabase_client")
@patch("backend.services.bcm_projector.get_upstash_client")
async def test_projector_reconstruction_fidelity(MockUpstash, MockSupabase):
    """Test that projector accurately reconstructs state from mixed ledger events"""
    mock_db = Mock()
    MockSupabase.return_value = mock_db

    # 1. Mock a sequence of events: Shift -> Move -> Interaction
    mock_events = [
        {
            "event_type": EventType.STRATEGIC_SHIFT,
            "payload": {"identity": {"name": "Evolution Brand", "mission": "Evolve"}},
            "created_at": "2026-01-20T10:00:00Z",
        },
        {
            "event_type": EventType.MOVE_COMPLETED,
            "payload": {"title": "First Strategic Move"},
            "created_at": "2026-01-20T11:00:00Z",
        },
        {
            "event_type": EventType.USER_INTERACTION,
            "payload": {"interaction_type": "CHAT", "agent_name": "Muse"},
            "created_at": "2026-01-20T12:00:00Z",
        },
    ]

    mock_db.table.return_value.select.return_value.eq.return_value.order.return_value.execute = AsyncMock(
        return_value=Mock(data=mock_events)
    )

    # Mock cache miss
    mock_redis = MockUpstash.return_value
    mock_redis.get = AsyncMock(return_value=None)
    mock_redis.set = AsyncMock()

    projector = BCMProjector()
    state = await projector.get_latest_state("ws-fidelity", "RF-TEST")

    # 2. Verify state fidelity
    assert state.identity.name == "Evolution Brand"
    assert "First Strategic Move" in state.history.significant_milestones
    assert state.telemetry.total_interactions == 1
    assert state.history.total_events == 3

    # 3. Verify cache was populated
    mock_redis.set.assert_called_once()
