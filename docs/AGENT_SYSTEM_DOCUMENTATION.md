# Raptorflow Agent System Documentation

## Overview

The Raptorflow Agent System is a sophisticated, production-ready backend system that provides intelligent agent capabilities for content creation, marketing automation, and business intelligence. This documentation covers the architecture, components, and usage patterns for developers and system administrators.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Core Components](#core-components)
3. [Agent System](#agent-system)
4. [Skills System](#skills-system)
5. [Tools System](#tools-system)
6. [Performance Optimization](#performance-optimization)
7. [Security & Validation](#security--validation)
8. [Configuration](#configuration)
9. [Deployment](#deployment)
10. [Monitoring & Troubleshooting](#monitoring--troubleshooting)

---

## Architecture Overview

### System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Raptorflow Agent System                    │
├─────────────────────────────────────────────────────────────────┤
│  API Layer (FastAPI)                                         │
│  ├── Request Validation & Security                              │
│  ├── Rate Limiting & Caching                                   │
│  └── Health Monitoring                                        │
├─────────────────────────────────────────────────────────────────┤
│  Agent Dispatcher                                             │
│  ├── Request Routing Pipeline                                     │
│  ├── Agent Registry                                            │
│  └── Context Management                                       │
├─────────────────────────────────────────────────────────────────┤
│  Agent Execution Layer                                         │
│  ├── BaseAgent (Abstract)                                    │
│  ├── Specialist Agents                                         │
│  ├── Skills System                                            │
│  └── Tools System                                             │
├─────────────────────────────────────────────────────────────────┤
│  Infrastructure Layer                                         │
│  ├── LLM Manager (Google Vertex AI)                           │
│  ├── Connection Pooling (Database + Redis)                      │
│  ├── Caching System                                           │
│  ├── State Management                                         │
│  ├── Performance Optimizer                                   │
│  └── Security Validator                                        │
└─────────────────────────────────────────────────────────────────┘
```

### Key Design Principles

1. **Modularity**: Each component is independently testable and replaceable
2. **Scalability**: Built for horizontal scaling with connection pooling
3. **Security**: Zero-trust architecture with comprehensive validation
4. **Performance**: Intelligent caching and adaptive optimization
5. **Observability**: Comprehensive monitoring and health checks

---

## Core Components

### Configuration System

The configuration system provides centralized management of all system settings:

```python
from backend.config import get_config

config = get_config()
print(f"Environment: {config.environment}")
print(f"LLM Provider: {config.llm_provider}")
print(f"Database URL: {config.database_url}")
```

**Key Configuration Files:**
- `backend/config.py` - Main configuration
- `.env` - Environment variables
- `backend/config_simple.py` - Simplified configuration

### Connection Management

Connection pooling provides efficient resource management:

```python
from backend.core.connections import get_connection_manager

manager = await get_connection_manager()
stats = manager.get_stats()
print(f"Database pool: {stats['database']}")
print(f"Redis pool: {stats['redis']}")
```

### Health Monitoring

Comprehensive health monitoring for all system components:

```python
from backend.core.health import run_health_checks

health = await run_health_checks()
print(f"System status: {health.status.value}")
print(f"Active checks: {len(health.checks)}")
```

---

## Agent System

### BaseAgent Class

All agents inherit from the `BaseAgent` abstract class:

```python
from backend.agents.base import BaseAgent

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="MyAgent",
            description="Custom agent for specific tasks",
            model_tier=ModelTier.FLASH,
            tools=["web_search", "database"],
            skills=["content_generation", "analysis"]
        )
    
    def get_system_prompt(self) -> str:
        return "You are a specialized agent for..."
    
    async def execute_logic(self, state: AgentState) -> AgentState:
        # Implement agent logic here
        return self._set_output(state, "Task completed")
```

### Specialist Agents

The system includes several specialist agents:

#### ICP Architect
```python
from backend.agents.specialists.icp_architect import ICPArchitect

agent = ICPArchitect()
result = await agent.execute({
    "request": "Create an ICP for a SaaS company",
    "workspace_id": "workspace123",
    "user_id": "user456",
    "session_id": "session789"
})
```

### Agent Registry

The agent registry manages all available agents:

```python
from backend.agents.dispatcher import AgentDispatcher

dispatcher = AgentDispatcher()
agents = dispatcher.registry.list_agents()
print(f"Available agents: {agents}")
```

---

## Skills System

### Skill Categories

Skills are categorized by their function:

- **Content Generation**: Content creation and writing
- **Strategy**: Business strategy and planning
- **Operations**: Operational tasks and automation
- **Marketing**: Marketing and promotional content
- **Creative**: Creative and design tasks
- **Analysis**: Data analysis and insights

### Creating Custom Skills

```python
from backend.agents.skills.base import Skill, SkillCategory, SkillLevel

class CustomSkill(Skill):
    def __init__(self):
        super().__init__(
            name="custom_skill",
            category=SkillCategory.OPERATIONS,
            level=SkillLevel.INTERMEDIATE,
            description="Custom skill for specific tasks",
            capabilities=["Task execution", "Data processing"]
        )
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        agent = context.get("agent")
        # Implement skill logic
        return {"result": "Custom skill completed"}
```

### Using Skills in Agents

```python
# Skills are automatically available to agents
result = await agent.use_skill("content_generation", {
    "prompt": "Write a blog post about AI",
    "tone": "professional"
})
```

---

## Tools System

### Available Tools

The system includes several essential tools:

#### Web Search Tool
```python
from backend.agents.tools.web_search import WebSearchTool

tool = WebSearchTool()
result = await tool.arun(
    query="artificial intelligence trends 2024",
    max_results=10
)
```

#### Database Tool
```python
from backend.agents.tools.database import DatabaseTool

tool = DatabaseTool()
result = await tool.arun(
    table="users",
    workspace_id="workspace123",
    filters={"status": "active"},
    limit=50
)
```

### Tool Registry

```python
from backend.agents.tools.registry import get_tool_registry

registry = get_tool_registry()
tools = registry.list_tools()
print(f"Available tools: {tools}")
```

---

## Performance Optimization

### Performance Optimizer

The performance optimizer provides intelligent optimization strategies:

```python
from backend.core.performance import optimize_agent_execution

# Automatically optimize agent execution
result = await optimize_agent_execution(
    agent_name="MyAgent",
    execution_func=agent.execute,
    request_data
)
```

### Optimization Levels

- **Conservative**: Basic caching, minimal risk
- **Balanced**: Standard optimizations
- **Aggressive**: Advanced caching and parallel execution
- **Maximum**: Maximum performance optimizations

### Performance Monitoring

```python
from backend.core.performance import get_performance_stats

stats = get_performance_stats()
print(f"Average execution time: {stats['recent_performance']['avg_execution_time']}")
print(f"Cache hit rate: {stats['recent_performance']['avg_cache_hit_rate']}")
```

---

## Security & Validation

### Security Validator

Comprehensive security validation for all requests:

```python
from backend.core.security import validate_agent_request

is_valid, error = await validate_agent_request(
    request_data=request_data,
    client_ip="192.168.1.1",
    user_id="user123",
    workspace_id="workspace456"
)
```

### Security Features

- **Input Validation**: Prevents injection attacks
- **Rate Limiting**: Prevents abuse and DoS attacks
- **Threat Detection**: Identifies malicious patterns
- **Auto-blocking**: Automatically blocks malicious entities
- **Security Events**: Comprehensive logging of security events

### Security Statistics

```python
from backend.core.security import get_security_stats

stats = get_security_stats()
print(f"Total security events: {stats['total_events']}")
print(f"Blocked entities: {stats['blocked_users']}")
```

---

## Configuration

### Environment Variables

Essential environment variables:

```bash
# Application Settings
APP_NAME=Raptorflow Backend
ENVIRONMENT=production
DEBUG=false

# Server Settings
HOST=0.0.0.0
PORT=8000

# Database Configuration
DATABASE_URL=postgresql://user:pass@localhost:5432/raptorflow

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# LLM Configuration (Google Vertex AI)
GOOGLE_API_KEY=your_api_key
GOOGLE_PROJECT_ID=your_project_id
GOOGLE_REGION=us-central1

# Security
SECRET_KEY=your-secret-key-change-in-production
```

### Configuration Validation

```python
from backend.config import validate_config

if validate_config():
    print("Configuration is valid")
else:
    print("Configuration validation failed")
```

---

## Deployment

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV ENVIRONMENT=production
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  raptorflow-backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    depends_on:
      - postgres
      - redis
  
  postgres:
    image: postgres:13
    environment:
      - POSTGRES_DB=raptorflow
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:6-alpine
    volumes:
      - redis_data:/data
```

### Health Checks

```python
# Health check endpoint
GET /api/v1/agents/health

# Expected response
{
    "status": "healthy",
    "timestamp": "2024-01-01T12:00:00Z",
    "dispatcher_status": {...},
    "context_loader_status": {...},
    "registered_agents": 5
}
```

---

## Monitoring & Troubleshooting

### Health Monitoring

```python
from backend.core.health import start_health_monitoring

# Start continuous health monitoring
await start_health_monitoring(interval=60)
```

### Performance Monitoring

```python
from backend.core.performance import get_performance_stats

# Get current performance statistics
stats = get_performance_stats()
```

### Security Monitoring

```python
from backend.core.security import get_recent_security_events

# Get recent security events
events = get_recent_security_events(hours=24)
```

### Common Issues

#### High Memory Usage
- Check memory usage: `stats['recent_performance']['avg_memory_usage_mb']`
- Reduce cache TTL: Adjust `cache_ttl` in configuration
- Trigger manual cleanup: `await optimizer._memory_cleanup()`

#### Slow Execution
- Check optimization level: `stats['optimization_level']`
- Enable aggressive caching: Set `optimization_level` to "maximum"
- Monitor cache hit rate: Low hit rates indicate caching issues

#### Security Events
- Review security events: `get_recent_security_events()`
- Check blocked entities: `stats['blocked_users']`
- Adjust security policies if needed

### Logging

The system uses structured logging with appropriate levels:

```python
import logging

logger = logging.getLogger(__name__)
logger.info("Information message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")
```

---

## API Reference

### Agent Execution Endpoint

```http
POST /api/v1/agents/execute
Content-Type: application/json

{
    "request": "Create a marketing campaign",
    "workspace_id": "workspace123",
    "user_id": "user456",
    "session_id": "session789",
    "context": {},
    "agent_hint": "marketing_agent",
    "fast_mode": false
}
```

### Health Check Endpoint

```http
GET /api/v1/agents/health
```

### Agent List Endpoint

```http
GET /api/v1/agents
Authorization: Bearer <token>
```

### Performance Stats Endpoint

```http
GET /api/v1/agents/stats
Authorization: Bearer <token>
```

---

## Development Guide

### Adding New Agents

1. Create agent class inheriting from `BaseAgent`
2. Implement required methods: `get_system_prompt()` and `execute_logic()`
3. Register agent in dispatcher
4. Add tests

### Adding New Skills

1. Create skill class inheriting from `Skill`
2. Implement `execute()` method
3. Register skill in skills registry
4. Add to agent's skill list

### Adding New Tools

1. Create tool class inheriting from `BaseTool`
2. Implement `arun()` method
3. Register tool in tool registry
4. Add to agent's tool list

### Testing

```python
# Unit test example
import pytest
from backend.agents.base import BaseAgent

class TestAgent(BaseAgent):
    def __init__(self):
        super().__init__("TestAgent", "Test agent", ModelTier.FLASH)

    def get_system_prompt(self) -> str:
        return "You are a test agent"

    async def execute_logic(self, state):
        return self._set_output(state, "Test completed")

@pytest.mark.asyncio
async def test_agent_execution():
    agent = TestAgent()
    state = {"workspace_id": "test", "user_id": "test", "session_id": "test"}
    result = await agent.execute(state)
    assert result["output"] == "Test completed"
```

---

## Best Practices

### Performance

1. **Use Caching**: Enable caching for repeated requests
2. **Connection Pooling**: Use connection pools for database and Redis
3. **Optimization Levels**: Start with conservative, adjust based on performance
4. **Resource Management**: Clean up resources after execution

### Security

1. **Input Validation**: Always validate user input
2. **Rate Limiting**: Implement rate limiting for all endpoints
3. **Authentication**: Require proper authentication for sensitive operations
4. **Monitoring**: Monitor security events and adjust policies

### Error Handling

1. **Graceful Degradation**: Handle errors gracefully
2. **Logging**: Log errors with appropriate context
3. **Recovery**: Implement error recovery mechanisms
4. **Timeouts**: Use appropriate timeouts for all operations

### Monitoring

1. **Health Checks**: Implement health checks for all components
2. **Performance Metrics**: Monitor execution time, memory usage, cache hit rates
3. **Security Events**: Monitor security events and threats
4. **Alerting**: Set up alerts for critical issues

---

## Support

For support, questions, or contributions:

1. **Documentation**: Check this documentation first
2. **Issues**: Report issues on the project repository
3. **Discussions**: Join community discussions
4. **Contributions**: Follow contribution guidelines

---

## Version History

- **v1.0.0**: Initial production release
- **v1.1.0**: Added performance optimization
- **v1.2.0**: Enhanced security features
- **v1.3.0**: Improved monitoring and health checks

---

*This documentation covers the Raptorflow Agent System as of version 1.3.0. For the latest updates, please check the source code and inline documentation.*
