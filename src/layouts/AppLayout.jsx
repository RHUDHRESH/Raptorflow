import React from 'react'
import { NavLink, Outlet, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import useRaptorflowStore from '../store/raptorflowStore'
import useNotificationsStore from '../store/notificationsStore'
import {
  LayoutDashboard,
  Zap,
  Sparkles,
  Target,
  Users,
  Settings,
  LogOut,
  Bell,
  X,
  Search,
  Layers,
  Radio,
  Box,
  Command
} from 'lucide-react'
import ThemeToggle from '../components/ui/ThemeToggle'
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarInset,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarRail,
  SidebarTrigger,
} from '../components/ui/sidebar'
import { RaptorFlowLogo } from '../components/brand/Logo'

// Navigation organized by hierarchy - Editorial styling
// Based on spec: Matrix, Campaigns, Moves, Radar, Lab, Settings
const navSections = [
  {
    label: 'Command',
    items: [
      { name: 'Matrix', icon: LayoutDashboard, path: '/app/matrix', description: 'Daily dashboard' },
    ]
  },
  {
    label: 'Strategy',
    items: [
      { name: 'Campaigns', icon: Layers, path: '/app/campaigns', description: 'Mission containers' },
      { name: 'Moves', icon: Zap, path: '/app/moves', description: 'Tactical strikes' },
      { name: 'Muse', icon: Sparkles, path: '/app/muse', description: 'Asset studio' },
    ]
  },
  {
    label: 'Intelligence',
    items: [
      { name: 'Radar', icon: Radio, path: '/app/radar', description: 'Trend scanner' },
      { name: 'Signals', icon: Target, path: '/app/signals', description: 'Leverage map' },
      { name: 'Lab', icon: Box, path: '/app/black-box', description: 'A/B Duels' },
    ]
  }
]

const AppLayout = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { profile, signOut } = useAuth()
  const { getPlanLimits } = useRaptorflowStore()
  const {
    notifications,
    markRead,
    markAllRead,
    clearNotifications,
    removeNotification,
    toastsEnabled,
    setToastsEnabled,
    seedDemoNotifications,
  } = useNotificationsStore()

  const [unreadOnly, setUnreadOnly] = React.useState(false)

  const notificationsRef = React.useRef(null)
  const [notificationsOpen, setNotificationsOpen] = React.useState(false)

  const handleSignOut = async () => {
    await signOut()
    navigate('/')
  }

  React.useEffect(() => {
    seedDemoNotifications()
  }, [seedDemoNotifications])

  const formatRelativeTime = (iso) => {
    if (!iso) return ''
    const ms = Date.now() - new Date(iso).getTime()
    if (!Number.isFinite(ms)) return ''

    const min = Math.floor(ms / 60000)
    if (min < 1) return 'just now'
    if (min < 60) return `${min}m`

    const hr = Math.floor(min / 60)
    if (hr < 24) return `${hr}h`

    const d = Math.floor(hr / 24)
    return `${d}d`
  }

  React.useEffect(() => {
    if (!notificationsOpen) return

    const handlePointerDown = (e) => {
      if (!notificationsRef.current) return
      if (notificationsRef.current.contains(e.target)) return
      setNotificationsOpen(false)
    }

    const handleKeyDown = (e) => {
      if (e.key === 'Escape') setNotificationsOpen(false)
    }

    document.addEventListener('mousedown', handlePointerDown)
    document.addEventListener('keydown', handleKeyDown)
    return () => {
      document.removeEventListener('mousedown', handlePointerDown)
      document.removeEventListener('keydown', handleKeyDown)
    }
  }, [notificationsOpen])

  // Get user's plan info from store or profile
  const planLimits = getPlanLimits()
  const planName = planLimits?.name || profile?.plan || 'Glide'

  const isFullBleedPage = location.pathname === '/app/muse'

  return (
    <SidebarProvider defaultOpen={true}>
      <Sidebar variant="inset">
        <SidebarHeader>
          <div className="flex items-center gap-3 px-2 py-2" data-component-name="AppLayout">
            <RaptorFlowLogo size="sm" animated={false} linkTo="/app" />
          </div>
        </SidebarHeader>

        <SidebarContent>
          {navSections.map((section) => (
            <SidebarGroup key={section.label}>
              <SidebarGroupLabel className="px-2 font-serif text-[11px] tracking-wide text-ink-400">
                {section.label}
              </SidebarGroupLabel>
              <SidebarMenu>
                {section.items.map((item) => (
                  <SidebarMenuItem key={item.path}>
                    <SidebarMenuButton
                      asChild
                      isActive={location.pathname === item.path || location.pathname.startsWith(item.path + '/')}
                      tooltip={item.name}
                      className="text-ink-500 hover:text-ink"
                    >
                      <NavLink to={item.path} end={item.path === '/app'}>
                        <item.icon strokeWidth={1.5} />
                        <span>{item.name}</span>
                        {item.badge && (
                          <span className="ml-auto px-1.5 py-0.5 text-[9px] bg-paper-200 text-ink-400 rounded">
                            {item.badge}
                          </span>
                        )}
                        {item.isNew && (
                          <span className="ml-auto w-2 h-2 bg-ink-300 rounded-full" />
                        )}
                      </NavLink>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                ))}
              </SidebarMenu>
            </SidebarGroup>
          ))}
        </SidebarContent>

        <SidebarFooter>
          {/* Bottom section */}
          <div className="p-2 space-y-1">
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton asChild tooltip="Settings">
                  <button onClick={() => navigate('/app/settings')}>
                    <Settings strokeWidth={1.5} />
                    <span>Settings</span>
                  </button>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton asChild tooltip="Sign Out">
                  <button onClick={handleSignOut}>
                    <LogOut strokeWidth={1.5} />
                    <span>Sign Out</span>
                  </button>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </div>
        </SidebarFooter>

        <SidebarRail />
      </Sidebar>

      <SidebarInset className="main-inset-saas">
        {/* Top bar - Premium SaaS styling */}
        <header className="h-16 header-saas flex items-center justify-between px-6 sticky top-0 z-40">
          <div className="flex items-center gap-4">
            <SidebarTrigger className="h-8 w-8 text-muted-foreground hover:text-foreground transition-colors" />
            {/* Search */}
            <div className="relative">
              <button aria-label="Search" className="flex items-center gap-2 px-4 py-2.5 bg-muted/50 border border-border/50 rounded-xl text-muted-foreground hover:text-foreground hover:border-border hover:bg-muted transition-all duration-200">
                <Search className="w-4 h-4" strokeWidth={1.5} />
                <span className="text-sm">Search...</span>
                <kbd className="ml-4 px-2 py-0.5 bg-background/80 rounded-md text-[10px] text-muted-foreground font-medium border border-border/50">⌘K</kbd>
              </button>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Theme Toggle */}
            <ThemeToggle />

            <div className="relative" ref={notificationsRef}>
              <button
                type="button"
                aria-label="Notifications"
                aria-haspopup="menu"
                aria-expanded={notificationsOpen}
                onClick={() => setNotificationsOpen((v) => !v)}
                className="relative p-2.5 text-muted-foreground hover:text-foreground transition-all duration-200 rounded-xl hover:bg-muted/50"
              >
                <Bell className="w-5 h-5" strokeWidth={1.5} />
                {notifications.some((n) => n.unread) && (
                  <span className="absolute top-2 right-2 w-2 h-2 bg-primary rounded-full ring-2 ring-background" />
                )}
              </button>

              {notificationsOpen && (
                <div
                  role="menu"
                  aria-label="Notifications"
                  className="absolute right-0 mt-2 w-[380px] bg-card border border-border rounded-2xl shadow-2xl p-3 z-50 dark:bg-[hsl(213_28%_14%)] dark:border-[hsl(213_28%_24%)]"
                >
                  <div className="px-2 py-2 flex items-center justify-between gap-3">
                    <div className="text-ink font-serif">Notifications</div>
                    {notifications.some((n) => n.unread) && (
                      <div className="text-[11px] text-ink-400">
                        {notifications.filter((n) => n.unread).length} unread
                      </div>
                    )}
                  </div>
                  <div className="h-px bg-border-light my-1" />

                  <div className="px-2 pb-2 flex items-center justify-between gap-2">
                    <button
                      type="button"
                      onClick={() => setUnreadOnly((v) => !v)}
                      className="px-2 py-1 bg-paper-200 border border-border-light rounded-editorial text-[11px] text-ink-400 hover:text-ink hover:border-border transition-editorial"
                    >
                      {unreadOnly ? 'Showing: Unread' : 'Showing: All'}
                    </button>
                    <button
                      type="button"
                      onClick={() => setToastsEnabled(!toastsEnabled)}
                      className="px-2 py-1 bg-paper-200 border border-border-light rounded-editorial text-[11px] text-ink-400 hover:text-ink hover:border-border transition-editorial"
                    >
                      Toasts: {toastsEnabled ? 'On' : 'Off'}
                    </button>
                  </div>

                  {unreadOnly && notifications.every((n) => !n.unread) && (
                    <div className="px-3 py-3 text-body-sm text-ink-400">
                      No unread notifications.
                    </div>
                  )}

                  {(unreadOnly ? notifications.filter((n) => n.unread) : notifications).length === 0 ? (
                    <div className="px-3 py-6 text-center text-body-sm text-ink-400">
                      All quiet for now.
                    </div>
                  ) : (
                    <div className="max-h-[320px] overflow-auto">
                      {(unreadOnly ? notifications.filter((n) => n.unread) : notifications).map((n) => (
                        <div
                          key={n.id}
                          role="menuitem"
                          tabIndex={0}
                          onClick={() => {
                            markRead(n.id)
                            if (n.href) {
                              setNotificationsOpen(false)
                              navigate(n.href)
                            }
                          }}
                          onKeyDown={(e) => {
                            if (e.key !== 'Enter' && e.key !== ' ') return
                            e.preventDefault()
                            markRead(n.id)
                            if (n.href) {
                              setNotificationsOpen(false)
                              navigate(n.href)
                            }
                          }}
                          className="w-full text-left rounded-editorial px-3 py-2 hover:bg-paper-200 transition-editorial cursor-pointer outline-none"
                        >
                          <div className="flex items-start justify-between gap-3">
                            <div className="min-w-0">
                              <div className="flex items-start gap-2">
                                <div className="text-body-sm text-ink leading-snug truncate">{n.title}</div>
                                {n.unread && (
                                  <span className="mt-1 w-2 h-2 bg-ink-300 rounded-full flex-shrink-0" />
                                )}
                              </div>
                              <div className="text-body-xs text-ink-400 mt-1 leading-snug">{n.detail}</div>
                            </div>
                            <div className="flex items-start gap-2 flex-shrink-0">
                              <div className="text-[10px] text-ink-400 mt-0.5">{formatRelativeTime(n.createdAt)}</div>
                              <button
                                type="button"
                                aria-label="Dismiss"
                                onClick={(e) => {
                                  e.preventDefault()
                                  e.stopPropagation()
                                  removeNotification(n.id)
                                }}
                                className="p-1 rounded-editorial text-ink-400 hover:text-ink hover:bg-paper-300 transition-editorial"
                              >
                                <X className="w-4 h-4" strokeWidth={1.5} />
                              </button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  <div className="h-px bg-border-light my-1" />

                  <button
                    type="button"
                    role="menuitem"
                    onClick={() => {
                      markAllRead()
                    }}
                    className="w-full text-left rounded-editorial px-3 py-2 hover:bg-paper-200 transition-editorial flex items-center gap-2 text-body-sm text-ink"
                  >
                    <Sparkles className="w-4 h-4" strokeWidth={1.5} />
                    Mark all as read
                  </button>

                  <button
                    type="button"
                    role="menuitem"
                    onClick={() => {
                      clearNotifications()
                    }}
                    className="w-full text-left rounded-editorial px-3 py-2 hover:bg-paper-200 transition-editorial text-body-sm text-ink"
                  >
                    Clear all
                  </button>

                  <button
                    type="button"
                    role="menuitem"
                    onClick={() => {
                      setNotificationsOpen(false)
                      navigate('/app/matrix')
                    }}
                    className="w-full text-left rounded-editorial px-3 py-2 hover:bg-paper-200 transition-editorial text-body-sm text-ink"
                  >
                    View activity
                  </button>
                </div>
              )}
            </div>

            {/* Account + plan */}
            <button
              aria-label="Account and plan"
              onClick={() => navigate('/app/settings')}
              className="flex items-center gap-2.5 px-3 py-2 bg-muted/50 border border-border/50 rounded-xl hover:border-border hover:bg-muted transition-all duration-200"
            >
              <div className="w-8 h-8 bg-gradient-to-br from-primary/20 to-primary/10 border border-primary/20 rounded-lg flex items-center justify-center flex-shrink-0">
                <span className="text-foreground text-sm font-medium">
                  {profile?.full_name?.[0] || profile?.email?.[0]?.toUpperCase() || 'U'}
                </span>
              </div>
              <span className="text-sm text-foreground max-w-[120px] truncate">
                {profile?.full_name?.split(' ')?.[0] || 'Account'}
              </span>
              <span className="badge-saas badge-saas-warning text-[10px] py-0.5">
                {planName}
              </span>
            </button>
          </div>
        </header>

        {/* Page content */}
        {isFullBleedPage ? (
          <Outlet />
        ) : (
          <div className="p-6">
            <Outlet />
          </div>
        )}
      </SidebarInset>
    </SidebarProvider>
  )
}

export default AppLayout
