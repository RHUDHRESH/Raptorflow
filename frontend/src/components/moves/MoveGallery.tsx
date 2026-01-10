"use client";

import { useState, useRef, useEffect } from "react";
import { Move, MoveStatus, MOVE_CATEGORIES } from "./types";
import { MoveIntelCenter } from "./MoveIntelCenter";
import { BlueprintModal } from "@/components/ui/BlueprintModal";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { BlueprintProgress } from "@/components/ui/BlueprintProgress";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { Search, ArrowRight, Activity, Calendar, Play, MoreVertical, Trash2, Copy, Pause, Clock, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";
import { useMovesStore } from "@/stores/movesStore";
import { format, formatDistanceToNow } from "date-fns";
import gsap from "gsap";

/* ══════════════════════════════════════════════════════════════════════════════
   MOVE GALLERY — RAPTORFLOW PREMIUM
   Displays all moves with quick actions, animations, and premium cards.
   ══════════════════════════════════════════════════════════════════════════════ */

interface MoveGalleryProps {
    moves: Move[];
    searchQuery: string;
    className?: string;
}

export function MoveGallery({ moves, searchQuery, className }: MoveGalleryProps) {
    const gridRef = useRef<HTMLDivElement>(null);
    const [selectedMove, setSelectedMove] = useState<Move | null>(null);
    const [filter, setFilter] = useState<MoveStatus | 'all'>('all');
    const [menuOpenId, setMenuOpenId] = useState<string | null>(null);

    const { updateMoveStatus, deleteMove } = useMovesStore();

    const filteredMoves = moves
        .filter(move => {
            const q = searchQuery.toLowerCase();
            const matchesSearch =
                move.name.toLowerCase().includes(q) ||
                move.goal.toLowerCase().includes(q) ||
                move.context.toLowerCase().includes(q) ||
                move.category.toLowerCase().includes(q);

            const matchesFilter = filter === 'all' || move.status === filter;
            return matchesSearch && matchesFilter;
        })
        .sort((a, b) => {
            // Active first, then by date
            if (a.status === 'active' && b.status !== 'active') return -1;
            if (a.status !== 'active' && b.status === 'active') return 1;
            return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
        });

    const statusCounts = {
        all: moves.length,
        active: moves.filter(m => m.status === 'active').length,
        draft: moves.filter(m => m.status === 'draft').length,
        completed: moves.filter(m => m.status === 'completed').length,
        paused: moves.filter(m => m.status === 'paused').length,
    };

    const handleStartMove = (e: React.MouseEvent, move: Move) => {
        e.stopPropagation();
        updateMoveStatus(move.id, 'active');
        setMenuOpenId(null);
    };

    const handlePauseMove = (e: React.MouseEvent, move: Move) => {
        e.stopPropagation();
        updateMoveStatus(move.id, 'paused');
        setMenuOpenId(null);
    };

    const handleDeleteMove = (e: React.MouseEvent, move: Move) => {
        e.stopPropagation();
        if (confirm(`Are you sure you want to delete "${move.name}"?`)) {
            deleteMove(move.id);
        }
        setMenuOpenId(null);
    };

    return (
        <div className={cn("space-y-8", className)}>
            {/* Toolbar */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h2 className="font-editorial text-2xl text-[var(--ink)]">Your Moves</h2>
                    <p className="text-sm text-[var(--ink-secondary)]">
                        {statusCounts.active} active, {statusCounts.draft} drafts
                    </p>
                </div>

                <div className="flex items-center gap-3">
                    {/* Filter Pills */}
                    <div className="flex items-center p-1 bg-[var(--surface)] rounded-[var(--radius)] border border-[var(--border)] shadow-sm">
                        {(['all', 'active', 'draft', 'completed'] as const).map((s) => (
                            <button
                                key={s}
                                onClick={() => setFilter(s)}
                                className={cn(
                                    "px-3 py-2 text-xs font-medium rounded-[var(--radius-sm)] capitalize transition-all",
                                    filter === s
                                        ? "bg-[var(--paper)] text-[var(--ink)] shadow-md"
                                        : "text-[var(--muted)] hover:text-[var(--ink)]"
                                )}
                            >
                                {s}
                                {statusCounts[s] > 0 && (
                                    <span className="ml-1.5 text-[10px] opacity-70">({statusCounts[s]})</span>
                                )}
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {/* Grid */}
            <div ref={gridRef} className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
                {filteredMoves.length === 0 ? (
                    <div className="col-span-full py-20 text-center border-2 border-dashed border-[var(--border)] rounded-[var(--radius-lg)] bg-gradient-to-b from-[var(--surface-subtle)]/50 to-transparent">
                        <div className="w-16 h-16 bg-[var(--surface)] rounded-full flex items-center justify-center mx-auto mb-6 text-[var(--muted)]">
                            <Sparkles size={28} />
                        </div>
                        <p className="text-lg font-medium text-[var(--ink)]">
                            {searchQuery ? "No moves found" : "No moves yet"}
                        </p>
                        <p className="text-sm text-[var(--muted)] mt-2">
                            {searchQuery ? "Try adjusting your search." : "Create your first move to get started!"}
                        </p>
                    </div>
                ) : (
                    filteredMoves.map((move, idx) => (
                        <GalleryCard
                            key={move.id}
                            move={move}
                            index={idx}
                            onClick={() => setSelectedMove(move)}
                            onStart={(e) => handleStartMove(e, move)}
                            onPause={(e) => handlePauseMove(e, move)}
                            onDelete={(e) => handleDeleteMove(e, move)}
                            menuOpen={menuOpenId === move.id}
                            onMenuToggle={(e) => {
                                e.stopPropagation();
                                setMenuOpenId(menuOpenId === move.id ? null : move.id);
                            }}
                        />
                    ))
                )}
            </div>

            {/* INTEL CENTER MODAL */}
            <BlueprintModal
                isOpen={!!selectedMove}
                onClose={() => setSelectedMove(null)}
                title="Move Details"
                code="MOV-DET"
                size="xl"
            >
                {selectedMove && (
                    <div className="py-2">
                        <MoveIntelCenter move={selectedMove} />
                    </div>
                )}
            </BlueprintModal>
        </div>
    );
}

interface GalleryCardProps {
    move: Move;
    index: number;
    onClick: () => void;
    onStart: (e: React.MouseEvent) => void;
    onPause: (e: React.MouseEvent) => void;
    onDelete: (e: React.MouseEvent) => void;
    menuOpen: boolean;
    onMenuToggle: (e: React.MouseEvent) => void;
}

function GalleryCard({ move, index, onClick, onStart, onPause, onDelete, menuOpen, onMenuToggle }: GalleryCardProps) {
    const category = MOVE_CATEGORIES[move.category];

    const statusColors = {
        draft: "bg-[var(--surface)] text-[var(--muted)] border-[var(--border)]",
        active: "bg-[var(--blueprint)]/10 text-[var(--blueprint)] border-[var(--blueprint)]/30",
        completed: "bg-[var(--success)]/10 text-[var(--success)] border-[var(--success)]/30",
        paused: "bg-[var(--warning)]/10 text-[var(--warning)] border-[var(--warning)]/30",
    };

    // Calculate progress for active moves
    const progress = move.status === 'active' && move.execution.length > 0
        ? Math.round((move.execution.filter(d => d.pillarTask.status === 'done').length / move.execution.length) * 100)
        : move.progress || 0;

    return (
        <div
            onClick={onClick}
            style={{ animationDelay: `${index * 80}ms` }}
            className={cn(
                "group relative p-6 rounded-[var(--radius-lg)] bg-[var(--paper)] border border-[var(--border)]",
                "hover:border-[var(--blueprint)] hover:shadow-xl transition-all duration-300 cursor-pointer",
                "animate-in fade-in slide-in-from-bottom-4",
                "hover:-translate-y-1",
                move.status === 'active' && "ring-1 ring-[var(--blueprint)]/20"
            )}
        >
            {/* Status Ribbon for Active */}
            {move.status === 'active' && (
                <div className="absolute top-0 right-5 w-1.5 h-10 bg-gradient-to-b from-[var(--blueprint)] to-[var(--blueprint)]/30 rounded-b-full" />
            )}

            {/* Corner Accent */}
            <div className="absolute top-0 left-0 w-8 h-8 overflow-hidden">
                <div className="absolute -top-4 -left-4 w-8 h-8 rotate-45 bg-gradient-to-r from-[var(--blueprint)]/0 to-[var(--blueprint)]/20 group-hover:to-[var(--blueprint)]/40 transition-colors" />
            </div>

            {/* Top Row */}
            <div className="flex justify-between items-start mb-5">
                <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-[var(--radius)] bg-gradient-to-br from-[var(--surface)] to-[var(--surface-subtle)] flex items-center justify-center border border-[var(--border)] text-2xl shadow-sm group-hover:scale-110 transition-transform">
                        {category.emoji}
                    </div>
                    <div>
                        <h3 className="font-editorial text-lg text-[var(--ink)] leading-tight group-hover:text-[var(--blueprint)] transition-colors line-clamp-1">
                            {move.name}
                        </h3>
                        <span className="text-[10px] font-mono text-[var(--muted)] uppercase tracking-wider">
                            {category.name}
                        </span>
                    </div>
                </div>

                {/* Menu Button */}
                <div className="relative">
                    <button
                        onClick={onMenuToggle}
                        className="p-2 rounded-[var(--radius)] hover:bg-[var(--surface)] text-[var(--muted)] opacity-0 group-hover:opacity-100 transition-all"
                    >
                        <MoreVertical size={16} />
                    </button>

                    {/* Dropdown Menu */}
                    {menuOpen && (
                        <div className="absolute top-full right-0 mt-1 w-44 bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius)] shadow-xl z-20 py-1 animate-in fade-in slide-in-from-top-2 duration-150">
                            {move.status === 'draft' && (
                                <button
                                    onClick={onStart}
                                    className="w-full px-4 py-2.5 text-left text-sm text-[var(--ink)] hover:bg-[var(--surface)] flex items-center gap-3 transition-colors"
                                >
                                    <Play size={14} className="text-[var(--success)]" /> Start Move
                                </button>
                            )}
                            {move.status === 'active' && (
                                <button
                                    onClick={onPause}
                                    className="w-full px-4 py-2.5 text-left text-sm text-[var(--ink)] hover:bg-[var(--surface)] flex items-center gap-3 transition-colors"
                                >
                                    <Pause size={14} className="text-[var(--warning)]" /> Pause Move
                                </button>
                            )}
                            {move.status === 'paused' && (
                                <button
                                    onClick={onStart}
                                    className="w-full px-4 py-2.5 text-left text-sm text-[var(--ink)] hover:bg-[var(--surface)] flex items-center gap-3 transition-colors"
                                >
                                    <Play size={14} className="text-[var(--success)]" /> Resume Move
                                </button>
                            )}
                            <button
                                onClick={(e) => { e.stopPropagation(); }}
                                className="w-full px-4 py-2.5 text-left text-sm text-[var(--ink)] hover:bg-[var(--surface)] flex items-center gap-3 transition-colors"
                            >
                                <Copy size={14} className="text-[var(--muted)]" /> Duplicate
                            </button>
                            <hr className="my-1 border-[var(--border)]" />
                            <button
                                onClick={onDelete}
                                className="w-full px-4 py-2.5 text-left text-sm text-[var(--warning)] hover:bg-[var(--warning)]/10 flex items-center gap-3 transition-colors"
                            >
                                <Trash2 size={14} /> Delete
                            </button>
                        </div>
                    )}
                </div>
            </div>

            {/* Status Badge */}
            <div className="flex items-center gap-2 mb-4">
                <span className={cn(
                    "px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider border",
                    statusColors[move.status]
                )}>
                    {move.status}
                </span>
                {move.status === 'active' && (
                    <span className="text-[10px] text-[var(--blueprint)] flex items-center gap-1.5 font-medium">
                        <span className="w-1.5 h-1.5 bg-[var(--blueprint)] rounded-full animate-pulse" />
                        Live
                    </span>
                )}
            </div>

            {/* Goal */}
            <div className="mb-5">
                <p className="text-sm text-[var(--ink-secondary)] line-clamp-2 leading-relaxed">
                    {move.goal || "No specific goal set."}
                </p>
            </div>

            {/* Progress Bar (for active) */}
            {move.status === 'active' && (
                <div className="mb-5">
                    <div className="flex justify-between text-xs mb-2">
                        <span className="text-[var(--muted)]">Progress</span>
                        <span className="font-bold text-[var(--ink)]">{progress}%</span>
                    </div>
                    <div className="h-2 bg-[var(--surface)] rounded-full overflow-hidden">
                        <div
                            className="h-full bg-gradient-to-r from-[var(--blueprint)] to-[var(--success)] transition-all duration-700 ease-out"
                            style={{ width: `${progress}%` }}
                        />
                    </div>
                </div>
            )}

            {/* Footer */}
            <div className="pt-5 border-t border-[var(--border-subtle)] flex items-center justify-between text-xs text-[var(--muted)]">
                <div className="flex items-center gap-4">
                    <span className="flex items-center gap-1.5">
                        <Calendar size={12} /> {move.duration} Days
                    </span>
                    <span className="flex items-center gap-1.5">
                        <Clock size={12} />
                        {formatDistanceToNow(new Date(move.createdAt), { addSuffix: true })}
                    </span>
                </div>

                <div className="flex items-center gap-1.5 group-hover:translate-x-1 transition-transform text-[var(--blueprint)] font-medium opacity-0 group-hover:opacity-100">
                    View <ArrowRight size={12} />
                </div>
            </div>

            {/* Quick Start Button for Drafts */}
            {move.status === 'draft' && (
                <div className="absolute inset-x-5 bottom-5 opacity-0 group-hover:opacity-100 transition-all duration-300 translate-y-3 group-hover:translate-y-0">
                    <button
                        onClick={onStart}
                        className="w-full py-2.5 bg-gradient-to-r from-[var(--ink)] to-[var(--ink)]/90 text-white text-sm font-medium rounded-[var(--radius)] hover:shadow-lg transition-all flex items-center justify-center gap-2"
                    >
                        <Play size={14} /> Start This Move
                    </button>
                </div>
            )}
        </div>
    );
}
