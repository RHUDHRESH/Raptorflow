'use client';

import React from 'react';
import { ExperimentCard } from './ExperimentCard';
import { Experiment } from '@/lib/blackbox-types';
import { Sparkles, ArrowUpDown, Filter } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface ExperimentListProps {
    experiments: Experiment[];
    onLaunch?: (id: string) => void;
    onSwap?: (id: string) => void;
    onCheckin?: (id: string) => void;
    onView?: (id: string) => void;
    onDelete?: (id: string) => void;
    onDuplicate?: (id: string) => void;
    onMove?: (id: string, direction: 'up' | 'down') => void;
    onEdit?: (id: string) => void;
}

export function ExperimentList({
    experiments,
    onLaunch,
    onSwap,
    onCheckin,
    onView,
    onDelete,
    onDuplicate,
    onMove,
    onEdit
}: ExperimentListProps) {
    if (experiments.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center py-12 px-4 rounded-xl border-2 border-dashed border-zinc-200 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-900/50">
                <div className="p-3 bg-zinc-100 dark:bg-zinc-800 rounded-full mb-3">
                    <Sparkles className="w-5 h-5 text-zinc-400" />
                </div>
                <h3 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100 font-sans">No experiments yet</h3>
                <p className="text-xs text-zinc-500 text-center max-w-[200px] mt-1 font-sans">
                    Generate some experiments to start testing your ideas.
                </p>
            </div>
        );
    }

    return (
        <div className="space-y-3">
            {experiments.map((exp, i) => (
                <div
                    key={exp.id}
                    className="animate-in fade-in slide-in-from-bottom-2 duration-500 fill-mode-backwards"
                    style={{ animationDelay: `${i * 100}ms` }}
                >
                    <ExperimentCard
                        experiment={exp}
                        index={i}
                        totalCount={experiments.length}
                        onLaunch={onLaunch}
                        onSwap={onSwap}
                        onCheckin={onCheckin}
                        onView={onView}
                        onDelete={onDelete}
                        onDuplicate={onDuplicate}
                        onMove={onMove}
                        onEdit={onEdit}
                    />
                </div>
            ))}
        </div>
    );
}
