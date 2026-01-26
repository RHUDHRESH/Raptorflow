'use client'

import { useEffect, useState, useCallback } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { CheckCircle, XCircle, Loader2, Mail, Sparkles } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'

export default function PaymentStatus() {
    const searchParams = useSearchParams()
    const router = useRouter()
    const [status, setStatus] = useState<'loading' | 'verifying' | 'success' | 'failure'>('loading')
    const [pollCount, setPollCount] = useState(0)
    const [error, setError] = useState<string | null>(null)

    // PhonePe redirects with params like ?code=PAYMENT_SUCCESS&merchantId=...&transactionId=...
    const code = searchParams.get('code')
    const transactionId = searchParams.get('transactionId') || searchParams.get('merchantTransactionId')

    const checkSubscriptionStatus = useCallback(async () => {
        try {
            const response = await fetch('/api/me/subscription')
            const data = await response.json()

            if (data.subscription_status === 'active') {
                setStatus('success')
                // Redirect based on onboarding status
                setTimeout(() => {
                    if (data.onboarding_status === 'active') {
                        router.push('/dashboard?welcome=true')
                    } else {
                        router.push('/onboarding')
                    }
                }, 3000)
                return true
            }
            return false
        } catch (err) {
            console.error('Error checking subscription:', err)
            return false
        }
    }, [router])

    useEffect(() => {
        async function verify() {
            if (!transactionId) {
                setError('No transaction ID found')
                setStatus('failure')
                return
            }

            setStatus('verifying')

            try {
                // Call verification endpoint
                const response = await fetch('/api/payments/verify', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ transactionId })
                })

                const data = await response.json()

                if (data.success) {
                    // Start polling for subscription activation
                    const isActive = await checkSubscriptionStatus()
                    if (!isActive) {
                        // Start polling every 2 seconds
                        setStatus('verifying')
                    }
                } else {
                    setError(data.error || 'Payment verification failed')
                    setStatus('failure')
                }
            } catch (err) {
                console.error('Verification error:', err)
                setError('Failed to verify payment. Please contact support.')
                setStatus('failure')
            }
        }

        if (code === 'PAYMENT_SUCCESS' || transactionId) {
            verify()
        } else if (code === 'PAYMENT_ERROR' || code === 'PAYMENT_DECLINED') {
            setError('Payment was declined or cancelled')
            setStatus('failure')
        }
    }, [code, transactionId, checkSubscriptionStatus])

    // Polling effect
    useEffect(() => {
        if (status !== 'verifying') return
        if (pollCount >= 30) { // Max 60 seconds of polling
            setError('Payment verification is taking longer than expected. Please check your email or contact support.')
            setStatus('failure')
            return
        }

        const timer = setTimeout(async () => {
            const isActive = await checkSubscriptionStatus()
            if (!isActive) {
                setPollCount(prev => prev + 1)
            }
        }, 2000)

        return () => clearTimeout(timer)
    }, [status, pollCount, checkSubscriptionStatus])

    return (
        <div className="min-h-screen flex items-center justify-center bg-[var(--canvas)] p-4">
            <Card className="max-w-md w-full">
                <CardContent className="pt-8 pb-8">
                    {(status === 'loading' || status === 'verifying') && (
                        <div className="text-center space-y-4">
                            <div className="relative inline-block">
                                <Loader2 className="w-16 h-16 text-primary animate-spin mx-auto" />
                                <div className="absolute inset-0 flex items-center justify-center">
                                    <Sparkles className="w-6 h-6 text-primary/50" />
                                </div>
                            </div>
                            <h2 className="text-2xl font-bold">
                                {status === 'loading' ? 'Processing...' : 'Activating Your Subscription...'}
                            </h2>
                            <p className="text-muted-foreground">
                                {status === 'verifying'
                                    ? 'This usually takes just a few seconds. Please don\'t close this window.'
                                    : 'Please wait while we verify your payment.'
                                }
                            </p>
                            {pollCount > 5 && (
                                <p className="text-sm text-muted-foreground">
                                    Still working... ({pollCount * 2}s)
                                </p>
                            )}
                        </div>
                    )}

                    {status === 'success' && (
                        <div className="text-center space-y-6">
                            <div className="relative inline-block">
                                <CheckCircle className="w-20 h-20 text-green-500 mx-auto" />
                            </div>
                            <div>
                                <h2 className="text-2xl font-bold text-green-700 mb-2">Payment Successful!</h2>
                                <p className="text-muted-foreground">
                                    Welcome to RaptorFlow! Your subscription is now active.
                                </p>
                            </div>

                            {/* Email confirmation notice */}
                            <div className="bg-blue-50 border border-blue-100 rounded-lg p-4 text-left">
                                <div className="flex items-start gap-3">
                                    <Mail className="w-5 h-5 text-blue-600 mt-0.5 shrink-0" />
                                    <div>
                                        <p className="text-sm font-medium text-blue-900">Check your email</p>
                                        <p className="text-sm text-blue-700">
                                            We've sent you a welcome email and payment confirmation with your invoice.
                                        </p>
                                    </div>
                                </div>
                            </div>

                            <p className="text-sm text-muted-foreground">
                                Redirecting you to complete setup...
                            </p>

                            <Button
                                onClick={() => router.push('/onboarding')}
                                className="w-full"
                                size="lg"
                            >
                                Continue to Setup
                            </Button>
                        </div>
                    )}

                    {status === 'failure' && (
                        <div className="text-center space-y-6">
                            <XCircle className="w-20 h-20 text-red-500 mx-auto" />
                            <div>
                                <h2 className="text-2xl font-bold text-red-700 mb-2">Payment Issue</h2>
                                <p className="text-muted-foreground">
                                    {error || 'Something went wrong with the transaction.'}
                                </p>
                            </div>

                            <div className="space-y-3">
                                <Button
                                    onClick={() => router.push('/onboarding/payment')}
                                    className="w-full"
                                    size="lg"
                                >
                                    Try Again
                                </Button>
                                <Button
                                    onClick={() => router.push('/onboarding/plans')}
                                    variant="outline"
                                    className="w-full"
                                >
                                    Change Plan
                                </Button>
                            </div>

                            <p className="text-sm text-muted-foreground">
                                Need help?{' '}
                                <a href="mailto:support@raptorflow.in" className="text-primary hover:underline">
                                    Contact Support
                                </a>
                            </p>
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    )
}
