/**
 * Upstash Redis Client
 * Used for caching, rate limiting, and session management
 */

import { Redis } from '@upstash/redis';
import { env } from '../config/env';

// Create Redis client (lazy initialization)
let redisClient: Redis | null = null;

export function getRedis(): Redis {
    if (!redisClient) {
        if (!env.UPSTASH_REDIS_URL || !env.UPSTASH_REDIS_TOKEN) {
            console.warn('⚠️ Redis not configured - using mock client');
            // Return a mock client for development
            return createMockRedis();
        }

        redisClient = new Redis({
            url: env.UPSTASH_REDIS_URL,
            token: env.UPSTASH_REDIS_TOKEN,
        });

        console.log('✅ Redis client initialized');
    }

    return redisClient;
}

// Mock Redis for development without Upstash
function createMockRedis(): Redis {
    const cache = new Map<string, { value: unknown; expiry?: number }>();

    return {
        get: async (key: string) => {
            const item = cache.get(key);
            if (!item) return null;
            if (item.expiry && Date.now() > item.expiry) {
                cache.delete(key);
                return null;
            }
            return item.value;
        },
        set: async (key: string, value: unknown, options?: { ex?: number }) => {
            const expiry = options?.ex ? Date.now() + options.ex * 1000 : undefined;
            cache.set(key, { value, expiry });
            return 'OK';
        },
        del: async (...keys: string[]) => {
            let count = 0;
            keys.forEach(key => {
                if (cache.delete(key)) count++;
            });
            return count;
        },
        incr: async (key: string) => {
            const current = (cache.get(key)?.value as number) || 0;
            cache.set(key, { value: current + 1 });
            return current + 1;
        },
        expire: async (key: string, seconds: number) => {
            const item = cache.get(key);
            if (item) {
                item.expiry = Date.now() + seconds * 1000;
                return 1;
            }
            return 0;
        },
    } as unknown as Redis;
}

// Cache helpers
export async function cacheGet<T>(key: string): Promise<T | null> {
    try {
        const redis = getRedis();
        return await redis.get(key) as T | null;
    } catch (error) {
        console.error('Cache get error:', error);
        return null;
    }
}

export async function cacheSet(
    key: string,
    value: unknown,
    ttlSeconds: number = 300
): Promise<void> {
    try {
        const redis = getRedis();
        await redis.set(key, value, { ex: ttlSeconds });
    } catch (error) {
        console.error('Cache set error:', error);
    }
}

export async function cacheDelete(key: string): Promise<void> {
    try {
        const redis = getRedis();
        await redis.del(key);
    } catch (error) {
        console.error('Cache delete error:', error);
    }
}

// Rate limiting helper
export async function checkRateLimit(
    identifier: string,
    limit: number = 100,
    windowSeconds: number = 60
): Promise<{ allowed: boolean; remaining: number; resetIn: number }> {
    const redis = getRedis();
    const key = `ratelimit:${identifier}`;

    try {
        const current = await redis.incr(key);

        if (current === 1) {
            await redis.expire(key, windowSeconds);
        }

        return {
            allowed: current <= limit,
            remaining: Math.max(0, limit - current),
            resetIn: windowSeconds,
        };
    } catch (error) {
        console.error('Rate limit check error:', error);
        return { allowed: true, remaining: limit, resetIn: windowSeconds };
    }
}

// User session cache
export async function cacheUserSession(userId: string, data: unknown): Promise<void> {
    await cacheSet(`session:${userId}`, data, 3600); // 1 hour
}

export async function getUserSession<T>(userId: string): Promise<T | null> {
    return await cacheGet<T>(`session:${userId}`);
}

// ICP/Cohort data cache
export async function cacheICPs(userId: string, icps: unknown[]): Promise<void> {
    await cacheSet(`icps:${userId}`, icps, 600); // 10 minutes
}

export async function getCachedICPs<T>(userId: string): Promise<T[] | null> {
    return await cacheGet<T[]>(`icps:${userId}`);
}

// Invalidate user cache
export async function invalidateUserCache(userId: string): Promise<void> {
    const redis = getRedis();
    const keys = [
        `session:${userId}`,
        `icps:${userId}`,
        `cohorts:${userId}`,
        `campaigns:${userId}`,
    ];

    try {
        await Promise.all(keys.map(key => redis.del(key)));
    } catch (error) {
        console.error('Cache invalidation error:', error);
    }
}
