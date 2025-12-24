'use client';

import React, { useState, useEffect } from 'react';
import { Campaign, OBJECTIVE_LABELS, CHANNEL_LABELS } from '@/lib/campaigns-types';
import { ChevronRight } from 'lucide-react';
import { InferenceStatusIndicator } from './InferenceStatusIndicator';
import { useInferenceStatus } from '@/hooks/useInferenceStatus';
import { getCampaignProgress } from '@/lib/campaigns';

interface CampaignCardProps {
    campaign: Campaign;
    progress?: {
        totalMoves: number;
        completedMoves: number;
        weekNumber: number;
        totalWeeks: number;
    };
    activeMove?: any;
    onClick: () => void;
}

export function CampaignCard({ campaign, progress: initialProgress, activeMove, onClick }: CampaignCardProps) {
    const [progress, setProgress] = useState(initialProgress);

    const { status: agentStatus } = useInferenceStatus(
        campaign.status === 'active' && !activeMove ? campaign.id : null
    );

    useEffect(() => {
        if (!initialProgress) {
            getCampaignProgress(campaign.id).then(setProgress);
        }
    }, [campaign.id, initialProgress]);

    const statusColors: Record<Campaign['status'], string> = {
        planned: 'bg-zinc-100 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400',
        active: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400',
        paused: 'bg-amber-50 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400',
        wrapup: 'bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
        archived: 'bg-zinc-100 text-zinc-500 dark:bg-zinc-800/50 dark:text-zinc-500',
    };

    const statusLabels: Record<Campaign['status'], string> = {
        planned: 'Planned',
        active: 'Active',
        paused: 'Paused',
        wrapup: 'Wrap-up',
        archived: 'Archived',
    };

    return (
        <button
            onClick={onClick}
            className="w-full text-left bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-5 hover:border-zinc-300 dark:hover:border-zinc-700 hover:shadow-md active:scale-[0.99] transition-all duration-200 group"
        >
            <div className="flex items-start justify-between gap-4">
                {/* Left side: Campaign info */}
                <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                        <h3 className="text-base font-semibold text-zinc-900 dark:text-zinc-100 truncate">
                            {campaign.name}
                        </h3>
                        <span className={`text-[10px] font-medium uppercase tracking-wide px-2 py-0.5 rounded-full ${statusColors[campaign.status]}`}>
                            {statusLabels[campaign.status]}
                        </span>
                    </div>

                    <div className="flex items-center gap-3 text-sm text-zinc-500 dark:text-zinc-400 mb-3">
                        <span className="font-medium text-zinc-700 dark:text-zinc-300">
                            {OBJECTIVE_LABELS[campaign.objective].label}
                        </span>
                        {campaign.cohortName && (
                            <>
                                <span className="text-zinc-300 dark:text-zinc-600">•</span>
                                <span>{campaign.cohortName}</span>
                            </>
                        )}
                        {progress && (
                            <>
                                <span className="text-zinc-300 dark:text-zinc-600">•</span>
                                <span>Week {progress.weekNumber} of {progress.totalWeeks}</span>
                            </>
                        )}
                    </div>

                    {/* Inference Indicator */}
                    {campaign.status === 'active' && !activeMove && (
                        <div className="mb-3">
                            <InferenceStatusIndicator status={agentStatus === 'idle' ? 'generating' : agentStatus === 'complete' ? 'complete' : agentStatus === 'error' ? 'error' : 'generating'} />
                        </div>
                    )}

                    {/* Current Move */}
                    {activeMove ? (
                        <div className="flex items-center gap-2 text-sm">
                            <span className="text-zinc-400 dark:text-zinc-500">Current Move:</span>
                            <span className="font-medium text-zinc-700 dark:text-zinc-300">
                                {activeMove.name}
                            </span>
                        </div>
                    ) : campaign.status === 'active' ? (
                        <div className="text-sm text-amber-600 dark:text-amber-400">
                            No active move — start one to continue
                        </div>
                    ) : null}

                    {/* Progress bar */}
                    {progress && progress.totalMoves > 0 && (
                        <div className="mt-3 flex items-center gap-2">
                            <div className="flex-1 h-1 bg-zinc-100 dark:bg-zinc-800 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-zinc-400 dark:bg-zinc-500 rounded-full transition-all"
                                    style={{ width: `${(progress.completedMoves / progress.totalMoves) * 100}%` }}
                                />
                            </div>
                            <span className="text-[10px] text-zinc-400 dark:text-zinc-500">
                                {progress.completedMoves}/{progress.totalMoves} moves
                            </span>
                        </div>
                    )}
                </div>

                {/* Right side: Action indicator */}
                <div className="flex items-center">
                    <ChevronRight className="w-5 h-5 text-zinc-300 dark:text-zinc-600 group-hover:text-zinc-400 dark:group-hover:text-zinc-500 transition-colors" />
                </div>
            </div>
        </button>
    );
}
