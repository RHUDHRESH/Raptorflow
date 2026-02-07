/**
 * API Client for RaptorFlow Backend Integration
 * Provides type-safe API calls to the backend services
 * Aligned with the RaptorFlow Bespoke API Standard.
 */

import { RaptorResponse } from '../../modules/infrastructure/types/api';
import { RaptorErrorCodes, RaptorErrorMessages } from '../../modules/infrastructure/services/apiResponse';

const API_BASE_URL = '/api';

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

      const data = await response.json().catch(() => null);
      const requestId = response.headers.get('x-request-id') || undefined;

      // If the backend already returns RaptorResponse, return it directly
      if (data && typeof data.success === 'boolean' && data.meta) {
        return {
          ...(data as RaptorResponse<T>),
          meta: {
            ...data.meta,
            requestId: data.meta?.requestId || requestId,
          },
        };
      }

      // Legacy support: Wrap non-standard responses
      if (response.ok) {
        return {
          success: true,
          data: data as T,
          error: null,
          meta: { timestamp: new Date().toISOString(), requestId }
        };
      } else {
        const errorDetails = data ?? { status: response.status };
        const error = this.mapError(response.status, errorDetails);
        return {
          success: false,
          data: null,
          error,
          meta: { timestamp: new Date().toISOString(), requestId }
        };
      }
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      if (process.env.NODE_ENV === 'development') {
        return this.getMockResponse<T>(endpoint);
      }
      return {
        success: false,
        data: null,
        error: {
          code: RaptorErrorCodes.NETWORK_ERROR,
          message:
            error instanceof Error
              ? error.message
              : RaptorErrorMessages[RaptorErrorCodes.NETWORK_ERROR],
        },
        meta: { timestamp: new Date().toISOString() },
      };
    }
  }

  private mapError(status: number, details?: any) {
    const statusMap: Record<number, { code: string; message: string }> = {
      400: { code: RaptorErrorCodes.BAD_REQUEST, message: RaptorErrorMessages[RaptorErrorCodes.BAD_REQUEST] },
      401: { code: RaptorErrorCodes.UNAUTHORIZED, message: RaptorErrorMessages[RaptorErrorCodes.UNAUTHORIZED] },
      403: { code: RaptorErrorCodes.FORBIDDEN, message: RaptorErrorMessages[RaptorErrorCodes.FORBIDDEN] },
      404: { code: RaptorErrorCodes.NOT_FOUND, message: RaptorErrorMessages[RaptorErrorCodes.NOT_FOUND] },
      422: {
        code: RaptorErrorCodes.UNPROCESSABLE_ENTITY,
        message: RaptorErrorMessages[RaptorErrorCodes.UNPROCESSABLE_ENTITY],
      },
      429: { code: RaptorErrorCodes.RATE_LIMITED, message: RaptorErrorMessages[RaptorErrorCodes.RATE_LIMITED] },
      500: {
        code: RaptorErrorCodes.INTERNAL_SERVER_ERROR,
        message: RaptorErrorMessages[RaptorErrorCodes.INTERNAL_SERVER_ERROR],
      },
    };

    const fallback = statusMap[status] || {
      code: RaptorErrorCodes.UNKNOWN_ERROR,
      message: RaptorErrorMessages[RaptorErrorCodes.UNKNOWN_ERROR],
    };

    return {
      ...fallback,
      details,
    };
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
        code: RaptorErrorCodes.NOT_FOUND,
        message: RaptorErrorMessages[RaptorErrorCodes.NOT_FOUND],
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
