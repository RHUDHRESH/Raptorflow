"""
Perception Module Tests

Tests for the perception module including entity extraction,
intent detection, sentiment analysis, and urgency classification.
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest

from backend.cognitive.models import PerceivedInput
from backend.cognitive.perception.module import PerceptionModule
from backend.llm import LLMClient, ModelConfig


@pytest.mark.asyncio
class TestPerceptionModule:
    """Test suite for PerceptionModule."""

    async def test_perceive_basic(self, perception_module, sample_text):
        """Test basic perception functionality."""
        # Arrange
        text = "Create a marketing email for our new product launch"
        history = []

        # Act
        result = await perception_module.perceive(text, history)

        # Assert
        assert isinstance(result, PerceivedInput)
        assert result.raw_text == text
        assert result.entities is not None
        assert result.intent is not None
        assert result.sentiment is not None
        assert isinstance(result.urgency, int)
        assert 1 <= result.urgency <= 5

    async def test_perceive_with_history(self, perception_module):
        """Test perception with conversation history."""
        # Arrange
        text = "Make it more professional"
        history = [
            {"role": "user", "content": "Create a marketing email"},
            {"role": "assistant", "content": "Here's a draft email..."},
        ]

        # Act
        result = await perception_module.perceive(text, history)

        # Assert
        assert result.context_signals is not None
        assert "topic_continuity" in result.context_signals

    async def test_entity_extraction(self, perception_module, mock_llm_client):
        """Test entity extraction functionality."""
        # Arrange
        text = "John Doe from Acme Corp wants to launch a $5000 product in Q1 2024"

        # Mock LLM response
        mock_response = Mock()
        mock_response.text = """
        {
            "entities": [
                {"type": "person", "text": "John Doe", "confidence": 0.9},
                {"type": "company", "text": "Acme Corp", "confidence": 0.8},
                {"type": "money", "text": "$5000", "confidence": 0.9},
                {"type": "date", "text": "Q1 2024", "confidence": 0.8}
            ]
        }
        """
        mock_llm_client.generate = AsyncMock(return_value=mock_response)

        # Act
        entities = await perception_module.entity_extractor.extract(text)

        # Assert
        assert len(entities) == 4
        assert entities[0]["type"] == "person"
        assert entities[0]["text"] == "John Doe"
        assert entities[0]["confidence"] == 0.9

    async def test_intent_detection(self, perception_module, mock_llm_client):
        """Test intent detection functionality."""
        # Arrange
        text = "Please delete all user data"

        # Mock LLM response
        mock_response = Mock()
        mock_response.text = """
        {
            "intent_type": "DELETE",
            "confidence": 0.95,
            "sub_intents": ["data_cleanup", "privacy"],
            "parameters": {"target": "user_data", "scope": "all"}
        }
        """
        mock_llm_client.generate = AsyncMock(return_value=mock_response)

        # Act
        intent = await perception_module.intent_detector.detect(text)

        # Assert
        assert intent.intent_type == "DELETE"
        assert intent.confidence == 0.95
        assert "data_cleanup" in intent.sub_intents

    async def test_sentiment_analysis(self, perception_module, mock_llm_client):
        """Test sentiment analysis functionality."""
        # Arrange
        text = "I'm absolutely thrilled with this amazing feature!"

        # Mock LLM response
        mock_response = Mock()
        mock_response.text = """
        {
            "sentiment": "POSITIVE",
            "confidence": 0.92,
            "emotional_signals": ["excited", "happy"],
            "intensity": 0.8
        }
        """
        mock_llm_client.generate = AsyncMock(return_value=mock_response)

        # Act
        sentiment = await perception_module.sentiment_analyzer.analyze(text)

        # Assert
        assert sentiment.sentiment == "POSITIVE"
        assert sentiment.confidence == 0.92
        assert "excited" in sentiment.emotional_signals

    async def test_urgency_classification(self, perception_module, mock_llm_client):
        """Test urgency classification functionality."""
        # Arrange
        text = "This is extremely urgent - we need it immediately!"

        # Mock LLM response
        mock_response = Mock()
        mock_response.text = """
        {
            "level": 5,
            "signals": ["immediately", "extremely urgent"],
            "deadline_mentioned": "ASAP"
        }
        """
        mock_llm_client.generate = AsyncMock(return_value=mock_response)

        # Act
        urgency = await perception_module.urgency_classifier.classify(text)

        # Assert
        assert urgency.level == 5
        assert "immediately" in urgency.signals
        assert urgency.deadline_mentioned == "ASAP"

    async def test_context_signal_extraction(self, perception_module, mock_llm_client):
        """Test context signal extraction."""
        # Arrange
        text = "Can you expand on that point?"
        history = [
            {"role": "user", "content": "Tell me about marketing"},
            {"role": "assistant", "content": "Marketing involves..."},
        ]

        # Mock LLM response
        mock_response = Mock()
        mock_response.text = """
        {
            "topic_continuity": true,
            "reference_to_prior": "that point",
            "new_topic": false,
            "implicit_assumptions": ["user wants more detail"]
        }
        """
        mock_llm_client.generate = AsyncMock(return_value=mock_response)

        # Act
        context = await perception_module.context_signals.extract(text, history)

        # Assert
        assert context.topic_continuity is True
        assert context.reference_to_prior == "that point"
        assert context.new_topic is False

    async def test_parallel_processing(self, perception_module, mock_llm_client):
        """Test that perception components run in parallel."""
        # Arrange
        text = "Test message for parallel processing"
        history = []

        # Track call counts
        call_count = 0

        async def mock_generate(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.1)  # Simulate processing time
            return Mock(text='{"test": "response"}')

        mock_llm_client.generate = mock_generate

        # Act
        start_time = datetime.now()
        result = await perception_module.perceive(text, history)
        end_time = datetime.now()

        # Assert
        processing_time = (end_time - start_time).total_seconds()

        # Should be faster than sequential processing
        # 4 components * 0.1s each = 0.4s sequential, but parallel should be ~0.1s
        assert processing_time < 0.3  # Allow some margin
        assert call_count >= 4  # Should call multiple components

    async def test_error_handling(self, perception_module, mock_llm_client):
        """Test error handling in perception module."""
        # Arrange
        text = "Test message"
        history = []

        # Mock LLM to raise exception
        mock_llm_client.generate = AsyncMock(side_effect=Exception("LLM error"))

        # Act & Assert
        result = await perception_module.perceive(text, history)

        # Should still return a valid PerceivedInput with defaults
        assert isinstance(result, PerceivedInput)
        assert result.raw_text == text
        assert result.entities == {}
        assert result.sentiment == "NEUTRAL"
        assert result.urgency == 3  # Default urgency

    async def test_empty_input(self, perception_module):
        """Test perception with empty input."""
        # Arrange
        text = ""
        history = []

        # Act
        result = await perception_module.perceive(text, history)

        # Assert
        assert result.raw_text == ""
        assert result.entities == {}
        assert result.sentiment == "NEUTRAL"
        assert result.urgency == 1  # Low urgency for empty input

    async def test_very_long_input(self, perception_module):
        """Test perception with very long input."""
        # Arrange
        text = "Test " * 10000  # Very long text
        history = []

        # Act
        result = await perception_module.perceive(text, history)

        # Assert
        assert isinstance(result, PerceivedInput)
        assert len(result.raw_text) == len(text)
        # Should handle long text without issues

    async def test_multilingual_input(self, perception_module, mock_llm_client):
        """Test perception with multilingual input."""
        # Arrange
        text = "Créez un email marketing pour notre nouveau produit"

        # Mock LLM response for French text
        mock_response = Mock()
        mock_response.text = """
        {
            "entities": [{"type": "product", "text": "produit", "confidence": 0.8}],
            "intent_type": "CREATE",
            "confidence": 0.9,
            "sentiment": "NEUTRAL",
            "confidence": 0.8,
            "level": 3,
            "signals": []
        }
        """
        mock_llm_client.generate = AsyncMock(return_value=mock_response)

        # Act
        result = await perception_module.perceive(text, [])

        # Assert
        assert isinstance(result, PerceivedInput)
        assert result.raw_text == text
        # Should handle multilingual input


@pytest.mark.asyncio
class TestPerceptionModuleIntegration:
    """Integration tests for perception module."""

    async def test_full_perception_pipeline(self, perception_module):
        """Test the complete perception pipeline."""
        # Arrange
        text = (
            "URGENT: John from Microsoft needs a technical presentation by tomorrow EOD"
        )
        history = [
            {"role": "user", "content": "I need help with a presentation"},
            {"role": "assistant", "content": "I can help you create a presentation"},
        ]

        # Act
        result = await perception_module.perceive(text, history)

        # Assert
        assert result.raw_text == text
        assert "John" in str(result.entities) or "Microsoft" in str(result.entities)
        assert result.urgency >= 4  # Should detect urgency
        assert result.sentiment in ["POSITIVE", "NEGATIVE", "NEUTRAL", "MIXED"]
        assert result.context_signals is not None

    async def test_perception_with_complex_context(self, perception_module):
        """Test perception with complex conversation context."""
        # Arrange
        text = "Actually, can you make it more formal?"
        history = [
            {"role": "user", "content": "Write an email to our investors"},
            {"role": "assistant", "content": "Hey investors, great news!"},
            {"role": "user", "content": "That's too casual"},
            {
                "role": "assistant",
                "content": "Dear investors, I'm pleased to announce...",
            },
        ]

        # Act
        result = await perception_module.perceive(text, history)

        # Assert
        assert result.context_signals.get("topic_continuity") is True
        assert result.context_signals.get("reference_to_prior") is not None
        # Should understand the context about formality


if __name__ == "__main__":
    pytest.main([__file__])
