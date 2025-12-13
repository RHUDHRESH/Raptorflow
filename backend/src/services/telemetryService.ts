/**
 * Telemetry Service
 *
 * Tracks usage metrics, costs, and performance for LLM calls and agent executions.
 */

import { env } from '../config/env';
import { redisMemory } from './redisMemory';

export interface LLMUsageRecord {
  id: string;
  traceId: string;
  timestamp: string;
  agentName?: string;
  jobId?: string;
  userId?: string;
  provider: 'vertex' | 'openai';
  model: string;
  fallbackUsed: boolean;
  usage: {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
  };
  cost: number;
  latency: number;
  error?: string;
  metadata?: Record<string, any>;
}

export interface AgentExecutionRecord {
  id: string;
  agentName: string;
  jobId?: string;
  userId?: string;
  startTime: string;
  endTime: string;
  duration: number;
  success: boolean;
  error?: string;
  inputTokens?: number;
  outputTokens?: number;
  totalTokens?: number;
  cost: number;
  metadata?: Record<string, any>;
}

export interface CostSummary {
  period: string;
  totalCost: number;
  totalTokens: number;
  totalRequests: number;
  byProvider: Record<string, { cost: number; tokens: number; requests: number }>;
  byAgent: Record<string, { cost: number; tokens: number; requests: number }>;
  byUser: Record<string, { cost: number; tokens: number; requests: number }>;
}

class TelemetryService {
  private readonly redisPrefix = 'telemetry';

  /**
   * Log LLM usage
   */
  async logLLMUsage(record: LLMUsageRecord): Promise<void> {
    try {
      // Store in Redis for short-term analytics
      const key = `${this.redisPrefix}:llm:${record.id}`;
      await redisMemory.store(key, record, 86400 * 30); // 30 days

      // Index by various dimensions for quick queries
      const indices = [
        `${this.redisPrefix}:by_provider:${record.provider}:${record.id}`,
        `${this.redisPrefix}:by_agent:${record.agentName}:${record.id}`,
        `${this.redisPrefix}:by_user:${record.userId}:${record.id}`,
        `${this.redisPrefix}:by_day:${record.timestamp.slice(0, 10)}:${record.id}`,
      ];

      for (const indexKey of indices) {
        await redisMemory.store(indexKey, record.id, 86400 * 30);
      }

      console.log(`📊 Logged LLM usage: ${record.traceId} - ${record.cost.toFixed(4)} USD`);

      // TODO: Also store in database for long-term persistence
      // await this.storeLLMUsageInDB(record);

    } catch (error) {
      console.error('Failed to log LLM usage:', error);
    }
  }

  /**
   * Log agent execution
   */
  async logAgentExecution(record: AgentExecutionRecord): Promise<void> {
    try {
      // Store in Redis
      const key = `${this.redisPrefix}:agent:${record.id}`;
      await redisMemory.store(key, record, 86400 * 30);

      // Index for queries
      const indices = [
        `${this.redisPrefix}:agent_executions:${record.agentName}:${record.id}`,
        `${this.redisPrefix}:agent_by_user:${record.userId}:${record.id}`,
        `${this.redisPrefix}:agent_by_day:${record.startTime.slice(0, 10)}:${record.id}`,
      ];

      for (const indexKey of indices) {
        await redisMemory.store(indexKey, record.id, 86400 * 30);
      }

      console.log(`📊 Logged agent execution: ${record.agentName} - ${record.duration}ms - ${record.success ? 'SUCCESS' : 'FAILED'}`);

      // TODO: Store in database
      // await this.storeAgentExecutionInDB(record);

    } catch (error) {
      console.error('Failed to log agent execution:', error);
    }
  }

  /**
   * Get cost summary for a period
   */
  async getCostSummary(
    startDate: Date,
    endDate: Date,
    groupBy?: 'provider' | 'agent' | 'user'
  ): Promise<CostSummary> {
    const summary: CostSummary = {
      period: `${startDate.toISOString().slice(0, 10)} to ${endDate.toISOString().slice(0, 10)}`,
      totalCost: 0,
      totalTokens: 0,
      totalRequests: 0,
      byProvider: {},
      byAgent: {},
      byUser: {},
    };

    try {
      // Get all LLM usage records for the period
      // This is a simplified implementation - in production, you'd query the database
      const pattern = `${this.redisPrefix}:llm:*`;
      // Note: Redis doesn't have native pattern scanning in this SDK
      // You'd need to use a database query in production

      // For now, return mock data structure
      summary.byProvider = {
        vertex: { cost: 0, tokens: 0, requests: 0 },
        openai: { cost: 0, tokens: 0, requests: 0 },
      };

      summary.byAgent = {};
      summary.byUser = {};

    } catch (error) {
      console.error('Failed to get cost summary:', error);
    }

    return summary;
  }

  /**
   * Get usage statistics
   */
  async getUsageStats(timeRange: 'hour' | 'day' | 'week' | 'month' = 'day'): Promise<{
    totalRequests: number;
    totalTokens: number;
    totalCost: number;
    averageLatency: number;
    errorRate: number;
    topAgents: Array<{ agent: string; requests: number; cost: number }>;
    topUsers: Array<{ user: string; requests: number; cost: number }>;
  }> {
    // Simplified implementation - would query database in production
    return {
      totalRequests: 0,
      totalTokens: 0,
      totalCost: 0,
      averageLatency: 0,
      errorRate: 0,
      topAgents: [],
      topUsers: [],
    };
  }

  /**
   * Get agent performance metrics
   */
  async getAgentMetrics(agentName: string, days: number = 7): Promise<{
    totalExecutions: number;
    successRate: number;
    averageDuration: number;
    averageCost: number;
    errorCount: number;
    recentErrors: string[];
  }> {
    // Simplified implementation
    return {
      totalExecutions: 0,
      successRate: 0,
      averageDuration: 0,
      averageCost: 0,
      errorCount: 0,
      recentErrors: [],
    };
  }

  /**
   * Export telemetry data
   */
  async exportData(startDate: Date, endDate: Date, format: 'json' | 'csv' = 'json'): Promise<string> {
    // This would collect all telemetry data and format it for export
    const data = {
      llmUsage: [],
      agentExecutions: [],
      summary: await this.getCostSummary(startDate, endDate),
    };

    if (format === 'json') {
      return JSON.stringify(data, null, 2);
    } else {
      // Convert to CSV format
      return this.convertToCSV(data);
    }
  }

  /**
   * Clean up old telemetry data
   */
  async cleanupOldData(daysToKeep: number = 90): Promise<void> {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - daysToKeep);

    try {
      // In Redis, data expires automatically with TTL
      // In database, you'd run a cleanup query
      console.log(`🧹 Cleaned up telemetry data older than ${cutoffDate.toISOString()}`);
    } catch (error) {
      console.error('Failed to cleanup telemetry data:', error);
    }
  }

  /**
   * Get real-time metrics
   */
  async getRealtimeMetrics(): Promise<{
    activeJobs: number;
    queueDepth: number;
    currentCostPerHour: number;
    errorRateLastHour: number;
  }> {
    return {
      activeJobs: 0,
      queueDepth: 0,
      currentCostPerHour: 0,
      errorRateLastHour: 0,
    };
  }

  // =====================================================
  // PRIVATE METHODS
  // =====================================================

  private convertToCSV(data: any): string {
    // Simple CSV conversion - in production, use a proper CSV library
    const lines = ['Type,Timestamp,Agent,User,Cost,Duration,Success'];
    // Add LLM usage rows
    data.llmUsage?.forEach((record: LLMUsageRecord) => {
      lines.push(`LLM,${record.timestamp},${record.agentName},${record.userId},${record.cost},,`);
    });
    // Add agent execution rows
    data.agentExecutions?.forEach((record: AgentExecutionRecord) => {
      lines.push(`Agent,${record.startTime},${record.agentName},${record.userId},${record.cost},${record.duration},${record.success}`);
    });
    return lines.join('\n');
  }

  // Database storage methods (to be implemented when database is set up)
  /*
  private async storeLLMUsageInDB(record: LLMUsageRecord): Promise<void> {
    // Insert into llm_usage table
  }

  private async storeAgentExecutionInDB(record: AgentExecutionRecord): Promise<void> {
    // Insert into agent_executions table
  }
  */
}

// Export singleton instance
export const telemetryService = new TelemetryService();

// Export types
export type { LLMUsageRecord, AgentExecutionRecord, CostSummary };

