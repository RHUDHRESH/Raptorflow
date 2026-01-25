import { create } from 'zustand';
import { authFetch } from '../lib/auth-helpers';

interface Agent {
  id: string;
  name: string;
  type: string;
  status: string;
  capabilities: string[];
  specializations: string[];
}

interface AgentExecution {
  agent_id: string;
  task: string;
  status: string;
  result: string;
  confidence: number;
  processing_time_ms: number;
  context_used: {
    bcm_context: boolean;
    user_history: boolean;
    business_stage: boolean;
  };
  insights: string[];
}

interface AgentsStore {
  agents: Record<string, Agent>;
  executions: Record<string, AgentExecution>;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  setAgents: (agents: Agent[]) => void;
  setExecution: (execution: AgentExecution) => void;
  fetchAvailableAgents: () => Promise<void>;
  executeAgent: (agentId: string, task: string, context?: any) => Promise<AgentExecution>;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

// API helper functions
const agentsApi = {
  async fetchAvailableAgents(): Promise<Agent[]> {
    const response = await authFetch('/api/proxy/api/v1/agents/available');
    
    if (!response.ok) {
      throw new Error('Failed to fetch available agents');
    }
    
    const data = await response.json();
    return data.agents;
  },
  
  async executeAgent(agentId: string, task: string, context?: any): Promise<AgentExecution> {
    const response = await authFetch(`/api/proxy/api/v1/agents/${agentId}/execute`, {
      method: 'POST',
      body: JSON.stringify({
        task,
        context: context || {}
      }),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to execute agent ${agentId}`);
    }
    
    const data = await response.json();
    return data.execution;
  }
};

export const useAgentsStore = create<AgentsStore>((set, get) => ({
  agents: {},
  executions: {},
  isLoading: false,
  error: null,

  setAgents: (agents) => {
    const agentsMap = agents.reduce((acc, agent) => {
      acc[agent.id] = agent;
      return acc;
    }, {} as Record<string, Agent>);
    
    set({ agents: agentsMap });
  },

  setExecution: (execution) => {
    set(state => ({
      executions: {
        ...state.executions,
        [execution.agent_id]: execution
      }
    }));
  },

  fetchAvailableAgents: async () => {
    set({ isLoading: true, error: null });
    try {
      const agents = await agentsApi.fetchAvailableAgents();
      get().setAgents(agents);
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Unknown error' });
    } finally {
      set({ isLoading: false });
    }
  },

  executeAgent: async (agentId, task, context) => {
    set({ isLoading: true, error: null });
    try {
      const execution = await agentsApi.executeAgent(agentId, task, context);
      get().setExecution(execution);
      return execution;
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Unknown error' });
      throw error;
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
