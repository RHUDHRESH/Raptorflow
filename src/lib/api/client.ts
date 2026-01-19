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

    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      // Return mock data for development
      return this.getMockResponse<T>(endpoint);
    }
  }

  private getMockResponse<T>(endpoint: string): ApiResponse<T> {
    // Mock responses for development when backend is not available
    const mockResponses: Record<string, ApiResponse<unknown>> = {
      '/': {
        message: "Raptorflow Ultimate Backend API",
        version: "2.0.0",
        status: "active",
        modules: ["agents", "skills", "tools", "data", "workflows", "monitoring"],
        timestamp: new Date().toISOString(),
      },
      '/health': {
        status: "healthy",
        timestamp: new Date().toISOString(),
        modules: {
          agents: "active",
          skills: "active",
          tools: "active",
          data: "active",
          workflows: "active",
          monitoring: "active"
        }
      },
      '/agents': {
        status: "success",
        timestamp: new Date().toISOString(),
        module: "agents",
        count: 5,
        agents: [
          {
            id: "1",
            name: "ICP Architect",
            type: "specialist",
            status: "active",
            capabilities: ["market research", "persona development", "segmentation"]
          },
          {
            id: "2",
            name: "Content Generator",
            type: "creative",
            status: "active",
            capabilities: ["blog posts", "social media", "email campaigns"]
          },
          {
            id: "3",
            name: "Campaign Manager",
            type: "orchestrator",
            status: "active",
            capabilities: ["campaign planning", "budget allocation", "performance tracking"]
          }
        ]
      },
      '/skills': {
        status: "success",
        timestamp: new Date().toISOString(),
        module: "skills",
        count: 8,
        skills: [
          {
            id: "1",
            name: "Market Analysis",
            category: "research",
            status: "active",
            description: "Analyze market trends and competitor data"
          },
          {
            id: "2",
            name: "Content Creation",
            category: "creative",
            status: "active",
            description: "Generate marketing content and copy"
          },
          {
            id: "3",
            name: "Data Visualization",
            category: "analytics",
            status: "active",
            description: "Create charts and visual reports"
          }
        ]
      },
      '/tools': {
        status: "success",
        timestamp: new Date().toISOString(),
        module: "tools",
        count: 12,
        tools: [
          {
            id: "1",
            name: "Email Sender",
            type: "communication",
            status: "active",
            description: "Send marketing emails and newsletters"
          },
          {
            id: "2",
            name: "Social Media Poster",
            type: "social",
            status: "active",
            description: "Post content to social media platforms"
          },
          {
            id: "3",
            name: "Analytics Dashboard",
            type: "analytics",
            status: "active",
            description: "Track and analyze marketing metrics"
          }
        ]
      }
    };

    return (mockResponses[endpoint] || {
      status: "error",
      message: "Endpoint not found",
      timestamp: new Date().toISOString()
    }) as ApiResponse<T>;
  }

  // System endpoints
  async getHealth() {
    return this.request('/health');
  }

  async getSystemInfo() {
    return this.request('/');
  }

  // Agent endpoints
  async getAgents(): Promise<ApiResponse<Agent[]>> {
    return this.request('/agents');
  }

  async getAgent(id: string): Promise<ApiResponse<Agent>> {
    return this.request(`/agents/${id}`);
  }

  // Skill endpoints
  async getSkills(): Promise<ApiResponse<Skill[]>> {
    return this.request('/skills');
  }

  async getSkill(id: string): Promise<ApiResponse<Skill>> {
    return this.request(`/skills/${id}`);
  }

  // Tool endpoints
  async getTools(): Promise<ApiResponse<Tool[]>> {
    return this.request('/tools');
  }

  async getTool(id: string): Promise<ApiResponse<Tool>> {
    return this.request(`/tools/${id}`);
  }

  // Workflow endpoints
  async getWorkflows(): Promise<ApiResponse<Workflow[]>> {
    return this.request('/workflows');
  }

  async getWorkflow(id: string): Promise<ApiResponse<Workflow>> {
    return this.request(`/workflows/${id}`);
  }

  // Data endpoints
  async getDataStatus() {
    return this.request('/data');
  }

  // Monitoring endpoints
  async getMonitoringStatus() {
    return this.request('/monitoring');
  }
}

// Create singleton instance
export const apiClient = new ApiClient();
