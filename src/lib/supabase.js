import { createClient } from '@supabase/supabase-js'

// Supabase configuration
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://vpwwzsanuyhpkvgorcnc.supabase.co'
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || ''

if (!supabaseAnonKey) {
  throw new Error('VITE_SUPABASE_ANON_KEY is required')
}

export const supabase = createClient(
  supabaseUrl,
  supabaseAnonKey,
  {
    auth: {
      autoRefreshToken: true,
      persistSession: true,
      detectSessionInUrl: true,
      flowType: 'pkce',
      debug: import.meta.env.DEV,
    },
    global: {
      headers: {
        'x-client-info': 'raptorflow-web'
      }
    }
  }
)

// Helper functions for auth
export const signInWithGoogle = async () => {
  const { data, error } = await supabase.auth.signInWithOAuth({
    provider: 'google',
    options: {
      redirectTo: `${window.location.origin}/auth/callback`,
      queryParams: {
        access_type: 'offline',
        prompt: 'consent',
      },
    },
  })
  return { data, error }
}

export const signOut = async () => {
  const { error } = await supabase.auth.signOut()
  return { error }
}

export const getCurrentUser = async () => {
  const { data: { user }, error } = await supabase.auth.getUser()
  return { user, error }
}

export const getSession = async () => {
  const { data: { session }, error } = await supabase.auth.getSession()
  return { session, error }
}

// Check if we have a cached session
export const hasCachedSession = () => {
  try {
    const projectRef = new URL(supabaseUrl).hostname.split('.')[0]
    const key = `sb-${projectRef}-auth-token`
    const session = localStorage.getItem(key)
    return !!session
  } catch (e) {
    console.warn('Error checking cached session:', e)
    return false
  }
}

// Force refresh the session
export const refreshSession = async () => {
  const { data, error } = await supabase.auth.refreshSession()
  return { session: data.session, error }
}
