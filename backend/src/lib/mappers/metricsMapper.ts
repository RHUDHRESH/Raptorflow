/**
 * Metrics data mappers
 * Transform database rows to API DTOs and vice versa
 */

import type {
  Metric,
  CreateMetricInput,
  RAGStatus
} from '../../types';

/**
 * Transform database metric row to API response DTO
 */
export function toApiMetric(dbMetric: any): Metric {
  return {
    id: dbMetric.id,
    user_id: dbMetric.user_id,
    scope_type: dbMetric.scope_type,
    scope_id: dbMetric.scope_id,
    metric_name: dbMetric.metric_name,
    metric_category: dbMetric.metric_category,
    value: dbMetric.value,
    unit: dbMetric.unit,
    period_start: dbMetric.period_start,
    period_end: dbMetric.period_end,
    rag_status: dbMetric.rag_status as RAGStatus,
    rag_thresholds: dbMetric.rag_thresholds || {},
    recorded_at: dbMetric.recorded_at,
    raw_data: dbMetric.raw_data || {}
  };
}

/**
 * Transform API input to database insert
 */
export function toDbMetricInsert(
  userId: string,
  input: CreateMetricInput
): Omit<Metric, 'id' | 'recorded_at'> {
  return {
    user_id: userId,
    scope_type: input.scope_type,
    scope_id: input.scope_id,
    metric_name: input.metric_name,
    metric_category: input.metric_category,
    value: input.value,
    unit: input.unit,
    period_start: input.period_start,
    period_end: input.period_end,
    target_value: input.target_value,
    rag_status: 'unknown' as RAGStatus,
    rag_thresholds: input.rag_thresholds || {},
    source: input.source,
    raw_data: {}
  };
}

/**
 * Calculate RAG status based on value and thresholds
 */
export function calculateRAGStatus(
  value: number,
  thresholds: { green_above?: number; red_below?: number } = {}
): RAGStatus {
  const { green_above, red_below } = thresholds;

  if (red_below !== undefined && value < red_below) {
    return 'red';
  }

  if (green_above !== undefined && value >= green_above) {
    return 'green';
  }

  return 'amber';
}

/**
 * Transform metrics array with calculated RAG status
 */
export function toApiMetricsWithRAG(
  dbMetrics: any[]
): Metric[] {
  return dbMetrics.map(dbMetric => {
    const metric = toApiMetric(dbMetric);

    // Recalculate RAG status if thresholds exist
    if (Object.keys(metric.rag_thresholds).length > 0) {
      metric.rag_status = calculateRAGStatus(
        metric.metric_value,
        metric.rag_thresholds
      );
    }

    return metric;
  });
}
