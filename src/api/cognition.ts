import apiClient from '../lib/api';

export interface RecordLearningRequest {
  learning_type: string; // success, failure, partial, optimization, pattern, risk, opportunity
  source: string;
  description: string;
  key_insight: string;
  context?: Record<string, any>;
  confidence?: number;
}

export interface SynthesizeKnowledgeRequest {
  synthesis_type: string; // trend, pattern, prediction, recommendation, warning, opportunity
  title: string;
  description: string;
  learning_ids: string[];
  recommendations: string[];
}

export interface MakeDecisionRequest {
  title: string;
  description: string;
  decision_type: string; // e.g., resource_allocation, process_change
  options: Record<string, any>;
  synthesis_ids: string[];
  impact_forecast?: Record<string, number>;
}

export interface MentorAgentRequest {
  agent_name: string;
  current_challenge: string;
  agent_goal: string;
}

export const cognitionApi = {
  // Learning
  recordLearning: (data: RecordLearningRequest) => 
    apiClient.request('/lords/cognition/learning/record', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  getRecentLearnings: (limit: number = 10) => 
    apiClient.request(`/lords/cognition/learning/recent?limit=${limit}`),

  getLearning: (id: string) => 
    apiClient.request(`/lords/cognition/learning/${id}`),

  // Synthesis
  synthesizeKnowledge: (data: SynthesizeKnowledgeRequest) => 
    apiClient.request('/lords/cognition/synthesis/create', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  getRecentSyntheses: (limit: number = 10) => 
    apiClient.request(`/lords/cognition/synthesis/recent?limit=${limit}`),

  getSynthesis: (id: string) => 
    apiClient.request(`/lords/cognition/synthesis/${id}`),

  // Decisions
  makeDecision: (data: MakeDecisionRequest) => 
    apiClient.request('/lords/cognition/decisions/make', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  getRecentDecisions: (limit: number = 10) => 
    apiClient.request(`/lords/cognition/decisions/recent?limit=${limit}`),

  getDecision: (id: string) => 
    apiClient.request(`/lords/cognition/decisions/${id}`),

  // Mentoring
  provideMentoring: (data: MentorAgentRequest) => 
    apiClient.request('/lords/cognition/mentoring/provide', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  // Summary & Status
  getLearningSummary: () => 
    apiClient.request('/lords/cognition/learning/summary'),

  getStatus: () => 
    apiClient.request('/lords/cognition/status')
};

export default cognitionApi;
