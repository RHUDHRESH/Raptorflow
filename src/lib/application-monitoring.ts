// Application Monitoring System
// Implements error tracking, performance metrics, and uptime monitoring

import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'

export interface ErrorLog {
  id: string
  error_type: string
  error_message: string
  stack_trace: string
  user_id?: string
  session_id?: string
  ip_address?: string
  user_agent?: string
  url?: string
  method?: string
  headers?: any
  body?: any
  severity: 'low' | 'medium' | 'high' | 'critical'
  status: 'open' | 'investigating' | 'resolved' | 'closed'
  assigned_to?: string
  resolution?: string
  created_at: string
  updated_at: string
  resolved_at?: string
}

export interface PerformanceMetric {
  id: string
  metric_type: 'response_time' | 'throughput' | 'error_rate' | 'cpu_usage' | 'memory_usage' | 'database_connections'
  metric_name: string
  value: number
  unit: string
  tags: Record<string, string>
  timestamp: string
  environment: 'development' | 'staging' | 'production'
  service: string
  host?: string
}

export interface UptimeCheck {
  id: string
  check_name: string
  url: string
  method: string
  expected_status: number
  timeout_ms: number
  interval_seconds: number
  is_active: boolean
  last_checked?: string
  last_status: 'up' | 'down' | 'unknown'
  last_response_time?: number
  consecutiveFailures: number
  total_checks: number
  successful_checks: number
  failed_checks: number
  uptime_percentage: number
  created_at: string
  updated_at: string
}

export interface HealthCheck {
  id: string
  service_name: string
  status: 'healthy' | 'unhealthy' | 'degraded'
  check_type: 'database' | 'redis' | 'external_api' | 'disk_space' | 'memory'
  response_time?: number
  error_message?: string
  metadata: any
  last_checked: string
  created_at: string
  updated_at: string
}

export interface Alert {
  id: string
  alert_type: 'error' | 'performance' | 'uptime' | 'security'
  severity: 'info' | 'warning' | 'error' | 'critical'
  title: string
  message: string
  source: string
  metadata: any
  is_active: boolean
  acknowledged_by?: string
  acknowledged_at?: string
  resolved_by?: string
  resolved_at?: string
  created_at: string
  updated_at: string
}

export class ApplicationMonitoring {
  private supabase: any

  constructor() {
    this.supabase = createServerClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
      {
        cookies: {
          getAll() {
            return cookies().getAll()
          },
          setAll(cookiesToSet: any[]) {
            try {
              cookiesToSet.forEach(({ name, value, options }) =>
                cookies().set(name, value, options)
              )
            } catch {
              // The `setSet` method was called from a Server Component.
              // This can be ignored.
            }
          },
        },
      }
    )
  }

  /**
   * Log application error
   */
  async logError(errorData: {
    errorType: string
    errorMessage: string
    stackTrace?: string
    userId?: string
    sessionId?: string
    ipAddress?: string
    userAgent?: string
    url?: string
    method?: string
    headers?: any
    body?: any
    severity?: 'low' | 'medium' | 'high' | 'critical'
  }): Promise<ErrorLog> {
    try {
      const { data, error } = await this.supabase
        .from('error_logs')
        .insert({
          error_type: errorData.errorType,
          error_message: errorData.errorMessage,
          stack_trace: errorData.stackTrace,
          user_id: errorData.userId,
          session_id: errorData.sessionId,
          ip_address: errorData.ipAddress,
          user_agent: errorData.userAgent,
          url: errorData.url,
          method: errorData.method,
          headers: errorData.headers,
          body: errorData.body,
          severity: errorData.severity || 'medium',
          status: 'open'
        })
        .select('*')
        .single()

      if (error) throw error

      // Create alert for critical errors
      if (errorData.severity === 'critical') {
        await this.createAlert({
          alertType: 'error',
          severity: 'critical',
          title: `Critical Error: ${errorData.errorType}`,
          message: errorData.errorMessage,
          source: 'error_logs',
          metadata: {
            error_id: data.id,
            error_type: errorData.errorType,
            user_id: errorData.userId
          }
        })
      }

      return data
    } catch (error) {
      console.error('Error logging application error:', error)
      throw error
    }
  }

  /**
   * Record performance metric
   */
  async recordMetric(metricData: {
    metricType: string
    metricName: string
    value: number
    unit: string
    tags?: Record<string, string>
    environment?: string
    service?: string
    host?: string
  }): Promise<PerformanceMetric> {
    try {
      const { data, error } = await this.supabase
        .from('performance_metrics')
        .insert({
          metric_type: metricData.metricType,
          metric_name: metricData.metricName,
          value: metricData.value,
          unit: metricData.unit,
          tags: metricData.tags || {},
          timestamp: new Date().toISOString(),
          environment: metricData.environment || 'production',
          service: metricData.service || 'raptorflow',
          host: metricData.host
        })
        .select('*')
        .single()

      if (error) throw error

      // Check for performance alerts
      await this.checkPerformanceAlerts(data)

      return data
    } catch (error) {
      console.error('Error recording performance metric:', error)
      throw error
    }
  }

  /**
   * Create uptime check
   */
  async createUptimeCheck(checkData: {
    checkName: string
    url: string
    method?: string
    expectedStatus?: number
    timeoutMs?: number
    intervalSeconds?: number
  }): Promise<UptimeCheck> {
    try {
      const { data, error } = await this.supabase
        .from('uptime_checks')
        .insert({
          check_name: checkData.checkName,
          url: checkData.url,
          method: checkData.method || 'GET',
          expected_status: checkData.expectedStatus || 200,
          timeout_ms: checkData.timeoutMs || 30000,
          interval_seconds: checkData.intervalSeconds || 60,
          is_active: true,
          last_status: 'unknown',
          consecutiveFailures: 0,
          total_checks: 0,
          successful_checks: 0,
          failed_checks: 0,
          uptime_percentage: 0
        })
        .select('*')
        .single()

      if (error) throw error

      return data
    } catch (error) {
      console.error('Error creating uptime check:', error)
      throw error
    }
  }

  /**
   * Perform uptime check
   */
  async performUptimeCheck(checkId: string): Promise<void> {
    try {
      // Get check details
      const { data: check } = await this.supabase
        .from('uptime_checks')
        .select('*')
        .eq('id', checkId)
        .single()

      if (!check || !check.is_active) {
        return
      }

      const startTime = Date.now()
      let status: 'up' | 'down' | 'unknown' = 'unknown'
      let responseTime: number | undefined

      try {
        // Perform HTTP check
        const response = await fetch(check.url, {
          method: check.method,
          signal: AbortSignal.timeout(check.timeout_ms)
        })

        responseTime = Date.now() - startTime
        status = response.status === check.expected_status ? 'up' : 'down'

        // Update check results
        const totalChecks = check.total_checks + 1
        const successfulChecks = status === 'up' ? check.successful_checks + 1 : check.successful_checks
        const failedChecks = status === 'down' ? check.failed_checks + 1 : check.failed_checks
        const consecutiveFailures = status === 'down' ? check.consecutiveFailures + 1 : 0
        const uptimePercentage = (successfulChecks / totalChecks) * 100

        await this.supabase
          .from('uptime_checks')
          .update({
            last_checked: new Date().toISOString(),
            last_status: status,
            last_response_time: responseTime,
            consecutiveFailures: consecutiveFailures,
            total_checks: totalChecks,
            successful_checks: successfulChecks,
            failed_checks: failedChecks,
            uptime_percentage: uptimePercentage,
            updated_at: new Date().toISOString()
          })
          .eq('id', checkId)

        // Create alert for consecutive failures
        if (consecutiveFailures >= 3 && status === 'down') {
          await this.createAlert({
            alertType: 'uptime',
            severity: 'critical',
            title: `Service Down: ${check.check_name}`,
            message: `${check.check_name} has been down for ${consecutiveFailures} consecutive checks`,
            source: 'uptime_checks',
            metadata: {
              check_id: checkId,
              check_name: check.check_name,
              url: check.url,
              consecutiveFailures
            }
          })
        }

        // Record performance metric
        await this.recordMetric({
          metricType: 'response_time',
          metricName: 'uptime_check_response_time',
          value: responseTime || 0,
          unit: 'ms',
          tags: {
            check_name: check.check_name,
            status: status
          },
          service: 'uptime_monitor'
        })

      } catch (error) {
        status = 'down'
        responseTime = check.timeout_ms

        // Update check with failure
        const totalChecks = check.total_checks + 1
        const failedChecks = check.failed_checks + 1
        const consecutiveFailures = check.consecutiveFailures + 1
        const uptimePercentage = (check.successful_checks / totalChecks) * 100

        await this.supabase
          .from('uptime_checks')
          .update({
            last_checked: new Date().toISOString(),
            last_status: status,
            last_response_time: responseTime,
            consecutiveFailures: consecutiveFailures,
            total_checks: totalChecks,
            failed_checks: failedChecks,
            uptime_percentage: uptimePercentage,
            updated_at: new Date().toISOString()
          })
          .eq('id', checkId)

        // Log error
        await this.logError({
          errorType: 'UptimeCheckFailure',
          errorMessage: `Uptime check failed for ${check.check_name}`,
          stackTrace: error.stack,
          severity: 'medium'
        })
      }

    } catch (error) {
      console.error('Error performing uptime check:', error)
    }
  }

  /**
   * Perform health check
   */
  async performHealthCheck(checkType: string, serviceName: string): Promise<HealthCheck> {
    try {
      let status: 'healthy' | 'unhealthy' | 'degraded' = 'healthy'
      let responseTime: number | undefined
      let errorMessage: string | undefined
      let metadata: any = {}

      switch (checkType) {
        case 'database':
          try {
            const startTime = Date.now()
            await this.supabase.from('profiles').select('id').limit(1)
            responseTime = Date.now() - startTime
            metadata = { connection_time: responseTime }
          } catch (error) {
            status = 'unhealthy'
            errorMessage = error.message
            metadata = { error: error.message }
          }
          break

        case 'redis':
          // Placeholder for Redis health check
          status = 'healthy'
          metadata = { status: 'connected' }
          break

        case 'external_api':
          // Placeholder for external API health check
          status = 'healthy'
          metadata = { api_status: 'ok' }
          break

        case 'disk_space':
          // Placeholder for disk space check
          status = 'healthy'
          metadata = { disk_usage: '45%' }
          break

        case 'memory':
          // Placeholder for memory check
          status = 'degraded'
          metadata = { memory_usage: '78%' }
          break

        default:
          status = 'unknown'
          errorMessage = 'Unknown check type'
      }

      const { data, error } = await this.supabase
        .from('health_checks')
        .upsert({
          service_name: serviceName,
          check_type: checkType,
          status,
          response_time: responseTime,
          error_message: errorMessage,
          metadata,
          last_checked: new Date().toISOString(),
          updated_at: new Date().toISOString()
        })
        .select('*')
        .single()

      if (error) throw error

      // Create alert for unhealthy services
      if (status === 'unhealthy') {
        await this.createAlert({
          alertType: 'performance',
          severity: 'error',
          title: `Service Unhealthy: ${serviceName}`,
          message: errorMessage || `Health check failed for ${serviceName}`,
          source: 'health_checks',
          metadata: {
            service_name: serviceName,
            check_type: checkType,
            error_message: errorMessage
          }
        })
      }

      return data
    } catch (error) {
      console.error('Error performing health check:', error)
      throw error
    }
  }

  /**
   * Create alert
   */
  async createAlert(alertData: {
    alertType: string
    severity: string
    title: string
    message: string
    source: string
    metadata?: any
  }): Promise<Alert> {
    try {
      const { data, error } = await this.supabase
        .from('alerts')
        .insert({
          alert_type: alertData.alertType,
          severity: alertData.severity,
          title: alertData.title,
          message: alertData.message,
          source: alertData.source,
          metadata: alertData.metadata || {},
          is_active: true
        })
        .select('*')
        .single()

      if (error) throw error

      return data
    } catch (error) {
      console.error('Error creating alert:', error)
      throw error
    }
  }

  /**
   * Get error logs
   */
  async getErrorLogs(
    filters?: {
      errorType?: string
      severity?: string
      status?: string
      userId?: string
      limit?: number
      offset?: number
    }
  ): Promise<ErrorLog[]> {
    try {
      let query = this.supabase
        .from('error_logs')
        .select('*')
        .order('created_at', { ascending: false })

      if (filters?.errorType) {
        query = query.eq('error_type', filters.errorType)
      }

      if (filters?.severity) {
        query = query.eq('severity', filters.severity)
      }

      if (filters?.status) {
        query = query.eq('status', filters.status)
      }

      if (filters?.userId) {
        query = query.eq('user_id', filters.userId)
      }

      if (filters?.limit) {
        query = query.limit(filters.limit)
      }

      if (filters?.offset) {
        query = query.offset(filters.offset)
      }

      const { data, error } = await query

      if (error) throw error

      return data || []
    } catch (error) {
      console.error('Error getting error logs:', error)
      throw error
    }
  }

  /**
   * Get performance metrics
   */
  async getPerformanceMetrics(
    filters?: {
      metricType?: string
      metricName?: string
      service?: string
      environment?: string
      startTime?: string
      endTime?: string
      limit?: number
    }
  ): Promise<PerformanceMetric[]> {
    try {
      let query = this.supabase
        .from('performance_metrics')
        .select('*')
        .order('timestamp', { ascending: false })

      if (filters?.metricType) {
        query = query.eq('metric_type', filters.metricType)
      }

      if (filters?.metricName) {
        query = query.eq('metric_name', filters.metricName)
      }

      if (filters?.service) {
        query = query.eq('service', filters.service)
      }

      if (filters?.environment) {
        query = query.eq('environment', filters.environment)
      }

      if (filters?.startTime) {
        query = query.gte('timestamp', filters.startTime)
      }

      if (filters?.endTime) {
        query = query.lte('timestamp', filters.endTime)
      }

      if (filters?.limit) {
        query = query.limit(filters.limit)
      }

      const { data, error } = await query

      if (error) throw error

      return data || []
    } catch (error) {
      console.error('Error getting performance metrics:', error)
      throw error
    }
  }

  /**
   * Get uptime checks
   */
  async getUptimeChecks(activeOnly: boolean = true): Promise<UptimeCheck[]> {
    try {
      let query = this.supabase
        .from('uptime_checks')
        .select('*')
        .order('created_at', { ascending: false })

      if (activeOnly) {
        query = query.eq('is_active', true)
      }

      const { data, error } = await query

      if (error) throw error

      return data || []
    } catch (error) {
      console.error('Error getting uptime checks:', error)
      throw error
    }
  }

  /**
   * Get health checks
   */
  async getHealthChecks(): Promise<HealthCheck[]> {
    try {
      const { data, error } = await this.supabase
        .from('health_checks')
        .select('*')
        .order('last_checked', { ascending: false })

      if (error) throw error

      return data || []
    } catch (error) {
      console.error('Error getting health checks:', error)
      throw error
    }
  }

  /**
   * Get alerts
   */
  async getAlerts(
    filters?: {
      alertType?: string
      severity?: string
      activeOnly?: boolean
      limit?: number
    }
  ): Promise<Alert[]> {
    try {
      let query = this.supabase
        .from('alerts')
        .select('*')
        .order('created_at', { ascending: false })

      if (filters?.alertType) {
        query = query.eq('alert_type', filters.alertType)
      }

      if (filters?.severity) {
        query = query.eq('severity', filters.severity)
      }

      if (filters?.activeOnly) {
        query = query.eq('is_active', true)
      }

      if (filters?.limit) {
        query = query.limit(filters.limit)
      }

      const { data, error } = await query

      if (error) throw error

      return data || []
    } catch (error) {
      console.error('Error getting alerts:', error)
      throw error
    }
  }

  /**
   * Acknowledge alert
   */
  async acknowledgeAlert(alertId: string, userId: string): Promise<void> {
    try {
      await this.supabase
        .from('alerts')
        .update({
          acknowledged_by: userId,
          acknowledged_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        })
        .eq('id', alertId)
    } catch (error) {
      console.error('Error acknowledging alert:', error)
      throw error
    }
  }

  /**
   * Resolve alert
   */
  async resolveAlert(alertId: string, userId: string, resolution?: string): Promise<void> {
    try {
      await this.supabase
        .from('alerts')
        .update({
          is_active: false,
          resolved_by: userId,
          resolved_at: new Date().toISOString(),
          resolution,
          updated_at: new Date().toISOString()
        })
        .eq('id', alertId)
    } catch (error) {
      console.error('Error resolving alert:', error)
      throw error
    }
  }

  /**
   * Check performance alerts
   */
  private async checkPerformanceAlerts(metric: PerformanceMetric): Promise<void> {
    try {
      // Define alert thresholds
      const thresholds = {
        response_time: { warning: 1000, critical: 5000 },
        error_rate: { warning: 5, critical: 10 },
        cpu_usage: { warning: 70, critical: 90 },
        memory_usage: { warning: 80, critical: 95 },
        database_connections: { warning: 80, critical: 95 }
      }

      const threshold = thresholds[metric.metric_type]
      if (!threshold) return

      let severity: 'warning' | 'critical' | undefined
      if (metric.value >= threshold.critical) {
        severity = 'critical'
      } else if (metric.value >= threshold.warning) {
        severity = 'warning'
      }

      if (severity) {
        await this.createAlert({
          alertType: 'performance',
          severity,
          title: `Performance Alert: ${metric.metric_name}`,
          message: `${metric.metric_name} is ${metric.value}${metric.unit} (threshold: ${threshold[severity]}${metric.unit})`,
          source: 'performance_metrics',
          metadata: {
            metric_id: metric.id,
            metric_type: metric.metric_type,
            metric_name: metric.metric_name,
            value: metric.value,
            threshold: threshold[severity]
          }
        })
      }
    } catch (error) {
      console.error('Error checking performance alerts:', error)
    }
  }

  /**
   * Get monitoring statistics
   */
  async getMonitoringStats(
    days: number = 30
  ): Promise<{
    total_errors: number
    critical_errors: number
    resolved_errors: number
    avg_response_time: number
    uptime_percentage: number
    active_alerts: number
    health_status: Record<string, 'healthy' | 'unhealthy' | 'degraded'>
  }> {
    try {
      const since = new Date(Date.now() - days * 24 * 60 * 60 * 1000).toISOString()

      const [
        totalErrors,
        criticalErrors,
        resolvedErrors,
        avgResponseTime,
        uptimePercentage,
        activeAlerts,
        healthStatus
      ] = await Promise.all([
        this.supabase
          .from('error_logs')
          .select('id', { count: 'exact', head: true })
          .gte('created_at', since),
        this.supabase
          .from('error_logs')
          .select('id', { count: 'exact', head: true })
          .eq('severity', 'critical')
          .gte('created_at', since),
        this.supabase
          .from('error_logs')
          .select('id', { count: 'exact', head: true })
          .eq('status', 'resolved')
          .gte('created_at', since),
        this.supabase
          .from('performance_metrics')
          .select('value')
          .eq('metric_type', 'response_time')
          .gte('timestamp', since),
        this.supabase
          .from('uptime_checks')
          .select('uptime_percentage')
          .eq('is_active', true),
        this.supabase
          .from('alerts')
          .select('id', { count: 'exact', head: true })
          .eq('is_active', true),
        this.supabase
          .from('health_checks')
          .select('service_name', 'status')
      ])

      // Calculate average response time
      const responseTimes = avgResponseTime?.map(m => m.value) || []
      const avgResponseTimeValue = responseTimes.length > 0 
        ? responseTimes.reduce((sum, val) => sum + val, 0) / responseTimes.length 
        : 0

      // Calculate overall uptime
      const uptimeValues = uptimePercentage?.map(u => u.uptime_percentage) || []
      const overallUptime = uptimeValues.length > 0
        ? uptimeValues.reduce((sum, val) => sum + val, 0) / uptimeValues.length
        : 100

      // Aggregate health status
      const healthStatusMap: Record<string, 'healthy' | 'unhealthy' | 'degraded'> = {}
      healthStatus?.forEach(check => {
        if (!healthStatusMap[check.service_name] || 
            (healthStatusMap[check.service_name] === 'healthy' && check.status === 'degraded') ||
            (healthStatusMap[check.service_name] !== 'unhealthy' && check.status === 'unhealthy')) {
          healthStatusMap[check.service_name] = check.status
        }
      })

      return {
        total_errors: totalErrors || 0,
        critical_errors: criticalErrors || 0,
        resolved_errors: resolvedErrors || 0,
        avg_response_time: avgResponseTimeValue,
        uptime_percentage: overallUptime,
        active_alerts: activeAlerts || 0,
        health_status: healthStatusMap
      }
    } catch (error) {
      console.error('Error getting monitoring stats:', error)
      throw error
    }
  }

  /**
   * Clean up old monitoring data
   */
  async cleanupOldData(daysOld: number = 90): Promise<{
    errorLogs: number
    performanceMetrics: number
    alerts: number
  }> {
    try {
      const cutoffDate = new Date(Date.now() - daysOld * 24 * 60 * 60 * 1000).toISOString()

      const [
        errorLogs,
        performanceMetrics,
        alerts
      ] = await Promise.all([
        this.supabase
          .from('error_logs')
          .delete()
          .lt('created_at', cutoffDate),
        this.supabase
          .from('performance_metrics')
          .delete()
          .lt('timestamp', cutoffDate),
        this.supabase
          .from('alerts')
          .delete()
          .lt('created_at', cutoffDate)
          .eq('is_active', false)
      ])

      return {
        errorLogs: errorLogs || 0,
        performanceMetrics: performanceMetrics || 0,
        alerts: alerts || 0
      }
    } catch (error) {
      console.error('Error cleaning up old monitoring data:', error)
      return {
        errorLogs: 0,
        performanceMetrics: 0,
        alerts: 0
      }
    }
  }
}

export const applicationMonitoring = new ApplicationMonitoring()
