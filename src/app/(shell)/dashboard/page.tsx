"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { DashboardHeader } from "@/components/dashboard/DashboardHeader";
import { DashboardMetrics, Metric } from "@/components/dashboard/DashboardMetrics";
import { DashboardFocus } from "@/components/dashboard/DashboardFocus";
import { DashboardActivity, ActivityItem } from "@/components/dashboard/DashboardActivity";
import { useMovesStore } from "@/stores/movesStore";
import { useCampaignStore } from "@/stores/campaignStore";
import { useFoundationStore } from "@/stores/foundationStore";
import { useWorkspace } from "@/components/workspace/WorkspaceProvider";
import { Target, Users, Zap, Layers } from "lucide-react";
import BCMStatusPanel from "@/components/bcm/BCMStatusPanel";
import { useBCMStore } from "@/stores/bcmStore";

/* ══════════════════════════════════════════════════════════════════════════════
   DASHBOARD — Founder Command Center
   Quiet Luxury: One decision per screen, editorial calm, decisive clarity.
   ══════════════════════════════════════════════════════════════════════════════ */

export default function DashboardPage() {
  const pageRef = useRef<HTMLDivElement>(null);
  const { moves, fetchMoves } = useMovesStore();
  const { campaigns, fetchCampaigns } = useCampaignStore();
  const { ricps, channels, fetchFoundation } = useFoundationStore();
  const { workspaceId, workspace } = useWorkspace();
  const { manifest: bcm } = useBCMStore();

  // Fetch data on mount
  useEffect(() => {
    if (!workspaceId) return;
    fetchMoves(workspaceId);
    fetchCampaigns(workspaceId);
    fetchFoundation(workspaceId);
  }, [workspaceId, fetchMoves, fetchCampaigns, fetchFoundation]);

  // Calculate active items
  const activeMoves = moves.filter(
    (m) => m.status === "active" || m.status === "draft"
  );
  const activeCampaigns = campaigns.filter((c) => c.status === "active");

  // Determine system status
  const systemStatus =
    activeCampaigns.length === 0 && activeMoves.length === 0
      ? "Attention"
      : "Nominal";

  // Primary focus move (first active)
  const primaryMove = activeMoves.length > 0 ? activeMoves[0] : null;

  const displayName = workspace?.name || "Workspace";

  // Metrics data
  const metrics: Metric[] = [
    {
      label: "Active Moves",
      value: activeMoves.length,
      icon: Zap,
    },
    {
      label: "Campaigns",
      value: activeCampaigns.length,
      trend: "neutral",
      trendValue: "Stable",
      icon: Target,
    },
    {
      label: "Cohorts (ICPs)",
      value: bcm?.meta?.icps_count ?? ricps.length,
      icon: Users,
    },
    {
      label: "Channels",
      value: bcm?.channels?.length ?? channels.length,
      icon: Layers,
    },
  ];

  // No fake "recent activity" without an event log.
  const recentActivity: ActivityItem[] = [];

  // Entrance animation
  useEffect(() => {
    if (!pageRef.current) return;

    gsap.fromTo(
      "[data-fade]",
      { opacity: 0, y: 12 },
      {
        opacity: 1,
        y: 0,
        duration: 0.5,
        stagger: 0.08,
        ease: "power2.out",
      }
    );
  }, []);

  return (
    <div ref={pageRef} className="min-h-screen bg-[var(--canvas)] pb-16">
      <div className="max-w-[1200px] mx-auto px-6 lg:px-12 pt-8">
        {/* Header */}
        <div data-fade className="flex items-center justify-between">
          <DashboardHeader
            userName={displayName}
            systemStatus={systemStatus}
          />
        </div>

        {/* Metrics row */}
        <div data-fade className="mt-10">
          <DashboardMetrics metrics={metrics} />
        </div>

        {/* Main content grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-10 mt-12">
          {/* Primary Focus (takes 2/3 on desktop) */}
          <div data-fade className="lg:col-span-2">
            <DashboardFocus move={primaryMove} />
          </div>

          {/* Activity feed + BCM panel (takes 1/3 on desktop) */}
          <div data-fade className="lg:col-span-1 space-y-6">
            {workspaceId && <BCMStatusPanel workspaceId={workspaceId} />}
            <DashboardActivity items={recentActivity} />
          </div>
        </div>

        {/* Footer meta */}
        <div
          data-fade
          className="mt-16 text-center text-[10px] font-mono text-[var(--ink-muted)] uppercase tracking-widest"
        >
          RaptorFlow | Reconstruction mode (no auth, no paywalls)
        </div>
      </div>
    </div>
  );
}
