"""
Perception Module - Stub implementation for testing
"""

from cognitive.models import PerceivedInput


class PerceptionModule:
    """Stub implementation"""

    async def perceive(self, text: str, history):
        return PerceivedInput(
            raw_text=text,
            entities=[],
            intent=None,
            sentiment=None,
            urgency=None,
            context_signals=None,
        )
