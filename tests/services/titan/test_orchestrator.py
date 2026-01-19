import pytest
import os
import json
from unittest.mock import AsyncMock, MagicMock, patch

# Set mock environment variables for Pydantic Settings
os.environ["RAPTORFLOW_SKIP_INIT"] = "true"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost:5432/db"
os.environ["UPSTASH_REDIS_URL"] = "https://test.upstash.io"
os.environ["UPSTASH_REDIS_TOKEN"] = "test-token"
os.environ["VERTEX_AI_PROJECT_ID"] = "test-project"
os.environ["GCP_PROJECT_ID"] = "test-project"
os.environ["WEBHOOK_SECRET"] = "test-webhook-secret"

# Import after setting env vars
from backend.services.titan.orchestrator import TitanOrchestrator
from backend.services.titan.tool import TitanIntelligenceTool
from backend.tools.base import ToolValidationError

@pytest.mark.asyncio
async def test_titan_orchestrator_initialization():
    # Mock SOTASearchOrchestrator to avoid initialization issues
    with patch("backend.services.titan.orchestrator.SOTASearchOrchestrator"):
        orchestrator = TitanOrchestrator()
        assert orchestrator is not None

@pytest.mark.asyncio
async def test_titan_orchestrator_lite_mode():
    # Mock SOTASearchOrchestrator
    mock_search = MagicMock()
    mock_search.query = AsyncMock(return_value=[{"url": "https://lite.com", "title": "Lite Result"}])
    mock_search.close = AsyncMock()

    with patch("backend.services.titan.orchestrator.SOTASearchOrchestrator", return_value=mock_search):
        orchestrator = TitanOrchestrator()
        results = await orchestrator.execute(query="test company", mode="LITE")
        
        assert "lite.com" in str(results)
        mock_search.query.assert_called_once()

@pytest.mark.asyncio
async def test_titan_orchestrator_invalid_mode():
    with patch("backend.services.titan.orchestrator.SOTASearchOrchestrator"):
        orchestrator = TitanOrchestrator()
        with pytest.raises(ValueError, match="Invalid mode"):
            await orchestrator.execute(query="test", mode="INVALID")
@pytest.mark.asyncio
async def test_titan_tool_validation():
    tool = TitanIntelligenceTool()
    
    # Missing query
    with pytest.raises(ToolValidationError):
        tool._validate_input({})
        
    # Invalid mode
    with pytest.raises(ToolValidationError):
        tool._validate_input({"query": "test", "mode": "INVALID"})
        
    # Valid input
    tool._validate_input({"query": "test", "mode": "RESEARCH"})

@pytest.mark.asyncio
async def test_titan_tool_execution():
    mock_orchestrator = AsyncMock()
    mock_orchestrator.execute.return_value = {"results": [], "mode": "LITE"}
    mock_orchestrator.close = AsyncMock()
    
    tool = TitanIntelligenceTool()
    with patch.object(tool, "_get_orchestrator", return_value=mock_orchestrator):
        result = await tool._execute(query="test company", mode="LITE")
        assert result["mode"] == "LITE"
        assert "engine" in result
        mock_orchestrator.execute.assert_called_once()
