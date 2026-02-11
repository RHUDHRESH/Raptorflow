/**
 * Performance monitoring utilities
 * Web Vitals tracking and reporting
 */

import { onCLS, onFCP, onINP, onLCP, onTTFB, Metric } from 'web-vitals'

export interface WebVitalsMetric {
  id: string
  name: string
  value: number
  rating: 'good' | 'needs-improvement' | 'poor'
  delta: number
  navigationType: string
}

/**
 * Report Web Vitals to analytics endpoint
 */
function sendToAnalytics(metric: Metric) {
  const body = JSON.stringify({
    id: metric.id,
    name: metric.name,
    value: metric.value,
    rating: metric.rating,
    delta: metric.delta,
    navigationType: metric.navigationType,
  })

  // Send to analytics endpoint
  if (navigator.sendBeacon) {
    navigator.sendBeacon('/api/analytics/vitals', body)
  } else {
    fetch('/api/analytics/vitals', {
      body,
      method: 'POST',
      keepalive: true,
      headers: {
        'Content-Type': 'application/json',
      },
    })
  }
}

/**
 * Initialize Web Vitals monitoring
 */
export function initWebVitals() {
  onCLS(sendToAnalytics)
  onFCP(sendToAnalytics)
  onINP(sendToAnalytics)
  onLCP(sendToAnalytics)
  onTTFB(sendToAnalytics)
}

/**
 * Performance mark utility
 */
export function mark(name: string) {
  if (typeof window !== 'undefined' && window.performance) {
    performance.mark(name)
  }
}

/**
 * Performance measure utility
 */
export function measure(name: string, startMark: string, endMark?: string) {
  if (typeof window !== 'undefined' && window.performance) {
    try {
      performance.measure(name, startMark, endMark)
      const measure = performance.getEntriesByName(name)[0]
      return measure?.duration
    } catch (e) {
      console.warn('Performance measure failed:', e)
    }
  }
  return 0
}

/**
 * Report custom metric
 */
export function reportMetric(name: string, value: number, metadata?: Record<string, any>) {
  const body = JSON.stringify({
    name,
    value,
    timestamp: Date.now(),
    ...metadata,
  })

  if (navigator.sendBeacon) {
    navigator.sendBeacon('/api/analytics/metrics', body)
  } else {
    fetch('/api/analytics/metrics', {
      body,
      method: 'POST',
      keepalive: true,
      headers: {
        'Content-Type': 'application/json',
      },
    })
  }
}

/**
 * Monitor component render time
 */
export function withPerformanceMonitoring<T extends (...args: any[]) => any>(
  fn: T,
  componentName: string
): T {
  return ((...args: any[]) => {
    const startMark = `${componentName}-start`
    const endMark = `${componentName}-end`
    
    mark(startMark)
    const result = fn(...args)
    mark(endMark)
    
    const duration = measure(componentName, startMark, endMark)
    if (duration && duration > 16) { // Report if > 1 frame (16ms)
      reportMetric('component-render', duration, { component: componentName })
    }
    
    return result
  }) as T
}
