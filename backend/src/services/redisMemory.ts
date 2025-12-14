/**
 * Redis Memory Service for Orchestrator
 *
 * Provides short-term memory primitives for the orchestrator with TTL policies.
 * Handles conversational memory, context snapshots, job state, and rate limiting.
 */

import { getRedis } from '../lib/redis';
import type { Redis } from '@upstash/redis';

export interface MemoryEntry {
  data: unknown;
  createdAt: number;
  expiresAt?: number;
  metadata?: Record<string, unknown>;
}

export interface ConversationContext {
  messages: Array<{
    role: 'user' | 'assistant' | 'system';
    content: string;
    timestamp: number;
  }>;
  metadata: {
    brandProfileId?: string;
    projectId?: string;
    sessionId: string;
    lastActivity: number;
  };
}

export interface JobContext {
  jobId: string;
  status: string;
  progress: number;
  contextSnapshot: Record<string, unknown>;
  lastUpdate: number;
}

export class RedisMemoryService {
  private redis: Redis;
  private readonly prefix = 'orchestrator';

  constructor() {
    this.redis = getRedis();
  }

  // =====================================================
  // SHORT-TERM MEMORY PRIMITIVES
  // =====================================================

  /**
   * Store data with TTL
   */
  async store(
    key: string,
    data: unknown,
    ttlSeconds: number = 3600,
    metadata?: Record<string, unknown>
  ): Promise<void> {
    const entry: MemoryEntry = {
      data,
      createdAt: Date.now(),
      expiresAt: Date.now() + ttlSeconds * 1000,
      metadata,
    };

    const fullKey = this.getFullKey('memory', key);
    await this.redis.set(fullKey, JSON.stringify(entry), { ex: ttlSeconds });
  }

  /**
   * Retrieve data from memory
   */
  async retrieve<T = unknown>(key: string): Promise<T | null> {
    try {
      const fullKey = this.getFullKey('memory', key);
      const data = await this.redis.get(fullKey);

      if (!data) return null;

      const entry: MemoryEntry = typeof data === 'string' ? JSON.parse(data) : data;

      // Check if expired
      if (entry.expiresAt && Date.now() > entry.expiresAt) {
        await this.delete(key);
        return null;
      }

      return entry.data as T;
    } catch (error) {
      console.error('Memory retrieve error:', error);
      return null;
    }
  }

  /**
   * Delete from memory
   */
  async delete(key: string): Promise<void> {
    const fullKey = this.getFullKey('memory', key);
    await this.redis.del(fullKey);
  }

  /**
   * Extend TTL for a key
   */
  async extendTTL(key: string, ttlSeconds: number): Promise<boolean> {
    const fullKey = this.getFullKey('memory', key);
    return await this.redis.expire(fullKey, ttlSeconds) === 1;
  }

  /**
   * Check if key exists and is not expired
   */
  async exists(key: string): Promise<boolean> {
    const fullKey = this.getFullKey('memory', key);
    return await this.redis.exists(fullKey) === 1;
  }

  // =====================================================
  // CONVERSATIONAL MEMORY
  // =====================================================

  /**
   * Store conversation context
   */
  async storeConversation(sessionId: string, context: ConversationContext, ttlSeconds: number = 86400): Promise<void> {
    const key = `conversation:${sessionId}`;
    await this.store(key, context, ttlSeconds);
  }

  /**
   * Retrieve conversation context
   */
  async getConversation(sessionId: string): Promise<ConversationContext | null> {
    const key = `conversation:${sessionId}`;
    return await this.retrieve<ConversationContext>(key);
  }

  /**
   * Add message to conversation
   */
  async addMessage(
    sessionId: string,
    message: { role: 'user' | 'assistant' | 'system'; content: string },
    maxMessages: number = 50
  ): Promise<void> {
    const context = await this.getConversation(sessionId) || {
      messages: [],
      metadata: {
        sessionId,
        lastActivity: Date.now(),
      },
    };

    context.messages.push({
      ...message,
      timestamp: Date.now(),
    });

    // Keep only the most recent messages
    if (context.messages.length > maxMessages) {
      context.messages = context.messages.slice(-maxMessages);
    }

    context.metadata.lastActivity = Date.now();

    await this.storeConversation(sessionId, context);
  }

  /**
   * Clear conversation memory
   */
  async clearConversation(sessionId: string): Promise<void> {
    const key = `conversation:${sessionId}`;
    await this.delete(key);
  }

  // =====================================================
  // JOB CONTEXT & STATE
  // =====================================================

  /**
   * Store job context snapshot
   */
  async storeJobContext(jobId: string, context: JobContext, ttlSeconds: number = 86400): Promise<void> {
    const key = `job:${jobId}`;
    await this.store(key, context, ttlSeconds);
  }

  /**
   * Get job context
   */
  async getJobContext(jobId: string): Promise<JobContext | null> {
    const key = `job:${jobId}`;
    return await this.retrieve<JobContext>(key);
  }

  /**
   * Update job progress
   */
  async updateJobProgress(jobId: string, progress: number, status?: string): Promise<void> {
    const context = await this.getJobContext(jobId);
    if (context) {
      context.progress = progress;
      if (status) context.status = status;
      context.lastUpdate = Date.now();
      await this.storeJobContext(jobId, context);
    }
  }

  /**
   * Clear job context
   */
  async clearJobContext(jobId: string): Promise<void> {
    const key = `job:${jobId}`;
    await this.delete(key);
  }

  // =====================================================
  // BRAND PROFILE CACHE
  // =====================================================

  /**
   * Cache brand profile for quick access
   */
  async cacheBrandProfile(brandProfileId: string, profile: unknown, ttlSeconds: number = 3600): Promise<void> {
    const key = `brand:${brandProfileId}`;
    await this.store(key, profile, ttlSeconds);
  }

  /**
   * Get cached brand profile
   */
  async getCachedBrandProfile(brandProfileId: string): Promise<unknown | null> {
    const key = `brand:${brandProfileId}`;
    return await this.retrieve(key);
  }

  /**
   * Invalidate brand profile cache
   */
  async invalidateBrandProfile(brandProfileId: string): Promise<void> {
    const key = `brand:${brandProfileId}`;
    await this.delete(key);
  }

  // =====================================================
  // AGENT MEMORY & CONTEXT
  // =====================================================

  /**
   * Store agent-specific memory
   */
  async storeAgentMemory(
    agentName: string,
    sessionId: string,
    data: unknown,
    ttlSeconds: number = 7200
  ): Promise<void> {
    const key = `agent:${agentName}:${sessionId}`;
    await this.store(key, data, ttlSeconds);
  }

  /**
   * Get agent memory
   */
  async getAgentMemory<T = unknown>(agentName: string, sessionId: string): Promise<T | null> {
    const key = `agent:${agentName}:${sessionId}`;
    return await this.retrieve<T>(key);
  }

  /**
   * Store agent prompt cache
   */
  async cachePrompt(agentName: string, promptKey: string, prompt: string, ttlSeconds: number = 3600): Promise<void> {
    const key = `prompt:${agentName}:${promptKey}`;
    await this.store(key, prompt, ttlSeconds);
  }

  /**
   * Get cached prompt
   */
  async getCachedPrompt(agentName: string, promptKey: string): Promise<string | null> {
    const key = `prompt:${agentName}:${promptKey}`;
    return await this.retrieve<string>(key);
  }

  // =====================================================
  // UTILITY METHODS
  // =====================================================

  /**
   * Clean up expired entries (maintenance)
   */
  async cleanupExpired(): Promise<void> {
    // Redis handles TTL automatically, but this could be used for custom cleanup logic
    console.log('Memory cleanup completed');
  }

  /**
   * Get memory stats
   */
  async getStats(): Promise<{
    totalKeys: number;
    memoryUsage: unknown;
  }> {
    try {
      // This is a simplified stats implementation
      // In production, you might want to use Redis INFO command
      return {
        totalKeys: 0, // Would need to implement key counting
        memoryUsage: null,
      };
    } catch (error) {
      console.error('Memory stats error:', error);
      return { totalKeys: 0, memoryUsage: null };
    }
  }

  /**
   * Clear all orchestrator memory (dangerous!)
   */
  async clearAll(): Promise<void> {
    // This would require careful implementation with pattern matching
    console.warn('Clear all memory operation not implemented for safety');
  }

  // =====================================================
  // PRIVATE METHODS
  // =====================================================

  private getFullKey(namespace: string, key: string): string {
    return `${this.prefix}:${namespace}:${key}`;
  }
}

// Export singleton instance
export const redisMemory = new RedisMemoryService();

// Export types for use in other modules
export type { MemoryEntry, ConversationContext, JobContext };

