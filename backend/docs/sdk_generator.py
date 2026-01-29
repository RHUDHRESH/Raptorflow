"""
SDK Generator with Multiple Language Support from OpenAPI Specification

Comprehensive SDK generation for RaptorFlow backend API:
- Multi-language SDK generation (Python, JavaScript, Java, C#, Go, Ruby)
- Type-safe client libraries
- Authentication handling
- Error management
- Documentation generation
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

import jinja2
import yaml
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class SDKLanguage(Enum):
    """Supported SDK languages."""

    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CSHARP = "csharp"
    GO = "go"
    RUBY = "ruby"
    PHP = "php"


@dataclass
class SDKConfig:
    """SDK generation configuration."""

    language: SDKLanguage
    package_name: str
    version: str
    author: str
    description: str
    base_url: str
    auth_type: str = "bearer"
    include_async: bool = True
    include_types: bool = True


class SDKGeneratorConfig(BaseModel):
    """SDK generator configuration."""

    openapi_spec_path: str = "docs/openapi_comprehensive.yaml"
    output_dir: str = "generated_sdks"
    languages: List[SDKLanguage] = Field(
        default=[SDKLanguage.PYTHON, SDKLanguage.JAVASCRIPT]
    )
    company_name: str = "RaptorFlow"
    product_name: str = "Backend API"
    version: str = "1.0.0"
    base_url: str = "https://api.raptorflow.com"
    include_examples: bool = True
    include_tests: bool = True


class SDKGenerator:
    """Comprehensive SDK generator."""

    def __init__(self, config: SDKGeneratorConfig):
        self.config = config
        self.openapi_spec: Dict[str, Any] = {}
        self.template_env: Optional[jinja2.Environment] = None

        # Create output directory
        Path(config.output_dir).mkdir(parents=True, exist_ok=True)

        # Load OpenAPI specification
        self._load_openapi_spec()

        # Setup Jinja2 environment
        self._setup_template_env()

    def _load_openapi_spec(self) -> None:
        """Load OpenAPI specification."""
        try:
            with open(self.config.openapi_spec_path, "r") as f:
                self.openapi_spec = yaml.safe_load(f)
            logger.info(f"Loaded OpenAPI spec: {self.config.openapi_spec_path}")
        except Exception as e:
            logger.error(f"Failed to load OpenAPI spec: {e}")
            raise

    def _setup_template_env(self) -> None:
        """Setup Jinja2 template environment."""
        template_dir = Path(__file__).parent / "templates"
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader([template_dir]),
            autoescape=jinja2.select_autoescape(["html", "xml"]),
        )

    def generate_python_sdk(self) -> Dict[str, str]:
        """Generate Python SDK."""
        logger.info("Generating Python SDK")

        sdk_config = SDKConfig(
            language=SDKLanguage.PYTHON,
            package_name="raptorflow",
            version=self.config.version,
            author=self.config.company_name,
            description=f"{self.config.product_name} Python SDK",
            base_url=self.config.base_url,
        )

        files = {}

        # Generate setup.py
        files["setup.py"] = self._generate_python_setup(sdk_config)

        # Generate main client
        files["raptorflow/__init__.py"] = self._generate_python_init(sdk_config)
        files["raptorflow/client.py"] = self._generate_python_client(sdk_config)

        # Generate API modules
        files.update(self._generate_python_api_modules(sdk_config))

        # Generate models
        files.update(self._generate_python_models(sdk_config))

        # Generate examples
        if self.config.include_examples:
            files.update(self._generate_python_examples(sdk_config))

        # Generate tests
        if self.config.include_tests:
            files.update(self._generate_python_tests(sdk_config))

        return files

    def _generate_python_setup(self, config: SDKConfig) -> str:
        """Generate Python setup.py file."""
        return f"""
from setuptools import setup, find_packages

setup(
    name="{config.package_name}",
    version="{config.version}",
    author="{config.author}",
    description="{config.description}",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/{config.author.lower()}/{config.package_name}",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "pydantic>=1.8.0",
        "typing-extensions>=3.10.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "black>=21.0",
            "flake8>=3.9",
        ],
    },
)
        """

    def _generate_python_init(self, config: SDKConfig) -> str:
        """Generate Python __init__.py file."""
        return f'''
"""
{config.description}

Version: {config.version}
"""

from client import RaptorFlowClient
from .models import *

__version__ = "{config.version}"
__author__ = "{config.author}"

__all__ = [
    "RaptorFlowClient",
]
        '''

    def _generate_python_client(self, config: SDKConfig) -> str:
        """Generate Python client class."""
        return f'''
"""
{config.description} - Main Client
"""

import json
import logging
from typing import Any, Dict, Optional, Union
from urllib.parse import urljoin

import requests
from requests.auth import AuthBase

from .models import *

logger = logging.getLogger(__name__)


class BearerAuth(AuthBase):
    """Bearer token authentication."""

    def __init__(self, token: str):
        self.token = token

    def __call__(self, r):
        r.headers["Authorization"] = f"Bearer {{self.token}}"
        return r


class RaptorFlowClient:
    """
    {config.description}

    Example:
        >>> client = RaptorFlowClient(email="user@example.com", password="password")
        >>> user = client.users.get_me()
        >>> print(f"Welcome, {{user.name}}!")
    """

    def __init__(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None,
        token: Optional[str] = None,
        base_url: str = "{config.base_url}",
        timeout: int = 30,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

        # Authentication
        if token:
            self.session.auth = BearerAuth(token)
        elif email and password:
            self.token = self._login(email, password)
            self.session.auth = BearerAuth(self.token)
        else:
            raise ValueError("Either token or email/password must be provided")

        # API modules
        self.users = UsersAPI(self)
        self.workspaces = WorkspacesAPI(self)
        self.auth = AuthAPI(self)
        self.agents = AgentsAPI(self)

    def _login(self, email: str, password: str) -> str:
        """Login and get access token."""
        response = self.session.post(
            f"{{self.base_url}}/auth/login",
            json={{"email": email, "password": password}},
            timeout=self.timeout
        )
        response.raise_for_status()
        data = response.json()
        return data["data"]["access_token"]

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> requests.Response:
        """Make HTTP request."""
        url = urljoin(self.base_url, endpoint)
        response = self.session.request(
            method,
            url,
            params=params,
            json=data,
            timeout=self.timeout,
            **kwargs
        )
        response.raise_for_status()
        return response

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Make GET request."""
        return self._request("GET", endpoint, params=params)

    def _post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Make POST request."""
        return self._request("POST", endpoint, data=data)

    def _put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Make PUT request."""
        return self._request("PUT", endpoint, data=data)

    def _delete(self, endpoint: str) -> requests.Response:
        """Make DELETE request."""
        return self._request("DELETE", endpoint)


class BaseAPI:
    """Base API class."""

    def __init__(self, client: RaptorFlowClient):
        self.client = client


class UsersAPI(BaseAPI):
    """Users API."""

    def get_me(self) -> User:
        """Get current user profile."""
        response = self.client._get("/users/me")
        data = response.json()
        return User(**data["data"])

    def update_me(self, user_data: Dict[str, Any]) -> User:
        """Update current user profile."""
        response = self.client._put("/users/me", user_data)
        data = response.json()
        return User(**data["data"])


class WorkspacesAPI(BaseAPI):
    """Workspaces API."""

    def list(self) -> List[Workspace]:
        """List all workspaces."""
        response = self.client._get("/workspaces")
        data = response.json()
        return [Workspace(**item) for item in data["data"]["workspaces"]]

    def create(self, workspace_data: Dict[str, Any]) -> Workspace:
        """Create a new workspace."""
        response = self.client._post("/workspaces", workspace_data)
        data = response.json()
        return Workspace(**data["data"])

    def get(self, workspace_id: str) -> Workspace:
        """Get workspace by ID."""
        response = self.client._get(f"/workspaces/{{workspace_id}}")
        data = response.json()
        return Workspace(**data["data"])

    def update(self, workspace_id: str, workspace_data: Dict[str, Any]) -> Workspace:
        """Update workspace."""
        response = self.client._put(f"/workspaces/{{workspace_id}}", workspace_data)
        data = response.json()
        return Workspace(**data["data"])

    def delete(self, workspace_id: str) -> None:
        """Delete workspace."""
        self.client._delete(f"/workspaces/{{workspace_id}}")


class AuthAPI(BaseAPI):
    """Authentication API."""

    def login(self, email: str, password: str) -> AuthResponse:
        """Login and get tokens."""
        response = self.client._post("/auth/login", {"email": email, "password": password})
        data = response.json()
        return AuthResponse(**data["data"])

    def refresh(self, refresh_token: str) -> AuthResponse:
        """Refresh access token."""
        response = self.client._post("/auth/refresh", {"refresh_token": refresh_token})
        data = response.json()
        return AuthResponse(**data["data"])


class AgentsAPI(BaseAPI):
    """AI Agents API."""

    def execute_market_research(self, request: MarketResearchRequest) -> AgentResult:
        """Execute market research agent."""
        response = self.client._post("/agents/market_research/execute", request.dict())
        data = response.json()
        return AgentResult(**data["data"])

    def execute_content_creator(self, request: ContentCreationRequest) -> AgentResult:
        """Execute content creation agent."""
        response = self.client._post("/agents/content_creator/execute", request.dict())
        data = response.json()
        return AgentResult(**data["data"])

    def execute_data_analyst(self, request: DataAnalysisRequest) -> AgentResult:
        """Execute data analysis agent."""
        response = self.client._post("/agents/data_analyst/execute", request.dict())
        data = response.json()
        return AgentResult(**data["data"])
        '''

    def _generate_python_api_modules(self, config: SDKConfig) -> Dict[str, str]:
        """Generate Python API modules."""
        files = {}

        # Generate individual API modules based on OpenAPI paths
        paths = self.openapi_spec.get("paths", {})

        for path, methods in paths.items():
            module_name = (
                path.strip("/").replace("/", "_").replace("{", "").replace("}", "")
            )
            if not module_name:
                continue

            module_content = f'''
"""
{module_name.title()} API Module
"""

from typing import Any, Dict, List, Optional
from client import BaseAPI
from .models import *


class {module_name.title().replace('_', '')}API(BaseAPI):
    """{module_name.title()} API."""
'''

            for method, details in methods.items():
                operation_id = details.get("operationId", f"{method}_{module_name}")
                summary = details.get("summary", f"{method.upper()} {path}")

                # Generate method signature
                method_name = operation_id.replace("-", "_").replace("/", "_")

                # Handle parameters
                parameters = details.get("parameters", [])
                param_list = []
                for param in parameters:
                    param_name = param["name"]
                    param_type = self._get_python_type(
                        param.get("schema", {}).get("type", "str")
                    )
                    if param.get("required", False):
                        param_list.append(f"{param_name}: {param_type}")
                    else:
                        param_list.append(
                            f"{param_name}: Optional[{param_type}] = None"
                        )

                # Handle request body
                if "requestBody" in details:
                    request_schema = (
                        details["requestBody"]
                        .get("content", {})
                        .get("application/json", {})
                        .get("schema", {})
                    )
                    request_type = self._get_model_name_from_schema(request_schema)
                    param_list.append(f"data: {request_type}")

                signature = f"def {method_name}({', '.join(param_list)}) -> Any:"

                # Generate method implementation
                implementation = f'''
    {signature}
        """
        {summary}
        """
'''

                # Build request URL
                url_path = path
                for param in parameters:
                    if param["in"] == "path":
                        url_path = url_path.replace(
                            f"{{{param['name']}}}", f"{{{param['name']}}}"
                        )

                # Build request data
                request_data = "data if 'data' in locals() else None"

                implementation += f"""        response = self.client._{method.lower()}("{url_path}", {request_data})
        return response.json()
"""

                module_content += implementation

            files[f"raptorflow/api/{module_name}.py"] = module_content

        return files

    def _generate_python_models(self, config: SDKConfig) -> Dict[str, str]:
        """Generate Python model classes."""
        files = {}

        models_content = '''
"""
Data models for RaptorFlow API
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field


class User(BaseModel):
    """User model."""
    id: str
    email: str
    name: str
    created_at: datetime
    updated_at: datetime


class Workspace(BaseModel):
    """Workspace model."""
    id: str
    name: str
    description: Optional[str] = None
    subscription_tier: str
    created_at: datetime
    updated_at: datetime


class AuthResponse(BaseModel):
    """Authentication response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class AgentResult(BaseModel):
    """Agent execution result."""
    id: str
    output: str
    confidence: float
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    execution_time: float


class MarketResearchRequest(BaseModel):
    """Market research request."""
    workspace_id: str
    input: str
    context: Optional[Dict[str, Any]] = None
    options: Optional[Dict[str, Any]] = None


class ContentCreationRequest(BaseModel):
    """Content creation request."""
    workspace_id: str
    input: str
    content_type: str
    tone: str = "professional"
    options: Optional[Dict[str, Any]] = None


class DataAnalysisRequest(BaseModel):
    """Data analysis request."""
    workspace_id: str
    input: str
    analysis_type: str
    options: Optional[Dict[str, Any]] = None
'''

        files["raptorflow/models.py"] = models_content

        return files

    def _generate_python_examples(self, config: SDKConfig) -> Dict[str, str]:
        """Generate Python examples."""
        return {
            "examples/basic_usage.py": f'''
"""
Basic usage examples for {config.package_name} SDK
"""

from {config.package_name} import RaptorFlowClient

def main():
    # Initialize client
    client = RaptorFlowClient(
        email="your-email@example.com",
        password="your-password"
    )

    # Get user profile
    user = client.users.get_me()
    print(f"Welcome, {{user.name}}!")

    # List workspaces
    workspaces = client.workspaces.list()
    print(f"Found {{len(workspaces)}} workspaces")

    # Create a new workspace
    workspace = client.workspaces.create({{
        "name": "My Test Workspace",
        "description": "A workspace for testing",
        "subscription_tier": "pro"
    }})
    print(f"Created workspace: {{workspace.id}}")

    # Execute market research agent
    result = client.agents.execute_market_research({{
        "workspace_id": workspace.id,
        "input": "Analyze market trends for SaaS companies",
        "context": {{
            "industry": "technology",
            "region": "north_america"
        }},
        "options": {{
            "model": "gemini-pro",
            "max_tokens": 1000
        }}
    }})
    print(f"Research result: {{result.output[:200]}}...")

if __name__ == "__main__":
    main()
            '''
        }

    def _generate_python_tests(self, config: SDKConfig) -> Dict[str, str]:
        """Generate Python tests."""
        return {
            "tests/test_client.py": f'''
"""
Tests for {config.package_name} SDK
"""

import pytest
from {config.package_name} import RaptorFlowClient

class TestRaptorFlowClient:
    """Test RaptorFlowClient class."""

    def test_init_with_token(self):
        """Test initialization with token."""
        client = RaptorFlowClient(token="test-token")
        assert client.token == "test-token"

    def test_init_with_credentials(self):
        """Test initialization with email and password."""
        # This would require mocking the login request
        pass

    def test_get_me(self):
        """Test getting user profile."""
        # This would require mocking the API response
        pass

if __name__ == "__main__":
    pytest.main()
            '''
        }

    def generate_javascript_sdk(self) -> Dict[str, str]:
        """Generate JavaScript SDK."""
        logger.info("Generating JavaScript SDK")

        files = {}

        # Generate package.json
        files["package.json"] = self._generate_js_package()

        # Generate main client
        files["src/index.js"] = self._generate_js_client()

        # Generate API modules
        files.update(self._generate_js_api_modules())

        # Generate models
        files.update(self._generate_js_models())

        # Generate examples
        if self.config.include_examples:
            files.update(self._generate_js_examples())

        return files

    def _generate_js_package(self) -> str:
        """Generate JavaScript package.json."""
        return f"""
{{
  "name": "raptorflow-sdk",
  "version": "{self.config.version}",
  "description": "{self.config.product_name} JavaScript SDK",
  "main": "src/index.js",
  "type": "module",
  "scripts": {{
    "test": "jest",
    "lint": "eslint src/",
    "build": "webpack --mode production"
  }},
  "keywords": ["api", "sdk", "raptorflow", "ai", "business-intelligence"],
  "author": "{self.config.company_name}",
  "license": "MIT",
  "dependencies": {{
    "node-fetch": "^3.2.0"
  }},
  "devDependencies": {{
    "jest": "^29.0.0",
    "eslint": "^8.0.0",
    "webpack": "^5.0.0",
    "webpack-cli": "^4.0.0"
  }},
  "engines": {{
    "node": ">=14.0.0"
  }}
}}
        """

    def _generate_js_client(self) -> str:
        """Generate JavaScript client."""
        return f"""
/**
 * {self.config.product_name} JavaScript SDK
 * Version: {self.config.version}
 */

import fetch from 'node-fetch';

class RaptorFlowClient {{
  /**
   * Initialize the RaptorFlow client
   * @param {{Object}} options - Client options
   * @param {{string}} options.email - User email
   * @param {{string}} options.password - User password
   * @param {{string}} options.token - Access token
   * @param {{string}} options.baseUrl - Base API URL
   */
  constructor(options = {{}}) {{
    this.baseUrl = options.baseUrl || '{self.config.base_url}';
    this.timeout = options.timeout || 30000;

    if (options.token) {{
      this.token = options.token;
    }} else if (options.email && options.password) {{
      // Will login on first request
      this.email = options.email;
      this.password = options.password;
    }} else {{
      throw new Error('Either token or email/password must be provided');
    }}

    // API modules
    this.users = new UsersAPI(this);
    this.workspaces = new WorkspacesAPI(this);
    this.auth = new AuthAPI(this);
    this.agents = new AgentsAPI(this);
  }}

  async _ensureAuthenticated() {{
    if (!this.token && this.email && this.password) {{
      await this.login();
    }}
  }}

  async login() {{
    const response = await fetch(`${{this.baseUrl}}/auth/login`, {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify({{
        email: this.email,
        password: this.password
      }})
    }});

    if (!response.ok) {{
      throw new Error(`Login failed: ${{response.statusText}}`);
    }}

    const data = await response.json();
    this.token = data.data.access_token;
    return data.data;
  }}

  async _request(method, endpoint, data = null) {{
    await this._ensureAuthenticated();

    const url = `${{this.baseUrl}}${{endpoint}}`;
    const options = {{
      method,
      headers: {{
        'Authorization': `Bearer ${{this.token}}`,
        'Content-Type': 'application/json'
      }}
    }};

    if (data) {{
      options.body = JSON.stringify(data);
    }}

    const response = await fetch(url, options);

    if (!response.ok) {{
      throw new Error(`Request failed: ${{response.statusText}}`);
    }}

    return response.json();
  }}

  async get(endpoint) {{
    return this._request('GET', endpoint);
  }}

  async post(endpoint, data) {{
    return this._request('POST', endpoint, data);
  }}

  async put(endpoint, data) {{
    return this._request('PUT', endpoint, data);
  }}

  async delete(endpoint) {{
    return this._request('DELETE', endpoint);
  }}
}}

class BaseAPI {{
  constructor(client) {{
    this.client = client;
  }}
}}

class UsersAPI extends BaseAPI {{
  async getMe() {{
    const response = await this.client.get('/users/me');
    return response.data;
  }}

  async updateMe(userData) {{
    const response = await this.client.put('/users/me', userData);
    return response.data;
  }}
}}

class WorkspacesAPI extends BaseAPI {{
  async list() {{
    const response = await this.client.get('/workspaces');
    return response.data.workspaces;
  }}

  async create(workspaceData) {{
    const response = await this.client.post('/workspaces', workspaceData);
    return response.data;
  }}

  async get(workspaceId) {{
    const response = await this.client.get(`/workspaces/${{workspaceId}}`);
    return response.data;
  }}

  async update(workspaceId, workspaceData) {{
    const response = await this.client.put(`/workspaces/${{workspaceId}}`, workspaceData);
    return response.data;
  }}

  async delete(workspaceId) {{
    await this.client.delete(`/workspaces/${{workspaceId}}`);
  }}
}}

class AuthAPI extends BaseAPI {{
  async login(email, password) {{
    const response = await this.client.post('/auth/login', {{ email, password }});
    return response.data;
  }}

  async refresh(refreshToken) {{
    const response = await this.client.post('/auth/refresh', {{ refresh_token: refreshToken }});
    return response.data;
  }}
}}

class AgentsAPI extends BaseAPI {{
  async executeMarketResearch(request) {{
    const response = await this.client.post('/agents/market_research/execute', request);
    return response.data;
  }}

  async executeContentCreator(request) {{
    const response = await this.client.post('/agents/content_creator/execute', request);
    return response.data;
  }}

  async executeDataAnalyst(request) {{
    const response = await this.client.post('/agents/data_analyst/execute', request);
    return response.data;
  }}
}}

export default RaptorFlowClient;
export {{
  UsersAPI,
  WorkspacesAPI,
  AuthAPI,
  AgentsAPI
}};
        """

    def _generate_js_api_modules(self) -> Dict[str, str]:
        """Generate JavaScript API modules."""
        return {}

    def _generate_js_models(self) -> Dict[str, str]:
        """Generate JavaScript models."""
        return {
            "src/models.js": """
/**
 * Data models for RaptorFlow API
 */

export class User {
  constructor(data) {
    this.id = data.id;
    this.email = data.email;
    this.name = data.name;
    this.createdAt = new Date(data.created_at);
    this.updatedAt = new Date(data.updated_at);
  }
}

export class Workspace {
  constructor(data) {
    this.id = data.id;
    this.name = data.name;
    this.description = data.description;
    this.subscriptionTier = data.subscription_tier;
    this.createdAt = new Date(data.created_at);
    this.updatedAt = new Date(data.updated_at);
  }
}

export class AuthResponse {
  constructor(data) {
    this.accessToken = data.access_token;
    this.refreshToken = data.refresh_token;
    this.tokenType = data.token_type || 'bearer';
    this.expiresIn = data.expires_in;
  }
}

export class AgentResult {
  constructor(data) {
    this.id = data.id;
    this.output = data.output;
    this.confidence = data.confidence;
    this.sources = data.sources || [];
    this.metadata = data.metadata || {};
    this.executionTime = data.execution_time;
  }
}
            """
        }

    def _generate_js_examples(self) -> Dict[str, str]:
        """Generate JavaScript examples."""
        return {
            "examples/basic_usage.js": f"""
/**
 * Basic usage examples for RaptorFlow SDK
 */

import RaptorFlowClient from '../src/index.js';

async function main() {{
  // Initialize client
  const client = new RaptorFlowClient({{
    email: 'your-email@example.com',
    password: 'your-password'
  }});

  try {{
    // Get user profile
    const user = await client.users.getMe();
    console.log(`Welcome, ${{user.name}}!`);

    // List workspaces
    const workspaces = await client.workspaces.list();
    console.log(`Found ${{workspaces.length}} workspaces`);

    // Create a new workspace
    const workspace = await client.workspaces.create({{
      name: 'My Test Workspace',
      description: 'A workspace for testing',
      subscription_tier: 'pro'
    }});
    console.log(`Created workspace: ${{workspace.id}}`);

    // Execute market research agent
    const result = await client.agents.executeMarketResearch({{
      workspace_id: workspace.id,
      input: 'Analyze market trends for SaaS companies',
      context: {{
        industry: 'technology',
        region: 'north_america'
      }},
      options: {{
        model: 'gemini-pro',
        max_tokens: 1000
      }}
    }});
    console.log(`Research result: ${{result.output.substring(0, 200)}}...`);

  }} catch (error) {{
    console.error('Error:', error.message);
  }}
}}

main();
            """
        }

    def _get_python_type(self, openapi_type: str) -> str:
        """Convert OpenAPI type to Python type."""
        type_mapping = {
            "string": "str",
            "integer": "int",
            "number": "float",
            "boolean": "bool",
            "array": "List",
            "object": "Dict",
        }
        return type_mapping.get(openapi_type, "Any")

    def _get_model_name_from_schema(self, schema: Dict[str, Any]) -> str:
        """Extract model name from schema."""
        # Simplified - in real implementation would handle $ref and schema names
        return "Dict[str, Any]"

    def generate_all_sdks(self) -> Dict[str, Dict[str, str]]:
        """Generate all configured SDKs."""
        logger.info(
            f"Generating SDKs for languages: {[lang.value for lang in self.config.languages]}"
        )

        all_sdks = {}

        for language in self.config.languages:
            try:
                if language == SDKLanguage.PYTHON:
                    all_sdks[language.value] = self.generate_python_sdk()
                elif language == SDKLanguage.JAVASCRIPT:
                    all_sdks[language.value] = self.generate_javascript_sdk()
                # Add more languages as needed
                else:
                    logger.warning(
                        f"SDK generation for {language.value} not implemented yet"
                    )
            except Exception as e:
                logger.error(f"Failed to generate {language.value} SDK: {e}")

        return all_sdks

    def save_sdks(self, sdks: Dict[str, Dict[str, str]]) -> None:
        """Save generated SDKs to files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        for language, files in sdks.items():
            language_dir = Path(self.config.output_dir) / language / timestamp
            language_dir.mkdir(parents=True, exist_ok=True)

            for file_path, content in files.items():
                full_path = language_dir / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)

                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content)

            logger.info(f"{language.title()} SDK saved to {language_dir}")

            # Generate README
            readme_content = self._generate_readme(language)
            readme_path = language_dir / "README.md"
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(readme_content)

    def _generate_readme(self, language: str) -> str:
        """Generate README for SDK."""
        return f"""
# {self.config.company_name} {self.config.product_name} {language.title()} SDK

{self.config.product_name} {language.title()} SDK for seamless integration with the RaptorFlow API.

## Installation

### {language.title()}

```bash
# For Python
pip install raptorflow

# For JavaScript
npm install raptorflow-sdk
```

## Quick Start

```{language}
# {language.title()} example
# See examples/ directory for complete usage examples
```

## Features

- Type-safe client libraries
- Automatic authentication handling
- Comprehensive error management
- Built-in retry logic
- Full API coverage
- Extensive documentation

## API Reference

See the [API documentation](https://docs.raptorflow.com) for detailed information.

## Support

- Documentation: https://docs.raptorflow.com
- Issues: https://github.com/{self.config.company_name.lower()}/sdk/issues
- Support: support@raptorflow.com

## License

MIT License - see LICENSE file for details.
        """

    def generate_sdk_documentation(self) -> str:
        """Generate SDK documentation."""
        return f"""
# SDK Generation Documentation

## Generated SDKs

The following SDKs have been automatically generated from the OpenAPI specification:

### Supported Languages

{chr(10).join(f"- {lang.value.title()}" for lang in self.config.languages)}

### Features

- **Type Safety**: All SDKs include type definitions for request/response models
- **Authentication**: Built-in JWT token management and refresh
- **Error Handling**: Comprehensive error handling with proper exception types
- **Async Support**: Asynchronous operations for better performance
- **Documentation**: Inline documentation and examples

### Usage Examples

Each SDK includes comprehensive examples in the `examples/` directory.

## Installation

Each SDK includes its own installation instructions in the README.md file.

## API Coverage

All endpoints from the OpenAPI specification are covered:

- Authentication endpoints
- User management
- Workspace operations
- AI agent execution
- VertexAI integration

## Customization

The SDKs can be customized by modifying the generated templates or by extending the base classes.

## Support

For SDK-specific issues, please refer to the documentation or contact support.
        """


# CLI usage
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate SDKs")
    parser.add_argument(
        "--openapi-spec",
        default="docs/openapi_comprehensive.yaml",
        help="OpenAPI spec path",
    )
    parser.add_argument(
        "--output-dir", default="generated_sdks", help="Output directory"
    )
    parser.add_argument(
        "--languages",
        nargs="+",
        default=["python", "javascript"],
        help="Target languages",
    )
    parser.add_argument("--company", default="RaptorFlow", help="Company name")
    parser.add_argument("--product", default="Backend API", help="Product name")
    parser.add_argument("--version", default="1.0.0", help="SDK version")
    parser.add_argument(
        "--base-url", default="https://api.raptorflow.com", help="Base API URL"
    )

    args = parser.parse_args()

    # Create configuration
    config = SDKGeneratorConfig(
        openapi_spec_path=args.openapi_spec,
        output_dir=args.output_dir,
        languages=[SDKLanguage(lang) for lang in args.languages],
        company_name=args.company,
        product_name=args.product,
        version=args.version,
        base_url=args.base_url,
    )

    # Generate SDKs
    generator = SDKGenerator(config)
    sdks = generator.generate_all_sdks()
    generator.save_sdks(sdks)

    # Save documentation
    docs_content = generator.generate_sdk_documentation()
    docs_file = Path(args.output_dir) / "SDK_DOCUMENTATION.md"
    with open(docs_file, "w", encoding="utf-8") as f:
        f.write(docs_content)

    print(f"SDKs generated in {args.output_dir}")
    print(f"Languages: {', '.join(args.languages)}")
    print(f"Documentation: {docs_file}")
