"use client";

import { cn } from "@/lib/utils";
import { ExecutionDay, TaskStatus, TaskItem } from "./types";
import { Check, Circle, Play, AlertCircle, MessageSquare, Mail, Phone, Share2, Layers, Zap, Hexagon } from "lucide-react";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";

/* ══════════════════════════════════════════════════════════════════════════════
   EXECUTION GRID (S.O.P. MANIFEST)
   The tactical battle plan, rendered as a high-fidelity data grid.
   ══════════════════════════════════════════════════════════════════════════════ */

interface ExecutionGridProps {
    days: ExecutionDay[];
    onTaskStatusChange?: (dayIndex: number, taskType: 'pillar' | 'cluster' | 'network', taskId: string, status: TaskStatus) => void;
    className?: string;
    compact?: boolean;
}

const PHASE_COLORS: Record<string, string> = {
    'Tease': 'bg-[var(--blueprint-light)] text-[var(--blueprint)] border-[var(--blueprint)]/30',
    'Reveal': 'bg-[var(--success-light)] text-[var(--success)] border-[var(--success)]/30',
    'Proof': 'bg-[var(--warning-light)] text-[var(--warning)] border-[var(--warning)]/30',
    'Urgency': 'bg-[var(--error-light)] text-[var(--error)] border-[var(--error)]/30',
    'Close': 'bg-[var(--ink)] text-[var(--paper)] border-[var(--ink)]',
    'Sustain': 'bg-[var(--surface)] text-[var(--secondary)] border-[var(--border)]',
};

export function ExecutionGrid({ days, onTaskStatusChange, className, compact = false }: ExecutionGridProps) {
    return (
        <div className={cn("space-y-6", className)}>
            {/* Section Header */}
            {!compact && (
                <div className="flex items-end justify-between">
                    <div>
                        <div className="flex items-center gap-3 mb-2">
                            <span className="font-technical text-[var(--blueprint)]">STEP 04</span>
                            <div className="h-px w-12 bg-[var(--blueprint-line)]" />
                            <span className="font-technical text-[var(--muted)]">EXECUTION PLAN</span>
                        </div>
                        <h2 className="font-serif text-2xl text-[var(--ink)]">Your 7-Day Plan</h2>
                    </div>
                </div>
            )}

            {/* The Grid Container */}
            <div className="border border-[var(--border)] rounded-[var(--radius-md)] overflow-hidden bg-[var(--paper)] shadow-sm">
                {/* Header Row */}
                <div className="grid grid-cols-12 bg-[var(--canvas)] border-b border-[var(--border)] py-3 px-4 text-xs font-technical text-[var(--muted)] tracking-wider">
                    <div className="col-span-1 text-center">DAY</div>
                    <div className="col-span-1">PHASE</div>
                    <div className="col-span-4 pl-4 border-l border-[var(--border-subtle)]">PILLAR (CORE)</div>
                    <div className="col-span-4 pl-4 border-l border-[var(--border-subtle)]">CLUSTER (AMPLIFY)</div>
                    <div className="col-span-2 pl-4 border-l border-[var(--border-subtle)]">NETWORK (PUSH)</div>
                </div>

                {/* Rows */}
                <div className="divide-y divide-[var(--border-subtle)]">
                    {days.map((day, dayIndex) => (
                        <div key={day.day} className="grid grid-cols-12 group hover:bg-[var(--canvas)] transition-colors min-h-[80px]">

                            {/* Day & Phase */}
                            <div className="col-span-2 grid grid-cols-2">
                                <div className="border-r border-[var(--border-subtle)] p-4 flex items-center justify-center bg-[var(--canvas)]/30">
                                    <span className="font-mono text-xl font-bold text-[var(--ink)]">
                                        {day.day.toString().padStart(2, '0')}
                                    </span>
                                </div>
                                <div className="p-4 flex items-center justify-center">
                                    <span className={cn("px-2 py-1 rounded text-[10px] font-bold uppercase tracking-wide border", PHASE_COLORS[day.phase] || 'bg-[var(--surface)] text-[var(--secondary)] border-[var(--border)]')}>
                                        {day.phase}
                                    </span>
                                </div>
                            </div>

                            {/* Pillar Task */}
                            <div className="col-span-4 p-4 border-r border-[var(--border-subtle)] flex items-start">
                                <TaskNode
                                    task={day.pillarTask}
                                    icon={<Hexagon size={14} className="text-[var(--blueprint)]" />}
                                    isMain
                                />
                            </div>

                            {/* Cluster Actions */}
                            <div className="col-span-4 p-4 border-r border-[var(--border-subtle)] space-y-3">
                                {day.clusterActions.map((action) => (
                                    <TaskNode
                                        key={action.id}
                                        task={action}
                                        icon={<Layers size={14} className="text-[var(--ink-muted)]" />}
                                    />
                                ))}
                            </div>

                            {/* Network Action */}
                            <div className="col-span-2 p-4 flex items-center">
                                <TaskNode
                                    task={day.networkAction}
                                    icon={<Zap size={14} className="text-[var(--warning)]" />}
                                />
                            </div>

                        </div>
                    ))}
                </div>
            </div>

            {!compact && (
                <div className="flex justify-end gap-6 text-xs text-[var(--muted)] font-technical pt-2">
                    <span>* PILLAR: HIGH EFFORT</span>
                    <span>* CLUSTER: MEDIUM EFFORT</span>
                    <span>* NETWORK: LOW EFFORT</span>
                </div>
            )}
        </div>
    );
}

function TaskNode({ task, icon, isMain = false }: { task: TaskItem, icon: React.ReactNode, isMain?: boolean }) {
    if (!task) return null;

    // Simple mock status toggle logic could go here if we wired up interactivity
    const isDone = task.status === 'done';

    return (
        <div className={cn("flex gap-3", isMain ? "items-start" : "items-center")}>
            <div className={cn(
                "mt-0.5 w-6 h-6 rounded-full flex items-center justify-center shrink-0 border transition-colors cursor-pointer",
                isDone ? "bg-[var(--success-light)] border-[var(--success)]" : "bg-[var(--paper)] border-[var(--border)] hover:border-[var(--blueprint)]"
            )}>
                {isDone ? <Check size={12} className="text-[var(--success)]" /> : icon}
            </div>
            <div>
                <p className={cn(
                    "font-medium leading-tight transition-opacity",
                    isMain ? "text-sm text-[var(--ink)]" : "text-xs text-[var(--secondary)]",
                    isDone && "line-through opacity-50"
                )}>
                    {task.title}
                </p>
                {isMain && task.description && (
                    <p className="text-xs text-[var(--muted)] mt-1 line-clamp-2 leading-relaxed">
                        {task.description}
                    </p>
                )}
                {task.channel && !isMain && (
                    <span className="inline-block mt-1 text-[9px] font-mono text-[var(--muted)] uppercase border border-[var(--border)] px-1 rounded bg-[var(--canvas)]">
                        {task.channel}
                    </span>
                )}
            </div>
        </div>
    );
}

export default ExecutionGrid;
