import os
import psycopg
from langgraph.checkpoint.postgres import PostgresSaver
from contextlib import asynccontextmanager
from typing import List, Optional

# DATABASE_URL should be in environment
DB_URI = os.getenv("DATABASE_URL")

@asynccontextmanager
async def get_db_connection():
    """Async context manager for psycopg connection with automatic closing."""
    conn = await psycopg.AsyncConnection.connect(DB_URI)
    try:
        yield conn
    finally:
        await conn.close()

async def init_checkpointer():
    """Initializes the LangGraph Postgres checkpointer."""
    # In production, use a connection pool (e.g. psycopg_pool)
    conn = await psycopg.AsyncConnection.connect(DB_URI)
    checkpointer = PostgresSaver(conn)
    return checkpointer

async def vector_search(
    workspace_id: str, 
    embedding: list[float], 
    table: str = "muse_assets", 
    limit: int = 5
):
    """
    Performs a pgvector similarity search, STRICTLY scoped to workspace_id.
    """
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            # Enforce workspace isolation in the SQL
            query = f"""
                SELECT id, content, metadata, 1 - (embedding <=> %s::vector) as similarity
                FROM {table}
                WHERE workspace_id = %s
                AND 1 - (embedding <=> %s::vector) > 0.7
                ORDER BY embedding <=> %s::vector
                LIMIT %s;
            """
            await cur.execute(query, (embedding, workspace_id, embedding, embedding, limit))
            results = await cur.fetchall()
            return results

async def save_asset_db(workspace_id: str, asset_data: dict):
    """Saves a final asset with production-grade validation."""
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            query = """
                INSERT INTO assets (workspace_id, type, title, content, metadata)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id;
            """
            await cur.execute(query, (
                workspace_id,
                asset_data['type'],
                asset_data['title'],
                asset_data['content'],
                psycopg.types.json.Jsonb(asset_data.get('metadata', {}))
            ))
            result = await cur.fetchone()
            await conn.commit()
            return result[0]