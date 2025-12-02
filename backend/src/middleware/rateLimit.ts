import { Response, NextFunction } from 'express';
import { redis } from '../lib/redis';
import { AuthenticatedRequest } from './auth';

interface RateLimitOptions {
  keyPrefix: string;
  limit: number;
  windowSeconds: number;
}

/**
 * Redis-based rate limiting middleware
 * Uses Upstash Redis to track request counts using a sliding window (via Expiration)
 */
export const rateLimit = (options: RateLimitOptions) => {
  return async (req: AuthenticatedRequest, res: Response, next: NextFunction) => {
    try {
      // Identify user by ID if authenticated, otherwise IP
      // Ensure we have a fallback for unauthenticated routes
      const identifier = req.user?.id || req.ip || 'anonymous';
      const key = `ratelimit:${options.keyPrefix}:${identifier}`;

      const requests = await redis.incr(key);

      // Set expiry on first request
      if (requests === 1) {
        await redis.expire(key, options.windowSeconds);
      }

      if (requests > options.limit) {
        const ttl = await redis.ttl(key);
        res.setHeader('Retry-After', ttl);
        return res.status(429).json({
          error: 'Too many requests',
          retryAfter: ttl
        });
      }

      next();
    } catch (error) {
      console.error('Rate limit error:', error);
      // Fail open: Allow request to proceed if Redis is down to avoid blocking users
      next();
    }
  };
};
