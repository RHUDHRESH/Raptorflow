import { Sidebar, SidebarInset, SidebarProvider } from './ui/sidebar'
import { Separator } from './ui/separator'
import { AppSidebar } from './app-sidebar'
import { SidebarTrigger } from './ui/sidebar'
import { useLocation } from 'react-router-dom'
import { useState } from 'react'

const getPageTitle = (pathname) => {
  if (pathname === '/') return 'Dashboard'
  const parts = pathname.split('/').filter(Boolean)
  const lastPart = parts[parts.length - 1]
  return lastPart.charAt(0).toUpperCase() + lastPart.slice(1).replace(/-/g, ' ')
}

export default function Layout({ children }) {
  const location = useLocation()
  const pageTitle = getPageTitle(location.pathname)
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <SidebarProvider open={sidebarOpen} setOpen={setSidebarOpen} animate={true}>
      <Sidebar>
        <AppSidebar />
      </Sidebar>
      <SidebarInset>
        <header className="flex h-16 shrink-0 items-center gap-3 border-b border-neutral-200 bg-white px-4 md:hidden">
          <SidebarTrigger className="-ml-1 rounded-full border border-neutral-200 p-2" />
          <Separator orientation="vertical" className="mr-2 h-4" />
          <div>
            <p className="micro-label tracking-[0.5em]">Scene</p>
            <h1 className="text-lg font-display text-neutral-900">{pageTitle}</h1>
          </div>
        </header>
        <main className="relative flex-1 min-h-[calc(100vh-4rem)] bg-white px-6 pb-16 pt-8 md:min-h-screen md:px-12 md:pt-12">
          <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.7),transparent_45%)]" />
          <div className="relative space-y-12 max-w-7xl mx-auto">{children}</div>
        </main>
      </SidebarInset>
    </SidebarProvider>
  )
}
