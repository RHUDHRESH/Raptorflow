import logging
from typing import Any, Dict, List, Optional

import psycopg

from backend.db import get_db_connection

logger = logging.getLogger("raptorflow.memory.knowledge_graph")


class KnowledgeGraphConnector:
    """
    SOTA Knowledge Graph Connector.
    Handles conceptual linking between agentic memories and business entities.
    Uses relational tables with JSONB metadata for flexible graph schema.
    """

    async def add_concept(
        self,
        workspace_id: str,
        name: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Adds a concept node to the knowledge graph."""
        async with get_db_connection() as conn:
            async with conn.cursor() as cur:
                query = """
                    INSERT INTO knowledge_concepts (workspace_id, name, description, metadata)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (workspace_id, name) DO UPDATE
                    SET description = EXCLUDED.description, metadata = knowledge_concepts.metadata || EXCLUDED.metadata
                    RETURNING id;
                """
                await cur.execute(
                    query,
                    (
                        workspace_id,
                        name,
                        description,
                        psycopg.types.json.Jsonb(metadata or {}),
                    ),
                )
                result = await cur.fetchone()
                await conn.commit()
                return result[0]

    async def link_concepts(
        self,
        workspace_id: str,
        source_id: str,
        target_id: str,
        relation: str,
        weight: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Creates a directed edge between two concept nodes."""
        async with get_db_connection() as conn:
            async with conn.cursor() as cur:
                query = """
                    INSERT INTO knowledge_links (workspace_id, source_id, target_id, relation, weight, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (source_id, target_id, relation) DO UPDATE
                    SET weight = EXCLUDED.weight, metadata = knowledge_links.metadata || EXCLUDED.metadata;
                """
                await cur.execute(
                    query,
                    (
                        workspace_id,
                        source_id,
                        target_id,
                        relation,
                        weight,
                        psycopg.types.json.Jsonb(metadata or {}),
                    ),
                )
                await conn.commit()
                return True

    async def get_related_concepts(
        self, concept_id: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Retrieves related concepts for a given node."""
        async with get_db_connection() as conn:
            async with conn.cursor() as cur:
                query = """
                    SELECT c.id, c.name, l.relation, l.weight
                    FROM knowledge_concepts c
                    JOIN knowledge_links l ON c.id = l.target_id
                    WHERE l.source_id = %s
                    ORDER BY l.weight DESC
                    LIMIT %s;
                """
                await cur.execute(query, (concept_id, limit))
                results = await cur.fetchall()
                return [
                    {"id": r[0], "name": r[1], "relation": r[2], "weight": r[3]}
                    for r in results
                ]
