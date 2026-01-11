# Memory System Documentation

## Overview

The Raptorflow Memory System provides comprehensive memory management capabilities including vector storage, knowledge graphs, episodic memory, and working memory. This system enables intelligent information retrieval, context-aware AI interactions, and persistent knowledge management.

## Architecture

### Core Components

1. **Vector Memory** (`vector_store.py`) - Semantic search using pgvector embeddings
2. **Graph Memory** (`graph_memory.py`) - Knowledge graph with entities and relationships
3. **Episodic Memory** (`episodic_memory.py`) - Conversation and session tracking
4. **Working Memory** (`working_memory.py`) - Real-time agent context management
5. **Memory Controller** (`controller.py`) - Unified interface for all memory types

### Specialized Components

- **Vectorizers** - Content-specific embedding generation
- **Graph Builders** - Automated knowledge graph construction
- **Embeddings** - Text-to-vector conversion
- **Chunker** - Content segmentation for optimal storage

## Quick Start

### Basic Usage

```python
from backend.memory import MemoryController, MemoryType

# Initialize memory controller
memory = MemoryController()

# Store content
chunk = MemoryChunk(
    workspace_id="workspace-123",
    memory_type=MemoryType.FOUNDATION,
    content="Our company mission is to revolutionize memory systems",
    metadata={"section": "mission"}
)
await memory.store(chunk)

# Search content
results = await memory.search(
    workspace_id="workspace-123",
    query="company mission",
    limit=10
)
```

### Vector Memory

```python
from backend.memory import VectorMemory, MemoryType

# Initialize vector memory
vector_memory = VectorMemory()

# Store foundation data
from backend.memory.vectorizers import FoundationVectorizer
vectorizer = FoundationVectorizer(vector_memory)

foundation_data = {
    "mission": "To revolutionize memory systems",
    "vision": "Perfect memory recall for everyone",
    "usps": ["Advanced embeddings", "Intelligent graphs"]
}

chunk_ids = await vectorizer.vectorize_foundation("workspace-123", foundation_data)
```

### Graph Memory

```python
from backend.memory import GraphMemory, EntityType, RelationType

# Initialize graph memory
graph_memory = GraphMemory()

# Create entities
company_id = await graph_memory.add_entity(
    workspace_id="workspace-123",
    entity_type=EntityType.COMPANY,
    name="TechCorp",
    properties={"industry": "Technology", "size": "Medium"}
)

# Create relationships
usp_id = await graph_memory.add_entity(
    workspace_id="workspace-123",
    entity_type=EntityType.USP,
    name="Advanced AI algorithms"
)

await graph_memory.add_relationship(
    source_id=company_id,
    target_id=usp_id,
    relation_type=RelationType.HAS_USP,
    weight=1.0
)
```

### Episodic Memory

```python
from backend.memory import EpisodicMemory

# Initialize episodic memory
episodic_memory = EpisodicMemory()

# Create episode
episode_id = await episodic_memory.create_episode(
    workspace_id="workspace-123",
    user_id="user-456",
    session_id="session-789",
    episode_type="conversation",
    title="Product Discussion"
)

# Add conversation turns
await episodic_memory.add_turn(
    episode_id=episode_id,
    role="user",
    content="How does the memory system work?"
)

await episodic_memory.add_turn(
    episode_id=episode_id,
    role="assistant",
    content="The system uses vector embeddings and knowledge graphs..."
)
```

### Working Memory

```python
from backend.memory import WorkingMemory

# Initialize working memory
working_memory = WorkingMemory()

# Create session
session_id = await working_memory.create_session(
    workspace_id="workspace-123",
    user_id="user-456",
    agent_type="assistant"
)

# Add to context window
await working_memory.add_to_context_window(
    session_id=session_id,
    content="User is asking about memory system capabilities",
    content_type="context"
)

# Use scratch pad
await working_memory.write_to_scratch_pad(
    session_id=session_id,
    key="user_intent",
    value="understand_memory_system"
)
```

## Configuration

### Environment Variables

```bash
# Supabase Configuration
SUPABASE_URL=your-supabase-url
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Redis Configuration (for working memory)
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=your-redis-password

# Embedding Model
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_CACHE_SIZE=1000
```

### Database Setup

1. Enable pgvector extension:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

2. Run migrations:
```bash
# Apply all memory system migrations
supabase db push
```

## Memory Types

### Foundation Memory
Stores company foundation information including mission, vision, USPs, and features.

```python
MemoryType.FOUNDATION
```

### ICP Memory
Stores Ideal Customer Profile data including demographics, psychographics, and pain points.

```python
MemoryType.ICP
```

### Move Memory
Stores strategic move information including goals, strategy, and execution plans.

```python
MemoryType.MOVE
```

### Campaign Memory
Stores marketing campaign data and performance metrics.

```python
MemoryType.CAMPAIGN
```

### Research Memory
Stores research findings, insights, and recommendations.

```python
MemoryType.RESEARCH
```

### Conversation Memory
Stores conversation history and interactions.

```python
MemoryType.CONVERSATION
```

### Feedback Memory
Stores user feedback and improvement suggestions.

```python
MemoryType.FEEDBACK
```

## Vectorizers

### Foundation Vectorizer
Processes company foundation data into searchable embeddings.

```python
from backend.memory.vectorizers import FoundationVectorizer

vectorizer = FoundationVectorizer()
await vectorizer.vectorize_foundation(workspace_id, foundation_data)
```

### ICP Vectorizer
Processes ICP profile data into searchable embeddings.

```python
from backend.memory.vectorizers import ICPVectorizer

vectorizer = ICPVectorizer()
await vectorizer.vectorize_icp(workspace_id, icp_data)
```

### Move Vectorizer
Processes strategic move data into searchable embeddings.

```python
from backend.memory.vectorizers import MoveVectorizer

vectorizer = MoveVectorizer()
await vectorizer.vectorize_move(workspace_id, move_data)
```

### Research Vectorizer
Processes research findings into searchable embeddings.

```python
from backend.memory.vectorizers import ResearchVectorizer

vectorizer = ResearchVectorizer()
await vectorizer.vectorize_research(workspace_id, research_data)
```

### Conversation Vectorizer
Processes conversation messages into searchable embeddings.

```python
from backend.memory.vectorizers import ConversationVectorizer

vectorizer = ConversationVectorizer()
await vectorizer.vectorize_conversation(workspace_id, session_id, messages)
```

## Graph Builders

### Company Entity Builder
Builds company entities and relationships in the knowledge graph.

```python
from backend.memory.graph_builders import CompanyEntityBuilder

builder = CompanyEntityBuilder()
company_id = await builder.build_company_entity(workspace_id, foundation_data)
```

### ICP Entity Builder
Builds ICP entities and relationships in the knowledge graph.

```python
from backend.memory.graph_builders import ICPEntityBuilder

builder = ICPEntityBuilder()
icp_id = await builder.build_icp_entity(workspace_id, icp_data)
```

### Competitor Entity Builder
Builds competitor entities and competitive intelligence.

```python
from backend.memory.graph_builders import CompetitorEntityBuilder

builder = CompetitorEntityBuilder()
competitor_id = await builder.build_competitor_entity(workspace_id, competitor_data)
```

### Content Entity Linker
Links content to existing graph entities based on mentions.

```python
from backend.memory.graph_builders import ContentEntityLinker

linker = ContentEntityLinker()
await linker.link_content_to_graph(workspace_id, content_id, content)
```

## API Endpoints

### Memory API
- `POST /api/v1/memory/search` - Search memory
- `POST /api/v1/memory/store` - Store content
- `GET /api/v1/memory/{id}` - Get memory chunk
- `PUT /api/v1/memory/{id}` - Update memory chunk
- `DELETE /api/v1/memory/{id}` - Delete memory chunk
- `GET /api/v1/memory/stats` - Get memory statistics

### Graph API
- `GET /api/v1/graph/entities` - List entities
- `POST /api/v1/graph/entities` - Create entity
- `GET /api/v1/graph/entities/{id}` - Get entity
- `PUT /api/v1/graph/entities/{id}` - Update entity
- `DELETE /api/v1/graph/entities/{id}` - Delete entity
- `GET /api/v1/graph/entities/{id}/relationships` - Get entity relationships
- `POST /api/v1/graph/relationships` - Create relationship
- `GET /api/v1/graph/subgraph` - Get subgraph
- `POST /api/v1/graph/query` - Query graph pattern

### Sessions API
- `GET /api/v1/sessions` - List sessions
- `POST /api/v1/sessions` - Create session
- `GET /api/v1/sessions/{id}` - Get session
- `PUT /api/v1/sessions/{id}` - Update session
- `DELETE /api/v1/sessions/{id}` - Delete session
- `GET /api/v1/sessions/{id}/context` - Get session context
- `POST /api/v1/sessions/{id}/context` - Add to context
- `GET /api/v1/sessions/{id}/scratch` - Get scratch pad
- `POST /api/v1/sessions/{id}/scratch` - Write to scratch pad

### Episodes API
- `GET /api/v1/episodes` - List episodes
- `POST /api/v1/episodes` - Create episode
- `GET /api/v1/episodes/{id}` - Get episode
- `PUT /api/v1/episodes/{id}/end` - End episode
- `GET /api/v1/episodes/{id}/turns` - Get episode turns
- `POST /api/v1/episodes/{id}/turns` - Add turn
- `GET /api/v1/episodes/{id}/summary` - Get episode summary
- `POST /api/v1/episodes/{id}/replay` - Replay episode
- `GET /api/v1/episodes/search` - Search episodes

## Performance Optimization

### Vector Search Optimization
- Use appropriate chunk sizes (400-500 tokens)
- Implement similarity thresholds
- Cache frequently accessed embeddings
- Use vector indexes for large datasets

### Graph Query Optimization
- Limit subgraph depth for complex queries
- Use entity type filters
- Implement relationship caching
- Batch graph operations when possible

### Memory Management
- Implement TTL for working memory
- Regular cleanup of expired sessions
- Monitor memory usage and storage
- Implement data retention policies

## Testing

### Running Tests
```bash
# Run all memory tests
pytest tests/memory/

# Run specific test file
pytest tests/memory/test_vector_store.py

# Run with coverage
pytest tests/memory/ --cov=backend.memory
```

### Test Fixtures
The test suite includes comprehensive fixtures for:
- Mock Supabase and Redis clients
- Sample data for all memory types
- Async test utilities
- Error scenario testing

## Troubleshooting

### Common Issues

1. **pgvector Extension Not Found**
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

2. **Connection Issues**
   - Verify Supabase URL and keys
   - Check Redis connection
   - Ensure network connectivity

3. **Memory Leaks**
   - Monitor session cleanup
   - Check TTL settings
   - Review connection pooling

4. **Performance Issues**
   - Optimize chunk sizes
   - Add database indexes
   - Implement caching strategies

### Debug Mode
Enable debug logging:
```python
import logging
logging.getLogger('backend.memory').setLevel(logging.DEBUG)
```

## Contributing

### Code Style
- Follow PEP 8 guidelines
- Use type hints consistently
- Document all public methods
- Write comprehensive tests

### Adding New Memory Types
1. Update `MemoryType` enum
2. Add corresponding vectorizer
3. Update API endpoints
4. Add tests
5. Update documentation

## License

This memory system is part of the Raptorflow project and follows the project's licensing terms.
