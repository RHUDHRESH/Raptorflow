"""
Urgency Classifier - Stub implementation for testing
"""

from cognitive.models import UrgencyResult


class UrgencyClassifier:
    """Stub implementation"""

    async def classify(self, text: str):
        return UrgencyResult(level=2, signals=[], reasoning="")
