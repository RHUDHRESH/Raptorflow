from typing import List, TypedDict

import psycopg
from langgraph.graph import END, START, StateGraph

from db import get_db_connection
from inference import InferenceProvider


class IngestState(TypedDict, total=False):
    workspace_id: str
    content: str
    filename: str
    chunks: List[str]
    embeddings: List[List[float]]
    status: str
    metadata: dict


async def chunk_document(state: IngestState):
    # Simple semantic chunking logic
    text = state["content"]
    # In production, use RecursiveCharacterTextSplitter
    chunks = [text[i : i + 1000] for i in range(0, len(text), 800)]
    return {"chunks": chunks}


async def embed_chunks(state: IngestState):
    embedder = InferenceProvider.get_embeddings()
    # Batch embedding for efficiency
    embeddings = await embedder.aembed_documents(state["chunks"])
    return {"embeddings": embeddings}


async def store_vectors(state: IngestState):
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            base_metadata = state.get("metadata", {})
            filename = state.get("filename") or base_metadata.get("filename") or "ingest"
            for index, (chunk, emb) in enumerate(
                zip(state["chunks"], state["embeddings"])
            ):
                metadata = {
                    **base_metadata,
                    "source": filename,
                    "chunk_index": index,
                    "chunk_total": len(state["chunks"]),
                }
                await cur.execute(
                    """
                    INSERT INTO muse_assets (workspace_id, content, metadata, embedding, asset_type, status)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        state["workspace_id"],
                        chunk,
                        psycopg.types.json.Jsonb(metadata),
                        emb,
                        base_metadata.get("asset_type") or "text",
                        base_metadata.get("status") or "ready",
                    ),
                )
            await conn.commit()
    return {"status": "complete"}


workflow = StateGraph(IngestState)
workflow.add_node("chunk", chunk_document)
workflow.add_node("embed", embed_chunks)
workflow.add_node("store", store_vectors)

workflow.add_edge(START, "chunk")
workflow.add_edge("chunk", "embed")
workflow.add_edge("embed", "store")
workflow.add_edge("store", END)

rag_ingest_graph = workflow.compile()
