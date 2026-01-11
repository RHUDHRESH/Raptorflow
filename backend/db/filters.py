"""
Query filters for database operations
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, List, Optional


class FilterOperator(Enum):
    """Filter operators"""

    EQ = "eq"
    NEQ = "neq"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    LIKE = "like"
    ILIKE = "ilike"
    IN = "in"
    NOT_IN = "not_in"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"


@dataclass
class Filter:
    """Single filter condition"""

    field: str
    operator: FilterOperator
    value: Any

    def __post_init__(self):
        if isinstance(self.operator, str):
            self.operator = FilterOperator(self.operator)


def build_query(query, filters: List[Filter]) -> Any:
    """Apply filters to Supabase query"""
    for filter_obj in filters:
        field = filter_obj.field
        operator = filter_obj.operator
        value = filter_obj.value

        if operator == FilterOperator.EQ:
            query = query.eq(field, value)
        elif operator == FilterOperator.NEQ:
            query = query.neq(field, value)
        elif operator == FilterOperator.GT:
            query = query.gt(field, value)
        elif operator == FilterOperator.GTE:
            query = query.gte(field, value)
        elif operator == FilterOperator.LT:
            query = query.lt(field, value)
        elif operator == FilterOperator.LTE:
            query = query.lte(field, value)
        elif operator == FilterOperator.LIKE:
            query = query.like(field, value)
        elif operator == FilterOperator.ILIKE:
            query = query.ilike(field, value)
        elif operator == FilterOperator.IN:
            query = query.in_(field, value)
        elif operator == FilterOperator.NOT_IN:
            query = query.not_in(field, value)
        elif operator == FilterOperator.IS_NULL:
            query = query.is_(field, None)
        elif operator == FilterOperator.IS_NOT_NULL:
            query = query.not_is_(field, None)

    return query


# Common filter builders
def workspace_filter(workspace_id: str) -> Filter:
    """Create workspace filter"""
    return Filter("workspace_id", FilterOperator.EQ, workspace_id)


def date_range_filter(field: str, start_date: str, end_date: str) -> List[Filter]:
    """Create date range filter"""
    return [
        Filter(field, FilterOperator.GTE, start_date),
        Filter(field, FilterOperator.LTE, end_date),
    ]


def text_search_filter(field: str, search_term: str) -> Filter:
    """Create text search filter"""
    return Filter(field, FilterOperator.ILIKE, f"%{search_term}%")
