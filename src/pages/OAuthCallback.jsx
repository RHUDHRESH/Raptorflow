import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { supabase } from '../lib/supabase'

const OAuthCallback = () => {
  const navigate = useNavigate()
  const [status, setStatus] = useState('Completing sign in...')
  const [error, setError] = useState(null)

  useEffect(() => {
    const handleCallback = async () => {
      try {
        // Check for errors in URL
        const params = new URLSearchParams(window.location.search)
        const hashParams = new URLSearchParams(window.location.hash.substring(1))
        const urlError = params.get('error') || hashParams.get('error')
        
        if (urlError) {
          const errorDesc = params.get('error_description') || hashParams.get('error_description') || urlError
          setError(errorDesc)
          setTimeout(() => {
            navigate('/login?error=' + encodeURIComponent(errorDesc), { replace: true })
          }, 2000)
          return
        }

        // Wait for Supabase to process the code exchange
        setStatus('Verifying session...')
        
        // Get the session - Supabase should have exchanged the code by now
        const { data: { session }, error: sessionError } = await supabase.auth.getSession()
        
        if (sessionError) {
          console.error('Session error:', sessionError)
          setError(sessionError.message)
          setTimeout(() => {
            navigate('/login?error=' + encodeURIComponent(sessionError.message), { replace: true })
          }, 2000)
          return
        }

        if (!session) {
          // No session yet, wait a bit and check again
          setStatus('Waiting for authentication...')
          await new Promise(resolve => setTimeout(resolve, 1000))
          
          const { data: { session: retrySession } } = await supabase.auth.getSession()
          
          if (!retrySession) {
            setError('Authentication failed - no session created')
            setTimeout(() => {
              navigate('/login?error=session_failed', { replace: true })
            }, 2000)
            return
          }
        }

        setStatus('Loading profile...')
        
        // Get session again to ensure we have latest
        const { data: { session: finalSession } } = await supabase.auth.getSession()
        
        if (finalSession?.user) {
          // Check if user has a profile with active plan
          const { data: profile } = await supabase
            .from('profiles')
            .select('plan, plan_status, onboarding_completed')
            .eq('id', finalSession.user.id)
            .single()

          setStatus('Redirecting...')
          
          // Determine where to redirect
          if (profile?.plan && profile.plan !== 'none' && profile.plan !== 'free' && profile.plan_status === 'active') {
            // User has active paid plan - go to app
            navigate('/app', { replace: true })
          } else if (profile?.onboarding_completed) {
            // Onboarding done but no plan - go to plan selection
            navigate('/onboarding/plan', { replace: true })
          } else {
            // New user or incomplete onboarding - go to onboarding start
            navigate('/onboarding/positioning', { replace: true })
          }
        } else {
          setError('No user found in session')
          setTimeout(() => {
            navigate('/login', { replace: true })
          }, 2000)
        }

      } catch (err) {
        console.error('OAuth callback error:', err)
        setError(err.message || 'Authentication failed')
        setTimeout(() => {
          navigate('/login?error=' + encodeURIComponent(err.message || 'auth_failed'), { replace: true })
        }, 2000)
      }
    }

    handleCallback()
  }, [navigate])

  return (
    <div className="min-h-screen bg-black flex items-center justify-center">
      <div className="flex flex-col items-center gap-4 text-center px-6">
        {error ? (
          <>
            <div className="w-12 h-12 rounded-full bg-red-500/20 flex items-center justify-center">
              <svg className="w-6 h-6 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <p className="text-red-400 text-sm">{error}</p>
            <p className="text-white/30 text-xs">Redirecting to login...</p>
          </>
        ) : (
          <>
            <div className="w-10 h-10 border-2 border-amber-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-white/60 text-sm">{status}</p>
          </>
        )}
      </div>
    </div>
  )
}

export default OAuthCallback
