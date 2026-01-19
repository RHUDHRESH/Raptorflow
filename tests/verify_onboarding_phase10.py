"""
Verification script for Onboarding Phase 10: Comparative Angle (Step 8).
"""

import asyncio
import logging
from backend.agents.graphs.onboarding_v2 import handle_comparative_angle

logging.basicConfig(level=logging.INFO)

async def verify_phase_10():
    print("Starting Phase 10 Verification...")
    
    # Mock state
    state = {
        "ucid": "RF-2026-PHASE10",
        "business_context": {"ucid": "RF-2026-PHASE10"},
        "step_data": {
            "market_intelligence": {"results": [{"title": "Competitor X"}]}
        },
        "completed_steps": [],
        "onboarding_progress": 30.43,
        "needs_user_input": False
    }
    
    # Run handle_comparative_angle
    print("\nRunning Step 8: Comparative Angle...")
    result = await handle_comparative_angle(state)
    
    # 1. Verify Comparative Angle generation
    print("\nVerification 1: Angle Generation")
    assert "comparative_angle" in result["step_data"]
    angles = result["step_data"]["comparative_angle"]["comparative_angles"]
    print(f"Generated {len(angles)} strategic angles.")
    assert len(angles) > 0
    
    # 2. Verify Differentiation Score
    print("\nVerification 2: Differentiation Metric")
    score = result["step_data"]["comparative_angle"]["differentiation_score"]
    print(f"Differentiation Score: {score:.2f}")
    assert score > 0
    
    # 3. Verify Progress Update
    print("\nVerification 3: Progress Update")
    assert result["onboarding_progress"] > 34.0
    print(f"Progress: {result['onboarding_progress']:.2f}%")

    print("\nPhase 10 Verification: PASSED")

if __name__ == "__main__":
    asyncio.run(verify_phase_10())
