/**
 * Performance Monitoring Dashboard Component
 * Real-time system monitoring and analytics
 */
"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { BlueprintCard } from "@/components/ui/BlueprintCard"
import { BlueprintKPI } from "@/components/ui/BlueprintKPI"
import { BlueprintProgress } from "@/components/ui/BlueprintProgress"
import { BlueprintChart } from "@/components/ui/BlueprintChart"
import { BlueprintTable } from "@/components/ui/BlueprintTable"
import { BlueprintTimeline } from "@/components/ui/BlueprintTimeline"
import { BlueprintLoader } from "@/components/ui/BlueprintLoader"
import { PageHeader } from "@/components/ui/PageHeader"
import {
  Activity,
  Cpu,
  HardDrive,
  MemoryStick,
  Database,
  Globe,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  TrendingUp,
  TrendingDown,
  Zap,
  BarChart3,
  LineChart,
  PieChart,
  Settings,
  RefreshCw,
  Download,
  Filter,
  Calendar,
  Search,
  Brain
} from "lucide-react"

interface SystemMetrics {
  timestamp: string
  cpu_usage: number
  memory_usage: number
  disk_usage: number
  network_io: {
    bytes_in: number
    bytes_out: number
  }
  active_connections: number
  uptime: number
}

interface AgentMetrics {
  agent_id: string
  agent_name: string
  status: "active" | "idle" | "error"
  execution_count: number
  avg_response_time: number
  success_rate: number
  total_tokens: number
  total_cost: number
  last_execution: string
}

interface WorkflowMetrics {
  workflow_id: string
  workflow_name: string
  status: "running" | "completed" | "failed" | "paused"
  total_executions: number
  avg_completion_time: number
  success_rate: number
  active_instances: number
  last_execution: string
}

interface Alert {
  id: string
  severity: "low" | "medium" | "high" | "critical"
  type: string
  message: string
  timestamp: string
  status: "active" | "resolved" | "acknowledged"
  acknowledged_by?: string
  resolved_at?: string
}

interface HealthCheck {
  name: string
  status: "healthy" | "warning" | "critical"
  message: string
  last_check: string
  response_time: number
  details: Record<string, any>
}

export default function PerformanceMonitoring() {
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics[]>([])
  const [agentMetrics, setAgentMetrics] = useState<AgentMetrics[]>([])
  const [workflowMetrics, setWorkflowMetrics] = useState<WorkflowMetrics[]>([])
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [healthChecks, setHealthChecks] = useState<HealthCheck[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedTimeRange, setSelectedTimeRange] = useState("1h")
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [refreshInterval, setRefreshInterval] = useState(5000)

  useEffect(() => {
    loadMonitoringData()

    if (autoRefresh) {
      const interval = setInterval(loadMonitoringData, refreshInterval)
      return () => clearInterval(interval)
    }
  }, [autoRefresh, refreshInterval, selectedTimeRange])

  const loadMonitoringData = async () => {
    try {
      const [systemRes, agentRes, workflowRes, alertRes, healthRes] = await Promise.all([
        fetch(`/api/monitoring/system?range=${selectedTimeRange}`),
        fetch(`/api/monitoring/agents?range=${selectedTimeRange}`),
        fetch(`/api/monitoring/workflows?range=${selectedTimeRange}`),
        fetch(`/api/monitoring/alerts?range=${selectedTimeRange}`),
        fetch(`/api/monitoring/health`)
      ])

      const [systemData, agentData, workflowData, alertData, healthData] = await Promise.all([
        systemRes.json(),
        agentRes.json(),
        workflowRes.json(),
        alertRes.json(),
        healthRes.json()
      ])

      setSystemMetrics(systemData)
      setAgentMetrics(agentData)
      setWorkflowMetrics(workflowData)
      setAlerts(alertData)
      setHealthChecks(healthData)
    } catch (error) {
      console.error('Failed to load monitoring data:', error)
    } finally {
      setLoading(false)
    }
  }

  const getLatestSystemMetrics = () => {
    return systemMetrics[systemMetrics.length - 1] || {}
  }

  const getSystemHealthStatus = () => {
    const criticalChecks = healthChecks.filter(check => check.status === 'critical')
    const warningChecks = healthChecks.filter(check => check.status === 'warning')

    if (criticalChecks.length > 0) return 'critical'
    if (warningChecks.length > 0) return 'warning'
    return 'healthy'
  }

  const getAlertSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-600 bg-red-50'
      case 'high': return 'text-orange-600 bg-orange-50'
      case 'medium': return 'text-yellow-600 bg-yellow-50'
      case 'low': return 'text-blue-600 bg-blue-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-600'
      case 'warning': return 'text-yellow-600'
      case 'critical': return 'text-red-600'
      case 'active': return 'text-green-600'
      case 'idle': return 'text-yellow-600'
      case 'error': return 'text-red-600'
      case 'running': return 'text-blue-600'
      case 'completed': return 'text-green-600'
      case 'failed': return 'text-red-600'
      case 'paused': return 'text-yellow-600'
      default: return 'text-gray-600'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return <CheckCircle className="w-4 h-4" />
      case 'warning': return <AlertTriangle className="w-4 h-4" />
      case 'critical': return <XCircle className="w-4 h-4" />
      case 'active': return <Activity className="w-4 h-4" />
      case 'idle': return <Clock className="w-4 h-4" />
      case 'error': return <XCircle className="w-4 h-4" />
      case 'running': return <Zap className="w-4 h-4" />
      case 'completed': return <CheckCircle className="w-4 h-4" />
      case 'failed': return <XCircle className="w-4 h-4" />
      case 'paused': return <Clock className="w-4 h-4" />
      default: return <Clock className="w-4 h-4" />
    }
  }

  const formatUptime = (seconds: number) => {
    const days = Math.floor(seconds / 86400)
    const hours = Math.floor((seconds % 86400) / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)

    if (days > 0) return `${days}d ${hours}h ${minutes}m`
    if (hours > 0) return `${hours}h ${minutes}m`
    return `${minutes}m`
  }

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-[var(--paper)] p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center h-64">
              <BlueprintLoader size="lg" />
            </div>
        </div>
      </div>
    )
  }

  const latestMetrics = getLatestSystemMetrics()
  const systemHealth = getSystemHealthStatus()

  return (
    <div className="min-h-screen bg-[var(--paper)] p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <PageHeader
          title="Performance Monitoring"
          descriptor="Real-time system monitoring and analytics"
          moduleCode="monitoring"
          actions={
            <div className="flex items-center gap-2">
              <select
                value={selectedTimeRange}
                onChange={(e) => setSelectedTimeRange(e.target.value)}
                className="px-3 py-2 border border-[var(--border)] rounded-lg bg-[var(--paper)] text-[var(--ink)]"
              >
                <option value="5m">Last 5 minutes</option>
                <option value="15m">Last 15 minutes</option>
                <option value="1h">Last hour</option>
                <option value="6h">Last 6 hours</option>
                <option value="24h">Last 24 hours</option>
              </select>

              <Button
                variant="outline"
                size="sm"
                onClick={() => setAutoRefresh(!autoRefresh)}
                className={autoRefresh ? 'bg-[var(--blueprint)] text-[var(--paper)]' : ''}
              >
                <RefreshCw className={`w-4 h-4 mr-2 ${autoRefresh ? 'animate-spin' : ''}`} />
                Auto Refresh
              </Button>

              <Button variant="outline" size="sm">
                <Download className="w-4 h-4 mr-2" />
                Export
              </Button>

              <Button variant="outline" size="sm">
                <Settings className="w-4 h-4 mr-2" />
                Settings
              </Button>
            </div>
          }
        />

        {/* System Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <BlueprintKPI
            title="CPU Usage"
            value={`${latestMetrics.cpu_usage || 0}%`}
            subtitle="Current utilization"
            icon={<Cpu className="w-5 h-5" />}
            trend={{ value: latestMetrics.cpu_usage > 80 ? -5 : 2, direction: latestMetrics.cpu_usage > 80 ? "down" as const : "up" as const }}
          />

          <BlueprintKPI
            title="Memory Usage"
            value={`${latestMetrics.memory_usage || 0}%`}
            subtitle="Current utilization"
            icon={<MemoryStick className="w-5 h-5" />}
            trend={{ value: latestMetrics.memory_usage > 80 ? -3 : 1, direction: latestMetrics.memory_usage > 80 ? "down" as const : "up" as const }}
          />

          <BlueprintKPI
            title="Disk Usage"
            value={`${latestMetrics.disk_usage || 0}%`}
            subtitle="Current utilization"
            icon={<HardDrive className="w-5 h-5" />}
            trend={{ value: 0, direction: "stable" as const }}
          />

          <BlueprintKPI
            title="System Uptime"
            value={formatUptime(latestMetrics.uptime || 0)}
            subtitle="System running time"
            icon={<Clock className="w-5 h-5" />}
            trend={{ value: 100, direction: "up" as const }}
          />
        </div>

        {/* System Health */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="w-5 h-5" />
              System Health
              <Badge className={getAlertSeverityColor(systemHealth)}>
                {systemHealth}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {healthChecks.map((check) => (
                <BlueprintCard
                  key={check.name}
                  className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      <div className={getStatusColor(check.status)}>
                        {getStatusIcon(check.status)}
                      </div>
                      <div>
                        <h3 className="font-medium text-[var(--ink)]">{check.name}</h3>
                        <p className="text-sm text-[var(--muted)] mt-1">{check.message}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-xs text-[var(--muted)]">Response Time</div>
                      <div className="text-sm font-medium text-[var(--ink)]">
                        {check.response_time}ms
                      </div>
                      <div className="text-xs text-[var(--muted)] mt-1">
                        {new Date(check.last_check).toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                </BlueprintCard>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* System Metrics Chart */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <LineChart className="w-5 h-5" />
                  System Metrics
                </CardTitle>
              </CardHeader>
              <CardContent>
                <BlueprintChart
                  type="line"
                  data={systemMetrics.map(metric => ({
                    label: metric.timestamp,
                    value: metric.cpu_usage,
                    cpu: metric.cpu_usage,
                    memory: metric.memory_usage,
                    disk: metric.disk_usage
                  }))}
                  options={{
                    x: 'timestamp',
                    y: ['cpu', 'memory', 'disk'],
                    colors: ['#3b82f6', '#10b981', '#f59e0b'],
                    height: 300
                  }}
                />
              </CardContent>
            </Card>
          </div>

          {/* Active Alerts */}
          <div>
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5" />
                  Active Alerts
                  <Badge variant="secondary">
                    {alerts.filter(a => a.status === 'active').length}
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {alerts.filter(alert => alert.status === 'active').slice(0, 5).map((alert) => (
                    <BlueprintCard
                      key={alert.id}
                      className="p-3">
                      <div className="flex items-start gap-2">
                        <div className={`mt-1 ${getAlertSeverityColor(alert.severity).split(' ')[0]}`}>
                          {getStatusIcon(alert.severity)}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <Badge className={getAlertSeverityColor(alert.severity)}>
                              {alert.severity}
                            </Badge>
                            <span className="text-xs text-[var(--muted)]">
                              {alert.type}
                            </span>
                          </div>
                          <p className="text-sm text-[var(--ink)] mt-1">{alert.message}</p>
                          <div className="text-xs text-[var(--muted)] mt-2">
                            {new Date(alert.timestamp).toLocaleString()}
                          </div>
                        </div>
                      </div>
                    </BlueprintCard>
                  ))}

                  {alerts.filter(alert => alert.status === 'active').length === 0 && (
                    <div className="text-center py-4">
                      <CheckCircle className="w-8 h-8 mx-auto mb-2 text-green-600" />
                      <p className="text-[var(--muted)]">No active alerts</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Agent Performance */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="w-5 h-5" />
              Agent Performance
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {agentMetrics.map((agent) => (
                <div key={agent.agent_id} className="flex items-center justify-between p-4 border border-[var(--border)] rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className={getStatusColor(agent.status)}>
                      {getStatusIcon(agent.status)}
                    </div>
                    <div>
                      <h3 className="font-medium text-[var(--ink)]">{agent.agent_name}</h3>
                      <p className="text-sm text-[var(--muted)]">Status: {agent.status}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-[var(--muted)]">Success Rate</div>
                    <div className="text-lg font-semibold text-[var(--ink)]">{agent.success_rate}%</div>
                    <div className="text-xs text-[var(--muted)] mt-1">
                      {agent.execution_count} executions
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Workflow Performance */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Zap className="w-5 h-5" />
              Workflow Performance
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {workflowMetrics.map((workflow) => (
                <div key={workflow.workflow_id} className="flex items-center justify-between p-4 border border-[var(--border)] rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className={getStatusColor(workflow.status)}>
                      {getStatusIcon(workflow.status)}
                    </div>
                    <div>
                      <h3 className="font-medium text-[var(--ink)]">{workflow.workflow_name}</h3>
                      <p className="text-sm text-[var(--muted)]">Status: {workflow.status}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-[var(--muted)]">Success Rate</div>
                    <div className="text-lg font-semibold text-[var(--ink)]">{workflow.success_rate}%</div>
                    <div className="text-xs text-[var(--muted)] mt-1">
                      {workflow.total_executions} executions
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
