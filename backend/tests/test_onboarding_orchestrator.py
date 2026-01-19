"""
Test script to verify OnboardingOrchestrator functionality.
"""

import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.agents.specialists.onboarding_orchestrator import OnboardingOrchestrator
from backend.agents.state import add_message, create_initial_state


async def test_onboarding_step_detection():
    """Test that the agent correctly identifies current onboarding step."""
    print("Testing OnboardingOrchestrator step detection...")

    try:
        # Create agent instance
        agent = OnboardingOrchestrator()
        print(f"✓ OnboardingOrchestrator instantiated: {agent.name}")

        # Test 1: New user should start at step 1
        print("\nTest 1: New user step detection")
        state1 = create_initial_state(
            workspace_id="test-workspace-123", user_id="test-user-456"
        )

        current_step = agent._detect_current_step(state1)
        assert (
            current_step.step_number == 1
        ), f"Expected step 1, got step {current_step.step_number}"
        print(
            f"✓ New user correctly starts at step {current_step.step_number}: {current_step.name}"
        )

        # Test 2: User mentioning step number
        print("\nTest 2: User mentioning specific step")
        state2 = create_initial_state(
            workspace_id="test-workspace-123", user_id="test-user-456"
        )
        state2 = add_message(state2, "user", "I want to work on step 3")

        current_step = agent._detect_current_step(state2)
        assert (
            current_step.step_number == 3
        ), f"Expected step 3, got step {current_step.step_number}"
        print(f"✓ User mentioning 'step 3' correctly detected: {current_step.name}")

        # Test 3: User mentioning step name
        print("\nTest 3: User mentioning step name")
        state3 = create_initial_state(
            workspace_id="test-workspace-123", user_id="test-user-456"
        )
        state3 = add_message(state3, "user", "Help me with company information")

        current_step = agent._detect_current_step(state3)
        assert (
            current_step.step_number == 2
        ), f"Expected step 2, got step {current_step.step_number}"
        print(
            f"✓ User mentioning 'company information' correctly detected: {current_step.name}"
        )

        return True

    except Exception as e:
        print(f"✗ Step detection test failed: {e}")
        return False


async def test_step_guidance():
    """Test that the agent provides appropriate guidance for each step."""
    print("\nTesting step guidance generation...")

    try:
        agent = OnboardingOrchestrator()

        # Test guidance for step 1 (new user)
        print("\nTest: Step 1 guidance for new user")
        state = create_initial_state(
            workspace_id="test-workspace-123", user_id="test-user-456"
        )

        result = await agent.execute(state)

        if result.get("error"):
            print(f"✗ Step guidance failed: {result['error']}")
            return False

        output = result.get("output")
        assert (
            output["current_step"] == 1
        ), f"Expected step 1, got step {output['current_step']}"
        assert "required_fields" in output, "Missing required_fields in output"
        assert "step_name" in output, "Missing step_name in output"

        print(f"✓ Step 1 guidance generated correctly")
        print(f"✓ Step name: {output['step_name']}")
        print(f"✓ Required fields: {output['required_fields']}")
        print(f"✓ Estimated time: {output['estimated_time']} minutes")

        # Test guidance for step with some data
        print("\nTest: Step guidance with partial data")
        state2 = create_initial_state(
            workspace_id="test-workspace-123",
            user_id="test-user-456",
            user_profile={"user_email": "test@example.com", "user_name": "Test User"},
        )

        result2 = await agent.execute(state2)

        if result2.get("error"):
            print(f"✗ Step guidance with data failed: {result2['error']}")
            return False

        output2 = result2.get("output")
        print(f"✓ Step guidance with partial data works")

        return True

    except Exception as e:
        print(f"✗ Step guidance test failed: {e}")
        return False


async def test_progress_tracking():
    """Test that progress tracking works correctly."""
    print("\nTesting progress tracking...")

    try:
        agent = OnboardingOrchestrator()

        # Test initial progress
        state = create_initial_state(
            workspace_id="test-workspace-123", user_id="test-user-456"
        )

        initial_progress = agent._calculate_progress(state)
        assert initial_progress == 0.0, f"Expected 0% progress, got {initial_progress}%"
        print(f"✓ Initial progress: {initial_progress}%")

        # Test progress after completing steps
        state = agent._mark_step_completed(state, 1)
        state = agent._mark_step_completed(state, 2)
        state = agent._mark_step_completed(state, 3)

        updated_progress = agent._calculate_progress(state)
        expected_progress = (3 / 13) * 100
        assert (
            abs(updated_progress - expected_progress) < 0.1
        ), f"Expected {expected_progress}%, got {updated_progress}%"
        print(f"✓ Progress after 3 steps: {updated_progress:.1f}%")

        # Test step completion detection
        assert agent._is_step_completed(state, 1), "Step 1 should be completed"
        assert agent._is_step_completed(state, 2), "Step 2 should be completed"
        assert agent._is_step_completed(state, 3), "Step 3 should be completed"
        assert not agent._is_step_completed(state, 4), "Step 4 should not be completed"
        print("✓ Step completion detection works correctly")

        return True

    except Exception as e:
        print(f"✗ Progress tracking test failed: {e}")
        return False


async def test_state_persistence():
    """Test that agent maintains state across interactions."""
    print("\nTesting state persistence...")

    try:
        agent = OnboardingOrchestrator()

        # Create initial state
        state = create_initial_state(
            workspace_id="test-workspace-123", user_id="test-user-456"
        )

        # Execute first interaction
        result1 = await agent.execute(state)
        state1 = result1

        # Check state was updated
        assert (
            "current_onboarding_step" in state1
        ), "State not updated with current step"
        assert "onboarding_progress" in state1, "State not updated with progress"
        print("✓ State updated after first interaction")

        # Execute second interaction
        result2 = await agent.execute(state1)
        state2 = result2

        # Check state persistence
        assert state2.get("current_onboarding_step") == state1.get(
            "current_onboarding_step"
        ), "Step number not persisted"
        assert len(state2.get("messages", [])) > len(
            state1.get("messages", [])
        ), "Messages not persisted"
        print("✓ State persists across interactions")

        return True

    except Exception as e:
        print(f"✗ State persistence test failed: {e}")
        return False


async def test_onboarding_summary():
    """Test onboarding summary generation."""
    print("\nTesting onboarding summary...")

    try:
        agent = OnboardingOrchestrator()

        # Create state with some progress
        state = create_initial_state(
            workspace_id="test-workspace-123", user_id="test-user-456"
        )
        state = agent._mark_step_completed(state, 1)
        state = agent._mark_step_completed(state, 2)

        summary = agent.get_onboarding_summary(state)

        assert (
            summary["total_steps"] == 13
        ), f"Expected 13 total steps, got {summary['total_steps']}"
        assert (
            summary["completed_steps"] == 2
        ), f"Expected 2 completed steps, got {summary['completed_steps']}"
        assert (
            summary["current_step"] == 3
        ), f"Expected current step 3, got {summary['current_step']}"
        assert (
            summary["progress_percentage"] > 0
        ), "Progress percentage should be greater than 0"
        assert (
            summary["estimated_remaining_time"] > 0
        ), "Should have estimated remaining time"

        print(f"✓ Summary generated correctly")
        print(f"✓ Total steps: {summary['total_steps']}")
        print(f"✓ Completed steps: {summary['completed_steps']}")
        print(f"✓ Progress: {summary['progress_percentage']:.1f}%")
        print(
            f"✓ Current step: {summary['current_step']} - {summary['current_step_name']}"
        )
        print(
            f"✓ Estimated remaining time: {summary['estimated_remaining_time']} minutes"
        )

        return True

    except Exception as e:
        print(f"✗ Onboarding summary test failed: {e}")
        return False


async def main():
    """Run all OnboardingOrchestrator tests."""
    print("=== OnboardingOrchestrator Verification Tests ===\n")

    # Run all tests
    test_results = []

    test_results.append(await test_onboarding_step_detection())
    test_results.append(await test_step_guidance())
    test_results.append(await test_progress_tracking())
    test_results.append(await test_state_persistence())
    test_results.append(await test_onboarding_summary())

    # Summary
    print("\n=== Test Summary ===")
    print(f"Step Detection: {'✓' if test_results[0] else '✗'}")
    print(f"Step Guidance: {'✓' if test_results[1] else '✗'}")
    print(f"Progress Tracking: {'✓' if test_results[2] else '✗'}")
    print(f"State Persistence: {'✓' if test_results[3] else '✗'}")
    print(f"Onboarding Summary: {'✓' if test_results[4] else '✗'}")

    if all(test_results):
        print("\n✅ All OnboardingOrchestrator tests passed!")
        return True
    else:
        print("\n❌ Some OnboardingOrchestrator tests failed")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
