import pytest
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
    from unittest.mock import AsyncMock
    
    mock_matrix = AsyncMock(spec=MatrixService)
    mock_matrix.halt_system.return_value = True
    skill = EmergencyHaltSkill(matrix_service=mock_matrix)
    
    result = await skill.execute({"reason": "Test engagement"})
    assert result["halt_engaged"] is True
    assert mock_matrix.halt_system.called
