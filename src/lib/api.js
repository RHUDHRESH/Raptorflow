/**
 * RaptorFlow API Client
 * Handles all communication with the backend API
 */

import { supabase } from './supabase';

// API Base URL - uses Vite proxy in development, direct URL in production
const API_BASE = import.meta.env.VITE_API_URL || import.meta.env.VITE_BACKEND_API_URL || '/api';

/**
 * Get the current auth token
 */
async function getAuthToken() {
  const { data: { session } } = await supabase.auth.getSession();
  return session?.access_token;
}

/**
 * Make an authenticated API request
 */
async function apiRequest(endpoint, options = {}) {
  const token = await getAuthToken();
  
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || 'API request failed');
  }

  return data;
}

// ============ ONBOARDING API ============

export const onboardingAPI = {
  /**
   * Get the current user's onboarding intake data
   */
  async getIntake() {
    return apiRequest('/onboarding/intake');
  },

  /**
   * Get onboarding status
   */
  async getStatus() {
    return apiRequest('/onboarding/status');
  },

  /**
   * Save step data and trigger agent processing
   */
  async saveStep(step, data) {
    return apiRequest('/onboarding/intake', {
      method: 'POST',
      body: JSON.stringify({ step, data }),
    });
  },

  /**
   * Generate ICPs (requires steps 1-5 completed)
   */
  async generateICPs() {
    return apiRequest('/onboarding/generate-icps', {
      method: 'POST',
    });
  },

  /**
   * Generate War Plan (requires ICPs generated)
   */
  async generateWarPlan() {
    return apiRequest('/onboarding/generate-warplan', {
      method: 'POST',
    });
  },

  /**
   * Mark onboarding as complete
   */
  async complete() {
    return apiRequest('/onboarding/complete', {
      method: 'POST',
    });
  },

  /**
   * Reset onboarding to start fresh
   */
  async reset() {
    return apiRequest('/onboarding/reset', {
      method: 'POST',
    });
  },
};

// ============ PAYMENTS API ============

export const paymentsAPI = {
  /**
   * Get available plans
   */
  async getPlans() {
    return apiRequest('/payments/plans');
  },

  /**
   * Initiate a payment
   */
  async initiate(plan, phone = '') {
    return apiRequest('/payments/initiate', {
      method: 'POST',
      body: JSON.stringify({ plan, phone }),
    });
  },

  /**
   * Check payment status
   */
  async getStatus(txnId) {
    return apiRequest(`/payments/status/${txnId}`);
  },

  /**
   * Verify and complete payment
   */
  async verify(txnId, mock = false) {
    return apiRequest('/payments/verify', {
      method: 'POST',
      body: JSON.stringify({ txnId, mock }),
    });
  },
};

// ============ SHARED LINKS API ============

export const sharedAPI = {
  /**
   * Create a shareable link for an intake
   */
  async createLink(intakeId) {
    return apiRequest('/shared/create', {
      method: 'POST',
      body: JSON.stringify({ intake_id: intakeId }),
    });
  },

  /**
   * Get shared intake data (no auth required)
   */
  async getData(token) {
    const response = await fetch(`${API_BASE}/shared/${token}`);
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.error || 'Failed to get shared data');
    }
    
    return data;
  },

  /**
   * Initiate payment from shared link
   */
  async initiatePayment(token, plan, email = '', phone = '') {
    const response = await fetch(`${API_BASE}/shared/${token}/payment`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ plan, email, phone }),
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.error || 'Payment initiation failed');
    }
    
    return data;
  },
};

// ============ HEALTH CHECK ============

export async function checkAPIHealth() {
  try {
    const response = await fetch(`${API_BASE.replace('/api', '')}/health`);
    const data = await response.json();
    return { healthy: data.status === 'ok', ...data };
  } catch (error) {
    return { healthy: false, error: error.message };
  }
}

// Export default object for convenience
export default {
  onboarding: onboardingAPI,
  payments: paymentsAPI,
  shared: sharedAPI,
  checkHealth: checkAPIHealth,
};

