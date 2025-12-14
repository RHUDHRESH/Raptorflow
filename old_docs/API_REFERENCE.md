## RaptorFlow 2.0 - API Reference

Complete API reference for all RaptorFlow endpoints including the master workflow orchestration.

## Base URL

```
Production: https://api.raptorflow.ai
Staging: https://staging-api.raptorflow.ai
Local: http://localhost:8000
```

## Authentication

All API endpoints (except `/health` and `/`) require authentication using JWT tokens from Supabase.

### Headers

```http
Authorization: Bearer <YOUR_JWT_TOKEN>
Content-Type: application/json
X-Correlation-ID: <optional-custom-correlation-id>
```

### Response Headers

All responses include:
- `X-Correlation-ID`: Unique identifier for request tracing
- `X-Process-Time`: Request processing time in seconds

---

## Master Orchestration API

The orchestration API coordinates complete end-to-end marketing workflows across all domain graphs.

### POST /api/v1/orchestration/execute

Execute a workflow based on specified goal.

**Request Body:**

```json
{
  "goal": "full_campaign",  // Required: Workflow goal
  "onboarding_session_id": "uuid",  // Optional: Resume from onboarding
  "icp_id": "uuid",  // Optional: Use existing ICP
  "strategy_id": "uuid",  // Optional: Use existing strategy
  "content_ids": ["uuid"],  // Optional: Existing content to publish
  "research_query": "B2B SaaS startups",  // Optional: Research query
  "research_mode": "deep",  // Optional: "quick" or "deep"
  "strategy_mode": "comprehensive",  // Optional: "quick" or "comprehensive"
  "content_type": "blog",  // Optional: blog, email, social_post, etc.
  "content_params": {  // Optional: Additional content parameters
    "topic": "How to scale SaaS sales",
    "tone": "professional",
    "length": "long"
  },
  "publish_platforms": ["linkedin", "twitter"]  // Optional: Publishing platforms
}
```

**Workflow Goals:**

- `full_campaign`: Complete end-to-end (research → strategy → content → publish → analytics)
- `research_only`: Generate ICP and customer intelligence only
- `strategy_only`: Generate marketing strategy (requires ICP)
- `content_only`: Generate content (requires strategy)
- `publish`: Publish existing content to platforms
- `onboard`: Just onboarding questionnaire

**Response:**

```json
{
  "workflow_id": "uuid",
  "correlation_id": "uuid",
  "goal": "full_campaign",
  "current_stage": "finalize",
  "completed_stages": ["research", "strategy", "content", "critic_review", "integration", "execution"],
  "failed_stages": [],
  "success": true,
  "message": "Workflow completed successfully",
  "started_at": "2024-01-01T00:00:00Z",
  "completed_at": "2024-01-01T00:10:00Z",

  "research_result": {
    "icp_id": "uuid",
    "icp": {
      "name": "B2B SaaS Startups",
      "pain_points": ["Scaling", "Retention"],
      "demographics": {...},
      "psychographics": {...}
    }
  },

  "strategy_result": {
    "strategy_id": "uuid",
    "campaign_ideas": [
      {
        "name": "Thought Leadership Campaign",
        "channels": ["linkedin", "blog"],
        "budget": 10000
      }
    ],
    "insights": {...}
  },

  "content_result": {
    "content_ids": ["uuid"],
    "content": "Generated content...",
    "meta": {...}
  },

  "critic_review": {
    "recommendation": "approve",
    "overall_score": 90,
    "strengths": ["Clear", "Engaging"],
    "improvements": [],
    "revision_suggestions": []
  },

  "integration_result": {
    "assets": [...]
  },

  "execution_result": {
    "published": ["linkedin"],
    "analytics": {...}
  },

  "errors": []
}
```

**Status Codes:**
- `200 OK`: Workflow executed successfully
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Missing or invalid JWT token
- `500 Internal Server Error`: Workflow execution failed

---

### GET /api/v1/orchestration/workflows

List all workflow executions for the current workspace.

**Query Parameters:**
- `limit` (integer, default: 20): Number of workflows to return
- `offset` (integer, default: 0): Pagination offset

**Response:**

```json
{
  "workflows": [
    {
      "workflow_id": "uuid",
      "goal": "full_campaign",
      "success": true,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 42
}
```

---

### GET /api/v1/orchestration/workflows/{workflow_id}

Get detailed status of a specific workflow execution.

**Response:**

```json
{
  "workflow_id": "uuid",
  "correlation_id": "uuid",
  "goal": "full_campaign",
  "current_stage": "finalize",
  "completed_stages": [...],
  "failed_stages": [],
  "success": true,
  "message": "Workflow completed",
  "started_at": "2024-01-01T00:00:00Z",
  "completed_at": "2024-01-01T00:10:00Z",
  "research_result": {...},
  "strategy_result": {...},
  "content_result": {...},
  "critic_review": {...},
  "integration_result": {...},
  "execution_result": {...},
  "errors": []
}
```

**Status Codes:**
- `200 OK`: Workflow found
- `404 Not Found`: Workflow not found

---

### POST /api/v1/orchestration/workflows/{workflow_id}/retry

Retry a failed workflow from the last successful stage.

**Response:**

```json
{
  "status": "not_implemented",
  "message": "Retry functionality coming soon"
}
```

---

## Domain-Specific APIs

### Onboarding

#### POST /api/v1/onboarding/start
Start dynamic onboarding questionnaire.

#### POST /api/v1/onboarding/answer
Submit answer to current question.

#### GET /api/v1/onboarding/session/{session_id}
Get onboarding session state.

---

### Customer Intelligence (Research)

#### POST /api/v1/cohorts/generate
Generate ICP from research query.

**Request:**
```json
{
  "query": "B2B SaaS startups",
  "mode": "deep",  // "quick" or "deep"
  "industry": "Software"
}
```

#### GET /api/v1/cohorts
List all ICPs for workspace.

#### GET /api/v1/cohorts/{cohort_id}
Get specific ICP details.

---

### Strategy

#### POST /api/v1/strategy/generate
Generate marketing strategy using ADAPT framework.

**Request:**
```json
{
  "goal": "Increase inbound leads by 50%",
  "timeframe_days": 90,
  "target_cohort_ids": ["uuid"],
  "constraints": {
    "budget": 50000,
    "channels": ["linkedin", "blog"]
  }
}
```

#### GET /api/v1/strategy/{strategy_id}
Get strategy details.

---

### Content

#### POST /api/v1/content/generate
Generate content (blog, email, social post, etc.).

**Request:**
```json
{
  "type": "blog",
  "topic": "How to scale SaaS sales",
  "icp_id": "uuid",
  "strategy_id": "uuid",
  "params": {
    "tone": "professional",
    "length": "long",
    "include_cta": true
  }
}
```

#### POST /api/v1/content/{content_id}/approve
Approve content for publishing.

#### GET /api/v1/content
List all content for workspace.

---

### Campaigns (Moves)

#### POST /api/v1/campaigns
Create new campaign.

#### GET /api/v1/campaigns
List campaigns.

#### GET /api/v1/campaigns/{campaign_id}
Get campaign details.

#### POST /api/v1/campaigns/{campaign_id}/tasks
Create task for campaign.

---

### Analytics

#### GET /api/v1/analytics/overview
Get workspace analytics overview.

#### GET /api/v1/analytics/campaigns/{campaign_id}
Get campaign performance metrics.

---

### Integrations

#### POST /api/v1/integrations/connect
Connect third-party platform.

**Request:**
```json
{
  "platform": "linkedin",
  "credentials": {
    "access_token": "...",
    "refresh_token": "..."
  }
}
```

#### GET /api/v1/integrations
List connected platforms.

#### DELETE /api/v1/integrations/{platform}
Disconnect platform.

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message",
  "type": "ErrorType",
  "correlation_id": "uuid"
}
```

### Common Error Codes

- `400 Bad Request`: Invalid request body or parameters
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service temporarily unavailable

---

## Rate Limits

- **Default:** 100 requests per minute per workspace
- **Workflow Execution:** 10 concurrent workflows per workspace
- **Content Generation:** 20 requests per minute

Rate limit headers:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1234567890
```

---

## Webhooks

Subscribe to events:

- `workflow.completed`
- `workflow.failed`
- `content.generated`
- `content.published`
- `campaign.completed`

**Webhook Payload:**
```json
{
  "event": "workflow.completed",
  "timestamp": "2024-01-01T00:00:00Z",
  "workspace_id": "uuid",
  "data": {...}
}
```

---

## SDKs

### Python

```python
from raptorflow import RaptorFlowClient

client = RaptorFlowClient(
    api_key="your-api-key",
    base_url="https://api.raptorflow.ai"
)

# Execute workflow
workflow = client.orchestration.execute(
    goal="full_campaign",
    research_query="B2B SaaS startups"
)

print(f"Workflow {workflow.id} completed: {workflow.success}")
```

### JavaScript/TypeScript

```typescript
import { RaptorFlowClient } from '@raptorflow/sdk';

const client = new RaptorFlowClient({
  apiKey: 'your-api-key',
  baseUrl: 'https://api.raptorflow.ai'
});

// Execute workflow
const workflow = await client.orchestration.execute({
  goal: 'full_campaign',
  researchQuery: 'B2B SaaS startups'
});

console.log(`Workflow ${workflow.id} completed: ${workflow.success}`);
```

---

## Examples

### Full Campaign Workflow

```bash
curl -X POST https://api.raptorflow.ai/api/v1/orchestration/execute \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "full_campaign",
    "research_query": "B2B SaaS startups",
    "research_mode": "deep",
    "strategy_mode": "comprehensive",
    "content_type": "blog",
    "content_params": {
      "topic": "How to scale SaaS sales",
      "tone": "professional"
    },
    "publish_platforms": ["linkedin"]
  }'
```

### Research Only

```bash
curl -X POST https://api.raptorflow.ai/api/v1/orchestration/execute \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "research_only",
    "research_query": "Enterprise cybersecurity companies",
    "research_mode": "deep"
  }'
```

### Content Generation with Critic Review

```bash
curl -X POST https://api.raptorflow.ai/api/v1/orchestration/execute \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "content_only",
    "icp_id": "existing-icp-uuid",
    "strategy_id": "existing-strategy-uuid",
    "content_type": "email",
    "content_params": {
      "subject": "Boost your sales with AI",
      "tone": "friendly",
      "length": "medium"
    }
  }'
```

---

## Support

- **API Status:** https://status.raptorflow.ai
- **Documentation:** https://docs.raptorflow.ai
- **Support:** support@raptorflow.ai
- **GitHub:** https://github.com/yourusername/raptorflow

---

**Version:** 2.0.0
**Last Updated:** 2024-01-15

---

## Advanced Analytics & Intelligence API

### Performance Prediction

#### POST /api/v1/analytics/predict/performance

Predict content performance before publishing.

**Request Body:**
```json
{
  "content_type": "blog",
  "platform": "linkedin",
  "content_features": {
    "word_count": 500,
    "has_media": true,
    "has_hashtags": true,
    "topic": "AI Marketing"
  }
}
```

**Response:**
```json
{
  "prediction_available": true,
  "content_type": "blog",
  "platform": "linkedin",
  "predicted_engagement_rate": 4.5,
  "predicted_impressions": 5000,
  "predicted_clicks": 225,
  "confidence_score": 85.2,
  "performance_range": {
    "min": 3.8,
    "max": 5.2
  },
  "data_points_used": 45
}
```

#### GET /api/v1/analytics/predict/optimal-time?platform=linkedin

Predict the best time to post based on historical engagement.

**Response:**
```json
{
  "prediction_available": true,
  "platform": "linkedin",
  "best_day_of_week": "Tuesday",
  "best_day_engagement": 5.8,
  "best_hour": 10,
  "best_hour_engagement": 6.2,
  "recommended_posting_time": "Tuesday at 10:00"
}
```

#### POST /api/v1/analytics/predict/ab-test

Get A/B test configuration suggestions.

**Request Body:**
```json
{
  "content_variants": [
    {
      "name": "Short Hook",
      "content_type": "social_post",
      "platform": "linkedin",
      "features": {"word_count": 100, "has_media": true}
    },
    {
      "name": "Long Story",
      "content_type": "social_post",
      "platform": "linkedin",
      "features": {"word_count": 300, "has_media": false}
    }
  ]
}
```

**Response:**
```json
{
  "variants": [...],
  "recommendation": "Variant 'Short Hook' shows 20%+ higher predicted engagement...",
  "suggested_split": {
    "Short Hook": 70.0,
    "Long Story": 30.0
  },
  "estimated_duration_days": 7
}
```

### Meta-Learning

#### GET /api/v1/analytics/meta-learning/insights?time_period_days=90

Learn from historical performance and generate recommendations.

**Response:**
```json
{
  "learning_available": true,
  "samples_analyzed": 85,
  "content_patterns": {
    "by_content_type": {
      "blog": {"avg_engagement": 4.2, "count": 30},
      "social_post": {"avg_engagement": 5.1, "count": 55}
    },
    "best_performing_type": "social_post"
  },
  "timing_patterns": {
    "best_day": "Tuesday",
    "best_day_engagement": 5.8
  },
  "platform_insights": {
    "best_platform": "linkedin",
    "best_platform_engagement": 6.2
  },
  "improvement_trends": {
    "trend": "improving",
    "improvement_percentage": 15.3
  },
  "recommendations": [
    {
      "category": "content_type",
      "priority": "high",
      "recommendation": "Focus on social_post content",
      "confidence": "high"
    }
  ]
}
```

#### GET /api/v1/analytics/meta-learning/strategy/{strategy_id}

Track effectiveness of a specific strategy.

**Response:**
```json
{
  "tracking_available": true,
  "strategy_id": "uuid",
  "total_posts": 25,
  "avg_engagement_rate": 4.8,
  "effectiveness": "high",
  "consistency_score": 87.5
}
```

### Agent Swarm & Collaborative Intelligence

#### POST /api/v1/analytics/debate

Run a multi-agent debate on a strategic question.

**Request Body:**
```json
{
  "topic": "Should we focus on LinkedIn or Twitter for B2B outreach?",
  "context": {
    "description": "We're a B2B SaaS company targeting enterprise clients"
  },
  "agent_roles": ["conservative_marketer", "innovative_disruptor", "data_analyst"]
}
```

**Response:**
```json
{
  "topic": "Should we focus on LinkedIn or Twitter for B2B outreach?",
  "agent_roles": ["conservative_marketer", "innovative_disruptor", "data_analyst"],
  "debate_rounds": 3,
  "transcript": [
    {
      "round": 1,
      "arguments": {
        "conservative_marketer": "LinkedIn is the proven platform for B2B...",
        "innovative_disruptor": "Twitter offers unique opportunities for viral growth...",
        "data_analyst": "The data shows LinkedIn has 3x higher conversion rates..."
      }
    }
  ],
  "consensus": {
    "reached": true,
    "synthesis": "While Twitter offers innovation potential, LinkedIn's proven B2B track record and higher conversion rates make it the primary focus, with Twitter as a secondary experimental channel."
  }
}
```

#### POST /api/v1/analytics/collaborative-decision

Make a collaborative decision using agent swarm.

**Request Body:**
```json
{
  "decision_type": "platform",
  "options": [
    {"name": "LinkedIn", "description": "Professional network"},
    {"name": "Twitter", "description": "Real-time updates"}
  ],
  "context": {"description": "B2B SaaS marketing"}
}
```

**Response:**
```json
{
  "decision_type": "platform",
  "winning_option_index": 0,
  "winning_option": {"name": "LinkedIn", "description": "Professional network"},
  "total_confidence": 78.5,
  "agent_votes": {...}
}
```

### Semantic Memory API

#### POST /api/v1/memory/context

Store context in semantic memory.

**Request Body:**
```json
{
  "context_type": "icp",
  "content": "Target audience: B2B SaaS founders aged 30-45...",
  "metadata": {
    "icp_id": "uuid",
    "industry": "SaaS"
  }
}
```

**Response:**
```json
{
  "context_id": "workspace_icp_1234567890",
  "workspace_id": "uuid",
  "context_type": "icp",
  "stored_at": "2024-01-01T00:00:00Z",
  "message": "Context stored successfully"
}
```

#### POST /api/v1/memory/context/search

Search context using semantic similarity.

**Request Body:**
```json
{
  "query": "What are our target audience's pain points?",
  "context_type": "icp",
  "limit": 5
}
```

**Response:**
```json
{
  "query": "What are our target audience's pain points?",
  "results": [
    {
      "id": "context_id",
      "content": "Target audience struggles with scaling, retention...",
      "context_type": "icp",
      "similarity": 0.89,
      "metadata": {...}
    }
  ],
  "result_count": 3
}
```

### Content Quality & Language Engine

#### POST /api/v1/analytics/content/check-grammar

Check grammar and spelling.

**Request Body:**
```json
{
  "text": "Your content to check",
  "language": "en-US"
}
```

**Response:**
```json
{
  "text": "Your content to check",
  "language": "en-US",
  "issues": [
    {
      "type": "spacing",
      "message": "Multiple consecutive spaces found",
      "severity": "low"
    }
  ],
  "issue_count": 1
}
```

#### POST /api/v1/analytics/content/analyze-readability

Analyze content readability.

**Request Body:**
```json
{
  "text": "Your content to analyze"
}
```

**Response:**
```json
{
  "sentences": 5,
  "words": 87,
  "syllables": 142,
  "avg_words_per_sentence": 17.4,
  "flesch_reading_ease": 68.5,
  "flesch_kincaid_grade": 8.2,
  "readability_level": "standard"
}
```

#### POST /api/v1/analytics/content/optimize-tone

Optimize content tone.

**Request Body:**
```json
{
  "text": "Your content",
  "target_tone": "professional"
}
```

**Response:**
```json
{
  "target_tone": "professional",
  "current_tone_analysis": {
    "contractions": 3,
    "personal_pronouns": 5,
    "informal_words": 2
  },
  "suggestions": [
    "Reduce contractions (don't → do not)",
    "Replace informal language"
  ],
  "tone_match_score": 65.0
}
```

#### POST /api/v1/analytics/content/suggest-improvements

Get comprehensive content analysis.

**Request Body:**
```json
{
  "text": "Your content to analyze"
}
```

**Response:**
```json
{
  "grammar_check": {...},
  "readability_analysis": {...},
  "suggestions": [
    {
      "category": "readability",
      "priority": "medium",
      "message": "Simplify language for better readability"
    }
  ],
  "quality_score": 82.5
}
```

---

## Error Handling

All endpoints return consistent error responses:

```json
{
  "detail": "Error message",
  "correlation_id": "uuid",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

**Common HTTP Status Codes:**
- `200 OK`: Success
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

