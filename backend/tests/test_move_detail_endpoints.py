import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from api.v1.moves import router as moves_router
from models.api_models import (
    MoveMetricRequest,
    MoveTaskCreateRequest,
    MoveTaskUpdateRequest,
    MoveUpdateRequest,
)
from services.move_service import MoveService


class TestMoveDetailEndpoints:
    """Test suite for Move detail page endpoints."""

    @pytest.fixture
    def mock_move_service(self):
        """Mock move service for testing."""
        service = AsyncMock(spec=MoveService)
        return service

    @pytest.fixture
    def sample_move_data(self):
        """Sample move data for testing."""
        return {
            "id": str(uuid4()),
            "campaign_id": str(uuid4()),
            "title": "Test Move",
            "description": "Test move description",
            "status": "active",
            "priority": 3,
            "move_type": "content",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "tool_requirements": [{"name": "tool1", "type": "search"}],
            "execution_result": None,
            "checklist": [
                {
                    "id": str(uuid4()),
                    "label": "Task 1",
                    "instructions": "Complete task 1",
                    "due_date": "2024-01-15",
                    "estimated_minutes": 30,
                    "completed": False,
                    "created_at": "2024-01-01T00:00:00Z",
                }
            ],
            "assets": [{"id": str(uuid4()), "type": "image", "url": "test.jpg"}],
            "daily_metrics": [
                {
                    "leads": 10,
                    "replies": 5,
                    "calls": 2,
                    "confidence": 7,
                    "note": "Good progress",
                    "submitted_at": "2024-01-01T00:00:00Z",
                }
            ],
            "confidence": 7.5,
            "started_at": "2024-01-01T00:00:00Z",
            "completed_at": None,
            "paused_at": None,
            "rag_status": "green",
            "rag_reason": "On pace",
            "refinement_data": {"muse_prompt": "Test prompt"},
            "campaign_name": "Test Campaign",
            "reasoning_chain_id": str(uuid4()),
            "consensus_metrics": {"alignment": 0.8, "confidence": 0.7, "risk": 0.3},
            "decree": "Test decree",
        }

    @pytest.fixture
    def sample_rationale_data(self):
        """Sample rationale data for testing."""
        return {
            "decree": "Test strategic decree",
            "consensus_alignment": 0.8,
            "confidence": 0.7,
            "risk": 0.3,
            "expert_thoughts": [
                {
                    "agent_id": "direct_response",
                    "agent_name": "Direct Response",
                    "agent_role": "Conversion Architect",
                    "content": "Test thought content",
                    "confidence": 0.9,
                    "round": 1,
                }
            ],
            "rejected_paths": [
                {"path": "Alternative A", "reason": "Low ROI"},
                {"path": "Alternative B", "reason": "High risk"},
            ],
            "historical_parallel": [{"title": "Similar move", "success": True}],
            "debate_rounds": [
                {
                    "round_number": 1,
                    "synthesis": "Round 1 synthesis",
                    "proposals": [
                        {"agent_id": "direct_response", "content": "Proposal content"}
                    ],
                    "critiques": [],
                }
            ],
            "cached": False,
        }

    @pytest.mark.asyncio
    async def test_get_move_detail_success(self, mock_move_service, sample_move_data):
        """Test successful move detail retrieval."""
        mock_move_service.get_move_detail.return_value = sample_move_data

        with patch("api.v1.moves.get_move_service", return_value=mock_move_service):
            from api.v1.moves import get_move_detail

            result = await get_move_detail(
                move_id=sample_move_data["id"],
                tenant_id=uuid4(),
                _current_user={"id": "test_user"},
                service=mock_move_service,
            )

            assert result.success is True
            move = result.data["move"]
            assert move["id"] == sample_move_data["id"]
            assert move["title"] == sample_move_data["title"]
            assert move["campaign_id"] == sample_move_data["campaign_id"]
            assert move["checklist"] == sample_move_data["checklist"]
            assert move["assets"] == sample_move_data["assets"]
            assert move["daily_metrics"] == sample_move_data["daily_metrics"]
            assert move["confidence"] == sample_move_data["confidence"]
            assert move["rag_status"] == sample_move_data["rag_status"]
            assert move["refinement_data"] == sample_move_data["refinement_data"]
            mock_move_service.get_move_detail.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_move_detail_not_found(self, mock_move_service):
        """Test move detail retrieval when move not found."""
        mock_move_service.get_move_detail.return_value = None

        with patch("api.v1.moves.get_move_service", return_value=mock_move_service):
            from fastapi import HTTPException

            from api.v1.moves import get_move_detail

            with pytest.raises(HTTPException) as exc_info:
                await get_move_detail(
                    move_id=str(uuid4()),
                    tenant_id=uuid4(),
                    _current_user={"id": "test_user"},
                    service=mock_move_service,
                )

            assert exc_info.value.status_code == 404
            assert "Move not found" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_move_rationale_success(
        self, mock_move_service, sample_rationale_data
    ):
        """Test successful move rationale retrieval."""
        mock_move_service.get_move_rationale.return_value = sample_rationale_data

        with patch("api.v1.moves.get_move_service", return_value=mock_move_service):
            from api.v1.moves import get_move_rationale

            result = await get_move_rationale(
                move_id=str(uuid4()),
                tenant_id=uuid4(),
                _current_user={"id": "test_user"},
                service=mock_move_service,
            )

            assert result.success is True
            rationale = result.data
            assert rationale["decree"] == sample_rationale_data["decree"]
            assert (
                rationale["consensus_alignment"]
                == sample_rationale_data["consensus_alignment"]
            )
            assert (
                rationale["expert_thoughts"] == sample_rationale_data["expert_thoughts"]
            )
            assert (
                rationale["rejected_paths"] == sample_rationale_data["rejected_paths"]
            )
            assert rationale["debate_rounds"] == sample_rationale_data["debate_rounds"]
            assert rationale["cached"] == sample_rationale_data["cached"]
            mock_move_service.get_move_rationale.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_move_rationale_cached(
        self, mock_move_service, sample_rationale_data
    ):
        """Test move rationale retrieval from cache."""
        cached_rationale = {**sample_rationale_data, "cached": True}
        mock_move_service.get_move_rationale.return_value = cached_rationale

        with patch("api.v1.moves.get_move_service", return_value=mock_move_service):
            from api.v1.moves import get_move_rationale

            result = await get_move_rationale(
                move_id=str(uuid4()),
                tenant_id=uuid4(),
                _current_user={"id": "test_user"},
                service=mock_move_service,
            )

            assert result.success is True
            assert result.data["cached"] is True

    @pytest.mark.asyncio
    async def test_add_move_task_success(self, mock_move_service, sample_move_data):
        """Test successful task addition."""
        mock_move_service.get_move_detail.return_value = sample_move_data
        # Return updated move with 2 tasks
        updated_move = {
            **sample_move_data,
            "checklist": sample_move_data["checklist"]
            + [
                {
                    "id": str(uuid4()),
                    "label": "New Task",
                    "instructions": "Complete new task",
                    "due_date": "2024-01-20",
                    "estimated_minutes": 45,
                    "completed": False,
                    "created_at": datetime.utcnow().isoformat(),
                }
            ],
        }
        mock_move_service.add_task.return_value = updated_move

        with patch("api.v1.moves.get_move_service", return_value=mock_move_service):
            from api.v1.moves import add_move_task

            task_data = MoveTaskCreateRequest(
                label="New Task",
                instructions="Complete new task",
                due_date="2024-01-20",
                estimated_minutes=45,
            )

            result = await add_move_task(
                move_id=sample_move_data["id"],
                task_data=task_data,
                tenant_id=uuid4(),
                _current_user={"id": "test_user"},
                service=mock_move_service,
            )

            assert result.success is True
            assert result.message == "Task added successfully"
            assert result.data["task_count"] == 2  # Original 1 + new 1
            mock_move_service.add_task.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_move_task_validation_error(self, mock_move_service):
        """Test task addition with invalid data."""
        with patch("api.v1.moves.get_move_service", return_value=mock_move_service):
            from fastapi import HTTPException
            from pydantic import ValidationError

            from api.v1.moves import add_move_task

            # Test empty label - this should be caught by Pydantic validation before reaching our endpoint
            try:
                task_data = MoveTaskCreateRequest(label="", instructions="Test")
                # If we get here, validation didn't work as expected
                assert False, "Pydantic validation should have failed"
            except ValidationError:
                # This is expected - Pydantic validates before our endpoint logic
                pass

            # Test negative minutes - this should be caught by Pydantic validation as well
            try:
                task_data = MoveTaskCreateRequest(
                    label="Test", instructions="Test", estimated_minutes=-5
                )
                # If we get here, validation didn't work as expected
                assert False, "Pydantic validation should have failed"
            except ValidationError:
                # This is expected - Pydantic validates before our endpoint logic
                pass

            # Test a validation that our endpoint handles (not Pydantic)
            # Since Pydantic handles most validation, let's test a scenario where the move doesn't exist
            mock_move_service.add_task.return_value = None

            task_data = MoveTaskCreateRequest(
                label="Test", instructions="Test", estimated_minutes=5
            )

            with pytest.raises(HTTPException) as exc_info:
                await add_move_task(
                    move_id=str(uuid4()),
                    task_data=task_data,
                    tenant_id=uuid4(),
                    _current_user={"id": "test_user"},
                    service=mock_move_service,
                )

            assert exc_info.value.status_code == 404
            assert "Move not found" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_update_move_task_success(self, mock_move_service, sample_move_data):
        """Test successful task update."""
        task_id = str(uuid4())
        mock_move_service.update_task.return_value = sample_move_data

        with patch("api.v1.moves.get_move_service", return_value=mock_move_service):
            from api.v1.moves import update_move_task

            task_updates = MoveTaskUpdateRequest(completed=True, label="Updated Task")

            result = await update_move_task(
                move_id=sample_move_data["id"],
                task_id=task_id,
                task_updates=task_updates,
                tenant_id=uuid4(),
                _current_user={"id": "test_user"},
                service=mock_move_service,
            )

            assert result.success is True
            assert result.message == "Task updated successfully"
            assert result.data["task_id"] == task_id
            mock_move_service.update_task.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_move_success(self, mock_move_service, sample_move_data):
        """Test successful move update."""
        updated_move = {
            **sample_move_data,
            "title": "Updated Move",
            "status": "completed",
            "confidence": 8,
        }
        mock_move_service.update_move.return_value = updated_move

        with patch("api.v1.moves.get_move_service", return_value=mock_move_service):
            from api.v1.moves import update_move

            move_updates = MoveUpdateRequest(
                title="Updated Move", status="completed", confidence=8
            )

            result = await update_move(
                move_id=sample_move_data["id"],
                move_updates=move_updates,
                tenant_id=uuid4(),
                _current_user={"id": "test_user"},
                service=mock_move_service,
            )

            assert result.success is True
            assert result.message == "Move updated successfully"
            updated = result.data["move"]
            assert updated["title"] == "Updated Move"
            assert updated["status"] == "completed"
            assert updated["confidence"] == 8
            mock_move_service.update_move.assert_called_once()

    @pytest.mark.asyncio
    async def test_log_move_metric_success(self, mock_move_service, sample_move_data):
        """Test successful metric logging."""
        mock_move_service.append_metric.return_value = {
            "move": sample_move_data,
            "rag": {"status": "green", "reason": "On pace"},
        }

        with patch("api.v1.moves.get_move_service", return_value=mock_move_service):
            from api.v1.moves import log_move_metric

            metrics = MoveMetricRequest(
                leads=15, replies=8, calls=3, confidence=8, note="Great progress today"
            )

            result = await log_move_metric(
                move_id=sample_move_data["id"],
                metrics=metrics,
                tenant_id=uuid4(),
                _current_user={"id": "test_user"},
                service=mock_move_service,
            )

            assert result.success is True
            assert result.message == "Metrics logged successfully"
            assert "rag" in result.data
            mock_move_service.append_metric.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_move_tasks_pagination(self, mock_move_service, sample_move_data):
        """Test paginated task retrieval."""
        # Create move with many tasks
        move_with_many_tasks = {
            **sample_move_data,
            "checklist": [
                {
                    "id": str(uuid4()),
                    "label": f"Task {i}",
                    "completed": i % 2 == 0,
                    "created_at": (datetime.utcnow() - timedelta(days=i)).isoformat(),
                }
                for i in range(25)
            ],
        }
        mock_move_service.get_move_detail.return_value = move_with_many_tasks

        with patch("api.v1.moves.get_move_service", return_value=mock_move_service):
            from api.v1.moves import get_move_tasks

            result = await get_move_tasks(
                move_id=sample_move_data["id"],
                page=1,
                page_size=10,
                status="pending",
                tenant_id=uuid4(),
                _current_user={"id": "test_user"},
                service=mock_move_service,
            )

            assert result.success is True
            tasks = result.data["tasks"]
            pagination = result.data["pagination"]
            assert len(tasks) == 10  # First page
            assert pagination["page"] == 1
            assert pagination["page_size"] == 10
            assert pagination["total"] == 12  # Even tasks (0,2,4...24) are pending
            assert pagination["total_pages"] == 2
            assert pagination["has_next"] is True
            assert pagination["has_prev"] is False

    @pytest.mark.asyncio
    async def test_get_move_metrics_pagination(
        self, mock_move_service, sample_move_data
    ):
        """Test paginated metrics retrieval."""
        # Create move with many metrics
        move_with_many_metrics = {
            **sample_move_data,
            "daily_metrics": [
                {
                    "leads": i * 2,
                    "replies": i,
                    "confidence": 5 + i % 5,
                    "submitted_at": (datetime.utcnow() - timedelta(days=i)).isoformat(),
                }
                for i in range(35)
            ],
        }
        mock_move_service.get_move_detail.return_value = move_with_many_metrics

        with patch("api.v1.moves.get_move_service", return_value=mock_move_service):
            from api.v1.moves import get_move_metrics

            result = await get_move_metrics(
                move_id=sample_move_data["id"],
                page=2,
                page_size=15,
                days=30,
                tenant_id=uuid4(),
                _current_user={"id": "test_user"},
                service=mock_move_service,
            )

            assert result.success is True
            metrics = result.data["metrics"]
            pagination = result.data["pagination"]
            assert len(metrics) == 15  # Second page
            assert pagination["page"] == 2
            assert pagination["page_size"] == 15
            assert pagination["total"] == 30  # Last 30 days
            assert pagination["total_pages"] == 2
            assert pagination["has_next"] is False
            assert pagination["has_prev"] is True

    @pytest.mark.asyncio
    async def test_workspace_authorization(self, mock_move_service):
        """Test workspace-level authorization."""
        mock_move_service.get_move_detail.return_value = None

        with patch("api.v1.moves.get_move_service", return_value=mock_move_service):
            from fastapi import HTTPException

            from api.v1.moves import get_move_detail

            # Test with different tenant_id
            with pytest.raises(HTTPException) as exc_info:
                await get_move_detail(
                    move_id=str(uuid4()),
                    tenant_id=uuid4(),
                    _current_user={"id": "test_user"},
                    service=mock_move_service,
                )

            assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_error_handling_validation(self):
        """Test comprehensive error handling and validation."""
        from fastapi import HTTPException

        from api.v1.moves import get_move_metrics, get_move_tasks

        # Test invalid page numbers
        with pytest.raises(HTTPException) as exc_info:
            await get_move_tasks(
                move_id=str(uuid4()),
                page=0,
                page_size=10,
                tenant_id=uuid4(),
                _current_user={"id": "test_user"},
                service=AsyncMock(),
            )
        assert exc_info.value.status_code == 400
        assert "Page must be >= 1" in str(exc_info.value.detail)

        # Test invalid page size
        with pytest.raises(HTTPException) as exc_info:
            await get_move_tasks(
                move_id=str(uuid4()),
                page=1,
                page_size=101,
                tenant_id=uuid4(),
                _current_user={"id": "test_user"},
                service=AsyncMock(),
            )
        assert exc_info.value.status_code == 400
        assert "Page size must be between 1 and 100" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_rag_status_calculation(self, mock_move_service):
        """Test RAG status calculation logic."""
        from services.move_service import MoveService

        service = MoveService()

        # Test different RAG scenarios
        inactive_move = {"status": "draft", "started_at": None}
        rag_status, rag_reason = service._calculate_rag(inactive_move)
        assert rag_status == "green"
        assert rag_reason == "Ready to start"

        # Test low confidence
        low_confidence_move = {
            "status": "active",
            "started_at": "2024-01-01T00:00:00Z",
            "confidence": 3,
            "checklist": [{"completed": True}, {"completed": True}],
        }
        rag_status, rag_reason = service._calculate_rag(low_confidence_move)
        assert rag_status == "red"
        assert "Low confidence" in rag_reason

        # Test behind pace
        behind_pace_move = {
            "status": "active",
            "started_at": "2024-01-01T00:00:00Z",
            "confidence": 7,
            "checklist": [
                {"completed": True},
                {"completed": False},
                {"completed": False},
            ],
        }
        rag_status, rag_reason = service._calculate_rag(behind_pace_move)
        assert rag_status == "red"
        assert "Behind pace" in rag_reason
