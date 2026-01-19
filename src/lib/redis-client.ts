// Redis client for frontend integration with Upstash Redis
// Provides direct Redis access for real-time features and session management

import { Redis } from '@upstash/redis'

const redis = new Redis({
  url: process.env.NEXT_PUBLIC_UPSTASH_REDIS_URL!,
  token: process.env.NEXT_PUBLIC_UPSTASH_REDIS_TOKEN!,
})

// Helper functions for common Redis operations
export const redisClient = {
  // Basic operations
  async get(key: string): Promise<string | null> {
    return await redis.get(key)
  },

  async set(key: string, value: string, options?: { ex?: number }): Promise<string | null> {
    if (options?.ex) {
      return await redis.set(key, value, { ex: options.ex })
    }
    return await redis.set(key, value)
  },

  async del(key: string): Promise<number> {
    return await redis.del(key)
  },

  async exists(key: string): Promise<number> {
    return await redis.exists(key)
  },

  async expire(key: string, seconds: number): Promise<boolean> {
    const result = await redis.expire(key, seconds)
    return result === 1
  },

  // JSON operations
  async getJSON<T = any>(key: string): Promise<T | null> {
    const value = await redis.get(key)
    if (value && typeof value === 'string') {
      try {
        return JSON.parse(value)
      } catch {
        return null
      }
    }
    return null
  },

  async setJSON(key: string, value: any, options?: { ex?: number }): Promise<string | null> {
    const jsonString = JSON.stringify(value)
    if (options?.ex) {
      return await redis.set(key, jsonString, { ex: options.ex })
    }
    return await redis.set(key, jsonString)
  },

  // Hash operations
  async hget(key: string, field: string): Promise<string | null> {
    return await redis.hget(key, field)
  },

  async hset(key: string, field: string, value: string): Promise<number> {
    return await redis.hset(key, { [field]: value })
  },

  async hgetall(key: string): Promise<Record<string, string>> {
    const result = await redis.hgetall(key)
    // Convert Record<string, unknown> to Record<string, string>
    const converted: Record<string, string> = {}
    if (result && typeof result === 'object') {
      for (const [k, v] of Object.entries(result)) {
        converted[k] = String(v)
      }
    }
    return converted
  },

  async hdel(key: string, field: string): Promise<number> {
    return await redis.hdel(key, field)
  },

  // List operations (for queues)
  async lpush(key: string, ...values: string[]): Promise<number> {
    return await redis.lpush(key, ...values)
  },

  async rpop(key: string): Promise<string | null> {
    return await redis.rpop(key)
  },

  async lrange(key: string, start: number, stop: number): Promise<string[]> {
    const result = await redis.lrange(key, start, stop)
    return result || []
  },

  async llen(key: string): Promise<number> {
    return await redis.llen(key)
  },

  // Health check
  async ping(): Promise<boolean> {
    try {
      const result = await redis.ping()
      return result === 'PONG'
    } catch {
      return false
    }
  },
}

export default redisClient
