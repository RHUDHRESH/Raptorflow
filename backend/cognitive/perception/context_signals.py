"""
Context Signal Extractor - Stub implementation for testing
"""

from cognitive.models import ContextSignals


class ContextSignalExtractor:
    """Stub implementation"""

    async def extract(self, text: str, history):
        return ContextSignals(topic_continuity=False, new_topic=True)
