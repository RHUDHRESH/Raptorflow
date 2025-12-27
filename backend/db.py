import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

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

# Global pool for production-grade connection management
_pool: Optional[AsyncConnectionPool] = None


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
                kwargs={
                    # Connection parameters optimization
                    "prepare_threshold": 5,
                    "cursor_factory": psycopg.ServerCursor,
                    "application_name": "raptorflow_backend",
                    "connect_timeout": 10,
                    "command_timeout": 30,
                    "options": "-c default_transaction_isolation=read_committed",
                },
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
    # Ensure pool is initialized/opened
    if not hasattr(pool, "_opened") or not pool._opened:
        try:
            await pool.open()
        except psycopg.OperationalError as e:
            raise RuntimeError(f"Failed to open database pool: {e}")
        except Exception as e:
            logger.warning(f"Pool opening warning: {e}")

    async with pool.connection() as conn:
        yield conn


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
        "muse_assets": {"content": "content", "workspace": "metadata->>'workspace_id'"},
        "agent_memory_semantic": {"content": "fact", "workspace": "tenant_id"},
        "agent_memory_episodic": {"content": "observation", "workspace": "thread_id"},
        "entity_embeddings": {"content": "description", "workspace": "workspace_id"},
    }

    schema = SCHEMA_MAP.get(
        table, {"content": "content", "workspace": "metadata->>'workspace_id'"}
    )
    content_col = schema["content"]
    workspace_col = schema["workspace"]

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
    workspace_id: str, reasoning_chain_id: str, rejections: list[dict]
):
    """
    Persists rejected strategic paths to Supabase for future learning/audit.
    """
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            try:
                query = """
                    INSERT INTO council_rejections (
                        workspace_id, reasoning_chain_id, discarded_path, rejection_reason, metadata
                    )
                    VALUES (%s, %s, %s, %s, %s);
                """
                for rejection in rejections:
                    await cur.execute(
                        query,
                        (
                            workspace_id,
                            reasoning_chain_id,
                            rejection.get("path"),
                            rejection.get("reason"),
                            psycopg.types.json.Jsonb(rejection.get("metadata", {})),
                        ),
                    )
                await conn.commit()
            except Exception as e:
                await conn.rollback()
                logger.error(f"Failed to save council rejections: {e}")
                raise
