"""
Developer Portal with Tutorials, Getting Started Guides, and Interactive Examples

Comprehensive developer portal for RaptorFlow backend API:
- Interactive tutorials and walkthroughs
- Getting started guides for different use cases
- Code examples in multiple languages
- SDK documentation and examples
- Community resources and support
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


class TutorialLevel(Enum):
    """Tutorial difficulty levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class TutorialType(Enum):
    """Tutorial types."""
    GETTING_STARTED = "getting_started"
    INTEGRATION = "integration"
    ADVANCED_FEATURES = "advanced_features"
    BEST_PRACTICES = "best_practices"
    TROUBLESHOOTING = "troubleshooting"


@dataclass
class Tutorial:
    """Tutorial content structure."""
    id: str
    title: str
    description: str
    level: TutorialLevel
    type: TutorialType
    estimated_time: str
    prerequisites: List[str] = field(default_factory=list)
    learning_objectives: List[str] = field(default_factory=list)
    sections: List[Dict[str, Any]] = field(default_factory=list)
    code_examples: List[Dict[str, str]] = field(default_factory=list)
    interactive_steps: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class CodeExample:
    """Code example structure."""
    id: str
    title: str
    description: str
    language: str
    code: str
    explanation: str
    runnable: bool = False
    dependencies: List[str] = field(default_factory=list)


class DeveloperPortalConfig(BaseModel):
    """Developer portal configuration."""
    output_dir: str = "developer_portal"
    base_url: str = "https://api.raptorflow.com"
    company_name: str = "RaptorFlow"
    product_name: str = "Backend API"
    version: str = "1.0.0"
    include_interactive_examples: bool = True
    include_sdk_examples: bool = True
    supported_languages: List[str] = Field(default=["python", "javascript", "curl", "java"])
    theme: str = "modern"


class DeveloperPortal:
    """Comprehensive developer portal generator."""

    def __init__(self, config: DeveloperPortalConfig):
        self.config = config
        self.template_env: Optional[jinja2.Environment] = None
        
        # Create output directory
        Path(config.output_dir).mkdir(parents=True, exist_ok=True)
        
        # Setup Jinja2 environment
        self._setup_template_env()

    def _setup_template_env(self) -> None:
        """Setup Jinja2 template environment."""
        template_dir = Path(__file__).parent / "templates"
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader([template_dir]),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )

    def generate_tutorials(self) -> List[Tutorial]:
        """Generate comprehensive tutorial content."""
        tutorials = []
        
        # Getting Started Tutorials
        tutorials.append(Tutorial(
            id="getting-started-authentication",
            title="Authentication & First API Call",
            description="Learn how to authenticate with RaptorFlow API and make your first request",
            level=TutorialLevel.BEGINNER,
            type=TutorialType.GETTING_STARTED,
            estimated_time="15 minutes",
            learning_objectives=[
                "Understand JWT authentication",
                "Make your first API request",
                "Handle authentication errors",
                "Set up your development environment"
            ],
            sections=[
                {
                    "title": "Setting Up Your Account",
                    "content": "Before you can use the RaptorFlow API, you need to set up your account and get your API credentials...",
                    "steps": [
                        "Sign up for a RaptorFlow account",
                        "Navigate to the API dashboard",
                        "Generate your API key",
                        "Note down your credentials securely"
                    ]
                },
                {
                    "title": "Understanding JWT Authentication",
                    "content": "RaptorFlow uses JWT (JSON Web Tokens) for authentication. Here's how it works...",
                    "steps": [
                        "Login with your credentials",
                        "Receive access and refresh tokens",
                        "Include access token in API requests",
                        "Refresh token when it expires"
                    ]
                },
                {
                    "title": "Making Your First API Call",
                    "content": "Now let's make your first authenticated API call to get your user profile...",
                    "steps": [
                        "Set up your HTTP client",
                        "Add authentication headers",
                        "Make the API request",
                        "Handle the response"
                    ]
                }
            ],
            code_examples=[
                {
                    "language": "python",
                    "title": "Python Authentication Example",
                    "code": '''
import requests
import json

# Login to get access token
login_url = "https://api.raptorflow.com/auth/login"
credentials = {
    "email": "your-email@example.com",
    "password": "your-password"
}

response = requests.post(login_url, json=credentials)

if response.status_code == 200:
    data = response.json()
    access_token = data["data"]["access_token"]
    
    # Make authenticated request
    headers = {"Authorization": f"Bearer {access_token}"}
    user_response = requests.get("https://api.raptorflow.com/users/me", headers=headers)
    
    if user_response.status_code == 200:
        user_data = user_response.json()
        print(f"Welcome, {user_data['data']['name']}!")
else:
    print(f"Login failed: {response.text}")
                    '''
                },
                {
                    "language": "javascript",
                    "title": "JavaScript Authentication Example",
                    "code": '''
// Login to get access token
const loginUrl = "https://api.raptorflow.com/auth/login";
const credentials = {
    email: "your-email@example.com",
    password: "your-password"
};

fetch(loginUrl, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(credentials)
})
.then(response => response.json())
.then(data => {
    const accessToken = data.data.access_token;
    
    // Make authenticated request
    const headers = {'Authorization': `Bearer ${accessToken}`};
    return fetch('https://api.raptorflow.com/users/me', {headers});
})
.then(response => response.json())
.then(userData => {
    console.log(`Welcome, ${userData.data.name}!`);
})
.catch(error => console.error('Error:', error));
                    '''
                }
            ]
        ))
        
        tutorials.append(Tutorial(
            id="workspace-management",
            title="Workspace Management",
            description="Learn how to create, manage, and organize workspaces for your business intelligence activities",
            level=TutorialLevel.BEGINNER,
            type=TutorialType.GETTING_STARTED,
            estimated_time="20 minutes",
            learning_objectives=[
                "Create and configure workspaces",
                "Manage workspace settings",
                "Understand workspace isolation",
                "Handle workspace permissions"
            ],
            sections=[
                {
                    "title": "Understanding Workspaces",
                    "content": "Workspaces are the primary container for your business data and AI agents...",
                    "steps": [
                        "Learn workspace concepts",
                        "Understand workspace isolation",
                        "Review workspace types",
                        "Plan your workspace structure"
                    ]
                },
                {
                    "title": "Creating Your First Workspace",
                    "content": "Let's create your first workspace and configure it for your needs...",
                    "steps": [
                        "Choose workspace type",
                        "Set basic configuration",
                        "Configure AI settings",
                        "Invite team members"
                    ]
                }
            ],
            code_examples=[
                {
                    "language": "python",
                    "title": "Create Workspace Example",
                    "code": '''
import requests

# Create a new workspace
headers = {"Authorization": "Bearer YOUR_ACCESS_TOKEN"}
workspace_data = {
    "name": "My Business Workspace",
    "description": "Workspace for market research and analysis",
    "subscription_tier": "pro"
}

response = requests.post(
    "https://api.raptorflow.com/workspaces",
    json=workspace_data,
    headers=headers
)

if response.status_code == 201:
    workspace = response.json()["data"]
    print(f"Created workspace: {workspace['id']}")
    print(f"Name: {workspace['name']}")
else:
    print(f"Error: {response.text}")
                    '''
                }
            ]
        ))
        
        # AI Integration Tutorials
        tutorials.append(Tutorial(
            id="vertexai-integration",
            title="VertexAI Integration & AI Agents",
            description="Learn how to integrate with VertexAI and use RaptorFlow's AI agents for business intelligence",
            level=TutorialLevel.INTERMEDIATE,
            type=TutorialType.INTEGRATION,
            estimated_time="30 minutes",
            learning_objectives=[
                "Understand VertexAI integration",
                "Execute AI agents",
                "Configure AI models",
                "Process AI responses"
            ],
            prerequisites=["Authentication setup", "Workspace creation"],
            sections=[
                {
                    "title": "VertexAI Overview",
                    "content": "RaptorFlow uses Google VertexAI as its primary AI provider. Here's what you need to know...",
                    "steps": [
                        "Understand VertexAI models",
                        "Review model capabilities",
                        "Learn about model parameters",
                        "Understand pricing and limits"
                    ]
                },
                {
                    "title": "Executing Market Research Agent",
                    "content": "Use the market research agent to analyze market trends and competitive intelligence...",
                    "steps": [
                        "Prepare your research query",
                        "Configure agent parameters",
                        "Execute the agent",
                        "Process the results"
                    ]
                },
                {
                    "title": "Content Creation with AI",
                    "content": "Generate marketing content, blog posts, and other materials using AI agents...",
                    "steps": [
                        "Define content requirements",
                        "Set content parameters",
                        "Generate content",
                        "Review and refine"
                    ]
                }
            ],
            code_examples=[
                {
                    "language": "python",
                    "title": "VertexAI Market Research Example",
                    "code": '''
import requests

# Execute market research agent
headers = {"Authorization": "Bearer YOUR_ACCESS_TOKEN"}
agent_request = {
    "workspace_id": "YOUR_WORKSPACE_ID",
    "input": "Analyze market trends for SaaS companies in 2024",
    "context": {
        "industry": "technology",
        "region": "north_america",
        "timeframe": "last_6_months"
    },
    "options": {
        "model": "gemini-pro",
        "max_tokens": 1000,
        "temperature": 0.7,
        "include_sources": True
    }
}

response = requests.post(
    "https://api.raptorflow.com/agents/market_research/execute",
    json=agent_request,
    headers=headers
)

if response.status_code == 200:
    result = response.json()["data"]
    print(f"Analysis: {result['output']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Sources found: {len(result.get('sources', []))}")
    
    # Display sources
    for source in result.get('sources', []):
        print(f"- {source['title']}: {source['url']}")
else:
    print(f"Error: {response.text}")
                    '''
                }
            ]
        ))
        
        # Advanced Features Tutorials
        tutorials.append(Tutorial(
            id="advanced-workflows",
            title="Advanced Workflows & Automation",
            description="Learn how to create complex workflows and automate business intelligence processes",
            level=TutorialLevel.ADVANCED,
            type=TutorialType.ADVANCED_FEATURES,
            estimated_time="45 minutes",
            learning_objectives=[
                "Create custom workflows",
                "Automate data processing",
                "Set up triggers and actions",
                "Monitor workflow execution"
            ],
            prerequisites=["Authentication setup", "Workspace management", "Basic AI integration"],
            sections=[
                {
                    "title": "Workflow Architecture",
                    "content": "Understand how RaptorFlow workflows are structured and executed...",
                    "steps": [
                        "Learn workflow components",
                        "Understand execution flow",
                        "Review error handling",
                        "Plan workflow design"
                    ]
                },
                {
                    "title": "Building Custom Workflows",
                    "content": "Create your own custom workflows for specific business needs...",
                    "steps": [
                        "Define workflow goals",
                        "Design workflow steps",
                        "Implement logic and conditions",
                        "Test and deploy"
                    ]
                }
            ],
            code_examples=[
                {
                    "language": "python",
                    "title": "Custom Workflow Example",
                    "code": '''
import requests

# Create a custom analysis workflow
headers = {"Authorization": "Bearer YOUR_ACCESS_TOKEN"}
workflow_definition = {
    "name": "Competitive Analysis Workflow",
    "description": "Automated competitive intelligence gathering",
    "steps": [
        {
            "name": "market_research",
            "agent": "market_research",
            "input": "Analyze competitive landscape for {{industry}}",
            "parameters": {"max_tokens": 500}
        },
        {
            "name": "content_generation",
            "agent": "content_creator",
            "input": "Create competitive analysis report based on: {{market_research.output}}",
            "parameters": {"content_type": "report", "tone": "professional"}
        }
    ],
    "triggers": ["weekly", "market_change"]
}

response = requests.post(
    "https://api.raptorflow.com/workflows/create",
    json=workflow_definition,
    headers=headers
)

if response.status_code == 201:
    workflow = response.json()["data"]
    print(f"Created workflow: {workflow['id']}")
else:
    print(f"Error: {response.text}")
                    '''
                }
            ]
        ))
        
        return tutorials

    def generate_quick_start_guides(self) -> List[Dict[str, Any]]:
        """Generate quick start guides for different use cases."""
        guides = [
            {
                "id": "quick-start-python",
                "title": "Quick Start with Python",
                "description": "Get up and running with RaptorFlow API in 5 minutes using Python",
                "language": "python",
                "steps": [
                    {
                        "title": "Install Required Packages",
                        "code": '''
pip install requests
pip install python-dotenv
                        '''
                    },
                    {
                        "title": "Set Up Environment",
                        "code": '''
import os
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = "https://api.raptorflow.com"
API_EMAIL = os.getenv("RAPTORFLOW_EMAIL")
API_PASSWORD = os.getenv("RAPTORFLOW_PASSWORD")
                        '''
                    },
                    {
                        "title": "Authenticate and Make Request",
                        "code": '''
import requests

# Login
login_response = requests.post(f"{API_BASE_URL}/auth/login", json={
    "email": API_EMAIL,
    "password": API_PASSWORD
})

token = login_response.json()["data"]["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Get user profile
user_response = requests.get(f"{API_BASE_URL}/users/me", headers=headers)
print(f"Welcome, {user_response.json()['data']['name']}!")
                        '''
                    }
                ]
            },
            {
                "id": "quick-start-javascript",
                "title": "Quick Start with JavaScript",
                "description": "Get up and running with RaptorFlow API in 5 minutes using JavaScript",
                "language": "javascript",
                "steps": [
                    {
                        "title": "Set Up Your Project",
                        "code": '''
npm init -y
npm install node-fetch
                        '''
                    },
                    {
                        "title": "Create API Client",
                        "code": '''
const fetch = require('node-fetch');

class RaptorFlowAPI {
    constructor(baseUrl = 'https://api.raptorflow.com') {
        this.baseUrl = baseUrl;
        this.token = null;
    }
    
    async login(email, password) {
        const response = await fetch(`${this.baseUrl}/auth/login`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({email, password})
        });
        
        const data = await response.json();
        this.token = data.data.access_token;
        return data;
    }
    
    async getUserProfile() {
        const response = await fetch(`${this.baseUrl}/users/me`, {
            headers: {'Authorization': `Bearer ${this.token}`}
        });
        
        return response.json();
    }
}
                        '''
                    },
                    {
                        "title": "Use the API",
                        "code': '''
const api = new RaptorFlowAPI();

await api.login('your-email@example.com', 'your-password');
const profile = await api.getUserProfile();
console.log(`Welcome, ${profile.data.name}!`);
                        '''
                    }
                ]
            },
            {
                "id": "quick-start-curl",
                "title": "Quick Start with cURL",
                "description": "Get up and running with RaptorFlow API in 5 minutes using cURL",
                "language": "bash",
                "steps": [
                    {
                        "title": "Login and Get Token",
                        "code": '''
curl -X POST https://api.raptorflow.com/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{"email":"your-email@example.com","password":"your-password"}' \\
  -c cookies.txt
                        '''
                    },
                    {
                        "title": "Make Authenticated Request",
                        "code": '''
curl -X GET https://api.raptorflow.com/users/me \\
  -H "Content-Type: application/json" \\
  -b cookies.txt
                        '''
                    }
                ]
            }
        ]
        
        return guides

    def generate_sdk_examples(self) -> List[Dict[str, Any]]:
        """Generate SDK examples for different languages."""
        return [
            {
                "language": "python",
                "title": "Python SDK",
                "description": "Official Python SDK for RaptorFlow API",
                "installation": "pip install raptorflow-sdk",
                "example": '''
from raptorflow import RaptorFlowClient

# Initialize client
client = RaptorFlowClient(
    email="your-email@example.com",
    password="your-password"
)

# Get user profile
user = client.users.get_me()
print(f"Welcome, {user.name}!")

# Create workspace
workspace = client.workspaces.create(
    name="My Workspace",
    description="Test workspace"
)

# Execute AI agent
result = client.agents.market_research.execute(
    workspace_id=workspace.id,
    input="Analyze SaaS market trends",
    options={"model": "gemini-pro"}
)
                '''
            },
            {
                "language": "javascript",
                "title": "JavaScript SDK",
                "description": "Official JavaScript SDK for RaptorFlow API",
                "installation": "npm install raptorflow-sdk",
                "example": '''
const { RaptorFlowClient } = require('raptorflow-sdk');

// Initialize client
const client = new RaptorFlowClient({
    email: 'your-email@example.com',
    password: 'your-password'
});

// Get user profile
const user = await client.users.getMe();
console.log(`Welcome, ${user.name}!`);

// Create workspace
const workspace = await client.workspaces.create({
    name: 'My Workspace',
    description: 'Test workspace'
});

// Execute AI agent
const result = await client.agents.marketResearch.execute({
    workspaceId: workspace.id,
    input: 'Analyze SaaS market trends',
    options: { model: 'gemini-pro' }
});
                '''
            },
            {
                "language": "java",
                "title": "Java SDK",
                "description": "Official Java SDK for RaptorFlow API",
                "installation": '''
<dependency>
    <groupId>com.raptorflow</groupId>
    <artifactId>raptorflow-sdk</artifactId>
    <version>1.0.0</version>
</dependency>
                ''',
                "example": '''
import com.raptorflow.RaptorFlowClient;
import com.raptorflow.models.User;
import com.raptorflow.models.Workspace;

// Initialize client
RaptorFlowClient client = new RaptorFlowClient(
    "your-email@example.com",
    "your-password"
);

// Get user profile
User user = client.users().getMe();
System.out.println("Welcome, " + user.getName() + "!");

// Create workspace
Workspace workspace = client.workspaces().create(
    Workspace.builder()
        .name("My Workspace")
        .description("Test workspace")
        .build()
);

// Execute AI agent
AgentResult result = client.agents().marketResearch().execute(
    MarketResearchRequest.builder()
        .workspaceId(workspace.getId())
        .input("Analyze SaaS market trends")
        .options(AgentOptions.builder()
            .model("gemini-pro")
            .build())
        .build()
);
                '''
            }
        ]

    def generate_portal_html(self) -> str:
        """Generate the complete developer portal HTML."""
        tutorials = self.generate_tutorials()
        quick_guides = self.generate_quick_start_guides()
        sdk_examples = self.generate_sdk_examples()
        
        template_str = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ config.company_name }} Developer Portal</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-core.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/autoloader/prism-autoloader.min.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.css" rel="stylesheet">
    <style>
        .tutorial-card { transition: all 0.3s ease; }
        .tutorial-card:hover { transform: translateY(-4px); box-shadow: 0 10px 25px rgba(0,0,0,0.1); }
        .level-badge { font-size: 0.75rem; padding: 0.25rem 0.75rem; border-radius: 9999px; font-weight: 600; }
        .level-beginner { background: #10b981; color: white; }
        .level-intermediate { background: #f59e0b; color: white; }
        .level-advanced { background: #ef4444; color: white; }
        .level-expert { background: #8b5cf6; color: white; }
        .code-block { background: #1f2937; border-radius: 0.5rem; overflow-x: auto; }
        .interactive-demo { border: 2px solid #e5e7eb; border-radius: 0.5rem; }
    </style>
</head>
<body class="bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center py-6">
                <div>
                    <h1 class="text-3xl font-bold text-gray-900">{{ config.company_name }} Developer Portal</h1>
                    <p class="text-gray-600 mt-1">{{ config.product_name }} v{{ config.version }}</p>
                </div>
                <nav class="hidden md:flex space-x-8">
                    <a href="#quick-start" class="text-gray-600 hover:text-gray-900">Quick Start</a>
                    <a href="#tutorials" class="text-gray-600 hover:text-gray-900">Tutorials</a>
                    <a href="#sdk" class="text-gray-600 hover:text-gray-900">SDKs</a>
                    <a href="#examples" class="text-gray-600 hover:text-gray-900">Examples</a>
                </nav>
            </div>
        </div>
    </header>

    <!-- Hero Section -->
    <section class="bg-gradient-to-r from-blue-600 to-purple-600 text-white py-16">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 class="text-4xl font-bold mb-4">Build Amazing Applications with {{ config.product_name }}</h2>
            <p class="text-xl mb-8">Comprehensive documentation, tutorials, and examples to get you started quickly</p>
            <div class="flex justify-center space-x-4">
                <a href="#quick-start" class="bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100">Get Started</a>
                <a href="#tutorials" class="border-2 border-white text-white px-6 py-3 rounded-lg font-semibold hover:bg-white hover:text-blue-600">View Tutorials</a>
            </div>
        </div>
    </section>

    <!-- Quick Start Section -->
    <section id="quick-start" class="py-16">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <h2 class="text-3xl font-bold text-center mb-12">Quick Start Guides</h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                {% for guide in quick_guides %}
                <div class="bg-white rounded-lg shadow-md p-6">
                    <div class="flex items-center mb-4">
                        <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mr-4">
                            <i class="fas fa-code text-blue-600"></i>
                        </div>
                        <div>
                            <h3 class="text-lg font-semibold">{{ guide.title }}</h3>
                            <span class="text-sm text-gray-600">{{ guide.language }}</span>
                        </div>
                    </div>
                    <p class="text-gray-600 mb-4">{{ guide.description }}</p>
                    <div class="space-y-4">
                        {% for step in guide.steps %}
                        <div>
                            <h4 class="font-medium mb-2">{{ step.title }}</h4>
                            <div class="code-block">
                                <pre><code class="language-{{ guide.language }}">{{ step.code }}</code></pre>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </section>

    <!-- Tutorials Section -->
    <section id="tutorials" class="py-16 bg-gray-100">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <h2 class="text-3xl font-bold text-center mb-12">Interactive Tutorials</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {% for tutorial in tutorials %}
                <div class="tutorial-card bg-white rounded-lg shadow-md p-6">
                    <div class="flex items-center justify-between mb-4">
                        <span class="level-badge level-{{ tutorial.level.value }}">{{ tutorial.level.value.title() }}</span>
                        <span class="text-sm text-gray-600">{{ tutorial.estimated_time }}</span>
                    </div>
                    <h3 class="text-xl font-semibold mb-2">{{ tutorial.title }}</h3>
                    <p class="text-gray-600 mb-4">{{ tutorial.description }}</p>
                    
                    <div class="mb-4">
                        <h4 class="font-medium mb-2">What you'll learn:</h4>
                        <ul class="text-sm text-gray-600 space-y-1">
                            {% for objective in tutorial.learning_objectives[:3] %}
                            <li class="flex items-start">
                                <i class="fas fa-check text-green-500 mr-2 mt-1"></i>
                                {{ objective }}
                            </li>
                            {% endfor %}
                        </ul>
                    </div>
                    
                    {% if tutorial.prerequisites %}
                    <div class="mb-4">
                        <h4 class="font-medium mb-2">Prerequisites:</h4>
                        <div class="flex flex-wrap gap-2">
                            {% for prereq in tutorial.prerequisites %}
                            <span class="text-xs bg-gray-200 text-gray-700 px-2 py-1 rounded">{{ prereq }}</span>
                            {% endfor %}
                        </div>
                    </div>
                    {% endif %}
                    
                    <button class="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700" 
                            onclick="openTutorial('{{ tutorial.id }}')">
                        Start Tutorial
                    </button>
                </div>
                {% endfor %}
            </div>
        </div>
    </section>

    <!-- SDK Section -->
    <section id="sdk" class="py-16">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <h2 class="text-3xl font-bold text-center mb-12">Official SDKs</h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                {% for sdk in sdk_examples %}
                <div class="bg-white rounded-lg shadow-md p-6">
                    <div class="flex items-center mb-4">
                        <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mr-4">
                            <i class="fas fa-package text-purple-600"></i>
                        </div>
                        <div>
                            <h3 class="text-lg font-semibold">{{ sdk.title }}</h3>
                            <span class="text-sm text-gray-600">{{ sdk.language }}</span>
                        </div>
                    </div>
                    <p class="text-gray-600 mb-4">{{ sdk.description }}</p>
                    
                    <div class="mb-4">
                        <h4 class="font-medium mb-2">Installation:</h4>
                        <div class="code-block">
                            <pre><code class="language-bash">{{ sdk.installation }}</code></pre>
                        </div>
                    </div>
                    
                    <div class="mb-4">
                        <h4 class="font-medium mb-2">Example:</h4>
                        <div class="code-block max-h-64 overflow-y-auto">
                            <pre><code class="language-{{ sdk.language }}">{{ sdk.example }}</code></pre>
                        </div>
                    </div>
                    
                    <button class="w-full bg-purple-600 text-white py-2 rounded-lg hover:bg-purple-700">
                        View Documentation
                    </button>
                </div>
                {% endfor %}
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="bg-gray-800 text-white py-12">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
                <div>
                    <h3 class="text-lg font-semibold mb-4">{{ config.company_name }}</h3>
                    <p class="text-gray-400">Building the future of business intelligence with AI.</p>
                </div>
                <div>
                    <h4 class="font-semibold mb-4">Resources</h4>
                    <ul class="space-y-2 text-gray-400">
                        <li><a href="#" class="hover:text-white">API Documentation</a></li>
                        <li><a href="#" class="hover:text-white">SDK Documentation</a></li>
                        <li><a href="#" class="hover:text-white">Examples</a></li>
                        <li><a href="#" class="hover:text-white">Community</a></li>
                    </ul>
                </div>
                <div>
                    <h4 class="font-semibold mb-4">Support</h4>
                    <ul class="space-y-2 text-gray-400">
                        <li><a href="#" class="hover:text-white">Help Center</a></li>
                        <li><a href="#" class="hover:text-white">Contact Us</a></li>
                        <li><a href="#" class="hover:text-white">Status Page</a></li>
                        <li><a href="#" class="hover:text-white">GitHub</a></li>
                    </ul>
                </div>
                <div>
                    <h4 class="font-semibold mb-4">Connect</h4>
                    <div class="flex space-x-4">
                        <a href="#" class="text-gray-400 hover:text-white"><i class="fab fa-twitter"></i></a>
                        <a href="#" class="text-gray-400 hover:text-white"><i class="fab fa-github"></i></a>
                        <a href="#" class="text-gray-400 hover:text-white"><i class="fab fa-discord"></i></a>
                        <a href="#" class="text-gray-400 hover:text-white"><i class="fab fa-linkedin"></i></a>
                    </div>
                </div>
            </div>
            <div class="mt-8 pt-8 border-t border-gray-700 text-center text-gray-400">
                <p>&copy; 2024 {{ config.company_name }}. All rights reserved.</p>
            </div>
        </div>
    </footer>

    <script>
        function openTutorial(tutorialId) {
            // Open tutorial modal or navigate to tutorial page
            console.log('Opening tutorial:', tutorialId);
            // Implementation for tutorial interaction
        }
        
        // Initialize code highlighting
        Prism.highlightAll();
        
        // Smooth scrolling
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    </script>
</body>
</html>
        '''
        
        template = self.template_env.from_string(template_str)
        return template.render(
            config=self.config,
            tutorials=tutorials,
            quick_guides=quick_guides,
            sdk_examples=sdk_examples
        )

    def save_portal(self) -> None:
        """Save the developer portal."""
        html_content = self.generate_portal_html()
        
        # Save main portal file
        portal_file = Path(self.config.output_dir) / "index.html"
        with open(portal_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Developer portal saved: {portal_file}")
        
        # Save tutorial data as JSON
        tutorials = self.generate_tutorials()
        tutorials_file = Path(self.config.output_dir) / "tutorials.json"
        with open(tutorials_file, 'w', encoding='utf-8') as f:
            json.dump([
                {
                    "id": t.id,
                    "title": t.title,
                    "description": t.description,
                    "level": t.level.value,
                    "type": t.type.value,
                    "estimated_time": t.estimated_time,
                    "learning_objectives": t.learning_objectives,
                    "sections": t.sections,
                    "code_examples": t.code_examples
                }
                for t in tutorials
            ], f, indent=2, ensure_ascii=False)
        
        logger.info(f"Tutorials data saved: {tutorials_file}")


# CLI usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate developer portal")
    parser.add_argument("--output-dir", default="developer_portal", help="Output directory")
    parser.add_argument("--base-url", default="https://api.raptorflow.com", help="Base API URL")
    parser.add_argument("--company", default="RaptorFlow", help="Company name")
    parser.add_argument("--product", default="Backend API", help="Product name")
    parser.add_argument("--version", default="1.0.0", help="API version")
    parser.add_argument("--theme", default="modern", help="Portal theme")
    
    args = parser.parse_args()
    
    # Create configuration
    config = DeveloperPortalConfig(
        output_dir=args.output_dir,
        base_url=args.base_url,
        company_name=args.company,
        product_name=args.product,
        version=args.version,
        theme=args.theme
    )
    
    # Generate portal
    portal = DeveloperPortal(config)
    portal.save_portal()
    
    print(f"Developer portal generated in {args.output_dir}")
    print(f"Open {args.output_dir}/index.html to view the portal")
