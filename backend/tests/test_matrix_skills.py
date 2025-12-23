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
