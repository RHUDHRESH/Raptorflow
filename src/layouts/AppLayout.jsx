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
  Command,
  Activity
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
import { NanobanaBackground } from '../components/ui/NanobanaBackground'

// Navigation "Command Center" Structure
const navSections = [
  {
    label: 'Command',
    items: [
      { name: 'Matrix', icon: LayoutDashboard, path: '/app/matrix', description: 'Daily dashboard' },
    ]
  },
  {
    label: 'Operations',
    items: [
      { name: 'Campaigns', icon: Layers, path: '/app/campaigns', description: 'Mission containers' },
      { name: 'Moves', icon: Zap, path: '/app/moves', description: 'Tactical strikes' },
      { name: 'Assets', icon: Sparkles, path: '/app/muse', description: 'Asset studio' },
    ]
  },
  {
    label: 'Intel',
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

  return (
    <SidebarProvider defaultOpen={true}>
      {/* 
        Nanobana Sidebar:
        - Glass/Blur background
        - Thin glowing borders
      */}
      <Sidebar variant="floating" collapsible="icon" className="border-r-0">
        <SidebarHeader className="bg-transparent pb-0">
          <div className="flex items-center gap-3 px-2 py-4" data-component-name="AppLayout">
            <RaptorFlowLogo size="sm" animated={true} linkTo="/app" />
            <span className="text-sm font-bold tracking-wider text-white">RAPTORFLOW</span>
          </div>
        </SidebarHeader>

        <SidebarContent className="px-2">
          {navSections.map((section) => (
            <SidebarGroup key={section.label} className="mt-4">
              <SidebarGroupLabel className="px-2 text-[10px] uppercase tracking-widest text-muted-foreground/60 font-mono">
                {section.label}
              </SidebarGroupLabel>
              <SidebarMenu>
                {section.items.map((item) => (
                  <SidebarMenuItem key={item.path}>
                    <SidebarMenuButton
                      asChild
                      isActive={location.pathname === item.path || location.pathname.startsWith(item.path + '/')}
                      tooltip={item.name}
                      className="text-muted-foreground hover:text-white hover:bg-white/5 data-[active=true]:bg-primary/10 data-[active=true]:text-primary data-[active=true]:shadow-glow-sm transition-all duration-300"
                    >
                      <NavLink to={item.path} end={item.path === '/app'}>
                        <item.icon strokeWidth={1.5} className="w-4 h-4" />
                        <span className="font-medium tracking-tight">{item.name}</span>
                        {item.badge && (
                          <span className="ml-auto px-1.5 py-0.5 text-[9px] bg-white/10 text-white rounded-full font-mono">
                            {item.badge}
                          </span>
                        )}
                      </NavLink>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                ))}
              </SidebarMenu>
            </SidebarGroup>
          ))}
        </SidebarContent>

        <SidebarFooter className="p-4">
          <div className="p-1 space-y-1">
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton asChild tooltip="Settings" className="text-muted-foreground hover:text-white hover:bg-white/5">
                  <button onClick={() => navigate('/app/settings')}>
                    <Settings strokeWidth={1.5} className="w-4 h-4" />
                    <span>Settings</span>
                  </button>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton asChild tooltip="Sign Out" className="text-muted-foreground hover:text-red-400 hover:bg-red-500/10">
                  <button onClick={handleSignOut}>
                    <LogOut strokeWidth={1.5} className="w-4 h-4" />
                    <span>Sign Out</span>
                  </button>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </div>
        </SidebarFooter>
        <SidebarRail />
      </Sidebar>

      <SidebarInset className="bg-black/95 relative overflow-hidden">
        {/* Nanobana Background System */}
        <NanobanaBackground variant="void" intensity="low" />

        {/* Top HUD Bar */}
        <header className="h-16 flex items-center justify-between px-6 sticky top-0 z-40 border-b border-white/5 bg-black/50 backdrop-blur-md">
          <div className="flex items-center gap-4">
            <SidebarTrigger className="h-8 w-8 text-muted-foreground hover:text-white transition-colors" />

            {/* Command Search */}
            <div className="relative group">
              <div className="absolute -inset-0.5 bg-gradient-to-r from-primary/20 to-purple-600/20 rounded-lg opacity-0 group-hover:opacity-100 transition duration-500 blur-sm" />
              <button aria-label="Search" className="relative flex items-center gap-2 px-4 py-2 bg-black/40 border border-white/10 rounded-lg text-muted-foreground hover:text-white transition-all duration-200 w-64">
                <Search className="w-3.5 h-3.5" strokeWidth={1.5} />
                <span className="text-xs font-mono">SEARCH COMMANDS...</span>
                <kbd className="ml-auto px-1.5 bg-white/5 rounded text-[10px] text-muted-foreground font-mono border border-white/10">⌘K</kbd>
              </button>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <ThemeToggle />

            {/* Notifications HUD */}
            <div className="relative" ref={notificationsRef}>
              <button
                type="button"
                className="relative p-2 text-muted-foreground hover:text-primary transition-colors"
                onClick={() => setNotificationsOpen((v) => !v)}
              >
                <Bell className="w-5 h-5" strokeWidth={1.5} />
                {notifications.some((n) => n.unread) && (
                  <span className="absolute top-1.5 right-2 w-1.5 h-1.5 bg-primary rounded-full shadow-[0_0_8px_var(--primary)] animate-pulse" />
                )}
              </button>

              {notificationsOpen && (
                <div className="absolute right-0 mt-4 w-[380px] bg-[#0A0A0F] border border-white/10 rounded-xl shadow-2xl p-0 z-50 overflow-hidden ring-1 ring-white/5">
                  <div className="px-4 py-3 flex items-center justify-between border-b border-white/5 bg-white/2">
                    <div className="text-sm font-medium text-white tracking-wide">NOTIFICATIONS</div>
                    {notifications.some((n) => n.unread) && (
                      <span className="text-[10px] bg-primary/20 text-primary px-2 py-0.5 rounded-full font-mono">
                        {notifications.filter((n) => n.unread).length} NEW
                      </span>
                    )}
                  </div>

                  <div className="max-h-[320px] overflow-auto custom-scrollbar">
                    {/* Notifications List Logic same as before but styled darker */}
                    {notifications.length === 0 ? (
                      <div className="p-8 text-center text-muted-foreground text-xs">No signals detected.</div>
                    ) : (
                      notifications.map((n) => (
                        <div key={n.id} onClick={() => markRead(n.id)} className="p-3 hover:bg-white/5 cursor-pointer border-b border-white/5 last:border-0 transition-colors group">
                          <div className="flex justify-between items-start mb-1">
                            <span className={`text-xs font-medium ${n.unread ? 'text-white' : 'text-muted-foreground'} group-hover:text-primary transition-colors`}>{n.title}</span>
                            <span className="text-[10px] text-muted-foreground font-mono">{formatRelativeTime(n.createdAt)}</span>
                          </div>
                          <p className="text-[11px] text-muted-foreground/80 line-clamp-2">{n.detail}</p>
                        </div>
                      ))
                    )}
                  </div>

                  <div className="p-2 border-t border-white/5 bg-white/2 grid grid-cols-2 gap-2">
                    <button onClick={markAllRead} className="flex items-center justify-center gap-2 py-1.5 text-[10px] font-medium text-muted-foreground hover:text-white hover:bg-white/5 rounded transition-colors">
                      <Sparkles className="w-3 h-3" /> MARK ALL READ
                    </button>
                    <button onClick={clearNotifications} className="flex items-center justify-center gap-2 py-1.5 text-[10px] font-medium text-muted-foreground hover:text-white hover:bg-white/5 rounded transition-colors">
                      <X className="w-3 h-3" /> CLEAR LOG
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Profile Pill */}
            <button
              onClick={() => navigate('/app/settings')}
              className="flex items-center gap-3 pl-3 pr-1 py-1 bg-white/5 hover:bg-white/10 border border-white/5 rounded-full transition-all group"
            >
              <span className="text-xs font-medium text-white group-hover:text-primary transition-colors">
                {profile?.full_name?.split(' ')[0] || 'Commander'}
              </span>
              <div className="w-7 h-7 rounded-full bg-gradient-to-br from-primary to-purple-600 flex items-center justify-center text-[10px] font-bold text-black border border-white/20">
                {profile?.full_name?.[0] || 'U'}
              </div>
            </button>
          </div>
        </header>

        {/* Content Area - Full Bleed */}
        <div className="relative z-10 w-full h-[calc(100vh-4rem)] overflow-auto scrollbar-hide">
          <Outlet />
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}

export default AppLayout
