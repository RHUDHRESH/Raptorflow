/**
 * Centralized Authentication Service
 * Handles all authentication operations with proper key separation
 */

import { createClient } from '@/lib/supabase/client'
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

import type { User as SupabaseUser, Session } from '@supabase/supabase-js'

// =============================================================================
// TYPES
// =============================================================================

export interface AuthUser {
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

export interface AuthResult {
  success: boolean
  user?: AuthUser
  session?: Session
  error?: string
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
      // Check if already on login page
      if (window.location.pathname === '/login') {
        return;
      }
      
      this.isSigningOut = true;
      
      // Clear local caches
      localStorage.removeItem('auth_cache');
      sessionStorage.removeItem('auth_cache');
      localStorage.removeItem('session_cache');
      localStorage.removeItem('raptorflow_session');
      localStorage.removeItem('raptorflow_user');
      
      // Redirect to login
      window.location.href = '/login';
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
   * Load user data from database with fallbacks
   */
  private async loadUserData(supabaseUser: SupabaseUser): Promise<AuthUser> {
    try {
      const { data: profileData } = await this.supabase
        .from('profiles')
        .select('*')
        .eq('id', supabaseUser.id)
        .maybeSingle()

      if (profileData) {
        return {
          id: supabaseUser.id,
          email: supabaseUser.email || '',
          fullName: profileData.full_name || supabaseUser.user_metadata?.full_name || supabaseUser.email?.split('@')[0] || 'User',
          subscriptionPlan: profileData.subscription_plan || supabaseUser.user_metadata?.subscription_plan || null,
          subscriptionStatus: profileData.subscription_status || supabaseUser.user_metadata?.subscription_status || 'none',
          hasCompletedOnboarding: profileData.onboarding_status === 'active',
          createdAt: supabaseUser.created_at,
          workspaceId: profileData.workspace_id,
          role: profileData.role || supabaseUser.user_metadata?.role,
          onboardingStatus: profileData.onboarding_status || 'pending',
        }
      }

      const { data: userProfilesData } = await this.supabase
        .from('user_profiles')
        .select('*')
        .eq('id', supabaseUser.id)
        .maybeSingle()

      if (userProfilesData) {
        return {
          id: supabaseUser.id,
          email: supabaseUser.email || '',
          fullName: userProfilesData.full_name || supabaseUser.user_metadata?.full_name || supabaseUser.email?.split('@')[0] || 'User',
          subscriptionPlan: userProfilesData.subscription_plan || supabaseUser.user_metadata?.subscription_plan || null,
          subscriptionStatus: userProfilesData.subscription_status || supabaseUser.user_metadata?.subscription_status || 'none',
          hasCompletedOnboarding: supabaseUser.user_metadata?.has_completed_onboarding === true,
          createdAt: supabaseUser.created_at,
          workspaceId: supabaseUser.user_metadata?.workspace_id,
          role: supabaseUser.user_metadata?.role,
          onboardingStatus: supabaseUser.user_metadata?.onboarding_status || 'pending',
        }
      }

      const { data: usersData } = await this.supabase
        .from('users')
        .select('id, auth_user_id, email, full_name, avatar_url, role, onboarding_status, subscription_plan, subscription_tier, subscription_status, workspace_id')
        .eq('auth_user_id', supabaseUser.id)
        .maybeSingle()

      if (usersData) {
        return {
          id: usersData.id || supabaseUser.id,
          email: usersData.email || supabaseUser.email || '',
          fullName: usersData.full_name || supabaseUser.user_metadata?.full_name || supabaseUser.email?.split('@')[0] || 'User',
          subscriptionPlan: usersData.subscription_plan || usersData.subscription_tier || supabaseUser.user_metadata?.subscription_plan || null,
          subscriptionStatus: usersData.subscription_status || supabaseUser.user_metadata?.subscription_status || 'none',
          hasCompletedOnboarding: usersData.onboarding_status === 'active',
          createdAt: supabaseUser.created_at,
          workspaceId: usersData.workspace_id || supabaseUser.user_metadata?.workspace_id,
          role: usersData.role || supabaseUser.user_metadata?.role,
          onboardingStatus: usersData.onboarding_status || 'pending',
        }
      }
    } catch (error) {
      console.error('Error loading user data:', error)
    }

    // Fallback to session metadata
    return {
      id: supabaseUser.id,
      email: supabaseUser.email || '',
      fullName: supabaseUser.user_metadata?.full_name || supabaseUser.email?.split('@')[0] || 'User',
      subscriptionPlan: supabaseUser.user_metadata?.subscription_plan || null,
      subscriptionStatus: supabaseUser.user_metadata?.subscription_status || 'none',
      hasCompletedOnboarding: supabaseUser.user_metadata?.has_completed_onboarding === true,
      createdAt: supabaseUser.created_at,
      workspaceId: supabaseUser.user_metadata?.workspace_id,
      role: supabaseUser.user_metadata?.role,
      onboardingStatus: supabaseUser.user_metadata?.onboarding_status || 'pending',
    }
  }

  /**
   * Sign in with OAuth provider (Google, GitHub, etc.)
   */
  async signInWithOAuth(provider: 'google' | 'github' | 'azure', options?: any): Promise<{ success: boolean; error?: string; url?: string }> {
    try {
      const { data, error } = await this.supabase.auth.signInWithOAuth({
        provider,
        options: {
          redirectTo: `${typeof window !== 'undefined' ? window.location.origin : 'http://localhost:3000'}/auth/callback`,
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

      return { success: true, url: data.url };
    } catch (error) {
      console.error('OAuth sign in error:', error);
      return { success: false, error: error instanceof Error ? error.message : 'OAuth sign in failed' };
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

    // Check profile for onboarding status if missing
    if (!onboardingStatus || onboardingStatus === 'pending') {
      const { data: profile } = await this.supabase
        .from('profiles')
        .select('onboarding_status')
        .eq('id', supabaseUser.id)
        .maybeSingle()

      if (profile?.onboarding_status) {
        onboardingStatus = profile.onboarding_status
      }

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
