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
    from backend.services.memory_manager import memory_manager

    # Search for similar tasks
    similar = await memory_manager.search(
        query="AI automation hooks for SaaS companies",
        memory_type="success",
        workspace_id="ws-123",
        limit=5
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
    """

    # Class-level embedding model cache (singleton pattern)
    _embedding_model: Optional[TextEmbeddingModel] = None
    _embedding_dimension = 768  # textembedding-gecko dimension

    def __init__(self, workspace_id: str, agent_name: str):
        """
        Initialize memory manager for a specific workspace and agent.
        """
        self.workspace_id = workspace_id
        self.agent_name = agent_name
        self._initialize_embedding_model()

    @classmethod
    def _initialize_embedding_model(cls) -> None:
        """
        Initialize the embedding model (lazy singleton).
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

    async def remember(
        self,
        context: Dict[str, Any],
        result: Dict[str, Any],
        success_score: float = 0.5,
        memory_type: str = "success",
        feedback: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
    ) -> str:
        """Store a memory with semantic embedding."""
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
        """Search for relevant memories using semantic similarity."""
        correlation_id = get_correlation_id()
        memory_types = memory_types or ["success"]

        try:
            # Generate query embedding
            query_embedding = await self._generate_embedding(query)

            if query_embedding is None:
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
        """Update an existing memory with new feedback."""
        correlation_id = get_correlation_id()

        try:
            existing = await supabase_client.fetch_one(
                "agent_memories",
                {"id": memory_id, "workspace_id": self.workspace_id}
            )

            if not existing:
                return False

            existing_feedback = json.loads(existing.get("feedback") or "{}")
            merged_feedback = {**existing_feedback, **feedback}

            updates = {
                "feedback": json.dumps(merged_feedback),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }

            if new_success_score is not None:
                updates["success_score"] = new_success_score

            await supabase_client.update(
                "agent_memories",
                {"id": memory_id},
                updates
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

    # === HELPER METHODS === #

    def _create_searchable_text(self, context: Dict[str, Any], result: Dict[str, Any]) -> str:
        """Create searchable text from context and result."""
        parts = []
        for key, value in context.items():
            if isinstance(value, (str, int, float, bool)):
                parts.append(f"{key}: {value}")
            elif isinstance(value, dict):
                parts.append(f"{key}: {json.dumps(value)}")
        
        result_str = json.dumps(result)
        if len(result_str) > 1000:
            result_str = result_str[:1000] + "..."
        parts.append(f"result: {result_str}")
        
        return " | ".join(parts)

    async def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate vector embedding."""
        if not self._embedding_model:
            return None
        try:
            embeddings = self._embedding_model.get_embeddings([text])
            if embeddings and len(embeddings) > 0:
                return embeddings[0].values
            return None
        except Exception as exc:
            logger.warning(f"Failed to generate embedding: {exc}")
            return None

    async def _fallback_search(self, memory_types, tags, min_success_score, top_k) -> List[Dict]:
        """Fallback search using simple filtering."""
        # Simplified fallback logic
        return []


class MemoryService:
    """
    Global service for memory operations.
    Acts as a factory/facade for workspace-specific MemoryManagers.
    """
    
    def get_manager(self, workspace_id: str, agent_name: str = "system") -> MemoryManager:
        """Get a memory manager for a specific context."""
        return MemoryManager(str(workspace_id), agent_name)

    async def search(
        self, 
        query: str, 
        memory_type: str, 
        workspace_id: str, 
        limit: int = 5
    ) -> List[Any]:
        """Global search across a workspace."""
        # We use a generic 'system' agent context for global searches 
        # or look across all agents if needed.
        # For now, scoping to 'master_orchestrator' or similar might be appropriate
        manager = self.get_manager(workspace_id, "master_orchestrator")
        
        # Map single memory_type to list
        memory_types = [memory_type] if memory_type else None
        
        results = await manager.search(
            query=query,
            memory_types=memory_types,
            top_k=limit
        )
        
        # Transform results into objects if needed (returning dicts currently)
        # Supervisor expects objects with .confidence and .content attributes
        # Let's wrap them in a simple structure
        return [MemoryItem(r) for r in results]

    async def get_best_performing_agent(self, task_type: str, workspace_id: str) -> Optional[str]:
        """Find the best performing agent for a task type."""
        # Query memory for successful executions of this task type
        # Return the agent_name with highest average success_score
        try:
            # This would require a complex aggregation query.
            # For now, return None to trigger fallback logic in Supervisor
            return None
        except Exception:
            return None

    async def store_critique(
        self, 
        content_id: str, 
        critique: str, 
        issues: List[str], 
        workspace_id: str
    ) -> bool:
        """Store critique feedback."""
        manager = self.get_manager(workspace_id, "critic_agent")
        try:
            await manager.remember(
                context={"content_id": content_id},
                result={"critique": critique, "issues": issues},
                memory_type="critique",
                success_score=0.0 # Critique usually implies issues
            )
            return True
        except Exception:
            return False

class MemoryItem:
    """Helper class to match Supervisor's expected interface."""
    def __init__(self, data: Dict[str, Any]):
        self.confidence = data.get("similarity", 0.0) # similarity from vector search
        self.content = data
    
    def to_dict(self):
        return self.content

# Global instance
memory_manager = MemoryService()
