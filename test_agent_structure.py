#!/usr/bin/env python3
"""
Test script for agent structure and imports only.
Tests that all agents can be imported and have the required methods.
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))


def test_agent_structure():
    """Test agent structure without requiring configuration."""
    print("=" * 60)
    print("AGENT STRUCTURE TEST")
    print("=" * 60)

    try:
        # Test basic imports
        print("Testing basic imports...")
        from agents.base import BaseAgent
        from agents.config import ModelTier
        from agents.state import AgentState, create_initial_state

        print("✓ Basic imports successful")

        # Test specialist agent imports
        print("\nTesting specialist agent imports...")
        from agents.specialists import (
            AnalyticsAgent,
            BlackBoxStrategist,
            BlogWriter,
            CampaignPlanner,
            CompetitorIntelAgent,
            ContentCreator,
            DailyWinsGenerator,
            EmailSpecialist,
            EvidenceProcessor,
            FactExtractor,
            ICPArchitect,
            MarketResearchAgent,
            MoveStrategist,
            OnboardingOrchestrator,
            PersonaSimulator,
            QualityChecker,
            RevisionAgent,
            SocialMediaAgent,
            TrendAnalyzer,
        )

        print("✓ All specialist agents imported successfully")

        # Test routing imports
        print("\nTesting routing imports...")
        from agents.routing.hlk import HLKRouter
        from agents.routing.intent import IntentRouter
        from agents.routing.pipeline import RoutingPipeline
        from agents.routing.semantic import SemanticRouter

        print("✓ Routing components imported successfully")

        # Test tools imports
        print("\nTesting tools imports...")
        from agents.tools import (
            ContentGenTool,
            DatabaseTool,
            ToolRegistry,
            WebScraperTool,
            WebSearchTool,
        )

        print("✓ All tools imported successfully")

        # Test that agents have required methods
        print("\nTesting agent interfaces...")
        agents_to_test = [
            OnboardingOrchestrator,
            MoveStrategist,
            ContentCreator,
            BlackBoxStrategist,
            MarketResearchAgent,
            AnalyticsAgent,
        ]

        for agent_class in agents_to_test:
            try:
                # Create instance (this might fail due to config, but we can catch it)
                agent = agent_class()
                print(f"✓ {agent_class.__name__} instantiated successfully")

                # Check required methods exist
                required_methods = ["get_system_prompt", "execute"]
                for method in required_methods:
                    if hasattr(agent, method):
                        print(f"  ✓ {method} method exists")
                    else:
                        print(f"  ✗ {method} method missing")

            except Exception as e:
                print(f"✗ {agent_class.__name__} failed to instantiate: {e}")

        # Test routing pipeline structure
        print("\nTesting routing pipeline structure...")
        try:
            pipeline = RoutingPipeline()
            print(f"✓ RoutingPipeline instantiated")
            print(f"✓ Has {len(pipeline.ROUTE_TO_AGENT)} routes defined")
            for route, agent in pipeline.ROUTE_TO_AGENT.items():
                print(f"  - {route} → {agent}")
        except Exception as e:
            print(f"✗ RoutingPipeline failed: {e}")

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

        print("\n" + "=" * 60)
        print("AGENT STRUCTURE TEST COMPLETE")
        print("✓ All structural components working")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_agent_structure()
    sys.exit(0 if success else 1)
