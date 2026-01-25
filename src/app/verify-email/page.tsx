"use client"

import { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Loader2, Mail, CheckCircle, AlertCircle } from 'lucide-react'

export default function VerifyEmailPage() {
  const [loading, setLoading] = useState(true)
  const [verifying, setVerifying] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [status, setStatus] = useState<'loading' | 'success' | 'error' | 'expired'>('loading')
  const router = useRouter()
  const searchParams = useSearchParams()
  const supabase = createClientComponentClient()

  useEffect(() => {
    const verifyEmail = async () => {
      const token = searchParams.get('token')
      const type = searchParams.get('type')

      if (!token || type !== 'signup') {
        setStatus('error')
        setError('Invalid verification link')
        setLoading(false)
        return
      }

      try {
        const email = searchParams.get('email')
        
        if (!email) {
          setStatus('error')
          setError('Email address is required for verification')
          setLoading(false)
          return
        }

        const { error } = await supabase.auth.verifyOtp({
          token,
          type: 'signup',
          email,
        })

        if (error) {
          if (error.message.includes('expired')) {
            setStatus('expired')
            setError('Verification link has expired')
          } else {
            setStatus('error')
            setError(error.message)
          }
        } else {
          setStatus('success')
          setMessage('Email verified successfully! Redirecting to login...')
          
          // Update user's email verification status
          const { data } = await supabase.auth.getSession()
          const session = data?.session
          if (session?.user) {
            await supabase
              .from('users')
              .update({ email_verified: true })
              .eq('auth_user_id', session.user.id)
          }

          // Redirect to login after 2 seconds
          setTimeout(() => {
            router.push('/login?message=email_verified')
          }, 2000)
        }
      } catch (err: any) {
        setStatus('error')
        setError(err.message || 'Failed to verify email')
      } finally {
        setLoading(false)
      }
    }

    verifyEmail()
  }, [searchParams, supabase, router])

  const handleResendVerification = async () => {
    setVerifying(true)
    setError('')
    setMessage('')

    try {
      const email = searchParams.get('email')
      if (!email) {
        setError('Email address not found')
        return
      }

      const { error } = await supabase.auth.resend({
        type: 'signup',
        email,
        options: {
          emailRedirectTo: `${window.location.origin}/auth/callback`,
        },
      })

      if (error) {
        setError(error.message)
      } else {
        setMessage('Verification email sent! Please check your inbox.')
      }
    } catch (err: any) {
      setError(err.message || 'Failed to resend verification email')
    } finally {
      setVerifying(false)
    }
  }

  const getStatusIcon = () => {
    switch (status) {
      case 'loading':
        return <Loader2 className="h-16 w-16 animate-spin text-blue-600" />
      case 'success':
        return <CheckCircle className="h-16 w-16 text-green-600" />
      case 'error':
      case 'expired':
        return <AlertCircle className="h-16 w-16 text-red-600" />
      default:
        return <Mail className="h-16 w-16 text-gray-400" />
    }
  }

  const getStatusTitle = () => {
    switch (status) {
      case 'loading':
        return 'Verifying your email...'
      case 'success':
        return 'Email Verified!'
      case 'error':
        return 'Verification Failed'
      case 'expired':
        return 'Link Expired'
      default:
        return 'Email Verification'
    }
  }

  const getStatusDescription = () => {
    switch (status) {
      case 'loading':
        return 'Please wait while we verify your email address.'
      case 'success':
        return 'Your email has been successfully verified.'
      case 'error':
        return 'We couldn\'t verify your email address.'
      case 'expired':
        return 'The verification link has expired.'
      default:
        return 'Check your email for a verification link.'
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full">
        <Card>
          <CardHeader className="text-center">
            <div className="flex justify-center mb-4">
              {getStatusIcon()}
            </div>
            <CardTitle className="text-2xl">
              {getStatusTitle()}
            </CardTitle>
            <CardDescription>
              {getStatusDescription()}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {message && (
              <Alert>
                <AlertDescription>{message}</AlertDescription>
              </Alert>
            )}

            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {status === 'expired' && (
              <div className="space-y-4">
                <p className="text-sm text-gray-600 text-center">
                  Would you like us to send a new verification link?
                </p>
                <Button
                  onClick={handleResendVerification}
                  disabled={verifying}
                  className="w-full"
                >
                  {verifying ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Sending...
                    </>
                  ) : (
                    'Resend Verification Email'
                  )}
                </Button>
              </div>
            )}

            {(status === 'error' || status === 'expired') && (
              <div className="text-center">
                <Link
                  href="/login"
                  className="text-sm text-blue-600 hover:text-blue-500"
                >
                  Back to login
                </Link>
              </div>
            )}

            {status === 'success' && (
              <div className="text-center">
                <p className="text-sm text-gray-600">
                  You can now sign in to your account.
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
