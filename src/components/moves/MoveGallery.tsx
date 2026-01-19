"use client";

import { useState, useMemo } from "react";
import { Move, MoveStatus, MOVE_CATEGORIES } from "./types";
import { MoveIntelCenter } from "./MoveIntelCenter";
import { BlueprintModal } from "@/components/ui/BlueprintModal";
import { Search, Play, MoreVertical, Trash2, Pause, Check, Calendar, ChevronRight, Layers, Zap } from "lucide-react";
import { cn } from "@/lib/utils";
import { useMovesStore } from "@/stores/movesStore";
import { MoveCategoryIcon } from "./MoveCategoryIcon";

/* ══════════════════════════════════════════════════════════════════════════════
   MOVE GALLERY — QUIET LUXURY REDESIGN
   Clean, editorial cards with proper hierarchy and campaign links
   ══════════════════════════════════════════════════════════════════════════════ */

interface MoveGalleryProps {
    moves: Move[];
    searchQuery?: string;
    selectedMove?: Move | null;
}

export function MoveGallery({ moves, searchQuery = "" }: MoveGalleryProps) {
    const [selectedMove, setSelectedMove] = useState<Move | null>(null);
    const [filter, setFilter] = useState<'all' | MoveStatus>('all');
    const [openMenuId, setOpenMenuId] = useState<string | null>(null);

    const { updateMove, deleteMove } = useMovesStore();

    // Filter moves
    const filteredMoves = moves
        .filter(m => filter === 'all' || m.status === filter)
        .filter(m =>
            searchQuery === "" ||
            m.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
            m.category.toLowerCase().includes(searchQuery.toLowerCase())
        );

    // Status counts
    const statusCounts = {
        all: moves.length,
        active: moves.filter(m => m.status === 'active').length,
        draft: moves.filter(m => m.status === 'draft').length,
        completed: moves.filter(m => m.status === 'completed').length,
        paused: moves.filter(m => m.status === 'paused').length,
    };

    const handleStartMove = (e: React.MouseEvent, move: Move) => {
        e.stopPropagation();
        updateMove(move.id, { status: 'active', startDate: new Date().toISOString() });
        setOpenMenuId(null);
    };

    const handlePauseMove = (e: React.MouseEvent, move: Move) => {
        e.stopPropagation();
        updateMove(move.id, { status: 'paused' });
        setOpenMenuId(null);
    };

    const handleDeleteMove = (e: React.MouseEvent, move: Move) => {
        e.stopPropagation();
        deleteMove(move.id);
        setOpenMenuId(null);
    };

    const tabs = [
        { key: 'all', label: 'All' },
        { key: 'active', label: 'Active' },
        { key: 'draft', label: 'Draft' },
        { key: 'completed', label: 'Completed' },
    ] as const;

    return (
        <div className="space-y-6">
            {/* Header with Tabs - Quiet Luxury Style */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h2 className="font-serif text-xl text-[var(--ink)]">Your Moves</h2>
                    <p className="text-xs text-[var(--muted)] mt-0.5">
                        {statusCounts.active} active · {statusCounts.draft} drafts · {statusCounts.completed} completed
                    </p>
                </div>

                {/* Segmented Control - Subtle */}
                <div className="inline-flex items-center p-1 bg-[var(--surface)] border border-[var(--border)] rounded-[var(--radius)]">
                    {tabs.map((tab) => (
                        <button
                            key={tab.key}
                            onClick={() => setFilter(tab.key)}
                            className={cn(
                                "px-4 py-1.5 text-xs font-medium rounded-[var(--radius-sm)] transition-all duration-200 min-w-[60px]",
                                filter === tab.key
                                    ? "bg-[var(--ink)] text-white"
                                    : "text-[var(--muted)] hover:text-[var(--ink)]"
                            )}
                        >
                            {tab.label}
                            {statusCounts[tab.key] > 0 && (
                                <span className={cn(
                                    "ml-1.5 text-[10px]",
                                    filter === tab.key ? "opacity-70" : ""
                                )}>
                                    {statusCounts[tab.key]}
                                </span>
                            )}
                        </button>
                    ))}
                </div>
            </div>

            {/* Cards Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {filteredMoves.length === 0 ? (
                    <div className="col-span-full py-16 text-center border border-dashed border-[var(--border)] rounded-[var(--radius-lg)] bg-[var(--surface-subtle)]">
                        <div className="w-12 h-12 bg-[var(--surface)] border border-[var(--border)] rounded-[var(--radius)] flex items-center justify-center mx-auto mb-4">
                            <Search size={20} className="text-[var(--muted)]" />
                        </div>
                        <h3 className="font-serif text-lg text-[var(--ink)] mb-1">No moves found</h3>
                        <p className="text-sm text-[var(--muted)]">
                            {searchQuery ? "Try a different search term" : "Create your first move to get started"}
                        </p>
                    </div>
                ) : (
                    filteredMoves.map((move) => (
                        <MoveCard
                            key={move.id}
                            move={move}
                            onClick={() => setSelectedMove(move)}
                            onStart={(e) => handleStartMove(e, move)}
                            onPause={(e) => handlePauseMove(e, move)}
                            onDelete={(e) => handleDeleteMove(e, move)}
                            menuOpen={openMenuId === move.id}
                            onMenuToggle={(e) => {
                                e.stopPropagation();
                                setOpenMenuId(openMenuId === move.id ? null : move.id);
                            }}
                        />
                    ))
                )}
            </div>

            {/* Detail Modal */}
            <BlueprintModal
                isOpen={!!selectedMove}
                onClose={() => setSelectedMove(null)}
                title={selectedMove?.name || "Move Details"}
                size="lg"
            >
                {selectedMove && <MoveIntelCenter move={selectedMove} />}
            </BlueprintModal>
        </div>
    );
}

/* ══════════════════════════════════════════════════════════════════════════════
   MOVE CARD — Quiet Luxury Design
   Clean borders, proper hierarchy, campaign badges, day progress
   ══════════════════════════════════════════════════════════════════════════════ */

interface MoveCardProps {
    move: Move;
    onClick: () => void;
    onStart: (e: React.MouseEvent) => void;
    onPause: (e: React.MouseEvent) => void;
    onDelete: (e: React.MouseEvent) => void;
    menuOpen: boolean;
    onMenuToggle: (e: React.MouseEvent) => void;
}

function MoveCard({ move, onClick, onStart, onPause, onDelete, menuOpen, onMenuToggle }: MoveCardProps) {
    const category = MOVE_CATEGORIES[move.category];

    // Calculate current day and progress
    const currentDay = useMemo(() => {
        if (!move.startDate || move.status !== 'active') return null;
        const startDate = new Date(move.startDate);
        const now = new Date();
        const daysDiff = Math.floor((now.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24)) + 1;
        return Math.min(daysDiff, move.duration);
    }, [move.startDate, move.status, move.duration]);

    // Calculate task completion
    const taskStats = useMemo(() => {
        if (!move.execution?.length) return { total: 0, completed: 0, percentage: 0 };

        let total = 0;
        let completed = 0;

        move.execution.forEach(day => {
            // Count pillar
            total++;
            if (day.pillarTask?.status === 'done') completed++;

            // Count clusters
            day.clusterActions?.forEach(task => {
                total++;
                if (task.status === 'done') completed++;
            });

            // Count network
            total++;
            if (day.networkAction?.status === 'done') completed++;
        });

        return { total, completed, percentage: total > 0 ? Math.round((completed / total) * 100) : 0 };
    }, [move.execution]);

    // Status config - Quiet Luxury (muted, border-based)
    const statusConfig = {
        draft: {
            border: "border-[var(--warning)]/30",
            bg: "bg-[var(--warning)]/5",
            text: "text-[var(--warning)]",
            label: "Draft"
        },
        active: {
            border: "border-[var(--success)]/30",
            bg: "bg-[var(--success)]/5",
            text: "text-[var(--success)]",
            label: "Active"
        },
        completed: {
            border: "border-[var(--blueprint)]/30",
            bg: "bg-[var(--blueprint)]/5",
            text: "text-[var(--blueprint)]",
            label: "Completed"
        },
        paused: {
            border: "border-[var(--muted)]/30",
            bg: "bg-[var(--muted)]/5",
            text: "text-[var(--muted)]",
            label: "Paused"
        },
    };

    const config = statusConfig[move.status] || statusConfig.draft;

    return (
        <div
            onClick={onClick}
            className={cn(
                "relative border rounded-[var(--radius)] bg-[var(--paper)] overflow-hidden cursor-pointer transition-all duration-200",
                "hover:border-[var(--ink)] hover:shadow-lg",
                "border-[var(--border)]"
            )}
        >
            {/* Card Header */}
            <div className="p-4 border-b border-[var(--border-subtle)]">
                <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3 flex-1 min-w-0">
                        {/* Category Emoji */}
                        <div className="w-10 h-10 rounded-[var(--radius)] bg-[var(--surface)] border border-[var(--border)] flex items-center justify-center text-lg shrink-0">
                            <MoveCategoryIcon category={move.category} size={20} />
                        </div>

                        {/* Move Info */}
                        <div className="flex-1 min-w-0">
                            <h3 className="font-semibold text-[var(--ink)] leading-tight truncate">
                                {move.name}
                            </h3>
                            <div className="flex items-center gap-2 mt-0.5">
                                <span className="text-xs text-[var(--muted)]">{category?.name}</span>
                                {move.campaignId && (
                                    <span className="flex items-center gap-1 text-[10px] text-[var(--success)] font-medium">
                                        <Layers size={10} />
                                        Campaign
                                    </span>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Actions Menu */}
                    <div className="relative shrink-0">
                        <button
                            onClick={onMenuToggle}
                            className="p-1.5 rounded-[var(--radius-sm)] hover:bg-[var(--surface)] text-[var(--muted)] hover:text-[var(--ink)] transition-colors"
                        >
                            <MoreVertical size={14} />
                        </button>

                        {menuOpen && (
                            <div className="absolute right-0 top-full mt-1 w-36 bg-[var(--paper)] rounded-[var(--radius)] border border-[var(--border)] shadow-lg z-20 py-1">
                                {move.status !== 'active' && (
                                    <button
                                        onClick={onStart}
                                        className="w-full flex items-center gap-2 px-3 py-2 text-xs text-[var(--ink)] hover:bg-[var(--surface)]"
                                    >
                                        <Play size={12} className="text-[var(--success)]" />
                                        Start
                                    </button>
                                )}
                                {move.status === 'active' && (
                                    <button
                                        onClick={onPause}
                                        className="w-full flex items-center gap-2 px-3 py-2 text-xs text-[var(--ink)] hover:bg-[var(--surface)]"
                                    >
                                        <Pause size={12} className="text-[var(--warning)]" />
                                        Pause
                                    </button>
                                )}
                                <button
                                    onClick={onDelete}
                                    className="w-full flex items-center gap-2 px-3 py-2 text-xs text-[var(--error)] hover:bg-[var(--error)]/5"
                                >
                                    <Trash2 size={12} />
                                    Delete
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Card Body */}
            <div className="p-4 space-y-4">
                {/* Progress Section */}
                <div>
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-xs text-[var(--muted)]">
                            {taskStats.completed} of {taskStats.total} tasks
                        </span>
                        <span className="text-xs font-semibold text-[var(--ink)]">
                            {taskStats.percentage}%
                        </span>
                    </div>
                    <div className="h-1.5 bg-[var(--surface)] rounded-full overflow-hidden">
                        <div
                            className="h-full bg-[var(--ink)] rounded-full transition-all duration-300"
                            style={{ width: `${taskStats.percentage}%` }}
                        />
                    </div>
                </div>

                {/* Meta Info Row */}
                <div className="flex items-center justify-between">
                    {/* Status Badge */}
                    <span className={cn(
                        "inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium border",
                        config.border, config.bg, config.text
                    )}>
                        {config.label}
                    </span>

                    {/* Day Progress / Duration */}
                    <div className="flex items-center gap-1.5 text-xs text-[var(--muted)]">
                        {currentDay ? (
                            <>
                                <Zap size={12} className="text-[var(--success)]" />
                                <span>Day {currentDay}/{move.duration}</span>
                            </>
                        ) : (
                            <>
                                <Calendar size={12} />
                                <span>{move.duration} days</span>
                            </>
                        )}
                    </div>
                </div>
            </div>

            {/* Active Indicator Line */}
            {move.status === 'active' && (
                <div className="absolute inset-x-0 bottom-0 h-0.5 bg-[var(--success)]" />
            )}

            {/* Hover Arrow */}
            <div className="absolute right-3 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity">
                <ChevronRight size={16} className="text-[var(--muted)]" />
            </div>
        </div>
    );
}

export default MoveGallery;
