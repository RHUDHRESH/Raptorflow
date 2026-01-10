import { NextRequest, NextResponse } from 'next/server';
import crypto from 'crypto';
import { createClient } from '@supabase/supabase-js';

const SALT_KEY = process.env.NEXT_PUBLIC_PHONEPE_SALT_KEY || '099eb0cd-02cf-4e2a-8aca-3e6c6aff0399';
const SALT_INDEX = '1';

// Initialize Supabase
const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

export async function POST(request: NextRequest) {
  try {
    const body = await request.text();
    const headers = request.headers;

    // Get checksum from headers
    const checksum = headers.get('x-verify') || headers.get('X-VERIFY');

    if (!checksum) {
      console.error('Missing checksum header');
      return NextResponse.json({ error: 'Missing checksum' }, { status: 400 });
    }

    // Verify checksum
    const expectedChecksum = crypto
      .createHash('sha256')
      .update(body + SALT_KEY)
      .digest('hex') + '###' + SALT_INDEX;

    if (checksum !== expectedChecksum) {
      console.error('Invalid checksum');
      return NextResponse.json({ error: 'Invalid checksum' }, { status: 400 });
    }

    // Parse webhook body
    const webhookData = JSON.parse(body);

    // Extract payment details
    const {
      code,
      data: {
        merchantTransactionId,
        transactionId,
        amount,
        state
      }
    } = webhookData;

    // Find the payment record
    const { data: payment, error: paymentError } = await supabase
      .from('payments')
      .select('*')
      .eq('transaction_id', merchantTransactionId)
      .single();

    if (paymentError || !payment) {
      console.error('Payment not found:', merchantTransactionId);
      return NextResponse.json({ error: 'Payment not found' }, { status: 404 });
    }

    // Update payment status based on webhook
    let status = 'failed';
    let subscriptionStatus = null;
    let subscriptionExpiresAt = null;

    if (code === 'PAYMENT_SUCCESS' && state === 'COMPLETED') {
      status = 'completed';
      subscriptionStatus = 'active';

      // Set subscription expiry to 30 days from now
      const expiryDate = new Date();
      expiryDate.setDate(expiryDate.getDate() + 30);
      subscriptionExpiresAt = expiryDate.toISOString();
    }

    // Update payment record
    await supabase
      .from('payments')
      .update({
        status,
        verified_at: new Date().toISOString(),
      })
      .eq('id', payment.id);

    // Update user subscription if payment was successful
    if (status === 'completed') {
      await supabase
        .from('user_profiles')
        .update({
          subscription_plan: payment.plan_id,
          subscription_status: subscriptionStatus,
          subscription_expires_at: subscriptionExpiresAt,
        })
        .eq('id', payment.user_id);

      console.log(`Subscription activated for user ${payment.user_id}, plan: ${payment.plan_id}`);
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Webhook error:', error);
    return NextResponse.json(
      { success: false, error: 'Webhook processing failed' },
      { status: 500 }
    );
  }
}
