/**
 * 🔐 SIMPLE AUTHENTICATION MIDDLEWARE - Textbook Implementation
 * 
 * This is most straightforward auth middleware possible.
 * No magic, no complexity, just pure textbook authentication.
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
import { jwtVerify } from 'jose';

// ============================================================================
// 🔐 JWT CONFIGURATION - Textbook Simple
// ============================================================================

const JWT_SECRET = new TextEncoder().encode(
  process.env.JWT_SECRET || 'your-secret-key-change-in-production'
);

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
  '/api/user',
  '/api/subscription',
  '/workspace',
  '/moves',
  '/campaigns',
  '/analytics',
  '/blackbox'
];

// Routes that should redirect to dashboard if already authenticated
const AUTH_ROUTES = [
  '/login',
  '/register'
];

// Routes that require active subscription
const SUBSCRIPTION_REQUIRED_ROUTES = [
  '/workspace',
  '/dashboard',
  '/moves',
  '/campaigns',
  '/analytics',
  '/blackbox',
  '/profile',
  '/settings'
];

// Routes that require completed onboarding
const ONBOARDING_REQUIRED_ROUTES = [
  '/workspace',
  '/dashboard',
  '/moves',
  '/campaigns',
  '/analytics',
  '/blackbox'
];

// Routes that require plan selection (no subscription)
const PLAN_SELECTION_ROUTES = [
  '/pricing',
  '/payment'
];

// Public routes that don't require authentication
const PUBLIC_ROUTES = [
  '/onboarding',
  '/api/v1/onboarding',
  '/auth',
  '/api/auth',
  '/login',
  '/register',
  '/pricing',
  '/payment',
  '/api/payments'
];

// ============================================================================
// 🔐 JWT VERIFICATION - Textbook Simple (Edge Runtime Compatible)
// ============================================================================

/**
 * Verify JWT token - textbook implementation
 * 
 * @param token - JWT token to verify
 * @returns User data or null if invalid
 */
async function verifyToken(token: string): Promise<any> {
  try {
    const { payload } = await jwtVerify(token, JWT_SECRET);
    return payload;
  } catch (error) {
    console.error('🔐 [Auth] Token verification failed:', (error as Error).message);
    return null;
  }
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

  // Clear invalid cookie
  response.cookies.delete('auth-token');

  return response;
}

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

  // Log request for debugging
  console.log(`🔐 [Auth] Request: ${pathname}`);

  // Check if route is public - allow access without authentication
  const isPublicRoute = PUBLIC_ROUTES.some(route => pathname.startsWith(route));
  if (isPublicRoute) {
    console.log(`🔐 [Auth] Public route: ${pathname}`);
    return NextResponse.next();
  }

  // Check if route is protected
  const isProtectedRoute = PROTECTED_ROUTES.some(route => pathname.startsWith(route));

  // Check if route is auth route (login/register)
  const isAuthRoute = AUTH_ROUTES.some(route => pathname.startsWith(route));

  // Check if route requires subscription
  const requiresSubscription = SUBSCRIPTION_REQUIRED_ROUTES.some(route => pathname.startsWith(route));

  // Check if route requires onboarding
  const requiresOnboarding = ONBOARDING_REQUIRED_ROUTES.some(route => pathname.startsWith(route));

  // Check if route is for plan selection
  const isPlanSelectionRoute = PLAN_SELECTION_ROUTES.some(route => pathname.startsWith(route));

  // Handle protected routes
  if (isProtectedRoute) {
    console.log(`🔐 [Auth] Protected route: ${pathname}`);

    // Get auth token from cookie
    const token = request.cookies.get('auth-token')?.value;

    if (!token) {
      console.log('🔐 [Auth] No token found, redirecting to login');
      return redirectToLogin(request);
    }

    // Verify token
    const user = await verifyToken(token);

    if (!user) {
      console.log('🔐 [Auth] Invalid token, redirecting to login');
      return redirectToLoginWithClearCookie(request);
    }

    console.log(`🔐 [Auth] User authenticated: ${user.email} (${user.userId})`);

    // Check subscription status for routes that require it
    if (requiresSubscription || requiresOnboarding) {
      try {
        // Call subscription status endpoint
        const subscriptionResponse = await fetch(`${process.env.NEXT_PUBLIC_APP_URL}/api/subscription/status`, {
          headers: {
            'Cookie': request.headers.get('cookie') || '',
          },
        });

        if (subscriptionResponse.ok) {
          const subscriptionData = await subscriptionResponse.json();
          const subscription = subscriptionData.subscription;

          console.log(`🔐 [Auth] Subscription status:`, subscription);

          // Check if user has active subscription for subscription-required routes
          if (requiresSubscription) {
            if (!subscription?.hasSubscription || subscription?.subscription_status !== 'active') {
              console.log('🔐 [Auth] No active subscription, redirecting to pricing');
              return NextResponse.redirect(new URL('/pricing', request.url));
            }
          }

          // Check onboarding status for routes that require it
          if (requiresOnboarding && !subscription?.onboardingCompleted) {
            console.log('🔐 [Auth] Onboarding incomplete, redirecting to onboarding');
            return NextResponse.redirect(new URL('/onboarding', request.url));
          }
        } else {
          console.log('🔐 [Auth] Could not verify subscription status');
          // If we can't verify subscription status, allow access but log warning
        }
      } catch (error) {
        console.error('🔐 [Auth] Error checking subscription status:', error);
        // Continue with access but log the error
      }
    }

    // User is authenticated, continue
    return NextResponse.next();
  }

  // Handle auth routes (redirect to dashboard if already authenticated)
  if (isAuthRoute) {
    const token = request.cookies.get('auth-token')?.value;
    const user = token ? await verifyToken(token) : null;

    if (user) {
      console.log(`🔐 [Auth] User already authenticated, redirecting to dashboard`);
      return NextResponse.redirect(new URL('/dashboard', request.url));
    }
  }

  // All other routes, continue
  return NextResponse.next();
}

// ============================================================================
// 🔐 MIDDLEWARE CONFIGURATION - Textbook Simple
// ============================================================================

/**
 * Middleware configuration - textbook implementation
 * 
 * This tells Next.js which routes to apply middleware to
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
