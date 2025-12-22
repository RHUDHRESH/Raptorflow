from typing import List, Dict
from db import vector_search
from inference import InferenceProvider
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field

class QueryExpansion(BaseModel):
    expanded_queries: List[str] = Field(description="3-5 search queries to capture different angles of the user's intent")

class RAGRetrievalAgent:
    def __init__(self):
        self.embeddings = InferenceProvider.get_embeddings()
        # Use fast model for query expansion
        self.expansion_llm = InferenceProvider.get_model(model_tier="fast").with_structured_output(QueryExpansion)

    async def retrieve(self, query: str, workspace_id: str) -> Dict:
        # 1. SOTA Technique: Multi-Query Expansion
        # Don't just search for "Linkedin post", search for "brand voice", "target audience", "offer details"
        expansion = await self.expansion_llm.ainvoke([
            SystemMessage(content="Expand the user's request into 3 surgical search queries for a vector database to find relevant brand and project context."),
            HumanMessage(content=query)
        ])
        
        all_results = []
        for q in expansion.expanded_queries:
            vector = await self.embeddings.aembed_query(q)
            results = await vector_search(workspace_id, vector, limit=3)
            all_results.extend(results)
            
        # 2. Basic Reranking (Remove duplicates, sort by similarity)
        seen_ids = set()
        unique_results = []
        for res in sorted(all_results, key=lambda x: x[3], reverse=True):
            if res[0] not in seen_ids:
                unique_results.append(res)
                seen_ids.add(res[0])
                
        return {
            "snippets": [r[1] for r in unique_results[:5]],
            "citations": [{"id": r[0], "score": r[3]} for r in unique_results[:5]]
        }