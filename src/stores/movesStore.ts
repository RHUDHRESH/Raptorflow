/* ══════════════════════════════════════════════════════════════════════════════
   MOVES STORE — Global State Management for Moves
   Supabase-backed store with RLS support
   ══════════════════════════════════════════════════════════════════════════════ */

import { create } from "zustand";
import { Move, MoveCategory, ExecutionDay } from "@/components/moves/types";
import { supabase } from "@/lib/supabaseClient";

interface MovesState {
    // State
    moves: Move[];
    pendingMove: Partial<Move> | null;
    isLoading: boolean;
    error: string | null;

    // Actions
    fetchMoves: (userId: string) => Promise<void>;
    addMove: (move: Move, userId: string, workspaceId?: string) => Promise<void>;
    updateMove: (moveId: string, updates: Partial<Move>) => Promise<void>;
    updateMoveStatus: (moveId: string, status: Move['status']) => Promise<void>;
    deleteMove: (moveId: string) => Promise<void>;
    archiveMove: (moveId: string) => Promise<void>;
    cloneMove: (moveId: string, userId: string, workspaceId?: string) => Promise<Move | null>;

    // Task Management
    toggleTaskStatus: (
        moveId: string,
        dayIndex: number,
        taskType: "pillar" | "cluster" | "network",
        taskIndex: number
    ) => Promise<void>;

    updateTaskNote: (
        moveId: string,
        dayIndex: number,
        taskType: "pillar" | "cluster" | "network",
        taskIndex: number,
        note: string
    ) => Promise<void>;

    // Cross-Module
    setPendingMove: (move: Partial<Move> | null) => void;
    createMoveFromBlackBox: (data: {
        focusArea: string;
        desiredOutcome: string;
        volatilityLevel: number;
        name: string;
        steps: string[];
    }, userId: string, workspaceId?: string) => Promise<string>;

    // Utilities
    getMoveById: (moveId: string) => Move | undefined;
    getActiveMoves: () => Move[];
    getCompletedMoves: () => Move[];
    getDraftMoves: () => Move[];
}

export const useMovesStore = create<MovesState>((set, get) => ({
    // Initial state
    moves: [],
    pendingMove: null,
    isLoading: false,
    error: null,

    // Fetch moves from Supabase
    fetchMoves: async (userId: string) => {
        set({ isLoading: true, error: null });
        try {
            const { data, error } = await supabase
                .from('moves')
                .select('*')
                .eq('user_id', userId)
                .order('created_at', { ascending: false });

            if (error) throw error;

            // Transform data if needed (assuming DB structure matches Move type closely)
            set({ moves: (data as unknown as Move[]) || [] });
        } catch (err: any) {
            console.error('Error fetching moves:', err);
            set({ error: err.message });
        } finally {
            set({ isLoading: false });
        }
    },

    // Add a new move
    addMove: async (move, userId, workspaceId) => {
        // Optimistic update
        set((state) => ({ moves: [move, ...state.moves] }));

        try {
            // DB Insert
            const payload = { ...move, user_id: userId, workspace_id: workspaceId };
            // Ensure we don't send undefined workspace_id if it's not present (DB might have default or allow null, but safer to omit if undefined)
            if (!workspaceId) delete (payload as any).workspace_id;

            const { error } = await supabase
                .from('moves')
                .insert([payload]);

            if (error) throw error;
        } catch (err: any) {
            console.error('Error adding move:', err);
            // Revert on error
            set((state) => ({ moves: state.moves.filter(m => m.id !== move.id), error: err.message }));
        }
    },

    // Update an existing move
    updateMove: async (moveId, updates) => {
        set((state) => ({
            moves: state.moves.map((m) =>
                m.id === moveId ? { ...m, ...updates } : m
            ),
        }));

        try {
            const { error } = await supabase
                .from('moves')
                .update(updates)
                .eq('id', moveId);

            if (error) throw error;
        } catch (err: any) {
            console.error('Error updating move:', err);
            // Should properly revert here in prod, simplified for now
            set({ error: err.message });
        }
    },

    // Update move status
    updateMoveStatus: async (moveId, status) => {
        const move = get().getMoveById(moveId);
        if (!move) return;

        const updates: Partial<Move> = { status };
        if (status === 'active' && !move.startDate) {
            updates.startDate = new Date().toISOString();
        }
        if (status === 'completed') {
            updates.endDate = new Date().toISOString();
        }

        await get().updateMove(moveId, updates);
    },

    // Delete a move
    deleteMove: async (moveId) => {
        const previousMoves = get().moves;
        set((state) => ({
            moves: state.moves.filter((m) => m.id !== moveId),
        }));

        try {
            const { error } = await supabase
                .from('moves')
                .delete()
                .eq('id', moveId);

            if (error) throw error;
        } catch (err: any) {
            console.error('Error deleting move:', err);
            set({ moves: previousMoves, error: err.message });
        }
    },

    // Archive a move
    archiveMove: async (moveId) => {
        await get().updateMoveStatus(moveId, "completed");
    },

    // Clone a move
    cloneMove: async (moveId, userId, workspaceId) => {
        const original = get().getMoveById(moveId);
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
            execution: original.execution.map((day) => ({
                ...day,
                pillarTask: { ...day.pillarTask, id: `pillar-${crypto.randomUUID()}`, status: "pending" },
                clusterActions: day.clusterActions.map((action, i) => ({
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
            workspaceId: workspaceId
        };

        await get().addMove(clonedMove, userId, workspaceId);
        return clonedMove;
    },

    // Toggle task status
    toggleTaskStatus: async (moveId, dayIndex, taskType, taskIndex) => {
        // Simple optimistic logic - in a real app, you'd sync the specific JSON path or entire execution array
        const move = get().getMoveById(moveId);
        if (!move) return;

        const updatedExecution = [...move.execution];
        const day = { ...updatedExecution[dayIndex] };

        if (taskType === "pillar") {
            day.pillarTask = {
                ...day.pillarTask,
                status: day.pillarTask.status === "done" ? "pending" : "done",
            };
        } else if (taskType === "cluster") {
            day.clusterActions = day.clusterActions.map((action, i) =>
                i === taskIndex
                    ? { ...action, status: action.status === "done" ? "pending" : "done" }
                    : action
            );
        } else if (taskType === "network") {
            day.networkAction = {
                ...day.networkAction,
                status: day.networkAction.status === "done" ? "pending" : "done",
            };
        }

        updatedExecution[dayIndex] = day;

        // Calculate new progress
        const totalTasks = updatedExecution.reduce(
            (acc, d) => acc + 1 + d.clusterActions.length + 1,
            0
        );
        const completedTasks = updatedExecution.reduce(
            (acc, d) =>
                acc +
                (d.pillarTask.status === "done" ? 1 : 0) +
                d.clusterActions.filter((a) => a.status === "done").length +
                (d.networkAction.status === "done" ? 1 : 0),
            0
        );

        const progress = Math.round((completedTasks / totalTasks) * 100);
        const updates = { execution: updatedExecution, progress };

        set((state) => ({
            moves: state.moves.map((m) =>
                m.id === moveId ? { ...m, ...updates } : m
            ),
        }));

        // Persist to DB
        try {
            const { error } = await supabase
                .from('moves')
                .update(updates)
                .eq('id', moveId);
            if (error) throw error;
        } catch (err: any) {
            console.error("Task update failed", err);
            set({ error: err.message });
        }
    },

    updateTaskNote: async (moveId, dayIndex, taskType, taskIndex, note) => {
        const move = get().getMoveById(moveId);
        if (!move) return;

        const updatedExecution = [...move.execution];
        const day = { ...updatedExecution[dayIndex] };

        if (taskType === "pillar") {
            day.pillarTask = { ...day.pillarTask, note };
        } else if (taskType === "cluster") {
            day.clusterActions = day.clusterActions.map((action, i) =>
                i === taskIndex ? { ...action, note } : action
            );
        } else if (taskType === "network") {
            day.networkAction = { ...day.networkAction, note };
        }

        updatedExecution[dayIndex] = day;
        const updates = { execution: updatedExecution };

        // Optimistic
        set((state) => ({
            moves: state.moves.map((m) =>
                m.id === moveId ? { ...m, ...updates } : m
            ),
        }));

        // Persist
        try {
            const { error } = await supabase
                .from('moves')
                .update(updates)
                .eq('id', moveId);
            if (error) throw error;
        } catch (err: any) {
            console.error("Note update failed", err);
            set({ error: err.message });
        }
    },

    setPendingMove: (move) => {
        set({ pendingMove: move });
    },

    createMoveFromBlackBox: async (data, userId, workspaceId) => {
        const categoryMap: Record<string, MoveCategory> = {
            "Acquisition / Growth": "capture",
            "Retention / Loyalty": "rally",
            "Monetization / Cash": "capture",
            "Brand / PR": "authority",
            "Product / Viral": "rally",
        };

        const category = categoryMap[data.focusArea] || "capture";
        const moveId = crypto.randomUUID();

        const execution: ExecutionDay[] = data.steps.map((step, i) => ({
            day: i + 1,
            phase: i === 0 ? "Trigger" : i === 1 ? "Pivot" : "Close",
            pillarTask: {
                id: `pillar-${crypto.randomUUID()}`,
                title: step,
                description: `Step ${i + 1} of experimental move`,
                status: "pending",
                channel: "Multi-channel",
            },
            clusterActions: [
                {
                    id: `cluster-${crypto.randomUUID()}`,
                    title: "Share on social",
                    description: "",
                    status: "pending",
                    channel: "Social",
                },
            ],
            networkAction: {
                id: `network-${crypto.randomUUID()}`,
                title: "DM 5 prospects",
                description: "",
                status: "pending",
                channel: "DM",
            },
        }));

        const newMove: Move = {
            id: moveId,
            name: data.name,
            category,
            status: "draft",
            duration: data.steps.length,
            goal: data.desiredOutcome,
            tone: data.volatilityLevel > 7 ? "Aggressive" : "Strategic",
            context: `Focus: ${data.focusArea}. Outcome: ${data.desiredOutcome}. Volatility: ${data.volatilityLevel}/10`,
            createdAt: new Date().toISOString(),
            progress: 0,
            execution,
            workspaceId: workspaceId
        };

        await get().addMove(newMove, userId, workspaceId);
        return moveId;
    },

    getMoveById: (moveId) => get().moves.find((m) => m.id === moveId),
    getActiveMoves: () => get().moves.filter((m) => m.status === "active"),
    getCompletedMoves: () => get().moves.filter((m) => m.status === "completed"),
    getDraftMoves: () => get().moves.filter((m) => m.status === "draft"),
}));

