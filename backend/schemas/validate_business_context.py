"""
Business Context Validator
Validates business context data against JSON schema
"""

import json
import jsonschema
from pathlib import Path
from typing import Dict, Any

SCHEMA_PATH = Path(__file__).parent / "business_context_schema.json"


class BusinessContextValidationError(Exception):
    """Custom exception for business context validation errors"""

    def __init__(self, message: str, errors: list):
        super().__init__(message)
        self.errors = errors
        self.message = f"{message}: {errors}"


def validate_business_context(data: Dict[str, Any]) -> None:
    """
    Validate business context data against schema

    Args:
        data: Business context data to validate

    Raises:
        BusinessContextValidationError: If validation fails
        FileNotFoundError: If schema file doesn't exist
    """
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Schema file not found at {SCHEMA_PATH}")

    with open(SCHEMA_PATH, "r") as f:
        schema = json.load(f)

    validator = jsonschema.Draft7Validator(schema)
    errors = list(validator.iter_errors(data))

    if errors:
        error_messages = [
            f"{error.message} at {'/'.join(map(str, error.path))}" for error in errors
        ]
        raise BusinessContextValidationError(
            "Business context validation failed", error_messages
        )


def validate_business_context_from_json(json_str: str) -> None:
    """
    Validate business context from JSON string

    Args:
        json_str: JSON string of business context data

    Raises:
        JSONDecodeError: If invalid JSON
        BusinessContextValidationError: If validation fails
    """
    data = json.loads(json_str)
    validate_business_context(data)
