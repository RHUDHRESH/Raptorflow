/**
 * Main Navigation Component
 * Primary navigation for the Raptorflow application
 */
"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { BlueprintCard } from "@/components/ui/BlueprintCard"
import { BlueprintAvatar } from "@/components/ui/BlueprintAvatar"
import {
  Home,
  Brain,
  Zap,
  BarChart3,
  Settings,
  Users,
  Activity,
  Menu,
  X,
  Search,
  Bell,
  ChevronDown,
  LogOut,
  User
} from "lucide-react"

interface NavItem {
  id: string
  label: string
  href: string
  icon: React.ReactNode
  badge?: number
  children?: NavItem[]
}

interface User {
  name: string
  email: string
  avatar?: string
  role: string
}

export default function MainNavigation() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const [user, setUser] = useState<User | null>(null)
  const [notifications, setNotifications] = useState(3)
  const pathname = usePathname()

  useEffect(() => {
    // Load user data
    const loadUser = async () => {
      try {
        const response = await fetch('/api/user/profile')
        if (response.ok) {
          const userData = await response.json()
          setUser(userData)
        }
      } catch (error) {
        console.error('Failed to load user:', error)
      }
    }

    loadUser()
  }, [])

  const navigationItems: NavItem[] = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      href: '/dashboard',
      icon: <Home className="w-4 h-4" />
    },
    {
      id: 'agents',
      label: 'Agents',
      href: '/agents',
      icon: <Brain className="w-4 h-4" />,
      badge: 5
    },
    {
      id: 'workflows',
      label: 'Workflows',
      href: '/workflows',
      icon: <Zap className="w-4 h-4" />,
      badge: 3
    },
    {
      id: 'monitoring',
      label: 'Monitoring',
      href: '/monitoring',
      icon: <Activity className="w-4 h-4" />
    },
    {
      id: 'analytics',
      label: 'Analytics',
      href: '/analytics',
      icon: <BarChart3 className="w-4 h-4" />
    }
  ]

  const isActive = (href: string) => {
    if (!pathname) return false
    if (href === '/dashboard') return pathname === '/'
    return pathname.startsWith(href)
  }

  const handleLogout = async () => {
    try {
      await fetch('/api/auth/logout', { method: 'POST' })
      window.location.href = '/signin'
    } catch (error) {
      console.error('Logout failed:', error)
    }
  }

  return (
    <div className="min-h-screen bg-[#FFFEF9]">
      {/* Mobile Header */}
      <div className="lg:hidden">
        <div className="flex items-center justify-between p-4 border-b border-[#C0C1BE]">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            >
              <Menu className="w-5 h-5" />
            </Button>
            <h1 className="text-lg font-semibold text-[#2D3538]">Raptorflow</h1>
          </div>
          <div className="flex items-center gap-3">
            <div className="relative">
              <Button variant="ghost" size="sm">
                <Bell className="w-4 h-4" />
              </Button>
              {notifications > 0 && (
                <Badge className="absolute -top-1 -right-1 h-5 w-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center p-0">
                  {notifications}
                </Badge>
              )}
            </div>
            <Button variant="ghost" size="sm">
              <Settings className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Sidebar */}
      <div className={`fixed inset-y-0 left-0 z-50 w-64 bg-[#FFFEF9] border-r border-[#C0C1BE] transform transition-transform duration-300 ease-in-out lg:translate-x-0 ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}>
        <div className="flex flex-col h-full">
          {/* Sidebar Header */}
          <div className="flex items-center justify-between p-6 border-b border-[#C0C1BE]">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-[#2D3538] text-[#FFFEF9] rounded-lg flex items-center justify-center font-bold">
                R
              </div>
              <div>
                <h1 className="text-lg font-semibold text-[#2D3538]">Raptorflow</h1>
                <p className="text-xs text-[#9D9F9F]">AI Agent System</p>
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsSidebarOpen(false)}
              className="lg:hidden"
            >
              <X className="w-4 h-4" />
            </Button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4">
            <div className="space-y-2">
              {navigationItems.map((item) => (
                <Link
                  key={item.id}
                  href={item.href}
                  className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${isActive(item.href)
                      ? 'bg-[#2D3538] text-[#FFFEF9]'
                      : 'text-[#9D9F9F] hover:text-[#2D3538] hover:bg-[#FDFCFA]'
                    }`}
                  onClick={() => setIsSidebarOpen(false)}
                >
                  {item.icon}
                  <span className="flex-1">{item.label}</span>
                  {item.badge && (
                    <Badge className="bg-[#FDFCFA] text-[#2D3538] text-xs">
                      {item.badge}
                    </Badge>
                  )}
                </Link>
              ))}
            </div>
          </nav>

          {/* User Section */}
          <div className="border-t border-[#C0C1BE] p-4">
            {user ? (
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-[#2D3538] text-[#FFFEF9] rounded-full flex items-center justify-center font-semibold">
                  {user.name.charAt(0).toUpperCase()}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-[#2D3538] truncate">
                    {user.name}
                  </p>
                  <p className="text-xs text-[#9D9F9F] truncate">
                    {user.role}
                  </p>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleLogout}
                  title="Logout"
                >
                  <LogOut className="w-4 h-4" />
                </Button>
              </div>
            ) : (
              <div className="text-center">
                <Button variant="outline" size="sm" asChild>
                  <Link href="/signin">
                    <User className="w-4 h-4 mr-2" />
                    Login
                  </Link>
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Mobile Overlay */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Main Content */}
      <div className="lg:pl-64">
        {/* Desktop Header */}
        <div className="hidden lg:flex items-center justify-between p-4 border-b border-[#C0C1BE] bg-[#FFFEF9]">
          <div className="flex items-center gap-4">
            <div className="w-8 h-8 bg-[#2D3538] text-[#FFFEF9] rounded-lg flex items-center justify-center font-bold">
              R
            </div>
            <div>
              <h1 className="text-lg font-semibold text-[#2D3538]">Raptorflow</h1>
              <p className="text-xs text-[#9D9F9F]">AI Agent System</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="relative">
              <Button variant="ghost" size="sm">
                <Search className="w-4 h-4" />
              </Button>
            </div>
            <div className="relative">
              <Button variant="ghost" size="sm">
                <Bell className="w-4 h-4" />
              </Button>
              {notifications > 0 && (
                <Badge className="absolute -top-1 -right-1 h-5 w-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center p-0">
                  {notifications}
                </Badge>
              )}
            </div>
            <Button variant="ghost" size="sm">
              <Settings className="w-4 h-4" />
            </Button>
            {user && (
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-[#2D3538] text-[#FFFEF9] rounded-full flex items-center justify-center font-semibold">
                  {user.name.charAt(0).toUpperCase()}
                </div>
                <Button variant="ghost" size="sm">
                  <ChevronDown className="w-4 h-4" />
                </Button>
              </div>
            )}
          </div>
        </div>

        {/* Page Content */}
        <div className="min-h-[calc(100vh-73px)]">
          {/* This is where the page content will be rendered */}
          <div className="p-6">
            <div className="text-center py-12">
              <Brain className="w-16 h-16 mx-auto mb-4 text-[#9D9F9F]" />
              <h2 className="text-2xl font-semibold text-[#2D3538] mb-2">
                Welcome to Raptorflow
              </h2>
              <p className="text-[#9D9F9F] mb-6">
                Select a section from the navigation to get started
              </p>
              <div className="flex justify-center gap-4">
                <Button asChild>
                  <Link href="/dashboard">
                    <Home className="w-4 h-4 mr-2" />
                    Dashboard
                  </Link>
                </Button>
                <Button asChild>
                  <Link href="/agents">
                    <Brain className="w-4 h-4 mr-2" />
                    Agents
                  </Link>
                </Button>
                <Button asChild>
                  <Link href="/workflows">
                    <Zap className="w-4 h-4 mr-2" />
                    Workflows
                  </Link>
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
