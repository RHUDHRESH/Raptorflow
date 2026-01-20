"""
Base repository class with workspace filtering
All repositories inherit from this to ensure workspace isolation
"""

import logging
import uuid
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Any, Dict, Generic, List, Optional, TypeVar

from backend.core.supabase_mgr import get_supabase_client
from backend.db.filters import Filter, build_query, workspace_filter
from backend.db.pagination import PaginatedResult, Pagination

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class BaseModel:
    """Base model for database entities"""

    id: str
    workspace_id: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class Repository(ABC, Generic[T]):
    """Base repository with workspace isolation"""

    def __init__(self, table_name: str):
        self.table_name = table_name
        # Get SupabaseClient singleton
        self._supabase_client = None

    def _get_supabase_client(self):
        """Get SupabaseClient singleton"""
        if self._supabase_client is None:
            self._supabase_client = get_supabase_client()
        return self._supabase_client

    @property
    def client(self):
        """Get Supabase client"""
        return self._get_supabase_client()

    async def get(self, id: str, workspace_id: str) -> Optional[T]:
        """Get single record by ID (workspace isolated)"""
        try:
            query = (
                self._get_supabase_client()
                .table(self.table_name)
                .select("*")
                .eq("id", id)
            )
            query = build_query(query, [workspace_filter(workspace_id)])

            result = query.single().execute()

            if result.data:
                return self._map_to_model(result.data)
            return None

        except Exception as e:
            logger.error(f"Error getting {self.table_name} {id}: {e}")
            return None

    async def list(
        self,
        workspace_id: str,
        filters: List[Filter] = None,
        pagination: Pagination = None,
        sort_by: str = None,
        sort_order: str = "asc",
    ) -> PaginatedResult[T]:
        """List records with filtering and pagination (workspace isolated)"""
        try:
            # Start with base query
            query = self._get_supabase_client().table(self.table_name).select("*")

            # Always apply workspace filter
            all_filters = [workspace_filter(workspace_id)]
            if filters:
                all_filters.extend(filters)

            query = build_query(query, all_filters)

            # Apply sorting
            if sort_by:
                if sort_order == "desc":
                    query = query.order(sort_by, desc=True)
                else:
                    query = query.order(sort_by)

            # Apply pagination
            if pagination:
                total_result = query.select("id", count="exact").execute()
                total = total_result.count or 0

                paginated_query = (
                    self._get_supabase_client().table(self.table_name).select("*")
                )
                paginated_query = build_query(paginated_query, all_filters)

                if sort_by:
                    if sort_order == "desc":
                        paginated_query = paginated_query.order(sort_by, desc=True)
                    else:
                        paginated_query = paginated_query.order(sort_by)

                result = paginated_query.range(
                    pagination.offset, pagination.offset + pagination.limit - 1
                ).execute()

                items = []
                if result.data:
                    for item in result.data:
                        items.append(self._map_to_model(item))

                total_pages = (total + pagination.page_size - 1) // pagination.page_size

                return PaginatedResult(
                    items=items,
                    total=total,
                    page=pagination.page,
                    page_size=pagination.page_size,
                    total_pages=total_pages,
                )
            else:
                # No pagination
                result = query.execute()
                items = []
                if result.data:
                    for item in result.data:
                        items.append(self._map_to_model(item))

                return PaginatedResult(
                    items=items,
                    total=len(items),
                    page=1,
                    page_size=len(items),
                    total_pages=1,
                )

        except Exception as e:
            logger.error(f"Error listing {self.table_name}: {e}")
            return PaginatedResult(
                items=[], total=0, page=1, page_size=20, total_pages=0
            )

    async def create(self, data: Dict[str, Any], workspace_id: str) -> Optional[T]:
        """Create new record (workspace isolated)"""
        try:
            # Ensure workspace_id is set
            data["workspace_id"] = workspace_id
            data["id"] = str(uuid.uuid4())

            result = (
                self._get_supabase_client()
                .table(self.table_name)
                .insert(data)
                .single()
                .execute()
            )

            if result.data:
                return self._map_to_model(result.data)
            return None

        except Exception as e:
            logger.error(f"Error creating {self.table_name}: {e}")
            return None

    async def update(
        self, id: str, data: Dict[str, Any], workspace_id: str
    ) -> Optional[T]:
        """Update record (workspace isolated)"""
        try:
            # Remove workspace_id from update data (shouldn't change)
            if "workspace_id" in data:
                del data["workspace_id"]
            if "id" in data:
                del data["id"]

            query = (
                self._get_supabase_client()
                .table(self.table_name)
                .update(data)
                .eq("id", id)
            )
            query = build_query(query, [workspace_filter(workspace_id)])

            result = query.single().execute()

            if result.data:
                return self._map_to_model(result.data)
            return None

        except Exception as e:
            logger.error(f"Error updating {self.table_name} {id}: {e}")
            return None

    async def delete(self, id: str, workspace_id: str) -> bool:
        """Delete record (workspace isolated)"""
        try:
            query = (
                self._get_supabase_client().table(self.table_name).delete().eq("id", id)
            )
            query = build_query(query, [workspace_filter(workspace_id)])

            result = query.execute()
            return result.data is not None

        except Exception as e:
            logger.error(f"Error deleting {self.table_name} {id}: {e}")
            return False

    async def count(self, workspace_id: str, filters: List[Filter] = None) -> int:
        """Count records (workspace isolated)"""
        try:
            query = (
                self._get_supabase_client()
                .table(self.table_name)
                .select("id", count="exact")
            )

            all_filters = [workspace_filter(workspace_id)]
            if filters:
                all_filters.extend(filters)

            query = build_query(query, all_filters)
            result = query.execute()

            return result.count or 0

        except Exception as e:
            logger.error(f"Error counting {self.table_name}: {e}")
            return 0

    @abstractmethod
    def _map_to_model(self, data: Dict[str, Any]) -> T:
        """Map database record to model instance"""
        pass

    def _ensure_workspace_filter(
        self, filters: List[Filter], workspace_id: str
    ) -> List[Filter]:
        """Ensure workspace filter is always applied"""
        if not any(f.field == "workspace_id" for f in filters):
            return [workspace_filter(workspace_id)] + filters
        return filters
