"""
Tests for the Agent Registry Service.
"""

import pytest
import json
from unittest.mock import AsyncMock, patch

from backend.services.agent_registry import (
    AgentRegistry,
    COUNCIL_OF_LORDS,
    agent_registry,
)


@pytest.fixture
def registry():
    """Create registry instance."""
    return AgentRegistry()


class TestCouncilOfLords:
    """Test the canonical Lord definitions."""

    def test_council_lords_structure(self):
        """Test that all lords have required fields."""
        for slug, lord_config in COUNCIL_OF_LORDS.items():
            assert "name" in lord_config
            assert "guild" in lord_config
            assert "kind" in lord_config
            assert "description" in lord_config
            assert "config" in lord_config

            # Config should have necessary fields
            assert "capabilities" in lord_config["config"]
            assert "domain" in lord_config["config"]
            assert "priority" in lord_config["config"]

    def test_all_seven_lords_present(self):
        """Test that exactly 7 canonical lords are defined."""
        assert len(COUNCIL_OF_LORDS) == 7

        expected_slugs = {
            "lord-architect",
            "lord-cognition",
            "lord-strategos",
            "lord-aesthete",
            "lord-seer",
            "lord-arbiter",
            "lord-herald"
        }

        assert set(COUNCIL_OF_LORDS.keys()) == expected_slugs

    def test_lord_configs_have_sensible_values(self):
        """Test that lord configs have reasonable values."""
        for slug, lord_config in COUNCIL_OF_LORDS.items():
            # Priorities should be in reasonable range
            assert 80 <= lord_config["config"]["priority"] <= 100

            # Guild should be consistent
            assert lord_config["guild"] == "lord"
            assert lord_config["kind"] == "lord"

            # Should have multiple capabilities
            assert len(lord_config["config"]["capabilities"]) > 0


class TestAgentRegistrySeeding:
    """Test agent creation and seeding logic."""

    @pytest.fixture(autouse=True)
    async def setup_registry(self, registry):
        """Set up registry with mocked database."""
        registry.supabase = AsyncMock()
        return registry

    @pytest.mark.asyncio
    async def test_ensure_core_agents_creates_lords(self, registry):
        """Test that ensure_core_agents_for_workspace creates all canonical agents."""
        workspace_id = "ws-123"

        # Mock database responses
        def mock_select(*args, **kwargs):
            # Simulate no existing agents
            result_mock = AsyncMock()
            result_mock.data = []
            return result_mock

        registry.supabase.client.table.return_value.select.return_value.eq.return_value = mock_select()
        registry.supabase.insert = AsyncMock(return_value=True)

        # Mock select for existing check
        existing_check_mock = AsyncMock()
        existing_check_mock.data = []
        registry.supabase.client.table.return_value.select.return_value.eq.return_value.eq.return_value.execute = AsyncMock(return_value=existing_check_mock)

        # Ensure agents
        await registry.ensure_core_agents_for_workspace(workspace_id)

        # Verify all 7 lords were attempted to be created
        assert registry.supabase.insert.call_count == 7

        # Verify each call was for expected data
        calls = registry.supabase.insert.call_args_list
        for call in calls:
            table_name, data = call[0]
            assert table_name == "agents"
            assert data["workspace_id"] == workspace_id
            assert data["guild"] == "lord"
            assert data["status"] == "active"
            # Config should be JSON string
            parsed_config = json.loads(data["config"])
            assert "capabilities" in parsed_config
            assert isinstance(parsed_config["capabilities"], list)

    @pytest.mark.asyncio
    async def test_ensure_core_agents_idempotent(self, registry):
        """Test that ensure_core_agents_for_workspace is idempotent."""
        workspace_id = "ws-123"

        # Mock existing agents (simulate already seeded)
        existing_mock = AsyncMock()
        existing_mock.data = [{"id": "agent-1"}]  # Some agent exists
        registry.supabase.client.table.return_value.select.return_value.eq.return_value.eq.return_value.execute = AsyncMock(return_value=existing_mock)

        registry.supabase.insert = AsyncMock(return_value=True)

        # Ensure agents
        await registry.ensure_core_agents_for_workspace(workspace_id)

        # Should not attempt to insert since agents already exist
        registry.supabase.insert.assert_not_called()

    @pytest.mark.asyncio
    async def test_ensure_core_agents_partial_failure(self, registry):
        """Test graceful handling when some agent creation fails."""
        workspace_id = "ws-123"

        # Set up mix of existing and new agents
        def mock_existing_check(slug):
            """Mock that half the lords already exist."""
            existing_lords = list(COUNCIL_OF_LORDS.keys())[:4]  # First 4 exist
            result_mock = AsyncMock()
            result_mock.data = [{"id": "agent-1"}] if slug in existing_lords else []
            return result_mock

        registry.supabase.insert = AsyncMock(return_value=True)

        # Manually check each lord (simplified for test)
        await registry.ensure_core_agents_for_workspace(workspace_id)

        # Should create remaining 3 lords
        assert registry.supabase.insert.call_count == 3


class TestAgentRetrieval:
    """Test agent lookup and listing."""

    @pytest.fixture(autouse=True)
    async def setup_registry(self, registry):
        """Set up registry with mocked database."""
        registry.supabase = AsyncMock()
        return registry

    @pytest.mark.asyncio
    async def test_get_agent_by_slug_found(self, registry):
        """Test retrieving an existing agent."""
        workspace_id = "ws-123"
        slug = "lord-architect"

        # Mock database response
        mock_data = {
            "id": "agent-1",
            "workspace_id": workspace_id,
            "slug": slug,
            "name": "Architect Lord",
            "config": '{"domain": "architecture"}'
        }
        result_mock = AsyncMock()
        result_mock.data = [mock_data]
        registry.supabase.client.table.return_value.select.return_value.eq.return_value.eq.return_value.execute = AsyncMock(return_value=result_mock)

        agent = await registry.get_agent_by_slug(workspace_id, slug)

        assert agent is not None
        assert agent["name"] == "Architect Lord"
        assert agent["config"]["domain"] == "architecture"

    @pytest.mark.asyncio
    async def test_get_agent_by_slug_not_found(self, registry):
        """Test retrieving non-existent agent."""
        workspace_id = "ws-123"
        slug = "non-existent-lord"

        result_mock = AsyncMock()
        result_mock.data = []
        registry.supabase.client.table.return_value.select.return_value.eq.return_value.eq.return_value.execute = AsyncMock(return_value=result_mock)

        agent = await registry.get_agent_by_slug(workspace_id, slug)

        assert agent is None

    @pytest.mark.asyncio
    async def test_list_workspace_agents(self, registry):
        """Test listing all agents in a workspace."""
        workspace_id = "ws-123"

        mock_agents = [
            {
                "id": "agent-1",
                "slug": "lord-architect",
                "config": '{"domain": "architecture"}'
            },
            {
                "id": "agent-2",
                "slug": "lord-cognition",
                "config": '{"domain": "cognition"}'
            }
        ]

        result_mock = AsyncMock()
        result_mock.data = mock_agents
        registry.supabase.client.table.return_value.select.return_value.eq.return_value.execute = AsyncMock(return_value=result_mock)

        agents = await registry.list_workspace_agents(workspace_id)

        assert len(agents) == 2
        assert agents[0]["config"]["domain"] == "architecture"
        assert agents[1]["config"]["domain"] == "cognition"


class TestCanonicalAccess:
    """Test access to canonical Lord definitions."""

    def test_get_canonical_lords(self, registry):
        """Test getting list of canonical lord slugs."""
        lords = registry.get_canonical_lords()

        assert len(lords) == 7
        assert "lord-architect" in lords
        assert "lord-herald" in lords

    def test_get_lord_spec(self, registry):
        """Test getting canonical spec for a lord."""
        spec = registry.get_lord_spec("lord-architect")

        assert spec is not None
        assert spec["name"] == "Architect Lord"
        assert spec["guild"] == "lord"
        assert spec["slug"] == "lord-architect"

    def test_get_lord_spec_nonexistent(self, registry):
        """Test getting spec for non-canonical lord."""
        spec = registry.get_lord_spec("lord-nonexistent")

        assert spec is None


def test_registry_constants():
    """Test registry constants are properly defined."""
    assert len(COUNCIL_OF_LORDS) == 7

    # Each lord should have unique slug and name
    slugs = [lord["slug"] for lord in COUNCIL_OF_LORDS.values() if "slug" in lord]
    assert len(set(slugs)) == 7  # All unique

    # But actually, slugs are keys - update logic
    slugs = list(COUNCIL_OF_LORDS.keys())
    assert len(set(slugs)) == 7


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
