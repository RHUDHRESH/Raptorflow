import pytest

from core.channels import ChannelAllocator


def test_channel_allocation_logic():
    """
    Phase 56: Verify that the ChannelAllocator weights channels based on ICP.
    """
    founder_personas = [{"name": "Solo Founder"}]

    allocations = ChannelAllocator.allocate("Lead gen", founder_personas)

    assert len(allocations) > 0
    linkedin = next(a for p in [allocations] for a in p if a.channel == "linkedin")
    assert linkedin.weight >= 0.4
    assert "founder" in linkedin.reasoning.lower()
