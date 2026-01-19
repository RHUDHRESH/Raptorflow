// Performance monitoring utilities
import { performance } from 'perf_hooks';

interface PerformanceMetrics {
  responseTime: number;
  memoryUsage: NodeJS.MemoryUsage;
  cpuUsage: NodeJS.CpuUsage;
  timestamp: number;
  endpoint: string;
  method: string;
  statusCode: number;
}

interface PerformanceStats {
  totalRequests: number;
  averageResponseTime: number;
  slowRequests: number;
  errorRate: number;
  requestsPerMinute: number;
  memoryUsage: NodeJS.MemoryUsage;
  cpuUsage: NodeJS.CpuUsage;
}

class PerformanceMonitor {
  private metrics: PerformanceMetrics[] = [];
  private stats: PerformanceStats = {
    totalRequests: 0,
    averageResponseTime: 0,
    slowRequests: 0,
    errorRate: 0,
    requestsPerMinute: 0,
    memoryUsage: process.memoryUsage(),
    cpuUsage: { user: 0, system: 0 }
  };
  
  private readonly SLOW_REQUEST_THRESHOLD = 1000; // 1 second
  private readonly MAX_METRICS_STORED = 1000;
  private readonly STATS_UPDATE_INTERVAL = 60000; // 1 minute
  
  constructor() {
    // Start monitoring
    this.startMonitoring();
  }
  
  private startMonitoring(): void {
    // Update stats periodically
    setInterval(() => {
      this.updateStats();
    }, this.STATS_UPDATE_INTERVAL);
    
    // Clean up old metrics periodically
    setInterval(() => {
      this.cleanupOldMetrics();
    }, 300000); // 5 minutes
  }
  
  recordRequest(
    endpoint: string,
    method: string,
    statusCode: number,
    responseTime: number
  ): void {
    const metric: PerformanceMetrics = {
      responseTime,
      memoryUsage: process.memoryUsage(),
      cpuUsage: process.cpuUsage(),
      timestamp: Date.now(),
      endpoint,
      method,
      statusCode
    };
    
    this.metrics.push(metric);
    
    // Update stats immediately
    this.updateStats();
    
    // Clean up if we have too many metrics
    if (this.metrics.length > this.MAX_METRICS_STORED) {
      this.metrics = this.metrics.slice(-this.MAX_METRICS_STORED);
    }
  }
  
  private updateStats(): void {
    const now = Date.now();
    const oneMinuteAgo = now - 60000;
    
    // Filter metrics from last minute for requests per minute
    const recentMetrics = this.metrics.filter(m => m.timestamp > oneMinuteAgo);
    this.stats.requestsPerMinute = recentMetrics.length;
    
    // Calculate average response time
    if (this.metrics.length > 0) {
      const totalResponseTime = this.metrics.reduce((sum, m) => sum + m.responseTime, 0);
      this.stats.averageResponseTime = totalResponseTime / this.metrics.length;
    }
    
    // Count slow requests
    this.stats.slowRequests = this.metrics.filter(m => m.responseTime > this.SLOW_REQUEST_THRESHOLD).length;
    
    // Calculate error rate
    const errorRequests = this.metrics.filter(m => m.statusCode >= 400).length;
    this.stats.errorRate = this.metrics.length > 0 ? (errorRequests / this.metrics.length) * 100 : 0;
    
    // Update memory and CPU usage
    this.stats.memoryUsage = process.memoryUsage();
    this.stats.cpuUsage = process.cpuUsage();
    
    // Update total requests
    this.stats.totalRequests = this.metrics.length;
  }
  
  private cleanupOldMetrics(): void {
    const oneHourAgo = Date.now() - 3600000; // 1 hour
    this.metrics = this.metrics.filter(m => m.timestamp > oneHourAgo);
  }
  
  getStats(): PerformanceStats {
    return { ...this.stats };
  }
  
  getMetrics(): PerformanceMetrics[] {
    return [...this.metrics];
  }
  
  getSlowRequests(): PerformanceMetrics[] {
    return this.metrics.filter(m => m.responseTime > this.SLOW_REQUEST_THRESHOLD);
  }
  
  getErrorRequests(): PerformanceMetrics[] {
    return this.metrics.filter(m => m.statusCode >= 400);
  }
  
  getEndpointStats(endpoint: string): {
    totalRequests: number;
    averageResponseTime: number;
    errorRate: number;
    slowRequests: number;
  } {
    const endpointMetrics = this.metrics.filter(m => m.endpoint === endpoint);
    
    if (endpointMetrics.length === 0) {
      return {
        totalRequests: 0,
        averageResponseTime: 0,
        errorRate: 0,
        slowRequests: 0
      };
    }
    
    const totalRequests = endpointMetrics.length;
    const totalResponseTime = endpointMetrics.reduce((sum, m) => sum + m.responseTime, 0);
    const averageResponseTime = totalResponseTime / totalRequests;
    const errorRequests = endpointMetrics.filter(m => m.statusCode >= 400).length;
    const errorRate = (errorRequests / totalRequests) * 100;
    const slowRequests = endpointMetrics.filter(m => m.responseTime > this.SLOW_REQUEST_THRESHOLD).length;
    
    return {
      totalRequests,
      averageResponseTime,
      errorRate,
      slowRequests
    };
  }
  
  // Performance monitoring middleware helper
  static createPerformanceMonitor() {
    return new PerformanceMonitor();
  }
  
  // Performance measurement wrapper
  static async measurePerformance<T>(
    fn: () => Promise<T>,
    endpoint: string,
    method: string
  ): Promise<{ result: T; metrics: PerformanceMetrics }> {
    const startTime = performance.now();
    let statusCode = 200;
    let error: Error | null = null;
    
    try {
      const result = await fn();
      return { result, metrics: this.createMetric(endpoint, method, 200, startTime) };
    } catch (err) {
      error = err as Error;
      statusCode = 500;
      throw err;
    } finally {
      const endTime = performance.now();
      const responseTime = endTime - startTime;
      const metrics = this.createMetric(endpoint, method, statusCode, startTime);
      
      if (error) {
        throw error;
      }
      
      return { result, metrics };
    }
  }
  
  private static createMetric(
    endpoint: string,
    method: string,
    statusCode: number,
    startTime: number
  ): PerformanceMetrics {
    const endTime = performance.now();
    const responseTime = endTime - startTime;
    
    return {
      responseTime,
      memoryUsage: process.memoryUsage(),
      cpuUsage: process.cpuUsage(),
      timestamp: Date.now(),
      endpoint,
      method,
      statusCode
    };
  }
}

// Performance monitoring singleton
export const performanceMonitor = PerformanceMonitor.createPerformanceMonitor();

// Performance decorator for API routes
export function withPerformanceMonitoring(
  target: any,
  propertyNameKey: string = 'performance'
) {
  const originalMethod = target[propertyNameKey];
  
  if (typeof originalMethod === 'function') {
    target[propertyNameKey] = async function (...args: any[]) {
      const startTime = performance.now();
      let statusCode = 200;
      let error: Error | null = null;
      
      try {
        const result = await originalMethod.apply(this, args);
        return result;
      } catch (err) {
        error = err as Error;
        statusCode = 500;
        throw err;
      } finally {
        const endTime = performance.now();
        const responseTime = endTime - startTime;
        
        // Extract endpoint and method from request if available
        const request = args[0];
        const endpoint = request?.url || 'unknown';
        const method = request?.method || 'GET';
        
        performanceMonitor.recordRequest(endpoint, method, statusCode, responseTime);
        
        if (error) {
          throw error;
        }
      }
    };
  }
  
  return target;
}

// Performance report generator
export class PerformanceReporter {
  static generateReport(): string {
    const stats = performanceMonitor.getStats();
    const slowRequests = performanceMonitor.getSlowRequests();
    const errorRequests = performanceMonitor.getErrorRequests();
    
    return `
Performance Report
================
Generated: ${new Date().toISOString()}

Overall Statistics:
- Total Requests: ${stats.totalRequests}
- Average Response Time: ${stats.averageResponseTime.toFixed(2)}ms
- Slow Requests: ${stats.slowRequests} (>1s)
- Error Rate: ${stats.errorRate.toFixed(2)}%
- Requests Per Minute: ${stats.requestsPerMinute}
- Memory Usage: ${Math.round(stats.memoryUsage.heapUsed / 1024 / 1024)}MB
- CPU Usage: ${stats.cpuUsage.user.toFixed(2)}%

Slow Requests (>1s):
${slowRequests.map(m => `- ${m.method} ${m.endpoint} - ${m.responseTime.toFixed(2)}ms`).join('\n')}

Error Requests:
${errorRequests.map(m => `- ${m.method} ${m.endpoint} - ${m.statusCode}`).join('\n')}

Top Endpoints by Response Time:
${Object.entries(
  Object.entries(
    performanceMonitor.getMetrics().reduce((acc, metric) => {
      const key = metric.endpoint;
      if (!acc[key]) acc[key] = [];
      acc[key].push(metric);
      return acc;
    }, {})
  )
)
  .sort(([, a], [, b]) => {
    const avgA = a.reduce((sum, m) => sum + m.responseTime, 0) / a.length;
    const avgB = b.reduce((sum, m) => sum + m.responseTime, 0) / b.length;
    return avgB - avgA;
  })
  .slice(0, 10)
  .map(([endpoint, metrics]) => {
    const avgTime = metrics.reduce((sum, m) => sum + m.responseTime, 0) / metrics.length;
    return `- ${endpoint}: ${avgTime.toFixed(2)}ms (${metrics.length} requests)`;
  })
  .join('\n')}
    `;
  }
  
  static getAlerts(): string[] {
    const alerts: string[] = [];
    const stats = performanceMonitor.getStats();
    
    // High error rate alert
    if (stats.errorRate > 10) {
      alerts.push(`High error rate detected: ${stats.errorRate.toFixed(2)}%`);
    }
    
    // High average response time alert
    if (stats.averageResponseTime > 500) {
      alerts.push(`High average response time: ${stats.averageResponseTime.toFixed(2)}ms`);
    }
    
    // Low memory alert
    const memoryUsagePercent = (stats.memoryUsage.heapUsed / stats.memoryUsage.heapTotal) * 100;
    if (memoryUsagePercent > 80) {
      alerts.push(`High memory usage: ${memoryUsagePercent.toFixed(2)}%`);
    }
    
    // High CPU usage alert
    if (stats.cpuUsage.user > 80) {
      alerts.push(`High CPU usage: ${stats.cpuUsage.user.toFixed(2)}%`);
    }
    
    return alerts;
  }
}

export default performanceMonitor;
