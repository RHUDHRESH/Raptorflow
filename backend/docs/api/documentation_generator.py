"""
API Documentation Generator and Interactive Examples
Provides comprehensive API documentation with interactive examples and tutorials.
"""

import json
from typing import Dict, Any, List
from .openapi_specification import get_openapi_spec, interactive_examples, rate_limiting, security_considerations, api_versioning


class APIDocumentationGenerator:
    """Generate comprehensive API documentation."""
    
    def __init__(self):
        self.openapi_spec = get_openapi_spec()
        self.examples = interactive_examples
        self.rate_limiting = rate_limiting
        self.security = security_considerations
        self.versioning = api_versioning
    
    def generate_documentation(self) -> Dict[str, Any]:
        """Generate complete API documentation."""
        return {
            "openapi": self.openapi_spec,
            "interactive_examples": self.examples,
            "rate_limiting": self.rate_limiting,
            "security_considerations": self.security,
            "api_versioning": self.versioning,
            "tutorials": self._generate_tutorials(),
            "best_practices": self._generate_best_practices(),
            "troubleshooting": self._generate_troubleshooting(),
        }
    
    def _generate_tutorials(self) -> Dict[str, Any]:
        """Generate API tutorials."""
        return {
            "getting_started": {
                "title": "Getting Started with Raptorflow API",
                "description": "Learn the basics of using the Raptorflow API",
                "steps": [
                    {
                        "step": 1,
                        "title": "Get API Credentials",
                        "description": "Sign up for an account and get your API keys",
                        "code": {
                            "curl": "curl -X POST https://api.raptorflow.com/v1/auth/login \\",
                            "python": "import requests\nfrom raptorflow import RaptorflowClient\n\nclient = RaptorflowClient(api_key='your_api_key')"
                        }
                    },
                    {
                        "step": 2,
                        "title": "Authenticate",
                        "description": "Login to get your access token",
                        "code": {
                            "curl": "curl -X POST https://api.raptorflow.com/v1/auth/login \\",
                            "python": "response = client.auth.login(\n    email='user@example.com',\n    password='your_password'\n)"
                        }
                    },
                    {
                        "step": 3,
                        "title": "Create Your First Agent",
                        "description": "Create an AI agent to perform tasks",
                        "code": {
                            "curl": "curl -X POST https://api.raptorflow.com/v1/agents \\",
                            "python": "agent = client.agents.create(\n    name='My First Agent',\n    type='analytical',\n    capabilities=['data_analysis']\n)"
                        }
                    },
                    {
                        "step": 4,
                        "title": "Execute a Task",
                        "description": "Run a task using your agent",
                        "code": {
                            "curl": "curl -X POST https://api.raptorflow.com/v1/agents/{agent_id}/execute \\",
                            "python": "result = client.agents.execute(\n    agent_id=agent.id,\n    task='Analyze this dataset',\n    input_data={'data': dataset}\n)"
                        }
                    }
                ]
            },
            "agent_management": {
                "title": "Agent Management Guide",
                "description": "Learn to create, configure, and manage AI agents",
                "topics": [
                    {
                        "title": "Creating Different Agent Types",
                        "description": "Understand the different types of agents available",
                        "examples": [
                            {
                                "type": "Cognitive Agent",
                                "description": "For reasoning and decision-making tasks",
                                "config": {
                                    "name": "Decision Maker",
                                    "type": "cognitive",
                                    "capabilities": ["reasoning", "decision_making", "analysis"]
                                }
                            },
                            {
                                "type": "Analytical Agent",
                                "description": "For data analysis and insights",
                                "config": {
                                    "name": "Data Analyst",
                                    "type": "analytical",
                                    "capabilities": ["data_analysis", "statistics", "visualization"]
                                }
                            }
                        ]
                    }
                ]
            }
        }
    
    def _generate_best_practices(self) -> Dict[str, Any]:
        """Generate API best practices."""
        return {
            "authentication": {
                "title": "Authentication Best Practices",
                "practices": [
                    "Always use HTTPS for API requests",
                    "Store API keys securely, never in client-side code",
                    "Use short-lived access tokens with refresh tokens",
                    "Implement proper token refresh logic",
                    "Enable MFA for admin accounts"
                ]
            },
            "error_handling": {
                "title": "Error Handling Best Practices",
                "practices": [
                    "Always check HTTP status codes",
                    "Parse error responses for detailed information",
                    "Implement exponential backoff for retries",
                    "Handle rate limiting gracefully",
                    "Log errors for debugging purposes"
                ]
            },
            "performance": {
                "title": "Performance Best Practices",
                "practices": [
                    "Use pagination for large datasets",
                    "Cache frequently accessed data",
                    "Batch requests when possible",
                    "Use appropriate HTTP methods",
                    "Optimize payload sizes"
                ]
            },
            "security": {
                "title": "Security Best Practices",
                "practices": [
                    "Validate all input data",
                    "Use principle of least privilege",
                    "Implement proper access controls",
                    "Monitor API usage for anomalies",
                    "Keep dependencies updated"
                ]
            }
        }
    
    def _generate_troubleshooting(self) -> Dict[str, Any]:
        """Generate troubleshooting guide."""
        return {
            "common_issues": [
                {
                    "issue": "401 Unauthorized",
                    "causes": ["Invalid token", "Expired token", "Missing token"],
                    "solutions": [
                        "Check your access token is valid",
                        "Refresh your token if expired",
                        "Include Authorization header"
                    ]
                },
                {
                    "issue": "429 Rate Limit Exceeded",
                    "causes": ["Too many requests", "Exceeded daily limit"],
                    "solutions": [
                        "Implement rate limiting in your client",
                        "Use exponential backoff",
                        "Upgrade your subscription tier"
                    ]
                },
                {
                    "issue": "500 Internal Server Error",
                    "causes": ["Server error", "Database issue", "Service unavailable"],
                    "solutions": [
                        "Retry the request after a delay",
                        "Check system status page",
                        "Contact support if issue persists"
                    ]
                }
            ],
            "debugging_tips": [
                "Use request IDs for troubleshooting",
                "Check response headers for additional information",
                "Enable debug logging in development",
                "Use API monitoring tools",
                "Test with small datasets first"
            ]
        }
    
    def export_openapi_json(self) -> str:
        """Export OpenAPI specification as JSON."""
        return json.dumps(self.openapi_spec, indent=2)
    
    def export_postman_collection(self) -> Dict[str, Any]:
        """Export Postman collection."""
        collection = {
            "info": {
                "name": "Raptorflow API",
                "description": "Raptorflow Backend API Collection",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "auth": {
                "type": "bearer",
                "bearer": [
                    {
                        "key": "token",
                        "value": "{{access_token}}",
                        "type": "string"
                    }
                ]
            },
            "variable": [
                {
                    "key": "base_url",
                    "value": "https://api.raptorflow.com/v1"
                },
                {
                    "key": "access_token",
                    "value": ""
                }
            ],
            "item": []
        }
        
        # Add endpoints from OpenAPI spec
        for path, methods in self.openapi_spec["paths"].items():
            for method, details in methods.items():
                if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                    item = {
                        "name": details.get("summary", f"{method.upper()} {path}"),
                        "request": {
                            "method": method.upper(),
                            "header": [
                                {
                                    "key": "Content-Type",
                                    "value": "application/json"
                                }
                            ],
                            "url": {
                                "raw": "{{base_url}}" + path,
                                "host": ["{{base_url}}"],
                                "path": path.strip("/").split("/")
                            }
                        }
                    }
                    
                    # Add request body if present
                    if "requestBody" in details:
                        item["request"]["body"] = {
                            "mode": "raw",
                            "raw": json.dumps(
                                details["requestBody"]["content"]["application/json"]["schema"],
                                indent=2
                            )
                        }
                    
                    collection["item"].append(item)
        
        return collection


# Documentation endpoints for FastAPI
def setup_documentation_routes(app):
    """Setup documentation routes for FastAPI app."""
    
    @app.get("/docs/openapi.json")
    async def get_openapi_json():
        """Get OpenAPI specification as JSON."""
        generator = APIDocumentationGenerator()
        return generator.openapi_spec
    
    @app.get("/docs/postman")
    async def get_postman_collection():
        """Get Postman collection."""
        generator = APIDocumentationGenerator()
        return generator.export_postman_collection()
    
    @app.get("/docs/interactive")
    async def get_interactive_examples():
        """Get interactive examples."""
        generator = APIDocumentationGenerator()
        return generator.examples
    
    @app.get("/docs/tutorials")
    async def get_tutorials():
        """Get API tutorials."""
        generator = APIDocumentationGenerator()
        return generator._generate_tutorials()
    
    @app.get("/docs/best-practices")
    async def get_best_practices():
        """Get API best practices."""
        generator = APIDocumentationGenerator()
        return generator._generate_best_practices()
    
    @app.get("/docs/troubleshooting")
    async def get_troubleshooting():
        """Get troubleshooting guide."""
        generator = APIDocumentationGenerator()
        return generator._generate_troubleshooting()


# CLI tool for documentation generation
def generate_docs_cli():
    """Generate documentation files from CLI."""
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description="Generate API documentation")
    parser.add_argument("--output", "-o", default="./docs", help="Output directory")
    parser.add_argument("--format", "-f", choices=["json", "yaml", "html"], default="json", help="Output format")
    
    args = parser.parse_args()
    
    generator = APIDocumentationGenerator()
    
    os.makedirs(args.output, exist_ok=True)
    
    if args.format == "json":
        # Export OpenAPI spec
        with open(os.path.join(args.output, "openapi.json"), "w") as f:
            json.dump(generator.openapi_spec, f, indent=2)
        
        # Export full documentation
        with open(os.path.join(args.output, "documentation.json"), "w") as f:
            json.dump(generator.generate_documentation(), f, indent=2)
    
    elif args.format == "yaml":
        import yaml
        with open(os.path.join(args.output, "openapi.yaml"), "w") as f:
            yaml.dump(generator.openapi_spec, f, default_flow_style=False)
    
    elif args.format == "html":
        # Generate HTML documentation
        html_content = generate_html_docs(generator)
        with open(os.path.join(args.output, "documentation.html"), "w") as f:
            f.write(html_content)
    
    print(f"Documentation generated in {args.output}")


def generate_html_docs(generator: APIDocumentationGenerator) -> str:
    """Generate HTML documentation."""
    docs = generator.generate_documentation()
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Raptorflow API Documentation</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .endpoint {{ background: #f5f5f5; padding: 20px; margin: 20px 0; border-radius: 5px; }}
            .method {{ padding: 5px 10px; color: white; border-radius: 3px; }}
            .get {{ background: #61affe; }}
            .post {{ background: #49cc90; }}
            .put {{ background: #fca130; }}
            .delete {{ background: #f93e3e; }}
            pre {{ background: #f8f8f8; padding: 10px; border-radius: 3px; overflow-x: auto; }}
        </style>
    </head>
    <body>
        <h1>Raptorflow API Documentation</h1>
        <p>Enterprise-grade AI agent platform with advanced security and monitoring</p>
        
        <h2>Authentication</h2>
        <p>All API endpoints require authentication using Bearer tokens or API keys.</p>
        
        <h2>Rate Limiting</h2>
        <p>API rate limiting is implemented using intelligent behavioral analysis.</p>
        
        <h2>Endpoints</h2>
    """
    
    # Add endpoints
    for path, methods in docs["openapi"]["paths"].items():
        html += f'<div class="endpoint">'
        html += f'<h3>{path}</h3>'
        
        for method, details in methods.items():
            if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                html += f'<div class="method {method.lower()}">{method.upper()}</div>'
                html += f'<p>{details.get("summary", "")}</p>'
                html += f'<p>{details.get("description", "")}</p>'
        
        html += '</div>'
    
    html += """
    </body>
    </html>
    """
    
    return html


if __name__ == "__main__":
    generate_docs_cli()
