/**
 * Main Layout Component
 * Wraps the entire application with navigation and structure
 */
"use client"

import MainNavigation from "./MainNavigation"

interface MainLayoutProps {
  children: React.ReactNode
}

export default function MainLayout({ children }: MainLayoutProps) {
  return (
    <div className="min-h-screen bg-[#FFFEF9]">
      <MainNavigation />
      <main className="flex-1">
        {children}
      </main>
    </div>
  )
}
