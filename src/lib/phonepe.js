/**
 * PhonePe Payment Gateway Integration
 * 
 * This module handles PhonePe payment integration for Raptorflow
 * Documentation: https://developer.phonepe.com/v1/docs
 */

import { supabase } from './supabase'

// PhonePe Configuration (set these in .env)
const PHONEPE_MERCHANT_ID = import.meta.env.VITE_PHONEPE_MERCHANT_ID || ''
const PHONEPE_SALT_KEY = import.meta.env.VITE_PHONEPE_SALT_KEY || ''
const PHONEPE_SALT_INDEX = import.meta.env.VITE_PHONEPE_SALT_INDEX || '1'
const PHONEPE_ENV = import.meta.env.VITE_PHONEPE_ENV || 'SANDBOX' // SANDBOX or PRODUCTION

// PhonePe API URLs
const PHONEPE_API_URL = PHONEPE_ENV === 'PRODUCTION' 
  ? 'https://api.phonepe.com/apis/hermes'
  : 'https://api-preprod.phonepe.com/apis/pg-sandbox'

// Plan prices in paise (INR smallest unit)
export const PLAN_PRICES = {
  ascent: { price: 500000, name: 'Ascent', priceDisplay: '₹5,000' },
  glide: { price: 700000, name: 'Glide', priceDisplay: '₹7,000' },
  soar: { price: 1000000, name: 'Soar', priceDisplay: '₹10,000' },
}

/**
 * Generate a unique merchant transaction ID
 */
export const generateTransactionId = () => {
  return `RF_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`
}

/**
 * Create SHA256 hash for PhonePe checksum
 * Note: In production, this should be done on the server side
 */
const createChecksum = async (payload, saltKey, saltIndex) => {
  const encoder = new TextEncoder()
  const data = encoder.encode(payload + '/pg/v1/pay' + saltKey)
  const hashBuffer = await crypto.subtle.digest('SHA-256', data)
  const hashArray = Array.from(new Uint8Array(hashBuffer))
  const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('')
  return hashHex + '###' + saltIndex
}

/**
 * Initialize a PhonePe payment
 * @param {Object} options - Payment options
 * @param {string} options.userId - User ID from Supabase
 * @param {string} options.plan - Plan name (ascent, glide, soar)
 * @param {string} options.userEmail - User email
 * @param {string} options.userPhone - User phone (optional)
 */
export const initiatePayment = async ({ userId, plan, userEmail, userPhone }) => {
  try {
    const planInfo = PLAN_PRICES[plan]
    if (!planInfo) {
      throw new Error('Invalid plan selected')
    }

    const merchantTransactionId = generateTransactionId()
    const amount = planInfo.price // in paise

    // Create payment record in database
    const { data: paymentRecord, error: dbError } = await supabase
      .from('payments')
      .insert({
        user_id: userId,
        amount: amount,
        plan: plan,
        phonepe_merchant_transaction_id: merchantTransactionId,
        status: 'initiated',
      })
      .select()
      .single()

    if (dbError) {
      throw new Error('Failed to create payment record: ' + dbError.message)
    }

    // Prepare PhonePe payload
    const payload = {
      merchantId: PHONEPE_MERCHANT_ID,
      merchantTransactionId: merchantTransactionId,
      merchantUserId: userId,
      amount: amount,
      redirectUrl: `${window.location.origin}/payment/callback?txnId=${merchantTransactionId}`,
      redirectMode: 'REDIRECT',
      callbackUrl: `${window.location.origin}/api/phonepe/callback`, // Server-side callback
      mobileNumber: userPhone || '',
      paymentInstrument: {
        type: 'PAY_PAGE',
      },
    }

    // Base64 encode payload
    const base64Payload = btoa(JSON.stringify(payload))
    
    // Create checksum (Note: In production, do this server-side)
    const checksum = await createChecksum(base64Payload, PHONEPE_SALT_KEY, PHONEPE_SALT_INDEX)

    // In a real implementation, you would:
    // 1. Send this to your backend
    // 2. Backend makes the PhonePe API call
    // 3. Backend returns the payment URL
    // 4. Redirect user to payment URL

    // For demo purposes, we'll simulate a payment flow
    console.log('Payment initiated:', {
      merchantTransactionId,
      amount: planInfo.priceDisplay,
      plan: planInfo.name,
    })

    return {
      success: true,
      merchantTransactionId,
      paymentId: paymentRecord.id,
      // In production, this would be the PhonePe payment URL
      redirectUrl: `/payment/process?txnId=${merchantTransactionId}&plan=${plan}`,
    }

  } catch (error) {
    console.error('Payment initiation failed:', error)
    return {
      success: false,
      error: error.message,
    }
  }
}

/**
 * Check payment status
 * @param {string} merchantTransactionId - Transaction ID to check
 */
export const checkPaymentStatus = async (merchantTransactionId) => {
  try {
    // In production, this would call PhonePe's status API
    // For now, we'll check our database
    const { data, error } = await supabase
      .from('payments')
      .select('*')
      .eq('phonepe_merchant_transaction_id', merchantTransactionId)
      .single()

    if (error) {
      throw new Error('Payment not found')
    }

    return {
      success: true,
      payment: data,
    }

  } catch (error) {
    console.error('Status check failed:', error)
    return {
      success: false,
      error: error.message,
    }
  }
}

/**
 * Process successful payment (called after PhonePe callback)
 * @param {string} merchantTransactionId - Transaction ID
 * @param {Object} phonepeResponse - Response from PhonePe
 */
export const processSuccessfulPayment = async (merchantTransactionId, phonepeResponse) => {
  try {
    // Get payment record
    const { data: payment, error: fetchError } = await supabase
      .from('payments')
      .select('*')
      .eq('phonepe_merchant_transaction_id', merchantTransactionId)
      .single()

    if (fetchError || !payment) {
      throw new Error('Payment record not found')
    }

    // Update payment record
    const { error: updateError } = await supabase
      .from('payments')
      .update({
        status: 'success',
        phonepe_transaction_id: phonepeResponse?.transactionId,
        phonepe_payment_instrument_type: phonepeResponse?.paymentInstrument?.type,
        completed_at: new Date().toISOString(),
        response_code: phonepeResponse?.code,
        response_message: phonepeResponse?.message,
        raw_response: phonepeResponse,
      })
      .eq('id', payment.id)

    if (updateError) {
      throw new Error('Failed to update payment record')
    }

    // Activate user's plan
    const { error: rpcError } = await supabase.rpc('activate_plan', {
      p_user_id: payment.user_id,
      p_plan: payment.plan,
      p_payment_id: payment.id,
      p_amount: payment.amount,
    })

    if (rpcError) {
      console.error('Failed to activate plan:', rpcError)
      // Don't throw - payment is recorded, plan activation can be retried
    }

    return {
      success: true,
      plan: payment.plan,
    }

  } catch (error) {
    console.error('Payment processing failed:', error)
    return {
      success: false,
      error: error.message,
    }
  }
}

/**
 * Demo: Simulate successful payment (for testing without PhonePe)
 */
export const simulatePayment = async (merchantTransactionId) => {
  // Simulate PhonePe success response
  const mockResponse = {
    success: true,
    code: 'PAYMENT_SUCCESS',
    message: 'Payment successful',
    transactionId: `PHONEPE_${Date.now()}`,
    paymentInstrument: {
      type: 'UPI',
    },
  }

  return processSuccessfulPayment(merchantTransactionId, mockResponse)
}

