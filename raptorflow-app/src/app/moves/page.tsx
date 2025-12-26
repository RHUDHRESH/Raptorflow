'use client';

import React, { useState, useCallback } from 'react';
import Link from 'next/link';
import { AppLayout } from '@/components/layout/AppLayout';
import { Move } from '@/lib/campaigns-types';
import { MoveCalendarView } from '@/components/moves/MoveCalendarView';
import { Check, Circle, Sparkles, Plus, Calendar, ChevronRight, Zap, Target, Clock, ArrowRight, Linkedin, Twitter, FileText } from 'lucide-react';
import { InferenceErrorBoundary } from '@/components/layout/InferenceErrorBoundary';
import { toast } from 'sonner';

type StatusFilter = 'active' | 'completed' | 'all';

interface TodayTask {
    id: string;
    label: string;
    completed: boolean;
    moveId: string;
    moveName: string;
    day: number;
    needsAsset?: boolean;
}

// Mock moves data - starts as "active" with realistic tasks
const createMockMoves = (): Move[] => [
    {
        id: 'move-1',
        name: 'Problem Post Sprint',
        description: 'Daily posts surfacing pain points → promise → CTA',
        duration: 7,
        status: 'active',
        goal: 'leads',
        channel: 'linkedin',
        dailyEffort: 30,
        startedAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
        checklist: [
            { id: 't1-1', label: 'Write post: "Pricing confusion" pain point', completed: true, group: 'create' },
            { id: 't1-2', label: 'Reply to 5 comments on yesterday\'s post', completed: true, group: 'followup' },
            { id: 't1-3', label: 'Write post: "Hiring first marketer" struggle', completed: false, group: 'create' },
            { id: 't1-4', label: 'Engage with 10 target accounts', completed: false, group: 'followup' },
            { id: 't1-5', label: 'Write post: "Tool fatigue" problem', completed: false, group: 'create' },
            { id: 't1-6', label: 'DM 3 warm leads from engagement', completed: false, group: 'followup' },
            { id: 't1-7', label: 'Write final CTA post with offer', completed: false, group: 'create' },
        ],
        assetIds: [],
        createdAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString()
    },
    {
        id: 'move-2',
        name: 'Case Study Sprint',
        description: 'Social proof daily to build trust fast',
        duration: 7,
        status: 'active',
        goal: 'proof',
        channel: 'twitter',
        dailyEffort: 30,
        startedAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
        checklist: [
            { id: 't2-1', label: 'Outline first case study (Acme Corp)', completed: true, group: 'create' },
            { id: 't2-2', label: 'Write case study thread (7 tweets)', completed: false, group: 'create' },
            { id: 't2-3', label: 'Create visual results graphic', completed: false, group: 'create' },
            { id: 't2-4', label: 'Post case study + engage replies', completed: false, group: 'publish' },
            { id: 't2-5', label: 'Outline second case study (Beta Inc)', completed: false, group: 'create' },
            { id: 't2-6', label: 'Write + post second case study', completed: false, group: 'create' },
            { id: 't2-7', label: 'Compile testimonials into carousel', completed: false, group: 'create' },
        ],
        assetIds: [],
        createdAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString()
    },
    {
        id: 'move-3',
        name: 'Authority Building',
        description: 'Position as thought leader through expert content',
        duration: 14,
        status: 'completed',
        goal: 'awareness',
        channel: 'linkedin',
        dailyEffort: 45,
        startedAt: new Date(Date.now() - 20 * 24 * 60 * 60 * 1000).toISOString(),
        checklist: [
            { id: 't3-1', label: 'Write framework post', completed: true, group: 'create' },
            { id: 't3-2', label: 'Create video explainer', completed: true, group: 'create' },
        ],
        assetIds: [],
        createdAt: new Date(Date.now() - 25 * 24 * 60 * 60 * 1000).toISOString()
    }
];

function ChannelIcon({ channel }: { channel?: string }) {
    switch (channel) {
        case 'linkedin': return <Linkedin className="w-4 h-4" />;
        case 'twitter': return <Twitter className="w-4 h-4" />;
        default: return <FileText className="w-4 h-4" />;
    }
}

export default function MovesPage() {
    const [moves, setMoves] = useState<Move[]>(createMockMoves);
    const [selectedMove, setSelectedMove] = useState<Move | null>(null);
    const [statusFilter, setStatusFilter] = useState<StatusFilter>('active');

    // Get today's tasks from all active moves
    const todayTasks: TodayTask[] = [];
    const activeMoves = moves.filter(m => m.status === 'active');

    for (const move of activeMoves) {
        if (!move.checklist) continue;

        // Calculate current day
        const startDate = move.startedAt ? new Date(move.startedAt) : new Date();
        const today = new Date();
        const dayNumber = Math.floor((today.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24)) + 1;
        const currentDay = Math.min(dayNumber, move.duration);

        // Get tasks for current day (distribute across days)
        const tasksPerDay = Math.ceil(move.checklist.length / move.duration);
        const startIdx = (currentDay - 1) * tasksPerDay;
        const endIdx = Math.min(startIdx + tasksPerDay, move.checklist.length);

        for (let i = startIdx; i < endIdx; i++) {
            const task = move.checklist[i];
            todayTasks.push({
                id: task.id,
                label: task.label,
                completed: task.completed,
                moveId: move.id,
                moveName: move.name,
                day: currentDay,
                needsAsset: task.group === 'create' // Content tasks link to Muse
            });
        }
    }

    // Handle task toggle
    const handleToggleTask = useCallback((task: TodayTask) => {
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

    // Filter moves for sidebar
    const filteredMoves = moves.filter(m => {
        if (statusFilter === 'active') return m.status === 'active';
        if (statusFilter === 'completed') return m.status === 'completed' || m.status === 'abandoned';
        return true;
    });

    const completedCount = todayTasks.filter(t => t.completed).length;
    const totalCount = todayTasks.length;
    const progressPercent = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0;

    return (
        <AppLayout fullBleed>
            <InferenceErrorBoundary>
                <div className="min-h-screen bg-[#F3F4EE]">
                    {/* Hero Header */}
                    <header className="px-8 lg:px-16 pt-12 pb-8">
                        <div className="max-w-6xl mx-auto">
                            <div className="flex items-start justify-between">
                                <div>
                                    <h1 className="font-serif text-[44px] text-[#2D3538] tracking-tight leading-none mb-2">
                                        Moves
                                    </h1>
                                    <p className="text-[15px] text-[#5B5F61] max-w-md">
                                        Your weekly execution packets. Each move is a focused sprint toward a specific goal.
                                    </p>
                                </div>
                                <button
                                    onClick={() => toast.info('New move wizard coming soon!')}
                                    className="flex items-center gap-2 px-5 py-3 bg-[#2D3538] text-white rounded-xl text-[14px] font-medium hover:bg-black transition-all hover:translate-y-[-2px] hover:shadow-lg"
                                >
                                    <Plus className="w-4 h-4" />
                                    New Move
                                </button>
                            </div>

                            {/* Today's Progress Bar */}
                            {totalCount > 0 && (
                                <div className="mt-8 p-6 bg-white rounded-2xl border border-[#C0C1BE]/50">
                                    <div className="flex items-center justify-between mb-4">
                                        <div className="flex items-center gap-3">
                                            <div className="w-10 h-10 rounded-xl bg-[#2D3538] text-white flex items-center justify-center">
                                                <Zap className="w-5 h-5" />
                                            </div>
                                            <div>
                                                <p className="text-[11px] font-semibold uppercase tracking-[0.1em] text-[#9D9F9F]">Today's Focus</p>
                                                <p className="text-[16px] font-medium text-[#2D3538]">{completedCount} of {totalCount} tasks complete</p>
                                            </div>
                                        </div>
                                        <span className="font-mono text-[28px] font-semibold text-[#2D3538]">{progressPercent}%</span>
                                    </div>
                                    <div className="h-2 bg-[#E5E6E3] rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-gradient-to-r from-[#2D3538] to-[#5B5F61] rounded-full transition-all duration-500"
                                            style={{ width: `${progressPercent}%` }}
                                        />
                                    </div>
                                </div>
                            )}
                        </div>
                    </header>

                    {/* Main Content */}
                    <main className="px-8 lg:px-16 pb-16">
                        <div className="max-w-6xl mx-auto">
                            {/* Tabs */}
                            <div className="flex items-center gap-8 mb-8 border-b border-[#C0C1BE]/30">
                                {(['active', 'completed', 'all'] as StatusFilter[]).map((tab) => (
                                    <button
                                        key={tab}
                                        onClick={() => setStatusFilter(tab)}
                                        className={`pb-4 text-[13px] font-medium transition-colors border-b-2 -mb-[1px] capitalize ${statusFilter === tab
                                            ? 'text-[#2D3538] border-[#2D3538]'
                                            : 'text-[#9D9F9F] border-transparent hover:text-[#5B5F61]'
                                            }`}
                                    >
                                        {tab === 'active' && `Active (${moves.filter(m => m.status === 'active').length})`}
                                        {tab === 'completed' && `Completed (${moves.filter(m => m.status === 'completed').length})`}
                                        {tab === 'all' && `All (${moves.length})`}
                                    </button>
                                ))}
                            </div>

                            {/* Moves Grid */}
                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                {filteredMoves.map((move) => {
                                    const completed = move.checklist?.filter(t => t.completed).length || 0;
                                    const total = move.checklist?.length || 0;
                                    const progress = total > 0 ? Math.round((completed / total) * 100) : 0;

                                    // Calculate current day
                                    const startDate = move.startedAt ? new Date(move.startedAt) : new Date();
                                    const today = new Date();
                                    const dayNumber = Math.floor((today.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24)) + 1;
                                    const currentDay = Math.min(dayNumber, move.duration);

                                    return (
                                        <div
                                            key={move.id}
                                            onClick={() => setSelectedMove(move)}
                                            className="group relative bg-white rounded-2xl border border-[#C0C1BE]/50 p-6 cursor-pointer transition-all duration-300 hover:border-[#2D3538]/30 hover:shadow-xl hover:shadow-black/5 hover:translate-y-[-4px]"
                                        >
                                            {/* Status Badge */}
                                            <div className="absolute top-6 right-6">
                                                <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-semibold uppercase tracking-wider ${move.status === 'active'
                                                        ? 'bg-[#22C55E]/10 text-[#16A34A]'
                                                        : 'bg-[#9D9F9F]/10 text-[#5B5F61]'
                                                    }`}>
                                                    <span className={`w-1.5 h-1.5 rounded-full ${move.status === 'active' ? 'bg-[#22C55E]' : 'bg-[#9D9F9F]'}`} />
                                                    {move.status}
                                                </span>
                                            </div>

                                            {/* Header */}
                                            <div className="flex items-start gap-4 mb-4">
                                                <div className="w-12 h-12 rounded-xl bg-[#F3F4EE] border border-[#C0C1BE]/30 flex items-center justify-center text-[#2D3538]">
                                                    <ChannelIcon channel={move.channel} />
                                                </div>
                                                <div className="flex-1 min-w-0 pr-20">
                                                    <h3 className="text-[18px] font-semibold text-[#2D3538] mb-1 truncate group-hover:text-black transition-colors">
                                                        {move.name}
                                                    </h3>
                                                    <p className="text-[13px] text-[#5B5F61] line-clamp-2">
                                                        {move.description}
                                                    </p>
                                                </div>
                                            </div>

                                            {/* Meta Row */}
                                            <div className="flex items-center gap-4 mb-5 text-[12px]">
                                                <div className="flex items-center gap-1.5 text-[#5B5F61]">
                                                    <Calendar className="w-3.5 h-3.5" />
                                                    <span>Day {currentDay} of {move.duration}</span>
                                                </div>
                                                <div className="flex items-center gap-1.5 text-[#5B5F61]">
                                                    <Clock className="w-3.5 h-3.5" />
                                                    <span>{move.dailyEffort}min/day</span>
                                                </div>
                                                <div className="flex items-center gap-1.5 text-[#5B5F61]">
                                                    <Target className="w-3.5 h-3.5" />
                                                    <span className="capitalize">{move.goal}</span>
                                                </div>
                                            </div>

                                            {/* Progress */}
                                            <div className="mb-4">
                                                <div className="flex items-center justify-between mb-2">
                                                    <span className="text-[11px] font-medium text-[#9D9F9F]">Progress</span>
                                                    <span className="font-mono text-[12px] font-semibold text-[#2D3538]">{progress}%</span>
                                                </div>
                                                <div className="h-1.5 bg-[#E5E6E3] rounded-full overflow-hidden">
                                                    <div
                                                        className={`h-full rounded-full transition-all duration-500 ${move.status === 'completed'
                                                                ? 'bg-[#22C55E]'
                                                                : 'bg-[#2D3538]'
                                                            }`}
                                                        style={{ width: `${progress}%` }}
                                                    />
                                                </div>
                                            </div>

                                            {/* Tasks Preview */}
                                            <div className="flex items-center justify-between pt-4 border-t border-[#E5E6E3]">
                                                <span className="text-[12px] text-[#9D9F9F]">
                                                    {completed}/{total} tasks complete
                                                </span>
                                                <div className="flex items-center gap-2 text-[12px] font-medium text-[#2D3538] opacity-0 group-hover:opacity-100 transition-opacity">
                                                    <span>View details</span>
                                                    <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
                                                </div>
                                            </div>
                                        </div>
                                    );
                                })}

                                {filteredMoves.length === 0 && (
                                    <div className="col-span-2 text-center py-24">
                                        <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-[#F3F4EE] border border-[#C0C1BE]/30 flex items-center justify-center">
                                            <Circle className="w-8 h-8 text-[#C0C1BE]" />
                                        </div>
                                        <h3 className="font-serif text-[24px] text-[#2D3538] mb-2">No moves yet</h3>
                                        <p className="text-[14px] text-[#5B5F61] mb-6 max-w-sm mx-auto">
                                            Create your first move to start executing on your marketing strategy.
                                        </p>
                                        <button
                                            onClick={() => toast.info('New move wizard coming soon!')}
                                            className="inline-flex items-center gap-2 px-5 py-3 bg-[#2D3538] text-white rounded-xl text-[14px] font-medium hover:bg-black transition-colors"
                                        >
                                            <Plus className="w-4 h-4" />
                                            Create First Move
                                        </button>
                                    </div>
                                )}
                            </div>

                            {/* Today's Tasks Section */}
                            {todayTasks.length > 0 && (
                                <section className="mt-12">
                                    <div className="flex items-center gap-3 mb-6">
                                        <h2 className="font-serif text-[28px] text-[#2D3538]">Today's Tasks</h2>
                                        <span className="font-mono text-[12px] text-[#9D9F9F] px-2 py-1 bg-[#E5E6E3] rounded-md">
                                            {completedCount}/{totalCount}
                                        </span>
                                    </div>

                                    <div className="space-y-3">
                                        {todayTasks.map((task) => (
                                            <div
                                                key={`${task.moveId}-${task.id}`}
                                                className={`flex items-center gap-4 p-5 rounded-xl transition-all ${task.completed
                                                    ? 'bg-[#F0FDF4] border border-[#22C55E]/20'
                                                    : 'bg-white border border-[#C0C1BE]/50 hover:border-[#2D3538]/30'
                                                    }`}
                                            >
                                                {/* Checkbox */}
                                                <button
                                                    onClick={() => handleToggleTask(task)}
                                                    className={`w-7 h-7 rounded-full border-2 flex items-center justify-center transition-all shrink-0 ${task.completed
                                                        ? 'bg-[#22C55E] border-[#22C55E] text-white'
                                                        : 'border-[#C0C1BE] hover:border-[#2D3538]'
                                                        }`}
                                                >
                                                    {task.completed && <Check className="w-4 h-4" />}
                                                </button>

                                                {/* Task Content */}
                                                <div className="flex-1 min-w-0">
                                                    <span className={`text-[15px] ${task.completed ? 'text-[#5B5F61] line-through' : 'text-[#2D3538]'}`}>
                                                        {task.label}
                                                    </span>
                                                </div>

                                                {/* Create in Muse Link */}
                                                {task.needsAsset && !task.completed && (
                                                    <Link
                                                        href="/muse"
                                                        className="inline-flex items-center gap-1.5 px-4 py-2 bg-[#2D3538] text-white rounded-lg text-[12px] font-medium hover:bg-black transition-colors shrink-0"
                                                    >
                                                        <Sparkles className="w-3.5 h-3.5" />
                                                        Create in Muse
                                                    </Link>
                                                )}

                                                {/* Move Tag */}
                                                <span className="text-[11px] text-[#9D9F9F] px-3 py-1.5 bg-[#F3F4EE] rounded-lg shrink-0 border border-[#E5E6E3]">
                                                    {task.moveName}
                                                </span>
                                            </div>
                                        ))}
                                    </div>
                                </section>
                            )}
                        </div>
                    </main>
                </div>

                {/* Calendar View Modal */}
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
