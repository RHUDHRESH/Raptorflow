import { NextRequest, NextResponse } from 'next/server';
import crypto from 'crypto';
import { createClient } from '@supabase/supabase-js';

const SALT_INDEX = '1';

// Lazy client creation to avoid build-time errors
function getSupabase() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.NEXT_PUBLIC_SUPABASE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

  if (!url || !key) {
    throw new Error('Missing Supabase configuration');
  }

  return createClient(url, key);
}

export async function POST(request: NextRequest) {
  try {
    const SALT_KEY = process.env.NEXT_PUBLIC_PHONEPE_SALT_KEY || '099eb0cd-02cf-4e2a-8aca-3e6c6aff0399';
    const supabase = getSupabase();

    const formData = await request.formData();

    const response = formData.get('response') as string;
    const merchantTransactionId = formData.get('merchantTransactionId') as string;

    if (!response || !merchantTransactionId) {
      return NextResponse.redirect(new URL('/payment/failed', request.url));
    }

    // Verify checksum
    const checksumString = response + SALT_KEY;
    const sha256 = crypto.createHash('sha256').update(checksumString).digest('hex');
    const expectedChecksum = sha256 + '###' + SALT_INDEX;

    // Decode response
    const responseBuffer = Buffer.from(response, 'base64');
    const responseJson = JSON.parse(responseBuffer.toString());

    // Check payment status
    if (responseJson.code === 'PAYMENT_SUCCESS' && responseJson.data.merchantTransactionId === merchantTransactionId) {
      // Update user's subscription in database
      const { data: paymentData } = await supabase
        .from('payments')
        .select('*')
        .eq('transaction_id', merchantTransactionId)
        .single();

      if (paymentData) {
        // Update user profile with subscription
        const expiryDate = new Date();
        expiryDate.setMonth(expiryDate.getMonth() + 1); // 1 month from now

        await supabase
          .from('user_profiles')
          .update({
            subscription_plan: paymentData.plan_id,
            subscription_status: 'active',
            subscription_expires_at: expiryDate.toISOString(),
          })
          .eq('id', paymentData.user_id);

        // Update payment status
        await supabase
          .from('payments')
          .update({
            status: 'completed',
            verified_at: new Date().toISOString(),
          })
          .eq('transaction_id', merchantTransactionId);
      }

      return NextResponse.redirect(new URL('/payment/success', request.url));
    } else {
      return NextResponse.redirect(new URL('/payment/failed', request.url));
    }
  } catch (error) {
    console.error('Payment verification error:', error);
    return NextResponse.redirect(new URL('/payment/failed', request.url));
  }
}
