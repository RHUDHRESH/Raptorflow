# Unified Inference Engine Migration Guide
==========================================

This guide helps you migrate from separate `REAL_INFERENCE_ENGINE.py` and `SIMULATED` versions to the new unified inference engine.

## Overview

The new [`UnifiedInferenceEngine`](backend/core/unified_inference_engine.py) provides a single, unified interface that seamlessly switches between REAL and SIMULATED modes based on configuration. No code changes are required to switch between modes.

## Quick Start

```python
# Import the unified engine
from backend.core.unified_inference_engine import (
    UnifiedInferenceEngine,
    UnifiedRequest,
    UnifiedResponse,
    InferenceMode,
    ResponseStyle,
    InferenceContext,
    get_inference_engine,
)

# Get the engine instance (singleton)
engine = get_inference_engine()

# Create a request
request = UnifiedRequest(
    prompt="Your prompt here",
    model="gemini-1.5-pro",
    temperature=0.7,
    style=ResponseStyle.PROFESSIONAL,
)

# Generate response
response = await engine.generate(request)
print(response.content)
```

## Configuration

The inference mode is controlled via the `INFERENCE_MODE` environment variable:

| Mode | Description | Environment Variable |
|-------|-------------|---------------------|
| REAL | Uses actual LLM providers (OpenAI, Google, Anthropic) | `INFERENCE_MODE=real` |
| SIMULATE | Uses simulated responses for development/testing | `INFERENCE_MODE=simulate` |
| AUTO | Auto-detects based on available API keys | `INFERENCE_MODE=auto` (default) |

### Setting the Mode

Add to your `.env` file:

```bash
# For real inference (requires API keys)
INFERENCE_MODE=real

# For simulated inference (no API keys needed)
INFERENCE_MODE=simulate

# For auto-detection (default)
INFERENCE_MODE=auto
```

## Migration from Separate Engines

### Before (Separate Files)

```python
# Old approach - separate files
from REAL_INFERENCE_ENGINE import RealInferenceEngine
from SIMULATED_ENGINE import SimulatedInferenceEngine

# You had to conditionally import and use different engines
if USE_REAL_ENGINE:
    engine = RealInferenceEngine()
else:
    engine = SimulatedInferenceEngine()
```

### After (Unified Engine)

```python
# New approach - single unified engine
from backend.core.unified_inference_engine import get_inference_engine

# Single engine handles both modes automatically
engine = get_inference_engine()

# Mode is controlled by INFERENCE_MODE environment variable
# No code changes needed to switch modes!
```

## API Reference

### UnifiedRequest

```python
@dataclass
class UnifiedRequest:
    prompt: str                              # Required: The user's prompt
    system_prompt: Optional[str] = None      # Optional: System prompt for the LLM
    context: Optional[InferenceContext] = None  # Optional: Request context
    model: str = "gemini-1.5-pro"        # Model to use
    temperature: float = 0.7                  # Sampling temperature (0.0-2.0)
    max_tokens: int = 2048                  # Maximum tokens to generate
    style: ResponseStyle = ResponseStyle.PROFESSIONAL  # Response style (for simulated mode)
    stream: bool = False                      # Enable streaming
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional metadata
```

### UnifiedResponse

```python
@dataclass
class UnifiedResponse:
    content: str                              # Generated response content
    model: str                               # Model used
    mode: InferenceMode                        # Mode used (REAL/SIMULATE)
    request_id: str                           # Unique request ID
    response_time_ms: float                     # Response time in milliseconds
    tokens_used: int                           # Tokens used
    cost_usd: float                           # Cost in USD
    cached: bool = False                        # Whether response was cached
    finish_reason: Optional[str] = None        # Finish reason
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional metadata
```

### InferenceMode

```python
class InferenceMode(str, Enum):
    REAL = "real"        # Use actual LLM providers
    SIMULATE = "simulate"  # Use simulated responses
    AUTO = "auto"        # Auto-detect based on API keys
```

### ResponseStyle

```python
class ResponseStyle(str, Enum):
    CREATIVE = "creative"        # More varied, imaginative responses
    PROFESSIONAL = "professional"  # Formal, business-like responses
    TECHNICAL = "technical"      # Detailed, technical responses
    CONCISE = "concise"        # Short, direct responses
```

### InferenceContext

```python
@dataclass
class InferenceContext:
    request_id: str                    # Request ID
    workspace_id: str                  # Workspace ID
    user_id: str                       # User ID
    session_id: str                     # Session ID
    timestamp: datetime = field(default_factory=datetime.utcnow)  # Request timestamp
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional context
```

## Advanced Usage

### Streaming Responses

```python
async def stream_response():
    engine = get_inference_engine()

    request = UnifiedRequest(
        prompt="Tell me about AI",
        stream=True,
    )

    async for chunk in engine.generate_stream(request):
        print(chunk, end="", flush=True)
```

### With Context

```python
async def with_context():
    engine = get_inference_engine()

    context = InferenceContext(
        request_id="req-123",
        workspace_id="ws-456",
        user_id="user-789",
        session_id="sess-abc",
        metadata={"workspace": "Marketing", "user": "Admin"},
    )

    request = UnifiedRequest(
        prompt="Generate a marketing plan",
        context=context,
    )

    response = await engine.generate(request)
```

### Runtime Mode Switching

```python
async def switch_modes():
    engine = get_inference_engine()

    # Check current mode
    status = engine.get_status()
    print(f"Current mode: {status['mode']}")
    print(f"Real available: {status['real_available']}")

    # Switch to real mode
    engine.set_mode(InferenceMode.REAL)

    # Generate request
    request = UnifiedRequest(prompt="Hello")
    response = await engine.generate(request)
    print(f"Response mode: {response.mode}")
```

## Benefits of Unified Engine

1. **Single Interface**: One import, one engine instance
2. **Zero Code Changes**: Switch modes via environment variable only
3. **Auto-Detection**: Automatically detects API keys and chooses appropriate mode
4. **Consistent API**: Same interface regardless of mode
5. **Graceful Fallback**: Falls back to simulation if real engine fails
6. **Caching**: Built-in caching for both modes
7. **Streaming Support**: Both modes support streaming responses
8. **Metrics**: Consistent token counting and cost tracking

## Troubleshooting

### Engine Not Using Real Mode

If you set `INFERENCE_MODE=real` but the engine is still using simulated mode:

1. Check your API keys are set:
   ```bash
   echo $OPENAI_API_KEY
   echo $GOOGLE_API_KEY
   echo $ANTHROPIC_API_KEY
   ```

2. Check the logs for initialization errors:
   ```bash
   # Look for "Failed to initialize real engine" or "No API keys found"
   ```

3. Verify your LLM provider configuration in `backend/config.py`

### Import Errors

If you get import errors:

```python
# Old import (will fail)
from REAL_INFERENCE_ENGINE import RealInferenceEngine

# New import (correct)
from backend.core.unified_inference_engine import UnifiedInferenceEngine
```

## Examples

### Example 1: Simple Prompt

```python
from backend.core.unified_inference_engine import get_inference_engine, UnifiedRequest

async def main():
    engine = get_inference_engine()

    request = UnifiedRequest(
        prompt="What is the capital of France?",
        model="gemini-1.5-pro",
    )

    response = await engine.generate(request)

    print(f"Response: {response.content}")
    print(f"Mode: {response.mode}")
    print(f"Tokens: {response.tokens_used}")
    print(f"Cost: ${response.cost_usd:.4f}")
```

### Example 2: With System Prompt

```python
from backend.core.unified_inference_engine import get_inference_engine, UnifiedRequest

async def with_system_prompt():
    engine = get_inference_engine()

    request = UnifiedRequest(
        prompt="Summarize this text",
        system_prompt="You are a helpful assistant. Be concise.",
        model="gemini-1.5-pro",
        style=ResponseStyle.CONCISE,
    )

    response = await engine.generate(request)
    return response.content
```

### Example 3: Streaming

```python
from backend.core.unified_inference_engine import get_inference_engine, UnifiedRequest

async def streaming_example():
    engine = get_inference_engine()

    request = UnifiedRequest(
        prompt="Write a short story",
        stream=True,
        style=ResponseStyle.CREATIVE,
    )

    print("Streaming response:")
    async for chunk in engine.generate_stream(request):
        print(chunk, end="", flush=True)
```

### Example 4: Check Engine Status

```python
from backend.core.unified_inference_engine import get_inference_engine

async def check_status():
    engine = get_inference_engine()

    status = engine.get_status()

    print(f"Mode: {status['mode']}")
    print(f"Real Available: {status['real_available']}")
    print(f"Providers: {status['providers_available']}")
```

## Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `INFERENCE_MODE` | Inference mode: real, simulate, or auto | `auto` |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `GOOGLE_API_KEY` | Google API key | - |
| `ANTHROPIC_API_KEY` | Anthropic API key | - |

## File Locations

- **Unified Engine**: [`backend/core/unified_inference_engine.py`](backend/core/unified_inference_engine.py)
- **Core Exports**: [`backend/core/__init__.py`](backend/core/__init__.py)
- **Configuration**: [`backend/config.py`](backend/config.py)
- **LLM Manager**: [`backend/llm.py`](backend/llm.py)

## Support

For issues or questions:
1. Check the logs for initialization messages
2. Verify environment variables are set correctly
3. Review the [`UnifiedInferenceEngine`](backend/core/unified_inference_engine.py) source code
4. Check API key configuration in [`backend/config.py`](backend/config.py)
==========================================

This guide helps you migrate from separate `REAL_INFERENCE_ENGINE.py` and `SIMULATED` versions to the new unified inference engine.

## Overview

The new [`UnifiedInferenceEngine`](backend/core/unified_inference_engine.py) provides a single, unified interface that seamlessly switches between REAL and SIMULATED modes based on configuration. No code changes are required to switch between modes.

## Quick Start

```python
# Import the unified engine
from backend.core.unified_inference_engine import (
    UnifiedInferenceEngine,
    UnifiedRequest,
    UnifiedResponse,
    InferenceMode,
    ResponseStyle,
    InferenceContext,
    get_inference_engine,
)

# Get the engine instance (singleton)
engine = get_inference_engine()

# Create a request
request = UnifiedRequest(
    prompt="Your prompt here",
    model="gemini-1.5-pro",
    temperature=0.7,
    style=ResponseStyle.PROFESSIONAL,
)

# Generate response
response = await engine.generate(request)
print(response.content)
```

## Configuration

The inference mode is controlled via the `INFERENCE_MODE` environment variable:

| Mode | Description | Environment Variable |
|-------|-------------|---------------------|
| REAL | Uses actual LLM providers (OpenAI, Google, Anthropic) | `INFERENCE_MODE=real` |
| SIMULATE | Uses simulated responses for development/testing | `INFERENCE_MODE=simulate` |
| AUTO | Auto-detects based on available API keys | `INFERENCE_MODE=auto` (default) |

### Setting the Mode

Add to your `.env` file:

```bash
# For real inference (requires API keys)
INFERENCE_MODE=real

# For simulated inference (no API keys needed)
INFERENCE_MODE=simulate

# For auto-detection (default)
INFERENCE_MODE=auto
```

## Migration from Separate Engines

### Before (Separate Files)

```python
# Old approach - separate files
from REAL_INFERENCE_ENGINE import RealInferenceEngine
from SIMULATED_ENGINE import SimulatedInferenceEngine

# You had to conditionally import and use different engines
if USE_REAL_ENGINE:
    engine = RealInferenceEngine()
else:
    engine = SimulatedInferenceEngine()
```

### After (Unified Engine)

```python
# New approach - single unified engine
from backend.core.unified_inference_engine import get_inference_engine

# Single engine handles both modes automatically
engine = get_inference_engine()

# Mode is controlled by INFERENCE_MODE environment variable
# No code changes needed to switch modes!
```

## API Reference

### UnifiedRequest

```python
@dataclass
class UnifiedRequest:
    prompt: str                              # Required: The user's prompt
    system_prompt: Optional[str] = None      # Optional: System prompt for the LLM
    context: Optional[InferenceContext] = None  # Optional: Request context
    model: str = "gemini-1.5-pro"        # Model to use
    temperature: float = 0.7                  # Sampling temperature (0.0-2.0)
    max_tokens: int = 2048                  # Maximum tokens to generate
    style: ResponseStyle = ResponseStyle.PROFESSIONAL  # Response style (for simulated mode)
    stream: bool = False                      # Enable streaming
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional metadata
```

### UnifiedResponse

```python
@dataclass
class UnifiedResponse:
    content: str                              # Generated response content
    model: str                               # Model used
    mode: InferenceMode                        # Mode used (REAL/SIMULATE)
    request_id: str                           # Unique request ID
    response_time_ms: float                     # Response time in milliseconds
    tokens_used: int                           # Tokens used
    cost_usd: float                           # Cost in USD
    cached: bool = False                        # Whether response was cached
    finish_reason: Optional[str] = None        # Finish reason
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional metadata
```

### InferenceMode

```python
class InferenceMode(str, Enum):
    REAL = "real"        # Use actual LLM providers
    SIMULATE = "simulate"  # Use simulated responses
    AUTO = "auto"        # Auto-detect based on API keys
```

### ResponseStyle

```python
class ResponseStyle(str, Enum):
    CREATIVE = "creative"        # More varied, imaginative responses
    PROFESSIONAL = "professional"  # Formal, business-like responses
    TECHNICAL = "technical"      # Detailed, technical responses
    CONCISE = "concise"        # Short, direct responses
```

### InferenceContext

```python
@dataclass
class InferenceContext:
    request_id: str                    # Request ID
    workspace_id: str                  # Workspace ID
    user_id: str                       # User ID
    session_id: str                     # Session ID
    timestamp: datetime = field(default_factory=datetime.utcnow)  # Request timestamp
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional context
```

## Advanced Usage

### Streaming Responses

```python
async def stream_response():
    engine = get_inference_engine()

    request = UnifiedRequest(
        prompt="Tell me about AI",
        stream=True,
    )

    async for chunk in engine.generate_stream(request):
        print(chunk, end="", flush=True)
```

### With Context

```python
async def with_context():
    engine = get_inference_engine()

    context = InferenceContext(
        request_id="req-123",
        workspace_id="ws-456",
        user_id="user-789",
        session_id="sess-abc",
        metadata={"workspace": "Marketing", "user": "Admin"},
    )

    request = UnifiedRequest(
        prompt="Generate a marketing plan",
        context=context,
    )

    response = await engine.generate(request)
```

### Runtime Mode Switching

```python
async def switch_modes():
    engine = get_inference_engine()

    # Check current mode
    status = engine.get_status()
    print(f"Current mode: {status['mode']}")
    print(f"Real available: {status['real_available']}")

    # Switch to real mode
    engine.set_mode(InferenceMode.REAL)

    # Generate request
    request = UnifiedRequest(prompt="Hello")
    response = await engine.generate(request)
    print(f"Response mode: {response.mode}")
```

## Benefits of Unified Engine

1. **Single Interface**: One import, one engine instance
2. **Zero Code Changes**: Switch modes via environment variable only
3. **Auto-Detection**: Automatically detects API keys and chooses appropriate mode
4. **Consistent API**: Same interface regardless of mode
5. **Graceful Fallback**: Falls back to simulation if real engine fails
6. **Caching**: Built-in caching for both modes
7. **Streaming Support**: Both modes support streaming responses
8. **Metrics**: Consistent token counting and cost tracking

## Troubleshooting

### Engine Not Using Real Mode

If you set `INFERENCE_MODE=real` but the engine is still using simulated mode:

1. Check your API keys are set:
   ```bash
   echo $OPENAI_API_KEY
   echo $GOOGLE_API_KEY
   echo $ANTHROPIC_API_KEY
   ```

2. Check the logs for initialization errors:
   ```bash
   # Look for "Failed to initialize real engine" or "No API keys found"
   ```

3. Verify your LLM provider configuration in `backend/config.py`

### Import Errors

If you get import errors:

```python
# Old import (will fail)
from REAL_INFERENCE_ENGINE import RealInferenceEngine

# New import (correct)
from backend.core.unified_inference_engine import UnifiedInferenceEngine
```

## Examples

### Example 1: Simple Prompt

```python
from backend.core.unified_inference_engine import get_inference_engine, UnifiedRequest

async def main():
    engine = get_inference_engine()

    request = UnifiedRequest(
        prompt="What is the capital of France?",
        model="gemini-1.5-pro",
    )

    response = await engine.generate(request)

    print(f"Response: {response.content}")
    print(f"Mode: {response.mode}")
    print(f"Tokens: {response.tokens_used}")
    print(f"Cost: ${response.cost_usd:.4f}")
```

### Example 2: With System Prompt

```python
from backend.core.unified_inference_engine import get_inference_engine, UnifiedRequest

async def with_system_prompt():
    engine = get_inference_engine()

    request = UnifiedRequest(
        prompt="Summarize this text",
        system_prompt="You are a helpful assistant. Be concise.",
        model="gemini-1.5-pro",
        style=ResponseStyle.CONCISE,
    )

    response = await engine.generate(request)
    return response.content
```

### Example 3: Streaming

```python
from backend.core.unified_inference_engine import get_inference_engine, UnifiedRequest

async def streaming_example():
    engine = get_inference_engine()

    request = UnifiedRequest(
        prompt="Write a short story",
        stream=True,
        style=ResponseStyle.CREATIVE,
    )

    print("Streaming response:")
    async for chunk in engine.generate_stream(request):
        print(chunk, end="", flush=True)
```

### Example 4: Check Engine Status

```python
from backend.core.unified_inference_engine import get_inference_engine

async def check_status():
    engine = get_inference_engine()

    status = engine.get_status()

    print(f"Mode: {status['mode']}")
    print(f"Real Available: {status['real_available']}")
    print(f"Providers: {status['providers_available']}")
```

## Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `INFERENCE_MODE` | Inference mode: real, simulate, or auto | `auto` |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `GOOGLE_API_KEY` | Google API key | - |
| `ANTHROPIC_API_KEY` | Anthropic API key | - |

## File Locations

- **Unified Engine**: [`backend/core/unified_inference_engine.py`](backend/core/unified_inference_engine.py)
- **Core Exports**: [`backend/core/__init__.py`](backend/core/__init__.py)
- **Configuration**: [`backend/config.py`](backend/config.py)
- **LLM Manager**: [`backend/llm.py`](backend/llm.py)

## Support

For issues or questions:
1. Check the logs for initialization messages
2. Verify environment variables are set correctly
3. Review the [`UnifiedInferenceEngine`](backend/core/unified_inference_engine.py) source code
4. Check API key configuration in [`backend/config.py`](backend/config.py)
