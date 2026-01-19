"""
Verification script for Onboarding Phase 5: Contradiction Check (Step 3).
"""

import asyncio
import logging
from backend.agents.graphs.onboarding_v2 import handle_contradiction_check

logging.basicConfig(level=logging.INFO)

async def verify_phase_5():
    print("Starting Phase 5 Verification...")
    
    # Mock state with conflicting facts
    state = {
        "ucid": "RF-2026-PHASE5",
        "business_context": {"ucid": "RF-2026-PHASE5"},
        "step_data": {
            "auto_extraction": {
                "facts": [
                    {"id": "F-COM-001", "category": "Company", "value": "CyberShield Inc"},
                    {"id": "F-COM-002", "category": "Company", "value": "ShieldNet Corp"}
                ]
            }
        },
        "contradictions": [],
        "completed_steps": [],
        "onboarding_progress": 8.70,
        "needs_user_input": False
    }
    
    # Run handle_contradiction_check
    print("\nRunning Step 3: Contradiction Check...")
    result = await handle_contradiction_check(state)
    
    # 1. Verify Contradiction detection
    print("\nVerification 1: Logic Audit")
    assert len(result["contradictions"]) > 0
    print(f"Detected {len(result['contradictions'])} contradictions.")
    print(f"First contradiction: {result['contradictions'][0]['description']}")
    
    # 2. Verify Step Data storage
    print("\nVerification 2: Report Storage")
    assert "contradiction_check" in result["step_data"]
    print("Report stored in step_data: SUCCESS")
    
    # 3. Verify Progress Update
    print("\nVerification 3: Progress Update")
    assert result["onboarding_progress"] > 13.0
    print(f"Progress: {result['onboarding_progress']:.2f}%")

    print("\nPhase 5 Verification: PASSED")

if __name__ == "__main__":
    asyncio.run(verify_phase_5())
