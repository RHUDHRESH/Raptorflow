'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  CheckCircle,
  AlertCircle,
  Clock,
  Loader2,
  RefreshCw,
  XCircle,
  CreditCard,
  Shield,
  Zap
} from 'lucide-react'

// =============================================================================
// TYPES
// =============================================================================

interface PaymentProgressProps {
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'timeout'
  progress?: number
  timeRemaining?: number
  onRetry?: () => void
  onCancel?: () => void
  errorType?: string
  planName?: string
}

type PaymentStatus = 'pending' | 'processing' | 'completed' | 'failed' | 'timeout'

// =============================================================================
// CONFIGURATION
// =============================================================================

const STATUS_CONFIG = {
  pending: {
    color: 'text-yellow-600',
    bgColor: 'bg-yellow-50',
    borderColor: 'border-yellow-200',
    icon: Clock,
    label: 'Payment Pending',
    description: 'Waiting for payment confirmation...',
  },
  processing: {
    color: 'text-blue-600',
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200',
    icon: Loader2,
    label: 'Processing Payment',
    description: 'Verifying your payment with our payment provider...',
  },
  completed: {
    color: 'text-green-600',
    bgColor: 'bg-green-50',
    borderColor: 'border-green-200',
    icon: CheckCircle,
    label: 'Payment Successful',
    description: 'Your payment has been processed successfully!',
  },
  failed: {
    color: 'text-red-600',
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200',
    icon: XCircle,
    label: 'Payment Failed',
    description: 'We couldn\'t process your payment. Please try again.',
  },
  timeout: {
    color: 'text-orange-600',
    bgColor: 'bg-orange-50',
    borderColor: 'border-orange-200',
    icon: AlertCircle,
    label: 'Payment Timeout',
    description: 'Payment verification timed out. Please check your payment status.',
  },
} as const

const ERROR_MESSAGES = {
  'insufficient_funds': 'Insufficient funds. Please use a different payment method.',
  'card_declined': 'Card declined. Please check your card details or use another card.',
  'expired_card': 'Card has expired. Please use a valid payment method.',
  'invalid_cvc': 'Invalid CVC. Please check your security code.',
  'processing_error': 'Payment processing error. Please try again.',
  'network_error': 'Network error. Please check your connection and try again.',
  'timeout': 'Payment timed out. Please try again.',
  'default': 'Payment failed. Please try again or contact support.',
} as const

// =============================================================================
// COMPONENT
// =============================================================================

export default function PaymentProgress({
  status,
  progress = 0,
  timeRemaining,
  onRetry,
  onCancel,
  errorType,
  planName,
}: PaymentProgressProps) {
  const [animatedProgress, setAnimatedProgress] = useState(0)
  const config = STATUS_CONFIG[status]
  const Icon = config.icon

  // Animate progress bar
  useEffect(() => {
    const timer = setTimeout(() => {
      setAnimatedProgress(progress)
    }, 100)
    return () => clearTimeout(timer)
  }, [progress])

  // Format time remaining
  const formatTimeRemaining = (seconds: number) => {
    if (seconds <= 0) return '0s'
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    if (mins > 0) return `${mins}m ${secs}s`
    return `${secs}s`
  }

  // Get error message
  const getErrorMessage = (type?: string) => {
    return ERROR_MESSAGES[type as keyof typeof ERROR_MESSAGES] || ERROR_MESSAGES.default
  }

  // Get status color for progress bar
  const getProgressColor = () => {
    switch (status) {
      case 'pending': return 'bg-yellow-500'
      case 'processing': return 'bg-blue-500'
      case 'completed': return 'bg-green-500'
      case 'failed':
      case 'timeout': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  }

  return (
    <div className={`w-full max-w-md mx-auto p-6 rounded-xl border ${config.borderColor} ${config.bgColor} transition-all duration-300`}>
      {/* Status Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", stiffness: 200, damping: 20 }}
            className={`p-2 rounded-full ${config.bgColor}`}
          >
            <Icon
              className={`w-6 h-6 ${config.color} ${status === 'processing' ? 'animate-spin' : ''}`}
            />
          </motion.div>
          <div>
            <h3 className={`font-semibold ${config.color}`}>
              {config.label}
            </h3>
            <p className="text-sm text-gray-600">
              {config.description}
            </p>
          </div>
        </div>

        {/* Action buttons */}
        <AnimatePresence>
          {(status === 'failed' || status === 'timeout') && onRetry && (
            <motion.button
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              onClick={onRetry}
              className="p-2 rounded-lg bg-white border border-gray-200 hover:bg-gray-50 transition-colors"
              title="Retry Payment"
            >
              <RefreshCw className="w-4 h-4 text-gray-600" />
            </motion.button>
          )}

          {(status === 'pending' || status === 'processing') && onCancel && (
            <motion.button
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              onClick={onCancel}
              className="p-2 rounded-lg bg-white border border-gray-200 hover:bg-gray-50 transition-colors"
              title="Cancel Payment"
            >
              <XCircle className="w-4 h-4 text-gray-600" />
            </motion.button>
          )}
        </AnimatePresence>
      </div>

      {/* Progress Bar */}
      {(status === 'pending' || status === 'processing') && (
        <div className="mb-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">Progress</span>
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-600">{Math.round(animatedProgress)}%</span>
              {timeRemaining !== undefined && (
                <span className="text-xs text-gray-500">
                  {formatTimeRemaining(timeRemaining)} remaining
                </span>
              )}
            </div>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
            <motion.div
              className={`h-full ${getProgressColor()} transition-all duration-300 ease-out`}
              initial={{ width: "0%" }}
              animate={{ width: `${animatedProgress}%` }}
              transition={{ duration: 0.5, ease: "easeOut" }}
            />
          </div>
        </div>
      )}

      {/* Plan Information */}
      {planName && (
        <div className="mb-4 p-3 bg-white rounded-lg border border-gray-200">
          <div className="flex items-center gap-2 mb-1">
            <CreditCard className="w-4 h-4 text-gray-600" />
            <span className="text-sm font-medium text-gray-700">Plan: {planName}</span>
          </div>
          {status === 'completed' && (
            <div className="flex items-center gap-2 text-sm text-green-600">
              <Shield className="w-4 h-4" />
              <span>Payment secured and verified</span>
            </div>
          )}
        </div>
      )}

      {/* Error Details */}
      {(status === 'failed' || status === 'timeout') && errorType && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-4 p-3 bg-white rounded-lg border border-red-200"
        >
          <div className="flex items-start gap-2">
            <AlertCircle className="w-4 h-4 text-red-600 mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-sm text-red-800 font-medium">Payment Error</p>
              <p className="text-xs text-red-600 mt-1">
                {getErrorMessage(errorType)}
              </p>
            </div>
          </div>
        </motion.div>
      )}

      {/* Success Details */}
      {status === 'completed' && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-4 p-3 bg-white rounded-lg border border-green-200"
        >
          <div className="flex items-center gap-2 text-green-600">
            <Zap className="w-4 h-4" />
            <span className="text-sm font-medium">Ready to go!</span>
          </div>
          <p className="text-xs text-gray-600 mt-1">
            Your workspace is now active. Redirecting to dashboard...
          </p>
        </motion.div>
      )}

      {/* Processing Steps */}
      {(status === 'pending' || status === 'processing') && (
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${progress >= 25 ? 'bg-green-500' : 'bg-gray-300'}`} />
            <span className={`text-xs ${progress >= 25 ? 'text-gray-700' : 'text-gray-400'}`}>
              Payment initiated
            </span>
          </div>
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${progress >= 50 ? 'bg-green-500' : 'bg-gray-300'}`} />
            <span className={`text-xs ${progress >= 50 ? 'text-gray-700' : 'text-gray-400'}`}>
              Processing payment
            </span>
          </div>
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${progress >= 75 ? 'bg-green-500' : 'bg-gray-300'}`} />
            <span className={`text-xs ${progress >= 75 ? 'text-gray-700' : 'text-gray-400'}`}>
              Verifying transaction
            </span>
          </div>
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${progress >= 100 ? 'bg-green-500' : 'bg-gray-300'}`} />
            <span className={`text-xs ${progress >= 100 ? 'text-gray-700' : 'text-gray-400'}`}>
              Activating workspace
            </span>
          </div>
        </div>
      )}

      {/* Help Text */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <p className="text-xs text-gray-500 text-center">
          {status === 'completed'
            ? 'Thank you for your payment! Your subscription is now active.'
            : status === 'failed' || status === 'timeout'
            ? 'Need help? Contact our support team for assistance.'
            : 'Please keep this window open until payment is complete.'
          }
        </p>
      </div>
    </div>
  )
}

// =============================================================================
// HELPER COMPONENTS
// =============================================================================

export function PaymentProgressSkeleton() {
  return (
    <div className="w-full max-w-md mx-auto p-6 rounded-xl border border-gray-200 bg-gray-50 animate-pulse">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 bg-gray-300 rounded-full" />
        <div className="flex-1">
          <div className="h-4 bg-gray-300 rounded w-3/4 mb-2" />
          <div className="h-3 bg-gray-300 rounded w-full" />
        </div>
      </div>
      <div className="mb-4">
        <div className="h-2 bg-gray-300 rounded-full" />
      </div>
      <div className="space-y-2">
        <div className="h-3 bg-gray-300 rounded w-full" />
        <div className="h-3 bg-gray-300 rounded w-5/6" />
        <div className="h-3 bg-gray-300 rounded w-4/6" />
      </div>
    </div>
  )
}
