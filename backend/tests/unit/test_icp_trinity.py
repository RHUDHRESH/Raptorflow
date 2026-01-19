import pytest
import json
import os
from unittest.mock import AsyncMock, MagicMock, patch

# Set dummy env vars for Supabase to avoid initialization error
os.environ["SUPABASE_URL"] = "https://example.supabase.co"
os.environ["SUPABASE_ANON_KEY"] = "dummy-key"

from backend.services.icp import ICPService
from backend.schemas import RICP, RICPDemographics, RICPPsychographics, BusinessContextState

@pytest.mark.asyncio
async def test_derive_trinity_success():
    """Test derive_trinity successfully generates and saves an RICP."""
    
    # Mocking Supabase and Repositories before initializing ICPService
    with patch('backend.core.supabase.get_supabase_client', return_value=MagicMock()), \
         patch('backend.db.icps.ICPRepository.__init__', return_value=None), \
         patch('backend.db.foundations.FoundationRepository.__init__', return_value=None), \
         patch('backend.services.business_context_graph.get_business_context_graph', return_value=MagicMock()):
        
        icp_service = ICPService()
        workspace_id = "test-ws-123"
        cohort_name = "Tech Founders"
        
        # Mock foundation repository
        icp_service.foundation_repository.get_by_workspace = AsyncMock(return_value={
            "company_name": "Test Co",
            "industry": "Software"
        })
        
        # Mock graph enhancement
        mock_ricp = RICP(
            name=cohort_name,
            persona_name="Sarah",
            avatar="👩‍💻",
            demographics=RICPDemographics(role="CEO"),
            psychographics=RICPPsychographics(beliefs="Efficiency is key"),
            market_sophistication=3,
            confidence=95
        )
        
        # Create a mock result state
        mock_state = {
            "context_data": BusinessContextState(ricps=[mock_ricp])
        }
        
        icp_service.graph.enhance_icp_node = AsyncMock(return_value=mock_state)
        icp_service.repository.create = AsyncMock(return_value={"id": "new-uuid-123"})
        
        result = await icp_service.derive_trinity(workspace_id, cohort_name)
        
        assert result.name == cohort_name
        assert result.persona_name == "Sarah"
        assert result.id == "new-uuid-123"
        assert icp_service.repository.create.called
        
        # Verify db_data mapping
        args, _ = icp_service.repository.create.call_args
        db_data = args[1]
        assert db_data["name"] == cohort_name
        assert db_data["persona_name"] == "Sarah"
        assert db_data["market_sophistication"]["stage"] == 3