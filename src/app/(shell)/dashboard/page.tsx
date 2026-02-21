import { Suspense } from "react";
import { Metadata } from "next";
import { DashboardContent } from "./dashboard-content";

export const metadata: Metadata = {
  title: "Dashboard | RaptorFlow",
  description: "Your marketing cockpit — Human-led, AI-accelerated",
};

// Server-side data fetching
async function getDashboardMetrics() {
  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/dashboard/metrics`, {
      next: { revalidate: 60 },
    });
    if (!res.ok) throw new Error("Failed to fetch");
    return res.json();
  } catch {
    return {
      activeMoves: 12,
      campaignHealth: 94,
      dailyWinRate: 87,
      decisionsLogged: 156,
    };
  }
}

async function getRecentMoves() {
  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/moves/recent`, {
      next: { revalidate: 30 },
    });
    return res.ok ? res.json() : [];
  } catch {
    return [
      { id: "1", name: "Q1 Campaign Launch", status: "active", progress: 75, category: "Campaign" },
      { id: "2", name: "Content Audit", status: "draft", progress: 30, category: "Audit" },
      { id: "3", name: "Competitor Analysis", status: "active", progress: 60, category: "Research" },
    ];
  }
}

async function getDailyWins() {
  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/daily-wins`, {
      next: { revalidate: 300 },
    });
    return res.ok ? res.json() : [];
  } catch {
    return [
      { id: "1", date: "2025-01-20", metric: "Landing page conversion", value: "+12%", moveId: "1" },
      { id: "2", date: "2025-01-19", metric: "Email open rate", value: "34%", moveId: "2" },
    ];
  }
}

function DashboardSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div 
            key={i} 
            className="h-24 bg-[var(--bg-surface)] rounded-[var(--radius-md)] border border-[var(--border-1)]"
          />
        ))}
      </div>
      <div className="h-64 bg-[var(--bg-surface)] rounded-[var(--radius-md)] border border-[var(--border-1)]" />
    </div>
  );
}

export default async function DashboardPage() {
  const [metrics, moves, wins] = await Promise.all([
    getDashboardMetrics(),
    getRecentMoves(),
    getDailyWins(),
  ]);

  return (
    <div className="min-h-screen bg-[var(--bg-canvas)]">
      <header className="h-14 border-b border-[var(--border-1)] bg-[var(--bg-surface)] flex items-center justify-between px-6">
        <div className="flex items-center gap-4">
          <span className="text-[11px] font-mono text-[var(--ink-3)] tracking-wider">
            MODE
          </span>
          <span className="text-[12px] font-semibold text-[var(--status-success)] flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-current animate-pulse" />
            Live
          </span>
        </div>
        <div className="text-[11px] font-mono text-[var(--ink-3)]">
          Last sync: 2m ago
        </div>
      </header>

      <main className="p-6 max-w-[1120px] mx-auto">
        <Suspense fallback={<DashboardSkeleton />}>
          <DashboardContent metrics={metrics} moves={moves} wins={wins} />
        </Suspense>
      </main>
    </div>
  );
}
