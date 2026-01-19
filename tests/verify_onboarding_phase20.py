"""
Verification script for Onboarding Phase 20: Soundbites Library (Step 18).
"""

import asyncio
import logging
from backend.agents.graphs.onboarding_v2 import handle_soundbites_library

logging.basicConfig(level=logging.INFO)

async def verify_phase_20():
    print("Starting Phase 20 Verification...")
    
    # Mock state
    state = {
        "ucid": "RF-2026-PHASE20",
        "business_context": {"ucid": "RF-2026-PHASE20", "identity": {"company_name": "CyberShield"}},
        "positioning": {"primary_statement": "CyberShield is..."},
        "icp_profiles": [{"name": "Enterprise Security Guard"}],
        "step_data": {},
        "completed_steps": [],
        "onboarding_progress": 73.91,
        "needs_user_input": False
    }
    
    # Run handle_soundbites_library
    print("\nRunning Step 18: Soundbites Library...")
    result = await handle_soundbites_library(state)
    
    # 1. Verify Library generation
    print("\nVerification 1: Messaging Library")
    assert "soundbites_library" in result["step_data"]
    data = result["step_data"]["soundbites_library"]
    assert len(data["soundbites"]) > 0
    print(f"Generated {len(data['soundbites'])} soundbites.")
    assert "tagline" in data["by_type"]
    
    # 2. Verify Progress Update
    print("\nVerification 2: Progress Update")
    assert result["onboarding_progress"] > 78.0
    print(f"Progress: {result['onboarding_progress']:.2f}%")

    print("\nPhase 20 Verification: PASSED")

if __name__ == "__main__":
    asyncio.run(verify_phase_20())
