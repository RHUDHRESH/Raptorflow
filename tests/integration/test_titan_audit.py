"""
Audit Integration Test for Titan Intelligence Spine.
Verifies multi-tier research modes (LITE, RESEARCH), semantic ranking, and synthesis logic.
"""

import os
import pytest
import uuid
import asyncio
from typing import Dict, Any, List
from unittest.mock import MagicMock, AsyncMock, patch

# Mock environment variables
os.environ["SECRET_KEY"] = "test_secret"
os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost:5432/db"
os.environ["GCP_PROJECT_ID"] = "test-project"
os.environ["WEBHOOK_SECRET"] = "test_webhook_secret"
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_ANON_KEY"] = "test_token"

@pytest.mark.asyncio
class TestTitanAudit:
    """Audit suite for Titan Intelligence engine."""

    @pytest.fixture
    def titan_orchestrator(self):
        from backend.services.titan.orchestrator import TitanOrchestrator
        # Mock dependencies in __init__
        with patch("backend.services.search.orchestrator.SOTASearchOrchestrator"), \
             patch("backend.services.titan.scraper.PlaywrightStealthPool"), \
             patch("backend.llm.LLMManager"):
            return TitanOrchestrator()

    async def test_lite_mode_execution(self, titan_orchestrator):
        """Test LITE mode research path."""
        titan_orchestrator.search_orchestrator.query = AsyncMock(return_value=[
            {"url": "https://example.com", "title": "Example", "snippet": "Test snippet"}
        ])
        
        result = await titan_orchestrator.execute("test query", mode="LITE")
        
        assert result["mode"] == "LITE"
        assert result["count"] == 1
        titan_orchestrator.search_orchestrator.query.assert_called_once()

    async def test_research_mode_synthesis(self, titan_orchestrator):
        """Test RESEARCH mode with semantic ranking and synthesis."""
        # 1. Mock Multiplexer
        titan_orchestrator.multiplexer.execute_multiplexed = AsyncMock(return_value=[
            {"url": "https://competitor.com", "title": "Competitor"}
        ])
        
        # 2. Mock Ranker
        titan_orchestrator.rank_results = AsyncMock(return_value=[
            {"url": "https://competitor.com", "title": "Competitor"}
        ])
        
        # 3. Mock Scraper
        titan_orchestrator._scrape_with_escalation = AsyncMock(return_value={
            "text": "Surgical pricing and features...", "method": "http"
        })
        
        # 4. Mock Synthesizer
        titan_orchestrator.synthesizer.synthesize = AsyncMock(return_value={
            "summary": "Synthesized insight",
            "key_findings": ["F1", "F2"]
        })
        
        result = await titan_orchestrator.execute("market research", mode="RESEARCH")
        
        assert result["mode"] == "RESEARCH"
        assert "intelligence_map" in result
        assert result["intelligence_map"]["summary"] == "Synthesized insight"
        titan_orchestrator.synthesizer.synthesize.assert_called_once()

    async def test_deep_mode_traversal_logic(self, titan_orchestrator):
        """Test DEEP mode recursive traversal entry point."""
        titan_orchestrator.multiplexer.execute_multiplexed = AsyncMock(return_value=[
            {"url": "https://deep.com", "title": "Deep Site"}
        ])
        titan_orchestrator.rank_results = AsyncMock(return_value=[
            {"url": "https://deep.com", "title": "Deep Site"}
        ])
        
        # Mock recursive traverse
        titan_orchestrator._recursive_traverse = AsyncMock(return_value={
            "root_url": "https://deep.com",
            "pages": [{"url": "https://deep.com/p1", "text": "content"}]
        })
        
        titan_orchestrator.synthesizer.synthesize = AsyncMock(return_value={"summary": "Deep Insight"})
        
        result = await titan_orchestrator.execute("deep research", mode="DEEP")
        
        assert result["mode"] == "DEEP"
        assert "deep_research_data" in result
        titan_orchestrator._recursive_traverse.assert_called_once()
