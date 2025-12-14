/**
 * PhonePe Payment Gateway Integration
 * 
 * This module handles PhonePe payment integration for Raptorflow
 * Uses the backend API for secure payment processing
 */

import { supabase } from './supabase'

// API base URL
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:3001/api'

// Plan prices for display (with RBI autopay compliance)
// RBI Regulation: Autopay without OTP only allowed up to ₹5,000
export const RBI_AUTOPAY_LIMIT_PAISE = 500000; // ₹5,000

export const PLAN_PRICES = {
  ascent: {
    price: 500000,
    name: 'Ascent',
    priceDisplay: '₹5,000',
    cohorts: 3,
    autopayEligible: true,
    requiresOtp: false,
    renewalNote: 'Seamless autopay'
  },
  glide: {
    price: 700000,
    name: 'Glide',
    priceDisplay: '₹7,000',
    cohorts: 5,
    autopayEligible: false,
    requiresOtp: true,
    renewalNote: 'Monthly payment link'
  },
  soar: {
    price: 1000000,
    name: 'Soar',
    priceDisplay: '₹10,000',
    cohorts: 10,
    autopayEligible: false,
    requiresOtp: true,
    renewalNote: 'Monthly payment link'
  },
}

/**
 * Get current user's auth token
 */
const getAuthToken = async () => {
  const { data: { session } } = await supabase.auth.getSession()
  return session?.access_token
}

/**
 * Initialize a PhonePe payment via backend API
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

    const token = await getAuthToken()
    if (!token) {
      throw new Error('Not authenticated')
    }

    // Call backend API to initiate payment
    const response = await fetch(`${API_BASE}/payments/initiate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        plan,
        phone: userPhone || ''
      })
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.error || 'Payment initiation failed')
    }

    // If real PhonePe payment URL returned, redirect to it
    if (data.paymentUrl && !data.mock) {
      return {
        success: true,
        merchantTransactionId: data.txnId,
        redirectUrl: data.paymentUrl, // PhonePe payment page
        isExternal: true
      }
    }

    // For mock/test mode, redirect to our payment process page
    return {
      success: true,
      merchantTransactionId: data.txnId,
      redirectUrl: `/payment/process?txnId=${data.txnId}&plan=${plan}`,
      isMock: data.mock
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
 * Check payment status via backend API
 * @param {string} merchantTransactionId - Transaction ID to check
 */
export const checkPaymentStatus = async (merchantTransactionId) => {
  try {
    const response = await fetch(`${API_BASE}/payments/status/${merchantTransactionId}`)
    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.error || 'Status check failed')
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
 * Verify and process payment completion via backend API
 * @param {string} merchantTransactionId - Transaction ID
 * @param {boolean} mock - Whether this is a mock payment
 */
export const verifyPayment = async (merchantTransactionId, mock = false) => {
  try {
    const token = await getAuthToken()
    if (!token) {
      throw new Error('Not authenticated')
    }

    const response = await fetch(`${API_BASE}/payments/verify`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        txnId: merchantTransactionId,
        mock
      })
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.error || 'Payment verification failed')
    }

    return {
      success: data.success,
      status: data.status,
      plan: data.plan,
      message: data.message
    }

  } catch (error) {
    console.error('Payment verification failed:', error)
    return {
      success: false,
      error: error.message,
    }
  }
}

/**
 * Process successful payment (called after PhonePe callback)
 * @deprecated Use verifyPayment instead
 */
export const processSuccessfulPayment = async (merchantTransactionId, phonepeResponse) => {
  return verifyPayment(merchantTransactionId, false)
}

/**
 * Simulate successful payment (for testing without PhonePe)
 * This still goes through the backend for proper plan activation
 */
export const simulatePayment = async (merchantTransactionId) => {
  return verifyPayment(merchantTransactionId, true)
}
