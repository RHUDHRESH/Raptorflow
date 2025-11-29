import apiClient from '../lib/api';

export interface StartOnboardingResponse {
  session_id: string | null;
  already_completed: boolean;
  profile_id?: string;
  message?: string;
  next_question?: any;
  current_step?: number;
}

export interface SubmitAnswerResponse {
  session_id: string;
  completed: boolean;
  next_question?: any;
  current_step: number;
  total_answers: number;
  profile?: any;
}

export const onboardingApi = {
  start: () => 
    apiClient.request('/onboarding/start', { method: 'POST' }),

  submitAnswer: (sessionId: string, questionId: string, answer: string) => 
    apiClient.request('/onboarding/answer', {
      method: 'POST',
      body: JSON.stringify({
        session_id: sessionId,
        question_id: questionId,
        answer
      })
    }),

  analyzeContext: (data: { raw_text: string, website?: string, pitch?: string, industry?: string }) =>
    apiClient.request('/onboarding/analyze-context', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  generateAxes: (data: { category: string, narrative: any, keywords: string[] }) =>
    apiClient.request('/onboarding/generate-axes', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  analyzeCompetitors: (data: { industry: string, context_summary: any, axis_frame: any }) =>
    apiClient.request('/onboarding/analyze-competitors', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  proposeICPs: (data: { industry: string, context_summary: any, positioning: any }) =>
    apiClient.request('/onboarding/propose-icps', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  getSession: (sessionId: string) => 
    apiClient.request(`/onboarding/session/${sessionId}`),

  getProfile: () => 
    apiClient.request('/onboarding/profile'),

  updateProfile: (updates: Record<string, any>) => 
    apiClient.request('/onboarding/profile', {
      method: 'PUT',
      body: JSON.stringify(updates)
    }),

  complete: (sessionId: string) => 
    apiClient.request('/onboarding/complete', {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId })
    }),

  deleteSession: (sessionId: string) => 
    apiClient.request(`/onboarding/session/${sessionId}`, { method: 'DELETE' })
};

export default onboardingApi;
