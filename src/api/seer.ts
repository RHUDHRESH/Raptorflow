import apiClient from '../lib/api';

export interface PredictTrendRequest {
  metric_name: string;
  historical_values: number[];
  forecast_period_days?: number;
  forecast_type?: string; // linear, exponential, polynomial, seasonal, cyclical
}

export interface GatherIntelligenceRequest {
  intelligence_type: string; // competitive, market_trend, customer_behavior, technology, regulatory, economic
  title: string;
  summary: string;
  source?: string;
  key_insights?: string[];
}

export interface AnalyzePerformanceRequest {
  scope: string; // campaign, guild, organization
  scope_id: string;
  metrics: Record<string, number>;
}

export interface GenerateRecommendationRequest {
  title: string;
  description: string;
  priority?: string; // critical, high, normal, low
  supporting_insights?: string[];
  required_resources?: Record<string, any>;
}

export interface GetForecastReportRequest {
  title?: string;
  forecast_period_days?: number;
  include_predictions?: boolean;
  include_intelligence?: boolean;
}

export const seerApi = {
  // Trend Prediction
  predictTrend: (data: PredictTrendRequest) => 
    apiClient.request('/lords/seer/predict-trend', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  getRecentPredictions: (limit: number = 10) => 
    apiClient.request(`/lords/seer/predictions?limit=${limit}`),

  getPrediction: (id: string) => 
    apiClient.request(`/lords/seer/predictions/${id}`),

  // Market Intelligence
  gatherIntelligence: (data: GatherIntelligenceRequest) => 
    apiClient.request('/lords/seer/intelligence/gather', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  getRecentIntelligence: (limit: number = 10) => 
    apiClient.request(`/lords/seer/intelligence?limit=${limit}`),

  getIntelligence: (id: string) => 
    apiClient.request(`/lords/seer/intelligence/${id}`),

  // Performance Analysis
  analyzePerformance: (data: AnalyzePerformanceRequest) => 
    apiClient.request('/lords/seer/analysis/performance', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  // Recommendations
  generateRecommendation: (data: GenerateRecommendationRequest) => 
    apiClient.request('/lords/seer/recommendations/generate', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  getRecentRecommendations: (limit: number = 10) => 
    apiClient.request(`/lords/seer/recommendations?limit=${limit}`),

  // Forecast Reports
  generateForecastReport: (data: GetForecastReportRequest) => 
    apiClient.request('/lords/seer/forecast/generate', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  getForecastReports: (limit: number = 10) => 
    apiClient.request(`/lords/seer/forecast/reports?limit=${limit}`),

  // Status
  getStatus: () => 
    apiClient.request('/lords/seer/status')
};

export default seerApi;
