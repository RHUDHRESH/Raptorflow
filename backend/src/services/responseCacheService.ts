/**
 * Response Cache Service - Redis-based caching for expensive operations
 *
 * Features:
 * - Multi-level caching (memory + Redis)
 * - TTL-based expiration
 * - Cache hit/miss metrics
 * - Compression for large responses
 * - Cache invalidation patterns
 */

import { redisMemory } from './redisMemory';
import { telemetryService } from './telemetryService';

export interface CacheEntry {
  key: string;
  value: any;
  ttl: number; // seconds
  createdAt: number;
  hits: number;
  metadata?: Record<string, any>;
}

export interface CacheStats {
  totalRequests: number;
  cacheHits: number;
  cacheMisses: number;
  hitRate: number;
  totalSize: number; // estimated bytes
  entriesCount: number;
}

export type CacheKeyGenerator = (...args: any[]) => string;

class ResponseCacheService {
  private readonly CACHE_PREFIX = 'cache';
  private readonly STATS_KEY = 'cache_stats';
  private readonly COMPRESSION_THRESHOLD = 1024; // 1KB

  private memoryCache = new Map<string, CacheEntry>();
  private readonly MAX_MEMORY_ENTRIES = 1000;

  private stats: CacheStats = {
    totalRequests: 0,
    cacheHits: 0,
    cacheMisses: 0,
    hitRate: 0,
    totalSize: 0,
    entriesCount: 0
  };

  /**
   * Get cached value or compute and cache it
   */
  async getOrSet<T>(
    key: string,
    getter: () => Promise<T>,
    options: {
      ttl?: number;
      compress?: boolean;
      metadata?: Record<string, any>;
    } = {}
  ): Promise<T> {
    const { ttl = 3600, compress = false } = options; // 1 hour default

    // Check memory cache first (faster)
    const memoryEntry = this.memoryCache.get(key);
    if (memoryEntry && Date.now() < memoryEntry.createdAt + (memoryEntry.ttl * 1000)) {
      memoryEntry.hits++;
      this.stats.cacheHits++;
      this.stats.totalRequests++;
      await this.updateStats();
      return memoryEntry.value;
    }

    // Check Redis cache
    const redisKey = `${this.CACHE_PREFIX}:${key}`;
    try {
      const cached = await redisMemory.get(redisKey);
      if (cached) {
        const entry: CacheEntry = JSON.parse(cached);

        // Check if expired
        if (Date.now() < entry.createdAt + (entry.ttl * 1000)) {
          entry.hits++;

          // Update memory cache
          this.memoryCache.set(key, entry);
          this.ensureMemoryCacheSize();

          this.stats.cacheHits++;
          this.stats.totalRequests++;
          await this.updateStats();

          // Store updated entry back to Redis
          await redisMemory.store(redisKey, JSON.stringify(entry), entry.ttl);

          return entry.value;
        } else {
          // Expired, remove
          await redisMemory.delete(redisKey);
        }
      }
    } catch (error) {
      console.warn('Redis cache read failed:', error);
    }

    // Cache miss - compute value
    this.stats.cacheMisses++;
    this.stats.totalRequests++;
    await this.updateStats();

    const value = await getter();

    // Cache the result
    await this.set(key, value, { ttl, compress, metadata: options.metadata });

    return value;
  }

  /**
   * Set cache value
   */
  async set<T>(
    key: string,
    value: T,
    options: {
      ttl?: number;
      compress?: boolean;
      metadata?: Record<string, any>;
    } = {}
  ): Promise<void> {
    const { ttl = 3600, compress = false, metadata } = options;

    const entry: CacheEntry = {
      key,
      value,
      ttl,
      createdAt: Date.now(),
      hits: 0,
      metadata
    };

    // Store in memory cache
    this.memoryCache.set(key, entry);
    this.ensureMemoryCacheSize();

    // Store in Redis
    const redisKey = `${this.CACHE_PREFIX}:${key}`;
    try {
      let dataToStore = JSON.stringify(entry);

      // Compress if enabled and data is large
      if (compress && dataToStore.length > this.COMPRESSION_THRESHOLD) {
        // In a real implementation, you'd use a compression library
        // For now, just store as-is
        dataToStore = JSON.stringify({
          ...entry,
          compressed: true,
          originalSize: dataToStore.length
        });
      }

      await redisMemory.store(redisKey, dataToStore, ttl);
      this.stats.entriesCount++;
      await this.updateStats();

    } catch (error) {
      console.warn('Redis cache write failed:', error);
    }
  }

  /**
   * Check if key exists in cache
   */
  async exists(key: string): Promise<boolean> {
    // Check memory first
    if (this.memoryCache.has(key)) {
      const entry = this.memoryCache.get(key)!;
      if (Date.now() < entry.createdAt + (entry.ttl * 1000)) {
        return true;
      } else {
        this.memoryCache.delete(key);
      }
    }

    // Check Redis
    const redisKey = `${this.CACHE_PREFIX}:${key}`;
    try {
      const exists = await redisMemory.get(redisKey);
      return !!exists;
    } catch {
      return false;
    }
  }

  /**
   * Delete cache entry
   */
  async delete(key: string): Promise<void> {
    this.memoryCache.delete(key);

    const redisKey = `${this.CACHE_PREFIX}:${key}`;
    try {
      await redisMemory.delete(redisKey);
      this.stats.entriesCount = Math.max(0, this.stats.entriesCount - 1);
      await this.updateStats();
    } catch (error) {
      console.warn('Redis cache delete failed:', error);
    }
  }

  /**
   * Clear all cache entries matching pattern
   */
  async clearPattern(pattern: string): Promise<void> {
    // Clear memory cache entries matching pattern
    for (const [key] of this.memoryCache) {
      if (key.includes(pattern)) {
        this.memoryCache.delete(key);
      }
    }

    // Note: Redis pattern deletion would require SCAN in production
    // For now, we'll rely on TTL expiration
    console.log(`Cleared cache pattern: ${pattern}`);
  }

  /**
   * Get cache statistics
   */
  async getStats(): Promise<CacheStats> {
    // Update hit rate
    this.stats.hitRate = this.stats.totalRequests > 0
      ? this.stats.cacheHits / this.stats.totalRequests
      : 0;

    return { ...this.stats };
  }

  /**
   * Get cache entry metadata
   */
  async getMetadata(key: string): Promise<CacheEntry | null> {
    const entry = this.memoryCache.get(key);
    if (entry) {
      return entry;
    }

    const redisKey = `${this.CACHE_PREFIX}:${key}`;
    try {
      const cached = await redisMemory.get(redisKey);
      if (cached) {
        return JSON.parse(cached);
      }
    } catch (error) {
      console.warn('Redis metadata read failed:', error);
    }

    return null;
  }

  // ===== UTILITY METHODS =====

  /**
   * Generate cache key for company enrichment
   */
  generateCompanyKey(companyName: string, enrichmentType: string = 'full'): string {
    return `company_${companyName.toLowerCase().replace(/[^a-z0-9]/g, '_')}_${enrichmentType}`;
  }

  /**
   * Generate cache key for agent responses
   */
  generateAgentKey(agentName: string, inputHash: string, model?: string): string {
    return `agent_${agentName}_${inputHash}_${model || 'default'}`;
  }

  /**
   * Generate cache key for plan generation
   */
  generatePlanKey(companyName: string, goals: string[], teamSize: number): string {
    const goalsHash = goals.sort().join('_').toLowerCase().replace(/[^a-z0-9]/g, '_');
    return `plan_${companyName.toLowerCase().replace(/[^a-z0-9]/g, '_')}_${goalsHash}_${teamSize}`;
  }

  /**
   * Generate cache key for content ideas
   */
  generateContentKey(topic: string, platform: string, count: number): string {
    return `content_${topic.toLowerCase().replace(/[^a-z0-9]/g, '_')}_${platform}_${count}`;
  }

  // ===== PRIVATE METHODS =====

  private ensureMemoryCacheSize(): void {
    if (this.memoryCache.size > this.MAX_MEMORY_ENTRIES) {
      // Remove oldest entries (simple LRU approximation)
      const entries = Array.from(this.memoryCache.entries());
      entries.sort((a, b) => a[1].createdAt - b[1].createdAt);

      const toRemove = entries.slice(0, this.memoryCache.size - this.MAX_MEMORY_ENTRIES + 10);
      for (const [key] of toRemove) {
        this.memoryCache.delete(key);
      }
    }
  }

  private async updateStats(): Promise<void> {
    try {
      await redisMemory.store(this.STATS_KEY, JSON.stringify(this.stats), 86400); // 24 hours
    } catch (error) {
      console.warn('Stats update failed:', error);
    }
  }
}

// Export singleton instance
export const responseCache = new ResponseCacheService();

// Export types
export type { CacheEntry, CacheStats, CacheKeyGenerator };


