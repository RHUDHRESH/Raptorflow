import { createClient } from '@supabase/supabase-js';
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export async function proxy(req: NextRequest) {
  const res = NextResponse.next();

  // Create Supabase client for middleware
  const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );

  // Get session from cookies
  const accessToken = req.cookies.get('sb-access-token')?.value;
  const refreshToken = req.cookies.get('sb-refresh-token')?.value;

  let session = null;

  if (accessToken && refreshToken) {
    const { data } = await supabase.auth.setSession({
      access_token: accessToken,
      refresh_token: refreshToken,
    });
    session = data.session;
  }

  // Protected routes
  const protectedRoutes = ['/workspace'];
  const authRoutes = ['/login'];
  const publicRoutes = ['/', '/pricing', '/payment/success', '/payment/failed'];

  const { pathname } = req.nextUrl;

  // Check if user is accessing a protected route
  if (protectedRoutes.some(route => pathname.startsWith(route))) {
    if (!session) {
      // No session, redirect to login
      const redirectUrl = new URL('/login', req.url);
      redirectUrl.searchParams.set('redirectedFrom', pathname);
      return NextResponse.redirect(redirectUrl);
    }

    // Check if user has active subscription
    if (session.user) {
      const { data: profile } = await supabase
        .from('user_profiles')
        .select('subscription_plan, subscription_status')
        .eq('id', session.user.id)
        .single();

      if (!profile?.subscription_plan || profile.subscription_status !== 'active') {
        // No active subscription, redirect to pricing
        return NextResponse.redirect(new URL('/pricing', req.url));
      }
    }
  }

  // If user is logged in and tries to access auth routes, redirect to workspace
  if (authRoutes.some(route => pathname.startsWith(route)) && session) {
    return NextResponse.redirect(new URL('/workspace', req.url));
  }

  return res;
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - api (API routes)
     */
    '/((?!_next/static|_next/image|favicon.ico|api).*)',
  ],
};
