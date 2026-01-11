"""
Data Schemas for Protocol Standardization

Standardized data schemas for cognitive engine communication.
Implements PROMPT 75 from STREAM_3_COGNITIVE_ENGINE.
"""

import asyncio
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Type, Union

import pydantic
from pydantic import BaseModel, Field, validator


class SchemaType(Enum):
    """Types of data schemas."""

    INPUT = "input"
    OUTPUT = "output"
    CONFIGURATION = "configuration"
    METADATA = "metadata"
    ERROR = "error"
    STATUS = "status"
    REQUEST = "request"
    RESPONSE = "response"
    EVENT = "event"


class SchemaFormat(Enum):
    """Schema serialization formats."""

    JSON = "json"
    YAML = "yaml"
    XML = "xml"
    PROTOBUF = "protobuf"
    AVRO = "avro"


class ValidationLevel(Enum):
    """Validation levels for schemas."""

    STRICT = "strict"
    MODERATE = "moderate"
    LENIENT = "lenient"
    DISABLED = "disabled"


@dataclass
class SchemaDefinition:
    """Definition of a data schema."""

    schema_id: str
    name: str
    description: str
    schema_type: SchemaType
    format: SchemaFormat
    version: str
    schema_dict: Dict[str, Any]
    validation_level: ValidationLevel
    required_fields: List[str]
    optional_fields: List[str]
    dependencies: Dict[str, List[str]]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize schema ID if not provided."""
        if not self.schema_id:
            self.schema_id = str(uuid.uuid4())


class SchemaValidator:
    """Validator for data schemas."""

    def __init__(self):
        """Initialize the schema validator."""
        self.schemas: Dict[str, SchemaDefinition] = {}
        self.pydantic_models: Dict[str, Type[BaseModel]] = {}
        self.validation_stats = {
            "total_validations": 0,
            "successful_validations": 0,
            "failed_validations": 0,
            "validations_by_schema": {},
            "validation_errors": [],
        }

    def register_schema(self, schema: SchemaDefinition) -> None:
        """Register a schema definition."""
        self.schemas[schema.schema_id] = schema

        # Create Pydantic model for validation
        try:
            pydantic_model = self._create_pydantic_model(schema)
            self.pydantic_models[schema.schema_id] = pydantic_model
        except Exception as e:
            print(f"Failed to create Pydantic model for schema {schema.schema_id}: {e}")

    def get_schema(self, schema_id: str) -> Optional[SchemaDefinition]:
        """Get a schema definition."""
        return self.schemas.get(schema_id)

    def validate_data(
        self,
        data: Dict[str, Any],
        schema_id: str,
        validation_level: ValidationLevel = None,
    ) -> Dict[str, Any]:
        """Validate data against a schema."""
        schema = self.schemas.get(schema_id)
        if not schema:
            return {
                "valid": False,
                "error": f"Schema {schema_id} not found",
                "errors": ["Schema not found"],
            }

        # Use specified validation level or schema default
        level = validation_level or schema.validation_level

        if level == ValidationLevel.DISABLED:
            return {"valid": True, "validation_level": "disabled", "errors": []}

        try:
            # Validate using Pydantic model
            pydantic_model = self.pydantic_models.get(schema_id)
            if pydantic_model:
                validation_result = self._validate_with_pydantic(
                    data, pydantic_model, level
                )
            else:
                validation_result = self._validate_manual(data, schema, level)

            # Update statistics
            self.validation_stats["total_validations"] += 1
            if validation_result["valid"]:
                self.validation_stats["successful_validations"] += 1
            else:
                self.validation_stats["failed_validations"] += 1
                self.validation_stats["validation_errors"].append(
                    {
                        "schema_id": schema_id,
                        "errors": validation_result["errors"],
                        "timestamp": datetime.now().isoformat(),
                    }
                )

            return validation_result

        except Exception as e:
            return {
                "valid": False,
                "error": f"Validation failed: {str(e)}",
                "errors": [str(e)],
            }

    def _create_pydantic_model(self, schema: SchemaDefinition) -> Type[BaseModel]:
        """Create a Pydantic model from schema definition."""
        fields = {}

        # Process schema fields
        for field_name, field_def in schema.schema_dict.get("properties", {}).items():
            field_type = field_def.get("type", "string")

            # Map JSON schema types to Python types
            python_type = self._map_json_type_to_python(field_type)

            # Handle required fields
            if field_name in schema.required_fields:
                fields[field_name] = (python_type, Field(...))
            else:
                fields[field_name] = (Optional[python_type], Field(None))

        # Create dynamic Pydantic model
        class_name = f"{schema.name.replace(' ', '')}Model"
        return type(class_name, (BaseModel,), fields)

    def _map_json_type_to_python(self, json_type: str) -> Type:
        """Map JSON schema type to Python type."""
        type_mapping = {
            "string": str,
            "integer": int,
            "number": float,
            "boolean": bool,
            "array": List,
            "object": Dict,
            "null": type(None),
        }

        return type_mapping.get(json_type, str)

    def _validate_with_pydantic(
        self,
        data: Dict[str, Any],
        pydantic_model: Type[BaseModel],
        level: ValidationLevel,
    ) -> Dict[str, Any]:
        """Validate data using Pydantic model."""
        try:
            if level == ValidationLevel.STRICT:
                # Strict validation
                instance = pydantic_model(**data)
            elif level == ValidationLevel.MODERATE:
                # Moderate validation - ignore extra fields
                instance = pydantic_model.parse_obj(data)
            elif level == ValidationLevel.LENIENT:
                # Lenient validation - coerce types
                instance = pydantic_model.parse_obj(data)
            else:
                instance = pydantic_model.parse_obj(data)

            return {
                "valid": True,
                "validation_level": level.value,
                "validated_data": instance.dict(),
                "errors": [],
            }

        except pydantic.ValidationError as e:
            return {
                "valid": False,
                "validation_level": level.value,
                "errors": [str(error) for error in e.errors()],
                "error_details": e.errors(),
            }
        except Exception as e:
            return {"valid": False, "validation_level": level.value, "errors": [str(e)]}

    def _validate_manual(
        self, data: Dict[str, Any], schema: SchemaDefinition, level: ValidationLevel
    ) -> Dict[str, Any]:
        """Manual validation without Pydantic."""
        errors = []

        # Check required fields
        if level in [ValidationLevel.STRICT, ValidationLevel.MODERATE]:
            for field in schema.required_fields:
                if field not in data:
                    errors.append(f"Required field '{field}' is missing")

        # Check field types
        if level == ValidationLevel.STRICT:
            for field_name, field_def in schema.schema_dict.get(
                "properties", {}
            ).items():
                if field_name in data:
                    expected_type = field_def.get("type")
                    actual_value = data[field_name]

                    if not self._check_type(actual_value, expected_type):
                        errors.append(f"Field '{field_name}' has incorrect type")

        # Check dependencies
        if schema.dependencies:
            for field, depends_on in schema.dependencies.items():
                if field in data and not any(dep in data for dep in depends_on):
                    errors.append(
                        f"Field '{field}' requires dependencies: {depends_on}"
                    )

        return {
            "valid": len(errors) == 0,
            "validation_level": level.value,
            "errors": errors,
        }

    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Check if value matches expected type."""
        type_checks = {
            "string": lambda v: isinstance(v, str),
            "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
            "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
            "boolean": lambda v: isinstance(v, bool),
            "array": lambda v: isinstance(v, list),
            "object": lambda v: isinstance(v, dict),
            "null": lambda v: v is None,
        }

        check_func = type_checks.get(expected_type)
        return check_func(value) if check_func else True

    def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation statistics."""
        return self.validation_stats

    def list_schemas(self, schema_type: SchemaType = None) -> List[SchemaDefinition]:
        """List registered schemas."""
        schemas = list(self.schemas.values())

        if schema_type:
            schemas = [s for s in schemas if s.schema_type == schema_type]

        return schemas

    def export_schema(
        self, schema_id: str, format: SchemaFormat = SchemaFormat.JSON
    ) -> str:
        """Export schema in specified format."""
        schema = self.schemas.get(schema_id)
        if not schema:
            raise ValueError(f"Schema {schema_id} not found")

        if format == SchemaFormat.JSON:
            return json.dumps(schema.schema_dict, indent=2)
        elif format == SchemaFormat.YAML:
            try:
                import yaml

                return yaml.dump(schema.schema_dict, default_flow_style=False)
            except ImportError:
                raise ImportError("PyYAML required for YAML export")
        else:
            raise ValueError(f"Format {format.value} not supported")

    def import_schema(
        self,
        schema_data: str,
        format: SchemaFormat = SchemaFormat.JSON,
        name: str = None,
        description: str = None,
    ) -> SchemaDefinition:
        """Import schema from data."""
        if format == SchemaFormat.JSON:
            schema_dict = json.loads(schema_data)
        elif format == SchemaFormat.YAML:
            try:
                import yaml

                schema_dict = yaml.safe_load(schema_data)
            except ImportError:
                raise ImportError("PyYAML required for YAML import")
        else:
            raise ValueError(f"Format {format.value} not supported")

        # Create schema definition
        schema = SchemaDefinition(
            schema_id=str(uuid.uuid4()),
            name=name or schema_dict.get("title", "Imported Schema"),
            description=description or schema_dict.get("description", ""),
            schema_type=SchemaType.INPUT,  # Default
            format=SchemaFormat.JSON,
            version="1.0",
            schema_dict=schema_dict,
            validation_level=ValidationLevel.MODERATE,
            required_fields=schema_dict.get("required", []),
            optional_fields=list(schema_dict.get("properties", {}).keys())
            - schema_dict.get("required", []),
            dependencies={},
        )

        # Register schema
        self.register_schema(schema)

        return schema


class SchemaRegistry:
    """Registry for managing multiple schemas."""

    def __init__(self):
        """Initialize the schema registry."""
        self.schemas: Dict[str, SchemaDefinition] = {}
        self.validators: Dict[str, SchemaValidator] = {}
        self.default_validator = SchemaValidator()

        # Schema relationships
        self.schema_relationships: Dict[str, List[str]] = {}

        # Setup default schemas
        self._setup_default_schemas()

    def register_schema(
        self, schema: SchemaDefinition, validator: SchemaValidator = None
    ) -> None:
        """Register a schema with optional validator."""
        self.schemas[schema.schema_id] = schema

        if validator:
            self.validators[schema.schema_id] = validator
        else:
            self.default_validator.register_schema(schema)

    def get_schema(self, schema_id: str) -> Optional[SchemaDefinition]:
        """Get a schema by ID."""
        return self.schemas.get(schema_id)

    def validate_data(
        self, data: Dict[str, Any], schema_id: str, validator: SchemaValidator = None
    ) -> Dict[str, Any]:
        """Validate data against a schema."""
        target_validator = (
            validator or self.validators.get(schema_id) or self.default_validator
        )
        return target_validator.validate_data(data, schema_id)

    def get_related_schemas(self, schema_id: str) -> List[SchemaDefinition]:
        """Get schemas related to a given schema."""
        related_ids = self.schema_relationships.get(schema_id, [])
        return [self.schemas[sid] for sid in related_ids if sid in self.schemas]

    def add_relationship(self, parent_schema_id: str, child_schema_id: str) -> None:
        """Add a relationship between schemas."""
        if parent_schema_id not in self.schema_relationships:
            self.schema_relationships[parent_schema_id] = []

        if child_schema_id not in self.schema_relationships[parent_schema_id]:
            self.schema_relationships[parent_schema_id].append(child_schema_id)

    def remove_relationship(self, parent_schema_id: str, child_schema_id: str) -> bool:
        """Remove a relationship between schemas."""
        if parent_schema_id in self.schema_relationships:
            if child_schema_id in self.schema_relationships[parent_schema_id]:
                self.schema_relationships[parent_schema_id].remove(child_schema_id)
                return True
        return False

    def find_schemas_by_type(self, schema_type: SchemaType) -> List[SchemaDefinition]:
        """Find schemas by type."""
        return [
            schema
            for schema in self.schemas.values()
            if schema.schema_type == schema_type
        ]

    def find_schemas_by_name(self, name_pattern: str) -> List[SchemaDefinition]:
        """Find schemas by name pattern."""
        return [
            schema
            for schema in self.schemas.values()
            if name_pattern.lower() in schema.name.lower()
        ]

    def get_schema_stats(self) -> Dict[str, Any]:
        """Get schema registry statistics."""
        return {
            "total_schemas": len(self.schemas),
            "schemas_by_type": {
                schema_type.value: len(self.find_schemas_by_type(schema_type))
                for schema_type in SchemaType
            },
            "relationships": len(self.schema_relationships),
            "validators": len(self.validators),
            "validation_stats": self.default_validator.get_validation_stats(),
        }

    def _setup_default_schemas(self) -> None:
        """Setup default cognitive engine schemas."""
        # Input schema
        input_schema = SchemaDefinition(
            schema_id="cognitive_input_v1",
            name="Cognitive Input Schema",
            description="Schema for cognitive engine input data",
            schema_type=SchemaType.INPUT,
            format=SchemaFormat.JSON,
            version="1.0",
            schema_dict={
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "context": {"type": "object"},
                    "metadata": {"type": "object"},
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"],
                    },
                    "session_id": {"type": "string"},
                },
                "required": ["text"],
            },
            validation_level=ValidationLevel.MODERATE,
            required_fields=["text"],
            optional_fields=["context", "metadata", "priority", "session_id"],
            dependencies={},
        )

        # Output schema
        output_schema = SchemaDefinition(
            schema_id="cognitive_output_v1",
            name="Cognitive Output Schema",
            description="Schema for cognitive engine output data",
            schema_type=SchemaType.OUTPUT,
            format=SchemaFormat.JSON,
            version="1.0",
            schema_dict={
                "type": "object",
                "properties": {
                    "result": {"type": "object"},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                    "metadata": {"type": "object"},
                    "processing_time_ms": {"type": "integer"},
                    "tokens_used": {"type": "integer"},
                    "cost_usd": {"type": "number"},
                },
                "required": ["result"],
            },
            validation_level=ValidationLevel.MODERATE,
            required_fields=["result"],
            optional_fields=[
                "confidence",
                "metadata",
                "processing_time_ms",
                "tokens_used",
                "cost_usd",
            ],
            dependencies={},
        )

        # Error schema
        error_schema = SchemaDefinition(
            schema_id="cognitive_error_v1",
            name="Cognitive Error Schema",
            description="Schema for cognitive engine error data",
            schema_type=SchemaType.ERROR,
            format=SchemaFormat.JSON,
            version="1.0",
            schema_dict={
                "type": "object",
                "properties": {
                    "error_id": {"type": "string"},
                    "error_type": {"type": "string"},
                    "message": {"type": "string"},
                    "severity": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical", "fatal"],
                    },
                    "context": {"type": "object"},
                    "stack_trace": {"type": "string"},
                    "timestamp": {"type": "string", "format": "date-time"},
                },
                "required": ["error_id", "error_type", "message"],
            },
            validation_level=ValidationLevel.STRICT,
            required_fields=["error_id", "error_type", "message"],
            optional_fields=["severity", "context", "stack_trace", "timestamp"],
            dependencies={},
        )

        # Register schemas
        self.register_schema(input_schema)
        self.register_schema(output_schema)
        self.register_schema(error_schema)

        # Add relationships
        self.add_relationship("cognitive_input_v1", "cognitive_output_v1")
        self.add_relationship("cognitive_input_v1", "cognitive_error_v1")


class SchemaTransformer:
    """Transformer for converting between schema formats."""

    def __init__(self):
        """Initialize the schema transformer."""
        self.transformations: Dict[str, Callable] = {}
        self._setup_transformations()

    def transform_data(
        self,
        data: Dict[str, Any],
        from_schema: str,
        to_schema: str,
        registry: SchemaRegistry,
    ) -> Dict[str, Any]:
        """Transform data from one schema to another."""
        transformation_key = f"{from_schema}_to_{to_schema}"

        if transformation_key in self.transformations:
            transform_func = self.transformations[transformation_key]
            return transform_func(data, registry)
        else:
            # Generic transformation
            return self._generic_transform(data, from_schema, to_schema, registry)

    def _generic_transform(
        self,
        data: Dict[str, Any],
        from_schema: str,
        to_schema: str,
        registry: SchemaRegistry,
    ) -> Dict[str, Any]:
        """Generic transformation between schemas."""
        from_schema_def = registry.get_schema(from_schema)
        to_schema_def = registry.get_schema(to_schema)

        if not from_schema_def or not to_schema_def:
            return data

        # Map common fields
        transformed = {}

        # Copy matching fields
        for field_name, field_value in data.items():
            if field_name in to_schema_def.schema_dict.get("properties", {}):
                transformed[field_name] = field_value

        return transformed

    def _setup_transformations(self) -> None:
        """Setup default transformations."""
        # Input to output transformation
        self.transformations["cognitive_input_v1_to_cognitive_output_v1"] = (
            self._transform_input_to_output
        )

        # Output to error transformation
        self.transformations["cognitive_output_v1_to_cognitive_error_v1"] = (
            self._transform_output_to_error
        )

    def _transform_input_to_output(
        self, data: Dict[str, Any], registry: SchemaRegistry
    ) -> Dict[str, Any]:
        """Transform input schema to output schema."""
        return {
            "result": {
                "processed_text": data.get("text", ""),
                "context": data.get("context", {}),
                "metadata": data.get("metadata", {}),
            },
            "confidence": 0.8,
            "metadata": data.get("metadata", {}),
            "processing_time_ms": 0,
            "tokens_used": 0,
            "cost_usd": 0.0,
        }

    def _transform_output_to_error(
        self, data: Dict[str, Any], registry: SchemaRegistry
    ) -> Dict[str, Any]:
        """Transform output schema to error schema."""
        return {
            "error_id": str(uuid.uuid4()),
            "error_type": "transformation_error",
            "message": "Failed to transform output to error",
            "severity": "medium",
            "context": data.get("metadata", {}),
            "stack_trace": "",
            "timestamp": datetime.now().isoformat(),
        }
