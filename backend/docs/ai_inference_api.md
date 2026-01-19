# AI Inference API Documentation

## Overview

The AI Inference API provides a comprehensive, production-ready interface for AI inference with intelligent caching, cost optimization, and high availability. This API is designed to reduce LLM costs by 60-80% while improving response times by 40% through advanced optimization techniques.

## Features

- **Intelligent Multi-Level Caching**: L1 (memory), L2 (Redis), L3 (persistent) caching
- **Request Deduplication**: Prevents duplicate LLM calls with semantic similarity matching
- **Cost Optimization**: Real-time token counting and optimal provider selection
- **Batch Processing**: Efficient handling of multiple requests
- **Response Streaming**: Real-time progress updates for long-running tasks
- **Priority Queuing**: Intelligent request prioritization and load balancing
- **Fallback Providers**: Automatic failover with 99.9% uptime guarantee
- **Performance Monitoring**: Comprehensive analytics and alerting
- **Cache Warming**: ML-based prediction of frequently used prompts

## Base URL

```
https://api.raptorflow.ai/v1/ai-inference
```

## Authentication

All API requests require authentication using Bearer tokens:

```http
Authorization: Bearer <your-api-key>
```

## API Endpoints

### 1. Single Inference

Process a single inference request with full optimization.

**Endpoint**: `POST /inference`

**Request Body**:
```json
{
  "prompt": "What is the capital of France?",
  "model_name": "gpt-3.5-turbo",
  "temperature": 0.7,
  "max_tokens": 500,
  "user_id": "user_123",
  "workspace_id": "workspace_456",
  "priority": 5,
  "stream": false,
  "timeout_seconds": 300,
  "use_cache": true,
  "cost_optimize": true,
  "strategy": "balanced",
  "budget_limit": 1.0,
  "metadata": {
    "source": "web_app",
    "session_id": "sess_789"
  }
}
```

**Response**:
```json
{
  "request_id": "req_abc123",
  "response": "The capital of France is Paris.",
  "model_used": "gpt-3.5-turbo",
  "provider_used": "openai",
  "processing_time": 1.234,
  "cache_hit": false,
  "input_tokens": 15,
  "output_tokens": 8,
  "estimated_cost": 0.000123,
  "actual_cost": 0.000115,
  "timestamp": "2024-01-15T10:30:00Z",
  "metadata": {
    "strategy": "balanced",
    "optimization_enabled": true
  }
}
```

**Parameters**:
- `prompt` (string, required): The prompt to process
- `model_name` (string, optional): Model to use (default: "gpt-3.5-turbo")
- `temperature` (float, optional): Sampling temperature (0.0-2.0, default: 0.7)
- `max_tokens` (integer, optional): Maximum tokens to generate
- `user_id` (string, optional): User ID for tracking
- `workspace_id` (string, optional): Workspace ID for tracking
- `priority` (integer, optional): Request priority (1-10, default: 5)
- `stream` (boolean, optional): Enable streaming response (default: false)
- `timeout_seconds` (integer, optional): Request timeout (default: 300)
- `use_cache` (boolean, optional): Use cached responses (default: true)
- `cost_optimize` (boolean, optional): Enable cost optimization (default: true)
- `strategy` (string, optional): Optimization strategy (default: "balanced")
- `budget_limit` (float, optional): Maximum cost limit in USD
- `metadata` (object, optional): Additional metadata

### 2. Batch Inference

Process multiple inference requests efficiently.

**Endpoint**: `POST /batch-inference`

**Request Body**:
```json
{
  "requests": [
    {
      "prompt": "What is 2 + 2?",
      "model_name": "gpt-3.5-turbo",
      "priority": 5
    },
    {
      "prompt": "Explain photosynthesis",
      "model_name": "gpt-4",
      "priority": 7
    }
  ],
  "batch_id": "batch_def456",
  "max_batch_size": 10,
  "timeout_seconds": 600,
  "deduplicate": true,
  "parallel_processing": true,
  "fail_fast": false
}
```

**Response**:
```json
{
  "batch_id": "batch_def456",
  "responses": [
    {
      "request_id": "req_ghi789",
      "response": "2 + 2 = 4",
      "model_used": "gpt-3.5-turbo",
      "provider_used": "openai",
      "processing_time": 0.856,
      "cache_hit": false,
      "input_tokens": 8,
      "output_tokens": 5,
      "estimated_cost": 0.000089,
      "actual_cost": 0.000085,
      "timestamp": "2024-01-15T10:30:05Z"
    }
  ],
  "total_requests": 2,
  "successful_requests": 2,
  "failed_requests": 0,
  "duplicate_requests": 0,
  "total_processing_time": 2.145,
  "avg_processing_time": 1.072,
  "total_estimated_cost": 0.001234,
  "total_actual_cost": 0.001156,
  "cache_hits": 0,
  "cache_hit_rate": 0.0,
  "timestamp": "2024-01-15T10:30:07Z"
}
```

### 3. Streaming Inference

Stream inference results for long-running tasks.

**Endpoint**: `WebSocket /stream/{request_id}`

**Connection**:
```javascript
const ws = new WebSocket('wss://api.raptorflow.ai/v1/ai-inference/stream/req_abc123');

ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};
```

**Stream Messages**:
```json
{
  "id": "chunk_001",
  "type": "progress",
  "data": {
    "current": 25,
    "total": 100,
    "percentage": 25.0,
    "message": "Processing step 1/4"
  },
  "timestamp": "2024-01-15T10:30:10Z",
  "sequence": 1
}
```

```json
{
  "id": "chunk_002",
  "type": "data",
  "data": "Partial response content...",
  "timestamp": "2024-01-15T10:30:15Z",
  "sequence": 2
}
```

### 4. System Status

Get system status and performance metrics.

**Endpoint**: `GET /status`

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "pending_requests": 12,
  "processing_requests": 8,
  "cache_stats": {
    "overall": {
      "total_requests": 10000,
      "hit_rate": 78.5,
      "l1_hit_rate": 45.2,
      "l2_hit_rate": 28.1,
      "l3_hit_rate": 5.2,
      "total_cost_saved": 123.45,
      "total_tokens_saved": 150000
    },
    "l1_memory": {
      "total_entries": 1000,
      "utilization": 0.65,
      "strategy": "lru"
    },
    "l2_redis": {
      "total_entries": 5000,
      "compression": true,
      "ttl_seconds": 3600
    },
    "l3_persistent": {
      "total_entries": 10000,
      "total_size_mb": 250.5,
      "storage_path": "/tmp/inference_cache"
    }
  },
  "cost_stats": {
    "period_days": 7,
    "total_cost": 45.67,
    "total_tokens": 250000,
    "total_requests": 1500,
    "avg_cost_per_request": 0.030,
    "avg_cost_per_token": 0.00018,
    "provider_breakdown": {
      "openai": 35.20,
      "google": 8.45,
      "anthropic": 2.02
    }
  },
  "worker_stats": {
    "total_workers": 10,
    "active_workers": 6,
    "total_requests_processed": 50000,
    "deduplicator": {
      "total_requests": 50000,
      "exact_duplicates": 5000,
      "semantic_duplicates": 3000,
      "deduplication_rate": 0.16
    },
    "batch_processor": {
      "total_batches": 1000,
      "successful_batches": 950,
      "failed_batches": 50,
      "average_batch_size": 5.2
    }
  }
}
```

### 5. Available Providers

Get available providers and recommendations.

**Endpoint**: `GET /providers`

**Response**:
```json
{
  "providers": [
    {
      "provider": "openai",
      "model": "gpt-3.5-turbo",
      "estimated_cost": 0.0015,
      "estimated_time": 1.5,
      "reliability_score": 0.95,
      "quality_score": 0.85,
      "tier": "basic",
      "actual_performance": {
        "total_requests": 10000,
        "avg_response_time": 1.45,
        "success_rate": 0.98
      },
      "pricing": {
        "input_token_price": 0.0015,
        "output_token_price": 0.002,
        "max_tokens_per_request": 4096,
        "requests_per_minute": 3500
      }
    },
    {
      "provider": "openai",
      "model": "gpt-4",
      "estimated_cost": 0.03,
      "estimated_time": 3.0,
      "reliability_score": 0.98,
      "quality_score": 0.95,
      "tier": "pro",
      "actual_performance": {
        "total_requests": 5000,
        "avg_response_time": 2.8,
        "success_rate": 0.99
      },
      "pricing": {
        "input_token_price": 0.03,
        "output_token_price": 0.06,
        "max_tokens_per_request": 8192,
        "requests_per_minute": 200
      }
    }
  ],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 6. Cache Management

Clear cache at specified level.

**Endpoint**: `POST /clear-cache`

**Request Parameters**:
- `level` (query): Cache level - "l1", "l2", "l3", or "all"

**Response**:
```json
{
  "success": true,
  "level": "all",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 7. Analytics

Get comprehensive analytics and insights.

**Endpoint**: `GET /analytics`

**Request Parameters**:
- `days` (query): Number of days for analysis (default: 7)

**Response**:
```json
{
  "cost_analysis": {
    "period_days": 7,
    "total_cost": 45.67,
    "total_tokens": 250000,
    "total_requests": 1500,
    "avg_cost_per_request": 0.030,
    "avg_cost_per_token": 0.00018,
    "provider_breakdown": {
      "openai": 35.20,
      "google": 8.45,
      "anthropic": 2.02
    },
    "daily_costs": {
      "2024-01-09": 6.50,
      "2024-01-10": 6.75,
      "2024-01-11": 6.25,
      "2024-01-12": 6.80,
      "2024-01-13": 6.45,
      "2024-01-14": 6.42,
      "2024-01-15": 6.50
    }
  },
  "cache_stats": {
    "overall": {
      "total_requests": 10000,
      "hit_rate": 78.5,
      "l1_hit_rate": 45.2,
      "l2_hit_rate": 28.1,
      "l3_hit_rate": 5.2,
      "total_cost_saved": 123.45,
      "total_tokens_saved": 150000
    }
  },
  "queue_stats": {
    "manager_stats": {
      "total_queues": 3,
      "total_workers": 10,
      "active_workers": 6,
      "total_requests_processed": 50000,
      "avg_queue_wait_time": 2.3,
      "system_throughput": 125.5
    }
  },
  "period_days": 7,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Optimization Strategies

### Cost Optimization Strategies

1. **Lowest Cost**: Always selects the cheapest available provider
2. **Fastest Response**: Prioritizes speed over cost
3. **Balanced**: Optimizes for both cost and performance (default)
4. **Quality Focused**: Prioritizes response quality
5. **Budget Constrained**: Respects strict budget limits

### Caching Strategies

1. **L1 Cache**: In-memory cache for ultra-fast access
2. **L2 Cache**: Redis cache for distributed access
3. **L3 Cache**: Persistent cache for long-term storage

### Queue Priorities

- **Critical (9-10)**: Emergency requests, system-critical operations
- **High (7-8)**: Important user requests, premium features
- **Medium (5-6)**: Standard user requests (default)
- **Low (3-4)**: Background tasks, analytics
- **Background (1-2)**: Maintenance, cleanup tasks

## Error Handling

### HTTP Status Codes

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error
- `503 Service Unavailable**: Service temporarily unavailable

### Error Response Format

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Prompt cannot be empty",
    "details": {
      "field": "prompt",
      "validation": "required"
    },
    "request_id": "req_abc123",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### Common Errors

| Error Code | Description | Solution |
|------------|-------------|----------|
| `INVALID_REQUEST` | Request parameters are invalid | Check request format |
| `MODEL_NOT_SUPPORTED` | Requested model is not available | Use supported model |
| `BUDGET_EXCEEDED` | Request exceeds budget limit | Increase budget or use cheaper model |
| `TIMEOUT` | Request processing timed out | Increase timeout or simplify request |
| `RATE_LIMITED` | Too many requests | Implement backoff strategy |
| `PROVIDER_UNAVAILABLE` | All providers are unavailable | Try again later |

## Rate Limiting

### Default Limits

- **Requests per minute**: 1000
- **Tokens per minute**: 100,000
- **Concurrent requests**: 50

### Rate Limit Headers

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642248600
```

## Best Practices

### 1. Cost Optimization

- Enable caching for repeated requests
- Use cost optimization for non-critical requests
- Set appropriate budget limits
- Monitor usage analytics

### 2. Performance Optimization

- Use appropriate priority levels
- Enable batch processing for multiple requests
- Use streaming for long-running tasks
- Implement client-side caching

### 3. Error Handling

- Implement exponential backoff for retries
- Handle timeout gracefully
- Monitor error rates and alerts
- Use fallback providers

### 4. Security

- Keep API keys secure
- Use HTTPS for all requests
- Validate and sanitize inputs
- Monitor for unusual activity

## SDK Examples

### Python

```python
import httpx
import asyncio

class RaptorflowClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.raptorflow.ai/v1/ai-inference"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def inference(self, prompt, model="gpt-3.5-turbo", **kwargs):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/inference",
                headers=self.headers,
                json={
                    "prompt": prompt,
                    "model_name": model,
                    **kwargs
                }
            )
            return response.json()
    
    async def batch_inference(self, requests, **kwargs):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/batch-inference",
                headers=self.headers,
                json={
                    "requests": requests,
                    **kwargs
                }
            )
            return response.json()

# Usage
client = RaptorflowClient("your-api-key")

result = await client.inference(
    "What is the meaning of life?",
    temperature=0.7,
    use_cache=True,
    cost_optimize=True
)

print(result["response"])
```

### JavaScript

```javascript
class RaptorflowClient {
    constructor(apiKey) {
        this.apiKey = apiKey;
        this.baseUrl = 'https://api.raptorflow.ai/v1/ai-inference';
        this.headers = {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json'
        };
    }

    async inference(prompt, options = {}) {
        const response = await fetch(`${this.baseUrl}/inference`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify({
                prompt,
                model_name: 'gpt-3.5-turbo',
                ...options
            })
        });
        return response.json();
    }

    async batchInference(requests, options = {}) {
        const response = await fetch(`${this.baseUrl}/batch-inference`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify({
                requests,
                ...options
            })
        });
        return response.json();
    }
}

// Usage
const client = new RaptorflowClient('your-api-key');

const result = await client.inference(
    'What is the meaning of life?',
    {
        temperature: 0.7,
        use_cache: true,
        cost_optimize: true
    }
);

console.log(result.response);
```

## Monitoring and Debugging

### Request Tracing

Each request includes a `request_id` for tracing:

```http
X-Request-ID: req_abc123def456
```

### Performance Metrics

Monitor these key metrics:

- **Response Time**: Average time to process requests
- **Cache Hit Rate**: Percentage of requests served from cache
- **Error Rate**: Percentage of failed requests
- **Cost per Request**: Average cost per inference
- **Queue Wait Time**: Average time in queue

### Logging

Enable debug logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Support

- **Documentation**: https://docs.raptorflow.ai
- **API Reference**: https://api.raptorflow.ai/docs
- **Status Page**: https://status.raptorflow.ai
- **Support**: support@raptorflow.ai
- **Community**: https://community.raptorflow.ai

## Changelog

### v1.0.0 (2024-01-15)
- Initial release
- Single and batch inference endpoints
- Multi-level caching system
- Cost optimization
- Provider failover
- Performance monitoring
- Streaming support

### v1.1.0 (Planned)
- A/B testing framework
- Advanced analytics
- Custom model support
- Enhanced security features
