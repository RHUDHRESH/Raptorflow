# backend/rag_integration.py
# RaptorFlow Codex - RAG Agent Integration
# Week 3 Wednesday - Agent Context Injection

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# ============================================================================
# RAG CONTEXT INJECTION
# ============================================================================

class AgentRAGMixin:
    """Mixin for agent RAG integration"""

    async def get_knowledge_context(
        self,
        task: str,
        workspace_id: str,
        category: Optional[str] = None,
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        Get knowledge context for agent execution.

        Args:
            task: Task description
            workspace_id: Workspace context
            category: Optional knowledge category
            limit: Max knowledge items

        Returns:
            Context dictionary with relevant knowledge
        """
        from chroma_db import get_chroma_rag

        try:
            chroma = await get_chroma_rag()

            context = await chroma.get_context_for_agent(
                agent_name=self.name,
                workspace_id=workspace_id,
                task=task,
                context_limit=limit
            )

            # Add context to agent's context
            if hasattr(self, 'context'):
                self.context["retrieved_knowledge"] = context["retrieved_knowledge"]

            logger.info(
                f"📚 Knowledge context loaded for {self.name}: "
                f"{len(context['retrieved_knowledge'])} items"
            )

            return context

        except Exception as e:
            logger.error(f"❌ Get knowledge context failed: {e}")
            return {"error": str(e), "retrieved_knowledge": []}

    async def search_knowledge_base(
        self,
        query: str,
        workspace_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search knowledge base for specific information.

        Args:
            query: Search query
            workspace_id: Workspace context
            limit: Max results

        Returns:
            Search results
        """
        from chroma_db import get_chroma_rag

        try:
            chroma = await get_chroma_rag()
            results = await chroma.search(
                query=query,
                workspace_id=workspace_id,
                limit=limit
            )

            logger.info(
                f"🔍 Knowledge search by {self.name}: '{query}' → {len(results)} results"
            )

            return results

        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            return []

    async def get_knowledge_summary(
        self,
        category: str,
        workspace_id: str
    ) -> str:
        """
        Get summary of knowledge in a category.

        Args:
            category: Knowledge category
            workspace_id: Workspace context

        Returns:
            Summary text
        """
        from chroma_db import get_chroma_rag

        try:
            chroma = await get_chroma_rag()

            # Search for category
            results = await chroma.search(
                query=category,
                workspace_id=workspace_id,
                limit=10
            )

            # Build summary
            summary_parts = []
            for result in results:
                if result["metadata"].get("category") == category:
                    summary_parts.append(result["text"][:200])

            summary = " ".join(summary_parts)[:1000]

            logger.info(
                f"📖 Knowledge summary retrieved for {self.name}: "
                f"{len(summary)} chars from {len(summary_parts)} items"
            )

            return summary

        except Exception as e:
            logger.error(f"❌ Get summary failed: {e}")
            return ""

# ============================================================================
# RAG CONTEXT BUILDER
# ============================================================================

class RAGContextBuilder:
    """Build RAG context for agent execution"""

    @staticmethod
    async def build_execution_context(
        agent_name: str,
        task: str,
        workspace_id: str,
        agent_type: str,
        campaign_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Build complete execution context with RAG knowledge.

        Args:
            agent_name: Agent executing task
            task: Task description
            workspace_id: Workspace context
            agent_type: Type of agent
            campaign_context: Optional campaign context

        Returns:
            Complete execution context
        """
        from chroma_db import get_chroma_rag

        try:
            chroma = await get_chroma_rag()

            # Get base knowledge context
            knowledge_context = await chroma.get_context_for_agent(
                agent_name=agent_name,
                workspace_id=workspace_id,
                task=task,
                context_limit=5
            )

            # Get agent-type specific guidance
            agent_guidance = await RAGContextBuilder._get_agent_guidance(
                agent_type=agent_type,
                workspace_id=workspace_id,
                chroma=chroma
            )

            # Build execution context
            execution_context = {
                "agent": {
                    "name": agent_name,
                    "type": agent_type,
                    "timestamp": datetime.utcnow().isoformat()
                },
                "task": {
                    "description": task,
                    "workspace_id": workspace_id
                },
                "knowledge": {
                    "retrieved_documents": knowledge_context["retrieved_knowledge"],
                    "total_items": knowledge_context["total_knowledge_items"],
                    "average_relevance": knowledge_context["average_relevance"]
                },
                "guidance": agent_guidance,
                "campaign": campaign_context or {}
            }

            logger.info(
                f"🎯 Execution context built for {agent_name}: "
                f"{len(execution_context['knowledge']['retrieved_documents'])} knowledge items"
            )

            return execution_context

        except Exception as e:
            logger.error(f"❌ Build context failed: {e}")
            return {
                "error": str(e),
                "agent": {"name": agent_name, "type": agent_type},
                "knowledge": {"retrieved_documents": []}
            }

    @staticmethod
    async def _get_agent_guidance(
        agent_type: str,
        workspace_id: str,
        chroma
    ) -> Dict[str, Any]:
        """Get type-specific guidance for agent"""
        guidance_map = {
            "researcher": "Research methodology and analysis frameworks",
            "creative": "Content creation guidelines and brand standards",
            "intelligence": "Competitive analysis and market insights",
            "guardian": "Compliance requirements and policy guidelines",
            "lord": "Strategic planning and decision frameworks"
        }

        query = guidance_map.get(agent_type, "General guidelines")

        try:
            guidance_docs = await chroma.search(
                query=query,
                workspace_id=workspace_id,
                limit=3
            )

            return {
                "type": agent_type,
                "guidance_documents": guidance_docs,
                "query_used": query
            }

        except Exception as e:
            logger.error(f"❌ Get guidance failed: {e}")
            return {"type": agent_type, "guidance_documents": [], "error": str(e)}

# ============================================================================
# RAG MEMORY SYSTEM
# ============================================================================

class RAGMemory:
    """
    RAG-based agent memory system.

    Allows agents to:
    - Remember previous interactions
    - Learn from past executions
    - Build on previous knowledge
    """

    def __init__(self, workspace_id: str):
        """Initialize RAG memory"""
        self.workspace_id = workspace_id
        self.execution_memory: List[Dict[str, Any]] = []

    async def record_execution(
        self,
        agent_name: str,
        task: str,
        result: Dict[str, Any],
        knowledge_used: Optional[List[str]] = None
    ) -> None:
        """
        Record agent execution for future reference.

        Args:
            agent_name: Agent name
            task: Task executed
            result: Execution result
            knowledge_used: Knowledge items used
        """
        execution_record = {
            "agent": agent_name,
            "task": task,
            "result_summary": result.get("summary", ""),
            "success": result.get("success", False),
            "duration_seconds": result.get("duration_seconds", 0),
            "tokens_used": result.get("tokens_used", 0),
            "knowledge_used": knowledge_used or [],
            "timestamp": datetime.utcnow().isoformat()
        }

        self.execution_memory.append(execution_record)

        logger.info(
            f"💾 Execution recorded for {agent_name}: "
            f"{task[:50]}... (success={execution_record['success']})"
        )

    async def get_similar_executions(
        self,
        task: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get similar past executions.

        Args:
            task: Current task
            limit: Max results

        Returns:
            Similar executions
        """
        # Simple string matching (could use embedding similarity)
        similar = []
        task_words = set(task.lower().split())

        for execution in self.execution_memory:
            exec_words = set(execution["task"].lower().split())
            overlap = len(task_words & exec_words)

            if overlap > 0:
                similar.append({
                    **execution,
                    "relevance": overlap / len(task_words | exec_words)
                })

        # Sort by relevance
        similar.sort(key=lambda x: x["relevance"], reverse=True)
        return similar[:limit]

    async def get_agent_history(
        self,
        agent_name: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get execution history for agent"""
        history = [
            execution for execution in self.execution_memory
            if execution["agent"] == agent_name
        ]
        return history[-limit:]

    async def get_success_rate(self, agent_name: str) -> float:
        """Get agent success rate"""
        agent_executions = [
            e for e in self.execution_memory
            if e["agent"] == agent_name
        ]

        if not agent_executions:
            return 0.0

        successes = sum(1 for e in agent_executions if e["success"])
        return (successes / len(agent_executions)) * 100

# ============================================================================
# RAG PERFORMANCE TRACKING
# ============================================================================

class RAGPerformanceTracker:
    """Track RAG system performance and quality"""

    def __init__(self):
        """Initialize tracker"""
        self.queries: List[Dict[str, Any]] = []
        self.retrievals: List[Dict[str, Any]] = []

    def track_query(
        self,
        query: str,
        workspace_id: str,
        agent: str,
        num_results: int,
        avg_relevance: float
    ) -> None:
        """Track RAG query"""
        self.queries.append({
            "query": query,
            "workspace_id": workspace_id,
            "agent": agent,
            "num_results": num_results,
            "avg_relevance": avg_relevance,
            "timestamp": datetime.utcnow().isoformat()
        })

    def track_retrieval(
        self,
        document_id: str,
        relevance_score: float,
        used_by_agent: str
    ) -> None:
        """Track document retrieval"""
        self.retrievals.append({
            "document_id": document_id,
            "relevance": relevance_score,
            "agent": used_by_agent,
            "timestamp": datetime.utcnow().isoformat()
        })

    def get_statistics(self) -> Dict[str, Any]:
        """Get RAG performance statistics"""
        if not self.queries:
            return {
                "total_queries": 0,
                "total_retrievals": 0,
                "avg_results_per_query": 0,
                "avg_relevance": 0
            }

        avg_results = sum(q["num_results"] for q in self.queries) / len(self.queries)
        avg_relevance = sum(q["avg_relevance"] for q in self.queries) / len(self.queries)

        # Most used documents
        doc_usage = {}
        for retrieval in self.retrievals:
            doc_id = retrieval["document_id"]
            doc_usage[doc_id] = doc_usage.get(doc_id, 0) + 1

        most_used = sorted(doc_usage.items(), key=lambda x: x[1], reverse=True)[:5]

        # Most active agents
        agent_usage = {}
        for query in self.queries:
            agent = query["agent"]
            agent_usage[agent] = agent_usage.get(agent, 0) + 1

        return {
            "total_queries": len(self.queries),
            "total_retrievals": len(self.retrievals),
            "avg_results_per_query": avg_results,
            "avg_relevance": avg_relevance,
            "most_used_documents": most_used,
            "most_active_agents": sorted(
                agent_usage.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }

