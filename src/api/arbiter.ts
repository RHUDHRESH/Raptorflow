import apiClient from '../lib/api';

export interface RegisterConflictRequest {
  conflict_type: string;
  title: string;
  description: string;
  parties_involved?: string[];
  conflicting_goals?: string[];
}

export interface AnalyzeConflictRequest {
  case_id: string;
  additional_context?: Record<string, any>;
}

export interface ProposeResolutionRequest {
  case_id: string;
  proposed_solution: string;
  priority_adjustment?: Record<string, any>;
}

export interface MakeDecisionRequest {
  case_id: string;
  proposal_id: string;
  enforcement_method?: string;
}

export interface HandleAppealRequest {
  decision_id: string;
  appellant_party: string;
  appeal_grounds?: string[];
  requested_review_points?: string[];
}

export const arbiterApi = {
  // Conflict Registration
  registerConflict: (data: RegisterConflictRequest) => 
    apiClient.request('/lords/arbiter/conflict/register', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  getCases: (limit: number = 10) => 
    apiClient.request(`/lords/arbiter/cases?limit=${limit}`),

  getCase: (id: string) => 
    apiClient.request(`/lords/arbiter/cases/${id}`),

  // Conflict Analysis
  analyzeConflict: (data: AnalyzeConflictRequest) => 
    apiClient.request('/lords/arbiter/analysis/analyze', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  // Resolution Proposal
  proposeResolution: (data: ProposeResolutionRequest) => 
    apiClient.request('/lords/arbiter/resolution/propose', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  getProposals: (limit: number = 10) => 
    apiClient.request(`/lords/arbiter/proposals?limit=${limit}`),

  // Arbitration Decision
  makeDecision: (data: MakeDecisionRequest) => 
    apiClient.request('/lords/arbiter/decision/make', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  getDecisions: (limit: number = 10) => 
    apiClient.request(`/lords/arbiter/decisions?limit=${limit}`),

  getDecision: (id: string) => 
    apiClient.request(`/lords/arbiter/decisions/${id}`),

  // Appeals
  handleAppeal: (data: HandleAppealRequest) => 
    apiClient.request('/lords/arbiter/appeals/handle', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  getAppeals: (limit: number = 10) => 
    apiClient.request(`/lords/arbiter/appeals?limit=${limit}`),

  // Fairness Report
  generateFairnessReport: (evaluationPeriodDays: number = 30) => 
    apiClient.request('/lords/arbiter/fairness/report', {
      method: 'POST',
      body: JSON.stringify({ evaluation_period_days: evaluationPeriodDays })
    }),

  // Status
  getStatus: () => 
    apiClient.request('/lords/arbiter/status')
};

export default arbiterApi;
