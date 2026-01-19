"use client";

import { useState, useMemo, useRef, useEffect } from "react";
import { Move, MOVE_CATEGORIES } from "./types";
import { cn } from "@/lib/utils";
import {
    ChevronLeft,
    ChevronRight,
    Calendar as CalendarIcon,
    Clock,
    Target,
    Layers,
    Filter,
    Plus,
    Sun,
    Moon,
    LayoutGrid,
    List,
    CalendarDays,
    CalendarRange
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
    subMonths,
    addWeeks,
    subWeeks,
    setHours,
    startOfDay,
    endOfDay
} from "date-fns";
import gsap from "gsap";

/* ══════════════════════════════════════════════════════════════════════════════
   MOVES CALENDAR PRO — Premium Scheduling Command Center
   Split-panel layout with Day/Week/Month/Agenda views
   ══════════════════════════════════════════════════════════════════════════════ */

interface MovesCalendarProProps {
    moves: Move[];
    onMoveClick?: (move: Move) => void;
    onDateClick?: (date: Date) => void;
    onCreateMove?: () => void;
}

type ViewMode = "day" | "week" | "month" | "agenda";

const HOURS = Array.from({ length: 24 }, (_, i) => i);
const WORK_HOURS = { start: 8, end: 20 };

export function MovesCalendarPro({ moves, onMoveClick, onCreateMove }: MovesCalendarProProps) {
    const [currentDate, setCurrentDate] = useState(new Date());
    const [viewMode, setViewMode] = useState<ViewMode>("week");
    const [selectedCampaign, setSelectedCampaign] = useState<string | null>(null);
    const contentRef = useRef<HTMLDivElement>(null);
    const nowLineRef = useRef<HTMLDivElement>(null);

    // --- ABSOLUTE INFINITY: TRIGGER ARC RESOLUTION ON MOUNT ---
    useEffect(() => {
        const triggerResolution = async () => {
            try {
                // We use a general health-check or heartbeat endpoint that triggers background workers
                // For now, we hit the agenda endpoint to wake up the ticker logic
                await apiClient.getDailyAgenda();
            } catch (e) {
                console.warn("Heartbeat failed, but system is still operational.");
            }
        };
        triggerResolution();
    }, []);

    // Animation on view change
    useEffect(() => {
        if (contentRef.current) {
            gsap.fromTo(contentRef.current,
                { opacity: 0, y: 8 },
                { opacity: 1, y: 0, duration: 0.3, ease: "power2.out" }
            );
        }
    }, [viewMode, currentDate]);

    // Update "now" line position
    useEffect(() => {
        if (nowLineRef.current && (viewMode === "day" || viewMode === "week")) {
            const now = new Date();
            const hours = now.getHours() + now.getMinutes() / 60;
            const percentage = ((hours - WORK_HOURS.start) / (WORK_HOURS.end - WORK_HOURS.start)) * 100;
            nowLineRef.current.style.top = `${Math.max(0, Math.min(100, percentage))}%`;
        }
    }, [viewMode]);

    // Get unique campaigns from moves
    const campaigns = useMemo(() => {
        const campaignSet = new Set<string>();
        moves.forEach(m => { if (m.campaignId) campaignSet.add(m.campaignId); });
        return Array.from(campaignSet);
    }, [moves]);

    // Filter moves by campaign
    const filteredMoves = useMemo(() => {
        if (!selectedCampaign) return moves;
        return moves.filter(m => m.campaignId === selectedCampaign);
    }, [moves, selectedCampaign]);

    // Calculate date ranges for different views
    const dateRange = useMemo(() => {
        switch (viewMode) {
            case "day":
                return { start: startOfDay(currentDate), end: endOfDay(currentDate) };
            case "week":
                return {
                    start: startOfWeek(currentDate, { weekStartsOn: 1 }),
                    end: endOfWeek(currentDate, { weekStartsOn: 1 })
                };
            case "month":
                const monthStart = startOfMonth(currentDate);
                const monthEnd = endOfMonth(currentDate);
                return {
                    start: startOfWeek(monthStart, { weekStartsOn: 1 }),
                    end: endOfWeek(monthEnd, { weekStartsOn: 1 })
                };
            case "agenda":
                return { start: currentDate, end: addDays(currentDate, 30) };
        }
    }, [viewMode, currentDate]);

    // Get moves visible in current range
    const visibleMoves = useMemo(() => {
        return filteredMoves.filter(move => {
            if (!move.startDate) return false;
            const start = new Date(move.startDate);
            const end = addDays(start, move.duration - 1);
            return end >= dateRange.start && start <= dateRange.end;
        }).sort((a, b) => new Date(a.startDate!).getTime() - new Date(b.startDate!).getTime());
    }, [filteredMoves, dateRange]);

    // Get days for current view
    const days = useMemo(() => {
        return eachDayOfInterval({ start: dateRange.start, end: dateRange.end });
    }, [dateRange]);

    // Navigation
    const navigate = (direction: 'prev' | 'next') => {
        const delta = direction === 'prev' ? -1 : 1;
        switch (viewMode) {
            case "day": setCurrentDate(d => addDays(d, delta)); break;
            case "week": setCurrentDate(d => addWeeks(d, delta)); break;
            case "month": setCurrentDate(d => direction === 'prev' ? subMonths(d, 1) : addMonths(d, 1)); break;
            case "agenda": setCurrentDate(d => addDays(d, delta * 7)); break;
        }
    };

    const goToToday = () => setCurrentDate(new Date());

    // Get moves for a specific day
    const getMovesForDay = (day: Date) => {
        return visibleMoves.filter(move => {
            if (!move.startDate) return false;
            const start = startOfDay(new Date(move.startDate));
            const end = endOfDay(addDays(start, move.duration - 1));
            return day >= start && day <= end;
        });
    };

    // Get status color
    const getStatusColor = (status: string, isBar = false) => {
        const colors = {
            active: isBar ? 'bg-[var(--ink)]' : 'bg-[var(--ink)] text-white',
            draft: isBar ? 'bg-[var(--muted)]' : 'bg-[var(--surface)] border border-[var(--border)]',
            completed: isBar ? 'bg-green-600' : 'bg-green-600 text-white',
            paused: isBar ? 'bg-amber-500' : 'bg-amber-500 text-white'
        };
        return colors[status as keyof typeof colors] || colors.draft;
    };

    // Upcoming moves for sidebar
    const upcomingMoves = useMemo(() => {
        const today = startOfDay(new Date());
        return filteredMoves
            .filter(m => m.startDate && new Date(m.startDate) >= today)
            .slice(0, 5);
    }, [filteredMoves]);

    // Mini calendar for sidebar
    const miniCalendarDays = useMemo(() => {
        const monthStart = startOfMonth(currentDate);
        const monthEnd = endOfMonth(currentDate);
        const start = startOfWeek(monthStart, { weekStartsOn: 1 });
        const end = endOfWeek(monthEnd, { weekStartsOn: 1 });
        return eachDayOfInterval({ start, end });
    }, [currentDate]);

    // View mode buttons
    const viewModes: { id: ViewMode; label: string; icon: React.ReactNode }[] = [
        { id: "day", label: "Day", icon: <Sun size={14} /> },
        { id: "week", label: "Week", icon: <CalendarDays size={14} /> },
        { id: "month", label: "Month", icon: <CalendarRange size={14} /> },
        { id: "agenda", label: "Agenda", icon: <List size={14} /> }
    ];

    return (
        <div className="h-[calc(100vh-220px)] flex border border-[var(--border)] rounded-[var(--radius-lg)] overflow-hidden bg-[var(--paper)]">
            {/* ═══════════════════════ SIDEBAR ═══════════════════════ */}
            <div className="w-72 border-r border-[var(--border)] bg-[var(--surface)] flex flex-col">
                {/* Mini Calendar */}
                <div className="p-4 border-b border-[var(--border)]">
                    <div className="flex items-center justify-between mb-3">
                        <h3 className="text-sm font-semibold text-[var(--ink)]">
                            {format(currentDate, 'MMMM yyyy')}
                        </h3>
                        <div className="flex gap-1">
                            <button onClick={() => setCurrentDate(d => subMonths(d, 1))} className="p-1 hover:bg-[var(--paper)] rounded">
                                <ChevronLeft size={14} className="text-[var(--muted)]" />
                            </button>
                            <button onClick={() => setCurrentDate(d => addMonths(d, 1))} className="p-1 hover:bg-[var(--paper)] rounded">
                                <ChevronRight size={14} className="text-[var(--muted)]" />
                            </button>
                        </div>
                    </div>

                    {/* Mini Grid */}
                    <div className="grid grid-cols-7 gap-0.5 text-center">
                        {['M', 'T', 'W', 'T', 'F', 'S', 'S'].map((d, i) => (
                            <div key={i} className="text-[9px] text-[var(--muted)] font-medium py-1">{d}</div>
                        ))}
                        {miniCalendarDays.map((day, i) => {
                            const hasMove = getMovesForDay(day).length > 0;
                            const isSelected = isSameDay(day, currentDate);
                            const isCurrent = isToday(day);
                            const isCurrentMonth = isSameMonth(day, currentDate);

                            return (
                                <button
                                    key={i}
                                    onClick={() => setCurrentDate(day)}
                                    className={cn(
                                        "w-7 h-7 text-[11px] rounded-full relative transition-all",
                                        !isCurrentMonth && "text-[var(--muted)]/40",
                                        isCurrentMonth && "text-[var(--ink)]",
                                        isSelected && "bg-[var(--ink)] text-white",
                                        isCurrent && !isSelected && "ring-1 ring-green-500 text-green-600 font-bold",
                                        !isSelected && "hover:bg-[var(--paper)]"
                                    )}
                                >
                                    {format(day, 'd')}
                                    {hasMove && !isSelected && (
                                        <span className="absolute bottom-0.5 left-1/2 -translate-x-1/2 w-1 h-1 rounded-full bg-[var(--ink)]" />
                                    )}
                                </button>
                            );
                        })}
                    </div>
                </div>

                {/* Quick Actions */}
                <div className="p-4 border-b border-[var(--border)]">
                    <button
                        onClick={onCreateMove}
                        className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-[var(--ink)] text-white rounded-[var(--radius)] hover:bg-[var(--ink)]/90 transition-all font-medium text-sm"
                    >
                        <Plus size={16} />
                        New Move
                    </button>
                </div>

                {/* Campaign Filter */}
                {campaigns.length > 0 && (
                    <div className="p-4 border-b border-[var(--border)]">
                        <div className="flex items-center gap-2 mb-3">
                            <Filter size={12} className="text-[var(--muted)]" />
                            <span className="text-xs font-semibold text-[var(--muted)] uppercase tracking-wider">Campaigns</span>
                        </div>
                        <div className="space-y-1">
                            <button
                                onClick={() => setSelectedCampaign(null)}
                                className={cn(
                                    "w-full text-left px-3 py-2 rounded-[var(--radius)] text-sm transition-colors",
                                    !selectedCampaign ? "bg-[var(--ink)] text-white" : "text-[var(--ink)] hover:bg-[var(--paper)]"
                                )}
                            >
                                All Campaigns
                            </button>
                            {campaigns.slice(0, 4).map(c => (
                                <button
                                    key={c}
                                    onClick={() => setSelectedCampaign(c)}
                                    className={cn(
                                        "w-full text-left px-3 py-2 rounded-[var(--radius)] text-sm transition-colors truncate",
                                        selectedCampaign === c ? "bg-[var(--ink)] text-white" : "text-[var(--ink)] hover:bg-[var(--paper)]"
                                    )}
                                >
                                    {c}
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {/* Upcoming Moves */}
                <div className="p-4 flex-1 overflow-y-auto">
                    <div className="flex items-center gap-2 mb-3">
                        <Clock size={12} className="text-[var(--muted)]" />
                        <span className="text-xs font-semibold text-[var(--muted)] uppercase tracking-wider">Upcoming</span>
                    </div>
                    <div className="space-y-2">
                        {upcomingMoves.length === 0 ? (
                            <p className="text-xs text-[var(--muted)] text-center py-4">No upcoming moves</p>
                        ) : (
                            upcomingMoves.map(move => (
                                <button
                                    key={move.id}
                                    onClick={() => onMoveClick?.(move)}
                                    className="w-full text-left p-3 rounded-[var(--radius)] border border-[var(--border)] bg-[var(--paper)] hover:border-[var(--ink)] transition-colors"
                                >
                                    <div className="flex items-center gap-2 mb-1">
                                        <span className={cn("w-2 h-2 rounded-full", getStatusColor(move.status, true))} />
                                        <span className="text-xs font-medium text-[var(--ink)] truncate">{move.name}</span>
                                    </div>
                                    <div className="text-[10px] text-[var(--muted)]">
                                        {move.startDate && format(new Date(move.startDate), 'MMM d')} · {move.duration}d
                                    </div>
                                </button>
                            ))
                        )}
                    </div>
                </div>
            </div>

            {/* ═══════════════════════ MAIN CONTENT ═══════════════════════ */}
            <div className="flex-1 flex flex-col">
                {/* Header */}
                <div className="h-14 px-5 flex items-center justify-between border-b border-[var(--border)] bg-[var(--paper)]">
                    <div className="flex items-center gap-4">
                        {/* Navigation */}
                        <div className="flex items-center gap-1">
                            <button onClick={() => navigate('prev')} className="p-2 hover:bg-[var(--surface)] rounded-[var(--radius)] border border-[var(--border)]">
                                <ChevronLeft size={16} className="text-[var(--ink)]" />
                            </button>
                            <button onClick={goToToday} className="px-3 py-1.5 text-xs font-medium text-[var(--ink)] hover:bg-[var(--surface)] rounded-[var(--radius)] border border-[var(--border)]">
                                Today
                            </button>
                            <button onClick={() => navigate('next')} className="p-2 hover:bg-[var(--surface)] rounded-[var(--radius)] border border-[var(--border)]">
                                <ChevronRight size={16} className="text-[var(--ink)]" />
                            </button>
                        </div>

                        {/* Current Range Title */}
                        <h2 className="font-serif text-lg text-[var(--ink)]">
                            {viewMode === 'day' && format(currentDate, 'EEEE, MMMM d, yyyy')}
                            {viewMode === 'week' && `${format(dateRange.start, 'MMM d')} – ${format(dateRange.end, 'MMM d, yyyy')}`}
                            {viewMode === 'month' && format(currentDate, 'MMMM yyyy')}
                            {viewMode === 'agenda' && `Next 30 days from ${format(currentDate, 'MMM d')}`}
                        </h2>
                    </div>

                    {/* View Mode Toggle */}
                    <div className="flex border border-[var(--border)] rounded-[var(--radius)] overflow-hidden">
                        {viewModes.map(v => (
                            <button
                                key={v.id}
                                onClick={() => setViewMode(v.id)}
                                className={cn(
                                    "flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium transition-colors",
                                    viewMode === v.id
                                        ? "bg-[var(--ink)] text-white"
                                        : "bg-[var(--paper)] text-[var(--muted)] hover:text-[var(--ink)]"
                                )}
                            >
                                {v.icon}
                                {v.label}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Content Area */}
                <div ref={contentRef} className="flex-1 overflow-auto">
                    {/* ═══════════════════ DAY VIEW ═══════════════════ */}
                    {viewMode === "day" && (
                        <div className="relative min-h-full">
                            {/* Time grid */}
                            <div className="absolute left-0 w-16 top-0 bottom-0 border-r border-[var(--border)] bg-[var(--surface)]">
                                {HOURS.filter(h => h >= WORK_HOURS.start && h <= WORK_HOURS.end).map(hour => (
                                    <div key={hour} className="h-16 flex items-start justify-end pr-3 pt-1">
                                        <span className="text-[10px] text-[var(--muted)]">
                                            {format(setHours(new Date(), hour), 'ha')}
                                        </span>
                                    </div>
                                ))}
                            </div>

                            {/* Day content */}
                            <div className="ml-16 relative">
                                {HOURS.filter(h => h >= WORK_HOURS.start && h <= WORK_HOURS.end).map(hour => (
                                    <div key={hour} className="h-16 border-b border-[var(--border)] hover:bg-[var(--surface)]/50 transition-colors" />
                                ))}

                                {/* Now line */}
                                {isToday(currentDate) && (
                                    <div
                                        ref={nowLineRef}
                                        className="absolute left-0 right-0 h-0.5 bg-red-500 z-20 pointer-events-none"
                                        style={{ top: '30%' }}
                                    >
                                        <span className="absolute -left-1 -top-1.5 w-3 h-3 rounded-full bg-red-500" />
                                    </div>
                                )}

                                {/* Moves for day */}
                                <div className="absolute inset-0 p-2 pointer-events-none">
                                    {getMovesForDay(currentDate).map((move, idx) => (
                                        <button
                                            key={move.id}
                                            onClick={() => onMoveClick?.(move)}
                                            className={cn(
                                                "absolute left-2 right-2 p-3 rounded-[var(--radius)] pointer-events-auto cursor-pointer transition-all hover:shadow-lg",
                                                getStatusColor(move.status)
                                            )}
                                            style={{ top: `${idx * 80 + 20}px`, minHeight: '60px' }}
                                        >
                                            <div className="flex items-center gap-2 mb-1">
                                                <Target size={12} />
                                                <span className="font-medium text-sm truncate">{move.name}</span>
                                            </div>
                                            <div className="text-xs opacity-80">{move.duration} day move</div>
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>
                    )}

                    {/* ═══════════════════ WEEK VIEW ═══════════════════ */}
                    {viewMode === "week" && (
                        <div className="h-full flex flex-col">
                            {/* Day headers */}
                            <div className="flex border-b border-[var(--border)] bg-[var(--surface)]">
                                <div className="w-16 shrink-0" />
                                {days.slice(0, 7).map((day, i) => (
                                    <div key={i} className="flex-1 py-3 text-center border-l border-[var(--border)] first:border-l-0">
                                        <div className="text-[10px] text-[var(--muted)] uppercase tracking-wider">{format(day, 'EEE')}</div>
                                        <div className={cn(
                                            "text-lg font-medium mt-0.5",
                                            isToday(day) ? "w-8 h-8 mx-auto rounded-full bg-green-600 text-white flex items-center justify-center" : "text-[var(--ink)]"
                                        )}>
                                            {format(day, 'd')}
                                        </div>
                                    </div>
                                ))}
                            </div>

                            {/* Time grid */}
                            <div className="flex-1 flex overflow-y-auto">
                                <div className="w-16 shrink-0 border-r border-[var(--border)] bg-[var(--surface)]">
                                    {HOURS.filter(h => h >= WORK_HOURS.start && h <= WORK_HOURS.end).map(hour => (
                                        <div key={hour} className="h-14 flex items-start justify-end pr-2 pt-1">
                                            <span className="text-[9px] text-[var(--muted)]">
                                                {format(setHours(new Date(), hour), 'ha')}
                                            </span>
                                        </div>
                                    ))}
                                </div>

                                {/* Day columns */}
                                <div className="flex-1 flex relative">
                                    {days.slice(0, 7).map((day, dayIdx) => (
                                        <div key={dayIdx} className="flex-1 border-l border-[var(--border)] first:border-l-0 relative">
                                            {HOURS.filter(h => h >= WORK_HOURS.start && h <= WORK_HOURS.end).map(hour => (
                                                <div key={hour} className="h-14 border-b border-[var(--border)] hover:bg-[var(--surface)]/30 transition-colors" />
                                            ))}

                                            {/* Moves for this day */}
                                            {getMovesForDay(day).slice(0, 3).map((move, moveIdx) => {
                                                const isStart = move.startDate && isSameDay(day, new Date(move.startDate));
                                                return (
                                                    <button
                                                        key={move.id}
                                                        onClick={() => onMoveClick?.(move)}
                                                        className={cn(
                                                            "absolute left-0.5 right-0.5 h-10 flex items-center px-2 text-xs font-medium rounded transition-all hover:shadow-md",
                                                            getStatusColor(move.status),
                                                            isStart ? "rounded-l" : "rounded-l-none border-l-0"
                                                        )}
                                                        style={{ top: `${moveIdx * 44 + 8}px` }}
                                                    >
                                                        {isStart && <span className="truncate">{move.name}</span>}
                                                    </button>
                                                );
                                            })}
                                        </div>
                                    ))}

                                    {/* Now line */}
                                    {days.slice(0, 7).some(d => isToday(d)) && (
                                        <div
                                            className="absolute h-0.5 bg-red-500 z-10 pointer-events-none"
                                            style={{
                                                left: `${(days.slice(0, 7).findIndex(d => isToday(d)) / 7) * 100}%`,
                                                width: `${100 / 7}%`,
                                                top: '30%'
                                            }}
                                        />
                                    )}
                                </div>
                            </div>
                        </div>
                    )}

                    {/* ═══════════════════ MONTH VIEW ═══════════════════ */}
                    {viewMode === "month" && (
                        <div className="h-full flex flex-col">
                            {/* Day headers */}
                            <div className="grid grid-cols-7 border-b border-[var(--border)] bg-[var(--surface)]">
                                {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map(d => (
                                    <div key={d} className="py-3 text-center text-[10px] text-[var(--muted)] uppercase tracking-wider font-semibold">{d}</div>
                                ))}
                            </div>

                            {/* Calendar grid */}
                            <div className="flex-1 grid grid-cols-7 auto-rows-fr">
                                {days.map((day, i) => {
                                    const dayMoves = getMovesForDay(day);
                                    const isCurrentMonth = isSameMonth(day, currentDate);

                                    return (
                                        <div
                                            key={i}
                                            className={cn(
                                                "border-b border-r border-[var(--border)] p-1.5 min-h-[100px] transition-colors",
                                                !isCurrentMonth && "bg-[var(--surface)]/50",
                                                isToday(day) && "bg-green-50"
                                            )}
                                        >
                                            <div className={cn(
                                                "text-xs font-medium mb-1 w-6 h-6 flex items-center justify-center rounded-full",
                                                !isCurrentMonth && "text-[var(--muted)]/40",
                                                isToday(day) && "bg-green-600 text-white",
                                                isCurrentMonth && !isToday(day) && "text-[var(--ink)]"
                                            )}>
                                                {format(day, 'd')}
                                            </div>

                                            <div className="space-y-0.5">
                                                {dayMoves.slice(0, 3).map(move => {
                                                    const isStart = move.startDate && isSameDay(day, new Date(move.startDate));
                                                    const isEnd = move.startDate && isSameDay(day, addDays(new Date(move.startDate), move.duration - 1));

                                                    return (
                                                        <button
                                                            key={move.id}
                                                            onClick={() => onMoveClick?.(move)}
                                                            className={cn(
                                                                "w-full h-5 flex items-center text-[9px] font-medium transition-all hover:brightness-110",
                                                                getStatusColor(move.status),
                                                                isStart && "rounded-l pl-1.5",
                                                                isEnd && "rounded-r pr-1.5",
                                                                isStart && isEnd && "rounded px-1.5"
                                                            )}
                                                        >
                                                            {isStart && <span className="truncate">{move.name}</span>}
                                                        </button>
                                                    );
                                                })}
                                                {dayMoves.length > 3 && (
                                                    <div className="text-[9px] text-[var(--muted)] pl-1.5">+{dayMoves.length - 3}</div>
                                                )}
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    )}

                    {/* ═══════════════════ AGENDA VIEW ═══════════════════ */}
                    {viewMode === "agenda" && (
                        <div className="max-w-2xl mx-auto py-6 px-4">
                            {visibleMoves.length === 0 ? (
                                <div className="text-center py-12">
                                    <CalendarIcon size={40} className="mx-auto mb-4 text-[var(--muted)]" />
                                    <h3 className="font-serif text-lg text-[var(--ink)] mb-2">No moves scheduled</h3>
                                    <p className="text-sm text-[var(--muted)]">Create a move to see it in your agenda</p>
                                </div>
                            ) : (
                                <div className="space-y-6">
                                    {/* Group moves by start date */}
                                    {visibleMoves.map(move => {
                                        const startDate = new Date(move.startDate!);
                                        const endDate = addDays(startDate, move.duration - 1);
                                        const category = MOVE_CATEGORIES[move.category];

                                        return (
                                            <div key={move.id} className="flex gap-4">
                                                {/* Date badge */}
                                                <div className="w-16 shrink-0 text-center">
                                                    <div className={cn(
                                                        "w-12 h-12 mx-auto rounded-[var(--radius)] flex flex-col items-center justify-center",
                                                        isToday(startDate) ? "bg-green-600 text-white" : "bg-[var(--surface)] border border-[var(--border)]"
                                                    )}>
                                                        <span className="text-[10px] uppercase">{format(startDate, 'MMM')}</span>
                                                        <span className="text-lg font-bold leading-none">{format(startDate, 'd')}</span>
                                                    </div>
                                                </div>

                                                {/* Move card */}
                                                <button
                                                    onClick={() => onMoveClick?.(move)}
                                                    className="flex-1 p-4 border border-[var(--border)] rounded-[var(--radius)] bg-[var(--paper)] hover:border-[var(--ink)] transition-all text-left group"
                                                >
                                                    <div className="flex items-start justify-between mb-2">
                                                        <div className="flex items-center gap-2">
                                                            <span className={cn("w-2.5 h-2.5 rounded-full", getStatusColor(move.status, true))} />
                                                            <h4 className="font-medium text-[var(--ink)] group-hover:text-[var(--ink)]">{move.name}</h4>
                                                        </div>
                                                        <span className={cn(
                                                            "px-2 py-0.5 text-[10px] font-medium rounded",
                                                            move.status === 'active' && "bg-green-100 text-green-700",
                                                            move.status === 'draft' && "bg-[var(--surface)] text-[var(--muted)]",
                                                            move.status === 'completed' && "bg-blue-100 text-blue-700"
                                                        )}>
                                                            {move.status}
                                                        </span>
                                                    </div>

                                                    <p className="text-sm text-[var(--muted)] mb-3 line-clamp-2">{move.goal}</p>

                                                    <div className="flex items-center gap-4 text-xs text-[var(--muted)]">
                                                        <span className="flex items-center gap-1">
                                                            <Clock size={12} />
                                                            {format(startDate, 'MMM d')} – {format(endDate, 'MMM d')}
                                                        </span>
                                                        <span className="flex items-center gap-1">
                                                            <Target size={12} />
                                                            {move.duration} days
                                                        </span>
                                                        {move.campaignId && (
                                                            <span className="flex items-center gap-1">
                                                                <Layers size={12} />
                                                                Campaign
                                                            </span>
                                                        )}
                                                    </div>
                                                </button>
                                            </div>
                                        );
                                    })}
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default MovesCalendarPro;
