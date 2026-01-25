import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'
import { NextResponse } from 'next/server'

export async function GET() {
  try {
    const cookieStore = await cookies()
    const supabase = createServerClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
      {
        cookies: {
          getAll() {
            return cookieStore.getAll()
          },
          setAll() {},
        },
      }
    )

    // Get session
    const { data: { session }, error } = await supabase.auth.getSession()

    // Get user if session exists
    let user = null
    if (session?.user) {
      const { data: profile } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', session.user.id)
        .maybeSingle()

      user = {
        ...session.user,
        profile
      }
    }

    return NextResponse.json({
      session,
      user,
      error: error?.message,
      isAuthenticated: !!session,
      cookies: cookieStore.getAll().map(c => ({ name: c.name, value: c.value }))
    })
  } catch (err) {
    return NextResponse.json({
      error: err.message,
      stack: err.stack,
      isAuthenticated: false
    })
  }
}
