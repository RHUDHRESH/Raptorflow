import asyncio
import json
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from graphs.council import (
    campaign_arc_generator_node,
    consensus_scorer_node,
    council_debate_node,
    cross_critique_node,
    kill_switch_monitor_node,
    move_decomposition_node,
    move_refiner_node,
    success_predictor_node,
    synthesis_node,
)
from models.council import CouncilBlackboardState
from services.council_service import CouncilService


class TestCouncilService:
    """Test suite for CouncilService with mocked council nodes."""

    @pytest.fixture
    def mock_cache_manager(self):
        """Mock cache manager for testing."""
        cache = MagicMock()
        cache.get_json = MagicMock(return_value=None)
        cache.set_json = MagicMock()
        return cache

    @pytest.fixture
    def council_service(self, mock_cache_manager):
        """Create CouncilService instance with mocked dependencies."""
        return CouncilService(cache_manager=mock_cache_manager)

    @pytest.fixture
    def sample_state(self):
        """Create a sample CouncilBlackboardState for testing."""
        return {
            "workspace_id": "test_workspace",
            "tenant_id": "test_workspace",
            "raw_prompt": "Test objective",
            "brief": {"goals": "Test objective", "context": "Test details"},
            "research_bundle": {"details": "Test details"},
            "current_plan": [],
            "active_move": None,
            "generated_assets": [],
            "messages": [
                {"role": "system", "content": "Council planning session"},
                {
                    "role": "human",
                    "content": "Objective: Test objective. Context: Test details",
                },
            ],
            "last_agent": "CouncilService",
            "reflection_log": [],
            "status": "planning",
            "lifecycle_state": "planning",
            "lifecycle_transitions": [],
            "quality_score": 0.0,
            "cost_accumulator": 0.0,
            "token_usage": {"input": 0, "output": 0},
            "tool_usage": {"calls": 0},
            "budget_caps": None,
            "budget_usage": None,
            "error": None,
            "next_node": None,
            "routing_metadata": {"intent": {"objective": "Test objective"}},
            "shared_memory_handles": {},
            "resource_budget": {},
            "parallel_thoughts": [],
            "debate_history": [],
            "consensus_metrics": {},
            "synthesis": None,
            "rejected_paths": [],
            "final_strategic_decree": None,
            "reasoning_chain_id": None,
            "radar_signals": [],
            "campaign_id": None,
            "suggested_moves": [],
            "refined_moves": [],
            "evaluated_moves": [],
            "approved_moves": [],
            "discarded_moves": [],
            "move_ids": [],
            "campaign_data": None,
        }

    @pytest.mark.asyncio
    async def test_generate_move_plan_success(
        self, council_service, mock_cache_manager
    ):
        """Test successful move plan generation."""
        # Mock cache miss
        mock_cache_manager.get_json.return_value = None

        # Mock node responses
        with (
            patch("services.council_service.council_debate_node") as mock_debate,
            patch("services.council_service.cross_critique_node") as mock_critique,
            patch("services.council_service.consensus_scorer_node") as mock_consensus,
            patch("services.council_service.synthesis_node") as mock_synthesis,
            patch(
                "services.council_service.reasoning_chain_logger_node"
            ) as mock_logger,
            patch("services.council_service.rejection_logger_node") as mock_rejection,
            patch("services.council_service.move_decomposition_node") as mock_decomp,
            patch("services.council_service.move_refiner_node") as mock_refiner,
            patch("services.council_service.success_predictor_node") as mock_predictor,
            patch(
                "services.council_service.kill_switch_monitor_node"
            ) as mock_killswitch,
        ):

            # Setup mock responses
            mock_debate.return_value = {
                "parallel_thoughts": [{"agent_id": "test", "content": "test"}]
            }
            mock_critique.return_value = {"debate_history": []}
            mock_consensus.return_value = {
                "consensus_metrics": {"alignment": 0.8, "confidence": 0.7, "risk": 0.3}
            }
            mock_synthesis.return_value = {
                "final_strategic_decree": "Test decree",
                "rejected_paths": [],
            }
            mock_logger.return_value = {"reasoning_chain_id": "test_chain_id"}
            mock_rejection.return_value = {}
            mock_decomp.return_value = {
                "suggested_moves": [{"title": "Test Move", "description": "Test"}]
            }
            mock_refiner.return_value = {
                "refined_moves": [{"title": "Test Move", "muse_prompt": "Test prompt"}]
            }
            mock_predictor.return_value = {
                "evaluated_moves": [{"title": "Test Move", "confidence_score": 85}]
            }
            mock_killswitch.return_value = {
                "approved_moves": [{"title": "Test Move"}],
                "discarded_moves": [],
            }

            result = await council_service.generate_move_plan(
                "test_workspace", "Test objective", "Test details"
            )

            assert result["decree"] == "Test decree"
            assert result["consensus_metrics"]["alignment"] == 0.8
            assert len(result["approved_moves"]) == 1
            assert result["approved_moves"][0]["title"] == "Test Move"
            assert "campaign_data" not in result

            # Verify cache was called
            mock_cache_manager.get_json.assert_called_once()
            mock_cache_manager.set_json.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_campaign_plan_success(
        self, council_service, mock_cache_manager
    ):
        """Test successful campaign plan generation."""
        # Mock cache miss
        mock_cache_manager.get_json.return_value = None

        # Mock node responses including campaign arc generator
        with (
            patch("services.council_service.council_debate_node") as mock_debate,
            patch("services.council_service.cross_critique_node") as mock_critique,
            patch("services.council_service.consensus_scorer_node") as mock_consensus,
            patch("services.council_service.synthesis_node") as mock_synthesis,
            patch(
                "services.council_service.reasoning_chain_logger_node"
            ) as mock_logger,
            patch("services.council_service.rejection_logger_node") as mock_rejection,
            patch(
                "services.council_service.campaign_arc_generator_node"
            ) as mock_campaign,
            patch("services.council_service.move_decomposition_node") as mock_decomp,
            patch("services.council_service.move_refiner_node") as mock_refiner,
            patch("services.council_service.success_predictor_node") as mock_predictor,
            patch(
                "services.council_service.kill_switch_monitor_node"
            ) as mock_killswitch,
        ):

            # Setup mock responses
            mock_debate.return_value = {
                "parallel_thoughts": [{"agent_id": "test", "content": "test"}]
            }
            mock_critique.return_value = {"debate_history": []}
            mock_consensus.return_value = {
                "consensus_metrics": {"alignment": 0.8, "confidence": 0.7, "risk": 0.3}
            }
            mock_synthesis.return_value = {
                "final_strategic_decree": "Test decree",
                "rejected_paths": [],
            }
            mock_logger.return_value = {"reasoning_chain_id": "test_chain_id"}
            mock_rejection.return_value = {}
            mock_campaign.return_value = {
                "campaign_id": "test_campaign_id",
                "campaign_data": {
                    "title": "Test Campaign",
                    "objective": "Test objective",
                    "arc_data": {"phases": ["Phase 1", "Phase 2"]},
                },
            }
            mock_decomp.return_value = {
                "suggested_moves": [{"title": "Test Move", "description": "Test"}]
            }
            mock_refiner.return_value = {
                "refined_moves": [{"title": "Test Move", "muse_prompt": "Test prompt"}]
            }
            mock_predictor.return_value = {
                "evaluated_moves": [{"title": "Test Move", "confidence_score": 85}]
            }
            mock_killswitch.return_value = {
                "approved_moves": [{"title": "Test Move"}],
                "discarded_moves": [],
            }

            result = await council_service.generate_campaign_plan(
                "test_workspace", "Test objective", "Test details", "Test ICP"
            )

            assert result["decree"] == "Test decree"
            assert result["consensus_metrics"]["alignment"] == 0.8
            assert len(result["approved_moves"]) == 1
            assert result["campaign_data"]["title"] == "Test Campaign"
            assert result["campaign_data"]["objective"] == "Test objective"
            assert "phases" in result["campaign_data"]["arc_data"]

            # Verify campaign arc generator was called
            mock_campaign.assert_called_once()

    @pytest.mark.asyncio
    async def test_cached_response_returned(self, council_service, mock_cache_manager):
        """Test that cached responses are returned when available."""
        # Mock cache hit
        cached_response = {
            "decree": "Cached decree",
            "consensus_metrics": {"alignment": 0.9},
            "approved_moves": [{"title": "Cached Move"}],
            "cached": True,
        }
        mock_cache_manager.get_json.return_value = cached_response

        result = await council_service.generate_move_plan(
            "test_workspace", "Test objective", "Test details"
        )

        assert result["cached"] is True
        assert result["decree"] == "Cached decree"

        # Verify cache was checked but not set (since we returned cached result)
        mock_cache_manager.get_json.assert_called_once()
        mock_cache_manager.set_json.assert_not_called()

    @pytest.mark.asyncio
    async def test_node_timeout_handling(self, council_service):
        """Test that node timeouts are handled properly."""
        with patch("services.council_service.council_debate_node") as mock_debate:
            # Mock timeout
            mock_debate.side_effect = asyncio.TimeoutError()

            with pytest.raises(RuntimeError, match="Council Debate timed out"):
                await council_service.generate_move_plan(
                    "test_workspace", "Test objective", "Test details"
                )

    @pytest.mark.asyncio
    async def test_node_failure_handling(self, council_service):
        """Test that node failures are handled properly."""
        with patch("services.council_service.council_debate_node") as mock_debate:
            # Mock node failure
            mock_debate.side_effect = ValueError("Node failed")

            with pytest.raises(
                RuntimeError, match="Council Debate failed: Node failed"
            ):
                await council_service.generate_move_plan(
                    "test_workspace", "Test objective", "Test details"
                )

    @pytest.mark.asyncio
    async def test_cache_key_generation(self, council_service):
        """Test cache key generation is consistent."""
        key1 = council_service._cache_key("ws1", "obj1", "details1", "move", "icp1")
        key2 = council_service._cache_key("ws1", "obj1", "details1", "move", "icp1")
        key3 = council_service._cache_key("ws1", "obj1", "details1", "campaign", "icp1")
        key4 = council_service._cache_key("ws2", "obj1", "details1", "move", "icp1")

        assert key1 == key2  # Same inputs should produce same key
        assert key1 != key3  # Different plan types should produce different keys
        assert key1 != key4  # Different workspace IDs should produce different keys
        assert key1.startswith("council:move:ws1:")

    @pytest.mark.asyncio
    async def test_cache_failure_handling(self, council_service, mock_cache_manager):
        """Test that cache failures don't break the pipeline."""
        # Mock cache failure
        mock_cache_manager.get_json.side_effect = Exception("Cache failed")

        with (
            patch("services.council_service.council_debate_node") as mock_debate,
            patch("services.council_service.cross_critique_node") as mock_critique,
            patch("services.council_service.consensus_scorer_node") as mock_consensus,
            patch("services.council_service.synthesis_node") as mock_synthesis,
            patch(
                "services.council_service.reasoning_chain_logger_node"
            ) as mock_logger,
            patch("services.council_service.rejection_logger_node") as mock_rejection,
            patch("services.council_service.move_decomposition_node") as mock_decomp,
            patch("services.council_service.move_refiner_node") as mock_refiner,
            patch("services.council_service.success_predictor_node") as mock_predictor,
            patch(
                "services.council_service.kill_switch_monitor_node"
            ) as mock_killswitch,
        ):

            # Setup mock responses
            mock_debate.return_value = {
                "parallel_thoughts": [{"agent_id": "test", "content": "test"}]
            }
            mock_critique.return_value = {"debate_history": []}
            mock_consensus.return_value = {"consensus_metrics": {"alignment": 0.8}}
            mock_synthesis.return_value = {
                "final_strategic_decree": "Test decree",
                "rejected_paths": [],
            }
            mock_logger.return_value = {"reasoning_chain_id": "test_chain_id"}
            mock_rejection.return_value = {}
            mock_decomp.return_value = {"suggested_moves": []}
            mock_refiner.return_value = {"refined_moves": []}
            mock_predictor.return_value = {"evaluated_moves": []}
            mock_killswitch.return_value = {"approved_moves": [], "discarded_moves": []}

            # Should not raise exception despite cache failure
            result = await council_service.generate_move_plan(
                "test_workspace", "Test objective", "Test details"
            )

            assert result["decree"] == "Test decree"

    def test_build_initial_state(self, council_service):
        """Test initial state building."""
        state = council_service._build_initial_state(
            "ws1", "Test objective", "Test details", "Test ICP"
        )

        assert state["workspace_id"] == "ws1"
        assert state["tenant_id"] == "ws1"
        assert state["raw_prompt"] == "Test objective"
        assert state["brief"]["goals"] == "Test objective"
        assert state["brief"]["context"] == "Test details"
        assert state["brief"]["target_icp"] == "Test ICP"
        assert len(state["messages"]) == 2
        assert state["messages"][0]["role"] == "system"
        assert state["messages"][1]["role"] == "human"

    def test_build_response_move_plan(self, council_service, sample_state):
        """Test response building for move plans."""
        sample_state.update(
            {
                "final_strategic_decree": "Test decree",
                "consensus_metrics": {"alignment": 0.8, "confidence": 0.7, "risk": 0.3},
                "suggested_moves": [{"title": "Move 1", "description": "Desc 1"}],
                "refined_moves": [
                    {
                        "title": "Move 1",
                        "description": "Desc 1",
                        "muse_prompt": "Prompt 1",
                    }
                ],
                "approved_moves": [{"title": "Move 1", "description": "Desc 1"}],
                "discarded_moves": [{"title": "Move 2", "description": "Desc 2"}],
                "debate_history": [
                    {"round_number": 1, "proposals": [], "critiques": []}
                ],
                "rejected_paths": [{"path": "Path 1", "reason": "Reason 1"}],
                "reasoning_chain_id": "chain_123",
                "campaign_id": None,
            }
        )

        response = council_service._build_response(sample_state, include_campaign=False)

        assert response["decree"] == "Test decree"
        assert response["consensus_metrics"]["alignment"] == 0.8
        assert len(response["suggested_moves"]) == 1
        assert len(response["refined_moves"]) == 1
        assert len(response["approved_moves"]) == 1
        assert len(response["discarded_moves"]) == 1
        assert len(response["debate_history"]) == 1
        assert len(response["rejected_paths"]) == 1
        assert response["reasoning_chain_id"] == "chain_123"
        assert "campaign_data" not in response

    def test_build_response_campaign_plan(self, council_service, sample_state):
        """Test response building for campaign plans."""
        sample_state.update(
            {
                "final_strategic_decree": "Test decree",
                "consensus_metrics": {"alignment": 0.8},
                "campaign_data": {
                    "title": "Test Campaign",
                    "objective": "Test objective",
                    "arc_data": {"phases": ["Phase 1"]},
                },
                "suggested_moves": [],
                "refined_moves": [],
                "approved_moves": [],
                "discarded_moves": [],
                "debate_history": [],
                "rejected_paths": [],
                "reasoning_chain_id": "chain_123",
                "campaign_id": "campaign_123",
            }
        )

        response = council_service._build_response(sample_state, include_campaign=True)

        assert response["campaign_data"]["title"] == "Test Campaign"
        assert response["campaign_data"]["objective"] == "Test objective"
        assert response["campaign_data"]["arc_data"]["phases"] == ["Phase 1"]
        assert response["campaign_id"] == "campaign_123"

    def test_serialize_transcripts(self, council_service):
        """Test transcript serialization."""
        # Mock transcript with model_dump method
        mock_transcript = MagicMock()
        mock_transcript.model_dump.return_value = {"round_number": 1, "data": "test"}

        # Mock transcript without model_dump method
        plain_transcript = {"round_number": 2, "data": "plain"}

        result = council_service._serialize_transcripts(
            [mock_transcript, plain_transcript]
        )

        assert len(result) == 2
        assert result[0] == {"round_number": 1, "data": "test"}
        assert result[1] == {"round_number": 2, "data": "plain"}

    def test_ensure_muse_prompt(self, council_service):
        """Test muse prompt normalization."""
        moves = [
            {"title": "Move 1", "description": "Desc 1"},  # No muse_prompt
            {
                "title": "Move 2",
                "description": "Desc 2",
                "muse_prompt": "Prompt 2",
            },  # Has muse_prompt
            "plain_move",  # Not a dict
        ]

        result = council_service._ensure_muse_prompt(moves)

        assert len(result) == 3
        assert result[0]["muse_prompt"] is None
        assert result[1]["muse_prompt"] == "Prompt 2"
        assert result[2] == "plain_move"
