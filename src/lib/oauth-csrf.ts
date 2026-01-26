/**
 * OAuth CSRF Protection
 * Generates and validates state parameters to prevent CSRF attacks
 */

import { createClient } from './supabase/client'

/**
 * Generate a cryptographically secure random state parameter
 */
export function generateOAuthState(): string {
  if (typeof window === 'undefined') {
    throw new Error('generateOAuthState can only be called in browser')
  }

  // Generate 32 random bytes and convert to hex string
  const array = new Uint8Array(32)
  crypto.getRandomValues(array)
  const state = Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('')

  // Store in session storage for validation
  sessionStorage.setItem('oauth_state', state)
  sessionStorage.setItem('oauth_state_timestamp', Date.now().toString())

  return state
}

/**
 * Validate OAuth state parameter from callback
 */
export function validateOAuthState(receivedState: string | null): boolean {
  if (!receivedState) {
    console.error('[OAuth CSRF] No state parameter received')
    return false
  }

  const storedState = sessionStorage.getItem('oauth_state')
  const timestamp = sessionStorage.getItem('oauth_state_timestamp')

  // Clear state from storage
  sessionStorage.removeItem('oauth_state')
  sessionStorage.removeItem('oauth_state_timestamp')

  if (!storedState) {
    console.error('[OAuth CSRF] No stored state found')
    return false
  }

  if (storedState !== receivedState) {
    console.error('[OAuth CSRF] State mismatch')
    return false
  }

  // Check if state is not too old (5 minutes max)
  if (timestamp) {
    const stateAge = Date.now() - parseInt(timestamp)
    if (stateAge > 5 * 60 * 1000) {
      console.error('[OAuth CSRF] State expired (older than 5 minutes)')
      return false
    }
  }

  return true
}

/**
 * Sign in with OAuth provider using CSRF-protected flow
 */
export async function signInWithOAuthProtected(
  provider: 'google' | 'github' | 'microsoft' | 'apple',
  redirectTo?: string
) {
  const supabase = createClient()
  if (!supabase) {
    throw new Error('Supabase client not available')
  }

  // Generate CSRF state
  const state = generateOAuthState()

  // Include state in OAuth flow
  const { data, error } = await supabase.auth.signInWithOAuth({
    provider,
    options: {
      redirectTo: redirectTo || `${window.location.origin}/auth/callback`,
      queryParams: {
        access_type: 'offline',
        prompt: 'consent',
        state, // CSRF protection
      },
    },
  })

  if (error) {
    console.error('[OAuth] Sign in error:', error)
    // Clear state on error
    sessionStorage.removeItem('oauth_state')
    sessionStorage.removeItem('oauth_state_timestamp')
    throw error
  }

  return data
}

/**
 * Handle OAuth callback with CSRF validation
 */
export async function handleOAuthCallback(
  searchParams: URLSearchParams
): Promise<{ success: boolean; error?: string }> {
  const state = searchParams.get('state')
  const error = searchParams.get('error')
  const errorDescription = searchParams.get('error_description')

  // Check for OAuth errors first
  if (error) {
    console.error('[OAuth] Provider error:', error, errorDescription)
    return {
      success: false,
      error: errorDescription || 'OAuth authentication failed'
    }
  }

  // Validate CSRF state
  if (!validateOAuthState(state)) {
    console.error('[OAuth] CSRF validation failed')
    return {
      success: false,
      error: 'Security validation failed. Please try logging in again.'
    }
  }

  // State is valid, Supabase will handle the rest
  const supabase = createClient()
  if (!supabase) {
    return {
      success: false,
      error: 'Authentication service unavailable'
    }
  }

  // Exchange code for session (Supabase handles this automatically)
  const { data: { session }, error: sessionError } = await supabase.auth.getSession()

  if (sessionError || !session) {
    console.error('[OAuth] Session error:', sessionError)
    return {
      success: false,
      error: 'Failed to establish session'
    }
  }

  return { success: true }
}

/**
 * Clear OAuth state (call on error or cancellation)
 */
export function clearOAuthState() {
  sessionStorage.removeItem('oauth_state')
  sessionStorage.removeItem('oauth_state_timestamp')
}
