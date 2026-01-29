'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Users,
  CreditCard,
  AlertCircle,
  BarChart3,
  PieChart,
  Activity,
  Calendar,
  Download,
  RefreshCw
} from 'lucide-react'

// =============================================================================
// TYPES
// =============================================================================

interface PaymentMetrics {
  total_payments: number
  successful_payments: number
  failed_payments: number
  total_revenue: number
  average_payment_amount: number
  conversion_rate: number
  failure_rate: number
  payment_by_plan: Record<string, {
    total: number
    successful: number
    failed: number
    revenue: number
  }>
}

interface PaymentAnalytics {
  metrics: PaymentMetrics
  recent_transactions: any[]
  error_breakdown: Record<string, number>
  plan_performance: Record<string, any>
  time_trends: {
    daily: any[]
    hourly: any[]
  }
}

interface PaymentAnalyticsProps {
  days?: number
  className?: string
}

// =============================================================================
// COMPONENT
// =============================================================================

export default function PaymentAnalytics({ days = 30, className = "" }: PaymentAnalyticsProps) {
  const [analytics, setAnalytics] = useState<PaymentAnalytics | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState("")
  const [selectedDays, setSelectedDays] = useState(days)

  useEffect(() => {
    fetchAnalytics()
  }, [selectedDays])

  const fetchAnalytics = async () => {
    try {
      setIsLoading(true)
      setError("")

      const response = await fetch(`/api/proxy/v1/payments/analytics/dashboard?days=${selectedDays}`, {
        credentials: 'include',
      })

      if (!response.ok) {
        throw new Error('Failed to fetch analytics')
      }

      const data = await response.json()
      setAnalytics(data.data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load analytics')
    } finally {
      setIsLoading(false)
    }
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR'
    }).format(amount / 100) // Convert from paise to rupees
  }

  const formatPercentage = (value: number) => {
    return `${value.toFixed(1)}%`
  }

  if (isLoading) {
    return (
      <div className={`bg-white rounded-xl border border-gray-200 p-6 ${className}`}>
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="h-20 bg-gray-200 rounded"></div>
            ))}
          </div>
          <div className="h-40 bg-gray-200 rounded"></div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className={`bg-white rounded-xl border border-red-200 p-6 ${className}`}>
        <div className="flex items-center gap-3 text-red-600">
          <AlertCircle className="w-5 h-5" />
          <span>{error}</span>
          <button
            onClick={fetchAnalytics}
            className="ml-auto p-2 hover:bg-red-50 rounded-lg transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>
    )
  }

  if (!analytics) {
    return null
  }

  return (
    <div className={`bg-white rounded-xl border border-gray-200 ${className}`}>
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <BarChart3 className="w-6 h-6 text-indigo-600" />
            <h2 className="text-xl font-semibold text-gray-900">Payment Analytics</h2>
          </div>

          <div className="flex items-center gap-3">
            {/* Days selector */}
            <select
              value={selectedDays}
              onChange={(e) => setSelectedDays(Number(e.target.value))}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value={7}>Last 7 days</option>
              <option value={30}>Last 30 days</option>
              <option value={90}>Last 90 days</option>
            </select>

            <button
              onClick={fetchAnalytics}
              className="p-2 hover:bg-gray-50 rounded-lg transition-colors"
              title="Refresh"
            >
              <RefreshCw className="w-4 h-4 text-gray-600" />
            </button>

            <button
              className="p-2 hover:bg-gray-50 rounded-lg transition-colors"
              title="Export"
            >
              <Download className="w-4 h-4 text-gray-600" />
            </button>
          </div>
        </div>
      </div>

      <div className="p-6 space-y-6">
        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-gradient-to-br from-blue-50 to-indigo-50 p-4 rounded-xl border border-blue-200"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-blue-600 font-medium">Total Revenue</p>
                <p className="text-2xl font-bold text-blue-900">
                  {formatCurrency(analytics.metrics.total_revenue)}
                </p>
              </div>
              <div className="p-3 bg-blue-100 rounded-lg">
                <DollarSign className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-gradient-to-br from-green-50 to-emerald-50 p-4 rounded-xl border border-green-200"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-green-600 font-medium">Successful Payments</p>
                <p className="text-2xl font-bold text-green-900">
                  {analytics.metrics.successful_payments}
                </p>
                <p className="text-xs text-green-600 mt-1">
                  {formatPercentage(analytics.metrics.conversion_rate)} conversion rate
                </p>
              </div>
              <div className="p-3 bg-green-100 rounded-lg">
                <TrendingUp className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-gradient-to-br from-red-50 to-rose-50 p-4 rounded-xl border border-red-200"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-red-600 font-medium">Failed Payments</p>
                <p className="text-2xl font-bold text-red-900">
                  {analytics.metrics.failed_payments}
                </p>
                <p className="text-xs text-red-600 mt-1">
                  {formatPercentage(analytics.metrics.failure_rate)} failure rate
                </p>
              </div>
              <div className="p-3 bg-red-100 rounded-lg">
                <TrendingDown className="w-6 h-6 text-red-600" />
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-gradient-to-br from-purple-50 to-violet-50 p-4 rounded-xl border border-purple-200"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-purple-600 font-medium">Avg. Payment</p>
                <p className="text-2xl font-bold text-purple-900">
                  {formatCurrency(analytics.metrics.average_payment_amount)}
                </p>
              </div>
              <div className="p-3 bg-purple-100 rounded-lg">
                <CreditCard className="w-6 h-6 text-purple-600" />
              </div>
            </div>
          </motion.div>
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Plan Performance */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5 }}
            className="bg-gray-50 p-4 rounded-xl"
          >
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <PieChart className="w-5 h-5 text-indigo-600" />
              Plan Performance
            </h3>
            <div className="space-y-3">
              {Object.entries(analytics.metrics.payment_by_plan).map(([plan, data]) => (
                <div key={plan} className="bg-white p-3 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-gray-900 capitalize">{plan}</span>
                    <span className="text-sm text-gray-600">{data.total} payments</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-green-600">{data.successful} successful</span>
                    <span className="text-red-600">{data.failed} failed</span>
                  </div>
                  <div className="mt-2">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-green-500 h-2 rounded-full"
                        style={{ width: `${(data.successful / data.total) * 100}%` }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Recent Transactions */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.6 }}
            className="bg-gray-50 p-4 rounded-xl"
          >
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Activity className="w-5 h-5 text-indigo-600" />
              Recent Transactions
            </h3>
            <div className="space-y-2">
              {analytics.recent_transactions.slice(0, 5).map((transaction, index) => (
                <div key={index} className="bg-white p-3 rounded-lg flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900 capitalize">{transaction.plan}</p>
                    <p className="text-sm text-gray-600">
                      {new Date(transaction.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium text-gray-900">
                      {formatCurrency(transaction.amount || 0)}
                    </p>
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      transaction.status === 'active'
                        ? 'bg-green-100 text-green-700'
                        : 'bg-red-100 text-red-700'
                    }`}>
                      {transaction.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Error Breakdown */}
        {Object.keys(analytics.error_breakdown).length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
            className="bg-red-50 p-4 rounded-xl border border-red-200"
          >
            <h3 className="text-lg font-semibold text-red-900 mb-4 flex items-center gap-2">
              <AlertCircle className="w-5 h-5" />
              Payment Failures by Reason
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {Object.entries(analytics.error_breakdown).map(([reason, count]) => (
                <div key={reason} className="bg-white p-3 rounded-lg">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-900 capitalize">
                      {reason.replace('_', ' ')}
                    </span>
                    <span className="text-lg font-bold text-red-600">{count}</span>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </div>
    </div>
  )
}

// =============================================================================
// HELPER COMPONENTS
// =============================================================================

export function PaymentAnalyticsSkeleton({ className = "" }: { className?: string }) {
  return (
    <div className={`bg-white rounded-xl border border-gray-200 p-6 ${className}`}>
      <div className="animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/4 mb-6"></div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="h-20 bg-gray-200 rounded"></div>
          ))}
        </div>
        <div className="h-40 bg-gray-200 rounded"></div>
      </div>
    </div>
  )
}
