"""
Memory Manager - Vector-based memory system for agent learning and context retention.

This service provides a sophisticated memory layer for all agents in the RaptorFlow system.
It enables agents to:
- Store execution results with semantic embeddings
- Retrieve relevant past experiences via vector similarity search
- Learn from feedback and improve over time
- Build workspace-specific knowledge bases

Architecture:
- Uses Supabase with pgvector for vector storage
- Leverages Vertex AI for text embeddings
- Supports workspace isolation for multi-tenancy
- Tracks success metrics and confidence scores

Tables Required (Supabase):
    agent_memories:
        - id (uuid, primary key)
        - workspace_id (uuid, foreign key)
        - agent_name (text) - e.g., "hook_generator", "icp_builder"
        - memory_type (text) - "success", "failure", "preference", "insight"
        - context (jsonb) - Input parameters and context
        - result (jsonb) - Output and metrics
        - embedding (vector(768)) - Semantic embedding for search
        - success_score (float) - 0.0-1.0 rating
        - feedback (jsonb) - User or critic feedback
        - tags (text[]) - Categorical tags for filtering
        - created_at (timestamp)
        - updated_at (timestamp)

Environment Variables Required:
    SUPABASE_URL: Supabase project URL
    SUPABASE_SERVICE_KEY: Service role key
    GOOGLE_CLOUD_PROJECT: GCP project for Vertex AI embeddings

Example Usage:
    from backend.services.memory_manager import MemoryManager

    memory = MemoryManager(workspace_id="ws-123", agent_name="hook_generator")

    # Store a successful execution
    await memory.remember(
        context={"icp_id": "icp-456", "topic": "AI automation"},
        result={"hooks": [...], "performance_score": 0.85},
        success_score=0.85,
        memory_type="success"
    )

    # Recall relevant past successes
    similar = await memory.search(
        query="AI automation hooks for SaaS companies",
        memory_types=["success"],
        top_k=5
    )
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import structlog
from vertexai.language_models import TextEmbeddingModel

from backend.config.settings import get_settings
from backend.services.supabase_client import supabase_client
from backend.utils.correlation import get_correlation_id

logger = structlog.get_logger(__name__)
settings = get_settings()


class MemoryManager:
    """
    Vector-based memory manager for agent learning and context retention.

    This class provides a comprehensive memory layer that allows agents to:
    1. Store execution results with semantic embeddings
    2. Search for similar past experiences using vector similarity
    3. Learn from user and critic feedback
    4. Build workspace-specific knowledge bases

    Attributes:
        workspace_id: UUID of the workspace (for multi-tenancy)
        agent_name: Name of the agent using this memory (e.g., "hook_generator")
        embedding_model: Vertex AI text embedding model
        embedding_dimension: Dimension of embeddings (default: 768)

    Memory Types:
        - "success": Successful executions with high scores
        - "failure": Failed executions to avoid repeating mistakes
        - "preference": User preferences and patterns
        - "insight": Learned insights from feedback
    """

    # Class-level embedding model cache (singleton pattern)
    _embedding_model: Optional[TextEmbeddingModel] = None
    _embedding_dimension = 768  # textembedding-gecko dimension

    def __init__(self, workspace_id: str, agent_name: str):
        """
        Initialize memory manager for a specific workspace and agent.

        Args:
            workspace_id: UUID of the workspace
            agent_name: Name of the agent (e.g., "hook_generator", "icp_builder")
        """
        self.workspace_id = workspace_id
        self.agent_name = agent_name
        self._initialize_embedding_model()

    @classmethod
    def _initialize_embedding_model(cls) -> None:
        """
        Initialize the embedding model (lazy singleton).

        Uses textembedding-gecko from Vertex AI for semantic embeddings.
        Only initializes once per process for efficiency.
        """
        if cls._embedding_model is None and settings.GOOGLE_CLOUD_PROJECT:
            try:
                cls._embedding_model = TextEmbeddingModel.from_pretrained(
                    "textembedding-gecko@003"
                )
                logger.info(
                    "Embedding model initialized",
                    model="textembedding-gecko@003",
                    dimension=cls._embedding_dimension,
                )
            except Exception as exc:
                logger.error(
                    "Failed to initialize embedding model",
                    error=str(exc),
                    correlation_id=get_correlation_id(),
                )
                # Don't raise - allow memory manager to work without embeddings
                # (will use exact match instead of semantic search)

    async def remember(
        self,
        context: Dict[str, Any],
        result: Dict[str, Any],
        success_score: float = 0.5,
        memory_type: str = "success",
        feedback: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
    ) -> str:
        """
        Store a memory with semantic embedding.

        Stores an agent execution result in the memory system with a vector
        embedding for later semantic retrieval. This allows agents to learn
        from past experiences and retrieve similar contexts.

        Args:
            context: Input parameters and context (will be embedded)
                Example: {"icp_id": "...", "topic": "AI automation", "industry": "SaaS"}
            result: Output data and metrics
                Example: {"hooks": [...], "performance_score": 0.85, "click_rate": 0.12}
            success_score: Rating from 0.0 (failure) to 1.0 (perfect success)
            memory_type: Type of memory ("success", "failure", "preference", "insight")
            feedback: Optional user or critic feedback
                Example: {"user_rating": 5, "comments": "Great hooks!", "critic_review": {...}}
            tags: Optional categorical tags for filtering
                Example: ["b2b", "saas", "high-performing"]

        Returns:
            UUID of the stored memory

        Raises:
            Exception: If database insertion fails

        Example:
            memory_id = await memory.remember(
                context={"icp_id": "icp-123", "topic": "AI automation"},
                result={"hooks": [...], "score": 0.9},
                success_score=0.9,
                memory_type="success",
                tags=["b2b", "high-performing"]
            )
        """
        correlation_id = get_correlation_id()

        try:
            # Create searchable text from context and result
            searchable_text = self._create_searchable_text(context, result)

            # Generate embedding
            embedding = await self._generate_embedding(searchable_text)

            # Prepare memory record
            memory_data = {
                "id": str(uuid.uuid4()),
                "workspace_id": self.workspace_id,
                "agent_name": self.agent_name,
                "memory_type": memory_type,
                "context": json.dumps(context),
                "result": json.dumps(result),
                "embedding": embedding,
                "success_score": success_score,
                "feedback": json.dumps(feedback) if feedback else None,
                "tags": tags or [],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }

            # Store in database
            stored = await supabase_client.insert("agent_memories", memory_data)
            memory_id = stored.get("id")

            logger.info(
                "Memory stored successfully",
                agent=self.agent_name,
                workspace_id=self.workspace_id,
                memory_id=memory_id,
                memory_type=memory_type,
                success_score=success_score,
                tags=tags,
                correlation_id=correlation_id,
            )

            return memory_id

        except Exception as exc:
            logger.error(
                "Failed to store memory",
                agent=self.agent_name,
                workspace_id=self.workspace_id,
                error=str(exc),
                correlation_id=correlation_id,
            )
            raise

    async def search(
        self,
        query: str,
        memory_types: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        min_success_score: float = 0.0,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant memories using semantic similarity.

        Performs vector similarity search to find memories most relevant to
        the query. Results are ranked by cosine similarity and filtered by
        memory type, tags, and success score.

        Args:
            query: Natural language search query
                Example: "successful hooks for AI automation in SaaS"
            memory_types: Filter by memory types (default: ["success"])
                Example: ["success", "preference"]
            tags: Filter by tags (AND logic - must have all tags)
                Example: ["b2b", "high-performing"]
            min_success_score: Minimum success score threshold (0.0-1.0)
            top_k: Maximum number of results to return

        Returns:
            List of memory records with similarity scores, ordered by relevance:
            [
                {
                    "id": "mem-123",
                    "context": {...},
                    "result": {...},
                    "success_score": 0.9,
                    "similarity": 0.87,
                    "tags": [...],
                    "created_at": "..."
                },
                ...
            ]

        Example:
            memories = await memory.search(
                query="high-performing hooks for B2B SaaS companies",
                memory_types=["success"],
                min_success_score=0.7,
                top_k=5
            )

            for mem in memories:
                print(f"Found similar context: {mem['context']}")
                print(f"Similarity: {mem['similarity']:.2f}")
        """
        correlation_id = get_correlation_id()
        memory_types = memory_types or ["success"]

        try:
            # Generate query embedding
            query_embedding = await self._generate_embedding(query)

            if query_embedding is None:
                # Fallback to non-semantic search if embeddings unavailable
                logger.warning(
                    "Embeddings unavailable, falling back to tag/type filtering",
                    correlation_id=correlation_id,
                )
                return await self._fallback_search(
                    memory_types=memory_types,
                    tags=tags,
                    min_success_score=min_success_score,
                    top_k=top_k,
                )

            # Use Supabase RPC for vector similarity search
            # Note: This requires a custom RPC function in Supabase
            # CREATE OR REPLACE FUNCTION search_agent_memories(...)
            # See migration SQL in DEPLOYMENT.md

            rpc_params = {
                "query_embedding": query_embedding,
                "filter_workspace_id": self.workspace_id,
                "filter_agent_name": self.agent_name,
                "filter_memory_types": memory_types,
                "filter_tags": tags,
                "min_score": min_success_score,
                "match_count": top_k,
            }

            result = supabase_client.client.rpc(
                "search_agent_memories",
                rpc_params
            ).execute()

            memories = result.data or []

            # Parse JSON fields
            for mem in memories:
                mem["context"] = json.loads(mem["context"]) if isinstance(mem["context"], str) else mem["context"]
                mem["result"] = json.loads(mem["result"]) if isinstance(mem["result"], str) else mem["result"]
                if mem.get("feedback"):
                    mem["feedback"] = json.loads(mem["feedback"]) if isinstance(mem["feedback"], str) else mem["feedback"]

            logger.info(
                "Memory search completed",
                agent=self.agent_name,
                workspace_id=self.workspace_id,
                query_length=len(query),
                results_found=len(memories),
                memory_types=memory_types,
                correlation_id=correlation_id,
            )

            return memories

        except Exception as exc:
            logger.error(
                "Memory search failed",
                agent=self.agent_name,
                workspace_id=self.workspace_id,
                error=str(exc),
                correlation_id=correlation_id,
            )
            # Fallback to simple filtering on error
            return await self._fallback_search(
                memory_types=memory_types,
                tags=tags,
                min_success_score=min_success_score,
                top_k=top_k,
            )

    async def update_feedback(
        self,
        memory_id: str,
        feedback: Dict[str, Any],
        new_success_score: Optional[float] = None,
    ) -> bool:
        """
        Update an existing memory with new feedback and optionally adjust success score.

        Allows agents to incorporate user feedback, critic reviews, and performance
        metrics after the initial memory was stored.

        Args:
            memory_id: UUID of the memory to update
            feedback: New feedback data to merge with existing feedback
                Example: {"user_rating": 4, "critic_suggestions": [...]}
            new_success_score: Optional updated success score based on real-world performance

        Returns:
            True if update succeeded, False otherwise

        Example:
            await memory.update_feedback(
                memory_id="mem-123",
                feedback={"user_rating": 5, "actual_clicks": 1200},
                new_success_score=0.95
            )
        """
        correlation_id = get_correlation_id()

        try:
            # Fetch existing memory
            existing = await supabase_client.fetch_one(
                "agent_memories",
                {"id": memory_id, "workspace_id": self.workspace_id}
            )

            if not existing:
                logger.warning(
                    "Memory not found for feedback update",
                    memory_id=memory_id,
                    workspace_id=self.workspace_id,
                    correlation_id=correlation_id,
                )
                return False

            # Merge feedback
            existing_feedback = json.loads(existing.get("feedback") or "{}")
            merged_feedback = {**existing_feedback, **feedback}

            # Prepare updates
            updates = {
                "feedback": json.dumps(merged_feedback),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }

            if new_success_score is not None:
                updates["success_score"] = new_success_score

            # Update in database
            await supabase_client.update(
                "agent_memories",
                {"id": memory_id},
                updates
            )

            logger.info(
                "Memory feedback updated",
                agent=self.agent_name,
                memory_id=memory_id,
                new_score=new_success_score,
                correlation_id=correlation_id,
            )

            return True

        except Exception as exc:
            logger.error(
                "Failed to update memory feedback",
                memory_id=memory_id,
                error=str(exc),
                correlation_id=correlation_id,
            )
            return False

    async def get_statistics(self) -> Dict[str, Any]:
        """
        Get memory statistics for this agent in this workspace.

        Returns summary metrics about stored memories, including counts,
        average success scores, and top tags.

        Returns:
            Dictionary with statistics:
            {
                "total_memories": 150,
                "success_count": 120,
                "failure_count": 20,
                "avg_success_score": 0.78,
                "top_tags": ["b2b", "saas", "high-performing"],
                "earliest_memory": "2024-01-15T10:30:00Z",
                "latest_memory": "2024-01-20T14:45:00Z"
            }
        """
        correlation_id = get_correlation_id()

        try:
            memories = await supabase_client.fetch_all(
                "agent_memories",
                {
                    "workspace_id": self.workspace_id,
                    "agent_name": self.agent_name
                }
            )

            if not memories:
                return {
                    "total_memories": 0,
                    "success_count": 0,
                    "failure_count": 0,
                    "avg_success_score": 0.0,
                    "top_tags": [],
                }

            # Calculate statistics
            total = len(memories)
            success_count = sum(1 for m in memories if m.get("memory_type") == "success")
            failure_count = sum(1 for m in memories if m.get("memory_type") == "failure")
            avg_score = sum(m.get("success_score", 0) for m in memories) / total

            # Aggregate tags
            all_tags = []
            for m in memories:
                all_tags.extend(m.get("tags", []))

            from collections import Counter
            tag_counts = Counter(all_tags)
            top_tags = [tag for tag, _ in tag_counts.most_common(10)]

            # Time range
            timestamps = [m.get("created_at") for m in memories if m.get("created_at")]
            earliest = min(timestamps) if timestamps else None
            latest = max(timestamps) if timestamps else None

            stats = {
                "total_memories": total,
                "success_count": success_count,
                "failure_count": failure_count,
                "avg_success_score": round(avg_score, 2),
                "top_tags": top_tags,
                "earliest_memory": earliest,
                "latest_memory": latest,
            }

            logger.info(
                "Memory statistics retrieved",
                agent=self.agent_name,
                workspace_id=self.workspace_id,
                stats=stats,
                correlation_id=correlation_id,
            )

            return stats

        except Exception as exc:
            logger.error(
                "Failed to get memory statistics",
                agent=self.agent_name,
                error=str(exc),
                correlation_id=correlation_id,
            )
            return {}

    # === PRIVATE HELPERS === #

    def _create_searchable_text(
        self,
        context: Dict[str, Any],
        result: Dict[str, Any]
    ) -> str:
        """
        Create searchable text from context and result for embedding.

        Combines relevant fields from context and result into a natural
        language representation for semantic embedding.

        Args:
            context: Input context dictionary
            result: Output result dictionary

        Returns:
            Searchable text string
        """
        parts = []

        # Add context fields
        for key, value in context.items():
            if isinstance(value, (str, int, float, bool)):
                parts.append(f"{key}: {value}")
            elif isinstance(value, dict):
                parts.append(f"{key}: {json.dumps(value)}")

        # Add result fields (limit size for large results)
        result_str = json.dumps(result)
        if len(result_str) > 1000:
            result_str = result_str[:1000] + "..."
        parts.append(f"result: {result_str}")

        return " | ".join(parts)

    async def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate vector embedding for text using Vertex AI.

        Args:
            text: Text to embed

        Returns:
            Embedding vector (768 dimensions) or None if unavailable
        """
        if not self._embedding_model:
            return None

        try:
            embeddings = self._embedding_model.get_embeddings([text])
            if embeddings and len(embeddings) > 0:
                return embeddings[0].values
            return None
        except Exception as exc:
            logger.warning(
                "Failed to generate embedding",
                error=str(exc),
                text_length=len(text),
                correlation_id=get_correlation_id(),
            )
            return None

    async def _fallback_search(
        self,
        memory_types: List[str],
        tags: Optional[List[str]],
        min_success_score: float,
        top_k: int,
    ) -> List[Dict[str, Any]]:
        """
        Fallback search when vector search is unavailable.

        Uses simple filtering by memory type, tags, and success score.
        Orders by success score descending.

        Args:
            memory_types: Memory types to filter
            tags: Tags to filter (AND logic)
            min_success_score: Minimum success score
            top_k: Max results

        Returns:
            List of matching memories
        """
        correlation_id = get_correlation_id()

        try:
            # Build query
            # Note: This is simplified - actual implementation would use Supabase filtering
            memories = await supabase_client.fetch_all(
                "agent_memories",
                {
                    "workspace_id": self.workspace_id,
                    "agent_name": self.agent_name,
                }
            )

            # Filter
            filtered = []
            for mem in memories:
                # Type filter
                if mem.get("memory_type") not in memory_types:
                    continue

                # Score filter
                if mem.get("success_score", 0) < min_success_score:
                    continue

                # Tag filter (AND logic)
                if tags:
                    mem_tags = mem.get("tags", [])
                    if not all(tag in mem_tags for tag in tags):
                        continue

                # Parse JSON fields
                mem["context"] = json.loads(mem["context"]) if isinstance(mem["context"], str) else mem["context"]
                mem["result"] = json.loads(mem["result"]) if isinstance(mem["result"], str) else mem["result"]
                if mem.get("feedback"):
                    mem["feedback"] = json.loads(mem["feedback"]) if isinstance(mem["feedback"], str) else mem["feedback"]

                filtered.append(mem)

            # Sort by success score
            filtered.sort(key=lambda m: m.get("success_score", 0), reverse=True)

            # Limit
            result = filtered[:top_k]

            logger.info(
                "Fallback search completed",
                agent=self.agent_name,
                results_found=len(result),
                correlation_id=correlation_id,
            )

            return result

        except Exception as exc:
            logger.error(
                "Fallback search failed",
                error=str(exc),
                correlation_id=correlation_id,
            )
            return []
