"use client";

import { useRef, useEffect, useState } from "react";
import gsap from "gsap";
import {
    Calendar, Check, Circle, Play, ChevronDown, ChevronRight, MessageSquare, Mail, Phone, Share2, Zap, Clock, ArrowRight, MoreHorizontal
} from "lucide-react";
import { cn } from "@/lib/utils";

import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { BlueprintProgress } from "@/components/ui/BlueprintProgress";

import { Move, ExecutionDay, TaskItem, TaskStatus, MOVE_CATEGORIES } from "./types";

/* ══════════════════════════════════════════════════════════════════════════════
   TODAY VIEW — DAILY PROTOCOL
   A high-density "Battle Card" for daily execution.
   ══════════════════════════════════════════════════════════════════════════════ */

interface TodayViewProps {
    moves: Move[];
    onTaskStatusChange?: (moveId: string, dayIndex: number, taskType: 'pillar' | 'cluster' | 'network', taskIndex: number, status: TaskStatus) => void;
    onMoveClick?: (move: Move) => void;
}

export function TodayView({ moves, onTaskStatusChange, onMoveClick }: TodayViewProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const today = new Date();
    const dateStr = today.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' });

    // Filter active moves
    const activeMoves = moves.filter(m => m.status === 'active' && m.startDate);

    const getMoveDayInfo = (move: Move) => {
        if (!move.startDate) return null;
        const startDate = new Date(move.startDate);
        const diffTime = today.getTime() - startDate.getTime();
        const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24)) + 1;

        if (diffDays < 1 || diffDays > move.duration) return null;

        return {
            dayNumber: diffDays,
            execution: move.execution[diffDays - 1],
            dayIndex: diffDays - 1,
        };
    };

    const taskStats = activeMoves.reduce((acc, move) => {
        const info = getMoveDayInfo(move);
        if (!info) return acc;

        const tasks = [
            info.execution.pillarTask,
            ...info.execution.clusterActions,
            info.execution.networkAction
        ];

        return {
            total: acc.total + tasks.length,
            completed: acc.completed + tasks.filter(t => t.status === 'done').length
        };
    }, { total: 0, completed: 0 });

    useEffect(() => {
        if (!containerRef.current) return;
        gsap.fromTo(containerRef.current, { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.5, ease: "power2.out" });
    }, []);

    if (activeMoves.length === 0 || activeMoves.every(m => !getMoveDayInfo(m))) {
        return (
            <BlueprintCard showCorners padding="lg" className="text-center py-20 bg-[var(--surface-subtle)] border-dashed">
                <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-[var(--surface)] text-[var(--muted)] flex items-center justify-center border border-[var(--border)]">
                    <Calendar size={24} />
                </div>
                <h3 className="font-editorial text-2xl text-[var(--ink)] mb-2">Protocol Standby</h3>
                <p className="text-sm text-[var(--secondary)] max-w-sm mx-auto mb-6">
                    No active operations scheduled for today. Launch a new campaign or advance existing timeline.
                </p>
                <div className="inline-flex items-center gap-2 text-xs font-mono text-[var(--blueprint)] uppercase tracking-wider cursor-pointer hover:underline">
                    Initialize Move <ArrowRight size={12} />
                </div>
            </BlueprintCard>
        );
    }

    return (
        <div ref={containerRef} className="space-y-8">
            {/* Protocol Header */}
            <div className="flex items-end justify-between border-b border-[var(--border)] pb-6">
                <div>
                    <div className="flex items-center gap-2 mb-2">
                        <div className="w-2 h-2 rounded-full bg-[var(--blueprint)] animate-pulse" />
                        <span className="font-mono text-[10px] text-[var(--blueprint)] uppercase tracking-widest">Live Protocol</span>
                    </div>
                    <h2 className="font-editorial text-4xl text-[var(--ink)] mb-1">Today's Orders</h2>
                    <p className="font-serif italic text-[var(--secondary)]">{dateStr}</p>
                </div>

                <div className="text-right">
                    <div className="flex items-baseline justify-end gap-2 mb-1">
                        <span className="font-data text-4xl text-[var(--ink)]">{taskStats.completed}</span>
                        <span className="font-light text-[var(--muted)] text-xl">/ {taskStats.total}</span>
                    </div>
                    <div className="w-48 h-1 bg-[var(--structure)] rounded-full overflow-hidden mt-2">
                        <div
                            className="h-full bg-[var(--ink)] transition-all duration-500 ease-out"
                            style={{ width: `${(taskStats.completed / taskStats.total) * 100}%` }}
                        />
                    </div>
                </div>
            </div>

            {/* Move Cards */}
            <div className="space-y-6">
                {activeMoves.map((move) => {
                    const dayInfo = getMoveDayInfo(move);
                    if (!dayInfo) return null;

                    return (
                        <div key={move.id} className="group relative">
                            {/* Connector Line */}
                            <div className="absolute left-6 top-8 bottom-0 w-px bg-[var(--border)] group-last:hidden" />

                            <div className="relative z-10">
                                <DailyMoveCard
                                    move={move}
                                    dayInfo={dayInfo}
                                    onTaskStatusChange={onTaskStatusChange}
                                    onMoveClick={onMoveClick}
                                />
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}

function DailyMoveCard({ move, dayInfo, onTaskStatusChange, onMoveClick }: { move: Move, dayInfo: any, onTaskStatusChange?: any, onMoveClick?: any }) {
    const { execution, dayNumber, dayIndex } = dayInfo;
    const categoryInfo = MOVE_CATEGORIES[move.category];

    // Calculate progress for this move
    const totalTasks = 1 + execution.clusterActions.length + 1;
    const completedTasks = (execution.pillarTask.status === 'done' ? 1 : 0) +
        execution.clusterActions.filter((a: any) => a.status === 'done').length +
        (execution.networkAction.status === 'done' ? 1 : 0);
    const progress = (completedTasks / totalTasks) * 100;

    return (
        <BlueprintCard className="bg-[var(--paper)] hover:shadow-lg transition-all duration-300 border-[var(--border)] group-hover:border-[var(--blueprint)]/50">
            {/* Card Header */}
            <div className="flex items-start justify-between p-6 pb-4 border-b border-[var(--border-subtle)] cursor-pointer" onClick={() => onMoveClick?.(move)}>
                <div className="flex gap-4">
                    <div className="w-12 h-12 rounded-[var(--radius-sm)] bg-[var(--surface)] text-2xl flex items-center justify-center border border-[var(--border)]">
                        {categoryInfo.emoji}
                    </div>
                    <div>
                        <div className="flex items-center gap-3 mb-1">
                            <h3 className="font-editorial text-lg text-[var(--ink)] group-hover:text-[var(--blueprint)] transition-colors">{move.name}</h3>
                            <span className="px-2 py-0.5 rounded-full border border-[var(--border)] text-[9px] font-bold uppercase tracking-wider text-[var(--muted)]">Day {dayNumber}</span>
                        </div>
                        <div className="flex items-center gap-2 text-xs text-[var(--secondary)]">
                            <span className="w-1.5 h-1.5 rounded-full bg-[var(--blueprint)]" />
                            <span className="font-medium">{execution.phase} Phase</span>
                        </div>
                    </div>
                </div>

                <div className="flex flex-col items-end gap-1">
                    <button className="text-[var(--muted)] hover:text-[var(--ink)] transition-colors">
                        <MoreHorizontal size={16} />
                    </button>
                    {progress === 100 && (
                        <span className="flex items-center gap-1 text-[10px] uppercase font-bold text-[var(--success)] bg-[var(--success-light)] px-2 py-0.5 rounded-full mt-2">
                            <Check size={10} strokeWidth={3} /> Complete
                        </span>
                    )}
                </div>
            </div>

            {/* Tasks List */}
            <div className="p-2">
                {/* Pillar (Hero Task) */}
                <TaskRow
                    task={execution.pillarTask}
                    type="pillar"
                    onClick={() => onTaskStatusChange?.(move.id, dayIndex, 'pillar', 0, execution.pillarTask.status)}
                />

                {/* Cluster Actions */}
                {execution.clusterActions.map((action: any, i: number) => (
                    <TaskRow
                        key={action.id}
                        task={action}
                        type="cluster"
                        onClick={() => onTaskStatusChange?.(move.id, dayIndex, 'cluster', i, action.status)}
                    />
                ))}

                {/* Network Action */}
                <TaskRow
                    task={execution.networkAction}
                    type="network"
                    onClick={() => onTaskStatusChange?.(move.id, dayIndex, 'network', 0, execution.networkAction.status)}
                />
            </div>

            {/* Quick Actions Footer */}
            <div className="px-4 py-2 bg-[var(--surface-subtle)] border-t border-[var(--border-subtle)] flex justify-between items-center opacity-0 group-hover:opacity-100 transition-opacity">
                <span className="text-[10px] font-mono text-[var(--muted)] uppercase">Estimated: 1h 45m</span>
                <button className="text-[10px] font-bold text-[var(--blueprint)] flex items-center gap-1 hover:underline">
                    OPEN WAR ROOM <ArrowRight size={10} />
                </button>
            </div>
        </BlueprintCard>
    );
}

function TaskRow({ task, type, onClick }: { task: TaskItem, type: 'pillar' | 'cluster' | 'network', onClick: () => void }) {
    const isDone = task.status === 'done';

    const config = {
        pillar: { icon: <Zap size={14} />, color: "text-[var(--blueprint)]", bg: "bg-[var(--blueprint-light)]/30" },
        cluster: { icon: <Share2 size={14} />, color: "text-[var(--ink-secondary)]", bg: "bg-[var(--surface)]" },
        network: { icon: <MessageSquare size={14} />, color: "text-[var(--success)]", bg: "bg-[var(--success-light)]/30" },
    }[type];

    return (
        <div
            onClick={onClick}
            className={cn(
                "flex items-center gap-3 p-3 rounded-[var(--radius-sm)] cursor-pointer transition-all border border-transparent hover:border-[var(--border)]",
                isDone ? "opacity-50" : "hover:bg-[var(--surface)]"
            )}
        >
            <div className={cn(
                "w-5 h-5 rounded flex items-center justify-center shrink-0 border transition-all",
                isDone
                    ? "bg-[var(--success)] border-[var(--success)] text-[var(--paper)]"
                    : "bg-[var(--paper)] border-[var(--border)] hover:border-[var(--blueprint)] text-transparent"
            )}>
                <Check size={12} strokeWidth={3} />
            </div>

            <div className={cn("w-8 h-8 rounded-[var(--radius-sm)] flex items-center justify-center shrink-0", config.bg, config.color)}>
                {config.icon}
            </div>

            <div className="flex-1 min-w-0">
                <p className={cn("text-sm font-medium truncate transition-all", isDone ? "line-through text-[var(--muted)]" : "text-[var(--ink)]")}>
                    {task.title}
                </p>
                {task.channel && !isDone && (
                    <span className="text-[10px] font-mono text-[var(--muted)] uppercase border border-[var(--border)] px-1 rounded bg-[var(--paper)] mt-0.5 inline-block">
                        {task.channel}
                    </span>
                )}
            </div>
        </div>
    );
}

export default TodayView;
