'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { AppLayout } from '@/components/layout/AppLayout';
import { Move } from '@/lib/campaigns-types';
import { MoveCard } from '@/components/moves/MoveCard';
import { NewMoveWizard } from '@/components/moves/NewMoveWizard';
import { MoveDetail } from '@/components/moves/MoveDetail';
import { Button } from '@/components/ui/button';
import { Plus, Zap, Check, ArrowRight, Clock, Target } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useCampaigns } from '@/hooks/useCampaigns';
import { InferenceErrorBoundary } from '@/components/layout/InferenceErrorBoundary';

export default function MovesPage() {
    const { moves, refresh: refreshMoves } = useCampaigns(10000);
    const [showWizard, setShowWizard] = useState(false);
    const [selectedMove, setSelectedMove] = useState<Move | null>(null);

    // Derived active move
    const activeMove = moves.find(m => m.status === 'active') || null;

    const handleMoveCreated = useCallback(() => {
        refreshMoves();
        setShowWizard(false);
    }, [refreshMoves]);

    const handleMoveUpdated = useCallback(() => {
        refreshMoves();
    }, [refreshMoves]);

    const handleMoveDeleted = useCallback(() => {
        refreshMoves();
        setSelectedMove(null);
    }, [refreshMoves]);

    const handleOpenMove = (move: Move) => {
        setSelectedMove(move);
    };

    const queuedMoves = moves.filter(m => m.status === 'queued');
    const completedMoves = moves.filter(m => m.status === 'completed' || m.status === 'abandoned');

    const [greeting, setGreeting] = useState('Welcome back');
    const [currentDate, setCurrentDate] = useState('');
    const [displayedActiveCount, setDisplayedActiveCount] = useState(0);
    const [statusText, setStatusText] = useState('Live');
    const [timeTint, setTimeTint] = useState('bg-white dark:bg-black');

    useEffect(() => {
        const hour = new Date().getHours();
        const newGreeting = hour < 12 ? 'Good morning' : hour < 18 ? 'Good afternoon' : 'Good evening';
        setGreeting(newGreeting);

        let newTint = 'bg-white dark:bg-zinc-950';
        if (hour < 10) newTint = 'bg-orange-50/30 dark:bg-orange-950/10';
        else if (hour > 18) newTint = 'bg-blue-50/30 dark:bg-blue-950/10';
        setTimeTint(newTint);

        setCurrentDate(new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', weekday: 'long' }));

        const activeCount = moves.filter(m => m.status === 'active').length;
        document.title = `(${activeCount}) Moves | RaptorFlow`;

        const statusInterval = setInterval(() => {
            const states = ['Live', 'Syncing...', 'Encrypted', 'Live'];
            const randomState = states[Math.floor(Math.random() * states.length)];
            setStatusText(randomState);
        }, 5000);

        const target = activeCount;
        let start = 0;
        const duration = 1000;
        const increment = target / (duration / 16);

        const timer = setInterval(() => {
            start += increment;
            if (start >= target) {
                setDisplayedActiveCount(target);
                clearInterval(timer);
            } else {
                setDisplayedActiveCount(Math.floor(start));
            }
        }, 16);

        return () => {
            clearInterval(timer);
            clearInterval(statusInterval);
        };
    }, [moves]);

    const activeStats = activeMove ? {
        total: activeMove.checklist.length,
        completed: activeMove.checklist.filter(i => i.completed).length,
        percent: activeMove.checklist.length > 0
            ? Math.round((activeMove.checklist.filter(i => i.completed).length / activeMove.checklist.length) * 100)
            : 0
    } : null;

    return (
        <AppLayout>
            <InferenceErrorBoundary>
                <div className={cn("min-h-screen transition-colors [transition-duration:2000ms] selection:bg-emerald-500/30 selection:text-emerald-900 dark:selection:bg-emerald-500/30 dark:selection:text-emerald-100", timeTint)}>
                    <div className="fixed top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[600px] bg-emerald-500/10 dark:bg-emerald-500/5 blur-[120px] rounded-full mix-blend-multiply dark:mix-blend-screen pointer-events-none animate-pulse [animation-duration:10000ms]" />
                    <div className="fixed inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-[0.015] pointer-events-none" />

                    <div className="max-w-[1400px] mx-auto px-6 md:px-12 py-8 md:py-12 pb-32 animate-in fade-in duration-500 relative z-10">
                        <div className="sticky top-0 z-20 flex items-end justify-between mb-16 pb-8 border-b border-zinc-100 dark:border-zinc-800 bg-white/80 dark:bg-black/80 backdrop-blur-md -mx-6 px-6 md:-mx-12 md:px-12 pt-8 transition-all duration-500 hover:backdrop-blur-xl">
                            <div>
                                <div className="flex items-center gap-3 mb-5">
                                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)] animate-pulse" />
                                    <div className="text-[11px] font-bold uppercase tracking-[0.25em] text-zinc-400 dark:text-zinc-500 font-mono">
                                        {currentDate}
                                    </div>
                                </div>
                                <h1 className="text-5xl md:text-6xl font-display font-normal text-zinc-900 dark:text-zinc-50 tracking-tight animate-in fade-in slide-in-from-left-4 duration-700">
                                    {greeting}, Founder
                                </h1>
                            </div>
                            <div className="flex items-center gap-6">
                                <div className="hidden md:block text-right mr-4 group cursor-default">
                                    <div className="text-[11px] font-bold uppercase tracking-[0.15em] text-zinc-400 dark:text-zinc-600 mb-0.5 group-hover:text-zinc-600 dark:group-hover:text-zinc-400 transition-colors">
                                        Current Objectives
                                    </div>
                                    <div className="text-sm font-medium text-zinc-900 dark:text-zinc-300 tabular-nums">
                                        <span className="text-lg">{displayedActiveCount}</span> Active • <span className="text-lg">{moves.filter(m => m.status === 'queued').length}</span> Queued
                                    </div>
                                </div>
                                <Button
                                    onClick={() => setShowWizard(true)}
                                    className="rounded-full bg-gradient-to-b from-zinc-800 to-zinc-950 text-white hover:from-zinc-700 hover:to-zinc-900 dark:from-zinc-100 dark:to-zinc-300 dark:text-zinc-900 dark:hover:from-white dark:hover:to-zinc-200 h-14 pl-6 pr-8 text-[15px] font-medium shadow-2xl shadow-zinc-900/20 dark:shadow-zinc-100/10 hover:-translate-y-0.5 transition-all duration-300 group active:scale-95 border border-zinc-800 dark:border-zinc-200 relative overflow-hidden"
                                >
                                    <div className="absolute inset-0 -translate-x-full group-hover:animate-[shimmer_1.5s_infinite] bg-gradient-to-r from-transparent via-white/10 to-transparent z-10" />
                                    <span className="w-8 h-8 rounded-full bg-zinc-700/50 dark:bg-zinc-900/10 flex items-center justify-center mr-3 group-hover:scale-110 transition-transform duration-500 relative z-20">
                                        <Plus className="w-4 h-4 text-white dark:text-zinc-900 stroke-[1.5]" />
                                    </span>
                                    <span className="relative z-20">Create Battle Plan</span>
                                </Button>
                            </div>
                        </div>

                        <div className="flex flex-col lg:flex-row gap-12 lg:gap-16 items-start">
                            <div className="lg:w-[65%] min-w-0">
                                <section aria-label="Active Move">
                                    {activeMove ? (
                                        <div className="space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-1000 fill-mode-backwards">
                                            <div className="relative group/active">
                                                <div className="absolute -left-6 -top-6 w-8 h-8 border-l-2 border-t-2 border-zinc-200 dark:border-zinc-800 opacity-0 group-hover/active:opacity-100 transition-opacity duration-500 rounded-tl-lg" />
                                                <div className="absolute -right-6 -top-6 w-8 h-8 border-r-2 border-t-2 border-zinc-200 dark:border-zinc-800 opacity-0 group-hover/active:opacity-100 transition-opacity duration-500 rounded-tr-lg" />

                                                <div className="flex items-center gap-3 mb-8 group cursor-default">
                                                    <span className="relative flex h-3 w-3">
                                                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-20"></span>
                                                        <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
                                                    </span>
                                                    <span className="text-[11px] font-bold uppercase tracking-widest text-emerald-600 dark:text-emerald-400">
                                                        Active Deployment
                                                    </span>
                                                </div>

                                                <h2 className="relative text-6xl md:text-[5rem] font-display font-normal text-zinc-900 dark:text-zinc-50 mb-8 leading-[0.95] tracking-tight text-balance animate-in fade-in blur-in duration-1000">
                                                    {activeMove.name}
                                                </h2>

                                                <div className="flex items-center gap-10 text-zinc-500 dark:text-zinc-400">
                                                    <div className="flex items-center gap-3">
                                                        <div className="w-9 h-9 rounded-full bg-zinc-50 dark:bg-zinc-800/50 flex items-center justify-center border border-zinc-100 dark:border-zinc-800">
                                                            <Clock className="w-4 h-4" />
                                                        </div>
                                                        <div>
                                                            <span className="block text-[10px] font-bold uppercase tracking-widest text-zinc-400 mb-0.5">Timeline</span>
                                                            <span className="font-mono text-sm font-medium text-zinc-900 dark:text-zinc-200">
                                                                Day 01 / {activeMove.duration}
                                                            </span>
                                                        </div>
                                                    </div>

                                                    <div className="flex items-center gap-3">
                                                        <div className="w-9 h-9 rounded-full bg-zinc-50 dark:bg-zinc-800/50 flex items-center justify-center border border-zinc-100 dark:border-zinc-800">
                                                            <Target className="w-4 h-4" />
                                                        </div>
                                                        <div>
                                                            <span className="block text-[10px] font-bold uppercase tracking-widest text-zinc-400 mb-0.5">Progress</span>
                                                            <span className="font-mono text-sm font-medium text-zinc-900 dark:text-zinc-200">
                                                                {activeStats?.percent}%
                                                            </span>
                                                        </div>
                                                    </div>

                                                    <Button
                                                        variant="ghost"
                                                        onClick={() => handleOpenMove(activeMove)}
                                                        className="text-emerald-700 hover:text-emerald-800 bg-emerald-50/50 hover:bg-emerald-50 dark:text-emerald-400 dark:hover:bg-emerald-900/10 px-5 rounded-full"
                                                    >
                                                        Open War Room
                                                        <ArrowRight className="w-3.5 h-3.5 ml-2" />
                                                    </Button>
                                                </div>
                                            </div>

                                            <div className="bg-white dark:bg-zinc-900 rounded-[2rem] p-8 border border-zinc-100 dark:border-zinc-800">
                                                <div className="space-y-4">
                                                    {activeMove.checklist.map((item) => (
                                                        <div key={item.id} className="flex items-start gap-5 p-4 rounded-xl hover:bg-zinc-50 dark:hover:bg-zinc-800/30 transition-colors">
                                                            <div className={cn(
                                                                "mt-0.5 w-6 h-6 rounded flex items-center justify-center border transition-all",
                                                                item.completed ? "bg-emerald-500 border-emerald-500 text-white" : "bg-white dark:bg-zinc-800 border-zinc-200 dark:border-zinc-700"
                                                            )}>
                                                                {item.completed && <Check className="w-3.5 h-3.5 stroke-[3]" />}
                                                            </div>
                                                            <span className={cn("text-lg font-medium", item.completed && "text-zinc-400 line-through")}>
                                                                {item.label}
                                                            </span>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        </div>
                                    ) : (
                                        <div className="bg-zinc-50 dark:bg-zinc-900/50 border border-dashed border-zinc-200 dark:border-zinc-800 rounded-[2rem] p-20 text-center h-full flex flex-col justify-center items-center">
                                            <h3 className="text-4xl font-display italic mb-6">No Active Move</h3>
                                            <Button onClick={() => setShowWizard(true)} variant="outline" className="h-14 px-8 rounded-full">
                                                <Zap className="w-4 h-4 mr-2" />
                                                Initialize First Move
                                            </Button>
                                        </div>
                                    )}
                                </section>
                            </div>

                            <div className="lg:w-[35%] flex flex-col gap-8">
                                <div className="space-y-4">
                                    <h3 className="text-[11px] font-bold uppercase tracking-[0.25em] text-zinc-400 border-b pb-4">Up Next</h3>
                                    {queuedMoves.map(move => (
                                        <MoveCard key={move.id} move={move} variant="row" onClick={() => handleOpenMove(move)} />
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <NewMoveWizard
                    open={showWizard}
                    onOpenChange={setShowWizard}
                    onComplete={handleMoveCreated}
                />

                <MoveDetail
                    move={selectedMove}
                    open={!!selectedMove}
                    onOpenChange={(open) => !open && setSelectedMove(null)}
                    onUpdate={handleMoveUpdated}
                    onDelete={handleMoveDeleted}
                />
            </InferenceErrorBoundary>
        </AppLayout>
    );
}
