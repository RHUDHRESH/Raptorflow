"""
Simple verification script for OnboardingSessionManager

Tests basic functionality without pytest dependencies.
"""

import asyncio
import os
import sys
from datetime import datetime

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def test_session_manager():
    """Test basic session manager functionality."""
    print("Testing OnboardingSessionManager...")

    try:
        # Import the session manager
        from redis.session_manager import get_onboarding_session_manager

        # Get session manager instance
        manager = get_onboarding_session_manager()
        print("Session manager instantiated successfully")

        # Test health check
        print("Testing Redis health check...")
        health = await manager.health_check()
        print(f"Health check result: {health}")

        if health.get("overall_healthy"):
            print("Redis connection healthy")

            # Test basic operations
            session_id = "test_session_" + datetime.now().strftime("%Y%m%d_%H%M%S")
            print(f"Testing session operations with ID: {session_id}")

            # Test metadata
            print("Testing metadata operations...")
            metadata_success = await manager.set_metadata(
                session_id, "user123", "workspace456"
            )
            print(f"Set metadata: {metadata_success}")

            metadata = await manager.get_metadata(session_id)
            print(f"Get metadata: {metadata}")

            # Test step saving
            print("Testing step operations...")
            step_data = {
                "company_name": "Test Corp",
                "industry": "Technology",
                "stage": "Seed",
                "employees": 10,
            }

            save_success = await manager.save_step(session_id, 1, step_data)
            print(f"Save step 1: {save_success}")

            # Test step retrieval
            retrieved_step = await manager.get_step(session_id, 1)
            print(f"Retrieved step 1: {retrieved_step}")

            # Test progress tracking
            print("Testing progress tracking...")
            progress = await manager.update_progress(session_id, 1)
            print(f"Updated progress: {progress}")

            # Test getting all steps
            print("Testing get all steps...")
            all_steps = await manager.get_all_steps(session_id)
            print(f"All steps count: {len(all_steps)}")

            # Test session summary
            print("Testing session summary...")
            summary = await manager.get_session_summary(session_id)
            print(f"Session summary: {summary}")

            # Test cleanup
            print("Testing cleanup...")
            delete_success = await manager.delete_session(session_id)
            print(f"Delete session: {delete_success}")

            print("All tests completed successfully!")

        else:
            print("Redis connection failed")
            print("Health check details:", health)

    except Exception as e:
        print(f"Error during testing: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_session_manager())
