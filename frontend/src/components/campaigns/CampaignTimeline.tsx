"use client";

import { useMemo } from "react";
import { X, Clock, ArrowRight, Play, Pause, CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { format, addDays, differenceInDays } from "date-fns";

/* ══════════════════════════════════════════════════════════════════════════════
   CAMPAIGN TIMELINE — Gantt-style view of campaign moves
   Shows move sequence, dependencies, and current position
   ══════════════════════════════════════════════════════════════════════════════ */

interface CampaignMove {
    id: string;
    title: string;
    type: string;
    status: 'Planned' | 'Active' | 'Completed';
    start: string;
    end: string;
    items_done: number;
    items_total: number;
    desc: string;
}

interface Campaign {
    id: string;
    name: string;
    status: string;
    progress: number;
    goal: string;
    moves: CampaignMove[];
}

interface CampaignTimelineProps {
    campaign: Campaign;
    onClose: () => void;
    onMoveClick?: (move: CampaignMove) => void;
}

export function CampaignTimeline({ campaign, onClose, onMoveClick }: CampaignTimelineProps) {
    // Calculate timeline range
    const timelineData = useMemo(() => {
        const today = new Date();

        // For demo, create timeline weeks
        const weeks = [];
        const startDate = today;
        for (let i = 0; i < 12; i++) {
            weeks.push(addDays(startDate, i * 7));
        }

        return { today, weeks, totalWeeks: 12 };
    }, []);

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'Active': return 'bg-[var(--ink)]';
            case 'Completed': return 'bg-green-600';
            case 'Planned': return 'bg-[var(--muted)]';
            default: return 'bg-[var(--muted)]';
        }
    };

    const getStatusBadge = (status: string) => {
        switch (status) {
            case 'Active': return <Play size={10} className="text-white" />;
            case 'Completed': return <CheckCircle2 size={10} className="text-white" />;
            default: return <Clock size={10} className="text-white" />;
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4" onClick={onClose}>
            {/* Backdrop */}
            <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" />

            {/* Modal */}
            <div
                className="relative w-full max-w-5xl max-h-[85vh] bg-[var(--paper)] rounded-[var(--radius-lg)] border border-[var(--border)] shadow-2xl overflow-hidden animate-in zoom-in-95 fade-in duration-200"
                onClick={e => e.stopPropagation()}
            >
                {/* Header */}
                <div className="flex items-center justify-between p-5 border-b border-[var(--border)] bg-[var(--surface)]">
                    <div>
                        <h2 className="font-serif text-xl text-[var(--ink)]">{campaign.name}</h2>
                        <p className="text-sm text-[var(--muted)]">Campaign Timeline • {campaign.moves.length} moves</p>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-[var(--paper)] rounded-[var(--radius)] transition-colors"
                    >
                        <X size={18} className="text-[var(--muted)]" />
                    </button>
                </div>

                {/* Timeline Content */}
                <div className="p-5 overflow-x-auto">
                    {/* Week Headers */}
                    <div className="flex border-b border-[var(--border)] pb-2 mb-4 min-w-[800px]">
                        <div className="w-48 shrink-0 text-xs font-semibold text-[var(--muted)] uppercase tracking-wider">
                            Move
                        </div>
                        <div className="flex-1 flex">
                            {timelineData.weeks.map((week, idx) => (
                                <div key={idx} className="flex-1 text-center text-[10px] text-[var(--muted)] font-medium uppercase">
                                    W{idx + 1}
                                    <div className="text-[9px] font-normal opacity-70">
                                        {format(week, 'MMM d')}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Moves with Gantt Bars */}
                    <div className="space-y-3 min-w-[800px]">
                        {campaign.moves.map((move, idx) => {
                            // Calculate position (demo: spread moves across timeline)
                            const startWeek = Math.floor(idx * 2);
                            const duration = 3; // weeks
                            const leftPercent = (startWeek / 12) * 100;
                            const widthPercent = (duration / 12) * 100;

                            return (
                                <div key={move.id} className="flex items-center group">
                                    {/* Move Label */}
                                    <div className="w-48 shrink-0 pr-4">
                                        <div className="flex items-center gap-2">
                                            {/* Sequence Number */}
                                            <div className={cn(
                                                "w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white shrink-0",
                                                getStatusColor(move.status)
                                            )}>
                                                {idx + 1}
                                            </div>
                                            <div className="min-w-0">
                                                <button
                                                    onClick={() => onMoveClick?.(move)}
                                                    className="text-sm font-medium text-[var(--ink)] truncate block hover:text-blue-600 transition-colors text-left"
                                                >
                                                    {move.title}
                                                </button>
                                                <div className="text-[10px] text-[var(--muted)]">{move.type}</div>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Gantt Bar Area */}
                                    <div className="flex-1 relative h-10">
                                        {/* Grid lines */}
                                        <div className="absolute inset-0 flex">
                                            {timelineData.weeks.map((_, idx) => (
                                                <div key={idx} className="flex-1 border-l border-[var(--border)]" />
                                            ))}
                                        </div>

                                        {/* Move Bar */}
                                        <div
                                            className={cn(
                                                "absolute top-1 h-8 rounded-md flex items-center px-2 gap-1 transition-all group-hover:shadow-md cursor-pointer",
                                                getStatusColor(move.status)
                                            )}
                                            style={{
                                                left: `${leftPercent}%`,
                                                width: `${widthPercent}%`,
                                                minWidth: '80px'
                                            }}
                                            onClick={() => onMoveClick?.(move)}
                                        >
                                            {getStatusBadge(move.status)}
                                            <span className="text-xs text-white font-medium truncate">
                                                {move.status}
                                            </span>
                                        </div>

                                        {/* Connection Arrow to Next */}
                                        {idx < campaign.moves.length - 1 && (
                                            <div
                                                className="absolute top-1/2 -translate-y-1/2 text-[var(--muted)]"
                                                style={{ left: `${leftPercent + widthPercent + 1}%` }}
                                            >
                                                <ArrowRight size={14} />
                                            </div>
                                        )}
                                    </div>
                                </div>
                            );
                        })}
                    </div>

                    {/* Legend */}
                    <div className="flex items-center gap-6 mt-8 pt-4 border-t border-[var(--border)]">
                        <span className="text-xs text-[var(--muted)] font-medium">Legend:</span>
                        <div className="flex items-center gap-2">
                            <div className="w-3 h-3 rounded bg-[var(--ink)]" />
                            <span className="text-xs text-[var(--muted)]">Active</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="w-3 h-3 rounded bg-[var(--muted)]" />
                            <span className="text-xs text-[var(--muted)]">Planned</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="w-3 h-3 rounded bg-green-600" />
                            <span className="text-xs text-[var(--muted)]">Completed</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <ArrowRight size={12} className="text-[var(--muted)]" />
                            <span className="text-xs text-[var(--muted)]">Sequence</span>
                        </div>
                    </div>
                </div>

                {/* Footer */}
                <div className="p-4 border-t border-[var(--border)] bg-[var(--surface)] flex items-center justify-between">
                    <div className="text-xs text-[var(--muted)]">
                        Campaign Progress: <span className="font-semibold text-[var(--ink)]">{campaign.progress}%</span>
                    </div>
                    <button
                        onClick={onClose}
                        className="px-4 py-2 text-sm font-medium text-[var(--ink)] border border-[var(--border)] hover:border-[var(--ink)] rounded-[var(--radius)] transition-colors"
                    >
                        Close
                    </button>
                </div>
            </div>
        </div>
    );
}
