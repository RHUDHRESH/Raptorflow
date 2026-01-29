/**
 * Payment polling utility for real-time payment status updates
 * Handles exponential backoff retry logic and timeout management
 */

interface PaymentStatus {
  success: boolean
  status: string
  transaction_id?: string
  amount?: number
  phonepe_transaction_id?: string
  subscription?: {
    id: string
    plan: string
    status: string
    current_period_end: string
  }
  error?: string
}

interface PaymentPollingOptions {
  merchantOrderId: string
  onSuccess?: (status: PaymentStatus) => void
  onFailure?: (status: PaymentStatus) => void
  onError?: (error: Error) => void
  onProgress?: (progress: number, timeRemaining: number) => void
  onTimeout?: () => void
  timeout?: number // Default: 5 minutes
  maxRetries?: number // Default: 30
  initialDelay?: number // Default: 2000ms
  maxDelay?: number // Default: 10000ms
}

export class PaymentPoller {
  private options: Required<PaymentPollingOptions>
  private pollCount = 0
  private timeoutId: NodeJS.Timeout | null = null
  private isPolling = false
  private startTime = 0

  constructor(options: PaymentPollingOptions) {
    this.options = {
      timeout: 5 * 60 * 1000, // 5 minutes
      maxRetries: 30,
      initialDelay: 2000, // 2 seconds
      maxDelay: 10000, // 10 seconds
      onSuccess: () => {},
      onFailure: () => {},
      onError: () => {},
      onProgress: () => {},
      onTimeout: () => {},
      ...options
    } as Required<PaymentPollingOptions>
  }

  /**
   * Start polling for payment status
   */
  public start(): void {
    if (this.isPolling) {
      console.warn('Payment polling already in progress')
      return
    }

    this.isPolling = true
    this.pollCount = 0
    this.startTime = Date.now()

    console.log(`Starting payment polling for order: ${this.options.merchantOrderId}`)
    this.poll()
  }

  /**
   * Stop polling
   */
  public stop(): void {
    if (this.timeoutId) {
      clearTimeout(this.timeoutId)
      this.timeoutId = null
    }
    this.isPolling = false
    console.log(`Stopped payment polling for order: ${this.options.merchantOrderId}`)
  }

  /**
   * Check if polling is active
   */
  public get isActive(): boolean {
    return this.isPolling
  }

  /**
   * Get polling statistics
   */
  public get stats(): {
    pollCount: number
    elapsedTime: number
    isPolling: boolean
  } {
    return {
      pollCount: this.pollCount,
      elapsedTime: Date.now() - this.startTime,
      isPolling: this.isPolling
    }
  }

  private async poll(): Promise<void> {
    if (!this.isPolling) {
      return
    }

    // Check timeout
    const elapsedTime = Date.now() - this.startTime
    if (elapsedTime > this.options.timeout) {
      console.warn(`Payment polling timeout for order: ${this.options.merchantOrderId}`)
      this.options.onTimeout()
      this.stop()
      return
    }

    // Calculate progress and time remaining
    const progress = Math.min((elapsedTime / this.options.timeout) * 100, 100)
    const timeRemaining = Math.max(0, Math.ceil((this.options.timeout - elapsedTime) / 1000))

    // Report progress
    this.options.onProgress(progress, timeRemaining)

    try {
      const response = await fetch(`/api/payments/status/${this.options.merchantOrderId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const status: PaymentStatus = await response.json()
      this.pollCount++

      console.log(`Payment poll #${this.pollCount} for order ${this.options.merchantOrderId}: ${status.status}`)

      // Check for successful payment
      if (status.success) {
        console.log(`Payment successful for order: ${this.options.merchantOrderId}`)
        this.options.onSuccess(status)
        this.stop()
        return
      }

      // Check for failed payment
      if (status.status === 'FAILED' || status.status === 'CANCELLED') {
        console.log(`Payment failed for order: ${this.options.merchantOrderId}`)
        this.options.onFailure(status)
        this.stop()
        return
      }

      // Check if we've exceeded max retries
      if (this.pollCount >= this.options.maxRetries) {
        console.warn(`Max retries exceeded for order: ${this.options.merchantOrderId}`)
        const error = new Error(`Payment verification timeout after ${this.options.maxRetries} attempts`)
        this.options.onError(error)
        this.stop()
        return
      }

      // Calculate next delay with exponential backoff
      const delay = Math.min(
        this.options.initialDelay * Math.pow(1.5, this.pollCount),
        this.options.maxDelay
      )

      // Schedule next poll
      this.timeoutId = setTimeout(() => {
        this.poll()
      }, delay)

    } catch (error) {
      console.error(`Payment polling error for order ${this.options.merchantOrderId}:`, error)

      // For network errors, continue polling with exponential backoff
      if (this.pollCount < this.options.maxRetries) {
        const delay = Math.min(
          this.options.initialDelay * Math.pow(2, this.pollCount),
          this.options.maxDelay
        )

        this.timeoutId = setTimeout(() => {
          this.poll()
        }, delay)
      } else {
        this.options.onError(error as Error)
        this.stop()
      }
    }
  }
}

/**
 * Convenience function to create and start payment polling
 */
export function pollPaymentStatus(options: PaymentPollingOptions): PaymentPoller {
  const poller = new PaymentPoller(options)
  poller.start()
  return poller
}

/**
 * React hook for payment polling
 */
export function usePaymentPolling() {
  const pollerRef = React.useRef<PaymentPoller | null>(null)

  const startPolling = React.useCallback((options: PaymentPollingOptions) => {
    // Stop any existing polling
    if (pollerRef.current) {
      pollerRef.current.stop()
    }

    // Start new polling
    pollerRef.current = new PaymentPoller(options)
    pollerRef.current.start()

    return pollerRef.current
  }, [])

  const stopPolling = React.useCallback(() => {
    if (pollerRef.current) {
      pollerRef.current.stop()
      pollerRef.current = null
    }
  }, [])

  const isPolling = React.useCallback(() => {
    return pollerRef.current?.isActive || false
  }, [])

  // Cleanup on unmount
  React.useEffect(() => {
    return () => {
      stopPolling()
    }
  }, [stopPolling])

  return {
    startPolling,
    stopPolling,
    isPolling,
    getStats: () => pollerRef.current?.stats || { pollCount: 0, elapsedTime: 0, isPolling: false }
  }
}

// Import React for the hook
import React from 'react'
