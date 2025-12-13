import { supabase } from '../lib/supabase';
import { storeEmbedding, ragQuery, getUserPreferences } from './rag_helper';
import { trace, Span, SpanStatusCode } from '@opentelemetry/api';

// =====================================================
// BRAND MEMORY CACHING LAYER
// =====================================================

interface BrandMemoryCacheEntry {
  data: BrandMemory;
  timestamp: number;
  ttl: number;
}

class BrandMemoryCache {
  private cache = new Map<string, BrandMemoryCacheEntry>();
  private maxSize = 500; // Cache up to 500 brand memories
  private defaultTTL = 10 * 60 * 1000; // 10 minutes

  get(userId: string): BrandMemory | null {
    const entry = this.cache.get(userId);
    if (!entry) return null;

    if (Date.now() - entry.timestamp > entry.ttl) {
      this.cache.delete(userId);
      return null;
    }

    return entry.data;
  }

  set(userId: string, data: BrandMemory, ttl?: number): void {
    // Evict oldest entries if at capacity
    if (this.cache.size >= this.maxSize) {
      const oldestKey = Array.from(this.cache.entries())
        .sort(([,a], [,b]) => a.timestamp - b.timestamp)[0][0];
      this.cache.delete(oldestKey);
    }

    this.cache.set(userId, {
      data,
      timestamp: Date.now(),
      ttl: ttl || this.defaultTTL
    });
  }

  invalidate(userId: string): void {
    this.cache.delete(userId);
  }

  clear(): void {
    this.cache.clear();
  }
}

const brandMemoryCache = new BrandMemoryCache();

// =====================================================
// BRAND MEMORY SERVICE
// =====================================================

export interface BrandMemory {
  id: string;
  user_id: string;
  brand_name?: string;
  voice_tone: Record<string, number>; // e.g., { 'professional': 0.8, 'conversational': 0.6 }
  style_guidelines: Record<string, any>;
  brand_colors: string[];
  brand_values: string[];
  competitor_mentions: any[];
  taboo_topics: string[];
  created_at: string;
  updated_at: string;
}

export interface CreateBrandMemoryInput {
  brand_name?: string;
  voice_tone?: Record<string, number>;
  style_guidelines?: Record<string, any>;
  brand_colors?: string[];
  brand_values?: string[];
  competitor_mentions?: any[];
  taboo_topics?: string[];
}

export class BrandMemoryService {
  /**
   * Get brand memory for a user with caching
   */
  async getBrandMemory(userId: string): Promise<BrandMemory | null> {
    const tracer = trace.getTracer('raptorflow-brand-memory');

    return tracer.startActiveSpan('get_brand_memory', async (span: Span) => {
      span.setAttribute('user.id', userId);

      try {
        // Check cache first
        const cached = brandMemoryCache.get(userId);
        if (cached) {
          span.setAttribute('cache.hit', true);
          console.log(`✅ Brand memory cache hit for user ${userId}`);
          span.end();
          return cached;
        }

        span.setAttribute('cache.hit', false);
        console.log(`🔍 Fetching brand memory for user ${userId}`);

        const startTime = Date.now();
        const { data, error } = await supabase
          .from('brand_memory')
          .select('*')
          .eq('user_id', userId)
          .single();

        const dbTime = Date.now() - startTime;
        span.setAttribute('database.duration_ms', dbTime);

        if (error && error.code !== 'PGRST116') { // Not found error
          span.recordException(error);
          span.setStatus({ code: SpanStatusCode.ERROR, message: error.message });
          span.end();
          throw error;
        }

        // Cache the result if found
        if (data) {
          brandMemoryCache.set(userId, data);
          span.setAttribute('cache.stored', true);
        }

        span.setStatus({ code: SpanStatusCode.OK });
        span.end();
        return data;
      } catch (error) {
        span.recordException(error as Error);
        span.setStatus({ code: SpanStatusCode.ERROR, message: (error as Error).message });
        span.end();
        console.error('Failed to get brand memory:', error);
        return null;
      }
    });
  }

  /**
   * Create or update brand memory with caching
   */
  async upsertBrandMemory(
    userId: string,
    input: CreateBrandMemoryInput
  ): Promise<BrandMemory> {
    const tracer = trace.getTracer('raptorflow-brand-memory');

    return tracer.startActiveSpan('upsert_brand_memory', async (span: Span) => {
      span.setAttributes({
        'user.id': userId,
        'operation': 'upsert'
      });

      try {
        const memoryData = {
          user_id: userId,
          ...input,
          updated_at: new Date().toISOString()
        };

        const dbStart = Date.now();
        const { data, error } = await supabase
          .from('brand_memory')
          .upsert(memoryData, {
            onConflict: 'user_id',
            returning: 'representation'
          })
          .select()
          .single();

        const dbTime = Date.now() - dbStart;
        span.setAttribute('database.duration_ms', dbTime);

        if (error) {
          span.recordException(error);
          span.setStatus({ code: SpanStatusCode.ERROR, message: error.message });
          span.end();
          throw error;
        }

        // Invalidate cache for this user
        brandMemoryCache.invalidate(userId);
        span.setAttribute('cache.invalidated', true);

        // Store embedding for semantic search (async to not block response)
        const memoryText = this.formatMemoryForEmbedding(data);
        storeEmbedding(
          userId,
          'brand_memory',
          memoryText,
          {
            brand_name: data.brand_name,
            type: 'brand_guidelines'
          },
          data.id
        ).catch(embeddingError => {
          console.error('Failed to store brand memory embedding:', embeddingError);
          // Don't fail the whole operation for embedding issues
        });

        console.log(`✅ Brand memory updated for user ${userId}`);
        span.setStatus({ code: SpanStatusCode.OK });
        span.end();
        return data;
      } catch (error) {
        span.recordException(error as Error);
        span.setStatus({ code: SpanStatusCode.ERROR, message: (error as Error).message });
        span.end();
        console.error('Failed to upsert brand memory:', error);
        throw error;
      }
    });
  }

  /**
   * Update specific aspects of brand memory
   */
  async updateBrandMemory(
    userId: string,
    updates: Partial<CreateBrandMemoryInput>
  ): Promise<BrandMemory | null> {
    try {
      const { data, error } = await supabase
        .from('brand_memory')
        .update({
          ...updates,
          updated_at: new Date().toISOString()
        })
        .eq('user_id', userId)
        .select()
        .single();

      if (error) {
        throw error;
      }

      // Update embedding
      const memoryText = this.formatMemoryForEmbedding(data);
      await storeEmbedding(
        userId,
        'brand_memory',
        memoryText,
        {
          brand_name: data.brand_name,
          type: 'brand_guidelines',
          updated_fields: Object.keys(updates)
        },
        data.id
      );

      return data;
    } catch (error) {
      console.error('Failed to update brand memory:', error);
      throw error;
    }
  }

  /**
   * Learn from successful copy and update brand voice
   */
  async learnFromSuccessfulCopy(
    userId: string,
    copyText: string,
    performance: 'high' | 'medium' | 'low' = 'medium'
  ): Promise<void> {
    try {
      // Analyze the copy for style patterns
      const styleAnalysis = await this.analyzeCopyStyle(copyText);

      // Get current brand memory
      const currentMemory = await this.getBrandMemory(userId);
      if (!currentMemory) return;

      // Update voice tone based on successful patterns
      const updatedVoiceTone = this.updateVoiceToneFromAnalysis(
        currentMemory.voice_tone,
        styleAnalysis,
        performance
      );

      // Update style guidelines
      const updatedGuidelines = this.updateStyleGuidelinesFromAnalysis(
        currentMemory.style_guidelines,
        styleAnalysis,
        performance
      );

      // Save updates
      await this.updateBrandMemory(userId, {
        voice_tone: updatedVoiceTone,
        style_guidelines: updatedGuidelines
      });

      console.log(`✅ Learned from successful copy for user ${userId}`);

    } catch (error) {
      console.error('Failed to learn from successful copy:', error);
    }
  }

  /**
   * Get brand voice context for content generation
   */
  async getBrandVoiceContext(userId: string): Promise<string> {
    try {
      const memory = await this.getBrandMemory(userId);
      if (!memory) {
        return "No brand memory available. Use professional, helpful tone.";
      }

      // Get relevant context from embeddings
      const contextResult = await ragQuery({
        query: "brand voice and style guidelines",
        user_id: userId,
        content_types: ['brand_memory'],
        limit: 3,
        threshold: 0.7
      });

      const voiceDescription = this.formatVoiceTone(memory.voice_tone);
      const styleDescription = this.formatStyleGuidelines(memory.style_guidelines);
      const ragContext = contextResult.chunks.length > 0
        ? `\n\nRelevant examples:\n${contextResult.chunks.map(c => `- ${c.content}`).join('\n')}`
        : '';

      return `Brand Voice Guidelines:
${voiceDescription}

Style Preferences:
${styleDescription}

Brand Values: ${memory.brand_values.join(', ') || 'Not specified'}
Taboo Topics: ${memory.taboo_topics.join(', ') || 'None specified'}
${ragContext}`;

    } catch (error) {
      console.error('Failed to get brand voice context:', error);
      return "Use professional, engaging tone appropriate for the brand.";
    }
  }

  /**
   * Analyze copy style patterns
   */
  private async analyzeCopyStyle(copyText: string): Promise<Record<string, number>> {
    // Simple heuristic analysis - in production, use NLP models
    const analysis: Record<string, number> = {
      formal: 0,
      conversational: 0,
      urgent: 0,
      benefit_focused: 0,
      feature_focused: 0,
      emotional: 0,
      logical: 0
    };

    const lowerText = copyText.toLowerCase();

    // Formal indicators
    if (/\b(therefore|thus|consequently|accordingly)\b/.test(lowerText)) {
      analysis.formal += 0.8;
    }
    if (lowerText.includes('we are pleased to') || lowerText.includes('we would like to')) {
      analysis.formal += 0.6;
    }

    // Conversational indicators
    if (lowerText.includes('you know') || lowerText.includes('let me tell you') || lowerText.includes('here\'s the thing')) {
      analysis.conversational += 0.8;
    }
    if (/\b(hey|hi|you)\b/.test(lowerText) && lowerText.includes('?')) {
      analysis.conversational += 0.5;
    }

    // Urgent indicators
    if (/\b(now|today|immediately|urgent|don\'t wait|limited time)\b/.test(lowerText)) {
      analysis.urgent += 0.7;
    }

    // Benefit vs feature focus
    const benefitWords = /\b(save time|make money|feel confident|get results|be successful)\b/;
    const featureWords = /\b(includes|features|has|comes with|provides)\b/;

    if (benefitWords.test(lowerText)) {
      analysis.benefit_focused += 0.6;
    }
    if (featureWords.test(lowerText)) {
      analysis.feature_focused += 0.6;
    }

    // Emotional vs logical
    const emotionalWords = /\b(love|hate|excited|worried|proud|happy|sad)\b/;
    const logicalWords = /\b(because|therefore|data|research|proven|statistics)\b/;

    if (emotionalWords.test(lowerText)) {
      analysis.emotional += 0.5;
    }
    if (logicalWords.test(lowerText)) {
      analysis.logical += 0.5;
    }

    return analysis;
  }

  /**
   * Update voice tone based on analysis
   */
  private updateVoiceToneFromAnalysis(
    currentTone: Record<string, number>,
    analysis: Record<string, number>,
    performance: 'high' | 'medium' | 'low'
  ): Record<string, number> {
    const learningRate = performance === 'high' ? 0.3 : performance === 'medium' ? 0.2 : 0.1;
    const updatedTone = { ...currentTone };

    // Map analysis to voice dimensions
    const mappings = {
      formal: ['professional', 'authoritative'],
      conversational: ['friendly', 'approachable'],
      urgent: ['direct', 'action-oriented'],
      emotional: ['passionate', 'engaging'],
      logical: ['analytical', 'credible']
    };

    Object.entries(analysis).forEach(([analysisKey, strength]) => {
      const voiceDimensions = mappings[analysisKey as keyof typeof mappings];
      if (voiceDimensions && strength > 0.3) {
        voiceDimensions.forEach(dimension => {
          updatedTone[dimension] = (updatedTone[dimension] || 0.5) + (strength * learningRate);
          updatedTone[dimension] = Math.max(0, Math.min(1, updatedTone[dimension]));
        });
      }
    });

    return updatedTone;
  }

  /**
   * Update style guidelines based on analysis
   */
  private updateStyleGuidelinesFromAnalysis(
    currentGuidelines: Record<string, any>,
    analysis: Record<string, number>,
    performance: 'high' | 'medium' | 'low'
  ): Record<string, any> {
    const updated = { ...currentGuidelines };

    // Update based on patterns found
    if (analysis.benefit_focused > analysis.feature_focused) {
      updated.focus_preference = 'benefits_over_features';
    } else if (analysis.feature_focused > 0.5) {
      updated.focus_preference = 'feature_comparison';
    }

    if (analysis.urgent > 0.5) {
      updated.call_to_action = 'urgent';
    }

    if (analysis.emotional > analysis.logical) {
      updated.approach = 'emotional_connection';
    } else if (analysis.logical > 0.5) {
      updated.approach = 'logical_proof';
    }

    return updated;
  }

  /**
   * Format memory for embedding
   */
  private formatMemoryForEmbedding(memory: BrandMemory): string {
    return `
Brand: ${memory.brand_name || 'Unnamed Brand'}

Voice Tone: ${this.formatVoiceTone(memory.voice_tone)}

Style Guidelines: ${JSON.stringify(memory.style_guidelines, null, 2)}

Brand Values: ${memory.brand_values.join(', ')}

Competitor Strategy: ${JSON.stringify(memory.competitor_mentions, null, 2)}

Restricted Topics: ${memory.taboo_topics.join(', ')}
    `.trim();
  }

  /**
   * Format voice tone for display
   */
  private formatVoiceTone(voiceTone: Record<string, number>): string {
    if (!voiceTone || Object.keys(voiceTone).length === 0) {
      return "Not specified - use professional tone";
    }

    const sorted = Object.entries(voiceTone)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 3); // Top 3

    return sorted.map(([tone, score]) =>
      `${tone} (${Math.round(score * 100)}%)`
    ).join(', ');
  }

  /**
   * Format style guidelines for display
   */
  private formatStyleGuidelines(guidelines: Record<string, any>): string {
    if (!guidelines || Object.keys(guidelines).length === 0) {
      return "No specific style guidelines";
    }

    return Object.entries(guidelines)
      .map(([key, value]) => `${key}: ${value}`)
      .join('; ');
  }
}

// =====================================================
// GLOBAL BRAND MEMORY SERVICE INSTANCE
// =====================================================

export const brandMemoryService = new BrandMemoryService();
