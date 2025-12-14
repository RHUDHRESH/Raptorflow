import { Redis } from '@upstash/redis';
import { env } from '../config/env';

// =====================================================
// SOTA CACHING LAYER - REDIS + IN-MEMORY FALLBACK
// =====================================================

export interface CacheEntry {
  data: any;
  timestamp: number;
  ttl: number;
  hits: number;
  metadata?: Record<string, any>;
}

export interface CacheConfig {
  ttl: number; // Time to live in seconds
  maxMemoryEntries?: number; // For in-memory cache
  compression?: boolean;
  namespace?: string; // Cache key prefix
}

export class CacheService {
  private static instance: CacheService;
  private redis: Redis | null = null;
  private memoryCache: Map<string, CacheEntry> = new Map();
  private isRedisAvailable = false;

  private constructor() {
    this.initializeRedis();
  }

  static getInstance(): CacheService {
    if (!CacheService.instance) {
      CacheService.instance = new CacheService();
    }
    return CacheService.instance;
  }

  /**
   * Initialize Redis connection
   */
  private initializeRedis(): void {
    if (env.UPSTASH_REDIS_URL && env.UPSTASH_REDIS_TOKEN) {
      try {
        this.redis = new Redis({
          url: env.UPSTASH_REDIS_URL,
          token: env.UPSTASH_REDIS_TOKEN
        });
        this.isRedisAvailable = true;
        console.log('✅ Redis cache initialized');
      } catch (error) {
        console.warn('⚠️ Redis initialization failed, using memory cache:', error);
        this.isRedisAvailable = false;
      }
    } else {
      console.log('ℹ️ Redis not configured, using memory cache');
    }
  }

  /**
   * Generate namespaced cache key
   */
  private getCacheKey(namespace: string, key: string): string {
    return `${namespace}:${key}`;
  }

  /**
   * Set cache entry
   */
  async set(
    namespace: string,
    key: string,
    data: any,
    config: CacheConfig = { ttl: 3600 }
  ): Promise<void> {
    const cacheKey = this.getCacheKey(namespace, key);
    const entry: CacheEntry = {
      data,
      timestamp: Date.now(),
      ttl: config.ttl,
      hits: 0,
      metadata: {
        compressed: config.compression || false,
        size: JSON.stringify(data).length
      }
    };

    try {
      if (this.isRedisAvailable && this.redis) {
        // Redis cache
        await this.redis.setex(cacheKey, config.ttl, JSON.stringify(entry));
      } else {
        // In-memory cache with LRU eviction
        this.memoryCache.set(cacheKey, entry);

        // Simple LRU eviction (keep last 1000 entries)
        if (this.memoryCache.size > (config.maxMemoryEntries || 1000)) {
          const firstKey = this.memoryCache.keys().next().value;
          this.memoryCache.delete(firstKey);
        }
      }
    } catch (error) {
      console.warn(`Cache set failed for ${cacheKey}:`, error);
      // Fallback to memory cache
      this.memoryCache.set(cacheKey, entry);
    }
  }

  /**
   * Get cache entry
   */
  async get(namespace: string, key: string): Promise<any | null> {
    const cacheKey = this.getCacheKey(namespace, key);

    try {
      let entry: CacheEntry | null = null;

      if (this.isRedisAvailable && this.redis) {
        // Redis cache
        const redisData = await this.redis.get(cacheKey);
        if (redisData) {
          entry = JSON.parse(redisData as string);
        }
      } else {
        // In-memory cache
        entry = this.memoryCache.get(cacheKey) || null;
      }

      if (!entry) return null;

      // Check TTL
      const age = (Date.now() - entry.timestamp) / 1000;
      if (age > entry.ttl) {
        // Expired, remove from cache
        await this.delete(namespace, key);
        return null;
      }

      // Update hit count
      entry.hits += 1;

      // Save updated entry (for hit tracking)
      if (this.isRedisAvailable && this.redis) {
        await this.redis.setex(cacheKey, entry.ttl - Math.floor(age), JSON.stringify(entry));
      } else {
        this.memoryCache.set(cacheKey, entry);
      }

      return entry.data;
    } catch (error) {
      console.warn(`Cache get failed for ${cacheKey}:`, error);
      return null;
    }
  }

  /**
   * Delete cache entry
   */
  async delete(namespace: string, key: string): Promise<void> {
    const cacheKey = this.getCacheKey(namespace, key);

    try {
      if (this.isRedisAvailable && this.redis) {
        await this.redis.del(cacheKey);
      } else {
        this.memoryCache.delete(cacheKey);
      }
    } catch (error) {
      console.warn(`Cache delete failed for ${cacheKey}:`, error);
    }
  }

  /**
   * Clear entire namespace
   */
  async clearNamespace(namespace: string): Promise<void> {
    try {
      if (this.isRedisAvailable && this.redis) {
        // Get all keys in namespace
        const pattern = `${namespace}:*`;
        const keys = await this.redis.keys(pattern);
        if (keys.length > 0) {
          await this.redis.del(...keys);
        }
      } else {
        // Clear memory cache for namespace
        for (const [key] of this.memoryCache) {
          if (key.startsWith(`${namespace}:`)) {
            this.memoryCache.delete(key);
          }
        }
      }
    } catch (error) {
      console.warn(`Cache clear failed for namespace ${namespace}:`, error);
    }
  }

  /**
   * Get cache statistics
   */
  async getStats(): Promise<{
    redis_available: boolean;
    memory_entries: number;
    namespaces: string[];
    hit_rate?: number;
  }> {
    const namespaces = new Set<string>();
    let totalHits = 0;
    let totalEntries = 0;

    // Collect from memory cache
    for (const [key, entry] of this.memoryCache) {
      const namespace = key.split(':')[0];
      namespaces.add(namespace);
      totalHits += entry.hits;
      totalEntries += 1;
    }

    // Try to get Redis stats if available
    if (this.isRedisAvailable && this.redis) {
      try {
        const keys = await this.redis.keys('*');
        for (const key of keys) {
          const namespace = key.split(':')[0];
          namespaces.add(namespace);
        }
        totalEntries += keys.length;
      } catch (error) {
        console.warn('Failed to get Redis stats:', error);
      }
    }

    return {
      redis_available: this.isRedisAvailable,
      memory_entries: this.memoryCache.size,
      namespaces: Array.from(namespaces),
      hit_rate: totalEntries > 0 ? totalHits / totalEntries : 0
    };
  }

  /**
   * Check cache health
   */
  async healthCheck(): Promise<{
    status: 'healthy' | 'degraded' | 'unhealthy';
    redis: boolean;
    memory: boolean;
    latency_ms: number;
  }> {
    const startTime = Date.now();

    try {
      // Test memory cache
      const testKey = 'health_check_test';
      await this.set('health', testKey, { test: true }, { ttl: 10 });
      const retrieved = await this.get('health', testKey);
      const memoryOk = retrieved?.test === true;

      // Test Redis if available
      let redisOk = false;
      if (this.isRedisAvailable && this.redis) {
        try {
          await this.redis.setex('health:redis_test', 10, 'ok');
          const redisResult = await this.redis.get('health:redis_test');
          redisOk = redisResult === 'ok';
        } catch {
          redisOk = false;
        }
      }

      const latency = Date.now() - startTime;

      let status: 'healthy' | 'degraded' | 'unhealthy' = 'healthy';
      if (!memoryOk) status = 'unhealthy';
      else if (!redisOk && this.isRedisAvailable) status = 'degraded';

      return {
        status,
        redis: redisOk,
        memory: memoryOk,
        latency_ms: latency
      };
    } catch (error) {
      return {
        status: 'unhealthy',
        redis: false,
        memory: false,
        latency_ms: Date.now() - startTime
      };
    }
  }
}

// =====================================================
// TOOL-SPECIFIC CACHE UTILITIES
// =====================================================

/**
 * Cache tool execution results (for deterministic tools)
 */
export class ToolCache {
  private cache: CacheService;
  private namespace: string;

  constructor(namespace = 'tools') {
    this.cache = CacheService.getInstance();
    this.namespace = namespace;
  }

  /**
   * Generate deterministic cache key from tool params
   */
  private generateKey(toolName: string, params: any): string {
    // Create deterministic key from sorted params
    const sortedParams = JSON.stringify(params, Object.keys(params).sort());
    return `${toolName}:${Buffer.from(sortedParams).toString('base64').slice(0, 64)}`;
  }

  /**
   * Cache tool result
   */
  async cacheResult(
    toolName: string,
    params: any,
    result: any,
    ttl = 3600
  ): Promise<void> {
    const key = this.generateKey(toolName, params);
    await this.cache.set(this.namespace, key, result, { ttl });
  }

  /**
   * Get cached tool result
   */
  async getCachedResult(toolName: string, params: any): Promise<any | null> {
    const key = this.generateKey(toolName, params);
    return await this.cache.get(this.namespace, key);
  }

  /**
   * Clear tool cache
   */
  async clearToolCache(toolName?: string): Promise<void> {
    if (toolName) {
      // Clear specific tool cache
      const pattern = `${this.namespace}:${toolName}:*`;
      // Note: This is a simplified implementation
      // In production, you'd want to use Redis SCAN or similar
      console.log(`Clearing cache for tool: ${toolName}`);
    } else {
      // Clear all tool cache
      await this.cache.clearNamespace(this.namespace);
    }
  }
}

/**
 * Cache LLM prompts and responses
 */
export class PromptCache {
  private cache: CacheService;
  private toolCache: ToolCache;

  constructor() {
    this.cache = CacheService.getInstance();
    this.toolCache = new ToolCache('prompts');
  }

  /**
   * Cache prompt-response pair
   */
  async cachePromptResponse(
    promptHash: string,
    response: any,
    metadata: {
      model: string;
      tokens_used: number;
      temperature: number;
    },
    ttl = 7200 // 2 hours
  ): Promise<void> {
    const cacheData = {
      response,
      metadata,
      cached_at: new Date().toISOString()
    };

    await this.cache.set('prompts', promptHash, cacheData, { ttl });
  }

  /**
   * Get cached prompt response
   */
  async getCachedPrompt(promptHash: string): Promise<any | null> {
    return await this.cache.get('prompts', promptHash);
  }

  /**
   * Generate prompt hash for caching
   */
  generatePromptHash(prompt: string, model: string, temperature: number): string {
    const content = `${prompt}|${model}|${temperature}`;
    // Simple hash function (in production, use crypto.createHash)
    let hash = 0;
    for (let i = 0; i < content.length; i++) {
      const char = content.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return Math.abs(hash).toString(36);
  }

  /**
   * Cache tool-specific results
   */
  getToolCache(): ToolCache {
    return this.toolCache;
  }
}

// =====================================================
// GLOBAL CACHE INSTANCES
// =====================================================

export const cacheService = CacheService.getInstance();
export const toolCache = new ToolCache();
export const promptCache = new PromptCache();


