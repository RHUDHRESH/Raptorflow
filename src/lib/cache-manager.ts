import { redisClient } from './redis-client';

const DEFAULT_TTL = 60 * 60 * 24; // 24 hours in seconds

export const cacheNamespaces = {
  FOUNDATION: 'fndn',
  MOVE: 'move',
  CAMPAIGN: 'camp',
  AI_RESULT: 'ai_res',
  SESSION: 'sess'
};

/**
 * Cache Wrapper with auto-set and invalidation support
 */
export async function withCache<T>(
  key: string,
  namespace: string,
  fetcher: () => Promise<T>,
  ttl: number = DEFAULT_TTL
): Promise<T> {
  const fullKey = `${namespace}:${key}`;
  
  try {
    // Try to get from cache
    const cached = await redisClient.getJSON<T>(fullKey);
    if (cached) {
      console.log(`🚀 Cache hit: ${fullKey}`);
      return cached;
    }
  } catch (error) {
    console.warn(`⚠️ Redis cache get failed: ${fullKey}`, error);
  }

  // Cache miss: fetch and set
  const data = await fetcher();
  
  try {
    await redisClient.setJSON(fullKey, data, { ex: ttl });
    console.log(`📥 Cache set: ${fullKey}`);
  } catch (error) {
    console.warn(`⚠️ Redis cache set failed: ${fullKey}`, error);
  }

  return data;
}

/**
 * Invalidate a specific cache key
 */
export async function invalidateCache(key: string, namespace: string) {
  const fullKey = `${namespace}:${key}`;
  await redisClient.del(fullKey);
}
