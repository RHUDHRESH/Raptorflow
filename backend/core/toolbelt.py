import os
import logging
import json
import psycopg
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, ValidationError

# Setup Industrial Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("raptorflow.toolbelt")

class ToolResult(BaseModel):
    success: bool
    data: Any = None
    error: Optional[str] = None
    latency_ms: float = 0.0

class Toolbelt:
    """
    The Shared Toolbelt (T01-T44). 
    Deterministic functions for Agents to interact with the world.
    """
    
    def __init__(self, db_uri: str):
        self.db_uri = db_uri

    async def _execute_query(self, query: str, params: tuple, fetch: bool = True):
        start_time = datetime.now()
        try:
            async with await psycopg.AsyncConnection.connect(self.db_uri) as conn:
                async with conn.cursor() as cur:
                    await cur.execute(query, params)
                    if fetch:
                        data = await cur.fetchall()
                    else:
                        await conn.commit()
                        data = True
                    
                    latency = (datetime.now() - start_time).total_seconds() * 1000
                    return ToolResult(success=True, data=data, latency_ms=latency)
        except Exception as e:
            logger.error(f"Database Error: {str(e)} | Query: {query}")
            return ToolResult(success=False, error=str(e))

    # --- T01: GetWorkspaceContext ---
    async def get_workspace_context(self, workspace_id: str) -> ToolResult:
        query = "SELECT brand_profile, settings, plan_limits FROM workspaces WHERE id = %s"
        return await self._execute_query(query, (workspace_id,))

    # --- T02: GetProjectContext ---
    async def get_project_context(self, project_id: str, workspace_id: str) -> ToolResult:
        query = """
            SELECT p.name, p.brand_voice, 
                   (SELECT json_agg(i) FROM icps i WHERE i.project_id = p.id) as icps
            FROM projects p 
            WHERE p.id = %s AND p.workspace_id = %s
        """
        return await self._execute_query(query, (project_id, workspace_id))

    # --- T20: CreateAsset ---
    async def create_asset(self, workspace_id: str, asset_data: Dict) -> ToolResult:
        query = """
            INSERT INTO assets (workspace_id, project_id, type, title, status, content, metadata)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        params = (
            workspace_id,
            asset_data.get('project_id'),
            asset_data['type'],
            asset_data['title'],
            'draft',
            asset_data['content'],
            json.dumps(asset_data.get('metadata', {}))
        )
        return await self._execute_query(query, params, fetch=True)

    # --- T10: ListSkills ---
    async def list_skills(self, workspace_id: str) -> ToolResult:
        query = "SELECT id, name, description, category FROM skills WHERE workspace_id = %s OR type = 'system'"
        return await self._execute_query(query, (workspace_id,))

    # --- T43: CostGovernor ---
    async def check_cost_limit(self, workspace_id: str, estimated_cost: float) -> ToolResult:
        query = "SELECT current_spend, monthly_budget FROM billing WHERE workspace_id = %s"
        res = await self._execute_query(query, (workspace_id,))
        if not res.success: return res
        
        spend, budget = res.data[0]
        if spend + estimated_cost > budget:
            return ToolResult(success=False, error="Budget exceeded", data={"spend": spend, "budget": budget})
        return ToolResult(success=True, data={"allowed": True})

    # --- T30: CanvasSerialize ---
    async def save_canvas_state(self, asset_id: str, canvas_json: str) -> ToolResult:
        query = "UPDATE assets SET canvas_state = %s WHERE id = %s"
        return await self._execute_query(query, (canvas_json, asset_id), fetch=False)
