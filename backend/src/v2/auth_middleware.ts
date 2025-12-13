import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';

// =====================================================
// AUTHENTICATION & AUTHORIZATION MIDDLEWARE
// =====================================================

interface AuthenticatedRequest extends Request {
  user?: {
    id: string;
    email: string;
    role: string;
    permissions: string[];
  };
}

// JWT Secret - in production, use environment variable
const JWT_SECRET = process.env.JWT_SECRET || 'your-jwt-secret-key-change-in-production';

/**
 * JWT Authentication Middleware
 */
export const authenticateJWT = (req: AuthenticatedRequest, res: Response, next: NextFunction) => {
  const authHeader = req.headers.authorization;

  if (!authHeader) {
    return res.status(401).json({ error: 'Authorization header required' });
  }

  const token = authHeader.split(' ')[1]; // Bearer TOKEN

  if (!token) {
    return res.status(401).json({ error: 'Bearer token required' });
  }

  try {
    const decoded = jwt.verify(token, JWT_SECRET) as any;
    req.user = {
      id: decoded.userId,
      email: decoded.email,
      role: decoded.role || 'user',
      permissions: decoded.permissions || ['read', 'write']
    };
    next();
  } catch (error) {
    return res.status(403).json({ error: 'Invalid or expired token' });
  }
};

/**
 * Role-based Authorization Middleware
 */
export const authorizeRole = (requiredRole: string) => {
  return (req: AuthenticatedRequest, res: Response, next: NextFunction) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    // Simple role hierarchy: admin > manager > user
    const roleHierarchy = { admin: 3, manager: 2, user: 1 };
    const userRoleLevel = roleHierarchy[req.user.role as keyof typeof roleHierarchy] || 0;
    const requiredRoleLevel = roleHierarchy[requiredRole as keyof typeof roleHierarchy] || 0;

    if (userRoleLevel < requiredRoleLevel) {
      return res.status(403).json({
        error: 'Insufficient permissions',
        required: requiredRole,
        current: req.user.role
      });
    }

    next();
  };
};

/**
 * Permission-based Authorization Middleware
 */
export const requirePermission = (requiredPermission: string) => {
  return (req: AuthenticatedRequest, res: Response, next: NextFunction) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    if (!req.user.permissions.includes(requiredPermission)) {
      return res.status(403).json({
        error: 'Permission denied',
        required: requiredPermission,
        available: req.user.permissions
      });
    }

    next();
  };
};

/**
 * API Key Authentication (alternative to JWT)
 */
export const authenticateApiKey = (req: AuthenticatedRequest, res: Response, next: NextFunction) => {
  const apiKey = req.headers['x-api-key'] as string;

  if (!apiKey) {
    return res.status(401).json({ error: 'API key required in x-api-key header' });
  }

  // In production, validate against database
  if (apiKey !== process.env.API_KEY && apiKey !== 'dev-api-key-123') {
    return res.status(403).json({ error: 'Invalid API key' });
  }

  // Mock user for API key auth
  req.user = {
    id: 'api-user',
    email: 'api@ractorflow.com',
    role: 'user',
    permissions: ['read', 'write']
  };

  next();
};

// =====================================================
// RATE LIMITING MIDDLEWARE
// =====================================================

interface RateLimitStore {
  [key: string]: {
    count: number;
    resetTime: number;
  };
}

// In-memory rate limiting (use Redis in production)
const rateLimitStore: RateLimitStore = {};

/**
 * Rate Limiting Middleware
 */
export const rateLimit = (
  maxRequests: number = 100,
  windowMs: number = 15 * 60 * 1000, // 15 minutes
  identifierFn?: (req: Request) => string
) => {
  return (req: AuthenticatedRequest, res: Response, next: NextFunction) => {
    const identifier = identifierFn
      ? identifierFn(req)
      : req.user?.id || req.ip || 'anonymous';

    const now = Date.now();
    const windowStart = now - windowMs;

    // Clean up expired entries
    Object.keys(rateLimitStore).forEach(key => {
      if (rateLimitStore[key].resetTime < windowStart) {
        delete rateLimitStore[key];
      }
    });

    // Get or create rate limit entry
    const entry = rateLimitStore[identifier] || {
      count: 0,
      resetTime: now + windowMs
    };

    // Check if limit exceeded
    if (entry.count >= maxRequests) {
      const resetIn = Math.ceil((entry.resetTime - now) / 1000);
      return res.status(429).json({
        error: 'Rate limit exceeded',
        retry_after: resetIn,
        limit: maxRequests,
        window: `${windowMs / 1000}s`
      });
    }

    // Increment counter
    entry.count++;
    rateLimitStore[identifier] = entry;

    // Add headers
    res.set({
      'X-RateLimit-Limit': maxRequests.toString(),
      'X-RateLimit-Remaining': (maxRequests - entry.count).toString(),
      'X-RateLimit-Reset': entry.resetTime.toString()
    });

    next();
  };
};

// =====================================================
// REQUEST LOGGING MIDDLEWARE
// =====================================================

export const requestLogger = (req: AuthenticatedRequest, res: Response, next: NextFunction) => {
  const startTime = Date.now();
  const userId = req.user?.id || 'anonymous';
  const method = req.method;
  const url = req.url;

  console.log(`📨 ${method} ${url} - User: ${userId} - ${new Date().toISOString()}`);

  // Log response
  res.on('finish', () => {
    const duration = Date.now() - startTime;
    const statusCode = res.statusCode;
    console.log(`📤 ${method} ${url} - ${statusCode} - ${duration}ms`);
  });

  next();
};

// =====================================================
// UTILITY FUNCTIONS
// =====================================================

/**
 * Generate JWT token
 */
export const generateToken = (user: { id: string; email: string; role?: string; permissions?: string[] }) => {
  return jwt.sign({
    userId: user.id,
    email: user.email,
    role: user.role || 'user',
    permissions: user.permissions || ['read', 'write']
  }, JWT_SECRET, { expiresIn: '24h' });
};

/**
 * Verify JWT token (utility function)
 */
export const verifyToken = (token: string) => {
  try {
    return jwt.verify(token, JWT_SECRET);
  } catch (error) {
    return null;
  }
};


