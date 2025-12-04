import React, { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { checkPaymentStatus, processSuccessfulPayment } from '../../lib/phonepe'
import { CheckCircle, XCircle } from 'lucide-react'

const PaymentCallback = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  
  const txnId = searchParams.get('txnId')
  const code = searchParams.get('code')
  
  const [status, setStatus] = useState('checking')
  const [message, setMessage] = useState('')

  useEffect(() => {
    const verifyPayment = async () => {
      if (!txnId) {
        setStatus('failed')
        setMessage('Invalid transaction')
        return
      }

      try {
        const result = await checkPaymentStatus(txnId)
        
        if (result.success && result.payment) {
          if (result.payment.status === 'success') {
            setStatus('success')
            setMessage('Payment verified successfully!')
            setTimeout(() => navigate('/app'), 2000)
          } else if (result.payment.status === 'failed') {
            setStatus('failed')
            setMessage('Payment was not completed')
          } else if (code === 'PAYMENT_SUCCESS') {
            const processResult = await processSuccessfulPayment(txnId, {
              code: code,
              transactionId: searchParams.get('transactionId'),
            })
            
            if (processResult.success) {
              setStatus('success')
              setMessage('Payment verified successfully!')
              setTimeout(() => navigate('/app'), 2000)
            } else {
              setStatus('failed')
              setMessage(processResult.error || 'Failed to process payment')
            }
          } else {
            setStatus('failed')
            setMessage('Payment verification failed')
          }
        } else {
          setStatus('failed')
          setMessage(result.error || 'Payment not found')
        }
      } catch (err) {
        setStatus('failed')
        setMessage(err.message || 'Verification failed')
      }
    }

    verifyPayment()
  }, [txnId, code, navigate, searchParams])

  return (
    <div className="min-h-screen bg-black flex flex-col items-center justify-center px-6">
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-gradient-radial from-amber-900/20 via-transparent to-transparent" />
      </div>

      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="relative z-10 text-center"
      >
        {status === 'checking' && (
          <div>
            <div className="w-20 h-20 border-4 border-amber-500/30 border-t-amber-500 rounded-full animate-spin mx-auto mb-6" />
            <h1 className="text-2xl font-light text-white mb-2">Verifying Payment</h1>
            <p className="text-white/40">Please wait...</p>
          </div>
        )}

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
            <p className="text-amber-400 text-sm">Redirecting...</p>
          </div>
        )}

        {status === 'failed' && (
          <div>
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className="w-20 h-20 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-6"
            >
              <XCircle className="w-10 h-10 text-red-400" />
            </motion.div>
            <h1 className="text-2xl font-light text-white mb-2">Payment Failed</h1>
            <p className="text-white/40 mb-6">{message}</p>
            <button
              onClick={() => navigate('/#pricing')}
              className="px-6 py-2.5 bg-white/10 hover:bg-white/20 text-white rounded-lg"
            >
              Try Again
            </button>
          </div>
        )}
      </motion.div>
    </div>
  )
}

export default PaymentCallback

