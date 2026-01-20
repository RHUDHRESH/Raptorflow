"use client";

import { useState, useMemo, useEffect } from "react";
import { Check, Calendar, Zap, Share2, MessageSquare, Layers, ArrowUpRight, TrendingUp, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";
import { useMovesStore } from "@/stores/movesStore";
import { Move, TaskItem, MOVE_CATEGORIES } from "./types";
import { TaskDetailPopup } from "./TaskDetailPopup";

/* ══════════════════════════════════════════════════════════════════════════════
   TODAY'S AGENDA — Command Center with Task Popup
   Aggregates tasks from ALL moves into a single prioritized execution list.
   ══════════════════════════════════════════════════════════════════════════════ */

interface TodaysAgendaProps {
    onMoveClick?: (move: Move) => void;
}

interface FlattenedTask {
    uniqueId: string;
    moveId: string;
    moveName: string;
    moveCategory: string;
    campaignId?: string;
    dayNumber: number;
    totalDays: number;
    task: TaskItem;
    taskType: 'pillar' | 'cluster' | 'network';
}

export function TodaysAgenda({ onMoveClick }: TodaysAgendaProps) {
    const { moves, fetchDailyAgenda, updateBackendTaskStatus } = useMovesStore();
    const [selectedTask, setSelectedTask] = useState<FlattenedTask | null>(null);
    const [realTasks, setRealTasks] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    // --- ABSOLUTE INFINITY: FETCH REAL AGENDA ---
    useEffect(() => {
        async function loadAgenda() {
            setLoading(true);
            const agenda = await fetchDailyAgenda();
            setRealTasks(agenda);
            setLoading(false);
        }
        loadAgenda();
    }, [fetchDailyAgenda]);

    const toggleTaskStatus = async (moveId: string, taskId: string, currentStatus: string) => {
        const newStatus = currentStatus === 'done' ? 'pending' : 'done';
        
        // 1. Update Backend (Triggering potential pushback logic)
        await updateBackendTaskStatus(taskId, newStatus);
        
        // 2. Optimistic local update
        setRealTasks(prev => prev.map(t => 
            t.id === taskId ? { ...t, status: newStatus } : t
        ));
    };

    const getTaskIcon = (type: 'pillar' | 'cluster' | 'network') => {
        switch (type) {
            case 'pillar': return <Zap size={14} className="text-blue-600" />;
            case 'cluster': return <Share2 size={14} className="text-[var(--muted)]" />;
            case 'network': return <MessageSquare size={14} className="text-green-600" />;
        }
    };

    const handleTaskClick = (task: FlattenedTask) => {
        setSelectedTask(task);
    };

    const getSelectedMove = () => {
        if (!selectedTask) return null;
        return moves.find(m => m.id === selectedTask.moveId) || null;
    };

    if (loading) {
        return <div className="p-8 text-center text-[var(--muted)]">Synchronizing Strategic Pulse...</div>;
    }

    if (realTasks.length === 0) {
        return (
            <div className="p-8 border border-dashed border-[var(--border)] rounded-[var(--radius-lg)] bg-[var(--surface)] text-center">
                <Calendar className="w-10 h-10 mx-auto mb-3 text-[var(--muted)]" />
                <h3 className="font-serif text-lg text-[var(--ink)] mb-1">No tasks for today</h3>
                <p className="text-sm text-[var(--muted)]">Create an active move to see your agenda.</p>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* ... rest of the header ... */}
            <div className="space-y-2">
                {realTasks.map((t) => {
                    const category = MOVE_CATEGORIES[t.moves?.category as keyof typeof MOVE_CATEGORIES];

                    return (
                        <div
                            key={t.id}
                            onClick={() => setSelectedTask(t)}
                            className={cn(
                                "group flex items-center justify-between p-3 rounded-[var(--radius)] border bg-[var(--paper)] transition-all cursor-pointer",
                                t.status === 'completed'
                                    ? "border-[var(--border)] opacity-60 bg-[var(--surface)]"
                                    : "border-[var(--border)] hover:border-blue-400 hover:shadow-md"
                            )}
                        >
                            {/* LEFT: Task Execution */}
                            <div className="flex items-center gap-3 flex-1">
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        toggleTaskStatus(t.move_id, t.id, t.status);
                                    }}
                                    className={cn(
                                        "w-6 h-6 rounded-full border-2 flex items-center justify-center transition-colors shrink-0",
                                        t.status === 'completed'
                                            ? "bg-green-600 border-green-600"
                                            : "border-[var(--border)] bg-[var(--paper)] group-hover:border-[var(--ink)]"
                                    )}
                                >
                                    {t.status === 'completed' && <Check size={12} className="text-white" strokeWidth={3} />}
                                </button>

                                <div className="min-w-0 flex-1">
                                    <div className="flex items-center gap-2 mb-0.5">
                                        {getTaskIcon(t.task_type)}
                                        <p className={cn(
                                            "text-sm font-medium truncate",
                                            t.status === 'completed' ? "text-[var(--muted)] line-through" : "text-[var(--ink)]"
                                        )}>
                                            {t.payload?.title || "Untitled Task"}
                                        </p>
                                    </div>
                                    <div className="flex gap-2">
                                        {t.payload?.channel && (
                                            <span className="text-[10px] uppercase text-[var(--muted)] font-medium tracking-wider">
                                                ON {t.payload.channel}
                                            </span>
                                        )}
                                    </div>
                                </div>
                            </div>

                            {/* RIGHT: Context */}
                            <div className="flex items-center gap-6 pl-4 border-l border-[var(--border)] ml-4 shrink-0 w-[200px] justify-end">
                                <div className="text-right">
                                    <div className="text-xs font-medium text-[var(--ink)]">
                                        {t.moves?.name}
                                    </div>
                                    <div className="text-[10px] text-[var(--muted)]">
                                        {category?.name || 'Strategic Move'}
                                    </div>
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Task Detail Popup */}
            {selectedTask && getSelectedMove() && (
                <TaskDetailPopup
                    task={selectedTask.task}
                    taskType={selectedTask.taskType}
                    move={getSelectedMove()!}
                    dayNumber={selectedTask.dayNumber}
                    onClose={() => setSelectedTask(null)}
                    onToggleComplete={() => {
                        toggleTaskStatus(selectedTask.moveId, selectedTask.task.id, selectedTask.task.status);
                        setSelectedTask(null);
                    }}
                    onViewMove={() => {
                        const move = getSelectedMove();
                        if (move) {
                            onMoveClick?.(move);
                            setSelectedTask(null);
                        }
                    }}
                />
            )}
        </div>
    );
}

export default TodaysAgenda;
