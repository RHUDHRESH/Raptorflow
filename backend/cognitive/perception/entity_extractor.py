"""
Entity Extractor

Extracts entities from text using LLM with confidence scoring.
"""

import asyncio
import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from cognitive.models import Entity, EntityType


@dataclass
class EntityExtractionResult:
    """Result of entity extraction."""

    entities: List[Entity]
    confidence: float
    processing_time_ms: int


class EntityExtractor:
    """Extracts entities from text using LLM with confidence scoring."""

    def __init__(self, llm_client=None):
        """
        Initialize the entity extractor.

        Args:
            llm_client: LLM client for entity extraction (e.g., VertexAI client)
        """
        self.llm_client = llm_client
        self.entity_patterns = {
            # Regex patterns for common entities as fallback
            EntityType.COMPANY: [
                r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+Inc\.?|Corp\.?|LLC|Ltd\.?)\b",
                r"\b[A-Z]{2,}\b",  # All caps company names
            ],
            EntityType.PERSON: [
                r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\b",  # First Last
            ],
            EntityType.MONEY: [
                r"\$\d+(?:,\d{3})*(?:\.\d{2})?",
                r"\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:USD|dollars?|cents?)",
            ],
            EntityType.DATE: [
                r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
                r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b",
            ],
            EntityType.PERCENTAGE: [
                r"\d+(?:\.\d+)?%",
                r"\d+(?:\.\d+)?\s*percent",
            ],
        }

    async def extract(self, text: str) -> List[Entity]:
        """
        Extract entities from text.

        Args:
            text: Input text to extract entities from

        Returns:
            List of extracted entities with confidence scores
        """
        if not text or not text.strip():
            return []

        start_time = asyncio.get_event_loop().time()

        # Try LLM extraction first if available
        if self.llm_client:
            try:
                entities = await self._extract_with_llm(text)
            except Exception as e:
                print(f"LLM extraction failed: {e}")
                entities = []
        else:
            entities = await self._extract_with_llm(text)  # Use mock LLM

        processing_time = int((asyncio.get_event_loop().time() - start_time) * 1000)

        # Sort by confidence and position
        entities.sort(key=lambda e: (-e.confidence, e.start_pos))

        return entities

    async def _extract_with_llm(self, text: str) -> List[Entity]:
        """
        Extract entities using LLM.

        Args:
            text: Input text

        Returns:
            List of entities extracted by LLM
        """
        # This is a mock implementation - in production, this would call the actual LLM
        # For now, we'll simulate LLM responses with some heuristics

        prompt = f"""
Extract entities from the following text. Return JSON with this format:
{{
    "entities": [
        {{
            "text": "entity text",
            "type": "person|company|product|location|date|money|percentage",
            "confidence": 0.95,
            "start_pos": 0,
            "end_pos": 10
        }}
    ]
}}

Text: {text}

Only extract clear, unambiguous entities. Be conservative with confidence scores.
"""

        # Mock LLM response - in production this would be an actual API call
        mock_response = self._generate_mock_llm_response(text)

        try:
            data = json.loads(mock_response)
            entities = []

            for entity_data in data.get("entities", []):
                try:
                    entity_type = EntityType(entity_data["type"])
                    entity = Entity(
                        text=entity_data["text"],
                        type=entity_type,
                        confidence=float(entity_data["confidence"]),
                        start_pos=int(entity_data["start_pos"]),
                        end_pos=int(entity_data["end_pos"]),
                        metadata=entity_data.get("metadata", {}),
                    )
                    entities.append(entity)
                except (ValueError, KeyError) as e:
                    print(f"Invalid entity data: {entity_data}, error: {e}")
                    continue

            return entities

        except json.JSONDecodeError as e:
            print(f"Failed to parse LLM response: {e}")
            return []  # Return empty list instead of fallback

    def _generate_mock_llm_response(self, text: str) -> str:
        """
        Generate mock LLM response for testing.
        In production, this would be replaced with actual LLM API call.
        """
        entities = []

        # More conservative entity extraction for mock
        # Only extract clear, unambiguous entities

        # Company names with Inc/Corp/Ltd
        import re

        company_patterns = [
            r"\b[A-Z][a-z]+\s+(?:Inc\.?|Corp\.?|LLC|Ltd\.?)\b",
            r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\s+(?:Inc\.?|Corp\.?|LLC|Ltd\.?)\b",
        ]

        for pattern in company_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                entities.append(
                    {
                        "text": match.group(),
                        "type": "company",
                        "confidence": 0.90,
                        "start_pos": match.start(),
                        "end_pos": match.end(),
                    }
                )

        # Money patterns
        money_patterns = [
            r"\$\d+(?:,\d{3})*(?:\.\d{2})?(?:\s*(?:billion|million|thousand))?",
            r"\$\d+(?:\.\d{2})?\s*(?:billion|million|thousand)",
            r"\$\d+\.\d+\s*billion",
            r"\$\d+\.\d+\s*million",
            r"\$\d+\.\d+\s*thousand",
        ]

        for pattern in money_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entities.append(
                    {
                        "text": match.group(),
                        "type": "money",
                        "confidence": 0.95,
                        "start_pos": match.start(),
                        "end_pos": match.end(),
                    }
                )

        # Percentage patterns
        percent_patterns = [r"\d+(?:\.\d+)?%", r"\d+(?:\.\d+)?\s*percent"]

        for pattern in percent_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entities.append(
                    {
                        "text": match.group(),
                        "type": "percentage",
                        "confidence": 0.92,
                        "start_pos": match.start(),
                        "end_pos": match.end(),
                    }
                )

        # Person names (First Last pattern)
        person_pattern = r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\b"
        # Only match if not part of company name and not common words
        common_words = {
            "The",
            "This",
            "That",
            "From",
            "With",
            "And",
            "For",
            "But",
            "Not",
            "All",
            "Any",
            "Can",
            "Will",
            "Just",
            "Out",
            "Get",
            "Got",
            "See",
            "Look",
            "Now",
            "New",
            "Old",
            "Good",
            "Bad",
            "Big",
            "Small",
        }

        for match in re.finditer(person_pattern, text):
            words = match.group().split()
            if words[0] in common_words or words[1] in common_words:
                continue

            text_before = text[: match.start()].lower()
            text_after = text[match.end() :].lower()

            # Check for company indicators - be more specific
            # Only check immediate vicinity (within 10 characters)
            immediate_before = (
                text_before[-10:] if len(text_before) >= 10 else text_before
            )
            immediate_after = text_after[:10] if len(text_after) >= 10 else text_after

            before_inc = any(
                inc in immediate_before for inc in ["inc", "corp", "llc", "ltd"]
            )
            after_inc = any(
                inc in immediate_after for inc in ["inc", "corp", "llc", "ltd"]
            )

            # Also check if the entity itself contains company indicators
            entity_has_company = any(
                inc in match.group().lower() for inc in ["inc", "corp", "llc", "ltd"]
            )

            if not entity_has_company and not before_inc and not after_inc:
                entities.append(
                    {
                        "text": match.group(),
                        "type": "person",
                        "confidence": 0.85,
                        "start_pos": match.start(),
                        "end_pos": match.end(),
                    }
                )

        # Date patterns
        date_patterns = [
            r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b",
            r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
        ]

        for pattern in date_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                entities.append(
                    {
                        "text": match.group(),
                        "type": "date",
                        "confidence": 0.88,
                        "start_pos": match.start(),
                        "end_pos": match.end(),
                    }
                )

        return json.dumps({"entities": entities})

    def _extract_with_regex(self, text: str) -> List[Entity]:
        """
        Extract entities using regex patterns as fallback.

        Args:
            text: Input text

        Returns:
            List of entities extracted via regex
        """
        entities = []

        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)

                for match in matches:
                    entity = Entity(
                        text=match.group(),
                        type=entity_type,
                        confidence=0.7,  # Lower confidence for regex
                        start_pos=match.start(),
                        end_pos=match.end(),
                        metadata={"extraction_method": "regex"},
                    )
                    entities.append(entity)

        return entities

    def validate_entity(self, entity: Entity) -> bool:
        """
        Validate an entity meets minimum criteria.

        Args:
            entity: Entity to validate

        Returns:
            True if entity is valid
        """
        # Basic validation
        if not entity.text or not entity.text.strip():
            return False

        if entity.confidence < 0.5:
            return False

        if entity.start_pos < 0 or entity.end_pos <= entity.start_pos:
            return False

        # Type-specific validation
        if entity.type == EntityType.MONEY:
            # Money should contain digits
            if not re.search(r"\d", entity.text):
                return False

        elif entity.type == EntityType.PERCENTAGE:
            # Percentage should contain % or 'percent'
            if "%" not in entity.text and "percent" not in entity.text.lower():
                return False

        return True

    def filter_overlapping_entities(self, entities: List[Entity]) -> List[Entity]:
        """
        Filter out overlapping entities, keeping higher confidence ones.

        Args:
            entities: List of entities to filter

        Returns:
            Filtered list of non-overlapping entities
        """
        if not entities:
            return []

        # Sort by confidence (descending) then by start position
        entities.sort(key=lambda e: (-e.confidence, e.start_pos))

        filtered = []
        occupied_ranges = []

        for entity in entities:
            # Check if this entity overlaps with any already accepted entity
            overlap = False
            for start, end in occupied_ranges:
                if not (entity.end_pos <= start or entity.start_pos >= end):
                    overlap = True
                    break

            if not overlap:
                filtered.append(entity)
                occupied_ranges.append((entity.start_pos, entity.end_pos))

        return filtered
