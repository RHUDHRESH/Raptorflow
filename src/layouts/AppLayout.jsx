import React, { useState } from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
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
  Plus
} from 'lucide-react'

const navItems = [
  { name: 'Dashboard', icon: LayoutDashboard, path: '/app' },
  { name: 'Moves', icon: Zap, path: '/app/moves' },
  { name: 'Muse', icon: Sparkles, path: '/app/muse' },
  { name: 'Campaigns', icon: Megaphone, path: '/app/campaigns' },
  { name: 'Matrix', icon: Grid3X3, path: '/app/matrix' },
  { name: 'Position', icon: Target, path: '/app/position' },
  { name: 'Cohorts', icon: Users, path: '/app/cohorts' },
  { name: 'Settings', icon: Settings, path: '/app/settings' },
]

const AppLayout = () => {
  const navigate = useNavigate()
  const [collapsed, setCollapsed] = useState(false)
  const [searchOpen, setSearchOpen] = useState(false)

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
        <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/app'}
              className={({ isActive }) => `
                flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200
                ${isActive 
                  ? 'bg-amber-500/10 text-amber-400' 
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
                    className="text-sm font-light whitespace-nowrap"
                  >
                    {item.name}
                  </motion.span>
                )}
              </AnimatePresence>
            </NavLink>
          ))}
        </nav>

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
            onClick={() => navigate('/')}
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

