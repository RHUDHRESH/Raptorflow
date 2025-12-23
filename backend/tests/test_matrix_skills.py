import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from backend.skills.matrix_skills import MatrixSkill, SkillRegistry

class MockSkill(MatrixSkill):
    @property
    def name(self) -> str:
        return "mock_skill"
    async def execute(self, params: dict) -> dict:
        return {"status": "executed"}

def test_skill_registration():
    """Test registering and retrieving skills."""
    registry = SkillRegistry()
    skill = MockSkill()
    registry.register(skill)
    assert registry.get("mock_skill") == skill
    assert "mock_skill" in registry.list_skills()

@pytest.mark.asyncio
async def test_skill_execution():
    """Test the base skill execution interface."""
    skill = MockSkill()
    result = await skill.execute({})
    assert result["status"] == "executed"

@pytest.mark.asyncio
async def test_emergency_halt_skill():
    """Test that the EmergencyHaltSkill engages the kill-switch."""
    from backend.skills.matrix_skills import EmergencyHaltSkill
    from backend.services.matrix_service import MatrixService
    mock_matrix = AsyncMock(spec=MatrixService)
    mock_matrix.halt_system.return_value = True
    skill = EmergencyHaltSkill(matrix_service=mock_matrix)
    result = await skill.execute({"reason": "Test engagement"})
    assert result["halt_engaged"] is True
    assert mock_matrix.halt_system.called

@pytest.mark.asyncio
async def test_emergency_halt_skill_failure():
    """Test EmergencyHaltSkill when MatrixService fails to halt."""
    from backend.skills.matrix_skills import EmergencyHaltSkill
    from backend.services.matrix_service import MatrixService
    
    mock_matrix = AsyncMock(spec=MatrixService)
    mock_matrix.halt_system.return_value = False
    skill = EmergencyHaltSkill(matrix_service=mock_matrix)
    
    result = await skill.execute({"reason": "Fail test"})
    assert result["halt_engaged"] is False
    assert result["status"] == "failed_to_halt"

@pytest.mark.asyncio
async def test_inference_throttling_skill():
    """Test that the InferenceThrottlingSkill updates rate limits."""
    from backend.skills.matrix_skills import InferenceThrottlingSkill
    mock_redis = AsyncMock()
    mock_redis.set.return_value = True
    skill = InferenceThrottlingSkill(redis_client=mock_redis)
    result = await skill.execute({"agent_id": "test_agent", "tpm_limit": 5000})
    assert result["throttling_applied"] is True
    assert mock_redis.set.called

@pytest.mark.asyncio
async def test_inference_throttling_skill_no_agent():
    """Test throttling skill when agent_id is missing."""
    from backend.skills.matrix_skills import InferenceThrottlingSkill
    skill = InferenceThrottlingSkill(redis_client=MagicMock())
    result = await skill.execute({})
    assert "error" in result

@pytest.mark.asyncio
async def test_inference_throttling_skill_exception():
    """Test throttling skill when redis raises exception."""
    from backend.skills.matrix_skills import InferenceThrottlingSkill
    mock_redis = AsyncMock()
    mock_redis.set.side_effect = Exception("Redis failure")
    skill = InferenceThrottlingSkill(redis_client=mock_redis)
    result = await skill.execute({"agent_id": "test"})
    assert result is False

@pytest.mark.asyncio
async def test_cache_purge_skill():
    """Test that the CachePurgeSkill clears keys."""
    from backend.skills.matrix_skills import CachePurgeSkill
    mock_redis = AsyncMock()
    mock_redis.delete.return_value = 1
    skill = CachePurgeSkill(redis_client=mock_redis)
    result = await skill.execute({"pattern": "throttle:*"})
    assert result["purge_successful"] is True
    assert mock_redis.delete.called

@pytest.mark.asyncio
async def test_cache_purge_skill_exception():
    """Test purge skill when redis fails."""
    from backend.skills.matrix_skills import CachePurgeSkill
    mock_redis = AsyncMock()
    mock_redis.delete.side_effect = Exception("Purge error")
    skill = CachePurgeSkill(redis_client=mock_redis)
    result = await skill.execute({})
    assert result is False