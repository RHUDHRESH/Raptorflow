'use client';

import React from 'react';
import { cn } from '@/lib/utils';

interface GanttItem {
    id: string;
    task: string;
    start_date: string;
    end_date: string;
    progress: number;
}

interface CampaignGanttProps {
    items: GanttItem[];
    className?: string;
}

/**
 * SOTA Campaign Gantt Chart
 * Visualizes the 90-day arc execution timeline.
 */
export function CampaignGantt({ items, className }: CampaignGanttProps) {
    if (!items || items.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center p-12 border border-dashed border-zinc-200 dark:border-zinc-800 rounded-2xl text-zinc-400">
                <p className="text-sm italic">No timeline data available for this campaign.</p>
            </div>
        );
    }

    // Sort items by start date
    const sortedItems = [...items].sort((a, b) => new Date(a.start_date).getTime() - new Date(b.start_date).getTime());

    // Calculate chart range
    const minDate = new Date(Math.min(...sortedItems.map(i => new Date(i.start_date).getTime())));
    const maxDate = new Date(Math.max(...sortedItems.map(i => new Date(i.end_date).getTime())));

    // Add some padding to the range (e.g., 7 days)
    minDate.setDate(minDate.getDate() - 2);
    maxDate.setDate(maxDate.getDate() + 2);

    const totalDays = Math.ceil((maxDate.getTime() - minDate.getTime()) / (1000 * 60 * 60 * 24));

    return (
        <div className={cn("space-y-6 overflow-x-auto pb-4", className)}>
            <div className="min-w-[800px]">
                {/* Header (Dates) */}
                <div className="grid grid-cols-[200px_1fr] border-b border-zinc-100 dark:border-zinc-800 pb-2 mb-4">
                    <div className="text-[10px] font-bold uppercase tracking-widest text-zinc-400">Strategic Milestone</div>
                    <div className="relative h-4">
                        <div className="absolute inset-0 flex justify-between px-2">
                            <span className="text-[10px] text-zinc-400">{minDate.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}</span>
                            <span className="text-[10px] text-zinc-400">{maxDate.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}</span>
                        </div>
                    </div>
                </div>

                {/* Rows */}
                <div className="space-y-3">
                    {sortedItems.map((item) => {
                        const start = new Date(item.start_date);
                        const end = new Date(item.end_date);

                        const startOffset = Math.max(0, (start.getTime() - minDate.getTime()) / (1000 * 60 * 60 * 24));
                        const duration = (end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24);

                        const leftPercent = (startOffset / totalDays) * 100;
                        const widthPercent = (duration / totalDays) * 100;

                        return (
                            <div key={item.id} className="grid grid-cols-[200px_1fr] items-center group">
                                <div className="text-sm font-medium text-zinc-700 dark:text-zinc-300 pr-4 truncate">
                                    {item.task}
                                </div>
                                <div className="relative h-8 bg-zinc-50 dark:bg-zinc-900/30 rounded-lg overflow-hidden">
                                    {/* Grid Lines (Weekly) */}
                                    <div className="absolute inset-0 flex justify-between pointer-events-none opacity-20">
                                        {Array.from({ length: Math.ceil(totalDays / 7) }).map((_, i) => (
                                            <div key={i} className="w-px h-full bg-zinc-300 dark:bg-zinc-700" style={{ left: `${(i * 7 / totalDays) * 100}%` }} />
                                        ))}
                                    </div>

                                    {/* Bar */}
                                    <div
                                        className="absolute top-1 bottom-1 bg-zinc-900 dark:bg-white rounded-md shadow-sm transition-all group-hover:opacity-90"
                                        style={{
                                            left: `${leftPercent}%`,
                                            width: `${widthPercent}%`
                                        }}
                                    >
                                        {/* Progress Overlay */}
                                        <div
                                            className="absolute inset-0 bg-emerald-500/30"
                                            style={{ width: `${item.progress * 100}%` }}
                                        />

                                        {/* Label on Hover */}
                                        <div className="absolute inset-0 flex items-center px-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                            <span className="text-[10px] font-bold text-white dark:text-zinc-900 drop-shadow-sm">
                                                {Math.round(item.progress * 100)}%
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}
