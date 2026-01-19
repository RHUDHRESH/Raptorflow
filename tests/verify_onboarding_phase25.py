"""
Verification script for Onboarding Phase 25: Final Synthesis (Step 23).
"""

import asyncio
import logging
from backend.agents.graphs.onboarding_v2 import handle_final_synthesis

logging.basicConfig(level=logging.INFO)

async def verify_phase_25():
    print("Starting Phase 25 Verification...")
    
    # Mock state
    state = {
        "ucid": "RF-2026-FINAL",
        "business_context": {"ucid": "RF-2026-FINAL"},
        "step_data": {
            "validation_todos": {"overall_score": 95.0}
        },
        "completed_steps": [],
        "onboarding_progress": 95.65,
        "needs_user_input": False
    }
    
    # Run handle_final_synthesis
    print("\nRunning Step 23: Final Synthesis...")
    result = await handle_final_synthesis(state)
    
    # 1. Verify Completion status
    print("\nVerification 1: System Activation")
    assert "final_synthesis" in result["step_data"]
    data = result["step_data"]["final_synthesis"]
    print(f"Status: {data['status']}")
    assert data["status"] == "COMPLETED"
    
    # 2. Verify Final Progress
    print("\nVerification 2: 100% Progress")
    assert result["onboarding_progress"] == 100.0
    print(f"Progress: {result['onboarding_progress']}%")

    print("\nPhase 25 Verification: PASSED")

if __name__ == "__main__":
    asyncio.run(verify_phase_25())
