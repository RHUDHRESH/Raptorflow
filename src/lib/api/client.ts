/**
 * API Client for RaptorFlow Backend Integration
 * Provides type-safe API calls to the backend services
 * Aligned with the RaptorFlow Bespoke API Standard.
 */

import { RaptorResponse } from '../../modules/infrastructure/types/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

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
  ): Promise<RaptorResponse<T>> {
    const url = `${this.baseUrl}${endpoint}`;

    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      const data = await response.json();
      
      // If the backend already returns RaptorResponse, return it directly
      if (typeof data.success === 'boolean' && data.meta) {
        return data as RaptorResponse<T>;
      }

      // Legacy support: Wrap non-standard responses
      if (response.ok) {
        return {
          success: true,
          data: data,
          error: null,
          meta: { timestamp: new Date().toISOString() }
        };
      } else {
        return {
          success: false,
          data: null,
          error: {
            code: 'API_ERROR',
            message: data.message || `HTTP error! status: ${response.status}`,
            details: data
          },
          meta: { timestamp: new Date().toISOString() }
        };
      }
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      // Return mock data for development
      return this.getMockResponse<T>(endpoint);
    }
  }

  private getMockResponse<T>(endpoint: string): RaptorResponse<T> {
    const timestamp = new Date().toISOString();
    
    const wrap = <T>(data: T): RaptorResponse<T> => ({
      success: true,
      data,
      error: null,
      meta: { timestamp }
    });

    const mockData: Record<string, any> = {
      '/': {
        message: "Raptorflow Ultimate Backend API",
        version: "2.0.0",
        status: "active",
        modules: ["agents", "skills", "tools", "data", "workflows", "monitoring"]
      },
      '/health': {
        status: "healthy",
        modules: {
          agents: "active",
          skills: "active",
          tools: "active",
          data: "active",
          workflows: "active",
          monitoring: "active"
        }
      },
      '/agents': [
        {
          id: "1",
          name: "ICP Architect",
          type: "specialist",
          status: "active",
          capabilities: ["market research", "persona development", "segmentation"]
        }
      ],
      '/skills': [
        {
          id: "1",
          name: "Market Analysis",
          category: "research",
          status: "active",
          description: "Analyze market trends and competitor data"
        }
      ],
      '/tools': [
        {
          id: "1",
          name: "Email Sender",
          type: "communication",
          status: "active",
          description: "Send marketing emails and newsletters"
        }
      ]
    };

    if (mockData[endpoint]) {
      return wrap(mockData[endpoint]);
    }

    return {
      success: false,
      data: null,
      error: {
        code: 'NOT_FOUND',
        message: 'Endpoint not found'
      },
      meta: { timestamp }
    };
  }

  // System endpoints
  async getHealth() {
    return this.request<any>('/health');
  }

  async getSystemInfo() {
    return this.request<any>('/');
  }

  // Agent endpoints
  async getAgents(): Promise<RaptorResponse<Agent[]>> {
    return this.request('/agents');
  }

  async getAgent(id: string): Promise<RaptorResponse<Agent>> {
    return this.request(`/agents/${id}`);
  }

  // Skill endpoints
  async getSkills(): Promise<RaptorResponse<Skill[]>> {
    return this.request('/skills');
  }

  async getSkill(id: string): Promise<RaptorResponse<Skill>> {
    return this.request(`/skills/${id}`);
  }

  // Tool endpoints
  async getTools(): Promise<RaptorResponse<Tool[]>> {
    return this.request('/tools');
  }

  async getTool(id: string): Promise<RaptorResponse<Tool>> {
    return this.request(`/tools/${id}`);
  }

  // Workflow endpoints
  async getWorkflows(): Promise<RaptorResponse<Workflow[]>> {
    return this.request('/workflows');
  }

  async getWorkflow(id: string): Promise<RaptorResponse<Workflow>> {
    return this.request(`/workflows/${id}`);
  }
}

// Create singleton instance
export const apiClient = new ApiClient();