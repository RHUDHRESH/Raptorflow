"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useMovesStore } from "@/stores/movesStore";
import {
    X,
    Check,
    Sparkles,
    ArrowRight,
    Clock,
    Zap,
    Share2,
    MessageSquare,
    ExternalLink
} from "lucide-react";
import { cn } from "@/lib/utils";
import { TaskItem, Move, MOVE_CATEGORIES } from "./types";

/* ══════════════════════════════════════════════════════════════════════════════
   TASK DETAIL POPUP — Quick task view with Muse integration
   Shows task details and allows marking complete or asking Muse for help
   ══════════════════════════════════════════════════════════════════════════════ */

interface TaskDetailPopupProps {
    task: TaskItem;
    taskType: 'pillar' | 'cluster' | 'network';
    move: Move;
    dayNumber: number;
    onClose: () => void;
    onToggleComplete: () => void;
    onViewMove: () => void;
}

export function TaskDetailPopup({
    task,
    taskType,
    move,
    dayNumber,
    onClose,
    onToggleComplete,
    onViewMove
}: TaskDetailPopupProps) {
    const router = useRouter();
    const { updateBackendTaskStatus } = useMovesStore();
    const [isCompleting, setIsCompleting] = useState(false);

    const category = MOVE_CATEGORIES[move.category];
    const isComplete = task.status === 'done';

    const getTaskIcon = () => {
        switch (taskType) {
            case 'pillar': return <Zap size={16} className="text-blue-600" />;
            case 'cluster': return <Share2 size={16} className="text-[var(--muted)]" />;
            case 'network': return <MessageSquare size={16} className="text-green-600" />;
        }
    };

    const getTaskLabel = () => {
        switch (taskType) {
            case 'pillar': return 'Core Focus';
            case 'cluster': return 'Support Task';
            case 'network': return 'Outreach';
        }
    };

    const handleComplete = async () => {
        setIsCompleting(true);
        try {
            // --- ABSOLUTE INFINITY: BACKEND SYNC ---
            await updateBackendTaskStatus(task.id, 'completed');
            onToggleComplete();
            setIsCompleting(false);
            onClose();
        } catch (error) {
            console.error("Failed to sync task status:", error);
            setIsCompleting(false);
        }
    };

    const handleAskMuse = () => {
        // Navigate to Muse with the task context pre-filled
        const context = encodeURIComponent(
            `Help me with this task:\n\nTask: ${task.title}\n${task.description ? `Details: ${task.description}\n` : ''}Move: ${move.name}\nCategory: ${category?.name || move.category}\nDay: ${dayNumber} of ${move.duration}`
        );
        router.push(`/muse?prompt=${context}`);
        onClose();
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4" onClick={onClose}>
            {/* Backdrop */}
            <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" />

            {/* Popup */}
            <div
                className={cn(
                    "relative w-full max-w-md bg-[var(--paper)] rounded-[var(--radius-lg)] border border-[var(--border)] shadow-2xl overflow-hidden",
                    "animate-in zoom-in-95 fade-in duration-200"
                )}
                onClick={e => e.stopPropagation()}
            >
                {/* Header */}
                <div className="flex items-center justify-between p-4 border-b border-[var(--border)] bg-[var(--surface)]">
                    <div className="flex items-center gap-2">
                        {getTaskIcon()}
                        <span className="text-xs font-semibold uppercase tracking-wider text-[var(--muted)]">
                            {getTaskLabel()}
                        </span>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-1.5 hover:bg-[var(--paper)] rounded-[var(--radius)] transition-colors"
                    >
                        <X size={16} className="text-[var(--muted)]" />
                    </button>
                </div>

                {/* Content */}
                <div className="p-5">
                    {/* Task Title */}
                    <h2 className={cn(
                        "text-lg font-semibold text-[var(--ink)] mb-2",
                        isComplete && "line-through opacity-60"
                    )}>
                        {task.title}
                    </h2>

                    {/* Task Description */}
                    {task.description && (
                        <p className="text-sm text-[var(--muted)] mb-4 leading-relaxed">
                            {task.description}
                        </p>
                    )}

                    {/* Meta Info */}
                    <div className="flex flex-wrap items-center gap-3 text-xs text-[var(--muted)] mb-6">
                        {task.channel && (
                            <span className="px-2 py-1 bg-[var(--surface)] border border-[var(--border)] rounded-full uppercase font-medium">
                                {task.channel}
                            </span>
                        )}
                        <span className="flex items-center gap-1">
                            <Clock size={12} />
                            Day {dayNumber} of {move.duration}
                        </span>
                    </div>

                    {/* Move Context */}
                    <div className="p-3 rounded-[var(--radius)] bg-[var(--surface)] border border-[var(--border)] mb-6">
                        <div className="text-[10px] uppercase tracking-wider text-[var(--muted)] mb-1">From Move</div>
                        <div className="flex items-center justify-between">
                            <span className="font-medium text-sm text-[var(--ink)]">{move.name}</span>
                            <button
                                onClick={onViewMove}
                                className="text-xs text-blue-600 hover:underline flex items-center gap-1"
                            >
                                View
                                <ExternalLink size={10} />
                            </button>
                        </div>
                        <div className="text-xs text-[var(--muted)] mt-0.5">{category?.name}</div>
                    </div>

                    {/* Actions */}
                    <div className="flex gap-3">
                        {/* Complete Button */}
                        <button
                            onClick={handleComplete}
                            disabled={isCompleting}
                            className={cn(
                                "flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-[var(--radius)] font-medium text-sm transition-all",
                                isComplete
                                    ? "bg-green-100 text-green-700 border border-green-200"
                                    : "bg-[var(--ink)] text-white hover:bg-[var(--ink)]/90"
                            )}
                        >
                            <Check size={16} className={isCompleting ? "animate-spin" : ""} />
                            {isComplete ? "Completed" : "Mark Complete"}
                        </button>

                        {/* Ask Muse Button */}
                        <button
                            onClick={handleAskMuse}
                            className="flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-[var(--radius)] font-medium text-sm bg-gradient-to-r from-purple-500 to-blue-500 text-white hover:from-purple-600 hover:to-blue-600 transition-all shadow-md hover:shadow-lg"
                        >
                            <Sparkles size={16} />
                            Ask Muse
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
