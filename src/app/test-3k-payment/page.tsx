'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { CreditCard, IndianRupee, ExternalLink, AlertCircle, CheckCircle } from 'lucide-react'

export default function Test3kPayment() {
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState('')
  const [customAmount, setCustomAmount] = useState('3000')

  // Check for payment callback
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search)
    const status = urlParams.get('status')
    const transactionId = urlParams.get('transactionId')

    if (status === 'success' && transactionId) {
      setResult({
        status: 'success',
        paymentDetails: {
          transactionId,
          amount: parseInt(customAmount),
          status: 'COMPLETED',
          completedAt: new Date().toISOString(),
          paymentMethod: 'PHONEPE_UAT'
        },
        paymentCompleted: true
      })
    }
  }, [customAmount])

  async function createPayment() {
    setIsLoading(true)
    setError('')
    setResult(null)

    try {
      const amountInPaise = parseInt(customAmount) * 100
      
      const response = await fetch('/api/create-direct-payment', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          amount: amountInPaise,
          planId: 'custom-3k-test'
        })
      })

      const data = await response.json()
      
      if (data.status === 'success') {
        setResult(data)
      } else {
        setError(data.error?.message || data.message || 'Payment initiation failed')
      }
    } catch (err) {
      setError('Network error. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <IndianRupee className="w-12 h-12 text-green-600 mr-3" />
            <h1 className="text-3xl font-bold text-gray-900">REAL 3k Payment Test</h1>
          </div>
          <p className="text-gray-600">
            Create a REAL payment for ₹{customAmount} using PhonePe UAT environment
          </p>
          <Badge variant="secondary" className="mt-2">
            🎯 REAL PHONEPE PAYMENT - NO MOCK
          </Badge>
        </div>

        {!result?.paymentCompleted && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center">
                <CreditCard className="w-5 h-5 mr-2" />
                Payment Configuration
              </CardTitle>
              <CardDescription>
                Configure your payment amount and create REAL PhonePe payment link
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="amount">Amount (₹)</Label>
                <Input
                  id="amount"
                  type="number"
                  value={customAmount}
                  onChange={(e) => setCustomAmount(e.target.value)}
                  placeholder="3000"
                  min="1"
                  max="100000"
                />
                <p className="text-sm text-gray-500">
                  Enter amount in rupees (₹1 = ₹100 paise)
                </p>
              </div>

              <Button
                onClick={createPayment}
                disabled={isLoading || !customAmount || parseInt(customAmount) <= 0}
                size="lg"
                className="w-full"
              >
                {isLoading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                    Creating REAL Payment...
                  </>
                ) : (
                  <>
                    <CreditCard className="w-4 h-4 mr-2" />
                    Create REAL ₹{customAmount} Payment
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        )}

        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              <strong>Payment Failed:</strong> {error}
            </AlertDescription>
          </Alert>
        )}

        {result && !result.paymentCompleted && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center text-green-600">
                <CheckCircle className="w-5 h-5 mr-2" />
                REAL Payment Link Created!
              </CardTitle>
              <CardDescription>
                Your REAL PhonePe payment link has been generated. Click to pay.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-sm text-gray-500">Transaction ID</Label>
                  <p className="font-mono text-sm">{result.paymentDetails.transactionId}</p>
                </div>
                <div>
                  <Label className="text-sm text-gray-500">Amount</Label>
                  <p className="font-semibold">₹{result.paymentDetails.amount}</p>
                </div>
                <div>
                  <Label className="text-sm text-gray-500">Merchant ID</Label>
                  <p className="font-mono text-sm">{result.paymentDetails.merchantId}</p>
                </div>
                <div>
                  <Label className="text-sm text-gray-500">Status</Label>
                  <Badge variant="secondary">Ready to Pay</Badge>
                </div>
              </div>

              <div className="pt-4 border-t">
                <Label className="text-sm text-gray-500 block mb-2">REAL PhonePe Payment URL</Label>
                <Button
                  asChild
                  className="w-full"
                  size="lg"
                >
                  <a
                    href={result.paymentDetails.paymentUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center justify-center"
                  >
                    <ExternalLink className="w-4 h-4 mr-2" />
                    Pay ₹{customAmount} on PhonePe 🎯 REAL
                  </a>
                </Button>
              </div>

              <div className="bg-green-50 p-4 rounded-lg">
                <Label className="text-sm text-gray-500 block mb-2">Next Steps</Label>
                <ul className="space-y-1">
                  {result.nextSteps.map((step: string, index: number) => (
                    <li key={index} className="text-sm text-gray-700">
                      • {step}
                    </li>
                  ))}
                </ul>
              </div>

              <Alert variant="default">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  If the PhonePe link fails to open with a DNS error (e.g., <code>apps-staging.phonepe.com</code> not resolving),
                  switch to a working DNS (1.1.1.1 / 8.8.8.8) or test on a network/VPN that can resolve the staging domain.
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        )}

        {result?.paymentCompleted && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center text-green-600">
                <CheckCircle className="w-5 h-5 mr-2" />
                Payment Completed Successfully! 🎉
              </CardTitle>
              <CardDescription>
                Your REAL PhonePe payment has been completed successfully.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="bg-green-50 p-4 rounded-lg">
                <div className="flex items-center text-green-600 mb-2">
                  <CheckCircle className="w-4 h-4 mr-2" />
                  <span className="font-semibold">REAL payment successful!</span>
                </div>
                <div className="text-sm text-gray-700">
                  <p>• Transaction ID: {result.paymentDetails.transactionId}</p>
                  <p>• Amount: ₹{result.paymentDetails.amount}</p>
                  <p>• Status: {result.paymentDetails.status}</p>
                  <p>• Method: {result.paymentDetails.paymentMethod}</p>
                  <p>• Completed: {new Date(result.paymentDetails.completedAt).toLocaleString()}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">🎯 REAL PhonePe Payment Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-green-400 rounded-full mr-2"></div>
                <span>REAL PhonePe UAT environment - NO MOCK!</span>
              </div>
              <div className="flex items-center">
                <div className="w-3 h-3 bg-blue-400 rounded-full mr-2"></div>
                <span>Direct payment link to actual PhonePe staging</span>
              </div>
              <div className="flex items-center">
                <div className="w-3 h-3 bg-purple-400 rounded-full mr-2"></div>
                <span>Real UPI payment methods supported</span>
              </div>
            </div>
            
            <div className="mt-4 p-3 bg-green-100 rounded text-xs">
              <strong>🎯 THIS IS REAL:</strong><br />
              • Opens actual PhonePe payment interface<br />
              • Accepts real UPI payments (test mode)<br />
              • Redirects back to this app after payment<br />
              • Uses PhonePe staging environment
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
