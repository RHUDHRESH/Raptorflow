import apiClient from '../lib/api';

export interface ChaosEvent {
  type: string;
  name: string;
  description: string;
  severity: string;
  timestamp: string;
  parameters?: Record<string, any>;
  expected_impact?: Record<string, number>;
}

export interface WargameScenario {
  id: string;
  name: string;
  description: string;
  events: ChaosEvent[];
  difficulty: string;
  created_at: string;
}

export interface ResilienceScore {
  overall_score: number;
  survival_probability: number;
  weaknesses_exposed: string[];
  recommendations: string[];
  timestamp: string;
}

export interface WargameResponse {
  scenario: WargameScenario;
  resilience_score: ResilienceScore;
}

export const erisApi = {
  // Chaos
  generateChaos: (domain: string, severity: string) => 
    apiClient.request('/lords/eris/chaos/generate', {
      method: 'POST',
      body: JSON.stringify({ target_domain: domain, severity })
    }),

  // Wargaming
  runWargame: (strategyId: string, details: Record<string, any>, numEvents: number = 3) => 
    apiClient.request('/lords/eris/wargame/run', {
      method: 'POST',
      body: JSON.stringify({ 
        strategy_id: strategyId, 
        strategy_details: details,
        num_events: numEvents
      })
    }),

  // Entropy
  injectEntropy: (data: Record<string, any>, noiseLevel: number = 0.1) => 
    apiClient.request('/lords/eris/entropy/inject', {
      method: 'POST',
      body: JSON.stringify({ data, noise_level: noiseLevel })
    }),

  // History
  getHistory: () => 
    apiClient.request('/lords/eris/history')
};

export default erisApi;
