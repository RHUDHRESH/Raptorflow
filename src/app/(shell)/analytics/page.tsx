"use client";

import { useRef, useEffect, useMemo, useState } from "react";
import gsap from "gsap";
import { Activity, Target, TrendingUp, Zap, Download, RefreshCw } from "lucide-react";
import { BlueprintButton } from "@/components/ui/BlueprintButton";
import { cn } from "@/lib/utils";
import { useMovesStore } from "@/stores/movesStore";
import { format, subDays, isAfter, parseISO } from "date-fns";

/* ══════════════════════════════════════════════════════════════════════════════
   ANALYTICS — Strategic Performance Overview
   Quiet Luxury: Clean metrics, minimal charts, editorial clarity.
   ══════════════════════════════════════════════════════════════════════════════ */

export default function AnalyticsPage() {
  const pageRef = useRef<HTMLDivElement>(null);
  const [dateRange, setDateRange] = useState<"7d" | "30d" | "90d">("30d");
  const { moves } = useMovesStore();

  // Calculate analytics data
  const analytics = useMemo(() => {
    const daysMap = { "7d": 7, "30d": 30, "90d": 90 };
    const days = daysMap[dateRange];
    const cutoff = subDays(new Date(), days);

    const activeMoves = moves.filter((m) => m.status === "active");
    const completedMoves = moves.filter(
      (m) => m.status === "completed" && m.endDate && isAfter(parseISO(m.endDate), cutoff)
    );

    // Category distribution
    const categoryCount: Record<string, number> = {};
    moves.forEach((m) => {
      if (isAfter(parseISO(m.createdAt), cutoff)) {
        categoryCount[m.category] = (categoryCount[m.category] || 0) + 1;
      }
    });

    // Calculate completion rate
    const totalMoves = activeMoves.length + completedMoves.length;
    const completionRate = totalMoves > 0 ? Math.round((completedMoves.length / totalMoves) * 100) : 0;

    // Velocity (moves completed per week)
    const weeksInRange = days / 7;
    const velocity = weeksInRange > 0 ? (completedMoves.length / weeksInRange).toFixed(1) : "0";

    return {
      activeMoves: activeMoves.length,
      completedMoves: completedMoves.length,
      completionRate,
      velocity,
      categoryCount,
      recentCompletions: completedMoves.slice(0, 5),
    };
  }, [moves, dateRange]);

  // Entrance animation
  useEffect(() => {
    if (!pageRef.current) return;
    gsap.fromTo(
      "[data-fade]",
      { opacity: 0, y: 12 },
      { opacity: 1, y: 0, duration: 0.5, stagger: 0.08, ease: "power2.out" }
    );
  }, []);

  return (
    <div ref={pageRef} className="min-h-screen bg-[var(--canvas)] pb-16">
      <div className="max-w-[1200px] mx-auto px-6 lg:px-12 pt-8">
        {/* Header */}
        <header data-fade className="pb-8 border-b border-[var(--border)]">
          <div className="flex items-center gap-3 mb-6">
            <span className="font-technical text-[var(--ink-secondary)] uppercase">
              Analytics
            </span>
            <div className="h-px w-8 bg-[var(--border)]" />
            <span className="font-technical text-[var(--ink-muted)]">
              Strategic Performance
            </span>
          </div>

          <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
            <h1 className="font-serif text-4xl text-[var(--ink)]">
              Performance Overview
            </h1>

            {/* Date range selector */}
            <div className="flex items-center gap-2">
              {(["7d", "30d", "90d"] as const).map((range) => (
                <button
                  key={range}
                  onClick={() => setDateRange(range)}
                  className={cn(
                    "px-4 py-2 text-xs font-mono uppercase tracking-wide rounded-[var(--radius)] border transition-colors",
                    dateRange === range
                      ? "bg-[var(--ink)] text-[var(--paper)] border-[var(--ink)]"
                      : "bg-[var(--paper)] text-[var(--ink-muted)] border-[var(--border)] hover:border-[var(--ink-secondary)]"
                  )}
                >
                  {range}
                </button>
              ))}
            </div>
          </div>
        </header>

        {/* Metrics Grid */}
        <div data-fade className="grid grid-cols-2 lg:grid-cols-4 gap-4 mt-10">
          <MetricCard
            label="Active Moves"
            value={analytics.activeMoves}
            icon={Zap}
          />
          <MetricCard
            label="Completed"
            value={analytics.completedMoves}
            subtext={`in ${dateRange}`}
            icon={Target}
          />
          <MetricCard
            label="Completion Rate"
            value={`${analytics.completionRate}%`}
            icon={TrendingUp}
          />
          <MetricCard
            label="Velocity"
            value={analytics.velocity}
            subtext="per week"
            icon={Activity}
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-12">
          {/* Category Distribution */}
          <section data-fade className="space-y-4">
            <div className="flex items-center gap-3">
              <span className="font-technical text-[var(--blueprint)]">01</span>
              <div className="h-px flex-1 bg-[var(--border)]" />
              <span className="font-technical text-[var(--ink-muted)]">
                CATEGORY MIX
              </span>
            </div>

            <div className="bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-lg)] p-6">
              {Object.entries(analytics.categoryCount).length > 0 ? (
                <div className="space-y-4">
                  {Object.entries(analytics.categoryCount)
                    .sort(([, a], [, b]) => b - a)
                    .map(([category, count]) => {
                      const total = Object.values(analytics.categoryCount).reduce(
                        (sum, c) => sum + c,
                        0
                      );
                      const percent = Math.round((count / total) * 100);
                      return (
                        <div key={category} className="space-y-2">
                          <div className="flex justify-between text-sm">
                            <span className="font-medium text-[var(--ink)] capitalize">
                              {category}
                            </span>
                            <span className="text-[var(--ink-muted)]">
                              {count} ({percent}%)
                            </span>
                          </div>
                          <div className="h-2 bg-[var(--surface)] rounded-full overflow-hidden">
                            <div
                              className="h-full bg-[var(--blueprint)] rounded-full transition-all duration-500"
                              style={{ width: `${percent}%` }}
                            />
                          </div>
                        </div>
                      );
                    })}
                </div>
              ) : (
                <p className="text-center text-[var(--ink-muted)] py-8">
                  No moves in this period.
                </p>
              )}
            </div>
          </section>

          {/* Recent Completions */}
          <section data-fade className="space-y-4">
            <div className="flex items-center gap-3">
              <span className="font-technical text-[var(--blueprint)]">02</span>
              <div className="h-px flex-1 bg-[var(--border)]" />
              <span className="font-technical text-[var(--ink-muted)]">
                COMPLETION LEDGER
              </span>
            </div>

            <div className="bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-lg)] overflow-hidden">
              {analytics.recentCompletions.length > 0 ? (
                <div className="divide-y divide-[var(--border)]">
                  {analytics.recentCompletions.map((move) => (
                    <div
                      key={move.id}
                      className="flex items-center justify-between p-4 hover:bg-[var(--surface)] transition-colors"
                    >
                      <div>
                        <p className="text-sm font-medium text-[var(--ink)]">
                          {move.name}
                        </p>
                        <p className="text-xs text-[var(--ink-muted)] capitalize">
                          {move.category}
                        </p>
                      </div>
                      <div className="text-right">
                        <span className="text-xs font-mono text-[var(--success)]">
                          COMPLETED
                        </span>
                        <p className="text-xs text-[var(--ink-muted)]">
                          {move.endDate
                            ? format(parseISO(move.endDate), "MMM d")
                            : "-"}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center text-[var(--ink-muted)] py-8">
                  No completed moves yet.
                </p>
              )}
            </div>

            {/* Export button */}
            <div className="flex justify-end pt-2">
              <BlueprintButton
                variant="secondary"
                size="sm"
                onClick={() => {
                  const csv =
                    "Date,Move,Category,Status\n" +
                    analytics.recentCompletions
                      .map(
                        (m) =>
                          `${m.endDate || ""},${m.name},${m.category},COMPLETED`
                      )
                      .join("\n");
                  const blob = new Blob([csv], { type: "text/csv" });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement("a");
                  a.href = url;
                  a.download = `analytics-${dateRange}.csv`;
                  a.click();
                }}
              >
                <Download size={14} className="mr-2" />
                Export CSV
              </BlueprintButton>
            </div>
          </section>
        </div>

        {/* Footer */}
        <div
          data-fade
          className="mt-16 text-center text-[10px] font-mono text-[var(--ink-muted)] uppercase tracking-widest"
        >
          RaptorFlow Analytics • Updated {format(new Date(), "MMM d, yyyy")}
        </div>
      </div>
    </div>
  );
}

// Simple metric card component
function MetricCard({
  label,
  value,
  subtext,
  icon: Icon,
}: {
  label: string;
  value: string | number;
  subtext?: string;
  icon: React.ElementType;
}) {
  return (
    <div className="bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-lg)] p-5 hover:border-[var(--ink-secondary)] transition-colors">
      <div className="flex items-center justify-between mb-3">
        <span className="text-[11px] font-mono text-[var(--ink-muted)] uppercase tracking-wider">
          {label}
        </span>
        <Icon size={14} className="text-[var(--ink-muted)]" />
      </div>
      <div className="text-2xl font-serif text-[var(--ink)]">{value}</div>
      {subtext && (
        <p className="text-xs text-[var(--ink-muted)] mt-1">{subtext}</p>
      )}
    </div>
  );
}
