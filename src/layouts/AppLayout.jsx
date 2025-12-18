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
import { Input } from '../components/ui/input'
import { ScrollArea } from '../components/ui/scroll-area'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../components/ui/dropdown-menu'
import { Avatar, AvatarFallback } from '../components/ui/avatar'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '../components/ui/dialog'
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarInset,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarRail,
  SidebarSeparator,
  SidebarTrigger,
} from '../components/ui/sidebar'
import { RaptorFlowLogo } from '../components/brand/Logo'
import { NanobanaBackground } from '../components/ui/NanobanaBackground'

// Navigation "Command Center" Structure
const navSections = [
  {
    label: 'Core',
    items: [
      { name: 'Matrix', icon: LayoutDashboard, path: '/app/matrix', description: 'Daily dashboard' },
      { name: 'Radar', icon: Radio, path: '/app/radar', description: 'Trend scanner' },
    ]
  },
  {
    label: 'Execution',
    items: [
      { name: 'Campaigns', icon: Layers, path: '/app/campaigns', description: 'Mission containers' },
      { name: 'Moves', icon: Zap, path: '/app/moves', description: 'Tactical strikes' },
      { name: 'Muse', icon: Sparkles, path: '/app/muse', description: 'Asset studio' },
    ]
  },
  {
    label: 'Foundation',
    items: [
      { name: 'Strategy', icon: Target, path: '/onboarding/strategy', description: 'Your growth doctrine' },
      { name: 'ICP', icon: Users, path: '/onboarding/icps', description: 'Ideal customer profiles' },
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
  const [commandOpen, setCommandOpen] = React.useState(false)
  const [commandQuery, setCommandQuery] = React.useState('')

  const handleSignOut = async () => {
    await signOut()
    navigate('/')
  }

  React.useEffect(() => {
    seedDemoNotifications()
  }, [seedDemoNotifications])

  React.useEffect(() => {
    const onKeyDown = (e) => {
      const isMac = navigator.platform.toLowerCase().includes('mac')
      const mod = isMac ? e.metaKey : e.ctrlKey
      if (!mod) return
      if (e.key.toLowerCase() !== 'k') return
      e.preventDefault()
      setCommandOpen(true)
    }

    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [])

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

  const commandItems = React.useMemo(() => {
    const items = navSections.flatMap((s) => s.items)
    return items
      .map((i) => ({
        label: i.name,
        path: i.path,
        icon: i.icon,
        section: i.description,
      }))
      .filter(Boolean)
  }, [])

  const filteredCommandItems = React.useMemo(() => {
    const q = String(commandQuery || '').trim().toLowerCase()
    if (!q) return commandItems
    return commandItems.filter((i) => {
      const hay = `${i.label} ${i.section || ''} ${i.path}`.toLowerCase()
      return hay.includes(q)
    })
  }, [commandItems, commandQuery])

  return (
    <SidebarProvider defaultOpen={true}>
      {/* 
        Nanobana Sidebar:
        - Glass/Blur background
        - Thin glowing borders
      */}
      <Sidebar variant="floating" collapsible="icon" className="border-r-0">
        <SidebarHeader>
          <SidebarMenu>
            <SidebarMenuItem>
              <SidebarMenuButton
                asChild
                size="lg"
                tooltip="RaptorFlow"
                className="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
              >
                <NavLink to="/app" end>
                  <div className="bg-sidebar-primary text-sidebar-primary-foreground flex aspect-square size-8 items-center justify-center rounded-lg overflow-hidden">
                    <RaptorFlowLogo size="sm" showText={false} animated={false} linkTo={null} />
                  </div>
                  <div className="flex flex-col gap-0.5 leading-none">
                    <span className="font-medium tracking-tight">RaptorFlow</span>
                    <span className="text-xs text-sidebar-foreground/70">{planName}</span>
                  </div>
                </NavLink>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarHeader>

        <SidebarSeparator />

        <SidebarContent>
          {navSections.map((section) => (
            <SidebarGroup key={section.label} className="py-0">
              <SidebarGroupLabel className="text-[10px] uppercase tracking-widest text-sidebar-foreground/60">
                {section.label}
              </SidebarGroupLabel>
              <SidebarGroupContent>
                <SidebarMenu>
                  {section.items.map((item) => (
                    <SidebarMenuItem key={item.path}>
                      <SidebarMenuButton
                        asChild
                        isActive={location.pathname === item.path || location.pathname.startsWith(item.path + '/')}
                        tooltip={item.name}
                      >
                        <NavLink to={item.path} end={item.path === '/app'}>
                          <item.icon strokeWidth={1.5} className="w-4 h-4" />
                          <span>{item.name}</span>
                        </NavLink>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  ))}
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>
          ))}
        </SidebarContent>
        <SidebarRail />
      </Sidebar>

      <SidebarInset className="bg-background relative overflow-hidden">

        {/* Top Bar — Editorial, Calm */}
        <header className="h-16 flex items-center justify-between px-6 sticky top-0 z-40 border-b border-border bg-background/95 backdrop-blur-md">
          <div className="flex items-center gap-4">
            <SidebarTrigger className="h-8 w-8 text-muted-foreground hover:text-foreground transition-colors" />

            {/* Command Search */}
            <div className="relative group">
              <button
                aria-label="Search"
                type="button"
                onClick={() => setCommandOpen(true)}
                className="relative flex items-center gap-2 px-4 py-2 bg-muted border border-border rounded-lg text-muted-foreground hover:text-foreground transition-all duration-200 w-64"
              >
                <Search className="w-3.5 h-3.5" strokeWidth={1.5} />
                <span className="text-xs">Search...</span>
                <kbd className="ml-auto px-1.5 bg-background rounded text-[10px] text-muted-foreground font-mono border border-border">⌘K</kbd>
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
                <div className="absolute right-0 mt-4 w-[380px] bg-popover text-popover-foreground border border-border rounded-xl shadow-2xl p-0 z-50 overflow-hidden ring-1 ring-border/50">
                  <div className="px-4 py-3 flex items-center justify-between border-b border-border bg-background/60">
                    <div className="text-sm font-medium tracking-wide">NOTIFICATIONS</div>
                    {notifications.some((n) => n.unread) && (
                      <span className="text-[10px] bg-primary/20 text-primary px-2 py-0.5 rounded-full font-mono">
                        {notifications.filter((n) => n.unread).length} NEW
                      </span>
                    )}
                  </div>

                  <ScrollArea className="h-[320px]">
                    {/* Notifications List Logic same as before but styled darker */}
                    {notifications.length === 0 ? (
                      <div className="p-8 text-center text-muted-foreground text-xs">No signals detected.</div>
                    ) : (
                      notifications.map((n) => (
                        <div key={n.id} onClick={() => markRead(n.id)} className="p-3 hover:bg-muted/60 cursor-pointer border-b border-border last:border-0 transition-colors group">
                          <div className="flex justify-between items-start mb-1">
                            <span className={`text-xs font-medium ${n.unread ? 'text-foreground' : 'text-muted-foreground'} group-hover:text-primary transition-colors`}>{n.title}</span>
                            <span className="text-[10px] text-muted-foreground font-mono">{formatRelativeTime(n.createdAt)}</span>
                          </div>
                          <p className="text-[11px] text-muted-foreground line-clamp-2">{n.detail}</p>
                        </div>
                      ))
                    )}
                  </ScrollArea>

                  <div className="p-2 border-t border-border bg-background/60 grid grid-cols-2 gap-2">
                    <button onClick={markAllRead} className="flex items-center justify-center gap-2 py-1.5 text-[10px] font-medium text-muted-foreground hover:text-foreground hover:bg-muted/60 rounded transition-colors">
                      <Sparkles className="w-3 h-3" /> MARK ALL READ
                    </button>
                    <button onClick={clearNotifications} className="flex items-center justify-center gap-2 py-1.5 text-[10px] font-medium text-muted-foreground hover:text-foreground hover:bg-muted/60 rounded transition-colors">
                      <X className="w-3 h-3" /> CLEAR LOG
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Profile Pill */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button
                  type="button"
                  className="flex items-center gap-3 pl-3 pr-1 py-1 bg-muted hover:bg-muted/70 border border-border rounded-full transition-all"
                >
                  <span className="text-xs font-medium text-foreground">
                    {profile?.full_name?.split(' ')[0] || 'Commander'}
                  </span>
                  <Avatar className="h-7 w-7 border border-border">
                    <AvatarFallback className="text-[10px] font-bold">
                      {profile?.full_name?.[0] || 'U'}
                    </AvatarFallback>
                  </Avatar>
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuLabel>
                  {profile?.full_name || 'Commander'}
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onSelect={() => navigate('/app/settings')}>
                  <Settings className="h-4 w-4" />
                  Settings
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onSelect={handleSignOut} className="text-destructive focus:text-destructive">
                  <LogOut className="h-4 w-4" />
                  Sign out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </header>

        <Dialog open={commandOpen} onOpenChange={setCommandOpen}>
          <DialogContent className="max-w-xl">
            <DialogHeader>
              <DialogTitle>Command</DialogTitle>
              <DialogDescription>Jump to a section.</DialogDescription>
            </DialogHeader>

            <div className="space-y-3">
              <Input
                value={commandQuery}
                onChange={(e) => setCommandQuery(e.target.value)}
                placeholder="Type to search…"
                autoFocus
              />

              <ScrollArea className="h-[280px] rounded-md border border-border">
                <div className="p-1">
                  {filteredCommandItems.length === 0 ? (
                    <div className="p-3 text-sm text-muted-foreground">No results.</div>
                  ) : (
                    filteredCommandItems.map((item) => (
                      <button
                        key={item.path}
                        type="button"
                        onClick={() => {
                          setCommandOpen(false)
                          setCommandQuery('')
                          navigate(item.path)
                        }}
                        className="w-full flex items-center gap-2 rounded-md px-2 py-2 text-sm text-foreground hover:bg-accent transition-colors"
                      >
                        {item.icon ? <item.icon className="h-4 w-4" /> : null}
                        <span className="flex-1 text-left">{item.label}</span>
                        <span className="text-[11px] text-muted-foreground">{item.section}</span>
                      </button>
                    ))
                  )}
                </div>
              </ScrollArea>
            </div>
          </DialogContent>
        </Dialog>

        {/* Content Area - Full Bleed */}
        <div className="relative z-10 w-full h-[calc(100vh-4rem)] overflow-auto scrollbar-hide">
          <Outlet />
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}

export default AppLayout
