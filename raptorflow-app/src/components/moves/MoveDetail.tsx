'use client';

import React, { useState } from 'react';
import { Dialog, DialogContent } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Move, MoveSelfReport } from '@/lib/campaigns-types';
import {
    updateMove,
    toggleChecklistItem,
    extendMove,
    isMoveOverdue,
    generateWeeklyMoves
} from '@/lib/campaigns';
import { useInferenceStatus } from '@/hooks/useInferenceStatus';
import { OverdueBanner } from './OverdueBanner';
import {
    CheckSquare,
    Square,
    Calendar,
    Target,
    Zap,
    Sparkles,
    MoreHorizontal,
    Trash2,
    Check,
    Loader2
} from 'lucide-react';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { toast } from 'sonner';

interface MoveDetailProps {
    move: Move | null;
    open: boolean;
    onOpenChange: (open: boolean) => void;
    onUpdate: (move: Move) => void;
    onDelete: (moveId: string) => void;
    onRefresh?: () => void;
}

export function MoveDetail({ move, open, onOpenChange, onUpdate, onDelete, onRefresh }: MoveDetailProps) {
    const [completing, setCompleting] = useState(false);
    const [whatHappened, setWhatHappened] = useState('');
    const [metricValue, setMetricValue] = useState('');

    const { status: agentStatus, messages: agentMessages } = useInferenceStatus(
        move?.status === 'active' && move.campaignId ? move.campaignId : null
    );

    if (!move) return null;

    const handleGenerateAgenticMoves = async () => {
        if (!move.campaignId) return;
        
        toast.promise(generateWeeklyMoves(move.campaignId), {
            loading: 'Triggering agentic move decomposition...',
            success: 'Decomposition started. Watch the live feed.',
            error: 'Failed to trigger agent'
        });
    };

    const daysOverdue = move.dueDate
        ? Math.ceil((Date.now() - new Date(move.dueDate).getTime()) / (1000 * 60 * 60 * 24))
        : 0;

    const isOverdue = daysOverdue > 0 && move.status === 'active';

    const handleToggleChecklist = (itemId: string) => {
        toggleChecklistItem(move.id, itemId);
        // Optimistic update locally
        const updatedChecklist = move.checklist.map(item =>
            item.id === itemId ? { ...item, completed: !item.completed } : item
        );
        onUpdate({ ...move, checklist: updatedChecklist });
    };

    const handleExtend = () => {
        extendMove(move.id, 3);
        const newDate = new Date(move.dueDate!);
        newDate.setDate(newDate.getDate() + 3);
        onUpdate({ ...move, dueDate: newDate.toISOString() });
        toast.success('Move extended by 3 days');
    };

    const handleAbandon = async () => {
        if (!confirm('Abandon this move? It will be marked as failed.')) return;
        const updated = { ...move, status: 'abandoned' as const, completedAt: new Date().toISOString() };
        await updateMove(updated);
        onUpdate(updated);
        onOpenChange(false);
        toast.info('Move abandoned');
    };

    const handleComplete = () => {
        setCompleting(true);
    };

    const submitCompletion = async () => {
        const report: MoveSelfReport = {
            didComplete: true,
            whatHappened,
            metrics: metricValue ? { name: move.goal, value: parseInt(metricValue) } : undefined,
            submittedAt: new Date().toISOString(),
        };

        const updated: Move = {
            ...move,
            status: 'completed',
            completedAt: new Date().toISOString(),
            selfReport: report
        };

        await updateMove(updated);
        onUpdate(updated);
        setCompleting(false);
        onOpenChange(false);
        toast.success('Move completed successfully!');
    };

    // Group checklist items
    const groups = {
        setup: move.checklist.filter(i => i.group === 'setup'),
        create: move.checklist.filter(i => i.group === 'create'),
        publish: move.checklist.filter(i => i.group === 'publish'),
        followup: move.checklist.filter(i => i.group === 'followup'),
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-3xl p-0 gap-0 bg-zinc-50 dark:bg-zinc-950 h-[85vh] flex flex-col overflow-hidden">
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 shrink-0">
                    <div>
                        <div className="flex items-center gap-3 mb-1">
                            <h2 className="text-xl font-display font-semibold text-zinc-900 dark:text-zinc-100">
                                {move.name}
                            </h2>
                            <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium uppercase tracking-wide
                                ${move.status === 'active' ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-400' : 'bg-zinc-100 text-zinc-500'}
                            `}>
                                {move.status}
                            </span>
                        </div>
                        <div className="flex items-center gap-4 text-sm text-zinc-500">
                            <div className="flex items-center gap-1.5">
                                <Target className="w-4 h-4" />
                                {move.goal}
                            </div>
                            {move.campaignName && (
                                <div className="flex items-center gap-1.5">
                                    <div className="w-1 h-1 rounded-full bg-zinc-300" />
                                    {move.campaignName}
                                </div>
                            )}
                        </div>
                    </div>

                    <div className="flex items-center gap-2">
                        {move.status === 'active' && move.campaignId && (
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={handleGenerateAgenticMoves}
                                disabled={agentStatus === 'generating'}
                                className="h-8 rounded-full border-accent/20 bg-accent/5 text-accent hover:bg-accent/10 transition-all"
                            >
                                {agentStatus === 'generating' ? (
                                    <>
                                        <Loader2 className="w-3 h-3 mr-2 animate-spin" />
                                        Thinking...
                                    </>
                                ) : (
                                    <>
                                        <Sparkles className="w-3 h-3 mr-2" />
                                        Agentic Move Pack
                                    </>
                                )}
                            </Button>
                        )}
                        <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                                <Button variant="ghost" size="icon" className="h-8 w-8">
                                    <MoreHorizontal className="w-4 h-4" />
                                </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                                <DropdownMenuItem className="text-red-600" onClick={() => {
                                    if (confirm('Delete this move entirely?')) {
                                        onDelete(move.id);
                                        onOpenChange(false);
                                    }
                                }}>
                                    <Trash2 className="w-4 h-4 mr-2" />
                                    Delete Move
                                </DropdownMenuItem>
                            </DropdownMenuContent>
                        </DropdownMenu>
                        <Button variant="ghost" size="icon" onClick={() => onOpenChange(false)}>
                            <span className="sr-only">Close</span>
                            <span className="text-2xl leading-none">&times;</span>
                        </Button>
                    </div>
                </div>

                {/* Body */}
                <div className="flex-1 overflow-y-auto p-8 space-y-8">
                    {/* Completion Mode Overlay */}
                    {completing ? (
                        <div className="bg-white dark:bg-zinc-900 rounded-xl p-8 border border-zinc-200 dark:border-zinc-800 shadow-lg space-y-6 animate-in fade-in zoom-in-95">
                            <h3 className="text-xl font-semibold">Complete Mission</h3>

                            <div className="space-y-2">
                                <label className="text-sm font-medium">What happened? (The truth)</label>
                                <textarea
                                    value={whatHappened}
                                    onChange={e => setWhatHappened(e.target.value)}
                                    className="w-full h-32 p-3 rounded-xl border bg-transparent text-sm"
                                    placeholder="Brief summary of results..."
                                />
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium">Any hard numbers? (Optional)</label>
                                <input
                                    type="number"
                                    value={metricValue}
                                    onChange={e => setMetricValue(e.target.value)}
                                    className="w-full p-3 rounded-xl border bg-transparent text-sm"
                                    placeholder={`e.g. Number of ${move.goal}`}
                                />
                            </div>

                            <div className="flex justify-end gap-3 pt-4">
                                <Button variant="ghost" onClick={() => setCompleting(false)}>Cancel</Button>
                                <Button onClick={submitCompletion} className="bg-emerald-600 hover:bg-emerald-700 text-white">
                                    Confirm Completion
                                </Button>
                            </div>
                        </div>
                    ) : (
                        <>
                            {isOverdue && (
                                <OverdueBanner
                                    daysOverdue={daysOverdue}
                                    onComplete={handleComplete}
                                    onExtend={handleExtend}
                                    onAbandon={handleAbandon}
                                />
                            )}

                            {/* Checklist */}
                            <div className="space-y-6">
                                {Object.entries(groups).map(([group, items]) => items.length > 0 && (
                                    <div key={group}>
                                        <h3 className="text-xs font-bold uppercase tracking-widest text-zinc-400 mb-3 ml-1">
                                            {group} Phase
                                        </h3>
                                        <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl overflow-hidden">
                                            {items.map(item => (
                                                <div
                                                    key={item.id}
                                                    className="flex items-start gap-3 p-4 border-b border-zinc-100 dark:border-zinc-800 last:border-0 hover:bg-zinc-50 dark:hover:bg-zinc-800/50 transition-colors cursor-pointer"
                                                    onClick={() => handleToggleChecklist(item.id)}
                                                >
                                                    <div className={`mt-0.5 w-5 h-5 rounded border flex items-center justify-center transition-colors ${item.completed
                                                            ? 'bg-emerald-500 border-emerald-500 text-white'
                                                            : 'bg-white dark:bg-zinc-900 border-zinc-300 dark:border-zinc-700 text-transparent hover:border-zinc-400'
                                                        }`}>
                                                        <Check className="w-3.5 h-3.5" />
                                                    </div>
                                                    <div className={`flex-1 text-sm ${item.completed ? 'text-zinc-400 line-through' : 'text-zinc-700 dark:text-zinc-300'}`}>
                                                        {item.label}
                                                    </div>
                                                    {item.assetLink && (
                                                        <div className="text-xs text-blue-500 flex items-center gap-1">
                                                            <Sparkles className="w-3 h-3" /> Asset
                                                        </div>
                                                    )}
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </>
                    )}
                </div>

                {/* Footer Controls */}
                {!completing && move.status === 'active' && (
                    <div className="p-4 border-t border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 flex justify-between items-center">
                        <div className="text-xs text-zinc-400">
                            {move.checklist.filter(i => i.completed).length}/{move.checklist.length} tasks done
                        </div>
                        <Button onClick={handleComplete} className="bg-zinc-900 text-white hover:bg-zinc-800 dark:bg-white dark:text-zinc-900 px-6">
                            Complete Move
                        </Button>
                    </div>
                )}
            </DialogContent>
        </Dialog>
    );
}
