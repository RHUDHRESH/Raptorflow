# RaptorFlow Memory System

A comprehensive memory architecture for the RaptorFlow multi-agent marketing OS, providing conversation memory, agent learning, workspace context, and semantic search capabilities.

## Overview

The memory system enables RaptorFlow agents to:
- Remember conversation history for context-aware responses
- Learn from past performance and feedback
- Access shared workspace context (brand voice, ICPs, preferences)
- Find semantically similar content across all generated assets
- Maintain working memory during complex multi-step tasks

## Architecture

### Memory Types

| Memory Type | Storage Backend | TTL | Purpose |
|------------|----------------|-----|---------|
| **Conversation** | Redis Lists | 1 hour | Session-based message history |
| **Agent** | Redis Hashes | Persistent | Agent performance and learning |
| **Workspace** | Supabase (PostgreSQL) | Persistent | Shared workspace context |
| **Semantic** | ChromaDB | Persistent | Vector-based content search |
| **Working** | Redis | Short (varies) | Temporary execution state |

### Component Structure

```
backend/memory/
├── __init__.py                 # Package initialization
├── README.md                   # This file
├── base.py                     # Abstract base class for all memory types
├── conversation_memory.py      # Session-based conversation storage
├── agent_memory.py             # Agent performance tracking
├── workspace_memory.py         # Shared workspace context
├── semantic_memory.py          # Vector search implementation
├── embeddings.py               # Text embedding generation
└── memory_manager.py           # Unified orchestration layer
```

## Installation

### 1. Install Dependencies

```bash
pip install -r backend/requirements.txt
```

Key dependencies:
- `redis>=5.0.1` - For conversation and agent memory
- `supabase>=2.3.4` - For workspace memory
- `chromadb>=0.4.22` - For semantic search
- `sentence-transformers>=2.2.2` - For embeddings
- `torch>=2.0.0` - For embedding model inference

### 2. Setup Redis

**Using Docker:**
```bash
docker run -d -p 6379:6379 redis:latest
```

**Using local installation:**
```bash
redis-server
```

### 3. Setup Supabase

Create the `workspace_memory` table:

```sql
CREATE TABLE workspace_memory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    memory_key VARCHAR(255) NOT NULL,
    memory_type VARCHAR(50),
    value JSONB NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    embedding vector(384),  -- For future pgvector integration
    UNIQUE(workspace_id, memory_key)
);

CREATE INDEX idx_workspace_memory_workspace ON workspace_memory(workspace_id);
CREATE INDEX idx_workspace_memory_type ON workspace_memory(memory_type);
CREATE INDEX idx_workspace_memory_key ON workspace_memory(workspace_id, memory_key);
```

### 4. Configure Environment

Add to your `.env` file:

```env
# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_MAX_CONNECTIONS=50
REDIS_SOCKET_TIMEOUT=5

# Supabase (already configured)
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_service_key
```

## Usage

### Quick Start

```python
from memory.memory_manager import MemoryManager
from uuid import UUID

# Initialize memory manager
memory = MemoryManager()

# Store a conversation message
await memory.remember(
    memory_type="conversation",
    key="session:abc123",
    value={"role": "user", "content": "Create a campaign"},
    workspace_id=UUID("...")
)

# Retrieve conversation history
messages = await memory.recall(
    memory_type="conversation",
    key="session:abc123",
    workspace_id=UUID("...")
)

# Learn from agent feedback
await memory.learn_from_feedback(
    agent_name="campaign_planner",
    feedback={
        "success": True,
        "rating": 5,
        "strategy": "persona_targeted"
    },
    workspace_id=UUID("...")
)

# Semantic search
results = await memory.search(
    query="AI marketing strategies",
    memory_type="semantic",
    workspace_id=UUID("..."),
    top_k=5
)

# Get comprehensive context
context = await memory.get_context(
    workspace_id=UUID("..."),
    task_type="campaign_planning",
    session_id="session:abc123"
)

# Cleanup when done
await memory.close()
```

### Conversation Memory

**Purpose:** Store session-based message history with automatic expiration.

```python
from memory.conversation_memory import ConversationMemory

conv_memory = ConversationMemory(default_ttl=3600)  # 1 hour TTL

# Store message
await conv_memory.remember(
    key="session:xyz",
    value={
        "role": "user",
        "content": "Help me with content",
        "timestamp": "2024-01-01T10:00:00Z"
    },
    workspace_id=workspace_id,
    ttl=3600
)

# Retrieve messages
messages = await conv_memory.recall(
    key="session:xyz",
    workspace_id=workspace_id
)
```

**Schema:**
- Key: `conversation:{workspace_id}:{session_id}`
- Value: List of message objects with role, content, timestamp
- TTL: 3600 seconds (configurable)

### Agent Memory

**Purpose:** Track agent performance and enable learning from feedback.

```python
from memory.agent_memory import AgentMemory

agent_memory = AgentMemory(max_feedback_history=50)

# Learn from task feedback
await agent_memory.learn_from_feedback(
    key="campaign_planner",
    feedback={
        "task": "campaign_creation",
        "success": True,
        "execution_time": 12.5,
        "user_rating": 5,
        "strategy": "persona_targeted"
    },
    workspace_id=workspace_id
)

# Get agent patterns
patterns = await agent_memory.recall(
    key="campaign_planner",
    workspace_id=workspace_id
)
# Returns: {
#   "total_tasks": 100,
#   "successful_tasks": 85,
#   "success_rate": 0.85,
#   "patterns": {"persona_targeted": {"count": 60, "avg_rating": 4.8}},
#   ...
# }
```

**Schema:**
- Key: `agent:{workspace_id}:{agent_name}`
- Fields: total_tasks, successful_tasks, success_rate, patterns, feedback_history

### Workspace Memory

**Purpose:** Store shared workspace context accessible to all agents.

```python
from memory.workspace_memory import WorkspaceMemory

ws_memory = WorkspaceMemory()

# Store brand voice
await ws_memory.remember(
    key="brand_voice",
    value={
        "tone": "professional yet friendly",
        "values": ["innovation", "transparency"],
        "avoid": ["jargon", "overpromising"]
    },
    workspace_id=workspace_id,
    metadata={"memory_type": "brand_voice"}
)

# Retrieve brand voice
brand = await ws_memory.recall(
    key="brand_voice",
    workspace_id=workspace_id
)

# Search for ICPs
icps = await ws_memory.search(
    query="enterprise",
    workspace_id=workspace_id,
    filters={"memory_type": "icp"}
)
```

**Database Table:** `workspace_memory`
- Columns: id, workspace_id, memory_key, memory_type, value (JSONB), metadata (JSONB)

### Semantic Memory

**Purpose:** Enable semantic search across all content using vector embeddings.

```python
from memory.semantic_memory import SemanticMemory

semantic = SemanticMemory(
    persist_directory="./data/chroma",
    embedding_model="all-MiniLM-L6-v2"
)

# Store content with automatic embedding
await semantic.remember(
    key="campaign_001",
    value="AI-powered marketing automation for SaaS",
    workspace_id=workspace_id,
    metadata={"content_type": "campaign"}
)

# Semantic search (finds based on meaning, not keywords)
results = await semantic.search(
    query="artificial intelligence marketing tools",
    workspace_id=workspace_id,
    top_k=5,
    filters={"content_type": "campaign"}
)
# Returns: [
#   {
#     "id": "campaign_001",
#     "text": "AI-powered marketing automation for SaaS",
#     "similarity": 0.87,
#     "metadata": {...}
#   },
#   ...
# ]

# Find similar content
similar = await semantic.get_similar(
    key="campaign_001",
    workspace_id=workspace_id,
    top_k=5
)
```

**Storage:** ChromaDB collection per workspace
- Collection: `ws_{workspace_id}_semantic`
- Embeddings: 384 or 768 dimensions (model-dependent)

## Memory Manager API

The `MemoryManager` provides a unified interface for all memory operations.

### Core Methods

#### `remember(memory_type, key, value, workspace_id, metadata=None, ttl=None)`
Store information in specified memory type.

#### `recall(memory_type, key, workspace_id, default=None)`
Retrieve information by key.

#### `search(query, memory_type, workspace_id, top_k=5, filters=None)`
Search for information.

#### `forget(memory_type, key, workspace_id)`
Delete information.

#### `learn_from_feedback(agent_name, feedback, workspace_id)`
Update agent memory based on feedback.

#### `get_context(workspace_id, task_type, session_id=None, include_semantic=True)`
Get comprehensive context for a task, aggregating from all memory types.

Returns:
```python
{
    "workspace_id": "...",
    "task_type": "campaign_planning",
    "conversation_history": [...],      # Recent messages
    "agent_patterns": {...},            # Agent performance data
    "workspace_context": {              # Brand, ICPs, preferences
        "brand_voice": {...},
        "icps": [...],
        "preferences": {...}
    },
    "relevant_content": [...]           # Semantically similar content
}
```

## Examples

### Complete workflow example:

```python
from memory.memory_manager import MemoryManager
from uuid import UUID

async def campaign_creation_workflow():
    memory = MemoryManager()
    workspace_id = UUID("...")
    session_id = "session:abc123"

    # 1. User starts conversation
    await memory.remember(
        memory_type="conversation",
        key=session_id,
        value={"role": "user", "content": "Create AI campaign"},
        workspace_id=workspace_id
    )

    # 2. Agent gets context
    context = await memory.get_context(
        workspace_id=workspace_id,
        task_type="campaign_planning",
        session_id=session_id
    )

    # 3. Agent uses context to create campaign
    # ... agent logic here ...

    # 4. Store result in semantic memory
    await memory.remember(
        memory_type="semantic",
        key="campaign_xyz",
        value="AI-driven campaign for tech startups...",
        workspace_id=workspace_id,
        metadata={"content_type": "campaign"}
    )

    # 5. Learn from feedback
    await memory.learn_from_feedback(
        agent_name="campaign_planner",
        feedback={"success": True, "rating": 5},
        workspace_id=workspace_id
    )

    await memory.close()
```

See `backend/examples/memory_system_example.py` for more detailed examples.

## Performance Considerations

### Redis Performance
- **Connection Pooling:** Reuses connections for efficiency
- **Pipeline Operations:** Batches Redis commands when possible
- **TTL Management:** Automatic cleanup prevents memory bloat

### Embedding Generation
- **Model Caching:** Models loaded once and reused
- **Batch Processing:** Generate embeddings in batches (32 items)
- **GPU Support:** Automatically uses CUDA if available

### Vector Search
- **Local Storage:** ChromaDB stores vectors on disk
- **Indexing:** Automatic indexing for fast similarity search
- **Filtering:** Pre-filters by metadata before vector search

## Testing

Run the example script:

```bash
# Ensure Redis and Supabase are running
python backend/examples/memory_system_example.py
```

Run tests:

```bash
pytest backend/tests/test_memory.py -v
```

## Troubleshooting

### Redis Connection Errors

**Error:** `ConnectionError: Error connecting to Redis`

**Solution:**
- Ensure Redis is running: `redis-cli ping` should return `PONG`
- Check `REDIS_URL` in `.env` file
- Verify firewall/network settings

### Supabase Errors

**Error:** `MemoryError: Failed to store workspace memory`

**Solution:**
- Verify `workspace_memory` table exists
- Check Supabase credentials in `.env`
- Ensure workspace_id exists in workspaces table

### ChromaDB Errors

**Error:** `ImportError: chromadb not installed`

**Solution:**
```bash
pip install chromadb sentence-transformers torch
```

### Embedding Model Download

**First run:** Models download automatically (300-500MB)
- Location: `~/.cache/torch/sentence_transformers/`
- Time: 1-5 minutes depending on connection
- Subsequent runs use cached models

## Advanced Configuration

### Custom Embedding Models

```python
from memory.embeddings import EmbeddingGenerator

# Use higher-quality model (768 dimensions)
embedder = EmbeddingGenerator(model_name="all-mpnet-base-v2")

# Use with semantic memory
semantic = SemanticMemory(embedding_model="all-mpnet-base-v2")
```

### Custom TTL for Conversation Memory

```python
memory = MemoryManager(
    conversation_ttl=7200,  # 2 hours
    max_conversation_messages=200
)
```

### Workspace Memory Types

Use memory_type metadata for categorization:

```python
# Store different types
await ws_memory.remember(
    key="icp_enterprise",
    value={...},
    workspace_id=workspace_id,
    metadata={"memory_type": "icp"}  # icp, brand_voice, preference, custom
)

# Filter by type
icps = await ws_memory.search(
    query="",
    workspace_id=workspace_id,
    filters={"memory_type": "icp"}
)
```

## Future Enhancements

- [ ] Supabase pgvector integration for unified storage
- [ ] Memory compression for long conversations
- [ ] Automated memory importance scoring
- [ ] Cross-workspace memory sharing (for multi-tenant scenarios)
- [ ] Memory export/import for backup
- [ ] Memory analytics dashboard

## Contributing

When adding new memory features:

1. Extend `BaseMemory` abstract class
2. Implement all required methods
3. Add comprehensive docstrings
4. Include usage examples
5. Update this README
6. Add tests to `backend/tests/test_memory.py`

## License

Part of RaptorFlow 2.0 - Enterprise Multi-Agent Marketing OS

---

For questions or issues, please refer to the main RaptorFlow documentation or contact the development team.
