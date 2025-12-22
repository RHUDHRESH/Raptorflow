'use client';

import React, { useState } from 'react';
import { Dialog, DialogContent } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import {
    Campaign,
    OBJECTIVE_LABELS,
    CHANNEL_LABELS,
    OFFER_LABELS,
    CampaignStatus
} from '@/lib/campaigns-types';
import {
    getCampaignProgress,
    getMovesByCampaign,
    getActiveMove,
    updateCampaign,
    setActiveMove
} from '@/lib/campaigns';
import {
    CheckCircle2,
    Clock,
    MoreHorizontal,
    Play,
    StopCircle,
    Archive,
    Trash2,
    Calendar,
    Target
} from 'lucide-react';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { toast } from 'sonner';

interface CampaignDetailProps {
    campaign: Campaign | null;
    open: boolean;
    onOpenChange: (open: boolean) => void;
    onUpdate: (campaign: Campaign) => void;
    onDelete: (campaignId: string) => void;
    onRefresh: () => void;
}

export function CampaignDetail({
    campaign,
    open,
    onOpenChange,
    onUpdate,
    onDelete,
    onRefresh
}: CampaignDetailProps) {
    if (!campaign) return null;

    const progress = getCampaignProgress(campaign.id);
    const moves = getMovesByCampaign(campaign.id);
    const activeMove = moves.find(m => m.status === 'active');
    const nextMove = moves.find(m => m.status === 'queued' || m.status === 'draft');

    const handleStatusChange = (status: Campaign['status']) => {
        const updated = { ...campaign, status };
        updateCampaign(updated);
        onUpdate(updated);
        toast.success(`Campaign ${status}`);
    };

    const handleStartNextMove = () => {
        if (!nextMove) return;
        // Check if there is already a global active move (in real app)
        // For this component we assume we can just switch
        setActiveMove(nextMove.id);
        onRefresh();
        toast.success(`Started move: ${nextMove.name}`);
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-4xl p-0 gap-0 bg-zinc-50 dark:bg-zinc-950 h-[85vh] flex flex-col overflow-hidden">
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 shrink-0">
                    <div>
                        <div className="flex items-center gap-3 mb-1">
                            <h2 className="text-xl font-display font-semibold text-zinc-900 dark:text-zinc-100">
                                {campaign.name}
                            </h2>
                            <span className="px-2 py-0.5 rounded-full bg-zinc-100 dark:bg-zinc-800 text-[10px] font-medium uppercase tracking-wide text-zinc-500">
                                Week {progress.weekNumber} of {progress.totalWeeks}
                            </span>
                        </div>
                        <div className="flex items-center gap-4 text-sm text-zinc-500">
                            <div className="flex items-center gap-1.5">
                                <Target className="w-4 h-4" />
                                {OBJECTIVE_LABELS[campaign.objective].label}
                            </div>
                            <div className="flex items-center gap-1.5">
                                <div className="w-1 h-1 rounded-full bg-zinc-300" />
                                {campaign.cohortName}
                            </div>
                        </div>
                    </div>

                    <div className="flex items-center gap-2">
                        <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                                <Button variant="ghost" size="icon" className="h-8 w-8">
                                    <MoreHorizontal className="w-4 h-4" />
                                </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                                <DropdownMenuItem onClick={() => handleStatusChange(campaign.status === 'active' ? 'paused' : 'active')}>
                                    {campaign.status === 'active' ? 'Pause Campaign' : 'Resume Campaign'}
                                </DropdownMenuItem>
                                <DropdownMenuSeparator />
                                <DropdownMenuItem className="text-red-600" onClick={() => {
                                    if (confirm('Are you sure? This cannot be undone.')) {
                                        onDelete(campaign.id);
                                    }
                                }}>
                                    <Trash2 className="w-4 h-4 mr-2" />
                                    Delete Campaign
                                </DropdownMenuItem>
                            </DropdownMenuContent>
                        </DropdownMenu>
                        <Button variant="ghost" size="icon" onClick={() => onOpenChange(false)}>
                            <span className="sr-only">Close</span>
                            <span className="text-2xl leading-none">&times;</span>
                        </Button>
                    </div>
                </div>

                {/* Body (Scrollable) */}
                <div className="flex-1 overflow-y-auto p-8 space-y-10">
                    {/* Hero: Current Move */}
                    <section>
                        <h3 className="text-xs font-bold uppercase tracking-widest text-zinc-400 mb-4">Current Focus</h3>
                        {activeMove ? (
                            <div className="bg-white dark:bg-zinc-900 rounded-2xl p-8 border border-zinc-200 dark:border-zinc-800 shadow-sm relative overflow-hidden group">
                                <div className="absolute top-0 left-0 w-1 h-full bg-emerald-500" />
                                <div className="flex justify-between items-start mb-6">
                                    <div>
                                        <div className="flex items-center gap-2 text-emerald-600 mb-2">
                                            <div className="w-2 h-2 rounded-full bg-current animate-pulse" />
                                            <span className="text-xs font-bold uppercase tracking-wide">In Progress</span>
                                        </div>
                                        <h2 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-100">
                                            {activeMove.name}
                                        </h2>
                                        <p className="text-zinc-500 mt-1">
                                            {CHANNEL_LABELS[activeMove.channel]} • {activeMove.duration} Day Sprint
                                        </p>
                                    </div>
                                    <Button className="bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl">
                                        Open Move
                                    </Button>
                                </div>

                                <div className="grid grid-cols-3 gap-8 pt-6 border-t border-zinc-100 dark:border-zinc-800">
                                    <div>
                                        <div className="text-xs text-zinc-400 uppercase font-medium mb-1">Micro-Goal</div>
                                        <div className="font-medium text-zinc-900 dark:text-zinc-100 capitalize">{activeMove.goal}</div>
                                    </div>
                                    <div>
                                        <div className="text-xs text-zinc-400 uppercase font-medium mb-1">Checklist</div>
                                        <div className="font-medium text-zinc-900 dark:text-zinc-100">
                                            {activeMove.checklist?.filter(i => i.completed).length} / {activeMove.checklist?.length} done
                                        </div>
                                    </div>
                                    <div>
                                        <div className="text-xs text-zinc-400 uppercase font-medium mb-1">Daily Effort</div>
                                        <div className="font-medium text-zinc-900 dark:text-zinc-100">{activeMove.dailyEffort} min</div>
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div className="bg-amber-50 dark:bg-amber-900/10 rounded-2xl p-8 border border-amber-200 dark:border-amber-800/30 text-center">
                                <h3 className="text-lg font-medium text-amber-900 dark:text-amber-100 mb-2">
                                    No active move
                                </h3>
                                <p className="text-amber-700 dark:text-amber-400 mb-6 max-w-sm mx-auto">
                                    Momentum is zero. Start the next move to keep the campaign alive.
                                </p>
                                {nextMove ? (
                                    <Button
                                        onClick={handleStartNextMove}
                                        className="bg-amber-600 hover:bg-amber-700 text-white"
                                    >
                                        <Play className="w-4 h-4 mr-2" />
                                        Start Next Move
                                    </Button>
                                ) : (
                                    <Button variant="outline" className="border-amber-300 text-amber-800">
                                        Plan New Move
                                    </Button>
                                )}
                            </div>
                        )}
                    </section>

                    {/* Timeline */}
                    <section>
                        <h3 className="text-xs font-bold uppercase tracking-widest text-zinc-400 mb-4">Moves Timeline</h3>
                        <div className="space-y-4 relative">
                            <div className="absolute left-[19px] top-4 bottom-4 w-px bg-zinc-200 dark:bg-zinc-800" />
                            {moves.map((move, i) => {
                                const isDone = move.status === 'completed';
                                const isActive = move.status === 'active';
                                const isFuture = move.status === 'queued' || move.status === 'draft';

                                return (
                                    <div key={move.id} className="relative pl-12 group">
                                        <div className={`absolute left-[11px] top-3 w-4 h-4 rounded-full border-2 transition-colors z-10 bg-white dark:bg-zinc-900 ${isActive
                                                ? 'border-emerald-500 ring-4 ring-emerald-50 dark:ring-emerald-900/30'
                                                : isDone
                                                    ? 'border-zinc-300 bg-zinc-100 dark:border-zinc-700 dark:bg-zinc-800'
                                                    : 'border-zinc-200 dark:border-zinc-800'
                                            }`} />

                                        <div className={`p-4 rounded-xl border transition-all ${isActive
                                                ? 'bg-white dark:bg-zinc-900 border-zinc-200 dark:border-zinc-700 shadow-sm'
                                                : 'bg-transparent border-transparent hover:bg-zinc-50 dark:hover:bg-zinc-900/50'
                                            }`}>
                                            <div className="flex justify-between items-center">
                                                <div>
                                                    <div className="font-medium text-zinc-900 dark:text-zinc-100">
                                                        {move.name}
                                                    </div>
                                                    <div className="text-sm text-zinc-500">
                                                        {move.duration} days • {CHANNEL_LABELS[move.channel]}
                                                    </div>
                                                </div>
                                                <div className="text-xs font-medium uppercase tracking-wide px-2 py-1 rounded bg-zinc-100 dark:bg-zinc-800 text-zinc-500">
                                                    {move.status}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </section>

                    {/* Stats (Lightweight) */}
                    <section className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                        <div className="p-4 bg-zinc-50 dark:bg-zinc-900/50 rounded-xl border border-zinc-100 dark:border-zinc-800">
                            <div className="text-xs text-zinc-500 mb-1">Time Elapsed</div>
                            <div className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
                                {Math.round(((Date.now() - new Date(campaign.createdAt).getTime()) / (1000 * 60 * 60 * 24)))} days
                            </div>
                        </div>
                        <div className="p-4 bg-zinc-50 dark:bg-zinc-900/50 rounded-xl border border-zinc-100 dark:border-zinc-800">
                            <div className="text-xs text-zinc-500 mb-1">Moves Completed</div>
                            <div className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
                                {moves.filter(m => m.status === 'completed').length} / {moves.length}
                            </div>
                        </div>
                    </section>
                </div>
            </DialogContent>
        </Dialog>
    );
}
