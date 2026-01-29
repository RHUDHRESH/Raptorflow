"""
Test script to verify BaseAgent instantiation and LLM response.
"""

import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from pydantic import BaseModel

from .agents.base import BaseAgent
from .agents.config import ModelTier
from .agents.state import create_initial_state


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

        print(f"Γ£ô Agent instantiated: {agent.name}")
        print(f"Γ£ô Model tier: {agent.model_tier}")
        print(f"Γ£ô System prompt: {agent.get_system_prompt()}")

        return agent
    except Exception as e:
        print(f"Γ£ù Failed to instantiate agent: {e}")
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
            print(f"Γ£ù Agent execution failed: {result_state['error']}")
            return False

        output = result_state.get("output")
        if output and "echo" in output:
            print(f"Γ£ô LLM responded: {output['echo']}")
            return True
        else:
            print(f"Γ£ù Unexpected output: {output}")
            return False

    except Exception as e:
        print(f"Γ£ù LLM response test failed: {e}")
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
            print(f"Γ£ô Usage tracked: {len(usage_after)} calls")
            print(f"Γ£ô Cost tracked: ${cost_after:.6f}")
            return True
        else:
            print("Γ£ù No usage tracked")
            return False

    except Exception as e:
        print(f"Γ£ù Cost tracking test failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("=== BaseAgent and LLM Verification Tests ===\n")

    # Test instantiation
    agent = await test_agent_instantiation()
    if not agent:
        print("\nΓ¥î Cannot proceed with LLM tests")
        return False

    # Test LLM response
    llm_test = await test_llm_response(agent)

    # Test cost tracking
    cost_test = await test_cost_tracking(agent)

    # Summary
    print("\n=== Test Summary ===")
    print(f"Agent Instantiation: Γ£ô")
    print(f"LLM Response: {'Γ£ô' if llm_test else 'Γ£ù'}")
    print(f"Cost Tracking: {'Γ£ô' if cost_test else 'Γ£ù'}")

    if llm_test and cost_test:
        print("\nΓ£à All tests passed!")
        return True
    else:
        print("\nΓ¥î Some tests failed")
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
        print(f"Γ¥î Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these variables and run again.")
        sys.exit(1)

    # Run tests
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
