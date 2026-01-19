"""
Verification script for Onboarding Phase 23: Channel Architecture & Market Size (Step 20/21).
"""

import asyncio
import logging
from backend.agents.graphs.onboarding_v2 import handle_channel_mapping, handle_tam_sam_som

logging.basicConfig(level=logging.INFO)

async def verify_phase_23():
    print("Starting Phase 23 Verification...")
    
    # Mock state
    state = {
        "ucid": "RF-2026-PHASE23",
        "business_context": {"ucid": "RF-2026-PHASE23", "identity": {"company_name": "CyberShield"}},
        "icp_profiles": [{"name": "Enterprise Security Guard"}],
        "step_data": {},
        "completed_steps": [],
        "onboarding_progress": 82.61,
        "needs_user_input": False
    }
    
    # Run handle_channel_mapping
    print("\nRunning Step 20: Channel Mapping...")
    state = await handle_channel_mapping(state)
    assert "channel_mapping" in state["step_data"]
    print(f"Mapped {len(state['step_data']['channel_mapping']['strategy']['recommendations'])} channels.")
    
    # Run handle_tam_sam_som
    print("\nRunning Step 21: TAM/SAM/SOM...")
    state = await handle_tam_sam_som(state)
    assert "tam_sam_som" in state["step_data"]
    tam_data = state["step_data"]["tam_sam_som"]["tam"]
    print(f"TAM Calculated: {tam_data['value_formatted']}")
    
    # Verify Progress Update
    print("\nVerification: Progress Update")
    assert state["onboarding_progress"] > 91.0
    print(f"Progress: {state['onboarding_progress']:.2f}%")

    print("\nPhase 23 Verification: PASSED")

if __name__ == "__main__":
    asyncio.run(verify_phase_23())
