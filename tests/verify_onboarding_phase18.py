"""
Verification script for Onboarding Phase 18: Buying Process (Step 16).
"""

import asyncio
import logging
from backend.agents.graphs.onboarding_v2 import handle_buying_process

logging.basicConfig(level=logging.INFO)

async def verify_phase_18():
    print("Starting Phase 18 Verification...")
    
    # Mock state
    state = {
        "ucid": "RF-2026-PHASE18",
        "business_context": {"ucid": "RF-2026-PHASE18"},
        "icp_profiles": [{"name": "Enterprise Security Guard"}],
        "step_data": {},
        "completed_steps": [],
        "onboarding_progress": 65.22,
        "needs_user_input": False
    }
    
    # Run handle_buying_process
    print("\nRunning Step 16: Buying Process...")
    result = await handle_buying_process(state)
    
    # 1. Verify Buying Stages generation
    print("\nVerification 1: Journey Mapping")
    assert "buying_process" in result["step_data"]
    stages = result["step_data"]["buying_process"]["buying_stages"]
    print(f"Mapped {len(stages)} buying stages.")
    assert len(stages) > 0
    
    # 2. Verify Complexity
    print("\nVerification 2: Process Complexity")
    complexity = result["step_data"]["buying_process"]["sales_cycle_complexity"]
    print(f"Complexity: {complexity}")
    assert complexity != ""
    
    # 3. Verify Progress Update
    print("\nVerification 3: Progress Update")
    assert result["onboarding_progress"] > 69.0
    print(f"Progress: {result['onboarding_progress']:.2f}%")

    print("\nPhase 18 Verification: PASSED")

if __name__ == "__main__":
    asyncio.run(verify_phase_18())
