import { Sidebar, SidebarInset } from './ui/sidebar'
import { Separator } from './ui/separator'
import { AppSidebar } from './app-sidebar'
import { SidebarTrigger } from './ui/sidebar'
import Footer from './Footer'
import { useLocation, Link } from 'react-router-dom'
import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { Bell, User } from 'lucide-react'
import { cn } from '../utils/cn'

const getPageTitle = (pathname) => {
  if (pathname === '/dashboard') return 'Dashboard'
  const parts = pathname.split('/').filter(Boolean)
  const lastPart = parts[parts.length - 1]
  return lastPart.charAt(0).toUpperCase() + lastPart.slice(1).replace(/-/g, ' ')
}

// Get current date and sprint info (mock - in production, fetch from API)
const getTopBarInfo = () => {
  const now = new Date()
  return {
    date: now.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
    sprint: 'Sprint 10 • 12–26 Apr',
    workspace: 'Workspace'
  }
}

export default function Layout({ children }) {
  const location = useLocation()
  const pageTitle = getPageTitle(location.pathname)
  const [sidebarOpen, setSidebarOpen] = useState(() => {
    if (typeof window === 'undefined') return true
    return window.innerWidth >= 768
  })
  const { user } = useAuth()
  const isDashboard = location.pathname === '/'
  const topBarInfo = getTopBarInfo()

  return (
    <Sidebar open={sidebarOpen} setOpen={setSidebarOpen} animate={true}>
      <AppSidebar />
      <SidebarInset>
        {/* Top Bar - Desktop - Luxury Editorial Monochrome */}
        {isDashboard && (
          <header className="hidden md:flex h-12 shrink-0 items-center justify-between border-b border-black/5 bg-white px-10">
            <div className="flex items-center gap-6">
              <span className="text-xs font-mono uppercase tracking-widest text-gray-400 font-medium">
                {topBarInfo.workspace}
              </span>
              <span className="h-3 w-px bg-black/10" />
              <span className="text-xs font-sans text-gray-500">
                {topBarInfo.date}
              </span>
              <span className="text-xs text-gray-300">•</span>
              <span className="text-xs font-sans text-gray-500">
                {topBarInfo.sprint}
              </span>
            </div>
            <div className="flex items-center gap-3">
              <button className="w-7 h-7 flex items-center justify-center text-gray-400 hover:text-black transition-colors duration-180">
                <Bell className="w-3.5 h-3.5" strokeWidth={1.5} />
              </button>
              <Link
                to="/account"
                className="w-7 h-7 rounded-full border border-black/10 bg-gray-50 flex items-center justify-center hover:border-black/20 transition-all duration-180"
              >
                {user?.avatar_url ? (
                  <img 
                    src={user.avatar_url} 
                    alt={user.name || 'User'} 
                    className="w-full h-full rounded-full object-cover"
                  />
                ) : (
                  <User className="w-3.5 h-3.5 text-gray-600" strokeWidth={1.5} />
                )}
              </Link>
            </div>
          </header>
        )}

        {/* Mobile Header */}
        <header className="flex h-16 shrink-0 items-center gap-3 border-b border-black/10 bg-white px-4 md:hidden">
          <SidebarTrigger className="-ml-1 rounded-full border border-black/10 p-2" />
          <Separator orientation="vertical" className="mr-2 h-4" />
          <div>
            <p className="text-micro">Scene</p>
            <h1 className="text-lg font-display text-black">{pageTitle}</h1>
          </div>
        </header>
        
        <main className={cn(
          "relative flex-1 bg-cream px-6 pb-0 pt-8",
          "md:px-8 lg:px-12",
          isDashboard ? "md:pt-12" : "md:pt-12"
        )}>
          {/* Clean background - no textures */}
          <div className={cn(
            "relative max-w-[1440px] mx-auto pb-16",
            isDashboard ? "space-y-12" : "space-y-12"
          )}>
            {children}
          </div>
        </main>
        <Footer />
      </SidebarInset>
    </Sidebar>
  )
}
