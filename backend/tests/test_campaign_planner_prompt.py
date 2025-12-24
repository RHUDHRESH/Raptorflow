import pytest

from backend.core.prompts import CampaignPrompts


def test_campaign_planner_persona_structure():
    """Verify that the campaign planner prompt has the required SOTA sections."""
    prompt = CampaignPrompts.PLANNER_SYSTEM
    assert "# ROLE" in prompt
    assert "Master Strategist" in prompt
    assert "90-day marketing arc" in prompt
    assert "CONSTRAINTS" in prompt


def test_campaign_arc_generation_structure():
    prompt = CampaignPrompts.ARC_GENERATION
    assert "{uvps}" in prompt
    assert "{evidence}" in prompt
