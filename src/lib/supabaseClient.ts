import { createBrowserClient } from '@supabase/ssr'

// Singleton instance for client-side only
let supabaseInstance: ReturnType<typeof createBrowserClient> | null = null

export function getSupabaseClient() {
  // Only create on client side
  if (typeof window === 'undefined') {
    throw new Error('getSupabaseClient() can only be called on the client side')
  }
  
  if (!supabaseInstance) {
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
    const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

    if (!supabaseUrl || !supabaseAnonKey) {
      throw new Error('Missing Supabase environment variables')
    }

    supabaseInstance = createBrowserClient(supabaseUrl, supabaseAnonKey, {
      auth: {
        persistSession: true,
        autoRefreshToken: true,
      },
    })
  }
  
  return supabaseInstance
}

// Legacy export for backward compatibility - use getSupabaseClient() in new code
export const supabase = typeof window !== 'undefined' ? getSupabaseClient() : null
