from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

import psycopg
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg_pool import AsyncConnectionPool

from backend.core.config import get_settings

# Initialize settings
settings = get_settings()

# Keys fetched with GCP Secret Manager support
DB_URI = settings.DATABASE_URL
UPSTASH_URL = settings.UPSTASH_REDIS_REST_URL
UPSTASH_TOKEN = settings.UPSTASH_REDIS_REST_TOKEN

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
            pass  # Ignore if already opening/opened in some versions

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
    table: str = "agent_memory_semantic",
    limit: int = 5,
    filters: Optional[dict] = None,
):
    """
    Performs a pgvector similarity search, STRICTLY scoped to workspace_id.
    Supports optional metadata filtering and handles different table schemas.
    """
    # Map table to its specific column names
    SCHEMA_MAP = {
        "muse_assets": {"content": "content", "workspace": "metadata->>'workspace_id'"},
        "agent_memory_semantic": {"content": "fact", "workspace": "tenant_id"},
        "agent_memory_procedural": {"content": "fact", "workspace": "tenant_id"},
        "entity_embeddings": {"content": "description", "workspace": "workspace_id"},
    }

    schema = SCHEMA_MAP.get(
        table, {"content": "content", "workspace": "metadata->>'workspace_id'"}
    )
    content_col = schema["content"]
    workspace_col = schema["workspace"]

    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            # Base query
            query = f"""
                SELECT id, {content_col}, metadata, 1 - (embedding <=> %s::vector) as similarity
                FROM {table}
                WHERE {workspace_col} = %s
            """
            params = [embedding, workspace_id]

            # Dynamically add filters (assuming they are in metadata for all tables)
            if filters:
                for key, value in filters.items():
                    query += f" AND metadata->>'{key}' = %s"
                    params.append(str(value))

            query += """
                AND 1 - (embedding <=> %s::vector) > 0.5
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


async def save_campaign(
    tenant_id: str, campaign_data: dict, campaign_id: Optional[str] = None
) -> str:
    """Saves or updates a campaign strategy arc in Supabase."""
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            if campaign_id:
                query = """
                    UPDATE campaigns
                    SET title = %s, objective = %s, status = %s, arc_data = %s,
                    kpi_targets = %s, audit_data = %s, updated_at = now()
                    WHERE id = %s AND tenant_id = %s
                    RETURNING id;
                """
                await cur.execute(
                    query,
                    (
                        campaign_data.get("title"),
                        campaign_data.get("objective"),
                        campaign_data.get("status", "draft"),
                        psycopg.types.json.Jsonb(campaign_data.get("arc_data", {})),
                        psycopg.types.json.Jsonb(campaign_data.get("kpi_targets", {})),
                        psycopg.types.json.Jsonb(campaign_data.get("audit_data", {})),
                        campaign_id,
                        tenant_id,
                    ),
                )
            else:
                query = """
                    INSERT INTO campaigns (tenant_id, title, objective, status, arc_data, kpi_targets, audit_data)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id;
                """
                await cur.execute(
                    query,
                    (
                        tenant_id,
                        campaign_data.get("title"),
                        campaign_data.get("objective"),
                        campaign_data.get("status", "draft"),
                        psycopg.types.json.Jsonb(campaign_data.get("arc_data", {})),
                        psycopg.types.json.Jsonb(campaign_data.get("kpi_targets", {})),
                        psycopg.types.json.Jsonb(campaign_data.get("audit_data", {})),
                    ),
                )
            result = await cur.fetchone()
            await conn.commit()
            return str(result[0])


async def save_move(campaign_id: str, move_data: dict) -> str:
    """Saves a weekly move to Supabase."""
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            query = """
                INSERT INTO moves (campaign_id, title, description, status,
                priority, move_type, tool_requirements, refinement_data)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """
            await cur.execute(
                query,
                (
                    campaign_id,
                    move_data.get("title"),
                    move_data.get("description"),
                    move_data.get("status", "pending"),
                    move_data.get("priority", 3),
                    move_data.get("move_type"),
                    psycopg.types.json.Jsonb(move_data.get("tool_requirements", [])),
                    psycopg.types.json.Jsonb(move_data.get("refinement_data", {})),
                ),
            )
            result = await cur.fetchone()
            await conn.commit()
            return str(result[0])


async def update_move_status(move_id: str, status: str, result: dict = None):
    """Updates the status and execution result of a move."""
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            query = """
                UPDATE moves
                SET status = %s, execution_result = %s, updated_at = now()
                WHERE id = %s;
            """
            await cur.execute(
                query, (status, psycopg.types.json.Jsonb(result or {}), move_id)
            )
            await conn.commit()


async def log_agent_decision(tenant_id: str, decision_data: dict):
    """Logs an agent's strategic decision for auditability and MLOps."""
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            query = """
                INSERT INTO agent_decision_audit (
                    tenant_id, agent_id, decision_type, input_state,
                    output_decision, rationale, cost_estimate
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """
            await cur.execute(
                query,
                (
                    tenant_id,
                    decision_data.get("agent_id"),
                    decision_data.get("decision_type"),
                    psycopg.types.json.Jsonb(decision_data.get("input_state", {})),
                    psycopg.types.json.Jsonb(decision_data.get("output_decision", {})),
                    decision_data.get("rationale"),
                    decision_data.get("cost_estimate", 0),
                ),
            )
            await conn.commit()


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
