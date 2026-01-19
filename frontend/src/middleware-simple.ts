/**
 * 🔐 SIMPLE AUTHENTICATION MIDDLEWARE - Textbook Implementation
 * 
 * This is the most straightforward auth middleware possible.
 * No complexity, no magic, just pure textbook authentication.
 * 
 * 📚 TEXTBOOK EXAMPLE:
 * 1. Request comes in → Check if it's a protected route
 * 2. Protected route → Look for auth cookie
 * 3. No cookie → Redirect to login
 * 4. Cookie found → Verify JWT
 * 5. JWT valid → Continue to destination
 * 6. JWT invalid → Clear cookie, redirect to login
 */

import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { verifyToken, getAuthToken } from './lib/simple-auth';

// ============================================================================
// 🔐 MIDDLEWARE CONFIGURATION - Textbook Simple
// ============================================================================

// Routes that require authentication
const PROTECTED_ROUTES = [
  '/dashboard',
  '/profile',
  '/settings',
  '/api/protected',
  '/api/storage',
  '/api/user'
];

// Routes that should redirect to dashboard if already authenticated
const AUTH_ROUTES = [
  '/login',
  '/register'
];

// ============================================================================
// 🔐 MAIN MIDDLEWARE FUNCTION - Textbook Simple
// ============================================================================

/**
 * Authentication middleware - textbook implementation
 * 
 * @param request - Next.js request object
 * @returns Response or NextResponse.next()
 */
export async function middleware(request: NextRequest): Promise<NextResponse> {
  const { pathname } = request.nextUrl;

  // Log the request for debugging
  console.log(`🔐 [Auth] Request: ${pathname}`);

  // Check if route is protected
  const isProtectedRoute = PROTECTED_ROUTES.some(route => pathname.startsWith(route));

  // Check if route is auth route (login/register)
  const isAuthRoute = AUTH_ROUTES.some(route => pathname.startsWith(route));

  // Handle protected routes
  if (isProtectedRoute) {
    console.log(`🔐 [Auth] Protected route: ${pathname}`);

    // Get auth token from cookie
    const token = await getAuthToken();

    if (!token) {
      console.log('🔐 [Auth] No token found, redirecting to login');
      return redirectToLogin(request);
    }

    // Verify token
    const user = verifyToken(token);

    if (!user) {
      console.log('🔐 [Auth] Invalid token, redirecting to login');
      return redirectToLoginWithClearCookie(request);
    }

    console.log(`🔐 [Auth] User authenticated: ${user.email} (${user.userId})`);

    // User is authenticated, continue
    return NextResponse.next();
  }

  // Handle auth routes (redirect to dashboard if already authenticated)
  if (isAuthRoute) {
    const token = await getAuthToken();
    const user = token ? verifyToken(token) : null;

    if (user) {
      console.log(`🔐 [Auth] User already authenticated, redirecting to dashboard`);
      return NextResponse.redirect(new URL('/dashboard', request.url));
    }
  }

  // All other routes, continue
  return NextResponse.next();
}

// ============================================================================
// 🔐 HELPER FUNCTIONS - Textbook Simple
// ============================================================================

/**
 * Redirect to login - textbook implementation
 * 
 * @param request - Next.js request object
 * @returns Response redirecting to login
 */
function redirectToLogin(request: NextRequest): NextResponse {
  const loginUrl = new URL('/login', request.url);
  return NextResponse.redirect(loginUrl);
}

/**
 * Redirect to login with cookie cleared - textbook implementation
 * 
 * @param request - Next.js request object
 * @returns Response redirecting to login with cleared cookie
 */
function redirectToLoginWithClearCookie(request: NextRequest): NextResponse {
  const loginUrl = new URL('/login', request.url);
  const response = NextResponse.redirect(loginUrl);

  // Clear the invalid cookie
  response.cookies.delete('auth-token');

  return response;
}

// ============================================================================
// 🔐 MIDDLEWARE CONFIGURATION - Textbook Simple
// ============================================================================

/**
 * Middleware configuration - textbook implementation
 * 
 * This tells Next.js which routes to apply the middleware to
 */
export const config = {
  // Apply to all routes except:
  // - API routes (they handle auth themselves)
  // - Static files (_next/static)
  // - Images (_next/image)
  // - Favicon
  matcher: [
    /*
     * Match all paths except:
     * - /api/* (API routes)
     * - /_next/static/* (static files)
     * - /_next/image/* (optimized images)
     * - /favicon.ico
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)'
  ]
};
