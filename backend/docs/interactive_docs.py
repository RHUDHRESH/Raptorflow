"""
Interactive Documentation Generator with Real-Time Testing Capabilities

Provides interactive API documentation with live testing, code generation,
and comprehensive examples for RaptorFlow backend API.
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path

import aiohttp
import jinja2
import yaml
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class APITestRequest(BaseModel):
    """API test request model."""
    method: str
    endpoint: str
    headers: Optional[Dict[str, str]] = {}
    params: Optional[Dict[str, Any]] = {}
    body: Optional[Dict[str, Any]] = None
    auth_token: Optional[str] = None


class APITestResponse(BaseModel):
    """API test response model."""
    success: bool
    status_code: int
    response_time: float
    response_body: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    headers: Optional[Dict[str, str]] = None


class CodeExample(BaseModel):
    """Code example model."""
    language: str
    code: str
    description: str
    requires_auth: bool = False


class InteractiveDocumentationGenerator:
    """Interactive documentation generator with real-time testing."""

    def __init__(self, openapi_spec_path: str, output_dir: str = "docs/interactive"):
        self.openapi_spec_path = Path(openapi_spec_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load OpenAPI specification
        self.openapi_spec = self._load_openapi_spec()
        
        # Setup Jinja2 environment
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader([
                self.output_dir / "templates",
                Path(__file__).parent / "templates"
            ]),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
        
        # Base API URL for testing
        self.base_url = "http://localhost:8000"
        
        # Cache for test results
        self.test_cache = {}

    def _load_openapi_spec(self) -> Dict[str, Any]:
        """Load OpenAPI specification from file."""
        try:
            with open(self.openapi_spec_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load OpenAPI spec: {e}")
            raise

    async def test_api_endpoint(self, request: APITestRequest) -> APITestResponse:
        """Test API endpoint with real-time execution."""
        start_time = time.time()
        
        try:
            # Prepare headers
            headers = request.headers.copy()
            if request.auth_token:
                headers['Authorization'] = f'Bearer {request.auth_token}'
            
            # Build URL
            url = f"{self.base_url}{request.endpoint}"
            
            # Make request
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=request.method,
                    url=url,
                    headers=headers,
                    params=request.params,
                    json=request.body
                ) as response:
                    response_time = time.time() - start_time
                    
                    try:
                        response_body = await response.json()
                    except:
                        response_body = await response.text()
                    
                    return APITestResponse(
                        success=response.status_code < 400,
                        status_code=response.status_code,
                        response_time=response_time,
                        response_body=response_body,
                        headers=dict(response.headers)
                    )
                    
        except Exception as e:
            response_time = time.time() - start_time
            return APITestResponse(
                success=False,
                status_code=0,
                response_time=response_time,
                error_message=str(e)
            )

    def generate_code_examples(self, endpoint: str, method: str) -> List[CodeExample]:
        """Generate code examples for different programming languages."""
        examples = []
        
        # Python example
        python_code = self._generate_python_example(endpoint, method)
        examples.append(CodeExample(
            language="python",
            code=python_code,
            description="Python requests example",
            requires_auth=True
        ))
        
        # JavaScript example
        js_code = self._generate_javascript_example(endpoint, method)
        examples.append(CodeExample(
            language="javascript",
            code=js_code,
            description="JavaScript fetch example",
            requires_auth=True
        ))
        
        # curl example
        curl_code = self._generate_curl_example(endpoint, method)
        examples.append(CodeExample(
            language="bash",
            code=curl_code,
            description="cURL command example",
            requires_auth=True
        ))
        
        return examples

    def _generate_python_example(self, endpoint: str, method: str) -> str:
        """Generate Python code example."""
        return f'''import requests
import json

# API Configuration
BASE_URL = "https://api.raptorflow.com"
API_TOKEN = "your_access_token_here"

# Make API request
url = f"{{BASE_URL}}{endpoint}"
headers = {{
    "Authorization": f"Bearer {{API_TOKEN}}",
    "Content-Type": "application/json"
}}

response = requests.{method.lower()}(url, headers=headers)

# Handle response
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print(f"Error: {{response.status_code}}")
    print("Response:", response.text)'''

    def _generate_javascript_example(self, endpoint: str, method: str) -> str:
        """Generate JavaScript code example."""
        return f'''// API Configuration
const BASE_URL = "https://api.raptorflow.com";
const API_TOKEN = "your_access_token_here";

// Make API request
const url = `${{BASE_URL}}{endpoint}`;
const headers = {{
  "Authorization": `Bearer ${{API_TOKEN}}`,
  "Content-Type": "application/json"
}};

fetch(url, {{
  method: "{method.upper()}",
  headers: headers
}})
.then(response => {{
  if (response.ok) {{
    return response.json();
  }} else {{
    throw new Error(`HTTP error! status: ${{response.status}}`);
  }}
}})
.then(data => {{
  console.log("Success:", data);
}})
.catch(error => {{
  console.error("Error:", error);
}});'''

    def _generate_curl_example(self, endpoint: str, method: str) -> str:
        """Generate cURL command example."""
        return f'''#!/bin/bash

# API Configuration
BASE_URL="https://api.raptorflow.com"
API_TOKEN="your_access_token_here"

# Make API request
curl -X {method.upper()} \\
  "{BASE_URL}{endpoint}" \\
  -H "Authorization: Bearer $API_TOKEN" \\
  -H "Content-Type: application/json" \\
  -w "\\nResponse Time: %{{time_total}}s\\nHTTP Code: %{{http_code}}\\n"'''

    def generate_interactive_html(self) -> str:
        """Generate interactive HTML documentation."""
        template_str = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RaptorFlow API Documentation</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/prismjs@1.29.0/components/prism-core.min.js"></script>
    <script src="https://unpkg.com/prismjs@1.29.0/plugins/autoloader/prism-autoloader.min.js"></script>
    <link href="https://unpkg.com/prismjs@1.29.0/themes/prism-tomorrow.css" rel="stylesheet">
    <style>
        .endpoint-card { transition: all 0.3s ease; }
        .endpoint-card:hover { transform: translateY(-2px); }
        .method-badge { font-weight: bold; padding: 2px 8px; border-radius: 4px; }
        .method-get { background: #10b981; color: white; }
        .method-post { background: #3b82f6; color: white; }
        .method-put { background: #f59e0b; color: white; }
        .method-delete { background: #ef4444; color: white; }
        .response-success { border-left: 4px solid #10b981; }
        .response-error { border-left: 4px solid #ef4444; }
    </style>
</head>
<body class="bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center py-6">
                <div>
                    <h1 class="text-3xl font-bold text-gray-900">RaptorFlow API</h1>
                    <p class="text-gray-600 mt-1">Interactive API Documentation</p>
                </div>
                <div class="flex items-center space-x-4">
                    <select id="server-select" class="border rounded px-3 py-2">
                        <option value="http://localhost:8000">Development</option>
                        <option value="https://api-staging.raptorflow.com">Staging</option>
                        <option value="https://api.raptorflow.com">Production</option>
                    </select>
                    <input type="text" id="auth-token" placeholder="Bearer Token" 
                           class="border rounded px-3 py-2 w-64">
                </div>
            </div>
        </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <!-- Navigation -->
        <nav class="mb-8">
            <div class="flex space-x-4">
                {% for tag in openapi_spec.tags %}
                <button class="tag-btn px-4 py-2 rounded-lg bg-white border hover:bg-gray-50"
                        data-tag="{{ tag.name }}">{{ tag.name }}</button>
                {% endfor %}
            </div>
        </nav>

        <!-- Endpoints -->
        <div class="space-y-6">
            {% for path, methods in openapi_spec.paths.items() %}
            {% for method, details in methods.items() %}
            <div class="endpoint-card bg-white rounded-lg shadow-md p-6" 
                 data-tags="{{ details.tags|join(',') }}">
                <!-- Method and Path -->
                <div class="flex items-center justify-between mb-4">
                    <div class="flex items-center space-x-3">
                        <span class="method-badge method-{{ method }}">{{ method.upper() }}</span>
                        <code class="text-lg font-mono">{{ path }}</code>
                    </div>
                    <button class="test-btn px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                            data-method="{{ method }}" data-path="{{ path }}">
                        Test API
                    </button>
                </div>

                <!-- Description -->
                <div class="mb-4">
                    <h3 class="font-semibold text-gray-900 mb-2">{{ details.summary }}</h3>
                    <p class="text-gray-600">{{ details.description }}</p>
                </div>

                <!-- Parameters -->
                {% if details.parameters %}
                <div class="mb-4">
                    <h4 class="font-semibold text-gray-900 mb-2">Parameters</h4>
                    <div class="bg-gray-50 rounded p-4">
                        <table class="w-full text-sm">
                            <thead>
                                <tr class="border-b">
                                    <th class="text-left py-2">Name</th>
                                    <th class="text-left py-2">Type</th>
                                    <th class="text-left py-2">Required</th>
                                    <th class="text-left py-2">Description</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for param in details.parameters %}
                                <tr class="border-b">
                                    <td class="py-2 font-mono">{{ param.name }}</td>
                                    <td class="py-2">{{ param.schema.type }}</td>
                                    <td class="py-2">{{ "Yes" if param.required else "No" }}</td>
                                    <td class="py-2">{{ param.description or "" }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
                {% endif %}

                <!-- Request Body -->
                {% if details.requestBody %}
                <div class="mb-4">
                    <h4 class="font-semibold text-gray-900 mb-2">Request Body</h4>
                    <div class="bg-gray-50 rounded p-4">
                        <pre class="text-sm overflow-x-auto"><code>{{ details.requestBody.content["application/json"].schema | tojson(indent=2) }}</code></pre>
                    </div>
                </div>
                {% endif %}

                <!-- Responses -->
                <div class="mb-4">
                    <h4 class="font-semibold text-gray-900 mb-2">Responses</h4>
                    {% for status, response in details.responses.items() %}
                    <div class="mb-2">
                        <span class="inline-block px-2 py-1 rounded text-sm font-mono
                                   {% if status.startswith('2') %}bg-green-100 text-green-800{% else %}bg-red-100 text-red-800{% endif %}">
                            {{ status }}
                        </span>
                        <span class="ml-2 text-gray-600">{{ response.description }}</span>
                    </div>
                    {% endfor %}
                </div>

                <!-- Code Examples -->
                <div class="mb-4">
                    <h4 class="font-semibold text-gray-900 mb-2">Code Examples</h4>
                    <div class="space-y-2">
                        {% for example in code_examples[path][method] %}
                        <div class="border rounded">
                            <div class="bg-gray-50 px-4 py-2 border-b flex justify-between items-center">
                                <span class="font-mono text-sm">{{ example.language }}</span>
                                <button class="copy-btn text-xs px-2 py-1 bg-gray-200 rounded hover:bg-gray-300"
                                        data-code="{{ example.code | replace('"', '&quot;') }}">
                                    Copy
                                </button>
                            </div>
                            <pre class="p-4 overflow-x-auto"><code class="language-{{ example.language }}">{{ example.code }}</code></pre>
                        </div>
                        {% endfor %}
                    </div>
                </div>

                <!-- Test Results -->
                <div id="test-results-{{ method }}-{{ path | replace('/', '-') }}" class="hidden">
                    <h4 class="font-semibold text-gray-900 mb-2">Test Results</h4>
                    <div class="test-results-content"></div>
                </div>
            </div>
            {% endfor %}
            {% endfor %}
        </div>
    </main>

    <!-- Test Modal -->
    <div id="test-modal" class="fixed inset-0 bg-black bg-opacity-50 hidden flex items-center justify-center z-50">
        <div class="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
            <div class="flex justify-between items-center mb-4">
                <h3 class="text-lg font-semibold">Test API Endpoint</h3>
                <button id="close-modal" class="text-gray-500 hover:text-gray-700">&times;</button>
            </div>
            
            <div class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Method</label>
                    <input type="text" id="test-method" readonly class="w-full border rounded px-3 py-2 bg-gray-50">
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Endpoint</label>
                    <input type="text" id="test-endpoint" readonly class="w-full border rounded px-3 py-2 bg-gray-50">
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Request Body (JSON)</label>
                    <textarea id="test-body" rows="6" class="w-full border rounded px-3 py-2 font-mono text-sm"
                              placeholder='{"key": "value"}'></textarea>
                </div>
                
                <div class="flex space-x-4">
                    <button id="execute-test" class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
                        Execute Test
                    </button>
                    <button id="clear-results" class="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400">
                        Clear Results
                    </button>
                </div>
                
                <div id="test-output" class="hidden">
                    <h4 class="font-semibold mb-2">Results</h4>
                    <div class="bg-gray-50 rounded p-4">
                        <div class="grid grid-cols-2 gap-4 mb-4">
                            <div>
                                <span class="font-medium">Status:</span>
                                <span id="result-status" class="ml-2"></span>
                            </div>
                            <div>
                                <span class="font-medium">Response Time:</span>
                                <span id="result-time" class="ml-2"></span>
                            </div>
                        </div>
                        <div class="mb-2">
                            <span class="font-medium">Response Body:</span>
                        </div>
                        <pre id="result-body" class="bg-white border rounded p-3 overflow-x-auto text-sm"></pre>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Interactive functionality
        let currentServer = 'http://localhost:8000';
        let authToken = '';

        // Server selection
        document.getElementById('server-select').addEventListener('change', (e) => {
            currentServer = e.target.value;
        });

        // Auth token
        document.getElementById('auth-token').addEventListener('input', (e) => {
            authToken = e.target.value;
        });

        // Tag filtering
        document.querySelectorAll('.tag-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const tag = btn.dataset.tag;
                document.querySelectorAll('.endpoint-card').forEach(card => {
                    if (card.dataset.tags.includes(tag)) {
                        card.style.display = 'block';
                    } else {
                        card.style.display = 'none';
                    }
                });
            });
        });

        // Test button clicks
        document.querySelectorAll('.test-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const method = btn.dataset.method;
                const path = btn.dataset.path;
                openTestModal(method, path);
            });
        });

        // Copy buttons
        document.querySelectorAll('.copy-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                navigator.clipboard.writeText(btn.dataset.code);
                btn.textContent = 'Copied!';
                setTimeout(() => {
                    btn.textContent = 'Copy';
                }, 2000);
            });
        });

        // Modal functionality
        const modal = document.getElementById('test-modal');
        const closeModal = document.getElementById('close-modal');

        function openTestModal(method, path) {
            document.getElementById('test-method').value = method.toUpperCase();
            document.getElementById('test-endpoint').value = path;
            document.getElementById('test-output').classList.add('hidden');
            modal.classList.remove('hidden');
        }

        closeModal.addEventListener('click', () => {
            modal.classList.add('hidden');
        });

        // Execute test
        document.getElementById('execute-test').addEventListener('click', async () => {
            const method = document.getElementById('test-method').value;
            const endpoint = document.getElementById('test-endpoint').value;
            let body = null;
            
            try {
                const bodyText = document.getElementById('test-body').value.trim();
                if (bodyText) {
                    body = JSON.parse(bodyText);
                }
            } catch (e) {
                alert('Invalid JSON in request body');
                return;
            }

            try {
                const response = await fetch(`${currentServer}/docs/test-api`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        method: method,
                        endpoint: endpoint,
                        body: body,
                        auth_token: authToken
                    })
                });

                const result = await response.json();
                displayTestResults(result);
            } catch (e) {
                displayTestResults({
                    success: false,
                    error_message: e.message
                });
            }
        });

        function displayTestResults(result) {
            const outputDiv = document.getElementById('test-output');
            const statusSpan = document.getElementById('result-status');
            const timeSpan = document.getElementById('result-time');
            const bodyPre = document.getElementById('result-body');

            if (result.success) {
                statusSpan.textContent = `${result.status_code} - Success`;
                statusSpan.className = 'ml-2 text-green-600';
            } else {
                statusSpan.textContent = result.error_message || 'Error';
                statusSpan.className = 'ml-2 text-red-600';
            }

            timeSpan.textContent = `${(result.response_time || 0).toFixed(3)}s`;
            bodyPre.textContent = JSON.stringify(result.response_body || result, null, 2);
            
            outputDiv.classList.remove('hidden');
        }

        document.getElementById('clear-results').addEventListener('click', () => {
            document.getElementById('test-output').classList.add('hidden');
            document.getElementById('test-body').value = '';
        });
    </script>
</body>
</html>
        '''
        
        # Generate code examples for all endpoints
        code_examples = {}
        for path, methods in self.openapi_spec['paths'].items():
            code_examples[path] = {}
            for method in methods.keys():
                code_examples[path][method] = self.generate_code_examples(path, method)
        
        template = self.jinja_env.from_string(template_str)
        return template.render(
            openapi_spec=self.openapi_spec,
            code_examples=code_examples
        )

    def generate_documentation(self) -> None:
        """Generate complete interactive documentation."""
        logger.info("Generating interactive documentation...")
        
        # Generate HTML documentation
        html_content = self.generate_interactive_html()
        
        # Write to file
        output_file = self.output_dir / "index.html"
        with open(output_file, 'w') as f:
            f.write(html_content)
        
        logger.info(f"Interactive documentation generated: {output_file}")

    def create_fastapi_app(self) -> FastAPI:
        """Create FastAPI app for serving interactive docs."""
        app = FastAPI(
            title="RaptorFlow Interactive Documentation",
            description="Interactive API documentation with real-time testing"
        )

        @app.post("/docs/test-api", response_model=APITestResponse)
        async def test_api(request: APITestRequest):
            """Test API endpoint."""
            return await self.test_api_endpoint(request)

        @app.get("/docs/interactive", response_class=HTMLResponse)
        async def interactive_docs():
            """Serve interactive documentation."""
            return self.generate_interactive_html()

        # Mount static files
        if (self.output_dir / "static").exists():
            app.mount("/static", StaticFiles(directory=self.output_dir / "static"))

        return app


# CLI usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate interactive API documentation")
    parser.add_argument(
        "--openapi-spec",
        default="docs/openapi_comprehensive.yaml",
        help="Path to OpenAPI specification file"
    )
    parser.add_argument(
        "--output-dir",
        default="docs/interactive",
        help="Output directory for generated documentation"
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Start documentation server"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port for documentation server"
    )
    
    args = parser.parse_args()
    
    # Generate documentation
    generator = InteractiveDocumentationGenerator(
        openapi_spec_path=args.openapi_spec,
        output_dir=args.output_dir
    )
    
    generator.generate_documentation()
    
    if args.serve:
        import uvicorn
        
        app = generator.create_fastapi_app()
        uvicorn.run(app, host="0.0.0.0", port=args.port)
        print(f"Interactive documentation server running on http://localhost:{args.port}")
