import apiClient from '../lib/api';

export interface AssessQualityRequest {
  content_id: string;
  content_type: string; // copy, visual, design, messaging, branding, video, audio, interactive
  guild_name: string;
  content_metrics: Record<string, number>;
}

export interface CheckBrandComplianceRequest {
  content_id: string;
  guild_name: string;
  content_elements: Record<string, any>;
}

export interface EvaluateVisualConsistencyRequest {
  scope: string; // campaign, guild, organization
  scope_id: string;
  items_count: number;
  consistency_data: Record<string, any>;
}

export interface ProvideFeedbackRequest {
  content_id: string;
  content_type: string;
  design_elements: Record<string, any>;
  guild_name: string;
}

export interface ApproveContentRequest {
  review_id: string;
  approval_notes?: string;
}

export const aestheteApi = {
  // Quality Assessment
  assessQuality: (data: AssessQualityRequest) => 
    apiClient.request('/lords/aesthete/assess-quality', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  getRecentReviews: (limit: number = 10) => 
    apiClient.request(`/lords/aesthete/reviews?limit=${limit}`),

  getReview: (id: string) => 
    apiClient.request(`/lords/aesthete/reviews/${id}`),

  // Brand Compliance
  checkBrandCompliance: (data: CheckBrandComplianceRequest) => 
    apiClient.request('/lords/aesthete/brand-compliance/check', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  // Visual Consistency
  evaluateConsistency: (data: EvaluateVisualConsistencyRequest) => 
    apiClient.request('/lords/aesthete/consistency/evaluate', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  // Design Feedback
  provideFeedback: (data: ProvideFeedbackRequest) => 
    apiClient.request('/lords/aesthete/feedback/provide', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  // Content Approval
  approveContent: (data: ApproveContentRequest) => 
    apiClient.request('/lords/aesthete/approve', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  getApprovedContent: () => 
    apiClient.request('/lords/aesthete/approved-content'),

  // Status
  getStatus: () => 
    apiClient.request('/lords/aesthete/status')
};

export default aestheteApi;
