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
        console.log('OAuth callback - URL:', window.location.href)
        console.log('OAuth callback - Hash:', window.location.hash)
        console.log('OAuth callback - Search:', window.location.search)

        // Supabase OAuth can return tokens in hash (#) or query (?)
        // Check hash first (PKCE flow)
        const hashParams = new URLSearchParams(window.location.hash.substring(1))
        const queryParams = new URLSearchParams(window.location.search)
        
        const accessToken = hashParams.get('access_token') || queryParams.get('access_token')
        const refreshToken = hashParams.get('refresh_token') || queryParams.get('refresh_token')
        const errorParam = hashParams.get('error') || queryParams.get('error')
        const errorDescription = hashParams.get('error_description') || queryParams.get('error_description')

        // Check for errors first
        if (errorParam) {
          console.error('OAuth error:', errorParam, errorDescription)
          navigate('/login?error=' + encodeURIComponent(errorDescription || errorParam), { replace: true })
          return
        }

        if (accessToken && refreshToken) {
          console.log('Found tokens, setting session...')
          // Set the session
          const { data, error } = await supabase.auth.setSession({
            access_token: accessToken,
            refresh_token: refreshToken,
          })

          if (error) {
            console.error('Error setting session:', error)
            navigate('/login?error=' + encodeURIComponent(error.message), { replace: true })
            return
          }

          if (data.session) {
            console.log('Session set successfully, user:', data.user?.id)
            // Wait a moment for profile to be created
            await new Promise(resolve => setTimeout(resolve, 500))
            // Refresh profile to ensure it's created
            await refreshProfile()
            // Redirect to app
            navigate('/app', { replace: true })
            return
          }
        }

        // No tokens in URL, check if we already have a session
        console.log('No tokens found, checking existing session...')
        const { data: { session }, error: sessionError } = await supabase.auth.getSession()
        
        if (sessionError) {
          console.error('Error getting session:', sessionError)
          navigate('/login?error=' + encodeURIComponent(sessionError.message), { replace: true })
          return
        }

        if (session) {
          console.log('Session already exists, user:', session.user?.id)
          await refreshProfile()
          navigate('/app', { replace: true })
        } else {
          console.log('No session found, redirecting to login')
          navigate('/login', { replace: true })
        }
      } catch (error) {
        console.error('OAuth callback error:', error)
        navigate('/login?error=' + encodeURIComponent(error.message), { replace: true })
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

