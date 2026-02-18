import { create } from 'zustand'
import { User, Session } from '@supabase/supabase-js'
import { createClient } from '@/lib/supabase/client'

let authSubscription: { unsubscribe: () => void } | null = null

interface AuthState {
  user: User | null
  session: Session | null
  loading: boolean
  initialized: boolean
  error: string | null
  
  // Actions
  setSession: (session: Session | null) => void
  setUser: (user: User | null) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  initialize: () => Promise<void>
  signIn: (email: string, password: string) => Promise<{ error: string | null }>
  signUp: (email: string, password: string) => Promise<{ error: string | null; needsConfirmation?: boolean }>
  signOut: () => Promise<void>
  resetPassword: (email: string) => Promise<{ error: string | null }>
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  session: null,
  loading: true,
  initialized: false,
  error: null,

  setSession: (session) => set({ 
    session, 
    user: session?.user ?? null 
  }),
  
  setUser: (user) => set({ user }),
  
  setLoading: (loading) => set({ loading }),
  
  setError: (error) => set({ error }),

  initialize: async () => {
    const supabase = createClient()
    
    try {
      if (authSubscription) {
        authSubscription.unsubscribe()
        authSubscription = null
      }

      // Get current session
      const { data: { session } } = await supabase.auth.getSession()
      
      set({ 
        session, 
        user: session?.user ?? null,
        loading: false,
        initialized: true 
      })

      // Listen for auth changes
      const { data: { subscription } } = supabase.auth.onAuthStateChange(
        async (event, session) => {
          set({ 
            session, 
            user: session?.user ?? null,
            loading: false 
          })
        }
      )

      authSubscription = subscription
    } catch (error) {
      console.error('Auth initialization error:', error)
      set({ 
        loading: false, 
        initialized: true,
        error: 'Failed to initialize authentication'
      })
    }
  },

  signIn: async (email, password) => {
    const supabase = createClient()
    set({ loading: true, error: null })

    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      })

      if (error) {
        set({ error: error.message, loading: false })
        return { error: error.message }
      }

      set({ 
        session: data.session, 
        user: data.user,
        loading: false 
      })
      
      return { error: null }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Sign in failed'
      set({ error: errorMessage, loading: false })
      return { error: errorMessage }
    }
  },

  signUp: async (email, password) => {
    const supabase = createClient()
    set({ loading: true, error: null })

    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          // If you have email confirmation enabled, this won't create a session
          emailRedirectTo: `${window.location.origin}/auth/callback`
        }
      })

      if (error) {
        set({ error: error.message, loading: false })
        return { error: error.message }
      }

      // Check if email confirmation is required
      if (!data.session && data.user) {
        set({ loading: false })
        return { 
          error: null, 
          needsConfirmation: true 
        }
      }

      set({ 
        session: data.session, 
        user: data.user,
        loading: false 
      })
      
      return { error: null }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Sign up failed'
      set({ error: errorMessage, loading: false })
      return { error: errorMessage }
    }
  },

  signOut: async () => {
    const supabase = createClient()
    set({ loading: true })

    try {
      await supabase.auth.signOut()
      set({ 
        user: null, 
        session: null, 
        loading: false,
        error: null 
      })
    } catch (error) {
      console.error('Sign out error:', error)
      // Still clear local state even if server call fails
      set({ 
        user: null, 
        session: null, 
        loading: false 
      })
    }
  },

  resetPassword: async (email) => {
    const supabase = createClient()
    set({ loading: true, error: null })

    try {
      const { error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/auth/reset-password`,
      })

      if (error) {
        set({ error: error.message, loading: false })
        return { error: error.message }
      }

      set({ loading: false })
      return { error: null }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Password reset failed'
      set({ error: errorMessage, loading: false })
      return { error: errorMessage }
    }
  },
}))

// Helper hook to check if user is authenticated
export function useIsAuthenticated() {
  return useAuthStore((state) => !!state.user)
}

// Helper hook to get current user
export function useUser() {
  return useAuthStore((state) => state.user)
}

// Helper hook for auth loading state
export function useAuthLoading() {
  return useAuthStore((state) => state.loading)
}
