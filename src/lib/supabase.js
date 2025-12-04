import { createClient } from '@supabase/supabase-js'

// Supabase configuration
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://vpwwzsanuyhpkvgorcnc.supabase.co'
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwd3d6c2FudXlocGt2Z29yY25jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIzOTk1OTEsImV4cCI6MjA3Nzk3NTU5MX0.-clyTrDDlCNpUGg-MEgXIki70uBt4oIFPuSA8swNuTU'

// Storage key for auth
const STORAGE_KEY = 'raptorflow-auth'

// Custom storage that uses localStorage with a custom key
const customStorage = {
  getItem: (key) => {
    try {
      const item = localStorage.getItem(`${STORAGE_KEY}-${key}`)
      return item
    } catch (error) {
      console.error('Storage getItem error:', error)
      return null
    }
  },
  setItem: (key, value) => {
    try {
      localStorage.setItem(`${STORAGE_KEY}-${key}`, value)
    } catch (error) {
      console.error('Storage setItem error:', error)
    }
  },
  removeItem: (key) => {
    try {
      localStorage.removeItem(`${STORAGE_KEY}-${key}`)
    } catch (error) {
      console.error('Storage removeItem error:', error)
    }
  }
}

// Debug logging in development
if (import.meta.env.DEV) {
  console.log('🔐 Supabase URL:', supabaseUrl)
  console.log('🔐 Auth storage key:', STORAGE_KEY)
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
      storage: customStorage,
      storageKey: 'session',
      // Keep session alive longer
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
  // Clear custom storage
  try {
    localStorage.removeItem(`${STORAGE_KEY}-session`)
  } catch (e) {
    console.error('Failed to clear storage:', e)
  }
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
    const session = localStorage.getItem(`${STORAGE_KEY}-session`)
    return !!session
  } catch {
    return false
  }
}

// Force refresh the session
export const refreshSession = async () => {
  const { data, error } = await supabase.auth.refreshSession()
  return { session: data.session, error }
}
