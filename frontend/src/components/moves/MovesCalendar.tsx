"use client";

import { useState, useMemo } from "react";
import { Move, MOVE_CATEGORIES } from "./types";
import { cn } from "@/lib/utils";
import { ChevronLeft, ChevronRight, Calendar as CalendarIcon, Zap, Activity, RotateCcw, Check, Circle } from "lucide-react";
import { format, addDays, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isSameDay, isToday, startOfWeek, endOfWeek, addMonths, subMonths } from "date-fns";

/* ══════════════════════════════════════════════════════════════════════════════
   MOVES CALENDAR — Premium Visual Calendar
   Shows all moves across a month with smooth interactions
   ══════════════════════════════════════════════════════════════════════════════ */

interface MovesCalendarProps {
    moves: Move[];
    onMoveClick?: (move: Move) => void;
    onDayClick?: (date: Date) => void;
}

export function MovesCalendar({ moves, onMoveClick, onDayClick }: MovesCalendarProps) {
    const [currentMonth, setCurrentMonth] = useState(new Date());
    const [hoveredMove, setHoveredMove] = useState<string | null>(null);

    const monthStart = startOfMonth(currentMonth);
    const monthEnd = endOfMonth(currentMonth);
    const calendarStart = startOfWeek(monthStart, { weekStartsOn: 0 });
    const calendarEnd = endOfWeek(monthEnd, { weekStartsOn: 0 });

    const days = eachDayOfInterval({ start: calendarStart, end: calendarEnd });

    // Get all moves that overlap with a specific date (shows draft, active, completed)
    const getMovesForDate = (date: Date) => {
        return moves.filter(move => {
            if (!move.startDate) return false;
            const start = new Date(move.startDate);
            const end = addDays(start, move.duration - 1);
            return date >= start && date <= end;
        });
    };

    // Calculate which day of a move a date represents
    const getMoveDay = (move: Move, date: Date): number => {
        if (!move.startDate) return 0;
        const start = new Date(move.startDate);
        const diff = Math.floor((date.getTime() - start.getTime()) / (1000 * 60 * 60 * 24));
        return diff + 1;
    };

    // Get tasks completed for a move on a specific day
    const getDayStatus = (move: Move, dayNum: number): 'complete' | 'partial' | 'pending' => {
        if (dayNum < 1 || dayNum > move.execution.length) return 'pending';
        const dayExecution = move.execution[dayNum - 1];
        if (!dayExecution) return 'pending';

        const tasks = [dayExecution.pillarTask, ...dayExecution.clusterActions, dayExecution.networkAction];
        const completed = tasks.filter(t => t.status === 'done').length;
        if (completed === tasks.length) return 'complete';
        if (completed > 0) return 'partial';
        return 'pending';
    };

    const navigateMonth = (direction: 'prev' | 'next') => {
        setCurrentMonth(prev => direction === 'prev' ? subMonths(prev, 1) : addMonths(prev, 1));
    };

    return (
        <div className="bg-[var(--paper)] rounded-[var(--radius-lg)] border border-[var(--border)] overflow-hidden shadow-lg">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-[var(--border)] bg-[var(--surface-subtle)]">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-[var(--ink)] rounded-[var(--radius)] flex items-center justify-center text-white">
                        <CalendarIcon size={18} />
                    </div>
                    <div>
                        <h2 className="font-serif text-xl text-[var(--ink)]">
                            {format(currentMonth, 'MMMM yyyy')}
                        </h2>
                        <p className="text-xs text-[var(--muted)]">
                            {moves.filter(m => m.status === 'active').length} active moves
                        </p>
                    </div>
                </div>

                <div className="flex items-center gap-1">
                    <button
                        onClick={() => navigateMonth('prev')}
                        className="p-2 hover:bg-[var(--surface)] rounded-[var(--radius)] transition-colors"
                    >
                        <ChevronLeft size={18} className="text-[var(--muted)]" />
                    </button>
                    <button
                        onClick={() => setCurrentMonth(new Date())}
                        className="px-3 py-1.5 text-xs font-medium text-[var(--ink)] hover:bg-[var(--surface)] rounded-[var(--radius)] transition-colors flex items-center gap-1"
                        title="Go to current month"
                    >
                        <RotateCcw size={12} />
                        Today
                    </button>
                    <button
                        onClick={() => navigateMonth('next')}
                        className="p-2 hover:bg-[var(--surface)] rounded-[var(--radius)] transition-colors"
                    >
                        <ChevronRight size={18} className="text-[var(--muted)]" />
                    </button>
                </div>
            </div>

            {/* Day Headers */}
            <div className="grid grid-cols-7 border-b border-[var(--border)]">
                {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
                    <div key={day} className="py-3 text-center text-xs font-medium text-[var(--muted)] uppercase tracking-wider">
                        {day}
                    </div>
                ))}
            </div>

            {/* Calendar Grid */}
            <div className="grid grid-cols-7">
                {days.map((day, idx) => {
                    const dayMoves = getMovesForDate(day);
                    const isCurrentMonth = isSameMonth(day, currentMonth);
                    const isCurrentDay = isToday(day);

                    return (
                        <div
                            key={idx}
                            onClick={() => onDayClick?.(day)}
                            className={cn(
                                "min-h-[68px] p-2 border-b border-r border-[var(--border)] transition-colors cursor-pointer group",
                                !isCurrentMonth && "bg-[var(--surface-subtle)]/50",
                                isCurrentDay && "bg-[var(--blueprint-light)]/20",
                                "hover:bg-[var(--surface)]"
                            )}
                        >
                            {/* Day Number */}
                            <div className="flex items-center justify-between mb-2">
                                <span className={cn(
                                    "text-sm font-medium",
                                    !isCurrentMonth && "text-[var(--muted)]",
                                    isCurrentMonth && "text-[var(--ink)]",
                                    isCurrentDay && "text-[var(--blueprint)] font-bold"
                                )}>
                                    {format(day, 'd')}
                                </span>
                                {isCurrentDay && (
                                    <span className="w-2 h-2 rounded-full bg-[var(--blueprint)] animate-pulse" />
                                )}
                            </div>

                            {/* Move Pills */}
                            <div className="space-y-1">
                                {dayMoves.slice(0, 3).map(move => {
                                    const category = MOVE_CATEGORIES[move.category];
                                    const dayNum = getMoveDay(move, day);
                                    const status = getDayStatus(move, dayNum);
                                    const isHovered = hoveredMove === move.id;
                                    const isStart = move.startDate && isSameDay(day, new Date(move.startDate));
                                    const isEnd = move.startDate && isSameDay(day, addDays(new Date(move.startDate), move.duration - 1));

                                    return (
                                        <button
                                            key={move.id}
                                            onClick={(e) => { e.stopPropagation(); onMoveClick?.(move); }}
                                            onMouseEnter={() => setHoveredMove(move.id)}
                                            onMouseLeave={() => setHoveredMove(null)}
                                            className={cn(
                                                "w-full text-left px-2 py-1 text-[10px] font-medium transition-all",
                                                "hover:shadow-md hover:scale-105 hover:z-10 relative",
                                                status === 'complete' && "bg-[var(--success)] text-white",
                                                status === 'partial' && "bg-[var(--warning)] text-white",
                                                status === 'pending' && "bg-[var(--ink)] text-white",
                                                isStart && "rounded-l-full pl-3",
                                                isEnd && "rounded-r-full pr-3",
                                                !isStart && !isEnd && "rounded-none",
                                                isStart && isEnd && "rounded-full",
                                                isHovered && "ring-2 ring-[var(--blueprint)] ring-offset-1"
                                            )}
                                        >
                                            <span className="flex items-center gap-1.5 min-w-0 w-full">
                                                {status === 'complete' ? (
                                                    <div className="w-3 h-3 rounded-full bg-[var(--success)] flex items-center justify-center shrink-0">
                                                        <Check size={8} strokeWidth={4} className="text-white" />
                                                    </div>
                                                ) : (
                                                    <div className={cn(
                                                        "w-3 h-3 rounded-full border flex items-center justify-center shrink-0",
                                                        status === 'partial' ? "border-[var(--warning)] bg-[var(--warning)]/20" : "border-[var(--muted)]"
                                                    )}>
                                                        {status === 'partial' && <div className="w-1.5 h-1.5 rounded-full bg-[var(--warning)]" />}
                                                    </div>
                                                )}

                                                <span className="truncate font-medium text-[10px]">
                                                    {move.name}
                                                </span>
                                            </span>
                                        </button>
                                    );
                                })}
                                {dayMoves.length > 3 && (
                                    <span className="text-[10px] text-[var(--muted)] pl-2">
                                        +{dayMoves.length - 3} more
                                    </span>
                                )}
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Legend */}
            <div className="flex items-center justify-between p-4 border-t border-[var(--border)] bg-[var(--surface-subtle)]">
                <div className="flex items-center gap-4 text-xs">
                    <span className="flex items-center gap-1.5">
                        <span className="w-3 h-3 rounded bg-[var(--success)]" />
                        <span className="text-[var(--muted)]">Complete</span>
                    </span>
                    <span className="flex items-center gap-1.5">
                        <span className="w-3 h-3 rounded bg-[var(--warning)]" />
                        <span className="text-[var(--muted)]">In Progress</span>
                    </span>
                    <span className="flex items-center gap-1.5">
                        <span className="w-3 h-3 rounded bg-[var(--ink)]" />
                        <span className="text-[var(--muted)]">Scheduled</span>
                    </span>
                </div>
                <div className="flex items-center gap-1.5 text-xs text-[var(--muted)]">
                    <Activity size={12} />
                    <span>{moves.filter(m => m.status === 'active').length} active</span>
                </div>
            </div>
        </div>
    );
}

export default MovesCalendar;
