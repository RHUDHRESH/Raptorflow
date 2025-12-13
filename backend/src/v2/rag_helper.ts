import { supabase } from '../lib/supabase';
import { modelRouter } from './router';
import { trace, Span, SpanStatusCode } from '@opentelemetry/api';

// =====================================================
// CACHING LAYER FOR PERFORMANCE
// =====================================================

interface CacheEntry<T> {
  data: T;
  timestamp: number;
  ttl: number;
}

class MemoryCache<T> {
  private cache = new Map<string, CacheEntry<T>>();
  private maxSize: number;
  private defaultTTL: number;

  constructor(maxSize = 1000, defaultTTL = 5 * 60 * 1000) { // 5 minutes default
    this.maxSize = maxSize;
    this.defaultTTL = defaultTTL;
  }

  get(key: string): T | null {
    const entry = this.cache.get(key);
    if (!entry) return null;

    if (Date.now() - entry.timestamp > entry.ttl) {
      this.cache.delete(key);
      return null;
    }

    return entry.data;
  }

  set(key: string, value: T, ttl?: number): void {
    // Evict oldest entries if at capacity
    if (this.cache.size >= this.maxSize) {
      const oldestKey = this.cache.keys().next().value;
      if (oldestKey) {
        this.cache.delete(oldestKey);
      }
    }

    this.cache.set(key, {
      data: value,
      timestamp: Date.now(),
      ttl: ttl || this.defaultTTL
    });
  }

  clear(): void {
    this.cache.clear();
  }

  size(): number {
    return this.cache.size;
  }
}

// Global caches for RAG operations
const embeddingCache = new MemoryCache<number[]>(1000, 10 * 60 * 1000); // 10 min TTL
const queryCache = new MemoryCache<RAGContext>(500, 2 * 60 * 1000); // 2 min TTL

// =====================================================
// RAG HELPER UTILITIES
// =====================================================

export interface RAGQuery {
  query: string;
  user_id: string;
  content_types?: string[];
  limit?: number;
  threshold?: number;
  include_metadata?: boolean;
}

export interface RAGChunk {
  id: string;
  content: string;
  content_type: string;
  content_id?: string;
  metadata?: any;
  similarity: number;
  source?: string;
}

export interface RAGContext {
  chunks: RAGChunk[];
  total_found: number;
  query: string;
  processing_time: number;
}

/**
 * Generate embedding for text using Vertex AI with caching
 */
async function generateEmbedding(text: string): Promise<number[]> {
  const tracer = trace.getTracer('raptorflow-rag');
  return tracer.startActiveSpan('generate_embedding', async (span: Span) => {
    span.setAttributes({
      'text.length': text.length,
      'cache.enabled': true
    });

    try {
      // Check cache first
      const cacheKey = `emb:${text.length}:${text.slice(0, 100)}`;
      const cached = embeddingCache.get(cacheKey);
      if (cached) {
        span.setAttribute('cache.hit', true);
        console.log(`✅ Cache hit for embedding (${text.length} chars)`);
        span.end();
        return cached;
      }

      span.setAttribute('cache.hit', false);
      const startTime = Date.now();
      console.log(`🔄 Generating embedding for text (${text.length} chars)`);

      const model = modelRouter.getModelForTask('simple');

      // TODO: Replace with actual Vertex AI embedding call
      // const result = await model.embeddings.create({
      //   input: text,
      //   model: 'text-embedding-ada-002'
      // });
      // return result.data[0].embedding;

      // Mock implementation - replace with real embedding
      const embedding = new Array(768).fill(0).map(() => Math.random());

      const duration = Date.now() - startTime;
      span.setAttribute('embedding.duration_ms', duration);
      console.log(`✅ Embedding generated in ${duration}ms`);

      // Cache the result
      embeddingCache.set(cacheKey, embedding);

      span.setStatus({ code: SpanStatusCode.OK });
      span.end();
      return embedding;
    } catch (error) {
      span.recordException(error as Error);
      span.setStatus({ code: SpanStatusCode.ERROR, message: (error as Error).message });
      span.end();
      console.error('❌ Embedding generation failed:', error);
      throw error;
    }
  });
}

/**
 * Batch generate embeddings for multiple texts
 */
export async function batchGenerateEmbeddings(texts: string[]): Promise<number[][]> {
  const startTime = Date.now();
  console.log(`🔄 Batch generating ${texts.length} embeddings`);

  const promises = texts.map(text => generateEmbedding(text));
  const results = await Promise.allSettled(promises);

  const embeddings: number[][] = [];
  let successCount = 0;

  results.forEach((result, index) => {
    if (result.status === 'fulfilled') {
      embeddings.push(result.value);
      successCount++;
    } else {
      console.error(`❌ Embedding ${index} failed:`, result.reason);
      // Return zero vector as fallback
      embeddings.push(new Array(768).fill(0));
    }
  });

  const duration = Date.now() - startTime;
  console.log(`✅ Batch embeddings completed: ${successCount}/${texts.length} successful in ${duration}ms`);

  return embeddings;
}

/**
 * Perform semantic search using vector similarity with caching
 */
export async function ragQuery(params: RAGQuery): Promise<RAGContext> {
  const tracer = trace.getTracer('raptorflow-rag');

  return tracer.startActiveSpan('rag_query', async (span: Span) => {
    const startTime = Date.now();

    span.setAttributes({
      'query.length': params.query.length,
      'user.id': params.user_id,
      'content_types.count': params.content_types?.length || 0,
      'limit': params.limit || 10,
      'threshold': params.threshold || 0.7
    });

    try {
      const {
        query,
        user_id,
        content_types = [],
        limit = 10,
        threshold = 0.7,
        include_metadata = true
      } = params;

      // Create cache key
      const cacheKey = `rag:${user_id}:${query.slice(0, 50)}:${content_types.join(',')}:${limit}:${threshold}`;
      const cached = queryCache.get(cacheKey);
      if (cached) {
        span.setAttribute('cache.hit', true);
        console.log(`✅ RAG cache hit for query: "${query.slice(0, 30)}..."`);
        span.end();
        return cached;
      }

      span.setAttribute('cache.hit', false);
      console.log(`🔍 RAG search: "${query.slice(0, 50)}..." (user: ${user_id})`);

      // Generate embedding for the query
      const embeddingStart = Date.now();
      const queryEmbedding = await generateEmbedding(query);
      const embeddingTime = Date.now() - embeddingStart;
      span.setAttribute('embedding.duration_ms', embeddingTime);

      // Build the similarity search query with proper content type filtering
      const dbStart = Date.now();
      let queryBuilder = supabase.rpc('match_embeddings', {
        query_embedding: `[${queryEmbedding.join(',')}]`,
        match_threshold: threshold,
        match_count: Math.max(limit * 2, 20), // Get more results for client-side filtering
        user_filter: user_id
      });

      const { data: results, error } = await queryBuilder;
      const dbTime = Date.now() - dbStart;
      span.setAttribute('database.duration_ms', dbTime);

      if (error) {
        span.recordException(new Error(`Vector search failed: ${error.message}`));
        span.setStatus({ code: SpanStatusCode.ERROR, message: error.message });
        throw new Error(`Vector search failed: ${error.message}`);
      }

      // Transform results to RAG chunks
      const allChunks: RAGChunk[] = (results || []).map((result: any) => ({
        id: result.id,
        content: result.content,
        content_type: result.content_type,
        content_id: result.content_id,
        metadata: include_metadata ? result.metadata : undefined,
        similarity: result.similarity,
        source: result.content_type
      }));

      // Filter by content types if specified (client-side for now)
      const filteredChunks = content_types.length > 0
        ? allChunks.filter(chunk => content_types.includes(chunk.content_type))
        : allChunks;

      // Sort by similarity and limit
      const sortedChunks = filteredChunks
        .sort((a, b) => b.similarity - a.similarity)
        .slice(0, limit);

      const processingTime = Date.now() - startTime;
      span.setAttributes({
        'results.count': sortedChunks.length,
        'results.total_found': filteredChunks.length,
        'processing.duration_ms': processingTime
      });

      console.log(`✅ RAG search completed: ${sortedChunks.length} results in ${processingTime}ms (emb: ${embeddingTime}ms, db: ${dbTime}ms)`);

      const result: RAGContext = {
        chunks: sortedChunks,
        total_found: filteredChunks.length,
        query,
        processing_time: processingTime
      };

      // Cache the result (shorter TTL for dynamic queries)
      queryCache.set(cacheKey, result, 60 * 1000); // 1 minute TTL

      span.setStatus({ code: SpanStatusCode.OK });
      span.end();
      return result;

    } catch (error) {
      span.recordException(error as Error);
      span.setStatus({ code: SpanStatusCode.ERROR, message: (error as Error).message });
      span.end();

      console.error('❌ RAG query failed:', error);
      const processingTime = Date.now() - startTime;

      return {
        chunks: [],
        total_found: 0,
        query: params.query,
        processing_time: processingTime
      };
    }
  });
}

/**
 * Store content with embedding for future retrieval
 */
export async function storeEmbedding(
  userId: string,
  contentType: string,
  content: string,
  metadata: any = {},
  contentId?: string
): Promise<string> {
  try {
    // Generate embedding
    const embedding = await generateEmbedding(content);

    // Store in database
    const { data, error } = await supabase
      .from('memory_embeddings')
      .insert({
        user_id: userId,
        content_type: contentType,
        content_id: contentId,
        content: content,
        embedding: `[${embedding.join(',')}]`,
        metadata: metadata
      })
      .select('id')
      .single();

    if (error) {
      throw new Error(`Failed to store embedding: ${error.message}`);
    }

    console.log(`✅ Stored embedding for ${contentType}: ${data.id}`);
    return data.id;

  } catch (error) {
    console.error('Failed to store embedding:', error);
    throw error;
  }
}

/**
 * Batch store multiple embeddings
 */
export async function batchStoreEmbeddings(
  embeddings: Array<{
    userId: string;
    contentType: string;
    content: string;
    metadata?: any;
    contentId?: string;
  }>
): Promise<string[]> {
  const results: string[] = [];

  // Process in batches to avoid rate limits
  const batchSize = 10;
  for (let i = 0; i < embeddings.length; i += batchSize) {
    const batch = embeddings.slice(i, i + batchSize);

    const batchPromises = batch.map(emb =>
      storeEmbedding(emb.userId, emb.contentType, emb.content, emb.metadata, emb.contentId)
    );

    try {
      const batchResults = await Promise.all(batchPromises);
      results.push(...batchResults);
    } catch (error) {
      console.error(`Batch ${Math.floor(i / batchSize) + 1} failed:`, error);
      // Continue with other batches
    }
  }

  return results;
}

/**
 * Get contextual information for agent execution
 */
export async function getAgentContext(
  userId: string,
  agentName: string,
  contextType: string,
  limit = 5
): Promise<RAGContext> {
  // Map agent to relevant content types
  const contentTypeMap: Record<string, string[]> = {
    market_intel_agent: ['market_research', 'competitor_analysis', 'trend_data'],
    positioning_architect_agent: ['brand_memory', 'positioning_research'],
    copywriter_agent: ['brand_memory', 'successful_copy', 'user_preferences'],
    creative_director_agent: ['brand_memory', 'design_guidelines', 'user_preferences'],
    move_designer_agent: ['campaign_history', 'move_templates', 'success_metrics']
  };

  const contentTypes = contentTypeMap[agentName] || ['general'];

  return ragQuery({
    query: `Context for ${agentName} working on ${contextType}`,
    user_id: userId,
    content_types: contentTypes,
    limit,
    threshold: 0.6
  });
}

/**
 * Learn from user feedback to improve future responses
 */
export async function learnFromFeedback(
  userId: string,
  agentName: string,
  originalOutput: string,
  feedback: 'positive' | 'negative' | 'edit',
  editedOutput?: string,
  feedbackText?: string
): Promise<void> {
  try {
    // Store the feedback event
    await supabase
      .from('preference_events')
      .insert({
        user_id: userId,
        agent_name: agentName,
        action_type: feedback === 'positive' ? 'thumbs_up' :
                    feedback === 'negative' ? 'thumbs_down' : 'edit',
        original_output: originalOutput,
        modified_output: editedOutput,
        feedback_text: feedbackText,
        metadata: {
          agent_name: agentName,
          feedback_type: feedback,
          timestamp: new Date().toISOString()
        }
      });

    // If edited, store the improvement as a learning example
    if (feedback === 'edit' && editedOutput) {
      await storeEmbedding(
        userId,
        'feedback_learning',
        `Original: ${originalOutput}\nImproved: ${editedOutput}`,
        {
          agent_name: agentName,
          feedback_text: feedbackText,
          improvement_type: 'user_edit'
        }
      );
    }

    // Update user preferences based on patterns
    await updateUserPreferencesFromFeedback(userId, agentName, feedback);

    console.log(`✅ Learned from ${feedback} feedback for ${agentName}`);

  } catch (error) {
    console.error('Failed to learn from feedback:', error);
  }
}

/**
 * Update user preferences based on feedback patterns
 */
async function updateUserPreferencesFromFeedback(
  userId: string,
  agentName: string,
  feedback: 'positive' | 'negative' | 'edit'
): Promise<void> {
  try {
    // Get recent feedback for this agent
    const { data: recentFeedback } = await supabase
      .from('preference_events')
      .select('action_type, metadata')
      .eq('user_id', userId)
      .eq('agent_name', agentName)
      .gte('created_at', new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString()) // Last 30 days
      .limit(50);

    if (!recentFeedback || recentFeedback.length < 5) {
      return; // Not enough data
    }

    // Analyze patterns
    const positiveCount = recentFeedback.filter(f => f.action_type === 'thumbs_up').length;
    const editCount = recentFeedback.filter(f => f.action_type === 'edit').length;
    const totalCount = recentFeedback.length;

    const positiveRate = positiveCount / totalCount;
    const editRate = editCount / totalCount;

    // Update preferences based on patterns
    if (positiveRate > 0.7) {
      // High positive feedback - reinforce current style
      await updatePreferenceConfidence(userId, 'tone', 0.1);
    } else if (editRate > 0.5) {
      // High edit rate - may need preference adjustment
      console.log(`High edit rate for ${agentName} - consider preference tuning`);
    }

  } catch (error) {
    console.error('Failed to update preferences from feedback:', error);
  }
}

/**
 * Update preference confidence score
 */
async function updatePreferenceConfidence(
  userId: string,
  preferenceType: string,
  confidenceChange: number
): Promise<void> {
  try {
    const { data: existing } = await supabase
      .from('user_preferences')
      .select('confidence_score, sample_size')
      .eq('user_id', userId)
      .eq('preference_type', preferenceType)
      .single();

    if (existing) {
      const newConfidence = Math.max(0, Math.min(1,
        (existing.confidence_score * existing.sample_size + confidenceChange) /
        (existing.sample_size + 1)
      ));

      await supabase
        .from('user_preferences')
        .update({
          confidence_score: newConfidence,
          sample_size: existing.sample_size + 1,
          last_updated: new Date().toISOString()
        })
        .eq('user_id', userId)
        .eq('preference_type', preferenceType);
    }
  } catch (error) {
    console.error('Failed to update preference confidence:', error);
  }
}

/**
 * Get user preferences for agent personalization
 */
export async function getUserPreferences(
  userId: string,
  agentName?: string
): Promise<Record<string, any>> {
  try {
    let query = supabase
      .from('user_preferences')
      .select('preference_type, preference_value, confidence_score')
      .eq('user_id', userId);

    if (agentName) {
      // Could filter by agent-specific preferences
      query = query.like('preference_type', `${agentName.split('_')[0]}%`);
    }

    const { data: preferences } = await query;

    if (!preferences) return {};

    // Convert to key-value object
    return preferences.reduce((acc, pref) => {
      acc[pref.preference_type] = {
        value: pref.preference_value,
        confidence: pref.confidence_score
      };
      return acc;
    }, {} as Record<string, any>);

  } catch (error) {
    console.error('Failed to get user preferences:', error);
    return {};
  }
}

/**
 * Periodic internet learning - scrape and store market data
 */
export async function periodicInternetLearning(): Promise<void> {
  try {
    console.log('🌐 Starting periodic internet learning...');

    // This would integrate with scraping tools
    // For now, just log the intent
    console.log('✅ Periodic learning completed (placeholder)');

    // In real implementation:
    // 1. Scrape RSS feeds, Twitter, Reddit
    // 2. Extract relevant market/trend data
    // 3. Store in raw_sources table
    // 4. Generate embeddings
    // 5. Update memory_embeddings

  } catch (error) {
    console.error('Periodic internet learning failed:', error);
  }
}

// =====================================================
// UTILITY FUNCTIONS
// =====================================================

/**
 * Format RAG context for prompt injection
 */
export function formatRAGContext(context: RAGContext): string {
  if (context.chunks.length === 0) {
    return "No relevant context found.";
  }

  const formatted = context.chunks
    .map((chunk, i) => `[${i + 1}] ${chunk.content}`)
    .join('\n\n');

  return `Relevant context:\n${formatted}`;
}

/**
 * Chunk text for embedding (basic implementation)
 */
export function chunkText(text: string, chunkSize = 1000, overlap = 200): string[] {
  const chunks: string[] = [];
  let start = 0;

  while (start < text.length) {
    let end = start + chunkSize;

    // Try to break at sentence boundary
    if (end < text.length) {
      const lastPeriod = text.lastIndexOf('.', end);
      const lastNewline = text.lastIndexOf('\n', end);

      if (lastPeriod > start && lastPeriod > lastNewline) {
        end = lastPeriod + 1;
      } else if (lastNewline > start) {
        end = lastNewline + 1;
      }
    }

    chunks.push(text.slice(start, end).trim());
    start = Math.max(start + 1, end - overlap);
  }

  return chunks;
}
