import React, { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { supabase } from '../lib/supabase'
import { useAuth } from '../contexts/AuthContext'

const OAuthCallback = () => {
  const navigate = useNavigate()
  const { refreshProfile } = useAuth()

  useEffect(() => {
    const handleCallback = async () => {
      try {
        // Get the hash from URL (OAuth callback)
        const hashParams = new URLSearchParams(window.location.hash.substring(1))
        const accessToken = hashParams.get('access_token')
        const refreshToken = hashParams.get('refresh_token')

        if (accessToken && refreshToken) {
          // Set the session
          const { data, error } = await supabase.auth.setSession({
            access_token: accessToken,
            refresh_token: refreshToken,
          })

          if (error) {
            console.error('Error setting session:', error)
            navigate('/login?error=' + encodeURIComponent(error.message))
            return
          }

          if (data.session) {
            console.log('Session set successfully, user:', data.user?.id)
            // Refresh profile to ensure it's created
            await refreshProfile()
            // Redirect to app
            navigate('/app', { replace: true })
          }
        } else {
          // No tokens in URL, check if we already have a session
          const { data: { session } } = await supabase.auth.getSession()
          if (session) {
            console.log('Session already exists, redirecting to app')
            await refreshProfile()
            navigate('/app', { replace: true })
          } else {
            console.log('No session found, redirecting to login')
            navigate('/login', { replace: true })
          }
        }
      } catch (error) {
        console.error('OAuth callback error:', error)
        navigate('/login?error=' + encodeURIComponent(error.message))
      }
    }

    handleCallback()
  }, [navigate, refreshProfile])

  return (
    <div className="min-h-screen bg-black flex items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <div className="w-10 h-10 border-2 border-amber-500 border-t-transparent rounded-full animate-spin" />
        <p className="text-white/40 text-sm">Completing sign in...</p>
      </div>
    </div>
  )
}

export default OAuthCallback

