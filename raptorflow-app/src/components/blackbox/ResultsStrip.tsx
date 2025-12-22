'use client';

import React from 'react';
import { Trophy, Lightbulb, ArrowRight } from 'lucide-react';
import { LearningArtifact, Experiment } from '@/lib/blackbox-types';
import { Button } from '@/components/ui/button';

interface ResultsStripProps {
    winner?: Experiment;
    learnings: LearningArtifact[];
    onRunAgain?: () => void;
}

export function ResultsStrip({ winner, learnings, onRunAgain }: ResultsStripProps) {
    const recentLearning = learnings[0];

    if (!winner && learnings.length === 0) return null;

    return (
        <div className="flex items-center gap-6 p-4 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900">
            {/* Winner */}
            <div className="flex items-center gap-3 flex-1 min-w-0">
                <div className="w-10 h-10 rounded-lg bg-zinc-900 dark:bg-white flex items-center justify-center shrink-0">
                    <Trophy className="w-5 h-5 text-white dark:text-zinc-900" />
                </div>
                <div className="min-w-0">
                    <p className="text-[10px] font-semibold uppercase tracking-widest text-zinc-400 font-sans">Winner</p>
                    <h4 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100 truncate font-sans">
                        {winner?.title || "—"}
                    </h4>
                </div>
            </div>

            <div className="w-px h-8 bg-zinc-200 dark:bg-zinc-800" />

            {/* Learning */}
            <div className="flex items-center gap-3 flex-[1.5] min-w-0">
                <Lightbulb className="w-4 h-4 text-zinc-400 shrink-0" />
                <p className="text-xs text-zinc-500 italic truncate font-sans">
                    {recentLearning?.summary || "Complete experiments to see insights."}
                </p>
            </div>

            {winner && onRunAgain && (
                <Button
                    onClick={onRunAgain}
                    size="sm"
                    variant="ghost"
                    className="rounded-lg text-zinc-500 shrink-0 font-sans"
                >
                    Run Again
                    <ArrowRight className="w-3 h-3 ml-1" />
                </Button>
            )}
        </div>
    );
}
