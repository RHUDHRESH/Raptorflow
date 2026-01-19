"""
Verification script for Onboarding Phase 14: Strategic Grid (Step 12).
"""

import asyncio
import logging
from backend.agents.graphs.onboarding_v2 import handle_strategic_grid

logging.basicConfig(level=logging.INFO)

async def verify_phase_14():
    print("Starting Phase 14 Verification...")
    
    # Mock state
    state = {
        "ucid": "RF-2026-PHASE14",
        "business_context": {"ucid": "RF-2026-PHASE14"},
        "step_data": {
            "capability_rating": {"ratings": [{"capability": "AI Model", "score": 9}]}
        },
        "completed_steps": [],
        "onboarding_progress": 47.83,
        "needs_user_input": False
    }
    
    # Run handle_strategic_grid
    print("\nRunning Step 12: Strategic Grid...")
    result = await handle_strategic_grid(state)
    
    # 1. Verify Grid data generation
    print("\nVerification 1: Value vs Rarity Analysis")
    assert "strategic_grid" in result["step_data"]
    assets = result["step_data"]["strategic_grid"]["grid_assets"]
    print(f"Mapped {len(assets)} strategic assets.")
    assert len(assets) > 0
    
    # 2. Verify Moat Strength
    print("\nVerification 2: Moat Strength Metric")
    score = result["step_data"]["strategic_grid"]["moat_strength"]
    print(f"Moat Strength: {score:.2f}")
    assert score > 0
    
    # 3. Verify Progress Update
    print("\nVerification 3: Progress Update")
    assert result["onboarding_progress"] > 52.0
    print(f"Progress: {result['onboarding_progress']:.2f}%")

    print("\nPhase 14 Verification: PASSED")

if __name__ == "__main__":
    asyncio.run(verify_phase_14())
