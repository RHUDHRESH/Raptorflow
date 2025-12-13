/**
 * Authentication and Authorization Service
 *
 * Manages API keys, user permissions, quotas, and RBAC for the orchestrator.
 */

import crypto from 'crypto';
import { env } from '../config/env';
import { redisMemory } from './redisMemory';

export interface APIKey {
  id: string;
  key: string;
  name: string;
  projectId: string;
  organizationId: string;
  userId: string;
  permissions: Permission[];
  quotas: QuotaLimits;
  isActive: boolean;
  createdAt: string;
  expiresAt?: string;
  lastUsedAt?: string;
  usageCount: number;
}

export interface Permission {
  resource: string;
  actions: string[];
  conditions?: Record<string, any>;
}

export interface QuotaLimits {
  requestsPerHour: number;
  requestsPerDay: number;
  tokensPerHour: number;
  tokensPerDay: number;
  costPerDay: number;
}

export interface QuotaUsage {
  requestsToday: number;
  requestsThisHour: number;
  tokensToday: number;
  tokensThisHour: number;
  costToday: number;
  lastReset: string;
}

export interface UserContext {
  userId: string;
  organizationId: string;
  projectId?: string;
  roles: string[];
  permissions: Permission[];
}

export type Role = 'admin' | 'user' | 'viewer' | 'api_user';

class AuthService {
  private readonly keyPrefix = 'auth';
  private readonly cacheTTL = 3600; // 1 hour

  /**
   * Create a new API key
   */
  async createAPIKey(
    name: string,
    projectId: string,
    organizationId: string,
    userId: string,
    permissions: Permission[] = [],
    quotas: Partial<QuotaLimits> = {},
    expiresIn?: number // days
  ): Promise<APIKey> {
    const keyId = crypto.randomUUID();
    const keyValue = this.generateAPIKey();

    const apiKey: APIKey = {
      id: keyId,
      key: keyValue,
      name,
      projectId,
      organizationId,
      userId,
      permissions,
      quotas: {
        requestsPerHour: quotas.requestsPerHour || 1000,
        requestsPerDay: quotas.requestsPerDay || 10000,
        tokensPerHour: quotas.tokensPerHour || 100000,
        tokensPerDay: quotas.tokensPerDay || 1000000,
        costPerDay: quotas.costPerDay || 50.00,
      },
      isActive: true,
      createdAt: new Date().toISOString(),
      expiresAt: expiresIn ? new Date(Date.now() + expiresIn * 24 * 60 * 60 * 1000).toISOString() : undefined,
      usageCount: 0,
    };

    // Store in Redis
    await redisMemory.store(`${this.keyPrefix}:key:${keyValue}`, apiKey, this.cacheTTL);

    // Index by project and user
    await redisMemory.store(`${this.keyPrefix}:project_keys:${projectId}:${keyId}`, keyValue, this.cacheTTL);
    await redisMemory.store(`${this.keyPrefix}:user_keys:${userId}:${keyId}`, keyValue, this.cacheTTL);

    console.log(`🔑 Created API key: ${name} for project ${projectId}`);

    return apiKey;
  }

  /**
   * Validate API key and return context
   */
  async validateAPIKey(apiKeyValue: string): Promise<UserContext | null> {
    try {
      const keyData = await redisMemory.retrieve<APIKey>(`${this.keyPrefix}:key:${apiKeyValue}`);

      if (!keyData || !keyData.isActive) {
        return null;
      }

      // Check expiration
      if (keyData.expiresAt && new Date(keyData.expiresAt) < new Date()) {
        return null;
      }

      // Update last used
      keyData.lastUsedAt = new Date().toISOString();
      keyData.usageCount++;
      await redisMemory.store(`${this.keyPrefix}:key:${apiKeyValue}`, keyData, this.cacheTTL);

      return {
        userId: keyData.userId,
        organizationId: keyData.organizationId,
        projectId: keyData.projectId,
        roles: ['api_user'],
        permissions: keyData.permissions,
      };

    } catch (error) {
      console.error('API key validation error:', error);
      return null;
    }
  }

  /**
   * Check if user has permission for action
   */
  checkPermission(userContext: UserContext, resource: string, action: string): boolean {
    // Admin override
    if (userContext.roles.includes('admin')) {
      return true;
    }

    // Check specific permissions
    return userContext.permissions.some(permission => {
      if (permission.resource !== resource && permission.resource !== '*') {
        return false;
      }

      return permission.actions.includes(action) || permission.actions.includes('*');
    });
  }

  /**
   * Check and update usage quotas
   */
  async checkQuota(
    userContext: UserContext,
    action: 'request' | 'tokens' | 'cost',
    amount: number = 1
  ): Promise<{ allowed: boolean; usage: QuotaUsage }> {
    const quotaKey = `${this.keyPrefix}:quota:${userContext.userId}:${new Date().toISOString().slice(0, 10)}`;
    const hourlyKey = `${this.keyPrefix}:quota_hourly:${userContext.userId}:${new Date().toISOString().slice(0, 13)}`;

    let usage = await redisMemory.retrieve<QuotaUsage>(quotaKey) || {
      requestsToday: 0,
      requestsThisHour: 0,
      tokensToday: 0,
      tokensThisHour: 0,
      costToday: 0,
      lastReset: new Date().toISOString(),
    };

    let hourlyUsage = await redisMemory.retrieve<QuotaUsage>(hourlyKey) || {
      requestsToday: 0,
      requestsThisHour: 0,
      tokensToday: 0,
      tokensThisHour: 0,
      costToday: 0,
      lastReset: new Date().toISOString(),
    };

    // Update usage based on action
    switch (action) {
      case 'request':
        usage.requestsToday += amount;
        hourlyUsage.requestsThisHour += amount;
        break;
      case 'tokens':
        usage.tokensToday += amount;
        hourlyUsage.tokensThisHour += amount;
        break;
      case 'cost':
        usage.costToday += amount;
        break;
    }

    // Check limits (simplified - in production, get from API key config)
    const limits: QuotaLimits = {
      requestsPerHour: 1000,
      requestsPerDay: 10000,
      tokensPerHour: 100000,
      tokensPerDay: 1000000,
      costPerDay: 50.00,
    };

    const allowed = (
      usage.requestsToday <= limits.requestsPerDay &&
      hourlyUsage.requestsThisHour <= limits.requestsPerHour &&
      usage.tokensToday <= limits.tokensPerDay &&
      hourlyUsage.tokensThisHour <= limits.tokensPerHour &&
      usage.costToday <= limits.costPerDay
    );

    if (allowed) {
      // Save updated usage
      await redisMemory.store(quotaKey, usage, 86400); // 24 hours
      await redisMemory.store(hourlyKey, hourlyUsage, 3600); // 1 hour
    }

    return { allowed, usage };
  }

  /**
   * Get API keys for a project
   */
  async getProjectAPIKeys(projectId: string): Promise<APIKey[]> {
    const keys: APIKey[] = [];
    // In production, this would query the database
    // For now, return empty array
    return keys;
  }

  /**
   * Revoke API key
   */
  async revokeAPIKey(apiKeyValue: string): Promise<boolean> {
    try {
      const keyData = await redisMemory.retrieve<APIKey>(`${this.keyPrefix}:key:${apiKeyValue}`);
      if (!keyData) return false;

      keyData.isActive = false;
      await redisMemory.store(`${this.keyPrefix}:key:${apiKeyValue}`, keyData, this.cacheTTL);

      console.log(`🚫 Revoked API key: ${keyData.name}`);
      return true;

    } catch (error) {
      console.error('API key revocation error:', error);
      return false;
    }
  }

  /**
   * Generate JWT token for user authentication
   */
  async generateJWT(userId: string, organizationId: string, roles: Role[] = ['user']): Promise<string> {
    // Simplified JWT generation - in production, use a proper JWT library
    const payload = {
      userId,
      organizationId,
      roles,
      iat: Math.floor(Date.now() / 1000),
      exp: Math.floor(Date.now() / 1000) + (24 * 60 * 60), // 24 hours
    };

    const header = {
      alg: 'HS256',
      typ: 'JWT',
    };

    const encodedHeader = Buffer.from(JSON.stringify(header)).toString('base64url');
    const encodedPayload = Buffer.from(JSON.stringify(payload)).toString('base64url');

    const signature = crypto
      .createHmac('sha256', env.JWT_SECRET || 'default-secret')
      .update(`${encodedHeader}.${encodedPayload}`)
      .digest('base64url');

    return `${encodedHeader}.${encodedPayload}.${signature}`;
  }

  /**
   * Validate JWT token
   */
  async validateJWT(token: string): Promise<UserContext | null> {
    try {
      const parts = token.split('.');
      if (parts.length !== 3) return null;

      const payload = JSON.parse(Buffer.from(parts[1], 'base64url').toString());

      // Check expiration
      if (payload.exp && payload.exp < Math.floor(Date.now() / 1000)) {
        return null;
      }

      return {
        userId: payload.userId,
        organizationId: payload.organizationId,
        roles: payload.roles || [],
        permissions: [], // Would be populated from database
      };

    } catch (error) {
      console.error('JWT validation error:', error);
      return null;
    }
  }

  /**
   * Middleware for API authentication
   */
  authenticateRequest(req: any, res: any, next: any): void {
    const authHeader = req.headers.authorization;
    const apiKey = req.headers['x-api-key'];

    if (apiKey) {
      // API key authentication
      const context = this.validateAPIKey(apiKey);
      if (context) {
        req.user = context;
        return next();
      }
    } else if (authHeader?.startsWith('Bearer ')) {
      // JWT authentication
      const token = authHeader.substring(7);
      const context = this.validateJWT(token);
      if (context) {
        req.user = context;
        return next();
      }
    }

    res.status(401).json({
      error: 'Authentication required',
      message: 'Valid API key or JWT token required',
    });
  }

  /**
   * Middleware for authorization
   */
  authorize(resource: string, action: string) {
    return (req: any, res: any, next: any): void => {
      if (!req.user) {
        return res.status(401).json({
          error: 'Authentication required',
        });
      }

      if (!this.checkPermission(req.user, resource, action)) {
        return res.status(403).json({
          error: 'Insufficient permissions',
          message: `Access denied for ${resource}:${action}`,
        });
      }

      next();
    };
  }

  /**
   * Middleware for quota checking
   */
  checkQuotaMiddleware(action: 'request' | 'tokens' | 'cost', amount: number = 1) {
    return async (req: any, res: any, next: any): Promise<void> => {
      if (!req.user) return next();

      const { allowed, usage } = await this.checkQuota(req.user, action, amount);

      if (!allowed) {
        return res.status(429).json({
          error: 'Quota exceeded',
          message: 'Usage quota has been exceeded',
          usage,
        });
      }

      req.quotaUsage = usage;
      next();
    };
  }

  // =====================================================
  // PRIVATE METHODS
  // =====================================================

  /**
   * Extract user context from request (for JWT-based auth)
   * TODO: Implement JWT token extraction and validation
   */
  extractUserContext(req: any): UserContext {
    // For now, return mock context - this should be replaced with actual JWT validation
    return {
      userId: req.user?.id || 'mock-user-id',
      organizationId: req.user?.organization_id || 'mock-org-id',
      projectId: req.user?.project_id,
      roles: ['user'],
      permissions: [
        {
          resource: 'orchestrator',
          actions: ['create_job', 'read_job', 'list_jobs'],
        },
      ],
    };
  }

  private generateAPIKey(): string {
    return `sk_${crypto.randomBytes(32).toString('hex')}`;
  }
}

// Export singleton instance
export const authService = new AuthService();

// Export types
export type { APIKey, Permission, QuotaLimits, QuotaUsage, UserContext, Role };
