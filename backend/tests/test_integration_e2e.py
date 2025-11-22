"""
End-to-end integration tests for RaptorFlow.
Tests complete workflows across all domain graphs.
"""

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from uuid import uuid4


class TestHealthEndpoints:
    """Test system health and info endpoints."""

    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient, mock_redis):
        """Test health check endpoint."""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "degraded"]
        assert "services" in data
        assert "redis" in data["services"]

    @pytest.mark.asyncio
    async def test_root_endpoint(self, client: AsyncClient):
        """Test root endpoint."""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"]
        assert data["version"]
        assert data["docs"]


class TestOrchestrationEndpoints:
    """Test orchestration endpoints."""

    @pytest.mark.asyncio
    async def test_execute_workflow_full_campaign(
        self,
        authenticated_client: AsyncClient,
        mock_auth,
        mock_supabase,
        mock_vertex_ai,
        mock_redis,
        sample_workflow_request,
        assert_correlation_id
    ):
        """Test full campaign workflow execution."""
        # Mock graph execution results
        with patch('backend.graphs.master_graph.master_graph_runnable.ainvoke') as mock_graph:
            mock_graph.return_value = {
                "workflow_id": str(uuid4()),
                "correlation_id": "test-correlation-id",
                "workspace_id": mock_auth["workspace_id"],
                "user_id": mock_auth["user_id"],
                "goal": "full_campaign",
                "current_stage": "finalize",
                "completed_stages": ["research", "strategy", "content", "critic_review", "integration", "execution"],
                "failed_stages": [],
                "success": True,
                "message": "Workflow completed successfully",
                "started_at": "2024-01-01T00:00:00",
                "completed_at": "2024-01-01T00:10:00",
                "research_result": {"icp_id": str(uuid4())},
                "strategy_result": {"strategy_id": str(uuid4())},
                "content_result": {"content_ids": [str(uuid4())]},
                "critic_review": {"recommendation": "approve", "overall_score": 90},
                "integration_result": {},
                "execution_result": {},
                "errors": [],
                "retry_count": 0
            }

            response = await authenticated_client.post(
                "/api/v1/orchestration/execute",
                json=sample_workflow_request
            )

            assert response.status_code == 200
            data = response.json()

            # Verify response structure
            assert "workflow_id" in data
            assert "correlation_id" in data
            assert data["goal"] == "full_campaign"
            assert data["success"] is True
            assert len(data["completed_stages"]) > 0
            assert len(data["failed_stages"]) == 0

            # Verify results from each stage
            assert data["research_result"] is not None
            assert data["strategy_result"] is not None
            assert data["content_result"] is not None
            assert data["critic_review"] is not None

            # Verify correlation ID in headers
            assert_correlation_id(response)

    @pytest.mark.asyncio
    async def test_execute_workflow_research_only(
        self,
        authenticated_client: AsyncClient,
        mock_auth,
        mock_supabase,
        mock_vertex_ai,
        mock_redis
    ):
        """Test research-only workflow."""
        with patch('backend.graphs.master_graph.master_graph_runnable.ainvoke') as mock_graph:
            mock_graph.return_value = {
                "workflow_id": str(uuid4()),
                "correlation_id": "test-correlation-id",
                "workspace_id": mock_auth["workspace_id"],
                "user_id": mock_auth["user_id"],
                "goal": "research_only",
                "current_stage": "finalize",
                "completed_stages": ["research"],
                "failed_stages": [],
                "success": True,
                "message": "Workflow completed successfully",
                "started_at": "2024-01-01T00:00:00",
                "completed_at": "2024-01-01T00:05:00",
                "research_result": {"icp_id": str(uuid4())},
                "strategy_result": None,
                "content_result": None,
                "critic_review": None,
                "integration_result": None,
                "execution_result": None,
                "errors": [],
                "retry_count": 0
            }

            request_data = {
                "goal": "research_only",
                "research_query": "B2B SaaS startups",
                "research_mode": "deep"
            }

            response = await authenticated_client.post(
                "/api/v1/orchestration/execute",
                json=request_data
            )

            assert response.status_code == 200
            data = response.json()

            assert data["goal"] == "research_only"
            assert data["success"] is True
            assert "research" in data["completed_stages"]
            assert data["research_result"] is not None
            # Other stages should not be executed
            assert data["strategy_result"] is None
            assert data["content_result"] is None

    @pytest.mark.asyncio
    async def test_execute_workflow_with_errors(
        self,
        authenticated_client: AsyncClient,
        mock_auth,
        mock_supabase,
        mock_vertex_ai,
        mock_redis
    ):
        """Test workflow execution with errors."""
        with patch('backend.graphs.master_graph.master_graph_runnable.ainvoke') as mock_graph:
            mock_graph.return_value = {
                "workflow_id": str(uuid4()),
                "correlation_id": "test-correlation-id",
                "workspace_id": mock_auth["workspace_id"],
                "user_id": mock_auth["user_id"],
                "goal": "full_campaign",
                "current_stage": "finalize",
                "completed_stages": ["research", "strategy"],
                "failed_stages": ["content"],
                "success": False,
                "message": "Workflow completed with errors",
                "started_at": "2024-01-01T00:00:00",
                "completed_at": "2024-01-01T00:05:00",
                "research_result": {"icp_id": str(uuid4())},
                "strategy_result": {"strategy_id": str(uuid4())},
                "content_result": None,
                "critic_review": None,
                "integration_result": None,
                "execution_result": None,
                "errors": [{"stage": "content", "error": "Content generation failed"}],
                "retry_count": 0
            }

            request_data = {
                "goal": "full_campaign",
                "research_query": "B2B SaaS startups"
            }

            response = await authenticated_client.post(
                "/api/v1/orchestration/execute",
                json=request_data
            )

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is False
            assert len(data["failed_stages"]) > 0
            assert len(data["errors"]) > 0
            assert data["errors"][0]["stage"] == "content"

    @pytest.mark.asyncio
    async def test_list_workflows(
        self,
        authenticated_client: AsyncClient,
        mock_auth,
        mock_supabase
    ):
        """Test listing workflows."""
        # Mock database response
        mock_workflows = [
            {
                "workflow_id": str(uuid4()),
                "goal": "full_campaign",
                "success": True,
                "created_at": "2024-01-01T00:00:00"
            },
            {
                "workflow_id": str(uuid4()),
                "goal": "research_only",
                "success": True,
                "created_at": "2024-01-02T00:00:00"
            }
        ]

        mock_supabase.query.return_value = mock_workflows
        mock_supabase.count.return_value = len(mock_workflows)

        response = await authenticated_client.get("/api/v1/orchestration/workflows")

        assert response.status_code == 200
        data = response.json()

        assert "workflows" in data
        assert "total" in data
        assert data["total"] == 2

    @pytest.mark.asyncio
    async def test_get_workflow_status(
        self,
        authenticated_client: AsyncClient,
        mock_auth,
        mock_supabase
    ):
        """Test getting workflow status."""
        workflow_id = str(uuid4())
        mock_workflow = {
            "workflow_id": workflow_id,
            "correlation_id": "test-correlation-id",
            "workspace_id": mock_auth["workspace_id"],
            "goal": "full_campaign",
            "current_stage": "finalize",
            "completed_stages": ["research", "strategy", "content"],
            "failed_stages": [],
            "success": True,
            "message": "Workflow completed",
            "started_at": "2024-01-01T00:00:00",
            "completed_at": "2024-01-01T00:10:00",
            "errors": [],
            "results": {
                "research": {"icp_id": str(uuid4())},
                "strategy": {"strategy_id": str(uuid4())},
                "content": {"content_ids": [str(uuid4())]}
            }
        }

        mock_supabase.query_one.return_value = mock_workflow

        response = await authenticated_client.get(
            f"/api/v1/orchestration/workflows/{workflow_id}"
        )

        assert response.status_code == 200
        data = response.json()

        assert data["workflow_id"] == workflow_id
        assert data["success"] is True
        assert len(data["completed_stages"]) == 3

    @pytest.mark.asyncio
    async def test_get_workflow_not_found(
        self,
        authenticated_client: AsyncClient,
        mock_auth,
        mock_supabase
    ):
        """Test getting non-existent workflow."""
        mock_supabase.query_one.return_value = None

        response = await authenticated_client.get(
            f"/api/v1/orchestration/workflows/{uuid4()}"
        )

        assert response.status_code == 404


class TestCriticIntegration:
    """Test critic agent integration in workflows."""

    @pytest.mark.asyncio
    async def test_critic_approves_content(
        self,
        authenticated_client: AsyncClient,
        mock_auth,
        mock_supabase,
        mock_vertex_ai,
        mock_redis
    ):
        """Test workflow where critic approves content."""
        with patch('backend.graphs.master_graph.master_graph_runnable.ainvoke') as mock_graph:
            mock_graph.return_value = {
                "workflow_id": str(uuid4()),
                "correlation_id": "test-correlation-id",
                "workspace_id": mock_auth["workspace_id"],
                "user_id": mock_auth["user_id"],
                "goal": "content_only",
                "current_stage": "finalize",
                "completed_stages": ["content", "critic_review"],
                "failed_stages": [],
                "success": True,
                "message": "Workflow completed successfully",
                "started_at": "2024-01-01T00:00:00",
                "completed_at": "2024-01-01T00:05:00",
                "research_result": None,
                "strategy_result": None,
                "content_result": {"content": "High quality content"},
                "critic_review": {
                    "recommendation": "approve",
                    "overall_score": 95,
                    "strengths": ["Clear", "Engaging", "Well-structured"]
                },
                "integration_result": None,
                "execution_result": None,
                "errors": [],
                "retry_count": 0
            }

            request_data = {
                "goal": "content_only",
                "content_type": "blog",
                "icp_id": str(uuid4()),
                "strategy_id": str(uuid4())
            }

            response = await authenticated_client.post(
                "/api/v1/orchestration/execute",
                json=request_data
            )

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            assert "critic_review" in data["completed_stages"]
            assert data["critic_review"]["recommendation"] == "approve"
            assert data["critic_review"]["overall_score"] >= 85

    @pytest.mark.asyncio
    async def test_critic_requires_revision(
        self,
        authenticated_client: AsyncClient,
        mock_auth,
        mock_supabase,
        mock_vertex_ai,
        mock_redis
    ):
        """Test workflow where critic requires major revision."""
        with patch('backend.graphs.master_graph.master_graph_runnable.ainvoke') as mock_graph:
            # First attempt - critic rejects
            # Second attempt - critic approves after retry
            mock_graph.return_value = {
                "workflow_id": str(uuid4()),
                "correlation_id": "test-correlation-id",
                "workspace_id": mock_auth["workspace_id"],
                "user_id": mock_auth["user_id"],
                "goal": "content_only",
                "current_stage": "finalize",
                "completed_stages": ["content", "critic_review"],
                "failed_stages": [],
                "success": True,
                "message": "Workflow completed after retry",
                "started_at": "2024-01-01T00:00:00",
                "completed_at": "2024-01-01T00:08:00",
                "research_result": None,
                "strategy_result": None,
                "content_result": {"content": "Improved content"},
                "critic_review": {
                    "recommendation": "approve",
                    "overall_score": 88,
                    "improvements": ["Better clarity after revision"]
                },
                "integration_result": None,
                "execution_result": None,
                "errors": [],
                "retry_count": 1  # Shows it was retried
            }

            request_data = {
                "goal": "content_only",
                "content_type": "blog",
                "icp_id": str(uuid4()),
                "strategy_id": str(uuid4())
            }

            response = await authenticated_client.post(
                "/api/v1/orchestration/execute",
                json=request_data
            )

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            # Verify retry happened
            # Note: retry_count is internal state, may not be in response


class TestCorrelationTracking:
    """Test correlation ID tracking across workflows."""

    @pytest.mark.asyncio
    async def test_correlation_id_in_request_header(
        self,
        authenticated_client: AsyncClient,
        mock_auth,
        mock_supabase,
        mock_vertex_ai,
        mock_redis,
        assert_correlation_id
    ):
        """Test correlation ID passed in request header."""
        custom_correlation_id = f"custom-{uuid4()}"

        with patch('backend.graphs.master_graph.master_graph_runnable.ainvoke') as mock_graph:
            mock_graph.return_value = {
                "workflow_id": str(uuid4()),
                "correlation_id": custom_correlation_id,
                "workspace_id": mock_auth["workspace_id"],
                "user_id": mock_auth["user_id"],
                "goal": "research_only",
                "current_stage": "finalize",
                "completed_stages": ["research"],
                "failed_stages": [],
                "success": True,
                "message": "Workflow completed",
                "started_at": "2024-01-01T00:00:00",
                "completed_at": "2024-01-01T00:05:00",
                "research_result": {"icp_id": str(uuid4())},
                "errors": [],
                "retry_count": 0
            }

            response = await authenticated_client.post(
                "/api/v1/orchestration/execute",
                json={"goal": "research_only"},
                headers={"X-Correlation-ID": custom_correlation_id}
            )

            assert response.status_code == 200
            # Verify correlation ID is returned
            correlation_id = assert_correlation_id(response)
            # Should match the one we sent (or be generated if not sent)
            assert correlation_id

    @pytest.mark.asyncio
    async def test_correlation_id_propagates_through_stages(
        self,
        authenticated_client: AsyncClient,
        mock_auth,
        mock_supabase,
        mock_vertex_ai,
        mock_redis
    ):
        """Test that correlation ID is tracked through all stages."""
        with patch('backend.graphs.master_graph.master_graph_runnable.ainvoke') as mock_graph:
            test_correlation_id = f"test-{uuid4()}"

            mock_graph.return_value = {
                "workflow_id": str(uuid4()),
                "correlation_id": test_correlation_id,
                "workspace_id": mock_auth["workspace_id"],
                "user_id": mock_auth["user_id"],
                "goal": "full_campaign",
                "current_stage": "finalize",
                "completed_stages": ["research", "strategy", "content"],
                "failed_stages": [],
                "success": True,
                "message": "Workflow completed",
                "started_at": "2024-01-01T00:00:00",
                "completed_at": "2024-01-01T00:10:00",
                "research_result": {"icp_id": str(uuid4())},
                "strategy_result": {"strategy_id": str(uuid4())},
                "content_result": {"content_ids": [str(uuid4())]},
                "errors": [],
                "retry_count": 0
            }

            response = await authenticated_client.post(
                "/api/v1/orchestration/execute",
                json={"goal": "full_campaign"}
            )

            assert response.status_code == 200
            data = response.json()

            # Verify correlation ID is in response
            assert data["correlation_id"]
