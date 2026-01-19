/**
 * 🎯 PHONEPE WEBHOOK HANDLER
 * Processes payment callbacks from PhonePe
 * Updates subscription status and triggers onboarding
 */

import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';
import { headers } from 'next/headers';

// Initialize Supabase client
const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

// Verify PhonePe webhook signature
function verifyPhonePeSignature(payload: string, signature: string, salt: string): boolean {
  const crypto = require('crypto');
  const expectedSignature = crypto
    .createHmac('sha256', salt)
    .update(payload)
    .digest('base64');

  return signature === expectedSignature;
}

export async function POST(request: NextRequest) {
  try {
    // Get PhonePe webhook headers
    const headersList = await headers();
    const xVerify = headersList.get('X-VERIFY') as string;
    const xWebhookTimestamp = headersList.get('X-WEBHOOK-TIMESTAMP') as string;

    // Get raw request body
    const body = await request.text();

    if (!xVerify || !body) {
      console.error('Missing webhook headers or body');
      return NextResponse.json(
        { error: 'Invalid webhook request' },
        { status: 400 }
      );
    }

    // Verify webhook signature
    const salt = process.env.PHONEPE_SALT || 'default_salt';
    const payload = body + xWebhookTimestamp + salt;

    if (!verifyPhonePeSignature(payload, xVerify, salt)) {
      console.error('Invalid webhook signature');
      return NextResponse.json(
        { error: 'Invalid signature' },
        { status: 401 }
      );
    }

    const webhookData = JSON.parse(body);
    console.log('PhonePe webhook received:', webhookData);

    // Extract transaction details
    const {
      code,
      merchantTransactionId,
      transactionId,
      amount,
      providerReferenceId,
      data
    } = webhookData;

    // Find the transaction record
    const { data: transaction, error: transactionError } = await supabase
      .from('payment_transactions')
      .select('*')
      .eq('merchant_transaction_id', merchantTransactionId)
      .single();

    if (transactionError || !transaction) {
      console.error('Transaction not found:', transactionError);
      return NextResponse.json(
        { error: 'Transaction not found' },
        { status: 404 }
      );
    }

    // Update transaction status based on PhonePe response
    let newStatus = 'FAILED';
    if (code === 'PAYMENT_SUCCESS') {
      newStatus = 'COMPLETED';
    } else if (code === 'PAYMENT_PENDING') {
      newStatus = 'PENDING';
    }

    // Update transaction with PhonePe details
    const { data: updatedTransaction, error: updateError } = await supabase
      .from('payment_transactions')
      .update({
        status: newStatus,
        phonepe_transaction_id: transactionId,
        payment_instrument: data?.paymentInstrument,
        gateway_response: webhookData,
        completed_at: newStatus === 'COMPLETED' ? new Date().toISOString() : null
      })
      .eq('id', transaction.id)
      .select()
      .single();

    if (updateError || !updatedTransaction) {
      console.error('Failed to update transaction:', updateError);
      return NextResponse.json(
        { error: 'Failed to update transaction' },
        { status: 500 }
      );
    }

    // If payment successful, create user subscription
    if (newStatus === 'COMPLETED') {
      const metadata = transaction.metadata as any;
      const { plan_slug, billing_cycle, user_id } = metadata;

      if (plan_slug && billing_cycle && user_id) {
        try {
          // Call the subscription creation function
          const { data: subscription, error: subscriptionError } = await supabase
            .rpc('create_user_subscription', {
              p_user_id: user_id,
              p_plan_slug: plan_slug,
              p_billing_cycle: billing_cycle,
              p_phonepe_order_id: transaction.merchant_order_id,
              p_amount_paid: amount
            });

          if (subscriptionError) {
            console.error('Failed to create subscription:', subscriptionError);
            // Don't fail the webhook response, but log the error
          } else {
            console.log('Subscription created successfully:', subscription);

            // Log subscription event
            await supabase
              .from('subscription_events')
              .insert({
                user_id: user_id,
                subscription_id: subscription.id,
                event_type: 'created',
                event_data: {
                  payment_transaction_id: transaction.id,
                  phonepe_transaction_id: transactionId,
                  plan_slug,
                  billing_cycle,
                  amount
                }
              });
          }
        } catch (subscriptionError) {
          console.error('Error creating subscription:', subscriptionError);
        }
      }
    }

    // Log webhook event
    await supabase
      .from('payment_webhook_logs')
      .insert({
        webhook_id: `WH_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        transaction_id: transaction.transaction_id,
        callback_type: 'PHONEPE_PAYMENT_STATUS',
        authorization_header: xVerify,
        request_body: webhookData,
        processed: true,
        received_at: new Date().toISOString(),
        processed_at: new Date().toISOString()
      });

    // Return success response to PhonePe
    return NextResponse.json({
      success: true,
      code: 'WEBHOOK_PROCESSED'
    });

  } catch (error) {
    console.error('Webhook processing error:', error);
    return NextResponse.json(
      { error: 'Webhook processing failed' },
      { status: 500 }
    );
  }
}
