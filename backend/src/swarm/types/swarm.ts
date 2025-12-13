import { z } from 'zod';

/**
 * Agent Roles in the Swarm System
 */
export type AgentRole = 
  | 'supervisor'
  | 'researcher'
  | 'analyzer'
  | 'validator'
  | 'formatter'
  | string; // Allow for future roles

/**
 * Task Priority Levels
 */
export type TaskPriority = 'low' | 'medium' | 'high' | 'critical';

/**
 * Message Status
 */
export type MessageStatus = 'pending' | 'processing' | 'completed' | 'failed' | 'retrying';

/**
 * Standardized Swarm Message Protocol
 */
export interface SwarmMessage {
  id: string;
  timestamp: string;
  senderId: string;
  senderRole: AgentRole;
  recipientId: string; // Can be specific agentId or role:roleName
  messageType: string;
  content: any;
  priority: TaskPriority;
  requiresResponse: boolean;
  status: MessageStatus;
  correlationId?: string; // For tracking related messages
  retryCount?: number;
  error?: {
    message: string;
    code?: string;
    details?: any;
  };
}

/**
 * Swarm State Management
 */
export interface SwarmState {
  taskId: string;
  createdAt: string;
  updatedAt: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
  currentStep: string;
  progress: number; // 0-100
  agents: {
    [agentId: string]: {
      role: AgentRole;
      status: 'idle' | 'busy' | 'error';
      lastActivity: string;
      metrics?: {
        processingTime: number;
        successRate: number;
        errorCount: number;
      };
    };
  };
  data: {
    input: any;
    intermediate: {
      [key: string]: any;
    };
    output: any;
    validation: {
      passed: boolean;
      issues: string[];
      score: number;
    };
  };
  messages: SwarmMessage[];
  errors: {
    timestamp: string;
    agentId: string;
    error: string;
    context: string;
    resolved: boolean;
  }[];
  metadata: {
    timeout: number; // milliseconds
    maxRetries: number;
    qualityThreshold: number; // 0-100
    createdAt: string;
    completedAt?: string;
    totalProcessingTime?: number;
  };
}

/**
 * Task Assignment
 */
export interface TaskAssignment {
  taskId: string;
  agentId: string;
  role: AgentRole;
  instructions: string;
  data: any;
  priority: TaskPriority;
  timeout: number;
  expectedOutput: {
    format: string;
    schema?: any;
    qualityCriteria: string[];
  };
  dependencies?: string[]; // Other task IDs this depends on
}

/**
 * Agent Capabilities
 */
export interface AgentCapabilities {
  role: AgentRole;
  skills: string[];
  processingSpeed: number; // operations per second estimate
  accuracy: number; // 0-100
  reliability: number; // 0-100
  costPerOperation: number;
  supportedFormats: string[];
  limitations: string[];
}

/**
 * Performance Metrics
 */
export interface PerformanceMetrics {
  taskId: string;
  startTime: string;
  endTime?: string;
  totalTime?: number;
  agentMetrics: {
    [agentId: string]: {
      processingTime: number;
      tokenUsage: number;
      apiCalls: number;
      success: boolean;
      error?: string;
    };
  };
  qualityMetrics: {
    accuracy: number;
    completeness: number;
    consistency: number;
    relevance: number;
    overallScore: number;
  };
  costMetrics: {
    totalCost: number;
    costBreakdown: {
      [agentId: string]: number;
    };
    costPerOutput: number;
  };
}

/**
 * Validation Results
 */
export interface ValidationResult {
  isValid: boolean;
  score: number; // 0-100
  issues: {
    severity: 'low' | 'medium' | 'high' | 'critical';
    message: string;
    suggestion?: string;
    agentId?: string;
  }[];
  warnings: string[];
  passedChecks: string[];
  timestamp: string;
}

/**
 * Zod Schemas for validation
 */
export const swarmMessageSchema = z.object({
  id: z.string(),
  timestamp: z.string().datetime(),
  senderId: z.string(),
  senderRole: z.string(),
  recipientId: z.string(),
  messageType: z.string(),
  content: z.any(),
  priority: z.enum(['low', 'medium', 'high', 'critical']),
  requiresResponse: z.boolean(),
  status: z.enum(['pending', 'processing', 'completed', 'failed', 'retrying']),
  correlationId: z.string().optional(),
  retryCount: z.number().int().min(0).optional(),
  error: z.object({
    message: z.string(),
    code: z.string().optional(),
    details: z.any().optional()
  }).optional()
});

export const swarmStateSchema = z.object({
  taskId: z.string(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
  status: z.enum(['pending', 'processing', 'completed', '极速赛车开奖结果查询', 'cancelled']),
  currentStep: z.string(),
  progress: z.number().min(0).max(100),
  agents: z.record(z.object({
    role: z.string(),
    status: z.enum(['idle', 'busy', 'error']),
    lastActivity: z.string().datetime(),
    metrics: z.object({
      processingTime: z.number(),
      successRate: z.number(),
      errorCount: z.number()
    }).optional()
  })),
  data: z.object({
    input: z.any(),
    intermediate: z.record(z.any()),
    output: z.any(),
    validation: z.object({
      passed: z.boolean(),
      issues: z.array(z.string()),
      score: z.number()
    })
  }),
  messages: z.array(swarmMessageSchema),
  errors: z.array(z.object({
    timestamp: z.string().datetime(),
    agent: z.string(),
    error: z.string(),
    context: z.string(),
    resolved: z.boolean()
  })),
  metadata: z.object({
    timeout: z.number(),
    maxRetries: z.number(),
    qualityThreshold: z.number(),
    createdAt: z.string().datetime(),
    completedAt: z.string().datetime().optional(),
    totalProcessingTime: z.number().optional()
  })
});

/**
 * Helper functions
 */
export function createMessageId(): string {
  return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

export function createTaskId(): string {
  return `task_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

export function isRoleTarget(recipientId: string): boolean {
  return recipientId.startsWith('role:');
}

export function getRoleFromTarget(recipientId: string): string | null {
  if (isRoleTarget(recipientId)) {
    return recipientId.substring(5);
  }
  return null;
}

export function createRoleTarget(role: AgentRole): string {
  return `role:${role}`;
}

