'use client';

import React from 'react';
import { Move, GOAL_LABELS, CHANNEL_LABELS } from '@/lib/campaigns-types';
import { ChevronRight, MoreHorizontal, Clock } from 'lucide-react';
import { cn } from '@/lib/utils';

interface MoveCardProps {
    move: Move;
    onClick: () => void;
    compact?: boolean;
    variant?: 'card' | 'row';
}

export function MoveCard({ move, onClick, compact = false, variant = 'card' }: MoveCardProps) {
    const isDone = move.status === 'completed' || move.status === 'abandoned';
    const isActive = move.status === 'active';

    // Status badges
    const StatusBadge = () => {
        if (move.status === 'active') {
            return (
                <span className="bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300 px-2.5 py-0.5 rounded-full text-[10px] uppercase font-bold tracking-wider border border-emerald-200 dark:border-emerald-800">
                    Active
                </span>
            );
        }
        if (move.status === 'queued') {
            return (
                <span className="bg-zinc-100 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400 px-2.5 py-0.5 rounded-full text-[10px] uppercase font-bold tracking-wider border border-zinc-200 dark:border-zinc-700">
                    Queued
                </span>
            );
        }
        return (
            <span className="bg-zinc-100 text-zinc-500 dark:bg-zinc-800 dark:text-zinc-500 px-2.5 py-0.5 rounded-full text-[10px] uppercase font-bold tracking-wider border border-zinc-200 dark:border-zinc-700">
                {move.status}
            </span>
        );
    };

    if (variant === 'row') {
        return (
            <div className="relative group/card">
                <button
                    onClick={onClick}
                    className="w-full text-left bg-transparent hover:bg-zinc-50 dark:hover:bg-zinc-800/50 transition-all duration-200 py-4 px-4 pl-2 hover:pl-6 rounded-lg active:scale-[0.99]"
                >
                    <div className="flex items-center justify-between gap-4">
                        <div className="flex items-center gap-4 min-w-0 overflow-hidden">
                            {/* Status Dot */}
                            <div className={cn(
                                "w-1.5 h-1.5 rounded-full shrink-0 transition-all duration-300",
                                move.status === 'active' ? "bg-emerald-500 ring-2 ring-emerald-100 dark:ring-emerald-900 scale-125 shadow-[0_0_8px_rgba(16,185,129,0.4)]" :
                                    move.status === 'queued' ? "bg-zinc-300 dark:bg-zinc-600 group-hover/card:bg-zinc-400" :
                                        "bg-zinc-200 dark:bg-zinc-700"
                            )} />

                            <div className="min-w-0">
                                {/* Name */}
                                <h3 className={cn(
                                    "font-display font-medium text-lg text-zinc-900 dark:text-zinc-100 truncate transition-colors group-hover/card:text-black dark:group-hover/card:text-white leading-normal",
                                    isDone && "text-zinc-400 dark:text-zinc-600 line-through"
                                )}>
                                    {move.name}
                                </h3>

                                {/* Meta Row - Simplified for sidebar */}
                                <div className="flex items-center gap-3 text-xs text-zinc-500 dark:text-zinc-400 mt-1">
                                    <span className={cn(
                                        "px-1.5 py-0.5 rounded text-[9px] font-bold uppercase tracking-widest border border-transparent shadow-sm",
                                        move.status === 'queued' ? "bg-white dark:bg-zinc-800 text-zinc-500 group-hover/card:border-zinc-200 dark:group-hover/card:border-zinc-700" : "hidden"
                                    )}>
                                        Up Next
                                    </span>
                                    <span className="flex items-center gap-1 font-mono text-[10px] tracking-wide tabular-nums opacity-80 group-hover/card:opacity-100 transition-opacity">
                                        <Clock className="w-3 h-3 text-zinc-300 dark:text-zinc-600 stroke-[1.5]" />
                                        {move.duration}d
                                    </span>
                                    <span className="text-zinc-200 dark:text-zinc-800">•</span>
                                    <span className="font-medium truncate text-[10px] uppercase tracking-wider text-zinc-400 group-hover/card:text-zinc-600 dark:group-hover/card:text-zinc-300 transition-colors">
                                        {CHANNEL_LABELS[move.channel]}
                                    </span>
                                </div>
                            </div>
                        </div>

                        <ChevronRight className="w-4 h-4 text-zinc-200 group-hover/card:text-zinc-400 dark:text-zinc-700 dark:group-hover/card:text-zinc-500 transition-all duration-300 shrink-0 group-hover/card:translate-x-1 stroke-[1.5]" />
                    </div>
                </button>
                {/* Fading Separator (Tidbit #3) */}
                <div className="absolute bottom-0 left-4 right-4 h-px bg-gradient-to-r from-transparent via-zinc-100 to-transparent dark:via-zinc-800 pointer-events-none group-last/card:hidden" />
            </div>
        );
    }

    return (
        <button
            onClick={onClick}
            className={cn(
                "w-full text-left bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl transition-all duration-300 group relative overflow-hidden",
                "hover:border-zinc-300 dark:hover:border-zinc-700 hover:shadow-lg hover:shadow-zinc-200/50 dark:hover:shadow-none hover:-translate-y-1",
                compact ? 'p-5' : 'p-6'
            )}
        >
            <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-2">
                        <h3 className={cn(
                            "font-display font-medium text-zinc-900 dark:text-zinc-100 truncate",
                            compact ? 'text-lg' : 'text-xl'
                        )}>
                            {move.name}
                        </h3>
                        <StatusBadge />
                    </div>

                    <div className="flex items-center gap-3 text-sm text-zinc-500 dark:text-zinc-400">
                        <span className="text-zinc-900 dark:text-zinc-200 font-medium flex items-center gap-1.5">
                            <Clock className="w-3.5 h-3.5 text-zinc-400" />
                            {move.duration} days
                        </span>

                        <span className="text-zinc-300 dark:text-zinc-700">•</span>

                        <span className="font-medium">{CHANNEL_LABELS[move.channel]}</span>

                        {isActive && move.startedAt && (
                            <>
                                <span className="text-zinc-300 dark:text-zinc-700">•</span>
                                <span className="text-emerald-700 dark:text-emerald-400 font-medium">
                                    Ends {new Date(new Date(move.startedAt).getTime() + move.duration * 86400000).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                                </span>
                            </>
                        )}

                        {/* Campaign context if available */}
                        {move.campaignName && !compact && (
                            <>
                                <span className="text-zinc-300 dark:text-zinc-700">•</span>
                                <span className="truncate max-w-[150px] bg-zinc-100 dark:bg-zinc-800 px-2 py-0.5 rounded text-xs text-zinc-600 dark:text-zinc-400">
                                    {move.campaignName}
                                </span>
                            </>
                        )}
                    </div>
                </div>

                <div className="flex items-center justify-center w-8 h-8 rounded-full bg-zinc-50 dark:bg-zinc-800 text-zinc-300 dark:text-zinc-600 group-hover:bg-zinc-100 dark:group-hover:bg-zinc-700 group-hover:text-zinc-900 dark:group-hover:text-zinc-100 transition-all">
                    <ChevronRight className="w-4 h-4" />
                </div>
            </div>
        </button>
    );
}
