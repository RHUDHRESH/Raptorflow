'use client';

import React, { useState, useCallback, useMemo, useEffect } from 'react';
import { AppLayout } from '@/components/layout/AppLayout';
import { InferenceErrorBoundary } from '@/components/layout/InferenceErrorBoundary';
import { Move, ChecklistItem } from '@/lib/campaigns-types';
import {
    Plus, Search, Filter, Calendar, BarChart2, MoreHorizontal,
    ArrowRight, Check, Play, Clock, Target, AlertCircle,
    Zap, Circle, ChevronRight, Sparkles
} from 'lucide-react';
import { toast } from 'sonner';
import { MoveCalendarView } from '@/components/moves/MoveCalendarView';
import Link from 'next/link';
import { useFoundation } from '@/context/FoundationProvider';

// Helper to generate moves from Foundation
function generateMovesFromFoundation(ops: any, messaging: any): Move[] {
    const moves: Move[] = [];

    // 1. GTM Channel Moves
    if (ops?.go_to_market?.channels_top3) {
        ops.go_to_market.channels_top3.forEach((channel: string, idx: number) => {
            moves.push({
                id: `move-channel-${idx}`,
                name: `Launch ${channel} Campaign`,
                goal: 'leads',
                channel: channel.toLowerCase(),
                duration: 14,
                dailyEffort: idx === 0 ? 60 : 30,
                description: `Establish dominance in ${channel} using new messaging foundation.`,
                outcomeTarget: '50 qualified leads',
                checklist: [
                    { id: `t-${idx}-1`, label: `Audit existing ${channel} presence`, completed: true, group: 'setup' },
                    { id: `t-${idx}-2`, label: 'Draft content calendar', completed: false, group: 'create' },
                    { id: `t-${idx}-3`, label: 'Setup tracking pixels', completed: false, group: 'setup' },
                    { id: `t-${idx}-4`, label: 'Launch initial creative test', completed: false, group: 'publish' },
                ],
                assetIds: [],
                status: idx === 0 ? 'active' : 'draft',
                createdAt: new Date().toISOString(),
                startedAt: idx === 0 ? new Date().toISOString() : undefined,
                dueDate: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString(),
                campaignId: 'foundation-launch',
                hypothesis: `If we focus on ${channel}, our ICP is most active there.`,
                control: 'Organic only',
                variant: 'Paid + Organic mix',
                success_metric: 'CPA < $50',
                sample_size: '10k impressions',
                action_steps: ['Audit', 'Plan', 'Execute', 'Optimize']
            });
        });
    }

    // 2. Messaging Testing Move
    if (messaging?.message_house?.controlling_idea) {
        moves.push({
            id: 'move-messaging-test',
            name: 'Validate Controlling Idea',
            goal: 'market_research',
            channel: 'email',
            duration: 7,
            dailyEffort: 45,
            description: `Test the resonance of: "${messaging.message_house.controlling_idea}"`,
            outcomeTarget: '30% reply rate on outreach',
            checklist: [
                { id: 'msg-1', label: 'Create 3 variant subject lines', completed: false, group: 'create' },
                { id: 'msg-2', label: 'Build list of 100 ICP prospects', completed: false, group: 'setup' },
                { id: 'msg-3', label: 'Send cold email sequence', completed: false, group: 'publish' },
            ],
            assetIds: [],
            status: 'active',
            createdAt: new Date().toISOString(),
            dueDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
            campaignId: 'foundation-launch',
            hypothesis: 'The new controlling idea will outperform generic messaging.',
            control: 'Feature-based messaging',
            variant: 'Narrative-led messaging',
            success_metric: 'Reply Rate',
            sample_size: '100 prospects',
            action_steps: ['Draft', 'List Build', 'Send', 'Analyze']
        });
    }

    return moves;
}

type StatusFilter = 'active' | 'completed' | 'all';

export default function MovesPage() {
    const { getBusiness, getMessaging, isLoading } = useFoundation();
    // In a real app we'd get Ops data too, accessing via business for now or assuming structure
    // Since OpsData is on root foundation, let's use the full object access if needed or modify provider
    // The provider generic `foundation` object has everything.
    const { foundation } = useFoundation();

    // Generate moves from Foundation
    const foundationMoves = useMemo(() => {
        if (!foundation) return [];
        return generateMovesFromFoundation(foundation.ops, foundation.messaging);
    }, [foundation]);

    const [moves, setMoves] = useState<Move[]>([]);
    const [selectedMove, setSelectedMove] = useState<Move | null>(null);
    const [statusFilter, setStatusFilter] = useState<StatusFilter>('active');

    // Initialize moves when foundation loads
    useEffect(() => {
        if (foundationMoves.length > 0 && moves.length === 0) {
            setMoves(foundationMoves);
        }
    }, [foundationMoves, moves.length]);

    // Filter moves
    const filteredMoves = moves.filter(move => {
        if (statusFilter === 'all') return true;
        return move.status === statusFilter;
    });

    // Calculate overall progress
    const totalMoves = moves.length;
    const completedMoves = moves.filter(m => m.status === 'completed').length;

    // Get all tasks for "Today's Focus"
    const todayTasks = useMemo(() => {
        const tasks: (ChecklistItem & { moveName: string, moveId: string })[] = [];
        moves.filter(m => m.status === 'active').forEach(move => {
            // For demo, just showing the first 3 uncompleted tasks as "today's tasks"
            const uncompleted = move.checklist?.filter(t => !t.completed) || [];
            uncompleted.slice(0, 3).forEach(task => {
                tasks.push({ ...task, moveName: move.name, moveId: move.id });
            });
        });
        return tasks;
    }, [moves]);

    const completedCount = todayTasks.filter(t => t.completed).length;
    const totalCount = todayTasks.length;
    const progressPercent = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0;

    // Handle task toggle from main view
    const handleToggleTask = useCallback((task: ChecklistItem & { moveId: string }) => {
        setMoves(prevMoves => prevMoves.map(move => {
            if (move.id !== task.moveId || !move.checklist) return move;

            return {
                ...move,
                checklist: move.checklist.map(t =>
                    t.id === task.id ? { ...t, completed: !t.completed } : t
                )
            };
        }));
        toast.success(task.completed ? 'Unchecked' : 'Done!');
    }, []);

    // Handle task update from calendar view
    const handleUpdateTask = useCallback((moveId: string, taskId: string, completed: boolean) => {
        setMoves(prevMoves => prevMoves.map(move => {
            if (move.id !== moveId || !move.checklist) return move;
            return {
                ...move,
                checklist: move.checklist.map(t =>
                    t.id === taskId ? { ...t, completed } : t
                )
            };
        }));
    }, []);

    if (isLoading) {
        return (
            <AppLayout>
                <div className="flex items-center justify-center min-h-[60vh]">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                </div>
            </AppLayout>
        );
    }

    if (!moves.length && !isLoading && foundationMoves.length === 0) {
        return (
            <AppLayout>
                <div className="flex flex-col items-center justify-center min-h-[60vh] text-center px-8">
                    <div className="w-20 h-20 rounded-full bg-muted flex items-center justify-center mb-6">
                        <Zap className="w-10 h-10 text-muted-foreground" />
                    </div>
                    <h1 className="font-serif text-4xl mb-4">No Moves Generated Yet</h1>
                    <p className="text-muted-foreground max-w-md mb-8">
                        Fill out your Foundation (specifically Ops &rarr; GTM Channels) to generate your first strategic moves.
                    </p>
                    <Link
                        href="/foundation"
                        className="inline-flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground rounded-xl font-medium hover:bg-primary/90 transition-colors"
                    >
                        Go to Foundation <ArrowRight className="w-4 h-4" />
                    </Link>
                </div>
            </AppLayout>
        )
    }

    return (
        <AppLayout>
            <InferenceErrorBoundary>
                <div className="min-h-screen px-6 lg:px-12 py-8">
                    <div className="max-w-5xl mx-auto">

                        {/* Header */}
                        <header className="flex items-center justify-between mb-8">
                            <div className="flex items-baseline gap-4">
                                <h1 className="font-serif text-[32px] text-[#2D3538]">Moves</h1>
                                <span className="text-[13px] text-[#9D9F9F]">{completedMoves}/{totalMoves} done</span>
                            </div>
                        </header>

                        <div className="grid grid-cols-12 gap-8">

                            {/* MAIN CONTENT (7 cols) */}
                            <main className="col-span-12 lg:col-span-7">
                                {/* Today's Focus Card */}
                                <div className="bg-white rounded-2xl border border-[#C0C1BE]/50 p-6 mb-8 hover:border-[#2D3538]/30 transition-colors shadow-sm">
                                    <div className="flex items-center justify-between mb-6">
                                        <div className="flex items-center gap-3">
                                            <div className="w-10 h-10 rounded-xl bg-[#2D3538] text-white flex items-center justify-center">
                                                <Zap className="w-5 h-5" />
                                            </div>
                                            <div>
                                                <p className="text-[11px] font-semibold uppercase tracking-wider text-[#9D9F9F]">Today's Focus</p>
                                                <p className="text-[15px] font-medium text-[#2D3538]">
                                                    {totalCount === 0 ? 'No tasks for today' : `${completedCount} of ${totalCount} tasks complete`}
                                                </p>
                                            </div>
                                        </div>
                                        {totalCount > 0 && <span className="font-mono text-[24px] font-semibold text-[#2D3538]">{progressPercent}%</span>}
                                    </div>

                                    {totalCount > 0 && (
                                        <div className="h-1.5 bg-[#E5E6E3] rounded-full overflow-hidden mb-6">
                                            <div
                                                className="h-full bg-[#2D3538] rounded-full transition-all duration-500"
                                                style={{ width: `${progressPercent}%` }}
                                            />
                                        </div>
                                    )}

                                    <div className="space-y-3">
                                        {todayTasks.length > 0 ? (
                                            todayTasks.map((task) => (
                                                <div
                                                    key={`${task.moveId}-${task.id}`}
                                                    className={`group flex items-start gap-3 p-4 rounded-xl transition-all border ${task.completed
                                                        ? 'bg-[#F0FDF4] border-[#22C55E]/20'
                                                        : 'bg-white border-[#E5E6E3] hover:border-[#2D3538]/30'
                                                        }`}
                                                >
                                                    <button
                                                        onClick={() => handleToggleTask(task)}
                                                        className={`mt-0.5 w-5 h-5 rounded-full border-2 flex items-center justify-center transition-all shrink-0 ${task.completed
                                                            ? 'bg-[#22C55E] border-[#22C55E] text-white'
                                                            : 'border-[#C0C1BE] hover:border-[#2D3538]'
                                                            }`}
                                                    >
                                                        {task.completed && <Check className="w-3 h-3" />}
                                                    </button>

                                                    <div className="flex-1 min-w-0">
                                                        <span className={`text-[14px] leading-snug block mb-1 ${task.completed ? 'text-[#5B5F61] line-through' : 'text-[#2D3538]'}`}>
                                                            {task.label}
                                                        </span>
                                                        <div className="flex items-center gap-2">
                                                            <span className="text-[10px] text-[#9D9F9F] px-2 py-0.5 bg-[#F8F9F7] rounded border border-[#E5E6E3]">
                                                                {task.moveName}
                                                            </span>
                                                            {task.needsAsset && !task.completed && (
                                                                <Link href="/muse" className="flex items-center gap-1 text-[10px] font-medium text-[#2D3538] hover:underline">
                                                                    <Sparkles className="w-3 h-3" />
                                                                    Create in Muse
                                                                </Link>
                                                            )}
                                                        </div>
                                                    </div>
                                                </div>
                                            ))
                                        ) : (
                                            <div className="text-center py-8 text-[#9D9F9F] text-[13px]">
                                                All caught up for today!
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </main>

                            {/* SIDEBAR (5 cols) */}
                            <aside className="col-span-12 lg:col-span-5">
                                <div className="sticky top-8">
                                    <div className="flex items-center justify-between mb-4">
                                        <h3 className="text-[12px] font-semibold uppercase tracking-wider text-[#9D9F9F]">Your Moves</h3>
                                        <div className="flex items-center gap-4">
                                            <div className="flex items-center gap-2">
                                                {(['active', 'completed', 'all'] as StatusFilter[]).map((tab) => (
                                                    <button
                                                        key={tab}
                                                        onClick={() => setStatusFilter(tab)}
                                                        className={`text-[11px] capitalize transition-colors ${statusFilter === tab
                                                            ? 'text-[#2D3538] font-medium underline underline-offset-4'
                                                            : 'text-[#9D9F9F] hover:text-[#5B5F61]'
                                                            }`}
                                                    >
                                                        {tab}
                                                    </button>
                                                ))}
                                            </div>
                                            <button
                                                onClick={() => toast.info('New move wizard coming soon!')}
                                                className="w-6 h-6 rounded-full bg-[#2D3538] text-white flex items-center justify-center hover:bg-black transition-colors"
                                            >
                                                <Plus className="w-3.5 h-3.5" />
                                            </button>
                                        </div>
                                    </div>

                                    <div className="space-y-4">
                                        {filteredMoves.map((move) => {
                                            const completed = move.checklist?.filter(t => t.completed).length || 0;
                                            const total = move.checklist?.length || 0;
                                            const progress = total > 0 ? Math.round((completed / total) * 100) : 0;
                                            // Calculate current day (simple mock)
                                            const startDate = move.startedAt ? new Date(move.startedAt) : new Date();
                                            const dayNumber = Math.min(Math.floor((new Date().getTime() - startDate.getTime()) / 86400000) + 1, move.duration);

                                            return (
                                                <div
                                                    key={move.id}
                                                    onClick={() => setSelectedMove(move)}
                                                    className="group bg-white rounded-xl border border-[#C0C1BE]/50 p-4 transition-all hover:border-[#2D3538]/30 hover:shadow-md cursor-pointer"
                                                >
                                                    <div className="flex items-start justify-between mb-3">
                                                        <h4 className="text-[15px] font-medium text-[#2D3538]">{move.name}</h4>
                                                        <button
                                                            title="View calendar"
                                                            className="w-6 h-6 rounded-full hover:bg-[#F3F4EE] flex items-center justify-center text-[#9D9F9F] hover:text-[#2D3538] transition-colors"
                                                        >
                                                            <Calendar className="w-3.5 h-3.5" />
                                                        </button>
                                                    </div>

                                                    <div className="flex items-center gap-3 text-[11px] text-[#5B5F61] mb-3">
                                                        <div className="flex items-center gap-1">
                                                            <Clock className="w-3 h-3" />
                                                            <span>Day {dayNumber}/{move.duration}</span>
                                                        </div>
                                                        <div className="flex items-center gap-1">
                                                            <Target className="w-3 h-3" />
                                                            <span className="capitalize">{move.goal}</span>
                                                        </div>
                                                    </div>

                                                    <div className="flex items-center gap-2">
                                                        <div className="flex-1 h-1 bg-[#E5E6E3] rounded-full overflow-hidden">
                                                            <div
                                                                className="h-full bg-[#2D3538] rounded-full"
                                                                style={{ width: `${progress}%` }}
                                                            />
                                                        </div>
                                                        <span className="text-[10px] font-mono text-[#9D9F9F]">{completed}/{total}</span>
                                                    </div>
                                                </div>
                                            );
                                        })}

                                        {filteredMoves.length === 0 && (
                                            <div className="text-center py-8 border border-dashed border-[#C0C1BE] rounded-xl">
                                                <p className="text-[12px] text-[#9D9F9F]">No moves found</p>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </aside>

                        </div>
                    </div>
                </div>

                {/* Calendar Detail View */}
                {selectedMove && (
                    <MoveCalendarView
                        move={selectedMove}
                        onClose={() => setSelectedMove(null)}
                        onUpdateTask={handleUpdateTask}
                    />
                )}
            </InferenceErrorBoundary>
        </AppLayout>
    );
}
