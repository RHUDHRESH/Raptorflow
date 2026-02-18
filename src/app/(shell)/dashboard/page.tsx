"use client";

import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { Layout } from "@/components/raptor/shell/Layout";
import { Card } from "@/components/raptor/ui/Card";
import { Button } from "@/components/raptor/ui/Button";
import { Badge } from "@/components/raptor/ui/Badge";
import { Tag } from "@/components/raptor/ui/Tag";
import { Progress } from "@/components/raptor/ui/Progress";

// Types
interface Win {
  id: string;
  title: string;
  description: string;
  impact: "high" | "medium" | "low";
  completed: boolean;
  category: "foundation" | "move" | "campaign" | "analysis";
}

interface Metric {
  label: string;
  value: number;
  trend: number;
  icon: React.ReactNode;
}

// Mock Data
const mockData = {
  company: "Acme Corp",
  valueProp: "AI-powered workflow automation for enterprise teams",
  mode: "draft" as const,
  moves: {
    active: 2,
    total: 5,
  },
  campaigns: {
    active: 1,
    total: 3,
  },
  icps: 3,
  channels: 4,
  foundation: {
    positioning: true,
    icps: true,
    messaging: false,
  },
  dailyWin: {
    id: "win-1",
    title: "Lock your Positioning",
    description: "Your value proposition is 90% complete. Lock it to enable campaign generation.",
    impact: "high" as const,
    category: "foundation" as const,
    completed: false,
  },
};

// Icons
const Icons = {
  moves: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
    </svg>
  ),
  campaigns: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z" />
    </svg>
  ),
  icps: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" />
      <circle cx="9" cy="7" r="4" />
      <path d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75" />
    </svg>
  ),
  channels: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <rect x="2" y="3" width="20" height="14" rx="2" ry="2" />
      <line x1="8" y1="21" x2="16" y2="21" />
      <line x1="12" y1="17" x2="12" y2="21" />
    </svg>
  ),
  check: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <polyline points="20 6 9 17 4 12" />
    </svg>
  ),
  circle: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="12" cy="12" r="10" />
    </svg>
  ),
  arrowRight: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <line x1="5" y1="12" x2="19" y2="12" />
      <polyline points="12 5 19 12 12 19" />
    </svg>
  ),
  lock: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
      <path d="M7 11V7a5 5 0 0110 0v4" />
    </svg>
  ),
  sparkles: (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M12 3l1.5 4.5L18 9l-4.5 1.5L12 15l-1.5-4.5L6 9l4.5-1.5L12 3z" />
      <path d="M5 17l.5 1.5L7 19l-1.5.5L5 21l-.5-1.5L3 19l1.5-.5L5 17z" />
      <path d="M19 15l.5 1.5L21 17l-1.5.5L19 19l-.5-1.5L17 17l1.5-.5L19 15z" />
    </svg>
  ),
};

// Daily Win Card Component
function DailyWinCard({
  win,
  onComplete,
  onSkip,
}: {
  win: Win;
  onComplete: () => void;
  onSkip: () => void;
}) {
  const cardRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!cardRef.current) return;
    gsap.fromTo(
      cardRef.current,
      { y: 20, opacity: 0, scale: 0.98 },
      { y: 0, opacity: 1, scale: 1, duration: 0.5, ease: "power2.out" }
    );
  }, [win.id]);

  const impactColors = {
    high: "bg-[#F5F0E6] text-[#8B6B3D] border-[#D4C4A8]",
    medium: "bg-[var(--bg-canvas)] text-[var(--ink-1)] border-[var(--border-2)]",
    low: "bg-[var(--bg-surface)] text-[var(--ink-3)] border-[var(--border-1)]",
  };

  const categoryLabels: Record<string, string> = {
    foundation: "Foundation",
    move: "Move",
    campaign: "Campaign",
    analysis: "Analysis",
  };

  return (
    <div
      ref={cardRef}
      className="daily-win-card relative bg-gradient-to-br from-[var(--bg-raised)] to-[var(--bg-surface)] border border-[var(--border-1)] rounded-[var(--radius-lg)] p-8 overflow-hidden"
    >
      {/* Decorative glow */}
      <div className="absolute top-0 right-0 w-64 h-64 bg-[var(--ink-1)] opacity-[0.02] rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />

      <div className="relative">
        {/* Header */}
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-[var(--radius-sm)] bg-[var(--ink-1)] text-[var(--ink-inverse)] flex items-center justify-center">
            {Icons.sparkles}
          </div>
          <div>
            <h2 className="rf-h4">Today&apos;s Win</h2>
            <p className="rf-body-sm text-[var(--ink-3)]">Focus on this one thing today</p>
          </div>
        </div>

        {/* Content */}
        <div className="mt-6 space-y-4">
          <h3 className="rf-h3">{win.title}</h3>
          <p className="rf-body text-[var(--ink-2)] max-w-2xl">{win.description}</p>

          {/* Tags */}
          <div className="flex items-center gap-3 pt-2">
            <span
              className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-[var(--radius-sm)] text-[12px] font-medium border ${impactColors[win.impact]}`}
            >
              <span
                className={`w-1.5 h-1.5 rounded-full ${
                  win.impact === "high"
                    ? "bg-[#8B6B3D]"
                    : win.impact === "medium"
                      ? "bg-[var(--ink-1)]"
                      : "bg-[var(--ink-3)]"
                }`}
              />
              {win.impact.charAt(0).toUpperCase() + win.impact.slice(1)} Impact
            </span>
            <Tag>{categoryLabels[win.category]}</Tag>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-3 mt-8">
          <Button variant="primary" size="lg" onClick={onComplete}>
            Mark Complete
          </Button>
          <Button variant="tertiary" size="lg" onClick={onSkip}>
            Skip → Next Win
          </Button>
        </div>
      </div>
    </div>
  );
}

// Metric Card Component
function MetricCard({ metric, index }: { metric: Metric; index: number }) {
  const cardRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!cardRef.current) return;
    gsap.fromTo(
      cardRef.current,
      { y: 20, opacity: 0 },
      {
        y: 0,
        opacity: 1,
        duration: 0.4,
        delay: index * 0.08,
        ease: "power2.out",
      }
    );
  }, [index]);

  const trendPositive = metric.trend >= 0;

  return (
    <div
      ref={cardRef}
      className="metric-card rf-card rf-card-hover group cursor-pointer"
    >
      <div className="flex items-start justify-between">
        <div className="w-10 h-10 rounded-[var(--radius-sm)] bg-[var(--bg-canvas)] text-[var(--ink-2)] flex items-center justify-center group-hover:text-[var(--ink-1)] transition-colors">
          {metric.icon}
        </div>
        <span
          className={`rf-mono-xs ${trendPositive ? "text-[var(--status-success)]" : "text-[var(--status-error)]"}`}
        >
          {trendPositive ? "+" : ""}
          {metric.trend}%
        </span>
      </div>
      <div className="mt-4">
        <div className="rf-h3">{metric.value}</div>
        <div className="rf-body-sm text-[var(--ink-3)]">{metric.label}</div>
      </div>
    </div>
  );
}

// Current Focus Section
function CurrentFocusSection() {
  const sectionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!sectionRef.current) return;
    gsap.fromTo(
      sectionRef.current,
      { y: 24, opacity: 0 },
      { y: 0, opacity: 1, duration: 0.5, ease: "power2.out", delay: 0.4 }
    );
  }, []);

  const hasActiveMove = mockData.moves.active > 0;

  if (!hasActiveMove) {
    return (
      <div ref={sectionRef} className="focus-section">
<Card variant="interactive" className="h-full">
          <div className="flex flex-col items-center justify-center h-full min-h-[280px] text-center">
            <div className="w-16 h-16 rounded-full bg-[var(--bg-canvas)] flex items-center justify-center mb-4">
              <svg
                width="32"
                height="32"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.5"
                className="text-[var(--ink-3)]"
              >
                <path d="M12 5v14M5 12h14" />
              </svg>
            </div>
            <h3 className="rf-h4 mb-2">No Active Moves</h3>
            <p className="rf-body-sm text-[var(--ink-3)] mb-6 max-w-sm">
              Create your first Move to start tracking progress toward your objectives.
            </p>
            <Button variant="primary">Create Move</Button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div ref={sectionRef} className="focus-section">
      <Card variant="interactive" className="h-full">
        <div className="flex items-start justify-between mb-6">
          <div>
            <span className="rf-label text-[var(--ink-3)] mb-2 block">Current Focus</span>
            <h3 className="rf-h3">Product Launch Campaign</h3>
            <p className="rf-body-sm text-[var(--ink-2)] mt-1">
              Enterprise SaaS rollout for Q1
            </p>
          </div>
          <Badge variant="info">In Progress</Badge>
        </div>

        {/* Progress */}
        <div className="space-y-3">
          <div className="flex items-center justify-between rf-body-sm">
            <span className="text-[var(--ink-2)]">Progress</span>
            <span className="rf-mono-xs">65%</span>
          </div>
          <Progress value={65} size="md" />
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mt-8 pt-6 border-t border-[var(--border-1)]">
          <div>
            <div className="rf-mono-xs text-[var(--ink-3)] mb-1">Tasks</div>
            <div className="rf-h4">13/20</div>
          </div>
          <div>
            <div className="rf-mono-xs text-[var(--ink-3)] mb-1">Days Left</div>
            <div className="rf-h4">12</div>
          </div>
          <div>
            <div className="rf-mono-xs text-[var(--ink-3)] mb-1">Campaigns</div>
            <div className="rf-h4">3</div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-3 mt-8">
          <Button variant="secondary">View Details</Button>
          <Button variant="primary">Continue Execution</Button>
        </div>
      </Card>
    </div>
  );
}

// Foundation Status Card
function FoundationCard() {
  const cardRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!cardRef.current) return;
    gsap.fromTo(
      cardRef.current,
      { y: 20, opacity: 0 },
      { y: 0, opacity: 1, duration: 0.5, ease: "power2.out", delay: 0.5 }
    );
  }, []);

  const items = [
    { label: "Positioning", complete: mockData.foundation.positioning },
    { label: "ICPs", complete: mockData.foundation.icps, count: mockData.icps },
    { label: "Messaging", complete: mockData.foundation.messaging },
  ];

  const completeCount = items.filter((i) => i.complete).length;
  const progress = (completeCount / items.length) * 100;
  const isLocked = progress === 100;

  return (
    <div ref={cardRef}>
      <Card>
        <div className="flex items-center gap-2 mb-4">
          {Icons.lock}
          <h3 className="rf-h4">Foundation</h3>
        </div>

        <Progress value={progress} size="sm" className="mb-6" />

        <div className="space-y-3">
          {items.map((item) => (
            <div key={item.label} className="flex items-center justify-between py-2">
              <div className="flex items-center gap-3">
                <span
                  className={`flex-shrink-0 ${item.complete ? "text-[var(--status-success)]" : "text-[var(--ink-3)]"}`}
                >
                  {item.complete ? Icons.check : Icons.circle}
                </span>
                <span className={`rf-body-sm ${item.complete ? "text-[var(--ink-1)]" : "text-[var(--ink-3)]"}`}>
                  {item.label}
                </span>
              </div>
              {item.count && <span className="rf-mono-xs text-[var(--ink-3)]">{item.count}</span>}
            </div>
          ))}
        </div>

        <div className="mt-6 pt-4 border-t border-[var(--border-1)]">
          <div className="flex items-center justify-between">
            <Badge variant={isLocked ? "success" : "warning"}>
              {isLocked ? "Locked" : "Draft"}
            </Badge>
            <Button variant="tertiary" size="sm">
              Configure
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}

// Quick Actions Card
function QuickActionsCard() {
  const cardRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!cardRef.current) return;
    gsap.fromTo(
      cardRef.current,
      { y: 20, opacity: 0 },
      { y: 0, opacity: 1, duration: 0.5, ease: "power2.out", delay: 0.6 }
    );
  }, []);

  const actions = [
    { label: "Create Move", href: "/moves/new" },
    { label: "Open Muse", href: "/muse" },
    { label: "View Campaigns", href: "/campaigns" },
  ];

  return (
    <div ref={cardRef}>
      <Card>
        <h3 className="rf-h4 mb-4">Quick Actions</h3>
        <div className="space-y-2">
          {actions.map((action) => (
            <a
              key={action.label}
              href={action.href}
              className="group flex items-center justify-between py-3 px-3 -mx-3 rounded-[var(--radius-sm)] hover:bg-[var(--state-hover)] transition-colors"
            >
              <span className="rf-body-sm font-medium">{action.label}</span>
              <span className="text-[var(--ink-3)] group-hover:text-[var(--ink-1)] transition-colors group-hover:translate-x-1 duration-200">
                {Icons.arrowRight}
              </span>
            </a>
          ))}
        </div>
      </Card>
    </div>
  );
}

// Main Dashboard Page
export default function DashboardPage() {
  const headerRef = useRef<HTMLDivElement>(null);
  const [currentWin, setCurrentWin] = useState<Win>(mockData.dailyWin);

  // Page entrance animation
  useEffect(() => {
    const tl = gsap.timeline({ defaults: { ease: "power2.out" } });

    tl.fromTo(
      ".dashboard-header",
      { y: -16, opacity: 0 },
      { y: 0, opacity: 1, duration: 0.5 }
    );

    return () => {
      tl.kill();
    };
  }, []);

  const handleWinComplete = () => {
    gsap.to(".daily-win-card", {
      y: -10,
      opacity: 0,
      scale: 0.98,
      duration: 0.3,
      onComplete: () => {
        setCurrentWin((prev) => ({ ...prev, completed: true }));
        // In real app, this would fetch next win
      },
    });
  };

  const handleWinSkip = () => {
    gsap.to(".daily-win-card", {
      x: -20,
      opacity: 0,
      duration: 0.3,
      onComplete: () => {
        // In real app, this would fetch next win
        setCurrentWin((prev) => ({
          ...prev,
          id: `win-${Date.now()}`,
          title: "Review Campaign Performance",
          description: "Check your active campaign metrics and identify optimization opportunities.",
          impact: "medium",
          category: "analysis",
        }));
      },
    });
  };

  // Metrics data
  const metrics: Metric[] = [
    {
      label: "Active Moves",
      value: mockData.moves.active,
      trend: 12,
      icon: Icons.moves,
    },
    {
      label: "Campaigns",
      value: mockData.campaigns.active,
      trend: 8,
      icon: Icons.campaigns,
    },
    {
      label: "ICPs Defined",
      value: mockData.icps,
      trend: 0,
      icon: Icons.icps,
    },
    {
      label: "Channels",
      value: mockData.channels,
      trend: 4,
      icon: Icons.channels,
    },
  ];

  return (
    <Layout mode={mockData.mode}>
      <div className="space-y-8 pb-12">
        {/* Header Section */}
        <header ref={headerRef} className="dashboard-header">
          <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
            <div>
              <h1 className="rf-h2">{mockData.company || "Your Workspace"}</h1>
              <p className="rf-body text-[var(--ink-2)] mt-1">
                {mockData.valueProp || "Define your foundation to unlock growth"}
              </p>
            </div>
            <div className="flex items-center gap-3">
              <Badge variant="success" dot>
                Nominal
              </Badge>
              <Button variant="secondary" size="sm">
                {Icons.lock}
                <span className="ml-2">Lock Foundation</span>
              </Button>
              <Button variant="primary" size="sm">
                New Move
              </Button>
            </div>
          </div>
        </header>

        {/* Daily Win Section */}
        {!currentWin.completed && (
          <DailyWinCard win={currentWin} onComplete={handleWinComplete} onSkip={handleWinSkip} />
        )}

        {/* Metrics Row */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {metrics.map((metric, index) => (
            <MetricCard key={metric.label} metric={metric} index={index} />
          ))}
        </div>

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Current Focus - 2/3 */}
          <div className="lg:col-span-2">
            <CurrentFocusSection />
          </div>

          {/* Side Panel - 1/3 */}
          <div className="space-y-6">
            <FoundationCard />
            <QuickActionsCard />
          </div>
        </div>
      </div>
    </Layout>
  );
}
