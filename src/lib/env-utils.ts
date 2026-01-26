/**
 * Environment Detection Utilities
 * Provides consistent environment detection across client and server
 */

/**
 * Check if running in Vercel preview environment
 */
export function isVercelPreview(): boolean {
  return !!(process.env.VERCEL_URL && process.env.VERCEL_ENV === 'preview');
}

/**
 * Check if running in development environment
 */
export function isDevelopment(): boolean {
  // Check environment variable first (server-side)
  if (process.env.NEXT_PUBLIC_APP_ENV === 'development') {
    return true;
  }

  // Check NODE_ENV (server-side)
  if (process.env.NODE_ENV === 'development') {
    return true;
  }

  // Client-side fallback
  if (typeof window !== 'undefined') {
    return window.location.hostname === 'localhost' ||
      window.location.hostname === '127.0.0.1' ||
      window.location.hostname === '0.0.0.0';
  }

  return false;
}

/**
 * Check if running in production environment
 */
export function isProduction(): boolean {
  return process.env.NEXT_PUBLIC_APP_ENV === 'production' ||
    process.env.NODE_ENV === 'production';
}

/**
 * Check if running in test environment
 */
export function isTest(): boolean {
  return process.env.NODE_ENV === 'test' ||
    process.env.NEXT_PUBLIC_APP_ENV === 'test';
}

/**
 * Get the appropriate base URL for the current environment
 */
export function getBaseUrl(): string {
  // Prefer explicit APP_URL if set (works for any custom domain/preview)
  if (process.env.NEXT_PUBLIC_APP_URL) {
    return process.env.NEXT_PUBLIC_APP_URL.replace(/\/$/, ''); // Remove trailing slash
  }

  // Vercel preview detection (explicit check)
  if (isVercelPreview()) {
    return `https://${process.env.VERCEL_URL}`;
  }

  // General Vercel detection (for production deployments)
  if (process.env.VERCEL_URL) {
    const protocol = process.env.VERCEL_ENV === 'production' ? 'https' : 'https';
    return `${protocol}://${process.env.VERCEL_URL}`;
  }

  // Environment-based fallbacks
  if (isDevelopment()) {
    return 'http://localhost:3000';
  }
  if (isProduction()) {
    return 'https://raptorflow.in';
  }

  // Default to localhost for unknown environments (support ports 3000-3005)
  return 'http://localhost:3000';
}

/**
 * Get the appropriate auth callback URL for the current environment
 */
export function getAuthCallbackUrl(): string {
  return `${getBaseUrl()}/auth/callback`;
}

/**
 * Get the appropriate API URL for the current environment
 */
export function getApiUrl(): string {
  if (isDevelopment()) {
    return 'http://localhost:8080';
  }
  if (isProduction()) {
    return 'https://api.raptorflow.in';
  }
  return 'http://localhost:8080';
}

/**
 * Get environment-specific configuration
 */
export function getEnvironmentConfig() {
  return {
    isDevelopment: isDevelopment(),
    isProduction: isProduction(),
    isTest: isTest(),
    baseUrl: getBaseUrl(),
    apiUrl: getApiUrl(),
    authCallbackUrl: getAuthCallbackUrl(),
  };
}
