import { createClient } from '@/lib/auth-client'

// OAuth types
export interface OAuthClient {
  client_id: string
  name: string
  description?: string
  website_url?: string
  logo_url?: string
  redirect_uris: string[]
  grant_types: string[]
  allowed_scopes: string[]
  client_type: 'confidential' | 'public'
  is_active: boolean
  is_verified: boolean
}

export interface OAuthScope {
  scope: string
  display_name: string
  description?: string
  category: string
  is_default: boolean
  is_sensitive: boolean
  is_system: boolean
}

export interface AuthorizationRequest {
  client_id: string
  redirect_uri: string
  scope: string[]
  state?: string
  code_challenge?: string
  code_challenge_method?: 'plain' | 'S256'
  response_type: 'code'
}

export interface AuthorizationResponse {
  code: string
  state?: string
}

export interface TokenRequest {
  grant_type: 'authorization_code' | 'refresh_token' | 'client_credentials'
  code?: string
  redirect_uri?: string
  client_id: string
  client_secret?: string
  code_verifier?: string
  refresh_token?: string
  scope?: string[]
}

export interface TokenResponse {
  access_token: string
  token_type: string
  expires_in: number
  refresh_token?: string
  scope: string[]
}

export interface UserInfo {
  sub: string
  client_id: string
  scope: string[]
  user_id: string
  email?: string
  full_name?: string
  avatar_url?: string
}

// OAuth 2.0 client implementation
export class OAuth2Client {
  private clientId: string
  private clientSecret?: string
  private redirectUri: string
  private scopes: string[]

  constructor(config: {
    client_id: string
    client_secret?: string
    redirect_uri: string
    scopes?: string[]
  }) {
    this.clientId = config.client_id
    this.clientSecret = config.client_secret
    this.redirectUri = config.redirect_uri
    this.scopes = config.scopes || []
  }

  // Generate PKCE challenge
  static generatePKCEChallenge(): { code_challenge: string; code_verifier: string } {
    const code_verifier = OAuth2Client.generateRandomString(128)
    const code_challenge = OAuth2Client.base64URLEncode(
      OAuth2Client.sha256(code_verifier)
    )
    return { code_challenge, code_verifier }
  }

  // Generate authorization URL
  generateAuthorizationURL(options: {
    state?: string
    scope?: string[]
    code_challenge?: string
    code_challenge_method?: 'plain' | 'S256'
  } = {}): string {
    const params = new URLSearchParams({
      response_type: 'code',
      client_id: this.clientId,
      redirect_uri: this.redirectUri,
      scope: (options.scope || this.scopes).join(' '),
      state: options.state || OAuth2Client.generateRandomString(32)
    })

    if (options.code_challenge) {
      params.append('code_challenge', options.code_challenge)
      params.append('code_challenge_method', options.code_challenge_method || 'S256')
    }

    return `${process.env.NEXT_PUBLIC_SUPABASE_URL}/oauth/authorize?${params.toString()}`
  }

  // Exchange authorization code for tokens
  async exchangeCodeForTokens(
    code: string,
    codeVerifier?: string
  ): Promise<TokenResponse> {
    const supabase = createClient()
    if (!supabase) {
      throw new Error('Supabase client not available')
    }

    try {
      const { data, error } = await supabase.rpc('exchange_authorization_code', {
        p_code: code,
        p_client_id: this.clientId,
        p_client_secret: this.clientSecret,
        p_code_verifier: codeVerifier,
        p_redirect_uri: this.redirectUri
      })

      if (error) {
        throw new Error(`Token exchange failed: ${error.message}`)
      }

      return data?.[0] || {}
    } catch (error) {
      console.error('Token exchange error:', error)
      throw error
    }
  }

  // Refresh access token
  async refreshAccessToken(
    refreshToken: string,
    scopes?: string[]
  ): Promise<TokenResponse> {
    const supabase = createClient()
    if (!supabase) {
      throw new Error('Supabase client not available')
    }

    try {
      const { data, error } = await supabase.rpc('refresh_access_token', {
        p_refresh_token: refreshToken,
        p_client_id: this.clientId,
        p_client_secret: this.clientSecret,
        p_scope: scopes
      })

      if (error) {
        throw new Error(`Token refresh failed: ${error.message}`)
      }

      return data?.[0] || {}
    } catch (error) {
      console.error('Token refresh error:', error)
      throw error
    }
  }

  // Get user info from access token
  async getUserInfo(accessToken: string): Promise<UserInfo> {
    try {
      // Decode JWT token (simplified)
      const payload = JSON.parse(atob(accessToken.split('.')[1]))
      
      // Get user details from database
      const supabase = createClient()
      if (!supabase) {
        throw new Error('Supabase client not available')
      }

      const { data: user } = await supabase
        .from('users')
        .select('id, email, full_name, avatar_url')
        .eq('id', payload.sub)
        .single()

      return {
        sub: payload.sub,
        client_id: payload.client_id,
        scope: payload.scope || [],
        user_id: payload.sub,
        email: user?.email,
        full_name: user?.full_name,
        avatar_url: user?.avatar_url
      }
    } catch (error) {
      console.error('Get user info error:', error)
      throw error
    }
  }

  // Revoke token
  async revokeToken(token: string, tokenType: 'access_token' | 'refresh_token' = 'access_token'): Promise<void> {
    // TODO: Implement token revocation
    console.log(`Token revocation not yet implemented for ${tokenType}`)
  }

  // Utility methods
  private static generateRandomString(length: number): string {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    let result = ''
    for (let i = 0; i < length; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length))
    }
    return result
  }

  private static sha256(input: string): string {
    // Simplified SHA256 implementation
    // In production, use a proper crypto library
    let hash = 0
    for (let i = 0; i < input.length; i++) {
      const char = input.charCodeAt(i)
      hash = ((hash << 5) - hash) + char
      hash = hash & hash // Convert to 32-bit integer
    }
    return hash.toString()
  }

  private static base64URLEncode(input: string): string {
    // Convert to base64 and make URL-safe
    return btoa(input)
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=/g, '')
  }
}

// OAuth scope utilities
export class OAuthScopes {
  // Default scopes
  static readonly DEFAULT = ['read:profile', 'read:workspace']

  // Profile scopes
  static readonly PROFILE = {
    READ: 'read:profile',
    WRITE: 'write:profile',
    DELETE: 'delete:profile'
  }

  // Workspace scopes
  static readonly WORKSPACE = {
    READ: 'read:workspace',
    WRITE: 'write:workspace',
    DELETE: 'delete:workspace',
    MANAGE_MEMBERS: 'manage:members'
  }

  // ICP scopes
  static readonly ICP = {
    READ: 'read:icp',
    WRITE: 'write:icp',
    DELETE: 'delete:icp'
  }

  // Campaign scopes
  static readonly CAMPAIGNS = {
    READ: 'read:campaigns',
    WRITE: 'write:campaigns',
    DELETE: 'delete:campaigns'
  }

  // Analytics scopes
  static readonly ANALYTICS = {
    READ: 'read:analytics',
    EXPORT: 'export:analytics'
  }

  // Admin scopes
  static readonly ADMIN = {
    USERS: 'admin:users',
    WORKSPACES: 'admin:workspaces',
    SYSTEM: 'admin:system'
  }

  // Billing scopes
  static readonly BILLING = {
    READ: 'read:billing',
    WRITE: 'write:billing'
  }

  // System scopes
  static readonly SYSTEM = {
    OFFLINE: 'offline'
  }

  // Get all available scopes
  static getAllScopes(): string[] {
    return [
      ...Object.values(this.PROFILE),
      ...Object.values(this.WORKSPACE),
      ...Object.values(this.ICP),
      ...Object.values(this.CAMPAIGNS),
      ...Object.values(this.ANALYTICS),
      ...Object.values(this.ADMIN),
      ...Object.values(this.BILLING),
      ...Object.values(this.SYSTEM)
    ]
  }

  // Validate scopes
  static validateScopes(scopes: string[]): { valid: string[]; invalid: string[] } {
    const allScopes = this.getAllScopes()
    const valid = scopes.filter(scope => allScopes.includes(scope))
    const invalid = scopes.filter(scope => !allScopes.includes(scope))
    return { valid, invalid }
  }

  // Get scope description
  static getScopeDescription(scope: string): string {
    const descriptions: Record<string, string> = {
      [this.PROFILE.READ]: 'Read your basic profile information',
      [this.PROFILE.WRITE]: 'Update your profile information',
      [this.PROFILE.DELETE]: 'Delete your account and profile',
      [this.WORKSPACE.READ]: 'Read your workspace data',
      [this.WORKSPACE.WRITE]: 'Create and update workspace data',
      [this.WORKSPACE.DELETE]: 'Delete your workspace',
      [this.WORKSPACE.MANAGE_MEMBERS]: 'Invite and manage workspace members',
      [this.ICP.READ]: 'Read your ICP profile data',
      [this.ICP.WRITE]: 'Create and update ICP profiles',
      [this.ICP.DELETE]: 'Delete ICP profiles',
      [this.CAMPAIGNS.READ]: 'Read your campaign data',
      [this.CAMPAIGNS.WRITE]: 'Create and update campaigns',
      [this.CAMPAIGNS.DELETE]: 'Delete campaigns',
      [this.ANALYTICS.READ]: 'Access your analytics data',
      [this.ANALYTICS.EXPORT]: 'Export analytics data',
      [this.ADMIN.USERS]: 'Manage user accounts (admin only)',
      [this.ADMIN.WORKSPACES]: 'Manage all workspaces (admin only)',
      [this.ADMIN.SYSTEM]: 'System administration (admin only)',
      [this.BILLING.READ]: 'Read your billing information',
      [this.BILLING.WRITE]: 'Manage your billing',
      [this.SYSTEM.OFFLINE]: 'Maintain access when you are offline'
    }
    return descriptions[scope] || scope
  }

  // Get required scopes for operation
  static getRequiredScopes(operation: string): string[] {
    const requirements: Record<string, string[]> = {
      'read_profile': [this.PROFILE.READ],
      'update_profile': [this.PROFILE.WRITE],
      'delete_account': [this.PROFILE.DELETE],
      'read_workspace': [this.WORKSPACE.READ],
      'create_workspace': [this.WORKSPACE.WRITE],
      'update_workspace': [this.WORKSPACE.WRITE],
      'delete_workspace': [this.WORKSPACE.DELETE],
      'invite_members': [this.WORKSPACE.MANAGE_MEMBERS],
      'read_icp': [this.ICP.READ],
      'create_icp': [this.ICP.WRITE],
      'update_icp': [this.ICP.WRITE],
      'delete_icp': [this.ICP.DELETE],
      'read_campaigns': [this.CAMPAIGNS.READ],
      'create_campaigns': [this.CAMPAIGNS.WRITE],
      'update_campaigns': [this.CAMPAIGNS.WRITE],
      'delete_campaigns': [this.CAMPAIGNS.DELETE],
      'read_analytics': [this.ANALYTICS.READ],
      'export_analytics': [this.ANALYTICS.EXPORT],
      'admin_users': [this.ADMIN.USERS],
      'admin_workspaces': [this.ADMIN.WORKSPACES],
      'admin_system': [this.ADMIN.SYSTEM],
      'read_billing': [this.BILLING.READ],
      'manage_billing': [this.BILLING.WRITE]
    }
    return requirements[operation] || []
  }
}

// OAuth session management
export class OAuthSession {
  private static readonly SESSION_KEY = 'oauth_session'
  private static readonly TOKEN_KEY = 'oauth_tokens'

  static storeSession(session: {
    access_token: string
    refresh_token?: string
    expires_at: number
    scope: string[]
    user_info: UserInfo
  }): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem(this.SESSION_KEY, JSON.stringify(session))
      if (session.refresh_token) {
        localStorage.setItem(this.TOKEN_KEY, session.refresh_token)
      }
    }
  }

  static getSession(): {
    access_token: string
    refresh_token?: string
    expires_at: number
    scope: string[]
    user_info: UserInfo
  } | null {
    if (typeof window !== 'undefined') {
      const sessionData = localStorage.getItem(this.SESSION_KEY)
      const refreshToken = localStorage.getItem(this.TOKEN_KEY)
      
      if (sessionData) {
        const session = JSON.parse(sessionData)
        return {
          access_token: session.access_token,
          refresh_token: refreshToken || session.refresh_token,
          expires_at: session.expires_at,
          scope: session.scope,
          user_info: session.user_info
        }
      }
    }
    return null
  }

  static clearSession(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem(this.SESSION_KEY)
      localStorage.removeItem(this.TOKEN_KEY)
    }
  }

  static isSessionValid(): boolean {
    const session = this.getSession()
    if (!session) return false
    
    return Date.now() < session.expires_at
  }

  static async refreshSession(): Promise<boolean> {
    const session = this.getSession()
    if (!session || !session.refresh_token) return false

    try {
      const oauthClient = new OAuth2Client({
        client_id: session.user_info.client_id,
        redirect_uri: window.location.origin,
        scopes: session.scope
      })

      const tokenResponse = await oauthClient.refreshAccessToken(
        session.refresh_token
      )

      // Update session with new tokens
      const updatedSession = {
        access_token: tokenResponse.access_token,
        refresh_token: tokenResponse.refresh_token || session.refresh_token,
        expires_at: Date.now() + (tokenResponse.expires_in * 1000),
        scope: tokenResponse.scope,
        user_info: session.user_info
      }

      this.storeSession(updatedSession)
      return true
    } catch (error) {
      console.error('Session refresh failed:', error)
      this.clearSession()
      return false
    }
  }
}

// OAuth configuration
export const OAuthConfig = {
  // Default client configuration
  DEFAULT_CLIENT: {
    client_id: process.env.NEXT_PUBLIC_OAUTH_CLIENT_ID || 'raptorflow_web',
    client_secret: process.env.OAUTH_CLIENT_SECRET,
    redirect_uri: process.env.NEXT_PUBLIC_OAUTH_REDIRECT_URI || `${window.location.origin}/auth/callback`,
    scopes: OAuthScopes.DEFAULT
  },

  // Token lifetimes
  TOKEN_LIFETIMES: {
    ACCESS_TOKEN: 3600, // 1 hour
    REFRESH_TOKEN: 2592000, // 30 days
    AUTHORIZATION_CODE: 600 // 10 minutes
  },

  // PKCE settings
  PKCE: {
    CODE_CHALLENGE_LENGTH: 128,
    CODE_VERIFIER_LENGTH: 128
  },

  // Security settings
  SECURITY: {
    REQUIRE_PKCE: true,
    REQUIRE_CLIENT_SECRET: true,
    MAX_FAILED_ATTEMPTS: 5,
    LOCKOUT_DURATION: 900 // 15 minutes
  }
}

// OAuth error types
export class OAuthError extends Error {
  constructor(
    message: string,
    public code: string,
    public type: 'invalid_request' | 'invalid_client' | 'invalid_grant' | 'unauthorized_client' | 'unsupported_grant_type' | 'invalid_scope' | 'server_error'
  ) {
    super(message)
    this.name = 'OAuthError'
  }
}

export const OAuthErrors = {
  // Client errors
  INVALID_REQUEST: new OAuthError('The request is missing a required parameter', 'invalid_request', 'invalid_request'),
  INVALID_CLIENT: new OAuthError('Client authentication failed', 'invalid_client', 'invalid_client'),
  INVALID_GRANT: new OAuthError('The provided authorization grant is invalid', 'invalid_grant', 'invalid_grant'),
  UNAUTHORIZED_CLIENT: new OAuthError('The client is not authorized to request an authorization code', 'unauthorized_client', 'unauthorized_client'),
  UNSUPPORTED_GRANT_TYPE: new OAuthError('The authorization grant type is not supported', 'unsupported_grant_type', 'unsupported_grant_type'),
  INVALID_SCOPE: new OAuthError('The requested scope is invalid', 'invalid_scope', 'invalid_scope'),

  // Server errors
  SERVER_ERROR: new OAuthError('The authorization server encountered an unexpected condition', 'server_error', 'server_error')
}
