import { NextResponse } from 'next/server'
import { cookies } from 'next/headers'
import { createServerClient } from '@supabase/auth-helpers-nextjs'

type CookieOptions = Parameters<ReturnType<typeof NextResponse.json>['cookies']['set']>[2]
type PendingCookie = { name: string; value: string; options?: CookieOptions }

export async function GET(request: Request) {
  const { searchParams, origin } = new URL(request.url)
  const code = searchParams.get('code')
  const error = searchParams.get('error')

  // Handle OAuth errors
  if (error) {
    console.error('OAuth error:', error)
    return NextResponse.redirect(`${origin}/login?error=${error}`)
  }

  if (code) {
    const cookieStore = await cookies()
    const pendingCookies: PendingCookie[] = []
    const supabase = createServerClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
      {
        cookies: {
          getAll: () => cookieStore.getAll(),
          setAll: (cookiesToSet) => {
            pendingCookies.push(...cookiesToSet)
          }
        }
      }
    )
    const applyCookies = (response: NextResponse) => {
      pendingCookies.forEach(({ name, value, options }) => {
        response.cookies.set(name, value, options)
      })
      return response
    }

    // Exchange code for session
    const { error: exchangeError } = await supabase.auth.exchangeCodeForSession(code)

    if (exchangeError) {
      console.error('Code exchange error:', exchangeError)
      return applyCookies(NextResponse.redirect(`${origin}/login?error=auth_failed`))
    }

    // Get current session
    const { data: { session } } = await supabase.auth.getSession()

    if (session?.user) {
      try {
        // Check if user profile exists
        const { data: profile, error: profileError } = await supabase
          .from('user_profiles')
          .select('*')
          .eq('id', session.user.id)
          .single()

        // Create profile if it doesn't exist
        if (profileError && profileError.code === 'PGRST116') {
          console.log('Creating new user profile for:', session.user.email)
          
          const { error: insertError } = await supabase
            .from('user_profiles')
            .insert({
              id: session.user.id,
              email: session.user.email!,
              full_name: session.user.user_metadata?.full_name || session.user.email!.split('@')[0],
              avatar_url: session.user.user_metadata?.avatar_url,
              subscription_plan: null,
              subscription_status: 'none',
              onboarding_completed: false,
              onboarding_step: 0,
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString()
            })

          if (insertError) {
            console.error('Failed to create user profile:', insertError)
            return applyCookies(NextResponse.redirect(`${origin}/login?error=profile_creation_failed`))
          }

          // New user - redirect to pricing
          return applyCookies(NextResponse.redirect(`${origin}/pricing`))
        }

        // Existing user - check subscription status
        if (profile) {
          console.log('Existing user found:', profile.email)
          console.log('Subscription status:', profile.subscription_status)

          // If user has active subscription and onboarding completed, go to workspace
          if (profile.subscription_status === 'active' && profile.onboarding_completed) {
            return applyCookies(NextResponse.redirect(`${origin}/workspace`))
          }

          // If user has active subscription but no onboarding, go to onboarding
          if (profile.subscription_status === 'active' && !profile.onboarding_completed) {
            return applyCookies(NextResponse.redirect(`${origin}/onboarding`))
          }

          // If user has no subscription, go to pricing
          if (profile.subscription_status === 'none' || !profile.subscription_plan) {
            return applyCookies(NextResponse.redirect(`${origin}/pricing`))
          }

          // Default - go to pricing for plan selection
          return applyCookies(NextResponse.redirect(`${origin}/pricing`))
        }

      } catch (error) {
        console.error('Error in auth callback:', error)
        return applyCookies(NextResponse.redirect(`${origin}/login?error=callback_error`))
      }
    }
  }

  // Fallback redirect
  return NextResponse.redirect(`${origin}/login?error=invalid_callback`)
}
