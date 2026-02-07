import { NextRequest, NextResponse } from 'next/server';
import crypto from 'crypto';

const MERCHANT_ID = process.env.NEXT_PUBLIC_PHONEPE_MERCHANT_ID || 'PGTESTPAYUAT';
const SALT_KEY = process.env.NEXT_PUBLIC_PHONEPE_SALT_KEY || '099eb0cd-02cf-4e2a-8aca-3e6c6aff0399';
const SALT_INDEX = '1';
const ENV = process.env.NEXT_PUBLIC_PHONEPE_ENV || 'TEST';

export async function POST(request: NextRequest) {
  try {
    const { planId, amount, userId, email } = await request.json();

    // Generate transaction ID
    const transactionId = `TXN-${Date.now()}-${userId.slice(0, 8)}`;

    // Create payload
    const payload = {
      merchantId: MERCHANT_ID,
      merchantTransactionId: transactionId,
      merchantUserId: userId,
      amount: amount * 100, // Convert to paise
      redirectUrl: `${process.env.NEXTAUTH_URL || 'http://localhost:3000'}/api/payment/verify`,
      redirectMode: 'POST',
      callbackUrl: `${process.env.NEXTAUTH_URL || 'http://localhost:3000'}/api/payment/webhook`,
      mobileNumber: '9999999999',
      paymentInstrument: {
        type: 'PAY_PAGE',
      },
    };

    // Encode payload
    const payloadString = JSON.stringify(payload);
    const payloadBase64 = Buffer.from(payloadString).toString('base64');

    // Generate checksum
    const checksumString = payloadBase64 + '/pg/v1/pay' + SALT_KEY;
    const sha256 = crypto.createHash('sha256').update(checksumString).digest('hex');
    const checksum = sha256 + '###' + SALT_INDEX;

    // Create payment URL
    const apiUrl = ENV === 'PROD'
      ? 'https://api.phonepe.com/apis/hermes/pg/v1/pay'
      : 'https://api-preprod.phonepe.com/apis/pg-sandbox/pg/v1/pay';

    const paymentUrl = `${apiUrl}?${new URLSearchParams({
      request: payloadBase64,
    })}`;

    // Store transaction details in database (for verification)
    // This would typically go to your database
    console.log('Payment initiated:', {
      transactionId,
      userId,
      planId,
      amount,
      status: 'initiated',
    });

    return NextResponse.json({
      success: true,
      paymentUrl,
      transactionId,
    });
  } catch (error) {
    console.error('Payment creation error:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to create payment order' },
      { status: 500 }
    );
  }
}
