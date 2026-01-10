import { createClient } from '@supabase/supabase-js'
import { NextResponse } from 'next/server'

export async function GET(request: Request) {
  const { searchParams, origin } = new URL(request.url)
  const code = searchParams.get('code')
  const next = searchParams.get('next') ?? '/pricing'

  if (code) {
    const supabase = createClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
    )

    const { error } = await supabase.auth.exchangeCodeForSession(code)

    if (!error) {
      // Check if user has profile and subscription
      const { data: { session } } = await supabase.auth.getSession()

      if (session) {
        const { data: profile } = await supabase
          .from('user_profiles')
          .select('subscription_plan, subscription_status')
          .eq('id', session.user.id)
          .single()

        // Redirect based on subscription
        if (profile?.subscription_plan && profile.subscription_status === 'active') {
          return NextResponse.redirect(`${origin}/workspace`)
        }
      }

      return NextResponse.redirect(`${origin}${next}`)
    }
  }

  // Redirect to login on error
  return NextResponse.redirect(`${origin}/login?error=auth_failed`)
}
