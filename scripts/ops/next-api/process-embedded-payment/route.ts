import { NextResponse } from 'next/server'

// Process embedded payment completion
export async function POST(request: Request) {
  try {
    const { transactionId, paymentMethod = 'UPI' } = await request.json()

    // Simulate payment processing
    await new Promise(resolve => setTimeout(resolve, 2000)) // 2 second processing

    // Random success for demo (in real would verify with payment gateway)
    const isSuccess = Math.random() > 0.1 // 90% success rate

    if (isSuccess) {
      return NextResponse.json({
        status: 'success',
        message: 'Payment completed successfully!',
        paymentDetails: {
          transactionId,
          amount: 3000,
          status: 'COMPLETED',
          paymentMethod,
          completedAt: new Date().toISOString(),
          transactionRef: `TXN${Date.now()}`,
          embeddedMode: true
        },
        receipt: {
          id: `RCP${Date.now()}`,
          date: new Date().toLocaleDateString(),
          time: new Date().toLocaleTimeString(),
          amount: '₹3000',
          method: paymentMethod,
          status: 'SUCCESS'
        }
      })
    } else {
      return NextResponse.json({
        status: 'error',
        message: 'Payment failed',
        error: 'Transaction could not be completed'
      }, { status: 400 })
    }
  } catch (error) {
    return NextResponse.json({
      status: 'error',
      message: 'Payment processing failed',
      error: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 })
  }
}
