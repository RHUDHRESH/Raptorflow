/**
 * V3 Unified Types
 *
 * Type definitions for the unified V1-V2 orchestration system
 */

import { z } from 'zod';

// =====================================================
// UNIFIED REQUEST/RESPONSE CONTRACTS
// =====================================================

export const UnifiedRequestSchema = z.object({
  userId: z.string(),
  goal: z.string().min(10, "Goal must be at least 10 characters"),
  context: z.object({
    campaign: z.record(z.any()).optional(),
    icp: z.record(z.any()).optional(),
    brand: z.record(z.any()).optional(),
    constraints: z.array(z.string()).optional()
  }).optional(),
  agentSelection: z.enum(['auto', 'manual']).default('auto'),
  selectedAgents: z.array(z.string()).optional(),
  priority: z.enum(['speed', 'quality', 'balanced']).default('balanced'),
  inputOverrides: z.record(z.any()).optional()
});

export const UnifiedResponseSchema = z.object({
  executionId: z.string(),
  status: z.enum(['queued', 'processing', 'completed', 'failed']),
  result: z.any().optional(),
  error: z.string().optional(),
  agentsInvolved: z.array(z.string()),
  startTime: z.date(),
  endTime: z.date().optional(),
  tokenUsage: z.number().optional(),
  costEstimate: z.number().optional(),
  systemUsed: z.enum(['v1', 'v2', 'hybrid']).optional(),
  routingReason: z.string().optional(),
  estimatedCompletion: z.string().optional()
});

export type UnifiedRequest = z.infer<typeof UnifiedRequestSchema>;
export type UnifiedResponse = z.infer<typeof UnifiedResponseSchema>;

// =====================================================
// AGENT CAPABILITIES
// =====================================================

export const AgentCapabilitiesSchema = z.object({
  name: z.string(),
  system: z.enum(['v1', 'v2']),
  description: z.string(),
  category: z.enum(['brand', 'content', 'marketing', 'technical']),
  capabilities: z.array(z.string()),
  inputs: z.array(z.string()),
  outputs: z.array(z.string()),
  costEstimate: z.object({
    minTokens: z.number(),
    maxTokens: z.number(),
    estimatedCost: z.number()
  }),
  metadata: z.object({
    author: z.string(),
    tags: z.array(z.string()),
    complexity: z.enum(['simple', 'medium', 'complex']),
    version: z.string()
  })
});

export type AgentCapabilities = z.infer<typeof AgentCapabilitiesSchema>;

// =====================================================
// ROUTING DECISIONS
// =====================================================

export const RoutingDecisionSchema = z.object({
  system: z.enum(['v1', 'v2', 'hybrid']),
  agents: z.array(z.string()),
  reason: z.string(),
  v1Agents: z.array(z.string()).optional(),
  v2Agents: z.array(z.string()).optional(),
  confidence: z.number().min(0).max(1).optional(),
  estimatedTokens: z.number().optional(),
  estimatedCost: z.number().optional()
});

export type RoutingDecision = z.infer<typeof RoutingDecisionSchema>;

// =====================================================
// EXECUTION STATUS
// =====================================================

export const ExecutionStatusSchema = z.object({
  executionId: z.string(),
  status: z.enum(['queued', 'processing', 'completed', 'failed']),
  startTime: z.date(),
  endTime: z.date().optional(),
  userId: z.string(),
  goal: z.string(),
  agentsInvolved: z.array(z.string()),
  systemUsed: z.enum(['v1', 'v2', 'hybrid']).optional(),
  progress: z.number().min(0).max(100),
  result: z.any().optional(),
  error: z.string().optional(),
  tokenUsage: z.number().optional(),
  costEstimate: z.number().optional()
});

export type ExecutionStatus = z.infer<typeof ExecutionStatusSchema>;

// =====================================================
// SYSTEM HEALTH
// =====================================================

export const SystemHealthSchema = z.object({
  v1: z.object({
    status: z.enum(['healthy', 'degraded', 'unhealthy']),
    agents: z.number(),
    message: z.string().optional()
  }),
  v2: z.object({
    status: z.enum(['healthy', 'degraded', 'unhealthy']),
    agents: z.number(),
    message: z.string().optional()
  }),
  overall: z.enum(['healthy', 'degraded', 'unhealthy']),
  lastChecked: z.date().optional(),
  version: z.string().optional()
});

export type SystemHealth = z.infer<typeof SystemHealthSchema>;

// =====================================================
// CONTEXT BRIDGE TYPES
// =====================================================

export const SharedContextSchema = z.object({
  fromSystem: z.enum(['v1', 'v2']),
  toSystem: z.enum(['v1', 'v2']),
  context: z.record(z.any()),
  sharedAt: z.string(),
  ttl: z.number(),
  version: z.string().optional()
});

export type SharedContext = z.infer<typeof SharedContextSchema>;

export const ExecutionContextSchema = z.object({
  executionId: z.string(),
  context: z.record(z.any()),
  storedAt: z.string(),
  expiresAt: z.string().optional()
});

export type ExecutionContext = z.infer<typeof ExecutionContextSchema>;

// =====================================================
// ADAPTER INTERFACE TYPES
// =====================================================

export interface AdapterHealth {
  status: 'healthy' | 'degraded' | 'unhealthy';
  agents: number;
  message?: string;
  lastChecked?: Date;
}

export interface AdapterCapabilities {
  canHandleAgents: (agentNames: string[]) => boolean;
  getExecutionStatus?: (executionId: string) => Promise<any>;
  getMetrics?: () => Promise<any>;
}

// =====================================================
// ERROR TYPES
// =====================================================

export class UnifiedOrchestratorError extends Error {
  constructor(
    message: string,
    public code: string,
    public system?: 'v1' | 'v2' | 'hybrid',
    public executionId?: string
  ) {
    super(message);
    this.name = 'UnifiedOrchestratorError';
  }
}

export class AdapterError extends Error {
  constructor(
    message: string,
    public adapter: string,
    public agent?: string,
    public originalError?: Error
  ) {
    super(message);
    this.name = 'AdapterError';
  }
}

export class RoutingError extends Error {
  constructor(
    message: string,
    public request: UnifiedRequest,
    public attemptedRoutes: string[]
  ) {
    super(message);
    this.name = 'RoutingError';
  }
}

// =====================================================
// CONFIGURATION TYPES
// =====================================================

export const UnifiedConfigSchema = z.object({
  v1: z.object({
    enabled: z.boolean().default(true),
    maxConcurrentExecutions: z.number().default(10),
    timeoutSeconds: z.number().default(300),
    retryAttempts: z.number().default(3)
  }),
  v2: z.object({
    enabled: z.boolean().default(true),
    maxConcurrentExecutions: z.number().default(20),
    timeoutSeconds: z.number().default(600),
    retryAttempts: z.number().default(2),
    tokenBudget: z.number().default(50000)
  }),
  routing: z.object({
    defaultSystem: z.enum(['v1', 'v2', 'auto']).default('auto'),
    costThreshold: z.number().default(0.50),
    complexityThreshold: z.number().default(0.7),
    enableHybrid: z.boolean().default(true)
  }),
  monitoring: z.object({
    enableMetrics: z.boolean().default(true),
    logLevel: z.enum(['debug', 'info', 'warn', 'error']).default('info'),
    enableTracing: z.boolean().default(false)
  })
});

export type UnifiedConfig = z.infer<typeof UnifiedConfigSchema>;

// Default configuration
export const DEFAULT_UNIFIED_CONFIG: UnifiedConfig = {
  v1: {
    enabled: true,
    maxConcurrentExecutions: 10,
    timeoutSeconds: 300,
    retryAttempts: 3
  },
  v2: {
    enabled: true,
    maxConcurrentExecutions: 20,
    timeoutSeconds: 600,
    retryAttempts: 2,
    tokenBudget: 50000
  },
  routing: {
    defaultSystem: 'auto',
    costThreshold: 0.50,
    complexityThreshold: 0.70,
    enableHybrid: true
  },
  monitoring: {
    enableMetrics: true,
    logLevel: 'info',
    enableTracing: false
  }
};


