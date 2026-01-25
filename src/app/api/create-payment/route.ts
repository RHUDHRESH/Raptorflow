import { NextResponse } from 'next/server';

// Simple payment endpoint without backend dependency
export async function POST(request: Request) {
  try {
    const { planId, billingCycle } = await request.json();
    
    // Basic validation
    if (!planId || !billingCycle) {
      return NextResponse.json(
        { error: 'Plan ID and billing cycle are required' },
        { status: 400 }
      );
    }

    // Get current frontend URL from request headers or use default
    const baseUrl = request.headers.get('origin') || 'http://localhost:3001';
    
    // Mock payment response for testing
    const mockPaymentResponse = {
      paymentId: `pay_mock_${Date.now()}`,
      amount: billingCycle === 'monthly' ? 999 : 9990, // $9.99 or $99.90
      currency: 'USD',
      status: 'pending',
      redirectUrl: `${baseUrl}/payment/success?payment_id=pay_mock_${Date.now()}`,
      message: 'Mock payment created - backend payment processor not available'
    };

    return NextResponse.json({
      success: true,
      payment: mockPaymentResponse
    });

  } catch (error) {
    console.error('Payment creation error:', error);
    return NextResponse.json(
      { error: 'Failed to create payment' },
      { status: 500 }
    );
  }
}
