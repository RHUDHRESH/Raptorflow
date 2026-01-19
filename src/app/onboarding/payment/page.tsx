'use client'

import { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { CreditCard, Shield, CheckCircle, AlertCircle, Smartphone, Loader2 } from 'lucide-react'

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
        router.push('/onboarding/plans')
      }
    } catch (err) {
      setError('Failed to load plan details')
    } finally {
      setIsLoading(false)
    }
  }

  async function verifyPayment(transactionId: string) {
    try {
      const response = await fetch('/api/payments/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ transactionId }),
      })

      const data = await response.json()

      if (data.success) {
        router.push('/dashboard?welcome=true')
      } else {
        setError(data.error || 'Payment verification failed')
        setIsLoading(false)
      }
    } catch (err) {
      setError('Payment verification failed')
      setIsLoading(false)
    }
  }

  async function initiatePayment() {
    setIsProcessing(true)
    setError('')

    try {
      const response = await fetch('/api/create-payment', {
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

      if (data.url) {
        window.location.href = data.url
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
      <div className="space-y-6">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center space-y-4">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-primary/10 rounded-full">
                <Loader2 className="w-8 h-8 text-primary animate-spin" />
              </div>
              <h1 className="text-2xl font-bold">Loading Payment Details</h1>
              <p className="text-muted-foreground">Please wait while we prepare your payment...</p>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-primary/10 rounded-full mb-4">
          <CreditCard className="w-8 h-8 text-primary" />
        </div>
        <h1 className="text-3xl font-bold">Complete Your Purchase</h1>
        <p className="text-muted-foreground max-w-md mx-auto">
          Secure payment powered by PhonePe. Your subscription starts immediately after payment.
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        {/* Order Summary */}
        <div className="md:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Order Summary</CardTitle>
              <CardDescription>Review your subscription details</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Plan Details */}
              <div className="flex items-center justify-between p-4 bg-muted/50 rounded-lg">
                <div>
                  <h3 className="font-semibold text-lg">{selectedPlan?.plan.name} Plan</h3>
                  <p className="text-sm text-muted-foreground capitalize">
                    {selectedPlan?.billingCycle} Billing
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold">{formatPrice(getPrice())}</p>
                  <p className="text-sm text-muted-foreground">
                    {formatPrice(getMonthlyEquivalent())}/month
                  </p>
                </div>
              </div>

              {/* Features */}
              <div>
                <h4 className="font-medium mb-3">What's included:</h4>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-primary" />
                    Full access to all platform features
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-primary" />
                    Priority customer support
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-primary" />
                    Cancel anytime
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-primary" />
                    30-day money-back guarantee
                  </li>
                </ul>
              </div>

              <Separator />

              {/* Total */}
              <div className="flex justify-between items-center">
                <span className="text-lg font-semibold">Total</span>
                <span className="text-2xl font-bold">{formatPrice(getPrice())}</span>
              </div>

              {/* Payment Button */}
              <Button
                onClick={initiatePayment}
                disabled={isProcessing}
                size="lg"
                className="w-full"
              >
                {isProcessing ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Redirecting to PhonePe...
                  </>
                ) : (
                  <>
                    <Smartphone className="mr-2 h-4 w-4" />
                    Pay {formatPrice(getPrice())} with PhonePe
                  </>
                )}
              </Button>

              {/* Back Button */}
              <Button
                onClick={() => router.push('/onboarding/plans')}
                variant="outline"
                className="w-full"
              >
                Change Plan
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Trust & Security */}
        <div className="space-y-6">
          {/* Security Badge */}
          <Card>
            <CardContent className="pt-6">
              <div className="text-center space-y-4">
                <Shield className="w-12 h-12 text-primary mx-auto" />
                <h3 className="font-semibold">Secure Payment</h3>
                <p className="text-sm text-muted-foreground">
                  Your payment information is encrypted and secure. We never store your card details.
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Payment Methods */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Payment Methods</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center gap-3 p-2">
                  <div className="w-10 h-10 bg-primary/10 rounded flex items-center justify-center">
                    <Smartphone className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <p className="font-medium text-sm">PhonePe</p>
                    <p className="text-xs text-muted-foreground">UPI, Cards, Wallets</p>
                  </div>
                  <Badge variant="secondary" className="ml-auto">Recommended</Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Support */}
          <Card>
            <CardContent className="pt-6">
              <div className="text-center space-y-2">
                <h4 className="font-medium">Need Help?</h4>
                <p className="text-sm text-muted-foreground">
                  Our support team is here to assist you
                </p>
                <Button variant="link" className="p-0 h-auto">
                  Contact Support
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Error */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Terms */}
      <p className="text-center text-xs text-muted-foreground">
        By completing this purchase, you agree to our{' '}
        <Link href="/terms" className="text-primary hover:underline">Terms of Service</Link> and{' '}
        <Link href="/privacy" className="text-primary hover:underline">Privacy Policy</Link>.
      </p>
    </div>
  )
}
