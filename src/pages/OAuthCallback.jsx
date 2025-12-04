import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { supabase } from '../lib/supabase'

const OAuthCallback = () => {
  const navigate = useNavigate()
  const [status, setStatus] = useState('Completing sign in...')

  useEffect(() => {
    // Simple approach: Just redirect to /app
    // The Supabase client with detectSessionInUrl: true will handle the code exchange
    // The AuthContext will detect the session via onAuthStateChange
    
    const timer = setTimeout(() => {
      // Give Supabase a moment to process, then redirect
      navigate('/app', { replace: true })
    }, 500)

    // Also listen for auth state changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
      console.log('OAuth callback - auth state changed:', event)
      if (event === 'SIGNED_IN' && session) {
        clearTimeout(timer)
        navigate('/app', { replace: true })
      }
    })

    // Check for errors in URL
    const params = new URLSearchParams(window.location.search)
    const hashParams = new URLSearchParams(window.location.hash.substring(1))
    const error = params.get('error') || hashParams.get('error')
    
    if (error) {
      const errorDesc = params.get('error_description') || hashParams.get('error_description') || error
      navigate('/login?error=' + encodeURIComponent(errorDesc), { replace: true })
      return
    }

    return () => {
      clearTimeout(timer)
      subscription.unsubscribe()
    }
  }, [navigate])

  return (
    <div className="min-h-screen bg-black flex items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <div className="w-10 h-10 border-2 border-amber-500 border-t-transparent rounded-full animate-spin" />
        <p className="text-white/40 text-sm">{status}</p>
      </div>
    </div>
  )
}

export default OAuthCallback
