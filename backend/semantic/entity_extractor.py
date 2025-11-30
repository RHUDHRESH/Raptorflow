"""
Entity Extractor - Identifies entities and builds knowledge graphs

This module extracts structured entities from content including:
- Products and services
- People and organizations
- Concepts and technologies
- Competitors and partners
- Relationships and connections

Builds a knowledge graph representation for semantic understanding.
"""

import json
from typing import Any, Dict, List, Optional, Set, Tuple
import structlog

from backend.services.vertex_ai_client import vertex_ai_client
from backend.utils.cache import redis_cache
from backend.utils.correlation import get_correlation_id

logger = structlog.get_logger(__name__)


class EntityExtractor:
    """
    Extracts entities and relationships from content to build knowledge graphs.

    Capabilities:
    - Extract typed entities (products, people, concepts, etc.)
    - Identify relationships between entities
    - Build knowledge graph representations
    - Detect sentiment and context for each entity
    - Track entity mentions across content
    """

    def __init__(self):
        self.cache_ttl = 86400  # 24 hours
        self.system_prompt = """You are an expert at extracting structured entities and relationships from text.

Extract all relevant entities and classify them into these categories:
1. PRODUCTS: Product names, features, services, offerings
2. PEOPLE: Individuals, roles, personas, influencers
3. ORGANIZATIONS: Companies, competitors, partners, institutions
4. CONCEPTS: Ideas, methodologies, frameworks, strategies
5. TECHNOLOGIES: Tools, platforms, programming languages, tech stacks
6. LOCATIONS: Geographic locations, markets, regions
7. METRICS: KPIs, numbers, statistics, benchmarks
8. EVENTS: Launches, milestones, campaigns, dates

For each entity, extract:
- Entity text (exact mention from content)
- Entity type (from categories above)
- Sentiment (positive, negative, neutral)
- Importance score (0.0 to 1.0)
- Context (surrounding context that explains the entity)
- Attributes (additional metadata about the entity)

Also identify RELATIONSHIPS between entities:
- Source entity
- Relationship type (competes_with, part_of, uses, created_by, enables, etc.)
- Target entity
- Confidence score (0.0 to 1.0)

Return your analysis as valid JSON matching this structure:
{
  "entities": [
    {
      "text": "entity mention",
      "type": "PRODUCT|PERSON|ORGANIZATION|CONCEPT|TECHNOLOGY|LOCATION|METRIC|EVENT",
      "normalized_name": "canonical name",
      "sentiment": "positive|negative|neutral",
      "importance": 0.85,
      "context": "surrounding context",
      "attributes": {
        "key": "value"
      },
      "mentions": 3,
      "positions": [12, 45, 89]
    }
  ],
  "relationships": [
    {
      "source": "entity1",
      "relation": "relationship_type",
      "target": "entity2",
      "confidence": 0.90,
      "evidence": "text that shows this relationship",
      "direction": "directed|undirected"
    }
  ],
  "knowledge_graph": {
    "nodes": [
      {
        "id": "node_id",
        "label": "entity name",
        "type": "entity type",
        "properties": {}
      }
    ],
    "edges": [
      {
        "source": "node_id1",
        "target": "node_id2",
        "label": "relationship",
        "weight": 0.90
      }
    ]
  },
  "summary": {
    "total_entities": 15,
    "entity_distribution": {
      "PRODUCT": 5,
      "TECHNOLOGY": 3
    },
    "key_entities": ["most important entities"],
    "central_concepts": ["main themes"]
  }
}"""

    async def extract_entities_and_relations(
        self,
        content: str,
        context: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract entities and relationships from content.

        Args:
            content: Text content to analyze
            context: Optional context including:
                - workspace_id: For storing in workspace memory
                - content_type: Type of content being analyzed
                - domain: Industry or domain for better entity recognition
                - existing_graph: Previous knowledge graph to merge with
            correlation_id: Request correlation ID

        Returns:
            Dict containing:
            {
                "entities": [...],
                "relationships": [...],
                "knowledge_graph": {...},
                "summary": {...},
                "metadata": {...}
            }
        """
        correlation_id = correlation_id or get_correlation_id()
        context = context or {}

        logger.info(
            "Extracting entities",
            content_length=len(content),
            has_context=bool(context),
            correlation_id=correlation_id
        )

        # Check cache
        cache_key = self._generate_cache_key(content)
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            logger.debug("Returning cached entity extraction", correlation_id=correlation_id)
            return cached_result

        try:
            # Build extraction prompt
            user_prompt = self._build_prompt(content, context)

            # Call Vertex AI for entity extraction
            response = await vertex_ai_client.generate_json(
                prompt=user_prompt,
                system_prompt=self.system_prompt,
                model_type="reasoning",
                temperature=0.2,  # Low temperature for consistent extraction
                max_tokens=3000
            )

            # Enhance result with metadata
            result = {
                **response,
                "metadata": {
                    "content_length": len(content),
                    "extracted_at": self._get_timestamp(),
                    "correlation_id": correlation_id,
                    "domain": context.get("domain", "general")
                }
            }

            # Post-process: deduplicate entities
            result = self._deduplicate_entities(result)

            # Post-process: calculate graph metrics
            result = self._calculate_graph_metrics(result)

            # Merge with existing graph if provided
            if context.get("existing_graph"):
                result = self._merge_knowledge_graphs(
                    result,
                    context["existing_graph"]
                )

            # Cache result
            await redis_cache.set(cache_key, result, ttl=self.cache_ttl)

            # Store in workspace memory
            if context.get("workspace_id"):
                await self._store_in_workspace_memory(
                    workspace_id=context["workspace_id"],
                    content_id=context.get("content_id", "unknown"),
                    entity_data=result
                )

            logger.info(
                "Entity extraction completed",
                entity_count=len(result.get("entities", [])),
                relationship_count=len(result.get("relationships", [])),
                correlation_id=correlation_id
            )

            return result

        except Exception as e:
            logger.error(
                "Entity extraction failed",
                error=str(e),
                correlation_id=correlation_id,
                exc_info=True
            )
            raise

    async def extract_specific_entities(
        self,
        content: str,
        entity_types: List[str],
        correlation_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract only specific types of entities.

        Args:
            content: Text to analyze
            entity_types: List of entity types to extract (e.g., ["PRODUCT", "TECHNOLOGY"])
            correlation_id: Request correlation ID

        Returns:
            List of entities matching the specified types
        """
        result = await self.extract_entities_and_relations(
            content=content,
            correlation_id=correlation_id
        )

        # Filter to requested types
        entities = [
            e for e in result.get("entities", [])
            if e.get("type") in entity_types
        ]

        logger.info(
            "Filtered entity extraction",
            total_entities=len(result.get("entities", [])),
            filtered_count=len(entities),
            types=entity_types
        )

        return entities

    async def build_cumulative_graph(
        self,
        contents: List[str],
        workspace_id: str,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Build a cumulative knowledge graph from multiple content pieces.

        Args:
            contents: List of content to analyze
            workspace_id: Workspace to store cumulative graph
            correlation_id: Request correlation ID

        Returns:
            Merged knowledge graph from all content
        """
        correlation_id = correlation_id or get_correlation_id()

        logger.info(
            "Building cumulative knowledge graph",
            content_count=len(contents),
            workspace_id=workspace_id,
            correlation_id=correlation_id
        )

        cumulative_graph = {
            "entities": [],
            "relationships": [],
            "knowledge_graph": {"nodes": [], "edges": []},
            "summary": {}
        }

        for i, content in enumerate(contents):
            try:
                result = await self.extract_entities_and_relations(
                    content=content,
                    context={
                        "workspace_id": workspace_id,
                        "existing_graph": cumulative_graph,
                        "content_id": f"content_{i}"
                    },
                    correlation_id=correlation_id
                )

                cumulative_graph = self._merge_knowledge_graphs(
                    cumulative_graph,
                    result
                )

            except Exception as e:
                logger.warning(
                    "Failed to extract entities from content",
                    index=i,
                    error=str(e)
                )

        # Recalculate summary
        cumulative_graph = self._calculate_graph_metrics(cumulative_graph)

        # Store cumulative graph
        await self._store_cumulative_graph(workspace_id, cumulative_graph)

        logger.info(
            "Cumulative graph built",
            total_entities=len(cumulative_graph.get("entities", [])),
            total_relationships=len(cumulative_graph.get("relationships", [])),
            workspace_id=workspace_id
        )

        return cumulative_graph

    def _build_prompt(self, content: str, context: Dict[str, Any]) -> str:
        """Build extraction prompt with context."""
        prompt_parts = [
            f"Extract all entities and relationships from the following text:\n\n{content}\n\n"
        ]

        if context.get("domain"):
            prompt_parts.append(
                f"Domain/Industry: {context['domain']}\n"
                "Focus on domain-specific terminology and entities.\n"
            )

        if context.get("entity_focus"):
            prompt_parts.append(
                f"Pay special attention to: {', '.join(context['entity_focus'])}\n"
            )

        prompt_parts.append(
            "\nProvide a comprehensive entity extraction with knowledge graph in valid JSON format."
        )

        return "".join(prompt_parts)

    def _deduplicate_entities(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Remove duplicate entities by normalizing names."""
        entities = result.get("entities", [])
        seen_names: Set[str] = set()
        deduplicated = []

        for entity in entities:
            normalized = entity.get("normalized_name", entity.get("text", "")).lower()
            if normalized not in seen_names:
                seen_names.add(normalized)
                deduplicated.append(entity)
            else:
                # Merge mentions if duplicate found
                for existing in deduplicated:
                    if existing.get("normalized_name", "").lower() == normalized:
                        existing["mentions"] = existing.get("mentions", 1) + entity.get("mentions", 1)
                        break

        result["entities"] = deduplicated
        return result

    def _calculate_graph_metrics(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate knowledge graph metrics."""
        entities = result.get("entities", [])
        relationships = result.get("relationships", [])

        # Entity distribution
        entity_distribution = {}
        for entity in entities:
            entity_type = entity.get("type", "UNKNOWN")
            entity_distribution[entity_type] = entity_distribution.get(entity_type, 0) + 1

        # Key entities (by importance)
        sorted_entities = sorted(
            entities,
            key=lambda e: e.get("importance", 0),
            reverse=True
        )
        key_entities = [e.get("normalized_name", e.get("text")) for e in sorted_entities[:5]]

        # Central concepts (concepts with most relationships)
        entity_connection_count = {}
        for rel in relationships:
            source = rel.get("source")
            target = rel.get("target")
            entity_connection_count[source] = entity_connection_count.get(source, 0) + 1
            entity_connection_count[target] = entity_connection_count.get(target, 0) + 1

        central_concepts = sorted(
            entity_connection_count.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        central_concepts = [name for name, _ in central_concepts]

        result["summary"] = {
            "total_entities": len(entities),
            "total_relationships": len(relationships),
            "entity_distribution": entity_distribution,
            "key_entities": key_entities,
            "central_concepts": central_concepts,
            "graph_density": len(relationships) / max(len(entities), 1)
        }

        return result

    def _merge_knowledge_graphs(
        self,
        graph1: Dict[str, Any],
        graph2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge two knowledge graphs, deduplicating entities."""
        merged = {
            "entities": [],
            "relationships": [],
            "knowledge_graph": {"nodes": [], "edges": []}
        }

        # Merge entities
        entity_map = {}
        for entity in graph1.get("entities", []) + graph2.get("entities", []):
            normalized = entity.get("normalized_name", entity.get("text", "")).lower()
            if normalized not in entity_map:
                entity_map[normalized] = entity
            else:
                # Merge mentions
                existing = entity_map[normalized]
                existing["mentions"] = existing.get("mentions", 1) + entity.get("mentions", 1)
                # Keep higher importance score
                existing["importance"] = max(
                    existing.get("importance", 0),
                    entity.get("importance", 0)
                )

        merged["entities"] = list(entity_map.values())

        # Merge relationships (deduplicate by source-relation-target)
        rel_set = set()
        for rel in graph1.get("relationships", []) + graph2.get("relationships", []):
            rel_key = (rel.get("source"), rel.get("relation"), rel.get("target"))
            if rel_key not in rel_set:
                rel_set.add(rel_key)
                merged["relationships"].append(rel)

        # Rebuild knowledge graph structure
        merged["knowledge_graph"]["nodes"] = [
            {
                "id": e.get("normalized_name", e.get("text")),
                "label": e.get("text"),
                "type": e.get("type"),
                "properties": e.get("attributes", {})
            }
            for e in merged["entities"]
        ]

        merged["knowledge_graph"]["edges"] = [
            {
                "source": r.get("source"),
                "target": r.get("target"),
                "label": r.get("relation"),
                "weight": r.get("confidence", 0.5)
            }
            for r in merged["relationships"]
        ]

        return merged

    def _generate_cache_key(self, content: str) -> str:
        """Generate cache key for entity extraction."""
        import hashlib
        content_hash = hashlib.md5(content.encode()).hexdigest()
        return f"entities:{content_hash}"

    async def _store_in_workspace_memory(
        self,
        workspace_id: str,
        content_id: str,
        entity_data: Dict[str, Any]
    ) -> None:
        """Store entity data in workspace memory."""
        memory_key = f"workspace:{workspace_id}:entities:{content_id}"

        try:
            await redis_cache.set(memory_key, entity_data, ttl=86400 * 30)  # 30 days
            logger.debug(
                "Stored entities in workspace memory",
                workspace_id=workspace_id,
                content_id=content_id
            )
        except Exception as e:
            logger.warning(
                "Failed to store entities in workspace memory",
                error=str(e)
            )

    async def _store_cumulative_graph(
        self,
        workspace_id: str,
        graph: Dict[str, Any]
    ) -> None:
        """Store cumulative knowledge graph for workspace."""
        graph_key = f"workspace:{workspace_id}:knowledge_graph"

        try:
            await redis_cache.set(graph_key, graph, ttl=86400 * 90)  # 90 days
            logger.debug(
                "Stored cumulative knowledge graph",
                workspace_id=workspace_id
            )
        except Exception as e:
            logger.warning(
                "Failed to store cumulative graph",
                error=str(e)
            )

    def _get_timestamp(self) -> str:
        """Get current ISO timestamp."""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()


# Global instance
entity_extractor = EntityExtractor()
