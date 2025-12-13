/**
 * Comprehensive Monitoring Service - Cost and Performance Metrics
 *
 * Aggregates metrics from all optimization services:
 * - LLM usage and costs
 * - Cache performance
 * - Batch processing stats
 * - Prompt optimization metrics
 * - Infrastructure costs
 * - Async worker queue performance
 */

import { getLLMCostMetrics } from '../lib/llm';
import { responseCache } from './responseCacheService';
import { batchProcessor } from './batchProcessorService';
import { promptEngineering } from './promptEngineeringService';
import { asyncWorkerQueue } from './asyncWorkerQueue';
import { redisMemory } from './redisMemory';

export interface SystemMetrics {
  timestamp: string;
  period: string; // '1h', '24h', '7d'

  // LLM Metrics
  llm: {
    totalRequests: number;
    totalTokens: number;
    totalCost: number;
    averageCostPerRequest: number;
    cacheHitRate: number;
    modelUsage: Record<string, { requests: number; cost: number }>;
    fallbackRate: number;
  };

  // Cache Metrics
  cache: {
    totalRequests: number;
    cacheHits: number;
    cacheMisses: number;
    hitRate: number;
    totalSize: number;
    entriesCount: number;
    averageEntrySize: number;
  };

  // Batch Processing Metrics
  batch: {
    totalBatchesProcessed: number;
    totalRequestsProcessed: number;
    averageBatchSize: number;
    averageProcessingTime: number;
    deduplicationRate: number;
    costSavings: number;
  };

  // Prompt Optimization Metrics
  prompt: {
    totalPromptsProcessed: number;
    totalTokensSaved: number;
    averageCompressionRatio: number;
    costSavings: number;
    optimizationTechniques: Record<string, number>;
  };

  // Async Worker Queue Metrics
  worker: {
    activeJobs: number;
    pendingJobs: number;
    completedJobs: number;
    failedJobs: number;
    averageProcessingTime: number;
    averageCostPerJob: number;
    totalCostToday: number;
    rateLimitHits: number;
    queueHealth: 'healthy' | 'degraded' | 'critical';
  };

  // Infrastructure Costs (estimated)
  infrastructure: {
    estimatedMonthlyCost: number;
    breakdown: {
      compute: number;
      database: number;
      cache: number;
      storage: number;
      networking: number;
    };
    optimizationSavings: number;
  };

  // Overall Cost Metrics
  costs: {
    totalCostLast24h: number;
    averageCostPerRequest: number;
    costReductionPercentage: number;
    projectedMonthlyCost: number;
    costEfficiency: 'excellent' | 'good' | 'fair' | 'poor';
  };

  // Performance Metrics
  performance: {
    averageResponseTime: number;
    p95ResponseTime: number;
    errorRate: number;
    throughput: number;
    availability: number;
  };
}

export interface CostAlert {
  id: string;
  type: 'budget_exceeded' | 'anomaly_detected' | 'optimization_opportunity';
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  metric: string;
  threshold: number;
  actual: number;
  timestamp: string;
  recommendations: string[];
}

class MonitoringService {
  private readonly METRICS_TTL = 86400; // 24 hours
  private readonly ALERTS_KEY = 'cost_alerts';

  /**
   * Get comprehensive system metrics
   */
  async getSystemMetrics(period: '1h' | '24h' | '7d' = '24h'): Promise<SystemMetrics> {
    const timestamp = new Date().toISOString();

    // Gather all metrics in parallel
    const [
      llmMetrics,
      cacheStats,
      batchStats,
      promptStats,
      workerStats
    ] = await Promise.all([
      getLLMCostMetrics(period === '1h' ? 1 : period === '24h' ? 24 : 168),
      responseCache.getStats(),
      batchProcessor.getStats(),
      promptEngineering.getStats(),
      asyncWorkerQueue.getQueueStats()
    ]);

    // Calculate derived metrics
    const totalRequests = llmMetrics.totalRequests + cacheStats.totalRequests;
    const totalCost = llmMetrics.totalCost + (batchStats.costSavings * -1); // Net cost after savings
    const averageCostPerRequest = totalRequests > 0 ? totalCost / totalRequests : 0;

    // Infrastructure cost estimates
    const infrastructureCosts = this.calculateInfrastructureCosts();

    // Cost efficiency rating
    const costEfficiency = this.calculateCostEfficiency(averageCostPerRequest);

    // Queue health assessment
    const queueHealth = this.assessQueueHealth(workerStats);

    const metrics: SystemMetrics = {
      timestamp,
      period,

      llm: llmMetrics,

      cache: {
        ...cacheStats,
        averageEntrySize: cacheStats.entriesCount > 0
          ? cacheStats.totalSize / cacheStats.entriesCount
          : 0
      },

      batch: batchStats,

      prompt: promptStats,

      worker: {
        ...workerStats,
        queueHealth
      },

      infrastructure: infrastructureCosts,

      costs: {
        totalCostLast24h: totalCost,
        averageCostPerRequest,
        costReductionPercentage: this.calculateCostReduction(),
        projectedMonthlyCost: totalCost * 30,
        costEfficiency
      },

      performance: await this.getPerformanceMetrics()
    };

    // Cache metrics for future use
    await this.cacheMetrics(metrics, period);

    return metrics;
  }

  /**
   * Get active cost alerts
   */
  async getCostAlerts(): Promise<CostAlert[]> {
    const cached = await redisMemory.get(this.ALERTS_KEY);
    if (cached) {
      return JSON.parse(cached);
    }

    // Generate new alerts based on current metrics
    const alerts = await this.generateCostAlerts();
    await redisMemory.store(this.ALERTS_KEY, JSON.stringify(alerts), 3600); // 1 hour

    return alerts;
  }

  /**
   * Get metrics dashboard data
   */
  async getDashboardData(): Promise<{
    summary: SystemMetrics;
    trends: {
      cost_trend: number[];
      performance_trend: number[];
      cache_hit_trend: number[];
    };
    alerts: CostAlert[];
    recommendations: string[];
  }> {
    const [summary, alerts] = await Promise.all([
      this.getSystemMetrics('24h'),
      this.getCostAlerts()
    ]);

    const trends = await this.getTrendsData();
    const recommendations = this.generateRecommendations(summary, alerts);

    return {
      summary,
      trends,
      alerts,
      recommendations
    };
  }

  /**
   * Export metrics for external monitoring
   */
  async exportMetrics(format: 'json' | 'prometheus' = 'json'): Promise<string> {
    const metrics = await this.getSystemMetrics('24h');

    if (format === 'prometheus') {
      return this.convertToPrometheusFormat(metrics);
    }

    return JSON.stringify(metrics, null, 2);
  }

  // ===== PRIVATE METHODS =====

  private async getPerformanceMetrics(): Promise<SystemMetrics['performance']> {
    // In a real implementation, these would come from actual monitoring
    // For now, return estimated values
    return {
      averageResponseTime: 1250, // ms
      p95ResponseTime: 3200,     // ms
      errorRate: 0.008,          // 0.8%
      throughput: 45,            // requests per minute
      availability: 0.999        // 99.9%
    };
  }

  private calculateInfrastructureCosts(): SystemMetrics['infrastructure'] {
    // Rough estimates based on current AWS pricing
    const breakdown = {
      compute: 15.50,    // ECS Fargate (optimized)
      database: 8.50,    // RDS t4g.micro
      cache: 8.50,       // ElastiCache t4g.micro
      storage: 2.30,     // S3 + EBS
      networking: 1.20   // Data transfer + ALB
    };

    const total = Object.values(breakdown).reduce((sum, cost) => sum + cost, 0);

    return {
      estimatedMonthlyCost: total,
      breakdown,
      optimizationSavings: 25.0 // Estimated savings from optimizations
    };
  }

  private calculateCostEfficiency(avgCostPerRequest: number): SystemMetrics['costs']['costEfficiency'] {
    if (avgCostPerRequest < 0.01) return 'excellent';
    if (avgCostPerRequest < 0.03) return 'good';
    if (avgCostPerRequest < 0.06) return 'fair';
    return 'poor';
  }

  private calculateCostReduction(): number {
    // Estimate based on implemented optimizations
    // In a real system, this would compare before/after metrics
    return 45.0; // 45% cost reduction
  }

  private assessQueueHealth(stats: any): 'healthy' | 'degraded' | 'critical' {
    const errorRate = stats.failedJobs / (stats.completedJobs + stats.failedJobs);
    if (errorRate < 0.05) return 'healthy';
    if (errorRate < 0.10) return 'degraded';
    return 'critical';
  }

  private async generateCostAlerts(): Promise<CostAlert[]> {
    const metrics = await this.getSystemMetrics('1h');
    const alerts: CostAlert[] = [];

    // High cost per request alert
    if (metrics.costs.averageCostPerRequest > 0.06) {
      alerts.push({
        id: 'high_cost_per_request',
        type: 'budget_exceeded',
        severity: 'high',
        message: `Cost per request (${(metrics.costs.averageCostPerRequest * 100).toFixed(2)}¢) exceeds threshold`,
        metric: 'average_cost_per_request',
        threshold: 0.06,
        actual: metrics.costs.averageCostPerRequest,
        timestamp: new Date().toISOString(),
        recommendations: [
          'Enable more aggressive caching',
          'Implement request batching',
          'Review model selection logic'
        ]
      });
    }

    // Low cache hit rate alert
    if (metrics.cache.hitRate < 0.7) {
      alerts.push({
        id: 'low_cache_hit_rate',
        type: 'optimization_opportunity',
        severity: 'medium',
        message: `Cache hit rate (${(metrics.cache.hitRate * 100).toFixed(1)}%) is below optimal`,
        metric: 'cache_hit_rate',
        threshold: 0.7,
        actual: metrics.cache.hitRate,
        timestamp: new Date().toISOString(),
        recommendations: [
          'Increase cache TTL for stable responses',
          'Implement more granular caching keys',
          'Cache more response types'
        ]
      });
    }

    // High error rate alert
    if (metrics.worker.failedJobs / (metrics.worker.completedJobs + metrics.worker.failedJobs) > 0.1) {
      alerts.push({
        id: 'high_error_rate',
        type: 'anomaly_detected',
        severity: 'high',
        message: 'Worker queue error rate is elevated',
        metric: 'worker_error_rate',
        threshold: 0.1,
        actual: metrics.worker.failedJobs / (metrics.worker.completedJobs + metrics.worker.failedJobs),
        timestamp: new Date().toISOString(),
        recommendations: [
          'Check LLM provider status',
          'Review rate limiting settings',
          'Implement circuit breaker recovery'
        ]
      });
    }

    return alerts;
  }

  private async getTrendsData(): Promise<{
    cost_trend: number[];
    performance_trend: number[];
    cache_hit_trend: number[];
  }> {
    // In a real implementation, this would fetch historical data
    // For now, return mock trend data
    return {
      cost_trend: [0.08, 0.07, 0.06, 0.05, 0.04, 0.03], // Decreasing costs over time
      performance_trend: [1500, 1400, 1300, 1250, 1200, 1150], // Improving response times
      cache_hit_trend: [0.6, 0.65, 0.7, 0.75, 0.8, 0.85] // Improving cache hit rates
    };
  }

  private generateRecommendations(metrics: SystemMetrics, alerts: CostAlert[]): string[] {
    const recommendations: string[] = [];

    if (metrics.costs.averageCostPerRequest > 0.05) {
      recommendations.push('Implement more aggressive prompt optimization');
    }

    if (metrics.cache.hitRate < 0.8) {
      recommendations.push('Expand caching strategy to cover more endpoints');
    }

    if (metrics.worker.rateLimitHits > 10) {
      recommendations.push('Optimize async worker queue configuration');
    }

    if (metrics.llm.fallbackRate > 0.2) {
      recommendations.push('Review LLM provider reliability and failover strategy');
    }

    // Add alert-based recommendations
    for (const alert of alerts) {
      recommendations.push(...alert.recommendations);
    }

    return [...new Set(recommendations)]; // Remove duplicates
  }

  private convertToPrometheusFormat(metrics: SystemMetrics): string {
    const lines: string[] = [];

    // LLM metrics
    lines.push(`# LLM Metrics`);
    lines.push(`llm_total_requests ${metrics.llm.totalRequests}`);
    lines.push(`llm_total_tokens ${metrics.llm.totalTokens}`);
    lines.push(`llm_total_cost ${metrics.llm.totalCost}`);
    lines.push(`llm_average_cost_per_request ${metrics.llm.averageCostPerRequest}`);
    lines.push(`llm_cache_hit_rate ${metrics.llm.cacheHitRate}`);

    // Cache metrics
    lines.push(`# Cache Metrics`);
    lines.push(`cache_total_requests ${metrics.cache.totalRequests}`);
    lines.push(`cache_hit_rate ${metrics.cache.hitRate}`);
    lines.push(`cache_entries_count ${metrics.cache.entriesCount}`);

    // Cost metrics
    lines.push(`# Cost Metrics`);
    lines.push(`cost_average_per_request ${metrics.costs.averageCostPerRequest}`);
    lines.push(`cost_total_last_24h ${metrics.costs.totalCostLast24h}`);
    lines.push(`cost_reduction_percentage ${metrics.costs.costReductionPercentage}`);

    return lines.join('\n');
  }

  private async cacheMetrics(metrics: SystemMetrics, period: string): Promise<void> {
    const key = `system_metrics:${period}`;
    await redisMemory.store(key, JSON.stringify(metrics), this.METRICS_TTL);
  }
}

// Export singleton instance
export const monitoring = new MonitoringService();

// Export types
export type { SystemMetrics, CostAlert };


