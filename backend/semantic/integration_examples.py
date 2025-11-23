"""
Semantic Layer Integration Examples

This module demonstrates how to integrate semantic intelligence modules
with existing content and research agents.

Usage Examples:
1. Enriching content generation with intent analysis
2. Enhancing research with entity extraction
3. Improving content quality with emotional intelligence
4. Topic-based content clustering
5. Semantic similarity for content recommendations
"""

from typing import Any, Dict, List, Optional
import structlog

from backend.semantic.intent_detector import intent_detector
from backend.semantic.entity_extractor import entity_extractor
from backend.semantic.emotional_intelligence import emotional_intelligence_agent
from backend.semantic.topic_modeler import topic_modeler
from backend.semantic.semantic_similarity import semantic_similarity

logger = structlog.get_logger(__name__)


class SemanticContentEnhancer:
    """
    Enhances content agent with semantic intelligence.

    Integration with ContentSupervisor:
    - Analyzes intent before content generation
    - Extracts entities to inform content strategy
    - Validates emotional alignment with brand
    - Ensures topic relevance
    """

    async def enrich_content_request(
        self,
        content_request: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enrich content request with semantic analysis before generation.

        Args:
            content_request: Original content request
            context: Additional context (workspace_id, icp_profile, etc.)

        Returns:
            Enriched context with semantic insights
        """
        topic = content_request.get("topic", "")
        workspace_id = context.get("workspace_id")

        logger.info(
            "Enriching content request with semantic analysis",
            topic=topic,
            workspace_id=workspace_id
        )

        # Step 1: Analyze intent of the requested topic
        intent_analysis = await intent_detector.analyze_intent(
            text=topic,
            context={
                "workspace_id": workspace_id,
                "content_type": content_request.get("content_type"),
                "stated_goals": content_request.get("goals"),
                "target_audience": context.get("icp_profile", {}).get("icp_name")
            }
        )

        # Step 2: Extract relevant entities from topic and ICP
        entity_data = await entity_extractor.extract_entities_and_relations(
            content=topic,
            context={
                "workspace_id": workspace_id,
                "domain": context.get("icp_profile", {}).get("industry")
            }
        )

        # Step 3: Find similar historical topics
        similar_topics = await topic_modeler.find_similar_topics(
            query_topic=topic,
            workspace_id=workspace_id,
            top_k=3
        )

        # Step 4: Find similar content for reference
        similar_content = await semantic_similarity.find_similar_content(
            query_text=topic,
            workspace_id=workspace_id,
            top_k=3,
            min_similarity=0.75
        )

        # Enrich context with semantic insights
        enriched_context = {
            **context,
            "semantic_intelligence": {
                "intent_analysis": {
                    "primary_intent": intent_analysis.get("primary", {}).get("intent"),
                    "intent_category": intent_analysis.get("primary", {}).get("category"),
                    "emotional_intent": intent_analysis.get("emotional", {}).get("primary_emotion"),
                    "conversion_goal": intent_analysis.get("conversion", {}).get("desired_action")
                },
                "key_entities": [
                    e.get("text")
                    for e in entity_data.get("entities", [])[:5]
                ],
                "related_topics": [
                    t.get("topic", {}).get("name")
                    for t in similar_topics
                ],
                "reference_content": [
                    c.get("content_id")
                    for c in similar_content
                ],
                "suggested_keywords": entity_data.get("summary", {}).get("key_entities", [])
            }
        }

        logger.info(
            "Content request enriched",
            intent=enriched_context["semantic_intelligence"]["intent_analysis"]["intent_category"],
            entities_found=len(enriched_context["semantic_intelligence"]["key_entities"])
        )

        return enriched_context

    async def validate_generated_content(
        self,
        content: str,
        original_request: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate generated content using semantic intelligence.

        Args:
            content: Generated content to validate
            original_request: Original content request
            context: Generation context

        Returns:
            Validation report with scores and recommendations
        """
        logger.info(
            "Validating generated content",
            content_length=len(content)
        )

        # Analyze emotional journey
        emotional_analysis = await emotional_intelligence_agent.analyze_emotional_journey(
            content=content,
            context={
                "target_audience": context.get("icp_profile", {}).get("icp_name"),
                "content_goal": original_request.get("topic"),
                "brand_values": context.get("brand_voice_profile", {}).get("values")
            }
        )

        # Extract entities to verify coverage
        content_entities = await entity_extractor.extract_entities_and_relations(
            content=content
        )

        # Analyze content intent
        content_intent = await intent_detector.analyze_intent(
            text=content,
            context={
                "stated_goals": original_request.get("goals")
            }
        )

        # Validation report
        validation = {
            "emotional_validation": {
                "resonance_score": emotional_analysis.get("emotional_resonance", {}).get("overall_resonance", 0),
                "authenticity_score": emotional_analysis.get("emotional_resonance", {}).get("authenticity_score", 0),
                "ethical_score": emotional_analysis.get("ethical_assessment", {}).get("ethical_score", 0),
                "passes_threshold": emotional_analysis.get("emotional_resonance", {}).get("overall_resonance", 0) >= 0.75
            },
            "entity_coverage": {
                "entities_found": len(content_entities.get("entities", [])),
                "key_concepts_covered": content_entities.get("summary", {}).get("central_concepts", []),
                "relationship_depth": len(content_entities.get("relationships", []))
            },
            "intent_alignment": {
                "intent_matches": (
                    content_intent.get("primary", {}).get("category") ==
                    context.get("semantic_intelligence", {}).get("intent_analysis", {}).get("intent_category")
                ),
                "alignment_score": content_intent.get("alignment", {}).get("context_alignment_score", 0),
                "passes_threshold": content_intent.get("alignment", {}).get("context_alignment_score", 0) >= 0.80
            },
            "overall_validation": {
                "passes_validation": True,  # Will be computed below
                "quality_score": 0.0,
                "recommendations": []
            }
        }

        # Compute overall validation
        quality_scores = [
            validation["emotional_validation"]["resonance_score"],
            validation["intent_alignment"]["alignment_score"],
            min(validation["entity_coverage"]["entities_found"] / 5.0, 1.0)  # Normalize
        ]

        validation["overall_validation"]["quality_score"] = sum(quality_scores) / len(quality_scores)
        validation["overall_validation"]["passes_validation"] = (
            validation["emotional_validation"]["passes_threshold"] and
            validation["intent_alignment"]["passes_threshold"]
        )

        # Generate recommendations
        if not validation["emotional_validation"]["passes_threshold"]:
            validation["overall_validation"]["recommendations"].append(
                "Improve emotional resonance - current score below threshold"
            )

        if not validation["intent_alignment"]["passes_threshold"]:
            validation["overall_validation"]["recommendations"].append(
                "Better align content with stated intent"
            )

        if validation["entity_coverage"]["entities_found"] < 3:
            validation["overall_validation"]["recommendations"].append(
                "Increase entity/concept coverage for richer content"
            )

        logger.info(
            "Content validation completed",
            passes=validation["overall_validation"]["passes_validation"],
            quality_score=validation["overall_validation"]["quality_score"]
        )

        return validation


class SemanticResearchEnhancer:
    """
    Enhances research agents with semantic intelligence.

    Integration with CustomerIntelligenceSupervisor:
    - Extract entities from research data
    - Build knowledge graphs of customer intelligence
    - Cluster ICPs by semantic similarity
    - Track topic trends in pain points
    """

    async def enrich_icp_with_entities(
        self,
        icp_data: Dict[str, Any],
        workspace_id: str
    ) -> Dict[str, Any]:
        """
        Enrich ICP profile with extracted entities and knowledge graph.

        Args:
            icp_data: ICP profile data
            workspace_id: Workspace ID

        Returns:
            Enriched ICP with entity data
        """
        logger.info(
            "Enriching ICP with entity extraction",
            icp_name=icp_data.get("icp_name"),
            workspace_id=workspace_id
        )

        # Combine ICP description fields
        combined_text = " ".join([
            icp_data.get("executive_summary", ""),
            " ".join(icp_data.get("pain_points", [])),
            " ".join(icp_data.get("goals", []))
        ])

        # Extract entities
        entity_data = await entity_extractor.extract_entities_and_relations(
            content=combined_text,
            context={
                "workspace_id": workspace_id,
                "domain": icp_data.get("industry"),
                "content_id": f"icp_{icp_data.get('id')}"
            }
        )

        # Enrich ICP data
        enriched_icp = {
            **icp_data,
            "semantic_enrichment": {
                "key_entities": entity_data.get("entities", [])[:10],
                "knowledge_graph": entity_data.get("knowledge_graph"),
                "central_concepts": entity_data.get("summary", {}).get("central_concepts", []),
                "entity_distribution": entity_data.get("summary", {}).get("entity_distribution", {})
            }
        }

        logger.info(
            "ICP enriched with entities",
            entity_count=len(entity_data.get("entities", []))
        )

        return enriched_icp

    async def cluster_icps_by_similarity(
        self,
        icps: List[Dict[str, Any]],
        workspace_id: str
    ) -> Dict[str, Any]:
        """
        Cluster ICPs by semantic similarity.

        Args:
            icps: List of ICP profiles
            workspace_id: Workspace ID

        Returns:
            Clustering results
        """
        logger.info(
            "Clustering ICPs by similarity",
            icp_count=len(icps),
            workspace_id=workspace_id
        )

        # Create text representations of ICPs
        icp_texts = [
            f"{icp.get('icp_name', '')} - {icp.get('executive_summary', '')}"
            for icp in icps
        ]

        # Cluster using semantic similarity
        clusters = await semantic_similarity.cluster_by_similarity(
            texts=icp_texts,
            num_clusters=None  # Auto-detect
        )

        # Enrich clusters with ICP data
        enriched_clusters = []
        for cluster in clusters.get("clusters", []):
            enriched_cluster = {
                **cluster,
                "icps": [
                    {
                        "id": icps[member["index"]].get("id"),
                        "name": icps[member["index"]].get("icp_name"),
                        "industry": icps[member["index"]].get("industry")
                    }
                    for member in cluster.get("members", [])
                ]
            }
            enriched_clusters.append(enriched_cluster)

        result = {
            "num_clusters": clusters.get("num_clusters"),
            "clusters": enriched_clusters,
            "insights": {
                "largest_cluster_size": max(len(c.get("icps", [])) for c in enriched_clusters) if enriched_clusters else 0,
                "average_cluster_size": sum(len(c.get("icps", [])) for c in enriched_clusters) / len(enriched_clusters) if enriched_clusters else 0
            }
        }

        logger.info(
            "ICP clustering completed",
            num_clusters=result["num_clusters"]
        )

        return result


# Example usage functions

async def example_content_generation_with_semantics():
    """Example: Generate content with semantic enrichment."""

    content_request = {
        "topic": "How AI is transforming B2B marketing automation",
        "content_type": "blog_post",
        "goals": "educate and convert",
        "length": "medium"
    }

    context = {
        "workspace_id": "workspace_123",
        "icp_profile": {
            "icp_name": "Marketing Directors at B2B SaaS",
            "industry": "B2B SaaS"
        }
    }

    enhancer = SemanticContentEnhancer()

    # Enrich request before generation
    enriched_context = await enhancer.enrich_content_request(
        content_request=content_request,
        context=context
    )

    # [Content generation would happen here using enriched_context]
    # generated_content = await content_supervisor.execute(...)

    # Validate generated content
    generated_content = "Sample generated content..."  # Placeholder

    validation = await enhancer.validate_generated_content(
        content=generated_content,
        original_request=content_request,
        context=enriched_context
    )

    return {
        "enriched_context": enriched_context,
        "validation": validation
    }


async def example_research_with_semantics():
    """Example: Enhance research with semantic intelligence."""

    icp_data = {
        "id": "icp_456",
        "icp_name": "DevOps Engineers",
        "industry": "Cloud Infrastructure",
        "executive_summary": "DevOps engineers managing Kubernetes clusters...",
        "pain_points": ["Complex deployment pipelines", "Monitoring overhead"],
        "goals": ["Automate infrastructure", "Reduce downtime"]
    }

    enhancer = SemanticResearchEnhancer()

    # Enrich ICP with entities
    enriched_icp = await enhancer.enrich_icp_with_entities(
        icp_data=icp_data,
        workspace_id="workspace_123"
    )

    return enriched_icp


# Export examples
__all__ = [
    "SemanticContentEnhancer",
    "SemanticResearchEnhancer",
    "example_content_generation_with_semantics",
    "example_research_with_semantics"
]
