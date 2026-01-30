import { NextResponse } from 'next/server'
import { createServerSupabaseClient } from '@/lib/auth-server'

export async function GET(request: Request) {
  try {
    const supabase = await createServerSupabaseClient()
    const authHeader = request.headers.get('authorization') || ''
    const token = authHeader.startsWith('Bearer ') ? authHeader.slice(7) : null

    const { data, error } = token
      ? await supabase.auth.getUser(token)
      : await supabase.auth.getUser()

    if (error || !data?.user) {
      return NextResponse.json({ error: 'Not authenticated' }, { status: 401 })
    }

    return NextResponse.json({
      user: {
        id: data.user.id,
        email: data.user.email,
      },
    })
  } catch (error) {
    console.error('Auth me error:', error)
    return NextResponse.json({ error: 'Failed to load user' }, { status: 500 })
  }
}
