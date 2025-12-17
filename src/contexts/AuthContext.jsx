import React, { createContext, useContext, useEffect, useState, useCallback, useRef } from 'react'
import { supabase, hasCachedSession, refreshSession, supabaseConfigured } from '../lib/supabase'
import { AUTH_DISABLED } from '../config/auth'

const AuthContext = createContext({})

// Cache key for profile
const PROFILE_CACHE_KEY = 'raptorflow-profile-cache'
const PROFILE_CACHE_TTL = 5 * 60 * 1000 // 5 minutes

const mapDbPlanCodeToFrontendPlan = (planCode) => {
  const normalized = String(planCode || '').toLowerCase()
  if (normalized === 'starter') return 'ascent'
  if (normalized === 'growth') return 'glide'
  if (normalized === 'enterprise') return 'soar'
  if (normalized === 'free') return 'free'
  return normalized
}

const fetchLatestOrgSubscription = async (organizationId) => {
  if (!organizationId) return null

  const { data, error } = await supabase
    .from('subscriptions')
    .select('id, status, current_period_start, current_period_end, autopay_enabled, mandate_id, plan:plans(code)')
    .eq('organization_id', organizationId)
    .is('deleted_at', null)
    .order('created_at', { ascending: false })
    .limit(1)
    .maybeSingle()

  if (error) {
    console.warn('Failed to fetch subscription:', error)
    return null
  }

  return data || null
}

const fetchMandateForSubscription = async ({ mandateId, subscriptionId, organizationId }) => {
  if (mandateId) {
    const { data, error } = await supabase
      .from('payment_mandates')
      .select('id, status, mandate_type, provider, provider_mandate_id, max_amount_paise, valid_from, valid_until, created_at')
      .eq('id', mandateId)
      .maybeSingle()

    if (error) {
      console.warn('Failed to fetch mandate by id:', error)
    }

    if (data) return data
  }

  if (subscriptionId) {
    const { data, error } = await supabase
      .from('payment_mandates')
      .select('id, status, mandate_type, provider, provider_mandate_id, max_amount_paise, valid_from, valid_until, created_at')
      .eq('subscription_id', subscriptionId)
      .order('created_at', { ascending: false })
      .limit(1)
      .maybeSingle()

    if (error) {
      console.warn('Failed to fetch mandate by subscription:', error)
    }

    if (data) return data
  }

  if (organizationId) {
    const { data, error } = await supabase
      .from('payment_mandates')
      .select('id, status, mandate_type, provider, provider_mandate_id, max_amount_paise, valid_from, valid_until, created_at')
      .eq('organization_id', organizationId)
      .order('created_at', { ascending: false })
      .limit(1)
      .maybeSingle()

    if (error) {
      console.warn('Failed to fetch mandate by org:', error)
    }

    return data || null
  }

  return null
}

const enrichProfileWithSubscription = async (profileRow) => {
  if (!profileRow) return null

  const organizationId = profileRow.current_org_id || profileRow.organization_id || null
  const subscription = await fetchLatestOrgSubscription(organizationId)
  const mandate = subscription
    ? await fetchMandateForSubscription({
        mandateId: subscription?.mandate_id || null,
        subscriptionId: subscription?.id || null,
        organizationId,
      })
    : null

  const planCode = subscription?.plan?.code
  const derivedPlan = planCode ? mapDbPlanCodeToFrontendPlan(planCode) : (profileRow.plan || 'free')
  const derivedStatus = subscription?.status === 'active' && derivedPlan !== 'free' ? 'active' : 'inactive'

  return {
    ...profileRow,
    current_org_id: organizationId,
    plan: derivedPlan,
    plan_status: derivedStatus,
    plan_started_at: subscription?.current_period_start || null,
    plan_expires_at: subscription?.current_period_end || null,
    subscription_status: subscription?.status || null,
    subscription_id: subscription?.id || null,
    autopay_enabled: subscription?.autopay_enabled === true,
    mandate_id: subscription?.mandate_id || null,
    mandate_status: mandate?.status || null,
    mandate_type: mandate?.mandate_type || null,
    mandate_provider: mandate?.provider || null,
    mandate_provider_id: mandate?.provider_mandate_id || null,
    mandate_max_amount_paise: mandate?.max_amount_paise || null,
    mandate_valid_from: mandate?.valid_from || null,
    mandate_valid_until: mandate?.valid_until || null,
  }
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

// Get cached profile from localStorage
const getCachedProfile = (userId) => {
  try {
    const cached = localStorage.getItem(PROFILE_CACHE_KEY)
    if (cached) {
      const { data, timestamp, uid } = JSON.parse(cached)
      // Check if cache is valid (same user and not expired)
      if (uid === userId && Date.now() - timestamp < PROFILE_CACHE_TTL) {
        return data
      }
    }
  } catch (e) {
    console.error('Cache read error:', e)
  }
  return null
}

// Set cached profile
const setCachedProfile = (userId, profile) => {
  try {
    localStorage.setItem(PROFILE_CACHE_KEY, JSON.stringify({
      data: profile,
      timestamp: Date.now(),
      uid: userId
    }))
  } catch (e) {
    console.error('Cache write error:', e)
  }
}

// Clear cached profile
const clearCachedProfile = () => {
  try {
    localStorage.removeItem(PROFILE_CACHE_KEY)
  } catch (e) {
    console.error('Cache clear error:', e)
  }
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const initRef = useRef(false)

  const previewMode = import.meta.env.DEV && !supabaseConfigured

  // Create profile if it doesn't exist
  const createProfile = async (user) => {
    try {
      console.log('Creating profile for user:', user.id)
      console.log('User metadata:', user.user_metadata)

      const profileData = {
        id: user.id,
        email: user.email,
        full_name: user.user_metadata?.full_name || user.user_metadata?.name || null,
        avatar_url: user.user_metadata?.avatar_url || user.user_metadata?.picture || null,
        onboarding_completed: false
      }

      console.log('Profile data to insert:', profileData)

      const { data, error } = await supabase
        .from('profiles')
        .insert(profileData)
        .select()
        .single()

      if (error) {
        console.error('Error creating profile:', error)
        console.error('Error details:', {
          code: error.code,
          message: error.message,
          details: error.details,
          hint: error.hint
        })

        // If profile already exists, fetch it
        if (error.code === '23505' || error.message?.includes('duplicate')) {
          console.log('Profile exists, fetching...')
          return await fetchProfile(user.id)
        }

        // If it's an RLS/permission error, the profile might exist but we can't see it
        // Try fetching first
        if (error.code === '42501' || error.message?.includes('permission') || error.message?.includes('policy')) {
          console.log('RLS error detected, trying to fetch existing profile...')
          return await fetchProfile(user.id)
        }

        // For other errors, still attempt to fetch
        console.log('Attempting to fetch profile despite error...')
        return await fetchProfile(user.id)
      }

      console.log('Profile created:', data?.id)
      const enriched = await enrichProfileWithSubscription(data)
      setCachedProfile(user.id, enriched)
      return enriched
    } catch (err) {
      console.error('Error in createProfile:', err)
      return await fetchProfile(user.id)
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

      const enriched = await enrichProfileWithSubscription(data)
      setCachedProfile(userId, enriched)
      return enriched
    } catch (err) {
      console.error('Error in fetchProfile:', err)
      return null
    }
  }

  // Ensure profile exists (fetch or create)
  const ensureProfile = async (user) => {
    if (!user) return null

    // Try cache first
    const cached = getCachedProfile(user.id)
    if (cached) {
      console.log('Using cached profile')
      if (cached.plan_status || cached.subscription_status || cached.subscription_id) {
        return cached
      }
      const enriched = await enrichProfileWithSubscription(cached)
      setCachedProfile(user.id, enriched)
      return enriched
    }

    let profile = await fetchProfile(user.id)

    if (!profile) {
      console.log('Profile not found, creating...')
      profile = await createProfile(user)
    }

    return profile
  }

  // Initialize auth state
  useEffect(() => {
    // Prevent double initialization in React strict mode
    if (initRef.current) return
    initRef.current = true

    if (AUTH_DISABLED || (import.meta.env.DEV && !supabaseConfigured)) {
      console.log('🔓 Auth disabled or preview mode active. Using mock user.')
      const now = new Date()
      const mockUser = {
        id: 'preview-user',
        email: 'preview@raptorflow.local',
        aud: 'authenticated',
        role: 'authenticated',
        created_at: now.toISOString(),
        user_metadata: {
          full_name: 'Preview User',
          name: 'Preview User',
          avatar_url: null
        },
      }

      const mockProfile = {
        id: mockUser.id,
        email: mockUser.email,
        full_name: mockUser.user_metadata.full_name,
        plan: 'ascent', // Use a premium plan by default for preview
        plan_status: 'active',
        plan_started_at: new Date(now.getTime() - 1000 * 60 * 60 * 24 * 7).toISOString(),
        plan_expires_at: new Date(now.getTime() + 1000 * 60 * 60 * 24 * 21).toISOString(),
        onboarding_completed: true,
        onboarding_completed_at: new Date(now.getTime() - 1000 * 60 * 60 * 24 * 3).toISOString(),
        current_org_id: 'preview-org',
        subscription_status: 'active',
        subscription_id: 'preview-subscription',
        autopay_enabled: false,
        mandate_id: null,
        mandate_status: null,
        mandate_type: null,
        mandate_provider: null,
        mandate_provider_id: null,
        mandate_max_amount_paise: null,
        mandate_valid_from: null,
        mandate_valid_until: null,
      }

      setUser(mockUser)
      setProfile(mockProfile)
      setLoading(false)
      return
    }

    const initAuth = async () => {
      try {
        console.log('🔐 AuthContext: initializing...')

        // Check for cached session first for instant UI
        const hasCached = hasCachedSession()
        console.log('🔐 Has cached session:', hasCached)

        // Get current session
        const { data: { session }, error: sessionError } = await supabase.auth.getSession()

        if (sessionError) {
          console.error('Session error:', sessionError)
          setError(sessionError.message)
          setLoading(false)
          return
        }

        if (session?.user) {
          console.log('🔐 User found:', session.user.email)
          setUser(session.user)

          // Load profile (from cache or fetch)
          const profileData = await ensureProfile(session.user)
          setProfile(profileData)
          console.log('🔐 Profile loaded:', profileData?.plan || 'no plan')
        } else {
          console.log('🔐 No session found')
          clearCachedProfile()
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
        console.log('🔐 Auth state changed:', event)

        if (event === 'SIGNED_OUT') {
          setUser(null)
          setProfile(null)
          clearCachedProfile()
          setLoading(false)
          return
        }

        if (session?.user) {
          setUser(session.user)

          // For sign in events, ensure profile exists
          if (event === 'SIGNED_IN' || event === 'TOKEN_REFRESHED') {
            const profileData = await ensureProfile(session.user)
            setProfile(profileData)
          }
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
    }
  }

  // Sign in with email + password
  const signInWithPassword = async (email, password) => {
    setError(null)

    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      })

      if (error) {
        setError(error.message)
        setLoading(false)
        return { error }
      }

      return { data }
    } catch (err) {
      setError(err.message)
      setLoading(false)
      return { error: err }
    }
  }

  // Sign in with email OTP
  const signInWithEmail = async (email) => {
    setError(null)

    try {
      const { data, error } = await supabase.auth.signInWithOtp({
        email,
        options: {
          emailRedirectTo: `${window.location.origin}/auth/callback`,
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
    }
  }

  // Sign out
  const signOut = async () => {
    setLoading(true)
    try {
      clearCachedProfile()
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

      const enriched = await enrichProfileWithSubscription(data)
      setProfile(enriched)
      setCachedProfile(user.id, enriched)
      return { data: enriched }
    } catch (err) {
      return { error: err.message }
    }
  }

  // Refresh profile data (force fetch from server)
  const refreshProfile = useCallback(async () => {
    if (!user) return null

    // Clear cache to force fresh fetch
    clearCachedProfile()
    const profileData = await fetchProfile(user.id)
    setProfile(profileData)
    return profileData
  }, [user])

  // Check if onboarding is completed
  const isOnboardingCompleted = profile?.onboarding_completed === true

  // Check if user has a paid plan
  const isPaid = profile?.plan && profile.plan !== 'none' && profile.plan !== 'free' && profile.plan_status === 'active'

  const value = {
    user,
    profile,
    loading,
    error,
    isAuthenticated: !!user,
    isPaid,
    isOnboardingCompleted,
    needsOnboarding: !!user && !isOnboardingCompleted,
    signInWithGoogle,
    signInWithEmail,
    signInWithPassword,
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
