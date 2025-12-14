import React, { useEffect, useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { supabase } from '../lib/supabase'

const OAuthCallback = () => {
  const navigate = useNavigate()
  const [status, setStatus] = useState('Completing sign in...')
  const [error, setError] = useState(null)
  const processedRef = useRef(false)

  useEffect(() => {
    // Prevent double processing in Strict Mode
    if (processedRef.current) return
    processedRef.current = true

    let subscription = null
    let timeoutId = null

    const handleSession = async (session) => {
      if (!session?.user) {
        setError('No user found in session')
        setTimeout(() => {
          navigate('/login', { replace: true })
        }, 2000)
        return
      }

      setStatus('Loading profile...')

      try {
        // First, try to get the profile
        let { data: profile, error: profileError } = await supabase
          .from('profiles')
          .select('plan, plan_status, onboarding_completed')
          .eq('id', session.user.id)
          .single()

        // If profile doesn't exist, create it
        if (profileError?.code === 'PGRST116' || !profile) {
          console.log('Profile not found, creating...')

          const { data: newProfile, error: createError } = await supabase
            .from('profiles')
            .insert({
              id: session.user.id,
              email: session.user.email,
              full_name: session.user.user_metadata?.full_name || session.user.user_metadata?.name || null,
              avatar_url: session.user.user_metadata?.avatar_url || session.user.user_metadata?.picture || null,
              onboarding_completed: false
            })
            .select('plan, plan_status, onboarding_completed')
            .single()

          if (createError) {
            console.error('Failed to create profile:', createError)
            // Still proceed, just go to onboarding
            profile = { onboarding_completed: false, plan: 'none', plan_status: 'inactive' }
          } else {
            profile = newProfile
          }
        } else if (profileError) {
          console.error('Profile fetch error:', profileError)
          // If other error, assume new user
          profile = { onboarding_completed: false, plan: 'none', plan_status: 'inactive' }
        }

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
      } catch (err) {
        console.error('Profile check error:', err)
        // Even if profile check fails, redirect to onboarding or app as fallback
        navigate('/onboarding/positioning', { replace: true })
      }
    }

    const init = async () => {
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

        setStatus('Verifying session...')

        // 1. Exchange the PKCE code for a session if present
        const authCode = params.get('code') || hashParams.get('code')
        if (authCode) {
          const { data, error: exchangeError } = await supabase.auth.exchangeCodeForSession({ code: authCode })

          if (exchangeError) {
            console.error('Code exchange failed:', exchangeError)
            setError(exchangeError.message || 'Authentication failed')
            setTimeout(() => {
              navigate('/login?error=' + encodeURIComponent(exchangeError.message || 'auth_failed'), { replace: true })
            }, 2000)
            return
          }

          if (data?.session) {
            await handleSession(data.session)
            return
          }
        }

        // 2. Check existing session
        const { data: { session }, error: sessionError } = await supabase.auth.getSession()

        if (session) {
          await handleSession(session)
          return
        }

        if (sessionError) {
          console.warn('Initial session check error:', sessionError)
          // Don't fail yet, try listening for changes
        }

        // 3. Listen for auth state changes (needed for PKCE flow completion)
        const { data: sub } = supabase.auth.onAuthStateChange(async (event, session) => {
          if (event === 'SIGNED_IN' && session) {
            if (timeoutId) clearTimeout(timeoutId)
            await handleSession(session)
          }
        })
        subscription = sub.subscription

        // 4. Set timeout fallback
        timeoutId = setTimeout(async () => {
          // One final check
          const { data: { session: finalSession } } = await supabase.auth.getSession()
          if (finalSession) {
            await handleSession(finalSession)
          } else {
            console.error('Auth timeout')
            setError('Authentication timed out. Please try again.')
            setTimeout(() => {
              navigate('/login?error=session_timeout', { replace: true })
            }, 2000)
          }
        }, 8000) // Wait up to 8 seconds

      } catch (err) {
        console.error('OAuth callback error:', err)
        setError(err.message || 'Authentication failed')
        setTimeout(() => {
          navigate('/login?error=' + encodeURIComponent(err.message || 'auth_failed'), { replace: true })
        }, 2000)
      }
    }

    init()

    return () => {
      if (subscription) subscription.unsubscribe()
      if (timeoutId) clearTimeout(timeoutId)
    }
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
