/**
 * AI Cost Tracking System
 * Monitors and tracks AI usage costs across all services
 */

interface CostMetrics {
  totalTokens: number;
  totalCost: number;
  requestCount: number;
  modelUsage: Record<string, { tokens: number; cost: number; requests: number }>;
  dailyUsage: Record<string, { tokens: number; cost: number }>;
}

interface UsageRecord {
  timestamp: Date;
  model: string;
  tokens: number;
  cost: number;
  operation: string;
}

export class CostTracker {
  private static instance: CostTracker;
  private metrics: CostMetrics;
  private storageKey = 'raptorflow-ai-costs';

  constructor() {
    this.metrics = this.loadMetrics();
  }

  static getInstance(): CostTracker {
    if (!CostTracker.instance) {
      CostTracker.instance = new CostTracker();
    }
    return CostTracker.instance;
  }

  private loadMetrics(): CostMetrics {
    if (typeof window === 'undefined') {
      return this.getDefaultMetrics();
    }

    try {
      const stored = localStorage.getItem(this.storageKey);
      if (stored) {
        return JSON.parse(stored);
      }
    } catch (error) {
      console.warn('Failed to load cost metrics:', error);
    }

    return this.getDefaultMetrics();
  }

  private getDefaultMetrics(): CostMetrics {
    return {
      totalTokens: 0,
      totalCost: 0,
      requestCount: 0,
      modelUsage: {},
      dailyUsage: {}
    };
  }

  private saveMetrics(): void {
    if (typeof window === 'undefined') return;

    try {
      localStorage.setItem(this.storageKey, JSON.stringify(this.metrics));
    } catch (error) {
      console.warn('Failed to save cost metrics:', error);
    }
  }

  trackUsage(record: Omit<UsageRecord, 'timestamp'>): void {
    const timestamp = new Date();
    const dateKey = timestamp.toISOString().split('T')[0]; // YYYY-MM-DD

    // Update totals
    this.metrics.totalTokens += record.tokens;
    this.metrics.totalCost += record.cost;
    this.metrics.requestCount += 1;

    // Update model usage
    if (!this.metrics.modelUsage[record.model]) {
      this.metrics.modelUsage[record.model] = { tokens: 0, cost: 0, requests: 0 };
    }
    this.metrics.modelUsage[record.model].tokens += record.tokens;
    this.metrics.modelUsage[record.model].cost += record.cost;
    this.metrics.modelUsage[record.model].requests += 1;

    // Update daily usage
    if (!this.metrics.dailyUsage[dateKey]) {
      this.metrics.dailyUsage[dateKey] = { tokens: 0, cost: 0 };
    }
    this.metrics.dailyUsage[dateKey].tokens += record.tokens;
    this.metrics.dailyUsage[dateKey].cost += record.cost;

    this.saveMetrics();

    // Log for monitoring
    console.log(`💰 AI Usage: ${record.tokens} tokens, $${record.cost.toFixed(6)} (${record.operation})`);
  }

  getMetrics(): CostMetrics {
    return { ...this.metrics };
  }

  getDailyUsage(days: number = 7): Array<{ date: string; tokens: number; cost: number }> {
    const result = [];
    const today = new Date();
    
    for (let i = days - 1; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      const dateKey = date.toISOString().split('T')[0];
      
      result.push({
        date: dateKey,
        tokens: this.metrics.dailyUsage[dateKey]?.tokens || 0,
        cost: this.metrics.dailyUsage[dateKey]?.cost || 0
      });
    }
    
    return result;
  }

  getModelBreakdown(): Array<{ model: string; tokens: number; cost: number; requests: number; avgCostPerRequest: number }> {
    return Object.entries(this.metrics.modelUsage).map(([model, usage]) => ({
      model,
      tokens: usage.tokens,
      cost: usage.cost,
      requests: usage.requests,
      avgCostPerRequest: usage.requests > 0 ? usage.cost / usage.requests : 0
    })).sort((a, b) => b.cost - a.cost);
  }

  getCostProjection(): { daily: number; weekly: number; monthly: number } {
    const recentDays = this.getDailyUsage(7);
    const avgDailyCost = recentDays.reduce((sum, day) => sum + day.cost, 0) / 7;
    
    return {
      daily: avgDailyCost,
      weekly: avgDailyCost * 7,
      monthly: avgDailyCost * 30
    };
  }

  resetMetrics(): void {
    this.metrics = this.getDefaultMetrics();
    this.saveMetrics();
    console.log('🧹 Cost metrics reset');
  }

  exportData(): string {
    return JSON.stringify({
      metrics: this.metrics,
      dailyUsage: this.getDailyUsage(30),
      modelBreakdown: this.getModelBreakdown(),
      projections: this.getCostProjection(),
      exportDate: new Date().toISOString()
    }, null, 2);
  }
}

// Cost calculation helper
export function calculateCost(tokens: number, model: string): number {
  const costs: Record<string, number> = {
    'gemini-2.0-flash-001': 0.000000075, // $0.075 per 1M tokens
    'gemini-2.0-flash-exp': 0.000000075,
    'text-embedding-004': 0.00000002,   // $0.02 per 1M tokens
  };

  const costPerToken = costs[model] || 0.000000075; // Default to flash pricing
  return tokens * costPerToken;
}

// React hook for easy integration
export function useCostTracker() {
  const tracker = CostTracker.getInstance();
  
  return {
    trackUsage: (record: Omit<UsageRecord, 'timestamp'>) => tracker.trackUsage(record),
    getMetrics: () => tracker.getMetrics(),
    getDailyUsage: (days?: number) => tracker.getDailyUsage(days),
    getModelBreakdown: () => tracker.getModelBreakdown(),
    getCostProjection: () => tracker.getCostProjection(),
    resetMetrics: () => tracker.resetMetrics(),
    exportData: () => tracker.exportData()
  };
}

export const costTracker = CostTracker.getInstance();
