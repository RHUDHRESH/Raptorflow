"""
Topic Modeler - Extracts topics and clusters from content corpus

This module provides topic modeling capabilities including:
- Topic extraction from individual documents
- Topic clustering across document collections
- Trend analysis and topic evolution
- Topic similarity and relationships
- Keyword extraction per topic
"""

import json
from typing import Any, Dict, List, Optional, Set
from collections import Counter
import structlog

from backend.services.openai_client import openai_client
from backend.utils.cache import redis_cache
from backend.utils.correlation import get_correlation_id

logger = structlog.get_logger(__name__)


class TopicModeler:
    """
    Extracts topics and performs clustering analysis on text corpora.

    Capabilities:
    - Extract main topics from documents
    - Cluster related topics across multiple documents
    - Identify trending topics
    - Track topic evolution over time
    - Generate topic hierarchies and relationships
    """

    def __init__(self):
        self.cache_ttl = 86400  # 24 hours
        self.system_prompt = """You are an expert at topic modeling and content analysis.

Extract and analyze topics from text content.

For SINGLE DOCUMENT analysis, identify:
1. Main topics (3-7 primary subjects/themes)
2. Subtopics (detailed aspects of main topics)
3. Keywords (most relevant terms for each topic)
4. Topic weights (importance/prevalence of each topic, 0.0-1.0)
5. Topic relationships (how topics connect to each other)

For MULTI-DOCUMENT analysis, additionally identify:
1. Topic clusters (groups of related topics)
2. Trending topics (topics appearing frequently)
3. Emerging topics (new or growing topics)
4. Declining topics (less frequent topics)
5. Topic evolution (how topics change over the corpus)

Return analysis as valid JSON:
{
  "topics": [
    {
      "topic_id": "unique_id",
      "name": "topic name",
      "description": "detailed description",
      "keywords": ["keyword1", "keyword2", "keyword3"],
      "weight": 0.85,
      "sentiment": "positive|negative|neutral",
      "subtopics": ["subtopic1", "subtopic2"],
      "examples": ["quote from text"],
      "category": "technology|business|marketing|etc"
    }
  ],
  "topic_relationships": [
    {
      "topic1": "topic_id_1",
      "topic2": "topic_id_2",
      "relationship": "supports|contradicts|extends|examples_of",
      "strength": 0.75
    }
  ],
  "topic_hierarchy": {
    "parent_topic": ["child_topic_1", "child_topic_2"]
  },
  "summary": {
    "primary_topic": "most dominant topic",
    "topic_diversity": 0.80,
    "topic_coherence": 0.85,
    "total_topics": 5
  }
}

For CORPUS analysis (multiple documents), also include:
{
  "clusters": [
    {
      "cluster_id": "cluster_1",
      "name": "cluster name",
      "topics": ["topic_id_1", "topic_id_2"],
      "documents": ["doc_1", "doc_2"],
      "centroid_keywords": ["keyword1", "keyword2"],
      "cohesion_score": 0.82
    }
  ],
  "trends": {
    "trending_topics": [
      {
        "topic": "topic name",
        "frequency": 15,
        "growth_rate": 0.45,
        "trend": "rising|stable|declining"
      }
    ],
    "emerging_topics": ["new topic 1", "new topic 2"],
    "declining_topics": ["old topic 1"]
  },
  "evolution": {
    "topic_timeline": [
      {
        "period": "early|middle|late",
        "dominant_topics": ["topic1", "topic2"]
      }
    ]
  }
}"""

    async def extract_topics(
        self,
        content: str,
        context: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract topics from a single document.

        Args:
            content: Text content to analyze
            context: Optional context including:
                - min_topics: Minimum number of topics to extract
                - max_topics: Maximum number of topics to extract
                - domain: Industry/domain for better topic detection
                - workspace_id: For storing results
            correlation_id: Request correlation ID

        Returns:
            Dict containing topics, relationships, and hierarchy
        """
        correlation_id = correlation_id or get_correlation_id()
        context = context or {}

        logger.info(
            "Extracting topics",
            content_length=len(content),
            correlation_id=correlation_id
        )

        # Check cache
        cache_key = self._generate_cache_key(content, "single")
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            logger.debug("Returning cached topic extraction", correlation_id=correlation_id)
            return cached_result

        try:
            # Build prompt
            user_prompt = self._build_single_doc_prompt(content, context)

            # Extract topics using OpenAI
            response = await openai_client.generate_json(
                prompt=user_prompt,
                system_prompt=self.system_prompt,
                temperature=0.3,
                max_tokens=2500
            )

            # Add metadata
            result = {
                **response,
                "metadata": {
                    "content_length": len(content),
                    "extracted_at": self._get_timestamp(),
                    "correlation_id": correlation_id,
                    "document_type": "single"
                }
            }

            # Cache result
            await redis_cache.set(cache_key, result, ttl=self.cache_ttl)

            # Store in workspace memory
            if context.get("workspace_id"):
                await self._store_topics_in_memory(
                    workspace_id=context["workspace_id"],
                    content_id=context.get("content_id", "unknown"),
                    topics=result
                )

            logger.info(
                "Topic extraction completed",
                topic_count=len(result.get("topics", [])),
                primary_topic=result.get("summary", {}).get("primary_topic"),
                correlation_id=correlation_id
            )

            return result

        except Exception as e:
            logger.error(
                "Topic extraction failed",
                error=str(e),
                correlation_id=correlation_id,
                exc_info=True
            )
            raise

    async def extract_topics_from_corpus(
        self,
        documents: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract and cluster topics across multiple documents.

        Args:
            documents: List of documents, each with 'id' and 'content'
            context: Optional context for analysis
            correlation_id: Request correlation ID

        Returns:
            Dict containing topics, clusters, trends, and evolution
        """
        correlation_id = correlation_id or get_correlation_id()
        context = context or {}

        logger.info(
            "Extracting topics from corpus",
            document_count=len(documents),
            correlation_id=correlation_id
        )

        # First, extract topics from each document
        import asyncio
        individual_analyses = await asyncio.gather(*[
            self.extract_topics(
                content=doc.get("content", ""),
                context={**context, "content_id": doc.get("id")},
                correlation_id=correlation_id
            )
            for doc in documents
        ], return_exceptions=True)

        # Filter out exceptions
        valid_analyses = [
            a for a in individual_analyses
            if not isinstance(a, Exception)
        ]

        if not valid_analyses:
            raise ValueError("Failed to extract topics from any document")

        # Aggregate topics
        all_topics = []
        for analysis in valid_analyses:
            all_topics.extend(analysis.get("topics", []))

        # Build corpus analysis prompt
        corpus_summary = {
            "document_count": len(documents),
            "total_topics": len(all_topics),
            "topics": all_topics
        }

        user_prompt = self._build_corpus_prompt(corpus_summary, context)

        try:
            # Perform corpus-level analysis
            response = await openai_client.generate_json(
                prompt=user_prompt,
                system_prompt=self.system_prompt,
                temperature=0.3,
                max_tokens=3500
            )

            # Combine individual and corpus analyses
            result = {
                **response,
                "individual_analyses": valid_analyses,
                "metadata": {
                    "document_count": len(documents),
                    "total_topics_extracted": len(all_topics),
                    "analyzed_at": self._get_timestamp(),
                    "correlation_id": correlation_id,
                    "document_type": "corpus"
                }
            }

            # Store corpus analysis
            if context.get("workspace_id"):
                await self._store_corpus_analysis(
                    workspace_id=context["workspace_id"],
                    corpus_id=context.get("corpus_id", "default"),
                    analysis=result
                )

            logger.info(
                "Corpus topic extraction completed",
                document_count=len(documents),
                cluster_count=len(result.get("clusters", [])),
                trending_count=len(result.get("trends", {}).get("trending_topics", [])),
                correlation_id=correlation_id
            )

            return result

        except Exception as e:
            logger.error(
                "Corpus topic extraction failed",
                error=str(e),
                correlation_id=correlation_id,
                exc_info=True
            )
            raise

    async def find_similar_topics(
        self,
        query_topic: str,
        workspace_id: str,
        top_k: int = 5,
        correlation_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find topics similar to a query topic from workspace history.

        Args:
            query_topic: Topic to search for
            workspace_id: Workspace to search in
            top_k: Number of similar topics to return
            correlation_id: Request correlation ID

        Returns:
            List of similar topics with similarity scores
        """
        correlation_id = correlation_id or get_correlation_id()

        logger.info(
            "Finding similar topics",
            query=query_topic,
            workspace_id=workspace_id,
            correlation_id=correlation_id
        )

        # Get all topics from workspace
        workspace_topics = await self._get_workspace_topics(workspace_id)

        if not workspace_topics:
            logger.warning("No topics found in workspace", workspace_id=workspace_id)
            return []

        # Use semantic similarity to find matches
        # For now, we'll use a simple keyword-based approach
        # In production, this would use embeddings
        similar_topics = []

        query_keywords = set(query_topic.lower().split())

        for topic_data in workspace_topics:
            topics = topic_data.get("topics", [])
            for topic in topics:
                topic_keywords = set(
                    " ".join(topic.get("keywords", [])).lower().split()
                )
                topic_name_keywords = set(topic.get("name", "").lower().split())

                # Calculate simple similarity score
                keyword_overlap = len(query_keywords & topic_keywords) / max(len(query_keywords), 1)
                name_overlap = len(query_keywords & topic_name_keywords) / max(len(query_keywords), 1)

                similarity = max(keyword_overlap, name_overlap)

                if similarity > 0.1:  # Threshold
                    similar_topics.append({
                        "topic": topic,
                        "similarity_score": similarity,
                        "source": topic_data.get("metadata", {})
                    })

        # Sort by similarity and return top_k
        similar_topics.sort(key=lambda x: x["similarity_score"], reverse=True)

        logger.info(
            "Found similar topics",
            count=len(similar_topics[:top_k]),
            correlation_id=correlation_id
        )

        return similar_topics[:top_k]

    async def track_topic_trends(
        self,
        workspace_id: str,
        time_window_days: int = 30,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Track how topics trend over time in a workspace.

        Args:
            workspace_id: Workspace to analyze
            time_window_days: Number of days to analyze
            correlation_id: Request correlation ID

        Returns:
            Trend analysis showing topic changes over time
        """
        correlation_id = correlation_id or get_correlation_id()

        logger.info(
            "Tracking topic trends",
            workspace_id=workspace_id,
            time_window=time_window_days,
            correlation_id=correlation_id
        )

        # Get workspace topics with timestamps
        workspace_topics = await self._get_workspace_topics(workspace_id)

        if not workspace_topics:
            return {
                "trending_topics": [],
                "emerging_topics": [],
                "declining_topics": [],
                "stable_topics": []
            }

        # Aggregate topic frequencies
        topic_timeline = {}

        for topic_data in workspace_topics:
            timestamp = topic_data.get("metadata", {}).get("extracted_at", "")
            topics = topic_data.get("topics", [])

            for topic in topics:
                topic_name = topic.get("name")
                if topic_name not in topic_timeline:
                    topic_timeline[topic_name] = []
                topic_timeline[topic_name].append(timestamp)

        # Calculate trends
        trending_topics = []
        emerging_topics = []
        declining_topics = []
        stable_topics = []

        for topic_name, timestamps in topic_timeline.items():
            frequency = len(timestamps)

            # Simple trend detection based on frequency
            if frequency >= 5:
                if self._is_growing(timestamps):
                    trending_topics.append({
                        "topic": topic_name,
                        "frequency": frequency,
                        "trend": "rising"
                    })
                elif self._is_declining(timestamps):
                    declining_topics.append({
                        "topic": topic_name,
                        "frequency": frequency,
                        "trend": "declining"
                    })
                else:
                    stable_topics.append({
                        "topic": topic_name,
                        "frequency": frequency,
                        "trend": "stable"
                    })
            elif frequency >= 2:
                emerging_topics.append({
                    "topic": topic_name,
                    "frequency": frequency,
                    "trend": "emerging"
                })

        trend_report = {
            "trending_topics": sorted(trending_topics, key=lambda x: x["frequency"], reverse=True),
            "emerging_topics": sorted(emerging_topics, key=lambda x: x["frequency"], reverse=True),
            "declining_topics": sorted(declining_topics, key=lambda x: x["frequency"], reverse=True),
            "stable_topics": sorted(stable_topics, key=lambda x: x["frequency"], reverse=True),
            "metadata": {
                "workspace_id": workspace_id,
                "time_window_days": time_window_days,
                "analyzed_at": self._get_timestamp(),
                "total_unique_topics": len(topic_timeline)
            }
        }

        logger.info(
            "Topic trend analysis completed",
            trending=len(trending_topics),
            emerging=len(emerging_topics),
            declining=len(declining_topics),
            correlation_id=correlation_id
        )

        return trend_report

    def _build_single_doc_prompt(self, content: str, context: Dict[str, Any]) -> str:
        """Build prompt for single document topic extraction."""
        prompt_parts = [
            f"Extract topics from the following content:\n\n{content}\n\n"
        ]

        if context.get("min_topics") or context.get("max_topics"):
            min_topics = context.get("min_topics", 3)
            max_topics = context.get("max_topics", 7)
            prompt_parts.append(f"Extract between {min_topics} and {max_topics} topics.\n")

        if context.get("domain"):
            prompt_parts.append(
                f"Domain: {context['domain']}\n"
                "Focus on domain-specific topics.\n"
            )

        prompt_parts.append(
            "\nProvide topic analysis in valid JSON format."
        )

        return "".join(prompt_parts)

    def _build_corpus_prompt(self, corpus_summary: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Build prompt for corpus-level analysis."""
        prompt = f"""Analyze this corpus of {corpus_summary['document_count']} documents with {corpus_summary['total_topics']} extracted topics.

Topics extracted:
{json.dumps(corpus_summary['topics'][:50], indent=2)}  # Limit to first 50 for token efficiency

Perform corpus-level analysis including:
1. Topic clustering (group related topics)
2. Trend identification (which topics appear most frequently)
3. Emerging vs declining topics
4. Topic evolution across the corpus

Provide comprehensive corpus analysis in valid JSON format.
"""
        return prompt

    def _is_growing(self, timestamps: List[str]) -> bool:
        """Determine if topic is growing based on timestamps."""
        # Simple heuristic: more recent mentions than older mentions
        if len(timestamps) < 2:
            return False

        sorted_timestamps = sorted(timestamps)
        mid_point = len(sorted_timestamps) // 2

        recent_count = len(sorted_timestamps[mid_point:])
        older_count = len(sorted_timestamps[:mid_point])

        return recent_count > older_count

    def _is_declining(self, timestamps: List[str]) -> bool:
        """Determine if topic is declining based on timestamps."""
        if len(timestamps) < 2:
            return False

        sorted_timestamps = sorted(timestamps)
        mid_point = len(sorted_timestamps) // 2

        recent_count = len(sorted_timestamps[mid_point:])
        older_count = len(sorted_timestamps[:mid_point])

        return older_count > recent_count

    def _generate_cache_key(self, content: str, analysis_type: str) -> str:
        """Generate cache key for topic analysis."""
        import hashlib
        content_hash = hashlib.md5(content.encode()).hexdigest()
        return f"topics:{analysis_type}:{content_hash}"

    async def _store_topics_in_memory(
        self,
        workspace_id: str,
        content_id: str,
        topics: Dict[str, Any]
    ) -> None:
        """Store topic analysis in workspace memory."""
        memory_key = f"workspace:{workspace_id}:topics:{content_id}"

        try:
            await redis_cache.set(memory_key, topics, ttl=86400 * 90)  # 90 days
            logger.debug(
                "Stored topics in workspace memory",
                workspace_id=workspace_id,
                content_id=content_id
            )
        except Exception as e:
            logger.warning("Failed to store topics", error=str(e))

    async def _store_corpus_analysis(
        self,
        workspace_id: str,
        corpus_id: str,
        analysis: Dict[str, Any]
    ) -> None:
        """Store corpus analysis in workspace memory."""
        memory_key = f"workspace:{workspace_id}:corpus:{corpus_id}"

        try:
            await redis_cache.set(memory_key, analysis, ttl=86400 * 90)  # 90 days
            logger.debug(
                "Stored corpus analysis",
                workspace_id=workspace_id,
                corpus_id=corpus_id
            )
        except Exception as e:
            logger.warning("Failed to store corpus analysis", error=str(e))

    async def _get_workspace_topics(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Retrieve all topic analyses from workspace."""
        # This is a simplified version - in production, you'd query a database
        # For now, we'll return empty list as placeholder
        logger.debug("Getting workspace topics", workspace_id=workspace_id)
        return []

    def _get_timestamp(self) -> str:
        """Get current ISO timestamp."""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()


# Global instance
topic_modeler = TopicModeler()
