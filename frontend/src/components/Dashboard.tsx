/**
 * Main Dashboard Component
 * Central hub for Raptorflow agent system
 */
"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { BlueprintCard } from "@/components/ui/BlueprintCard"
import { BlueprintKPI } from "@/components/ui/BlueprintKPI"
import { BlueprintProgress } from "@/components/ui/BlueprintProgress"
import { BlueprintAvatar } from "@/components/ui/BlueprintAvatar"
import { BlueprintLoader } from "@/components/ui/BlueprintLoader"
import { PageHeader } from "@/components/ui/PageHeader"
import {
  Brain,
  Zap,
  TrendingUp,
  Users,
  Activity,
  AlertTriangle,
  CheckCircle,
  Clock,
  MessageSquare,
  BarChart3,
  Settings,
  Plus,
  ArrowRight
} from "lucide-react"

interface DashboardStats {
  totalAgents: number
  activeAgents: number
  totalWorkflows: number
  activeWorkflows: number
  totalRequests: number
  successRate: number
  averageResponseTime: number
  systemHealth: "healthy" | "warning" | "critical"
}

interface RecentActivity {
  id: string
  type: "agent" | "workflow" | "system"
  title: string
  description: string
  timestamp: string
  status: "success" | "warning" | "error"
}

interface AgentCard {
  id: string
  name: string
  description: string
  status: "active" | "idle" | "error"
  category: string
  lastUsed: string
  performance: number
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([])
  const [agents, setAgents] = useState<AgentCard[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    setLoading(true)
    try {
      // Load dashboard stats
      const statsResponse = await fetch('/api/dashboard/stats')
      const statsData = await statsResponse.json()
      setStats(statsData)

      // Load recent activity
      const activityResponse = await fetch('/api/dashboard/activity')
      const activityData = await activityResponse.json()
      setRecentActivity(activityData)

      // Load agent cards
      const agentsResponse = await fetch('/api/agents')
      const agentsData = await agentsResponse.json()
      setAgents(agentsData)
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'text-green-600 bg-green-50 border-green-200'
      case 'warning': return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      case 'error': return 'text-red-600 bg-red-50 border-red-200'
      default: return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'agent': return <Brain className="w-4 h-4" />
      case 'workflow': return <Zap className="w-4 h-4" />
      case 'system': return <Activity className="w-4 h-4" />
      default: return <MessageSquare className="w-4 h-4" />
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-[var(--paper)] p-6 flex items-center justify-center">
        <div className="text-center space-y-4">
          <BlueprintLoader size="lg" />
          <p className="font-mono text-xs text-[var(--muted)] animate-pulse">
            INITIALIZING SYSTEM DASHBOARD...
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[var(--paper)] p-6 pb-24">
      <div className="max-w-[1600px] mx-auto space-y-8">

        {/* Header - Strictly aligned */}
        <PageHeader
          moduleCode="DASHBOARD"
          descriptor="SYSTEM OVERVIEW"
          title="Command Center"
          subtitle="Real-time monitoring and control of autonomous agent systems."
          actions={
            <div className="flex items-center gap-3">
              <Button variant="outline" size="sm" className="h-9 border-[var(--border)] gap-2">
                <Settings className="w-4 h-4" />
                Config
              </Button>
              <Button size="sm" className="h-9 bg-[var(--ink)] text-white gap-2 hover:bg-[var(--ink)]/90">
                <Plus className="w-4 h-4" />
                Deploy Agent
              </Button>
            </div>
          }
        />

        {/* KPI Grid - 4 Columns strict */}
        {stats && (
          <section className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
            <BlueprintKPI
              label="Active Agents"
              value={stats.activeAgents}
              unit="ONLINE"
              code="KPI-01"
              figure="FIG 1.1"
              trend="up"
              trendValue="+12%"
              className="h-full"
            />
            <BlueprintKPI
              label="Active Workflows"
              value={stats.activeWorkflows}
              unit="RUNNING"
              code="KPI-02"
              figure="FIG 1.2"
              trend="up"
              trendValue="+8.4%"
              className="h-full"
            />
            <BlueprintKPI
              label="Success Rate"
              value={stats.successRate}
              unit="%"
              code="KPI-03"
              figure="FIG 1.3"
              trend="up"
              trendValue="+2.1%"
              className="h-full"
            />
            <BlueprintKPI
              label="System Latency"
              value={stats.averageResponseTime}
              unit="MS"
              code="KPI-04"
              figure="FIG 1.4"
              trend="down" // Down is good for latency, but component defaults red for down. Might need override or context.
              trendValue="-15ms"
              className="h-full"
            />
          </section>
        )}

        {/* Main Content Grid - 12 Column System */}
        <div className="grid grid-cols-12 gap-6">

          {/* System Health (Span 8) */}
          <div className="col-span-12 xl:col-span-8 space-y-6">
            {/* Health Status Bar */}
            {stats && (
              <BlueprintCard
                className="p-6 flex items-center gap-6"
                variant="default"
              >
                <div className="flex items-center gap-3 min-w-[180px]">
                  <Activity className={cn(
                    "w-5 h-5",
                    stats.systemHealth === 'healthy' ? "text-green-600" : "text-yellow-600"
                  )} />
                  <div>
                    <h3 className="text-sm font-bold uppercase tracking-wide text-[var(--ink)]">System Health</h3>
                    <p className={cn(
                      "text-xs font-mono uppercase",
                      stats.systemHealth === 'healthy' ? "text-green-600" : "text-yellow-600"
                    )}>
                      {stats.systemHealth}
                    </p>
                  </div>
                </div>

                <div className="flex-1 space-y-2">
                  <div className="flex justify-between text-[10px] font-mono text-[var(--muted)] uppercase">
                    <span>Resources</span>
                    <span>98% Optimal</span>
                  </div>
                  <BlueprintProgress
                    value={98}
                    className="h-1.5"
                    indicatorClassName={stats.systemHealth === 'healthy' ? "bg-green-600" : "bg-yellow-500"}
                  />
                </div>
              </BlueprintCard>
            )}

            {/* Agent Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {agents.map((agent) => (
                <BlueprintCard
                  key={agent.id}
                  variant="default"
                  showCorners={true}
                  className="p-5 group hover:border-[var(--blueprint)] transition-colors cursor-pointer"
                >
                  <div className="flex justify-between items-start mb-4">
                    <BlueprintAvatar
                      initials={agent.name.substring(0, 2)}
                      className="bg-[var(--surface-subtle)] text-[var(--ink)] border border-[var(--border)]"
                    />
                    <Badge variant={agent.status === 'active' ? 'default' : 'secondary'} className="rounded-sm font-mono text-[10px]">
                      {agent.status}
                    </Badge>
                  </div>

                  <h3 className="font-serif text-lg text-[var(--ink)] group-hover:text-[var(--blueprint)] transition-colors">
                    {agent.name}
                  </h3>
                  <p className="text-sm text-[var(--muted)] line-clamp-2 mt-1 mb-4 min-h-[40px]">
                    {agent.description}
                  </p>

                  <div className="flex items-center justify-between pt-4 border-t border-[var(--border-subtle)]">
                    <span className="text-[10px] font-mono text-[var(--muted)] uppercase tracking-wider">
                      PERF: {agent.performance}%
                    </span>
                    <ArrowRight className="w-4 h-4 text-[var(--muted)] group-hover:text-[var(--blueprint)] transition-transform group-hover:translate-x-1" />
                  </div>
                </BlueprintCard>
              ))}
            </div>
          </div>

          {/* Sidebar / Activity (Span 4) */}
          <div className="col-span-12 xl:col-span-4 space-y-6">
            <BlueprintCard title="Recent Activity" code="LOG-01" className="h-full">
              <div className="space-y-4">
                {recentActivity.map((activity, idx) => (
                  <div key={activity.id} className="relative pl-6 pb-4 border-l border-[var(--border-subtle)] last:border-0 last:pb-0">
                    <div className={cn(
                      "absolute -left-[5px] top-0 w-2.5 h-2.5 rounded-full border-2 border-[var(--paper)]",
                      activity.status === 'success' ? "bg-green-500" : "bg-yellow-500"
                    )} />

                    <span className="text-[10px] font-mono text-[var(--muted)] block mb-0.5">
                      {activity.timestamp}
                    </span>
                    <h4 className="text-sm font-medium text-[var(--ink)]">
                      {activity.title}
                    </h4>
                    <p className="text-xs text-[var(--ink-secondary)] mt-0.5 line-clamp-1">
                      {activity.description}
                    </p>
                  </div>
                ))}
              </div>
            </BlueprintCard>
          </div>

        </div>
      </div>
    </div>
  )
}

function cn(...classes: (string | undefined | null | false)[]) {
  return classes.filter(Boolean).join(" ");
}
