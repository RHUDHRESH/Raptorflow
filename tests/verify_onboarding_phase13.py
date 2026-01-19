"""
Verification script for Onboarding Phase 13: Perceptual Map (Step 11).
"""

import asyncio
import logging
from backend.agents.graphs.onboarding_v2 import handle_perceptual_map

logging.basicConfig(level=logging.INFO)

async def verify_phase_13():
    print("Starting Phase 13 Verification...")
    
    # Mock state
    state = {
        "ucid": "RF-2026-PHASE13",
        "business_context": {
            "ucid": "RF-2026-PHASE13",
            "identity": {"company_name": "CyberShield", "product_description": "AI Threat Detection"}
        },
        "step_data": {
            "market_intelligence": {"results": [{"name": "Competitor X"}]}
        },
        "completed_steps": [],
        "onboarding_progress": 43.48,
        "needs_user_input": False
    }
    
    # Run handle_perceptual_map
    print("\nRunning Step 11: Perceptual Map...")
    result = await handle_perceptual_map(state)
    
    # 1. Verify Map data generation
    print("\nVerification 1: Axis & Positioning")
    assert "perceptual_map" in result["step_data"]
    map_data = result["step_data"]["perceptual_map"]
    assert "primary_axis" in map_data
    assert "secondary_axis" in map_data
    assert len(map_data["positioning_options"]) > 0
    print(f"Primary Axis: {map_data['primary_axis']['name']}")
    
    # 2. Verify Progress Update
    print("\nVerification 2: Progress Update")
    assert result["onboarding_progress"] > 47.0
    print(f"Progress: {result['onboarding_progress']:.2f}%")

    print("\nPhase 13 Verification: PASSED")

if __name__ == "__main__":
    asyncio.run(verify_phase_13())
