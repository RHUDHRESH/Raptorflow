/**
 * Enhanced LLM Service - Cost-Optimized Centralized Client
 *
 * Features:
 * - Cost-aware model selection with budget constraints
 * - Automatic model fallback based on cost/performance tradeoffs
 * - Token usage tracking and hard limits
 * - Response caching integration
 * - Request batching capabilities
 * - Circuit breaker for cost control
 */

import { llmAdapter, LLMRequest, LLMResponse } from '../v2/llm/adapter';
import { redisMemory } from './redisMemory';
import { telemetryService } from './telemetryService';
import { responseCache } from './responseCacheService';
import { batchProcessor } from './batchProcessorService';
import { promptEngineering } from './promptEngineeringService';
import { env } from '../config/env';

export interface CostAwareRequest extends LLMRequest {
  maxCost?: number; // Maximum cost in USD for this request
  priority?: 'speed' | 'cost' | 'balanced';
  cacheKey?: string; // For response caching
  allowFallback?: boolean;
  enableBatching?: boolean; // Whether to enable batching for this request
  batchPriority?: number; // Priority for batch processing (1-5)
}

export interface BatchRequest extends CostAwareRequest {
  batchId: string;
  batchSize: number;
}

export interface CostMetrics {
  totalCost: number;
  totalTokens: number;
  requestsCount: number;
  averageCostPerRequest: number;
  cacheHitRate: number;
  modelUsage: Record<string, { requests: number; cost: number }>;
}

class LLMService {
  private readonly COST_THRESHOLDS = {
    LOW: 0.01,      // <$0.01 per request (simple tasks)
    MEDIUM: 0.05,   // <$0.05 per request (general tasks)
    HIGH: 0.15      // <$0.15 per request (complex tasks)
  };

  private readonly TOKEN_LIMITS = {
    SOFT: 10000,    // Soft limit - prefer cheaper models
    HARD: 25000     // Hard limit - reject requests
  };

  // Daily budget caps to prevent runaway costs
  private readonly BUDGET_LIMITS = {
    DAILY_MAX_USD: parseFloat(env.LLM_DAILY_BUDGET_USD || '50'),
    PER_USER_DAILY_USD: parseFloat(env.LLM_PER_USER_DAILY_USD || '5'),
    ALERT_THRESHOLD_PERCENT: 80 // Alert when 80% of budget used
  };

  private costMetrics: CostMetrics = {
    totalCost: 0,
    totalTokens: 0,
    requestsCount: 0,
    averageCostPerRequest: 0,
    cacheHitRate: 0,
    modelUsage: {}
  };

  /**
   * Generate completion with cost optimization
   */
  async generate(request: CostAwareRequest): Promise<LLMResponse> {
    const startTime = Date.now();
    const traceId = `llm_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    console.log(`🔄 [${traceId}] Cost-aware LLM request: ${request.agentName || 'unknown'}`);

    // Check daily budget limits FIRST
    const budgetCheck = await this.checkDailyBudget(request.userId);
    if (!budgetCheck.allowed) {
      console.error(`🚫 [${traceId}] Daily budget exceeded: ${budgetCheck.reason}`);
      throw new Error(`Daily AI budget exceeded: ${budgetCheck.reason}. Try again tomorrow or contact support.`);
    }

    // Alert if approaching budget limit
    if (budgetCheck.usedPercent >= this.BUDGET_LIMITS.ALERT_THRESHOLD_PERCENT) {
      console.warn(`⚠️ [${traceId}] Budget alert: ${budgetCheck.usedPercent.toFixed(1)}% of daily budget used`);
    }

    // Check token limits
    if (request.maxTokens && request.maxTokens > this.TOKEN_LIMITS.HARD) {
      throw new Error(`Token limit exceeded: ${request.maxTokens} > ${this.TOKEN_LIMITS.HARD}`);
    }

    // Try cache first
    if (request.cacheKey) {
      try {
        const cached = await responseCache.getOrSet(
          request.cacheKey,
          async () => null, // Will never be called due to TTL check
          { ttl: 3600 } // 1 hour TTL for LLM responses
        );

        if (cached) {
          console.log(`✅ [${traceId}] Cache hit for ${request.cacheKey}`);
          await this.updateMetrics({ ...cached, latency: Date.now() - startTime }, request, true);
          return cached;
        }
      } catch (error) {
        console.warn(`Cache check failed for ${request.cacheKey}:`, error);
      }
    }

    // Check if batching is enabled and appropriate
    if (request.enableBatching && this.shouldUseBatching(request)) {
      console.log(`📦 [${traceId}] Using batch processing`);
      return this.processViaBatch(request, traceId);
    }

    // Optimize model selection based on cost constraints
    const optimizedRequest = await this.optimizeRequest(request);

    // Execute with cost control
    const response = await this.executeWithCostControl(optimizedRequest, traceId);

    // Cache response if cache key provided
    if (request.cacheKey) {
      try {
        await responseCache.set(request.cacheKey, response, {
          ttl: 3600, // 1 hour TTL for LLM responses
          metadata: {
            agentName: request.agentName,
            model: response.model,
            cost: response.cost,
            tokens: response.usage.totalTokens
          }
        });
      } catch (error) {
        console.warn(`Cache write failed for ${request.cacheKey}:`, error);
      }
    }

    // Update metrics
    await this.updateMetrics(response, request, false);

    console.log(`✅ [${traceId}] Cost-optimized completion: ${response.cost.toFixed(4)} USD`);
    return response;
  }

  /**
   * Batch multiple requests for efficiency
   */
  async generateBatch(requests: BatchRequest[]): Promise<LLMResponse[]> {
    if (requests.length === 0) return [];

    const batchId = requests[0].batchId;
    console.log(`🔄 Batch processing ${requests.length} requests: ${batchId}`);

    // Group by model and priority for efficient batching
    const grouped = this.groupRequestsByModel(requests);

    const results: LLMResponse[] = [];

    // Process groups in parallel
    const promises = Object.entries(grouped).map(async ([modelKey, groupRequests]) => {
      // For now, process sequentially but could be optimized further
      const groupResults = [];
      for (const request of groupRequests) {
        try {
          const result = await this.generate(request);
          groupResults.push(result);
        } catch (error) {
          console.error(`Batch request failed:`, error);
          // Continue with other requests
        }
      }
      return groupResults;
    });

    const batchResults = await Promise.all(promises);
    return batchResults.flat();
  }

  /**
   * Get cost metrics and analytics
   */
  async getCostMetrics(hours: number = 24): Promise<CostMetrics> {
    // Get recent metrics from Redis/cache
    const cacheKey = `llm_metrics:${hours}h`;
    const cached = await redisMemory.get(cacheKey);

    if (cached) {
      return JSON.parse(cached);
    }

    // Aggregate from telemetry service
    const metrics = await this.aggregateMetrics(hours);
    await redisMemory.store(cacheKey, JSON.stringify(metrics), 3600); // Cache for 1 hour

    return metrics;
  }

  /**
   * Check if request would exceed budget
   */
  async checkBudget(request: CostAwareRequest): Promise<{
    withinBudget: boolean;
    estimatedCost: number;
    recommendedModel: string;
  }> {
    const estimatedCost = await this.estimateCost(request);
    const withinBudget = !request.maxCost || estimatedCost <= request.maxCost;

    const recommendedModel = this.selectOptimalModel(request, estimatedCost);

    return {
      withinBudget,
      estimatedCost,
      recommendedModel
    };
  }

  // ===== PRIVATE METHODS =====

  /**
   * Check if daily budget allows this request
   */
  private async checkDailyBudget(userId?: string): Promise<{
    allowed: boolean;
    reason?: string;
    usedPercent: number;
    dailySpent: number;
    userSpent: number;
  }> {
    const today = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
    const dailyKey = `llm_daily_cost:${today}`;
    const userKey = userId ? `llm_user_cost:${today}:${userId}` : null;

    try {
      // Get daily total spent
      const dailySpentStr = await redisMemory.get(dailyKey);
      const dailySpent = dailySpentStr ? parseFloat(dailySpentStr) : 0;

      // Get user-specific spent (if userId provided)
      let userSpent = 0;
      if (userKey) {
        const userSpentStr = await redisMemory.get(userKey);
        userSpent = userSpentStr ? parseFloat(userSpentStr) : 0;
      }

      // Check global daily limit
      if (dailySpent >= this.BUDGET_LIMITS.DAILY_MAX_USD) {
        return {
          allowed: false,
          reason: `Global daily limit of $${this.BUDGET_LIMITS.DAILY_MAX_USD} reached`,
          usedPercent: 100,
          dailySpent,
          userSpent
        };
      }

      // Check per-user daily limit
      if (userId && userSpent >= this.BUDGET_LIMITS.PER_USER_DAILY_USD) {
        return {
          allowed: false,
          reason: `Your daily limit of $${this.BUDGET_LIMITS.PER_USER_DAILY_USD} reached`,
          usedPercent: (userSpent / this.BUDGET_LIMITS.PER_USER_DAILY_USD) * 100,
          dailySpent,
          userSpent
        };
      }

      return {
        allowed: true,
        usedPercent: (dailySpent / this.BUDGET_LIMITS.DAILY_MAX_USD) * 100,
        dailySpent,
        userSpent
      };
    } catch (error) {
      console.warn('Budget check failed, allowing request:', error);
      return { allowed: true, usedPercent: 0, dailySpent: 0, userSpent: 0 };
    }
  }

  /**
   * Track spending for budget limits
   */
  private async trackSpending(cost: number, userId?: string): Promise<void> {
    const today = new Date().toISOString().split('T')[0];
    const dailyKey = `llm_daily_cost:${today}`;
    const userKey = userId ? `llm_user_cost:${today}:${userId}` : null;
    const ttl = 86400; // 24 hours

    try {
      // Increment daily total
      const dailyStr = await redisMemory.get(dailyKey);
      const daily = dailyStr ? parseFloat(dailyStr) : 0;
      await redisMemory.store(dailyKey, (daily + cost).toString(), ttl);

      // Increment user total
      if (userKey) {
        const userStr = await redisMemory.get(userKey);
        const user = userStr ? parseFloat(userStr) : 0;
        await redisMemory.store(userKey, (user + cost).toString(), ttl);
      }
    } catch (error) {
      console.warn('Failed to track spending:', error);
    }
  }

  private shouldUseBatching(request: CostAwareRequest): boolean {
    // Don't batch if priority is speed
    if (request.priority === 'speed') return false;

    // Don't batch if maxTokens is very high (complex requests)
    if (request.maxTokens && request.maxTokens > this.TOKEN_LIMITS.SOFT) return false;

    // Batch simple, repetitive tasks
    return request.priority === 'cost' || request.agentName?.includes('Simple') || false;
  }

  private recalculateCost(response: LLMResponse, optimization: any): number {
    // Recalculate cost based on optimized token usage
    const model = response.model;
    if (model.includes('vertex') || model.includes('gemini')) {
      return this.calculateVertexCost(response.usage.totalTokens);
    } else if (model.includes('openai') || model.includes('gpt')) {
      return this.calculateOpenAICost(response.usage.totalTokens, model);
    }
    return response.cost; // Fallback to original cost
  }

  private async processViaBatch(request: CostAwareRequest, traceId: string): Promise<LLMResponse> {
    try {
      // Queue request for batch processing
      const batchRequestId = await batchProcessor.queueRequest(request, request.batchPriority || 1);

      // Wait for result (with timeout)
      const maxWaitTime = 10000; // 10 seconds
      const startWait = Date.now();

      while (Date.now() - startWait < maxWaitTime) {
        const result = await batchProcessor.getBatchResult(batchRequestId);
        if (result) {
          if (result.error) {
            throw new Error(result.error);
          }
          console.log(`✅ [${traceId}] Batch result received: ${result.processingTime}ms`);
          return result.result;
        }

        // Wait a bit before checking again
        await new Promise(resolve => setTimeout(resolve, 500));
      }

      // Timeout - fall back to immediate processing
      console.warn(`⏰ [${traceId}] Batch timeout, falling back to immediate processing`);
      return this.executeWithCostControl(await this.optimizeRequest(request), traceId);

    } catch (error) {
      console.error(`❌ [${traceId}] Batch processing failed:`, error);
      // Fall back to immediate processing
      return this.executeWithCostControl(await this.optimizeRequest(request), traceId);
    }
  }

  private async optimizeRequest(request: CostAwareRequest): Promise<LLMRequest> {
    // Start with original request
    let optimized = { ...request };

    // Adjust model based on priority and cost constraints
    if (request.priority === 'cost' || (request.maxCost && request.maxCost < this.COST_THRESHOLDS.MEDIUM)) {
      // Force cheaper model
      optimized.model = 'gemini-1.5-flash';
      optimized.temperature = Math.min(optimized.temperature || 0.3, 0.2); // Lower temperature for cost
    } else if (request.priority === 'speed' || !request.maxCost) {
      // Keep expensive model for speed
      optimized.model = request.model; // Use requested or default expensive model
    }

    // Adjust token limits for cost control
    if (request.maxTokens && request.maxTokens > this.TOKEN_LIMITS.SOFT) {
      optimized.maxTokens = Math.min(request.maxTokens, this.TOKEN_LIMITS.SOFT);
    }

    return optimized;
  }

  private selectOptimalModel(request: CostAwareRequest, estimatedCost: number): string {
    if (request.maxCost && estimatedCost > request.maxCost) {
      // Need cheaper model
      return 'gemini-1.5-flash';
    }

    if (request.priority === 'cost') {
      return 'gemini-1.5-flash';
    }

    if (request.priority === 'speed') {
      return 'gemini-2.5-pro-preview-06-05';
    }

    // Balanced - use current model
    return request.model || 'gemini-2.5-flash-preview-05-20';
  }

  private async executeWithCostControl(request: LLMRequest, traceId: string): Promise<LLMResponse> {
    try {
      // Optimize prompt if it's text-based
      let finalRequest = request;
      let optimizationResult = null;

      if (request.messages && request.messages.length > 0) {
        const combinedPrompt = request.messages.map(m => m.content).join(' ');

        // Only optimize if prompt is long enough to benefit
        if (combinedPrompt.length > 500) {
          optimizationResult = await promptEngineering.optimizePrompt(combinedPrompt, {
            maxTokens: request.maxTokens || 4000,
            category: request.agentName ? 'agent' : 'general',
            aggressive: false, // Conservative optimization by default
            preserveStructure: true
          });

          if (optimizationResult.compressionRatio < 0.9) { // Only use if significant savings
            console.log(`📝 [${traceId}] Optimized prompt: ${optimizationResult.originalTokens} → ${optimizationResult.optimizedTokens} tokens (${(optimizationResult.compressionRatio * 100).toFixed(1)}%)`);

            finalRequest = {
              ...request,
              messages: [{
                role: 'user',
                content: optimizationResult.optimizedPrompt
              }]
            };
          }
        }
      }

      const response = await llmAdapter.generate({
        ...finalRequest,
        jobId: request.jobId || traceId,
        userId: request.userId || 'system'
      });

      // Adjust token counts if prompt was optimized
      if (optimizationResult) {
        response.usage.promptTokens = optimizationResult.optimizedTokens;
        response.cost = this.recalculateCost(response, optimizationResult);
      }

      // Check if response exceeded cost budget
      if (request.maxCost && response.cost > request.maxCost) {
        console.warn(`⚠️ [${traceId}] Response cost ${response.cost} exceeded budget ${request.maxCost}`);

        // Could implement fallback to cheaper model here
        // For now, just log the warning
      }

      return response;
    } catch (error) {
      console.error(`❌ [${traceId}] LLM request failed:`, error);
      throw error;
    }
  }

  private groupRequestsByModel(requests: BatchRequest[]): Record<string, CostAwareRequest[]> {
    const groups: Record<string, CostAwareRequest[]> = {};

    for (const request of requests) {
      const modelKey = request.model || 'default';
      if (!groups[modelKey]) {
        groups[modelKey] = [];
      }
      groups[modelKey].push(request);
    }

    return groups;
  }

  private async estimateCost(request: CostAwareRequest): Promise<number> {
    // Rough estimation based on model and expected token usage
    const model = request.model || 'gemini-2.5-flash-preview-05-20';
    const estimatedTokens = request.maxTokens || 1000;

    // Very rough cost estimation
    const costPerThousandTokens = model.includes('flash') ? 0.0003 : 0.0015;
    return (estimatedTokens / 1000) * costPerThousandTokens;
  }

  private async updateMetrics(
    response: LLMResponse,
    request: CostAwareRequest,
    fromCache: boolean
  ): Promise<void> {
    try {
      // Track spending for budget limits (skip if from cache - no cost)
      if (!fromCache && response.cost > 0) {
        await this.trackSpending(response.cost, request.userId);
      }

      // Update in-memory metrics
      this.costMetrics.totalCost += response.cost;
      this.costMetrics.totalTokens += response.usage.totalTokens;
      this.costMetrics.requestsCount += 1;
      this.costMetrics.averageCostPerRequest = this.costMetrics.totalCost / this.costMetrics.requestsCount;

      // Track model usage
      const modelKey = response.model;
      if (!this.costMetrics.modelUsage[modelKey]) {
        this.costMetrics.modelUsage[modelKey] = { requests: 0, cost: 0 };
      }
      this.costMetrics.modelUsage[modelKey].requests += 1;
      this.costMetrics.modelUsage[modelKey].cost += response.cost;

      // Store in Redis for persistence
      await redisMemory.store(
        'llm_cost_metrics',
        JSON.stringify(this.costMetrics),
        86400 // 24 hours
      );

    } catch (error) {
      console.warn('Metrics update failed:', error);
    }
  }

  private async aggregateMetrics(hours: number): Promise<CostMetrics> {
    // In a real implementation, this would query the telemetry service
    // For now, return cached metrics
    return this.costMetrics;
  }
}

// Export singleton instance
export const llmService = new LLMService();

// Export types
export type { CostAwareRequest, BatchRequest, CostMetrics };
