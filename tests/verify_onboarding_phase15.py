"""
Verification script for Onboarding Phase 15: Positioning Statements (Step 13).
"""

import asyncio
import logging
from backend.agents.graphs.onboarding_v2 import handle_positioning_statements

logging.basicConfig(level=logging.INFO)

async def verify_phase_15():
    print("Starting Phase 15 Verification...")
    
    # Mock state
    state = {
        "ucid": "RF-2026-PHASE15",
        "business_context": {
            "ucid": "RF-2026-PHASE15",
            "identity": {"company_name": "CyberShield"}
        },
        "step_data": {
            "strategic_grid": {"moat_strength": 7.5}
        },
        "completed_steps": [],
        "onboarding_progress": 52.17,
        "needs_user_input": False
    }
    
    # Run handle_positioning_statements
    print("\nRunning Step 13: Positioning Statements...")
    result = await handle_positioning_statements(state)
    
    # 1. Verify Statements generation
    print("\nVerification 1: Multi-framework Statements")
    assert "positioning_statements" in result["step_data"]
    data = result["step_data"]["positioning_statements"]
    assert len(data["statements"]) > 0
    assert "primary_statement" in data
    print(f"Primary Statement: {data['primary_statement']['statement'][:100]}...")
    
    # 2. Verify State update
    print("\nVerification 2: State Persistence")
    assert "positioning" in result
    print("Positioning data stored in top-level state: SUCCESS")
    
    # 3. Verify Progress Update
    print("\nVerification 3: Progress Update")
    assert result["onboarding_progress"] > 56.0
    print(f"Progress: {result['onboarding_progress']:.2f}%")

    print("\nPhase 15 Verification: PASSED")

if __name__ == "__main__":
    asyncio.run(verify_phase_15())
