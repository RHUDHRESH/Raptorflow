/**
 * 🔐 SIMPLE AUTHENTICATION - Textbook Implementation (Fixed)
 * 
 * This is most straightforward JWT auth system possible.
 * No magic, no complexity, just pure textbook authentication.
 * 
 * 📚 TEXTBOOK EXAMPLE:
 * 1. User logs in → Server validates credentials
 * 2. Server creates JWT → JWT contains user info + expiration
 * 3. JWT stored in HttpOnly cookie → Client can't access it
 * 4. Every request → Middleware checks JWT
 * 5. JWT valid → User is authenticated
 * 6. JWT invalid/expired → Redirect to login
 */

import jwt from 'jsonwebtoken';
import { cookies } from 'next/headers';
import { NextResponse } from 'next/server';

// ============================================================================
// 🔐 JWT CONFIGURATION - Simple & Clear
// ============================================================================

interface JWTPayload {
  userId: string;
  email: string;
  iat: number;  // Issued at
  exp: number;  // Expires at
}

interface AuthConfig {
  secret: string;
  expiresIn: string;
  cookieName: string;
}

// Get configuration from environment
const getConfig = (): AuthConfig => ({
  secret: process.env.JWT_SECRET || 'your-secret-key-change-in-production',
  expiresIn: process.env.JWT_EXPIRES_IN || '7d', // 7 days
  cookieName: 'auth-token'
});

// ============================================================================
// 🔐 JWT CREATION - Textbook Simple
// ============================================================================

/**
 * Create JWT token - textbook implementation
 * 
 * @param user - User object with id and email
 * @returns JWT token
 */
export function createToken(user: { userId: string; email: string }): string {
  const config = getConfig();
  
  // Create payload with user info and timestamps
  const payload: JWTPayload = {
    userId: user.userId,
    email: user.email,
    iat: Math.floor(Date.now() / 1000),  // Current time in seconds
    exp: Math.floor(Date.now() / 1000) + (7 * 24 * 60 * 60)  // 7 days from now
  };
  
  // Sign token with secret
  return jwt.sign(payload, config.secret);
}

// ============================================================================
// 🔍 JWT VERIFICATION - Textbook Simple
// ============================================================================

/**
 * Verify JWT token - textbook implementation
 * 
 * @param token - JWT token to verify
 * @returns User data or null if invalid
 */
export function verifyToken(token: string): JWTPayload | null {
  try {
    const config = getConfig();
    
    // Verify token and return payload
    const decoded = jwt.verify(token, config.secret) as JWTPayload;
    return decoded;
  } catch (error) {
    // Token is invalid or expired
    console.error('🔐 [Auth] Token verification failed:', (error as Error).message);
    return null;
  }
}

// ============================================================================
// 🍪 COOKIE HELPERS - Textbook Simple
// ============================================================================

/**
 * Set auth cookie - textbook implementation
 * 
 * @param token - JWT token
 * @returns Response object with cookie set
 */
export function setAuthCookie(token: string): Response {
  const config = getConfig();
  
  // Create response
  const response = new NextResponse(JSON.stringify({ success: true }), {
    status: 200,
    headers: { 'Content-Type': 'application/json' }
  });
  
  // Set HttpOnly cookie (security best practice)
  response.cookies.set(config.cookieName, token, {
    httpOnly: true,        // Client-side JavaScript can't access
    secure: process.env.NODE_ENV === 'production',  // HTTPS only in production
    sameSite: 'lax',      // CSRF protection
    maxAge: 7 * 24 * 60 * 60 * 1000,  // 7 days
    path: '/'             // Available everywhere
  });
  
  return response;
}

/**
 * Clear auth cookie - textbook implementation
 * 
 * @returns Response object with cookie cleared
 */
export function clearAuthCookie(): Response {
  const config = getConfig();
  
  // Create response
  const response = new NextResponse(JSON.stringify({ success: true }), {
    status: 200,
    headers: { 'Content-Type': 'application/json' }
  });
  
  // Clear cookie
  response.cookies.set(config.cookieName, '', {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    maxAge: 0,  // Immediately expires
    path: '/'
  });
  
  return response;
}

/**
 * Get auth token from cookie - textbook implementation
 * 
 * @returns JWT token or null
 */
export async function getAuthToken(): Promise<string | null> {
  try {
    const cookieStore = await cookies();
    const config = getConfig();
    
    // Get token from cookie
    const token = cookieStore.get(config.cookieName)?.value;
    return token ?? null;
  } catch (error) {
    console.error('🔐 [Auth] Error reading cookie:', (error as Error).message);
    return null;
  }
}

// ============================================================================
// 🔐 AUTHENTICATION HELPERS - Textbook Simple
// ============================================================================

/**
 * Get current user - textbook implementation
 * 
 * @returns User data or null if not authenticated
 */
export async function getCurrentUser(): Promise<JWTPayload | null> {
  const token = await getAuthToken();
  
  if (!token) {
    return null;
  }
  
  return verifyToken(token);
}

/**
 * Check if user is authenticated - textbook implementation
 * 
 * @returns True if authenticated, false otherwise
 */
export async function isAuthenticated(): Promise<boolean> {
  return (await getCurrentUser()) !== null;
}

/**
 * Get user ID - textbook implementation
 * 
 * @returns User ID or null
 */
export async function getUserId(): Promise<string | null> {
  const user = await getCurrentUser();
  return user?.userId || null;
}

/**
 * Get user email - textbook implementation
 * 
 * @returns User email or null
 */
export async function getUserEmail(): Promise<string | null> {
  const user = await getCurrentUser();
  return user?.email || null;
}

// ============================================================================
// 🔐 AUTHENTICATION MIDDLEWARE - Textbook Simple
// ============================================================================

/**
 * Authentication middleware - textbook implementation
 * 
 * This middleware checks if user is authenticated
 * If not, it returns a 401 response
 * If yes, it allows the request to continue
 * 
 * @param handler - Next.js API route handler
 * @returns Protected handler
 */
export function withAuth<T extends (...args: any[]) => Promise<any>>(
  handler: T
): T {
  return (async (...args: any[]) => {
    // Check if user is authenticated
    const user = await getCurrentUser();
    
    if (!user) {
      // User is not authenticated
      return new Response(
        JSON.stringify({ 
          error: 'Unauthorized',
          message: 'Please log in to access this resource'
        }),
        { 
          status: 401,
          headers: { 'Content-Type': 'application/json' }
        }
      );
    }
    
    // User is authenticated, proceed with handler
    return await handler(...args);
  }) as T;
}

// ============================================================================
// 🔐 AUTHENTICATION API ROUTES - Textbook Simple
// ============================================================================

/**
 * Login API route - textbook implementation
 * 
 * @param request - Request object
 * @returns Response with auth cookie set
 */
export async function loginRoute(request: Request): Promise<Response> {
  try {
    const { email, password } = await request.json();
    
    // TODO: Validate credentials against database
    // For now, we'll use a simple mock validation
    if (!email || !password) {
      return new Response(
        JSON.stringify({ error: 'Email and password are required' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      );
    }
    
    // Mock user validation (replace with real database check)
    const mockUser = {
      userId: 'user-123',
      email: email.toLowerCase()
    };
    
    // Create JWT token
    const token = createToken(mockUser);
    
    // Set auth cookie
    return setAuthCookie(token);
    
  } catch (error) {
    console.error('🔐 [Auth] Login error:', error);
    return new Response(
      JSON.stringify({ error: 'Internal server error' }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
}

/**
 * Logout API route - textbook implementation
 * 
 * @returns Response with auth cookie cleared
 */
export async function logoutRoute(): Promise<Response> {
  try {
    // Clear auth cookie
    return clearAuthCookie();
    
  } catch (error) {
    console.error('🔐 [Auth] Logout error:', error);
    return new Response(
      JSON.stringify({ error: 'Internal server error' }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
}

/**
 * Get current user API route - textbook implementation
 * 
 * @returns Response with user data
 */
export async function getCurrentUserRoute(): Promise<Response> {
  try {
    const user = await getCurrentUser();
    
    if (!user) {
      return new Response(
        JSON.stringify({ error: 'Not authenticated' }),
        { status: 401, headers: { 'Content-Type': 'application/json' } }
      );
    }
    
    return new Response(
      JSON.stringify({ 
        user: {
          userId: user.userId,
          email: user.email
        }
      }),
      { status: 200, headers: { 'Content-Type': 'application/json' } }
    );
    
  } catch (error) {
    console.error('🔐 [Auth] Get user error:', error);
    return new Response(
      JSON.stringify({ error: 'Internal server error' }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
}

// ============================================================================
// 🔐 CLIENT-SIDE AUTH HELPERS - Textbook Simple
// ============================================================================

/**
 * Client-side auth check - textbook implementation
 * 
 * @returns True if authenticated, false otherwise
 */
export function clientIsAuthenticated(): boolean {
  // This would be called from client components
  // For now, we'll use a simple check
  if (typeof window !== 'undefined') {
    return document.cookie.includes('auth-token=');
  }
  return false;
}

/**
 * Client-side redirect to login - textbook implementation
 */
export function clientRedirectToLogin(): void {
  if (typeof window !== 'undefined') {
    window.location.href = '/login';
  }
}

// ============================================================================
// 🔐 TYPESCRIPT TYPES - Textbook Simple
// ============================================================================

export type { JWTPayload };
export type AuthUser = {
  userId: string;
  email: string;
};
