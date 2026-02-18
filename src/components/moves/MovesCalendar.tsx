"use client";

import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { ChevronLeft, ChevronRight, Calendar as CalendarIcon } from "lucide-react";

/* ═══════════════════════════════════════════════════════════════════════════════
   MOVES CALENDAR — Quiet Luxury Timeline
   Month/Week views with GSAP animations
   ═══════════════════════════════════════════════════════════════════════════════ */

export interface CalendarMove {
  id: string;
  title: string;
  startDate: Date;
  endDate: Date;
  status: "draft" | "active" | "completed" | "paused";
  category: "growth" | "retention" | "positioning" | "conversion";
  color?: string;
}

interface MovesCalendarProps {
  moves: CalendarMove[];
  onMoveClick?: (moveId: string) => void;
  onDateClick?: (date: Date) => void;
}

type ViewMode = "month" | "week";

// Category colors mapped to design system
const CATEGORY_COLORS: Record<string, string> = {
  growth: "#2A2529",      // Charcoal
  retention: "#5C565B",   // Muted ink
  positioning: "#D2CCC0", // Border-2
  conversion: "#847C82",  // Soft accent
};

export function MovesCalendar({ moves, onMoveClick, onDateClick }: MovesCalendarProps) {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [viewMode, setViewMode] = useState<ViewMode>("month");
  const [direction, setDirection] = useState<"left" | "right">("right");
  
  const gridRef = useRef<HTMLDivElement>(null);
  const headerRef = useRef<HTMLDivElement>(null);
  const moveBarsRef = useRef<(HTMLButtonElement | null)[]>([]);

  const today = new Date();

  // Calendar calculations
  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();
  
  const firstDayOfMonth = new Date(year, month, 1);
  const lastDayOfMonth = new Date(year, month + 1, 0);
  const daysInMonth = lastDayOfMonth.getDate();
  const startDayOfWeek = firstDayOfMonth.getDay(); // 0 = Sunday

  // Generate calendar days
  const calendarDays = Array.from({ length: 42 }, (_, i) => {
    const dayOffset = i - startDayOfWeek;
    return new Date(year, month, dayOffset + 1);
  });

  // Get moves for a specific day
  const getMovesForDay = (date: Date) => {
    return moves.filter((move) => {
      const moveStart = new Date(move.startDate);
      const moveEnd = new Date(move.endDate);
      // Normalize to start of day for comparison
      const checkDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());
      const startNormalized = new Date(moveStart.getFullYear(), moveStart.getMonth(), moveStart.getDate());
      const endNormalized = new Date(moveEnd.getFullYear(), moveEnd.getMonth(), moveEnd.getDate());
      
      return checkDate >= startNormalized && checkDate <= endNormalized;
    });
  };

  // Check if date is today
  const isToday = (date: Date) => {
    return (
      date.getDate() === today.getDate() &&
      date.getMonth() === today.getMonth() &&
      date.getFullYear() === today.getFullYear()
    );
  };

  // Check if date is in current month
  const isCurrentMonth = (date: Date) => {
    return date.getMonth() === month;
  };

  // Navigation handlers
  const navigateMonth = (dir: "prev" | "next") => {
    setDirection(dir === "next" ? "right" : "left");
    setCurrentDate((prev) => {
      const newDate = new Date(prev);
      if (viewMode === "month") {
        newDate.setMonth(prev.getMonth() + (dir === "next" ? 1 : -1));
      } else {
        newDate.setDate(prev.getDate() + (dir === "next" ? 7 : -7));
      }
      return newDate;
    });
  };

  const goToToday = () => {
    setDirection(currentDate > today ? "left" : "right");
    setCurrentDate(new Date());
  };

  // GSAP: Month transition animation
  useEffect(() => {
    if (!gridRef.current) return;

    const ctx = gsap.context(() => {
      gsap.fromTo(
        gridRef.current,
        { x: direction === "right" ? 30 : -30, opacity: 0 },
        { x: 0, opacity: 1, duration: 0.4, ease: "power2.out" }
      );
    });

    return () => ctx.revert();
  }, [currentDate, direction, viewMode]);

  // GSAP: Move bars stagger entrance
  useEffect(() => {
    if (moveBarsRef.current.length === 0) return;

    const validBars = moveBarsRef.current.filter(Boolean);
    if (validBars.length === 0) return;

    const ctx = gsap.context(() => {
      gsap.fromTo(
        validBars,
        { scaleX: 0, opacity: 0 },
        {
          scaleX: 1,
          opacity: 1,
          duration: 0.3,
          stagger: 0.03,
          ease: "power2.out",
          delay: 0.2,
        }
      );
    });

    return () => ctx.revert();
  }, [currentDate, moves, viewMode]);

  // Move bar hover animation
  const handleMoveBarEnter = (e: React.MouseEvent<HTMLButtonElement>) => {
    gsap.to(e.currentTarget, {
      y: -2,
      boxShadow: "0 4px 12px rgba(42, 37, 41, 0.15)",
      duration: 0.2,
      ease: "power2.out",
    });
  };

  const handleMoveBarLeave = (e: React.MouseEvent<HTMLButtonElement>) => {
    gsap.to(e.currentTarget, {
      y: 0,
      boxShadow: "0 1px 3px rgba(42, 37, 41, 0.08)",
      duration: 0.2,
      ease: "power2.out",
    });
  };

  // Day cell hover animation
  const handleDayEnter = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!isCurrentMonth(new Date(year, month, parseInt(e.currentTarget.dataset.day || "0")))) return;
    gsap.to(e.currentTarget, {
      backgroundColor: "rgba(243, 240, 231, 0.5)",
      duration: 0.2,
    });
  };

  const handleDayLeave = (e: React.MouseEvent<HTMLDivElement>) => {
    gsap.to(e.currentTarget, {
      backgroundColor: "transparent",
      duration: 0.2,
    });
  };

  const weekDays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  const monthName = currentDate.toLocaleDateString("en-US", { month: "long", year: "numeric" });

  // Reset move bars ref array on re-render
  moveBarsRef.current = [];

  return (
    <div className="w-full">
      {/* Header */}
      <div ref={headerRef} className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-[#F7F5EF] border border-[#E3DED3] rounded-[10px] flex items-center justify-center">
            <CalendarIcon size={18} className="text-[#2A2529]" />
          </div>
          <div>
            <h3 className="text-[20px] font-semibold text-[#2A2529] font-['DM_Sans',system-ui,sans-serif]">
              {monthName}
            </h3>
            <p className="text-[12px] text-[#847C82] font-['DM_Sans',system-ui,sans-serif]">
              {moves.length} moves scheduled
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* View Toggle */}
          <div className="flex border border-[#D2CCC0] rounded-[10px] overflow-hidden">
            <button
              onClick={() => setViewMode("month")}
              className={`px-3 py-1.5 text-[13px] font-medium transition-colors ${
                viewMode === "month"
                  ? "bg-[#2A2529] text-[#F3F0E7]"
                  : "bg-[#F7F5EF] text-[#5C565B] hover:text-[#2A2529]"
              }`}
            >
              Month
            </button>
            <button
              onClick={() => setViewMode("week")}
              className={`px-3 py-1.5 text-[13px] font-medium transition-colors ${
                viewMode === "week"
                  ? "bg-[#2A2529] text-[#F3F0E7]"
                  : "bg-[#F7F5EF] text-[#5C565B] hover:text-[#2A2529]"
              }`}
            >
              Week
            </button>
          </div>

          {/* Navigation */}
          <div className="flex items-center gap-1">
            <button
              onClick={() => navigateMonth("prev")}
              className="p-2 hover:bg-[#F3F0E7] rounded-[10px] transition-colors border border-[#E3DED3]"
              aria-label="Previous month"
            >
              <ChevronLeft size={18} className="text-[#2A2529]" />
            </button>
            <button
              onClick={goToToday}
              className="px-3 py-1.5 text-[13px] font-medium text-[#2A2529] hover:bg-[#F3F0E7] rounded-[10px] transition-colors border border-[#E3DED3]"
            >
              Today
            </button>
            <button
              onClick={() => navigateMonth("next")}
              className="p-2 hover:bg-[#F3F0E7] rounded-[10px] transition-colors border border-[#E3DED3]"
              aria-label="Next month"
            >
              <ChevronRight size={18} className="text-[#2A2529]" />
            </button>
          </div>
        </div>
      </div>

      {/* Calendar Grid */}
      <div className="border border-[#E3DED3] rounded-[14px] overflow-hidden bg-[#F7F5EF]">
        {/* Weekday Headers */}
        <div className="grid grid-cols-7 bg-[#EFEDE6] border-b border-[#E3DED3]">
          {weekDays.map((day) => (
            <div
              key={day}
              className="py-3 text-center text-[11px] font-semibold text-[#5C565B] uppercase tracking-wider font-['JetBrains_Mono',monospace]"
            >
              {day}
            </div>
          ))}
        </div>

        {/* Days Grid */}
        <div ref={gridRef} className="grid grid-cols-7">
          {calendarDays.map((date, index) => {
            const dayMoves = getMovesForDay(date);
            const dayIsToday = isToday(date);
            const dayIsCurrentMonth = isCurrentMonth(date);
            const dayNumber = date.getDate();

            return (
              <div
                key={index}
                data-day={dayNumber}
                onClick={() => dayIsCurrentMonth && onDateClick?.(date)}
                onMouseEnter={handleDayEnter}
                onMouseLeave={handleDayLeave}
                className={`
                  min-h-[100px] p-2 border-r border-b border-[#E3DED3] last:border-r-0
                  ${!dayIsCurrentMonth ? "bg-[#EFEDE6]/50" : "bg-[#F7F5EF]"}
                  ${dayIsToday ? "bg-[#F3F0E7]" : ""}
                  ${dayMoves.length > 0 && dayIsCurrentMonth ? "cursor-pointer" : ""}
                  transition-colors
                `}
              >
                {/* Day Number */}
                <div className="flex items-center justify-between mb-1">
                  <span
                    className={`
                      text-[13px] font-medium w-7 h-7 flex items-center justify-center rounded-full
                      ${dayIsToday 
                        ? "bg-[#2A2529] text-[#F3F0E7] font-semibold" 
                        : dayIsCurrentMonth 
                          ? "text-[#2A2529]" 
                          : "text-[#D2CCC0]"
                      }
                      font-['DM_Sans',system-ui,sans-serif]
                    `}
                  >
                    {dayNumber}
                  </span>
                  {dayIsToday && (
                    <span className="w-1.5 h-1.5 rounded-full bg-[#2A2529]" />
                  )}
                </div>

                {/* Move Bars */}
                <div className="space-y-1 mt-2">
                  {dayMoves.slice(0, 3).map((move, moveIndex) => {
                    const isStartDay = 
                      date.getDate() === new Date(move.startDate).getDate() &&
                      date.getMonth() === new Date(move.startDate).getMonth();
                    
                    return (
                      <button
                        key={move.id}
                        ref={(el) => {
                          moveBarsRef.current.push(el);
                        }}
                        onClick={(e) => {
                          e.stopPropagation();
                          onMoveClick?.(move.id);
                        }}
                        onMouseEnter={handleMoveBarEnter}
                        onMouseLeave={handleMoveBarLeave}
                        className={`
                          w-full h-[24px] flex items-center px-2 rounded-[4px] text-left
                          origin-left
                          ${move.category === "positioning" ? "text-[#2A2529]" : "text-white"}
                        `}
                        style={{
                          backgroundColor: move.color || CATEGORY_COLORS[move.category] || "#2A2529",
                          boxShadow: "0 1px 3px rgba(42, 37, 41, 0.08)",
                        }}
                      >
                        {isStartDay && (
                          <span className="text-[10px] font-medium font-['JetBrains_Mono',monospace] truncate">
                            {move.title}
                          </span>
                        )}
                      </button>
                    );
                  })}
                  {dayMoves.length > 3 && (
                    <div className="text-[10px] text-[#847C82] font-['JetBrains_Mono',monospace] pl-1">
                      +{dayMoves.length - 3} more
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Empty State */}
      {moves.length === 0 && (
        <div className="py-16 text-center border border-dashed border-[#D2CCC0] rounded-[14px] mt-6">
          <CalendarIcon size={40} className="mx-auto mb-3 text-[#D2CCC0]" />
          <h4 className="text-[16px] font-semibold text-[#2A2529] mb-1 font-['DM_Sans',system-ui,sans-serif]">
            No moves scheduled
          </h4>
          <p className="text-[14px] text-[#847C82] mb-4 font-['DM_Sans',system-ui,sans-serif]">
            Create your first move to see it on the calendar
          </p>
          <button className="px-4 py-2 bg-[#2A2529] text-[#F3F0E7] rounded-[10px] text-[14px] font-medium hover:bg-[#3D383C] transition-colors">
            Create Move
          </button>
        </div>
      )}
    </div>
  );
}

export default MovesCalendar;
