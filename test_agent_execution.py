#!/usr/bin/env python3
"""
Red Team Test 1: Agent Execution Chain Test
Tests if agents can execute basic requests without crashing
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from agents.base import BaseAgent
from agents.config import ModelTier
from agents.state import AgentState

class TestAgent(BaseAgent):
    """Simple test agent to verify execution chain."""
    
    def __init__(self):
        super().__init__(
            name="TestAgent",
            description="Test agent for red team verification",
            model_tier=ModelTier.FLASH_LITE
        )
    
    def get_system_prompt(self) -> str:
        return "You are a test agent. Respond briefly with 'Test successful'."
    
    async def execute(self, state: AgentState) -> AgentState:
        try:
            # Test basic LLM call
            response = await self._call_llm("Say 'test successful'")
            
            # Set output
            state = self._set_output(state, response)
            return state
            
        except Exception as e:
            state = self._set_error(state, f"Execution failed: {str(e)}")
            return state

async def test_agent_execution():
    """Test agent execution chain."""
    print("🔴 RED TEAM TEST 1: Agent Execution Chain")
    print("=" * 50)
    
    try:
        # Create test agent
        agent = TestAgent()
        print(f"✅ Agent created: {agent.name}")
        
        # Create test state
        test_state = AgentState(
            workspace_id="test_workspace",
            user_id="test_user", 
            session_id="test_session",
            messages=[{"role": "user", "content": "test request"}]
        )
        print("✅ Test state created")
        
        # Execute agent
        print("🚀 Executing agent...")
        result_state = await agent.execute(test_state)
        
        # Check results
        if result_state.get("error"):
            print(f"❌ FAILED: {result_state['error']}")
            return False
        elif result_state.get("output"):
            print(f"✅ SUCCESS: Agent executed successfully")
            print(f"📤 Output: {result_state['output'][:100]}...")
            return True
        else:
            print("❌ FAILED: No output or error")
            return False
            
    except Exception as e:
        print(f"❌ CRITICAL FAILURE: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_agent_execution())
    print(f"\n🎯 RESULT: {'PASS' if result else 'FAIL'}")
    sys.exit(0 if result else 1)
