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

  return (
    <Sidebar open={sidebarOpen} setOpen={setSidebarOpen} animate={true}>
      <AppSidebar />
      <SidebarInset>
        {/* Mobile Header */}
        <header className="flex h-16 shrink-0 items-center gap-3 border-b border-black/10 bg-white px-4 md:hidden">
          <SidebarTrigger className="-ml-1 rounded-full border border-black/10 p-2" />
          <Separator orientation="vertical" className="mr-2 h-4" />
          <div>
            <p className="text-micro">Scene</p>
            <h1 className="text-lg font-display text-black">{pageTitle}</h1>
          </div>
        </header>

        <main className="relative flex-1 bg-cream px-6 pb-0 pt-8 md:px-8 lg:px-12 md:pt-12">
          {/* Clean background - no textures */}
          <div className="relative max-w-[1440px] mx-auto pb-16 space-y-12">
            {children}
          </div>
        </main>
        <Footer />
      </SidebarInset>
    </Sidebar>
  )
}
