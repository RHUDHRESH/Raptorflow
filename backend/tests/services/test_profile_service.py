import pytest
from core.models import User
from services.profile_service import ProfileService


@pytest.fixture
def auth_user() -> User:
    return User(
        id="auth-user-123",
        email="founder@example.com",
        full_name="Test Founder",
        subscription_tier="free",
    )


def test_ensure_profile_returns_workspace_and_subscription(monkeypatch, auth_user):
    service = ProfileService()

    def fake_get_or_create_user(user: User):
        assert user.id == auth_user.id
        return {
            "id": "db-user-123",
            "subscription_plan": "growth",
            "subscription_status": "trial",
        }

    def fake_get_or_create_workspace(user_record, user):
        assert user_record["id"] == "db-user-123"
        assert user.id == auth_user.id
        return {"id": "ws-456"}

    monkeypatch.setattr(service, "_get_or_create_user", fake_get_or_create_user)
    monkeypatch.setattr(
        service, "_get_or_create_workspace", fake_get_or_create_workspace
    )

    result = service.ensure_profile(auth_user)

    assert result["workspace_id"] == "ws-456"
    assert result["subscription_plan"] == "growth"
    assert result["subscription_status"] == "trial"


def test_verify_profile_uses_subscription_status(monkeypatch, auth_user):
    service = ProfileService()

    monkeypatch.setattr(
        service,
        "_get_user_by_auth_id",
        lambda auth_id: {
            "id": "db-user-123",
            "subscription_plan": "starter",
            "subscription_status": "trial",
        },
    )
    monkeypatch.setattr(service, "_get_user_by_id", lambda user_id: None)
    monkeypatch.setattr(
        service,
        "_get_workspace_for_owner",
        lambda owner_id: {"id": "ws-999"},
    )
    monkeypatch.setattr(
        service,
        "_get_active_subscription",
        lambda workspace_id: {"plan": "growth", "status": "active"},
    )

    result = service.verify_profile(auth_user)

    assert result["workspace_exists"] is True
    assert result["workspace_id"] == "ws-999"
    assert result["needs_payment"] is False
    assert result["subscription_plan"] == "growth"
    assert result["subscription_status"] == "active"
