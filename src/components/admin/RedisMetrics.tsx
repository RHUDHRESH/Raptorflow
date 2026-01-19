"use client"

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  Activity, 
  Database, 
  Zap, 
  Clock, 
  CheckCircle, 
  AlertTriangle, 
  XCircle,
  RefreshCw
} from 'lucide-react'

interface RedisMetrics {
  status: string
  timestamp: string
  connection: {
    healthy: boolean
    response_time_ms: number
    test_operation: string
  }
  services: {
    session_service: boolean
    cache_service: boolean
    rate_limit_service: boolean
    usage_tracker: boolean
    queue_service: boolean
  }
  performance: {
    read_latency_ms: number
    write_latency_ms: number
    operations_per_second: number
  }
  memory: {
    status: string
    usage_mb: string
    max_memory_mb: string
  }
  connections: {
    active: string
    max: string
  }
}

export function RedisMetrics() {
  const [metrics, setMetrics] = useState<RedisMetrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [refreshing, setRefreshing] = useState(false)

  const fetchMetrics = async () => {
    try {
      setRefreshing(true)
      const response = await fetch('/api/v1/admin/redis-metrics')
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.json()
      setMetrics(data)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch metrics')
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    fetchMetrics()
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchMetrics, 30000)
    return () => clearInterval(interval)
  }, [])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'degraded':
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />
      case 'unhealthy':
        return <XCircle className="h-4 w-4 text-red-500" />
      default:
        return <Clock className="h-4 w-4 text-gray-500" />
    }
  }

  const getStatusBadge = (status: string) => {
    const variant = status === 'healthy' ? 'default' : status === 'degraded' ? 'secondary' : 'destructive'
    return <Badge variant={variant}>{status}</Badge>
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-6 w-6 animate-spin" />
        <span className="ml-2">Loading Redis metrics...</span>
      </div>
    )
  }

  if (error) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center text-red-600">
            <XCircle className="h-5 w-5 mr-2" />
            <span>Error loading metrics: {error}</span>
          </div>
          <Button onClick={fetchMetrics} className="mt-4">
            Retry
          </Button>
        </CardContent>
      </Card>
    )
  }

  if (!metrics) return null

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Database className="h-6 w-6" />
          <h2 className="text-2xl font-bold">Redis Performance</h2>
          {getStatusBadge(metrics.status)}
        </div>
        <Button 
          onClick={fetchMetrics} 
          disabled={refreshing}
          variant="outline"
          size="sm"
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Connection Status</CardTitle>
            {getStatusIcon(metrics.connection.healthy ? 'healthy' : 'unhealthy')}
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {metrics.connection.healthy ? 'Connected' : 'Disconnected'}
            </div>
            <p className="text-xs text-muted-foreground">
              {metrics.connection.response_time_ms.toFixed(2)}ms response time
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Operations/sec</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {metrics.performance.operations_per_second.toFixed(0)}
            </div>
            <p className="text-xs text-muted-foreground">
              Current throughput
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Read Latency</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {metrics.performance.read_latency_ms.toFixed(2)}ms
            </div>
            <p className="text-xs text-muted-foreground">
              Average read time
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Write Latency</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {metrics.performance.write_latency_ms.toFixed(2)}ms
            </div>
            <p className="text-xs text-muted-foreground">
              Average write time
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Services Status */}
      <Card>
        <CardHeader>
          <CardTitle>Redis Services Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {Object.entries(metrics.services).map(([service, status]) => (
              <div key={service} className="flex items-center space-x-2">
                {getStatusIcon(status ? 'healthy' : 'unhealthy')}
                <span className="text-sm capitalize">
                  {service.replace(/_/g, ' ')}
                </span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Performance Details */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Performance Metrics</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between">
              <span>Read Latency:</span>
              <span className="font-mono">{metrics.performance.read_latency_ms.toFixed(2)}ms</span>
            </div>
            <div className="flex justify-between">
              <span>Write Latency:</span>
              <span className="font-mono">{metrics.performance.write_latency_ms.toFixed(2)}ms</span>
            </div>
            <div className="flex justify-between">
              <span>Operations/sec:</span>
              <span className="font-mono">{metrics.performance.operations_per_second.toFixed(0)}</span>
            </div>
            <div className="flex justify-between">
              <span>Test Operation:</span>
              <Badge variant={metrics.connection.test_operation === 'ok' ? 'default' : 'destructive'}>
                {metrics.connection.test_operation}
              </Badge>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Connection Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between">
              <span>Health:</span>
              <Badge variant={metrics.connection.healthy ? 'default' : 'destructive'}>
                {metrics.connection.healthy ? 'Healthy' : 'Unhealthy'}
              </Badge>
            </div>
            <div className="flex justify-between">
              <span>Response Time:</span>
              <span className="font-mono">{metrics.connection.response_time_ms.toFixed(2)}ms</span>
            </div>
            <div className="flex justify-between">
              <span>Last Updated:</span>
              <span className="text-sm text-muted-foreground">
                {new Date(metrics.timestamp).toLocaleString()}
              </span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
