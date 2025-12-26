import pytest

from agents.specialists.security_auditor import SecurityAuditorAgent


@pytest.mark.asyncio
async def test_security_auditor_scan_logic():
    """Test the logic of the security auditor specialist."""
    agent = SecurityAuditorAgent()

    # Text with PII
    content = "My email is test@example.com and my phone is 555-0199."
    state = {"instructions": f"Scan for PII in: {content}", "messages": []}

    result = await agent(state)
    assert "pii_detected" in result
    assert result["pii_detected"] is True
    assert "redacted_content" in result
    assert "test@example.com" not in result["redacted_content"]


@pytest.mark.asyncio
async def test_security_auditor_clean_content():
    """Test security auditor with clean content."""
    agent = SecurityAuditorAgent()
    state = {"instructions": "Scan for PII in: Hello world", "messages": []}
    result = await agent(state)
    assert result["pii_detected"] is False


@pytest.mark.asyncio
async def test_security_auditor_phone_only():
    """Test security auditor with phone number only."""
    agent = SecurityAuditorAgent()
    state = {"instructions": "Call me at 123-456-7890", "messages": []}
    result = await agent(state)
    assert result["pii_detected"] is True
    assert "[PHONE_REDACTED]" in result["redacted_content"]
