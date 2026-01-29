'use client'

import { clientAuth } from '@/lib/auth-service'
import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import {
  Users,
  UserCheck,
  CreditCard,
  AlertCircle,
  TrendingUp,
  Search,
  Filter,
  Download,
  Eye,
  Edit,
  Ban,
  Shield
} from 'lucide-react'

interface DashboardStats {
  total_users: number
  active_users: number
  pending_payments: number
  active_subscriptions: number
  past_due_subscriptions: number
  daily_revenue: number
  weekly_revenue: number
  monthly_revenue: number
}

interface User {
  id: string
  email: string
  full_name: string | null
  role: string
  onboarding_status: string
  created_at: string
  last_login_at: string | null
  login_count: number
  is_banned: boolean
  is_active: boolean
}

export default function AdminDashboard() {
  const supabase = clientAuth.getSupabaseClient()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterRole, setFilterRole] = useState('all')
  const [filterStatus, setFilterStatus] = useState('all')

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      // Fetch dashboard stats
      const { data: statsData } = await supabase
        .from('admin_dashboard')
        .select('*')
        .single()

      if (statsData) {
        setStats(statsData)
      }

      // Fetch users
      const { data: usersData } = await supabase
        .from('users')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(100)

      if (usersData) {
        setUsers(usersData)
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredUsers = users.filter(user => {
    const matchesSearch = user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (user.full_name && user.full_name.toLowerCase().includes(searchTerm.toLowerCase()))
    const matchesRole = filterRole === 'all' || user.role === filterRole
    const matchesStatus = filterStatus === 'all' || user.onboarding_status === filterStatus

    return matchesSearch && matchesRole && matchesStatus
  })

  const handleImpersonateUser = async (userId: string) => {
    try {
      const { data, error } = await supabase.functions.invoke('admin-impersonate', {
        body: { targetUserId: userId }
      })

      if (error) throw error

      // Store impersonation token
      localStorage.setItem('impersonationToken', data.token)
      localStorage.setItem('originalUserId', data.originalUserId)

      // Redirect to user's view
      window.location.href = '/dashboard'
    } catch (error) {
      console.error('Error impersonating user:', error)
    }
  }

  const handleBanUser = async (userId: string, isBanned: boolean) => {
    try {
      const { error } = await supabase
        .from('users')
        .update({ is_banned: !isBanned })
        .eq('id', userId)

      if (error) throw error

      // Log admin action
      await supabase
        .from('admin_actions')
        .insert({
          action: isBanned ? 'unban_user' : 'ban_user',
          target_user_id: userId,
          details: { previous_state: isBanned }
        })

      fetchDashboardData()
    } catch (error) {
      console.error('Error updating user:', error)
    }
  }

  const getRoleBadgeVariant = (role: string) => {
    switch (role) {
      case 'super_admin': return 'destructive'
      case 'admin': return 'default'
      case 'billing_admin': return 'secondary'
      case 'support': return 'outline'
      default: return 'outline'
    }
  }

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case 'active': return 'default'
      case 'pending_payment': return 'destructive'
      case 'suspended': return 'secondary'
      default: return 'outline'
    }
  }

  if (loading) {
    return <div className="flex items-center justify-center h-64">Loading...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Admin Dashboard</h1>
          <p className="text-muted-foreground">Manage users and monitor system health</p>
        </div>
        <Button variant="outline">
          <Download className="w-4 h-4 mr-2" />
          Export Data
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Users</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_users || 0}</div>
            <p className="text-xs text-muted-foreground">
              +{stats?.active_users || 0} active this month
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Subscriptions</CardTitle>
            <CreditCard className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.active_subscriptions || 0}</div>
            <p className="text-xs text-destructive">
              {stats?.past_due_subscriptions || 0} past due
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Payments</CardTitle>
            <AlertCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.pending_payments || 0}</div>
            <p className="text-xs text-muted-foreground">
              Awaiting payment completion
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Monthly Revenue</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">₹{(stats?.monthly_revenue || 0).toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              +₹{(stats?.daily_revenue || 0).toLocaleString()} today
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Users Table */}
      <Card>
        <CardHeader>
          <CardTitle>Users</CardTitle>
          <CardDescription>Manage and monitor user accounts</CardDescription>
          <div className="flex gap-4 mt-4">
            <div className="flex-1">
              <Label htmlFor="search">Search</Label>
              <div className="relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  id="search"
                  placeholder="Search users..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-8"
                />
              </div>
            </div>
            <div>
              <Label htmlFor="role">Role</Label>
              <select
                id="role"
                value={filterRole}
                onChange={(e) => setFilterRole(e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              >
                <option value="all">All Roles</option>
                <option value="user">User</option>
                <option value="admin">Admin</option>
                <option value="super_admin">Super Admin</option>
                <option value="support">Support</option>
                <option value="billing_admin">Billing Admin</option>
              </select>
            </div>
            <div>
              <Label htmlFor="status">Status</Label>
              <select
                id="status"
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              >
                <option value="all">All Status</option>
                <option value="active">Active</option>
                <option value="pending_payment">Pending Payment</option>
                <option value="pending_workspace">Pending Workspace</option>
                <option value="suspended">Suspended</option>
              </select>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border">
            <div className="grid grid-cols-6 gap-4 p-4 font-medium border-b bg-muted/50">
              <div>User</div>
              <div>Role</div>
              <div>Status</div>
              <div>Last Login</div>
              <div>Login Count</div>
              <div>Actions</div>
            </div>
            {filteredUsers.map((user) => (
              <div key={user.id} className="grid grid-cols-6 gap-4 p-4 border-b items-center">
                <div>
                  <div className="font-medium">{user.email}</div>
                  {user.full_name && (
                    <div className="text-sm text-muted-foreground">{user.full_name}</div>
                  )}
                </div>
                <div>
                  <Badge variant={getRoleBadgeVariant(user.role)}>
                    {user.role.replace('_', ' ')}
                  </Badge>
                </div>
                <div>
                  <Badge variant={getStatusBadgeVariant(user.onboarding_status)}>
                    {user.onboarding_status.replace('_', ' ')}
                  </Badge>
                  {user.is_banned && (
                    <Badge variant="destructive" className="ml-1">
                      Banned
                    </Badge>
                  )}
                </div>
                <div className="text-sm text-muted-foreground">
                  {user.last_login_at
                    ? new Date(user.last_login_at).toLocaleDateString()
                    : 'Never'
                  }
                </div>
                <div className="text-sm">{user.login_count}</div>
                <div className="flex gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleImpersonateUser(user.id)}
                    title="Impersonate User"
                  >
                    <Eye className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleBanUser(user.id, user.is_banned)}
                    title={user.is_banned ? 'Unban User' : 'Ban User'}
                  >
                    <Ban className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    title="Edit User"
                  >
                    <Edit className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Security Alerts */}
      <Alert>
        <Shield className="h-4 w-4" />
        <AlertDescription>
          Last 24 hours: 5 failed login attempts detected, 2 suspicious activities flagged.
          <Button variant="link" className="p-0 ml-2">
            View Security Events
          </Button>
        </AlertDescription>
      </Alert>
    </div>
  )
}
