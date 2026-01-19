"""
Verification script for Onboarding Phase 24: Reality Check & Validation (Step 22).
"""

import asyncio
import logging
from backend.agents.graphs.onboarding_v2 import handle_validation_todos

logging.basicConfig(level=logging.INFO)

async def verify_phase_24():
    print("Starting Phase 24 Verification...")
    
    # Mock state
    state = {
        "ucid": "RF-2026-PHASE24",
        "business_context": {"ucid": "RF-2026-PHASE24"},
        "step_data": {
            "positioning_statements": {"primary_statement": "CyberShield is..."},
            "soundbites_library": {"count": 10},
            "icp_profiles": {"primary_icp": {"name": "Guard"}}
        },
        "completed_steps": [],
        "onboarding_progress": 91.30,
        "needs_user_input": False
    }
    
    # Run handle_validation_todos
    print("\nRunning Step 22: Validation Todos...")
    result = await handle_validation_todos(state)
    
    # 1. Verify Readiness Audit
    print("\nVerification 1: Launch Readiness")
    assert "validation_todos" in result["step_data"]
    data = result["step_data"]["validation_todos"]
    print(f"Overall Readiness Score: {data['overall_score']}%")
    assert data["overall_score"] > 0
    assert len(data["items"]) > 0
    
    # 2. Verify Progress Update
    print("\nVerification 2: Progress Update")
    assert result["onboarding_progress"] > 95.0
    print(f"Progress: {result['onboarding_progress']:.2f}%")

    print("\nPhase 24 Verification: PASSED")

if __name__ == "__main__":
    asyncio.run(verify_phase_24())
