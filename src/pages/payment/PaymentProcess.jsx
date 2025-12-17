import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useAuth } from '../../contexts/AuthContext'
import { PLAN_PRICES, verifyPayment } from '../../lib/phonepe'
import { CreditCard, Shield, CheckCircle, ArrowLeft, Loader, AlertCircle } from 'lucide-react'

const PaymentProcess = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { refreshProfile } = useAuth()
  
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
    <div className="min-h-screen bg-paper flex flex-col">
      <header className="p-6">
        <button
          onClick={() => navigate('/')}
          className="text-ink text-xl tracking-tight font-serif"
        >
          Raptorflow
        </button>
      </header>

      <main className="flex-1 flex items-center justify-center px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full max-w-md"
        >
          {status === 'success' ? (
            // Success state
            <div className="rounded-card border border-border bg-card p-8 text-center">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="w-20 h-20 bg-signal-muted rounded-full flex items-center justify-center mx-auto mb-6"
              >
                <CheckCircle className="w-10 h-10 text-primary" />
              </motion.div>
              <h1 className="font-serif text-headline-sm text-ink mb-2">Payment confirmed</h1>
              <p className="text-body-sm text-ink-400 mb-4">
                Welcome to <span className="text-primary">{plan.name}</span>
              </p>
              <p className="text-body-xs text-ink-400 mb-6">
                Your plan has been activated. Redirecting to your dashboard…
              </p>
              <div className="w-8 h-8 border-2 border-primary/40 border-t-primary rounded-full animate-spin mx-auto" />
            </div>
          ) : (
            // Payment form
            <div className="rounded-card border border-border bg-card overflow-hidden">
              {/* Header */}
              <div className="bg-muted border-b border-border p-6">
                <button
                  onClick={() => navigate('/onboarding/plan')}
                  className="flex items-center gap-2 text-ink-400 hover:text-ink text-sm mb-4 transition-editorial"
                >
                  <ArrowLeft className="w-4 h-4" />
                  Back to plans
                </button>
                <h1 className="font-serif text-headline-sm text-ink">Complete your purchase</h1>
                <p className="text-body-sm text-ink-400 mt-1">
                  You're getting the <span className="text-primary">{plan.name}</span> plan
                </p>
              </div>

              {/* Order summary */}
              <div className="p-6 border-b border-border">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-ink">{plan.name} plan</span>
                  <span className="text-ink font-medium">{plan.priceDisplay}</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-ink-400">GST included</span>
                  <span className="text-ink-400">One-time payment</span>
                </div>
                <div className="mt-4 pt-4 border-t border-border">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-ink-400 text-sm">Cohort limit</span>
                    <span className="text-ink-400 text-sm">{plan.cohorts} cohorts</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-ink font-medium">Total</span>
                    <span className="text-2xl font-light text-ink">{plan.priceDisplay}</span>
                  </div>
                </div>
              </div>

              {/* Transaction info */}
              <div className="px-6 py-3 bg-muted border-b border-border">
                <p className="text-xs text-ink-400">
                  Transaction ID: <span className="text-ink font-mono">{txnId}</span>
                </p>
              </div>

              {/* Error */}
              {error && (
                <div className="mx-6 mt-6 p-4 bg-signal-muted border border-primary/20 rounded-lg flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
                  <p className="text-ink text-sm">{error}</p>
                </div>
              )}

              {/* Payment button */}
              <div className="p-6">
                <button
                  onClick={handlePayment}
                  disabled={processing}
                  className="w-full flex items-center justify-center gap-3 px-6 py-4 bg-primary hover:opacity-95 text-primary-foreground font-medium rounded-xl transition-editorial disabled:opacity-50"
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
                  <div className="mt-4 p-3 bg-muted border border-border rounded-lg">
                    <p className="text-ink-400 text-xs text-center">
                      Test mode — no real payment will be processed
                    </p>
                  </div>
                )}

                {/* Security note */}
                <div className="flex items-center justify-center gap-2 mt-4 text-ink-400 text-xs">
                  <Shield className="w-4 h-4" />
                  <span>Secured by PhonePe Payment Gateway</span>
                </div>
              </div>

              {/* Features */}
              <div className="px-6 pb-6">
                <p className="text-xs text-ink-400 text-center">
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
