import { trace as opentelemetryTrace, Span, Attributes, SpanStatusCode } from '@opentelemetry/api';
import { NodeSDK } from '@opentelemetry/sdk-node';
import { ConsoleSpanExporter } from '@opentelemetry/sdk-trace-node';
import Resource from '@opentelemetry/resources';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';
import { ExpressInstrumentation } from '@opentelemetry/instrumentation-express';
import { HttpInstrumentation } from '@opentelemetry/instrumentation-http';
import { PgInstrumentation } from '@opentelemetry/instrumentation-pg';
import * as promClient from 'prom-client';

// =====================================================
// OPENTELEMETRY TRACING
// =====================================================

const serviceName = 'raptorflow-backend-v2';

const sdk = new NodeSDK({
  // resource: new Resource({
  //   [SemanticResourceAttributes.SERVICE_NAME]: serviceName,
  // }),
  traceExporter: new ConsoleSpanExporter(), // Replace with OTLP exporter for production
  instrumentations: [
    new HttpInstrumentation(),
    new ExpressInstrumentation(),
    new PgInstrumentation(),
  ],
});

sdk.start();
console.log('OpenTelemetry SDK started');

export const tracer = opentelemetryTrace.getTracer(serviceName);

/**
 * Decorator for tracing async methods
 */
export function trace(spanName: string, attributes?: Attributes) {
  return function (target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    const originalMethod = descriptor.value;
    descriptor.value = async function (...args: any[]) {
      return await tracer.startActiveSpan(spanName, { attributes }, async (span: Span) => {
        try {
          if (attributes) {
            span.setAttributes(attributes);
          }
          const result = await originalMethod.apply(this, args);
          span.setStatus({ code: SpanStatusCode.OK });
          return result;
        } catch (error: any) {
          span.setStatus({ code: SpanStatusCode.ERROR, message: error.message });
          span.recordException(error);
          throw error;
        } finally {
          span.end();
        }
      });
    };
    return descriptor;
  };
}

// =====================================================
// PROMETHEUS METRICS
// =====================================================

export const metrics = {
  httpRequestsTotal: new promClient.Counter({
    name: 'http_requests_total',
    help: 'Total number of HTTP requests',
    labelNames: ['method', 'route', 'status_code'],
  }),
  httpRequestDurationSeconds: new promClient.Histogram({
    name: 'http_request_duration_seconds',
    help: 'Duration of HTTP requests in seconds',
    labelNames: ['method', 'route', 'status_code'],
    buckets: [0.1, 0.3, 0.5, 1, 1.5, 2, 5, 10],
  }),
  agentExecutionsTotal: new promClient.Counter({
    name: 'agent_executions_total',
    help: 'Total number of agent executions',
    labelNames: ['agent_name', 'status'],
  }),
  agentExecutionDurationSeconds: new promClient.Histogram({
    name: 'agent_execution_duration_seconds',
    help: 'Duration of agent executions in seconds',
    labelNames: ['agent_name', 'status'],
    buckets: [0.1, 0.5, 1, 2, 5, 10, 30],
  }),
  toolExecutionsTotal: new promClient.Counter({
    name: 'tool_executions_total',
    help: 'Total number of tool executions',
    labelNames: ['tool_name', 'status'],
  }),
  toolExecutionDurationSeconds: new promClient.Histogram({
    name: 'tool_execution_duration_seconds',
    help: 'Duration of tool executions in seconds',
    labelNames: ['tool_name', 'status'],
    buckets: [0.01, 0.05, 0.1, 0.5, 1, 2, 5],
  }),
  tokenUsageTotal: new promClient.Counter({
    name: 'token_usage_total',
    help: 'Total tokens used by the system',
    labelNames: ['model_name', 'agent_name'],
  }),
  ragQueryDurationSeconds: new promClient.Histogram({
    name: 'rag_query_duration_seconds',
    help: 'Duration of RAG queries in seconds',
    buckets: [0.01, 0.05, 0.1, 0.5, 1, 2, 5],
  }),
  embeddingGenerationDurationSeconds: new promClient.Histogram({
    name: 'embedding_generation_duration_seconds',
    help: 'Duration of embedding generation in seconds',
    buckets: [0.01, 0.05, 0.1, 0.5, 1, 2, 5],
  }),
  cacheHitsTotal: new promClient.Counter({
    name: 'cache_hits_total',
    help: 'Total cache hits',
    labelNames: ['cache_name'],
  }),
  cacheMissesTotal: new promClient.Counter({
    name: 'cache_misses_total',
    help: 'Total cache misses',
    labelNames: ['cache_name'],
  }),
};

// Expose register for metrics endpoint
export const register = promClient.register;

// =====================================================
// SOTA METRICS & MONITORING
// =====================================================

// Prometheus metrics for agent performance
export const agentMetrics = {
  executionTime: new promClient.Histogram({
    name: 'agent_execution_duration_seconds',
    help: 'Time taken to execute agents',
    labelNames: ['agent_name', 'department', 'status']
  }),

  tokenUsage: new promClient.Counter({
    name: 'agent_token_usage_total',
    help: 'Total tokens used by agents',
    labelNames: ['agent_name', 'model']
  }),

  cacheHits: new promClient.Counter({
    name: 'cache_hits_total',
    help: 'Cache hit counter',
    labelNames: ['cache_type', 'namespace']
  }),

  errorRate: new promClient.Counter({
    name: 'agent_errors_total',
    help: 'Agent execution errors',
    labelNames: ['agent_name', 'error_type']
  }),

  budgetUsage: new promClient.Gauge({
    name: 'budget_usage_ratio',
    help: 'Current budget usage ratio (0-1)',
    labelNames: ['user_id']
  })
};

// Enhanced performance profiler with metrics integration
export const performanceProfiler = {
  startTimer: (name: string) => {
    const start = Date.now();
    return {
      end: (labels?: Record<string, string>) => {
        const duration = Date.now() - start;
        // Record to Prometheus
        agentMetrics.executionTime
          .labels(labels?.agent_name || 'unknown', labels?.department || 'unknown', 'success')
          .observe(duration / 1000);
        return duration;
      }
    };
  },

  recordMetric: (name: string, value: number, labels?: Record<string, string>) => {
    if (name === 'token_usage') {
      agentMetrics.tokenUsage
        .labels(labels?.agent_name || 'unknown', labels?.model || 'unknown')
        .inc(value);
    } else if (name === 'cache_hit') {
      agentMetrics.cacheHits
        .labels(labels?.cache_type || 'unknown', labels?.namespace || 'unknown')
        .inc();
    }
  },

  recordError: (agentName: string, errorType: string) => {
    agentMetrics.errorRate
      .labels(agentName, errorType)
      .inc();
  },

  updateBudgetGauge: (userId: string, usageRatio: number) => {
    agentMetrics.budgetUsage
      .labels(userId)
      .set(usageRatio);
  }
};