"""
Verification script for Onboarding Phase 2: Evidence Vault & Classification.
"""

import asyncio
import logging
from backend.agents.graphs.onboarding_v2 import handle_evidence_vault, OnboardingStateV2

logging.basicConfig(level=logging.INFO)

async def verify_phase_2():
    print("Starting Phase 2 Verification...")
    
    # Mock state
    state = {
        "ucid": "RF-2026-PHASE2",
        "business_context": {},
        "evidence": [
            {"filename": "vision_deck.pptx", "content_type": "application/vnd.openxmlformats-officedocument.presentationml.presentation"},
            {"filename": "app_screenshot.png", "content_type": "image/png"}
        ],
        "step_data": {},
        "completed_steps": [],
        "onboarding_progress": 0.0,
        "needs_user_input": False
    }
    
    # Run handle_evidence_vault
    print("\nRunning Step 1: Evidence Vault...")
    result = await handle_evidence_vault(state)
    
    # 1. Verify Classification
    print("\nVerification 1: AI Classification")
    for item in result["evidence"]:
        print(f"File: {item['filename']} -> Type: {item['evidence_type']} (Confidence: {item['confidence']:.2f})")
        assert "evidence_type" in item
        assert item["confidence"] > 0
        
    # 2. Verify Recommended Evidence Logic
    print("\nVerification 2: Recommended Evidence Logic")
    step_data = result["step_data"]["evidence_vault"]
    print(f"Missing recommended items: {step_data['missing_recommended']}")
    assert len(step_data["missing_recommended"]) > 0
    
    # 3. Verify BCM Sync (Partial)
    print("\nVerification 3: BCM Metadata Sync")
    assert "evidence_ids" in result["business_context"]
    print("BCM Metadata Sync: SUCCESS")

    print("\nPhase 2 Step 1 Verification: PASSED")

if __name__ == "__main__":
    asyncio.run(verify_phase_2())
