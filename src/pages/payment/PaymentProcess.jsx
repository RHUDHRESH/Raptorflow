import React, { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useAuth } from '../../contexts/AuthContext'
import { PLAN_PRICES, simulatePayment, verifyPayment } from '../../lib/phonepe'
import { CreditCard, Shield, CheckCircle, ArrowLeft, Loader, AlertCircle } from 'lucide-react'

const PaymentProcess = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { user, refreshProfile } = useAuth()
  
  const txnId = searchParams.get('txnId')
  const planId = searchParams.get('plan')
  const isMock = searchParams.get('mock') === 'true'
  
  const [processing, setProcessing] = useState(false)
  const [status, setStatus] = useState('pending') // pending, processing, success, error
  const [error, setError] = useState('')

  const plan = PLAN_PRICES[planId]

  useEffect(() => {
    if (!txnId || !plan) {
      navigate('/#pricing')
    }
  }, [txnId, plan, navigate])

  const handlePayment = async () => {
    setProcessing(true)
    setStatus('processing')
    setError('')

    try {
      // Call backend to verify/complete payment
      // For mock mode, this will mark it as completed
      const result = await verifyPayment(txnId, isMock)
      
      if (result.success && result.status === 'completed') {
        setStatus('success')
        
        // Refresh user profile to get updated plan
        if (refreshProfile) {
          await refreshProfile()
        }
        
        // Redirect to app after 2 seconds
        setTimeout(() => {
          navigate('/app')
        }, 2000)
      } else if (result.status === 'pending') {
        setStatus('error')
        setError('Payment is still being processed. Please wait a moment and try again.')
      } else {
        setStatus('error')
        setError(result.message || result.error || 'Payment verification failed')
      }
    } catch (err) {
      setStatus('error')
      setError(err.message || 'Something went wrong')
    } finally {
      setProcessing(false)
    }
  }

  if (!plan) {
    return null
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
          {status === 'success' ? (
            // Success state
            <div className="bg-zinc-900/50 border border-emerald-500/30 rounded-2xl p-8 text-center">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="w-20 h-20 bg-emerald-500/20 rounded-full flex items-center justify-center mx-auto mb-6"
              >
                <CheckCircle className="w-10 h-10 text-emerald-400" />
              </motion.div>
              <h1 className="text-2xl font-light text-white mb-2">Payment Successful!</h1>
              <p className="text-white/40 mb-4">
                Welcome to <span className="text-amber-400">{plan.name}</span>
              </p>
              <p className="text-white/30 text-sm mb-6">
                Your plan has been activated. Redirecting to your dashboard...
              </p>
              <div className="w-8 h-8 border-2 border-amber-500 border-t-transparent rounded-full animate-spin mx-auto" />
            </div>
          ) : (
            // Payment form
            <div className="bg-zinc-900/50 border border-white/10 rounded-2xl overflow-hidden">
              {/* Header */}
              <div className="bg-gradient-to-r from-amber-500/10 to-amber-600/5 border-b border-white/5 p-6">
                <button
                  onClick={() => navigate('/onboarding/plan')}
                  className="flex items-center gap-2 text-white/40 hover:text-white text-sm mb-4 transition-colors"
                >
                  <ArrowLeft className="w-4 h-4" />
                  Back to plans
                </button>
                <h1 className="text-2xl font-light text-white">Complete your purchase</h1>
                <p className="text-white/40 text-sm mt-1">
                  You're getting the <span className="text-amber-400">{plan.name}</span> plan
                </p>
              </div>

              {/* Order summary */}
              <div className="p-6 border-b border-white/5">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-white/60">{plan.name} Plan</span>
                  <span className="text-white font-medium">{plan.priceDisplay}</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-white/40">GST included</span>
                  <span className="text-white/40">One-time payment</span>
                </div>
                <div className="mt-4 pt-4 border-t border-white/5">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-white/40 text-sm">Cohort limit</span>
                    <span className="text-white/60 text-sm">{plan.cohorts} cohorts</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-white font-medium">Total</span>
                    <span className="text-2xl font-light text-white">{plan.priceDisplay}</span>
                  </div>
                </div>
              </div>

              {/* Transaction info */}
              <div className="px-6 py-3 bg-white/5 border-b border-white/5">
                <p className="text-xs text-white/30">
                  Transaction ID: <span className="text-white/50 font-mono">{txnId}</span>
                </p>
              </div>

              {/* Error */}
              {error && (
                <div className="mx-6 mt-6 p-4 bg-red-500/10 border border-red-500/20 rounded-lg flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                  <p className="text-red-400 text-sm">{error}</p>
                </div>
              )}

              {/* Payment button */}
              <div className="p-6">
                <button
                  onClick={handlePayment}
                  disabled={processing}
                  className="w-full flex items-center justify-center gap-3 px-6 py-4 bg-amber-500 hover:bg-amber-400 text-black font-medium rounded-xl transition-colors disabled:opacity-50"
                >
                  {processing ? (
                    <>
                      <Loader className="w-5 h-5 animate-spin" />
                      Processing Payment...
                    </>
                  ) : (
                    <>
                      <CreditCard className="w-5 h-5" />
                      {isMock ? 'Complete Test Payment' : 'Pay with PhonePe'}
                    </>
                  )}
                </button>

                {/* Mock mode notice */}
                {isMock && (
                  <div className="mt-4 p-3 bg-amber-500/10 border border-amber-500/20 rounded-lg">
                    <p className="text-amber-400 text-xs text-center">
                      🧪 Test Mode - No real payment will be processed
                    </p>
                  </div>
                )}

                {/* Security note */}
                <div className="flex items-center justify-center gap-2 mt-4 text-white/30 text-xs">
                  <Shield className="w-4 h-4" />
                  <span>Secured by PhonePe Payment Gateway</span>
                </div>
              </div>

              {/* Features */}
              <div className="px-6 pb-6">
                <p className="text-xs text-white/30 text-center">
                  7-day satisfaction guarantee. Cancel anytime.
                </p>
              </div>
            </div>
          )}
        </motion.div>
      </main>
    </div>
  )
}

export default PaymentProcess
