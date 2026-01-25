import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const { planSlug, billingCycle, userEmail, userId } = await request.json();

    // Validate required fields
    if (!planSlug || !billingCycle || !userEmail || !userId) {
      return NextResponse.json(
        { success: false, error: 'Missing required fields' },
        { status: 400 }
      );
    }

    // Mock payment order creation for now
    // In production, this would integrate with PhonePe or other payment provider
    const mockOrder = {
      orderId: `ORDER_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      amount: planSlug === 'ascent' ? 2900 : planSlug === 'glide' ? 7900 : 19900,
      currency: 'INR',
      planSlug,
      billingCycle,
      userEmail,
      userId,
      timestamp: new Date().toISOString()
    };

    // For now, return a mock checkout URL
    // In production, this would be the actual PhonePe payment URL
    const checkoutUrl = `/onboarding/payment?order=${mockOrder.orderId}`;

    return NextResponse.json({
      success: true,
      orderId: mockOrder.orderId,
      checkoutUrl,
      amount: mockOrder.amount,
      currency: mockOrder.currency
    });

  } catch (error) {
    console.error('Payment order creation error:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to create payment order' },
      { status: 500 }
    );
  }
}
