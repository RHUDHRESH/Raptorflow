import { create } from 'zustand';

interface Campaign {
  id: string;
  name: string;
  description?: string;
  target_icps?: string[];
  phases?: Array<{
    name: string;
    status: string;
    start_date?: string;
    end_date?: string;
  }>;
  budget_usd?: number;
  start_date?: string;
  end_date?: string;
  status?: string;
  settings?: {
    autoOptimization?: boolean;
    abTesting?: boolean;
  };
  createdAt?: Date;
  updatedAt?: Date;
}

interface EnhancedCampaignStore {
  campaigns: Record<string, Campaign>;
  currentCampaign: Campaign | null;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  setCampaigns: (campaigns: Campaign[]) => void;
  setCurrentCampaign: (campaign: Campaign | null) => void;
  addCampaign: (campaign: Omit<Campaign, 'id'>) => Promise<string>;
  updateCampaign: (campaign: Partial<Campaign> & { id: string }) => Promise<void>;
  deleteCampaign: (id: string) => Promise<void>;
  fetchCampaigns: () => Promise<void>;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

// API helper functions
const campaignsApi = {
  async fetchCampaigns(): Promise<Campaign[]> {
    const response = await fetch('/api/proxy/api/v1/campaigns/', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch campaigns');
    }
    
    const data = await response.json();
    return data.campaigns || [];
  },
  
  async createCampaign(campaign: Omit<Campaign, 'id'>): Promise<Campaign> {
    const response = await fetch('/api/proxy/api/v1/campaigns/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(campaign),
    });
    
    if (!response.ok) {
      throw new Error('Failed to create campaign');
    }
    
    return response.json();
  },
  
  async updateCampaign(id: string, updates: Partial<Campaign>): Promise<Campaign> {
    const response = await fetch(`/api/proxy/api/v1/campaigns/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updates),
    });
    
    if (!response.ok) {
      throw new Error('Failed to update campaign');
    }
    
    return response.json();
  },
  
  async deleteCampaign(id: string): Promise<void> {
    const response = await fetch(`/api/proxy/api/v1/campaigns/${id}`, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      throw new Error('Failed to delete campaign');
    }
  }
};

export const useEnhancedCampaignStore = create<EnhancedCampaignStore>((set, get) => ({
  campaigns: {},
  currentCampaign: null,
  isLoading: false,
  error: null,

  setCampaigns: (campaigns) => {
    const campaignsMap = campaigns.reduce((acc, campaign) => {
      acc[campaign.id] = campaign;
      return acc;
    }, {} as Record<string, Campaign>);
    
    set({ campaigns: campaignsMap });
  },

  setCurrentCampaign: (campaign) => {
    set({ currentCampaign: campaign });
  },

  fetchCampaigns: async () => {
    set({ isLoading: true, error: null });
    try {
      const campaigns = await campaignsApi.fetchCampaigns();
      get().setCampaigns(campaigns);
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Unknown error' });
    } finally {
      set({ isLoading: false });
    }
  },

  addCampaign: async (campaign) => {
    set({ isLoading: true, error: null });
    try {
      const newCampaign = await campaignsApi.createCampaign(campaign);
      set(state => ({
        campaigns: {
          ...state.campaigns,
          [newCampaign.id]: newCampaign
        }
      }));
      return newCampaign.id;
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Unknown error' });
      throw error;
    } finally {
      set({ isLoading: false });
    }
  },

  updateCampaign: async (campaignUpdate) => {
    const { id, ...updates } = campaignUpdate;
    
    set({ isLoading: true, error: null });
    try {
      const updatedCampaign = await campaignsApi.updateCampaign(id, updates);
      set(state => ({
        campaigns: {
          ...state.campaigns,
          [id]: updatedCampaign
        }
      }));
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Unknown error' });
      throw error;
    } finally {
      set({ isLoading: false });
    }
  },

  deleteCampaign: async (id) => {
    set({ isLoading: true, error: null });
    try {
      await campaignsApi.deleteCampaign(id);
      set(state => {
        const newCampaigns = { ...state.campaigns };
        delete newCampaigns[id];
        return { campaigns: newCampaigns };
      });
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
