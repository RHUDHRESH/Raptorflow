"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { DashboardHeader } from "@/components/dashboard/DashboardHeader";
import { DashboardMetrics, Metric } from "@/components/dashboard/DashboardMetrics";
import { DashboardFocus } from "@/components/dashboard/DashboardFocus";
import { DashboardActivity, ActivityItem } from "@/components/dashboard/DashboardActivity";
import { useMovesStore } from "@/stores/movesStore";
import { useCampaignStore } from "@/stores/campaignStore";
import { useAuth } from "@/contexts/AuthContext";
import { Activity, Target, Users, Zap } from "lucide-react";

/* ══════════════════════════════════════════════════════════════════════════════
   DASHBOARD — Founder Command Center
   Quiet Luxury: One decision per screen, editorial calm, decisive clarity.
   ══════════════════════════════════════════════════════════════════════════════ */

export default function DashboardPage() {
  const pageRef = useRef<HTMLDivElement>(null);
  const { moves, fetchMoves } = useMovesStore();
  const { campaigns, fetchCampaigns } = useCampaignStore();
  const { user, profile } = useAuth();

  // Fetch data on mount
  useEffect(() => {
    if (user?.id) {
      fetchMoves(user.id);
    }
    if (profile?.workspace_id) {
      fetchCampaigns(profile.workspace_id);
    }
  }, [user?.id, profile?.workspace_id, fetchMoves, fetchCampaigns]);

  // Calculate active items
  const activeMoves = moves.filter(
    (m) => m.status === "active" || m.status === "draft"
  );
  const activeCampaigns = campaigns.filter((c) => c.status === "Active");

  // Determine system status
  const systemStatus =
    activeCampaigns.length === 0 && activeMoves.length === 0
      ? "Attention"
      : "Nominal";

  // Primary focus move (first active)
  const primaryMove = activeMoves.length > 0 ? activeMoves[0] : null;

  // Extract user name
  const userName = profile?.full_name || (user
    ? user.email.split("@")[0].charAt(0).toUpperCase() +
    user.email.split("@")[0].slice(1)
    : "Founder");

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
      label: "Est. Reach",
      value: "12.4k",
      trend: "up",
      trendValue: "+12%",
      icon: Users,
    },
    {
      label: "Engagement",
      value: "2.8%",
      trend: "up",
      trendValue: "+0.4%",
      icon: Activity,
    },
  ];

  // Recent activity (mock for now - would come from real data)
  const recentActivity: ActivityItem[] = [
    {
      id: "1",
      type: "campaign",
      title: "Q1 Launch campaign activated",
      timestamp: "2h ago",
      status: "active",
      href: "/campaigns",
    },
    {
      id: "2",
      type: "move",
      title: "Welcome Sequence protocol completed",
      timestamp: "1d ago",
      status: "completed",
      href: "/moves",
    },
    {
      id: "3",
      type: "cohort",
      title: "New segment added: Enterprise Early Adopters",
      timestamp: "2d ago",
      href: "/cohorts",
    },
  ];

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
        <div data-fade>
          <DashboardHeader
            userName={userName}
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

          {/* Activity feed (takes 1/3 on desktop) */}
          <div data-fade className="lg:col-span-1">
            <DashboardActivity items={recentActivity} />
          </div>
        </div>

        {/* Footer meta */}
        <div
          data-fade
          className="mt-16 text-center text-[10px] font-mono text-[var(--ink-muted)] uppercase tracking-widest"
        >
          RaptorFlow OS v4.2 • Secure
        </div>
      </div>
    </div>
  );
}
