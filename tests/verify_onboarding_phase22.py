"""
Verification script for Onboarding Phase 22: Message Hierarchy (Step 19).
"""

import asyncio
import logging
from backend.agents.graphs.onboarding_v2 import handle_message_hierarchy

logging.basicConfig(level=logging.INFO)

async def verify_phase_22():
    print("Starting Phase 22 Verification...")
    
    # Mock state
    state = {
        "ucid": "RF-2026-PHASE22",
        "business_context": {"ucid": "RF-2026-PHASE22"},
        "positioning": {"primary_statement": "CyberShield is..."},
        "step_data": {
            "soundbites_library": {"soundbites": [{"content": "Protecting your data"}]}
        },
        "completed_steps": [],
        "onboarding_progress": 78.26,
        "needs_user_input": False
    }
    
    # Run handle_message_hierarchy
    print("\nRunning Step 19: Message Hierarchy...")
    result = await handle_message_hierarchy(state)
    
    # 1. Verify Hierarchy data generation
    print("\nVerification 1: Structural Hierarchy")
    assert "message_hierarchy" in result["step_data"]
    data = result["step_data"]["message_hierarchy"]
    assert "level_1_manifesto" in data["message_hierarchy"]
    assert len(data["message_hierarchy"]["level_2_pillars"]) > 0
    print(f"Manifesto: {data['message_hierarchy']['level_1_manifesto']}")
    
    # 2. Verify Structural Integrity
    print("\nVerification 2: Integrity Metric")
    score = data["structural_integrity"]
    print(f"Integrity Score: {score:.2f}")
    assert score > 0
    
    # 3. Verify Progress Update
    print("\nVerification 3: Progress Update")
    assert result["onboarding_progress"] > 82.0
    print(f"Progress: {result['onboarding_progress']:.2f}%")

    print("\nPhase 22 Verification: PASSED")

if __name__ == "__main__":
    asyncio.run(verify_phase_22())
