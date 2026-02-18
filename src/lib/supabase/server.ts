import { createServerClient as createServerClientBase } from '@supabase/ssr'
import { cookies } from 'next/headers'
import type { CookieOptions } from '@supabase/ssr'

export async function createServerClient() {
  const cookieStore = await cookies()

  function getAll() {
    return cookieStore.getAll()
  }

  function setAll(cookiesToSet: Array<{
    name: string
    value: string
    options: CookieOptions
  }>) {
    try {
      cookiesToSet.forEach(({ name, value, options }) => {
        cookieStore.set(name, value, options)
      })
    } catch {
      // Called from Server Component
    }
  }

  return createServerClientBase(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll,
        setAll,
      },
    }
  )
}
