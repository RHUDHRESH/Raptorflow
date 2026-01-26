import { create } from 'zustand';

interface Asset {
  id: string;
  title: string;
  content: string;
  platform: 'email' | 'linkedin' | 'blog' | 'tweet' | 'script';
  tags: string[];
  icp_context?: string;
  created_at: string;
  workspace_id: string;
  user_id: string;
}

interface MuseChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  platform?: string;
  tone?: string;
  assets?: Asset[];
  created_at: string;
}

interface MuseStore {
  assets: Record<string, Asset>;
  chatHistory: Record<string, MuseChatMessage[]>;
  currentChat: MuseChatMessage[];
  isLoading: boolean;
  isGenerating: boolean;
  error: string | null;

  // Actions
  setAssets: (assets: Asset[]) => void;
  setCurrentChat: (chat: MuseChatMessage[]) => void;
  generateContent: (data: {
    prompt: string;
    platform: string;
    tone?: string;
    icp_context?: string;
    workspace_id: string;
    user_id: string;
  }) => Promise<Asset>;
  chatWithMuse: (data: {
    message: string;
    platform?: string;
    tone?: string;
    workspace_id: string;
    user_id: string;
    session_id?: string;
  }) => Promise<MuseChatMessage>;
  saveAsset: (asset: Omit<Asset, 'id' | 'created_at'>) => Promise<string>;
  fetchAssets: (workspace_id: string, user_id: string) => Promise<void>;
  setLoading: (loading: boolean) => void;
  setGenerating: (generating: boolean) => void;
  setError: (error: string | null) => void;
}

// API helper functions
const museApi = {
  async generateContent(data: {
    prompt: string;
    platform: string;
    tone?: string;
    icp_context?: string;
    workspace_id: string;
    user_id: string;
  }): Promise<Asset> {
    const response = await fetch('/api/proxy/api/v1/muse/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error('Failed to generate content');
    }

    const result = await response.json();
    return result.asset;
  },

  async chatWithMuse(data: {
    message: string;
    platform?: string;
    tone?: string;
    workspace_id: string;
    user_id: string;
    session_id?: string;
  }): Promise<MuseChatMessage> {
    const response = await fetch('/api/proxy/api/v1/muse/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error('Failed to chat with Muse');
    }

    const result = await response.json();
    return result.message;
  },

  async saveAsset(asset: Omit<Asset, 'id' | 'created_at'>): Promise<Asset> {
    const response = await fetch('/api/proxy/api/v1/muse/assets', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(asset),
    });

    if (!response.ok) {
      throw new Error('Failed to save asset');
    }

    return response.json();
  },

  async fetchAssets(workspace_id: string, user_id: string): Promise<Asset[]> {
    const response = await fetch(`/api/proxy/api/v1/muse/assets?workspace_id=${workspace_id}&user_id=${user_id}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch assets');
    }

    const data = await response.json();
    return data.assets || [];
  }
};

export const useMuseStore = create<MuseStore>((set, get) => ({
  assets: {},
  chatHistory: {},
  currentChat: [],
  isLoading: false,
  isGenerating: false,
  error: null,

  setAssets: (assets) => {
    const assetsMap = assets.reduce((acc, asset) => {
      acc[asset.id] = asset;
      return acc;
    }, {} as Record<string, Asset>);

    set({ assets: assetsMap });
  },

  setCurrentChat: (chat) => {
    set({ currentChat: chat });
  },

  generateContent: async (data) => {
    set({ isGenerating: true, error: null });
    try {
      const asset = await museApi.generateContent(data);
      set(state => ({
        assets: {
          ...state.assets,
          [asset.id]: asset
        }
      }));
      return asset;
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Unknown error' });
      throw error;
    } finally {
      set({ isGenerating: false });
    }
  },

  chatWithMuse: async (data) => {
    set({ isGenerating: true, error: null });
    try {
      // Add user message to current chat
      const userMessage: MuseChatMessage = {
        id: Date.now().toString(),
        role: 'user',
        content: data.message,
        platform: data.platform,
        tone: data.tone,
        created_at: new Date().toISOString()
      };

      const newChat = [...get().currentChat, userMessage];
      set({ currentChat: newChat });

      // Get AI response
      const assistantMessage = await museApi.chatWithMuse(data);

      const updatedChat = [...newChat, assistantMessage];
      set({ currentChat: updatedChat });

      return assistantMessage;
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Unknown error' });
      throw error;
    } finally {
      set({ isGenerating: false });
    }
  },

  saveAsset: async (asset) => {
    set({ isLoading: true, error: null });
    try {
      const newAsset = await museApi.saveAsset(asset);
      set(state => ({
        assets: {
          ...state.assets,
          [newAsset.id]: newAsset
        }
      }));
      return newAsset.id;
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Unknown error' });
      throw error;
    } finally {
      set({ isLoading: false });
    }
  },

  fetchAssets: async (workspace_id, user_id) => {
    set({ isLoading: true, error: null });
    try {
      const assets = await museApi.fetchAssets(workspace_id, user_id);
      get().setAssets(assets);
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Unknown error' });
    } finally {
      set({ isLoading: false });
    }
  },

  setLoading: (loading) => {
    set({ isLoading: loading });
  },

  setGenerating: (generating) => {
    set({ isGenerating: generating });
  },

  setError: (error) => {
    set({ error });
  }
}));
