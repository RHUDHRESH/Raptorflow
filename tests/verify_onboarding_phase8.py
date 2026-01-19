"""
Verification script for Onboarding Phase 8: Offer & Pricing (Step 6).
"""

import asyncio
import logging
from backend.agents.graphs.onboarding_v2 import handle_offer_pricing

logging.basicConfig(level=logging.INFO)

async def verify_phase_8():
    print("Starting Phase 8 Verification...")
    
    # Mock state
    state = {
        "ucid": "RF-2026-PHASE8",
        "business_context": {"ucid": "RF-2026-PHASE8"},
        "step_data": {
            "truth_sheet": {
                "entries": [{"field_name": "pricing_model", "value": "Subscription"}]}
        },
        "completed_steps": [],
        "onboarding_progress": 21.74,
        "needs_user_input": False
    }
    
    # Run handle_offer_pricing
    print("\nRunning Step 6: Offer & Pricing...")
    result = await handle_offer_pricing(state)
    
    # 1. Verify Pricing Analysis
    print("\nVerification 1: Benchmark Analysis")
    assert "offer_pricing" in result["step_data"]
    analysis = result["step_data"]["offer_pricing"]
    print(f"Current Offer: {analysis['current_offer']}")
    assert "optimizations" in analysis
    print(f"Number of optimizations: {len(analysis['optimizations'])}")
    
    # 2. Verify Progress Update
    print("\nVerification 2: Progress Update")
    assert result["onboarding_progress"] > 26.0
    print(f"Progress: {result['onboarding_progress']:.2f}%")

    print("\nPhase 8 Verification: PASSED")

if __name__ == "__main__":
    asyncio.run(verify_phase_8())
