"""
Verification script for Onboarding Phase 19: Messaging Guardrails (Step 17).
"""

import asyncio
import logging
from backend.agents.graphs.onboarding_v2 import handle_messaging_guardrails

logging.basicConfig(level=logging.INFO)

async def verify_phase_19():
    print("Starting Phase 19 Verification...")
    
    # Mock state
    state = {
        "ucid": "RF-2026-PHASE19",
        "business_context": {"ucid": "RF-2026-PHASE19", "identity": {"company_name": "CyberShield"}},
        "positioning": {"primary_statement": "CyberShield is..."},
        "step_data": {},
        "completed_steps": [],
        "onboarding_progress": 69.57,
        "needs_user_input": False
    }
    
    # Run handle_messaging_guardrails
    print("\nRunning Step 17: Messaging Guardrails...")
    result = await handle_messaging_guardrails(state)
    
    # 1. Verify Rules generation
    print("\nVerification 1: Rules Coverage")
    assert "messaging_guardrails" in result["step_data"]
    data = result["step_data"]["messaging_guardrails"]
    assert len(data["rules"]) > 0
    print(f"Generated {len(data['rules'])} guardrails.")
    assert "categories_covered" in data
    
    # 2. Verify Progress Update
    print("\nVerification 2: Progress Update")
    assert result["onboarding_progress"] > 73.0
    print(f"Progress: {result['onboarding_progress']:.2f}%")

    print("\nPhase 19 Verification: PASSED")

if __name__ == "__main__":
    asyncio.run(verify_phase_19())
