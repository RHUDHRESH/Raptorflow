"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { 
  Target, 
  Zap, 
  TrendingUp, 
  CheckCircle2,
  ArrowRight,
  Lock,
  Unlock,
} from "lucide-react";

// Register GSAP plugins
if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}

interface DashboardContentProps {
  metrics: {
    activeMoves: number;
    campaignHealth: number;
    dailyWinRate: number;
    decisionsLogged: number;
  };
  moves: Array<{
    id: string;
    name: string;
    status: "active" | "completed" | "draft";
    progress: number;
    category: string;
  }>;
  wins: Array<{
    id: string;
    date: string;
    metric: string;
    value: string;
    moveId: string;
  }>;
}

export function DashboardContent({ metrics, moves, wins }: DashboardContentProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReducedMotion || !containerRef.current) return;

    const ctx = gsap.context(() => {
      gsap.from(".metric-card", {
        y: 30,
        opacity: 0,
        duration: 0.6,
        stagger: 0.08,
        ease: "power3.out",
      });

      gsap.from(".move-item", {
        x: -20,
        opacity: 0,
        duration: 0.5,
        stagger: 0.06,
        delay: 0.3,
        ease: "power2.out",
      });

      gsap.from(".daily-win-item", {
        y: 15,
        opacity: 0,
        duration: 0.4,
        stagger: 0.05,
        delay: 0.5,
        ease: "back.out(1.2)",
      });
    }, containerRef);

    return () => ctx.revert();
  }, []);

  const handleCardHover = (e: React.MouseEvent<HTMLDivElement>) => {
    gsap.to(e.currentTarget, {
      y: -4,
      scale: 1.01,
      duration: 0.25,
      ease: "power2.out",
    });
  };

  const handleCardLeave = (e: React.MouseEvent<HTMLDivElement>) => {
    gsap.to(e.currentTarget, {
      y: 0,
      scale: 1,
      duration: 0.25,
      ease: "power2.out",
    });
  };

  return (
    <div ref={containerRef} className="space-y-8">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          label="Active Moves"
          value={metrics.activeMoves}
          icon={Zap}
          trend="+2 this week"
          status="success"
          onHover={handleCardHover}
          onLeave={handleCardLeave}
        />
        <MetricCard
          label="Campaign Health"
          value={`${metrics.campaignHealth}%`}
          icon={Target}
          trend="On track"
          status="success"
          onHover={handleCardHover}
          onLeave={handleCardLeave}
        />
        <MetricCard
          label="Daily Win Rate"
          value={`${metrics.dailyWinRate}%`}
          icon={TrendingUp}
          trend="Above target"
          status="warning"
          onHover={handleCardHover}
          onLeave={handleCardLeave}
        />
        <MetricCard
          label="Decisions Logged"
          value={metrics.decisionsLogged}
          icon={CheckCircle2}
          trend="In Blackbox"
          status="info"
          onHover={handleCardHover}
          onLeave={handleCardLeave}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-[18px] font-bold text-[var(--ink-1)]">Active Moves</h2>
            <button className="text-[13px] font-medium text-[var(--ink-2)] hover:text-[var(--ink-1)] flex items-center gap-1 transition-colors">
              View All
              <ArrowRight size={14} />
            </button>
          </div>
          
          <div className="space-y-3">
            {moves.slice(0, 5).map((move) => (
              <MoveItem key={move.id} move={move} />
            ))}
          </div>
        </div>

        <div className="space-y-4">
          <h2 className="text-[18px] font-bold text-[var(--ink-1)]">Daily Wins</h2>
          <div className="space-y-3">
            {wins.slice(0, 5).map((win) => (
              <DailyWinItem key={win.id} win={win} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

interface MetricCardProps {
  label: string;
  value: string | number;
  icon: React.ElementType;
  trend: string;
  status: "success" | "warning" | "info" | "error";
  onHover: (e: React.MouseEvent<HTMLDivElement>) => void;
  onLeave: (e: React.MouseEvent<HTMLDivElement>) => void;
}

function MetricCard({ label, value, icon: Icon, trend, status, onHover, onLeave }: MetricCardProps) {
  const statusColors = {
    success: "bg-[var(--status-success)]/10 text-[var(--status-success)]",
    warning: "bg-[var(--status-warning)]/10 text-[var(--status-warning)]",
    info: "bg-[var(--status-info)]/10 text-[var(--status-info)]",
    error: "bg-red-100 text-red-700",
  };

  return (
    <div
      className="metric-card p-5 rounded-[var(--radius-md)] bg-[var(--bg-surface)] border border-[var(--border-1)] cursor-pointer will-change-transform"
      onMouseEnter={onHover}
      onMouseLeave={onLeave}
    >
      <div className="flex items-start justify-between mb-3">
        <span className="text-[12px] font-mono text-[var(--ink-3)] tracking-wider">
          {label.toUpperCase()}
        </span>
        <div className={`p-2 rounded-[var(--radius-sm)] ${statusColors[status]}`}>
          <Icon size={16} />
        </div>
      </div>
      <div className="text-[32px] font-bold text-[var(--ink-1)] leading-none mb-1">
        {value}
      </div>
      <span className={`text-[11px] font-medium ${statusColors[status].split(" ")[1]}`}>
        {trend}
      </span>
    </div>
  );
}

interface MoveItemProps {
  move: {
    id: string;
    name: string;
    status: "active" | "completed" | "draft";
    progress: number;
    category: string;
  };
}

function MoveItem({ move }: MoveItemProps) {
  const statusConfig = {
    active: { icon: Zap, color: "text-[var(--status-success)]", bg: "bg-[var(--status-success)]" },
    completed: { icon: CheckCircle2, color: "text-[var(--ink-3)]", bg: "bg-[var(--ink-3)]" },
    draft: { icon: Unlock, color: "text-[var(--status-warning)]", bg: "bg-[var(--status-warning)]" },
  };

  const config = statusConfig[move.status];
  const Icon = config.icon;

  return (
    <div className="move-item group flex items-center gap-4 p-4 rounded-[var(--radius-md)] bg-[var(--bg-surface)] border border-[var(--border-1)] hover:border-[var(--border-2)] transition-colors cursor-pointer">
      <div className={`p-2 rounded-[var(--radius-sm)] bg-[var(--bg-canvas)] ${config.color}`}>
        <Icon size={18} />
      </div>
      
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-[14px] font-semibold text-[var(--ink-1)] truncate">
            {move.name}
          </span>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-[var(--bg-canvas)] text-[var(--ink-3)]">
            {move.category}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex-1 h-1.5 bg-[var(--border-1)] rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full ${config.bg}`}
              style={{ width: `${move.progress}%` }}
            />
          </div>
          <span className="text-[11px] font-mono text-[var(--ink-3)] w-8 text-right">
            {move.progress}%
          </span>
        </div>
      </div>

      {move.status === "draft" && (
        <button className="opacity-0 group-hover:opacity-100 transition-opacity p-2 rounded-[var(--radius-sm)] hover:bg-[var(--bg-canvas)] text-[var(--ink-3)]">
          <Lock size={16} />
        </button>
      )}
    </div>
  );
}

interface DailyWinItemProps {
  win: {
    id: string;
    date: string;
    metric: string;
    value: string;
    moveId: string;
  };
}

function DailyWinItem({ win }: DailyWinItemProps) {
  return (
    <div className="daily-win-item flex items-start gap-3 p-3 rounded-[var(--radius-sm)] bg-[var(--bg-surface)] border border-[var(--border-1)] hover:border-[var(--border-2)] transition-colors cursor-pointer group">
      <div className="w-8 h-8 rounded-full bg-[var(--rf-charcoal)] text-[var(--rf-ivory)] flex items-center justify-center flex-shrink-0 text-[11px] font-bold">
        {new Date(win.date).getDate()}
      </div>
      <div className="flex-1 min-w-0">
        <div className="text-[13px] font-medium text-[var(--ink-1)] group-hover:text-[var(--rf-charcoal)] transition-colors">
          {win.metric}
        </div>
        <div className="text-[12px] text-[var(--ink-2)]">
          {win.value}
        </div>
      </div>
      <ArrowRight 
        size={14} 
        className="text-[var(--ink-3)] opacity-0 group-hover:opacity-100 transition-opacity self-center" 
      />
    </div>
  );
}
