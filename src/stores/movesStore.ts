/* ════════════════════════════════════════════════════════════════════════════════════════
   MOVES STORE — No-Auth Reconstruction
   Source of truth: backend `/api/v1/*` (via Next proxy) scoped by `X-Workspace-Id`.
   No Supabase browser client, no RLS, no silent fallbacks.
   ════════════════════════════════════════════════════════════════════════════════════════ */

import { create } from "zustand";
import type { Move } from "@/components/moves/types";
import { movesService } from "@/services/moves.service";

interface MovesState {
  moves: Move[];
  pendingMove: Partial<Move> | null;
  isLoading: boolean;
  error: string | null;

  fetchMoves: (workspaceId: string) => Promise<void>;
  addMove: (move: Move, workspaceId: string) => Promise<void>;
  updateMove: (moveId: string, updates: Partial<Move>, workspaceId: string) => Promise<void>;
  deleteMove: (moveId: string, workspaceId: string) => Promise<void>;
  cloneMove: (moveId: string, workspaceId: string) => Promise<Move | null>;

  setPendingMove: (move: Partial<Move> | null) => void;

  getMoveById: (moveId: string) => Move | undefined;
  getActiveMoves: () => Move[];
  getCompletedMoves: () => Move[];
  getDraftMoves: () => Move[];
}

export const useMovesStore = create<MovesState>((set, get) => ({
  moves: [],
  pendingMove: null,
  isLoading: false,
  error: null,

  fetchMoves: async (workspaceId) => {
    set({ isLoading: true, error: null });
    try {
      const moves = await movesService.list(workspaceId);
      set({ moves });
    } catch (err: any) {
      console.error("Error fetching moves:", err);
      set({ moves: [], error: err?.message || "Failed to fetch moves" });
    } finally {
      set({ isLoading: false });
    }
  },

  addMove: async (move, workspaceId) => {
    // Optimistic insert
    set((state) => ({ moves: [move, ...state.moves], error: null }));

    try {
      await movesService.create(workspaceId, move);
    } catch (err: any) {
      console.error("Error adding move:", err);
      // Revert
      set((state) => ({
        moves: state.moves.filter((m) => m.id !== move.id),
        error: err?.message || "Failed to add move",
      }));
      throw err;
    }
  },

  updateMove: async (moveId, updates, workspaceId) => {
    const prev = get().moves;
    set((state) => ({
      moves: state.moves.map((m) => (m.id === moveId ? { ...m, ...updates } : m)),
      error: null,
    }));

    try {
      await movesService.update(workspaceId, moveId, updates);
    } catch (err: any) {
      console.error("Error updating move:", err);
      set({ moves: prev, error: err?.message || "Failed to update move" });
      throw err;
    }
  },

  deleteMove: async (moveId, workspaceId) => {
    const prev = get().moves;
    set((state) => ({ moves: state.moves.filter((m) => m.id !== moveId), error: null }));

    try {
      await movesService.delete(workspaceId, moveId);
    } catch (err: any) {
      console.error("Error deleting move:", err);
      set({ moves: prev, error: err?.message || "Failed to delete move" });
      throw err;
    }
  },

  cloneMove: async (moveId, workspaceId) => {
    const original = get().moves.find((m) => m.id === moveId);
    if (!original) return null;

    const clonedMove: Move = {
      ...original,
      id: crypto.randomUUID(),
      name: `${original.name} (Copy)`,
      status: "draft",
      createdAt: new Date().toISOString(),
      startDate: undefined,
      endDate: undefined,
      progress: 0,
      execution: (original.execution || []).map((day) => ({
        ...day,
        pillarTask: { ...day.pillarTask, id: `pillar-${crypto.randomUUID()}`, status: "pending" },
        clusterActions: (day.clusterActions || []).map((action) => ({
          ...action,
          id: `cluster-${crypto.randomUUID()}`,
          status: "pending",
        })),
        networkAction: {
          ...day.networkAction,
          id: `network-${crypto.randomUUID()}`,
          status: "pending",
        },
      })),
      workspaceId,
    };

    await get().addMove(clonedMove, workspaceId);
    return clonedMove;
  },

  setPendingMove: (move) => set({ pendingMove: move }),

  getMoveById: (moveId) => get().moves.find((m) => m.id === moveId),
  getActiveMoves: () => get().moves.filter((m) => m.status === "active"),
  getCompletedMoves: () => get().moves.filter((m) => m.status === "completed"),
  getDraftMoves: () => get().moves.filter((m) => m.status === "draft"),
}));
