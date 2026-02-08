"use client";

import { useState, useMemo } from "react";
import { Check, Calendar, Zap, Share2, MessageSquare, Layers, ArrowUpRight, TrendingUp, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";
import { useMovesStore } from "@/stores/movesStore";
import { Move, TaskItem, MOVE_CATEGORIES } from "./types";
import { TaskDetailPopup } from "./TaskDetailPopup";
import { useWorkspace } from "@/components/workspace/WorkspaceProvider";
import { toast } from "sonner";

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
  const { moves, updateMove } = useMovesStore();
  const { workspaceId } = useWorkspace();
  const [selectedTask, setSelectedTask] = useState<FlattenedTask | null>(null);

    // Get today's date for comparison
    const today = useMemo(() => {
        const now = new Date();
        now.setHours(0, 0, 0, 0);
        return now;
    }, []);

    // Flatten all tasks from active moves into a single list
    const allTasks = useMemo(() => {
        const activeMoves = moves.filter(m => m.status === 'active' && m.startDate);
        const tasks: FlattenedTask[] = [];

        activeMoves.forEach(move => {
            if (!move.startDate || !move.execution?.length) return;

            const startDate = new Date(move.startDate);
            startDate.setHours(0, 0, 0, 0);

            const daysSinceStart = Math.floor(
                (today.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24)
            );
            const dayNumber = daysSinceStart + 1;

            // Check validity
            if (dayNumber < 1 || dayNumber > move.duration) return;

            const dayExecution = move.execution[dayNumber - 1];
            if (!dayExecution) return;

            // Helper to push task
            const pushTask = (t: TaskItem, type: 'pillar' | 'cluster' | 'network') => {
                tasks.push({
                    uniqueId: `${move.id}-${t.id}`,
                    moveId: move.id,
                    moveName: move.name,
                    moveCategory: move.category,
                    campaignId: move.campaignId,
                    dayNumber,
                    totalDays: move.duration,
                    task: t,
                    taskType: type
                });
            };

            // Add tasks
            if (dayExecution.pillarTask) pushTask(dayExecution.pillarTask, 'pillar');
            dayExecution.clusterActions?.forEach(t => pushTask(t, 'cluster'));
            if (dayExecution.networkAction) pushTask(dayExecution.networkAction, 'network');
        });

        // Sort: Pending first, then by Move Priority (implied), then Done
        return tasks.sort((a, b) => {
            if (a.task.status === b.task.status) return 0;
            return a.task.status === 'done' ? 1 : -1;
        });
    }, [moves, today]);

    // Calculate progress
    const progress = useMemo(() => {
        if (allTasks.length === 0) return { total: 0, completed: 0, percentage: 0 };
        const completed = allTasks.filter(t => t.task.status === 'done').length;
        return {
            total: allTasks.length,
            completed,
            percentage: Math.round((completed / allTasks.length) * 100)
        };
    }, [allTasks]);

  const toggleTaskStatus = (moveId: string, taskId: string, currentStatus: string) => {
    const move = moves.find(m => m.id === moveId);
    if (!move || !workspaceId) return;

        const updatedExecution = move.execution.map(day => ({
            ...day,
            pillarTask: day.pillarTask.id === taskId
                ? { ...day.pillarTask, status: currentStatus === 'done' ? 'pending' as const : 'done' as const }
                : day.pillarTask,
            clusterActions: day.clusterActions.map(t =>
                t.id === taskId
                    ? { ...t, status: currentStatus === 'done' ? 'pending' as const : 'done' as const }
                    : t
            ),
            networkAction: day.networkAction.id === taskId
                ? { ...day.networkAction, status: currentStatus === 'done' ? 'pending' as const : 'done' as const }
                : day.networkAction
        }));

        void updateMove(moveId, { execution: updatedExecution }, workspaceId).catch((err: any) => {
            console.error("Failed to update move execution:", err);
            toast.error(err?.message || "Failed to update task");
        });
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

    if (allTasks.length === 0) {
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
            {/* Header */}
            <div className="flex items-center justify-between bg-[var(--paper)] p-4 rounded-[var(--radius-lg)] border border-[var(--border)] shadow-sm">
                <div className="flex items-center gap-4">
                    <div className="relative w-12 h-12 flex items-center justify-center">
                        <svg className="w-full h-full transform -rotate-90">
                            <circle cx="24" cy="24" r="20" className="stroke-[var(--surface)]" strokeWidth="4" fill="none" />
                            <circle
                                cx="24" cy="24" r="20"
                                className="stroke-[var(--ink)] transition-all duration-1000 ease-out"
                                strokeWidth="4"
                                fill="none"
                                strokeDasharray={126}
                                strokeDashoffset={126 - (126 * progress.percentage) / 100}
                            />
                        </svg>
                        <div className="absolute inset-0 flex items-center justify-center text-xs font-bold">{progress.percentage}%</div>
                    </div>
                    <div>
                        <h2 className="font-serif text-xl text-[var(--ink)]">Today's Agenda</h2>
                        <p className="text-xs text-[var(--muted)]">
                            {progress.completed} of {progress.total} tasks completed
                        </p>
                    </div>
                </div>
                <div className="flex flex-col items-end">
                    <div className="flex items-center gap-2 text-xs font-medium text-green-700 bg-green-50 px-2.5 py-1 rounded-full border border-green-200">
                        <TrendingUp size={12} />
                        High Velocity
                    </div>
                </div>
            </div>

            {/* Flattened Task List */}
            <div className="space-y-2">
                {allTasks.map((t) => {
                    const move = moves.find(m => m.id === t.moveId);
                    const category = MOVE_CATEGORIES[t.moveCategory as keyof typeof MOVE_CATEGORIES];

                    return (
                        <div
                            key={t.uniqueId}
                            onClick={() => handleTaskClick(t)}
                            className={cn(
                                "group flex items-center justify-between p-3 rounded-[var(--radius)] border bg-[var(--paper)] transition-all cursor-pointer",
                                t.task.status === 'done'
                                    ? "border-[var(--border)] opacity-60 bg-[var(--surface)]"
                                    : "border-[var(--border)] hover:border-blue-400 hover:shadow-md"
                            )}
                        >
                            {/* LEFT: Task Execution */}
                            <div className="flex items-center gap-3 flex-1">
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        toggleTaskStatus(t.moveId, t.task.id, t.task.status);
                                    }}
                                    className={cn(
                                        "w-6 h-6 rounded-full border-2 flex items-center justify-center transition-colors shrink-0",
                                        t.task.status === 'done'
                                            ? "bg-green-600 border-green-600"
                                            : "border-[var(--border)] bg-[var(--paper)] group-hover:border-[var(--ink)]"
                                    )}
                                >
                                    {t.task.status === 'done' && <Check size={12} className="text-white" strokeWidth={3} />}
                                </button>

                                <div className="min-w-0 flex-1">
                                    <div className="flex items-center gap-2 mb-0.5">
                                        {getTaskIcon(t.taskType)}
                                        <p className={cn(
                                            "text-sm font-medium truncate",
                                            t.task.status === 'done' ? "text-[var(--muted)] line-through" : "text-[var(--ink)]"
                                        )}>
                                            {t.task.title}
                                        </p>
                                    </div>
                                    <div className="flex gap-2">
                                        {t.task.channel && (
                                            <span className="text-[10px] uppercase text-[var(--muted)] font-medium tracking-wider">
                                                ON {t.task.channel}
                                            </span>
                                        )}
                                        {t.task.description && (
                                            <span className="text-[10px] text-[var(--muted)] truncate max-w-[200px]">
                                                — {t.task.description}
                                            </span>
                                        )}
                                    </div>
                                </div>

                                {/* Muse Hint */}
                                <div className="opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1 text-xs text-purple-600 bg-purple-50 px-2 py-1 rounded-full">
                                    <Sparkles size={10} />
                                    Ask Muse
                                </div>
                            </div>

                            {/* RIGHT: Context (Move & Campaign) */}
                            <div className="flex items-center gap-6 pl-4 border-l border-[var(--border)] ml-4 shrink-0 w-[200px] justify-end">
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        move && onMoveClick?.(move);
                                    }}
                                    className="text-right group/move"
                                >
                                    <div className="flex items-center justify-end gap-1.5 text-xs font-medium text-[var(--ink)] group-hover/move:text-blue-600 transition-colors">
                                        {t.moveName}
                                        <ArrowUpRight size={10} className="opacity-0 group-hover/move:opacity-100 transition-opacity" />
                                    </div>
                                    <div className="flex items-center justify-end gap-1 text-[10px] text-[var(--muted)]">
                                        <span>{category?.name || 'Move'}</span>
                                        <span>•</span>
                                        <span>Day {t.dayNumber}</span>
                                    </div>
                                </button>

                                {t.campaignId && (
                                    <div className="hidden sm:block">
                                        <div className="w-8 h-8 rounded bg-green-50 text-green-600 flex items-center justify-center border border-green-200">
                                            <Layers size={14} />
                                        </div>
                                    </div>
                                )}
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
