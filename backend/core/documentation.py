import asyncio
import inspect
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from fastapi import APIRouter, FastAPI
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel

logger = logging.getLogger("raptorflow.docs")


class DocumentationType(Enum):
    """Types of documentation."""

    OPENAPI = "openapi"
    SWAGGER = "swagger"
    REDOC = "redoc"
    POSTMAN = "postman"
    MARKDOWN = "markdown"


@dataclass
class DocumentationConfig:
    """Documentation configuration."""

    title: str = "RaptorFlow API"
    description: str = (
        "Production-grade agentic platform for growth marketing automation"
    )
    version: str = "1.0.0"
    contact_name: str = "RaptorFlow Team"
    contact_email: str = "support@raptorflow.com"
    license_name: str = "MIT"
    license_url: str = "https://opensource.org/licenses/MIT"
    servers: List[Dict[str, str]] = field(default_factory=list)
    tags: List[Dict[str, str]] = field(default_factory=list)

    def __post_init__(self):
        if not self.servers:
            self.servers = [
                {"url": "http://localhost:8000", "description": "Development server"},
                {
                    "url": "https://api.raptorflow.com",
                    "description": "Production server",
                },
            ]

        if not self.tags:
            self.tags = [
                {
                    "name": "Authentication",
                    "description": "Authentication and authorization",
                },
                {"name": "Campaigns", "description": "Campaign management"},
                {"name": "Moves", "description": "Move execution"},
                {"name": "Analytics", "description": "Analytics and reporting"},
                {"name": "System", "description": "System health and monitoring"},
            ]


@dataclass
class EndpointDocumentation:
    """Endpoint documentation details."""

    path: str
    method: str
    summary: str
    description: str
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    request_body: Optional[Dict[str, Any]] = None
    responses: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    security: List[Dict[str, Any]] = field(default_factory=list)
    deprecated: bool = False
    examples: List[Dict[str, Any]] = field(default_factory=list)


class DocumentationManager:
    """
    Production-grade API documentation and OpenAPI specification management.
    """

    def __init__(self, app: FastAPI, config: DocumentationConfig = None):
        self.app = app
        self.config = config or DocumentationConfig()
        self.endpoint_docs: Dict[str, EndpointDocumentation] = {}
        self.custom_schemas: Dict[str, Any] = {}
        self.stats = {
            "endpoints_documented": 0,
            "schemas_generated": 0,
            "docs_generated": 0,
            "last_updated": None,
        }
        self._lock = asyncio.Lock()

    async def generate_openapi_spec(self) -> Dict[str, Any]:
        """Generate OpenAPI 3.0 specification."""
        try:
            # Generate base OpenAPI spec
            openapi_spec = get_openapi(
                title=self.config.title,
                version=self.config.version,
                description=self.config.description,
                routes=self.app.routes,
                servers=self.config.servers,
            )

            # Add custom metadata
            openapi_spec["info"]["contact"] = {
                "name": self.config.contact_name,
                "email": self.config.contact_email,
            }

            openapi_spec["info"]["license"] = {
                "name": self.config.license_name,
                "url": self.config.license_url,
            }

            # Add custom tags
            openapi_spec["tags"] = self.config.tags

            # Add security schemes
            openapi_spec["components"]["securitySchemes"] = {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                },
                "apiKeyAuth": {"type": "apiKey", "in": "header", "name": "X-API-Key"},
            }

            # Add global security
            openapi_spec["security"] = [{"bearerAuth": []}, {"apiKeyAuth": []}]

            # Enhance endpoint documentation
            await self._enhance_endpoint_docs(openapi_spec)

            # Update stats
            self.stats["schemas_generated"] += 1
            self.stats["last_updated"] = datetime.utcnow().isoformat()

            return openapi_spec

        except Exception as e:
            logger.error(f"Error generating OpenAPI spec: {e}")
            raise

    async def _enhance_endpoint_docs(self, openapi_spec: Dict[str, Any]):
        """Enhance endpoint documentation with custom details."""
        paths = openapi_spec.get("paths", {})

        for path, methods in paths.items():
            for method, endpoint_spec in methods.items():
                # Look for custom documentation
                doc_key = f"{method.upper()} {path}"

                if doc_key in self.endpoint_docs:
                    custom_doc = self.endpoint_docs[doc_key]

                    # Add summary and description
                    if custom_doc.summary:
                        endpoint_spec["summary"] = custom_doc.summary

                    if custom_doc.description:
                        endpoint_spec["description"] = custom_doc.description

                    # Add tags
                    if custom_doc.tags:
                        endpoint_spec["tags"] = custom_doc.tags

                    # Add examples
                    if custom_doc.examples:
                        endpoint_spec["examples"] = custom_doc.examples

                    # Add deprecation notice
                    if custom_doc.deprecated:
                        endpoint_spec["deprecated"] = True

                    # Enhance responses
                    if custom_doc.responses:
                        for status_code, response in custom_doc.responses.items():
                            if status_code not in endpoint_spec.get("responses", {}):
                                if "responses" not in endpoint_spec:
                                    endpoint_spec["responses"] = {}
                                endpoint_spec["responses"][status_code] = response

    async def add_endpoint_documentation(self, doc: EndpointDocumentation):
        """Add custom documentation for an endpoint."""
        doc_key = f"{doc.method.upper()} {doc.path}"
        self.endpoint_docs[doc_key] = doc

        self.stats["endpoints_documented"] += 1
        logger.info(f"Added documentation for {doc_key}")

    async def generate_swagger_ui(self) -> Dict[str, Any]:
        """Generate Swagger UI configuration."""
        openapi_spec = await self.generate_openapi_spec()

        return {
            "openapi": openapi_spec,
            "swagger_ui_config": {
                "deepLinking": True,
                "displayRequestDuration": True,
                "docExpansion": "none",
                "operationsSorter": "alpha",
                "filter": True,
                "showExtensions": True,
                "showCommonExtensions": True,
                "tryItOutEnabled": True,
            },
        }

    async def generate_redoc_config(self) -> Dict[str, Any]:
        """Generate ReDoc configuration."""
        openapi_spec = await self.generate_openapi_spec()

        return {
            "openapi": openapi_spec,
            "redoc_config": {
                "hideHostname": True,
                "expandResponses": "200",
                "hideDownloadButton": False,
                "hideLoading": False,
                "nativeScrollbars": False,
                "noAutoAuth": False,
                "pathInMiddlePanel": False,
                "hideSingleRequestSampleTab": False,
                "jsonSampleExpandLevel": 2,
            },
        }

    async def generate_postman_collection(self) -> Dict[str, Any]:
        """Generate Postman collection."""
        openapi_spec = await self.generate_openapi_spec()

        collection = {
            "info": {
                "name": self.config.title,
                "description": self.config.description,
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
            },
            "auth": {
                "type": "bearer",
                "bearer": [
                    {"key": "token", "value": "{{access_token}}", "type": "string"}
                ],
            },
            "variable": [
                {
                    "key": "base_url",
                    "value": (
                        self.config.servers[0]["url"]
                        if self.config.servers
                        else "http://localhost:8000"
                    ),
                },
                {"key": "access_token", "value": ""},
            ],
            "item": [],
        }

        # Convert OpenAPI paths to Postman items
        paths = openapi_spec.get("paths", {})

        for path, methods in paths.items():
            for method, endpoint_spec in methods.items():
                if method.lower() in ["get", "post", "put", "delete", "patch"]:
                    item = {
                        "name": endpoint_spec.get(
                            "summary", f"{method.upper()} {path}"
                        ),
                        "request": {
                            "method": method.upper(),
                            "header": [
                                {"key": "Content-Type", "value": "application/json"}
                            ],
                            "url": {
                                "raw": "{{base_url}}" + path,
                                "host": ["{{base_url}}"],
                                "path": (
                                    path.strip("/").split("/") if path != "/" else []
                                ),
                            },
                        },
                    }

                    # Add request body if present
                    if "requestBody" in endpoint_spec:
                        content = endpoint_spec["requestBody"].get("content", {})
                        if "application/json" in content:
                            schema = content["application/json"].get("schema", {})
                            item["request"]["body"] = {
                                "mode": "raw",
                                "raw": json.dumps(schema, indent=2),
                                "options": {"raw": {"language": "json"}},
                            }

                    # Add responses
                    if "responses" in endpoint_spec:
                        item["response"] = []
                        for status_code, response in endpoint_spec["responses"].items():
                            item["response"].append(
                                {
                                    "name": response.get(
                                        "description", f"Status {status_code}"
                                    ),
                                    "originalRequest": item["request"],
                                    "status": status_code,
                                    "code": int(status_code),
                                }
                            )

                    collection["item"].append(item)

        return collection

    async def generate_markdown_docs(self) -> str:
        """Generate Markdown documentation."""
        openapi_spec = await self.generate_openapi_spec()

        markdown = f"""# {self.config.title}

{self.config.description}

## Table of Contents

- [Authentication](#authentication)
- [Endpoints](#endpoints)
- [Data Models](#data-models)
- [Error Handling](#error-handling)

## Authentication

This API uses JWT Bearer tokens for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### Getting a Token

POST `/auth/login`
```json
{
  "email": "user@example.com",
  "password": "your-password"
}
```

## Endpoints

"""

        # Add endpoints
        paths = openapi_spec.get("paths", {})

        for path, methods in paths.items():
            for method, endpoint_spec in methods.items():
                if method.lower() in ["get", "post", "put", "delete", "patch"]:
                    markdown += f"""
### {method.upper()} {path}

{endpoint_spec.get('summary', '')}

{endpoint_spec.get('description', '')}

**Parameters:**
"""

                    # Add parameters
                    parameters = endpoint_spec.get("parameters", [])
                    if parameters:
                        for param in parameters:
                            param_name = param.get("name", "")
                            param_type = param.get("in", "")
                            param_required = param.get("required", False)
                            param_desc = param.get("description", "")
                            markdown += f"- `{param_name}` ({param_type}, {'required' if param_required else 'optional'}): {param_desc}\n"
                    else:
                        markdown += "- None\n"

                    # Add request body
                    if "requestBody" in endpoint_spec:
                        markdown += "\n**Request Body:**\n"
                        content = endpoint_spec["requestBody"].get("content", {})
                        if "application/json" in content:
                            schema = content["application/json"].get("schema", {})
                            markdown += (
                                "```json\n" + json.dumps(schema, indent=2) + "\n```\n"
                            )

                    # Add responses
                    if "responses" in endpoint_spec:
                        markdown += "\n**Responses:**\n"
                        for status_code, response in endpoint_spec["responses"].items():
                            response_desc = response.get("description", "")
                            markdown += f"- `{status_code}`: {response_desc}\n"

                    markdown += "\n---\n"

        # Add data models
        components = openapi_spec.get("components", {})
        schemas = components.get("schemas", {})

        if schemas:
            markdown += "\n## Data Models\n\n"

            for schema_name, schema in schemas.items():
                markdown += f"### {schema_name}\n\n"

                if "description" in schema:
                    markdown += f"{schema['description']}\n\n"

                if "properties" in schema:
                    markdown += "**Properties:**\n"
                    for prop_name, prop_schema in schema["properties"].items():
                        prop_type = prop_schema.get("type", "unknown")
                        prop_desc = prop_schema.get("description", "")
                        prop_required = prop_name in schema.get("required", [])
                        markdown += f"- `{prop_name}` ({prop_type}, {'required' if prop_required else 'optional'}): {prop_desc}\n"

                markdown += "\n---\n"

        # Add error handling
        markdown += """
## Error Handling

The API uses standard HTTP status codes and returns error details in the following format:

```json
{
  "error": true,
  "error_id": "uuid",
  "message": "Error description",
  "category": "error_category",
  "severity": "error_severity",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Common Error Codes

- `400` - Bad Request (validation errors)
- `401` - Unauthorized (authentication required)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (resource doesn't exist)
- `422` - Unprocessable Entity (validation failed)
- `500` - Internal Server Error (system error)
- `503` - Service Unavailable (system maintenance)

"""

        return markdown

    async def export_documentation(
        self, doc_type: DocumentationType
    ) -> Union[Dict[str, Any], str]:
        """Export documentation in specified format."""
        self.stats["docs_generated"] += 1

        if doc_type == DocumentationType.OPENAPI:
            return await self.generate_openapi_spec()
        elif doc_type == DocumentationType.SWAGGER:
            return await self.generate_swagger_ui()
        elif doc_type == DocumentationType.REDOC:
            return await self.generate_redoc_config()
        elif doc_type == DocumentationType.POSTMAN:
            return await self.generate_postman_collection()
        elif doc_type == DocumentationType.MARKDOWN:
            return await self.generate_markdown_docs()
        else:
            raise ValueError(f"Unsupported documentation type: {doc_type}")

    async def get_documentation_stats(self) -> Dict[str, Any]:
        """Get documentation statistics."""
        async with self._lock:
            return self.stats.copy()

    def add_custom_schema(self, name: str, schema: Dict[str, Any]):
        """Add custom schema definition."""
        self.custom_schemas[name] = schema
        self.stats["schemas_generated"] += 1
        logger.info(f"Added custom schema: {name}")


class DocumentationGenerator:
    """Utility for generating documentation from code."""

    @staticmethod
    def extract_endpoint_info(func) -> Dict[str, Any]:
        """Extract endpoint information from function."""
        info = {
            "name": func.__name__,
            "description": func.__doc__ or "",
            "parameters": [],
            "return_type": None,
        }

        # Extract function signature
        sig = inspect.signature(func)

        for param_name, param in sig.parameters.items():
            param_info = {
                "name": param_name,
                "type": (
                    str(param.annotation)
                    if param.annotation != inspect.Parameter.empty
                    else "unknown"
                ),
                "default": (
                    str(param.default)
                    if param.default != inspect.Parameter.empty
                    else None
                ),
                "required": param.default == inspect.Parameter.empty,
            }
            info["parameters"].append(param_info)

        # Extract return type
        if sig.return_annotation != inspect.Signature.empty:
            info["return_type"] = str(sig.return_annotation)

        return info

    @staticmethod
    def generate_schema_from_model(model_class: BaseModel) -> Dict[str, Any]:
        """Generate OpenAPI schema from Pydantic model."""
        return model_class.schema()


# Global documentation manager
_doc_manager: Optional[DocumentationManager] = None


def get_documentation_manager(app: FastAPI) -> DocumentationManager:
    """Get the global documentation manager instance."""
    global _doc_manager
    if _doc_manager is None:
        _doc_manager = DocumentationManager(app)
    return _doc_manager


def document_endpoint(
    path: str,
    method: str,
    summary: str,
    description: str,
    tags: List[str] = None,
    deprecated: bool = False,
):
    """Decorator for documenting endpoints."""

    def decorator(func):
        # Create endpoint documentation
        doc = EndpointDocumentation(
            path=path,
            method=method,
            summary=summary,
            description=description,
            tags=tags or [],
            deprecated=deprecated,
        )

        # Add to documentation manager (if available)
        if _doc_manager:
            asyncio.create_task(_doc_manager.add_endpoint_documentation(doc))

        return func

    return decorator


async def generate_api_docs(
    app: FastAPI, doc_type: DocumentationType = DocumentationType.OPENAPI
):
    """Generate API documentation."""
    doc_manager = get_documentation_manager(app)
    return await doc_manager.export_documentation(doc_type)


async def get_documentation_statistics(app: FastAPI) -> Dict[str, Any]:
    """Get documentation statistics."""
    doc_manager = get_documentation_manager(app)
    return await doc_manager.get_documentation_stats()
