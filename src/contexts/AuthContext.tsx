"use client"

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { Session } from '@supabase/supabase-js'
import { useRouter } from 'next/navigation'
import { createClient } from '@/lib/auth-client'

// =============================================================================
// TYPES
// =============================================================================

export interface User {
  id: string
  email: string
  fullName: string
  subscriptionPlan: 'soar' | 'glide' | 'ascent' | null
  subscriptionStatus: 'active' | 'trial' | 'cancelled' | 'expired' | 'none'
  hasCompletedOnboarding: boolean
  createdAt: string
  workspaceId?: string
  role?: string
  onboardingStatus?: string
}

interface AuthContextType {
  user: User | null
  session: Session | null
  isLoading: boolean
  isAuthenticated: boolean
  hasActiveSubscription: boolean
  hasCompletedOnboarding: boolean
  signOut: () => Promise<void>
  refreshUser: () => Promise<void>
}

// =============================================================================
// CONTEXT
// =============================================================================

const AuthContext = createContext<AuthContextType | undefined>(undefined)

// =============================================================================
// PROVIDER
// =============================================================================

interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [session, setSession] = useState<Session | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  // =============================================================================
  // EFFECTS
  // =============================================================================

  useEffect(() => {
    // Don't run during SSR
    if (typeof window === 'undefined') {
      setIsLoading(false)
      return
    }

    let mounted = true

    const initializeAuth = async () => {
      try {
        const supabase = createClient()
        if (!supabase) {
          console.error('Supabase client not available')
          setIsLoading(false)
          return
        }

        const { data: { session } } = await supabase.auth.getSession()
        
        if (session && mounted) {
          setSession(session)
          const userData = await getCurrentUser(supabase)
          if (userData && mounted) {
            setUser(userData)
          }
        }
      } catch (error) {
        console.error('Error initializing auth:', error)
      } finally {
        if (mounted) {
          setIsLoading(false)
        }
      }
    }

    initializeAuth()

    return () => {
      mounted = false
    }
  }, [])

  const getCurrentUser = async (supabase: any): Promise<User | null> => {
    try {
      const { data: { user: authUser } } = await supabase.auth.getUser()
      if (!authUser) return null

      // Try to get user profile from various tables
      const { data: profile } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', authUser.id)
        .maybeSingle()

      if (profile) {
        return {
          id: authUser.id,
          email: authUser.email || '',
          fullName: profile.full_name || authUser.user_metadata?.full_name || authUser.email?.split('@')[0] || 'User',
          subscriptionPlan: profile.subscription_plan || null,
          subscriptionStatus: profile.subscription_status || 'none',
          hasCompletedOnboarding: profile.onboarding_status === 'active',
          createdAt: authUser.created_at,
          workspaceId: profile.workspace_id,
          role: profile.role,
          onboardingStatus: profile.onboarding_status || 'pending',
        }
      }

      // Fallback to basic user info
      return {
        id: authUser.id,
        email: authUser.email || '',
        fullName: authUser.user_metadata?.full_name || authUser.email?.split('@')[0] || 'User',
        subscriptionPlan: authUser.user_metadata?.subscription_plan || null,
        subscriptionStatus: authUser.user_metadata?.subscription_status || 'none',
        hasCompletedOnboarding: authUser.user_metadata?.has_completed_onboarding === true,
        createdAt: authUser.created_at,
        workspaceId: authUser.user_metadata?.workspace_id,
        role: authUser.user_metadata?.role,
        onboardingStatus: authUser.user_metadata?.onboarding_status || 'pending',
      }
    } catch (error) {
      console.error('Error getting current user:', error)
      return null
    }
  }

  // Periodic session refresh
  useEffect(() => {
    if (typeof window === 'undefined') return

    const interval = setInterval(async () => {
      if (session) {
        try {
          const supabase = createClient()
          if (supabase) {
            const { data: { user: authUser } } = await supabase.auth.getUser()
            if (authUser) {
              const userData = await getCurrentUser(supabase)
              if (userData) {
                setUser(userData)
              }
            }
          }
        } catch (error) {
          console.error('Error refreshing user:', error)
        }
      }
    }, 5 * 60 * 1000)

    return () => clearInterval(interval)
  }, [session])

  // =============================================================================
  // ACTIONS
  // =============================================================================

  const signOut = async () => {
    try {
      const supabase = createClient()
      if (supabase) {
        await supabase.auth.signOut()
      }
      setUser(null)
      setSession(null)
      router.push('/login')
    } catch (error) {
      console.error('Error signing out:', error)
      // Force redirect even if sign out fails
      setUser(null)
      setSession(null)
      router.push('/login')
    }
  }

  const refreshUser = async () => {
    try {
      const supabase = createClient()
      if (supabase) {
        const userData = await getCurrentUser(supabase)
        if (userData) {
          setUser(userData)
        }
      }
    } catch (error) {
      console.error('Error refreshing user:', error)
    }
  }

  // =============================================================================
  // COMPUTED VALUES
  // =============================================================================

  const isAuthenticated = !!user
  const hasActiveSubscription = user?.subscriptionStatus === 'active' || user?.subscriptionStatus === 'trial'
  const hasCompletedOnboarding = user?.hasCompletedOnboarding === true || user?.onboardingStatus === 'active'

  // =============================================================================
  // CONTEXT VALUE
  // =============================================================================

  const value: AuthContextType = {
    user,
    session,
    isLoading,
    isAuthenticated,
    hasActiveSubscription,
    hasCompletedOnboarding,
    signOut,
    refreshUser,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

// =============================================================================
// HOOK
// =============================================================================

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

// =============================================================================
// HOC FOR PROTECTED ROUTES
// =============================================================================

interface WithAuthProps {
  children: ReactNode
  requireOnboarding?: boolean
}

export function withAuth({ children, requireOnboarding = false }: WithAuthProps) {
  return function WithAuthComponent(props: any) {
    const { user, isLoading, isAuthenticated, hasCompletedOnboarding } = useAuth()
    const router = useRouter()

    useEffect(() => {
      if (!isLoading) {
        if (!isAuthenticated) {
          router.push('/login')
          return
        }

        if (requireOnboarding && !hasCompletedOnboarding) {
          router.push('/onboarding')
          return
        }
      }
    }, [isLoading, isAuthenticated, hasCompletedOnboarding, router, requireOnboarding])

    if (isLoading) {
      return (
        <div className="min-h-screen flex items-center justify-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-gray-900"></div>
        </div>
      )
    }

    if (!isAuthenticated) {
      return null
    }

    if (requireOnboarding && !hasCompletedOnboarding) {
      return null
    }

    return <>{children}</>
  }
}
