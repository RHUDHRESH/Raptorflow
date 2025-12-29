import asyncio
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

import psycopg
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg_pool import AsyncConnectionPool

from core.config import get_settings

logger = logging.getLogger("raptorflow.db")

# Initialize settings
settings = get_settings()

# Keys fetched with GCP Secret Manager support
DB_URI = settings.DATABASE_URL
UPSTASH_URL = settings.UPSTASH_REDIS_REST_URL
UPSTASH_TOKEN = settings.UPSTASH_REDIS_REST_TOKEN

DB_CONN_KWARGS = {
    "prepare_threshold": 5,
    "application_name": "raptorflow_backend",
    "connect_timeout": 10,
    "options": "-c statement_timeout=30000",
}

# Global pool for production-grade connection management
_pool: Optional[AsyncConnectionPool] = None
_TENANT_COLUMN_CACHE: Dict[str, str] = {}


def get_pool() -> AsyncConnectionPool:
    global _pool
    if _pool is None:
        if not DB_URI:
            raise ValueError("DATABASE_URL is not configured")
        try:
            # Optimized connection pool configuration
            _pool = AsyncConnectionPool(
                DB_URI,
                min_size=5,  # Increased minimum connections
                max_size=50,  # Increased maximum for production
                open=False,
                timeout=30,  # Connection timeout
                max_lifetime=3600,  # 1 hour lifetime (increased)
                max_idle=600,  # 10 minutes idle timeout
                kwargs=dict(DB_CONN_KWARGS),
            )
            logger.info("Created optimized database pool: min_size=5, max_size=50")
        except Exception as e:
            logger.error(f"Failed to create database pool: {e}")
            raise
    return _pool


async def close_pool():
    """Close the global connection pool."""
    global _pool
    if _pool is not None:
        try:
            await _pool.close()
        except Exception as e:
            logger.warning(f"Error closing database pool: {e}")
        finally:
            _pool = None


@asynccontextmanager
async def get_db_connection():
    """Async context manager for psycopg connection from the pool."""
    pool = get_pool()
    if settings.DB_DISABLE_POOL or os.name == "nt":
        pool = None
    pool_cm = None
    conn = None

    # Ensure pool is initialized/opened
    if pool is not None and (not hasattr(pool, "_opened") or not pool._opened):
        try:
            await asyncio.wait_for(pool.open(), timeout=10)
        except Exception as e:
            logger.warning("Pool opening failed, falling back: %s", e)
            pool = None

    if pool is not None:
        try:
            pool_cm = pool.connection(timeout=10)
            conn = await pool_cm.__aenter__()
        except Exception as e:
            logger.warning("Pool connection failed, falling back: %s", e)
            if pool_cm is not None:
                try:
                    await pool_cm.__aexit__(None, None, None)
                except Exception:
                    pass
            conn = None

    if conn is None:
        conn = await psycopg.AsyncConnection.connect(DB_URI, **DB_CONN_KWARGS)
        try:
            yield conn
        finally:
            await conn.close()
        return

    try:
        yield conn
    finally:
        if pool_cm is not None:
            await pool_cm.__aexit__(None, None, None)


@asynccontextmanager
async def get_db_transaction():
    """Async context manager for database transactions with proper rollback."""
    async with get_db_connection() as conn:
        transaction = conn.transaction()
        try:
            await transaction.start()
            yield conn
            await transaction.commit()
        except Exception as e:
            await transaction.rollback()
            logger.error(f"Database transaction rolled back: {e}")
            raise
        finally:
            await transaction.__aexit__(None, None, None)


async def resolve_tenant_column(table: str) -> str:
    """
    Resolve whether the table uses tenant_id or workspace_id.
    Caches the result to avoid repeated information_schema lookups.
    """
    table_key = table.lower()
    cached = _TENANT_COLUMN_CACHE.get(table_key)
    if cached:
        return cached

    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = %s
                  AND column_name IN ('tenant_id', 'workspace_id')
                """,
                (table_key,),
            )
            rows = await cur.fetchall()

    columns = {row[0] for row in rows}
    if "tenant_id" in columns:
        selected = "tenant_id"
    elif "workspace_id" in columns:
        selected = "workspace_id"
    else:
        raise ValueError(
            f"Table {table_key} is missing tenant_id/workspace_id column."
        )

    _TENANT_COLUMN_CACHE[table_key] = selected
    return selected


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
        try:
            await pool.open()
        except Exception as e:
            logger.error(f"Failed to open database pool for checkpointer: {e}")
            raise

    try:
        # In LangGraph 0.2.x, PostgresSaver.from_conn_string or constructor with pool
        checkpointer = SupabaseSaver(pool)
        return checkpointer
    except Exception as e:
        logger.error(f"Failed to initialize checkpointer: {e}")
        raise


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
    # Input validation
    if not workspace_id or not isinstance(workspace_id, str):
        raise ValueError("workspace_id must be a non-empty string")

    if not embedding or not isinstance(embedding, list) or len(embedding) == 0:
        raise ValueError("embedding must be a non-empty list of floats")

    if not all(isinstance(x, (int, float)) for x in embedding):
        raise ValueError("embedding must contain only numeric values")

    if limit <= 0 or limit > 100:
        raise ValueError("limit must be between 1 and 100")

    # Validate table name against allowed tables
    allowed_tables = [
        "muse_assets",
        "agent_memory_semantic",
        "agent_memory_episodic",
        "entity_embeddings",
    ]
    if table not in allowed_tables:
        raise ValueError(f"table must be one of: {allowed_tables}")
    # Map table to its specific column names
    SCHEMA_MAP = {
        "muse_assets": {"content": "content", "workspace": "workspace_id"},
        "agent_memory_semantic": {"content": "fact", "workspace": "tenant_id"},
        "agent_memory_episodic": {"content": "observation", "workspace": "thread_id"},
        "entity_embeddings": {"content": "description", "workspace": "workspace_id"},
    }

    schema = SCHEMA_MAP.get(
        table, {"content": "content", "workspace": "metadata->>'workspace_id'"}
    )
    content_col = schema["content"]
    workspace_col = schema["workspace"]
    if workspace_col in ("tenant_id", "workspace_id"):
        workspace_col = await resolve_tenant_column(table)

    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            # Base query - use parameterized queries
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

            try:
                await cur.execute(query, tuple(params))
                results = await cur.fetchall()
                return results
            except psycopg.Error as e:
                logger.error(f"Vector search query failed: {e}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error in vector search: {e}")
                raise


async def get_memory(
    workspace_id: str,
    query_embedding: list[float],
    memory_type: str = "semantic",
    limit: int = 5,
):
    """
    Retrieves memory (episodic or semantic) using vector similarity.
    """
    table = (
        "agent_memory_semantic"
        if memory_type == "semantic"
        else "agent_memory_episodic"
    )
    workspace_col = "tenant_id" if memory_type == "semantic" else "thread_id"
    content_col = "fact" if memory_type == "semantic" else "observation"

    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            query = f"""
                SELECT id, {content_col}, 1 - (embedding <=> %s::vector) as similarity
                FROM {table}
                WHERE {workspace_col} = %s
                AND 1 - (embedding <=> %s::vector) > 0.7
                ORDER BY embedding <=> %s::vector
                LIMIT %s;
            """
            await cur.execute(
                query,
                (
                    query_embedding,
                    workspace_id,
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
            try:
                tenant_column = await resolve_tenant_column("muse_assets")
                query = """
                    INSERT INTO muse_assets (
                        {tenant_column},
                        content,
                        asset_type,
                        metadata,
                        embedding,
                        status,
                        quality_score,
                        generation_prompt,
                        generation_model,
                        generation_tokens,
                        tags
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id;
                """
                metadata = asset_data.get("metadata", {})
                metadata["workspace_id"] = workspace_id
                metadata["tenant_id"] = workspace_id

                asset_type = asset_data.get("asset_type") or "text"
                status = asset_data.get("status") or "ready"

                await cur.execute(
                    query.format(tenant_column=tenant_column),
                    (
                        workspace_id,
                        asset_data["content"],
                        asset_type,
                        psycopg.types.json.Jsonb(metadata),
                        asset_data.get("embedding"),
                        status,
                        asset_data.get("quality_score"),
                        asset_data.get("generation_prompt"),
                        asset_data.get("generation_model"),
                        asset_data.get("generation_tokens"),
                        asset_data.get("tags"),
                    ),
                )
                result = await cur.fetchone()
                await conn.commit()
                return str(result[0])
            except Exception:
                await conn.rollback()
                raise


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

    asset_data = {"content": content, "metadata": metadata, "asset_type": asset_type}
    return await save_asset_db(workspace_id, asset_data)


async def save_campaign(
    tenant_id: str, campaign_data: dict, campaign_id: Optional[str] = None
) -> str:
    """Saves or updates a campaign strategy arc in Supabase."""
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            workspace_id = campaign_data.get("workspace_id", tenant_id)
            phase_order = campaign_data.get("phase_order", [])
            milestones = campaign_data.get("milestones", [])
            campaign_tag = campaign_data.get("campaign_tag")

            if campaign_id:
                query = """
                    UPDATE campaigns
                    SET title = %s,
                        objective = %s,
                        status = %s,
                        arc_data = %s,
                        phase_order = %s,
                        milestones = %s,
                        campaign_tag = %s,
                        kpi_targets = %s,
                        audit_data = %s,
                        updated_at = now()
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
                        psycopg.types.json.Jsonb(phase_order),
                        psycopg.types.json.Jsonb(milestones),
                        campaign_tag,
                        psycopg.types.json.Jsonb(campaign_data.get("kpi_targets", {})),
                        psycopg.types.json.Jsonb(campaign_data.get("audit_data", {})),
                        campaign_id,
                        tenant_id,
                    ),
                )
            else:
                query = """
                    INSERT INTO campaigns (
                        tenant_id, workspace_id, title, objective, status,
                        arc_data, phase_order, milestones, campaign_tag,
                        kpi_targets, audit_data
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id;
                """
                await cur.execute(
                    query,
                    (
                        tenant_id,
                        workspace_id,
                        campaign_data.get("title"),
                        campaign_data.get("objective"),
                        campaign_data.get("status", "draft"),
                        psycopg.types.json.Jsonb(campaign_data.get("arc_data", {})),
                        psycopg.types.json.Jsonb(phase_order),
                        psycopg.types.json.Jsonb(milestones),
                        campaign_tag,
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
                INSERT INTO moves (
                    campaign_id, workspace_id, title, description, status, priority,
                    move_type, tool_requirements, refinement_data, consensus_metrics,
                    decree, reasoning_chain_id, campaign_name,
                    checklist, assets, daily_metrics,
                    confidence, started_at, completed_at, paused_at,
                    rag_status, rag_reason
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """
            await cur.execute(
                query,
                (
                    campaign_id,
                    move_data.get("workspace_id"),
                    move_data.get("title"),
                    move_data.get("description"),
                    move_data.get("status", "pending"),
                    move_data.get("priority", 3),
                    move_data.get("move_type"),
                    psycopg.types.json.Jsonb(move_data.get("tool_requirements", [])),
                    psycopg.types.json.Jsonb(move_data.get("refinement_data", {})),
                    psycopg.types.json.Jsonb(move_data.get("consensus_metrics", {})),
                    move_data.get("decree"),
                    move_data.get("reasoning_chain_id"),
                    move_data.get("campaign_name"),
                    psycopg.types.json.Jsonb(move_data.get("checklist", [])),
                    psycopg.types.json.Jsonb(move_data.get("assets", [])),
                    psycopg.types.json.Jsonb(move_data.get("daily_metrics", [])),
                    move_data.get("confidence"),
                    move_data.get("started_at"),
                    move_data.get("completed_at"),
                    move_data.get("paused_at"),
                    move_data.get("rag_status"),
                    move_data.get("rag_reason"),
                ),
            )
            result = await cur.fetchone()
            await conn.commit()
            return str(result[0])


_MOVE_COLUMNS = """
    id, campaign_id, workspace_id, title, description, status, priority,
    move_type, tool_requirements, refinement_data, consensus_metrics,
    decree, reasoning_chain_id, campaign_name, execution_result,
    checklist, assets, daily_metrics, confidence, started_at, completed_at,
    paused_at, rag_status, rag_reason, created_at, updated_at
"""


def _serialize_move_row(row):
    (
        move_id,
        campaign_ref,
        move_workspace,
        title,
        description,
        status,
        priority,
        move_type,
        tool_requirements,
        refinement_data,
        consensus_metrics,
        decree,
        reasoning_chain_id,
        campaign_name,
        execution_result,
        checklist,
        assets,
        daily_metrics,
        confidence,
        started_at,
        completed_at,
        paused_at,
        rag_status,
        rag_reason,
        created_at,
        updated_at,
    ) = row

    return {
        "id": str(move_id),
        "campaign_id": str(campaign_ref) if campaign_ref else None,
        "workspace_id": str(move_workspace),
        "title": title,
        "description": description,
        "status": status,
        "priority": priority,
        "move_type": move_type,
        "tool_requirements": tool_requirements or [],
        "refinement_data": refinement_data or {},
        "consensus_metrics": consensus_metrics or {},
        "decree": decree,
        "reasoning_chain_id": str(reasoning_chain_id) if reasoning_chain_id else None,
        "campaign_name": campaign_name,
        "execution_result": execution_result or {},
        "checklist": checklist or [],
        "assets": assets or [],
        "daily_metrics": daily_metrics or [],
        "confidence": confidence,
        "started_at": started_at.isoformat() if started_at else None,
        "completed_at": completed_at.isoformat() if completed_at else None,
        "paused_at": paused_at.isoformat() if paused_at else None,
        "rag_status": rag_status,
        "rag_reason": rag_reason,
        "created_at": created_at.isoformat() if created_at else None,
        "updated_at": updated_at.isoformat() if updated_at else None,
    }


async def fetch_move_detail(
    workspace_id: str, move_id: str
) -> Optional[Dict[str, Any]]:
    """Fetch a single move with extended metadata."""
    query = f"""
        SELECT {_MOVE_COLUMNS}
        FROM moves
        WHERE id = %s AND workspace_id = %s
        LIMIT 1
    """
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(query, (move_id, workspace_id))
            row = await cur.fetchone()
    if not row:
        return None
    return _serialize_move_row(row)


async def update_move_record(
    workspace_id: str, move_id: str, updates: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """Update selected move fields."""
    allowed = {
        "title": "title",
        "description": "description",
        "status": "status",
        "priority": "priority",
        "move_type": "move_type",
        "tool_requirements": "tool_requirements",
        "refinement_data": "refinement_data",
        "consensus_metrics": "consensus_metrics",
        "decree": "decree",
        "reasoning_chain_id": "reasoning_chain_id",
        "campaign_name": "campaign_name",
        "execution_result": "execution_result",
        "checklist": "checklist",
        "assets": "assets",
        "daily_metrics": "daily_metrics",
        "confidence": "confidence",
        "started_at": "started_at",
        "completed_at": "completed_at",
        "paused_at": "paused_at",
        "rag_status": "rag_status",
        "rag_reason": "rag_reason",
    }
    set_clauses = []
    params: List[Any] = []
    json_defaults = {
        "tool_requirements": [],
        "refinement_data": {},
        "consensus_metrics": {},
        "checklist": [],
        "assets": [],
        "daily_metrics": [],
        "execution_result": {},
    }
    for key, column in allowed.items():
        if key in updates:
            set_clauses.append(f"{column} = %s")
            value = updates[key]
            if column in {
                "tool_requirements",
                "refinement_data",
                "consensus_metrics",
                "checklist",
                "assets",
                "daily_metrics",
                "execution_result",
            }:
                default = json_defaults.get(column, {})
                params.append(
                    psycopg.types.json.Jsonb(value if value is not None else default)
                )
            else:
                params.append(value)
    if not set_clauses:
        return None
    set_clause = ", ".join(set_clauses + ["updated_at = now()"])
    query = f"""
        UPDATE moves
        SET {set_clause}
        WHERE id = %s AND workspace_id = %s
        RETURNING {_MOVE_COLUMNS}
    """
    params.extend([move_id, workspace_id])
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(query, tuple(params))
            row = await cur.fetchone()
    if not row:
        return None
    return _serialize_move_row(row)


async def fetch_reasoning_chain(
    workspace_id: str, chain_id: str
) -> Optional[Dict[str, Any]]:
    query = """
        SELECT id, debate_history, final_synthesis, metrics, metadata
        FROM reasoning_chains
        WHERE id = %s AND workspace_id = %s
        LIMIT 1
    """
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(query, (chain_id, workspace_id))
            row = await cur.fetchone()
    if not row:
        return None
    id_val, debate_history, final_synthesis, metrics, metadata = row
    return {
        "id": str(id_val),
        "debate_history": debate_history or [],
        "final_synthesis": final_synthesis,
        "metrics": metrics or {},
        "metadata": metadata or {},
    }


async def fetch_rejected_paths(
    workspace_id: str, chain_id: str
) -> List[Dict[str, Any]]:
    query = """
        SELECT path_name, reason
        FROM rejected_paths
        WHERE reasoning_chain_id = %s AND workspace_id = %s
    """
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(query, (chain_id, workspace_id))
            rows = await cur.fetchall()
    return [{"path": row[0], "reason": row[1]} for row in rows]


async def fetch_exploit_by_id(
    workspace_id: str, exploit_id: str
) -> Optional[Dict[str, Any]]:
    query = """
        SELECT id, title, description, predicted_roi
        FROM agent_exploits
        WHERE id = %s AND workspace_id = %s
        LIMIT 1
    """
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(query, (exploit_id, workspace_id))
            row = await cur.fetchone()
    if not row:
        return None
    return {
        "id": str(row[0]),
        "title": row[1],
        "description": row[2],
        "predicted_roi": float(row[3]) if row[3] is not None else None,
    }


async def fetch_campaign_summaries(
    workspace_id: str,
    status: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    """List campaigns for a workspace with move counts."""
    filters = ["c.workspace_id = %s"]
    params: List[Any] = [workspace_id]
    if status:
        filters.append("c.status = %s")
        params.append(status)
    if search:
        filters.append("c.title ILIKE %s")
        params.append(f"%{search}%")

    where_clause = " AND ".join(filters)
    query = f"""
        SELECT
            c.id,
            c.title,
            c.objective,
            c.status,
            c.workspace_id,
            c.campaign_tag,
            c.arc_data,
            c.phase_order,
            c.milestones,
            COUNT(m.id) AS move_count,
            c.created_at,
            c.updated_at
        FROM campaigns c
        LEFT JOIN moves m ON m.campaign_id = c.id
        WHERE {where_clause}
        GROUP BY c.id
        ORDER BY c.created_at DESC
        LIMIT %s OFFSET %s
    """
    params.extend([limit, offset])
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(query, tuple(params))
            rows = await cur.fetchall()

    summaries = []
    for row in rows:
        (
            cam_id,
            title,
            objective,
            cam_status,
            cam_workspace,
            campaign_tag,
            arc_data,
            phase_order,
            milestones,
            move_count,
            created_at,
            updated_at,
        ) = row
        summaries.append(
            {
                "id": str(cam_id),
                "title": title,
                "objective": objective,
                "status": cam_status,
                "workspace_id": str(cam_workspace),
                "campaign_tag": campaign_tag,
                "arc_data": arc_data or {},
                "phase_order": phase_order or [],
                "milestones": milestones or [],
                "move_count": move_count or 0,
                "created_at": created_at.isoformat() if created_at else None,
                "updated_at": updated_at.isoformat() if updated_at else None,
            }
        )
    return summaries


async def fetch_campaign_details(
    workspace_id: str, campaign_id: str
) -> Optional[Dict[str, Any]]:
    """Fetch a single campaign plus metadata."""
    query = """
        SELECT
            id, tenant_id, title, objective, status, workspace_id, campaign_tag,
            arc_data, phase_order, milestones, created_at, updated_at
        FROM campaigns
        WHERE id = %s AND workspace_id = %s
        LIMIT 1
    """
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(query, (campaign_id, workspace_id))
            row = await cur.fetchone()
    if not row:
        return None
    (
        cam_id,
        tenant_id,
        title,
        objective,
        cam_status,
        cam_workspace,
        campaign_tag,
        arc_data,
        phase_order,
        milestones,
        created_at,
        updated_at,
    ) = row
    return {
        "id": str(cam_id),
        "tenant_id": str(tenant_id),
        "title": title,
        "objective": objective,
        "status": cam_status,
        "workspace_id": str(cam_workspace),
        "campaign_tag": campaign_tag,
        "arc_data": arc_data or {},
        "phase_order": phase_order or [],
        "milestones": milestones or [],
        "created_at": created_at.isoformat() if created_at else None,
        "updated_at": updated_at.isoformat() if updated_at else None,
    }


async def fetch_moves_for_campaign(
    workspace_id: str, campaign_id: str
) -> List[Dict[str, Any]]:
    """Return all moves scoped to a campaign."""
    query = """
        SELECT
            id, title, description, status, priority, move_type,
            campaign_id, workspace_id, campaign_name,
            consensus_metrics, decree, reasoning_chain_id,
            created_at, updated_at
        FROM moves
        WHERE workspace_id = %s AND campaign_id = %s
        ORDER BY created_at DESC
    """
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(query, (workspace_id, campaign_id))
            rows = await cur.fetchall()
    moves = []
    for row in rows:
        (
            move_id,
            title,
            description,
            status,
            priority,
            move_type,
            campaign_ref,
            move_workspace,
            campaign_name,
            consensus_metrics,
            decree,
            reasoning_chain_id,
            created_at,
            updated_at,
        ) = row

        moves.append(
            {
                "id": str(move_id),
                "title": title,
                "description": description,
                "status": status,
                "priority": priority,
                "move_type": move_type,
                "campaign_id": str(campaign_ref) if campaign_ref else None,
                "workspace_id": str(move_workspace),
                "campaign_name": campaign_name,
                "consensus_metrics": consensus_metrics,
                "decree": decree,
                "reasoning_chain_id": reasoning_chain_id,
                "created_at": created_at.isoformat() if created_at else None,
                "updated_at": updated_at.isoformat() if updated_at else None,
            }
        )
    return moves


async def update_campaign_record(
    workspace_id: str, campaign_id: str, updates: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """Update selected fields on a campaign."""
    allowed = {
        "title": "title",
        "objective": "objective",
        "status": "status",
        "arc_data": "arc_data",
        "phase_order": "phase_order",
        "milestones": "milestones",
        "campaign_tag": "campaign_tag",
    }
    set_clauses = []
    params: List[Any] = []
    for key, column in allowed.items():
        if key in updates:
            set_clauses.append(f"{column} = %s")
            value = updates[key]
            if column == "arc_data":
                params.append(psycopg.types.json.Jsonb(value or {}))
            elif column in ("phase_order", "milestones"):
                params.append(psycopg.types.json.Jsonb(value or []))
            else:
                params.append(value)
    if not set_clauses:
        return None
    set_clause = ", ".join(set_clauses + ["updated_at = now()"])
    query = f"""
        UPDATE campaigns
        SET {set_clause}
        WHERE id = %s AND workspace_id = %s
        RETURNING id, title, objective, status, workspace_id, campaign_tag,
                  arc_data, phase_order, milestones, created_at, updated_at
    """
    params.extend([campaign_id, workspace_id])
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(query, tuple(params))
            row = await cur.fetchone()
    if not row:
        return None
    (
        cam_id,
        title,
        objective,
        cam_status,
        cam_workspace,
        campaign_tag,
        arc_data,
        phase_order,
        milestones,
        created_at,
        updated_at,
    ) = row
    return {
        "id": str(cam_id),
        "title": title,
        "objective": objective,
        "status": cam_status,
        "workspace_id": str(cam_workspace),
        "campaign_tag": campaign_tag,
        "arc_data": arc_data or {},
        "phase_order": phase_order or [],
        "milestones": milestones or [],
        "created_at": created_at.isoformat() if created_at else None,
        "updated_at": updated_at.isoformat() if updated_at else None,
    }


async def archive_campaign(workspace_id: str, campaign_id: str) -> None:
    """Soft delete a campaign and cascade move updates."""
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                UPDATE campaigns
                SET status = 'archived', updated_at = now()
                WHERE id = %s AND workspace_id = %s
                """,
                (campaign_id, workspace_id),
            )
            await cur.execute(
                """
                UPDATE moves
                SET status = 'rejected',
                    refinement_data = COALESCE(
                        jsonb_set(
                            refinement_data,
                            '{campaign_status}',
                            to_jsonb('archived'::text),
                            true
                        ),
                        jsonb_build_object('campaign_status', to_jsonb('archived'::text))
                    ),
                    updated_at = now()
                WHERE campaign_id = %s AND workspace_id = %s
                """,
                (campaign_id, workspace_id),
            )


async def update_moves_phase_order(
    workspace_id: str, campaign_id: str, phase_order: List[str]
) -> None:
    """Propagate new phase order into move metadata."""
    if not phase_order:
        return
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                UPDATE moves
                SET refinement_data = CASE
                    WHEN refinement_data IS NULL THEN jsonb_build_object(
                        'campaign_phase_order', to_jsonb(%s)
                    )
                    ELSE jsonb_set(
                        refinement_data,
                        '{campaign_phase_order}',
                        to_jsonb(%s),
                        true
                    )
                END,
                    updated_at = now()
                WHERE campaign_id = %s AND workspace_id = %s
                """,
                (
                    psycopg.types.json.Jsonb(phase_order),
                    psycopg.types.json.Jsonb(phase_order),
                    campaign_id,
                    workspace_id,
                ),
            )


async def fetch_moves(
    workspace_id: str,
    campaign_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    """List moves with optional campaign/status filters."""
    filters = ["workspace_id = %s"]
    params: List[Any] = [workspace_id]
    if campaign_id:
        filters.append("campaign_id = %s")
        params.append(campaign_id)
    if status:
        filters.append("status = %s")
        params.append(status)

    filters_clause = " AND ".join(filters)
    query = f"""
        SELECT
            id, title, description, status, priority, move_type,
            campaign_id, workspace_id, campaign_name,
            consensus_metrics, decree, reasoning_chain_id,
            created_at, updated_at
        FROM moves
        WHERE {filters_clause}
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """
    params.extend([limit, offset])
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(query, tuple(params))
            rows = await cur.fetchall()
    results: List[Dict[str, Any]] = []
    for row in rows:
        (
            move_id,
            title,
            description,
            status_value,
            priority,
            move_type,
            campaign_ref,
            move_workspace,
            campaign_name,
            consensus_metrics,
            decree,
            reasoning_chain_id,
            created_at,
            updated_at,
        ) = row
        results.append(
            {
                "id": str(move_id),
                "title": title,
                "description": description,
                "status": status_value,
                "priority": priority,
                "move_type": move_type,
                "campaign_id": str(campaign_ref) if campaign_ref else None,
                "workspace_id": str(move_workspace),
                "campaign_name": campaign_name,
                "consensus_metrics": consensus_metrics,
                "decree": decree,
                "reasoning_chain_id": reasoning_chain_id,
                "created_at": created_at.isoformat() if created_at else None,
                "updated_at": updated_at.isoformat() if updated_at else None,
            }
        )
    return results


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


async def update_move_description(move_id: str, description: str):
    """Updates the description of a move."""
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            query = """
                UPDATE moves
                SET description = %s, updated_at = now()
                WHERE id = %s;
            """
            await cur.execute(query, (description, move_id))
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


async def save_reasoning_chain(workspace_id: str, chain_data: dict) -> str:
    """
    Persists a full Council reasoning chain (debate log) to Supabase.
    """
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            try:
                # Use provided ID or generate one
                chain_id = chain_data.get("id")

                if chain_id:
                    query = """
                        INSERT INTO reasoning_chains (
                            id, workspace_id, debate_history, final_synthesis, metrics, metadata
                        )
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE SET
                            debate_history = EXCLUDED.debate_history,
                            final_synthesis = EXCLUDED.final_synthesis,
                            metrics = EXCLUDED.metrics,
                            metadata = EXCLUDED.metadata
                        RETURNING id;
                    """
                    await cur.execute(
                        query,
                        (
                            chain_id,
                            workspace_id,
                            psycopg.types.json.Jsonb(
                                chain_data.get("debate_history", [])
                            ),
                            chain_data.get("final_synthesis"),
                            psycopg.types.json.Jsonb(chain_data.get("metrics", {})),
                            psycopg.types.json.Jsonb(chain_data.get("metadata", {})),
                        ),
                    )
                else:
                    query = """
                        INSERT INTO reasoning_chains (workspace_id, debate_history, final_synthesis, metrics, metadata)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id;
                    """
                    await cur.execute(
                        query,
                        (
                            workspace_id,
                            psycopg.types.json.Jsonb(
                                chain_data.get("debate_history", [])
                            ),
                            chain_data.get("final_synthesis"),
                            psycopg.types.json.Jsonb(chain_data.get("metrics", {})),
                            psycopg.types.json.Jsonb(chain_data.get("metadata", {})),
                        ),
                    )

                result = await cur.fetchone()
                await conn.commit()
                return str(result[0])
            except Exception as e:
                await conn.rollback()
                logger.error(f"Failed to save reasoning chain: {e}")
                raise


async def save_rejections(
    workspace_id: str, chain_id: str, rejected_paths: List[Dict[str, Any]]
):
    """Save rejected strategic paths for future avoidance."""
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            for path in rejected_paths:
                await cur.execute(
                    """
                    INSERT INTO rejected_paths (workspace_id, reasoning_chain_id, path_name, reason)
                    VALUES (%s, %s, %s, %s)
                """,
                    (workspace_id, chain_id, path.get("path"), path.get("reason")),
                )


async def save_heuristics(workspace_id: str, heuristics: Dict[str, List[str]]):
    """Save Never/Always rules extracted by the Librarian."""
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            # Save Never rules
            for rule in heuristics.get("never_rules", []):
                await cur.execute(
                    """
                    INSERT INTO agent_heuristics (workspace_id, rule_type, content)
                    VALUES (%s, 'never', %s)
                """,
                    (workspace_id, rule),
                )
            # Save Always rules
            for rule in heuristics.get("always_rules", []):
                await cur.execute(
                    """
                    INSERT INTO agent_heuristics (workspace_id, rule_type, content)
                    VALUES (%s, 'always', %s)
                """,
                    (workspace_id, rule),
                )


async def save_exploits(workspace_id: str, exploits: List[Dict[str, Any]]):
    """Save proven exploits extracted by the Librarian."""
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            for exploit in exploits:
                await cur.execute(
                    """
                    INSERT INTO agent_exploits (workspace_id, title, description, predicted_roi)
                    VALUES (%s, %s, %s, %s)
                """,
                    (
                        workspace_id,
                        exploit.get("title"),
                        exploit.get("description"),
                        exploit.get("predicted_roi"),
                    ),
                )


async def fetch_heuristics(workspace_id: str, role: str) -> Dict[str, List[str]]:
    """Fetch all active heuristics for a specific role and workspace."""
    heuristics = {"never_rules": [], "always_rules": []}
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT rule_type, content FROM agent_heuristics
                WHERE workspace_id = %s AND (agent_role = %s OR agent_role IS NULL)
            """,
                (workspace_id, role),
            )
            rows = await cur.fetchall()
            for row in rows:
                if row[0] == "never":
                    heuristics["never_rules"].append(row[1])
                else:
                    heuristics["always_rules"].append(row[1])
    return heuristics


async def fetch_exploits(workspace_id: str, role: str) -> List[Dict[str, Any]]:
    """Fetch all relevant exploits for a specific role and workspace."""
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            # For now, fetch all exploits for the workspace
            # In production, we'd use semantic search or role filtering
            await cur.execute(
                """
                SELECT title, description, predicted_roi FROM agent_exploits
                WHERE workspace_id = %s
                ORDER BY actual_roi DESC NULLS LAST
                LIMIT 5
            """,
                (workspace_id,),
            )
            rows = await cur.fetchall()
            return [{"title": r[0], "description": r[1], "roi": r[2]} for r in rows]
