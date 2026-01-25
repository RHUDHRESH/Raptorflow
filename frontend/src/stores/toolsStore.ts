import { create } from 'zustand';
import { authFetch } from '../lib/auth-helpers';

interface Tool {
  id: string;
  name: string;
  type: string;
  status: string;
  capabilities: string[];
  usage?: any;
}

interface ServiceStatus {
  ai_services: Record<string, any>;
  data_services: Record<string, any>;
  communication: Record<string, any>;
  monitoring: Record<string, any>;
}

interface ServicesStatusResponse {
  services: ServiceStatus;
  overall_health: string;
}

interface ToolsStore {
  tools: Record<string, Tool>;
  servicesStatus: ServiceStatus | null;
  overallHealth: string;
  isLoading: boolean;
  error: string | null;

  // Actions
  setTools: (tools: Tool[]) => void;
  setServicesStatus: (status: ServicesStatusResponse) => void;
  fetchAvailableTools: () => Promise<void>;
  fetchServicesStatus: () => Promise<void>;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

// API helper functions
const toolsApi = {
  async fetchAvailableTools(): Promise<Tool[]> {
    const response = await authFetch('/api/proxy/api/v1/tools/available');

    if (!response.ok) {
      throw new Error('Failed to fetch available tools');
    }

    const data = await response.json();
    return data.tools;
  },

  async fetchServicesStatus(): Promise<ServicesStatusResponse> {
    const response = await authFetch('/api/proxy/api/v1/services/status');

    if (!response.ok) {
      throw new Error('Failed to fetch services status');
    }

    const data = await response.json();
    return {
      services: data.services,
      overall_health: data.overall_health
    };
  }
};

export const useToolsStore = create<ToolsStore>((set, get) => ({
  tools: {},
  servicesStatus: null,
  overallHealth: 'unknown',
  isLoading: false,
  error: null,

  setTools: (tools) => {
    const toolsMap = tools.reduce((acc, tool) => {
      acc[tool.id] = tool;
      return acc;
    }, {} as Record<string, Tool>);

    set({ tools: toolsMap });
  },

  setServicesStatus: (status) => {
    set({
      servicesStatus: status.services,
      overallHealth: status.overall_health
    });
  },

  fetchAvailableTools: async () => {
    set({ isLoading: true, error: null });
    try {
      const tools = await toolsApi.fetchAvailableTools();
      get().setTools(tools);
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Unknown error' });
    } finally {
      set({ isLoading: false });
    }
  },

  fetchServicesStatus: async () => {
    set({ isLoading: true, error: null });
    try {
      const status = await toolsApi.fetchServicesStatus();
      get().setServicesStatus(status);
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Unknown error' });
    } finally {
      set({ isLoading: false });
    }
  },

  setLoading: (loading) => {
    set({ isLoading: loading });
  },

  setError: (error) => {
    set({ error });
  }
}));
