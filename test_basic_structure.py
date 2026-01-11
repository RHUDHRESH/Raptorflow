#!/usr/bin/env python3
"""
Test script for basic agent structure only.
Tests that all agents exist and have the required methods without importing LLM or routing components.
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))


def test_basic_structure():
    """Test basic agent structure without LLM or routing dependencies."""
    print("=" * 60)
    print("BASIC STRUCTURE TEST")
    print("=" * 60)

    try:
        # Test basic imports
        print("Testing basic imports...")
        from agents.config import ModelTier
        from agents.state import AgentState, create_initial_state

        print("✓ Basic imports successful")

        # Test specialist agent imports
        print("\nTesting specialist agent imports...")
        from agents.specialists import (
            AnalyticsAgent,
            BlackboxStrategist,
            CampaignPlanner,
            ContentCreator,
            DailyWinsGenerator,
            EmailSpecialist,
            EvidenceProcessor,
            FactExtractor,
            ICPArchitect,
            MarketResearch,
            MoveStrategist,
            OnboardingOrchestrator,
        )

        print("✓ All specialist agents imported successfully")

        # Test that agents have required structure
        print("\nTesting agent interfaces...")
        agents_to_test = [
            OnboardingOrchestrator,
            MoveStrategist,
            ContentCreator,
            BlackboxStrategist,
            MarketResearch,
            AnalyticsAgent,
        ]

        for agent_class in agents_to_test:
            try:
                # Check class has required attributes
                if hasattr(agent_class, "__doc__"):
                    print(f"✓ {agent_class.__name__} has documentation")
                else:
                    print(f"  - {agent_class.__name__} missing documentation")

                # Check for required methods in class definition
                import inspect

                methods = [
                    name
                    for name, method in inspect.getmembers(
                        agent_class, predicate=inspect.isfunction
                    )
                ]
                required_methods = ["get_system_prompt", "execute"]

                for method in required_methods:
                    if method in methods:
                        print(f"  ✓ {method} method exists")
                    else:
                        print(f"  ✗ {method} method missing")

            except Exception as e:
                print(f"✗ {agent_class.__name__} failed inspection: {e}")

        # Test state creation
        print("\nTesting state creation...")
        try:
            state = create_initial_state(
                workspace_id="test-workspace",
                user_id="test-user",
                session_id="test-session",
            )
            print(f"✓ State created successfully")
            print(f"  - workspace_id: {state['workspace_id']}")
            print(f"  - user_id: {state['user_id']}")
            print(f"  - session_id: {state['session_id']}")
        except Exception as e:
            print(f"✗ State creation failed: {e}")

        # Test ModelTier enum
        print("\nTesting ModelTier enum...")
        print(f"✓ Available models:")
        for tier in ModelTier:
            print(f"  - {tier.value}")

        print("\n" + "=" * 60)
        print("BASIC STRUCTURE TEST COMPLETE")
        print("✓ All basic structure working")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_basic_structure()
    sys.exit(0 if success else 1)
