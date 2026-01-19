"""
Verification script for Onboarding Phase 7: Brand Audit (Step 5).
"""

import asyncio
import logging
from backend.agents.graphs.onboarding_v2 import handle_brand_audit

logging.basicConfig(level=logging.INFO)

async def verify_phase_7():
    print("Starting Phase 7 Verification...")
    
    # Mock state
    state = {
        "ucid": "RF-2026-PHASE7",
        "business_context": {"ucid": "RF-2026-PHASE7"},
        "step_data": {
            "truth_sheet": {
                "entries": [{"field_name": "company_name", "value": "CyberShield"}]
            }
        },
        "completed_steps": [],
        "onboarding_progress": 17.39,
        "needs_user_input": False
    }
    
    # Run handle_brand_audit
    print("\nRunning Step 5: Brand Audit...")
    result = await handle_brand_audit(state)
    
    # 1. Verify Brand Audit generation
    print("\nVerification 1: Gap Identification")
    assert "brand_audit" in result["step_data"]
    gaps = result["step_data"]["brand_audit"]["brand_gaps"]
    print(f"Identified {len(gaps)} brand gaps.")
    assert len(gaps) > 0
    
    # 2. Verify Audit Score
    print("\nVerification 2: Brand Integrity Score")
    score = result["step_data"]["brand_audit"]["score"]
    print(f"Brand Score: {score:.2f}")
    assert score > 0
    
    # 3. Verify Progress Update
    print("\nVerification 3: Progress Update")
    assert result["onboarding_progress"] > 21.0
    print(f"Progress: {result['onboarding_progress']:.2f}%")

    print("\nPhase 7 Verification: PASSED")

if __name__ == "__main__":
    asyncio.run(verify_phase_7())
