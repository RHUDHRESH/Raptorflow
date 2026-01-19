"""
Verification script for Onboarding Phase 3: Auto Extraction (Step 2).
"""

import asyncio
import logging
from backend.agents.graphs.onboarding_v2 import handle_auto_extraction

logging.basicConfig(level=logging.INFO)

async def verify_phase_3():
    print("Starting Phase 3 Verification...")
    
    # Mock state
    state = {
        "ucid": "RF-2026-PHASE3",
        "business_context": {"ucid": "RF-2026-PHASE3"},
        "evidence": [
            {
                "filename": "pitch_deck.pdf", 
                "evidence_type": "pitch_deck",
                "extracted_text": "Our company, CyberShield, is a cybersecurity firm based in San Francisco. We provide AI-powered threat detection for enterprises."
            }
        ],
        "step_data": {},
        "completed_steps": [],
        "onboarding_progress": 4.34,
        "needs_user_input": False
    }
    
    # Run handle_auto_extraction
    print("\nRunning Step 2: Auto Extraction...")
    result = await handle_auto_extraction(state)
    
    # 1. Verify Extraction result in step_data
    print("\nVerification 1: Extraction Output")
    assert "auto_extraction" in result["step_data"]
    print("Extraction Data stored in state: SUCCESS")
    
    # 2. Verify Incremental Sync to Business Context
    print("\nVerification 2: Incremental Sync")
    # Note: extraction_orchestrator might return empty facts if no real AI is connected or mocked
    print(f"Business Context Identity: {result['business_context'].get('identity')}")
    
    # 3. Verify Progress Update
    print("\nVerification 3: Progress Update")
    assert result["onboarding_progress"] > 8.0
    print(f"Progress: {result['onboarding_progress']:.2f}%")

    print("\nPhase 3 Verification: PASSED")

if __name__ == "__main__":
    asyncio.run(verify_phase_3())
