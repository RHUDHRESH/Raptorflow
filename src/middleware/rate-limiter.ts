import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Rate limiting configuration
const RATE_LIMITS = {
  // Authentication endpoints: 10 requests per minute
  auth: { limit: 10, windowMs: 60 * 1000 },
  // API endpoints: 30 requests per minute
  api: { limit: 30, windowMs: 60 * 1000 },
  // General: 100 requests per minute
  general: { limit: 100, windowMs: 60 * 1000 }
};

// In-memory store for rate limiting (in production, use Redis or database)
const rateLimitStore = new Map<string, { count: number; resetTime: number }>();

// Clean up expired entries periodically
setInterval(() => {
  const now = Date.now();
  for (const [key, value] of rateLimitStore.entries()) {
    if (now > value.resetTime) {
      rateLimitStore.delete(key);
    }
  }
}, 60000); // Clean up every minute

function getRateLimitKey(req: NextRequest, type: string): string {
  const ip = req.ip || req.headers.get('x-forwarded-for') || 'unknown';
  const userAgent = req.headers.get('user-agent') || 'unknown';
  return `${type}:${ip}:${userAgent}`;
}

function isRateLimited(key: string, limit: number, windowMs: number): boolean {
  const now = Date.now();
  const record = rateLimitStore.get(key);
  
  if (!record || now > record.resetTime) {
    // First request or window expired
    rateLimitStore.set(key, {
      count: 1,
      resetTime: now + windowMs
    });
    return false;
  }
  
  if (record.count >= limit) {
    return true;
  }
  
  // Increment counter
  record.count++;
  return false;
}

export function rateLimit(type: 'auth' | 'api' | 'general' = 'general') {
  return async (req: NextRequest): Promise<NextResponse | undefined> => {
    const config = RATE_LIMITS[type];
    const key = getRateLimitKey(req, type);
    
    if (isRateLimited(key, config.limit, config.windowMs)) {
      return NextResponse.json(
        { 
          error: 'Rate limit exceeded',
          message: `Too many requests. Please try again later.`,
          retryAfter: Math.ceil(config.windowMs / 1000)
        },
        { 
          status: 429,
          headers: {
            'Retry-After': Math.ceil(config.windowMs / 1000).toString(),
            'X-RateLimit-Limit': config.limit.toString(),
            'X-RateLimit-Remaining': '0',
            'X-RateLimit-Reset': new Date(Date.now() + config.windowMs).toISOString()
          }
        }
      );
    }
    
    // Add rate limit headers to successful responses
    const record = rateLimitStore.get(key);
    const remaining = record ? Math.max(0, config.limit - record.count) : config.limit;
    
    const response = NextResponse.next();
    response.headers.set('X-RateLimit-Limit', config.limit.toString());
    response.headers.set('X-RateLimit-Remaining', remaining.toString());
    response.headers.set('X-RateLimit-Reset', record?.resetTime?.toString() || '');
    
    return response;
  };
}

// Specific rate limiters for different endpoint types
export const authRateLimit = rateLimit('auth');
export const apiRateLimit = rateLimit('api');
export const generalRateLimit = rateLimit('general');
