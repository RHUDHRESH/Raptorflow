import { NextResponse } from 'next/server'

// Mock payment completion endpoint
export async function POST(request: Request) {
  try {
    const { transactionId, phonePeTransactionId } = await request.json()

    // Simulate successful payment completion
    return NextResponse.json({
      status: 'success',
      message: 'Mock payment completed successfully!',
      paymentDetails: {
        transactionId,
        phonePeTransactionId,
        status: 'COMPLETED',
        amount: '₹3000',
        paymentMethod: 'PHONEPE_MOCK',
        completedAt: new Date().toISOString(),
        mockMode: true
      },
      nextSteps: [
        '✅ Mock payment completed',
        '💰 Funds credited (simulated)',
        '📋 Payment successful',
        '🎯 Test completed successfully'
      ]
    })
  } catch (error) {
    return NextResponse.json({
      status: 'error',
      message: 'Mock payment completion failed',
      error: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 })
  }
}
