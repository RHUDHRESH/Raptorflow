import { create } from 'zustand';
import { authFetch, getCurrentUserId, getCurrentWorkspaceId } from '../lib/auth-helpers';

interface Move {
  id: string;
  name: string;
  focusArea: string;
  desiredOutcome: string;
  volatilityLevel: number;
  steps: string[];
  createdAt?: Date;
  updatedAt?: Date;
  status?: 'draft' | 'active' | 'completed' | 'archived';
}

interface MovesStore {
  moves: Record<string, Move>;
  currentMove: Move | null;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  setMoves: (moves: Move[]) => void;
  setCurrentMove: (move: Move | null) => void;
  addMove: (move: Omit<Move, 'id'>) => Promise<string>;
  updateMove: (move: Partial<Move> & { id: string }) => Promise<void>;
  deleteMove: (id: string) => Promise<void>;
  createMoveFromBlackBox: (data: {
    focusArea: string;
    desiredOutcome: string;
    volatilityLevel: number;
    name: string;
    steps: string[];
  }) => Promise<string>;
  fetchMoves: () => Promise<void>;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

// API helper functions
const movesApi = {
  async fetchMoves(): Promise<Move[]> {
    const workspaceId = getCurrentWorkspaceId();
    const userId = getCurrentUserId();
    
    if (!workspaceId || !userId) {
      throw new Error('Authentication required');
    }

    const response = await authFetch(`/api/proxy/api/v1/moves/?workspace_id=${workspaceId}&user_id=${userId}`, {
      method: 'GET',
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch moves');
    }
    
    const data = await response.json();
    return data.moves || [];
  },
  
  async createMove(move: Omit<Move, 'id'>): Promise<Move> {
    const workspaceId = getCurrentWorkspaceId();
    const userId = getCurrentUserId();
    
    if (!workspaceId || !userId) {
      throw new Error('Authentication required');
    }

    const response = await authFetch('/api/proxy/api/v1/moves/', {
      method: 'POST',
      body: JSON.stringify({
        ...move,
        workspace_id: workspaceId,
        user_id: userId,
      }),
    });
    
    if (!response.ok) {
      throw new Error('Failed to create move');
    }
    
    return response.json();
  },
  
  async updateMove(id: string, updates: Partial<Move>): Promise<Move> {
    const response = await authFetch(`/api/proxy/api/v1/moves/${id}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
    
    if (!response.ok) {
      throw new Error('Failed to update move');
    }
    
    return response.json();
  },
  
  async deleteMove(id: string): Promise<void> {
    const response = await authFetch(`/api/proxy/api/v1/moves/${id}`, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      throw new Error('Failed to delete move');
    }
  }
};

export const useMovesStore = create<MovesStore>((set, get) => ({
  moves: {},
  currentMove: null,
  isLoading: false,
  error: null,

  setMoves: (moves) => {
    const movesMap = moves.reduce((acc, move) => {
      acc[move.id] = move;
      return acc;
    }, {} as Record<string, Move>);
    
    set({ moves: movesMap });
  },

  setCurrentMove: (move) => {
    set({ currentMove: move });
  },

  fetchMoves: async () => {
    set({ isLoading: true, error: null });
    try {
      const moves = await movesApi.fetchMoves();
      get().setMoves(moves);
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Unknown error' });
    } finally {
      set({ isLoading: false });
    }
  },

  addMove: async (move) => {
    set({ isLoading: true, error: null });
    try {
      const newMove = await movesApi.createMove(move);
      set(state => ({
        moves: {
          ...state.moves,
          [newMove.id]: newMove
        }
      }));
      return newMove.id;
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Unknown error' });
      throw error;
    } finally {
      set({ isLoading: false });
    }
  },

  updateMove: async (moveUpdate) => {
    const { id, ...updates } = moveUpdate;
    
    set({ isLoading: true, error: null });
    try {
      const updatedMove = await movesApi.updateMove(id, updates);
      set(state => ({
        moves: {
          ...state.moves,
          [id]: updatedMove
        }
      }));
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Unknown error' });
      throw error;
    } finally {
      set({ isLoading: false });
    }
  },

  deleteMove: async (id) => {
    set({ isLoading: true, error: null });
    try {
      await movesApi.deleteMove(id);
      set(state => {
        const newMoves = { ...state.moves };
        delete newMoves[id];
        return { moves: newMoves };
      });
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Unknown error' });
      throw error;
    } finally {
      set({ isLoading: false });
    }
  },

  createMoveFromBlackBox: async (data) => {
    set({ isLoading: true, error: null });
    try {
      const newMove = await movesApi.createMove(data);
      set(state => ({
        moves: {
          ...state.moves,
          [newMove.id]: newMove
        }
      }));
      return newMove.id;
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
