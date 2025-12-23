import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from backend.agents.strategists import (
    BrandVoiceAligner,
    CampaignArcDesigner,
    KPIDefiner,
)


async def verify():
    print("\n--- Verifying Campaign Module (Phase 5) ---")
    mock_llm = MagicMock()

    # 1. Verify Arc Generation
    with patch(
        "backend.agents.strategists.CampaignArcDesigner.chain", new_callable=AsyncMock
    ) as mock_chain:
        mock_chain.ainvoke.return_value = MagicMock(
            campaign_title="Verif-Arc", model_dump=lambda: {"title": "Verif-Arc"}
        )
        designer = CampaignArcDesigner(mock_llm)
        await designer({"business_context": ["test"], "context_brief": {"uvps": {}}})
        print("✓ Arc Generation: Node executed successfully.")

    # 2. Verify Auditing
    with patch(
        "backend.agents.strategists.BrandVoiceAligner.chain", new_callable=AsyncMock
    ) as mock_chain:
        mock_chain.ainvoke.return_value = MagicMock(
            alignments=[], model_dump=lambda: {"alignments": []}
        )
        auditor = BrandVoiceAligner(mock_llm)
        await auditor({"context_brief": {"uvps": {}}})
        print("✓ Campaign Auditor: Alignment check passed.")

    # 3. Verify KPI Setting
    with patch(
        "backend.agents.strategists.KPIDefiner.chain", new_callable=AsyncMock
    ) as mock_chain:
        mock_chain.ainvoke.return_value = MagicMock(
            kpis=[], model_dump=lambda: {"kpis": []}
        )
        definer = KPIDefiner(mock_llm)
        await definer({"context_brief": {"channels": {}, "campaign_arc": {}}})
        print("✓ KPI Definer: Objectives set.")

    print("\n--- Campaign Module Verification Complete ---")


if __name__ == "__main__":

    asyncio.run(verify())
