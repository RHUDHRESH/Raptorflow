import { Link, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  LayoutDashboard, 
  Target, 
  TrendingUp, 
  Users, 
  FileText, 
  Clock,
  HelpCircle,
  Sparkles
} from 'lucide-react'
import { cn } from '../utils/cn'

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Moves', href: '/moves', icon: Target },
  { name: 'Strategy', href: '/strategy', icon: Sparkles },
  { name: 'Analytics', href: '/analytics', icon: TrendingUp },
  { name: 'Weekly Review', href: '/review', icon: Clock },
  { name: 'ICPs', href: '/icps', icon: Users },
  { name: 'Support', href: '/support', icon: HelpCircle },
  { name: 'History', href: '/history', icon: FileText },
]

export default function Layout({ children }) {
  const location = useLocation()

  return (
    <div className="min-h-screen bg-gradient-to-br from-neutral-50 via-primary-50/30 to-neutral-50">
      {/* Sidebar */}
      <aside className="fixed left-0 top-0 h-full w-64 bg-white/80 backdrop-blur-xl border-r border-neutral-200/50 z-50">
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="p-6 border-b border-neutral-200/50">
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center gap-3"
            >
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary-600 to-accent-600 flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-display font-bold text-neutral-900">Raptorflow</h1>
                <p className="text-xs text-neutral-500">Strategy Execution</p>
              </div>
            </motion.div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
            {navigation.map((item, index) => {
              const isActive = location.pathname === item.href || 
                (item.href !== '/' && location.pathname.startsWith(item.href))
              const Icon = item.icon

              return (
                <motion.div
                  key={item.name}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <Link
                    to={item.href}
                    className={cn(
                      "group flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200",
                      isActive
                        ? "bg-primary-600 text-white shadow-lg shadow-primary-600/20"
                        : "text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900"
                    )}
                  >
                    <Icon className={cn(
                      "w-5 h-5 transition-transform group-hover:scale-110",
                      isActive ? "text-white" : "text-neutral-400"
                    )} />
                    <span>{item.name}</span>
                  </Link>
                </motion.div>
              )
            })}
          </nav>

          {/* Footer */}
          <div className="p-4 border-t border-neutral-200/50">
            <div className="text-xs text-neutral-500 text-center">
              <p>Raptorflow v1.0</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="ml-64 min-h-screen">
        <div className="p-8">
          {children}
        </div>
      </main>
    </div>
  )
}

