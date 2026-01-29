import { createBrowserClient } from '@supabase/ssr'
import { getAuthCallbackUrl } from './env-utils'
import type { Session, User as SupabaseUser } from '@supabase/supabase-js'

// =============================================================================
// CLIENT-SIDE FUNCTIONS (use 'use client' in components that import these)
// =============================================================================

/**
 * Get Supabase client for client-side usage
 */
export function createClient() {
  // Return null during SSR, only create client on browser
  if (typeof window === 'undefined') {
    return null
  }

  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
}

/**
 * Sign in with Google OAuth (client-side only)
 */
export async function signInWithGoogle() {
  if (typeof window === 'undefined') {
    throw new Error('signInWithGoogle() can only be used in client components')
  }

  const supabase = createClient()
  if (!supabase) {
    throw new Error('Supabase client not available')
  }

  const { data, error } = await supabase.auth.signInWithOAuth({
    provider: 'google',
    options: {
      redirectTo: getAuthCallbackUrl(),
      queryParams: {
        access_type: 'offline',
        prompt: 'consent',
      },
    },
  })

  if (error) {
    console.error('OAuth error:', error)
    throw error
  }

  return data
}

/**
 * Sign out current user (client-side only)
 */
export async function signOut() {
  if (typeof window === 'undefined') {
    throw new Error('signOut() can only be used in client components')
  }

  const supabase = createClient()
  if (!supabase) {
    throw new Error('Supabase client not available')
  }

  const { error } = await supabase.auth.signOut()

  if (error) {
    console.error('Sign out error:', error)
    throw error
  }

  // Redirect to sign in page
  window.location.href = '/signin'
}

/**
 * Get current user (client-side)
 */
export async function getCurrentUser(): Promise<SupabaseUser | null> {
  const supabase = createClient()
  if (!supabase) {
    return null
  }
  const { data: { user } } = await supabase.auth.getUser()
  return user
}

/**
 * Get current session (client-side)
 */
export async function getSession(): Promise<Session | null> {
  const supabase = createClient()
  if (!supabase) {
    return null
  }
  const { data: { session } } = await supabase.auth.getSession()
  return session
}

/**
 * Sign up with email and password
 */
export async function signUpWithEmail(email: string, password: string, fullName: string) {
  const supabase = createClient()
  if (!supabase) {
    throw new Error('Supabase client not available')
  }
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
    options: {
      data: {
        full_name: fullName,
      },
      emailRedirectTo: getAuthCallbackUrl(),
    },
  })

  if (error) throw error
  return data
}

/**
 * Sign in with email and password
 */
export async function signInWithEmail(email: string, password: string) {
  const supabase = createClient()
  if (!supabase) {
    throw new Error('Supabase client not available')
  }

  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password,
  })

  if (error) throw error
  return data
}

/**
 * Reset password for email
 */
export async function resetPassword(email: string) {
  const supabase = createClient()
  if (!supabase) {
    throw new Error('Supabase client not available')
  }
  const { error } = await supabase.auth.resetPasswordForEmail(email, {
    redirectTo: `${getAuthCallbackUrl().replace('/auth/callback', '')}/auth/reset-password`,
  })
  if (error) throw error
}

/**
 * Update user password
 */
export async function updatePassword(newPassword: string) {
  const supabase = createClient()
  if (!supabase) {
    throw new Error('Supabase client not available')
  }
  const { error } = await supabase.auth.updateUser({
    password: newPassword,
  })
  if (error) throw error
}

/**
 * Resend verification email
 */
export async function resendVerificationEmail(email: string) {
  const supabase = createClient()
  if (!supabase) {
    throw new Error('Supabase client not available')
  }
  const { error } = await supabase.auth.resend({
    type: 'signup',
    email,
    options: {
      emailRedirectTo: getAuthCallbackUrl(),
    },
  })

  if (error) throw error
}

/**
 * Update user onboarding status
 */
export async function updateOnboardingStatus(status: string) {
  const supabase = createClient()
  if (!supabase) {
    throw new Error('Supabase client not available')
  }

  const { data: { session } } = await supabase.auth.getSession()

  if (!session) {
    throw new Error('No active session')
  }

  const { data, error } = await supabase
    .from('users')
    .update({ onboarding_status: status })
    .eq('auth_user_id', session.user.id)
    .select()
    .single()

  if (error) {
    console.error('Update onboarding status error:', error)
    throw error
  }

  return data
}

// =============================================================================
// SESSION MANAGEMENT (Optional - for custom session tracking)
// =============================================================================

/**
 * Create or update user session in database
 */
export async function createUserSession(metadata: Record<string, any> = {}) {
  const supabase = createClient()
  if (!supabase) {
    throw new Error('Supabase client not available')
  }

  const { data: { session } } = await supabase.auth.getSession()

  if (!session) {
    throw new Error('No active session')
  }

  // Get user ID
  const { data: user } = await supabase
    .from('users')
    .select('id')
    .eq('auth_user_id', session.user.id)
    .single()

  if (!user) {
    throw new Error('User not found')
  }

  // Create session token
  const token = crypto.randomUUID()

  // Store session in database
  const { error } = await supabase
    .from('user_sessions')
    .insert({
      user_id: user.id,
      session_token: token,
      ip_address: metadata.ip_address,
      user_agent: metadata.user_agent,
      device_fingerprint: metadata.device_fingerprint,
      expires_at: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(), // 30 days
    })

  if (error) {
    console.error('Create session error:', error)
    throw error
  }

  return token
}

/**
 * Revoke user session
 */
export async function revokeSession(sessionToken: string) {
  const supabase = createClient()
  if (!supabase) {
    throw new Error('Supabase client not available')
  }

  const { error } = await supabase
    .from('user_sessions')
    .update({
      is_active: false,
      revoked_at: new Date().toISOString(),
      revoked_reason: 'manual_logout',
    })
    .eq('session_token', sessionToken)

  if (error) {
    console.error('Revoke session error:', error)
    throw error
  }
}

/**
 * Revoke all user sessions except current
 */
export async function revokeAllOtherSessions(currentToken: string) {
  const supabase = createClient()
  if (!supabase) {
    throw new Error('Supabase client not available')
  }

  const { data: { session } } = await supabase.auth.getSession()

  if (!session) {
    throw new Error('No active session')
  }

  const { data: user } = await supabase
    .from('users')
    .select('id')
    .eq('auth_user_id', session.user.id)
    .single()

  if (!user) {
    throw new Error('User not found')
  }

  const { error } = await supabase
    .from('user_sessions')
    .update({
      is_active: false,
      revoked_at: new Date().toISOString(),
      revoked_reason: 'revoke_all',
    })
    .eq('user_id', user.id)
    .neq('session_token', currentToken)

  if (error) {
    console.error('Revoke all sessions error:', error)
    throw error
  }
}
