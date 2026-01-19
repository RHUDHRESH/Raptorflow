/**
 * 🚀 CREATE PAYMENT ORDER API
 * Integrates with PhonePe SDK for payment processing
 * Handles plan selection and order creation
 */

import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

// Initialize Supabase client
const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

// Plan configuration (matches database)
const PLANS = {
  ascent: {
    name: 'Ascent',
    price_monthly: 2900, // ₹29 in paise
    price_annual: 24000, // ₹240 in paise
    slug: 'ascent'
  },
  glide: {
    name: 'Glide', 
    price_monthly: 7900, // ₹79 in paise
    price_annual: 66000, // ₹660 in paise
    slug: 'glide'
  },
  soar: {
    name: 'Soar',
    price_monthly: 19900, // ₹199 in paise  
    price_annual: 166000, // ₹1660 in paise
    slug: 'soar'
  }
};

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { planSlug, billingCycle = 'monthly', userEmail, userId } = body;

    // Validate input
    if (!planSlug || !userEmail || !userId) {
      return NextResponse.json(
        { error: 'Missing required fields: planSlug, userEmail, userId' },
        { status: 400 }
      );
    }

    // Validate plan
    const plan = PLANS[planSlug as keyof typeof PLANS];
    if (!plan) {
      return NextResponse.json(
        { error: 'Invalid plan selected' },
        { status: 400 }
      );
    }

    // Calculate amount based on billing cycle
    const amount = billingCycle === 'annual' ? plan.price_annual : plan.price_monthly;

    // Generate unique order IDs
    const merchantOrderId = `RF_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const merchantTransactionId = `RF_TXN_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    // Create payment transaction record
    const { data: transaction, error: transactionError } = await supabase
      .from('payment_transactions')
      .insert({
        transaction_id: merchantTransactionId,
        merchant_order_id: merchantOrderId,
        merchant_transaction_id: merchantTransactionId,
        amount: amount,
        currency: 'INR',
        customer_id: userId,
        customer_name: userEmail.split('@')[0],
        customer_email: userEmail,
        customer_mobile: null,
        redirect_url: `${process.env.NEXT_PUBLIC_APP_URL}/payment/success`,
        callback_url: `${process.env.NEXT_PUBLIC_APP_URL}/api/payments/webhook`,
        metadata: {
          plan_slug: planSlug,
          billing_cycle: billingCycle,
          user_id: userId,
          plan_name: plan.name
        },
        status: 'INITIATED'
      })
      .select()
      .single();

    if (transactionError || !transaction) {
      console.error('Failed to create transaction:', transactionError);
      return NextResponse.json(
        { error: 'Failed to create payment transaction' },
        { status: 500 }
      );
    }

    // Call PhonePe SDK to create payment order
    try {
      const phonepeResponse = await fetch(`${process.env.BACKEND_URL}/api/v1/payments/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          merchantOrderId: merchantOrderId,
          merchantTransactionId: merchantTransactionId,
          amount: amount,
          customerInfo: {
            customerId: userId,
            customerName: userEmail.split('@')[0],
            customerEmail: userEmail,
          },
          redirectUrl: `${process.env.NEXT_PUBLIC_APP_URL}/payment/success`,
          callbackUrl: `${process.env.NEXT_PUBLIC_APP_URL}/api/payments/webhook`,
          paymentInstrument: {
            type: 'PAY_PAGE',
            targetApp: 'PHONEPE'
          },
          metadata: {
            plan_slug: planSlug,
            billing_cycle: billingCycle,
            user_id: userId,
            plan_name: plan.name
          }
        })
      });

      const phonepeData = await phonepeResponse.json();

      if (!phonepeResponse.ok || phonepeData.error) {
        // Update transaction status to failed
        await supabase
          .from('payment_transactions')
          .update({ status: 'FAILED' })
          .eq('id', transaction.id);

        return NextResponse.json(
          { error: phonepeData.error || 'Failed to create PhonePe order' },
          { status: 500 }
        );
      }

      // Update transaction with PhonePe details
      await supabase
        .from('payment_transactions')
        .update({
          phonepe_transaction_id: phonepeData.transactionId,
          checkout_url: phonepeData.checkoutUrl,
          payment_instrument: phonepeData.paymentInstrument
        })
        .eq('id', transaction.id);

      return NextResponse.json({
        success: true,
        orderId: merchantOrderId,
        transactionId: merchantTransactionId,
        checkoutUrl: phonepeData.checkoutUrl,
        amount: amount,
        plan: {
          name: plan.name,
          slug: plan.slug,
          billingCycle,
          price: billingCycle === 'annual' ? plan.price_annual / 100 : plan.price_monthly / 100
        }
      });

    } catch (phonepeError) {
      console.error('PhonePe API error:', phonepeError);
      
      // Update transaction status to failed
      await supabase
        .from('payment_transactions')
        .update({ status: 'FAILED' })
        .eq('id', transaction.id);

      return NextResponse.json(
        { error: 'Payment gateway error' },
        { status: 500 }
      );
    }

  } catch (error) {
    console.error('Create order error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
