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

        // Show tasks if current day is within duration OR if tasks are pending (overdue)
        if (diffDays < 1) return [];

        const dayIndex = Math.min(diffDays - 1, move.duration - 1); // Cap at last day if overdue
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

    const pendingCount = todaysTasks.filter(t => t.task.status !== 'done').length;

    // Animation on mount
    useEffect(() => {
        if (!containerRef.current) return;
        gsap.fromTo(containerRef.current.children,
            { opacity: 0, y: 10 },
            { opacity: 1, y: 0, duration: 0.4, stagger: 0.05, ease: "power2.out" }
        );
    }, [todaysTasks.length]);

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

    if (activeMoves.length === 0) {
        return (
            <div className="py-12 border border-dashed border-[var(--border)] rounded-[var(--radius-lg)] text-center bg-[var(--surface-subtle)]/30">
                <div className="w-12 h-12 bg-[var(--surface)] rounded-full flex items-center justify-center mx-auto mb-3 text-[var(--muted)]">
                    <Trophy size={20} />
                </div>
                <h3 className="font-serif text-lg text-[var(--ink)] mb-1">System Idle</h3>
                <p className="text-sm text-[var(--muted)]">No active moves scheduled for today.</p>
            </div>
        );
    }

    return (
        <BlueprintCard
            title="Execution Protocol"
            subtitle={`${pendingCount} tasks pending`}
            code="EXEC-01"
            className="h-full"
            variant="default"
        >
            <div ref={containerRef} className="space-y-6">
                {activeMoves.map(move => {
                    const moveTasks = todaysTasks.filter(t => t.move.id === move.id);
                    if (moveTasks.length === 0) return null;

                    const category = MOVE_CATEGORIES[move.category];
                    const moveProgress = Math.round((moveTasks.filter(t => t.task.status === 'done').length / moveTasks.length) * 100);

                    return (
                        <div key={move.id} className="group">
                            {/* Move Header */}
                            <div className="flex items-center justify-between mb-3 pb-2 border-b border-[var(--border-subtle)]">
                                <div className="flex items-center gap-3">
                                    <span className="text-lg">{category.emoji}</span>
                                    <div>
                                        <h4 className="font-serif text-base text-[var(--ink)]">{move.name}</h4>
                                        <div className="flex items-center gap-2">
                                            <span className="text-[10px] font-mono uppercase text-[var(--muted)] tracking-wider">
                                                DAY {moveTasks[0].dayNumber} · {moveTasks[0].phase.toUpperCase()}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <span className="font-mono text-xs text-[var(--blueprint)] font-medium">
                                        {moveProgress}%
                                    </span>
                                </div>
                            </div>

                            {/* Task List */}
                            <div className="space-y-2">
                                {moveTasks.map((item, idx) => {
                                    const isCelebrating = celebrateTask === `${item.move.id}-${item.type}-${item.task.id}`;

                                    return (
                                        <div
                                            key={`${item.type}-${idx}`}
                                            className={cn(
                                                "relative flex items-start gap-3 p-3 rounded-[var(--radius-md)] border transition-all duration-200 cursor-pointer group/task",
                                                item.task.status === 'done'
                                                    ? "bg-[var(--surface-subtle)] border-transparent opacity-60"
                                                    : "bg-[var(--paper)] border-[var(--border)] hover:border-[var(--blueprint)] hover:shadow-sm"
                                            )}
                                            onClick={(e) => handleTaskToggle(e, item)}
                                        >
                                            {/* Status Checkbox */}
                                            <div className={cn(
                                                "mt-0.5 w-5 h-5 rounded-[var(--radius-sm)] border flex items-center justify-center transition-colors shrink-0",
                                                item.task.status === 'done'
                                                    ? "bg-[var(--success)] border-[var(--success)] text-white"
                                                    : "bg-[var(--surface)] border-[var(--border)] group-hover/task:border-[var(--blueprint)]"
                                            )}>
                                                {item.task.status === 'done' && <Check size={12} strokeWidth={3} />}
                                            </div>

                                            <div className="flex-1 min-w-0">
                                                <div className="flex items-center gap-2 mb-0.5">
                                                    <span className={cn(
                                                        "text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded-[var(--radius-xs)]",
                                                        item.type === 'pillar' && "bg-[var(--blueprint-light)] text-[var(--blueprint)]",
                                                        item.type === 'cluster' && "bg-[var(--surface)] text-[var(--ink-secondary)]",
                                                        item.type === 'network' && "bg-[var(--success-light)] text-[var(--success)]"
                                                    )}>
                                                        {item.type}
                                                    </span>
                                                    <span className="text-[10px] text-[var(--muted)] font-mono">
                                                        {TIME_ESTIMATES[item.type]}
                                                    </span>
                                                </div>
                                                <p className={cn(
                                                    "text-sm font-medium transition-colors",
                                                    item.task.status === 'done' ? "text-[var(--muted)] line-through decoration-[var(--border)]" : "text-[var(--ink)]"
                                                )}>
                                                    {item.task.title}
                                                </p>
                                            </div>

                                            {/* Hidden Actions */}
                                            <div className="opacity-0 group-hover/task:opacity-100 transition-opacity">
                                                <button className="p-1.5 hover:bg-[var(--surface)] rounded text-[var(--muted)] hover:text-[var(--ink)]">
                                                    <ArrowRight size={14} />
                                                </button>
                                            </div>

                                            {/* Celebration particles */}
                                            {isCelebrating && (
                                                <div className="absolute inset-0 pointer-events-none overflow-hidden rounded-[var(--radius-md)]">
                                                    {[...Array(6)].map((_, i) => (
                                                        <div
                                                            key={i}
                                                            className="absolute w-2 h-2 bg-[var(--success)] rounded-full animate-ping"
                                                            style={{
                                                                left: `${20 + i * 15}%`,
                                                                top: `${Math.random() * 80}%`,
                                                                animationDelay: `${i * 50}ms`,
                                                                animationDuration: '600ms'
                                                            }}
                                                        />
                                                    ))}
                                                </div>
                                            )}
                                        </div>
                                    )
                                })}
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Task Detail Modal */}
            <BlueprintModal
                isOpen={!!selectedTask}
                onClose={() => setSelectedTask(null)}
                title="Task Details"
                code="TSK-01"
                size="md"
            >
                {selectedTask && (
                    <div className="space-y-6">
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
                                        <h3 className="text-xl font-serif text-[var(--ink)] leading-tight">
                                            {selectedTask.task.title}
                                        </h3>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="p-4 bg-[var(--surface)] rounded border border-[var(--border)]">
                            <p className="text-sm text-[var(--ink)]">{selectedTask.task.description || "No description provided."}</p>
                        </div>
                        <div className="flex justify-end gap-3">
                            <BlueprintButton onClick={() => setSelectedTask(null)}>Close</BlueprintButton>
                        </div>
                    </div>
                )}
            </BlueprintModal>
        </BlueprintCard>
    );
}
