# Vertex AI Client Service

## Overview

The Vertex AI client provides a unified, production-ready interface for accessing Google's Gemini models and Anthropic's Claude models via Google Cloud Vertex AI. It serves as the primary LLM integration layer for the RaptorFlow 2.0 backend.

## Features

- ✅ **Unified Interface**: Single API for both Gemini and Claude models
- ✅ **Streaming Support**: Real-time response streaming with async generators
- ✅ **Automatic Retries**: Exponential backoff for transient failures
- ✅ **JSON Validation**: Schema-based validation with descriptive errors
- ✅ **Correlation Tracking**: Distributed tracing with correlation IDs
- ✅ **Comprehensive Logging**: Structured logging with error context
- ✅ **Singleton Pattern**: Efficient resource management
- ✅ **Type Safety**: Full type hints and Pydantic integration

## Installation & Setup

### Prerequisites

1. **Google Cloud Project**: Set up a GCP project with Vertex AI enabled
2. **Service Account**: Create a service account with Vertex AI permissions
3. **Credentials**: Download service account JSON key

### Environment Variables

Add these to your `.env` file:

```bash
# Required for Vertex AI
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Model Configuration
VERTEX_AI_GEMINI_3_MODEL=gemini-1.5-pro-002
VERTEX_AI_SONNET_4_5_MODEL=claude-3-5-sonnet@20240620

# LLM Defaults
DEFAULT_LLM_TEMPERATURE=0.7
DEFAULT_LLM_MAX_OUTPUT_TOKENS=4096

# Retry Configuration
MAX_RETRIES=3
```

### Authentication

The client uses Application Default Credentials (ADC). Set up authentication:

```bash
# Option 1: Service Account JSON
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Option 2: gcloud CLI (for development)
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

## Usage Examples

### Basic Text Generation

```python
from backend.services.vertex_ai_client import vertex_ai_client

# Simple text generation
response = await vertex_ai_client.generate_text(
    prompt="Explain quantum computing in simple terms",
    system_prompt="You are a helpful physics teacher",
    model="gemini"
)
print(response)
```

### Streaming Responses

```python
# Stream text in real-time
async for chunk in await vertex_ai_client.generate_text(
    prompt="Write a long story about space exploration",
    model="claude",
    stream=True
):
    print(chunk, end="", flush=True)
```

### JSON Generation with Schema Validation

```python
# Define expected schema
user_schema = {
    "type": "object",
    "required": ["name", "email", "age", "interests"],
    "properties": {
        "name": {"type": "string"},
        "email": {"type": "string", "format": "email"},
        "age": {"type": "integer", "minimum": 0},
        "interests": {
            "type": "array",
            "items": {"type": "string"}
        }
    }
}

# Generate validated JSON
user_data = await vertex_ai_client.generate_json(
    prompt="Generate a user profile for a 30-year-old software engineer",
    system_prompt="Return only valid JSON matching the schema",
    model="gemini",
    schema=user_schema,
    strict=True  # Raise error on validation failure
)
```

### Chat Completion (Multi-turn Conversation)

```python
# Multi-turn conversation
messages = [
    {"role": "system", "content": "You are a helpful coding assistant"},
    {"role": "user", "content": "How do I sort a list in Python?"},
    {"role": "assistant", "content": "You can use the sorted() function..."},
    {"role": "user", "content": "What about in-place sorting?"}
]

response = await vertex_ai_client.chat_completion(
    messages=messages,
    model_type="fast",
    temperature=0.5
)
```

### Model Selection

The client supports logical model names that map to specific models:

```python
# Fast Gemini model
response = await vertex_ai_client.generate_text(
    prompt="Quick factual answer needed",
    model="fast"
)

# Creative Claude model
response = await vertex_ai_client.generate_text(
    prompt="Write creative marketing copy",
    model="creative"
)

# Explicit model selection
response = await vertex_ai_client.generate_text(
    prompt="Analyze this data",
    model="gemini"  # or "claude"
)
```

**Available Model Types:**
- `fast`: Fast Gemini model (default)
- `reasoning`: Gemini optimized for reasoning
- `creative`: Claude Sonnet for creative tasks
- `creative_fast`: Claude Sonnet
- `gemini`: Explicit Gemini selection
- `claude`: Explicit Claude selection

## Error Handling

### Automatic Retries

The client automatically retries on transient errors:

- `GoogleAPIError`: General API errors
- `DeadlineExceeded`: Request timeouts
- `ResourceExhausted`: Rate limit errors
- `ServiceUnavailable`: Service temporarily down
- `ConnectionError`: Network issues

**Retry Configuration:**
- Max attempts: 3 (configurable via `MAX_RETRIES`)
- Backoff: Exponential with random jitter (1-30 seconds)

### Manual Error Handling

```python
from google.api_core.exceptions import GoogleAPIError
import json

try:
    result = await vertex_ai_client.generate_json(
        prompt="Generate data",
        schema=my_schema,
        strict=True
    )
except GoogleAPIError as e:
    logger.error(f"Vertex AI API error: {e}")
    # Handle API failure
except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON response: {e}")
    # Handle JSON parsing failure
except ValueError as e:
    logger.error(f"Schema validation failed: {e}")
    # Handle validation failure
```

### Non-Strict Mode for Robustness

```python
# Non-strict mode returns best-effort results
result = await vertex_ai_client.generate_json(
    prompt="Generate data",
    schema=my_schema,
    strict=False  # Won't raise errors, logs warnings instead
)

# Check for errors in response
if "error" in result:
    logger.warning(f"JSON parsing failed: {result['error']}")
    raw_text = result.get("raw", "")

if "_schema_validation_error" in result:
    logger.warning(f"Schema validation failed: {result['_schema_validation_error']}")
    # Data is still available, just doesn't match schema
```

## Integration with Agents

### Basic Agent Pattern

```python
from backend.services.vertex_ai_client import vertex_ai_client
from backend.utils.correlation import get_correlation_id
import structlog

logger = structlog.get_logger(__name__)

class MyAgent:
    def __init__(self):
        self.llm = vertex_ai_client

    async def process(self, user_input: str, correlation_id: str = None):
        correlation_id = correlation_id or get_correlation_id()

        logger.info(
            "Agent processing started",
            agent="MyAgent",
            correlation_id=correlation_id
        )

        messages = [
            {"role": "system", "content": "You are a helpful agent"},
            {"role": "user", "content": user_input}
        ]

        response = await self.llm.chat_completion(
            messages=messages,
            model_type="fast",
            temperature=0.7
        )

        logger.info(
            "Agent processing completed",
            agent="MyAgent",
            correlation_id=correlation_id
        )

        return response
```

## Configuration

### Model Configuration

Edit `backend/config/settings.py` to change model defaults:

```python
# Google Cloud / Vertex AI
GOOGLE_CLOUD_PROJECT: Optional[str] = None
GOOGLE_CLOUD_LOCATION: str = "us-central1"
VERTEX_AI_GEMINI_3_MODEL: str = "gemini-1.5-pro-002"
VERTEX_AI_SONNET_4_5_MODEL: str = "claude-3-5-sonnet@20240620"
DEFAULT_LLM_TEMPERATURE: float = 0.7
DEFAULT_LLM_MAX_OUTPUT_TOKENS: int = 4096

# Model aliases (customize these for your use case)
MODEL_REASONING = VERTEX_AI_GEMINI_3_MODEL
MODEL_FAST = VERTEX_AI_GEMINI_3_MODEL
MODEL_CREATIVE = VERTEX_AI_SONNET_4_5_MODEL
MODEL_CREATIVE_FAST = VERTEX_AI_SONNET_4_5_MODEL
```

### Feature Flags

Enable/disable OpenAI fallback:

```python
# Feature Flags
ENABLE_OPENAI_FALLBACK: bool = False  # Set to True to enable OpenAI fallback
```

**Note:** OpenAI fallback is currently a configuration option but not yet implemented in the client. Future versions will support automatic fallback to OpenAI if Vertex AI is unavailable.

## Testing

Run the test suite:

```bash
# Run all tests
pytest backend/tests/test_vertex_ai_client.py -v

# Run specific test class
pytest backend/tests/test_vertex_ai_client.py::TestTextGeneration -v

# Run with coverage
pytest backend/tests/test_vertex_ai_client.py --cov=backend.services.vertex_ai_client
```

## Migration from OpenAI

All agents have been migrated from `openai_client` to `vertex_ai_client`. The interfaces are compatible:

```python
# Old (OpenAI)
from backend.services.openai_client import openai_client
response = await openai_client.chat_completion(messages)

# New (Vertex AI)
from backend.services.vertex_ai_client import vertex_ai_client
response = await vertex_ai_client.chat_completion(messages)
```

## Performance Considerations

### Streaming vs Non-Streaming

- **Streaming**: Use for long-form content, real-time UIs, or when you need immediate feedback
  - Lower perceived latency
  - Can process chunks as they arrive
  - Better UX for chat interfaces

- **Non-Streaming**: Use for short responses, batch processing, or when you need the complete response
  - Simpler code
  - Better for JSON responses
  - Easier error handling

### Model Selection

- **Gemini (fast)**: Best for factual queries, data analysis, short responses
  - Faster response times
  - Lower cost
  - Good for high-volume operations

- **Claude (creative)**: Best for creative writing, complex reasoning, nuanced content
  - Higher quality output
  - Better at following complex instructions
  - Ideal for marketing copy, blog posts

## Troubleshooting

### "Vertex AI not configured" Error

**Problem:** `RuntimeError: Vertex AI not configured. Set GOOGLE_CLOUD_PROJECT environment variable.`

**Solution:**
1. Ensure `GOOGLE_CLOUD_PROJECT` is set in `.env`
2. Verify credentials: `echo $GOOGLE_APPLICATION_CREDENTIALS`
3. Check service account has Vertex AI permissions

### Authentication Errors

**Problem:** Permission denied or authentication failures

**Solution:**
1. Verify service account JSON is valid
2. Ensure service account has these roles:
   - `roles/aiplatform.user`
   - `roles/ml.developer`
3. Run: `gcloud auth application-default login` for local development

### Rate Limiting

**Problem:** `ResourceExhausted: 429 Too Many Requests`

**Solution:**
- Client automatically retries with backoff
- Consider implementing request queuing for high-volume scenarios
- Monitor quota usage in GCP Console
- Request quota increase if needed

### JSON Validation Failures

**Problem:** Schema validation errors even with valid-looking JSON

**Solution:**
1. Use `strict=False` for debugging to see the raw response
2. Refine your prompt to be more explicit about the schema
3. Add schema description to system prompt
4. Use simpler schemas for better LLM compliance

## Logging and Monitoring

All operations log with correlation IDs for distributed tracing:

```python
from backend.utils.correlation import set_correlation_id

# Set correlation ID for request
set_correlation_id("unique-request-id")

# All subsequent logs will include this ID
response = await vertex_ai_client.generate_text(...)
```

**Log Levels:**
- `DEBUG`: Model parameters, chunk counts, detailed execution
- `INFO`: Request start/completion, timing, high-level operations
- `WARNING`: Retry attempts, non-strict validation failures, salvaged responses
- `ERROR`: API errors, validation failures (strict mode), unexpected exceptions

## Best Practices

1. **Always use correlation IDs** for request tracing
2. **Use streaming** for long-form content to improve UX
3. **Implement schema validation** for structured outputs
4. **Start with non-strict mode** when developing, switch to strict for production
5. **Handle errors gracefully** with appropriate fallbacks
6. **Monitor costs** by tracking model usage and token counts
7. **Use appropriate models** (Gemini for fast/factual, Claude for creative)
8. **Test retry logic** under failure conditions
9. **Cache results** when possible to reduce API calls
10. **Set timeouts** for operations that should complete quickly

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                 VertexAIClient                      │
│  (Singleton instance: vertex_ai_client)             │
├─────────────────────────────────────────────────────┤
│  Public Methods:                                    │
│  - generate_text()      ← Text generation           │
│  - generate_json()      ← JSON with validation      │
│  - chat_completion()    ← Multi-turn conversations  │
├─────────────────────────────────────────────────────┤
│  Internal Methods:                                  │
│  - _call_gemini()       ← Gemini API wrapper        │
│  - _call_claude()       ← Claude API wrapper        │
│  - _resolve_model()     ← Model name resolution     │
│  - _convert_to_gemini_format() ← Message conversion │
├─────────────────────────────────────────────────────┤
│  Dependencies:                                      │
│  - vertexai (Google)    ← Gemini models             │
│  - anthropic (Vertex)   ← Claude models             │
│  - tenacity             ← Retry logic               │
│  - jsonschema           ← Validation                │
│  - structlog            ← Logging                   │
└─────────────────────────────────────────────────────┘
```

## License

Part of RaptorFlow 2.0 - All rights reserved.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review logs with correlation IDs
3. Consult Google Cloud Vertex AI documentation
4. Contact the backend team

---

**Last Updated:** 2025-01-22
**Version:** 2.0.0
