'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { AppLayout } from '@/components/layout/AppLayout';
import { Move } from '@/lib/campaigns-types';
import { getMoves, getActiveMove, setActiveMove } from '@/lib/campaigns';
import { MoveCard } from '@/components/moves/MoveCard';
import { NewMoveWizard } from '@/components/moves/NewMoveWizard';
import { MoveDetail } from '@/components/moves/MoveDetail';
import { Button } from '@/components/ui/button';
import { Plus, Zap, Play, Check } from 'lucide-react';
import { toast } from 'sonner';

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
    }, [refreshMoves]);

    const handleMoveCreated = useCallback((move: Move) => {
        refreshMoves();
        setShowWizard(false);
        // If it was auto-started, open details
        if (move.status === 'active') {
            setSelectedMove(move);
        }
    }, [refreshMoves]);

    const handleMoveUpdated = useCallback((updatedMove: Move) => {
        refreshMoves();
        if (selectedMove?.id === updatedMove.id) {
            setSelectedMove(updatedMove);
        }
    }, [refreshMoves, selectedMove]);

    const handleMoveDeleted = useCallback((moveId: string) => {
        // delete logic is in detail component, just refresh
        refreshMoves();
        setSelectedMove(null);
    }, [refreshMoves]);

    // Grouping
    const queuedMoves = moves.filter(m => m.status === 'queued' || m.status === 'draft');
    const completedMoves = moves.filter(m => m.status === 'completed' || m.status === 'abandoned');

    const handleOpenMove = (move: Move) => {
        setSelectedMove(move);
    };

    return (
        <AppLayout>
            <div className="max-w-[1200px] mx-auto px-12 py-12 space-y-12 pb-24 animate-in fade-in duration-500">
                {/* Header */}
                <div className="flex items-end justify-between border-b border-zinc-200 dark:border-zinc-800 pb-8">
                    <div>
                        <div className="text-xs font-bold uppercase tracking-[0.15em] text-zinc-400 dark:text-zinc-500 mb-3 ml-1">
                            Tactical
                        </div>
                        <h1 className="text-[40px] leading-[1.1] font-display font-medium text-zinc-900 dark:text-zinc-100">
                            Moves
                        </h1>
                        <p className="text-base text-zinc-500 dark:text-zinc-400 mt-4 max-w-xl leading-relaxed">
                            Weekly execution packets that ship outcomes.
                            Execute one Move at a time.
                        </p>
                    </div>
                    <Button
                        onClick={() => setShowWizard(true)}
                        className="rounded-full bg-zinc-900 text-white hover:bg-zinc-800 dark:bg-white dark:text-zinc-900 dark:hover:bg-zinc-100 h-11 px-6 shadow-sm hover:shadow-md transition-all"
                    >
                        <Plus className="w-4 h-4 mr-2" />
                        Create Move
                    </Button>
                </div>

                <div className="animate-in slide-in-from-bottom-4 duration-700 fade-in fill-mode-backwards delay-150">
                    {/* Active Hero Block */}
                    <div className="mb-12">
                        <div className="flex items-center gap-2 mb-4">
                            <div className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                            <h2 className="text-xs font-bold uppercase tracking-widest text-zinc-500 dark:text-zinc-400">
                                Current Environment
                            </h2>
                        </div>

                        {activeMove ? (
                            <div className="bg-white dark:bg-zinc-900 rounded-2xl p-8 border border-zinc-200 dark:border-zinc-800 shadow-lg shadow-zinc-200/50 dark:shadow-none relative overflow-hidden group hover:border-zinc-300 dark:hover:border-zinc-700 transition-all">
                                <div className="absolute top-0 left-0 w-1.5 h-full bg-emerald-500" />
                                <div className="flex justify-between items-start mb-8">
                                    <div>
                                        <div className="flex items-center gap-2 text-emerald-600 mb-3">
                                            <span className="text-[10px] font-bold uppercase tracking-wide bg-emerald-50 dark:bg-emerald-900/30 px-2 py-1 rounded-full border border-emerald-100 dark:border-emerald-900">
                                                Active • Week 1
                                            </span>
                                        </div>
                                        <h2 className="text-3xl font-display font-semibold text-zinc-900 dark:text-zinc-100 pb-3">
                                            {activeMove.name}
                                        </h2>
                                        <div className="flex items-center gap-4 text-zinc-500 text-sm">
                                            <span className="font-medium text-zinc-900 dark:text-zinc-100">
                                                {activeMove.duration} Day Sprint
                                            </span>
                                            <span className="w-1 h-1 rounded-full bg-zinc-300 dark:bg-zinc-700" />
                                            <span>
                                                {activeMove.checklist.filter(i => i.completed).length} of {activeMove.checklist.length} Tasks Complete
                                            </span>
                                        </div>
                                    </div>
                                    <Button
                                        onClick={() => handleOpenMove(activeMove)}
                                        className="bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl shadow-lg shadow-emerald-900/10 h-10 px-6 font-medium"
                                    >
                                        Open Move
                                    </Button>
                                </div>

                                {/* Mini Checklist Preview */}
                                <div className="space-y-3 bg-zinc-50 dark:bg-zinc-800/50 p-6 rounded-xl border border-zinc-100 dark:border-zinc-800/50">
                                    {activeMove.checklist.slice(0, 3).map((item) => (
                                        <div key={item.id} className="flex items-center gap-3 text-sm">
                                            <div className={`w-5 h-5 rounded border flex items-center justify-center transition-colors ${item.completed ? 'bg-emerald-100 border-emerald-200 text-emerald-600' : 'bg-white dark:bg-zinc-900 border-zinc-300 dark:border-zinc-600 text-transparent'}`}>
                                                <Check className="w-3.5 h-3.5" />
                                            </div>
                                            <span className={item.completed ? 'text-zinc-400 line-through' : 'text-zinc-700 dark:text-zinc-300'}>
                                                {item.label}
                                            </span>
                                        </div>
                                    ))}
                                    {activeMove.checklist.length > 3 && (
                                        <div className="text-xs font-medium text-emerald-600 dark:text-emerald-400 pl-8 pt-1">
                                            + {activeMove.checklist.length - 3} remaining
                                        </div>
                                    )}
                                </div>
                            </div>
                        ) : (
                            <div className="bg-zinc-50 dark:bg-zinc-900/50 rounded-2xl p-8 border border-dashed border-zinc-300 dark:border-zinc-700 text-center flex flex-col items-center justify-center py-16 hover:bg-zinc-100/50 dark:hover:bg-zinc-900 transition-colors cursor-pointer" onClick={() => setShowWizard(true)}>
                                <div className="w-14 h-14 rounded-full bg-white dark:bg-zinc-800 shadow-sm border border-zinc-200 dark:border-zinc-700 flex items-center justify-center text-zinc-400 mb-5">
                                    <Zap className="w-7 h-7" />
                                </div>
                                <h3 className="text-xl font-display font-medium text-zinc-900 dark:text-zinc-100 mb-2">No active move</h3>
                                <p className="text-zinc-500 max-w-sm mx-auto mb-6 leading-relaxed">
                                    You are not executing anything right now. <br />
                                    Momentum kills doubt. Start a sprint.
                                </p>
                                <Button onClick={(e) => { e.stopPropagation(); setShowWizard(true); }}>
                                    Launch New Move
                                </Button>
                            </div>
                        )}
                    </div>

                    {/* Moves List (Grid Layout for Desktop) */}
                    <div className="space-y-6">
                        {/* Filters */}
                        <div className="flex gap-6 border-b border-zinc-200 dark:border-zinc-800">
                            {(['all', 'queued', 'completed'] as const).map(f => (
                                <button
                                    key={f}
                                    onClick={() => setFilter(f)}
                                    className={`pb-4 text-sm font-medium capitalize transition-all relative ${filter === f
                                        ? 'text-zinc-900 dark:text-zinc-100'
                                        : 'text-zinc-500 hover:text-zinc-800 dark:hover:text-zinc-300'
                                        }`}
                                >
                                    {f === 'queued' ? 'Up Next' : f === 'completed' ? 'History' : 'All Moves'}
                                    {filter === f && (
                                        <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-zinc-900 dark:bg-zinc-100 rounded-t-full" />
                                    )}
                                </button>
                            ))}
                        </div>

                        <div className="min-h-[200px]">
                            {filter !== 'completed' && queuedMoves.length > 0 && (
                                <div className="mb-10 animate-in fade-in">
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        {queuedMoves.map(move => (
                                            <div key={move.id} className="group transition-all duration-300 hover:-translate-y-1">
                                                <MoveCard move={move} onClick={() => handleOpenMove(move)} />
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {filter !== 'queued' && completedMoves.length > 0 && (
                                <div className="animate-in fade-in">
                                    <h3 className="text-xs font-bold uppercase tracking-widest text-zinc-400 dark:text-zinc-600 mb-4 pl-1">
                                        Execution Archive
                                    </h3>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 opacity-90">
                                        {completedMoves.map(move => (
                                            <div key={move.id} className="group transition-all duration-300 hover:-translate-y-1">
                                                <MoveCard move={move} onClick={() => handleOpenMove(move)} />
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {queuedMoves.length === 0 && completedMoves.length === 0 && activeMove && (
                                <div className="text-center py-16 text-zinc-400">
                                    <p>Your queue is empty. Focus on your active move.</p>
                                </div>
                            )}
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
        </AppLayout>
    );
}
