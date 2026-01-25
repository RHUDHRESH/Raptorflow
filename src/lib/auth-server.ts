import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'
import type { Session, User as SupabaseUser } from '@supabase/supabase-js'
import { getBaseUrl } from './env-utils'

// =============================================================================
// TYPES
// =============================================================================

export interface ServerAuthUser {
  id: string
  email: string
  role: string
  is_active: boolean
  is_banned: boolean
  workspace_id?: string
  onboarding_status: string
  subscription_status: string
}

export interface SessionValidationResult {
  valid: boolean
  user?: ServerAuthUser
  needsRotation?: boolean
  error?: string
}

// =============================================================================
// SERVER-SIDE AUTH SERVICE CLASS
// =============================================================================

export class ServerAuthService {
  private supabase: any

  constructor(request?: any) {
    // Create server client with proper cookie handling
    this.supabase = createServerClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
      {
        cookies: {
          getAll() {
            if (request) {
              return request.cookies.getAll()
            }
            return cookies().getAll()
          },
          setAll(cookiesToSet) {
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
   */
  async validateSession(): Promise<SessionValidationResult> {
    try {
      // Use getUser() for secure server-side validation
      const { data: { user: authUser }, error: userError } = await this.supabase.auth.getUser()

      if (userError || !authUser) {
        return { valid: false, error: userError?.message || 'No authenticated user' }
      }

      // Get session for expiry info
      const { data: { session } } = await this.supabase.auth.getSession()

      // Check if session needs rotation
      let needsRotation = false
      if (session?.expires_at) {
        const expiresAtMs = typeof session.expires_at === 'number' 
          ? session.expires_at * 1000 
          : new Date(session.expires_at).getTime()
        const timeUntilExpiry = expiresAtMs - Date.now()
        
        if (timeUntilExpiry < 5 * 60 * 1000) {
          needsRotation = true
        }
      } else {
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
   * Load user data with workspace lookup
   */
  private async loadUserDataWithWorkspace(supabaseUser: SupabaseUser): Promise<Partial<ServerAuthUser>> {
    let workspaceId = supabaseUser.user_metadata?.workspace_id
    let onboardingStatus = supabaseUser.user_metadata?.onboarding_status
    let subscriptionStatus = supabaseUser.user_metadata?.subscription_status

    // Try to get workspace_id from database if missing
    if (!workspaceId) {
      const { data: workspace } = await this.supabase
        .from('workspaces')
        .select('id')
        .eq('owner_id', supabaseUser.id)
        .limit(1)
        .maybeSingle()

      if (workspace) {
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
// FACTORY FUNCTION
// =============================================================================

export function createServerAuth(request?: any): ServerAuthService {
  return new ServerAuthService(request)
}

// =============================================================================
// SERVER-SIDE FUNCTIONS
// =============================================================================

/**
 * Get Supabase client for server-side usage
 */
export async function createServerSupabaseClient() {
  const cookieStore = await cookies()
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || process.env.SUPABASE_URL
  const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || process.env.SUPABASE_ANON_KEY

  if (!supabaseUrl || !supabaseAnonKey) {
    console.error('❌ Supabase configuration missing:', {
      hasUrl: !!supabaseUrl,
      hasAnonKey: !!supabaseAnonKey,
      urlPrefix: supabaseUrl?.substring(0, 30),
      keyLength: supabaseAnonKey?.length
    })
    throw new Error('Supabase configuration missing')
  }
  
  return createServerClient(
    supabaseUrl,
    supabaseAnonKey,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll().map((cookie: any) => ({
            name: cookie.name,
            value: cookie.value
          }))
        },
        setAll(cookiesToSet) {
          try {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, options)
            )
          } catch {
            // The `setAll` method was called from a Server Component.
            // This can be ignored if you have middleware refreshing
            // user sessions.
          }
        },
      },
    }
  )
}

/**
 * Get Supabase client with service role for trusted server operations only
 */
export async function createServiceSupabaseClient() {
  const cookieStore = await cookies()
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || process.env.SUPABASE_URL
  const serviceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY

  if (!supabaseUrl || !serviceRoleKey) {
    throw new Error('Supabase service configuration missing')
  }
  
  return createServerClient(
    supabaseUrl,
    serviceRoleKey,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll().map((cookie: any) => ({
            name: cookie.name,
            value: cookie.value
          }))
        },
        setAll(cookiesToSet) {
          try {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, options)
            )
          } catch {
            // The `setAll` method was called from a Server Component.
            // This can be ignored if you have middleware refreshing
            // user sessions.
          }
        },
      },
    }
  )
}

/**
 * Get server session
 * Note: For secure authentication, prefer getServerUser() which validates the token
 */
export async function getServerSession(): Promise<Session | null> {
  const supabase = await createServerSupabaseClient()
  const { data } = await supabase.auth.getSession()
  return data?.session || null
}

/**
 * Get server user (SECURE - validates token with Supabase Auth server)
 * This should be preferred over getServerSession() for authentication checks
 */
export async function getServerUser(): Promise<SupabaseUser | null> {
  const supabase = await createServerSupabaseClient()
  const { data, error } = await supabase.auth.getUser()
  if (error) {
    console.warn('getServerUser error:', error.message)
    return null
  }
  return data?.user || null
}

export type ProfileSource = 'profiles' | 'user_profiles' | 'users' | null

export interface NormalizedProfile {
  id: string
  auth_user_id?: string | null
  email?: string | null
  full_name?: string | null
  avatar_url?: string | null
  role?: string | null
  workspace_id?: string | null
  onboarding_status?: string | null
  subscription_plan?: string | null
  subscription_status?: string | null
  is_active?: boolean | null
  is_banned?: boolean | null
  phone?: string | null
  created_at?: string | null
  updated_at?: string | null
}

const omitUndefined = (payload: Record<string, any>) =>
  Object.fromEntries(Object.entries(payload).filter(([, value]) => value !== undefined))

const mapProfilesRecord = (record: any, authUserId: string): NormalizedProfile => ({
  id: record.id,
  auth_user_id: authUserId,
  email: record.email ?? null,
  full_name: record.full_name ?? null,
  avatar_url: record.avatar_url ?? null,
  role: record.role ?? null,
  workspace_id: record.workspace_id ?? null,
  onboarding_status: record.onboarding_status ?? null,
  subscription_plan: record.subscription_plan ?? null,
  subscription_status: record.subscription_status ?? null,
  is_active: record.is_active ?? true,
  is_banned: record.is_banned ?? false,
  phone: record.phone ?? null,
  created_at: record.created_at ?? null,
  updated_at: record.updated_at ?? null,
})

const mapUserProfilesRecord = (record: any, authUserId: string): NormalizedProfile => ({
  id: record.id,
  auth_user_id: authUserId,
  email: record.email ?? null,
  full_name: record.full_name ?? null,
  avatar_url: record.avatar_url ?? null,
  subscription_plan: record.subscription_plan ?? null,
  subscription_status: record.subscription_status ?? null,
  is_active: true,
  is_banned: false,
  created_at: record.created_at ?? null,
  updated_at: record.updated_at ?? null,
})

const mapUsersRecord = (record: any, authUserId: string): NormalizedProfile => ({
  id: record.id,
  auth_user_id: record.auth_user_id ?? authUserId,
  email: record.email ?? null,
  full_name: record.full_name ?? null,
  avatar_url: record.avatar_url ?? null,
  role: record.role ?? null,
  onboarding_status: record.onboarding_status ?? null,
  subscription_plan: record.subscription_plan ?? record.subscription_tier ?? null,
  subscription_status: record.subscription_status ?? null,
  is_active: record.is_active ?? true,
  is_banned: record.is_banned ?? false,
  phone: record.phone ?? null,
  created_at: record.created_at ?? null,
  updated_at: record.updated_at ?? null,
})

export async function getProfileByAuthUserId(
  supabase: any,
  authUserId: string
): Promise<{ profile: NormalizedProfile | null; source: ProfileSource }> {
  const { data: profilesData } = await supabase
    .from('profiles')
    .select('id, email, full_name, avatar_url, role, workspace_id, onboarding_status, subscription_plan, subscription_status, is_active, is_banned, phone, created_at, updated_at')
    .eq('id', authUserId)
    .maybeSingle()

  if (profilesData) {
    return { profile: mapProfilesRecord(profilesData, authUserId), source: 'profiles' }
  }

  const { data: userProfilesData } = await supabase
    .from('user_profiles')
    .select('id, email, full_name, avatar_url, subscription_plan, subscription_status, created_at, updated_at')
    .eq('id', authUserId)
    .maybeSingle()

  if (userProfilesData) {
    return { profile: mapUserProfilesRecord(userProfilesData, authUserId), source: 'user_profiles' }
  }

  const { data: usersByAuthId } = await supabase
    .from('users')
    .select('id, auth_user_id, email, full_name, avatar_url, phone, role, onboarding_status, subscription_plan, subscription_tier, subscription_status, is_active, is_banned, created_at, updated_at')
    .eq('auth_user_id', authUserId)
    .maybeSingle()

  if (usersByAuthId) {
    return { profile: mapUsersRecord(usersByAuthId, authUserId), source: 'users' }
  }

  const { data: usersById } = await supabase
    .from('users')
    .select('id, auth_user_id, email, full_name, avatar_url, phone, role, onboarding_status, subscription_plan, subscription_tier, subscription_status, is_active, is_banned, created_at, updated_at')
    .eq('id', authUserId)
    .maybeSingle()

  if (usersById) {
    return { profile: mapUsersRecord(usersById, authUserId), source: 'users' }
  }

  return { profile: null, source: null }
}

export async function getProfileByAnyId(
  supabase: any,
  identifier: string
): Promise<{ profile: NormalizedProfile | null; source: ProfileSource }> {
  const { data: profilesData } = await supabase
    .from('profiles')
    .select('id, email, full_name, avatar_url, role, workspace_id, onboarding_status, subscription_plan, subscription_status, is_active, is_banned, phone, created_at, updated_at')
    .eq('id', identifier)
    .maybeSingle()

  if (profilesData) {
    return { profile: mapProfilesRecord(profilesData, identifier), source: 'profiles' }
  }

  const { data: userProfilesData } = await supabase
    .from('user_profiles')
    .select('id, email, full_name, avatar_url, subscription_plan, subscription_status, created_at, updated_at')
    .eq('id', identifier)
    .maybeSingle()

  if (userProfilesData) {
    return { profile: mapUserProfilesRecord(userProfilesData, identifier), source: 'user_profiles' }
  }

  const { data: usersById } = await supabase
    .from('users')
    .select('id, auth_user_id, email, full_name, avatar_url, phone, role, onboarding_status, subscription_plan, subscription_tier, subscription_status, is_active, is_banned, created_at, updated_at')
    .eq('id', identifier)
    .maybeSingle()

  if (usersById) {
    return { profile: mapUsersRecord(usersById, usersById.auth_user_id || identifier), source: 'users' }
  }

  const { data: usersByAuthId } = await supabase
    .from('users')
    .select('id, auth_user_id, email, full_name, avatar_url, phone, role, onboarding_status, subscription_plan, subscription_tier, subscription_status, is_active, is_banned, created_at, updated_at')
    .eq('auth_user_id', identifier)
    .maybeSingle()

  if (usersByAuthId) {
    return { profile: mapUsersRecord(usersByAuthId, identifier), source: 'users' }
  }

  return { profile: null, source: null }
}

export async function upsertProfileForAuthUser(supabase: any, authUser: SupabaseUser) {
  const baseProfile = {
    id: authUser.id,
    email: authUser.email,
    full_name: authUser.user_metadata?.full_name || authUser.user_metadata?.name || authUser.email?.split('@')[0],
    avatar_url: authUser.user_metadata?.avatar_url || authUser.user_metadata?.picture,
    onboarding_status: 'pending',
    subscription_plan: null,
    subscription_status: 'none',
    is_active: true,
    is_banned: false,
    role: 'user',
  }

  console.log('📝 Attempting to upsert profile for user:', authUser.id)

  // Try profiles table first
  const { data: profilesData, error: profilesError } = await supabase
    .from('profiles')
    .upsert(omitUndefined(baseProfile), { onConflict: 'id' })
    .select('id, email, full_name, avatar_url, role, workspace_id, onboarding_status, subscription_plan, subscription_status, is_active, is_banned, phone, created_at, updated_at')
    .maybeSingle()

  if (profilesError) {
    console.error('❌ Profiles upsert error:', profilesError.message, profilesError.code, profilesError.details)
  }

  if (profilesData && !profilesError) {
    console.log('✅ Profile created in profiles table:', profilesData.id)
    return { profile: mapProfilesRecord(profilesData, authUser.id), source: 'profiles' as ProfileSource }
  }

  // Fallback: try user_profiles table
  const userProfilesPayload = omitUndefined({
    id: baseProfile.id,
    email: baseProfile.email,
    full_name: baseProfile.full_name,
    avatar_url: baseProfile.avatar_url,
    subscription_plan: baseProfile.subscription_plan,
    subscription_status: baseProfile.subscription_status,
  })

  const { data: userProfilesData, error: userProfilesError } = await supabase
    .from('user_profiles')
    .upsert(userProfilesPayload, { onConflict: 'id' })
    .select('id, email, full_name, avatar_url, subscription_plan, subscription_status, created_at, updated_at')
    .maybeSingle()

  if (userProfilesError) {
    console.error('❌ User_profiles upsert error:', userProfilesError.message, userProfilesError.code, userProfilesError.details)
  }

  if (userProfilesData && !userProfilesError) {
    console.log('✅ Profile created in user_profiles table:', userProfilesData.id)
    return { profile: mapUserProfilesRecord(userProfilesData, authUser.id), source: 'user_profiles' as ProfileSource }
  }

  // Last fallback: try users table
  const usersPayload = omitUndefined({
    id: authUser.id,
    auth_user_id: authUser.id,
    email: baseProfile.email,
    full_name: baseProfile.full_name,
    avatar_url: baseProfile.avatar_url,
    role: 'user',
    onboarding_status: 'pending',
    subscription_status: 'none',
    is_active: true,
    is_banned: false,
  })

  const { data: usersData, error: usersError } = await supabase
    .from('users')
    .upsert(usersPayload, { onConflict: 'auth_user_id' })
    .select('id, auth_user_id, email, full_name, avatar_url, phone, role, onboarding_status, subscription_plan, subscription_tier, subscription_status, is_active, is_banned, created_at, updated_at')
    .maybeSingle()

  if (usersError) {
    console.error('❌ Users upsert error:', usersError.message, usersError.code, usersError.details)
  }

  if (usersData && !usersError) {
    console.log('✅ Profile created in users table:', usersData.id)
    return { profile: mapUsersRecord(usersData, authUser.id), source: 'users' as ProfileSource }
  }

  console.error('❌ Failed to create profile in any table')
  return { profile: null, source: null }
}

export async function updateProfileRecord(
  supabase: any,
  identifiers: { authUserId?: string; profileId?: string },
  updates: {
    email?: string | null
    full_name?: string | null
    avatar_url?: string | null
    role?: string | null
    workspace_id?: string | null
    onboarding_status?: string | null
    subscription_plan?: string | null
    subscription_status?: string | null
    is_active?: boolean | null
    is_banned?: boolean | null
    phone?: string | null
    updated_at?: string | null
  }
) {
  const profileId = identifiers.profileId || identifiers.authUserId
  const profilesUpdate = omitUndefined({
    email: updates.email,
    full_name: updates.full_name,
    avatar_url: updates.avatar_url,
    role: updates.role,
    workspace_id: updates.workspace_id,
    onboarding_status: updates.onboarding_status,
    subscription_plan: updates.subscription_plan,
    subscription_status: updates.subscription_status,
    is_active: updates.is_active,
    is_banned: updates.is_banned,
    phone: updates.phone,
    updated_at: updates.updated_at,
  })

  if (profileId) {
    const { error: profilesError } = await supabase
      .from('profiles')
      .update(profilesUpdate)
      .eq('id', profileId)

    if (!profilesError) {
      return { success: true, source: 'profiles' as ProfileSource }
    }

    const userProfilesUpdate = omitUndefined({
      email: updates.email,
      full_name: updates.full_name,
      avatar_url: updates.avatar_url,
      subscription_plan: updates.subscription_plan,
      subscription_status: updates.subscription_status,
      updated_at: updates.updated_at,
    })

    const { error: userProfilesError } = await supabase
      .from('user_profiles')
      .update(userProfilesUpdate)
      .eq('id', profileId)

    if (!userProfilesError) {
      return { success: true, source: 'user_profiles' as ProfileSource }
    }
  }

  const usersUpdate = omitUndefined({
    email: updates.email,
    full_name: updates.full_name,
    avatar_url: updates.avatar_url,
    role: updates.role,
    onboarding_status: updates.onboarding_status,
    subscription_plan: updates.subscription_plan,
    subscription_tier: updates.subscription_plan,
    subscription_status: updates.subscription_status,
    is_active: updates.is_active,
    is_banned: updates.is_banned,
    phone: updates.phone,
    updated_at: updates.updated_at,
  })

  if (identifiers.authUserId) {
    const { error: usersByAuthError } = await supabase
      .from('users')
      .update(usersUpdate)
      .eq('auth_user_id', identifiers.authUserId)

    if (!usersByAuthError) {
      return { success: true, source: 'users' as ProfileSource }
    }
  }

  if (profileId) {
    const { error: usersByIdError } = await supabase
      .from('users')
      .update(usersUpdate)
      .eq('id', profileId)

    if (!usersByIdError) {
      return { success: true, source: 'users' as ProfileSource }
    }
  }

  return { success: false, source: null }
}

/**
 * Get current user from database (server-side)
 */
export async function getCurrentUserFromDB() {
  const session = await getServerSession()
  
  if (!session) {
    return null
  }
  
  const supabase = await createServerSupabaseClient()
  const { profile } = await getProfileByAuthUserId(supabase, session.user.id)
  return profile
}

/**
 * Require authentication - redirects to login if not authenticated
 */
export async function requireAuth(): Promise<Session> {
  const session = await getServerSession()
  
  if (!session) {
    redirect('/login')
  }
  
  return session
}

/**
 * Require onboarding completion - redirects based on status
 */
export async function requireOnboarding(step?: string) {
  const session = await requireAuth()
  const supabase = await createServerSupabaseClient()
  
  const { profile: user } = await getProfileByAuthUserId(supabase, session.user.id)
  
  if (!user) {
    redirect('/login')
  }
  
  // If user is fully onboarded, redirect to dashboard
  if (user.onboarding_status === 'active') {
    redirect('/dashboard')
  }
  
  // If specific step is required and user is not at that step
  if (step && user.onboarding_status !== step) {
    const redirectPath = getRedirectPath(user.onboarding_status || 'pending')
    redirect(redirectPath)
  }
  
  return { session, user }
}

/**
 * Require active user - checks for banned/inactive status
 */
export async function requireActiveUser() {
  const session = await requireAuth()
  const supabase = await createServerSupabaseClient()
  
  const { profile: user } = await getProfileByAuthUserId(supabase, session.user.id)
  
  if (!user) {
    redirect('/login')
  }
  
  if (user.is_banned) {
    redirect('/account/banned')
  }
  
  if (user.is_active === false) {
    redirect('/account/inactive')
  }
  
  if (user.onboarding_status !== 'active') {
    const redirectPath = getRedirectPath(user.onboarding_status || 'pending')
    redirect(redirectPath)
  }
  
  return { session, user }
}

/**
 * Require admin role
 */
export async function requireAdmin() {
  const session = await requireAuth()
  const supabase = await createServerSupabaseClient()
  
  const { profile: user } = await getProfileByAuthUserId(supabase, session.user.id)
  
  if (!user || !['admin', 'super_admin', 'support', 'billing_admin'].includes(user.role || '')) {
    redirect('/unauthorized')
  }
  
  return { session, user }
}

/**
 * Check if user has specific permission
 */
export async function hasPermission(permission: string): Promise<boolean> {
  const supabase = await createServerSupabaseClient()
  const session = await getServerSession()
  
  if (!session) {
    return false
  }
  
  const { data: user } = await supabase
    .from('users')
    .select('role')
    .eq('auth_user_id', session.user.id)
    .single()
  
  if (!user) {
    return false
  }
  
  // Super admin has all permissions
  if (user.role === 'super_admin') {
    return true
  }
  
  // Define role permissions
  const rolePermissions: Record<string, string[]> = {
    admin: ['read:users', 'write:users', 'read:subscriptions', 'write:subscriptions', 'read:payments', 'read:audit_logs'],
    billing_admin: ['read:users', 'read:subscriptions', 'write:subscriptions', 'read:payments', 'refund:payments'],
    support: ['read:users', 'read:subscriptions'],
    user: [],
  }
  
  const permissions = rolePermissions[user.role] || []
  
  return permissions.includes(permission) || permissions.includes('*')
}

// =============================================================================
// HELPER FUNCTIONS
// =============================================================================

/**
 * Get redirect path based on onboarding status
 */
export function getRedirectPath(status: string): string {
  switch (status) {
    case 'pending_workspace':
      return '/onboarding'
    case 'pending_storage':
      return '/onboarding/storage'
    case 'pending_plan_selection':
      return '/onboarding/plans'
    case 'pending_payment':
      return '/onboarding/payment'
    case 'active':
      return '/dashboard'
    case 'suspended':
      return '/account/suspended'
    case 'cancelled':
      return '/account/reactivate'
    default:
      return '/onboarding'
  }
}
