# RaptorFlow Backend Documentation

## Overview

RaptorFlow Backend is a comprehensive AI-powered business intelligence platform that provides end-to-end workflow orchestration, cognitive processing, and intelligent automation. This documentation covers the complete system architecture, implementation details, and operational procedures.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [System Components](#system-components)
- [API Documentation](#api-documentation)
- [Deployment Guide](#deployment-guide)
- [Development Guide](#development-guide)
- [Operations Guide](#operations-guide)
- [Security Guide](#security-guide)
- [Troubleshooting](#troubleshooting)

## Architecture Overview

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend UI    │    │   Mobile App    │    │   External API  │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                    │                    │
          └────────────────────┼────────────────────┘
                               │
                    ┌─────────┴─────────┐
                    │   API Gateway   │
                    │   (FastAPI)      │
                    └─────────┬─────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
    ┌─────┴─────┐    ┌─────┴─────┐    ┌─────┴─────┐
    │  Agents   │    │  Cognitive │    │  Memory   │
    │  System   │    │  Engine   │    │  System   │
    └─────┬─────┘    └─────┬─────┘    └─────┬─────┘
          │                   │                   │
          └───────────────────┼───────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │  Data Layer      │
                    │ (PostgreSQL +     │
                    │  Redis +          │
                    │  Vector DB)       │
                    └───────────────────┘
```

### Core Components

1. **API Gateway** - FastAPI-based REST API with authentication, rate limiting, and request routing
2. **Agent System** - Specialized AI agents for different business functions
3. **Cognitive Engine** - Perception, planning, reflection, and adversarial critic modules
4. **Memory System** - Vector memory, graph memory, episodic memory, and working memory
5. **Database Layer** - PostgreSQL for structured data, Redis for caching, pgvector for vector storage
6. **Integration Layer** - Cross-module coordination and workflow orchestration

## System Components

### API Gateway (`backend/main.py`)

The API Gateway serves as the entry point for all client requests and provides:

- **Authentication & Authorization**: JWT-based auth with role-based access control
- **Request Routing**: Intelligent routing to appropriate agents and workflows
- **Rate Limiting**: Per-user and per-workspace rate limiting
- **Middleware**: Logging, error handling, metrics collection
- **Health Checks**: Comprehensive system health monitoring

### Agent System (`backend/agents/`)

The Agent System consists of specialized AI agents:

- **Market Research Agent**: Market analysis and competitive intelligence
- **Content Creator Agent**: Content generation and optimization
- **ICP Architect Agent**: Ideal Customer Profile creation and management
- **Move Strategist Agent**: Strategic move planning and execution
- **Campaign Planner Agent**: Campaign orchestration and management
- **Daily Wins Agent**: Daily content generation and scheduling
- **Analytics Agent**: Data analysis and insights generation
- **Competitor Intel Agent**: Competitive intelligence gathering

### Cognitive Engine (`backend/cognitive/`)

The Cognitive Engine provides AI-powered processing capabilities:

- **Perception Module**: Natural language understanding and entity extraction
- **Planning Module**: Goal-oriented planning and task decomposition
- **Reflection Module**: Quality assessment and improvement suggestions
- **HITL Module**: Human-in-the-loop approval and feedback
- **Adversarial Critic**: Risk assessment and critical analysis

### Memory System (`backend/memory/`)

The Memory System provides comprehensive data storage and retrieval:

- **Vector Memory**: Semantic search and similarity matching
- **Graph Memory**: Relationship mapping and network analysis
- **Episodic Memory**: Event-based memory storage and retrieval
- **Working Memory**: Short-term context management
- **Memory Controller**: Unified memory access and coordination

### Database Layer

- **PostgreSQL**: Primary database for structured data
- **Redis**: Caching and session management
- **pgvector**: Vector similarity search
- **Supabase**: Database-as-a-Service with RLS policies

## API Documentation

### Authentication Endpoints

#### POST `/auth/login`
Authenticate user and return access token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "user_123",
    "email": "user@example.com",
    "subscription_tier": "pro"
  }
}
```

#### POST `/auth/refresh`
Refresh access token.

**Request Headers:**
```
Authorization: Bearer <refresh_token>
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Workspace Endpoints

#### GET `/workspaces`
List user's workspaces.

**Response:**
```json
{
  "workspaces": [
    {
      "id": "workspace_123",
      "name": "My Business",
      "created_at": "2024-01-01T00:00:00Z",
      "subscription_tier": "pro"
    }
  ]
}
```

#### POST `/workspaces`
Create new workspace.

**Request Body:**
```json
{
  "name": "New Business",
  "description": "Business description"
}
```

**Response:**
```json
{
  "id": "workspace_456",
  "name": "New Business",
  "description": "Business description",
  "created_at": "2024-01-01T00:00:00Z",
  "subscription_tier": "free"
}
```

### Agent Endpoints

#### POST `/agents/{agent_name}/execute`
Execute agent with specified parameters.

**Request Body:**
```json
{
  "workspace_id": "workspace_123",
  "input": "Analyze market trends for SaaS companies",
  "context": {
    "industry": "technology",
    "region": "north_america"
  }
}
```

**Response:**
```json
{
  "success": true,
  "output": "Market analysis results...",
  "tokens_used": 150,
  "execution_time": 2.5,
  "agent_name": "market_research"
}
```

### Workflow Endpoints

#### POST `/workflows/onboarding/step/{step}`
Execute onboarding workflow step.

**Request Body:**
```json
{
  "workspace_id": "workspace_123",
  "data": {
    "files": [{"filename": "business_plan.pdf"}]
  }
}
```

**Response:**
```json
{
  "success": true,
  "step": "evidence_upload",
  "next_step": "evidence_extraction",
  "progress": {
    "total_steps": 13,
    "completed_steps": 1,
    "progress_percentage": 7.69
  }
}
```

## Deployment Guide

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose
- GCP Account (for production deployment)

### Local Development Setup

1. **Clone Repository**
   ```bash
   git clone https://github.com/raptorflow-dev/Raptorflow.git
   cd Raptorflow/backend
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Start Services with Docker Compose**
   ```bash
   docker-compose up -d
   ```

6. **Run Database Migrations**
   ```bash
   python apply_migrations.py
   ```

7. **Start Application**
   ```bash
   python main.py
   ```

### Production Deployment

#### Using Docker Compose

1. **Configure Environment**
   ```bash
   cp .env.example .env.production
   # Edit .env.production with production values
   ```

2. **Deploy**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

#### Using GCP Cloud Run

1. **Build and Push Image**
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/raptorflow-backend:latest
   ```

2. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy raptorflow-backend \
     --image gcr.io/PROJECT_ID/raptorflow-backend:latest \
     --region us-central1 \
     --platform managed \
     --allow-unauthenticated \
     --set-env-vars ENVIRONMENT=production
   ```

#### Using Kubernetes

1. **Apply Kubernetes Manifests**
   ```bash
   kubectl apply -f deployment/kubernetes/
   ```

2. **Monitor Deployment**
   ```bash
   kubectl get pods -l app=raptorflow-backend
   ```

## Development Guide

### Code Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── dependencies.py         # Dependency injection
├── middleware/            # Custom middleware
├── api/                   # API endpoints
├── agents/                # AI agents
├── cognitive/             # Cognitive engine
├── memory/                # Memory system
├── workflows/             # Workflow orchestrators
├── integration/           # Cross-module integration
├── tests/                 # Test suite
├── deployment/            # Deployment configurations
└── docs/                  # Documentation
```

### Adding New Agents

1. **Create Agent Class**
   ```python
   # backend/agents/specialists/new_agent.py
   from agents.base import BaseAgent

   class NewAgent(BaseAgent):
       def __init__(self):
           super().__init__(
               name="new_agent",
               description="Description of the new agent"
           )
   ```

2. **Register Agent**
   ```python
   # backend/agents/dispatcher.py
   from agents.specialists.new_agent import NewAgent

   class AgentDispatcher:
       def __init__(self):
           self.agents = {
               "new_agent": NewAgent(),
               # ... other agents
           }
   ```

3. **Add Tests**
   ```python
   # backend/tests/test_new_agent.py
   import pytest
   from agents.specialists.new_agent import NewAgent

   def test_new_agent():
       agent = NewAgent()
       assert agent.name == "new_agent"
   ```

### Adding New Workflows

1. **Create Workflow Class**
   ```python
   # backend/workflows/new_workflow.py
   class NewWorkflow:
       def __init__(self, db_client, memory_controller, cognitive_engine, agent_dispatcher):
           # Initialize dependencies
           pass

       async def execute(self, workspace_id: str, params: Dict[str, Any]):
           # Implement workflow logic
           pass
   ```

2. **Add API Endpoints**
   ```python
   # backend/api/v1/workflows.py
   @router.post("/workflows/new_workflow")
   async def execute_new_workflow(request: NewWorkflowRequest):
       workflow = NewWorkflow(...)
       result = await workflow.execute(request.workspace_id, request.dict())
       return result
   ```

### Testing

#### Unit Tests
```bash
python -m pytest tests/test_unit.py -v
```

#### Integration Tests
```bash
python -m pytest tests/test_integration.py -v
```

#### End-to-End Tests
```bash
python -m pytest tests/test_e2e.py -v
```

#### Performance Tests
```bash
python -m pytest tests/test_performance.py -v
```

### Code Quality

#### Linting
```bash
flake8 backend/
black backend/
isort backend/
```

#### Type Checking
```bash
mypy backend/
```

#### Security Scanning
```bash
bandit -r backend/
safety check
```

## Operations Guide

### Monitoring

#### Health Checks
- **Endpoint**: `/health`
- **Components**: Database, Redis, Memory, Cognitive Engine, Agents
- **Status**: UP/DOWN with detailed component status

#### Metrics
- **Prometheus**: Available at `/metrics`
- **Grafana Dashboard**: Pre-configured dashboards for system monitoring
- **Key Metrics**: Request rate, response time, error rate, resource usage

#### Logging
- **Structured JSON Logs**: All logs in structured format
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Log Aggregation**: Centralized logging with Cloud Logging

#### Alerting
- **Critical Alerts**: Service down, high error rate, security incidents
- **Warning Alerts**: High response time, resource usage warnings
- **Notification Channels**: Email, Slack, PagerDuty

### Backup and Recovery

#### Database Backups
- **Frequency**: Daily full backups, hourly incremental
- **Retention**: 30 days
- **Location**: GCS Cloud Storage
- **Encryption**: Encrypted at rest and in transit

#### Disaster Recovery
- **RTO**: 4 hours (Recovery Time Objective)
- **RPO**: 1 hour (Recovery Point Objective)
- **Failover**: Multi-region deployment
- **Testing**: Quarterly disaster recovery drills

### Scaling

#### Horizontal Scaling
- **Auto-scaling**: Based on CPU and memory metrics
- **Load Balancing**: Cloud Load Balancer with health checks
- **Database**: Read replicas for read-heavy workloads

#### Vertical Scaling
- **Resource Allocation**: Dynamic resource allocation
- **Performance Tuning**: Database and cache optimization
- **Memory Management**: Efficient memory usage patterns

## Security Guide

### Authentication & Authorization

#### JWT Authentication
- **Access Tokens**: 30-minute expiration
- **Refresh Tokens**: 7-day expiration
- **Secret Rotation**: Automatic key rotation

#### Role-Based Access Control (RBAC)
- **Roles**: Admin, User, Viewer
- **Permissions**: Read, Write, Delete, Manage
- **Workspace Isolation**: Row-level security

### Data Protection

#### Encryption
- **At Rest**: AES-256 encryption
- **In Transit**: TLS 1.3
- **Secrets**: GCP Secret Manager with automatic rotation

#### Data Classification
- **Public**: No encryption required
- **Internal**: Encrypted, access logged
- **Confidential**: Encrypted, strict access controls
- **Restricted**: Maximum security controls

### Compliance

#### Standards
- **SOC 2**: Security and compliance controls
- **GDPR**: Data protection and privacy
- **HIPAA**: Healthcare data protection (optional)

#### Auditing
- **Access Logs**: All access attempts logged
- **Change Logs**: All configuration changes tracked
- **Security Events**: Real-time security monitoring

## Troubleshooting

### Common Issues

#### Database Connection Issues
```bash
# Check database connectivity
python -c "from backend.db.connection import test_connection; test_connection()"

# Check connection pool status
python -c "from backend.db.connection import check_pool_status; check_pool_status()"
```

#### Redis Connection Issues
```bash
# Check Redis connectivity
python -c "from backend.redis.client import test_connection; test_connection()"

# Check Redis memory usage
redis-cli info memory
```

#### Memory System Issues
```bash
# Check memory system health
python -c "from backend.memory.controller import check_health; check_health()"

# Check vector index status
python -c "from backend.memory.vector import check_index_status; check_index_status()"
```

#### Agent Execution Issues
```bash
# Check agent availability
python -c "from backend.agents.dispatcher import check_agents; check_agents()"

# Check agent performance
python -c "from backend.agents.monitoring import check_performance; check_performance()"
```

### Performance Issues

#### Slow Response Times
1. **Check Database Queries**: Use EXPLAIN ANALYZE for slow queries
2. **Check Memory Usage**: Monitor memory consumption and garbage collection
3. **Check Agent Performance**: Review agent execution times
4. **Check Network Latency**: Monitor network connectivity and latency

#### High Memory Usage
1. **Check Memory Leaks**: Use memory profiling tools
2. **Check Cache Size**: Monitor Redis and application cache usage
3. **Check Vector Storage**: Review vector database memory usage
4. **Check Agent State**: Review agent state management

#### High CPU Usage
1. **Check Agent Processing**: Monitor agent CPU usage
2. **Check Database Queries**: Review query optimization
3. **Check Background Jobs**: Monitor background job processing
4. **Check Cognitive Processing**: Review cognitive engine performance

### Debugging

#### Enable Debug Mode
```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
python main.py
```

#### Enable Detailed Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Enable Performance Profiling
```python
import cProfile
cProfile.run('main()', 'profile_output.prof')
```

### Support

#### Getting Help
- **Documentation**: Check this documentation first
- **GitHub Issues**: Report bugs and feature requests
- **Community**: Join our Discord community
- **Support Email**: support@raptorflow.com

#### Reporting Issues
When reporting issues, please include:
- **Environment**: Python version, OS, deployment type
- **Error Messages**: Full error messages and stack traces
- **Steps to Reproduce**: Detailed steps to reproduce the issue
- **Expected Behavior**: What you expected to happen
- **Actual Behavior**: What actually happened

---

## Contributing

We welcome contributions to RaptorFlow Backend! Please see our [Contributing Guide](CONTRIBUTING.md) for details on how to contribute.

## License

RaptorFlow Backend is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Contact

- **Website**: https://raptorflow.com
- **Email**: team@raptorflow.com
- **GitHub**: https://github.com/raptorflow-dev/Raptorflow
- **Discord**: https://discord.gg/raptorflow
