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

        const hashParams = new URLSearchParams(window.location.hash.substring(1))
        const queryParams = new URLSearchParams(window.location.search)
        
        // Check for errors first
        const errorParam = hashParams.get('error') || queryParams.get('error')
        const errorDescription = hashParams.get('error_description') || queryParams.get('error_description')

        if (errorParam) {
          console.error('OAuth error:', errorParam, errorDescription)
          navigate('/login?error=' + encodeURIComponent(errorDescription || errorParam), { replace: true })
          return
        }

        // PKCE flow returns a 'code' parameter that needs to be exchanged
        const code = queryParams.get('code')
        
        if (code) {
          console.log('Found PKCE code, exchanging for session...')
          setStatus('Exchanging authorization code...')
          
          // Exchange the code for a session with timeout
          const exchangePromise = supabase.auth.exchangeCodeForSession(code)
          const timeoutPromise = new Promise((_, reject) => 
            setTimeout(() => reject(new Error('Code exchange timed out. Please try again.')), 10000)
          )
          
          let data, error
          try {
            const result = await Promise.race([exchangePromise, timeoutPromise])
            data = result.data
            error = result.error
          } catch (timeoutError) {
            console.error('Exchange timeout:', timeoutError)
            // Try getting existing session instead
            const { data: sessionData } = await supabase.auth.getSession()
            if (sessionData?.session) {
              console.log('Found existing session after timeout')
              data = sessionData
            } else {
              navigate('/login?error=' + encodeURIComponent(timeoutError.message), { replace: true })
              return
            }
          }
          
          if (error) {
            console.error('Error exchanging code for session:', error)
            // Try getting existing session as fallback
            const { data: sessionData } = await supabase.auth.getSession()
            if (sessionData?.session) {
              console.log('Found existing session after error')
              data = sessionData
            } else {
              navigate('/login?error=' + encodeURIComponent(error.message), { replace: true })
              return
            }
          }

          if (data?.session) {
            console.log('Session created successfully, user:', data.session?.user?.id || data.user?.id)
            // Clear URL to prevent re-processing
            window.history.replaceState({}, '', '/auth/callback')
            
            setStatus('Setting up your profile...')
            
            // Wait a moment for profile to be created by trigger
            await new Promise(resolve => setTimeout(resolve, 500))
            
            // Refresh profile to ensure it's created
            try {
              await refreshProfile()
            } catch (profileError) {
              console.warn('Profile refresh error (non-critical):', profileError)
            }
            
            setStatus('Success! Redirecting...')
            navigate('/app', { replace: true })
            return
          }
        }

        // Check for tokens directly in hash (implicit flow fallback)
        const accessToken = hashParams.get('access_token')
        const refreshToken = hashParams.get('refresh_token')

        if (accessToken && refreshToken) {
          console.log('Found tokens in URL hash, setting session...')
          setStatus('Setting up session...')
          
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
            window.history.replaceState({}, '', '/auth/callback')
            
            setStatus('Setting up your profile...')
            await new Promise(resolve => setTimeout(resolve, 1500))
            
            try {
              await refreshProfile()
            } catch (profileError) {
              console.warn('Profile refresh error (non-critical):', profileError)
            }
            
            setStatus('Success! Redirecting...')
            navigate('/app', { replace: true })
            return
          }
        }

        // No code or tokens, check if session already exists
        console.log('No code/tokens found, checking existing session...')
        setStatus('Verifying session...')
        
        const { data: { session }, error: sessionError } = await supabase.auth.getSession()
        
        if (sessionError) {
          console.error('Error getting session:', sessionError)
          navigate('/login?error=' + encodeURIComponent(sessionError.message), { replace: true })
          return
        }

        if (session) {
          console.log('Existing session found, user:', session.user?.id)
          window.history.replaceState({}, '', '/auth/callback')
          
          setStatus('Setting up your profile...')
          await new Promise(resolve => setTimeout(resolve, 1000))
          
          try {
            await refreshProfile()
          } catch (profileError) {
            console.warn('Profile refresh error (non-critical):', profileError)
          }
          
          setStatus('Success! Redirecting...')
          navigate('/app', { replace: true })
        } else {
          console.log('No session found, redirecting to login')
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

