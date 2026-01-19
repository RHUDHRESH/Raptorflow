"""
Database tests configuration and fixtures
"""

import asyncio
from typing import Any, Dict, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.core.auth import get_current_user
from backend.core.models import AuthContext, User, Workspace
from backend.core.supabase import get_supabase_client


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client for testing"""
    client = AsyncMock()

    # Mock table methods
    client.table = MagicMock()
    client.table.return_value.select.return_value.execute.return_value = AsyncMock(
        return_value={"data": [], "count": 0}
    )
    client.table.return_value.insert.return_value.execute.return_value = AsyncMock(
        return_value={"data": [{"id": "test-id"}]}
    )
    client.table.return_value.update.return_value.execute.return_value = AsyncMock(
        return_value={"data": [{"id": "test-id"}]}
    )
    client.table.return_value.delete.return_value.execute.return_value = AsyncMock(
        return_value={"data": [{"id": "test-id"}]}
    )

    # Mock RPC methods
    client.rpc = MagicMock()
    client.rpc.return_value.execute.return_value = AsyncMock(return_value={"data": []})

    return client


@pytest.fixture
def mock_user():
    """Mock user for testing"""
    return User(
        id="test-user-id",
        email="test@example.com",
        full_name="Test User",
        subscription_tier="free",
        budget_limit_monthly=1.0,
        preferences={"theme": "light"},
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z",
    )


@pytest.fixture
def mock_workspace():
    """Mock workspace for testing"""
    return Workspace(
        id="test-workspace-id",
        user_id="test-user-id",
        name="Test Workspace",
        slug="test-workspace",
        settings={"timezone": "UTC", "currency": "USD"},
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z",
    )


@pytest.fixture
def mock_auth_context(mock_user, mock_workspace):
    """Mock auth context for testing"""
    return AuthContext(
        user=mock_user,
        workspace_id=mock_workspace.id,
        workspace=mock_workspace,
        permissions={"read": True, "write": True, "delete": True, "admin": False},
    )


@pytest.fixture
def sample_foundation():
    """Sample foundation data for testing"""
    return {
        "id": "test-foundation-id",
        "workspace_id": "test-workspace-id",
        "company_name": "Test Company",
        "mission": "To test effectively",
        "vision": "Comprehensive test coverage",
        "values": ["Quality", "Reliability", "Performance"],
        "industry": "Technology",
        "target_market": "Developers",
        "positioning": "Best testing solution",
        "brand_voice": "Professional and helpful",
        "messaging_guardrails": ["No hype", "Be accurate"],
        "summary": "A company dedicated to testing excellence",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def sample_icp():
    """Sample ICP data for testing"""
    return {
        "id": "test-icp-id",
        "workspace_id": "test-workspace-id",
        "name": "Test ICP",
        "tagline": "Ideal customer profile for testing",
        "market_sophistication": 3,
        "demographics": {"age_range": "25-45", "company_size": "10-50"},
        "psychographics": {"values": ["Quality", "Efficiency"]},
        "behaviors": {"tech_savvy": True, "early_adopter": False},
        "pain_points": ["Testing challenges", "Quality concerns"],
        "goals": ["Improve test coverage", "Reduce bugs"],
        "fit_score": 85,
        "summary": "Tech-savvy developers focused on quality",
        "is_primary": True,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def sample_move():
    """Sample move data for testing"""
    return {
        "id": "test-move-id",
        "workspace_id": "test-workspace-id",
        "campaign_id": None,
        "name": "Test Move",
        "category": "ignite",
        "goal": "Test the move functionality",
        "target_icp_id": "test-icp-id",
        "strategy": {"approach": "comprehensive"},
        "execution_plan": [{"step": "Plan", "duration": 1}],
        "status": "draft",
        "duration_days": 30,
        "started_at": None,
        "completed_at": None,
        "success_metrics": [{"metric": "coverage", "target": 90}],
        "results": {},
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def sample_campaign():
    """Sample campaign data for testing"""
    return {
        "id": "test-campaign-id",
        "workspace_id": "test-workspace-id",
        "name": "Test Campaign",
        "description": "A campaign for testing purposes",
        "target_icps": ["test-icp-id"],
        "phases": [{"phase": "Planning", "duration": 7}],
        "budget_usd": 1000.0,
        "status": "planning",
        "started_at": None,
        "ended_at": None,
        "success_metrics": [{"metric": "leads", "target": 100}],
        "results": {},
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def sample_muse_asset():
    """Sample muse asset data for testing"""
    return {
        "id": "test-asset-id",
        "workspace_id": "test-workspace-id",
        "asset_type": "email",
        "title": "Test Email",
        "content": "This is a test email content",
        "content_html": "<p>This is a test email content</p>",
        "metadata": {"word_count": 100},
        "target_icp_id": "test-icp-id",
        "move_id": None,
        "status": "draft",
        "quality_score": 75,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def sample_blackbox_strategy():
    """Sample blackbox strategy data for testing"""
    return {
        "id": "test-strategy-id",
        "workspace_id": "test-workspace-id",
        "name": "Test Strategy",
        "focus_area": "acquisition",
        "risk_level": 5,
        "risk_reasons": ["Market uncertainty", "Competition"],
        "phases": [{"phase": "Research", "duration_days": 7}],
        "expected_upside": "Increased user acquisition",
        "potential_downside": "Resource requirements",
        "status": "proposed",
        "accepted_at": None,
        "converted_move_id": None,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def sample_daily_win():
    """Sample daily win data for testing"""
    return {
        "id": "test-win-id",
        "workspace_id": "test-workspace-id",
        "win_date": "2024-01-01",
        "topic": "Test Topic",
        "angle": "Testing angle",
        "hook": "Did you know?",
        "outline": "Introduction, main points, conclusion",
        "platform": "twitter",
        "estimated_minutes": 15,
        "trend_source": "Industry trends",
        "relevance_score": 80,
        "status": "idea",
        "posted_at": None,
        "expanded_content_id": None,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def sample_agent_execution():
    """Sample agent execution data for testing"""
    return {
        "id": "test-execution-id",
        "workspace_id": "test-workspace-id",
        "user_id": "test-user-id",
        "session_id": "test-session-id",
        "agent_name": "test_agent",
        "input": {"task": "test"},
        "output": {"result": "success"},
        "status": "completed",
        "tokens_used": 1000,
        "cost_usd": 0.01,
        "started_at": "2024-01-01T00:00:00Z",
        "completed_at": "2024-01-01T00:05:00Z",
        "error": None,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:05:00Z",
    }


@pytest.fixture
async def test_database():
    """Test database setup and teardown"""
    # This would set up a test database
    # For now, we'll use the mock client
    yield mock_supabase_client()

    # Cleanup would happen here


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Test utilities
def assert_valid_uuid(uuid_string: str):
    """Assert that a string is a valid UUID"""
    import uuid

    try:
        uuid.UUID(uuid_string)
    except ValueError:
        pytest.fail(f"Invalid UUID: {uuid_string}")


def assert_valid_email(email: str):
    """Assert that a string is a valid email"""
    import re

    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        pytest.fail(f"Invalid email: {email}")


def assert_valid_subscription_tier(tier: str):
    """Assert that a subscription tier is valid"""
    valid_tiers = {"free", "starter", "pro", "growth", "enterprise"}
    if tier not in valid_tiers:
        pytest.fail(f"Invalid subscription tier: {tier}")


def assert_valid_asset_type(asset_type: str):
    """Assert that an asset type is valid"""
    valid_types = {
        "email",
        "social_post",
        "blog",
        "ad_copy",
        "headline",
        "script",
        "carousel",
    }
    if asset_type not in valid_types:
        pytest.fail(f"Invalid asset type: {asset_type}")


def assert_valid_platform(platform: str):
    """Assert that a platform is valid"""
    valid_platforms = {
        "twitter",
        "linkedin",
        "instagram",
        "facebook",
        "tiktok",
        "blog",
        "email",
    }
    if platform not in valid_platforms:
        pytest.fail(f"Invalid platform: {platform}")


def assert_valid_status(status: str, status_type: str = "general"):
    """Assert that a status is valid for the given type"""
    if status_type == "general":
        valid_statuses = {"draft", "active", "paused", "completed", "archived"}
    elif status_type == "campaign":
        valid_statuses = {"planning", "active", "paused", "completed", "archived"}
    elif status_type == "move":
        valid_statuses = {"draft", "active", "paused", "completed", "archived"}
    elif status_type == "asset":
        valid_statuses = {"draft", "published", "archived", "template"}
    elif status_type == "strategy":
        valid_statuses = {"proposed", "accepted", "rejected", "archived"}
    elif status_type == "daily_win":
        valid_statuses = {"idea", "expanded", "posted", "archived"}
    elif status_type == "execution":
        valid_statuses = {"running", "completed", "failed", "cancelled"}
    else:
        pytest.fail(f"Unknown status type: {status_type}")

    if status not in valid_statuses:
        pytest.fail(f"Invalid {status_type} status: {status}")


# Mock data generators
def generate_test_user_data(overrides: Dict[str, Any] = None) -> Dict[str, Any]:
    """Generate test user data with optional overrides"""
    data = {
        "email": "test@example.com",
        "full_name": "Test User",
        "subscription_tier": "free",
        "budget_limit_monthly": 1.0,
        "preferences": {"theme": "light"},
    }
    if overrides:
        data.update(overrides)
    return data


def generate_test_workspace_data(overrides: Dict[str, Any] = None) -> Dict[str, Any]:
    """Generate test workspace data with optional overrides"""
    data = {
        "name": "Test Workspace",
        "slug": "test-workspace",
        "settings": {"timezone": "UTC", "currency": "USD"},
    }
    if overrides:
        data.update(overrides)
    return data


def generate_test_foundation_data(overrides: Dict[str, Any] = None) -> Dict[str, Any]:
    """Generate test foundation data with optional overrides"""
    data = {
        "company_name": "Test Company",
        "mission": "To test effectively",
        "vision": "Comprehensive test coverage",
        "values": ["Quality", "Reliability"],
        "industry": "Technology",
        "target_market": "Developers",
    }
    if overrides:
        data.update(overrides)
    return data


def generate_test_icp_data(overrides: Dict[str, Any] = None) -> Dict[str, Any]:
    """Generate test ICP data with optional overrides"""
    data = {
        "name": "Test ICP",
        "tagline": "Ideal customer profile",
        "market_sophistication": 3,
        "demographics": {"age_range": "25-45"},
        "psychographics": {"values": ["Quality"]},
        "behaviors": {"tech_savvy": True},
        "pain_points": ["Testing challenges"],
        "goals": ["Improve coverage"],
        "fit_score": 85,
        "is_primary": False,
    }
    if overrides:
        data.update(overrides)
    return data
