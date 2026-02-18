"""
Core type aliases.

These type aliases are used across the application layer to ensure consistency.
"""

from typing import Any, TypeVar

# Generic type variable for entities
T = TypeVar("T")

# Common type aliases
JSON = dict[str, Any]
JSONList = list[Any]
JSONValue = str | int | float | bool | None


# Pagination
class PageParams:
    """Parameters for paginated queries."""

    def __init__(self, limit: int = 50, offset: int = 0):
        self.limit = limit
        self.offset = offset


class PageResult[T]:
    """Result of a paginated query."""

    def __init__(self, items: list[T], total: int, limit: int, offset: int):
        self.items = items
        self.total = total
        self.limit = limit
        self.offset = offset
        self.has_more = offset + limit < total
