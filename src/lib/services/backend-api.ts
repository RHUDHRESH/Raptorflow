/**
 * RaptorFlow 2.0 Backend API Client
 * TypeScript client for communicating with the FastAPI backend
 * Enhanced with Memory, Performance Prediction, and Advanced Features
 */

import { supabase } from '../supabase';
import { v4 as uuidv4 } from 'uuid';

const BACKEND_URL = import.meta.env.VITE_BACKEND_API_URL || 'http://localhost:8000/api/v1';

/**
 * Base fetch wrapper with authentication and correlation ID tracking
 */
async function apiFetch(endpoint: string, options: RequestInit = {}) {
  const { data: { session } } = await supabase.auth.getSession();

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    'X-Correlation-ID': uuidv4(), // Track requests across the system
    ...options.headers,
  };

  if (session?.access_token) {
    headers['Authorization'] = `Bearer ${session.access_token}`;
  }

  const response = await fetch(`${BACKEND_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `API Error: ${response.status}`);
  }

  return response.json();
}

/**
 * Onboarding API
 */
export const onboardingAPI = {
  /**
   * Start a new onboarding session
   */
  async startSession(sessionId?: string) {
    return apiFetch('/onboarding/start', {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId }),
    });
  },
  
  /**
   * Submit an answer to the current onboarding question
   */
  async submitAnswer(sessionId: string, questionId: string, answer: any) {
    return apiFetch(`/onboarding/answer/${sessionId}`, {
      method: 'POST',
      body: JSON.stringify({ question_id: questionId, answer }),
    });
  },
  
  /**
   * Get current onboarding session state
   */
  async getSession(sessionId: string) {
    return apiFetch(`/onboarding/session/${sessionId}`);
  },
  
  /**
   * Get completed onboarding profile
   */
  async getProfile(sessionId: string) {
    return apiFetch(`/onboarding/profile/${sessionId}`);
  },
  
  /**
   * Complete onboarding session
   */
  async completeSession(sessionId: string) {
    return apiFetch(`/onboarding/complete/${sessionId}`, { method: 'POST' });
  },
};

/**
 * Customer Intelligence API (ICPs)
 */
export const icpAPI = {
  /**
   * Create a new ICP
   */
  async createICP(data: { nickname: string; role: string; biggest_pain_point: string; known_attributes?: string[] }) {
    return apiFetch('/customer-intelligence/create', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
  
  /**
   * Get all ICPs for workspace
   */
  async listICPs() {
    return apiFetch('/customer-intelligence/list');
  },
  
  /**
   * Get specific ICP
   */
  async getICP(icpId: string) {
    return apiFetch(`/customer-intelligence/${icpId}`);
  },
  
  /**
   * Enrich ICP with psychographics
   */
  async enrichICP(icpId: string) {
    return apiFetch(`/customer-intelligence/${icpId}/enrich`, { method: 'POST' });
  },
};

/**
 * Strategy API
 */
export const strategyAPI = {
  /**
   * Generate a new marketing strategy
   */
  async generateStrategy(data: {
    goal: string;
    timeframe_days?: number;
    target_cohort_ids?: string[];
    constraints?: Record<string, any>;
  }) {
    return apiFetch('/strategy/generate', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
  
  /**
   * Get strategy by ID
   */
  async getStrategy(strategyId: string) {
    return apiFetch(`/strategy/${strategyId}`);
  },
  
  /**
   * List all strategies
   */
  async listStrategies() {
    return apiFetch('/strategy/');
  },
};

/**
 * Campaigns API
 */
export const campaignsAPI = {
  /**
   * Create a new campaign
   */
  async createCampaign(data: {
    name: string;
    goal: string;
    timeframe_days: number;
    target_cohort_ids: string[];
    channels: string[];
    constraints?: Record<string, any>;
  }) {
    return apiFetch('/campaigns/create', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
  
  /**
   * Get campaign by ID
   */
  async getCampaign(moveId: string) {
    return apiFetch(`/campaigns/${moveId}`);
  },
  
  /**
   * Get today's tasks for a campaign
   */
  async getTodaysTasks(moveId: string) {
    return apiFetch(`/campaigns/${moveId}/tasks/today`);
  },
  
  /**
   * Mark task as complete
   */
  async completeTask(moveId: string, taskId: string) {
    return apiFetch(`/campaigns/${moveId}/task/${taskId}/complete`, {
      method: 'PUT',
    });
  },
  
  /**
   * List all campaigns
   */
  async listCampaigns() {
    return apiFetch('/campaigns/');
  },
};

/**
 * Content API
 */
export const contentAPI = {
  /**
   * Generate blog post
   */
  async generateBlog(data: {
    persona_id: string;
    topic: string;
    goal?: string;
    keywords?: string[];
    tone?: string;
  }) {
    return apiFetch('/content/generate/blog', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
  
  /**
   * Generate email
   */
  async generateEmail(data: {
    persona_id: string;
    topic: string;
    goal?: string;
    tone?: string;
  }) {
    return apiFetch('/content/generate/email', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
  
  /**
   * Generate social post
   */
  async generateSocial(data: {
    persona_id: string;
    topic: string;
    goal?: string;
    tone?: string;
  }) {
    return apiFetch('/content/generate/social', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
  
  /**
   * Generate hooks
   */
  async generateHooks(topic: string, count?: number) {
    const params = new URLSearchParams({ topic });
    if (count) params.append('count', count.toString());
    return apiFetch(`/content/generate/hooks?${params}`);
  },
  
  /**
   * Review content with critic agent
   */
  async reviewContent(contentId: string) {
    return apiFetch(`/content/${contentId}/review`, { method: 'POST' });
  },
  
  /**
   * Approve or reject content
   */
  async approveContent(contentId: string, approved: boolean, feedback?: string) {
    return apiFetch(`/content/${contentId}/approve`, {
      method: 'PUT',
      body: JSON.stringify({ approved, feedback }),
    });
  },
  
  /**
   * Get content by ID
   */
  async getContent(contentId: string) {
    return apiFetch(`/content/${contentId}`);
  },
};

/**
 * Analytics API
 */
export const analyticsAPI = {
  /**
   * Collect metrics from platforms
   */
  async collectMetrics(moveId?: string, platforms?: string[]) {
    const body: any = {};
    if (moveId) body.move_id = moveId;
    if (platforms) body.platforms = platforms;
    
    return apiFetch('/analytics/collect', {
      method: 'POST',
      body: JSON.stringify(body),
    });
  },
  
  /**
   * Get workspace metrics
   */
  async getWorkspaceMetrics(workspaceId: string) {
    return apiFetch(`/analytics/workspace/${workspaceId}`);
  },
  
  /**
   * Get campaign metrics
   */
  async getCampaignMetrics(moveId: string) {
    return apiFetch(`/analytics/move/${moveId}`);
  },
  
  /**
   * Get campaign insights
   */
  async getCampaignInsights(moveId: string, timePeriodDays?: number) {
    const params = new URLSearchParams();
    if (timePeriodDays) params.append('time_period_days', timePeriodDays.toString());
    return apiFetch(`/analytics/move/${moveId}/insights?${params}`);
  },
  
  /**
   * Get pivot suggestion
   */
  async getPivotSuggestion(moveId: string) {
    return apiFetch(`/analytics/move/${moveId}/pivot`);
  },
  
  /**
   * Generate post-mortem report
   */
  async generatePostMortem(moveId: string) {
    return apiFetch(`/analytics/move/${moveId}/post-mortem`, { method: 'POST' });
  },
  
  /**
   * Get cross-campaign learnings
   */
  async getLearnings(timeframeDays?: number) {
    const params = new URLSearchParams();
    if (timeframeDays) params.append('timeframe_days', timeframeDays.toString());
    return apiFetch(`/analytics/learnings?${params}`);
  },
};

/**
 * Integrations API
 */
export const integrationsAPI = {
  /**
   * Connect a platform
   */
  async connectPlatform(platform: string, data: {
    access_token: string;
    refresh_token?: string;
    account_id?: string;
    metadata?: Record<string, any>;
  }) {
    return apiFetch(`/integrations/connect/${platform}`, {
      method: 'POST',
      body: JSON.stringify({ platform, ...data }),
    });
  },

  /**
   * Disconnect a platform
   */
  async disconnectPlatform(platform: string) {
    return apiFetch(`/integrations/disconnect/${platform}`, { method: 'DELETE' });
  },

  /**
   * Get integration status for all platforms
   */
  async getIntegrationStatus() {
    return apiFetch('/integrations/status');
  },

  /**
   * Get specific platform status
   */
  async getPlatformStatus(platform: string) {
    return apiFetch(`/integrations/${platform}/status`);
  },
};

/**
 * Memory API - Advanced Memory System
 * Supports workspace, semantic, conversation, and agent memory
 */
export const memoryAPI = {
  /**
   * Store information in workspace memory
   */
  async remember(workspaceId: string, key: string, value: any, metadata?: any) {
    return apiFetch('/memory/remember', {
      method: 'POST',
      body: JSON.stringify({
        workspace_id: workspaceId,
        key,
        value,
        metadata
      })
    });
  },

  /**
   * Recall information from workspace memory
   */
  async recall(workspaceId: string, key: string) {
    return apiFetch(`/memory/recall/${workspaceId}/${key}`);
  },

  /**
   * Semantic search across all memory
   */
  async search(workspaceId: string, query: string, topK: number = 5) {
    const params = new URLSearchParams({
      query,
      top_k: topK.toString()
    });
    return apiFetch(`/memory/search/${workspaceId}?${params}`);
  },

  /**
   * Get full context for a task type
   */
  async getContext(workspaceId: string, taskType: string, topK: number = 10) {
    const params = new URLSearchParams({
      task_type: taskType,
      top_k: topK.toString()
    });
    return apiFetch(`/memory/context/${workspaceId}?${params}`);
  },

  /**
   * List all memory entries for a workspace
   */
  async list(workspaceId: string, memoryType?: string) {
    const params = new URLSearchParams();
    if (memoryType) params.append('memory_type', memoryType);
    return apiFetch(`/memory/list/${workspaceId}?${params}`);
  },

  /**
   * Delete a memory entry
   */
  async forget(workspaceId: string, key: string) {
    return apiFetch(`/memory/forget/${workspaceId}/${key}`, {
      method: 'DELETE'
    });
  },
};

/**
 * Performance Prediction API
 * AI-powered performance prediction before publishing
 */
export const performanceAPI = {
  /**
   * Predict engagement metrics for content
   */
  async predictEngagement(data: {
    content: string;
    icp_id: string;
    channel: 'linkedin' | 'twitter' | 'blog' | 'email';
    content_type: 'blog' | 'email' | 'social';
  }) {
    return apiFetch('/analytics/predict/performance', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  /**
   * Get optimal posting time for content
   */
  async getOptimalTime(data: {
    icp_id: string;
    channel: string;
    content_type: string;
  }) {
    return apiFetch('/analytics/predict/optimal-time', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  /**
   * Predict A/B test outcomes
   */
  async predictABTest(data: {
    variant_a: string;
    variant_b: string;
    icp_id: string;
    channel: string;
  }) {
    return apiFetch('/analytics/predict/ab-test', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },
};

/**
 * Guardian API - Compliance and Safety Checks
 */
export const guardianAPI = {
  /**
   * Run compliance check on content
   */
  async checkContent(contentId: string) {
    return apiFetch(`/content/${contentId}/guardian-check`, {
      method: 'POST'
    });
  },

  /**
   * Get compliance history
   */
  async getHistory(workspaceId: string, limit: number = 50) {
    const params = new URLSearchParams({
      limit: limit.toString()
    });
    return apiFetch(`/guardian/history/${workspaceId}?${params}`);
  },
};

/**
 * Orchestration API - Agent Debugging and Tracing
 */
export const orchestrationAPI = {
  /**
   * List recent agent execution runs
   */
  async listRecentRuns(limit: number = 20) {
    const params = new URLSearchParams({
      limit: limit.toString()
    });
    return apiFetch(`/orchestration/runs?${params}`);
  },

  /**
   * Get detailed execution trace for a correlation ID
   */
  async getExecutionTrace(correlationId: string) {
    return apiFetch(`/orchestration/trace/${correlationId}`);
  },

  /**
   * Get agent performance metrics
   */
  async getAgentMetrics(agentName?: string) {
    const params = new URLSearchParams();
    if (agentName) params.append('agent_name', agentName);
    return apiFetch(`/orchestration/metrics?${params}`);
  },
};

/**
 * Cohorts API (replaces icpAPI with correct endpoint names)
 */
export const cohortsAPI = {
  /**
   * Generate a new cohort/ICP
   */
  async generate(data: {
    nickname: string;
    role: string;
    biggest_pain_point: string;
    known_attributes?: string[];
  }) {
    return apiFetch('/cohorts/generate', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Compute psychographics for a cohort
   */
  async computePsychographics(cohortId: string, cohortData: any) {
    return apiFetch('/cohorts/compute_psychographics', {
      method: 'POST',
      body: JSON.stringify({
        cohort: cohortData
      }),
    });
  },

  /**
   * Get all cohorts for workspace
   */
  async list() {
    return apiFetch('/cohorts/');
  },

  /**
   * Get specific cohort
   */
  async get(cohortId: string) {
    return apiFetch(`/cohorts/${cohortId}`);
  },

  /**
   * Update cohort
   */
  async update(cohortId: string, data: any) {
    return apiFetch(`/cohorts/${cohortId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  /**
   * Delete cohort
   */
  async delete(cohortId: string) {
    return apiFetch(`/cohorts/${cohortId}`, {
      method: 'DELETE',
    });
  },
};

/**
 * Payment & Subscription API
 */
export const paymentAPI = {
  /**
   * Get all available subscription plans
   */
  async getPlans() {
    return apiFetch('/payments/plans');
  },

  /**
   * Create a checkout session for subscription purchase
   */
  async createCheckout(data: { plan: string; billing_period: string; success_url: string; cancel_url: string }) {
    return apiFetch('/payments/checkout/create', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Get current subscription status
   */
  async getSubscriptionStatus() {
    return apiFetch('/payments/subscription/status');
  },

  /**
   * Change subscription plan
   */
  async changeSubscription(data: { new_plan: string; billing_period: string; immediate?: boolean }) {
    return apiFetch('/payments/subscription/change', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Cancel subscription
   */
  async cancelSubscription(data: { reason?: string; immediate?: boolean }) {
    return apiFetch('/payments/subscription/cancel', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Get billing history
   */
  async getBillingHistory() {
    return apiFetch('/payments/billing/history');
  },

  /**
   * Check payment status
   */
  async checkPaymentStatus(merchantTransactionId: string) {
    return apiFetch(`/payments/payment/status/${merchantTransactionId}`);
  },
};

/**
 * Export all APIs as a single object
 */
export const backendAPI = {
  onboarding: onboardingAPI,
  icp: icpAPI, // Keep for backwards compatibility
  cohorts: cohortsAPI, // New correct endpoint
  strategy: strategyAPI,
  campaigns: campaignsAPI,
  content: contentAPI,
  analytics: analyticsAPI,
  integrations: integrationsAPI,
  memory: memoryAPI,
  performance: performanceAPI,
  guardian: guardianAPI,
  orchestration: orchestrationAPI,
  payment: paymentAPI,
};

export default backendAPI;




