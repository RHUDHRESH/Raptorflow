import React, { createContext, useContext, useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'

const AuthContext = createContext({})

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Create profile if it doesn't exist
  const createProfile = async (user) => {
    try {
      console.log('Creating profile for user:', user.id, user.email)
      
      const { data, error } = await supabase
        .from('profiles')
        .insert({
          id: user.id,
          email: user.email,
          full_name: user.user_metadata?.full_name || user.user_metadata?.name || user.user_metadata?.full_name || null,
          avatar_url: user.user_metadata?.avatar_url || user.user_metadata?.picture || null,
        })
        .select()
        .single()

      if (error) {
        // If profile already exists (unique constraint violation), fetch it
        if (error.code === '23505' || error.message?.includes('duplicate') || error.message?.includes('unique')) {
          console.log('Profile already exists, fetching...')
          return await fetchProfile(user.id)
        }
        console.error('Error creating profile:', error)
        // Try to fetch anyway in case it was created by trigger
        const existing = await fetchProfile(user.id)
        if (existing) {
          console.log('Found existing profile after error')
          return existing
        }
        return null
      }
      console.log('Profile created successfully:', data)
      return data
    } catch (err) {
      console.error('Error in createProfile:', err)
      // Last resort: try to fetch
      try {
        const existing = await fetchProfile(user.id)
        if (existing) {
          console.log('Found existing profile after exception')
          return existing
        }
      } catch (fetchErr) {
        console.error('Failed to fetch profile after creation error:', fetchErr)
      }
      return null
    }
  }

  // Fetch user profile from database
  const fetchProfile = async (userId) => {
    try {
      const { data, error } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', userId)
        .single()

      if (error) {
        console.error('Error fetching profile:', error)
        return null
      }
      return data
    } catch (err) {
      console.error('Error in fetchProfile:', err)
      return null
    }
  }

  // Ensure profile exists (fetch or create)
  const ensureProfile = async (user) => {
    if (!user) return null
    
    let profile = await fetchProfile(user.id)
    
    // If profile doesn't exist, create it
    if (!profile) {
      console.log('Profile not found, creating...')
      profile = await createProfile(user)
    }
    
    return profile
  }

  // Initialize auth state
  useEffect(() => {
    const initAuth = async () => {
      try {
        // Get current session
        const { data: { session }, error: sessionError } = await supabase.auth.getSession()
        
        if (sessionError) {
          console.error('Session error:', sessionError)
          setError(sessionError.message)
        }

        if (session?.user) {
          setUser(session.user)
          const profileData = await ensureProfile(session.user)
          setProfile(profileData)
        }
      } catch (err) {
        console.error('Auth init error:', err)
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    initAuth()

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        console.log('Auth state changed:', event, session?.user?.id)
        
        if (session?.user) {
          setUser(session.user)
          // Ensure profile exists (create if needed)
          const profileData = await ensureProfile(session.user)
          setProfile(profileData)
          
          // If we just signed in and have a session, we're good to go
          if (event === 'SIGNED_IN' && window.location.pathname === '/app') {
            // Already on app page, profile should be loaded
            console.log('Signed in, profile loaded:', profileData)
          }
        } else {
          setUser(null)
          setProfile(null)
        }
        setLoading(false)
      }
    )

    return () => {
      subscription.unsubscribe()
    }
  }, [])

  // Sign in with Google
  const signInWithGoogle = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const { data, error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/auth/callback`,
          queryParams: {
            access_type: 'offline',
            prompt: 'consent',
          },
        },
      })

      if (error) {
        setError(error.message)
        return { error }
      }

      return { data }
    } catch (err) {
      setError(err.message)
      return { error: err }
    } finally {
      setLoading(false)
    }
  }

  // Sign in with email OTP
  const signInWithEmail = async (email) => {
    setLoading(true)
    setError(null)

    try {
      const { data, error } = await supabase.auth.signInWithOtp({
        email,
        options: {
          emailRedirectTo: `${window.location.origin}/app`,
        },
      })

      if (error) {
        setError(error.message)
        return { error }
      }

      return { data, message: 'Check your email for the login link!' }
    } catch (err) {
      setError(err.message)
      return { error: err }
    } finally {
      setLoading(false)
    }
  }

  // Sign out
  const signOut = async () => {
    setLoading(true)
    try {
      const { error } = await supabase.auth.signOut()
      if (error) {
        setError(error.message)
        return { error }
      }
      setUser(null)
      setProfile(null)
      return { success: true }
    } catch (err) {
      setError(err.message)
      return { error: err }
    } finally {
      setLoading(false)
    }
  }

  // Update profile
  const updateProfile = async (updates) => {
    if (!user) return { error: 'Not authenticated' }

    try {
      const { data, error } = await supabase
        .from('profiles')
        .update(updates)
        .eq('id', user.id)
        .select()
        .single()

      if (error) {
        return { error: error.message }
      }

      setProfile(data)
      return { data }
    } catch (err) {
      return { error: err.message }
    }
  }

  // Refresh profile data
  const refreshProfile = async () => {
    if (!user) return
    const profileData = await fetchProfile(user.id)
    setProfile(profileData)
  }

  const value = {
    user,
    profile,
    loading,
    error,
    isAuthenticated: !!user,
    isPaid: profile?.plan && profile.plan !== 'none' && profile.plan_status === 'active',
    signInWithGoogle,
    signInWithEmail,
    signOut,
    updateProfile,
    refreshProfile,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export default AuthContext

