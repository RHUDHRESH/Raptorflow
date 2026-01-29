"""
Database tool for Raptorflow agents with workspace isolation.
"""

import hashlib
import json
import logging
import os
import time
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel

from ..base import RaptorflowTool, ToolError, ToolResult

logger = logging.getLogger(__name__)


class DatabaseQueryInput(BaseModel):
    """Input schema for database queries."""

    table: Literal[
        "foundations",
        "icp_profiles",
        "moves",
        "campaigns",
        "muse_assets",
        "blackbox_strategies",
        "daily_wins",
        "agent_executions",
    ]
    workspace_id: str
    filters: Optional[Dict[str, Any]] = None
    limit: int = 20
    offset: int = 0


class DatabaseTool(RaptorflowTool):
    """Enhanced database query tool with workspace isolation enforcement, connection pooling, and query optimization."""

    def __init__(self):
        super().__init__(
            name="database",
            description="Enhanced database tool with connection pooling and query optimization",
        )

        # Connection pooling and caching
        self.connection_pool = None
        self.query_cache = {}
        self.cache_ttl = 300  # 5 minutes cache TTL
        self.max_cache_size = 1000

        # Performance metrics
        self.query_metrics = {
            "total_queries": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "slow_queries": 0,
            "failed_queries": 0,
        }

        # Table schemas for validation
        self.table_schemas = {
            "foundations": [
                "id",
                "workspace_id",
                "company_name",
                "industry",
                "summary",
                "brand_voice",
                "onboarding_completed",
            ],
            "icp_profiles": [
                "id",
                "workspace_id",
                "name",
                "tagline",
                "is_primary",
                "demographics",
                "psychographics",
                "behaviors",
            ],
            "moves": [
                "id",
                "workspace_id",
                "name",
                "category",
                "status",
                "goal",
                "duration_days",
                "start_date",
                "end_date",
            ],
            "campaigns": [
                "id",
                "workspace_id",
                "name",
                "objective",
                "status",
                "goal",
                "duration_days",
                "start_date",
                "end_date",
            ],
            "muse_assets": [
                "id",
                "workspace_id",
                "title",
                "type",
                "content",
                "status",
                "created_at",
                "updated_at",
            ],
            "blackbox_strategies": [
                "id",
                "workspace_id",
                "name",
                "focus_area",
                "risk_level",
                "status",
                "created_at",
                "updated_at",
            ],
            "daily_wins": [
                "id",
                "workspace_id",
                "topic",
                "angle",
                "hook",
                "platform",
                "status",
                "generated_at",
            ],
            "agent_executions": [
                "id",
                "workspace_id",
                "request_type",
                "success",
                "tokens_used",
                "cost_usd",
                "created_at",
            ],
        }

    async def _arun(
        self,
        table: str,
        workspace_id: str,
        filters: Dict[str, Any] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> ToolResult:
        """Execute database query with workspace isolation, connection pooling, and query optimization."""
        start_time = time.time()
        self.query_metrics["total_queries"] += 1

        try:
            # Generate cache key
            cache_key = self._generate_cache_key(
                table, workspace_id, filters, limit, offset
            )

            # Check cache first
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                self.query_metrics["cache_hits"] += 1
                logger.debug(f"Database cache hit for query: {cache_key}")
                return ToolResult(success=True, data=cached_result, cached=True)

            self.query_metrics["cache_misses"] += 1

            # Validate table name
            if table not in self.table_schemas:
                self.query_metrics["failed_queries"] += 1
                return ToolResult(
                    success=False,
                    error=f"Invalid table: {table}. Valid tables: {list(self.table_schemas.keys())}",
                )

            # Validate workspace_id
            if not workspace_id:
                self.query_metrics["failed_queries"] += 1
                return ToolResult(success=False, error="workspace_id is required")

            # Set workspace context
            self.set_workspace_id(workspace_id)

            # Build and execute optimized query
            query_result = await self._build_optimized_query(
                table, workspace_id, filters, limit, offset
            )

            # Cache the result
            self._cache_result(cache_key, query_result)

            # Log performance metrics
            query_time = time.time() - start_time
            if query_time > 1.0:  # Slow query threshold
                self.query_metrics["slow_queries"] += 1
                logger.warning(
                    f"Slow database query detected: {cache_key} took {query_time:.2f}s"
                )

            logger.debug(
                f"Database query executed successfully: {cache_key} in {query_time:.2f}s"
            )

            return ToolResult(
                success=True,
                data=query_result,
                cached=False,
                execution_time=query_time,
                metrics=self.get_performance_metrics(),
            )

        except Exception as e:
            self.query_metrics["failed_queries"] += 1
            query_time = time.time() - start_time
            logger.error(f"Database query failed after {query_time:.2f}s: {e}")
            return ToolResult(
                success=False,
                error=str(e),
                execution_time=query_time,
                metrics=self.get_performance_metrics(),
            )

    async def _build_optimized_query(
        self,
        table: str,
        workspace_id: str,
        filters: Dict[str, Any] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Build and execute optimized database query with connection pooling."""
        try:
            # Try new database system first for optimal performance
            try:
                from core.database import get_database_service

                db_service = await get_database_service()
                if db_service:
                    # Use new database service
                    return await self._execute_new_database_query(
                        db_service, table, workspace_id, filters, limit, offset
                    )

            except ImportError:
                # Fall back to legacy connection pooling
                pass

            # Try legacy connection pooling as fallback
            try:
                from core.connections import get_db_pool

                db_pool = await get_db_pool()
                if db_pool._initialized:
                    # Use connection pool for optimal performance
                    return await self._execute_pooled_query(
                        db_pool, table, workspace_id, filters, limit, offset
                    )

            except ImportError:
                # Fall back to direct connection
                pass

            # Original Supabase implementation as fallback
            from supabase import Client, create_client

            # Initialize Supabase client with connection optimization
            supabase: Client = create_client(
                url=os.getenv("SUPABASE_URL"), key=os.getenv("SUPABASE_SERVICE_KEY")
            )

            # Validate workspace_id
            if not workspace_id or not workspace_id.strip():
                raise ToolError(self.name, "Invalid workspace_id: cannot be empty")

            # Build optimized query with proper indexing
            query = self._build_optimized_supabase_query(
                supabase, table, workspace_id, filters, limit, offset
            )

            # Execute query
            result = query.execute()

            if result.error:
                raise ToolError(
                    self.name, f"Database query failed: {result.error.message}"
                )

            # Verify all results have correct workspace_id (double-check isolation)
            for item in result.data:
                if item.get("workspace_id") != workspace_id:
                    logger.error(
                        f"Workspace isolation breach detected in {table}: {item}"
                    )
                    raise ToolError(self.name, "Workspace isolation violation detected")

            return {
                "data": result.data,
                "total_count": len(result.data),
                "limit": limit,
                "offset": offset,
                "table": table,
                "workspace_id": workspace_id,
                "filters_applied": filters or {},
                "query_method": "supabase_direct",
            }

        except ImportError:
            raise ToolError(
                self.name,
                "Neither connection pooling nor Supabase client available",
            )
        except Exception as e:
            logger.error(f"Database query error: {e}")
            raise ToolError(self.name, f"Database operation failed: {str(e)}")

    async def _execute_new_database_query(
        self,
        db_service,
        table: str,
        workspace_id: str,
        filters: Dict[str, Any],
        limit: int,
        offset: int,
    ) -> Dict[str, Any]:
        """Execute query using new database service."""
        try:
            # Use new database service for optimal performance
            connection = await db_service.get_connection()

            # Build optimized query
            query = f"SELECT * FROM {table} WHERE workspace_id = $1"
            params = [workspace_id]

            # Apply additional filters
            if filters:
                optimized_filters = self._optimize_filters(table, filters)
                for key, value in optimized_filters.items():
                    if key in self.table_schemas.get(table, []):
                        query += f" AND {key} = ${len(params) + 1}"
                        params.append(value)

            # Add pagination
            if limit > 100:  # Prevent overly large queries
                limit = 100
                logger.warning(f"Query limit reduced to {limit} for performance")

            query += f" LIMIT {limit} OFFSET {offset}"

            # Execute query
            results = await connection.fetch(query, *params)

            # Verify workspace isolation
            for item in results:
                if item.get("workspace_id") != workspace_id:
                    logger.error(
                        f"Workspace isolation breach detected in {table}: {item}"
                    )
                    raise ToolError(self.name, "Workspace isolation violation detected")

            # Release connection
            await db_service.release_connection(connection)

            return {
                "data": [dict(row) for row in results],
                "total_count": len(results),
                "limit": limit,
                "offset": offset,
                "table": table,
                "workspace_id": workspace_id,
                "filters_applied": filters or {},
                "query_method": "new_database_service",
            }

        except Exception as e:
            logger.error(f"New database service query error: {e}")
            raise ToolError(self.name, f"Database operation failed: {str(e)}")

    async def _execute_pooled_query(
        self,
        db_pool,
        table: str,
        workspace_id: str,
        filters: Dict[str, Any],
        limit: int,
        offset: int,
    ) -> Dict[str, Any]:
        """Execute query using connection pool for optimal performance."""
        # Build optimized SQL query
        query = f"SELECT * FROM {table} WHERE workspace_id = $1"
        params = [workspace_id]

        # Apply additional filters with proper indexing
        if filters:
            indexed_filters = self._optimize_filters(table, filters)
            for key, value in indexed_filters.items():
                if key in self.table_schemas.get(table, []):
                    query += f" AND {key} = ${len(params) + 1}"
                    params.append(value)

        # Add pagination with limit optimization
        if limit > 100:  # Prevent overly large queries
            limit = 100
            logger.warning(f"Query limit reduced to {limit} for performance")

        query += f" LIMIT {limit} OFFSET {offset}"

        # Execute with connection pool
        results = await db_pool.fetch(query, *params)

        # Verify workspace isolation
        for item in results:
            if item.get("workspace_id") != workspace_id:
                logger.error(f"Workspace isolation breach detected in {table}: {item}")
                raise ToolError(self.name, "Workspace isolation violation detected")

        return {
            "data": [dict(row) for row in results],
            "total_count": len(results),
            "limit": limit,
            "offset": offset,
            "table": table,
            "workspace_id": workspace_id,
            "filters_applied": filters or {},
            "query_method": "connection_pool",
        }

    def _optimize_filters(self, table: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize filters for better query performance."""
        # Reorder filters by index priority (common indexed columns first)
        index_priority = {
            "id": 1,
            "workspace_id": 2,
            "created_at": 3,
            "updated_at": 4,
            "status": 5,
            "name": 6,
            "type": 7,
        }

        optimized_filters = {}

        # Sort filters by index priority
        sorted_filters = sorted(
            filters.items(), key=lambda x: index_priority.get(x[0], 99)
        )

        for key, value in sorted_filters:
            if key in self.table_schemas.get(table, []):
                optimized_filters[key] = value

        return optimized_filters

    def _build_optimized_supabase_query(
        self,
        supabase,
        table: str,
        workspace_id: str,
        filters: Dict[str, Any],
        limit: int,
        offset: int,
    ):
        """Build optimized Supabase query."""
        # Build base query with workspace_id filter (always first for RLS)
        query = supabase.table(table).select("*").eq("workspace_id", workspace_id)

        # Apply optimized filters
        if filters:
            optimized_filters = self._optimize_filters(table, filters)
            for key, value in optimized_filters.items():
                query = query.eq(key, value)

        # Apply pagination with range optimization
        if limit > 100:  # Prevent overly large queries
            limit = 100
            logger.warning(f"Query limit reduced to {limit} for performance")

        query = query.range(offset, offset + limit - 1)

        return query

    def _generate_cache_key(
        self,
        table: str,
        workspace_id: str,
        filters: Dict[str, Any],
        limit: int,
        offset: int,
    ) -> str:
        """Generate cache key for query."""
        import hashlib

        # Create deterministic cache key
        key_data = {
            "table": table,
            "workspace_id": workspace_id,
            "filters": sorted(filters.items()) if filters else [],
            "limit": limit,
            "offset": offset,
        }

        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()

    def _get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get result from cache if valid."""
        if cache_key not in self.query_cache:
            return None

        cached = self.query_cache[cache_key]
        current_time = time.time()

        # Check if cache is still valid
        if current_time - cached["timestamp"] > self.cache_ttl:
            # Cache expired, remove it
            del self.query_cache[cache_key]
            return None

        return cached["data"]

    def _cache_result(self, cache_key: str, result: Dict[str, Any]):
        """Cache query result with TTL management."""
        current_time = time.time()

        # Add to cache
        self.query_cache[cache_key] = {"data": result, "timestamp": current_time}

        # Clean up old cache entries if cache is too large
        if len(self.query_cache) > self.max_cache_size:
            self._cleanup_cache()

    def _cleanup_cache(self):
        """Clean up expired cache entries."""
        current_time = time.time()
        expired_keys = []

        for key, cached in self.query_cache.items():
            if current_time - cached["timestamp"] > self.cache_ttl:
                expired_keys.append(key)

        for key in expired_keys:
            del self.query_cache[key]

        logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        total = self.query_metrics["total_queries"]
        if total == 0:
            total = 1  # Avoid division by zero

        return {
            **self.query_metrics,
            "cache_hit_rate": (self.query_metrics["cache_hits"] / total) * 100,
            "cache_miss_rate": (self.query_metrics["cache_misses"] / total) * 100,
            "failure_rate": (self.query_metrics["failed_queries"] / total) * 100,
            "slow_query_rate": (self.query_metrics["slow_queries"] / total) * 100,
        }

    def get_table_schema(self, table: str) -> Optional[List[str]]:
        """Get schema for a table."""
        return self.table_schemas.get(table)

    def validate_filters(self, table: str, filters: Dict[str, Any]) -> bool:
        """Validate filters against table schema."""
        schema = self.table_schemas.get(table, [])

        for key in filters.keys():
            if key not in schema:
                logger.warning(f"Invalid filter key '{key}' for table '{table}'")
                return False

        return True

    async def validate_workspace_access(self, workspace_id: str) -> bool:
        """Validate that the workspace exists and is accessible."""
        # In a real implementation, this would check the database
        # For now, assume any non-empty workspace_id is valid
        return bool(workspace_id and workspace_id.strip())

    def get_available_tables(self) -> List[str]:
        """Get list of available tables."""
        return list(self.table_schemas.keys())

    def explain_workspace_isolation(self) -> str:
        """Explain how workspace isolation works."""
        return """
        Workspace Isolation in DatabaseTool:

        1. Every query MUST include workspace_id parameter
        2. All data returned is filtered by workspace_id
        3. No cross-workspace data leakage possible
        4. RLS policies enforce isolation at database level

        This ensures users can only access their own data.
        """
