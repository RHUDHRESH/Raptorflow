"""
Pagination utilities for database queries
"""

from dataclasses import dataclass
from typing import Generic, List, Optional, TypeVar

T = TypeVar("T")


@dataclass
class Pagination:
    """Pagination parameters"""

    page: int = 1
    page_size: int = 20
    sort_by: Optional[str] = None
    sort_order: str = "asc"  # asc or desc

    def __post_init__(self):
        if self.page < 1:
            self.page = 1
        if self.page_size < 1:
            self.page_size = 20
        if self.page_size > 100:
            self.page_size = 100
        if self.sort_order not in ["asc", "desc"]:
            self.sort_order = "asc"

    @property
    def offset(self) -> int:
        """Calculate offset for database query"""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """Get limit for database query"""
        return self.page_size


@dataclass
class PaginatedResult(Generic[T]):
    """Result of paginated query"""

    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int

    @property
    def has_next(self) -> bool:
        """Check if there's a next page"""
        return self.page < self.total_pages

    @property
    def has_previous(self) -> bool:
        """Check if there's a previous page"""
        return self.page > 1

    @property
    def next_page(self) -> Optional[int]:
        """Get next page number"""
        return self.page + 1 if self.has_next else None

    @property
    def previous_page(self) -> Optional[int]:
        """Get previous page number"""
        return self.page - 1 if self.has_previous else None
