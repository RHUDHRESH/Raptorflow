"""
Semantic Intelligence Layer for RaptorFlow

This module provides deep semantic understanding capabilities including:
- Intent detection (primary, secondary, hidden intents)
- Entity extraction and knowledge graph construction
- Emotional intelligence and journey analysis
- Topic modeling and clustering
- Semantic similarity computation

All modules integrate with the existing agent architecture and memory systems.
"""

from backend.semantic.intent_detector import IntentDetector, intent_detector
from backend.semantic.entity_extractor import EntityExtractor, entity_extractor
from backend.semantic.emotional_intelligence import EmotionalIntelligenceAgent, emotional_intelligence_agent
from backend.semantic.topic_modeler import TopicModeler, topic_modeler
from backend.semantic.semantic_similarity import SemanticSimilarity, semantic_similarity

__all__ = [
    "IntentDetector",
    "intent_detector",
    "EntityExtractor",
    "entity_extractor",
    "EmotionalIntelligenceAgent",
    "emotional_intelligence_agent",
    "TopicModeler",
    "topic_modeler",
    "SemanticSimilarity",
    "semantic_similarity",
]
