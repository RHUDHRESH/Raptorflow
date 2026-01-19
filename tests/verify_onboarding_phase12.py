"""
Verification script for Onboarding Phase 12: Capability Rating (Step 10).
"""

import asyncio
import logging
from backend.agents.graphs.onboarding_v2 import handle_capability_rating

logging.basicConfig(level=logging.INFO)

async def verify_phase_12():
    print("Starting Phase 12 Verification...")
    
    # Mock state
    state = {
        "ucid": "RF-2026-PHASE12",
        "business_context": {"ucid": "RF-2026-PHASE12"},
        "step_data": {
            "truth_sheet": {
                "entries": [{"field_name": "core_feature", "value": "Real-time AI detection"}]
            }
        },
        "completed_steps": [],
        "onboarding_progress": 39.13,
        "needs_user_input": False
    }
    
    # Run handle_capability_rating
    print("\nRunning Step 10: Capability Rating...")
    result = await handle_capability_rating(state)
    
    # 1. Verify Ratings generation
    print("\nVerification 1: Capability Benchmarking")
    assert "capability_rating" in result["step_data"]
    ratings = result["step_data"]["capability_rating"]["ratings"]
    print(f"Rated {len(ratings)} capabilities.")
    assert len(ratings) > 0
    
    # 2. Verify Overall Strength
    print("\nVerification 2: Overall Strength Metric")
    score = result["step_data"]["capability_rating"]["overall_strength"]
    print(f"Overall Strength: {score:.2f}")
    assert score > 0
    
    # 3. Verify Progress Update
    print("\nVerification 3: Progress Update")
    assert result["onboarding_progress"] > 43.0
    print(f"Progress: {result['onboarding_progress']:.2f}%")

    print("\nPhase 12 Verification: PASSED")

if __name__ == "__main__":
    asyncio.run(verify_phase_12())
