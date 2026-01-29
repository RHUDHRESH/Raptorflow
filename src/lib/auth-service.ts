/**
 * Centralized Authentication Service
 * Handles all authentication operations with proper key separation
 * CONSOLIDATED: Single source of truth for all auth operations
 */

import { createClient } from '@/lib/supabase/client'
import { getAuthCallbackUrl, getBaseUrl } from '@/lib/env-utils'
// Only import server-side modules in server environment
const isServer = typeof window === 'undefined'
let createServerClient: any = null
let cookies: any = null

if (isServer) {
  try {
    // Use dynamic imports for server-side modules
    import('@supabase/ssr').then(({ createServerClient: serverClient }) => {
      createServerClient = serverClient
    }).catch(() => {
      // Server modules not available
    })
    import('next/headers').then(({ cookies: serverCookies }) => {
      cookies = serverCookies
    }).catch(() => {
      // Server modules not available
    })
  } catch (e) {
    // Server modules not available
  }
}

import type { User as SupabaseUser, Session, AuthError, Provider } from '@supabase/supabase-js'

// =============================================================================
// CONFIGURATION & HELPER FUNCTIONS
// =============================================================================

/**
 * Get auth configuration (consolidated from auth-config.ts)
 */
export function getAuthConfig() {
  return {
    baseUrl: getBaseUrl(),
    authCallbackUrl: getAuthCallbackUrl(),
    isDevelopment: process.env.NODE_ENV === 'development',
    isProduction: process.env.NODE_ENV === 'production',
    oauth: {
      google: {
        enabled: !!(process.env.GOOGLE_CLIENT_ID && process.env.GOOGLE_CLIENT_SECRET),
        clientId: process.env.GOOGLE_CLIENT_ID,
      },
      github: {
        enabled: !!(process.env.GITHUB_CLIENT_ID && process.env.GITHUB_CLIENT_SECRET),
        clientId: process.env.GITHUB_CLIENT_ID,
      },
    },
    supabase: {
      url: process.env.NEXT_PUBLIC_SUPABASE_URL,
      hasAnonKey: !!process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
    }
  }
}

/**
 * Handle authentication error (consolidated from auth-helpers.ts)
 */
export function handleAuthError(error: any): string {
  if (error instanceof Error) {
    return error.message;
  }

  if (typeof error === 'string') {
    return error;
  }

  return 'An unknown error occurred';
}

/**
 * Redirect to sign in page (consolidated from auth-helpers.ts)
 */
export function redirectToLogin(): void {
  if (typeof window !== 'undefined') {
    window.location.href = '/signin';
  }
}

/**
 * Redirect to dashboard (consolidated from auth-helpers.ts)
 */
export function redirectToDashboard(): void {
  if (typeof window !== 'undefined') {
    window.location.href = '/dashboard';
  }
}

/**
 * Check if user is authenticated using API (consolidated from auth-helpers.ts)
 */
export async function isAuthenticated(): Promise<boolean> {
  try {
    const response = await fetch('/api/auth/me');
    return response.ok;
  } catch (error) {
    console.error('🔐 [Auth] Error checking authentication:', error);
    return false;
  }
}

/**
 * Get current user data using API (consolidated from auth-helpers.ts)
 */
export async function getCurrentUserAPI(): Promise<{
  userId: string;
  email: string;
} | null> {
  try {
    const response = await fetch('/api/auth/me');

    if (!response.ok) {
      return null;
    }

    const data = await response.json();
    return data.user;
  } catch (error) {
    console.error('🔐 [Auth] Error getting current user:', error);
    return null;
  }
}

// =============================================================================
// TYPES
// =============================================================================

export interface AuthUser {
  id: string
  email: string
  fullName: string
  avatarUrl?: string
  phone?: string
  role: 'user' | 'admin' | 'super_admin'
  subscriptionPlan: 'soar' | 'glide' | 'ascent' | 'free' | null
  subscriptionStatus: 'active' | 'trial' | 'cancelled' | 'expired' | 'none' | 'pending' | 'suspended' | null
  onboardingStatus: 'pending' | 'in_progress' | 'active' | 'skipped'
  hasCompletedOnboarding: boolean
  isActive: boolean
  isBanned: boolean
  createdAt: string
  updatedAt?: string
  workspaceId?: string
  ucid?: string
}

export interface AuthResult<T = void> {
  success: boolean
  data?: T
  user?: AuthUser
  session?: Session
  error?: string
  authError?: AuthError
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
// CROSS-TAB COMMUNICATION
// =============================================================================

class CrossTabManager {
  private broadcastChannel: BroadcastChannel | null = null;
  private storageKey = 'auth_session_event';
  private isEdgeRuntime: boolean;
  private isSigningOut = false; // Prevent duplicate signout handling
  private useBroadcastChannel = false; // Track which mechanism we're using

  // Store bound handlers as class fields to properly remove them later
  private boundHandleBroadcastMessage: ((event: MessageEvent) => void) | null = null;
  private boundHandleStorageEvent: ((event: StorageEvent) => void) | null = null;

  constructor() {
    // Check if we're in Edge Runtime (middleware)
    this.isEdgeRuntime = typeof window === 'undefined' && typeof globalThis !== 'undefined' &&
                       (globalThis as any).EdgeRuntime !== undefined;

    // Only initialize for client-side (not Edge Runtime)
    if (this.isEdgeRuntime || typeof window === 'undefined') {
      return;
    }

    // Prefer BroadcastChannel if available (no fallback needed if BC works)
    if (typeof BroadcastChannel !== 'undefined') {
      try {
        this.broadcastChannel = new BroadcastChannel('auth_session');
        this.boundHandleBroadcastMessage = this.handleBroadcastMessage.bind(this);
        this.broadcastChannel.onmessage = this.boundHandleBroadcastMessage;
        this.useBroadcastChannel = true;
      } catch (error) {
        console.warn('BroadcastChannel not available, using localStorage fallback');
      }
    }

    // Only use storage fallback if BroadcastChannel is not available
    if (!this.useBroadcastChannel) {
      this.boundHandleStorageEvent = this.handleStorageEvent.bind(this);
      window.addEventListener('storage', this.boundHandleStorageEvent);
    }
  }

  private handleBroadcastMessage(event: MessageEvent) {
    if (event.data.type === 'SIGN_OUT') {
      this.handleSignOut();
    } else if (event.data.type === 'SESSION_REFRESH') {
      this.handleSessionRefresh(event.data.session);
    }
  }

  private handleStorageEvent(event: StorageEvent) {
    if (event.key === this.storageKey && event.newValue) {
      try {
        const data = JSON.parse(event.newValue);
        if (data.type === 'SIGN_OUT') {
          this.handleSignOut();
        } else if (data.type === 'SESSION_REFRESH') {
          this.handleSessionRefresh(data.session);
        }
      } catch (error) {
        console.error('Error parsing storage event:', error);
      }
    }
  }

  private handleSignOut() {
    // Idempotent: if already signing out or already on login page, skip
    if (this.isSigningOut) {
      return;
    }

    if (typeof window !== 'undefined') {
      // Check if already on sign in page
      if (window.location.pathname === '/signin') {
        return;
      }

      this.isSigningOut = true;

      // Clear local caches
      localStorage.removeItem('auth_cache');
      sessionStorage.removeItem('auth_cache');
      localStorage.removeItem('session_cache');
      localStorage.removeItem('raptorflow_session');
      localStorage.removeItem('raptorflow_user');

      // Redirect to sign in
      window.location.href = '/signin';
    }
  }

  private handleSessionRefresh(session: Session) {
    // Update local cache with new session
    if (typeof window !== 'undefined' && session) {
      const cachedData = {
        session,
        timestamp: Date.now()
      };
      localStorage.setItem('session_cache', JSON.stringify(cachedData));
    }
  }

  public broadcastSignOut() {
    // Skip broadcasting in Edge Runtime (middleware)
    if (this.isEdgeRuntime || typeof window === 'undefined') {
      return;
    }

    // Use only one mechanism to avoid duplicate events
    if (this.useBroadcastChannel && this.broadcastChannel) {
      this.broadcastChannel.postMessage({ type: 'SIGN_OUT' });
    } else {
      // Fallback to localStorage for older browsers
      localStorage.setItem(this.storageKey, JSON.stringify({
        type: 'SIGN_OUT',
        timestamp: Date.now()
      }));

      // Clear the event after a short delay
      setTimeout(() => {
        localStorage.removeItem(this.storageKey);
      }, 1000);
    }
  }

  public broadcastSessionRefresh(session: Session) {
    // Skip broadcasting in Edge Runtime (middleware)
    if (this.isEdgeRuntime || typeof window === 'undefined') {
      return;
    }

    // Use only one mechanism to avoid duplicate events
    if (this.useBroadcastChannel && this.broadcastChannel) {
      this.broadcastChannel.postMessage({
        type: 'SESSION_REFRESH',
        session
      });
    } else {
      // Fallback to localStorage for older browsers
      localStorage.setItem(this.storageKey, JSON.stringify({
        type: 'SESSION_REFRESH',
        session,
        timestamp: Date.now()
      }));

      // Clear the event after a short delay
      setTimeout(() => {
        localStorage.removeItem(this.storageKey);
      }, 1000);
    }
  }

  public cleanup() {
    if (this.broadcastChannel) {
      this.broadcastChannel.close();
      this.broadcastChannel = null;
    }

    // Use the stored bound handler reference for proper removal
    if (typeof window !== 'undefined' && this.boundHandleStorageEvent) {
      window.removeEventListener('storage', this.boundHandleStorageEvent);
      this.boundHandleStorageEvent = null;
    }

    this.isSigningOut = false;
  }
}

// =============================================================================
// CLIENT-SIDE AUTH SERVICE
// =============================================================================

export class ClientAuthService {
  private supabase = createClient()
  private crossTabManager: CrossTabManager | null = null

  constructor() {
    // Only initialize CrossTabManager on client side (not in Edge Runtime)
    if (typeof window !== 'undefined') {
      this.crossTabManager = new CrossTabManager();
    }
  }

  /**
   * Cleanup resources when service is destroyed
   */
  public cleanup() {
    if (this.crossTabManager) {
      this.crossTabManager.cleanup();
    }
  }

  /**
   * Get the underlying Supabase client
   */
  public getSupabaseClient() {
    return this.supabase
  }

  /**
   * Get current session with proper error handling
   */
  async getSession(): Promise<Session | null> {
    try {
      const { data: { session }, error } = await this.supabase.auth.getSession()
      if (error) {
        console.error('Error getting session:', error)
        return null
      }
      return session
    } catch (error) {
      console.error('Unexpected error getting session:', error)
      return null
    }
  }

  /**
   * Get current user with profile data
   */
  async getCurrentUser(): Promise<AuthUser | null> {
    try {
      const session = await this.getSession()
      if (!session?.user) {
        return null
      }

      return await this.loadUserData(session.user)
    } catch (error) {
      console.error('Error getting current user:', error)
      return null
    }
  }

  /**
   * Load user data from database with unified lookup strategy
   * Order of priority: profiles -> users -> user_profiles -> auth metadata
   */
  private async loadUserData(supabaseUser: SupabaseUser): Promise<AuthUser> {
    try {
      // 1. Primary: profiles table (modern schema)
      const { data: profile } = await this.supabase
        .from('profiles')
        .select('*')
        .eq('id', supabaseUser.id)
        .maybeSingle()

      if (profile) {
        return {
          id: supabaseUser.id,
          email: profile.email || supabaseUser.email || '',
          fullName: profile.full_name || supabaseUser.user_metadata?.full_name || profile.email?.split('@')[0] || 'User',
          avatarUrl: profile.avatar_url || supabaseUser.user_metadata?.avatar_url,
          role: profile.role || (supabaseUser.user_metadata?.role as any) || 'user',
          subscriptionPlan: (profile.subscription_plan || supabaseUser.user_metadata?.subscription_plan || 'free') as any,
          subscriptionStatus: (profile.subscription_status || supabaseUser.user_metadata?.subscription_status || 'none') as any,
          onboardingStatus: (profile.onboarding_status || supabaseUser.user_metadata?.onboarding_status || 'pending') as any,
          hasCompletedOnboarding: profile.onboarding_status === 'active' || supabaseUser.user_metadata?.has_completed_onboarding === true,
          isActive: profile.is_active ?? true,
          isBanned: profile.is_banned ?? false,
          createdAt: profile.created_at || supabaseUser.created_at,
          updatedAt: profile.updated_at,
          workspaceId: profile.workspace_id || supabaseUser.user_metadata?.workspace_id,
          ucid: profile.ucid
        }
      }

      // 2. Fallback: users table (some legacy parts use this)
      const { data: userRecord } = await this.supabase
        .from('users')
        .select('*')
        .or(`id.eq.${supabaseUser.id},auth_user_id.eq.${supabaseUser.id}`)
        .maybeSingle()

      if (userRecord) {
        return {
          id: userRecord.id || supabaseUser.id,
          email: userRecord.email || supabaseUser.email || '',
          fullName: userRecord.full_name || supabaseUser.user_metadata?.full_name || userRecord.email?.split('@')[0] || 'User',
          avatarUrl: userRecord.avatar_url || supabaseUser.user_metadata?.avatar_url,
          phone: userRecord.phone,
          role: userRecord.role || (supabaseUser.user_metadata?.role as any) || 'user',
          subscriptionPlan: (userRecord.subscription_plan || userRecord.subscription_tier || supabaseUser.user_metadata?.subscription_plan || 'free') as any,
          subscriptionStatus: (userRecord.subscription_status || supabaseUser.user_metadata?.subscription_status || 'none') as any,
          onboardingStatus: (userRecord.onboarding_status || supabaseUser.user_metadata?.onboarding_status || 'pending') as any,
          hasCompletedOnboarding: userRecord.onboarding_status === 'active',
          isActive: userRecord.is_active ?? true,
          isBanned: userRecord.is_banned ?? false,
          createdAt: userRecord.created_at || supabaseUser.created_at,
          updatedAt: userRecord.updated_at,
          workspaceId: userRecord.workspace_id || supabaseUser.user_metadata?.workspace_id,
        }
      }

      // 3. Last Resort Fallback: user_profiles table
      const { data: legacyProfile } = await this.supabase
        .from('user_profiles')
        .select('*')
        .eq('id', supabaseUser.id)
        .maybeSingle()

      if (legacyProfile) {
        return {
          id: supabaseUser.id,
          email: legacyProfile.email || supabaseUser.email || '',
          fullName: legacyProfile.full_name || supabaseUser.user_metadata?.full_name || legacyProfile.email?.split('@')[0] || 'User',
          role: (supabaseUser.user_metadata?.role as any) || 'user',
          subscriptionPlan: (legacyProfile.subscription_plan || 'free') as any,
          subscriptionStatus: (legacyProfile.subscription_status || 'none') as any,
          onboardingStatus: (supabaseUser.user_metadata?.onboarding_status || 'pending') as any,
          hasCompletedOnboarding: supabaseUser.user_metadata?.has_completed_onboarding === true,
          isActive: true,
          isBanned: false,
          createdAt: legacyProfile.created_at || supabaseUser.created_at,
          workspaceId: supabaseUser.user_metadata?.workspace_id,
        }
      }
    } catch (error) {
      console.error('Error in unified user data lookup:', error)
    }

    // 4. Emergency: use Supabase Auth metadata only
    return {
      id: supabaseUser.id,
      email: supabaseUser.email || '',
      fullName: supabaseUser.user_metadata?.full_name || supabaseUser.email?.split('@')[0] || 'User',
      avatarUrl: supabaseUser.user_metadata?.avatar_url,
      role: (supabaseUser.user_metadata?.role as any) || 'user',
      subscriptionPlan: (supabaseUser.user_metadata?.subscription_plan || 'free') as any,
      subscriptionStatus: (supabaseUser.user_metadata?.subscription_status || 'none') as any,
      onboardingStatus: (supabaseUser.user_metadata?.onboarding_status || 'pending') as any,
      hasCompletedOnboarding: supabaseUser.user_metadata?.has_completed_onboarding === true,
      isActive: true,
      isBanned: false,
      createdAt: supabaseUser.created_at,
      workspaceId: supabaseUser.user_metadata?.workspace_id,
    }
  }

  /**
   * Sign in with OAuth provider (Google, GitHub, etc.)
   */
  async signInWithOAuth(provider: Provider, options?: any): Promise<{ success: boolean; error?: string; url?: string }> {
    try {
      const { data, error } = await this.supabase.auth.signInWithOAuth({
        provider,
        options: {
          redirectTo: getAuthCallbackUrl(),
          queryParams: {
            access_type: 'offline',
            prompt: 'consent',
          },
          ...options
        },
      });

      if (error) {
        console.error('OAuth error:', error);
        return { success: false, error: error.message };
      }

      return { success: true, url: data.url || undefined };
    } catch (error) {
      console.error('OAuth sign in error:', error);
      return { success: false, error: error instanceof Error ? error.message : 'OAuth sign in failed' };
    }
  }

  /**
   * Sign up with email and password
   */
  async signUp(data: SignUpData): Promise<AuthResult<{ user: SupabaseUser | null; session: Session | null }>> {
    try {
      const { data: authData, error } = await this.supabase.auth.signUp({
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
        return { success: false, error: error.message, authError: error }
      }

      return { success: true, data: authData }
    } catch (err) {
      return { success: false, error: err instanceof Error ? err.message : 'Sign up failed' }
    }
  }

  /**
   * Sign in with email and password
   */
  async signIn(data: SignInData): Promise<AuthResult<{ user: SupabaseUser | null; session: Session | null }>> {
    try {
      const { data: authData, error } = await this.supabase.auth.signInWithPassword({
        email: data.email,
        password: data.password,
      })

      if (error) {
        return { success: false, error: error.message, authError: error }
      }

      const user = authData.user ? await this.loadUserData(authData.user) : undefined

      return {
        success: true,
        data: authData,
        user,
        session: authData.session || undefined
      }
    } catch (err) {
      return { success: false, error: err instanceof Error ? err.message : 'Sign in failed' }
    }
  }

  /**
   * Sign in with magic link (passwordless)
   */
  async signInWithMagicLink(email: string): Promise<AuthResult> {
    try {
      const { error } = await this.supabase.auth.signInWithOtp({
        email,
        options: {
          emailRedirectTo: getAuthCallbackUrl(),
          shouldCreateUser: true,
        },
      })

      if (error) {
        return { success: false, error: error.message, authError: error }
      }

      return { success: true }
    } catch (err) {
      return { success: false, error: err instanceof Error ? err.message : 'Magic link failed' }
    }
  }

  /**
   * Send password reset email
   */
  async resetPassword(email: string): Promise<AuthResult> {
    try {
      const { error } = await this.supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${getAuthCallbackUrl().replace('/auth/callback', '')}/auth/reset-password`,
      })

      if (error) {
        return { success: false, error: error.message, authError: error }
      }

      return { success: true }
    } catch (err) {
      return { success: false, error: err instanceof Error ? err.message : 'Password reset failed' }
    }
  }

  /**
   * Update user password
   */
  async updatePassword(newPassword: string): Promise<AuthResult> {
    try {
      const { error } = await this.supabase.auth.updateUser({
        password: newPassword,
      })

      if (error) {
        return { success: false, error: error.message, authError: error }
      }

      return { success: true }
    } catch (err) {
      return { success: false, error: err instanceof Error ? err.message : 'Password update failed' }
    }
  }

  /**
   * Enroll TOTP MFA
   */
  async enrollTOTP(): Promise<AuthResult<{ qr: string; secret: string; uri: string }>> {
    try {
      const { data, error } = await this.supabase.auth.mfa.enroll({
        factorType: 'totp'
      })

      if (error) {
        return { success: false, error: error.message, authError: error }
      }

      return {
        success: true,
        data: {
          qr: data.totp.qr_code,
          secret: data.totp.secret,
          uri: data.totp.uri
        }
      }
    } catch (err) {
      return { success: false, error: err instanceof Error ? err.message : 'MFA enrollment failed' }
    }
  }

  /**
   * Verify TOTP MFA
   */
  async verifyTOTP(factorId: string, code: string): Promise<AuthResult> {
    try {
      const { error } = await this.supabase.auth.mfa.challengeAndVerify({
        factorId,
        code
      })

      if (error) {
        return { success: false, error: error.message, authError: error }
      }

      return { success: true }
    } catch (err) {
      return { success: false, error: err instanceof Error ? err.message : 'MFA verification failed' }
    }
  }

  /**
   * Unenroll MFA
   */
  async unenrollMFA(factorId: string): Promise<AuthResult> {
    try {
      const { error } = await this.supabase.auth.mfa.unenroll({
        factorId
      })

      if (error) {
        return { success: false, error: error.message, authError: error }
      }

      return { success: true }
    } catch (err) {
      return { success: false, error: err instanceof Error ? err.message : 'MFA unenrollment failed' }
    }
  }

  /**
   * Check if user has active subscription
   */
  async hasActiveSubscription(): Promise<boolean> {
    const user = await this.getCurrentUser()
    return user?.subscriptionStatus === 'active' || user?.subscriptionStatus === 'trial'
  }

  /**
   * Check if user has completed onboarding
   */
  async hasCompletedOnboarding(): Promise<boolean> {
    const user = await this.getCurrentUser()
    return user?.onboardingStatus === 'active' || user?.hasCompletedOnboarding === true
  }

  /**
   * Resend verification email
   */
  async resendVerificationEmail(email: string): Promise<AuthResult> {
    try {
      const { error } = await this.supabase.auth.resend({
        type: 'signup',
        email,
        options: {
          emailRedirectTo: getAuthCallbackUrl(),
        },
      })

      if (error) {
        return { success: false, error: error.message, authError: error }
      }

      return { success: true }
    } catch (err) {
      return { success: false, error: err instanceof Error ? err.message : 'Resend verification failed' }
    }
  }

  /**
   * Update user onboarding status
   */
  async updateOnboardingStatus(status: string): Promise<AuthResult> {
    try {
      const user = await this.getCurrentUser()
      if (!user) {
        return { success: false, error: 'Not authenticated' }
      }

      const { error } = await this.supabase
        .from('profiles')
        .update({ onboarding_status: status })
        .eq('id', user.id)

      if (error) {
        // Fallback to users table if profiles update fails
        const { error: usersError } = await this.supabase
          .from('users')
          .update({ onboarding_status: status })
          .eq('auth_user_id', user.id)

        if (usersError) {
          return { success: false, error: usersError.message }
        }
      }

      return { success: true }
    } catch (err) {
      return { success: false, error: err instanceof Error ? err.message : 'Update onboarding status failed' }
    }
  }

  /**
   * Sign out with proper cleanup and cross-tab invalidation
   */
  async signOut(): Promise<{ success: boolean; error?: string }> {
    try {
      // Sign out from Supabase
      await this.supabase.auth.signOut()

      // Broadcast sign out to all tabs (if available)
      if (this.crossTabManager) {
        this.crossTabManager.broadcastSignOut();
      }

      // Clear any local storage/cache
      if (typeof window !== 'undefined') {
        localStorage.removeItem('auth_cache')
        sessionStorage.removeItem('auth_cache')
        localStorage.removeItem('session_cache')
      }

      return { success: true }
    } catch (error) {
      console.error('Error signing out:', error)

      // Still broadcast sign out even if Supabase sign out fails
      if (this.crossTabManager) {
        this.crossTabManager.broadcastSignOut();
      }

      return { success: false, error: 'Failed to sign out' }
    }
  }

  /**
   * Refresh user data
   */
  async refreshUser(): Promise<AuthUser | null> {
    return this.getCurrentUser()
  }

  /**
   * Check if user is authenticated
   */
  async isAuthenticated(): Promise<boolean> {
    const session = await this.getSession()
    return !!session?.user
  }

  /**
   * Get cached user data (client-side only)
   */
  getCachedUser(): AuthUser | null {
    if (typeof window === 'undefined') return null

    try {
      const cached = localStorage.getItem('auth_cache')
      if (cached) {
        const data = JSON.parse(cached)
        // Check if cache is still valid (5 minutes)
        if (Date.now() - data.timestamp < 5 * 60 * 1000) {
          return data.user
        }
      }
    } catch (error) {
      console.error('Error reading cached user:', error)
    }

    return null
  }

  /**
   * Cache user data (client-side only)
   */
  private cacheUser(user: AuthUser): void {
    if (typeof window === 'undefined') return

    try {
      localStorage.setItem('auth_cache', JSON.stringify({
        user,
        timestamp: Date.now()
      }))
    } catch (error) {
      console.error('Error caching user:', error)
    }
  }
}

// =============================================================================
// SERVER-SIDE AUTH SERVICE (for middleware/API routes)
// =============================================================================

export class ServerAuthService {
  private supabase: any

  constructor(request?: any) {
    // Only create server client in server environment
    if (!isServer || !createServerClient || !cookies) {
      throw new Error('ServerAuthService can only be used in server environment')
    }

    // Create server client with proper cookie handling
    const cookieStore = cookies()
    this.supabase = createServerClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!, // Always use anon key for session validation
      {
        cookies: {
          getAll() {
            if (request) {
              return request.cookies.getAll()
            }
            return cookies().getAll()
          },
          setAll(cookiesToSet: Array<{name: string; value: string; options?: any}>) {
            cookiesToSet.forEach(({ name, value, options }) => {
              if (request) {
                request.cookies.set(name, value)
              } else {
                cookies().set(name, value, options)
              }
            })
          },
        },
      }
    )
  }

  /**
   * Validate session with robust error handling
   * Uses getUser() for secure authentication (getSession can be spoofed from cookies)
   */
  async validateSession(): Promise<{ valid: boolean; user?: any; needsRotation?: boolean; error?: string }> {
    try {
      // Use getUser() for secure server-side validation
      // This contacts the Supabase Auth server to verify the token
      const { data: { user: authUser }, error: userError } = await this.supabase.auth.getUser()

      if (userError || !authUser) {
        return { valid: false, error: userError?.message || 'No authenticated user' }
      }

      // Get session for expiry info (but user is already verified)
      const { data: { session } } = await this.supabase.auth.getSession()

      // Check if session needs rotation - based on time until expiry
      let needsRotation = false
      if (session?.expires_at) {
        // expires_at is a unix timestamp in seconds from Supabase
        const expiresAtMs = typeof session.expires_at === 'number'
          ? session.expires_at * 1000
          : new Date(session.expires_at).getTime()
        const timeUntilExpiry = expiresAtMs - Date.now()

        // Rotate if less than 5 minutes until expiry, or already expired
        if (timeUntilExpiry < 5 * 60 * 1000) {
          needsRotation = true
        }
      } else {
        // If no session or expires_at, be safe and rotate
        needsRotation = true
      }

      // Get user data with workspace lookup
      const userData = await this.loadUserDataWithWorkspace(authUser)

      return {
        valid: true,
        user: { ...authUser, ...userData },
        needsRotation
      }
    } catch (error) {
      console.error('Session validation error:', error)
      return { valid: false, error: 'Session validation failed' }
    }
  }

  /**
   * Load user data with workspace lookup to prevent redirect loops
   */
  private async loadUserDataWithWorkspace(supabaseUser: SupabaseUser): Promise<any> {
    let workspaceId = supabaseUser.user_metadata?.workspace_id
    let onboardingStatus = supabaseUser.user_metadata?.onboarding_status
    let subscriptionStatus = supabaseUser.user_metadata?.subscription_status

    // ROBUSTNESS: If workspace_id is missing from metadata, try to fetch it from the database
    if (!workspaceId) {
      const { data: workspace, error: wsError } = await this.supabase
        .from('workspaces')
        .select('id')
        .eq('owner_id', supabaseUser.id)
        .limit(1)
        .maybeSingle()

      if (!wsError && workspace) {
        workspaceId = workspace.id
      }
    }

    // Always check profile for full_name (not just when onboarding is pending)
    const { data: profile } = await this.supabase
      .from('profiles')
      .select('onboarding_status, full_name')
      .eq('id', supabaseUser.id)
      .maybeSingle()

    if (profile?.onboarding_status) {
      onboardingStatus = profile.onboarding_status
    }

    // Store full_name in user metadata for client-side access
    if (profile?.full_name) {
      supabaseUser.user_metadata = {
        ...supabaseUser.user_metadata,
        full_name: profile.full_name
      }
    }

    // Additional checks for onboarding status if still pending
    if (!onboardingStatus || onboardingStatus === 'pending') {
        const { data: userProfile } = await this.supabase
          .from('user_profiles')
          .select('id')
          .eq('id', supabaseUser.id)
          .maybeSingle()

        if (userProfile) {
          onboardingStatus = onboardingStatus || 'pending'
        }
      }

      if (!onboardingStatus || onboardingStatus === 'pending') {
        const { data: usersRecord } = await this.supabase
          .from('users')
          .select('onboarding_status')
          .eq('auth_user_id', supabaseUser.id)
          .maybeSingle()

        if (usersRecord?.onboarding_status) {
          onboardingStatus = usersRecord.onboarding_status
        }
      }

    // Fetch subscription status if missing
    if (!subscriptionStatus) {
      const { data: subscription } = await this.supabase
        .from('subscriptions')
        .select('status')
        .eq('user_id', supabaseUser.id)
        .eq('status', 'active')
        .maybeSingle()

      subscriptionStatus = subscription?.status || 'none'
    }

    return {
      id: supabaseUser.id,
      email: supabaseUser.email,
      role: supabaseUser.user_metadata?.role || 'user',
      is_active: true,
      is_banned: false,
      workspace_id: workspaceId,
      onboarding_status: onboardingStatus || 'pending',
      subscription_status: subscriptionStatus || 'none'
    }
  }

  /**
   * Rotate session if needed
   */
  async rotateSession(): Promise<{ success: boolean; session?: Session; error?: string }> {
    try {
      const { data: { session }, error } = await this.supabase.auth.refreshSession()

      if (error) {
        return { success: false, error: error.message }
      }

      return { success: true, session: session! }
    } catch (error) {
      console.error('Session rotation error:', error)
      return { success: false, error: 'Session rotation failed' }
    }
  }
}

// =============================================================================
// SERVICE ROLE CLIENT (for admin operations only)
// =============================================================================

export class ServiceRoleAuthService {
  private static instance: ServiceRoleAuthService
  private supabase: any

  private constructor() {
    // Only use service role key for trusted server-side operations
    if (!process.env.SUPABASE_SERVICE_ROLE_KEY) {
      throw new Error('SUPABASE_SERVICE_ROLE_KEY is required for service operations')
    }

    this.supabase = createServerClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_ROLE_KEY,
      {
        cookies: {
          getAll() { return [] },
          setAll() { /* No cookies for service role */ },
        },
      }
    )
  }

  static getInstance(): ServiceRoleAuthService {
    if (!ServiceRoleAuthService.instance) {
      ServiceRoleAuthService.instance = new ServiceRoleAuthService()
    }
    return ServiceRoleAuthService.instance
  }

  /**
   * Get the underlying Supabase client for admin operations
   */
  getSupabaseClient() {
    return this.supabase
  }

  /**
   * Admin-only operations
   */
  async updateUserRole(userId: string, role: string): Promise<{ success: boolean; error?: string }> {
    try {
      const { error } = await this.supabase
        .from('profiles')
        .update({ role })
        .eq('id', userId)

      if (error) {
        return { success: false, error: error.message }
      }

      return { success: true }
    } catch (error) {
      console.error('Error updating user role:', error)
      return { success: false, error: 'Failed to update user role' }
    }
  }

  /**
   * Get user by ID (admin operation)
   */
  async getUserById(userId: string): Promise<any> {
    try {
      const { data, error } = await this.supabase
        .from('profiles')
        .select('*')
        .eq('id', userId)
        .single()

      if (error) {
        console.error('Error getting user:', error)
        return null
      }

      return data
    } catch (error) {
      console.error('Error getting user by ID:', error)
      return null
    }
  }
}

// =============================================================================
// INSTANCES
// =============================================================================

export const clientAuth = new ClientAuthService()

// Server auth should be created per request
export function createServerAuth(request?: any): ServerAuthService {
  return new ServerAuthService(request)
}

// Service role auth - lazy initialization (server-only)
let _serviceAuth: ServiceRoleAuthService | null = null

export function getServiceAuth(): ServiceRoleAuthService {
  // Prevent client-side usage
  if (typeof window !== 'undefined') {
    throw new Error('ServiceRoleAuthService can only be used on the server')
  }

  if (!_serviceAuth) {
    _serviceAuth = ServiceRoleAuthService.getInstance()
  }
  return _serviceAuth
}

// Deprecated: use getServiceAuth() instead. Kept for backward compatibility.
// Will throw if accessed on client or if env vars are missing.
export const serviceAuth = {
  get instance() {
    return getServiceAuth()
  },
  getSupabaseClient() {
    return getServiceAuth().getSupabaseClient()
  },
  updateUserRole(userId: string, role: string) {
    return getServiceAuth().updateUserRole(userId, role)
  },
  getUserById(userId: string) {
    return getServiceAuth().getUserById(userId)
  }
}
