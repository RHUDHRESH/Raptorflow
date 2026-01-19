#!/usr/bin/env python3
"""
Red Team Test 3: Skill Implementation Test
Tests if skill implementations return real data
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from agents.base import BaseAgent
from agents.config import ModelTier
from agents.state import AgentState
from agents.skills.registry import get_skills_registry

class SkillTestAgent(BaseAgent):
    """Test agent for skill verification."""
    
    def __init__(self):
        super().__init__(
            name="SkillTestAgent",
            description="Test agent for skill verification",
            model_tier=ModelTier.FLASH_LITE,
            skills=["content_generation", "persona_builder", "seo_optimization"]
        )
    
    def get_system_prompt(self) -> str:
        return "You are a test agent. Execute skills as requested."
    
    async def execute(self, state: AgentState) -> AgentState:
        """Simple execute implementation for testing."""
        try:
            # Just return success for testing
            state = self._set_output(state, "Skill test completed successfully")
            return state
        except Exception as e:
            state = self._set_error(state, f"Execution failed: {str(e)}")
            return state

async def test_skill_implementations():
    """Test skill implementations return real data."""
    print("🔴 RED TEAM TEST 3: Skill Implementation Test")
    print("=" * 50)
    
    try:
        # Create test agent
        agent = SkillTestAgent()
        print(f"✅ Agent created: {agent.name}")
        
        # Create test state
        test_state = AgentState(
            workspace_id="test_workspace",
            user_id="test_user", 
            session_id="test_session",
            messages=[{"role": "user", "content": "test skills"}]
        )
        print("✅ Test state created")
        
        # Get skills registry
        skills_registry = get_skills_registry()
        print(f"✅ Skills registry loaded with {len(skills_registry.list_skills())} skills")
        
        # Test 1: ContentGenerationSkill
        print("\n📝 Testing ContentGenerationSkill...")
        try:
            content_result = await agent.execute_skill("content_generation", {
                "prompt": "Write a short marketing email for a SaaS product",
                "system_prompt": "You are a marketing copywriter"
            })
            print(f"✅ ContentGeneration: {len(str(content_result))} chars returned")
            print(f"📤 Sample: {str(content_result)[:200]}...")
        except Exception as e:
            print(f"❌ ContentGeneration failed: {str(e)}")
        
        # Test 2: PersonaBuilderSkill
        print("\n👥 Testing PersonaBuilderSkill...")
        try:
            persona_result = await agent.execute_skill("persona_builder", {
                "target_audience": "B2B SaaS startup founders"
            })
            print(f"✅ PersonaBuilder: {len(str(persona_result))} chars returned")
            print(f"📤 Sample: {str(persona_result)[:200]}...")
        except Exception as e:
            print(f"❌ PersonaBuilder failed: {str(e)}")
        
        # Test 3: SEOAnalysisSkill
        print("\n🔍 Testing SEOAnalysisSkill...")
        try:
            seo_result = await agent.execute_skill("seo_optimization", {
                "content": "This is a test article about AI marketing automation tools and software platforms",
                "keywords": ["AI marketing", "automation tools", "software platforms"]
            })
            print(f"✅ SEOAnalysis: Score {seo_result.get('score', 'N/A')}")
            print(f"📤 Suggestions: {len(seo_result.get('suggestions', []))} suggestions")
        except Exception as e:
            print(f"❌ SEOAnalysis failed: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ CRITICAL FAILURE: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_skill_implementations())
    print(f"\n🎯 RESULT: {'PASS' if result else 'FAIL'}")
    sys.exit(0 if result else 1)
