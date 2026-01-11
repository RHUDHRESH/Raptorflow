"use client";

import { useRef, useEffect, useState, useMemo } from "react";
import gsap from "gsap";
import { Download, Zap, Activity, Target, Layers, ArrowUpRight, CheckCircle2, AlertTriangle, Lightbulb, TrendingUp, List, BarChart2, PieChart, Play, RefreshCw } from "lucide-react";
import dynamic from 'next/dynamic';
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { cn } from "@/lib/utils";
import { useMovesStore } from "@/stores/movesStore";
import { format, subDays, isAfter, parseISO } from "date-fns";

const BlueprintButton = dynamic(() => import("@/components/ui/BlueprintButton").then(mod => ({ default: mod.BlueprintButton })), { ssr: false });

export const runtime = 'edge';
import { StrategicInferenceEngine } from "@/lib/analytics/StrategicInferenceEngine";
import { StrategicRadar } from "@/components/analytics/StrategicRadar";

/* ══════════════════════════════════════════════════════════════════════════════
   ANALYTICS — Strategic Intelligence Dashboard
   "The Brain": Raptor Score, Gap Detection, and Next Best Action.
   ══════════════════════════════════════════════════════════════════════════════ */

const CATEGORY_COLORS: Record<string, string> = {
  capture: "var(--blueprint)",
  rally: "var(--success)",
  authority: "var(--ink)",
  pulse: "var(--warning)",
  deepen: "var(--ink-secondary)",
  repair: "var(--error)",
};

const CATEGORY_LABELS: Record<string, string> = {
  capture: "Growth / Capture",
  rally: "Retention / Rally",
  authority: "Brand / Authority",
  ignite: "Ignite",
  deepen: "Deepen",
  repair: "Repair",
};

export default function AnalyticsPage() {
  const pageRef = useRef<HTMLDivElement>(null);
  const [dateRange, setDateRange] = useState("30d");
  const [isRefreshing, setIsRefreshing] = useState(false);
  const { moves } = useMovesStore();

  const handleRefresh = async () => {
    setIsRefreshing(true);
    // Simulate data refresh
    await new Promise(resolve => setTimeout(resolve, 1000));
    setIsRefreshing(false);
  };

  useEffect(() => {
    if (!pageRef.current) return;
    gsap.fromTo(
      pageRef.current,
      { opacity: 0, y: 12 },
      { opacity: 1, y: 0, duration: 0.4, ease: "power2.out" }
    );
  }, []);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.ctrlKey || e.metaKey) {
        switch (e.key) {
          case 'r':
            e.preventDefault();
            handleRefresh();
            break;
          case 'e':
            e.preventDefault();
            // Trigger export
            const exportButton = document.querySelector('button[onclick*="csv"]');
            if (exportButton) (exportButton as HTMLButtonElement).click();
            break;
          case '1':
            e.preventDefault();
            setDateRange('7d');
            break;
          case '3':
            e.preventDefault();
            setDateRange('30d');
            break;
          case '9':
            e.preventDefault();
            setDateRange('90d');
            break;
        }
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [dateRange]);

  // --- STRATEGIC INFERENCE ---
  const { raptorScore, gaps, recommendation, channelMix, strategySplit, recentCompletions, categoryScores, statsRaw, activeMoves } = useMemo(() => {
    // Convert range string to days
    const daysMap: Record<string, number> = { "7d": 7, "30d": 30, "90d": 90 };
    const daysInRange = daysMap[dateRange] || 30;

    const engine = new StrategicInferenceEngine(moves, daysInRange);
    const raptorScore = engine.calculateRaptorScore();
    const categoryScores = engine.getCategoryScores(); // NEW
    const gaps = engine.detectGaps();
    const recommendation = engine.getNextBestAction(gaps);

    // --- Standard Stats Calculation (retained for charts) ---
    const now = new Date();
    const cutoff = subDays(now, daysInRange);
    const activeMoves = moves.filter(m => m.status === "active");
    const completedMoves = moves.filter(m =>
      m.status === "completed" && m.endDate && isAfter(parseISO(m.endDate), cutoff)
    );
    const allMovesInRange = moves.filter(m => isAfter(parseISO(m.createdAt), cutoff));

    // Task & Channel Logic
    let totalTasks = 0;
    const channelCounts: Record<string, number> = {};
    moves.forEach(move => {
      move.execution.forEach(day => {
        if (day.pillarTask.status === "done") {
          totalTasks++;
          const ch = day.pillarTask.channel || "General";
          channelCounts[ch] = (channelCounts[ch] || 0) + 1;
        }
        day.clusterActions.forEach(action => {
          if (action.status === "done") {
            totalTasks++;
            const ch = action.channel || "Social";
            channelCounts[ch] = (channelCounts[ch] || 0) + 1;
          }
        });
        // Check Network
        if (day.networkAction.status === "done") {
          totalTasks++;
          const ch = day.networkAction.channel || "Network";
          channelCounts[ch] = (channelCounts[ch] || 0) + 1;
        }
      });
    });

    const channelMix = Object.entries(channelCounts)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 5)
      .map(([name, count]) => ({ name, count, percent: Math.round((count / (totalTasks || 1)) * 100) }));

    const strategyCounts: Record<string, number> = {};
    allMovesInRange.forEach(m => { strategyCounts[m.category] = (strategyCounts[m.category] || 0) + 1; });
    const strategySplit = Object.entries(strategyCounts).map(([cat, count]) => ({
      category: cat,
      count,
      percent: Math.round((count / (allMovesInRange.length || 1)) * 100)
    }));

    return {
      raptorScore, gaps, recommendation, channelMix, strategySplit, categoryScores,
      activeMoves, // EXPORTED FOR UI
      recentCompletions: completedMoves.sort((a, b) => new Date(b.endDate!).getTime() - new Date(a.endDate!).getTime()),
      statsRaw: { velocity: completedMoves.length, active: activeMoves.length, tasks: totalTasks }
    };
  }, [moves, dateRange]);


  return (
    <div ref={pageRef} className="space-y-8 pb-12 opacity-0">
      {/* Header */}
      <div className="flex justify-between items-end">
        <div>
          <div className="align-center gap-3 mb-2">
            <span className="font-technical text-[var(--blueprint)]">SYS.ANALYTICS</span>
            <div className="h-px w-6 bg-[var(--structure)]" />
            <span className="font-technical text-[var(--ink-muted)]">INTELLIGENCE</span>
            <div className="ml-2 p-1 bg-[var(--blueprint)]/10 rounded-full cursor-help" title="Strategic Intelligence Dashboard - Analyze your marketing performance across all dimensions">
              <Lightbulb size={12} className="text-[var(--blueprint)]" />
            </div>
          </div>
          <h1 className="font-serif text-4xl text-[var(--ink)]">Strategic Intelligence</h1>
          <p className="text-[var(--ink-secondary)] mt-1">
            Analyzing your execution balance across the 5 dimensions.
          </p>
        </div>
        <div className="flex gap-3">
          <div className="flex bg-[var(--paper)] border border-[var(--structure)] rounded-[var(--radius)] overflow-hidden">
            {["7d", "30d", "90d"].map((range) => (
              <button
                key={range}
                onClick={() => setDateRange(range)}
                className={cn(
                  "px-4 py-2 text-xs font-medium transition-colors border-r border-[var(--structure)] last:border-r-0",
                  dateRange === range
                    ? "bg-[var(--ink)] text-[var(--paper)]"
                    : "bg-[var(--paper)] text-[var(--ink-muted)] hover:text-[var(--ink)]"
                )}
              >
                {range}
              </button>
            ))}
          </div>
          <BlueprintButton variant="ghost" size="sm" onClick={handleRefresh} disabled={isRefreshing}>
            <RefreshCw size={14} className={isRefreshing ? "animate-spin" : ""} />
            {isRefreshing ? "Refreshing..." : "Refresh"}
          </BlueprintButton>
        </div>
      </div>

      {/* --- HERO: RAPTOR SCORE --- */}
      <div className="mb-8">
        <RaptorScoreCard raptorScore={raptorScore} />
      </div>

      {/* --- QUICK STATS ROW --- */}
      <div className="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <KpiCard
          label="Active Moves"
          value={statsRaw.active}
          subValue="Currently running"
          icon={Activity}
          trend="neutral"
          onClick={() => window.location.href = '/moves'}
        />
        <KpiCard
          label="Completed"
          value={recentCompletions.length}
          subValue="Last 30 days"
          icon={CheckCircle2}
          trend="up"
          onClick={() => setDateRange('30d')}
        />
        <KpiCard
          label="Engagement Rate"
          value="87%"
          subValue="+5% vs last month"
          icon={TrendingUp}
          trend="up"
          onClick={() => setDateRange('90d')}
        />
        <KpiCard
          label="Strategic Health"
          value={raptorScore.total}
          subValue="Raptor Score"
          icon={Target}
          trend={raptorScore.total >= 80 ? "up" : "neutral"}
          onClick={() => console.log('Show Raptor Score details')}
        />
      </div>

      {/* --- ALERTS & GAPS --- */}
      {
        gaps.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {gaps.map((gap, i) => (
              <div key={i} className={cn(
                "flex items-start gap-3 p-4 rounded-[var(--radius)] border",
                gap.type === "critical"
                  ? "bg-red-50 border-red-200 text-red-900"
                  : gap.type === "warning"
                    ? "bg-amber-50 border-amber-200 text-amber-900"
                    : "bg-[var(--paper)] border-[var(--structure)]"
              )}>
                <AlertTriangle size={16} className="mt-0.5 shrink-0" />
                <div>
                  <span className="block text-xs font-bold uppercase tracking-wider mb-1">{gap.type} GAP</span>
                  <p className="text-sm font-medium">{gap.message}</p>
                </div>
              </div>
            ))}
          </div>
        )
      }


      {/* --- VISUAL INTELLIGENCE ROW --- */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 mb-8">
        {/* RADAR CHART: Strategic Shape */}
        <BlueprintCard className="h-full" padding="lg">
          <div className="align-between mb-4">
            <div className="align-center gap-2">
              <Target size={16} className="text-[var(--ink-muted)]" />
              <span className="font-technical text-[var(--ink-muted)]">STRATEGIC SHAPE</span>
            </div>
            <BlueprintButton variant="ghost" size="sm">
              <Layers size={14} /> Details
            </BlueprintButton>
          </div>
          <div className="h-64 flex items-center justify-center">
            <StrategicRadar scores={categoryScores} />
          </div>
          <div className="mt-4 text-center">
            <p className="text-xs text-[var(--ink-secondary)]">Balanced distribution across all strategic pillars</p>
          </div>
        </BlueprintCard>

        {/* CHANNEL MIX CHART */}
        <BlueprintCard className="h-full" padding="lg">
          <div className="align-between mb-4">
            <div className="align-center gap-2">
              <BarChart2 size={16} className="text-[var(--ink-muted)]" />
              <span className="font-technical text-[var(--ink-muted)]">CHANNEL PERFORMANCE</span>
            </div>
            <BlueprintButton variant="ghost" size="sm">
              <PieChart size={14} /> View All
            </BlueprintButton>
          </div>
          <div className="space-y-3">
            {channelMix.slice(0, 5).map((item) => (
              <div key={item.name} className="flex items-center justify-between">
                <span className="text-sm font-medium text-[var(--ink)]">{item.name}</span>
                <div className="flex items-center gap-2">
                  <div className="w-24 bg-[var(--surface)] rounded-full h-2">
                    <div
                      className="h-2 bg-[var(--blueprint)] rounded-full"
                      style={{ width: `${item.percent}%` }}
                    />
                  </div>
                  <span className="text-xs text-[var(--ink-secondary)] w-8 text-right">{item.count}</span>
                </div>
              </div>
            ))}
          </div>
        </BlueprintCard>
      </div>

      {/* The Ledger */}
      <div className="space-y-4 pt-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="p-2 bg-[var(--surface)] rounded-lg">
              <List size={24} className="text-[var(--ink)]" />
            </div>
            <div>
              <h2 className="font-serif text-2xl text-[var(--ink)]">Completion Ledger</h2>
              <p className="text-xs text-[var(--ink-secondary)]">Track record of execution</p>
            </div>
          </div>

          <div className="flex gap-4">
            <div className="flex gap-2">
              <span className="text-xs font-medium px-3 py-1.5 rounded-full bg-[var(--surface)] text-[var(--ink-secondary)] flex items-center gap-1">
                <CheckCircle2 size={12} />
                {recentCompletions.length} Completed
              </span>
              <span className="text-xs font-medium px-3 py-1.5 rounded-full bg-[var(--blueprint)]/10 text-[var(--blueprint)] flex items-center gap-1">
                <Play size={10} fill="currentColor" />
                {statsRaw.active} Active
              </span>
            </div>
            <BlueprintButton variant="ghost" size="sm" onClick={() => {
              const csvContent = "data:text/csv;charset=utf-8," +
                "Date,Move Name,Category,Result\n" +
                recentCompletions.map(m =>
                  `${m.endDate},${m.name},${m.category},COMPLETED`
                ).join("\n");
              const encodedUri = encodeURI(csvContent);
              const link = document.createElement("a");
              link.setAttribute("href", encodedUri);
              link.setAttribute("download", `analytics-${dateRange}.csv`);
              document.body.appendChild(link);
              link.click();
              document.body.removeChild(link);
            }}>
              <Download size={14} /> Export CSV
            </BlueprintButton>
          </div>
        </div>

        <div className="border border-[var(--structure)] rounded-[var(--radius)] overflow-hidden bg-[var(--paper)]">
          <table className="w-full text-left text-sm">
            <thead className="bg-[var(--surface)] border-b border-[var(--structure-subtle)]">
              <tr>
                <th className="px-6 py-4 font-technical text-[10px] text-[var(--ink-muted)] uppercase">Date</th>
                <th className="px-6 py-4 font-technical text-[10px] text-[var(--ink-muted)] uppercase">Move Name</th>
                <th className="px-6 py-4 font-technical text-[10px] text-[var(--ink-muted)] uppercase">Category</th>
                <th className="px-6 py-4 font-technical text-[10px] text-[var(--ink-muted)] uppercase text-right">Result</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--structure-subtle)]">
              {/* 1. Show Active Moves First (Context) */}
              {activeMoves.map((move) => (
                <tr key={move.id} className="hover:bg-[var(--surface)] transition-colors bg-[var(--surface)]/30">
                  <td className="px-6 py-4 font-data text-[var(--ink-secondary)]">
                    {move.createdAt ? format(parseISO(move.createdAt), "MMM dd") : "—"}
                  </td>
                  <td className="px-6 py-4 font-medium text-[var(--ink)] flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-[var(--blueprint)] animate-pulse" />
                    {move.name}
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className="inline-flex items-center px-2 py-1 rounded text-[10px] font-bold uppercase tracking-wider border"
                      style={{
                        color: CATEGORY_COLORS[move.category],
                        borderColor: CATEGORY_COLORS[move.category],
                        backgroundColor: "var(--paper)"
                      }}
                    >
                      {move.category}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <span className="text-[var(--blueprint)] font-bold text-xs uppercase">IN PROGRESS</span>
                  </td>
                </tr>
              ))}

              {recentCompletions.length > 0 ? (
                recentCompletions.map((move) => (
                  <tr key={move.id} className="hover:bg-[var(--surface)] transition-colors">
                    <td className="px-6 py-4 font-data text-[var(--ink-secondary)]">
                      {move.endDate ? format(parseISO(move.endDate), "MMM dd, yyyy") : "—"}
                    </td>
                    <td className="px-6 py-4 font-medium text-[var(--ink)]">
                      {move.name}
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className="inline-flex items-center px-2 py-1 rounded text-[10px] font-bold uppercase tracking-wider border"
                        style={{
                          color: CATEGORY_COLORS[move.category],
                          borderColor: CATEGORY_COLORS[move.category],
                          backgroundColor: "var(--paper)"
                        }}
                      >
                        {move.category}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <span className="text-[var(--success)] font-bold text-xs">COMPLETED</span>
                    </td>
                  </tr>
                ))
              ) : (
                activeMoves.length === 0 && (
                  <tr>
                    <td colSpan={4} className="px-6 py-8 text-center text-[var(--ink-muted)]">
                      No completed moves in this period. Start executing!
                    </td>
                  </tr>
                )
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div >
  );
}

// Helper Component for KPI
function KpiCard({ label, value, subValue, icon: Icon, trend, onClick }: {
  label: string,
  value: string | number,
  subValue: string,
  icon: any,
  trend: "up" | "down" | "neutral",
  onClick?: () => void
}) {
  return (
    <div
      className="bg-[var(--paper)] border border-[var(--structure)] rounded-[var(--radius)] p-6 hover:border-[var(--structure-strong)] transition-colors group cursor-pointer focus:outline-none focus:ring-2 focus:ring-[var(--blueprint)] focus:ring-offset-2"
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && onClick?.()}
    >
      <div className="align-start justify-between mb-4">
        <span className="font-technical text-[10px] text-[var(--ink-muted)] tracking-wider">{label}</span>
        <div className="p-2 bg-[var(--surface)] rounded-lg text-[var(--ink-muted)] group-hover:text-[var(--blueprint)] group-hover:bg-[var(--blueprint-light)] transition-colors" aria-hidden="true">
          <Icon size={16} />
        </div>
      </div>
      <div className="align-baseline gap-2">
        <span className="font-serif text-4xl text-[var(--ink)]" aria-label={`${label}: ${value}`}>{value}</span>
      </div>
      <div className="align-center gap-2 mt-2">
        {trend === "up" && <ArrowUpRight size={14} className="text-[var(--success)]" aria-hidden="true" />}
        <span className="text-xs text-[var(--ink-secondary)]">{subValue}</span>
      </div>
    </div>
  );
}

function RaptorScoreCard({ raptorScore }: { raptorScore: any }) {
  // Determine status color/icon
  const isOptimal = raptorScore.total >= 80;
  const isWarning = raptorScore.total >= 50 && raptorScore.total < 80;

  const scoreColor = isOptimal ? "text-[var(--success)]" : isWarning ? "text-[var(--warning)]" : "text-[var(--error)]";

  return (
    <div className="col-span-12 bg-[var(--paper)] border border-[var(--structure)] rounded-[var(--radius)] p-10 relative overflow-hidden">
      {/* Background Ambient Glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 p-[400px] bg-[var(--blueprint)]/5 rounded-full blur-[120px] pointer-events-none" />

      <div className="grid grid-cols-12 gap-12 relative z-10 items-center">

        {/* LEFT: The Big Score */}
        <div className="col-span-4 flex flex-col justify-center border-r border-[var(--structure-subtle)] pr-12">
          <span className="font-technical text-sm text-[var(--ink-muted)] tracking-[0.2em] font-bold uppercase mb-4">Strategic Health</span>
          <div className="flex items-baseline gap-4">
            <h2 className="font-serif text-8xl text-[var(--ink)] leading-none">
              {raptorScore.total}
            </h2>
            <span className="text-3xl text-[var(--ink-secondary)] font-light">/ 100</span>
          </div>

          <div className="mt-6 flex items-center gap-3">
            {isOptimal ? (
              <div className="flex items-center gap-2 text-[var(--success)] bg-[var(--success)]/10 px-4 py-2 rounded-full">
                <CheckCircle2 size={20} />
                <span className="font-bold text-sm tracking-wide uppercase">Optimal Execution</span>
              </div>
            ) : isWarning ? (
              <div className="flex items-center gap-2 text-[var(--warning)] bg-[var(--warning)]/10 px-4 py-2 rounded-full">
                <Activity size={20} />
                <span className="font-bold text-sm tracking-wide uppercase">Room for Growth</span>
              </div>
            ) : (
              <div className="flex items-center gap-2 text-[var(--error)] bg-[var(--error)]/10 px-4 py-2 rounded-full">
                <AlertTriangle size={20} />
                <span className="font-bold text-sm tracking-wide uppercase">Critical Action Needed</span>
              </div>
            )}
          </div>
        </div>

        {/* RIGHT: The Interactive Breakdown */}
        <div className="col-span-8 grid grid-cols-4 gap-6">
          <ScorePillarCard
            label="Velocity"
            score={raptorScore.velocityScore}
            weight="30%"
            desc="Weekly Output"
            target="Target: 1 Move/wk"
          />
          <ScorePillarCard
            label="Consistency"
            score={raptorScore.consistencyScore}
            weight="30%"
            desc="Daily Momentum"
            target="No stalled Moves"
          />
          <ScorePillarCard
            label="Variety"
            score={raptorScore.varietyScore}
            weight="20%"
            desc="Category Mix"
            target="Hit 2+ Categories"
          />
          <ScorePillarCard
            label="Focus"
            score={raptorScore.focusScore}
            weight="20%"
            desc="Strategic Depth"
            target="One Main Effort"
          />
        </div>
      </div>
    </div>
  );
}

function ScorePillarCard({ label, score, weight, desc, target }: { label: string, score: number, weight: string, desc: string, target: string }) {
  // Color scale for the bar
  const barColor = score >= 80 ? "bg-[var(--success)]" : score >= 50 ? "bg-[var(--warning)]" : "bg-[var(--error)]";

  return (
    <div className="group p-4 rounded-xl border border-[var(--structure-subtle)] bg-[var(--surface)] hover:border-[var(--blueprint)] transition-all duration-300 hover:shadow-lg cursor-default">
      <div className="flex justify-between items-center mb-3">
        <span className="font-technical text-[10px] bg-[var(--paper)] px-2 py-1 rounded border border-[var(--structure)] text-[var(--ink-secondary)]">{weight}</span>
        <span className={cn("font-bold text-xl", score >= 80 ? "text-[var(--success)]" : score >= 50 ? "text-[var(--warning)]" : "text-[var(--error)]")}>
          {score}
        </span>
      </div>

      {/* Bar Chart Visualization */}
      <div className="h-24 w-full bg-[var(--paper)] rounded-lg relative overflow-hidden mb-4 border border-[var(--structure-subtle)]">
        <div
          className={cn("absolute bottom-0 left-0 w-full transition-all duration-1000 opacity-80 group-hover:opacity-100", barColor)}
          style={{ height: `${score}%` }}
        />
      </div>

      <h4 className="font-bold text-[var(--ink)] text-sm mb-1">{label}</h4>
      <p className="text-[10px] text-[var(--ink-secondary)] uppercase tracking-wide font-medium">{desc}</p>
      <p className="text-[10px] text-[var(--ink-muted)] mt-2 italic border-t border-[var(--structure-subtle)] pt-2">
        {target}
      </p>
    </div>
  )
}
