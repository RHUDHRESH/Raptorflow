"use client";

import { useState, useRef, useEffect } from "react";
import { Move, TaskItem, ExecutionDay, MOVE_CATEGORIES, TaskStatus } from "./types";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintModal } from "@/components/ui/BlueprintModal";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { BlueprintButton } from "@/components/ui/BlueprintButton";
import { Check, Circle, Zap, Share2, MessageSquare, Clock, ArrowRight, Target, Layout, User, Sparkles, Trophy } from "lucide-react";
import { cn } from "@/lib/utils";
import { useMovesStore } from "@/stores/movesStore";
import gsap from "gsap";

/* ══════════════════════════════════════════════════════════════════════════════
   DAILY TASK BOARD — RAPTORFLOW PREMIUM
   Aggregated view of all tasks for today with quick actions and animations
   ══════════════════════════════════════════════════════════════════════════════ */

interface DailyTaskBoardProps {
    moves: Move[];
    searchQuery?: string;
}

interface EnrichedTask {
    task: TaskItem;
    move: Move;
    dayNumber: number;
    phase: string;
    type: 'pillar' | 'cluster' | 'network';
    dayIndex: number;
    subIndex: number;
}

// Estimated time per task type
const TIME_ESTIMATES = {
    pillar: '45-60 min',
    cluster: '10-15 min',
    network: '15-20 min',
};

const TYPE_COLORS = {
    pillar: 'text-[var(--blueprint)]',
    cluster: 'text-[var(--ink-secondary)]',
    network: 'text-[var(--success)]',
};

export function DailyTaskBoard({ moves, searchQuery = "" }: DailyTaskBoardProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const [selectedTask, setSelectedTask] = useState<EnrichedTask | null>(null);
    const [celebrateTask, setCelebrateTask] = useState<string | null>(null);
    const { toggleTaskStatus } = useMovesStore();

    const today = new Date();
    const q = searchQuery.toLowerCase();

    // Filter moves first based on search
    const activeMoves = moves.filter(m => {
        const matchesSearch = !q || m.name.toLowerCase().includes(q) || m.category.toLowerCase().includes(q);
        return m.status === 'active' && m.startDate && matchesSearch;
    });

    const todaysTasks: EnrichedTask[] = activeMoves.flatMap(move => {
        if (!move.startDate) return [];

        const startDate = new Date(move.startDate);
        const diffTime = today.getTime() - startDate.getTime();
        const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24)) + 1;

        if (diffDays < 1 || diffDays > move.duration) return [];

        const dayIndex = diffDays - 1;
        const execution = move.execution[dayIndex];
        const dayNumber = diffDays;

        if (!execution) return [];

        const tasks: EnrichedTask[] = [];

        // Pillar (most important, show first)
        tasks.push({
            task: execution.pillarTask,
            move,
            dayNumber,
            phase: execution.phase,
            type: 'pillar',
            dayIndex,
            subIndex: 0
        });

        // Cluster
        execution.clusterActions.forEach((task, idx) => {
            tasks.push({
                task,
                move,
                dayNumber,
                phase: execution.phase,
                type: 'cluster',
                dayIndex,
                subIndex: idx
            });
        });

        // Network
        tasks.push({
            task: execution.networkAction,
            move,
            dayNumber,
            phase: execution.phase,
            type: 'network',
            dayIndex,
            subIndex: 0
        });

        return tasks;
    });

    // Sort: Pillar first, then pending before done
    const sortedTasks = [...todaysTasks].sort((a, b) => {
        // Pillar tasks first
        if (a.type === 'pillar' && b.type !== 'pillar') return -1;
        if (a.type !== 'pillar' && b.type === 'pillar') return 1;
        // Then pending before done
        if (a.task.status === 'pending' && b.task.status === 'done') return -1;
        if (a.task.status === 'done' && b.task.status === 'pending') return 1;
        return 0;
    });

    const completedCount = todaysTasks.filter(t => t.task.status === 'done').length;
    const totalCount = todaysTasks.length;
    const progressPercent = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0;

    const handleTaskToggle = (e: React.MouseEvent, enriched: EnrichedTask) => {
        e.stopPropagation();

        // Trigger celebration animation if completing
        if (enriched.task.status !== 'done') {
            setCelebrateTask(`${enriched.move.id}-${enriched.type}-${enriched.task.id}`);
            setTimeout(() => setCelebrateTask(null), 1200);
        }

        toggleTaskStatus(enriched.move.id, enriched.dayIndex, enriched.type, enriched.subIndex);
    };

    const TaskIcon = ({ type, size = 14 }: { type: string, size?: number }) => {
        switch (type) {
            case 'pillar': return <Zap size={size} />;
            case 'cluster': return <Share2 size={size} />;
            case 'network': return <MessageSquare size={size} />;
            default: return <Circle size={size} />;
        }
    };

    // Calculate estimated total time remaining
    const estimatedMinutes = sortedTasks
        .filter(t => t.task.status !== 'done')
        .reduce((acc, t) => {
            const mins = t.type === 'pillar' ? 50 : t.type === 'cluster' ? 12 : 17;
            return acc + mins;
        }, 0);

    const formatTime = (mins: number) => {
        if (mins < 60) return `${mins} min`;
        const hours = Math.floor(mins / 60);
        const remaining = mins % 60;
        return remaining > 0 ? `${hours}h ${remaining}m` : `${hours}h`;
    };

    return (
        <div ref={containerRef} className="space-y-6">
            {/* Header with Progress */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="font-editorial text-2xl text-[var(--ink)]">Today's Tasks</h2>
                    <p className="text-sm text-[var(--ink-secondary)]">
                        {today.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
                    </p>
                </div>
                <div className="text-right">
                    <div className="flex items-center gap-3">
                        <div className="w-32 h-2 bg-[var(--surface)] rounded-full overflow-hidden">
                            <div
                                className="h-full bg-[var(--success)] transition-all duration-700 ease-out"
                                style={{ width: `${progressPercent}%` }}
                            />
                        </div>
                        <span className="font-data text-lg text-[var(--ink)]">
                            {completedCount}/{totalCount}
                        </span>
                    </div>
                    {estimatedMinutes > 0 && (
                        <p className="text-xs text-[var(--muted)] mt-1 flex items-center justify-end gap-1">
                            <Clock size={10} />
                            ~{formatTime(estimatedMinutes)} remaining
                        </p>
                    )}
                </div>
            </div>

            {/* All Done Celebration */}
            {totalCount > 0 && completedCount === totalCount && (
                <div className="bg-gradient-to-r from-[var(--success-light)] to-[var(--blueprint-light)] border border-[var(--success)]/30 rounded-[var(--radius-lg)] p-8 text-center animate-in zoom-in duration-500">
                    <div className="relative inline-block">
                        <Trophy size={40} className="mx-auto mb-4 text-[var(--success)] animate-bounce" />
                        <div className="absolute -top-2 -right-2 w-4 h-4 bg-[var(--warning)] rounded-full animate-ping" />
                    </div>
                    <h3 className="text-xl font-editorial text-[var(--ink)]">All tasks completed! 🎉</h3>
                    <p className="text-sm text-[var(--muted)] mt-2">Great work today. Take a break or check tomorrow's tasks.</p>
                </div>
            )}

            {todaysTasks.length === 0 ? (
                <BlueprintCard className="py-16 text-center border-dashed border-2">
                    <div className="w-16 h-16 bg-[var(--surface)] rounded-full flex items-center justify-center mx-auto mb-6 text-[var(--muted)]">
                        <Sparkles size={28} />
                    </div>
                    <h3 className="text-xl font-editorial text-[var(--ink)]">No tasks for today</h3>
                    <p className="text-sm text-[var(--muted)] mt-2 max-w-sm mx-auto">
                        Start a new move to get daily tasks assigned to your schedule.
                    </p>
                </BlueprintCard>
            ) : (
                <div className="grid gap-3 overflow-y-auto pr-1">
                    {sortedTasks.map((item, idx) => {
                        const isDone = item.task.status === 'done';
                        const categoryInfo = MOVE_CATEGORIES[item.move.category];
                        const taskKey = `${item.move.id}-${item.type}-${item.task.id}`;
                        const isCelebrating = celebrateTask === taskKey;

                        return (
                            <div
                                key={taskKey}
                                onClick={() => setSelectedTask(item)}
                                style={{ animationDelay: `${idx * 50}ms` }}
                                className={cn(
                                    "group relative flex items-center gap-4 p-5 rounded-[var(--radius-lg)] border transition-all duration-300 cursor-pointer",
                                    "animate-in fade-in slide-in-from-left-4",
                                    isDone
                                        ? "bg-[var(--surface-subtle)]/80 border-[var(--border)]"
                                        : item.type === 'pillar'
                                            ? "bg-[var(--paper)] border-[var(--blueprint)]/40 shadow-md hover:shadow-xl hover:border-[var(--blueprint)] hover:-translate-y-0.5"
                                            : "bg-[var(--paper)] border-[var(--border)] hover:shadow-lg hover:border-[var(--blueprint)]/40 hover:-translate-y-0.5",
                                    isCelebrating && "ring-4 ring-[var(--success)]/50 scale-[1.02]"
                                )}
                            >
                                {/* Priority Indicator for Pillar */}
                                {item.type === 'pillar' && !isDone && (
                                    <div className="absolute -left-1 top-1/2 -translate-y-1/2 w-1.5 h-10 bg-gradient-to-b from-[var(--blueprint)] to-[var(--blueprint)]/50 rounded-full" />
                                )}

                                {/* Celebration particles */}
                                {isCelebrating && (
                                    <div className="absolute inset-0 pointer-events-none overflow-hidden rounded-[var(--radius-lg)]">
                                        {[...Array(8)].map((_, i) => (
                                            <div
                                                key={i}
                                                className="absolute w-2 h-2 bg-[var(--success)] rounded-full animate-ping"
                                                style={{
                                                    left: `${10 + i * 12}%`,
                                                    top: `${Math.random() * 100}%`,
                                                    animationDelay: `${i * 100}ms`,
                                                    animationDuration: '800ms'
                                                }}
                                            />
                                        ))}
                                    </div>
                                )}

                                {/* Status Toggle */}
                                <button
                                    onClick={(e) => handleTaskToggle(e, item)}
                                    className={cn(
                                        "w-8 h-8 rounded-full border-2 flex items-center justify-center transition-all duration-300 z-10 shrink-0",
                                        isDone
                                            ? "bg-[var(--success)] border-[var(--success)] text-white scale-100"
                                            : "border-[var(--muted)] hover:border-[var(--success)] hover:bg-[var(--success-light)] hover:scale-110 bg-[var(--paper)]"
                                    )}
                                    title={isDone ? "Mark as pending" : "Mark as done"}
                                >
                                    {isDone && <Check size={16} strokeWidth={3} />}
                                </button>

                                {/* Task Info */}
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2 mb-1.5">
                                        {/* Type Badge */}
                                        <span className={cn(
                                            "flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider px-2 py-1 rounded-md transition-colors",
                                            item.type === 'pillar' && "bg-[var(--blueprint)]/10 text-[var(--blueprint)]",
                                            item.type === 'cluster' && "bg-[var(--surface)] text-[var(--muted)]",
                                            item.type === 'network' && "bg-[var(--success)]/10 text-[var(--success)]"
                                        )}>
                                            <TaskIcon type={item.type} size={10} />
                                            {item.type}
                                        </span>

                                        {/* Move Name */}
                                        <span className="text-[10px] text-[var(--muted)] flex items-center gap-1.5 bg-[var(--surface-subtle)] px-2 py-0.5 rounded">
                                            {categoryInfo.emoji} {item.move.name}
                                        </span>

                                        {/* Channel if exists */}
                                        {item.task.channel && (
                                            <span className="text-[10px] text-[var(--muted)] px-2 py-1 rounded-md bg-[var(--surface)] border border-[var(--border)]">
                                                {item.task.channel}
                                            </span>
                                        )}
                                    </div>

                                    <h3 className={cn(
                                        "font-medium text-[var(--ink)] text-[15px] transition-all leading-snug",
                                        isDone && "line-through text-[var(--muted)]"
                                    )}>
                                        {item.task.title}
                                    </h3>
                                </div>

                                {/* Time Estimate */}
                                <div className={cn(
                                    "text-xs flex items-center gap-1.5 shrink-0 px-3 py-1.5 rounded-lg transition-colors",
                                    isDone ? "text-[var(--muted)] bg-transparent" : "text-[var(--ink-secondary)] bg-[var(--surface-subtle)]"
                                )}>
                                    <Clock size={12} />
                                    {TIME_ESTIMATES[item.type]}
                                </div>

                                {/* Arrow - Slides in on hover */}
                                <ArrowRight size={18} className="text-[var(--border)] group-hover:text-[var(--blueprint)] group-hover:translate-x-1 transition-all shrink-0" />
                            </div>
                        );
                    })}
                </div>
            )}

            {/* TASK DETAIL MODAL */}
            <BlueprintModal
                isOpen={!!selectedTask}
                onClose={() => setSelectedTask(null)}
                title="Task Details"
                code="TSK-01"
                size="md"
            >
                {selectedTask && (
                    <div className="space-y-8">
                        {/* Header Info */}
                        <div className="flex items-start justify-between">
                            <div className="space-y-4">
                                <div className="flex items-center gap-3">
                                    <div className={cn(
                                        "w-12 h-12 rounded-[var(--radius)] flex items-center justify-center",
                                        selectedTask.type === 'pillar' && "bg-[var(--blueprint-light)] text-[var(--blueprint)]",
                                        selectedTask.type === 'cluster' && "bg-[var(--surface)] text-[var(--muted)]",
                                        selectedTask.type === 'network' && "bg-[var(--success-light)] text-[var(--success)]"
                                    )}>
                                        <TaskIcon type={selectedTask.type} size={24} />
                                    </div>
                                    <div>
                                        <span className="text-xs font-semibold uppercase tracking-wider text-[var(--muted)]">
                                            {selectedTask.type} Task
                                        </span>
                                        <h3 className="text-xl font-editorial text-[var(--ink)] leading-tight">
                                            {selectedTask.task.title}
                                        </h3>
                                    </div>
                                </div>

                                <div className="flex flex-wrap gap-2">
                                    <BlueprintBadge variant={selectedTask.task.status === 'done' ? 'success' : 'default'}>
                                        {selectedTask.task.status === 'done' ? '✓ Complete' : '○ Pending'}
                                    </BlueprintBadge>
                                    <BlueprintBadge variant="default">
                                        <Clock size={10} className="mr-1" />
                                        {TIME_ESTIMATES[selectedTask.type]}
                                    </BlueprintBadge>
                                    {selectedTask.task.channel && (
                                        <BlueprintBadge variant="default">
                                            {selectedTask.task.channel}
                                        </BlueprintBadge>
                                    )}
                                </div>
                            </div>
                        </div>

                        {/* Description */}
                        <div className="prose prose-sm max-w-none text-[var(--ink-secondary)]">
                            <p>{selectedTask.task.description || "No additional details for this task."}</p>
                        </div>

                        {/* Context Data Grid */}
                        <div className="bg-[var(--surface)] rounded-[var(--radius-lg)] border border-[var(--border)] p-6 space-y-4">
                            <h4 className="font-mono text-[10px] uppercase text-[var(--muted)] tracking-widest border-b border-[var(--border-subtle)] pb-3 mb-4">
                                Context
                            </h4>

                            <div className="grid grid-cols-2 gap-6">
                                <div>
                                    <span className="text-[10px] text-[var(--muted)] uppercase block mb-1.5">Source Move</span>
                                    <div className="flex items-center gap-2 text-sm font-medium text-[var(--ink)]">
                                        <span>{MOVE_CATEGORIES[selectedTask.move.category].emoji}</span>
                                        {selectedTask.move.name}
                                    </div>
                                </div>

                                <div>
                                    <span className="text-[10px] text-[var(--muted)] uppercase block mb-1.5">Day / Phase</span>
                                    <div className="flex items-center gap-2 text-sm text-[var(--ink)]">
                                        Day {selectedTask.dayNumber} • {selectedTask.phase}
                                    </div>
                                </div>

                                <div>
                                    <span className="text-[10px] text-[var(--muted)] uppercase block mb-1.5">Target Audience</span>
                                    <div className="flex items-center gap-2 text-sm text-[var(--ink)]">
                                        <User size={14} className="text-[var(--muted)]" />
                                        {selectedTask.move.icp || "General Audience"}
                                    </div>
                                </div>

                                <div>
                                    <span className="text-[10px] text-[var(--muted)] uppercase block mb-1.5">Campaign</span>
                                    <div className="flex items-center gap-2 text-sm text-[var(--ink)]">
                                        <Layout size={14} className="text-[var(--muted)]" />
                                        {selectedTask.move.campaignId || "Not linked"}
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Why / Purpose */}
                        <div className="bg-gradient-to-br from-[var(--blueprint-light)]/20 to-transparent rounded-[var(--radius-lg)] border border-[var(--blueprint)]/20 p-6">
                            <div className="flex items-center gap-2 mb-3 text-[var(--blueprint)]">
                                <Target size={18} />
                                <h4 className="font-bold text-sm">Why This Matters</h4>
                            </div>
                            <p className="text-sm text-[var(--ink)] leading-relaxed">
                                {selectedTask.move.goal || selectedTask.move.context}
                            </p>
                        </div>

                        {/* Action Buttons */}
                        <div className="pt-6 border-t border-[var(--border)] flex justify-between items-center">
                            <button
                                onClick={() => setSelectedTask(null)}
                                className="text-sm text-[var(--muted)] hover:text-[var(--ink)] transition-colors"
                            >
                                Close
                            </button>
                            <BlueprintButton
                                onClick={(e) => {
                                    handleTaskToggle(e, selectedTask);
                                    if (selectedTask.task.status !== 'done') setSelectedTask(null);
                                }}
                            >
                                {selectedTask.task.status === 'done' ? (
                                    <><Circle size={14} /> Mark as Pending</>
                                ) : (
                                    <><Check size={14} /> Complete Task</>
                                )}
                            </BlueprintButton>
                        </div>
                    </div>
                )}
            </BlueprintModal>
        </div>
    );
}
