from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.operators import (
    AuditResult,
    create_cdn_uploader,
    create_notion_operator,
    create_post_execution_auditor,
    create_slack_operator,
    create_social_publisher,
)


@pytest.mark.asyncio
async def test_post_execution_audit_logic():
    """Verify that the auditor verifies execution correctly."""
    mock_llm = MagicMock()
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = AuditResult(
        is_verified=True, final_location="CDN", metadata_integrity=0.99
    )

    with patch(
        "backend.agents.operators.PostExecutionAuditor.__init__", return_value=None
    ):
        auditor = create_post_execution_auditor(mock_llm)
        auditor.chain = mock_chain

        state = {"status": "synced", "current_brief": {}}
        result = await auditor(state)

        assert result["status"] == "fully_verified"


@pytest.mark.asyncio
async def test_social_publish_logic():
    """Verify that the operator simulates social publishing correctly."""
    operator = create_social_publisher(platform="LinkedIn")
    state = {"current_draft": "SOTA Post"}

    result = await operator(state)
    assert result["status"] == "published_to_linkedin"


@pytest.mark.asyncio
async def test_cdn_upload_logic():
    """Verify that the operator simulates CDN upload correctly."""
    operator = create_cdn_uploader(bucket="test-bucket")
    state = {"current_brief": {"image_prompt": {"temp_url": "tmp_123"}}}

    result = await operator(state)
    assert (
        "https://cdn.raptorflow.ai/test-bucket/"
        in result["current_brief"]["permanent_image_url"]
    )


@pytest.mark.asyncio
async def test_slack_notify_logic():
    """Verify that the operator simulates slack notification correctly."""
    operator = create_slack_operator(webhook_url="https://slack.com/hook")
    state = {"status": "completed"}

    result = await operator(state)
    assert result["status"] == "slack_notified"


@pytest.mark.asyncio
async def test_notion_sync_logic():
    """Verify that the operator simulates notion sync correctly."""
    operator = create_notion_operator(api_key="secret_notion")
    state = {"context_brief": {"campaign_arc": {"campaign_title": "Fortress"}}}

    result = await operator(state)
    assert result["status"] == "synced_to_notion"
