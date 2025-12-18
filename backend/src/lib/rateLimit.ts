import { getRedis } from './redis';

export function rateLimit(options?: {
  windowSeconds?: number;
  maxRequests?: number;
  keyPrefix?: string;
  identifier?: (req: any) => string;
}) {
  const windowSeconds = options?.windowSeconds ?? 60;
  const maxRequests = options?.maxRequests ?? 120;
  const keyPrefix = options?.keyPrefix ?? 'rl';
  const identifier = options?.identifier ?? ((req: any) => req.ip || 'anonymous');

  return async (req: any, res: any, next: any) => {
    try {
      const redis = getRedis();
      const id = identifier(req);
      const key = `${keyPrefix}:${id}:${Math.floor(Date.now() / 1000 / windowSeconds)}`;

      const count = await redis.incr(key);
      if (count === 1) {
        await redis.expire(key, windowSeconds);
      }

      res.setHeader('X-RateLimit-Limit', String(maxRequests));
      res.setHeader('X-RateLimit-Remaining', String(Math.max(0, maxRequests - count)));

      if (count > maxRequests) {
        return res.status(429).json({
          error: 'Rate limit exceeded',
          limit: maxRequests,
          windowSeconds,
        });
      }

      return next();
    } catch (e) {
      return next();
    }
  };
}
