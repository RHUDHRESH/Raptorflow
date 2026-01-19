import { NextResponse } from 'next/server'

// Mock payment endpoint for testing 3k payments
export async function POST(request: Request) {
  try {
    const { amount = 30000, planId = 'custom-3k-test' } = await request.json()

    // Create mock successful payment response
    const transactionId = `MOCK_${Date.now()}_${Math.random().toString(36).substr(2, 6).toUpperCase()}`
    const phonePeTransactionId = `PY_${Date.now()}`
    
    // Mock payment URL (simulates PhonePe redirect)
    const mockPaymentUrl = `https://mock-phonepe.com/pay?id=${phonePeTransactionId}&amount=${amount}&callback=${encodeURIComponent(process.env.NEXT_PUBLIC_APP_URL + '/test-3k-payment')}`

    return NextResponse.json({
      status: 'success',
      message: 'Mock payment initiation test successful!',
      testResults: {
        transactionId,
        amount: amount / 100, // Convert to rupees for display
        phonePeTransactionId,
        paymentUrl: mockPaymentUrl,
        redirectMethod: 'REDIRECT',
        mockMode: true
      },
      nextSteps: [
        '✅ Mock payment initiation successful',
        '🔗 Mock payment URL generated',
        '💳 Ready to simulate payment flow',
        '📋 This is a TEST MODE payment',
        '🎯 Click the link to simulate payment completion'
      ],
      mockPaymentDetails: {
        mode: 'TEST_MODE',
        provider: 'MOCK_PHONEPE',
        amount: `₹${amount / 100}`,
        status: 'PENDING_PAYMENT',
        expiresIn: '15 minutes'
      }
    })
  } catch (error) {
    return NextResponse.json({
      status: 'error',
      message: 'Mock payment test failed',
      error: error instanceof Error ? error.message : 'Unknown error',
      troubleshooting: [
        '🔧 Check mock payment configuration',
        '🔧 Verify test parameters',
        '🔧 Check network connectivity',
        '🔧 Review error logs'
      ]
    }, { status: 500 })
  }
}
