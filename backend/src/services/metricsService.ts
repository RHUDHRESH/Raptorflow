/**
 * Metrics Service
 * Handles RAG calculation, metric aggregation, and trend analysis
 */

import { db } from '../lib/db';
import type { RAGStatus, Metric, CreateMetricInput } from '../types';

// =====================================================
// METRIC DEFINITIONS
// =====================================================

export interface MetricDefinition {
  name: string;
  category: string;
  unit: string;
  default_target?: number;
  rag_thresholds: {
    green_above: number;  // Percentage of target
    red_below: number;    // Percentage of target
  };
  higher_is_better: boolean;
  description: string;
}

export const METRIC_DEFINITIONS: Record<string, MetricDefinition> = {
  // Acquisition metrics
  brand_search_volume: {
    name: 'Brand Search Volume',
    category: 'acquisition',
    unit: 'searches/month',
    default_target: 500,
    rag_thresholds: { green_above: 100, red_below: 50 },
    higher_is_better: true,
    description: 'Monthly branded search queries'
  },
  website_traffic: {
    name: 'Website Traffic',
    category: 'acquisition',
    unit: 'visits/month',
    default_target: 10000,
    rag_thresholds: { green_above: 90, red_below: 70 },
    higher_is_better: true,
    description: 'Total monthly website visits'
  },
  demo_requests: {
    name: 'Demo Requests',
    category: 'acquisition',
    unit: 'requests/month',
    default_target: 50,
    rag_thresholds: { green_above: 90, red_below: 70 },
    higher_is_better: true,
    description: 'Monthly demo/trial requests'
  },
  demo_conversion_rate: {
    name: 'Demo Conversion Rate',
    category: 'conversion',
    unit: 'percentage',
    default_target: 20,
    rag_thresholds: { green_above: 90, red_below: 70 },
    higher_is_better: true,
    description: 'Percentage of demos that convert to opportunity'
  },
  
  // Pipeline metrics
  pipeline_value: {
    name: 'Pipeline Value',
    category: 'pipeline',
    unit: 'currency',
    default_target: 500000,
    rag_thresholds: { green_above: 90, red_below: 70 },
    higher_is_better: true,
    description: 'Total value of active pipeline'
  },
  opportunities_created: {
    name: 'Opportunities Created',
    category: 'pipeline',
    unit: 'count/month',
    default_target: 30,
    rag_thresholds: { green_above: 90, red_below: 70 },
    higher_is_better: true,
    description: 'New opportunities created per month'
  },
  avg_sales_cycle_days: {
    name: 'Average Sales Cycle',
    category: 'pipeline',
    unit: 'days',
    default_target: 45,
    rag_thresholds: { green_above: 110, red_below: 150 },  // Inverted - lower is better
    higher_is_better: false,
    description: 'Average days from opportunity to close'
  },
  win_rate: {
    name: 'Win Rate',
    category: 'pipeline',
    unit: 'percentage',
    default_target: 25,
    rag_thresholds: { green_above: 90, red_below: 70 },
    higher_is_better: true,
    description: 'Percentage of opportunities won'
  },
  
  // Activation metrics
  activation_rate: {
    name: 'Activation Rate',
    category: 'activation',
    unit: 'percentage',
    default_target: 60,
    rag_thresholds: { green_above: 90, red_below: 70 },
    higher_is_better: true,
    description: 'Percentage of signups reaching activation'
  },
  time_to_value: {
    name: 'Time to Value',
    category: 'activation',
    unit: 'days',
    default_target: 3,
    rag_thresholds: { green_above: 130, red_below: 200 },  // Inverted
    higher_is_better: false,
    description: 'Days from signup to first value'
  },
  onboarding_completion: {
    name: 'Onboarding Completion',
    category: 'activation',
    unit: 'percentage',
    default_target: 70,
    rag_thresholds: { green_above: 90, red_below: 70 },
    higher_is_better: true,
    description: 'Percentage completing onboarding'
  },
  
  // Retention metrics
  monthly_churn_rate: {
    name: 'Monthly Churn Rate',
    category: 'retention',
    unit: 'percentage',
    default_target: 3,
    rag_thresholds: { green_above: 130, red_below: 200 },  // Inverted
    higher_is_better: false,
    description: 'Monthly customer churn rate'
  },
  nrr: {
    name: 'Net Revenue Retention',
    category: 'retention',
    unit: 'percentage',
    default_target: 110,
    rag_thresholds: { green_above: 95, red_below: 85 },
    higher_is_better: true,
    description: 'Net revenue retention rate'
  },
  health_score: {
    name: 'Customer Health Score',
    category: 'retention',
    unit: 'score',
    default_target: 70,
    rag_thresholds: { green_above: 90, red_below: 70 },
    higher_is_better: true,
    description: 'Average customer health score'
  },
  
  // Expansion metrics
  expansion_rate: {
    name: 'Expansion Rate',
    category: 'expansion',
    unit: 'percentage',
    default_target: 15,
    rag_thresholds: { green_above: 90, red_below: 70 },
    higher_is_better: true,
    description: 'Percentage of customers expanding'
  },
  upsell_conversion: {
    name: 'Upsell Conversion Rate',
    category: 'expansion',
    unit: 'percentage',
    default_target: 20,
    rag_thresholds: { green_above: 90, red_below: 70 },
    higher_is_better: true,
    description: 'Percentage of upsell attempts that convert'
  },
  
  // Unit economics
  cac: {
    name: 'Customer Acquisition Cost',
    category: 'economics',
    unit: 'currency',
    default_target: 5000,
    rag_thresholds: { green_above: 120, red_below: 80 },  // Inverted
    higher_is_better: false,
    description: 'Cost to acquire a customer'
  },
  ltv: {
    name: 'Customer Lifetime Value',
    category: 'economics',
    unit: 'currency',
    default_target: 25000,
    rag_thresholds: { green_above: 90, red_below: 70 },
    higher_is_better: true,
    description: 'Expected lifetime value per customer'
  },
  ltv_cac_ratio: {
    name: 'LTV:CAC Ratio',
    category: 'economics',
    unit: 'ratio',
    default_target: 5,
    rag_thresholds: { green_above: 90, red_below: 60 },
    higher_is_better: true,
    description: 'Ratio of LTV to CAC'
  },
  payback_months: {
    name: 'CAC Payback Period',
    category: 'economics',
    unit: 'months',
    default_target: 12,
    rag_thresholds: { green_above: 120, red_below: 80 },  // Inverted
    higher_is_better: false,
    description: 'Months to recover CAC'
  }
};

// =====================================================
// RAG CALCULATION
// =====================================================

export function calculateRAGStatus(
  value: number,
  target: number,
  definition: MetricDefinition
): RAGStatus {
  if (value === undefined || target === undefined || !definition) {
    return 'unknown';
  }
  
  let percentOfTarget: number;
  
  if (definition.higher_is_better) {
    percentOfTarget = (value / target) * 100;
  } else {
    // For metrics where lower is better, invert the calculation
    percentOfTarget = (target / value) * 100;
  }
  
  const { green_above, red_below } = definition.rag_thresholds;
  
  if (percentOfTarget >= green_above) {
    return 'green';
  } else if (percentOfTarget < red_below) {
    return 'red';
  } else {
    return 'amber';
  }
}

// =====================================================
// METRICS SERVICE CLASS
// =====================================================

export class MetricsService {
  /**
   * Record a metric with automatic RAG calculation
   */
  async recordMetric(
    userId: string,
    input: CreateMetricInput
  ): Promise<{ metric: Metric | null; error: string | null }> {
    const definition = METRIC_DEFINITIONS[input.metric_name];
    
    // Calculate RAG status
    let rag_status: RAGStatus = 'unknown';
    const target = input.target_value ?? definition?.default_target;
    
    if (input.value !== undefined && target !== undefined && definition) {
      rag_status = calculateRAGStatus(input.value, target, definition);
    }
    
    const metricData: CreateMetricInput = {
      ...input,
      target_value: target,
      rag_thresholds: input.rag_thresholds || {
        green_above: definition?.rag_thresholds.green_above,
        red_below: definition?.rag_thresholds.red_below
      },
      source: input.source || 'manual'
    };
    
    const { data, error } = await db.metrics.create(userId, metricData);
    
    if (error) {
      return { metric: null, error: error.message };
    }
    
    // Update RAG status
    if (data) {
      const { supabase } = await import('../lib/db');
      await supabase
        .from('metrics')
        .update({ rag_status })
        .eq('id', data.id);
      
      data.rag_status = rag_status;
    }
    
    return { metric: data, error: null };
  }

  /**
   * Get RAG summary for a scope
   */
  async getRAGSummary(
    userId: string,
    scopeType: string,
    scopeId: string
  ): Promise<{
    overall: RAGStatus;
    breakdown: Record<RAGStatus, number>;
    metrics: Array<{
      name: string;
      value: number;
      target: number;
      rag: RAGStatus;
      trend?: 'up' | 'down' | 'flat';
    }>;
  }> {
    const { data: metrics } = await db.metrics.getLatest(userId, scopeType, scopeId);
    
    const breakdown: Record<RAGStatus, number> = {
      green: 0,
      amber: 0,
      red: 0,
      unknown: 0
    };
    
    const metricSummaries = (metrics || []).map(m => {
      breakdown[m.rag_status]++;
      
      return {
        name: m.metric_name,
        value: m.value || 0,
        target: m.target_value || 0,
        rag: m.rag_status
      };
    });
    
    // Calculate overall RAG
    let overall: RAGStatus = 'unknown';
    if (breakdown.red > 0) {
      overall = 'red';
    } else if (breakdown.amber > 0) {
      overall = 'amber';
    } else if (breakdown.green > 0) {
      overall = 'green';
    }
    
    return {
      overall,
      breakdown,
      metrics: metricSummaries
    };
  }

  /**
   * Get trend for a metric
   */
  async getMetricTrend(
    userId: string,
    scopeType: string,
    scopeId: string,
    metricName: string,
    periods: number = 6
  ): Promise<Array<{ period: string; value: number; rag: RAGStatus }>> {
    const { data: metrics } = await db.metrics.list(userId, {
      scope_type: scopeType,
      scope_id: scopeId,
      metric_name: metricName
    });
    
    // Get last N periods
    const sorted = (metrics || [])
      .sort((a, b) => new Date(b.recorded_at).getTime() - new Date(a.recorded_at).getTime())
      .slice(0, periods)
      .reverse();
    
    return sorted.map(m => ({
      period: m.period_start || m.recorded_at,
      value: m.value || 0,
      rag: m.rag_status
    }));
  }

  /**
   * Compare metrics across scopes
   */
  async compareAcrossScopes(
    userId: string,
    metricName: string,
    scopes: Array<{ type: string; id: string; label: string }>
  ): Promise<Array<{ scope: string; value: number; rag: RAGStatus }>> {
    const comparisons = await Promise.all(
      scopes.map(async (scope) => {
        const { data: metrics } = await db.metrics.getLatest(userId, scope.type, scope.id);
        const metric = metrics?.find(m => m.metric_name === metricName);
        
        return {
          scope: scope.label,
          value: metric?.value || 0,
          rag: metric?.rag_status || 'unknown' as RAGStatus
        };
      })
    );
    
    return comparisons;
  }

  /**
   * Get metric definitions
   */
  getMetricDefinitions(category?: string): MetricDefinition[] {
    const definitions = Object.values(METRIC_DEFINITIONS);
    
    if (category) {
      return definitions.filter(d => d.category === category);
    }
    
    return definitions;
  }

  /**
   * Get metric categories
   */
  getMetricCategories(): string[] {
    return [...new Set(Object.values(METRIC_DEFINITIONS).map(d => d.category))];
  }

  /**
   * Bulk update metrics (for imports or integrations)
   */
  async bulkRecordMetrics(
    userId: string,
    metrics: CreateMetricInput[]
  ): Promise<{ success: number; failed: number; errors: string[] }> {
    let success = 0;
    let failed = 0;
    const errors: string[] = [];
    
    for (const metric of metrics) {
      const result = await this.recordMetric(userId, metric);
      
      if (result.error) {
        failed++;
        errors.push(`${metric.metric_name}: ${result.error}`);
      } else {
        success++;
      }
    }
    
    return { success, failed, errors };
  }

  /**
   * Calculate derived metrics
   */
  calculateDerivedMetrics(metrics: Record<string, number>): Record<string, number> {
    const derived: Record<string, number> = {};
    
    // LTV:CAC Ratio
    if (metrics.ltv && metrics.cac && metrics.cac > 0) {
      derived.ltv_cac_ratio = metrics.ltv / metrics.cac;
    }
    
    // Payback months
    if (metrics.cac && metrics.mrr && metrics.mrr > 0) {
      derived.payback_months = metrics.cac / metrics.mrr;
    }
    
    // NRR from components
    if (metrics.starting_mrr && metrics.expansion && metrics.contraction && metrics.churn) {
      const endingMrr = metrics.starting_mrr + metrics.expansion - metrics.contraction - metrics.churn;
      derived.nrr = (endingMrr / metrics.starting_mrr) * 100;
    }
    
    return derived;
  }
}

export const metricsService = new MetricsService();

