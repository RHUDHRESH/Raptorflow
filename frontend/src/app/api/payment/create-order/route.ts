/**
 * ≡ƒÆ│ PAYMENT CREATE ORDER API
 * 
 * Creates a PhonePe payment order by calling the backend API.
 * Stores transaction details in Supabase for verification.
 */

import { NextRequest, NextResponse } from 'next/server';
import { getSupabaseAdmin } from '@/lib/supabase-admin';

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  const supabase = getSupabaseAdmin();
  try {
    const { planId, planName, amount, userId, email, redirectUrl } = await request.json();

    // Validate required fields
    if (!planId || !amount || !userId) {
      return NextResponse.json(
        { success: false, error: 'Missing required fields' },
        { status: 400 }
      );
    }

    // Generate transaction ID
    const transactionId = `RF-${Date.now()}-${userId.slice(0, 8)}`;

    // Store pending transaction in Supabase
    const { error: dbError } = await supabase
      .from('payment_transactions')
      .insert({
        transaction_id: transactionId,
        user_id: userId,
        plan_id: planId,
        plan_name: planName,
        amount: amount, // in paise
        status: 'pending',
        created_at: new Date().toISOString(),
      });

    if (dbError) {
      console.error('Failed to store transaction:', dbError);
      // Continue anyway - we can still process the payment
    }

    // Call backend API to initiate PhonePe payment
    try {
      const backendResponse = await fetch(`${BACKEND_URL}/api/payments/v2/initiate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          amount: amount, // in paise
          merchant_order_id: transactionId,
          redirect_url: redirectUrl || `${process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'}/payment/processing`,
          customer_email: email,
          customer_name: email?.split('@')[0],
          metadata: {
            plan_id: planId,
            plan_name: planName,
            user_id: userId,
          },
        }),
      });

      const backendData = await backendResponse.json();

      if (backendData.success && backendData.checkout_url) {
        return NextResponse.json({
          success: true,
          paymentUrl: backendData.checkout_url,
          checkoutUrl: backendData.checkout_url,
          transactionId: transactionId,
          orderId: backendData.order_id,
        });
      }

      // Backend failed, fall back to direct PhonePe integration
      console.warn('Backend payment API failed, using fallback:', backendData.error);
    } catch (backendError) {
      console.warn('Backend payment API unavailable, using fallback:', backendError);
    }

    // Fallback: Direct PhonePe integration (for development/testing)
    const MERCHANT_ID = process.env.PHONEPE_MERCHANT_ID || 'PGTESTPAYUAT';
    const SALT_KEY = process.env.PHONEPE_SALT_KEY || '099eb0cd-02cf-4e2a-8aca-3e6c6aff0399';
    const SALT_INDEX = '1';
    const ENV = process.env.PHONEPE_ENV || 'UAT';

    const crypto = await import('crypto');

    const payload = {
      merchantId: MERCHANT_ID,
      merchantTransactionId: transactionId,
      merchantUserId: userId,
      amount: amount,
      redirectUrl: redirectUrl || `${process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'}/payment/processing?transactionId=${transactionId}`,
      redirectMode: 'REDIRECT',
      callbackUrl: `${process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'}/api/payment/webhook`,
      paymentInstrument: {
        type: 'PAY_PAGE',
      },
    };

    const payloadString = JSON.stringify(payload);
    const payloadBase64 = Buffer.from(payloadString).toString('base64');
    const checksumString = payloadBase64 + '/pg/v1/pay' + SALT_KEY;
    const sha256 = crypto.createHash('sha256').update(checksumString).digest('hex');
    const checksum = sha256 + '###' + SALT_INDEX;

    const apiUrl = ENV === 'PRODUCTION'
      ? 'https://api.phonepe.com/apis/hermes/pg/v1/pay'
      : 'https://api-preprod.phonepe.com/apis/pg-sandbox/pg/v1/pay';

    // Make request to PhonePe
    const phonepeResponse = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-VERIFY': checksum,
      },
      body: JSON.stringify({ request: payloadBase64 }),
    });

    const phonepeData = await phonepeResponse.json();

    if (phonepeData.success && phonepeData.data?.instrumentResponse?.redirectInfo?.url) {
      return NextResponse.json({
        success: true,
        paymentUrl: phonepeData.data.instrumentResponse.redirectInfo.url,
        checkoutUrl: phonepeData.data.instrumentResponse.redirectInfo.url,
        transactionId: transactionId,
      });
    }

    // If PhonePe API also fails, return error
    console.error('PhonePe API error:', phonepeData);
    return NextResponse.json({
      success: false,
      error: phonepeData.message || 'Payment initiation failed',
    }, { status: 500 });

  } catch (error) {
    console.error('Payment creation error:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to create payment order' },
      { status: 500 }
    );
  }
}

