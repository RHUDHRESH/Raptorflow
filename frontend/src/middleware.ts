import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { createServerClient } from '@supabase/auth-helpers-nextjs';

const PROTECTED_ROUTES = [
  '/dashboard',
  '/profile',
  '/settings',
  '/workspace',
  '/workspace-setup',
  '/moves',
  '/campaigns',
  '/analytics',
  '/blackbox',
  '/system-check'
];

const AUTH_ROUTES = [
  '/login',
  '/signup'
];

const PUBLIC_ROUTES = [
  '/onboarding',
  '/auth/callback',
  '/login',
  '/signup',
  '/forgot-password',
  '/reset-password',
  '/pricing',
  '/payment',
  '/pay'
];

export async function middleware(request: NextRequest): Promise<NextResponse> {
  const { pathname } = request.nextUrl;
  const response = NextResponse.next();

  if (PUBLIC_ROUTES.some(route => pathname.startsWith(route))) {
    return response;
  }

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll: () => request.cookies.getAll(),
        setAll: (cookiesToSet) => {
          cookiesToSet.forEach(({ name, value, options }) => {
            response.cookies.set(name, value, options);
          });
        }
      }
    }
  );
  const { data: { session } } = await supabase.auth.getSession();

  if (PROTECTED_ROUTES.some(route => pathname.startsWith(route)) && !session) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  if (AUTH_ROUTES.some(route => pathname.startsWith(route)) && session) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  return response;
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
