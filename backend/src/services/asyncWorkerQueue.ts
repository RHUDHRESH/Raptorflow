/**
 * Async Worker Queue Service - Cost-optimized async processing for LLM tasks
 *
 * Features:
 * - Priority-based job queuing
 * - Rate limiting and cost throttling
 * - Async result retrieval
 * - Circuit breaker for cost control
 * - Worker pool management
 */

import { sqsJobQueue } from './sqsJobQueue';
import { redisMemory } from './redisMemory';
import { llmService, CostAwareRequest } from './llmService';
import { responseCache } from './responseCacheService';

export interface AsyncLLMJob {
  jobId: string;
  request: CostAwareRequest;
  priority: 'low' | 'normal' | 'high' | 'urgent';
  queuedAt: number;
  estimatedCost: number;
  metadata?: {
    userId?: string;
    sessionId?: string;
    requestId?: string;
    timeout?: number; // seconds
  };
}

export interface JobResult {
  jobId: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'timeout';
  result?: any;
  error?: string;
  startedAt?: number;
  completedAt?: number;
  cost?: number;
  tokens?: number;
  processingTime?: number;
}

export interface QueueStats {
  activeJobs: number;
  pendingJobs: number;
  completedJobs: number;
  failedJobs: number;
  averageProcessingTime: number;
  averageCostPerJob: number;
  totalCostToday: number;
  rateLimitHits: number;
}

export interface RateLimitConfig {
  maxConcurrentJobs: number;
  maxJobsPerMinute: number;
  maxCostPerMinute: number;
  maxCostPerHour: number;
  circuitBreakerThreshold: number; // consecutive failures before opening circuit
}

class AsyncWorkerQueueService {
  private readonly JOB_PREFIX = 'async_job';
  private readonly RESULT_PREFIX = 'job_result';
  private readonly STATS_PREFIX = 'queue_stats';
  private readonly RATE_LIMIT_PREFIX = 'rate_limit';

  private config: RateLimitConfig = {
    maxConcurrentJobs: 3,
    maxJobsPerMinute: 10,
    maxCostPerMinute: 0.50, // $0.50 per minute
    maxCostPerHour: 5.00,   // $5.00 per hour
    circuitBreakerThreshold: 5
  };

  private activeJobs = new Set<string>();
  private circuitBreakerOpen = false;
  private consecutiveFailures = 0;

  constructor() {
    this.startWorkerPool();
    this.loadConfig();
  }

  /**
   * Queue an LLM job for async processing
   */
  async queueLLMJob(request: CostAwareRequest, priority: AsyncLLMJob['priority'] = 'normal'): Promise<string> {
    // Check rate limits
    if (!(await this.checkRateLimits(request))) {
      throw new Error('Rate limit exceeded. Please try again later.');
    }

    // Check circuit breaker
    if (this.circuitBreakerOpen) {
      throw new Error('Service temporarily unavailable due to high error rate.');
    }

    const jobId = `${this.JOB_PREFIX}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    // Estimate cost for the request
    const budgetCheck = await llmService.checkBudget(request);
    const estimatedCost = budgetCheck.estimatedCost;

    const job: AsyncLLMJob = {
      jobId,
      request,
      priority,
      queuedAt: Date.now(),
      estimatedCost
    };

    // Store job metadata in Redis
    await redisMemory.store(`${this.JOB_PREFIX}:${jobId}`, JSON.stringify(job), 3600); // 1 hour TTL

    // Create initial result record
    const initialResult: JobResult = {
      jobId,
      status: 'pending'
    };
    await this.storeJobResult(jobId, initialResult);

    // Queue for processing (use SQS with priority)
    await this.queueForProcessing(job);

    console.log(`📋 Queued async job ${jobId}: ${request.agentName || 'unknown'} (est. cost: $${estimatedCost.toFixed(4)})`);

    return jobId;
  }

  /**
   * Get job result
   */
  async getJobResult(jobId: string): Promise<JobResult | null> {
    const resultKey = `${this.RESULT_PREFIX}:${jobId}`;
    const cached = await redisMemory.get(resultKey);

    if (cached) {
      return JSON.parse(cached);
    }

    return null;
  }

  /**
   * Get queue statistics
   */
  async getQueueStats(): Promise<QueueStats> {
    // Get stats from Redis (would be aggregated in production)
    const stats: QueueStats = {
      activeJobs: this.activeJobs.size,
      pendingJobs: 0, // Would count from Redis/queue
      completedJobs: 0,
      failedJobs: 0,
      averageProcessingTime: 0,
      averageCostPerJob: 0,
      totalCostToday: 0,
      rateLimitHits: 0
    };

    // Load from Redis if available
    const savedStats = await redisMemory.get(`${this.STATS_PREFIX}:current`);
    if (savedStats) {
      Object.assign(stats, JSON.parse(savedStats));
    }

    return stats;
  }

  /**
   * Update rate limit configuration
   */
  async updateRateLimits(newConfig: Partial<RateLimitConfig>): Promise<void> {
    this.config = { ...this.config, ...newConfig };
    await redisMemory.store('async_worker_config', JSON.stringify(this.config), 86400);
    console.log('Async worker rate limits updated:', this.config);
  }

  /**
   * Cancel a job
   */
  async cancelJob(jobId: string): Promise<boolean> {
    const jobKey = `${this.JOB_PREFIX}:${jobId}`;
    const jobData = await redisMemory.get(jobKey);

    if (!jobData) {
      return false;
    }

    // Remove from active jobs if processing
    this.activeJobs.delete(jobId);

    // Update result status
    const result: JobResult = {
      jobId,
      status: 'failed',
      error: 'Job cancelled by user'
    };
    await this.storeJobResult(jobId, result);

    // Remove job data
    await redisMemory.delete(jobKey);

    console.log(`❌ Cancelled job ${jobId}`);
    return true;
  }

  // ===== PRIVATE METHODS =====

  private async checkRateLimits(request: CostAwareRequest): Promise<boolean> {
    const now = Date.now();
    const minuteKey = `${this.RATE_LIMIT_PREFIX}:minute:${Math.floor(now / 60000)}`;
    const hourKey = `${this.RATE_LIMIT_PREFIX}:hour:${Math.floor(now / 3600000)}`;

    // Get current usage
    const minuteUsage = JSON.parse(await redisMemory.get(minuteKey) || '{"jobs": 0, "cost": 0}');
    const hourUsage = JSON.parse(await redisMemory.get(hourKey) || '{"jobs": 0, "cost": 0}');

    // Estimate request cost
    const budgetCheck = await llmService.checkBudget(request);
    const requestCost = budgetCheck.estimatedCost;

    // Check limits
    if (minuteUsage.jobs >= this.config.maxJobsPerMinute) {
      console.warn('Rate limit: max jobs per minute exceeded');
      await this.incrementRateLimitHits();
      return false;
    }

    if (minuteUsage.cost + requestCost > this.config.maxCostPerMinute) {
      console.warn('Rate limit: max cost per minute exceeded');
      await this.incrementRateLimitHits();
      return false;
    }

    if (hourUsage.cost + requestCost > this.config.maxCostPerHour) {
      console.warn('Rate limit: max cost per hour exceeded');
      await this.incrementRateLimitHits();
      return false;
    }

    if (this.activeJobs.size >= this.config.maxConcurrentJobs) {
      console.warn('Rate limit: max concurrent jobs exceeded');
      return false;
    }

    return true;
  }

  private async incrementRateLimitHits(): Promise<void> {
    const stats = await this.getQueueStats();
    stats.rateLimitHits++;
    await redisMemory.store(`${this.STATS_PREFIX}:current`, JSON.stringify(stats), 86400);
  }

  private async queueForProcessing(job: AsyncLLMJob): Promise<void> {
    // Use SQS for reliable queuing
    try {
      await sqsJobQueue.sendJob({
        jobId: job.jobId,
        agentName: 'AsyncLLMWorker', // Special agent for async processing
        input: job,
        priority: this.priorityToNumber(job.priority),
        contextSnapshot: {
          job,
          queuedAt: job.queuedAt
        },
        queuedAt: new Date(job.queuedAt).toISOString()
      });
    } catch (error) {
      console.error('Failed to queue job for processing:', error);
      throw error;
    }
  }

  private priorityToNumber(priority: AsyncLLMJob['priority']): number {
    const mapping = { low: 1, normal: 2, high: 3, urgent: 4 };
    return mapping[priority] || 2;
  }

  private async processJob(job: AsyncLLMJob): Promise<void> {
    const startTime = Date.now();
    this.activeJobs.add(job.jobId);

    // Update status to processing
    const processingResult: JobResult = {
      jobId: job.jobId,
      status: 'processing',
      startedAt: startTime
    };
    await this.storeJobResult(job.jobId, processingResult);

    try {
      console.log(`⚙️ Processing async job ${job.jobId}`);

      // Process the LLM request
      const response = await llmService.generate(job.request);

      // Create success result
      const completedResult: JobResult = {
        jobId: job.jobId,
        status: 'completed',
        result: response,
        startedAt: startTime,
        completedAt: Date.now(),
        cost: response.cost,
        tokens: response.usage.totalTokens,
        processingTime: Date.now() - startTime
      };

      await this.storeJobResult(job.jobId, completedResult);

      // Reset circuit breaker on success
      this.consecutiveFailures = 0;
      this.circuitBreakerOpen = false;

      // Update statistics
      await this.updateJobStats(completedResult);

      console.log(`✅ Async job ${job.jobId} completed: ${response.usage.totalTokens} tokens, $${response.cost.toFixed(4)}`);

    } catch (error) {
      console.error(`❌ Async job ${job.jobId} failed:`, error);

      // Update failure result
      const failedResult: JobResult = {
        jobId: job.jobId,
        status: 'failed',
        error: error instanceof Error ? error.message : 'Unknown error',
        startedAt: startTime,
        completedAt: Date.now(),
        processingTime: Date.now() - startTime
      };

      await this.storeJobResult(job.jobId, failedResult);

      // Circuit breaker logic
      this.consecutiveFailures++;
      if (this.consecutiveFailures >= this.config.circuitBreakerThreshold) {
        this.circuitBreakerOpen = true;
        console.warn('🚨 Circuit breaker opened due to consecutive failures');
      }

    } finally {
      this.activeJobs.delete(job.jobId);
    }
  }

  private async storeJobResult(jobId: string, result: JobResult): Promise<void> {
    const resultKey = `${this.RESULT_PREFIX}:${jobId}`;
    await redisMemory.store(resultKey, JSON.stringify(result), 86400); // 24 hours TTL
  }

  private async updateJobStats(result: JobResult): Promise<void> {
    const stats = await this.getQueueStats();

    if (result.status === 'completed') {
      stats.completedJobs++;
      stats.averageProcessingTime = (
        (stats.averageProcessingTime * (stats.completedJobs - 1)) + (result.processingTime || 0)
      ) / stats.completedJobs;

      if (result.cost) {
        stats.averageCostPerJob = (
          (stats.averageCostPerJob * (stats.completedJobs - 1)) + result.cost
        ) / stats.completedJobs;

        // Track daily cost
        const today = new Date().toISOString().slice(0, 10);
        const dailyCostKey = `${this.STATS_PREFIX}:daily_cost:${today}`;
        const currentDailyCost = parseFloat(await redisMemory.get(dailyCostKey) || '0');
        await redisMemory.store(dailyCostKey, (currentDailyCost + result.cost).toString(), 86400 * 7);
        stats.totalCostToday = currentDailyCost + result.cost;
      }
    } else if (result.status === 'failed') {
      stats.failedJobs++;
    }

    await redisMemory.store(`${this.STATS_PREFIX}:current`, JSON.stringify(stats), 86400);
  }

  private async loadConfig(): Promise<void> {
    try {
      const savedConfig = await redisMemory.get('async_worker_config');
      if (savedConfig) {
        this.config = { ...this.config, ...JSON.parse(savedConfig) };
      }
    } catch (error) {
      console.warn('Failed to load async worker config:', error);
    }
  }

  private startWorkerPool(): void {
    // Start background job processor
    setInterval(async () => {
      try {
        if (!this.circuitBreakerOpen && this.activeJobs.size < this.config.maxConcurrentJobs) {
          await this.processPendingJobs();
        }
      } catch (error) {
        console.error('Worker pool error:', error);
      }
    }, 5000); // Check every 5 seconds

    console.log('Async worker pool started with config:', this.config);
  }

  private async processPendingJobs(): Promise<void> {
    // Poll SQS for pending jobs (simplified - would integrate with sqsJobQueue)
    // This is a placeholder for the actual job polling logic
    // In production, this would receive messages from SQS and process them
  }
}

// Export singleton instance
export const asyncWorkerQueue = new AsyncWorkerQueueService();

// Export types
export type { AsyncLLMJob, JobResult, QueueStats, RateLimitConfig };


