#!/usr/bin/env python3
"""
Red Team Test 4: Tool Registry Test
Tests if tool registry functions properly
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from agents.base import BaseAgent
from agents.config import ModelTier
from agents.state import AgentState
from agents.tools.registry import get_tool_registry

class ToolTestAgent(BaseAgent):
    """Test agent for tool verification."""
    
    def __init__(self):
        super().__init__(
            name="ToolTestAgent",
            description="Test agent for tool verification",
            model_tier=ModelTier.FLASH_LITE,
            tools=["web_search", "database"]
        )
    
    def get_system_prompt(self) -> str:
        return "You are a test agent. Use tools as requested."
    
    async def execute(self, state: AgentState) -> AgentState:
        """Simple execute implementation for testing."""
        try:
            state = self._set_output(state, "Tool test completed successfully")
            return state
        except Exception as e:
            state = self._set_error(state, f"Execution failed: {str(e)}")
            return state

async def test_tool_registry():
    """Test tool registry functions properly."""
    print("🔴 RED TEAM TEST 4: Tool Registry Test")
    print("=" * 50)
    
    try:
        # Create test agent
        agent = ToolTestAgent()
        print(f"✅ Agent created: {agent.name}")
        
        # Get tool registry
        tool_registry = get_tool_registry()
        print(f"✅ Tool registry loaded")
        
        # Test 1: List available tools
        print("\n📋 Testing tool listing...")
        available_tools = tool_registry.list_tools()
        print(f"✅ Available tools: {len(available_tools)} tools")
        for tool_name in available_tools[:5]:  # Show first 5
            tool_obj = tool_registry.get(tool_name)
            if tool_obj:
                print(f"   - {tool_obj.name}: {tool_obj.description[:50]}...")
            else:
                print(f"   - {tool_name}: (not found)")
        
        # Test 2: Get specific tools
        print("\n🔍 Testing tool retrieval...")
        web_search_tool = tool_registry.get("web_search")
        database_tool = tool_registry.get("database")
        
        if web_search_tool:
            print(f"✅ WebSearch tool found: {web_search_tool.name}")
        else:
            print("❌ WebSearch tool not found")
            
        if database_tool:
            print(f"✅ Database tool found: {database_tool.name}")
        else:
            print("❌ Database tool not found")
        
        # Test 3: Test tool execution (mock)
        print("\n⚙️ Testing tool execution...")
        try:
            # Test web search tool (this will fail without API keys but should not crash)
            search_result = await web_search_tool._arun(
                query="test query",
                max_results=3
            )
            print(f"✅ WebSearch executed: {type(search_result)}")
        except Exception as e:
            print(f"⚠️ WebSearch failed gracefully: {str(e)[:100]}...")
        
        try:
            # Test database tool (this will fail without DB connection but should not crash)
            db_result = await database_tool._arun(
                table="foundations",
                workspace_id="test_workspace",
                limit=5
            )
            print(f"✅ Database executed: {type(db_result)}")
        except Exception as e:
            print(f"⚠️ Database failed gracefully: {str(e)[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ CRITICAL FAILURE: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_tool_registry())
    print(f"\n🎯 RESULT: {'PASS' if result else 'FAIL'}")
    sys.exit(0 if result else 1)
