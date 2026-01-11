# STREAM 2: MEMORY SYSTEMS (100 Prompts)

> **INSTRUCTIONS**: Copy each prompt to your AI assistant. Each is self-contained.
> **CONTEXT**: Reference `DOCUMENTATION/SWARM/IMPLEMENTATION/02_MEMORY_SYSTEMS.md`

---

## PROMPTS 1-25: Vector Memory (pgvector)

### PROMPT 1
```
Run this SQL in Supabase SQL Editor to enable pgvector extension:
CREATE EXTENSION IF NOT EXISTS vector;
Then verify with: SELECT * FROM pg_extension WHERE extname = 'vector';
```

### PROMPT 2
```
Create supabase/migrations/20240201_memory_vectors.sql: Table memory_vectors with id UUID PK, workspace_id UUID FK workspaces ON DELETE CASCADE, memory_type TEXT CHECK IN ('foundation','icp','move','campaign','research','conversation','feedback'), content TEXT NOT NULL, metadata JSONB DEFAULT '{}', embedding vector(384) NOT NULL, reference_id UUID, reference_table TEXT, created_at, updated_at. Indexes on workspace_id, (workspace_id, memory_type), and ivfflat on embedding.
```

### PROMPT 3
```
Create supabase/migrations/20240201_memory_vectors_rls.sql: Enable RLS on memory_vectors. Policy "Workspace isolation" FOR ALL USING workspace_id IN (SELECT id FROM workspaces WHERE user_id = auth.uid()).
```

### PROMPT 4
```
Create supabase/migrations/20240201_similarity_search.sql: Function search_memory_vectors(p_workspace_id UUID, p_query_embedding vector(384), p_memory_types TEXT[], p_limit INT DEFAULT 10) RETURNS TABLE (id, content, metadata, memory_type, similarity FLOAT). Use 1 - (embedding <=> p_query_embedding) for cosine similarity. Filter by workspace and optional types. ORDER BY similarity DESC.
```

### PROMPT 5
```
Create backend/memory/__init__.py exporting: VectorMemory, GraphMemory, EpisodicMemory, WorkingMemory, MemoryController, MemoryType, MemoryChunk.
```

### PROMPT 6
```
Create backend/memory/models.py: MemoryType enum (FOUNDATION, ICP, MOVE, CAMPAIGN, RESEARCH, CONVERSATION, FEEDBACK). @dataclass MemoryChunk with id, workspace_id, memory_type, content, metadata, embedding (np.ndarray | None), score (float | None), created_at.
```

### PROMPT 7
```
Create backend/memory/embeddings.py: Singleton EmbeddingModel using SentenceTransformer("all-MiniLM-L6-v2"). Methods: encode(texts: List[str]) -> np.ndarray, encode_single(text: str) -> np.ndarray. Normalize embeddings. @lru_cache decorator for caching.
```

### PROMPT 8
```
Create backend/memory/chunker.py: ContentChunker using RecursiveCharacterTextSplitter from langchain. __init__(chunk_size=500, overlap=50). chunk(content: str) -> List[str]. Separators: ["\n\n", "\n", ". ", " ", ""].
```

### PROMPT 9
```
Create backend/memory/vector_store.py: VectorMemory class using Supabase client and EmbeddingModel. Methods: async store(workspace_id, memory_type, content, metadata) -> str, async search(workspace_id, query, memory_types, limit=10) -> List[MemoryChunk], async delete(chunk_id), async update(chunk_id, content, metadata).
```

### PROMPT 10
```
Create backend/memory/vectorizers/__init__.py exporting: FoundationVectorizer, ICPVectorizer, MoveVectorizer, ResearchVectorizer, ConversationVectorizer.
```

### PROMPT 11
```
Create backend/memory/vectorizers/foundation.py: FoundationVectorizer with vector_store. async vectorize_foundation(workspace_id, foundation: dict) extracts sections (mission, vision, USPs, etc.), chunks each, stores with metadata including section name. async update_foundation_vectors(), async delete_foundation_vectors().
```

### PROMPT 12
```
Create backend/memory/vectorizers/icp.py: ICPVectorizer. async vectorize_icp(workspace_id, icp: dict) extracts demographics, psychographics, behaviors, pain points. Creates searchable chunks with icp_id in metadata. async update_icp_vectors(), async delete_icp_vectors().
```

### PROMPT 13
```
Create backend/memory/vectorizers/move.py: MoveVectorizer. async vectorize_move(workspace_id, move: dict) vectorizes goals, strategy, execution plan. async vectorize_move_output(workspace_id, move_id, output: dict) stores generated content linked to move.
```

### PROMPT 14
```
Create backend/memory/vectorizers/research.py: ResearchVectorizer. async vectorize_research(workspace_id, research: dict) stores findings with source citations in metadata. async search_past_research(workspace_id, query) finds related prior research.
```

### PROMPT 15
```
Create backend/memory/vectorizers/conversation.py: ConversationVectorizer. async vectorize_conversation(workspace_id, session_id, messages: List[dict]) extracts key turns, decisions, action items. async search_conversations(workspace_id, query) enables history search.
```

### PROMPT 16
```
Create backend/memory/search.py: MemorySearch class. async search_all(workspace_id, query, limit=10) searches all types. async search_by_types(workspace_id, query, types: List[MemoryType]) filters by type. async get_relevant_context(workspace_id, query, max_tokens=2000) returns compressed context string.
```

### PROMPT 17
```
Create backend/memory/retriever.py: WorkspaceRetriever(BaseRetriever) LangChain-compatible. workspace_id, memory_types, k=5 fields. async _aget_relevant_documents(query) returns List[Document] from MemorySearch. Integration with LangChain chains.
```

### PROMPT 18
```
Create backend/memory/deduplication.py: @dataclass DuplicateSet with original_id, duplicate_ids, similarity. async find_duplicates(workspace_id, threshold=0.95) finds near-duplicates. async merge_duplicates(duplicate_set) keeps best metadata. async deduplicate_workspace(workspace_id).
```

### PROMPT 19
```
Create backend/memory/pruning.py: @dataclass MemoryStats with total_chunks, by_type, storage_bytes, avg_age_days. async prune_old_memories(workspace_id, days_old=90) archives then deletes. async prune_low_value_memories(workspace_id, min_access_count=0). async get_memory_stats(workspace_id).
```

### PROMPT 20
```
Create backend/memory/hybrid_search.py: async hybrid_search(workspace_id, query, semantic_weight=0.7) combines BM25 keyword + vector search. Reranks results. Returns fused ranking.
```

### PROMPT 21
```
Create backend/memory/reranker.py: CrossEncoderReranker using cross-encoder/ms-marco-MiniLM-L-6-v2. async rerank(query, chunks: List[MemoryChunk], top_k) rescores with cross-encoder, returns top_k.
```

### PROMPT 22
```
Create backend/memory/compression.py: ContextCompressor using LLM. async compress_context(chunks: List[MemoryChunk], max_tokens) summarizes multiple chunks. async extract_key_facts(chunks) extracts bullet points. Respects token budget.
```

### PROMPT 23
```
Create backend/memory/indexing.py: MemoryIndexer background service. async index_content(workspace_id, content_type, content_id, content) creates vectors. async reindex_workspace(workspace_id) rebuilds all. @dataclass IndexingStatus with total, indexed, pending, errors.
```

### PROMPT 24
```
Create backend/memory/export.py: async export_memories(workspace_id, include_embeddings=False) -> dict exports to JSON. async export_to_file(workspace_id, filepath). Include metadata, timestamps.
```

### PROMPT 25
```
Create backend/memory/import.py: async import_memories(workspace_id, data: dict, overwrite=False) imports from JSON. Regenerates embeddings. Handles conflicts. async import_from_file(workspace_id, filepath).
```

---

## PROMPTS 26-50: Graph Memory (Knowledge Graph)

### PROMPT 26
```
Create supabase/migrations/20240202_graph_entities.sql: Table graph_entities with id UUID PK, workspace_id UUID FK, entity_type TEXT CHECK IN ('company','icp','competitor','channel','pain_point','usp','feature','move','campaign','content'), name TEXT NOT NULL, properties JSONB DEFAULT '{}', embedding vector(384), created_at. Indexes on workspace_id, (workspace_id, entity_type), (workspace_id, name).
```

### PROMPT 27
```
Create supabase/migrations/20240202_graph_relationships.sql: Table graph_relationships with id UUID PK, workspace_id UUID FK, source_id UUID FK graph_entities ON DELETE CASCADE, target_id UUID FK graph_entities ON DELETE CASCADE, relation_type TEXT NOT NULL, properties JSONB DEFAULT '{}', weight DECIMAL(3,2) DEFAULT 1.0, created_at. Indexes on workspace_id, source_id, target_id.
```

### PROMPT 28
```
Create supabase/migrations/20240202_graph_rls.sql: Enable RLS on graph_entities and graph_relationships. Policies filter by workspace_id matching user's workspaces.
```

### PROMPT 29
```
Create backend/memory/graph_types.py: EntityType enum (COMPANY, ICP, COMPETITOR, CHANNEL, PAIN_POINT, USP, FEATURE, MOVE, CAMPAIGN, CONTENT). RelationType enum (HAS_ICP, COMPETES_WITH, USES_CHANNEL, SOLVES_PAIN, HAS_USP, HAS_FEATURE, TARGETS, PART_OF, CREATED_BY, MENTIONS).
```

### PROMPT 30
```
Create backend/memory/graph_models.py: @dataclass GraphEntity with id, workspace_id, entity_type, name, properties, embedding. @dataclass GraphRelationship with id, workspace_id, source_id, target_id, relation_type, properties, weight. @dataclass SubGraph with entities, relationships.
```

### PROMPT 31
```
Create backend/memory/graph_store.py: GraphMemory class using Supabase. async add_entity(workspace_id, entity_type, name, properties) -> str. async add_relationship(source_id, target_id, relation_type, weight). async get_entity(entity_id). async find_entities(workspace_id, entity_type, name_pattern). async get_relationships(entity_id, direction="both").
```

### PROMPT 32
```
Create backend/memory/graph_extractor.py: GraphExtractor using LLM. async extract_entities(content: str) -> List[ExtractedEntity] with name, type, confidence. async extract_relationships(content, entities) -> List[ExtractedRelationship]. Prompt templates for NER.
```

### PROMPT 33
```
Create backend/memory/graph_builder.py: GraphBuilder orchestrates graph construction. async build_from_foundation(workspace_id, foundation: dict) creates company, USP, feature entities. async add_icp_to_graph(), async add_competitor_to_graph(), async link_content().
```

### PROMPT 34
```
Create backend/memory/graph_query.py: GraphQueryEngine. async find_path(workspace_id, from_entity, to_entity) -> List[GraphEntity]. async get_subgraph(workspace_id, center_entity, depth=2) -> SubGraph. async find_pattern(workspace_id, pattern: GraphPattern) -> List[PatternMatch].
```

### PROMPT 35
```
Create backend/memory/graph_context.py: GraphContextGenerator. async get_graph_context(workspace_id, focus_entity, max_tokens) builds narrative from subgraph. async generate_entity_summary(entity). async describe_relationships(entity).
```

### PROMPT 36
```
Create backend/memory/graph_builders/company.py: CompanyEntityBuilder. async build_company_entity(workspace_id, foundation) extracts company attributes, creates entity, links to USPs, features, channels.
```

### PROMPT 37
```
Create backend/memory/graph_builders/icp.py: ICPEntityBuilder. async build_icp_entity(workspace_id, icp_profile) creates ICP entity, links to pain points, channels, content that targets them.
```

### PROMPT 38
```
Create backend/memory/graph_builders/competitor.py: CompetitorEntityBuilder. async build_competitor_entity(workspace_id, competitor_data) creates competitor, links COMPETES_WITH company, stores intel.
```

### PROMPT 39
```
Create backend/memory/graph_builders/content.py: ContentEntityLinker. async link_content_to_graph(workspace_id, content_id, content) extracts mentioned entities, creates MENTIONS relationships.
```

### PROMPT 40
```
Create backend/memory/graph_analytics.py: GraphAnalytics. async get_entity_centrality(workspace_id) identifies most connected entities. async find_gaps() identifies missing relationships. async cluster_entities() groups related entities.
```

### PROMPT 41
```
Create backend/memory/graph_visualization.py: GraphVisualizer. async to_d3_format(subgraph) converts to D3.js nodes/links JSON. async to_cytoscape_format(subgraph). Export for frontend visualization.
```

### PROMPT 42
```
Create backend/memory/graph_merge.py: GraphMerger. async merge_duplicate_entities(entity_ids) merges entities with same name. async resolve_entity(workspace_id, name, type) finds or creates. Deduplication logic.
```

---

## PROMPTS 43-60: Episodic Memory

### PROMPT 43
```
Create supabase/migrations/20240203_episodic_memory.sql: Table conversation_episodes with id UUID PK, workspace_id UUID FK, session_id UUID NOT NULL, episode_type TEXT CHECK IN ('conversation','task','approval','feedback'), summary TEXT, key_decisions JSONB DEFAULT '[]', entities_mentioned JSONB DEFAULT '[]', started_at, ended_at, token_count INT. Index on workspace_id, session_id.
```

### PROMPT 44
```
Create supabase/migrations/20240203_conversation_turns.sql: Table conversation_turns with id UUID PK, episode_id UUID FK conversation_episodes ON DELETE CASCADE, role TEXT CHECK IN ('user','assistant','system','tool'), content TEXT NOT NULL, tool_calls JSONB, turn_index INT NOT NULL, timestamp. Index on episode_id.
```

### PROMPT 45
```
Create backend/memory/episodic/__init__.py exporting: EpisodicMemory, Episode, ConversationTurn, EpisodeSummary.
```

### PROMPT 46
```
Create backend/memory/episodic/models.py: @dataclass ConversationTurn with id, role, content, tool_calls, turn_index, timestamp. @dataclass Episode with id, workspace_id, session_id, episode_type, turns, summary, key_decisions, started_at, ended_at.
```

### PROMPT 47
```
Create backend/memory/episodic/store.py: EpisodicMemory class. async create_episode(workspace_id, session_id, episode_type) -> str. async add_turn(episode_id, role, content, tool_calls). async end_episode(episode_id). async get_episode(episode_id). async list_episodes(workspace_id, limit).
```

### PROMPT 48
```
Create backend/memory/episodic/summarizer.py: EpisodeSummarizer using LLM. async summarize_episode(episode: Episode) creates summary, extracts key decisions, mentioned entities. async summarize_session(session_id) aggregates all episodes.
```

### PROMPT 49
```
Create backend/memory/episodic/retrieval.py: EpisodicRetrieval. async search_episodes(workspace_id, query) searches summaries. async get_related_episodes(episode_id) finds similar. async get_session_history(session_id) full history.
```

### PROMPT 50
```
Create backend/memory/episodic/replay.py: EpisodeReplay. async replay_episode(episode_id) reconstructs conversation state. async get_context_at_turn(episode_id, turn_index) state at specific point. For debugging.
```

---

## PROMPTS 51-70: Working Memory (Redis)

### PROMPT 51
```
Create backend/memory/working/__init__.py exporting: WorkingMemory, SessionState, ContextWindow, WorkingMemoryManager.
```

### PROMPT 52
```
Create backend/memory/working/models.py: @dataclass SessionState with session_id, workspace_id, user_id, current_agent, messages (recent), context_window, pending_output, created_at, updated_at, ttl_seconds.
```

### PROMPT 53
```
Create backend/memory/working/redis_client.py: RedisClient wrapper for Upstash. __init__ from config. async get(key), async set(key, value, ttl), async delete(key), async exists(key), async hget/hset/hdel for hashes.
```

### PROMPT 54
```
Create backend/memory/working/store.py: WorkingMemory using RedisClient. async get_session(session_id) -> SessionState. async set_session(session_id, state). async update_session(session_id, **updates). async delete_session(session_id). Key prefix: "session:{session_id}".
```

### PROMPT 55
```
Create backend/memory/working/context_window.py: ContextWindow manages current context. async push(content, type). async get_recent(n). async compress_if_needed(max_tokens). async clear(). Circular buffer behavior.
```

### PROMPT 56
```
Create backend/memory/working/scratch_pad.py: ScratchPad for intermediate agent results. async write(key, value). async read(key). async clear(). TTL auto-expiry. Key prefix: "scratch:{session_id}".
```

### PROMPT 57
```
Create backend/memory/working/locks.py: DistributedLock using Redis. async acquire(resource, timeout=30) -> bool. async release(resource). Context manager support. Prevents concurrent access.
```

### PROMPT 58
```
Create backend/memory/working/pubsub.py: WorkingMemoryPubSub for real-time updates. async publish(channel, message). async subscribe(channel, callback). Channels: session updates, agent handoffs.
```

### PROMPT 59
```
Create backend/memory/working/ttl_manager.py: TTLManager. async refresh_ttl(session_id). async set_custom_ttl(session_id, seconds). async cleanup_expired(). Default TTL: 30 minutes active, 24 hours dormant.
```

### PROMPT 60
```
Create backend/memory/working/session_manager.py: SessionManager orchestrates working memory. async create_session(workspace_id, user_id) -> session_id. async get_or_create_session(). async end_session(session_id). async list_active_sessions(workspace_id).
```

---

## PROMPTS 61-80: Memory Controller & Integration

### PROMPT 61
```
Create backend/memory/controller.py: MemoryController unifies all memory types. __init__ creates VectorMemory, GraphMemory, EpisodicMemory, WorkingMemory. async store(), async retrieve(), async search() with unified interface.
```

### PROMPT 62
```
Create backend/memory/context_assembler.py: ContextAssembler. async assemble_context(workspace_id, query, max_tokens) gathers from all memory types, ranks by relevance, fits in token budget. Returns formatted context string.
```

### PROMPT 63
```
Create backend/memory/memory_router.py: MemoryRouter determines where to store/retrieve. route_storage(content_type) -> MemoryType. route_retrieval(query_type) -> List[MemoryType]. Rules-based routing.
```

### PROMPT 64
```
Create backend/memory/sync.py: MemorySync keeps memory types consistent. async sync_to_vector(entity) vectorizes graph entities. async sync_to_graph(chunks) extracts graph from vectors. async full_sync(workspace_id).
```

### PROMPT 65
```
Create backend/memory/triggers.py: MemoryTriggers for automatic indexing. on_foundation_update(workspace_id, foundation), on_icp_create(workspace_id, icp), on_move_complete(workspace_id, move_id). Hooks into data changes.
```

### PROMPT 66
```
Create backend/memory/cache.py: MemoryCache using Redis. async get_cached_search(query_hash), async cache_search_result(query_hash, results, ttl=300). Reduces embedding/search calls. LRU eviction.
```

### PROMPT 67
```
Create backend/memory/analytics.py: MemoryAnalytics. async get_memory_usage(workspace_id) -> MemoryUsageReport. async get_retrieval_stats(). async identify_knowledge_gaps(workspace_id).
```

### PROMPT 68
```
Create backend/memory/maintenance.py: MemoryMaintenance scheduled tasks. async daily_cleanup() prunes old data. async weekly_reindex() refreshes embeddings. async monthly_analytics() generates reports.
```

### PROMPT 69
```
Create backend/memory/backup.py: MemoryBackup. async backup_workspace_memory(workspace_id) -> backup_id. async restore_workspace_memory(workspace_id, backup_id). async list_backups(workspace_id).
```

### PROMPT 70
```
Create backend/memory/migration.py: MemoryMigration for schema changes. async migrate_v1_to_v2(). async recompute_embeddings(new_model). async batch_migrate(workspaces).
```

---

## PROMPTS 71-85: Memory Access Patterns

### PROMPT 71
```
Create backend/memory/patterns/__init__.py exporting: OnboardingMemoryPattern, MoveExecutionPattern, ContentGenerationPattern, ResearchPattern.
```

### PROMPT 72
```
Create backend/memory/patterns/onboarding.py: OnboardingMemoryPattern. async store_evidence(workspace_id, evidence). async store_extracted_facts(workspace_id, facts). async build_foundation_graph(workspace_id). Pattern for onboarding flow.
```

### PROMPT 73
```
Create backend/memory/patterns/move_execution.py: MoveExecutionPattern. async get_move_context(workspace_id, move_id) retrieves all relevant memory. async store_move_output(workspace_id, move_id, output). async track_progress(move_id).
```

### PROMPT 74
```
Create backend/memory/patterns/content_generation.py: ContentGenerationPattern. async get_content_context(workspace_id, content_type, icp_id) retrieves brand voice, ICP, examples. async store_generated_content(). async get_similar_content().
```

### PROMPT 75
```
Create backend/memory/patterns/research.py: ResearchPattern. async store_research_findings(workspace_id, findings). async get_past_research(query). async link_research_to_entities(). Deduplication of findings.
```

### PROMPT 76
```
Create backend/memory/query_optimizer.py: QueryOptimizer. optimize_search_query(query) expands with synonyms. select_memory_types(query) auto-selects relevant types. estimate_search_cost(query).
```

### PROMPT 77
```
Create backend/memory/relevance_scorer.py: RelevanceScorer. score_chunk(query, chunk) combines semantic similarity, recency, access count. async rank_results(query, chunks) multi-factor ranking.
```

### PROMPT 78
```
Create backend/memory/context_window_manager.py: ContextWindowManager. async fit_to_window(chunks, max_tokens) selects most relevant subset. async compress_overflow(chunks). Respects model context limits.
```

### PROMPT 79
```
Create backend/memory/memory_aware_prompting.py: MemoryAwarePrompter. async build_prompt_with_memory(base_prompt, workspace_id, query) injects relevant memory context. Automatic context retrieval.
```

### PROMPT 80
```
Create backend/memory/feedback_integration.py: FeedbackIntegration. async incorporate_feedback(workspace_id, output_id, feedback) updates memory weights. async learn_from_corrections(). Improves retrieval over time.
```

---

## PROMPTS 81-100: API & Testing

### PROMPT 81
```
Create backend/api/v1/memory.py: GET /memory/search with query, types[], limit. POST /memory/store with content, type, metadata. GET /memory/stats. DELETE /memory/{id}. All workspace-scoped via auth.
```

### PROMPT 82
```
Create backend/api/v1/graph.py: GET /graph/entities with type filter. GET /graph/entity/{id}. GET /graph/entity/{id}/relationships. GET /graph/subgraph with center_entity, depth. POST /graph/query for pattern matching.
```

### PROMPT 83
```
Create backend/api/v1/sessions.py: GET /sessions lists active. GET /sessions/{id} details. POST /sessions create new. DELETE /sessions/{id} end. GET /sessions/{id}/history.
```

### PROMPT 84
```
Create backend/api/v1/episodes.py: GET /episodes lists for workspace. GET /episodes/{id} with turns. GET /episodes/{id}/summary. POST /episodes/{id}/replay. Pagination support.
```

### PROMPT 85
```
Create tests/memory/__init__.py and tests/memory/conftest.py: Pytest fixtures for memory tests. mock_supabase, mock_redis, test_workspace_id, sample_foundation, sample_icp.
```

### PROMPT 86
```
Create tests/memory/test_vector_store.py: Tests for VectorMemory. test_store_and_retrieve(), test_search_by_type(), test_update_chunk(), test_delete_chunk(), test_workspace_isolation().
```

### PROMPT 87
```
Create tests/memory/test_graph_store.py: Tests for GraphMemory. test_add_entity(), test_add_relationship(), test_find_path(), test_get_subgraph(), test_entity_types().
```

### PROMPT 88
```
Create tests/memory/test_episodic.py: Tests for EpisodicMemory. test_create_episode(), test_add_turns(), test_summarize(), test_search_episodes().
```

### PROMPT 89
```
Create tests/memory/test_working.py: Tests for WorkingMemory. test_session_lifecycle(), test_context_window(), test_scratch_pad(), test_ttl_expiry().
```

### PROMPT 90
```
Create tests/memory/test_controller.py: Tests for MemoryController. test_unified_store(), test_unified_search(), test_context_assembly(), test_cross_type_search().
```

### PROMPT 91
```
Create tests/memory/test_vectorizers.py: Tests for all vectorizers. test_foundation_vectorizer(), test_icp_vectorizer(), test_move_vectorizer(), test_chunking().
```

### PROMPT 92
```
Create tests/memory/test_retriever.py: Tests for WorkspaceRetriever. test_langchain_integration(), test_k_parameter(), test_type_filtering().
```

### PROMPT 93
```
Create tests/memory/test_compression.py: Tests for ContextCompressor. test_compress_to_budget(), test_extract_facts(), test_token_counting().
```

### PROMPT 94
```
Create tests/memory/test_integration.py: Integration tests. test_full_onboarding_memory_flow(), test_move_execution_memory_flow(), test_content_generation_with_memory().
```

### PROMPT 95
```
Create backend/memory/scripts/seed_data.py: Script to seed test memory data. Creates sample foundation, ICPs, vectors, graph entities. For development/testing.
```

### PROMPT 96
```
Create backend/memory/scripts/migrate_embeddings.py: Script to migrate to new embedding model. Reads all chunks, re-embeds, updates. Progress bar. Resume capability.
```

### PROMPT 97
```
Create backend/memory/scripts/cleanup.py: Script for manual cleanup. Remove orphaned chunks, fix broken relationships, recalculate stats. CLI arguments.
```

### PROMPT 98
```
Create backend/memory/scripts/benchmark.py: Benchmark memory performance. Measure search latency, throughput, accuracy. Generate report. Compare configurations.
```

### PROMPT 99
```
Create backend/memory/health.py: MemoryHealthChecker. async check_vector_health() verifies pgvector. async check_graph_health(). async check_redis_health(). Returns detailed report.
```

### PROMPT 100
```
Create backend/memory/README.md: Documentation for memory system. Architecture overview, usage examples, configuration options, performance tips, troubleshooting guide.
```

---

## VERIFICATION

After all prompts completed, verify:
- [ ] pgvector extension enabled in Supabase
- [ ] All migrations run successfully
- [ ] RLS policies active on memory tables
- [ ] Embeddings generate correctly
- [ ] Graph queries return valid results
- [ ] Redis sessions work
- [ ] All tests pass
