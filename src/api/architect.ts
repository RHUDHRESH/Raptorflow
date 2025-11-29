import apiClient from '../lib/api';

export interface Initiative {
  id: string;
  name: string;
  objectives: string[];
  target_guilds: string[];
  timeline_weeks: number;
  status: string;
  success_metrics?: Record<string, any>;
  phases?: any[];
  risk_assessment?: any;
  created_at: string;
  updated_at: string;
}

export interface InitiativeRequest {
  name: string;
  objectives: string[];
  target_guilds: string[];
  timeline_weeks: number;
  success_metrics?: Record<string, any>;
}

export interface ArchitectureAnalysisRequest {
  component: string;
  metrics: Record<string, number>;
}

export interface ComponentOptimizationRequest {
  component_type: string;
  current_metrics: Record<string, number>;
}

export interface GuidanceRequest {
  guild_name: string;
  topic: string;
}

export interface StrategyReviewRequest {
  guild_name: string;
  guild_strategy: Record<string, any>;
}

export const architectApi = {
  // Initiatives
  designInitiative: (data: InitiativeRequest) => 
    apiClient.request('/lords/architect/initiatives/design', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  listInitiatives: (status?: string) => 
    apiClient.request(`/lords/architect/initiatives${status ? `?status=${status}` : ''}`),

  getInitiative: (id: string) => 
    apiClient.request(`/lords/architect/initiatives/${id}`),

  approveInitiative: (id: string, approver: string) =>
    apiClient.request(`/lords/architect/initiatives/${id}/approve?approver=${approver}`, {
      method: 'POST'
    }),

  // Architecture
  analyzeArchitecture: (data: ArchitectureAnalysisRequest) => 
    apiClient.request('/lords/architect/architecture/analyze', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  optimizeComponent: (data: ComponentOptimizationRequest) => 
    apiClient.request('/lords/architect/architecture/optimize', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  // Guidance
  provideGuidance: (data: GuidanceRequest) => 
    apiClient.request('/lords/architect/guidance/provide', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  getGuildGuidance: (guildName: string) => 
    apiClient.request(`/lords/architect/guidance/${guildName}`),

  // Strategy Review
  reviewStrategy: (data: StrategyReviewRequest) => 
    apiClient.request('/lords/architect/strategy-review', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  // Status & Decisions
  getDecisions: (limit: number = 10) => 
    apiClient.request(`/lords/architect/decisions?limit=${limit}`),

  getStatus: () => 
    apiClient.request('/lords/architect/status')
};

export default architectApi;
