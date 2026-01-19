// OAuth Provider Configuration for RaptorFlow Authentication
// This file handles configuration for various OAuth providers

export interface OAuthProvider {
  id: string;
  name: string;
  clientId: string;
  clientSecret?: string;
  redirectUri: string;
  scope: string;
  authorizationUrl: string;
  tokenUrl: string;
  userInfoUrl: string;
  enabled: boolean;
}

export interface OAuthConfig {
  providers: Record<string, OAuthProvider>;
  defaultProvider?: string;
}

// Get OAuth configuration based on environment
export function getOAuthConfig(): OAuthConfig {
  const baseUrl = process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000';
  
  const config: OAuthConfig = {
    providers: {
      google: {
        id: 'google',
        name: 'Google',
        clientId: process.env.GOOGLE_CLIENT_ID || '',
        clientSecret: process.env.GOOGLE_CLIENT_SECRET || '',
        redirectUri: `${baseUrl}/auth/callback/google`,
        scope: 'openid email profile',
        authorizationUrl: 'https://accounts.google.com/o/oauth2/v2/auth',
        tokenUrl: 'https://oauth2.googleapis.com/token',
        userInfoUrl: 'https://www.googleapis.com/oauth2/v2/userinfo',
        enabled: !!(process.env.GOOGLE_CLIENT_ID && process.env.GOOGLE_CLIENT_SECRET)
      },
      github: {
        id: 'github',
        name: 'GitHub',
        clientId: process.env.GITHUB_CLIENT_ID || '',
        clientSecret: process.env.GITHUB_CLIENT_SECRET || '',
        redirectUri: `${baseUrl}/auth/callback/github`,
        scope: 'user:email',
        authorizationUrl: 'https://github.com/login/oauth/authorize',
        tokenUrl: 'https://github.com/login/oauth/access_token',
        userInfoUrl: 'https://api.github.com/user',
        enabled: !!(process.env.GITHUB_CLIENT_ID && process.env.GITHUB_CLIENT_SECRET)
      },
      microsoft: {
        id: 'microsoft',
        name: 'Microsoft',
        clientId: process.env.MICROSOFT_CLIENT_ID || '',
        clientSecret: process.env.MICROSOFT_CLIENT_SECRET || '',
        redirectUri: `${baseUrl}/auth/callback/microsoft`,
        scope: 'openid email profile',
        authorizationUrl: 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
        tokenUrl: 'https://login.microsoftonline.com/common/oauth2/v2.0/token',
        userInfoUrl: 'https://graph.microsoft.com/v1.0/me',
        enabled: !!(process.env.MICROSOFT_CLIENT_ID && process.env.MICROSOFT_CLIENT_SECRET)
      },
      apple: {
        id: 'apple',
        name: 'Apple',
        clientId: process.env.APPLE_CLIENT_ID || '',
        clientSecret: process.env.APPLE_CLIENT_SECRET || '',
        redirectUri: `${baseUrl}/auth/callback/apple`,
        scope: 'name email',
        authorizationUrl: 'https://appleid.apple.com/auth/authorize',
        tokenUrl: 'https://appleid.apple.com/auth/token',
        userInfoUrl: '', // Apple doesn't have a separate user info endpoint
        enabled: !!(process.env.APPLE_CLIENT_ID && process.env.APPLE_CLIENT_SECRET)
      }
    },
    defaultProvider: process.env.DEFAULT_OAUTH_PROVIDER || 'google'
  };
  
  return config;
}

// Get enabled OAuth providers
export function getEnabledProviders(): OAuthProvider[] {
  const config = getOAuthConfig();
  return Object.values(config.providers).filter(provider => provider.enabled);
}

// Get OAuth provider by ID
export function getOAuthProvider(providerId: string): OAuthProvider | null {
  const config = getOAuthConfig();
  return config.providers[providerId] || null;
}

// Generate OAuth authorization URL
export function generateOAuthUrl(provider: OAuthProvider, state?: string): string {
  const params = new URLSearchParams({
    client_id: provider.clientId,
    redirect_uri: provider.redirectUri,
    scope: provider.scope,
    response_type: 'code',
    state: state || generateRandomState()
  });
  
  // Add provider-specific parameters
  switch (provider.id) {
    case 'google':
      params.append('access_type', 'offline');
      params.append('prompt', 'consent');
      break;
    case 'microsoft':
      params.append('response_mode', 'query');
      break;
    case 'apple':
      params.append('response_mode', 'form_post');
      break;
  }
  
  return `${provider.authorizationUrl}?${params.toString()}`;
}

// Exchange authorization code for access token
export async function exchangeCodeForToken(
  provider: OAuthProvider,
  code: string,
  state?: string
): Promise<OAuthTokenResponse> {
  const tokenUrl = provider.tokenUrl;
  const body = new URLSearchParams({
    grant_type: 'authorization_code',
    client_id: provider.clientId,
    client_secret: provider.clientSecret || '',
    code: code,
    redirect_uri: provider.redirectUri,
    state: state || ''
  });
  
  const response = await fetch(tokenUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'Accept': 'application/json'
    },
    body: body.toString()
  });
  
  if (!response.ok) {
    throw new Error(`Token exchange failed: ${response.statusText}`);
  }
  
  return response.json();
}

// Get user information from OAuth provider
export async function getOAuthUserInfo(
  provider: OAuthProvider,
  accessToken: string
): Promise<OAuthUserInfo> {
  if (!provider.userInfoUrl) {
    throw new Error('Provider does not support user info endpoint');
  }
  
  const response = await fetch(provider.userInfoUrl, {
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Accept': 'application/json'
    }
  });
  
  if (!response.ok) {
    throw new Error(`Failed to get user info: ${response.statusText}`);
  }
  
  return response.json();
}

// Generate random state for OAuth flow
function generateRandomState(): string {
  return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
}

// Validate OAuth state
export function validateState(receivedState: string, expectedState: string): boolean {
  return receivedState === expectedState;
}

// OAuth token response interface
export interface OAuthTokenResponse {
  access_token: string;
  token_type: string;
  expires_in?: number;
  refresh_token?: string;
  scope?: string;
  id_token?: string;
}

// OAuth user info interface
export interface OAuthUserInfo {
  id: string;
  email?: string;
  name?: string;
  picture?: string;
  verified_email?: boolean;
  locale?: string;
  hd?: string; // For Google Workspace domain
}

// Provider-specific user info interfaces
export interface GoogleUserInfo extends OAuthUserInfo {
  sub: string;
  email: string;
  name: string;
  picture: string;
  email_verified: boolean;
  locale: string;
  hd?: string;
}

export interface GitHubUserInfo extends OAuthUserInfo {
  id: number;
  login: string;
  name: string;
  email?: string;
  avatar_url: string;
}

export interface MicrosoftUserInfo extends OAuthUserInfo {
  id: string;
  displayName: string;
  userPrincipalName: string;
  mail?: string;
}

export interface AppleUserInfo extends OAuthUserInfo {
  sub: string;
  email?: string;
  name?: {
    firstName: string;
    lastName: string;
  };
}

// Environment variable validation
export function validateOAuthEnvironment(): { valid: boolean; errors: string[] } {
  const errors: string[] = [];
  const config = getOAuthConfig();
  
  // Check default provider
  if (config.defaultProvider && !config.providers[config.defaultProvider]) {
    errors.push(`Default OAuth provider '${config.defaultProvider}' is not configured`);
  }
  
  // Check each enabled provider
  Object.entries(config.providers).forEach(([id, provider]) => {
    if (provider.enabled) {
      if (!provider.clientId) {
        errors.push(`${provider.name} client ID is missing`);
      }
      if (!provider.clientSecret && id !== 'apple') { // Apple doesn't always need client secret
        errors.push(`${provider.name} client secret is missing`);
      }
    }
  });
  
  return {
    valid: errors.length === 0,
    errors
  };
}

// Get OAuth provider configuration for frontend
export function getFrontendOAuthConfig() {
  const config = getOAuthConfig();
  const frontendConfig: Record<string, { name: string; enabled: boolean }> = {};
  
  Object.entries(config.providers).forEach(([id, provider]) => {
    frontendConfig[id] = {
      name: provider.name,
      enabled: provider.enabled
    };
  });
  
  return {
    providers: frontendConfig,
    defaultProvider: config.defaultProvider
  };
}
