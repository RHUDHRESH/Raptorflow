"""
Verification script for Onboarding Phase 9: Market Intelligence (Step 7).
"""

import asyncio
import logging
from unittest.mock import patch, AsyncMock
from backend.agents.graphs.onboarding_v2 import handle_market_intelligence

logging.basicConfig(level=logging.INFO)

async def verify_phase_9():
    print("Starting Phase 9 Verification...")
    
    # Mock state
    state = {
        "ucid": "RF-2026-PHASE9",
        "business_context": {
            "ucid": "RF-2026-PHASE9",
            "identity": {"company_name": "CyberShield"}
        },
        "step_data": {},
        "market_insights": [],
        "completed_steps": [],
        "onboarding_progress": 26.09,
        "needs_user_input": False
    }
    
    # Patch TitanOrchestrator
    with patch("backend.agents.graphs.onboarding_v2.titan_sorter.execute", new_callable=AsyncMock) as mock_titan:
        mock_titan.return_value = {
            "query": "Competitors and market landscape for CyberShield",
            "mode": "LITE",
            "results": [
                {"title": "Competitor A", "url": "https://comp-a.com"},
                {"title": "Market Report 2026", "url": "https://market-intel.com"}
            ],
            "count": 2
        }
        
        # Run handle_market_intelligence
        print("\nRunning Step 7: Market Intelligence...")
        result = await handle_market_intelligence(state)
        
        # 1. Verify Titan call
        print("\nVerification 1: Titan Sorter Trigger")
        mock_titan.assert_called_once()
        print(f"Titan queried with: {mock_titan.call_args[0][0]}")
        
        # 2. Verify state update
        print("\nVerification 2: Insight Storage")
        assert len(result["market_insights"]) == 2
        assert "market_intelligence" in result["step_data"]
        print("Market insights stored in state: SUCCESS")
        
        # 3. Verify Progress Update
        print("\nVerification 3: Progress Update")
        assert result["onboarding_progress"] > 30.0
        print(f"Progress: {result['onboarding_progress']:.2f}%")

    print("\nPhase 9 Verification: PASSED")

if __name__ == "__main__":
    asyncio.run(verify_phase_9())
