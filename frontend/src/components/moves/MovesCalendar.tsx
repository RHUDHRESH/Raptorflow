"use client";

import { useState, useMemo } from "react";
import { Move, MOVE_CATEGORIES } from "./types";
import { cn } from "@/lib/utils";
import {
    ChevronLeft,
    ChevronRight,
    Calendar as CalendarIcon,
    Check,
    Zap,
    LayoutGrid,
    Rows3,
    Clock,
    Target
} from "lucide-react";
import {
    format,
    addDays,
    startOfMonth,
    endOfMonth,
    eachDayOfInterval,
    isSameMonth,
    isSameDay,
    isToday,
    startOfWeek,
    endOfWeek,
    addMonths,
    subMonths
} from "date-fns";

/* ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
   MOVES CALENDAR ΓÇö Enhanced Quiet Luxury Version
   Clean timeline with month/week toggle and better move visualization
   ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ */

interface MovesCalendarProps {
    moves: Move[];
    onMoveClick?: (move: Move) => void;
    onDayClick?: (date: Date) => void;
}

type ViewMode = "month" | "week";

export function MovesCalendar({ moves, onMoveClick }: MovesCalendarProps) {
    const [currentMonth, setCurrentMonth] = useState(new Date());
    const [viewMode, setViewMode] = useState<ViewMode>("month");

    const monthStart = startOfMonth(currentMonth);
    const monthEnd = endOfMonth(currentMonth);
    const calendarStart = viewMode === "week"
        ? startOfWeek(currentMonth, { weekStartsOn: 1 })
        : startOfWeek(monthStart, { weekStartsOn: 1 });
    const calendarEnd = viewMode === "week"
        ? endOfWeek(currentMonth, { weekStartsOn: 1 })
        : endOfWeek(monthEnd, { weekStartsOn: 1 });

    const days = eachDayOfInterval({ start: calendarStart, end: calendarEnd });
    const weeks = [];
    for (let i = 0; i < days.length; i += 7) {
        weeks.push(days.slice(i, i + 7));
    }

    // Filter moves that overlap with current view
    const visibleMoves = useMemo(() => {
        return moves.filter(move => {
            if (!move.startDate) return false;
            const start = new Date(move.startDate);
            const end = addDays(start, move.duration - 1);
            return end >= calendarStart && start <= calendarEnd;
        }).sort((a, b) => new Date(a.startDate!).getTime() - new Date(b.startDate!).getTime());
    }, [moves, calendarStart, calendarEnd]);

    const navigateMonth = (direction: 'prev' | 'next') => {
        if (viewMode === "week") {
            setCurrentMonth(prev => addDays(prev, direction === 'prev' ? -7 : 7));
        } else {
            setCurrentMonth(prev => direction === 'prev' ? subMonths(prev, 1) : addMonths(prev, 1));
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'active': return 'bg-[var(--ink)] text-white';
            case 'draft': return 'bg-[var(--muted)] text-white';
            case 'completed': return 'bg-green-600 text-white';
            case 'paused': return 'bg-amber-500 text-white';
            default: return 'bg-[var(--muted)] text-white';
        }
    };

    const getCategoryIcon = (category: string) => {
        const cat = MOVE_CATEGORIES[category as keyof typeof MOVE_CATEGORIES];
        return cat?.name || category;
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-[var(--surface)] border border-[var(--border)] rounded-[var(--radius)] flex items-center justify-center">
                        <CalendarIcon size={18} className="text-[var(--ink)]" />
                    </div>
                    <div>
                        <h2 className="font-serif text-xl text-[var(--ink)]">
                            {viewMode === "week"
                                ? `Week of ${format(calendarStart, 'MMM d')}`
                                : format(currentMonth, 'MMMM yyyy')
                            }
                        </h2>
                        <p className="text-xs text-[var(--muted)]">
                            {visibleMoves.length} moves scheduled
                        </p>
                    </div>
                </div>

                <div className="flex items-center gap-2">
                    {/* View Mode Toggle */}
                    <div className="flex border border-[var(--border)] rounded-[var(--radius)] overflow-hidden">
                        <button
                            onClick={() => setViewMode("month")}
                            className={cn(
                                "px-3 py-1.5 text-xs font-medium transition-colors flex items-center gap-1.5",
                                viewMode === "month"
                                    ? "bg-[var(--ink)] text-white"
                                    : "bg-[var(--paper)] text-[var(--muted)] hover:text-[var(--ink)]"
                            )}
                        >
                            <LayoutGrid size={12} />
                            Month
                        </button>
                        <button
                            onClick={() => setViewMode("week")}
                            className={cn(
                                "px-3 py-1.5 text-xs font-medium transition-colors flex items-center gap-1.5",
                                viewMode === "week"
                                    ? "bg-[var(--ink)] text-white"
                                    : "bg-[var(--paper)] text-[var(--muted)] hover:text-[var(--ink)]"
                            )}
                        >
                            <Rows3 size={12} />
                            Week
                        </button>
                    </div>

                    {/* Navigation */}
                    <div className="flex items-center gap-1">
                        <button
                            onClick={() => navigateMonth('prev')}
                            className="p-2 hover:bg-[var(--surface)] rounded-[var(--radius)] transition-colors border border-[var(--border)]"
                        >
                            <ChevronLeft size={16} className="text-[var(--ink)]" />
                        </button>
                        <button
                            onClick={() => setCurrentMonth(new Date())}
                            className="px-3 py-2 text-xs font-medium text-[var(--ink)] hover:bg-[var(--surface)] rounded-[var(--radius)] transition-colors border border-[var(--border)]"
                        >
                            Today
                        </button>
                        <button
                            onClick={() => navigateMonth('next')}
                            className="p-2 hover:bg-[var(--surface)] rounded-[var(--radius)] transition-colors border border-[var(--border)]"
                        >
                            <ChevronRight size={16} className="text-[var(--ink)]" />
                        </button>
                    </div>
                </div>
            </div>

            {/* Calendar Grid */}
            <div className="border border-[var(--border)] rounded-[var(--radius)] overflow-hidden bg-[var(--paper)]">
                {/* Day Headers */}
                <div className="grid grid-cols-7 bg-[var(--surface)] border-b border-[var(--border)]">
                    {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map(day => (
                        <div key={day} className="py-3 text-center text-[10px] font-semibold text-[var(--muted)] uppercase tracking-wider">
                            {day}
                        </div>
                    ))}
                </div>

                {/* Weeks */}
                {weeks.map((week, weekIdx) => (
                    <div key={weekIdx} className="grid grid-cols-7 border-b border-[var(--border)] last:border-b-0">
                        {week.map((day, dayIdx) => {
                            const isCurrentMonth = isSameMonth(day, currentMonth);
                            const isCurrentDay = isToday(day);
                            const dayMoves = visibleMoves.filter(move => {
                                if (!move.startDate) return false;
                                const start = new Date(move.startDate);
                                const end = addDays(start, move.duration - 1);
                                return day >= start && day <= end;
                            });

                            return (
                                <div
                                    key={dayIdx}
                                    className={cn(
                                        "min-h-[90px] p-2 border-r border-[var(--border)] last:border-r-0 transition-colors",
                                        !isCurrentMonth && "bg-[var(--surface)]/30",
                                        isCurrentDay && "bg-green-50/50"
                                    )}
                                >
                                    {/* Day Number */}
                                    <div className={cn(
                                        "text-xs font-medium mb-1.5 flex items-center justify-between",
                                        !isCurrentMonth && "text-[var(--muted)]/40",
                                        isCurrentMonth && "text-[var(--ink)]",
                                    )}>
                                        <span className={cn(
                                            "w-6 h-6 flex items-center justify-center rounded-full",
                                            isCurrentDay && "bg-green-600 text-white font-bold"
                                        )}>
                                            {format(day, 'd')}
                                        </span>
                                    </div>

                                    {/* Move indicators */}
                                    <div className="space-y-1">
                                        {dayMoves.slice(0, 3).map(move => {
                                            const isStart = move.startDate && isSameDay(day, new Date(move.startDate));
                                            const isEnd = move.startDate && isSameDay(day, addDays(new Date(move.startDate), move.duration - 1));

                                            return (
                                                <button
                                                    key={move.id}
                                                    onClick={() => onMoveClick?.(move)}
                                                    className={cn(
                                                        "w-full h-6 flex items-center gap-1 text-[10px] font-medium transition-all hover:brightness-110",
                                                        getStatusColor(move.status),
                                                        isStart && "rounded-l-md pl-1.5",
                                                        isEnd && "rounded-r-md pr-1.5",
                                                        isStart && isEnd && "rounded-md px-1.5",
                                                        !isStart && !isEnd && "px-1"
                                                    )}
                                                >
                                                    {isStart && (
                                                        <>
                                                            <Target size={10} className="shrink-0" />
                                                            <span className="truncate">{move.name}</span>
                                                        </>
                                                    )}
                                                </button>
                                            );
                                        })}
                                        {dayMoves.length > 3 && (
                                            <div className="text-[10px] text-[var(--muted)] font-medium pl-1">
                                                +{dayMoves.length - 3} more
                                            </div>
                                        )}
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                ))}
            </div>

            {/* Moves List Summary */}
            {visibleMoves.length > 0 && (
                <div className="space-y-3">
                    <h3 className="text-sm font-semibold text-[var(--ink)]">
                        {viewMode === "week" ? "This Week" : "This Month"}
                    </h3>
                    <div className="grid gap-2">
                        {visibleMoves.map(move => {
                            const category = MOVE_CATEGORIES[move.category];
                            const startDate = move.startDate ? new Date(move.startDate) : null;
                            const endDate = startDate ? addDays(startDate, move.duration - 1) : null;

                            return (
                                <button
                                    key={move.id}
                                    onClick={() => onMoveClick?.(move)}
                                    className="flex items-center justify-between p-3 border border-[var(--border)] rounded-[var(--radius)] bg-[var(--paper)] hover:border-[var(--ink)] transition-colors text-left group"
                                >
                                    <div className="flex items-center gap-3">
                                        <div className={cn(
                                            "w-10 h-10 rounded-[var(--radius)] flex items-center justify-center",
                                            move.status === 'active' && "bg-[var(--ink)] text-white",
                                            move.status === 'draft' && "bg-[var(--surface)] text-[var(--muted)] border border-[var(--border)]",
                                            move.status === 'completed' && "bg-green-100 text-green-700",
                                            move.status === 'paused' && "bg-amber-100 text-amber-700"
                                        )}>
                                            {move.status === 'completed' ? (
                                                <Check size={18} />
                                            ) : (
                                                <Target size={18} />
                                            )}
                                        </div>
                                        <div>
                                            <div className="font-medium text-sm text-[var(--ink)] group-hover:text-[var(--ink)]">{move.name}</div>
                                            <div className="flex items-center gap-2 text-xs text-[var(--muted)]">
                                                <Clock size={10} />
                                                {startDate && format(startDate, 'MMM d')} - {endDate && format(endDate, 'MMM d')}
                                                <span className="text-[var(--border)]">ΓÇó</span>
                                                {move.duration} days
                                            </div>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-3">
                                        <span className="text-xs text-[var(--muted)]">{category?.name}</span>
                                        <span className={cn(
                                            "px-2 py-0.5 rounded text-[10px] font-medium",
                                            move.status === 'active' && "bg-green-100 text-green-700",
                                            move.status === 'draft' && "bg-amber-100 text-amber-700",
                                            move.status === 'completed' && "bg-blue-100 text-blue-700",
                                            move.status === 'paused' && "bg-gray-100 text-gray-600"
                                        )}>
                                            {move.status}
                                        </span>
                                    </div>
                                </button>
                            );
                        })}
                    </div>
                </div>
            )}

            {/* Empty State */}
            {visibleMoves.length === 0 && (
                <div className="py-12 text-center border border-dashed border-[var(--border)] rounded-[var(--radius)]">
                    <CalendarIcon size={32} className="mx-auto mb-3 text-[var(--muted)]" />
                    <h3 className="text-sm font-medium text-[var(--ink)] mb-1">No moves scheduled</h3>
                    <p className="text-xs text-[var(--muted)]">Create an active move to see it on the calendar</p>
                </div>
            )}
        </div>
    );
}

export default MovesCalendar;
