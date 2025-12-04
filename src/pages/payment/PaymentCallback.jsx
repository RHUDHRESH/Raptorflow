import React, { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { verifyPayment, checkPaymentStatus } from '../../lib/phonepe'
import { useAuth } from '../../contexts/AuthContext'
import { CheckCircle, XCircle, Clock, RefreshCw } from 'lucide-react'

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
    <div className="min-h-screen bg-black flex flex-col items-center justify-center px-6">
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-gradient-radial from-amber-900/20 via-transparent to-transparent" />
      </div>

      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="relative z-10 text-center max-w-md"
      >
        {/* Checking / Loading state */}
        {status === 'checking' && (
          <div>
            <div className="w-20 h-20 border-4 border-amber-500/30 border-t-amber-500 rounded-full animate-spin mx-auto mb-6" />
            <h1 className="text-2xl font-light text-white mb-2">Verifying Payment</h1>
            <p className="text-white/40">Please wait while we confirm your payment...</p>
          </div>
        )}

        {/* Pending state */}
        {status === 'pending' && (
          <div>
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
              className="w-20 h-20 bg-amber-500/20 rounded-full flex items-center justify-center mx-auto mb-6"
            >
              <Clock className="w-10 h-10 text-amber-400" />
            </motion.div>
            <h1 className="text-2xl font-light text-white mb-2">Processing Payment</h1>
            <p className="text-white/40 mb-4">{message}</p>
            <p className="text-white/30 text-sm">
              Attempt {retryCount + 1}/5
            </p>
          </div>
        )}

        {/* Success state */}
        {status === 'success' && (
          <div>
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className="w-20 h-20 bg-emerald-500/20 rounded-full flex items-center justify-center mx-auto mb-6"
            >
              <CheckCircle className="w-10 h-10 text-emerald-400" />
            </motion.div>
            <h1 className="text-2xl font-light text-white mb-2">Payment Successful!</h1>
            <p className="text-white/40 mb-6">{message}</p>
            <p className="text-amber-400 text-sm">Redirecting to your dashboard...</p>
          </div>
        )}

        {/* Failed state */}
        {status === 'failed' && (
          <div>
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className="w-20 h-20 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-6"
            >
              <XCircle className="w-10 h-10 text-red-400" />
            </motion.div>
            <h1 className="text-2xl font-light text-white mb-2">Payment Issue</h1>
            <p className="text-white/40 mb-6">{message}</p>
            
            <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
              <button
                onClick={handleRetry}
                className="flex items-center gap-2 px-6 py-2.5 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors"
              >
                <RefreshCw className="w-4 h-4" />
                Try Again
              </button>
              <button
                onClick={() => navigate('/onboarding/plan')}
                className="px-6 py-2.5 bg-amber-500 hover:bg-amber-400 text-black rounded-lg transition-colors"
              >
                Back to Plans
              </button>
            </div>
            
            <p className="text-white/30 text-xs mt-6">
              Transaction ID: <span className="font-mono">{txnId}</span>
            </p>
            <p className="text-white/30 text-xs mt-2">
              Need help? <a href="mailto:support@raptorflow.com" className="text-amber-400 hover:underline">Contact support</a>
            </p>
          </div>
        )}
      </motion.div>
    </div>
  )
}

export default PaymentCallback
