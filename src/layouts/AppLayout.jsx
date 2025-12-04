import React, { useState } from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { useAuth } from '../contexts/AuthContext'
import { 
  LayoutDashboard, 
  Zap, 
  Sparkles, 
  Megaphone, 
  Grid3X3,
  Target,
  Users,
  ChevronLeft,
  ChevronRight,
  Settings,
  LogOut,
  Bell,
  Search,
  Plus,
  Rocket,
  Shield,
  BarChart3,
  Layers,
  Radio,
  Crown
} from 'lucide-react'

// Navigation organized by hierarchy
const navSections = [
  {
    label: 'Command',
    items: [
      { name: 'Dashboard', icon: LayoutDashboard, path: '/app' },
      { name: 'War Room', icon: Target, path: '/app/warroom', accent: true },
    ]
  },
  {
    label: 'Strategy',
    items: [
      { name: 'Spikes', icon: Rocket, path: '/app/spikes', badge: '30d' },
      { name: 'Campaigns', icon: Layers, path: '/app/campaigns' },
      { name: 'Cohorts', icon: Users, path: '/app/cohorts' },
    ]
  },
  {
    label: 'Execution',
    items: [
      { name: 'Moves', icon: Zap, path: '/app/moves' },
      { name: 'Muse', icon: Sparkles, path: '/app/muse' },
      { name: 'Radar', icon: Radio, path: '/app/radar', isNew: true },
    ]
  },
  {
    label: 'Intelligence',
    items: [
      { name: 'Matrix', icon: BarChart3, path: '/app/matrix' },
      { name: 'Position', icon: Megaphone, path: '/app/position' },
    ]
  }
]

const AppLayout = () => {
  const navigate = useNavigate()
  const { profile, signOut } = useAuth()
  const [collapsed, setCollapsed] = useState(false)
  const [searchOpen, setSearchOpen] = useState(false)

  const handleSignOut = async () => {
    await signOut()
    navigate('/')
  }

  // Get user's plan info
  const planName = profile?.plan || 'Free'
  const daysRemaining = profile?.plan_expires_at 
    ? Math.max(0, Math.ceil((new Date(profile.plan_expires_at) - new Date()) / (1000 * 60 * 60 * 24)))
    : 0

  return (
    <div className="min-h-screen bg-zinc-950 flex">
      {/* Sidebar */}
      <motion.aside
        initial={false}
        animate={{ width: collapsed ? 72 : 240 }}
        transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
        className="fixed left-0 top-0 h-screen bg-black border-r border-white/5 flex flex-col z-50"
      >
        {/* Logo */}
        <div className="h-16 flex items-center px-5 border-b border-white/5">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="w-8 h-8 bg-gradient-to-br from-amber-500 to-amber-600 rounded flex items-center justify-center flex-shrink-0">
              <span className="text-black font-bold text-sm">Rf</span>
            </div>
            <AnimatePresence>
              {!collapsed && (
                <motion.span
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -10 }}
                  className="text-white font-light tracking-tight whitespace-nowrap"
                >
                  Raptor<span className="italic text-amber-200">flow</span>
                </motion.span>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 py-4 px-3 space-y-6 overflow-y-auto">
          {navSections.map((section) => (
            <div key={section.label}>
              {/* Section label */}
              <AnimatePresence>
                {!collapsed && (
                  <motion.p
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="px-3 mb-2 text-[10px] uppercase tracking-[0.15em] text-white/30"
                  >
                    {section.label}
                  </motion.p>
                )}
              </AnimatePresence>
              
              {/* Section items */}
              <div className="space-y-1">
                {section.items.map((item) => (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    end={item.path === '/app'}
                    className={({ isActive }) => `
                      flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 relative
                      ${isActive 
                        ? item.accent 
                          ? 'bg-red-500/10 text-red-400' 
                          : 'bg-amber-500/10 text-amber-400' 
                        : 'text-white/50 hover:text-white hover:bg-white/5'
                      }
                    `}
                  >
                    <item.icon className="w-5 h-5 flex-shrink-0" strokeWidth={1.5} />
                    <AnimatePresence>
                      {!collapsed && (
                        <motion.span
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          exit={{ opacity: 0 }}
                          className="text-sm font-light whitespace-nowrap flex-1"
                        >
                          {item.name}
                        </motion.span>
                      )}
                    </AnimatePresence>
                    
                    {/* Badge */}
                    {item.badge && !collapsed && (
                      <span className="px-1.5 py-0.5 text-[9px] bg-amber-500/20 text-amber-400 rounded">
                        {item.badge}
                      </span>
                    )}
                    
                    {/* New indicator */}
                    {item.isNew && (
                      <span className={`${collapsed ? 'absolute -top-1 -right-1' : ''} w-2 h-2 bg-emerald-400 rounded-full animate-pulse`} />
                    )}
                  </NavLink>
                ))}
              </div>
            </div>
          ))}
        </nav>

        {/* Plan info */}
        {!collapsed && profile?.plan && profile.plan !== 'none' && profile.plan !== 'free' && (
          <div className="mx-3 mb-3 p-3 bg-gradient-to-r from-amber-500/10 to-amber-600/5 rounded-lg border border-amber-500/20">
            <div className="flex items-center gap-2 mb-1">
              <Crown className="w-4 h-4 text-amber-400" />
              <span className="text-xs text-amber-400 font-medium capitalize">{planName}</span>
            </div>
            <p className="text-[10px] text-white/40">
              {daysRemaining > 0 ? `${daysRemaining} days remaining` : 'Plan expired'}
            </p>
          </div>
        )}

        {/* Bottom section */}
        <div className="p-3 border-t border-white/5 space-y-1">
          <button 
            onClick={() => navigate('/app/settings')}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-white/50 hover:text-white hover:bg-white/5 transition-all"
          >
            <Settings className="w-5 h-5 flex-shrink-0" strokeWidth={1.5} />
            {!collapsed && <span className="text-sm font-light">Settings</span>}
          </button>
          <button 
            onClick={handleSignOut}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-white/50 hover:text-red-400 hover:bg-red-500/10 transition-all"
          >
            <LogOut className="w-5 h-5 flex-shrink-0" strokeWidth={1.5} />
            {!collapsed && <span className="text-sm font-light">Sign Out</span>}
          </button>
        </div>

        {/* Collapse toggle */}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="absolute -right-3 top-20 w-6 h-6 bg-zinc-900 border border-white/10 rounded-full flex items-center justify-center text-white/50 hover:text-white hover:border-white/20 transition-all"
        >
          {collapsed ? (
            <ChevronRight className="w-3 h-3" />
          ) : (
            <ChevronLeft className="w-3 h-3" />
          )}
        </button>
      </motion.aside>

      {/* Main content */}
      <main 
        className="flex-1 transition-all duration-300"
        style={{ marginLeft: collapsed ? 72 : 240 }}
      >
        {/* Top bar */}
        <header className="h-16 bg-black/50 backdrop-blur-xl border-b border-white/5 flex items-center justify-between px-6 sticky top-0 z-40">
          <div className="flex items-center gap-4">
            {/* Search */}
            <div className="relative">
              <button
                onClick={() => setSearchOpen(!searchOpen)}
                className="flex items-center gap-2 px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white/40 hover:text-white/60 hover:border-white/20 transition-all"
              >
                <Search className="w-4 h-4" />
                <span className="text-sm">Search...</span>
                <kbd className="ml-8 px-1.5 py-0.5 bg-white/5 rounded text-[10px] text-white/30">⌘K</kbd>
              </button>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* New button */}
            <button className="flex items-center gap-2 px-4 py-2 bg-amber-500 hover:bg-amber-400 text-black text-sm font-medium rounded-lg transition-colors">
              <Plus className="w-4 h-4" />
              New Move
            </button>

            {/* Notifications */}
            <button className="relative p-2 text-white/50 hover:text-white transition-colors">
              <Bell className="w-5 h-5" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-amber-500 rounded-full" />
            </button>

            {/* User avatar */}
            <button className="w-9 h-9 bg-gradient-to-br from-amber-500/20 to-amber-600/20 border border-amber-500/30 rounded-full flex items-center justify-center">
              <span className="text-amber-400 text-sm font-medium">U</span>
            </button>
          </div>
        </header>

        {/* Page content */}
        <div className="p-6">
          <Outlet />
        </div>
      </main>
    </div>
  )
}

export default AppLayout

