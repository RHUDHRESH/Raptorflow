/**
 * API Client for RaptorFlow Backend Integration
 * Provides type-safe API calls to the backend services
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ApiResponse<T = unknown> {
  data?: T;
  message?: string;
  status: string;
  timestamp: string;
  [key: string]: unknown; // Allow additional properties
}

export interface Agent {
  id: string;
  name: string;
  type: string;
  status: string;
  capabilities: string[];
}

export interface Skill {
  id: string;
  name: string;
  category: string;
  status: string;
  description: string;
}

export interface Tool {
  id: string;
  name: string;
  type: string;
  status: string;
  description: string;
}

export interface Workflow {
  id: string;
  name: string;
  status: string;
  steps: number;
  progress: number;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${endpoint}`;

    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  }

  async get<T>(endpoint: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'GET' });
  }

  async post<T>(endpoint: string, body: any, options: RequestInit = {}): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: JSON.stringify(body),
    });
  }

  // Dashboard endpoints
  async getDashboardSummary(): Promise<ApiResponse<any>> {
    return this.request('/api/v1/dashboard/summary');
  }

  // Analytics endpoints
  async getMovesPerformance(): Promise<ApiResponse<any>> {
    return this.request('/api/v1/analytics-v2/moves');
  }

  async getMusePerformance(): Promise<ApiResponse<any>> {
    return this.request('/api/v1/analytics-v2/muse');
  }

  // Moves endpoints
  async listMoves(): Promise<ApiResponse<any[]>> {
    return this.request('/api/v1/moves/');
  }

  async createMove(data: any): Promise<ApiResponse<any>> {
    return this.request('/api/v1/moves/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateMove(moveId: string, data: any): Promise<ApiResponse<any>> {
    return this.request(`/api/v1/moves/${moveId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async getMovesCalendar(): Promise<ApiResponse<any>> {
    return this.request('/api/v1/moves/calendar/events');
  }

  // Campaigns endpoints
  async listCampaigns(): Promise<ApiResponse<any>> {
    return this.request('/api/v1/campaigns/');
  }

  async createCampaign(data: any): Promise<ApiResponse<any>> {
    return this.request('/api/v1/campaigns/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getCampaignCalendar(): Promise<ApiResponse<any>> {
    return this.request('/api/v1/campaigns/calendar/events');
  }

  // Muse endpoints
  async generateMuseAsset(data: any): Promise<ApiResponse<any>> {
    return this.request('/api/v1/muse/generate', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async listMuseAssets(): Promise<ApiResponse<any[]>> {
    return this.request('/api/v1/muse/assets');
  }

  async deriveTrinity(cohortName: string): Promise<ApiResponse<any>> {
    return this.request('/api/v1/icps/derive-trinity', {
      method: 'POST',
      body: JSON.stringify({ name: cohortName }),
    });
  }

  async createBlueprint(goal: string): Promise<ApiResponse<any>> {
    return this.request('/api/v1/moves/create-blueprint', {
      method: 'POST',
      body: JSON.stringify({ goal }),
    });
  }

  async getExpertReasoning(moveId: string): Promise<ApiResponse<any>> {
    return this.request(`/api/v1/moves/${moveId}/reasoning`);
  }

  async getAgents(): Promise<ApiResponse<Agent[]>> {
    return this.request('/api/v1/agents/');
  }

  async getSkills(): Promise<ApiResponse<Skill[]>> {
    return this.request('/api/v1/agents/skills');
  }

  async getTools(): Promise<ApiResponse<Tool[]>> {
    return this.request('/api/v1/agents/tools');
  }

  async getWorkflows(): Promise<ApiResponse<Workflow[]>> {
    return this.request('/api/v1/agents/workflows');
  }

  async getSystemHealth(): Promise<ApiResponse<any>> {
    return this.request('/api/v1/health');
  }

  async getHealth(): Promise<ApiResponse<any>> {
    return this.getSystemHealth();
  }

  async getSystemInfo(): Promise<ApiResponse<any>> {
    return this.request('/');
  }

  async generateBlackBoxStrategy(data: any): Promise<ApiResponse<any>> {
    return this.request('/api/v1/blackbox/generate', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async acceptBlackBoxStrategy(strategyId: string, data: any): Promise<ApiResponse<any>> {
    return this.request(`/api/v1/blackbox/strategies/${strategyId}/accept`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getDailyAgenda(): Promise<ApiResponse<any>> {
    return this.request('/api/v1/moves/calendar/events');
  }

  // Daily Wins endpoints
  async generateDailyWin(data: {
    workspace_id: string;
    user_id: string;
    platform: string;
  }): Promise<ApiResponse<any>> {
    return this.request('/api/v1/daily_wins/generate', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async markWinAsPosted(winId: string, data: any): Promise<ApiResponse<any>> {
    return this.request(`/api/v1/daily_wins/${winId}/mark-posted`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
}

// Create singleton instance
export const apiClient = new ApiClient();
export const api = apiClient;
