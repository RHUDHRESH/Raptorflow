/* ══════════════════════════════════════════════════════════════════════════════
   MOVES STORE — Global State Management for Moves
   Zustand store enabling cross-module integration
   ══════════════════════════════════════════════════════════════════════════════ */

import { create } from "zustand";
import { persist } from "zustand/middleware";
import { Move, MoveCategory, ExecutionDay } from "@/components/moves/types";
import { SAMPLE_MOVES } from "@/components/moves/mockMoves";

interface MovesState {
    // State
    moves: Move[];
    pendingMove: Partial<Move> | null;

    // Actions
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
    updateTaskNote: (
        moveId: string,
        dayIndex: number,
        taskType: "pillar" | "cluster" | "network",
        taskIndex: number,
        note: string
    ) => void;

    // Cross-Module
    setPendingMove: (move: Partial<Move> | null) => void;
    createMoveFromBlackBox: (data: {
        focusArea: string;
        desiredOutcome: string;
        volatilityLevel: number;
        name: string;
        steps: string[];
    }) => string;

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

            // Add a new move
            addMove: (move) => {
                set((state) => ({
                    moves: [...state.moves, move],
                }));
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

            // Create move from BlackBox data
            createMoveFromBlackBox: (data) => {
                const categoryMap: Record<string, MoveCategory> = {
                    "Acquisition / Growth": "capture",
                    "Retention / Loyalty": "rally",
                    "Monetization / Cash": "capture",
                    "Brand / PR": "authority",
                    "Product / Viral": "rally",
                };

                const category = categoryMap[data.focusArea] || "capture";
                const moveId = `mov-${Date.now()}`;

                const execution: ExecutionDay[] = data.steps.map((step, i) => ({
                    day: i + 1,
                    phase: i === 0 ? "Trigger" : i === 1 ? "Pivot" : "Close",
                    pillarTask: {
                        id: `pillar-${moveId}-${i + 1}`,
                        title: step,
                        description: `Step ${i + 1} of experimental move`,
                        status: "pending",
                        channel: "Multi-channel",
                    },
                    clusterActions: [
                        {
                            id: `cluster-${moveId}-${i + 1}-1`,
                            title: "Share on social",
                            description: "",
                            status: "pending",
                            channel: "Social",
                        },
                    ],
                    networkAction: {
                        id: `network-${moveId}-${i + 1}`,
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
                };

                get().addMove(newMove);
                return moveId;
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
