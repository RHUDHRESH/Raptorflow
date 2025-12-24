import logging
from typing import Any, Dict, List, Optional, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from backend.inference import InferenceProvider
from backend.memory.manager import MemoryManager

logger = logging.getLogger("raptorflow.agents.rag_retrieval")


class QueryExpansion(BaseModel):
    expanded_queries: List[str] = Field(
        description="3-5 search queries to capture different angles of the user's intent"
    )


class RAGRetrievalNode:
    """
    SOTA RAG Retrieval Node.
    Orchestrates multi-tier context retrieval with query expansion and citation support.
    Designed for use in LangGraph orchestrators.
    """

    def __init__(self):
        self.memory = MemoryManager()
        self.expansion_llm = InferenceProvider.get_model(
            model_tier="fast"
        ).with_structured_output(QueryExpansion)

    async def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Node execution logic for LangGraph."""
        workspace_id = state.get("workspace_id")
        thread_id = state.get("thread_id")
        messages = state.get("messages", [])

        if not messages:
            return {"error": "No messages found in state for RAG retrieval."}

        last_message = messages[-1].content
        logger.info(f"RAG Retrieval triggered for query: {last_message[:50]}...")

        # 1. Multi-Query Expansion
        expansion = await self.expansion_llm.ainvoke(
            [
                SystemMessage(
                    content="Expand the user's request into 2-3 surgical search queries for a vector database to find relevant brand and project context."
                ),
                HumanMessage(content=last_message),
            ]
        )

        queries = expansion.expanded_queries
        if last_message not in queries:
            queries.append(last_message)

        # 2. Parallel Retrieval via MemoryManager
        all_contexts = []
        citations = []

        for q in queries:
            tier_context = await self.memory.retrieve_context(
                workspace_id=workspace_id, query=q, thread_id=thread_id
            )

            # Aggregate and format
            for tier in ["short_term", "episodic", "semantic"]:
                for item in tier_context[tier]:
                    content = item.get("content", str(item))
                    if content not in all_contexts:
                        all_contexts.append(content)
                        citations.append(
                            {
                                "source": tier,
                                "id": item.get("id", "n/a"),
                                "similarity": item.get("similarity", 1.0),
                            }
                        )

        return {
            "retrieved_context": all_contexts[:7],  # Top 7 unique snippets
            "citations": citations[:7],
        }


class RAG:
    """
    SOTA RAG Utility class.
    Provides heuristic and semantic scoring for context relevance.
    """

    def calculate_relevance_score(self, query: str, snippet: str) -> float:
        """
        Calculates a heuristic relevance score [0.0 - 1.0] between a query and a snippet.
        Uses simple keyword overlap for industrial speed.
        """
        query_words = set(query.lower().split())
        snippet_words = set(snippet.lower().split())

        if not query_words:
            return 0.0

        overlap = query_words.intersection(snippet_words)
        score = len(overlap) / len(query_words)

        # SOTA: Boost score if query is a substring
        if query.lower() in snippet.lower():
            score = max(score, 0.9)

        return min(score, 1.0)
