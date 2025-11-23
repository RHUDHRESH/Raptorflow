# Semantic Intelligence Layer

## Overview

The Semantic Intelligence Layer provides deep semantic understanding capabilities for RaptorFlow, going beyond basic content generation to extract intent, entities, emotions, topics, and semantic relationships.

## Architecture

```
backend/semantic/
├── __init__.py                      # Package initialization
├── intent_detector.py               # Multi-layered intent analysis
├── entity_extractor.py              # Entity extraction & knowledge graphs
├── emotional_intelligence.py        # Emotional journey analysis
├── topic_modeler.py                 # Topic extraction & clustering
├── semantic_similarity.py           # Embeddings & similarity computation
├── integration_examples.py          # Integration with agents
├── test_semantic_layer.py           # Comprehensive test suite
└── README.md                        # This file
```

## Core Modules

### 1. Intent Detector (`intent_detector.py`)

Analyzes text to extract multi-layered intents with confidence scores.

**Capabilities:**
- Primary intent detection (main goal/purpose)
- Secondary intent identification
- Hidden intent discovery (implicit goals)
- Emotional intent analysis
- Conversion intent mapping
- Alignment scoring

**Usage:**
```python
from backend.semantic.intent_detector import intent_detector

result = await intent_detector.analyze_intent(
    text="Your content here",
    context={
        "content_type": "blog_post",
        "target_audience": "Marketing Directors",
        "stated_goals": "educate and convert"
    }
)

print(result['primary']['intent'])        # Primary intent description
print(result['primary']['category'])      # inform|persuade|convert|educate|inspire
print(result['primary']['confidence'])    # 0.0 to 1.0
print(result['emotional']['primary_emotion'])
print(result['conversion']['desired_action'])
```

**Output Structure:**
```json
{
  "primary": {
    "intent": "Educate audience about AI marketing automation",
    "confidence": 0.92,
    "category": "educate",
    "evidence": ["quote 1", "quote 2"]
  },
  "secondary": [...],
  "hidden": [...],
  "emotional": {
    "primary_emotion": "curiosity",
    "intensity": 0.80,
    "triggers": ["..."],
    "psychological_drivers": ["..."]
  },
  "conversion": {
    "desired_action": "schedule demo",
    "urgency_level": "high",
    "confidence": 0.88
  },
  "alignment": {
    "context_alignment_score": 0.85,
    "consistency_score": 0.90
  }
}
```

### 2. Entity Extractor (`entity_extractor.py`)

Extracts structured entities and builds knowledge graphs.

**Capabilities:**
- Entity extraction (products, people, organizations, concepts, technologies)
- Relationship mapping
- Knowledge graph construction
- Entity deduplication
- Cumulative graph building

**Usage:**
```python
from backend.semantic.entity_extractor import entity_extractor

result = await entity_extractor.extract_entities_and_relations(
    content="Your content here",
    context={
        "workspace_id": "ws_123",
        "domain": "B2B SaaS"
    }
)

# Access entities
for entity in result['entities']:
    print(f"{entity['text']} ({entity['type']}) - {entity['importance']}")

# Access relationships
for rel in result['relationships']:
    print(f"{rel['source']} -> {rel['relation']} -> {rel['target']}")

# Access knowledge graph
graph = result['knowledge_graph']
print(f"Nodes: {len(graph['nodes'])}")
print(f"Edges: {len(graph['edges'])}")
```

**Entity Types:**
- `PRODUCT` - Products, services, features
- `PERSON` - Individuals, roles, personas
- `ORGANIZATION` - Companies, competitors, partners
- `CONCEPT` - Ideas, methodologies, frameworks
- `TECHNOLOGY` - Tools, platforms, tech stacks
- `LOCATION` - Geographic locations, markets
- `METRIC` - KPIs, statistics, benchmarks
- `EVENT` - Launches, milestones, campaigns

### 3. Emotional Intelligence Agent (`emotional_intelligence.py`)

Analyzes emotional journeys and psychological triggers.

**Capabilities:**
- Emotional arc mapping
- Psychological trigger identification
- Persuasion technique detection
- Emotional resonance scoring
- Sentiment progression tracking
- Ethical assessment

**Usage:**
```python
from backend.semantic.emotional_intelligence import emotional_intelligence_agent

result = await emotional_intelligence_agent.analyze_emotional_journey(
    content="Your content here",
    context={
        "target_audience": "Marketing Directors",
        "content_goal": "educate and inspire",
        "brand_values": ["innovation", "authenticity"]
    }
)

# Emotional arc
arc = result['emotional_arc']
print(f"Trajectory: {arc['trajectory']}")
print(f"From {arc['starting_emotion']} to {arc['ending_emotion']}")

# Resonance scores
resonance = result['emotional_resonance']
print(f"Overall: {resonance['overall_resonance']}")
print(f"Empathy: {resonance['empathy_score']}")
print(f"Authenticity: {resonance['authenticity_score']}")

# Psychological triggers
for trigger in result['psychological_triggers']:
    print(f"{trigger['trigger_type']}: {trigger['effectiveness']}")
```

**Psychological Triggers Detected:**
- Scarcity
- Authority
- Social proof
- Reciprocity
- Commitment & consistency
- Liking & rapport
- Loss aversion
- Curiosity gaps

### 4. Topic Modeler (`topic_modeler.py`)

Extracts topics and performs clustering analysis.

**Capabilities:**
- Topic extraction from documents
- Topic clustering across corpora
- Trend identification
- Topic evolution tracking
- Similar topic discovery

**Usage:**
```python
from backend.semantic.topic_modeler import topic_modeler

# Single document
topics = await topic_modeler.extract_topics(
    content="Your content here",
    context={"domain": "B2B Marketing"}
)

# Corpus analysis
corpus_topics = await topic_modeler.extract_topics_from_corpus(
    documents=[
        {"id": "doc1", "content": "..."},
        {"id": "doc2", "content": "..."}
    ],
    context={"workspace_id": "ws_123"}
)

# Track trends
trends = await topic_modeler.track_topic_trends(
    workspace_id="ws_123",
    time_window_days=30
)
```

### 5. Semantic Similarity (`semantic_similarity.py`)

Computes similarity using embeddings and enables semantic search.

**Capabilities:**
- Embedding generation (OpenAI text-embedding-3-small)
- Cosine similarity computation
- Similar content retrieval
- Duplicate detection
- Semantic search
- Content clustering

**Usage:**
```python
from backend.semantic.semantic_similarity import semantic_similarity

# Compute similarity
similarity = await semantic_similarity.compute_similarity(
    text1="Content A",
    text2="Content B"
)
print(f"Similarity: {similarity:.4f}")  # 0.0 to 1.0

# Find similar content
similar = await semantic_similarity.find_similar_content(
    query_text="AI marketing automation",
    workspace_id="ws_123",
    top_k=5,
    min_similarity=0.75
)

# Detect duplicates
duplicates = await semantic_similarity.detect_duplicates(
    texts=["text1", "text2", "text3"],
    threshold=0.95
)

# Semantic search
results = await semantic_similarity.semantic_search(
    query="search query",
    documents=[{"id": "1", "content": "..."}],
    top_k=10
)

# Store with embedding
await semantic_similarity.store_content_with_embedding(
    workspace_id="ws_123",
    content_id="content_001",
    content="Your content",
    metadata={"type": "blog_post"}
)
```

## Integration with Agents

### Content Agent Integration

Enrich content generation with semantic intelligence:

```python
from backend.semantic.integration_examples import SemanticContentEnhancer

enhancer = SemanticContentEnhancer()

# Before generation: enrich request
enriched_context = await enhancer.enrich_content_request(
    content_request={
        "topic": "AI marketing automation",
        "content_type": "blog_post",
        "goals": "educate and convert"
    },
    context={
        "workspace_id": "ws_123",
        "icp_profile": {...}
    }
)

# After generation: validate quality
validation = await enhancer.validate_generated_content(
    content=generated_content,
    original_request=content_request,
    context=enriched_context
)

if validation['overall_validation']['passes_validation']:
    print("✓ Content meets quality standards")
else:
    print("Recommendations:", validation['overall_validation']['recommendations'])
```

### Research Agent Integration

Enhance ICP building and customer intelligence:

```python
from backend.semantic.integration_examples import SemanticResearchEnhancer

enhancer = SemanticResearchEnhancer()

# Enrich ICP with entities and knowledge graph
enriched_icp = await enhancer.enrich_icp_with_entities(
    icp_data={
        "icp_name": "DevOps Engineers",
        "executive_summary": "...",
        "pain_points": [...]
    },
    workspace_id="ws_123"
)

# Access semantic enrichment
entities = enriched_icp['semantic_enrichment']['key_entities']
graph = enriched_icp['semantic_enrichment']['knowledge_graph']
concepts = enriched_icp['semantic_enrichment']['central_concepts']

# Cluster ICPs by similarity
clusters = await enhancer.cluster_icps_by_similarity(
    icps=[icp1, icp2, icp3],
    workspace_id="ws_123"
)
```

## Memory Integration

All semantic modules automatically store results in workspace memory for future retrieval:

- **Intent analyses**: `workspace:{workspace_id}:intents:{content_id}`
- **Entity data**: `workspace:{workspace_id}:entities:{content_id}`
- **Emotional analyses**: `workspace:{workspace_id}:emotional:{content_id}`
- **Topics**: `workspace:{workspace_id}:topics:{content_id}`
- **Embeddings**: `workspace:{workspace_id}:semantic:{content_id}`
- **Knowledge graphs**: `workspace:{workspace_id}:knowledge_graph`
- **Corpus analyses**: `workspace:{workspace_id}:corpus:{corpus_id}`

All data is cached in Redis with appropriate TTLs:
- Embeddings: 7 days
- Analyses: 24 hours
- Workspace memory: 30-90 days

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
python backend/semantic/test_semantic_layer.py

# Or use pytest
pytest backend/semantic/test_semantic_layer.py -v

# Run specific test
python -c "
import asyncio
from backend.semantic.test_semantic_layer import test_intent_detection
asyncio.run(test_intent_detection())
"
```

Test results are saved to `semantic_test_results.json` with sample outputs from all modules.

## Sample Outputs

### Intent Detection Output
```json
{
  "primary": {
    "intent": "Educate B2B marketers about AI automation benefits",
    "category": "educate",
    "confidence": 0.92
  },
  "emotional": {
    "primary_emotion": "curiosity",
    "intensity": 0.80
  },
  "conversion": {
    "desired_action": "explore AI solutions",
    "urgency_level": "medium"
  }
}
```

### Entity Extraction Output
```json
{
  "entities": [
    {
      "text": "HubSpot",
      "type": "TECHNOLOGY",
      "importance": 0.85,
      "sentiment": "positive"
    },
    {
      "text": "Marketing Directors",
      "type": "PERSON",
      "importance": 0.90,
      "sentiment": "neutral"
    }
  ],
  "relationships": [
    {
      "source": "Marketing Directors",
      "relation": "uses",
      "target": "HubSpot",
      "confidence": 0.90
    }
  ]
}
```

### Emotional Analysis Output
```json
{
  "emotional_arc": {
    "trajectory": "rising",
    "starting_emotion": "concern",
    "ending_emotion": "confidence"
  },
  "emotional_resonance": {
    "overall_resonance": 0.88,
    "empathy_score": 0.90,
    "authenticity_score": 0.92
  },
  "psychological_triggers": [
    {
      "trigger_type": "social_proof",
      "effectiveness": 0.85
    },
    {
      "trigger_type": "authority",
      "effectiveness": 0.78
    }
  ]
}
```

## Best Practices

### 1. Use Context for Better Analysis
Always provide context when available:
```python
result = await intent_detector.analyze_intent(
    text=content,
    context={
        "workspace_id": workspace_id,
        "content_type": "blog_post",
        "target_audience": icp_profile.icp_name,
        "stated_goals": "educate and convert"
    }
)
```

### 2. Cache Management
Semantic analyses are cached automatically. To force refresh:
```python
# Clear specific cache
await redis_cache.delete(f"intent:{content_hash}")

# Or use different context to bypass cache
```

### 3. Batch Processing
Use batch methods for efficiency:
```python
# Intent detection
results = await intent_detector.batch_analyze(
    texts=[text1, text2, text3],
    context=context
)

# Similarity computation
embeddings = await asyncio.gather(*[
    semantic_similarity.get_embedding(text)
    for text in texts
])
```

### 4. Error Handling
All modules include comprehensive error handling:
```python
try:
    result = await entity_extractor.extract_entities_and_relations(content)
except Exception as e:
    logger.error(f"Entity extraction failed: {e}")
    # Fallback logic
```

### 5. Memory Storage
Store important analyses for future reference:
```python
# Automatically stored when workspace_id provided
result = await intent_detector.analyze_intent(
    text=content,
    context={"workspace_id": "ws_123", "content_id": "content_001"}
)

# Retrieved later
cached = await redis_cache.get(f"workspace:ws_123:intents:content_001")
```

## Performance Considerations

- **API Calls**: Each semantic analysis makes 1-2 OpenAI API calls
- **Caching**: Results are cached to minimize repeated API calls
- **Batch Processing**: Use batch methods to process multiple items efficiently
- **Embeddings**: Embedding generation is the most API-intensive operation (use sparingly)
- **Rate Limits**: Built-in retry logic handles rate limits automatically

## Future Enhancements

Planned improvements:
1. **Vector Database Integration**: Replace Redis with Pinecone/Weaviate for better embedding storage
2. **Fine-tuned Models**: Train custom models for domain-specific entity extraction
3. **Real-time Analysis**: Stream processing for live content analysis
4. **Multi-language Support**: Extend to non-English content
5. **Advanced Clustering**: Implement HDBSCAN for better topic clustering
6. **Sentiment Tracking**: Time-series sentiment analysis across content

## API Reference

See individual module docstrings for complete API documentation:
- `backend/semantic/intent_detector.py`
- `backend/semantic/entity_extractor.py`
- `backend/semantic/emotional_intelligence.py`
- `backend/semantic/topic_modeler.py`
- `backend/semantic/semantic_similarity.py`

## Support

For issues or questions:
1. Check the test suite for usage examples
2. Review integration examples in `integration_examples.py`
3. Consult module docstrings for detailed API docs
4. Review logs for debugging (uses structlog)

---

**Version**: 1.0.0
**Last Updated**: 2025-11-22
**Maintainer**: RaptorFlow Engineering Team
