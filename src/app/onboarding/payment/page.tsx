'use client'

import { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { motion, AnimatePresence } from 'framer-motion'
import { CreditCard, Shield, CheckCircle, AlertCircle, Smartphone, Loader2, ArrowLeft, Sparkles, Lock, Zap } from 'lucide-react'
import PaymentProgress from '@/components/payment/PaymentProgress'
import { PaymentPoller, pollPaymentStatus } from '@/lib/payment-polling'

// =============================================================================
// TYPES
// =============================================================================

interface SelectedPlan {
  plan: {
    id: string
    name: string
    price_monthly_paise: number
    price_yearly_paise: number
  }
  billingCycle: 'monthly' | 'yearly'
}

// =============================================================================
// PAYMENT PAGE
// =============================================================================

export default function Payment() {
  const [selectedPlan, setSelectedPlan] = useState<SelectedPlan | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState('')
  const [paymentStatus, setPaymentStatus] = useState<'pending' | 'processing' | 'completed' | 'failed' | 'timeout'>('pending')
  const [paymentProgress, setPaymentProgress] = useState(0)
  const [timeRemaining, setTimeRemaining] = useState(0)
  const [paymentError, setPaymentError] = useState('')
  const [paymentPoller, setPaymentPoller] = useState<PaymentPoller | null>(null)

  const router = useRouter()
  const searchParams = useSearchParams()

  useEffect(() => {
    const status = searchParams.get('status')
    const transactionId = searchParams.get('transactionId')

    if (status && transactionId) {
      verifyPayment(transactionId)
    } else {
      fetchSelectedPlan()
    }
  }, [searchParams])

  async function fetchSelectedPlan() {
    try {
      const response = await fetch('/api/onboarding/current-selection')
      const data = await response.json()

      if (data.selectedPlan) {
        setSelectedPlan(data.selectedPlan)
      } else {
        setError('Please choose a plan to continue')
      }
    } catch (err) {
      setError('Failed to load plan details')
    } finally {
      setIsLoading(false)
    }
  }

  async function verifyPayment(transactionId: string) {
    setIsProcessing(true)
    setPaymentStatus('pending')
    setPaymentError('')

    // Start payment polling with enhanced progress tracking
    const poller = pollPaymentStatus({
      merchantOrderId: transactionId,
      onSuccess: (status) => {
        setPaymentStatus('completed')
        setPaymentProgress(100)
        setIsProcessing(false)

        // Redirect to onboarding session after a short delay
        setTimeout(() => {
          router.push('/onboarding/session/step/1?welcome=true')
        }, 2000)
      },
      onFailure: (status) => {
        setPaymentStatus('failed')
        setPaymentError(status.error || 'Payment failed. Please try again.')
        setIsProcessing(false)
      },
      onError: (error) => {
        setPaymentStatus('failed')
        setPaymentError(error.message || 'Payment verification failed. Please try again.')
        setIsProcessing(false)
      },
      onProgress: (progress, timeRemaining) => {
        setPaymentProgress(progress)
        setTimeRemaining(timeRemaining)

        // Update status based on progress
        if (progress < 25) {
          setPaymentStatus('pending')
        } else if (progress < 75) {
          setPaymentStatus('processing')
        }
      },
      onTimeout: () => {
        setPaymentStatus('timeout')
        setPaymentError('Payment verification timed out. Please check your payment status or try again.')
        setIsProcessing(false)
      },
      timeout: 5 * 60 * 1000, // 5 minutes
      maxRetries: 30,
      initialDelay: 2000,
      maxDelay: 10000,
    })

    setPaymentPoller(poller)
  }

  function retryPayment() {
    if (paymentPoller) {
      paymentPoller.stop()
    }

    // Reset state and retry
    setPaymentStatus('pending')
    setPaymentProgress(0)
    setTimeRemaining(0)
    setPaymentError('')

    const transactionId = searchParams.get('transactionId')
    if (transactionId) {
      verifyPayment(transactionId)
    }
  }

  function cancelPayment() {
    if (paymentPoller) {
      paymentPoller.stop()
    }
    setIsProcessing(false)
    setPaymentStatus('pending')
    router.push('/onboarding/plans')
  }

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (paymentPoller) {
        paymentPoller.stop()
      }
    }
  }, [paymentPoller])

  async function initiatePayment() {
    setIsProcessing(true)
    setError('')

    try {
      const response = await fetch('/api/payments/initiate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          planId: selectedPlan?.plan.id,
          billingCycle: selectedPlan?.billingCycle,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to initiate payment')
      }

      // PhonePe API returns redirectUrl
      if (data.redirectUrl) {
        window.location.href = data.redirectUrl
      } else if (data.url) {
        // Fallback for backwards compatibility
        window.location.href = data.url
      } else {
        throw new Error('No redirect URL received from payment provider')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Payment failed')
      setIsProcessing(false)
    }
  }


  function formatPrice(paise: number): string {
    return `₹${(paise / 100).toLocaleString('en-IN')}`
  }

  function getPrice(): number {
    if (!selectedPlan) return 0
    return selectedPlan.billingCycle === 'monthly'
      ? selectedPlan.plan.price_monthly_paise
      : selectedPlan.plan.price_yearly_paise
  }

  function getMonthlyEquivalent(): number {
    if (!selectedPlan) return 0
    return Math.round(getPrice() / (selectedPlan.billingCycle === 'yearly' ? 12 : 1))
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center"
        >
          <div className="relative">
            <Loader2 className="w-16 h-16 animate-spin text-indigo-500 mx-auto mb-6" />
            <div className="absolute inset-0 w-16 h-16 mx-auto rounded-full bg-indigo-500/20 animate-ping" />
          </div>
          <h2 className="text-xl font-semibold text-white mb-2">Preparing Your Payment</h2>
          <p className="text-slate-400">Please wait while we set everything up...</p>
        </motion.div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/3 -left-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-1/3 -right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse delay-1000" />
      </div>

      <div className="relative z-10 max-w-4xl mx-auto px-4 py-12">
        {/* Back button */}
        <motion.button
          onClick={() => router.push('/onboarding/plans')}
          className="flex items-center gap-2 text-slate-400 hover:text-white mb-8 transition-colors group"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
        >
          <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
          <span>Change Plan</span>
        </motion.button>

        {/* Header */}
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <motion.div
            className="inline-flex items-center justify-center w-20 h-20 rounded-3xl bg-gradient-to-br from-indigo-500 to-purple-600 shadow-2xl shadow-indigo-500/30 mb-6"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", stiffness: 200, delay: 0.2 }}
          >
            <CreditCard className="w-10 h-10 text-white" />
          </motion.div>
          <h1 className="text-3xl md:text-4xl font-bold text-white mb-3">
            Complete Your
            <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent"> Purchase</span>
          </h1>
          <p className="text-slate-400 max-w-md mx-auto">
            Secure payment powered by PhonePe. Your subscription starts immediately after payment.
          </p>
        </motion.div>

        <div className="grid lg:grid-cols-5 gap-8">
          {/* Order Summary - Main */}
          <motion.div
            className="lg:col-span-3"
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <div className="bg-slate-900/80 backdrop-blur-xl rounded-3xl border border-slate-800 p-8">
              <h2 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-indigo-400" />
                Order Summary
              </h2>

              {/* Plan card */}
              <div className="bg-gradient-to-br from-slate-800/50 to-slate-800/30 rounded-2xl p-6 mb-6 border border-slate-700/50">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-xl font-bold text-white">{selectedPlan?.plan.name} Plan</h3>
                    <p className="text-slate-400 text-sm capitalize">{selectedPlan?.billingCycle} Billing</p>
                  </div>
                  <div className="text-right">
                    <p className="text-3xl font-bold text-white">{formatPrice(getPrice())}</p>
                    <p className="text-slate-500 text-sm">{formatPrice(getMonthlyEquivalent())}/month</p>
                  </div>
                </div>
              </div>

              {/* Features included */}
              <div className="mb-8">
                <h4 className="text-sm font-medium text-slate-400 uppercase tracking-wider mb-4">What's included:</h4>
                <div className="grid grid-cols-2 gap-3">
                  {[
                    'Full platform access',
                    'Priority support',
                    'Cancel anytime',
                    '30-day guarantee'
                  ].map((feature, i) => (
                    <motion.div
                      key={feature}
                      className="flex items-center gap-2 text-slate-300"
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.3 + i * 0.1 }}
                    >
                      <div className="flex-shrink-0 w-5 h-5 rounded-full bg-emerald-500/20 flex items-center justify-center">
                        <CheckCircle className="w-3 h-3 text-emerald-400" />
                      </div>
                      <span className="text-sm">{feature}</span>
                    </motion.div>
                  ))}
                </div>
              </div>

              {/* Divider */}
              <div className="border-t border-slate-700/50 my-6" />

              {/* Total */}
              <div className="flex items-center justify-between mb-8">
                <span className="text-lg font-semibold text-white">Total</span>
                <div className="text-right">
                  <span className="text-3xl font-bold bg-gradient-to-r from-white to-slate-300 bg-clip-text text-transparent">
                    {formatPrice(getPrice())}
                  </span>
                  {selectedPlan?.billingCycle === 'yearly' && (
                    <p className="text-sm text-emerald-400">You save 17%!</p>
                  )}
                </div>
              </div>

              {/* Enhanced Payment Progress */}
              <AnimatePresence>
                {isProcessing && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    className="mb-6"
                  >
                    <PaymentProgress
                      status={paymentStatus}
                      progress={paymentProgress}
                      timeRemaining={timeRemaining}
                      onRetry={retryPayment}
                      onCancel={cancelPayment}
                      errorType={paymentError}
                      planName={selectedPlan?.plan.name}
                    />
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Payment button */}
              <motion.button
                onClick={initiatePayment}
                disabled={isProcessing}
                className={`w-full py-4 rounded-2xl font-semibold text-lg flex items-center justify-center gap-3 transition-all duration-300 ${isProcessing
                    ? 'bg-slate-700 text-slate-400 cursor-not-allowed'
                    : 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-xl shadow-indigo-500/25 hover:shadow-2xl hover:shadow-indigo-500/40 hover:scale-[1.02] active:scale-[0.98]'
                  }`}
                whileTap={{ scale: isProcessing ? 1 : 0.98 }}
              >
                {isProcessing ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Redirecting to PhonePe...
                  </>
                ) : (
                  <>
                    <Smartphone className="w-5 h-5" />
                    Pay {formatPrice(getPrice())} with PhonePe
                  </>
                )}
              </motion.button>
            </div>
          </motion.div>

          {/* Sidebar - Trust & Security */}
          <motion.div
            className="lg:col-span-2 space-y-6"
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
          >
            {/* Security card */}
            <div className="bg-slate-900/80 backdrop-blur-xl rounded-3xl border border-slate-800 p-6 text-center">
              <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-emerald-500/10 mb-4">
                <Shield className="w-7 h-7 text-emerald-400" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Secure Payment</h3>
              <p className="text-slate-400 text-sm">
                Your payment is encrypted with bank-level security. We never store your card details.
              </p>
            </div>

            {/* Payment method */}
            <div className="bg-slate-900/80 backdrop-blur-xl rounded-3xl border border-slate-800 p-6">
              <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wider mb-4">Payment Method</h3>
              <div className="flex items-center gap-4 p-4 rounded-xl bg-slate-800/50 border border-slate-700/50">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-indigo-600 flex items-center justify-center">
                  <Smartphone className="w-6 h-6 text-white" />
                </div>
                <div className="flex-1">
                  <p className="font-semibold text-white">PhonePe</p>
                  <p className="text-xs text-slate-400">UPI, Cards, Wallets & More</p>
                </div>
                <div className="px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-400 text-xs font-medium">
                  Recommended
                </div>
              </div>
            </div>

            {/* Support */}
            <div className="bg-slate-900/80 backdrop-blur-xl rounded-3xl border border-slate-800 p-6 text-center">
              <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-blue-500/10 mb-4">
                <Zap className="w-7 h-7 text-blue-400" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Need Help?</h3>
              <p className="text-slate-400 text-sm mb-4">
                Our support team is here to assist you 24/7.
              </p>
              <button className="text-indigo-400 hover:text-indigo-300 text-sm font-medium transition-colors">
                Contact Support →
              </button>
            </div>
          </motion.div>
        </div>

        {/* Error message */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="mt-8 max-w-lg mx-auto p-4 rounded-xl bg-red-500/10 border border-red-500/20 flex items-center gap-3"
            >
              <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
              <p className="text-red-400">{error}</p>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Terms */}
        <motion.p
          className="text-center text-xs text-slate-500 mt-12"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
        >
          By completing this purchase, you agree to our{' '}
          <Link href="/terms" className="text-indigo-400 hover:text-indigo-300 transition-colors">Terms of Service</Link> and{' '}
          <Link href="/privacy" className="text-indigo-400 hover:text-indigo-300 transition-colors">Privacy Policy</Link>.
        </motion.p>

        {/* Security badges */}
        <motion.div
          className="flex justify-center items-center gap-6 mt-8 text-slate-600"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.9 }}
        >
          <div className="flex items-center gap-1.5">
            <Lock className="w-3.5 h-3.5" />
            <span className="text-xs">256-bit SSL</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Shield className="w-3.5 h-3.5" />
            <span className="text-xs">PCI Compliant</span>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
