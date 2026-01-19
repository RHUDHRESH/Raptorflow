'use client'

import React, { useState } from 'react'
import Link from 'next/link'
import { Loader2, Mail, ArrowLeft, CheckCircle2 } from 'lucide-react'

// =============================================================================
// FORGOT PASSWORD PAGE - RaptorFlow Quiet Luxury Design
// =============================================================================

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setIsLoading(true)
    setError('')
    setMessage('')

    try {
      const response = await fetch('/api/auth/forgot-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to send reset instructions')
      }

      setMessage('Password reset instructions have been sent to your email.')
    } catch (err: any) {
      setError(err.message || 'Failed to send reset instructions')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#F3F4EE] px-4 py-12">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <Link href="/" className="inline-block">
            <span className="font-serif text-2xl font-semibold text-[#2D3538]">
              RaptorFlow
            </span>
          </Link>
        </div>

        {/* Card */}
        <div className="bg-white border border-[#C0C1BE] rounded-2xl p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="font-serif text-2xl font-semibold text-[#2D3538] mb-2">
              Reset your password
            </h1>
            <p className="text-sm text-[#5B5F61]">
              Enter your email and we'll send you a link to reset your password.
            </p>
          </div>

          {/* Success Message */}
          {message && (
            <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-xl flex items-start gap-3">
              <CheckCircle2 className="w-5 h-5 text-green-600 shrink-0 mt-0.5" />
              <p className="text-sm text-green-700">{message}</p>
            </div>
          )}

          {/* Error Alert */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          {!message ? (
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Email Input */}
              <div>
                <label
                  htmlFor="email"
                  className="block text-sm font-medium text-[#2D3538] mb-1.5"
                >
                  Email
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[#9D9F9F]" />
                  <input
                    id="email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@example.com"
                    className="w-full pl-11 pr-4 py-3 border border-[#C0C1BE] rounded-xl text-[#2D3538] placeholder-[#9D9F9F] focus:outline-none focus:border-[#2D3538] focus:ring-1 focus:ring-[#2D3538] transition-colors"
                  />
                </div>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-[#2D3538] text-[#F3F4EE] font-medium rounded-xl hover:bg-[#1a1f21] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Sending...
                  </>
                ) : (
                  'Send Reset Instructions'
                )}
              </button>
            </form>
          ) : (
            <div className="text-center">
              <p className="text-sm text-[#5B5F61] mb-6">
                Didn't receive the email? Check your spam folder or try again.
              </p>
              <button
                onClick={() => {
                  setMessage('')
                  setEmail('')
                }}
                className="w-full px-4 py-3 border border-[#C0C1BE] text-[#2D3538] font-medium rounded-xl hover:border-[#2D3538] transition-colors"
              >
                Try Again
              </button>
            </div>
          )}

          {/* Back to Login */}
          <div className="mt-8 pt-6 border-t border-[#C0C1BE] text-center">
            <Link
              href="/login"
              className="inline-flex items-center gap-2 text-sm font-medium text-[#5B5F61] hover:text-[#2D3538] transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to sign in
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
