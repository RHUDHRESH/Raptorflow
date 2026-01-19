import pytest
import os
import yaml
from unittest.mock import MagicMock, patch

# Mock LLMCache before importing UniversalAgent to avoid Redis initialization
with patch('backend.llm.LLMCache'):
    from backend.agents.universal.agent import UniversalAgent
    from backend.llm import LLMResponse

@pytest.mark.asyncio
async def test_universal_agent_load_skill():
    """Test that the agent can load a skill from YAML."""
    with patch('backend.llm.LLMCache'):
        agent = UniversalAgent()
        skill_def = agent.registry.get_skill("hello_world")
        
        assert skill_def.metadata.name == "hello_world"
        assert skill_def.prompt is not None

@pytest.mark.asyncio
async def test_universal_agent_run_step_mock(mocker):
    """Test running a step with a mocked LLM response."""
    with patch('backend.llm.LLMCache'):
        agent = UniversalAgent()
        
        # Mock llm_manager.generate
        mock_response = LLMResponse(
            content="Hello Test Corp! I am ready for Step 1.",
            model="gemini-1.5-pro"
        )
        
        mocker.patch("backend.agents.universal.agent.llm_manager.generate", return_value=mock_response)
        
        input_data = {
            "company_name": "Test Corp",
            "step_name": "Step 1"
        }
        
        result = await agent.run_step("hello_world", input_data)
        
@pytest.mark.asyncio
async def test_universal_agent_load_all_initial_skills():
    """Test that all initial 5 onboarding skills can be loaded and validated."""
    with patch('backend.llm.LLMCache'):
        agent = UniversalAgent()
        skills = ["evidence_vault", "fact_extraction", "contradiction_detection", "truth_sheet", "pricing_analysis"]
        
        for skill_name in skills:
            skill_def = agent.registry.get_skill(skill_name)
            assert skill_def.metadata.name == skill_name
            assert skill_def.prompt is not None
            assert skill_def.parameters.get("temperature") is not None
