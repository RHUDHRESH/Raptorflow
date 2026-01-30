'use client'

import React, { useState, useEffect } from 'react'
import { createBrowserClient } from '@supabase/ssr'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { BlueprintLoader } from '@/components/ui/BlueprintLoader'
import {
  Users,
  Activity,
  Shield,
  AlertTriangle,
  CheckCircle,
  XCircle,
  TrendingUp,
  TrendingDown,
  Clock,
  Globe,
  Server,
  Database,
  Mail,
  Settings,
  Eye,
  Ban,
  UserX,
  RefreshCw,
  Download,
  Filter,
  Search
} from 'lucide-react'

interface AdminStats {
  totalUsers: number
  activeUsers: number
  totalWorkspaces: number
  activeWorkspaces: number
  totalSessions: number
  securityEvents: number
  systemHealth: 'healthy' | 'warning' | 'critical'
  lastUpdated: string
}

interface User {
  id: string
  email: string
  full_name: string
  subscription_plan: string
  subscription_status: string
  created_at: string
  last_sign_in: string
  is_active: boolean
  mfa_enabled: boolean
  risk_score: number
}

interface SecurityEvent {
  id: string
  user_id: string
  event_type: string
  severity: string
  message: string
  ip_address: string
  created_at: string
  user?: {
    email: string
    full_name: string
  }
}

interface SystemMetric {
  name: string
  value: number
  unit: string
  status: 'good' | 'warning' | 'critical'
  trend: 'up' | 'down' | 'stable'
}

export default function AdminDashboard() {
  const [stats, setStats] = useState<AdminStats | null>(null)
  const [users, setUsers] = useState<User[]>([])
  const [securityEvents, setSecurityEvents] = useState<SecurityEvent[]>([])
  const [systemMetrics, setSystemMetrics] = useState<SystemMetric[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'overview' | 'users' | 'security' | 'metrics'>('overview')
  const [searchTerm, setSearchTerm] = useState('')
  const [filterStatus, setFilterStatus] = useState<'all' | 'active' | 'inactive'>('all')
  const supabase = createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    setLoading(true)
    try {
      const [statsData, usersData, eventsData, metricsData] = await Promise.all([
        fetchAdminStats(),
        fetchUsers(),
        fetchSecurityEvents(),
        fetchSystemMetrics()
      ])

      setStats(statsData)
      setUsers(usersData)
      setSecurityEvents(eventsData)
      setSystemMetrics(metricsData)
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchAdminStats = async (): Promise<AdminStats> => {
    const { data: profiles } = await supabase
      .from('profiles')
      .select('id, subscription_plan, subscription_status, last_sign_in, created_at')

    const { data: workspaces } = await supabase
      .from('workspaces')
      .select('id, is_active, created_at')

    const { data: sessions } = await supabase
      .from('user_sessions')
      .select('id, is_active, created_at')

    const { data: mfaUsers } = await supabase
      .from('user_mfa')
      .select('user_id, totp_enabled')

    const { count: securityCount } = await supabase
      .from('security_events')
      .select('id', { count: 'exact', head: true })
      .gte('created_at', new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString())

    const now = new Date()
    const activeUsers = profiles?.filter(p =>
      p.last_sign_in && new Date(p.last_sign_in) > new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
    ).length || 0

    const activeWorkspaces = workspaces?.filter(w => w.is_active).length || 0
    const activeSessions = sessions?.filter(s => s.is_active).length || 0
    const mfaEnabledCount = mfaUsers?.filter(m => m.totp_enabled).length || 0

    return {
      totalUsers: profiles?.length || 0,
      activeUsers,
      totalWorkspaces: workspaces?.length || 0,
      activeWorkspaces,
      totalSessions: sessions?.length || 0,
      securityEvents: securityCount || 0,
      systemHealth: 'healthy',
      lastUpdated: new Date().toISOString()
    }
  }

  const fetchUsers = async (): Promise<User[]> => {
    const { data } = await supabase
      .from('profiles')
      .select(`
        id,
        email,
        full_name,
        subscription_plan,
        subscription_status,
        created_at,
        last_sign_in,
        user_mfa (
          totp_enabled
        )
      `)
      .order('created_at', { ascending: false })
      .limit(50)

    return data?.map(user => ({
      ...user,
      is_active: user.last_sign_in && new Date(user.last_sign_in) > new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
      mfa_enabled: user.user_mfa?.[0]?.totp_enabled || false,
      risk_score: Math.floor(Math.random() * 100) // Placeholder - would calculate from actual data
    })) || []
  }

  const fetchSecurityEvents = async (): Promise<SecurityEvent[]> => {
    const { data } = await supabase
      .from('security_events')
      .select(`
        *,
        profiles (
          email,
          full_name
        )
      `)
      .order('created_at', { ascending: false })
      .limit(20)

    return data || []
  }

  const fetchSystemMetrics = async (): Promise<SystemMetric[]> => {
    // Placeholder metrics - would fetch from actual monitoring system
    return [
      { name: 'CPU Usage', value: 45, unit: '%', status: 'good', trend: 'stable' },
      { name: 'Memory', value: 67, unit: '%', status: 'good', trend: 'up' },
      { name: 'Disk Space', value: 78, unit: '%', status: 'warning', trend: 'up' },
      { name: 'Response Time', value: 245, unit: 'ms', status: 'good', trend: 'down' },
      { name: 'Error Rate', value: 0.2, unit: '%', status: 'good', trend: 'stable' },
      { name: 'Database Connections', value: 12, unit: '', status: 'good', trend: 'stable' }
    ]
  }

  const handleUserAction = async (userId: string, action: 'suspend' | 'activate' | 'impersonate') => {
    try {
      if (action === 'impersonate') {
        // Implement user impersonation
        console.log('Impersonating user:', userId)
      } else {
        const isActive = action === 'activate'
        await supabase
          .from('profiles')
          .update({ updated_at: new Date().toISOString() })
          .eq('id', userId)

        await fetchUsers()
      }
    } catch (error) {
      console.error('Error performing user action:', error)
    }
  }

  const filteredUsers = users.filter(user => {
    const matchesSearch = user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.full_name?.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = filterStatus === 'all' ||
                         (filterStatus === 'active' && user.is_active) ||
                         (filterStatus === 'inactive' && !user.is_active)
    return matchesSearch && matchesStatus
  })

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-600 bg-red-100'
      case 'high': return 'text-orange-600 bg-orange-100'
      case 'medium': return 'text-yellow-600 bg-yellow-100'
      case 'low': return 'text-blue-600 bg-blue-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const getHealthColor = (health: string) => {
    switch (health) {
      case 'healthy': return 'text-green-600'
      case 'warning': return 'text-yellow-600'
      case 'critical': return 'text-red-600'
      default: return 'text-gray-600'
    }
  }

  const getMetricIcon = (name: string) => {
    if (name.includes('CPU')) return <Server className="w-4 h-4" />
    if (name.includes('Memory')) return <Database className="w-4 h-4" />
    if (name.includes('Disk')) return <Server className="w-4 h-4" />
    if (name.includes('Response')) return <Clock className="w-4 h-4" />
    if (name.includes('Error')) return <AlertTriangle className="w-4 h-4" />
    return <Activity className="w-4 h-4" />
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-[var(--canvas)] flex items-center justify-center">
        <BlueprintLoader size="lg" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[var(--canvas)] p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-serif text-[var(--ink)]">Admin Dashboard</h1>
            <p className="text-[var(--muted)] mt-1">
              System overview and management
            </p>
          </div>
          <div className="flex items-center gap-4">
            <Button
              variant="outline"
              size="sm"
              onClick={fetchDashboardData}
              className="flex items-center gap-2"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="flex items-center gap-2"
            >
              <Download className="w-4 h-4" />
              Export
            </Button>
          </div>
        </div>

        {/* System Health Banner */}
        <Card className="border-[var(--border)]">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className={`w-3 h-3 rounded-full ${
                  stats?.systemHealth === 'healthy' ? 'bg-green-500' :
                  stats?.systemHealth === 'warning' ? 'bg-yellow-500' : 'bg-red-500'
                }`} />
                <span className="font-medium text-[var(--ink)]">
                  System Status: <span className={getHealthColor(stats?.systemHealth || 'healthy')}>
                    {stats?.systemHealth?.toUpperCase() || 'UNKNOWN'}
                  </span>
                </span>
              </div>
              <span className="text-sm text-[var(--muted)]">
                Last updated: {stats?.lastUpdated ? new Date(stats.lastUpdated).toLocaleString() : 'Never'}
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Navigation Tabs */}
        <div className="flex gap-1 border-b border-[var(--border)]">
          {[
            { id: 'overview', label: 'Overview', icon: <Activity className="w-4 h-4" /> },
            { id: 'users', label: 'Users', icon: <Users className="w-4 h-4" /> },
            { id: 'security', label: 'Security', icon: <Shield className="w-4 h-4" /> },
            { id: 'metrics', label: 'Metrics', icon: <TrendingUp className="w-4 h-4" /> }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-2 border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-[var(--blueprint)] text-[var(--ink)]'
                  : 'border-transparent text-[var(--muted)] hover:text-[var(--ink)]'
              }`}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { label: 'Total Users', value: stats?.totalUsers || 0, icon: <Users className="w-5 h-5" />, color: 'text-blue-600' },
              { label: 'Active Users', value: stats?.activeUsers || 0, icon: <CheckCircle className="w-5 h-5" />, color: 'text-green-600' },
              { label: 'Workspaces', value: stats?.totalWorkspaces || 0, icon: <Globe className="w-5 h-5" />, color: 'text-purple-600' },
              { label: 'Active Sessions', value: stats?.totalSessions || 0, icon: <Activity className="w-5 h-5" />, color: 'text-orange-600' },
              { label: 'Security Events', value: stats?.securityEvents || 0, icon: <Shield className="w-5 h-5" />, color: 'text-red-600' },
              { label: 'Active Workspaces', value: stats?.activeWorkspaces || 0, icon: <CheckCircle className="w-5 h-5" />, color: 'text-green-600' },
              { label: 'System Health', value: stats?.systemHealth || 'unknown', icon: <Activity className="w-5 h-5" />, color: getHealthColor(stats?.systemHealth || 'healthy') },
              { label: 'Response Time', value: '245ms', icon: <Clock className="w-5 h-5" />, color: 'text-blue-600' }
            ].map((stat, index) => (
              <Card key={index} className="border-[var(--border)]">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-[var(--muted)]">{stat.label}</p>
                      <p className={`text-2xl font-bold ${stat.color}`}>{stat.value}</p>
                    </div>
                    <div className={stat.color}>{stat.icon}</div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Users Tab */}
        {activeTab === 'users' && (
          <Card className="border-[var(--border)]">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>User Management</CardTitle>
                <div className="flex items-center gap-2">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-[var(--muted)]" />
                    <input
                      type="text"
                      placeholder="Search users..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10 pr-4 py-2 border border-[var(--border)] rounded-md bg-[var(--paper)] text-[var(--ink)] placeholder-[var(--muted)]"
                    />
                  </div>
                  <select
                    value={filterStatus}
                    onChange={(e) => setFilterStatus(e.target.value as any)}
                    className="px-3 py-2 border border-[var(--border)] rounded-md bg-[var(--paper)] text-[var(--ink)]"
                  >
                    <option value="all">All Users</option>
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                  </select>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-[var(--border)]">
                      <th className="text-left p-3 text-sm font-medium text-[var(--muted)]">User</th>
                      <th className="text-left p-3 text-sm font-medium text-[var(--muted)]">Plan</th>
                      <th className="text-left p-3 text-sm font-medium text-[var(--muted)]">Status</th>
                      <th className="text-left p-3 text-sm font-medium text-[var(--muted)]">MFA</th>
                      <th className="text-left p-3 text-sm font-medium text-[var(--muted)]">Risk</th>
                      <th className="text-left p-3 text-sm font-medium text-[var(--muted)]">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredUsers.map((user) => (
                      <tr key={user.id} className="border-b border-[var(--border)]">
                        <td className="p-3">
                          <div>
                            <p className="font-medium text-[var(--ink)]">{user.full_name || 'Unknown'}</p>
                            <p className="text-sm text-[var(--muted)]">{user.email}</p>
                          </div>
                        </td>
                        <td className="p-3">
                          <Badge variant="outline">{user.subscription_plan}</Badge>
                        </td>
                        <td className="p-3">
                          <Badge className={user.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
                            {user.is_active ? 'Active' : 'Inactive'}
                          </Badge>
                        </td>
                        <td className="p-3">
                          <Badge className={user.mfa_enabled ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'}>
                            {user.mfa_enabled ? 'Enabled' : 'Disabled'}
                          </Badge>
                        </td>
                        <td className="p-3">
                          <div className="flex items-center gap-2">
                            <div className={`w-2 h-2 rounded-full ${
                              user.risk_score < 30 ? 'bg-green-500' :
                              user.risk_score < 70 ? 'bg-yellow-500' : 'bg-red-500'
                            }`} />
                            <span className="text-sm text-[var(--ink)]">{user.risk_score}</span>
                          </div>
                        </td>
                        <td className="p-3">
                          <div className="flex items-center gap-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleUserAction(user.id, 'impersonate')}
                              className="flex items-center gap-1"
                            >
                              <Eye className="w-3 h-3" />
                              Impersonate
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleUserAction(user.id, user.is_active ? 'suspend' : 'activate')}
                              className="flex items-center gap-1"
                            >
                              {user.is_active ? <Ban className="w-3 h-3" /> : <CheckCircle className="w-3 h-3" />}
                              {user.is_active ? 'Suspend' : 'Activate'}
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Security Tab */}
        {activeTab === 'security' && (
          <Card className="border-[var(--border)]">
            <CardHeader>
              <CardTitle>Security Events</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {securityEvents.map((event) => (
                  <div key={event.id} className="flex items-start gap-4 p-4 border border-[var(--border)] rounded-lg">
                    <div className={`p-2 rounded-full ${getSeverityColor(event.severity)}`}>
                      <AlertTriangle className="w-4 h-4" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <h4 className="font-medium text-[var(--ink)]">{event.event_type}</h4>
                        <Badge className={getSeverityColor(event.severity)}>
                          {event.severity}
                        </Badge>
                      </div>
                      <p className="text-sm text-[var(--muted)] mt-1">{event.message}</p>
                      <div className="flex items-center gap-4 mt-2 text-xs text-[var(--muted)]">
                        <span>IP: {event.ip_address}</span>
                        <span>User: {event.user?.email || 'System'}</span>
                        <span>{new Date(event.created_at).toLocaleString()}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Metrics Tab */}
        {activeTab === 'metrics' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {systemMetrics.map((metric, index) => (
              <Card key={index} className="border-[var(--border)]">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                      <div className={`p-2 rounded-full ${
                        metric.status === 'good' ? 'bg-green-100 text-green-800' :
                        metric.status === 'warning' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {getMetricIcon(metric.name)}
                      </div>
                      <h3 className="font-medium text-[var(--ink)]">{metric.name}</h3>
                    </div>
                    <div className={`flex items-center gap-1 text-sm ${
                      metric.trend === 'up' ? 'text-red-600' :
                      metric.trend === 'down' ? 'text-green-600' : 'text-gray-600'
                    }`}>
                      {metric.trend === 'up' ? <TrendingUp className="w-3 h-3" /> :
                       metric.trend === 'down' ? <TrendingDown className="w-3 h-3" /> :
                       <Activity className="w-3 h-3" />}
                    </div>
                  </div>
                  <div className="flex items-baseline gap-2">
                    <span className="text-2xl font-bold text-[var(--ink)]">{metric.value}</span>
                    <span className="text-sm text-[var(--muted)]">{metric.unit}</span>
                  </div>
                  <div className="mt-2">
                    <div className="w-full bg-[var(--border)] rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${
                          metric.status === 'good' ? 'bg-green-500' :
                          metric.status === 'warning' ? 'bg-yellow-500' : 'bg-red-500'
                        }`}
                        style={{ width: `${Math.min(metric.value, 100)}%` }}
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
