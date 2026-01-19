"""
Verification script for Onboarding Phase 17: ICP Profiles (Step 15).
"""

import asyncio
import logging
from backend.agents.graphs.onboarding_v2 import handle_icp_profiles

logging.basicConfig(level=logging.INFO)

async def verify_phase_17():
    print("Starting Phase 17 Verification...")
    
    # Mock state
    state = {
        "ucid": "RF-2026-PHASE17",
        "business_context": {
            "ucid": "RF-2026-PHASE17",
            "identity": {"company_name": "CyberShield", "industry": "Cybersecurity"}
        },
        "positioning": {"primary_statement": "CyberShield is the AI Security Platform..."},
        "step_data": {
            "focus_sacrifice": {"focus_items": [{"description": "Enterprise Security Teams"}]}
        },
        "completed_steps": [],
        "onboarding_progress": 60.87,
        "needs_user_input": False
    }
    
    # Run handle_icp_profiles
    print("\nRunning Step 15: ICP Profiles...")
    result = await handle_icp_profiles(state)
    
    # 1. Verify ICP data generation
    print("\nVerification 1: Deep ICP Profiles")
    assert "icp_profiles" in result["step_data"]
    data = result["step_data"]["icp_profiles"]
    assert len(data["profiles"]) > 0
    assert "primary_icp" in data
    print(f"Primary ICP: {data['primary_icp']['name']}")
    assert "psychographics" in data["primary_icp"]
    print(f"Motivations: {data['primary_icp']['psychographics']['motivations'][:2]}")
    
    # 2. Verify State update
    print("\nVerification 2: Top-level State Sync")
    assert "icp_profiles" in result
    assert len(result["icp_profiles"]) > 0
    print("ICP profiles stored in top-level state: SUCCESS")
    
    # 3. Verify Progress Update
    print("\nVerification 3: Progress Update")
    assert result["onboarding_progress"] > 65.0
    print(f"Progress: {result['onboarding_progress']:.2f}%")

    print("\nPhase 17 Verification: PASSED")

if __name__ == "__main__":
    asyncio.run(verify_phase_17())
