"use client"

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { User as SupabaseUser, Session } from '@supabase/supabase-js'
import { createClient } from '@/lib/supabase/client'
import { useRouter } from 'next/navigation'

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
  const supabase = createClient()

  // =============================================================================
  // HELPERS
  // =============================================================================

  function mapSupabaseUser(supabaseUser: SupabaseUser): User {
    const subscriptionStatus = supabaseUser.user_metadata?.subscription_status || 'none'
    const subscriptionPlan = supabaseUser.user_metadata?.subscription_plan || null
    const hasCompletedOnboarding = supabaseUser.user_metadata?.has_completed_onboarding === true

    return {
      id: supabaseUser.id,
      email: supabaseUser.email || '',
      fullName: supabaseUser.user_metadata?.full_name || supabaseUser.email?.split('@')[0] || 'User',
      subscriptionPlan,
      subscriptionStatus,
      hasCompletedOnboarding,
      createdAt: supabaseUser.created_at,
      workspaceId: supabaseUser.user_metadata?.workspace_id,
      role: supabaseUser.user_metadata?.role,
      onboardingStatus: supabaseUser.user_metadata?.onboarding_status,
    }
  }

  async function loadUserData(supabaseUser: SupabaseUser) {
    try {
      // Load user data from database
      if (!supabase) {
        console.error('Supabase client not available')
        return mapSupabaseUser(supabaseUser)
      }

      const { data: userData, error } = await supabase
        .from('users')
        .select('*')
        .eq('auth_user_id', supabaseUser.id)
        .single()

      if (userData && !error) {
        return {
          ...mapSupabaseUser(supabaseUser),
          subscriptionPlan: userData.subscription_plan || supabaseUser.user_metadata?.subscription_plan,
          subscriptionStatus: userData.subscription_status || supabaseUser.user_metadata?.subscription_status || 'none',
          hasCompletedOnboarding: userData.onboarding_status === 'active',
          onboardingStatus: userData.onboarding_status,
          workspaceId: userData.workspace_id,
          role: userData.role,
        }
      }
    } catch (error) {
      console.error('Error loading user data:', error)
    }

    return mapSupabaseUser(supabaseUser)
  }

  // =============================================================================
  // EFFECTS
  // =============================================================================

  useEffect(() => {
    // Don't run during SSR
    if (typeof window === 'undefined') {
      setIsLoading(false)
      return
    }

    // Don't run if supabase is not available
    if (!supabase) {
      console.error('Supabase client not available')
      setIsLoading(false)
      return
    }

    // Get initial session
    const getInitialSession = async () => {
      try {
        console.log('Getting initial session...')
        const { data: { session } } = await supabase.auth.getSession()
        console.log('Session retrieved:', session ? 'found' : 'none')
        
        if (session?.user) {
          const userData = await loadUserData(session.user)
          setUser(userData)
          setSession(session)
        }
      } catch (error) {
        console.error('Error getting initial session:', error)
      } finally {
        setIsLoading(false)
      }
    }

    getInitialSession()

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        console.log('Auth state changed:', event, session?.user?.email)

        if (session?.user) {
          const userData = await loadUserData(session.user)
          setUser(userData)
          setSession(session)
        } else {
          setUser(null)
          setSession(null)
        }

        setIsLoading(false)
      }
    )

    return () => subscription.unsubscribe()
  }, [supabase])

  // =============================================================================
  // ACTIONS
  // =============================================================================

  const signOut = async () => {
    try {
      await supabase.auth.signOut()
      setUser(null)
      setSession(null)
      router.push('/login')
    } catch (error) {
      console.error('Error signing out:', error)
    }
  }

  const refreshUser = async () => {
    if (!session?.user) return

    try {
      const userData = await loadUserData(session.user)
      setUser(userData)
    } catch (error) {
      console.error('Error refreshing user:', error)
    }
  }

  // =============================================================================
  // COMPUTED VALUES
  // =============================================================================

  const isAuthenticated = !!user
  const hasActiveSubscription = user?.subscriptionStatus === 'active'
  const hasCompletedOnboarding = user?.onboardingStatus === 'active'

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
