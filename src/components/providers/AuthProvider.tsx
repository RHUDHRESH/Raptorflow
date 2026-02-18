'use client'

import { useEffect } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { useAuthStore } from '@/stores/authStore'

interface AuthProviderProps {
  children: React.ReactNode
}

const publicPaths = ['/login', '/signup', '/auth/verify', '/auth/reset-password']

export function AuthProvider({ children }: AuthProviderProps) {
  const router = useRouter()
  const pathname = usePathname()
  const { user, loading, initialized, initialize } = useAuthStore()

  useEffect(() => {
    // Initialize auth state
    initialize()
  }, [initialize])

  useEffect(() => {
    if (!initialized || loading) return

    const isPublicPath = publicPaths.some(
      path => pathname === path || pathname.startsWith(path)
    )

    // If not authenticated and trying to access protected route
    if (!user && !isPublicPath) {
      router.push('/login')
      return
    }

    // If authenticated and trying to access auth pages
    if (user && isPublicPath && pathname !== '/auth/verify') {
      router.push('/dashboard')
      return
    }
  }, [user, loading, initialized, pathname, router])

  // Show loading state while initializing
  if (!initialized || loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    )
  }

  return <>{children}</>
}
