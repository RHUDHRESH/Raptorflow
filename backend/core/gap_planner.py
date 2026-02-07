from __future__ import annotations

from typing import Dict, Iterable, List, Tuple

from models.dossier_schema import DEFAULT_DOSSIER_SCHEMA, DossierSchema


def _is_missing_value(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, (list, tuple, set, dict)):
        return len(value) == 0
    return False


def _iter_schema_fields(schema: DossierSchema):
    for field in schema.fields:
        if field.required:
            yield field


def evaluate_dossier_gaps(
    data: Dict[str, object],
    schema: DossierSchema = DEFAULT_DOSSIER_SCHEMA,
) -> Tuple[List[str], List[str], Dict[str, str]]:
    """
    Compare dossier data to schema and return missing fields and search queries.
    Returns (missing_fields, suggested_queries, gap_notes)
    """
    missing_fields: List[str] = []
    suggested_queries: List[str] = []
    gap_notes: Dict[str, str] = {}

    for field in _iter_schema_fields(schema):
        value = data.get(field.name)
        if _is_missing_value(value):
            missing_fields.append(field.name)
            gap_notes[field.name] = field.description
            if field.query_hints:
                suggested_queries.extend(field.query_hints)

    return missing_fields, sorted(set(suggested_queries)), gap_notes


def build_gap_queries(
    company_name: str,
    missing_fields: Iterable[str],
    gap_notes: Dict[str, str],
    schema: DossierSchema = DEFAULT_DOSSIER_SCHEMA,
) -> List[str]:
    field_map = {field.name: field for field in schema.fields}
    queries: List[str] = []
    for field_name in missing_fields:
        field = field_map.get(field_name)
        if not field:
            continue
        if field.query_hints:
            queries.extend([f"{company_name} {hint}" for hint in field.query_hints])
        else:
            description = gap_notes.get(field_name) or field.description
            queries.append(f"{company_name} {description}")

    return sorted(set(queries))
