import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useAuth } from '../contexts/AuthContext'
import { Mail, ArrowRight, AlertCircle, CheckCircle } from 'lucide-react'

const Login = () => {
  const navigate = useNavigate()
  const { signInWithGoogle, signInWithEmail, isAuthenticated, loading } = useAuth()
  
  const [email, setEmail] = useState('')
  const [emailSent, setEmailSent] = useState(false)
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Check for error in URL params (from OAuth callback redirect)
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search)
    const errorParam = urlParams.get('error')
    if (errorParam) {
      setError(decodeURIComponent(errorParam))
      // Clean up URL
      window.history.replaceState({}, '', window.location.pathname)
    }
  }, [])

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/app', { replace: true })
    }
  }, [isAuthenticated, navigate])

  const handleGoogleSignIn = async () => {
    setError('')
    const { error } = await signInWithGoogle()
    if (error) {
      setError(error.message || 'Failed to sign in with Google')
    }
  }

  const handleEmailSignIn = async (e) => {
    e.preventDefault()
    if (!email) return

    setError('')
    setIsSubmitting(true)

    const { error, message } = await signInWithEmail(email)
    
    if (error) {
      setError(error.message || 'Failed to send login link')
    } else {
      setEmailSent(true)
    }
    
    setIsSubmitting(false)
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-amber-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-black flex flex-col">
      {/* Background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-gradient-radial from-amber-900/20 via-transparent to-transparent" />
      </div>

      {/* Header */}
      <header className="relative z-10 p-6">
        <button 
          onClick={() => navigate('/')}
          className="text-white text-xl tracking-tight font-light"
        >
          Raptor<span className="italic font-normal text-amber-200">flow</span>
        </button>
      </header>

      {/* Main content */}
      <main className="flex-1 flex items-center justify-center px-6 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full max-w-md"
        >
          {/* Card */}
          <div className="bg-zinc-900/50 border border-white/10 rounded-2xl p-8 backdrop-blur-xl">
            
            {!emailSent ? (
              <>
                {/* Header */}
                <div className="text-center mb-8">
                  <h1 className="text-2xl font-light text-white mb-2">
                    Welcome back
                  </h1>
                  <p className="text-white/40 text-sm">
                    Sign in to access your strategic workspace
                  </p>
                </div>

                {/* Error */}
                {error && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-lg flex items-center gap-3"
                  >
                    <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
                    <p className="text-red-400 text-sm">{error}</p>
                  </motion.div>
                )}

                {/* Google Sign In */}
                <button
                  onClick={handleGoogleSignIn}
                  disabled={loading}
                  className="w-full flex items-center justify-center gap-3 px-4 py-3.5 bg-white hover:bg-gray-100 text-black font-medium rounded-xl transition-colors disabled:opacity-50"
                >
                  <svg className="w-5 h-5" viewBox="0 0 24 24">
                    <path
                      fill="currentColor"
                      d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                    />
                    <path
                      fill="#34A853"
                      d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                    />
                    <path
                      fill="#FBBC05"
                      d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                    />
                    <path
                      fill="#EA4335"
                      d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                    />
                  </svg>
                  Continue with Google
                </button>

                {/* Divider */}
                <div className="flex items-center gap-4 my-6">
                  <div className="flex-1 h-px bg-white/10" />
                  <span className="text-white/30 text-xs uppercase tracking-wider">or</span>
                  <div className="flex-1 h-px bg-white/10" />
                </div>

                {/* Email Sign In */}
                <form onSubmit={handleEmailSignIn}>
                  <div className="relative mb-4">
                    <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/30" />
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="Enter your email"
                      className="w-full pl-12 pr-4 py-3.5 bg-white/5 border border-white/10 rounded-xl text-white placeholder:text-white/30 focus:border-amber-500/50 focus:outline-none transition-colors"
                      required
                    />
                  </div>
                  
                  <button
                    type="submit"
                    disabled={isSubmitting || !email}
                    className="w-full flex items-center justify-center gap-2 px-4 py-3.5 bg-amber-500 hover:bg-amber-400 text-black font-medium rounded-xl transition-colors disabled:opacity-50"
                  >
                    {isSubmitting ? (
                      <div className="w-5 h-5 border-2 border-black/30 border-t-black rounded-full animate-spin" />
                    ) : (
                      <>
                        Continue with Email
                        <ArrowRight className="w-4 h-4" />
                      </>
                    )}
                  </button>
                </form>

                {/* Terms */}
                <p className="mt-6 text-center text-xs text-white/30">
                  By continuing, you agree to our{' '}
                  <a href="#" className="text-white/50 hover:text-white">Terms of Service</a>
                  {' '}and{' '}
                  <a href="#" className="text-white/50 hover:text-white">Privacy Policy</a>
                </p>
              </>
            ) : (
              // Email sent confirmation
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="text-center py-8"
              >
                <div className="w-16 h-16 bg-emerald-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
                  <CheckCircle className="w-8 h-8 text-emerald-400" />
                </div>
                <h2 className="text-xl font-light text-white mb-2">Check your email</h2>
                <p className="text-white/40 text-sm mb-6">
                  We sent a magic link to <span className="text-white">{email}</span>
                </p>
                <button
                  onClick={() => setEmailSent(false)}
                  className="text-amber-400 hover:text-amber-300 text-sm"
                >
                  Use a different email
                </button>
              </motion.div>
            )}
          </div>

          {/* Bottom link */}
          <p className="text-center mt-6 text-white/40 text-sm">
            Don't have an account?{' '}
            <button 
              onClick={() => navigate('/#pricing')}
              className="text-amber-400 hover:text-amber-300"
            >
              View pricing
            </button>
          </p>
        </motion.div>
      </main>
    </div>
  )
}

export default Login
