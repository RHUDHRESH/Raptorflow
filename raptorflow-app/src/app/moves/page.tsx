'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { AppLayout } from '@/components/layout/AppLayout';
import { Move } from '@/lib/campaigns-types';
import { getMoves, getActiveMove, setActiveMove } from '@/lib/campaigns';
import { MoveCard } from '@/components/moves/MoveCard';
import { NewMoveWizard } from '@/components/moves/NewMoveWizard';
import { MoveDetail } from '@/components/moves/MoveDetail';
import { Button } from '@/components/ui/button';
import { Plus, Zap, Check, ArrowRight, Clock, Target } from 'lucide-react';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';

export default function MovesPage() {
    const [moves, setMoves] = useState<Move[]>([]);
    const [activeMove, setActiveMoveState] = useState<Move | null>(null);
    const [showWizard, setShowWizard] = useState(false);
    const [selectedMove, setSelectedMove] = useState<Move | null>(null);
    const [filter, setFilter] = useState<'all' | 'queued' | 'completed'>('all');

    const refreshMoves = useCallback(() => {
        const allMoves = getMoves();
        setMoves(allMoves);
        setActiveMoveState(getActiveMove());
    }, []);

    useEffect(() => {
        refreshMoves();
        const interval = setInterval(refreshMoves, 5000);
        return () => clearInterval(interval);
    }, [refreshMoves]);

    const handleMoveCreated = useCallback((newMoves: Move[]) => {
        refreshMoves();
        setShowWizard(false);
        // If the first new move is active, open it
        const newActive = newMoves.find(m => m.status === 'active');
        if (newActive) {
            setSelectedMove(newActive);
        }
    }, [refreshMoves]);

    const handleMoveUpdated = useCallback((move: Move) => {
        refreshMoves();
    }, [refreshMoves]);

    const handleMoveDeleted = useCallback((moveId: string) => {
        refreshMoves();
        setSelectedMove(null);
    }, [refreshMoves]);

    const handleOpenMove = (move: Move) => {
        setSelectedMove(move);
    };

    const queuedMoves = moves.filter(m => m.status === 'queued');
    const completedMoves = moves.filter(m => m.status === 'completed' || m.status === 'abandoned');

    // Batch 4 & 5: Intelligence, Counters, Atmosphere
    const [greeting, setGreeting] = useState('Welcome back');
    const [currentDate, setCurrentDate] = useState('');
    const [displayedActiveCount, setDisplayedActiveCount] = useState(0);
    const [statusText, setStatusText] = useState('Live'); // Batch 5: Status Cycler
    const [timeTint, setTimeTint] = useState('bg-white dark:bg-black'); // Batch 5: Time-Tint

    useEffect(() => {
        // Smart Greeting & Time-Tint
        const hour = new Date().getHours();
        setGreeting(hour < 12 ? 'Good morning' : hour < 18 ? 'Good afternoon' : 'Good evening');

        // Batch 5: Time-Aware Tint
        if (hour < 10) setTimeTint('bg-orange-50/30 dark:bg-orange-950/10'); // Morning Warmth
        else if (hour > 18) setTimeTint('bg-blue-50/30 dark:bg-blue-950/10'); // Evening Cool
        else setTimeTint('bg-white dark:bg-zinc-950'); // Day Neutral

        // Live Date
        setCurrentDate(new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', weekday: 'long' }));

        // Batch 5: Console Art
        console.log(
            '%c RAPTORFLOW %c MOVES v2.4 ',
            'background: #10b981; color: white; font-weight: bold; padding: 4px;',
            'background: #333; color: white; padding: 4px;'
        );

        // Batch 5: Document Title Sync
        document.title = `(${moves.filter(m => m.status === 'active').length}) Moves | RaptorFlow`;

        // Batch 5: Status Cycler
        const statusInterval = setInterval(() => {
            const states = ['Live', 'Syncing...', 'Encrypted', 'Live'];
            const randomState = states[Math.floor(Math.random() * states.length)];
            setStatusText(randomState);
        }, 5000);

        // CountUp Animation
        const target = moves.filter(m => m.status === 'active').length;
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
            {/* Batch 5: Aurora Background & Time-Tint */}
            <div className={cn("min-h-screen transition-colors duration-[2000ms] selection:bg-emerald-500/30 selection:text-emerald-900 dark:selection:bg-emerald-500/30 dark:selection:text-emerald-100", timeTint)}>
                {/* Batch 5: Fixed Aurora Blob */}
                <div className="fixed top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[600px] bg-emerald-500/10 dark:bg-emerald-500/5 blur-[120px] rounded-full mix-blend-multiply dark:mix-blend-screen pointer-events-none animate-pulse duration-[10000ms]" />

                {/* Batch 5: Grid Reveal */}
                <div className="fixed inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-[0.015] pointer-events-none" />

                <div className="max-w-[1400px] mx-auto px-6 md:px-12 py-8 md:py-12 pb-32 animate-in fade-in duration-500 relative z-10">

                    {/* Header - Stays top - Batch 5: Header Breath */}
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
                                {/* Batch 5: Shimmer Effect */}
                                <div className="absolute inset-0 -translate-x-full group-hover:animate-[shimmer_1.5s_infinite] bg-gradient-to-r from-transparent via-white/10 to-transparent z-10" />

                                <span className="w-8 h-8 rounded-full bg-zinc-700/50 dark:bg-zinc-900/10 flex items-center justify-center mr-3 group-hover:scale-110 transition-transform duration-500 relative z-20">
                                    <Plus className="w-4 h-4 text-white dark:text-zinc-900 stroke-[1.5]" />
                                </span>
                                <span className="relative z-20">Create Battle Plan</span>
                                {/* Keyboard Hint [C] */}
                                <span className="absolute right-3 top-1/2 -translate-y-1/2 text-[9px] font-bold opacity-0 group-hover:opacity-30 transition-opacity bg-white/20 px-1 rounded z-20">C</span>
                            </Button>
                        </div>
                    </div>

                    {/* Main Split Layout */}
                    <div className="flex flex-col lg:flex-row gap-12 lg:gap-16 items-start">

                        {/* LEFT COLUMN: Active Execution (65%) */}
                        <div className="lg:w-[65%] min-w-0">
                            <section aria-label="Active Move">
                                {activeMove ? (
                                    <div className="space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-1000 fill-mode-backwards">
                                        {/* Active Header */}
                                        <div className="relative group/active">
                                            {/* Batch 4: HUD visuals (Corner Brackets) */}
                                            <div className="absolute -left-6 -top-6 w-8 h-8 border-l-2 border-t-2 border-zinc-200 dark:border-zinc-800 opacity-0 group-hover/active:opacity-100 transition-opacity duration-500 rounded-tl-lg" />
                                            <div className="absolute -right-6 -top-6 w-8 h-8 border-r-2 border-t-2 border-zinc-200 dark:border-zinc-800 opacity-0 group-hover/active:opacity-100 transition-opacity duration-500 rounded-tr-lg" />

                                            <div className="flex items-center gap-3 mb-8 group cursor-default">
                                                <span className="relative flex h-3 w-3">
                                                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-20 duration-3000 delay-300"></span>
                                                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-40 duration-1000"></span>
                                                    {/* Batch 4: 3rd massive pulse */}
                                                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-10 duration-[4000ms] scale-150"></span>
                                                    <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500 border border-white dark:border-zinc-900 overflow-hidden">
                                                        {/* Glossy Reflection (Tidbit #18) */}
                                                        <span className="absolute top-0.5 right-0.5 w-1 h-1 bg-white/40 rounded-full"></span>
                                                    </span>
                                                </span>
                                                <span className="text-[11px] font-bold uppercase tracking-widest text-emerald-600 dark:text-emerald-400 shadow-emerald-500/20 drop-shadow-sm group-hover:text-emerald-500 transition-colors duration-300">
                                                    Active Deployment
                                                </span>
                                            </div>

                                            {/* Batch 4: Text Unblur & Scanline */}
                                            <h2 className="relative text-6xl md:text-[5rem] font-display font-normal text-zinc-900 dark:text-zinc-50 mb-8 leading-[0.95] tracking-tight selection:bg-emerald-100 selection:text-emerald-900 text-balance animate-in fade-in blur-in duration-1000">
                                                {activeMove.name}
                                                {/* Subtle Scanline Overlay on Text */}
                                                <span className="absolute inset-0 bg-gradient-to-b from-transparent via-white/10 to-transparent pointer-events-none opacity-0 group-hover/active:opacity-20 animate-pulse bg-[length:100%_4px]" />
                                            </h2>

                                            <div className="flex items-center gap-10 text-zinc-500 dark:text-zinc-400">
                                                <div className="flex items-center gap-3 group cursor-help" title="Oct 24 - Nov 7">
                                                    <div className="w-9 h-9 rounded-full bg-zinc-50 dark:bg-zinc-800/50 flex items-center justify-center border border-zinc-100 dark:border-zinc-800 group-hover:scale-110 transition-transform duration-500">
                                                        <Clock className="w-4 h-4 text-zinc-400 dark:text-zinc-500 stroke-[1.5]" />
                                                    </div>
                                                    <div>
                                                        <span className="block text-[10px] font-bold uppercase tracking-widest text-zinc-400 mb-0.5">Timeline</span>
                                                        <span className="font-mono text-sm font-medium text-zinc-900 dark:text-zinc-200 tabular-nums">
                                                            Day 01 <span className="text-zinc-400 font-normal">/ {activeMove.duration}</span>
                                                        </span>
                                                    </div>
                                                </div>

                                                {/* Tapered Divider (Tidbit #2) */}
                                                <div className="w-px h-10 bg-gradient-to-b from-transparent via-zinc-200 to-transparent dark:via-zinc-800 opacity-80" />

                                                <div className="flex items-center gap-3 group cursor-default">
                                                    <div className="w-9 h-9 rounded-full bg-zinc-50 dark:bg-zinc-800/50 flex items-center justify-center border border-zinc-100 dark:border-zinc-800 group-hover:scale-110 transition-transform duration-500">
                                                        <Target className="w-4 h-4 text-zinc-400 dark:text-zinc-500 stroke-[1.5]" />
                                                    </div>
                                                    <div>
                                                        <span className="block text-[10px] font-bold uppercase tracking-widest text-zinc-400 mb-0.5">Progress</span>
                                                        <span className="font-mono text-sm font-medium text-zinc-900 dark:text-zinc-200 tabular-nums">
                                                            {activeStats?.percent === 100 ? "DONE" : `${String(activeStats?.completed).padStart(2, '0')}/${String(activeStats?.total).padStart(2, '0')}`} <span className="text-zinc-400 font-normal">Tasks</span>
                                                        </span>
                                                    </div>
                                                </div>

                                                <div className="w-px h-10 bg-gradient-to-b from-transparent via-zinc-200 to-transparent dark:via-zinc-800 opacity-80" />

                                                <Button
                                                    variant="ghost"
                                                    onClick={() => handleOpenMove(activeMove)}
                                                    className="relative overflow-hidden text-emerald-700 hover:text-emerald-800 bg-emerald-50/50 hover:bg-emerald-50 dark:text-emerald-400 dark:hover:bg-emerald-900/10 px-5 py-2.5 h-auto font-medium text-sm rounded-full transition-all duration-300 group active:scale-95 cursor-alias"
                                                >
                                                    <span className="relative z-10 flex items-center group-hover:underline decoration-emerald-300/50 underline-offset-4 decoration-2">
                                                        Open War Room
                                                        <ArrowRight className="w-3.5 h-3.5 ml-2 group-hover:translate-x-1 group-hover:opacity-100 opacity-70 transition-all duration-300" />
                                                    </span>
                                                </Button>
                                            </div>
                                        </div>

                                        {/* The "Todo List" - Prominent Checklist */}
                                        <div className="relative bg-white dark:bg-zinc-900 rounded-[2rem] p-8 md:p-12 shadow-[0_8px_40px_-12px_rgba(0,0,0,0.05)] dark:shadow-none border border-zinc-100/50 dark:border-zinc-800/50 group/card hover:shadow-[0_20px_60px_-12px_rgba(0,0,0,0.08)] transition-all duration-[800ms] ring-1 ring-zinc-900/5 dark:ring-zinc-100/5 overflow-hidden">
                                            {/* Batch 5: Active Card Heartbeat Shadow */}
                                            <div className="absolute inset-0 bg-transparent shadow-[0_0_0_0_rgba(16,185,129,0)] group-hover/card:animate-[pulse-shadow_3s_infinite] rounded-[2rem] pointer-events-none" />

                                            {/* Batch 4: Grain Texture */}
                                            <div className="absolute inset-0 opacity-[0.03] pointer-events-none mix-blend-overlay" style={{ backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")` }}></div>

                                            {/* Double border effect */}
                                            <div className="absolute inset-0 rounded-[2rem] border border-zinc-900/5 dark:border-zinc-100/5 pointer-events-none" />

                                            {/* Batch 5: Corner Folds (Top-Right Dog Ear - subtle) */}
                                            <div className="absolute top-0 right-0 w-16 h-16 bg-gradient-to-bl from-zinc-50 to-transparent dark:from-zinc-800/50 opacity-50 rounded-bl-[2rem] pointer-events-none" />

                                            <div className="flex items-center justify-between mb-10 pb-6 border-b border-dashed border-zinc-100 dark:border-zinc-800/50">
                                                <h3 className="text-[10px] font-bold uppercase tracking-widest text-zinc-400 dark:text-zinc-500 pl-1">
                                                    Highest Priority Actions
                                                </h3>
                                                <div className="flex items-center gap-2">
                                                    <span className="relative flex h-2 w-2">
                                                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                                                        <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                                                    </span>
                                                    {/* Batch 5: Liquid Progress / Number Flip */}
                                                    <span className="text-[10px] font-bold text-emerald-700 dark:text-emerald-400 tabular-nums animate-[slide-up_0.5s_ease-out]">
                                                        {activeStats?.percent}% COMPLETE
                                                    </span>
                                                </div>
                                            </div>
                                            <div className="space-y-4 group/list">
                                                {activeMove.checklist.map((item, index) => (
                                                    <div
                                                        key={item.id}
                                                        className={cn(
                                                            "flex items-start gap-5 p-4 rounded-xl -mx-4 transition-all duration-500 group/item",
                                                            "hover:bg-zinc-50 dark:hover:bg-zinc-800/30",
                                                            "group-hover/list:opacity-50 hover:!opacity-100", // Spotlight effect (Tidbit #5)
                                                            item.completed && "opacity-60 grayscale hover:grayscale-0 hover:opacity-100"
                                                        )}
                                                    >
                                                        <div className={cn(
                                                            "mt-0.5 w-6 h-6 rounded-[0.4rem] flex items-center justify-center border transition-all duration-300 shrink-0 shadow-sm",
                                                            item.completed
                                                                ? "bg-emerald-500 border-emerald-500 text-white scale-95"
                                                                : "bg-white dark:bg-zinc-800 border-zinc-200 dark:border-zinc-700 hover:border-emerald-400 hover:shadow-emerald-100 dark:hover:shadow-none"
                                                        )}>
                                                            {item.completed && (
                                                                <Check className="w-3.5 h-3.5 stroke-[3] animate-in zoom-in spin-in-12 duration-300" />
                                                            )}
                                                        </div>
                                                        <div className="space-y-1.5 pt-0.5">
                                                            <span className={cn(
                                                                "text-lg block transition-colors leading-relaxed font-medium tracking-tight",
                                                                item.completed
                                                                    ? "text-zinc-400 dark:text-zinc-500 line-through decoration-zinc-300/50 dark:decoration-zinc-700 decoration-2"
                                                                    : "text-zinc-900 dark:text-zinc-100 selection:bg-emerald-100 selection:text-emerald-900"
                                                            )}>
                                                                {item.label}
                                                            </span>
                                                        </div>
                                                    </div>
                                                ))}

                                                {activeMove.checklist.length === 0 && (
                                                    <p className="text-zinc-400 italic font-serif text-lg text-center py-8">No tasks defined for this move.</p>
                                                )}
                                            </div>

                                            {/* Footer Status Line */}
                                            <div className="mt-8 pt-6 border-t border-zinc-50 dark:border-zinc-800/50 text-center flex items-center justify-center gap-3">
                                                <div className="h-px w-8 bg-gradient-to-r from-transparent to-zinc-200 dark:to-zinc-800" />
                                                {/* Batch 4 & 5: Beacon and Status Cycle */}
                                                <div className="flex items-center gap-2 group cursor-help" title="System Normal">
                                                    <span className="relative flex h-1.5 w-1.5">
                                                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                                                        <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-emerald-500"></span>
                                                    </span>
                                                    <p className="text-[10px] uppercase tracking-widest text-zinc-300 dark:text-zinc-600 font-medium font-mono min-w-[60px] text-left transition-all duration-500">
                                                        {statusText}
                                                    </p>
                                                </div>
                                                <span className="text-[10px] text-zinc-200 dark:text-zinc-800">•</span>
                                                {/* Batch 5: 100 Easter Egg & Version */}
                                                <div className="flex items-center gap-1 group">
                                                    <p className="text-[10px] uppercase tracking-widest text-zinc-300 dark:text-zinc-600 font-medium font-mono">
                                                        v2.4
                                                    </p>
                                                    <span className="w-0.5 h-0.5 bg-yellow-500/50 rounded-full opacity-0 group-hover:opacity-100 transition-opacity" title="100/100 Polish Score"></span>
                                                    <span className="text-[8px] text-zinc-200 dark:text-zinc-800 ml-2 font-mono tabular-nums">
                                                        14ms
                                                    </span>
                                                </div>
                                                <div className="h-px w-8 bg-gradient-to-l from-transparent to-zinc-200 dark:to-zinc-800" />
                                            </div>
                                        </div>
                                    </div>
                                ) : (
                                    <div className="bg-zinc-50 dark:bg-zinc-900/50 border border-dashed border-zinc-200 dark:border-zinc-800 rounded-[2rem] p-20 text-center h-full flex flex-col justify-center items-center group transition-colors hover:border-zinc-300 dark:hover:border-zinc-700">
                                        <h3 className="text-4xl font-display italic text-zinc-900 dark:text-zinc-100 mb-6 group-hover:scale-105 transition-transform duration-500">No Active Move</h3>
                                        <p className="text-lg text-zinc-500 max-w-md mx-auto mb-10 font-light leading-relaxed">
                                            The war room is quiet. Select a move from your queue or create a new battle plan to begin execution.
                                        </p>
                                        <Button
                                            onClick={() => setShowWizard(true)}
                                            variant="outline"
                                            className="h-14 px-8 rounded-full border-zinc-300 dark:border-zinc-700 text-zinc-700 dark:text-zinc-300 hover:bg-white dark:hover:bg-zinc-800 hover:border-zinc-900 dark:hover:border-zinc-100 hover:text-zinc-900 dark:hover:text-zinc-100 transition-all duration-300 active:scale-95"
                                        >
                                            <Zap className="w-4 h-4 mr-2" />
                                            Initialize First Move
                                        </Button>
                                    </div>
                                )}
                            </section>
                        </div>

                        {/* RIGHT COLUMN: The Queue (35%) */}
                        <div className="lg:w-[35%] min-w-0 flex flex-col gap-8">

                            {/* Queue Header */}
                            <div className="flex items-center justify-between pb-4 border-b border-zinc-100 dark:border-zinc-800">
                                <div className="flex items-center gap-2">
                                    <div className="w-1 h-1 rounded-full bg-zinc-300 dark:bg-zinc-700" />
                                    <div className="text-[11px] font-bold uppercase tracking-[0.25em] text-zinc-400 dark:text-zinc-500">
                                        Up Next
                                    </div>
                                </div>
                                <span className="text-[10px] font-bold uppercase tracking-wider text-zinc-300 dark:text-zinc-700">
                                    {queuedMoves.length} Missions
                                </span>
                            </div>

                            {/* Queue List */}
                            <div className="space-y-4">
                                {queuedMoves.length > 0 ? (
                                    <div className="space-y-2">
                                        {queuedMoves.map((move, index) => (
                                            <div
                                                key={move.id}
                                                className="relative group animate-in fade-in slide-in-from-right-8 duration-700 fill-mode-backwards"
                                                style={{ animationDelay: `${index * 100}ms` }}
                                            >
                                                <div className="absolute -left-4 top-1/2 -translate-y-1/2 w-0.5 h-6 bg-zinc-200 dark:bg-zinc-700 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                                                <MoveCard
                                                    move={move}
                                                    variant="row"
                                                    onClick={() => handleOpenMove(move)}
                                                />
                                                {/* Batch 4: Visual Keyboard Hint [1], [2] etc */}
                                                <span className="absolute right-2 top-1/2 -translate-y-1/2 text-[9px] font-mono text-zinc-300 dark:text-zinc-600 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
                                                    [{index + 1}]
                                                </span>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <div className="text-zinc-400 italic py-8 text-center bg-zinc-50/50 dark:bg-zinc-900/50 rounded-2xl border border-zinc-100 dark:border-zinc-800">
                                        Queue is empty.
                                    </div>
                                )}
                            </div>

                            {/* Archive / Completed (Collapsed or Bottom) */}
                            {completedMoves.length > 0 && (
                                <div className="pt-8 mt-auto">
                                    <h3 className="text-xs font-bold uppercase tracking-[0.2em] text-zinc-400 dark:text-zinc-600 mb-4 pl-1 border-b border-zinc-100 dark:border-zinc-800 pb-2">
                                        Completed
                                    </h3>
                                    <div className="space-y-2 opacity-60 hover:opacity-100 transition-opacity">
                                        {completedMoves.slice(0, 3).map(move => (
                                            <MoveCard
                                                key={move.id}
                                                move={move}
                                                variant="row"
                                                onClick={() => handleOpenMove(move)}
                                            />
                                        ))}
                                        {completedMoves.length > 3 && (
                                            <Button variant="ghost" className="w-full text-zinc-400 text-xs uppercase tracking-wider">
                                                View All Archived
                                            </Button>
                                        )}
                                    </div>
                                </div>
                            )}

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
            </div>
        </AppLayout>
    );
}
