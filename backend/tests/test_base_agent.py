"""
Test script to verify BaseAgent instantiation and LLM response.
"""

import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from agents.base import BaseAgent
from agents.config import ModelTier
from agents.state import create_initial_state
from pydantic import BaseModel


class TestAgent(BaseAgent):
    """Simple test agent for verification."""

    def get_system_prompt(self) -> str:
        return "You are a helpful test assistant. Respond briefly and clearly."

    async def execute(self, state):
        """Simple execution that echoes back the input."""
        # Extract user input
        user_input = self._extract_user_input(state)
        if not user_input:
            return self._set_error(state, "No user input found")

        # Generate response
        try:
            response = await self._call_llm(f"Echo this: {user_input}")
            return self._set_output(state, {"echo": response})
        except Exception as e:
            return self._set_error(state, str(e))


async def test_agent_instantiation():
    """Test that BaseAgent can be instantiated."""
    print("Testing BaseAgent instantiation...")

    try:
        agent = TestAgent(
            name="TestAgent",
            description="A simple test agent",
            model_tier=ModelTier.FLASH_LITE,
        )

        print(f"✓ Agent instantiated: {agent.name}")
        print(f"✓ Model tier: {agent.model_tier}")
        print(f"✓ System prompt: {agent.get_system_prompt()}")

        return agent
    except Exception as e:
        print(f"✗ Failed to instantiate agent: {e}")
        return None


async def test_llm_response(agent):
    """Test that LLM responds correctly."""
    print("\nTesting LLM response...")

    try:
        # Create test state
        state = create_initial_state(workspace_id="test-workspace", user_id="test-user")

        # Add user message
        state = agent._add_user_message(state, "Hello, this is a test message")

        # Execute agent
        result_state = await agent.execute(state)

        # Check result
        if result_state.get("error"):
            print(f"✗ Agent execution failed: {result_state['error']}")
            return False

        output = result_state.get("output")
        if output and "echo" in output:
            print(f"✓ LLM responded: {output['echo']}")
            return True
        else:
            print(f"✗ Unexpected output: {output}")
            return False

    except Exception as e:
        print(f"✗ LLM response test failed: {e}")
        return False


async def test_cost_tracking(agent):
    """Test that cost tracking works."""
    print("\nTesting cost tracking...")

    try:
        # Get usage before
        usage_before = agent.llm.get_usage()
        cost_before = agent.llm.get_total_cost()

        # Make a call
        state = create_initial_state(workspace_id="test-workspace", user_id="test-user")
        state = agent._add_user_message(state, "Test cost tracking")
        await agent.execute(state)

        # Get usage after
        usage_after = agent.llm.get_usage()
        cost_after = agent.llm.get_total_cost()

        if len(usage_after) > len(usage_before):
            print(f"✓ Usage tracked: {len(usage_after)} calls")
            print(f"✓ Cost tracked: ${cost_after:.6f}")
            return True
        else:
            print("✗ No usage tracked")
            return False

    except Exception as e:
        print(f"✗ Cost tracking test failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("=== BaseAgent and LLM Verification Tests ===\n")

    # Test instantiation
    agent = await test_agent_instantiation()
    if not agent:
        print("\n❌ Cannot proceed with LLM tests")
        return False

    # Test LLM response
    llm_test = await test_llm_response(agent)

    # Test cost tracking
    cost_test = await test_cost_tracking(agent)

    # Summary
    print("\n=== Test Summary ===")
    print(f"Agent Instantiation: ✓")
    print(f"LLM Response: {'✓' if llm_test else '✗'}")
    print(f"Cost Tracking: {'✓' if cost_test else '✗'}")

    if llm_test and cost_test:
        print("\n✅ All tests passed!")
        return True
    else:
        print("\n❌ Some tests failed")
        return False


if __name__ == "__main__":
    # Check for required environment variables
    required_vars = [
        "GCP_PROJECT_ID",
        "SUPABASE_URL",
        "SUPABASE_SERVICE_KEY",
        "UPSTASH_REDIS_URL",
        "UPSTASH_REDIS_TOKEN",
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these variables and run again.")
        sys.exit(1)

    # Run tests
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
