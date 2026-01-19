"""
Verification script for Onboarding Phase 16: Focus & Sacrifice (Step 14).
"""

import asyncio
import logging
from backend.agents.graphs.onboarding_v2 import handle_focus_sacrifice

logging.basicConfig(level=logging.INFO)

async def verify_phase_16():
    print("Starting Phase 16 Verification...")
    
    # Mock state
    state = {
        "ucid": "RF-2026-PHASE16",
        "business_context": {
            "ucid": "RF-2026-PHASE16",
            "identity": {"company_name": "CyberShield"}
        },
        "positioning": {"primary_statement": "CyberShield is the AI Security Platform..."},
        "step_data": {},
        "completed_steps": [],
        "onboarding_progress": 56.52,
        "needs_user_input": False
    }
    
    # Run handle_focus_sacrifice
    print("\nRunning Step 14: Focus & Sacrifice...")
    result = await handle_focus_sacrifice(state)
    
    # 1. Verify Tradeoff data generation
    print("\nVerification 1: Strategic Tradeoffs")
    assert "focus_sacrifice" in result["step_data"]
    data = result["step_data"]["focus_sacrifice"]
    assert len(data["focus_items"]) > 0
    assert len(data["sacrifice_items"]) > 0
    assert len(data["tradeoff_pairs"]) > 0
    print(f"Tradeoff: {data['tradeoff_pairs'][0]['focus']['description']} vs {data['tradeoff_pairs'][0]['sacrifice']['description']}")
    
    # 2. Verify Progress Update
    print("\nVerification 2: Progress Update")
    assert result["onboarding_progress"] > 60.0
    print(f"Progress: {result['onboarding_progress']:.2f}%")

    print("\nPhase 16 Verification: PASSED")

if __name__ == "__main__":
    asyncio.run(verify_phase_16())
