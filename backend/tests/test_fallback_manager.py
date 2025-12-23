import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from backend.core.fallback import FallbackManager

@pytest.mark.asyncio
async def test_fallback_manager_trigger():
    """Verify that fallback is triggered when LLM call fails."""
    # We want a wrapper that tries a callable and falls back on error
    manager = FallbackManager()
    
    async def failing_llm_call():
        raise Exception("LLM Timeout")
        
    fallback_response = {"thought": "Heuristic fallback", "action": "wait"}
    
    result = await manager.execute_with_fallback(
        failing_llm_call,
        fallback_value=fallback_response
    )
    
    assert result == fallback_response
    assert result["thought"] == "Heuristic fallback"

@pytest.mark.asyncio
async def test_fallback_manager_success():
    """Verify that original result is returned when LLM call succeeds."""
    manager = FallbackManager()
    
    async def successful_llm_call():
        return {"thought": "SOTA reasoning", "action": "execute"}
        
    result = await manager.execute_with_fallback(
        successful_llm_call,
        fallback_value={"thought": "fallback"}
    )
    
    assert result["thought"] == "SOTA reasoning"
