'use client'

import { useEffect, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { CheckCircle, XCircle, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'

export default function PaymentStatus() {
    const searchParams = useSearchParams()
    const router = useRouter()
    const [status, setStatus] = useState<'loading' | 'success' | 'failure'>('loading')

    // PhonePe redirects with params like ?code=PAYMENT_SUCCESS&merchantId=...&transactionId=...
    const code = searchParams.get('code')
    const transactionId = searchParams.get('transactionId') || searchParams.get('merchantTransactionId')

    useEffect(() => {
        async function verify() {
            if (!transactionId) return;
            
            try {
                // Call our verification bridge which uses the backend SDK
                const response = await fetch('/api/payments/verify', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ transactionId })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    setStatus('success');
                    // Small delay before redirecting to dashboard
                    setTimeout(() => {
                        router.push('/dashboard?welcome=true');
                    }, 2000);
                } else {
                    setStatus('failure');
                }
            } catch (err) {
                console.error('Verification error:', err);
                setStatus('failure');
            }
        }

        if (code === 'PAYMENT_SUCCESS' || transactionId) {
            verify();
        } else if (code === 'PAYMENT_ERROR') {
            setStatus('failure');
        }
    }, [code, transactionId, router])

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
            <div className="bg-white p-8 rounded-lg shadow-lg max-w-md w-full text-center">
                {status === 'loading' && (
                    <>
                        <Loader2 className="w-16 h-16 text-blue-600 animate-spin mx-auto mb-4" />
                        <h2 className="text-2xl font-bold mb-2">Verifying Payment...</h2>
                        <p className="text-gray-600">Please do not close this window.</p>
                    </>
                )}

                {status === 'success' && (
                    <>
                        <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
                        <h2 className="text-2xl font-bold mb-2">Payment Successful!</h2>
                        <p className="text-gray-600 mb-6">Your workspace is ready. Redirecting...</p>
                        <Button onClick={() => router.push('/dashboard')} className="w-full bg-blue-600 text-white">
                            Go to Dashboard
                        </Button>
                    </>
                )}

                {status === 'failure' && (
                    <>
                        <XCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
                        <h2 className="text-2xl font-bold mb-2">Payment Failed</h2>
                        <p className="text-gray-600 mb-6">Something went wrong with the transaction.</p>
                        <Button onClick={() => router.push('/onboarding/payment')} variant="outline" className="w-full">
                            Try Again
                        </Button>
                    </>
                )}
            </div>
        </div>
    )
}
