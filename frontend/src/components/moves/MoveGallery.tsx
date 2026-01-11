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
import { BlueprintCard } from "@/components/ui/BlueprintCard";

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
                    <h2 className="font-serif text-3xl text-[var(--ink)]">Your Moves</h2>
                    <p className="text-sm text-[var(--ink-secondary)] mt-1">
                        {statusCounts.active} active · {statusCounts.draft} drafts
                    </p>
                </div>

                <div className="flex items-center gap-2">
                    {/* Filter Buttons */}
                    {(['all', 'active', 'draft', 'completed'] as const).map((s) => (
                        <button
                            key={s}
                            onClick={() => setFilter(s)}
                            className={cn(
                                "px-3 py-1.5 text-xs font-mono uppercase tracking-wider rounded-[var(--radius-sm)] border transition-all",
                                filter === s
                                    ? "bg-[var(--ink)] text-[var(--paper)] border-[var(--ink)]"
                                    : "bg-transparent text-[var(--muted)] border-transparent hover:border-[var(--border)] hover:text-[var(--ink)]"
                            )}
                        >
                            {s}
                            {statusCounts[s] > 0 && <span className="ml-2 opacity-50">{statusCounts[s]}</span>}
                        </button>
                    ))}
                </div>
            </div>

            {/* Grid */}
            <div ref={gridRef} className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                {filteredMoves.length === 0 ? (
                    <div className="col-span-full py-24 text-center border border-dashed border-[var(--border)] rounded-[var(--radius-lg)]">
                        <div className="w-12 h-12 bg-[var(--surface)] border border-[var(--border)] flex items-center justify-center mx-auto mb-4 rounded-full">
                            <Sparkles size={20} className="text-[var(--muted)]" />
                        </div>
                        <h3 className="font-serif text-xl text-[var(--ink)] mb-2">
                            {searchQuery ? "No matching moves" : "No moves detected"}
                        </h3>
                        <p className="text-sm text-[var(--muted)] mb-6 max-w-sm mx-auto">
                            {searchQuery ? "Try adjusting your search filters." : "Initialize your first strategic move to begin the campaign."}
                        </p>
                        {!searchQuery && (
                            <BlueprintButton>
                                Create First Move
                            </BlueprintButton>
                        )}
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

    // Status config
    const statusConfig = {
        draft: { color: "var(--muted)", label: "DRAFT" },
        active: { color: "var(--blueprint)", label: "ACTIVE" },
        completed: { color: "var(--success)", label: "COMPLETE" },
        paused: { color: "var(--warning)", label: "PAUSED" },
    };

    const config = statusConfig[move.status] || statusConfig.draft;

    // Calculate progress for active moves
    const progress = move.status === 'active' && move.execution.length > 0
        ? Math.round((move.execution.filter(d => d.pillarTask.status === 'done').length / move.execution.length) * 100)
        : move.progress || 0;

    return (
        <BlueprintCard
            onClick={onClick}
            variant="default"
            showCorners={true}
            padding="md"
            className="cursor-pointer hover:shadow-lg transition-all duration-300 group"
        >
            {/* Header */}
            <div className="flex justify-between items-start mb-6">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 border border-[var(--border)] bg-[var(--surface)] flex items-center justify-center text-xl">
                        {category.emoji}
                    </div>
                    <div>
                        <div className="flex items-center gap-2 mb-0.5">
                            <span className="font-technical text-[10px] text-[var(--blueprint)]">FIG.{String(index + 1).padStart(2, '0')}</span>
                            <div className="w-px h-3 bg-[var(--border)]" />
                            <span className="font-technical text-[10px] text-[var(--muted)] uppercase tracking-wider">{category.name}</span>
                        </div>
                        <h3 className="font-serif text-lg text-[var(--ink)] leading-tight group-hover:text-[var(--blueprint)] transition-colors">
                            {move.name}
                        </h3>
                    </div>
                </div>

                <div className="relative">
                    <button onClick={onMenuToggle} className="p-1 hover:bg-[var(--surface)] rounded transition-colors opacity-0 group-hover:opacity-100">
                        <MoreVertical size={16} className="text-[var(--muted)]" />
                    </button>
                    {/* Dropdown Menu - Simplified for brevity */}
                    {menuOpen && (
                        <div className="absolute top-full right-0 mt-1 w-44 bg-[var(--paper)] border border-[var(--border)] z-20 shadow-xl p-1">
                            {move.status === 'draft' && <button onClick={onStart} className="w-full text-left px-3 py-2 hover:bg-[var(--surface)] text-sm">Start Move</button>}
                            <button onClick={onDelete} className="w-full text-left px-3 py-2 hover:bg-[var(--error-light)] text-[var(--error)] text-sm">Delete</button>
                        </div>
                    )}
                </div>
            </div>

            {/* Content */}
            <p className="text-sm text-[var(--ink-secondary)] line-clamp-2 min-h-[40px] mb-6 font-sans leading-relaxed">
                {move.context || move.goal || "No specific context provided."}
            </p>

            {/* Footer / Status */}
            <div className="pt-4 border-t border-[var(--border-subtle)] flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <span
                        className="w-2 h-2 rounded-full"
                        style={{ backgroundColor: config.color, boxShadow: move.status === 'active' ? `0 0 8px ${config.color}` : 'none' }}
                    />
                    <span className="font-mono text-xs text-[var(--ink)] uppercase tracking-wide">
                        {config.label}
                    </span>
                </div>

                {move.status === 'active' ? (
                    <span className="font-mono text-xs text-[var(--blueprint)]">{progress}% DONE</span>
                ) : (
                    <div className="flex items-center gap-1 text-[var(--muted)] text-xs">
                        <Clock size={12} />
                        <span>{move.duration} DAYS</span>
                    </div>
                )}
            </div>

            {/* Active Progress Bar */}
            {move.status === 'active' && (
                <div className="absolute bottom-0 left-0 right-0 h-1 bg-[var(--surface)]">
                    <div
                        className="h-full bg-[var(--blueprint)] transition-all duration-500"
                        style={{ width: `${progress}%` }}
                    />
                </div>
            )}
        </BlueprintCard>
    );
}
