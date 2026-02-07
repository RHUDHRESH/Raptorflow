from typing import List, TypedDict

from langgraph.graph import END, START, StateGraph

from db import get_db_connection
from inference import InferenceProvider


class IngestState(TypedDict):
    workspace_id: str
    content: str
    filename: str
    chunks: List[str]
    embeddings: List[List[float]]
    status: str


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
            for chunk, emb in zip(state["chunks"], state["embeddings"]):
                await cur.execute(
                    "INSERT INTO muse_assets (workspace_id, content, metadata, embedding) VALUES (%s, %s, %s, %s)",
                    (state["workspace_id"], chunk, {"source": state["filename"]}, emb),
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
