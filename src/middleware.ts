import { createServerClient } from '@supabase/ssr'
import type { SetAllCookies } from '@supabase/ssr'
import { NextResponse, type NextRequest } from 'next/server'
import { isAccountProfileComplete } from '@/lib/auth/account'

const PUBLIC_PATHS = [
  '/login',
  '/signup',
  '/auth/callback',
  '/auth/verify',
  '/auth/reset-password',
  '/',
  '/landing',
]

function isPublicPath(pathname: string): boolean {
  return PUBLIC_PATHS.some(
    (path) => pathname === path || pathname.startsWith(path)
  )
}

export async function middleware(request: NextRequest) {
  let response = NextResponse.next({
    request: {
      headers: request.headers,
    },
  })

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll()
        },
        setAll(cookiesToSet: Parameters<SetAllCookies>[0]) {
          cookiesToSet.forEach(({ name, value, options }) => {
            request.cookies.set(name, value)
            response.cookies.set(name, value, options)
          })
        },
      },
    }
  )

  const {
    data: { user },
  } = await supabase.auth.getUser()

  const { pathname } = request.nextUrl
  const accountSetupPath = '/account/setup'
  const onboardingPath = '/onboarding'

  const isAuthPath = pathname.startsWith('/login') || pathname.startsWith('/signup')
  const isAccountSetupRoute = pathname === accountSetupPath || pathname.startsWith(`${accountSetupPath}/`)
  const isOnboardingRoute = pathname === onboardingPath || pathname.startsWith(`${onboardingPath}/`)

  if (!user && !isPublicPath(pathname)) {
    const url = new URL('/login', request.url)
    url.searchParams.set('redirect', pathname)
    return NextResponse.redirect(url)
  }

  if (!user) {
    return response
  }

  const accountProfileComplete = isAccountProfileComplete(user)

  if (!accountProfileComplete && !isAccountSetupRoute) {
    return NextResponse.redirect(new URL(accountSetupPath, request.url))
  }

  if (accountProfileComplete && (isAuthPath || isAccountSetupRoute)) {
    return NextResponse.redirect(new URL(onboardingPath, request.url))
  }

  if (!accountProfileComplete && (isAuthPath || isOnboardingRoute)) {
    return NextResponse.redirect(new URL(accountSetupPath, request.url))
  }

  return response
}

export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
}
