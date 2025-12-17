import React, { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { verifyPayment, checkPaymentStatus } from '../../lib/phonepe'
import { useAuth } from '../../contexts/AuthContext'
import { CheckCircle, Clock } from 'lucide-react'

import { ErrorState } from '@/components/ErrorState'

const PaymentCallback = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { refreshProfile } = useAuth()
  
  // PhonePe callback params
  const txnId = searchParams.get('txnId') || searchParams.get('transactionId')
  const code = searchParams.get('code')
  const isMock = searchParams.get('mock') === 'true'
  
  const [status, setStatus] = useState('checking')
  const [message, setMessage] = useState('')
  const [retryCount, setRetryCount] = useState(0)

  useEffect(() => {
    const verifyPaymentStatus = async () => {
      if (!txnId) {
        setStatus('failed')
        setMessage('Invalid transaction - no transaction ID found')
        return
      }

      try {
        // First check the current status
        const statusResult = await checkPaymentStatus(txnId)
        
        if (statusResult.success && statusResult.payment?.status === 'completed') {
          // Already completed
          setStatus('success')
          setMessage('Payment verified successfully!')
          
          if (refreshProfile) {
            await refreshProfile()
          }
          
          setTimeout(() => navigate('/app'), 2000)
          return
        }

        // If PhonePe callback indicates success, verify and complete
        if (code === 'PAYMENT_SUCCESS') {
          const result = await verifyPayment(txnId, false)
          
          if (result.success && result.status === 'completed') {
            setStatus('success')
            setMessage('Payment verified successfully!')
            
            if (refreshProfile) {
              await refreshProfile()
            }
            
            setTimeout(() => navigate('/app'), 2000)
          } else {
            setStatus('failed')
            setMessage(result.message || result.error || 'Payment verification failed')
          }
          return
        }

        // If mock mode, process as mock
        if (isMock) {
          const result = await verifyPayment(txnId, true)
          
          if (result.success && result.status === 'completed') {
            setStatus('success')
            setMessage('Test payment completed!')
            
            if (refreshProfile) {
              await refreshProfile()
            }
            
            setTimeout(() => navigate('/app'), 2000)
          } else {
            setStatus('failed')
            setMessage(result.message || result.error || 'Test payment failed')
          }
          return
        }

        // If we get here with PAYMENT_PENDING or unknown status
        if (code === 'PAYMENT_PENDING') {
          setStatus('pending')
          setMessage('Payment is being processed. This may take a few moments...')
          
          // Retry verification after 3 seconds
          if (retryCount < 5) {
            setTimeout(() => {
              setRetryCount(prev => prev + 1)
            }, 3000)
          } else {
            setStatus('failed')
            setMessage('Payment verification timed out. Please check your payment status or try again.')
          }
          return
        }

        // Payment failed or cancelled
        if (code === 'PAYMENT_DECLINED' || code === 'PAYMENT_CANCELLED' || code === 'PAYMENT_ERROR') {
          setStatus('failed')
          setMessage(
            code === 'PAYMENT_CANCELLED' 
              ? 'Payment was cancelled' 
              : 'Payment was declined or failed'
          )
          return
        }

        // Unknown status - check with backend
        if (statusResult.payment?.status === 'pending' || statusResult.payment?.status === 'initiated') {
          setStatus('pending')
          setMessage('Waiting for payment confirmation...')
          
          if (retryCount < 5) {
            setTimeout(() => {
              setRetryCount(prev => prev + 1)
            }, 3000)
          }
        } else if (statusResult.payment?.status === 'failed') {
          setStatus('failed')
          setMessage('Payment failed. Please try again.')
        } else {
          setStatus('failed')
          setMessage('Unable to verify payment status')
        }

      } catch (err) {
        console.error('Payment verification error:', err)
        setStatus('failed')
        setMessage(err.message || 'Verification failed')
      }
    }

    verifyPaymentStatus()
  }, [txnId, code, isMock, navigate, refreshProfile, retryCount])

  const handleRetry = () => {
    setRetryCount(0)
    setStatus('checking')
    setMessage('')
  }

  return (
    <div className="min-h-screen bg-paper flex flex-col items-center justify-center px-6">
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-2xl"
      >
        {status === 'checking' && (
          <div className="rounded-card border border-border bg-card p-8 md:p-10 text-center">
            <div className="mx-auto h-12 w-12 rounded-full border-2 border-primary/40 border-t-primary animate-spin" />
            <h1 className="mt-5 font-serif text-headline-sm text-ink">Verifying payment</h1>
            <p className="mt-2 text-body-sm text-ink-400">Please wait while we confirm your payment.</p>
          </div>
        )}

        {status === 'pending' && (
          <div className="rounded-card border border-border bg-card p-8 md:p-10 text-center">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
              className="mx-auto mb-5 flex h-12 w-12 items-center justify-center rounded-full bg-signal-muted"
            >
              <Clock className="h-6 w-6 text-primary" />
            </motion.div>
            <h1 className="font-serif text-headline-sm text-ink">Processing payment</h1>
            <p className="mt-2 text-body-sm text-ink-400">{message}</p>
            <p className="mt-4 text-caption text-ink-400">Attempt {retryCount + 1}/5</p>
          </div>
        )}

        {status === 'success' && (
          <div className="rounded-card border border-border bg-card p-8 md:p-10 text-center">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className="mx-auto mb-5 flex h-12 w-12 items-center justify-center rounded-full bg-signal-muted"
            >
              <CheckCircle className="h-6 w-6 text-primary" />
            </motion.div>
            <h1 className="font-serif text-headline-sm text-ink">Payment confirmed</h1>
            <p className="mt-2 text-body-sm text-ink-400">{message}</p>
            <p className="mt-6 text-body-sm text-primary">Redirecting to your dashboard…</p>
          </div>
        )}

        {status === 'failed' && (
          <div className="space-y-4">
            <ErrorState
              title="We couldn't verify your payment"
              description={message}
              action={{
                label: 'Try again',
                onClick: handleRetry
              }}
              secondaryAction={{
                label: 'Back to plans',
                onClick: () => navigate('/onboarding/plan')
              }}
            />

            <div className="rounded-card border border-border bg-card px-6 py-4">
              <p className="text-body-xs text-ink-400">
                Transaction ID: <span className="font-mono text-ink">{txnId}</span>
              </p>
              <p className="mt-2 text-body-xs text-ink-400">
                Need help?{' '}
                <a href="mailto:support@raptorflow.com" className="text-primary hover:text-primary/80 transition-editorial">
                  Contact support
                </a>
              </p>
            </div>
          </div>
        )}
      </motion.div>
    </div>
  )
}

export default PaymentCallback
