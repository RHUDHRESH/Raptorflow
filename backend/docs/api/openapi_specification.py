"""
OpenAPI 3.1 Specification for Raptorflow Backend API
Comprehensive API documentation with interactive examples and security schemas.
"""

openapi_spec = {
    "openapi": "3.1.0",
    "info": {
        "title": "Raptorflow Backend API",
        "description": "Enterprise-grade AI agent platform with advanced security and monitoring",
        "version": "1.0.0",
        "contact": {
            "name": "Raptorflow API Team",
            "email": "api@raptorflow.com",
            "url": "https://raptorflow.com"
        },
        "license": {
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT"
        }
    },
    "servers": [
        {
            "url": "https://api.raptorflow.com/v1",
            "description": "Production server"
        },
        {
            "url": "https://staging-api.raptorflow.com/v1",
            "description": "Staging server"
        },
        {
            "url": "http://localhost:8000/v1",
            "description": "Development server"
        }
    ],
    "security": [
        {
            "BearerAuth": [],
            "ApiKeyAuth": []
        },
        {
            "OAuth2": ["read", "write"]
        }
    ],
    "components": {
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "JWT token for authentication"
            },
            "ApiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key",
                "description": "API key for service-to-service authentication"
            },
            "OAuth2": {
                "type": "oauth2",
                "flows": {
                    "authorizationCode": {
                        "authorizationUrl": "https://auth.raptorflow.com/oauth/authorize",
                        "tokenUrl": "https://auth.raptorflow.com/oauth/token",
                        "scopes": {
                            "read": "Read access to resources",
                            "write": "Write access to resources",
                            "admin": "Administrative access"
                        }
                    }
                }
            }
        },
        "schemas": {
            "User": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "format": "uuid"},
                    "email": {"type": "string", "format": "email"},
                    "name": {"type": "string"},
                    "role": {"type": "string", "enum": ["user", "admin", "super_admin"]},
                    "workspace_id": {"type": "string", "format": "uuid"},
                    "created_at": {"type": "string", "format": "date-time"},
                    "updated_at": {"type": "string", "format": "date-time"},
                    "last_login": {"type": "string", "format": "date-time"},
                    "is_active": {"type": "boolean"},
                    "mfa_enabled": {"type": "boolean"}
                },
                "required": ["id", "email", "name", "role", "workspace_id"]
            },
            "Agent": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "format": "uuid"},
                    "name": {"type": "string"},
                    "type": {"type": "string", "enum": ["cognitive", "analytical", "creative", "technical"]},
                    "status": {"type": "string", "enum": ["active", "inactive", "training", "error"]},
                    "config": {"type": "object"},
                    "capabilities": {"type": "array", "items": {"type": "string"}},
                    "workspace_id": {"type": "string", "format": "uuid"},
                    "created_by": {"type": "string", "format": "uuid"},
                    "created_at": {"type": "string", "format": "date-time"},
                    "updated_at": {"type": "string", "format": "date-time"}
                },
                "required": ["id", "name", "type", "status", "workspace_id"]
            },
            "Workspace": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "format": "uuid"},
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "owner_id": {"type": "string", "format": "uuid"},
                    "settings": {"type": "object"},
                    "subscription_tier": {"type": "string", "enum": ["free", "pro", "enterprise"]},
                    "created_at": {"type": "string", "format": "date-time"},
                    "updated_at": {"type": "string", "format": "date-time"}
                },
                "required": ["id", "name", "owner_id", "subscription_tier"]
            },
            "ErrorResponse": {
                "type": "object",
                "properties": {
                    "error": {"type": "string"},
                    "message": {"type": "string"},
                    "details": {"type": "object"},
                    "timestamp": {"type": "string", "format": "date-time"},
                    "request_id": {"type": "string"}
                },
                "required": ["error", "message", "timestamp"]
            },
            "PaginatedResponse": {
                "type": "object",
                "properties": {
                    "data": {"type": "array"},
                    "pagination": {
                        "type": "object",
                        "properties": {
                            "page": {"type": "integer"},
                            "limit": {"type": "integer"},
                            "total": {"type": "integer"},
                            "total_pages": {"type": "integer"}
                        }
                    }
                }
            }
        },
        "responses": {
            "Unauthorized": {
                "description": "Unauthorized access",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                    }
                }
            },
            "Forbidden": {
                "description": "Access forbidden",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                    }
                }
            },
            "NotFound": {
                "description": "Resource not found",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                    }
                }
            },
            "RateLimitExceeded": {
                "description": "Rate limit exceeded",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                    }
                }
            }
        }
    },
    "paths": {
        "/auth/login": {
            "post": {
                "tags": ["Authentication"],
                "summary": "User login",
                "description": "Authenticate user and return access token",
                "requestBody": {
                    "required": true,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "email": {"type": "string", "format": "email"},
                                    "password": {"type": "string", "minLength": 8},
                                    "mfa_code": {"type": "string"}
                                },
                                "required": ["email", "password"]
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Login successful",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "access_token": {"type": "string"},
                                        "refresh_token": {"type": "string"},
                                        "token_type": {"type": "string"},
                                        "expires_in": {"type": "integer"},
                                        "user": {"$ref": "#/components/schemas/User"}
                                    }
                                }
                            }
                        }
                    },
                    "401": {"$ref": "#/components/responses/Unauthorized"}
                }
            }
        },
        "/users": {
            "get": {
                "tags": ["Users"],
                "summary": "List users",
                "description": "Get paginated list of users in workspace",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {"name": "page", "in": "query", "schema": {"type": "integer", "default": 1}},
                    {"name": "limit", "in": "query", "schema": {"type": "integer", "default": 20}},
                    {"name": "search", "in": "query", "schema": {"type": "string"}},
                    {"name": "role", "in": "query", "schema": {"type": "string", "enum": ["user", "admin"]}}
                ],
                "responses": {
                    "200": {
                        "description": "Users retrieved successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "allOf": [
                                        {"$ref": "#/components/schemas/PaginatedResponse"},
                                        {
                                            "type": "object",
                                            "properties": {
                                                "data": {
                                                    "type": "array",
                                                    "items": {"$ref": "#/components/schemas/User"}
                                                }
                                            }
                                        }
                                    ]
                                }
                            }
                        }
                    },
                    "401": {"$ref": "#/components/responses/Unauthorized"},
                    "403": {"$ref": "#/components/responses/Forbidden"}
                }
            },
            "post": {
                "tags": ["Users"],
                "summary": "Create user",
                "description": "Create new user in workspace",
                "security": [{"BearerAuth": []}],
                "requestBody": {
                    "required": true,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "email": {"type": "string", "format": "email"},
                                    "name": {"type": "string"},
                                    "password": {"type": "string", "minLength": 8},
                                    "role": {"type": "string", "enum": ["user", "admin"]}
                                },
                                "required": ["email", "name", "password"]
                            }
                        }
                    }
                },
                "responses": {
                    "201": {
                        "description": "User created successfully",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/User"}
                            }
                        }
                    },
                    "400": {"$ref": "#/components/responses/Unauthorized"},
                    "403": {"$ref": "#/components/responses/Forbidden"}
                }
            }
        },
        "/agents": {
            "get": {
                "tags": ["Agents"],
                "summary": "List agents",
                "description": "Get paginated list of agents in workspace",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {"name": "page", "in": "query", "schema": {"type": "integer", "default": 1}},
                    {"name": "limit", "in": "query", "schema": {"type": "integer", "default": 20}},
                    {"name": "type", "in": "query", "schema": {"type": "string", "enum": ["cognitive", "analytical", "creative", "technical"]}},
                    {"name": "status", "in": "query", "schema": {"type": "string", "enum": ["active", "inactive", "training"]}}
                ],
                "responses": {
                    "200": {
                        "description": "Agents retrieved successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "allOf": [
                                        {"$ref": "#/components/schemas/PaginatedResponse"},
                                        {
                                            "type": "object",
                                            "properties": {
                                                "data": {
                                                    "type": "array",
                                                    "items": {"$ref": "#/components/schemas/Agent"}
                                                }
                                            }
                                        }
                                    ]
                                }
                            }
                        }
                    }
                }
            },
            "post": {
                "tags": ["Agents"],
                "summary": "Create agent",
                "description": "Create new AI agent",
                "security": [{"BearerAuth": []}],
                "requestBody": {
                    "required": true,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "type": {"type": "string", "enum": ["cognitive", "analytical", "creative", "technical"]},
                                    "config": {"type": "object"},
                                    "capabilities": {"type": "array", "items": {"type": "string"}}
                                },
                                "required": ["name", "type"]
                            }
                        }
                    }
                },
                "responses": {
                    "201": {
                        "description": "Agent created successfully",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Agent"}
                            }
                        }
                    }
                }
            }
        },
        "/agents/{agent_id}/execute": {
            "post": {
                "tags": ["Agents"],
                "summary": "Execute agent task",
                "description": "Execute a task using the specified agent",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {"name": "agent_id", "in": "path", "required": True, "schema": {"type": "string", "format": "uuid"}}
                ],
                "requestBody": {
                    "required": true,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "task": {"type": "string"},
                                    "input_data": {"type": "object"},
                                    "parameters": {"type": "object"}
                                },
                                "required": ["task"]
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Task executed successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "task_id": {"type": "string"},
                                        "status": {"type": "string"},
                                        "result": {"type": "object"},
                                        "execution_time": {"type": "number"},
                                        "tokens_used": {"type": "integer"}
                                    }
                                }
                            }
                        }
                    },
                    "404": {"$ref": "#/components/responses/NotFound"}
                }
            }
        },
        "/workspaces": {
            "get": {
                "tags": ["Workspaces"],
                "summary": "List workspaces",
                "description": "Get workspaces accessible to current user",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {
                        "description": "Workspaces retrieved successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/Workspace"}
                                }
                            }
                        }
                    }
                }
            }
        },
        "/health": {
            "get": {
                "tags": ["Health"],
                "summary": "Health check",
                "description": "Check system health and status",
                "responses": {
                    "200": {
                        "description": "System healthy",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {"type": "string"},
                                        "timestamp": {"type": "string", "format": "date-time"},
                                        "version": {"type": "string"},
                                        "services": {"type": "object"},
                                        "metrics": {"type": "object"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "/security/audit": {
            "get": {
                "tags": ["Security"],
                "summary": "Get audit logs",
                "description": "Retrieve security audit logs",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {"name": "start_date", "in": "query", "schema": {"type": "string", "format": "date"}},
                    {"name": "end_date", "in": "query", "schema": {"type": "string", "format": "date"}},
                    {"name": "event_type", "in": "query", "schema": {"type": "string"}},
                    {"name": "user_id", "in": "query", "schema": {"type": "string"}}
                ],
                "responses": {
                    "200": {
                        "description": "Audit logs retrieved",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "logs": {"type": "array", "items": {"type": "object"}},
                                        "total": {"type": "integer"},
                                        "page": {"type": "integer"}
                                    }
                                }
                            }
                        }
                    },
                    "403": {"$ref": "#/components/responses/Forbidden"}
                }
            }
        }
    },
    "tags": [
        {
            "name": "Authentication",
            "description": "User authentication and authorization"
        },
        {
            "name": "Users",
            "description": "User management operations"
        },
        {
            "name": "Agents",
            "description": "AI agent management and execution"
        },
        {
            "name": "Workspaces",
            "description": "Workspace management"
        },
        {
            "name": "Security",
            "description": "Security and audit operations"
        },
        {
            "name": "Health",
            "description": "System health monitoring"
        }
    ]
}

# Export the specification
def get_openapi_spec():
    """Get the OpenAPI specification."""
    return openapi_spec

# Interactive examples
interactive_examples = {
    "authentication": {
        "login": {
            "description": "Login with email and password",
            "request": {
                "method": "POST",
                "url": "/auth/login",
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": {
                    "email": "user@example.com",
                    "password": "securepassword123"
                }
            },
            "response": {
                "status": 200,
                "body": {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "Bearer",
                    "expires_in": 3600,
                    "user": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "email": "user@example.com",
                        "name": "John Doe",
                        "role": "user"
                    }
                }
            }
        }
    },
    "agents": {
        "create_agent": {
            "description": "Create a new AI agent",
            "request": {
                "method": "POST",
                "url": "/agents",
                "headers": {
                    "Authorization": "Bearer YOUR_TOKEN_HERE",
                    "Content-Type": "application/json"
                },
                "body": {
                    "name": "Data Analysis Agent",
                    "type": "analytical",
                    "capabilities": ["data_analysis", "visualization", "reporting"]
                }
            }
        },
        "execute_agent": {
            "description": "Execute a task with an agent",
            "request": {
                "method": "POST",
                "url": "/agents/123e4567-e89b-12d3-a456-426614174000/execute",
                "headers": {
                    "Authorization": "Bearer YOUR_TOKEN_HERE",
                    "Content-Type": "application/json"
                },
                "body": {
                    "task": "Analyze sales data for Q4 2023",
                    "input_data": {
                        "data_source": "sales_database",
                        "time_period": "Q4_2023"
                    }
                }
            }
        }
    }
}

# Rate limiting information
rate_limiting = {
    "description": "API rate limiting is implemented using intelligent behavioral analysis",
    "limits": {
        "free_tier": {
            "requests_per_minute": 60,
            "requests_per_hour": 1000,
            "requests_per_day": 10000
        },
        "pro_tier": {
            "requests_per_minute": 120,
            "requests_per_hour": 2500,
            "requests_per_day": 50000
        },
        "enterprise_tier": {
            "requests_per_minute": 300,
            "requests_per_hour": 10000,
            "requests_per_day": 1000000
        }
    },
    "headers": {
        "X-RateLimit-Limit": "Total requests allowed in the time window",
        "X-RateLimit-Remaining": "Remaining requests in the current window",
        "X-RateLimit-Reset": "Time when the rate limit window resets (Unix timestamp)"
    }
}

# Security considerations
security_considerations = {
    "authentication": [
        "All API endpoints require authentication except /health and /auth/login",
        "JWT tokens are valid for 1 hour",
        "Refresh tokens are valid for 30 days",
        "MFA is required for admin operations"
    ],
    "authorization": [
        "Role-based access control (RBAC) is implemented",
        "Users can only access resources in their workspace",
        "Admin users have elevated privileges",
        "Super admin users can access all resources"
    ],
    "data_protection": [
        "All data is encrypted at rest and in transit",
        "PII is automatically detected and protected",
        "Audit logging is enabled for all operations",
        "Data retention policies are enforced automatically"
    ],
    "rate_limiting": [
        "Intelligent rate limiting based on user behavior",
        "Automatic blocking of suspicious activity",
        "Custom rate limits for different subscription tiers",
        "Real-time threat detection and response"
    ]
}

# API versioning
api_versioning = {
    "current_version": "v1",
    "versioning_strategy": "URL path versioning",
    "backward_compatibility": "Maintained for at least 12 months",
    "deprecation_policy": {
        "notification_period": "6 months",
        "deprecation_headers": ["X-API-Deprecation-Warning", "X-API-Sunset"],
        "migration_guides": "Provided for all breaking changes"
    },
    "supported_versions": ["v1"],
    "version_lifecycle": {
        "v1": {
            "status": "current",
            "released": "2024-01-01",
            "sunset": None,
            "deprecated": False
        }
    }
}
