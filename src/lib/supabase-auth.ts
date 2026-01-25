/**
 * RAPTORFLOW UNIFIED AUTHENTICATION LIBRARY
 * 
 * This is the SINGLE SOURCE OF TRUTH for all authentication operations.
 * DO NOT use any other auth files - they are deprecated.
 * 
 * Supports:
 * - Email/Password authentication
 * - Google OAuth (SSO)
 * - Magic Links (Passwordless)
 * - Password Reset
 * - Session Management
 * - MFA (when enabled)
 */

import { createBrowserClient } from '@supabase/ssr'
import type { 
  Session, 
  User as SupabaseUser, 
  AuthError,
  Provider 
} from '@supabase/supabase-js'
import { getAuthCallbackUrl } from './env-utils'

// =============================================================================
// TYPES
// =============================================================================

export interface RaptorflowUser {
  id: string
  authUserId: string
  email: string
  fullName: string
  avatarUrl?: string
  phone?: string
  role: 'user' | 'admin' | 'super_admin'
  isActive: boolean
  isBanned: boolean
  subscriptionTier: 'ascent' | 'glide' | 'soar' | null
  subscriptionStatus: 'pending' | 'active' | 'cancelled' | 'expired' | 'suspended' | null
  onboardingStatus: 'pending' | 'in_progress' | 'active' | 'skipped'
  defaultWorkspaceId?: string
  createdAt: string
  updatedAt: string
}

export interface AuthResult<T = void> {
  data: T | null
  error: AuthError | Error | null
}

export interface SignUpData {
  email: string
  password: string
  fullName: string
  phone?: string
}

export interface SignInData {
  email: string
  password: string
}

// =============================================================================
// SUPABASE CLIENT
// =============================================================================

let supabaseClient: ReturnType<typeof createBrowserClient> | null = null

/**
 * Get or create Supabase client (singleton pattern)
 * Only available in browser environment
 */
export function getSupabaseClient() {
  if (typeof window === 'undefined') {
    return null
  }

  if (!supabaseClient) {
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
    const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

    if (!supabaseUrl || !supabaseAnonKey) {
      console.error('Missing Supabase environment variables')
      return null
    }

    supabaseClient = createBrowserClient(supabaseUrl, supabaseAnonKey)
  }

  return supabaseClient
}

// =============================================================================
// AUTHENTICATION METHODS
// =============================================================================

/**
 * Sign up with email and password
 * Creates user in auth.users, triggers create public.users and workspace
 */
export async function signUp(data: SignUpData): Promise<AuthResult<{ user: SupabaseUser | null; session: Session | null }>> {
  const supabase = getSupabaseClient()
  if (!supabase) {
    return { data: null, error: new Error('Supabase client not available') }
  }

  try {
    const { data: authData, error } = await supabase.auth.signUp({
      email: data.email,
      password: data.password,
      options: {
        data: {
          full_name: data.fullName,
          phone: data.phone,
        },
        emailRedirectTo: getAuthCallbackUrl(),
      },
    })

    if (error) {
      return { data: null, error }
    }

    return { data: authData, error: null }
  } catch (err) {
    return { data: null, error: err as Error }
  }
}

/**
 * Sign in with email and password
 */
export async function signIn(data: SignInData): Promise<AuthResult<{ user: SupabaseUser | null; session: Session | null }>> {
  const supabase = getSupabaseClient()
  if (!supabase) {
    return { data: null, error: new Error('Supabase client not available') }
  }

  try {
    const { data: authData, error } = await supabase.auth.signInWithPassword({
      email: data.email,
      password: data.password,
    })

    if (error) {
      return { data: null, error }
    }

    return { data: authData, error: null }
  } catch (err) {
    return { data: null, error: err as Error }
  }
}

/**
 * Sign in with OAuth provider (Google, etc.)
 */
export async function signInWithOAuth(provider: Provider = 'google'): Promise<AuthResult<{ url: string | null }>> {
  const supabase = getSupabaseClient()
  if (!supabase) {
    return { data: null, error: new Error('Supabase client not available') }
  }

  try {
    const { data, error } = await supabase.auth.signInWithOAuth({
      provider,
      options: {
        redirectTo: getAuthCallbackUrl(),
        queryParams: {
          access_type: 'offline',
          prompt: 'consent',
        },
      },
    })

    if (error) {
      return { data: null, error }
    }

    return { data: { url: data.url }, error: null }
  } catch (err) {
    return { data: null, error: err as Error }
  }
}

/**
 * Sign in with magic link (passwordless)
 */
export async function signInWithMagicLink(email: string): Promise<AuthResult<void>> {
  const supabase = getSupabaseClient()
  if (!supabase) {
    return { data: null, error: new Error('Supabase client not available') }
  }

  try {
    const { error } = await supabase.auth.signInWithOtp({
      email,
      options: {
        emailRedirectTo: getAuthCallbackUrl(),
        shouldCreateUser: true,
      },
    })

    if (error) {
      return { data: null, error }
    }

    return { data: null, error: null }
  } catch (err) {
    return { data: null, error: err as Error }
  }
}

/**
 * Sign out current user
 */
export async function signOut(): Promise<AuthResult<void>> {
  const supabase = getSupabaseClient()
  if (!supabase) {
    return { data: null, error: new Error('Supabase client not available') }
  }

  try {
    const { error } = await supabase.auth.signOut()

    if (error) {
      return { data: null, error }
    }

    // Clear any local storage
    if (typeof window !== 'undefined') {
      localStorage.removeItem('raptorflow_session')
      localStorage.removeItem('raptorflow_user')
    }

    return { data: null, error: null }
  } catch (err) {
    return { data: null, error: err as Error }
  }
}

// =============================================================================
// PASSWORD MANAGEMENT
// =============================================================================

/**
 * Send password reset email
 */
export async function resetPassword(email: string): Promise<AuthResult<void>> {
  const supabase = getSupabaseClient()
  if (!supabase) {
    return { data: null, error: new Error('Supabase client not available') }
  }

  try {
    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/auth/reset-password`,
    })

    if (error) {
      return { data: null, error }
    }

    return { data: null, error: null }
  } catch (err) {
    return { data: null, error: err as Error }
  }
}

/**
 * Update user password (after clicking reset link)
 */
export async function updatePassword(newPassword: string): Promise<AuthResult<void>> {
  const supabase = getSupabaseClient()
  if (!supabase) {
    return { data: null, error: new Error('Supabase client not available') }
  }

  try {
    const { error } = await supabase.auth.updateUser({
      password: newPassword,
    })

    if (error) {
      return { data: null, error }
    }

    return { data: null, error: null }
  } catch (err) {
    return { data: null, error: err as Error }
  }
}

// =============================================================================
// SESSION & USER MANAGEMENT
// =============================================================================

/**
 * Get current session
 */
export async function getSession(): Promise<AuthResult<Session | null>> {
  const supabase = getSupabaseClient()
  if (!supabase) {
    return { data: null, error: new Error('Supabase client not available') }
  }

  try {
    const { data: { session }, error } = await supabase.auth.getSession()

    if (error) {
      return { data: null, error }
    }

    return { data: session, error: null }
  } catch (err) {
    return { data: null, error: err as Error }
  }
}

/**
 * Get current Supabase auth user
 */
export async function getAuthUser(): Promise<AuthResult<SupabaseUser | null>> {
  const supabase = getSupabaseClient()
  if (!supabase) {
    return { data: null, error: new Error('Supabase client not available') }
  }

  try {
    const { data: { user }, error } = await supabase.auth.getUser()

    if (error) {
      return { data: null, error }
    }

    return { data: user, error: null }
  } catch (err) {
    return { data: null, error: err as Error }
  }
}

/**
 * Get full user profile from public.users table
 */
export async function getUserProfile(): Promise<AuthResult<RaptorflowUser | null>> {
  const supabase = getSupabaseClient()
  if (!supabase) {
    return { data: null, error: new Error('Supabase client not available') }
  }

  try {
    const { data: { user: authUser }, error: authError } = await supabase.auth.getUser()

    if (authError || !authUser) {
      return { data: null, error: authError || new Error('Not authenticated') }
    }

    const { data: usersProfile } = await supabase
      .from('users')
      .select('id, auth_user_id, email, full_name, avatar_url, phone, role, is_active, is_banned, onboarding_status, subscription_plan, subscription_tier, subscription_status, created_at, updated_at')
      .eq('auth_user_id', authUser.id)
      .maybeSingle()

    if (usersProfile) {
      return {
        data: {
          id: usersProfile.id,
          authUserId: usersProfile.auth_user_id || authUser.id,
          email: usersProfile.email || authUser.email || '',
          fullName: usersProfile.full_name || usersProfile.email?.split('@')[0] || 'User',
          avatarUrl: usersProfile.avatar_url,
          phone: usersProfile.phone,
          role: usersProfile.role || 'user',
          isActive: usersProfile.is_active ?? true,
          isBanned: usersProfile.is_banned ?? false,
          subscriptionTier: usersProfile.subscription_plan || usersProfile.subscription_tier || null,
          subscriptionStatus: usersProfile.subscription_status || null,
          onboardingStatus: usersProfile.onboarding_status || 'pending',
          createdAt: usersProfile.created_at,
          updatedAt: usersProfile.updated_at,
        },
        error: null,
      }
    }

    const { data: profilesRecord } = await supabase
      .from('profiles')
      .select('id, email, full_name, avatar_url, role, onboarding_status, subscription_plan, subscription_status, workspace_id, created_at, updated_at')
      .eq('id', authUser.id)
      .maybeSingle()

    if (profilesRecord) {
      const { data: subscription } = await supabase
        .from('subscriptions')
        .select('status, plan_id')
        .eq('user_id', profilesRecord.id)
        .maybeSingle()

      return {
        data: {
          id: profilesRecord.id,
          authUserId: authUser.id,
          email: profilesRecord.email || authUser.email || '',
          fullName: profilesRecord.full_name || profilesRecord.email?.split('@')[0] || 'User',
          avatarUrl: profilesRecord.avatar_url,
          role: profilesRecord.role || 'user',
          isActive: true,
          isBanned: false,
          subscriptionTier: subscription?.plan_id || profilesRecord.subscription_plan || null,
          subscriptionStatus: subscription?.status || profilesRecord.subscription_status || null,
          onboardingStatus: profilesRecord.onboarding_status || 'pending',
          defaultWorkspaceId: profilesRecord.workspace_id,
          createdAt: profilesRecord.created_at,
          updatedAt: profilesRecord.updated_at,
        },
        error: null,
      }
    }

    const { data: userProfilesRecord } = await supabase
      .from('user_profiles')
      .select('id, email, full_name, avatar_url, subscription_plan, subscription_status, created_at, updated_at')
      .eq('id', authUser.id)
      .maybeSingle()

    if (userProfilesRecord) {
      return {
        data: {
          id: userProfilesRecord.id,
          authUserId: authUser.id,
          email: userProfilesRecord.email || authUser.email || '',
          fullName: userProfilesRecord.full_name || userProfilesRecord.email?.split('@')[0] || 'User',
          avatarUrl: userProfilesRecord.avatar_url,
          role: 'user',
          isActive: true,
          isBanned: false,
          subscriptionTier: userProfilesRecord.subscription_plan || null,
          subscriptionStatus: userProfilesRecord.subscription_status || null,
          onboardingStatus: 'pending',
          createdAt: userProfilesRecord.created_at,
          updatedAt: userProfilesRecord.updated_at,
        },
        error: null,
      }
    }

    return {
      data: {
        id: authUser.id,
        authUserId: authUser.id,
        email: authUser.email || '',
        fullName: authUser.user_metadata?.full_name || authUser.email?.split('@')[0] || 'User',
        role: 'user',
        isActive: true,
        isBanned: false,
        subscriptionTier: null,
        subscriptionStatus: null,
        onboardingStatus: 'pending',
        createdAt: authUser.created_at,
        updatedAt: authUser.updated_at || authUser.created_at,
      },
      error: null,
    }
  } catch (err) {
    return { data: null, error: err as Error }
  }
}

/**
 * Check if user is authenticated
 */
export async function isAuthenticated(): Promise<boolean> {
  const { data: session } = await getSession()
  return !!session
}

/**
 * Check if user has active subscription
 */
export async function hasActiveSubscription(): Promise<boolean> {
  const { data: user } = await getUserProfile()
  return user?.subscriptionStatus === 'active'
}

/**
 * Check if user has completed onboarding
 */
export async function hasCompletedOnboarding(): Promise<boolean> {
  const { data: user } = await getUserProfile()
  return user?.onboardingStatus === 'active'
}

// =============================================================================
// MFA METHODS
// =============================================================================

/**
 * Enroll TOTP MFA (returns QR code URL)
 */
export async function enrollTOTP(): Promise<AuthResult<{ qr: string; secret: string; uri: string }>> {
  const supabase = getSupabaseClient()
  if (!supabase) {
    return { data: null, error: new Error('Supabase client not available') }
  }

  try {
    const { data, error } = await supabase.auth.mfa.enroll({
      factorType: 'totp',
      friendlyName: 'Authenticator App',
    })

    if (error) {
      return { data: null, error }
    }

    return {
      data: {
        qr: data.totp.qr_code,
        secret: data.totp.secret,
        uri: data.totp.uri,
      },
      error: null,
    }
  } catch (err) {
    return { data: null, error: err as Error }
  }
}

/**
 * Verify TOTP code during enrollment
 */
export async function verifyTOTP(factorId: string, code: string): Promise<AuthResult<void>> {
  const supabase = getSupabaseClient()
  if (!supabase) {
    return { data: null, error: new Error('Supabase client not available') }
  }

  try {
    const { data: challenge, error: challengeError } = await supabase.auth.mfa.challenge({
      factorId,
    })

    if (challengeError) {
      return { data: null, error: challengeError }
    }

    const { error: verifyError } = await supabase.auth.mfa.verify({
      factorId,
      challengeId: challenge.id,
      code,
    })

    if (verifyError) {
      return { data: null, error: verifyError }
    }

    return { data: null, error: null }
  } catch (err) {
    return { data: null, error: err as Error }
  }
}

/**
 * Get MFA factors for current user
 */
export async function getMFAFactors(): Promise<AuthResult<{ totp: any[]; phone: any[] }>> {
  const supabase = getSupabaseClient()
  if (!supabase) {
    return { data: null, error: new Error('Supabase client not available') }
  }

  try {
    const { data, error } = await supabase.auth.mfa.listFactors()

    if (error) {
      return { data: null, error }
    }

    return {
      data: {
        totp: data.totp || [],
        phone: data.phone || [],
      },
      error: null,
    }
  } catch (err) {
    return { data: null, error: err as Error }
  }
}

/**
 * Check if MFA is required for current session
 */
export async function isMFARequired(): Promise<boolean> {
  const supabase = getSupabaseClient()
  if (!supabase) return false

  try {
    const { data, error } = await supabase.auth.mfa.getAuthenticatorAssuranceLevel()
    
    if (error) return false

    // If current level is aal1 but next level requires aal2, MFA is needed
    return data.currentLevel === 'aal1' && data.nextLevel === 'aal2'
  } catch {
    return false
  }
}

// =============================================================================
// EMAIL VERIFICATION
// =============================================================================

/**
 * Resend verification email
 */
export async function resendVerificationEmail(email: string): Promise<AuthResult<void>> {
  const supabase = getSupabaseClient()
  if (!supabase) {
    return { data: null, error: new Error('Supabase client not available') }
  }

  try {
    const { error } = await supabase.auth.resend({
      type: 'signup',
      email,
      options: {
        emailRedirectTo: getAuthCallbackUrl(),
      },
    })

    if (error) {
      return { data: null, error }
    }

    return { data: null, error: null }
  } catch (err) {
    return { data: null, error: err as Error }
  }
}

// =============================================================================
// AUTH STATE LISTENER
// =============================================================================

/**
 * Subscribe to auth state changes
 */
export function onAuthStateChange(
  callback: (event: string, session: Session | null) => void
): { unsubscribe: () => void } {
  const supabase = getSupabaseClient()
  
  if (!supabase) {
    return { unsubscribe: () => {} }
  }

  const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
    callback(event, session)
  })

  return { unsubscribe: () => subscription.unsubscribe() }
}

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

/**
 * Validate password strength
 */
export function validatePassword(password: string): { valid: boolean; errors: string[] } {
  const errors: string[] = []

  if (password.length < 8) {
    errors.push('Password must be at least 8 characters')
  }
  if (!/[A-Z]/.test(password)) {
    errors.push('Password must contain at least one uppercase letter')
  }
  if (!/[a-z]/.test(password)) {
    errors.push('Password must contain at least one lowercase letter')
  }
  if (!/[0-9]/.test(password)) {
    errors.push('Password must contain at least one number')
  }
  if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    errors.push('Password must contain at least one special character')
  }

  return {
    valid: errors.length === 0,
    errors,
  }
}

/**
 * Validate email format
 */
export function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

// =============================================================================
// EXPORTS
// =============================================================================

export default {
  // Client
  getSupabaseClient,
  
  // Auth methods
  signUp,
  signIn,
  signInWithOAuth,
  signInWithMagicLink,
  signOut,
  
  // Password
  resetPassword,
  updatePassword,
  
  // Session & User
  getSession,
  getAuthUser,
  getUserProfile,
  isAuthenticated,
  hasActiveSubscription,
  hasCompletedOnboarding,
  
  // MFA
  enrollTOTP,
  verifyTOTP,
  getMFAFactors,
  isMFARequired,
  
  // Email
  resendVerificationEmail,
  
  // Listener
  onAuthStateChange,
  
  // Utilities
  validatePassword,
  validateEmail,
}
