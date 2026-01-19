"""
Verification script for Onboarding Phase 11: Category Paths (Step 9).
"""

import asyncio
import logging
from backend.agents.graphs.onboarding_v2 import handle_category_paths

logging.basicConfig(level=logging.INFO)

async def verify_phase_11():
    print("Starting Phase 11 Verification...")
    
    # Mock state
    state = {
        "ucid": "RF-2026-PHASE11",
        "business_context": {
            "ucid": "RF-2026-PHASE11",
            "identity": {"company_name": "CyberShield", "industry": "Cybersecurity", "product_description": "AI Threat Detection"}
        },
        "step_data": {
            "market_intelligence": {"results": [{"name": "Competitor X"}]}
        },
        "completed_steps": [],
        "onboarding_progress": 34.78,
        "needs_user_input": False
    }
    
    # Run handle_category_paths
    print("\nRunning Step 9: Category Paths...")
    result = await handle_category_paths(state)
    
    # 1. Verify Path options generation
    print("\nVerification 1: Strategic Options")
    assert "category_paths" in result["step_data"]
    paths = result["step_data"]["category_paths"]
    assert "safe_path" in paths
    assert "clever_path" in paths
    assert "bold_path" in paths
    print(f"Recommended Path: {paths['recommended_path']}")
    
    # 2. Verify Progress Update
    print("\nVerification 2: Progress Update")
    assert result["onboarding_progress"] > 39.0
    print(f"Progress: {result['onboarding_progress']:.2f}%")

    print("\nPhase 11 Verification: PASSED")

if __name__ == "__main__":
    asyncio.run(verify_phase_11())
