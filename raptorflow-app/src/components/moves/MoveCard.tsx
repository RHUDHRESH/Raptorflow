'use client';

import React from 'react';
import { Move, GOAL_LABELS, CHANNEL_LABELS } from '@/lib/campaigns-types';
import { ChevronRight, MoreHorizontal, Clock } from 'lucide-react';

interface MoveCardProps {
    move: Move;
    onClick: () => void;
    compact?: boolean;
}

export function MoveCard({ move, onClick, compact = false }: MoveCardProps) {
    const isDone = move.status === 'completed' || move.status === 'abandoned';
    const isActive = move.status === 'active';

    // Status badges
    const StatusBadge = () => {
        if (move.status === 'active') {
            return (
                <span className="bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-400 px-2 py-0.5 rounded-full text-[10px] uppercase font-bold tracking-wide">
                    Active
                </span>
            );
        }
        if (move.status === 'queued') {
            return (
                <span className="bg-zinc-100 text-zinc-500 dark:bg-zinc-800 dark:text-zinc-400 px-2 py-0.5 rounded-full text-[10px] uppercase font-bold tracking-wide">
                    Queued
                </span>
            );
        }
        return (
            <span className="bg-zinc-100 text-zinc-400 dark:bg-zinc-800 dark:text-zinc-500 px-2 py-0.5 rounded-full text-[10px] uppercase font-bold tracking-wide">
                {move.status}
            </span>
        );
    };

    return (
        <button
            onClick={onClick}
            className={`w-full text-left bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl hover:border-zinc-300 dark:hover:border-zinc-700 hover:shadow-md active:scale-[0.99] transition-all duration-200 group ${compact ? 'p-4' : 'p-5'
                }`}
        >
            <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1.5">
                        <h3 className={`font-semibold text-zinc-900 dark:text-zinc-100 truncate ${compact ? 'text-sm' : 'text-base'}`}>
                            {move.name}
                        </h3>
                        <StatusBadge />
                    </div>

                    <div className="flex items-center gap-3 text-sm text-zinc-500 dark:text-zinc-400">
                        <span className="text-zinc-700 dark:text-zinc-300 font-medium">
                            {move.duration} days
                        </span>
                        {isActive && move.startedAt && (
                            <>
                                <span className="text-zinc-300 dark:text-zinc-600">•</span>
                                <span className="text-emerald-600 dark:text-emerald-400 font-medium">
                                    Ends {new Date(new Date(move.startedAt).getTime() + move.duration * 86400000).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                                </span>
                            </>
                        )}
                        <span className="text-zinc-300 dark:text-zinc-600">•</span>
                        <span>{CHANNEL_LABELS[move.channel]}</span>
                        {/* Campaign context if available */}
                        {move.campaignName && !compact && (
                            <>
                                <span className="text-zinc-300 dark:text-zinc-600">•</span>
                                <span className="truncate max-w-[150px]">{move.campaignName}</span>
                            </>
                        )}
                    </div>
                </div>

                <div className="flex items-center text-zinc-300 dark:text-zinc-600 group-hover:text-zinc-400 dark:group-hover:text-zinc-500 transition-colors">
                    <ChevronRight className="w-5 h-5" />
                </div>
            </div>
        </button>
    );
}
