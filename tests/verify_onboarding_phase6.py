"""
Verification script for Onboarding Phase 6: Truth Sheet (Step 4).
"""

import asyncio
import logging
from backend.agents.graphs.onboarding_v2 import handle_truth_sheet

logging.basicConfig(level=logging.INFO)

async def verify_phase_6():
    print("Starting Phase 6 Verification...")
    
    # Mock state
    state = {
        "ucid": "RF-2026-PHASE6",
        "business_context": {"ucid": "RF-2026-PHASE6"},
        "evidence": [
            {
                "filename": "deck.pdf", 
                "extracted_text": "CyberShield mission is to protect the world's data."
            }
        ],
        "step_data": {},
        "completed_steps": [],
        "onboarding_progress": 13.04,
        "needs_user_input": False
    }
    
    # Run handle_truth_sheet
    print("\nRunning Step 4: Truth Sheet...")
    result = await handle_truth_sheet(state)
    
    # 1. Verify Truth Sheet generation
    print("\nVerification 1: Truth Consolidation")
    assert "truth_sheet" in result["step_data"]
    entries = result["step_data"]["truth_sheet"]["entries"]
    print(f"Generated {len(entries)} truth entries.")
    assert len(entries) > 0
    
    # 2. Verify Completeness Score
    print("\nVerification 2: Completeness Metric")
    score = result["step_data"]["truth_sheet"]["completeness_score"]
    print(f"Completeness Score: {score:.2f}")
    assert score >= 0
    
    # 3. Verify Progress Update
    print("\nVerification 3: Progress Update")
    assert result["onboarding_progress"] > 17.0
    print(f"Progress: {result['onboarding_progress']:.2f}%")

    print("\nPhase 6 Verification: PASSED")

if __name__ == "__main__":
    asyncio.run(verify_phase_6())
