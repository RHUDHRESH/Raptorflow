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

// ============ MUSE API ============

export const museAPI = {
  /**
   * Generate a new asset using Muse AI
   */
  async generateAsset(assetType, icpId = null, options = {}) {
    return apiRequest('/muse/generate', {
      method: 'POST',
      body: JSON.stringify({
        asset_type: assetType,
        icp_id: icpId,
        ...options,
      }),
    });
  },

  /**
   * Get the status of an asset generation job
   */
  async getGenerationStatus(jobId) {
    return apiRequest(`/muse/generate/${jobId}`);
  },

  /**
   * Generate a PDF from asset content
   */
  async generatePDF(content, title, assetType, metadata = {}) {
    return apiRequest('/muse/pdf/generate', {
      method: 'POST',
      body: JSON.stringify({
        content,
        title,
        assetType,
        metadata,
      }),
    });
  },

  /**
   * Get list of available agents (for future use)
   */
  async getAgents() {
    return apiRequest('/muse/agents');
  },

  /**
   * Get agent capabilities (for future use)
   */
  async getCapabilities() {
    return apiRequest('/muse/capabilities');
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

// ============ SUBSCRIPTIONS API ============

export const subscriptionsAPI = {
  /**
   * Get current subscription details
   */
  async getCurrent() {
    return apiRequest('/subscriptions/current');
  },

  /**
   * Preview proration for an upgrade (no charge)
   */
  async previewUpgrade(planId) {
    return apiRequest('/subscriptions/preview-upgrade', {
      method: 'POST',
      body: JSON.stringify({ planId }),
    });
  },

  /**
   * Upgrade to a higher plan (immediate charge)
   */
  async upgrade(planId) {
    return apiRequest('/subscriptions/upgrade', {
      method: 'POST',
      body: JSON.stringify({ planId }),
    });
  },

  /**
   * Schedule downgrade for next billing cycle
   */
  async downgrade(planId) {
    return apiRequest('/subscriptions/downgrade', {
      method: 'POST',
      body: JSON.stringify({ planId }),
    });
  },

  /**
   * Cancel subscription
   */
  async cancel(immediate = false, reason = '') {
    return apiRequest('/subscriptions/cancel', {
      method: 'POST',
      body: JSON.stringify({ immediate, reason }),
    });
  },

  /**
   * Pause subscription (retention tactic)
   */
  async pause(pauseUntil = null) {
    return apiRequest('/subscriptions/pause', {
      method: 'POST',
      body: JSON.stringify({ pauseUntil }),
    });
  },

  /**
   * Resume a paused subscription
   */
  async resume() {
    return apiRequest('/subscriptions/resume', {
      method: 'POST',
    });
  },

  /**
   * Reactivate a subscription scheduled for cancellation
   */
  async reactivate() {
    return apiRequest('/subscriptions/reactivate', {
      method: 'POST',
    });
  },
};

// ============ TEAM API ============

export const teamAPI = {
  /**
   * Get all team members
   */
  async getMembers() {
    return apiRequest('/team/members');
  },

  /**
   * Invite a new team member
   */
  async invite(email, role = 'viewer') {
    return apiRequest('/team/invite', {
      method: 'POST',
      body: JSON.stringify({ email, role }),
    });
  },

  /**
   * Get pending invites
   */
  async getInvites() {
    return apiRequest('/team/invites');
  },

  /**
   * Revoke a pending invite
   */
  async revokeInvite(inviteId) {
    return apiRequest(`/team/invites/${inviteId}`, {
      method: 'DELETE',
    });
  },

  /**
   * Accept an invite by token
   */
  async acceptInvite(token) {
    return apiRequest('/team/accept-invite', {
      method: 'POST',
      body: JSON.stringify({ token }),
    });
  },

  /**
   * Update a member's role
   */
  async updateRole(memberId, role) {
    return apiRequest(`/team/members/${memberId}`, {
      method: 'PATCH',
      body: JSON.stringify({ role }),
    });
  },

  /**
   * Remove a team member
   */
  async removeMember(memberId) {
    return apiRequest(`/team/members/${memberId}`, {
      method: 'DELETE',
    });
  },
};

// Export default object for convenience
export default {
  onboarding: onboardingAPI,
  payments: paymentsAPI,
  subscriptions: subscriptionsAPI,
  team: teamAPI,
  shared: sharedAPI,
  muse: museAPI,
  checkHealth: checkAPIHealth,
};
