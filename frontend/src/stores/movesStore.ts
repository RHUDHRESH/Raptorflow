/* ══════════════════════════════════════════════════════════════════════════════
   MOVES STORE — Global State Management for Moves
   Zustand store enabling cross-module integration
   ══════════════════════════════════════════════════════════════════════════════ */

import { create } from "zustand";
import { persist } from "zustand/middleware";
import { Move, MoveCategory, ExecutionDay } from "@/components/moves/types";
import { SAMPLE_MOVES } from "@/components/moves/mockMoves";
import { apiClient } from "@/lib/api/client";

interface MovesState {
    // State
    moves: Move[];
    pendingMove: Partial<Move> | null;
    isLoading: boolean;

    // Actions
    fetchMoves: () => Promise<void>;
    fetchDailyAgenda: () => Promise<any[]>;
    addMove: (move: Move) => void;
    updateMove: (moveId: string, updates: Partial<Move>) => void;
    updateMoveStatus: (moveId: string, status: Move['status']) => void;
    deleteMove: (moveId: string) => void;
    archiveMove: (moveId: string) => void;
    cloneMove: (moveId: string) => Move | null;

    // Task Management
    toggleTaskStatus: (
        moveId: string,
        dayIndex: number,
        taskType: "pillar" | "cluster" | "network",
        taskIndex: number
    ) => void;
    updateBackendTaskStatus: (taskId: string, status: string) => Promise<void>;
    updateTaskNote: (
        moveId: string,
        dayIndex: number,
        taskType: "pillar" | "cluster" | "network",
        taskIndex: number,
        note: string
    ) => void;

    // Cross-Module
    setPendingMove: (move: Partial<Move> | null) => void;
    generateStrategy: (data: {
        focusArea: string;
        volatilityLevel: number;
        workspaceId: string;
        userId: string;
    }) => Promise<any>;
    createMoveFromStrategy: (strategyId: string, data: {
        workspaceId: string;
        userId: string;
        name: string;
    }) => Promise<string>;

    // Utilities
    getMoveById: (moveId: string) => Move | undefined;
    getActiveMoves: () => Move[];
    getCompletedMoves: () => Move[];
    getDraftMoves: () => Move[];
}

export const useMovesStore = create<MovesState>()(
    persist(
        (set, get) => ({
            // Initial state - start with sample moves
            moves: SAMPLE_MOVES,
            pendingMove: null,
            isLoading: false,

            // Fetch moves from backend
            fetchMoves: async () => {
                set({ isLoading: true });
                try {
                    const response = await fetch('/api/v1/moves/');
                    if (!response.ok) throw new Error('Failed to fetch moves');
                    const data = await response.json();
                    set({ moves: data });
                } catch (error) {
                    console.error("Fetch moves failed:", error);
                } finally {
                    set({ isLoading: false });
                }
            },

            // Fetch calendar events
            fetchDailyAgenda: async () => {
                const response = await fetch('/api/v1/moves/calendar/events');
                const data = await response.json();
                return data.moves || [];
            },

            // Add a new move
            addMove: async (move) => {
                try {
                    const response = await fetch('/api/v1/moves/', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            name: move.name,
                            category: move.category,
                            goal: move.goal,
                            status: move.status,
                            duration_days: move.duration
                        })
                    });
                    
                    if (!response.ok) throw new Error('Failed to create move');
                    
                    const created = await response.json();
                    
                    set((state) => ({
                        moves: [...state.moves, { ...move, id: created.id }],
                    }));
                } catch (error) {
                    console.error("Move persistence failed:", error);
                    // Fallback to local
                    set((state) => ({
                        moves: [...state.moves, move],
                    }));
                }
            },

            // Update Backend Task Status (Industrial Sync)
            updateBackendTaskStatus: async (taskId, status) => {
                await apiClient.updateTaskStatus(taskId, status);
                // After backend update, we could optionally re-fetch or update locally
            },

            // Update an existing move
            updateMove: (moveId, updates) => {
                set((state) => ({
                    moves: state.moves.map((m) =>
                        m.id === moveId ? { ...m, ...updates } : m
                    ),
                }));
            },

            // Update move status with automatic start date handling
            updateMoveStatus: (moveId, status) => {
                set((state) => ({
                    moves: state.moves.map((m) => {
                        if (m.id !== moveId) return m;
                        const updates: Partial<Move> = { status };
                        if (status === 'active' && !m.startDate) {
                            updates.startDate = new Date().toISOString();
                        }
                        if (status === 'completed') {
                            updates.endDate = new Date().toISOString();
                        }
                        return { ...m, ...updates };
                    }),
                }));
            },

            // Delete a move
            deleteMove: (moveId) => {
                set((state) => ({
                    moves: state.moves.filter((m) => m.id !== moveId),
                }));
            },

            // Archive a move (set status to completed)
            archiveMove: (moveId) => {
                const move = get().getMoveById(moveId);
                if (move) {
                    get().updateMove(moveId, {
                        status: "completed",
                        endDate: new Date().toISOString(),
                    });
                }
            },

            // Clone a move
            cloneMove: (moveId) => {
                const original = get().getMoveById(moveId);
                if (!original) return null;

                const clonedMove: Move = {
                    ...original,
                    id: `mov-${Date.now()}`,
                    name: `${original.name} (Copy)`,
                    status: "draft",
                    createdAt: new Date().toISOString(),
                    startDate: undefined,
                    endDate: undefined,
                    progress: 0,
                    execution: original.execution.map((day) => ({
                        ...day,
                        pillarTask: { ...day.pillarTask, id: `pillar-${Date.now()}-${day.day}`, status: "pending" },
                        clusterActions: day.clusterActions.map((action, i) => ({
                            ...action,
                            id: `cluster-${Date.now()}-${day.day}-${i}`,
                            status: "pending",
                        })),
                        networkAction: {
                            ...day.networkAction,
                            id: `network-${Date.now()}-${day.day}`,
                            status: "pending",
                        },
                    })),
                };

                get().addMove(clonedMove);
                return clonedMove;
            },

            // Toggle task status
            toggleTaskStatus: (moveId, dayIndex, taskType, taskIndex) => {
                set((state) => ({
                    moves: state.moves.map((move) => {
                        if (move.id !== moveId) return move;

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

                        return {
                            ...move,
                            execution: updatedExecution,
                            progress: Math.round((completedTasks / totalTasks) * 100),
                        };
                    }),
                }));
            },

            // Update task note
            updateTaskNote: (moveId, dayIndex, taskType, taskIndex, note) => {
                set((state) => ({
                    moves: state.moves.map((move) => {
                        if (move.id !== moveId) return move;

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
                        return { ...move, execution: updatedExecution };
                    }),
                }));
            },

            // Set pending move (for cross-module handoff)
            setPendingMove: (move) => {
                set({ pendingMove: move });
            },

            // Generate strategy from BlackBox API
            generateStrategy: async (data) => {
                set({ isLoading: true });
                try {
                    const response = await apiClient.generateBlackBoxStrategy({
                        focus_area: data.focusArea,
                        business_context: "Autonomous strategy generation requested from Blackbox Engine.",
                        risk_tolerance: data.volatilityLevel,
                        workspace_id: data.workspaceId,
                        user_id: data.userId
                    });
                    return response;
                } finally {
                    set({ isLoading: false });
                }
            },

            // Create move from strategy using BlackBox API
            createMoveFromStrategy: async (strategyId, data) => {
                set({ isLoading: true });
                try {
                    const response = await apiClient.acceptBlackBoxStrategy(strategyId, {
                        workspace_id: data.workspaceId,
                        user_id: data.userId,
                        convert_to_move: true,
                        move_name: data.name
                    });
                    
                    const moveId = response.move_id || `mov-${Date.now()}`;
                    // Re-fetch moves to show the new one
                    await get().fetchMoves();
                    return moveId;
                } finally {
                    set({ isLoading: false });
                }
            },

            // Get move by ID
            getMoveById: (moveId) => get().moves.find((m) => m.id === moveId),

            // Get active moves
            getActiveMoves: () => get().moves.filter((m) => m.status === "active"),

            // Get completed moves
            getCompletedMoves: () => get().moves.filter((m) => m.status === "completed"),

            // Get draft moves
            getDraftMoves: () => get().moves.filter((m) => m.status === "draft"),
        }),
        {
            name: "raptorflow-moves-storage",
            partialize: (state) => ({ moves: state.moves }),
        }
    )
);
