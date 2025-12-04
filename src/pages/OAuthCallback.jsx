import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { supabase } from '../lib/supabase'
import { useAuth } from '../contexts/AuthContext'

const OAuthCallback = () => {
  const navigate = useNavigate()
  const { refreshProfile } = useAuth()
  const [status, setStatus] = useState('Processing...')

  useEffect(() => {
    const handleCallback = async () => {
      try {
        console.log('OAuth callback - URL:', window.location.href)
        console.log('OAuth callback - Hash:', window.location.hash)
        console.log('OAuth callback - Search:', window.location.search)
        console.log('OAuth callback - Origin:', window.location.origin)

        setStatus('Checking authentication...')

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
          console.log('Found tokens in URL, setting session...')
          setStatus('Setting up session...')
          
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
            // Clear URL hash/query to prevent re-processing
            window.history.replaceState({}, '', '/auth/callback')
            
            setStatus('Setting up your profile...')
            
            // Wait a moment for profile to be created by trigger
            await new Promise(resolve => setTimeout(resolve, 1500))
            
            // Refresh profile to ensure it's created
            try {
              await refreshProfile()
            } catch (profileError) {
              console.warn('Profile refresh error (non-critical):', profileError)
            }
            
            // Verify session is still valid before redirecting
            const { data: { session: verifySession } } = await supabase.auth.getSession()
            if (verifySession) {
              console.log('Session verified, redirecting to app...')
              setStatus('Success! Redirecting...')
              navigate('/app', { replace: true })
            } else {
              console.error('Session lost after setting, redirecting to login')
              navigate('/login?error=Session expired', { replace: true })
            }
            return
          }
        }

        // No tokens in URL, let Supabase client try to detect session from URL automatically
        // This is important for PKCE flow where detectSessionInUrl handles the exchange
        console.log('No tokens found directly, letting Supabase detect session...')
        setStatus('Verifying session...')
        
        // Wait a moment for Supabase to process the URL
        await new Promise(resolve => setTimeout(resolve, 500))
        
        const { data: { session }, error: sessionError } = await supabase.auth.getSession()
        
        if (sessionError) {
          console.error('Error getting session:', sessionError)
          navigate('/login?error=' + encodeURIComponent(sessionError.message), { replace: true })
          return
        }

        if (session) {
          console.log('Session found via Supabase detection, user:', session.user?.id)
          // Clear URL to prevent re-processing
          window.history.replaceState({}, '', '/auth/callback')
          
          setStatus('Setting up your profile...')
          
          // Wait for profile creation
          await new Promise(resolve => setTimeout(resolve, 1000))
          
          try {
            await refreshProfile()
          } catch (profileError) {
            console.warn('Profile refresh error (non-critical):', profileError)
          }
          
          setStatus('Success! Redirecting...')
          navigate('/app', { replace: true })
        } else {
          console.log('No session found after all attempts, redirecting to login')
          navigate('/login?error=' + encodeURIComponent('Authentication failed. Please try again.'), { replace: true })
        }
      } catch (error) {
        console.error('OAuth callback error:', error)
        navigate('/login?error=' + encodeURIComponent(error.message || 'Authentication failed'), { replace: true })
      }
    }

    handleCallback()
  }, [navigate, refreshProfile])

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

