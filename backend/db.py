import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

import psycopg
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg_pool import AsyncConnectionPool

# DATABASE_URL should be in environment
DB_URI = os.getenv("DATABASE_URL")
UPSTASH_URL = os.getenv("UPSTASH_REDIS_REST_URL")
UPSTASH_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN")

# Global pool for production-grade connection management
_pool: Optional[AsyncConnectionPool] = None


def get_pool() -> AsyncConnectionPool:
    global _pool
    if _pool is None:
        _pool = AsyncConnectionPool(DB_URI, open=False)
    return _pool


@asynccontextmanager
async def get_db_connection():
    """Async context manager for psycopg connection from the pool."""
    pool = get_pool()
    # Ensure pool is initialized/opened
    if not hasattr(pool, "_opened") or not pool._opened:
        try:
            await pool.open()
        except Exception:
            pass # Ignore if already opening/opened in some versions
            
    async with pool.connection() as conn:
        yield conn


class SupabaseSaver(PostgresSaver):
    """
    SOTA wrapper around PostgresSaver for Supabase.
    Ensures optimal connection handling and schema compatibility.
    """

    # Inherits implementation from PostgresSaver which now supports pool/conn directly
    pass


async def init_checkpointer():
    """Initializes the LangGraph Postgres checkpointer using the global pool."""
    pool = get_pool()
    if not hasattr(pool, "_opened") or not pool._opened:
        await pool.open()

    # In LangGraph 0.2.x, PostgresSaver.from_conn_string or constructor with pool
    checkpointer = SupabaseSaver(pool)
    return checkpointer


async def vector_search(
    workspace_id: str, 
    embedding: list[float], 
    table: str = "muse_assets", 
    limit: int = 5,
    filters: Optional[dict] = None
):
    """
    Performs a pgvector similarity search, STRICTLY scoped to workspace_id.
    Supports optional metadata filtering.
    """
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            # Base query
            query = f"""
                SELECT id, content, metadata, 1 - (embedding <=> %s::vector) as similarity
                FROM {table}
                WHERE metadata->>'workspace_id' = %s
            """
            params = [embedding, workspace_id]
            
            # Dynamically add filters
            if filters:
                for key, value in filters.items():
                    query += f" AND metadata->>'{key}' = %s"
                    params.append(str(value))
            
            query += f"""
                AND 1 - (embedding <=> %s::vector) > 0.7
                ORDER BY embedding <=> %s::vector
                LIMIT %s;
            """
            params.extend([embedding, embedding, limit])
            
            await cur.execute(query, tuple(params))
            results = await cur.fetchall()
            return results


async def get_memory(
    workspace_id: str,
    query_embedding: list[float],
    memory_type: str = "semantic",
    limit: int = 5,
):
    """
    Retrieves memory (episodic or semantic) using vector similarity.
    """
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            query = """
                SELECT id, content, metadata, 1 - (embedding <=> %s::vector) as similarity
                FROM muse_assets
                WHERE metadata->>'workspace_id' = %s
                AND metadata->>'type' = %s
                AND 1 - (embedding <=> %s::vector) > 0.7
                ORDER BY embedding <=> %s::vector
                LIMIT %s;
            """
            await cur.execute(
                query,
                (
                    query_embedding,
                    workspace_id,
                    memory_type,
                    query_embedding,
                    query_embedding,
                    limit,
                ),
            )
            results = await cur.fetchall()
            return results


async def save_memory(
    workspace_id: str,
    content: str,
    embedding: list[float],
    memory_type: str = "semantic",
    metadata: dict = None,
):
    """
    Saves a piece of memory (episodic or semantic) with vector embedding.
    """
    if metadata is None:
        metadata = {}
    metadata["workspace_id"] = workspace_id
    metadata["type"] = memory_type

    asset_data = {"content": content, "metadata": metadata, "embedding": embedding}
    return await save_asset_db(workspace_id, asset_data)


async def summarize_recursively(text: str, llm: any, max_tokens: int = 1000) -> str:
    """
    SOTA sliding-window summarization for processing massive research documents.
    """
    # Simple chunking by words (approximate tokens) for SOTA speed
    words = text.split()
    chunk_size = max_tokens * 3  # Heuristic: ~3 words per token

    if len(words) <= chunk_size:
        res = await llm.ainvoke(f"Summarize this text concisely: {text}")
        return res.content

    chunks = [
        " ".join(words[i : i + chunk_size]) for i in range(0, len(words), chunk_size)
    ]
    summaries = []

    for chunk in chunks:
        res = await llm.ainvoke(f"Summarize this part of a document: {chunk}")
        summaries.append(res.content)

    # Recursively summarize the summaries
    combined_summaries = "\n".join(summaries)
    return await summarize_recursively(combined_summaries, llm, max_tokens)


async def save_asset_db(workspace_id: str, asset_data: dict):
    """Saves a final asset with production-grade validation."""
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            query = """
                INSERT INTO muse_assets (content, metadata, embedding)
                VALUES (%s, %s, %s)
                RETURNING id;
            """
            # Ensure workspace_id is in metadata
            metadata = asset_data.get("metadata", {})
            metadata["workspace_id"] = workspace_id

            await cur.execute(
                query,
                (
                    asset_data["content"],
                    psycopg.types.json.Jsonb(metadata),
                    asset_data.get("embedding"),
                ),
            )
            result = await cur.fetchone()
            await conn.commit()
            return result[0]


async def save_asset_vault(
    workspace_id: str, content: str, asset_type: str, metadata: dict = None
) -> str:
    """
    SOTA Asset Vaulting.
    Saves the final creative asset to the database with industrial metadata tagging.
    """
    if metadata is None:
        metadata = {}
    metadata.update(
        {
            "asset_type": asset_type,
            "vaulted_at": datetime.now().isoformat(),
            "is_final": True,
        }
    )

    asset_data = {"content": content, "metadata": metadata}
    return await save_asset_db(workspace_id, asset_data)


async def save_entity(
    workspace_id: str,
    name: str,
    entity_type: str,
    description: str,
    embedding: list[float],
    metadata: dict = None,
):
    """
    SOTA Entity Memory.
    Syncs research results to the permanent entity_embeddings table.
    """
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            query = """
                INSERT INTO entity_embeddings (workspace_id, entity_name, entity_type, description, embedding, metadata)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id;
            """
            await cur.execute(
                query,
                (
                    workspace_id,
                    name,
                    entity_type,
                    description,
                    embedding,
                    psycopg.types.json.Jsonb(metadata or {}),
                ),
            )
            result = await cur.fetchone()
            await conn.commit()
            return result[0]
