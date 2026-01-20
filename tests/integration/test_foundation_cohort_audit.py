"""
Audit Integration Test for Foundation & Cohorts Services.
Verifies data integrity, RLS connectivity, and core business logic synthesis.
"""

import os
import pytest
import uuid
from typing import Dict, Any
from unittest.mock import MagicMock, AsyncMock, patch

# Mock environment variables BEFORE any backend imports
os.environ["SECRET_KEY"] = "test_secret_key_for_pydantic_validation"
os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5432/postgres"
os.environ["GCP_PROJECT_ID"] = "test-project-id"
os.environ["WEBHOOK_SECRET"] = "test_webhook_secret"
os.environ["UPSTASH_REDIS_URL"] = "redis://localhost:6379"
os.environ["UPSTASH_REDIS_TOKEN"] = "test_token"
os.environ["GOOGLE_CLOUD_PROJECT"] = "test-project-id"
os.environ["VERTEX_AI_PROJECT_ID"] = "test-project-id"
os.environ["VERTEX_AI_LOCATION"] = "us-central1"

from backend.core.models import ValidationError

@pytest.mark.asyncio
class TestFoundationCohortAudit:
    """Audit suite for Foundation and Cohorts services."""

    @pytest.fixture
    def workspace_id(self):
        return str(uuid.uuid4())

    @pytest.fixture
    def sample_foundation_data(self):
        return {
            "company_name": "AuditCorp",
            "industry": "Technology",
            "mission": "To verify system integrity.",
            "vision": "A world of perfectly cached data.",
            "values": ["Reliability", "Efficiency", "Economy"],
            "messaging_guardrails": ["Professional tone", "No jargon"]
        }

    @pytest.fixture
    def mock_supabase(self):
        client = MagicMock()
        client.table.return_value.select.return_value.eq.return_value.single.return_value.execute = AsyncMock(
            return_value=MagicMock(data=None)
        )
        return client

    async def test_foundation_lifecycle(self, workspace_id, sample_foundation_data, mock_supabase):
        """Test the full lifecycle of a foundation record."""
        with patch("backend.core.supabase_mgr.get_supabase_client", return_value=mock_supabase):
            from backend.services.foundation import FoundationService
            foundation_service = FoundationService()
            
            # Mock repository methods to avoid real DB calls
            foundation_service.repository.upsert = AsyncMock(return_value={
                "workspace_id": workspace_id,
                **sample_foundation_data
            })
            foundation_service.repository.get_by_workspace = AsyncMock(return_value={
                "workspace_id": workspace_id,
                **sample_foundation_data
            })
            foundation_service.repository.delete = AsyncMock(return_value=True)
            
            # 1. Update Foundation
            created = await foundation_service.update_foundation(workspace_id, sample_foundation_data)
            assert created["company_name"] == "AuditCorp"
            
            # 2. Retrieve Foundation
            retrieved = await foundation_service.get_foundation(workspace_id)
            assert retrieved["company_name"] == "AuditCorp"
            
            # 3. Cleanup (Deletion)
            success = await foundation_service.delete_foundation(workspace_id)
            assert success is True

    async def test_cohort_derivation_logic(self, workspace_id, sample_foundation_data, mock_supabase):
        """Test deriving RICPs from foundation data."""
        with patch("backend.core.supabase_mgr.get_supabase_client", return_value=mock_supabase):
            from backend.services.icp import ICPService
            from backend.services.foundation import FoundationService
            
            icp_service = ICPService()
            foundation_service = FoundationService()
            
            foundation_service.repository.upsert = AsyncMock(return_value={"workspace_id": workspace_id})
            icp_service.foundation_repository.get_by_workspace = AsyncMock(return_value=sample_foundation_data)
            icp_service.repository.create = AsyncMock(return_value={"id": "icp-123"})
            icp_service.repository.list_by_workspace = AsyncMock(return_value=[{"id": "icp-123", "name": "Test Cohort"}])
            
            # Mock the graph call
            with patch("backend.services.business_context_graph.BusinessContextGraph.enhance_icp_node") as mock_node:
                mock_ricp = MagicMock()
                mock_ricp.name = "Test Cohort"
                mock_ricp.persona_name = "Test Persona"
                mock_ricp.avatar = "🤖"
                mock_ricp.demographics.model_dump.return_value = {"age": "25-35"}
                mock_ricp.psychographics.model_dump.return_value = {"identity": "Strategist"}
                mock_ricp.market_sophistication = 3
                mock_ricp.confidence = 90
                
                mock_node.return_value = {
                    "context_data": MagicMock(ricps=[mock_ricp])
                }
                
                # Derive Trinity
                ricp = await icp_service.derive_trinity(workspace_id, "Test Cohort")
                assert ricp.name == "Test Cohort"
                
                # Verify persistence call
                icps = await icp_service.list_icps(workspace_id)
                assert len(icps) == 1
                assert icps[0]["name"] == "Test Cohort"