"""
Semantic router using sentence embeddings for fast routing.
"""

import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np

from ..base import BaseRouter

logger = logging.getLogger(__name__)


@dataclass
class SemanticRouteResult:
    """Result from semantic routing."""

    route: str
    confidence: float
    reasoning: str
    embedding_similarity: float


class SemanticRouter(BaseRouter):
    """Fast semantic router using sentence embeddings."""

    def __init__(self):
        super().__init__()
        self.model_name = os.getenv("MODEL_NAME")
        self.model = None
        self.route_embeddings = {}
        self._initialized = False

        # Route definitions with example phrases
        self.ROUTE_DEFINITIONS = {
            "onboarding": [
                "I need help getting started",
                "How do I begin the onboarding process",
                "What's the first step",
                "Help me set up my account",
                "I'm new here, what should I do",
            ],
            "moves": [
                "Create a marketing move",
                "I want to plan a campaign",
                "Help me with my marketing strategy",
                "Generate a move for my business",
                "What moves should I make",
            ],
            "muse": [
                "Write some content",
                "Generate marketing copy",
                "Create a blog post",
                "Write an email campaign",
                "Help with content creation",
            ],
            "blackbox": [
                "Generate a bold strategy",
                "I need creative marketing ideas",
                "Give me a black box strategy",
                "What's a risky marketing move",
                "Create an innovative approach",
            ],
            "research": [
                "Research my market",
                "Find information about competitors",
                "Analyze industry trends",
                "Search for market data",
                "Investigate customer behavior",
            ],
            "analytics": [
                "Show me my performance",
                "Analyze my results",
                "How are my campaigns doing",
                "Review my metrics",
                "Check my analytics",
            ],
            "general": [
                "Help me",
                "What can you do",
                "General question",
                "Random query",
                "Just testing",
            ],
        }

    async def _initialize(self):
        """Initialize the sentence transformer model."""
        if self._initialized:
            return

        try:
            from sentence_transformers import SentenceTransformer

            self.model = SentenceTransformer(self.model_name)
            await self._build_route_embeddings()
            self._initialized = True
            logger.info(
                f"SemanticRouter initialized with {len(self.route_embeddings)} routes"
            )
        except ImportError:
            logger.error(
                "sentence_transformers not installed. Install with: pip install sentence-transformers"
            )
            raise
        except Exception as e:
            logger.error(f"Failed to initialize SemanticRouter: {e}")
            raise

    async def _build_route_embeddings(self):
        """Pre-compute embeddings for all routes."""
        logger.info("Building route embeddings...")

        for route, examples in self.ROUTE_DEFINITIONS.items():
            # Encode all examples for this route
            embeddings = self.model.encode(examples)

            # Store the mean embedding for the route
            route_embedding = np.mean(embeddings, axis=0)
            self.route_embeddings[route] = route_embedding

            logger.debug(
                f"Built embedding for route '{route}' with {len(examples)} examples"
            )

    async def route(self, query: str, threshold: float = 0.5) -> SemanticRouteResult:
        """Route a query to the best matching route."""
        await self._initialize()

        if not query or len(query.strip()) < 3:
            return SemanticRouteResult(
                route="general",
                confidence=0.0,
                reasoning="Query too short or empty",
                embedding_similarity=0.0,
            )

        try:
            # Encode the query
            query_embedding = self.model.encode([query])[0]

            # Calculate similarity with all routes
            best_route = "general"
            best_similarity = 0.0

            for route, route_embedding in self.route_embeddings.items():
                # Calculate cosine similarity
                similarity = np.dot(query_embedding, route_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(route_embedding)
                )

                if similarity > best_similarity:
                    best_similarity = similarity
                    best_route = route

            # Check if similarity meets threshold
            if best_similarity < threshold:
                best_route = "general"
                reasoning = f"Low similarity ({best_similarity:.3f}) below threshold ({threshold})"
            else:
                reasoning = f"Matched route '{best_route}' with similarity {best_similarity:.3f}"

            return SemanticRouteResult(
                route=best_route,
                confidence=min(best_similarity, 1.0),
                reasoning=reasoning,
                embedding_similarity=best_similarity,
            )

        except Exception as e:
            logger.error(f"Error in semantic routing: {e}")
            return SemanticRouteResult(
                route="general",
                confidence=0.0,
                reasoning=f"Routing error: {str(e)}",
                embedding_similarity=0.0,
            )

    def get_route_info(self) -> Dict[str, Any]:
        """Get information about available routes."""
        return {
            "model": self.model_name,
            "total_routes": len(self.ROUTE_DEFINITIONS),
            "routes": list(self.ROUTE_DEFINITIONS.keys()),
            "examples_per_route": {
                route: len(examples)
                for route, examples in self.ROUTE_DEFINITIONS.items()
            },
            "initialized": self._initialized,
        }

    def add_route_examples(self, route: str, examples: List[str]):
        """Add new examples for a route."""
        if route not in self.ROUTE_DEFINITIONS:
            self.ROUTE_DEFINITIONS[route] = []

        self.ROUTE_DEFINITIONS[route].extend(examples)

        # Rebuild embeddings if already initialized
        if self._initialized:
            import asyncio

            asyncio.create_task(self._rebuild_embeddings())

    async def _rebuild_embeddings(self):
        """Rebuild all route embeddings."""
        if self.model:
            await self._build_route_embeddings()
            logger.info("Route embeddings rebuilt")

    def get_route_examples(self, route: str) -> List[str]:
        """Get examples for a specific route."""
        return self.ROUTE_DEFINITIONS.get(route, [])

    async def batch_route(
        self, queries: List[str], threshold: float = 0.5
    ) -> List[SemanticRouteResult]:
        """Route multiple queries efficiently."""
        await self._initialize()

        if not queries:
            return []

        try:
            # Encode all queries at once
            query_embeddings = self.model.encode(queries)

            results = []
            for i, query_embedding in enumerate(query_embeddings):
                query = queries[i]

                # Find best route
                best_route = "general"
                best_similarity = 0.0

                for route, route_embedding in self.route_embeddings.items():
                    similarity = np.dot(query_embedding, route_embedding) / (
                        np.linalg.norm(query_embedding)
                        * np.linalg.norm(route_embedding)
                    )

                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_route = route

                # Check threshold
                if best_similarity < threshold:
                    best_route = "general"
                    reasoning = f"Low similarity ({best_similarity:.3f})"
                else:
                    reasoning = f"Matched '{best_route}' with {best_similarity:.3f}"

                results.append(
                    SemanticRouteResult(
                        route=best_route,
                        confidence=min(best_similarity, 1.0),
                        reasoning=reasoning,
                        embedding_similarity=best_similarity,
                    )
                )

            return results

        except Exception as e:
            logger.error(f"Error in batch routing: {e}")
            # Return general route for all queries
            return [
                SemanticRouteResult(
                    route="general",
                    confidence=0.0,
                    reasoning=f"Batch routing error: {str(e)}",
                    embedding_similarity=0.0,
                )
                for _ in queries
            ]
