import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from backend.core.vault import Vault
from backend.models.blackbox import BlackboxOutcome, BlackboxTelemetry
from backend.services.blackbox_service import BlackboxService


class TestBlackboxE2E(unittest.TestCase):
    """
    End-to-End Simulation of the Blackbox Learning Flywheel.
    Move -> Telemetry -> Outcome -> Learning
    """

    def setUp(self):
        self.mock_vault = MagicMock(spec=Vault)
        self.mock_session = MagicMock()
        self.mock_vault.get_session.return_value = self.mock_session
        self.service = BlackboxService(vault=self.mock_vault)

    @patch("backend.graphs.blackbox_analysis.create_blackbox_graph")
    @patch("backend.services.blackbox_service.InferenceProvider")
    def test_e2e_flywheel_simulation(self, mock_inference, mock_create_graph):
        """
        Simulates the entire data flow from move execution to strategic insight.
        """
        move_id = uuid4()
        campaign_id = uuid4()

        # 1. Simulate Move Execution & Telemetry Logging
        telemetry = BlackboxTelemetry(
            move_id=move_id,
            agent_id="research_agent",
            trace={"step": "market_scan", "found": ["link1", "link2"]},
            tokens=500,
            latency=1.5,
        )

        with patch.object(self.service, "stream_to_bigquery"):
            self.service.log_telemetry(telemetry)
            self.mock_session.table.assert_any_call("blackbox_telemetry_industrial")

        # 2. Simulate Outcome Attribution
        outcome = BlackboxOutcome(
            campaign_id=campaign_id,
            move_id=move_id,
            source="linkedin",
            value=250.0,
            confidence=0.95,
        )

        with patch.object(self.service, "stream_outcome_to_bigquery"):
            self.service.attribute_outcome(outcome)
            self.mock_session.table.assert_any_call("blackbox_outcomes_industrial")

        # 3. Simulate Learning Cycle (LangGraph)
        mock_graph = AsyncMock()
        mock_graph.ainvoke.return_value = {
            "findings": ["High engagement on LinkedIn for B2B SaaS Founders"],
            "confidence": 0.92,
            "status": ["validated"],
        }
        mock_create_graph.return_value = mock_graph

        # Mock Categorization & Embedding
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(content="strategic")
        mock_inference.get_model.return_value = mock_llm

        mock_embed = MagicMock()
        mock_embed.embed_query.return_value = [0.1, 0.2, 0.3]
        mock_inference.get_embeddings.return_value = mock_embed

        # Trigger Cycle
        result = asyncio.run(self.service.trigger_learning_cycle(str(move_id)))

        # 4. Verify Results
        self.assertEqual(result["findings_count"], 1)
        self.assertEqual(result["status"], "cycle_complete")

        # Verify that learning was persisted
        self.mock_session.table.assert_any_call("blackbox_learnings_industrial")

        print(
            f"\nE2E Flywheel Test Passed: Move {move_id} -> Outcome $250 -> 1 Strategic Insight"
        )


if __name__ == "__main__":
    unittest.main()
