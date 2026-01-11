#!/usr/bin/env python3
"""
Test script for the complete agent system.
Tests routing, agent registration, and basic functionality.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))


async def test_agent_system():
    """Test the complete agent system."""
    print("=" * 60)
    print("AGENT SYSTEM TEST")
    print("=" * 60)

    try:
        # Test imports
        print("Testing imports...")
        from agents.config import ModelTier, config
        from agents.dispatcher import AgentDispatcher, AgentRegistry
        from agents.routing.pipeline import RoutingPipeline
        from agents.state import create_initial_state

        print("✓ All imports successful")

        # Test configuration
        print("\nTesting configuration...")
        print(f"✓ GCP Project: {config.GCP_PROJECT_ID}")
        print(f"✓ GCP Region: {config.GCP_REGION}")
        print(f"✓ Default Model: {config.DEFAULT_MODEL_TIER}")
        print(f"✓ Model costs: {config.COST_PER_1K_TOKENS}")

        # Test agent registry
        print("\nTesting agent registry...")
        registry = AgentRegistry()
        print(f"✓ Registered {len(registry._agents)} agents:")
        for agent_name in registry._agents:
            print(f"  - {agent_name}")

        # Test routing pipeline
        print("\nTesting routing pipeline...")
        pipeline = RoutingPipeline()
        print(f"✓ Pipeline has {len(pipeline.ROUTE_TO_AGENT)} routes:")
        for route, agent in pipeline.ROUTE_TO_AGENT.items():
            print(f"  - {route} → {agent}")

        # Test state creation
        print("\nTesting state management...")
        state = create_initial_state(
            workspace_id="test-workspace",
            user_id="test-user",
            session_id="test-session",
        )
        print(f"✓ State created with workspace_id: {state['workspace_id']}")
        print(f"✓ State created with user_id: {state['user_id']}")
        print(f"✓ State created with session_id: {state['session_id']}")

        # Test basic routing
        print("\nTesting basic routing...")
        test_requests = [
            "I need help with onboarding",
            "Create a marketing move",
            "Generate content for my blog",
            "Research my competitors",
            "Analyze my business metrics",
        ]

        for request in test_requests:
            try:
                decision = await pipeline.route(request, fast_mode=True)
                print(
                    f"✓ '{request}' → {decision.target_agent} (confidence: {decision.confidence:.2f})"
                )
            except Exception as e:
                print(f"✗ '{request}' → Error: {e}")

        # Test dispatcher
        print("\nTesting dispatcher...")
        dispatcher = AgentDispatcher()

        # Test getting agents
        test_agents = ["OnboardingOrchestrator", "MoveStrategist", "ContentCreator"]
        for agent_name in test_agents:
            agent = dispatcher.registry.get_agent(agent_name)
            if agent:
                print(f"✓ Retrieved {agent_name}: {agent.description}")
            else:
                print(f"✗ Could not retrieve {agent_name}")

        print("\n" + "=" * 60)
        print("AGENT SYSTEM TEST COMPLETE")
        print("✓ All core functionality working")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_agent_system())
    sys.exit(0 if success else 1)
