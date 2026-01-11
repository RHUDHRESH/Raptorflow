"""
Sentiment Analyzer - Stub implementation for testing
"""

from cognitive.models import Sentiment, SentimentResult


class SentimentAnalyzer:
    """Stub implementation"""

    async def analyze(self, text: str):
        return SentimentResult(sentiment=Sentiment.NEUTRAL, confidence=0.7)
