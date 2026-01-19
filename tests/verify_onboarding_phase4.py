"""
Verification script for Onboarding Phase 4: Data Purge Protocol.
"""

import asyncio
import logging
from unittest.mock import patch, AsyncMock
from backend.agents.graphs.onboarding_v2 import handle_data_purge

logging.basicConfig(level=logging.INFO)

async def verify_phase_4():
    print("Starting Phase 4 Verification...")
    
    # Mock state with file_ids
    state = {
        "ucid": "RF-2026-PHASE4",
        "evidence": [
            {"file_id": "file-123", "filename": "doc1.pdf"},
            {"file_id": "file-456", "filename": "doc2.png"}
        ]
    }
    
    # Patch delete_file to avoid real GCP calls
    with patch("backend.agents.graphs.onboarding_v2.delete_file", new_callable=AsyncMock) as mock_delete:
        mock_delete.return_value = True
        
        # Run handle_data_purge
        print("\nRunning Helper: Data Purge...")
        result = await handle_data_purge(state)
        
        # 1. Verify delete_file calls
        print("\nVerification 1: Lifecycle Enforcement")
        assert mock_delete.call_count == 2
        print(f"Delete calls made: {mock_delete.call_count}")
        
        # 2. Verify state update
        print("\nVerification 2: State Update")
        for item in result["evidence"]:
            assert item["purged"] == True
        print("State updated with purge status: SUCCESS")

    print("\nPhase 4 Verification: PASSED")

if __name__ == "__main__":
    asyncio.run(verify_phase_4())
