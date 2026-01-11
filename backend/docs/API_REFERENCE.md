# RaptorFlow Backend API Reference

## Overview

This document provides a comprehensive reference for all RaptorFlow Backend API endpoints, including request/response formats, authentication requirements, and usage examples.

## Base URL

- **Development**: `http://localhost:8000`
- **Staging**: `https://api-staging.raptorflow.com`
- **Production**: `https://api.raptorflow.com`

## Authentication

All API endpoints (except `/health` and `/auth/login`) require authentication using JWT tokens.

### Authorization Header

```
Authorization: Bearer <access_token>
```

### Token Format

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

## Response Format

All API responses follow a consistent format:

### Success Response

```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": { ... }
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Endpoints

### Health Check

#### GET `/health`

Check system health status.

**Authentication**: None required

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "services": {
    "database": {
      "status": "healthy",
      "response_time": 0.023
    },
    "redis": {
      "status": "healthy",
      "response_time": 0.015
    },
    "memory": {
      "status": "healthy",
      "response_time": 0.032
    },
    "cognitive": {
      "status": "healthy",
      "response_time": 0.045
    }
  }
}
```

### Authentication

#### POST `/auth/login`

Authenticate user and return access token.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 1800,
    "user": {
      "id": "user_123",
      "email": "user@example.com",
      "name": "John Doe",
      "subscription_tier": "pro",
      "created_at": "2024-01-01T00:00:00Z"
    }
  }
}
```

#### POST `/auth/refresh`

Refresh access token using refresh token.

**Request Headers**:
```
Authorization: Bearer <refresh_token>
```

**Response**:
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

#### POST `/auth/logout`

Logout user and invalidate tokens.

**Authentication**: Required

**Response**:
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

### Users

#### GET `/users/me`

Get current user profile.

**Authentication**: Required

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "user_123",
    "email": "user@example.com",
    "name": "John Doe",
    "subscription_tier": "pro",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

#### PUT `/users/me`

Update current user profile.

**Authentication**: Required

**Request Body**:
```json
{
  "name": "John Doe",
  "preferences": {
    "theme": "dark",
    "notifications": true
  }
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "user_123",
    "email": "user@example.com",
    "name": "John Doe",
    "preferences": {
      "theme": "dark",
      "notifications": true
    },
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

### Workspaces

#### GET `/workspaces`

List user's workspaces.

**Authentication**: Required

**Query Parameters**:
- `page` (int, optional): Page number (default: 1)
- `limit` (int, optional): Items per page (default: 20)

**Response**:
```json
{
  "success": true,
  "data": {
    "workspaces": [
      {
        "id": "workspace_123",
        "name": "My Business",
        "description": "Business description",
        "created_at": "2024-01-01T00:00:00Z",
        "subscription_tier": "pro",
        "status": "active"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 1,
      "pages": 1
    }
  }
}
```

#### POST `/workspaces`

Create new workspace.

**Authentication**: Required

**Request Body**:
```json
{
  "name": "New Business",
  "description": "Business description",
  "subscription_tier": "pro"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "workspace_456",
    "name": "New Business",
    "description": "Business description",
    "subscription_tier": "pro",
    "status": "active",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

#### GET `/workspaces/{workspace_id}`

Get workspace details.

**Authentication**: Required

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "workspace_123",
    "name": "My Business",
    "description": "Business description",
    "subscription_tier": "pro",
    "status": "active",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

#### PUT `/workspaces/{workspace_id}`

Update workspace details.

**Authentication**: Required

**Request Body**:
```json
{
  "name": "Updated Business",
  "description": "Updated description"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "workspace_123",
    "name": "Updated Business",
    "description": "Updated description",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

#### DELETE `/workspaces/{workspace_id}`

Delete workspace.

**Authentication**: Required

**Response**:
```json
{
  "success": true,
  "message": "Workspace deleted successfully"
}
```

### Agents

#### GET `/agents`

List available agents.

**Authentication**: Required

**Response**:
```json
{
  "success": true,
  "data": {
    "agents": [
      {
        "name": "market_research",
        "description": "Market analysis and competitive intelligence",
        "capabilities": ["market_analysis", "competitor_intel", "trend_analysis"],
        "status": "available"
      },
      {
        "name": "content_creator",
        "description": "Content generation and optimization",
        "capabilities": ["blog_posts", "social_media", "email_campaigns"],
        "status": "available"
      }
    ]
  }
}
```

#### POST `/agents/{agent_name}/execute`

Execute agent with specified parameters.

**Authentication**: Required

**Request Body**:
```json
{
  "workspace_id": "workspace_123",
  "input": "Analyze market trends for SaaS companies",
  "context": {
    "industry": "technology",
    "region": "north_america",
    "timeframe": "last_6_months"
  },
  "options": {
    "max_tokens": 1000,
    "temperature": 0.7,
    "include_sources": true
  }
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "output": "Market analysis results...",
    "agent_name": "market_research",
    "execution_time": 2.5,
    "tokens_used": 150,
    "sources": [
      {
        "title": "SaaS Market Report 2024",
        "url": "https://example.com/saas-report",
        "reliability": 0.9
      }
    ],
    "confidence": 0.85,
    "metadata": {
      "model": "gpt-4",
      "temperature": 0.7,
      "max_tokens": 1000
    }
  }
}
```

### Workflows

#### Onboarding Workflow

##### POST `/workflows/onboarding/step/{step}`

Execute onboarding workflow step.

**Authentication**: Required

**Request Body**:
```json
{
  "workspace_id": "workspace_123",
  "data": {
    "files": [
      {
        "filename": "business_plan.pdf",
        "file_type": "pdf",
        "file_size": 1024000
      }
    ]
  }
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "step": "evidence_upload",
    "next_step": "evidence_extraction",
    "progress": {
      "total_steps": 13,
      "completed_steps": 1,
      "progress_percentage": 7.69,
      "completed_step_names": ["evidence_upload"]
    },
    "result": {
      "files_stored": 1,
      "file_ids": ["file_123"]
    }
  }
}
```

##### GET `/workflows/onboarding/progress/{workspace_id}`

Get onboarding progress.

**Authentication**: Required

**Response**:
```json
{
  "success": true,
  "data": {
    "workspace_id": "workspace_123",
    "total_steps": 13,
    "completed_steps": 8,
    "progress_percentage": 61.54,
    "completed_step_names": [
      "evidence_upload",
      "evidence_extraction",
      "business_classification",
      "industry_analysis",
      "competitor_analysis",
      "value_proposition",
      "target_audience",
      "messaging_framework"
    ],
    "current_step": "foundation_creation",
    "status": "in_progress"
  }
}
```

#### Move Workflow

##### POST `/workflows/moves/create`

Create new move.

**Authentication**: Required

**Request Body**:
```json
{
  "workspace_id": "workspace_123",
  "goal": "Increase market share by 10%",
  "move_type": "strategic",
  "priority": "high",
  "estimated_duration": "30_days",
  "estimated_budget": 50000
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "move_id": "move_123",
    "plan": {
      "title": "Market Share Expansion",
      "description": "Strategic move to increase market share",
      "tasks": [
        {
          "title": "Market Analysis",
          "description": "Analyze current market position",
          "priority": "high",
          "estimated_duration": "5_days"
        }
      ],
      "estimated_duration": "30_days",
      "estimated_cost": 50000,
      "risk_level": "medium"
    }
  }
}
```

##### POST `/workflows/moves/{move_id}/execute`

Execute move.

**Authentication**: Required

**Response**:
```json
{
  "success": true,
  "data": {
    "execution_summary": {
      "total_tasks": 5,
      "successful_tasks": 4,
      "failed_tasks": 1,
      "success_rate": 80.0
    },
    "results": [
      {
        "task_id": "task_123",
        "success": true,
        "execution_time": 2.5,
        "result": "Task completed successfully"
      }
    ]
  }
}
```

##### POST `/workflows/moves/{move_id}/complete`

Complete move and generate insights.

**Authentication**: Required

**Response**:
```json
{
  "success": true,
  "data": {
    "analysis": {
      "goal_achievement": {
        "achievement_rate": 85.0,
        "assessment": "High"
      },
      "cost_analysis": {
        "estimated_cost": 50000,
        "actual_cost": 45000,
        "cost_variance": -5000
      },
      "quality_metrics": {
        "average_quality_score": 0.82,
        "min_quality_score": 0.75,
        "max_quality_score": 0.90
      }
    },
    "insights": [
      {
        "title": "Market Position Improved",
        "description": "Successfully increased market share by 8.5%",
        "confidence": 0.9
      }
    ],
    "recommendations": [
      {
        "title": "Expand to New Markets",
        "description": "Consider expanding to adjacent markets",
        "priority": "medium"
      }
    ]
  }
}
```

#### Content Workflow

##### POST `/workflows/content/generate`

Generate content.

**Authentication**: Required

**Request Body**:
```json
{
  "workspace_id": "workspace_123",
  "request": {
    "content_type": "blog",
    "title": "Market Trends Analysis",
    "topic": "SaaS industry trends",
    "tone": "professional",
    "length": "medium",
    "target_audience": "business_leaders"
  }
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "content_id": "content_123",
    "content": "Generated blog post content...",
    "agent_used": "content_creator",
    "quality_score": 0.85,
    "review_needed": false,
    "generated_at": "2024-01-01T00:00:00Z"
  }
}
```

##### POST `/workflows/content/{content_id}/review`

Review content quality.

**Authentication**: Required

**Response**:
```json
{
  "success": true,
  "data": {
    "content_id": "content_123",
    "quality_score": 0.85,
    "feedback": {
      "strengths": ["Well-structured", "Informative"],
      "weaknesses": ["Could be more engaging"],
      "suggestions": ["Add more examples"]
    },
    "revision_needed": false,
    "review_completed": true
  }
}
```

##### POST `/workflows/content/{content_id}/publish`

Publish content to channels.

**Authentication**: Required

**Request Body**:
```json
{
  "channels": ["blog", "linkedin", "twitter"],
  "publish_options": {
    "publish_time": "2024-01-01T09:00:00Z",
    "customizations": {
      "linkedin": {
        "hashtags": ["#SaaS", "#MarketTrends"]
      }
    }
  }
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "content_id": "content_123",
    "published_channels": ["blog", "linkedin"],
    "publish_results": [
      {
        "channel": "blog",
        "success": true,
        "publish_url": "https://blog.raptorflow.com/post/123"
      },
      {
        "channel": "linkedin",
        "success": true,
        "publish_url": "https://linkedin.com/posts/123"
      }
    ],
    "published_at": "2024-01-01T09:00:00Z"
  }
}
```

### Memory

#### GET `/memory/search`

Search memory for relevant information.

**Authentication**: Required

**Query Parameters**:
- `query` (string, required): Search query
- `memory_types` (string, optional): Memory types to search (comma-separated)
- `limit` (int, optional): Maximum results (default: 10)
- `workspace_id` (string, required): Workspace ID

**Response**:
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "content": "Market analysis results...",
        "score": 0.92,
        "memory_type": "foundation",
        "metadata": {
          "created_at": "2024-01-01T00:00:00Z",
          "source": "market_research_agent"
        }
      }
    ],
    "total_results": 1,
    "search_time": 0.045
  }
}
```

#### POST `/memory/store`

Store information in memory.

**Authentication**: Required

**Request Body**:
```json
{
  "workspace_id": "workspace_123",
  "memory_type": "conversation",
  "content": "Important conversation content...",
  "metadata": {
    "source": "user_input",
    "context": "market_discussion"
  }
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "memory_id": "memory_123",
    "stored_at": "2024-01-01T00:00:00Z"
  }
}
```

### Cognitive Engine

#### POST `/cognitive/perceive`

Perceive and analyze input.

**Authentication**: Required

**Request Body**:
```json
{
  "text": "We need to analyze our market position",
  "context": {
    "workspace_id": "workspace_123",
    "history": ["Previous conversation content"]
  }
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "intent": "market_analysis",
    "entities": [
      {
        "type": "concept",
        "name": "market_position",
        "confidence": 0.95
      }
    ],
    "sentiment": "neutral",
    "confidence": 0.88,
    "perceived_at": "2024-01-01T00:00:00Z"
  }
}
```

#### POST `/cognitive/plan`

Create execution plan.

**Authentication**: Required

**Request Body**:
```json
{
  "goal": "Increase market share by 10%",
  "perceived": {
    "intent": "market_expansion",
    "entities": [...]
  },
  "context": {
    "workspace_id": "workspace_123",
    "budget": 50000,
    "timeline": "3_months"
  }
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "goal": "Increase market share by 10%",
    "steps": [
      {
        "action": "market_analysis",
        "description": "Analyze current market position",
        "duration": "1_week",
        "estimated_cost": 5000
      }
    ],
    "total_cost": 45000,
    "total_duration": "12_weeks",
    "risk_level": "medium",
    "planned_at": "2024-01-01T00:00:00Z"
  }
}
```

#### POST `/cognitive/reflect`

Reflect on output quality.

**Authentication**: Required

**Request Body**:
```json
{
  "output": "Generated market analysis content...",
  "goal": "Provide comprehensive market analysis",
  "context": {
    "workspace_id": "workspace_123",
    "audience": "business_leaders"
  },
  "max_iterations": 3
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "quality_score": 0.85,
    "approved": true,
    "feedback": "Good quality analysis with actionable insights",
    "improvements": [
      "Add more specific data points",
      "Include competitor analysis"
    ],
    "reflected_at": "2024-01-01T00:00:00Z"
  }
}
```

### Analytics

#### GET `/analytics/metrics`

Get system metrics.

**Authentication**: Required

**Query Parameters**:
- `workspace_id` (string, optional): Filter by workspace
- `start_date` (string, optional): Start date (ISO format)
- `end_date` (string, optional): End date (ISO format)
- `metric_type` (string, optional): Type of metrics

**Response**:
```json
{
  "success": true,
  "data": {
    "metrics": {
      "total_requests": 1000,
      "successful_requests": 950,
      "failed_requests": 50,
      "average_response_time": 1.2,
      "95th_percentile_response_time": 2.5,
      "error_rate": 0.05,
      "agent_executions": 200,
      "cognitive_processing_time": 0.8
    },
    "period": {
      "start_date": "2024-01-01T00:00:00Z",
      "end_date": "2024-01-31T23:59:59Z"
    }
  }
}
```

#### GET `/analytics/reports/{report_id}`

Get analytics report.

**Authentication**: Required

**Response**:
```json
{
  "success": true,
  "data": {
    "report_id": "report_123",
    "title": "Monthly Performance Report",
    "generated_at": "2024-01-01T00:00:00Z",
    "period": {
      "start_date": "2024-01-01T00:00:00Z",
      "end_date": "2024-01-31T23:59:59Z"
    },
    "sections": [
      {
        "title": "Overview",
        "content": "Executive summary of performance..."
      },
      {
        "title": "Agent Performance",
        "content": "Detailed agent performance analysis..."
      }
    ]
  }
}
```

## Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `VALIDATION_ERROR` | Invalid input data | 400 |
| `AUTHENTICATION_ERROR` | Authentication failed | 401 |
| `AUTHORIZATION_ERROR` | Access denied | 403 |
| `NOT_FOUND` | Resource not found | 404 |
| `CONFLICT` | Resource conflict | 409 |
| `RATE_LIMIT_ERROR` | Rate limit exceeded | 429 |
| `INTERNAL_ERROR` | Internal server error | 500 |
| `SERVICE_UNAVAILABLE` | Service temporarily unavailable | 503 |

## Rate Limiting

- **Default Limit**: 100 requests per minute per user
- **Premium Users**: 500 requests per minute per user
- **Enterprise Users**: 1000 requests per minute per user

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Pagination

List endpoints support pagination using these parameters:
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20, max: 100)

Pagination information is included in responses:
```json
{
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "pages": 5
  }
}
```

## Webhooks

### Setup Webhooks

#### POST `/webhooks`

Create webhook subscription.

**Authentication**: Required

**Request Body**:
```json
{
  "url": "https://your-app.com/webhook",
  "events": ["agent.completed", "workflow.failed"],
  "secret": "webhook_secret",
  "active": true
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "webhook_id": "webhook_123",
    "url": "https://your-app.com/webhook",
    "events": ["agent.completed", "workflow.failed"],
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### Webhook Events

#### Agent Completed

```json
{
  "event": "agent.completed",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "agent_name": "market_research",
    "execution_id": "exec_123",
    "workspace_id": "workspace_123",
    "result": { ... },
    "success": true
  }
}
```

#### Workflow Failed

```json
{
  "event": "workflow.failed",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "workflow_type": "onboarding",
    "step": "evidence_extraction",
    "workspace_id": "workspace_123",
    "error": "Failed to extract evidence",
    "error_details": { ... }
  }
}
```

## SDK Examples

### Python

```python
import requests

# Login
response = requests.post('https://api.raptorflow.com/auth/login', json={
    'email': 'user@example.com',
    'password': 'password123'
})
token = response.json()['data']['access_token']

# Execute agent
headers = {'Authorization': f'Bearer {token}'}
response = requests.post('https://api.raptorflow.com/agents/market_research/execute',
                        json={
                            'workspace_id': 'workspace_123',
                            'input': 'Analyze market trends'
                        }, headers=headers)
result = response.json()['data']
```

### JavaScript

```javascript
// Login
const response = await fetch('https://api.raptorflow.com/auth/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123'
  })
});
const {access_token} = await response.json();

// Execute agent
const result = await fetch('https://api.raptorflow.com/agents/market_research/execute', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${access_token}`
  },
  body: JSON.stringify({
    workspace_id: 'workspace_123',
    input: 'Analyze market trends'
  })
});
const data = await result.json();
```

## Support

For API support and questions:
- **Documentation**: https://docs.raptorflow.com
- **GitHub Issues**: https://github.com/raptorflow-dev/Raptorflow/issues
- **Email**: api-support@raptorflow.com
- **Discord**: https://discord.gg/raptorflow
