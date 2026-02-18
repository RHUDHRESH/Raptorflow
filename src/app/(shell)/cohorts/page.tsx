"use client";

import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { Layout } from "@/components/raptor/shell/Layout";
import { Card } from "@/components/raptor/ui/Card";
import { Button } from "@/components/raptor/ui/Button";
import { Progress } from "@/components/raptor/ui/Progress";
import { Input } from "@/components/raptor/ui/Input";
import { 
  Users, 
  TrendingUp, 
  TrendingDown,
  Activity,
  Target,
  Plus,
  Search,
  Filter,
  MoreHorizontal,
  ArrowRight
} from "lucide-react";

// ═══════════════════════════════════════════════════════════════════════════════
// COHORTS PAGE — Audience Segments and ICPs
// ═══════════════════════════════════════════════════════════════════════════════

interface Cohort {
  id: string;
  name: string;
  description: string;
  size: number;
  sizeTrend: "up" | "down" | "stable";
  engagementScore: number;
  engagementTrend: "up" | "down" | "stable";
  traits: {
    role: string;
    companySize: string;
    painPoints: string[];
  };
  recency: "active" | "recent" | "dormant";
  campaigns: number;
  conversionRate: number;
  tags: string[];
}

// Mock Data
const mockCohorts: Cohort[] = [
  {
    id: "cohort-1",
    name: "Enterprise Operations",
    description: "Large teams struggling with process inefficiency and manual workflows",
    size: 12450,
    sizeTrend: "up",
    engagementScore: 78,
    engagementTrend: "up",
    traits: {
      role: "Operations Manager",
      companySize: "500+ employees",
      painPoints: ["Manual processes", "Approval bottlenecks", "Tool sprawl"]
    },
    recency: "active",
    campaigns: 3,
    conversionRate: 4.2,
    tags: ["enterprise", "high-value"]
  },
  {
    id: "cohort-2",
    name: "Growing Startups",
    description: "Scaling SaaS teams needing automation to maintain quality",
    size: 8320,
    sizeTrend: "stable",
    engagementScore: 65,
    engagementTrend: "down",
    traits: {
      role: "Founder / CTO",
      companySize: "50-200 employees",
      painPoints: ["Scaling operations", "Inconsistent processes"]
    },
    recency: "recent",
    campaigns: 2,
    conversionRate: 6.8,
    tags: ["startup", "fast-growing"]
  },
  {
    id: "cohort-3",
    name: "Product Leaders",
    description: "Product managers seeking workflow improvements",
    size: 5670,
    sizeTrend: "up",
    engagementScore: 82,
    engagementTrend: "up",
    traits: {
      role: "Product Manager",
      companySize: "100+ employees",
      painPoints: ["Cross-team coordination", "Delivery delays"]
    },
    recency: "active",
    campaigns: 4,
    conversionRate: 5.5,
    tags: ["product", "decision-makers"]
  }
];

const mockStats = {
  totalAudience: 26440,
  avgEngagement: 75,
  activeCohorts: 3,
  campaignsRunning: 9
};

// Recency config
const recencyConfig = {
  active: { label: "Active", color: "text-[var(--status-success)]", bg: "bg-[var(--status-success-bg)]" },
  recent: { label: "Recent", color: "text-[var(--status-warning)]", bg: "bg-[var(--status-warning-bg)]" },
  dormant: { label: "Dormant", color: "text-[var(--status-error)]", bg: "bg-[var(--status-error-bg)]" },
};

// Format number with K suffix
function formatNumber(num: number): string {
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
  return num.toString();
}

// Trend icon component
function TrendIcon({ trend, className }: { trend: "up" | "down" | "stable"; className?: string }) {
  if (trend === "up") return <TrendingUp size={14} className={className} />;
  if (trend === "down") return <TrendingDown size={14} className={className} />;
  return <span className={`text-[10px] ${className}`}>−</span>;
}

// Cohort Card Component
function CohortCard({ cohort, index }: { cohort: Cohort; index: number }) {
  const recency = recencyConfig[cohort.recency];
  const progressRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (progressRef.current) {
      gsap.fromTo(
        progressRef.current,
        { width: 0 },
        { width: `${cohort.engagementScore}%`, duration: 0.8, ease: "power2.out", delay: 0.3 + index * 0.1 }
      );
    }
  }, [cohort.engagementScore, index]);

  return (
    <Card className="cohort-card h-full flex flex-col cursor-pointer transition-all duration-200 hover:-translate-y-1 hover:border-[var(--border-2)] hover:shadow-[var(--shadow-modal)]">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="rf-h4 truncate">{cohort.name}</h3>
          </div>
          <p className="rf-body-sm text-[var(--ink-2)] line-clamp-2">{cohort.description}</p>
        </div>
        <span className={`px-2 py-1 rounded-[var(--radius-sm)] rf-mono-xs ${recency.bg} ${recency.color}`}>
          {recency.label}
        </span>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        {/* Size */}
        <div className="p-3 bg-[var(--bg-canvas)] rounded-[var(--radius-sm)]">
          <div className="flex items-center gap-1.5 mb-1">
            <Users size={14} className="text-[var(--ink-3)]" />
            <span className="rf-mono-xs text-[var(--ink-3)] uppercase">Size</span>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="rf-h3" style={{ fontFamily: 'var(--font-mono)' }}>{formatNumber(cohort.size)}</span>
            <span
              className={`rf-mono-xs flex items-center gap-0.5 ${
                cohort.sizeTrend === "up" ? "text-[var(--status-success)]" : 
                cohort.sizeTrend === "down" ? "text-[var(--status-error)]" : "text-[var(--ink-3)]"
              }`}
            >
              <TrendIcon trend={cohort.sizeTrend} />
              {cohort.sizeTrend !== "stable" && (cohort.sizeTrend === "up" ? "12%" : "5%")}
            </span>
          </div>
        </div>

        {/* Engagement */}
        <div className="p-3 bg-[var(--bg-canvas)] rounded-[var(--radius-sm)]">
          <div className="flex items-center gap-1.5 mb-1">
            <Activity size={14} className="text-[var(--ink-3)]" />
            <span className="rf-mono-xs text-[var(--ink-3)] uppercase">Engagement</span>
          </div>
          <div className="flex items-center gap-2 mb-1">
            <span className="rf-h3" style={{ fontFamily: 'var(--font-mono)' }}>{cohort.engagementScore}%</span>
            <span
              className={`rf-mono-xs flex items-center gap-0.5 ${
                cohort.engagementTrend === "up" ? "text-[var(--status-success)]" : 
                cohort.engagementTrend === "down" ? "text-[var(--status-error)]" : "text-[var(--ink-3)]"
              }`}
            >
              <TrendIcon trend={cohort.engagementTrend} />
              {cohort.engagementTrend !== "stable" && (cohort.engagementTrend === "up" ? "5%" : "3%")}
            </span>
          </div>
          <div className="w-full bg-[var(--bg-surface)] rounded-full h-1.5 overflow-hidden">
            <div
              ref={progressRef}
              className="h-full bg-[var(--ink-1)] rounded-full"
              style={{ width: 0 }}
            />
          </div>
        </div>
      </div>

      {/* Traits */}
      <div className="space-y-2 mb-4 flex-1">
        <div className="flex items-start gap-2">
          <span className="rf-mono-xs text-[var(--ink-3)] uppercase w-24 flex-shrink-0">
            Role
          </span>
          <span className="rf-body-sm text-[var(--ink-1)] truncate">{cohort.traits.role}</span>
        </div>
        <div className="flex items-start gap-2">
          <span className="rf-mono-xs text-[var(--ink-3)] uppercase w-24 flex-shrink-0">
            Company
          </span>
          <span className="rf-body-sm text-[var(--ink-1)] truncate">{cohort.traits.companySize}</span>
        </div>
        <div className="flex items-start gap-2">
          <span className="rf-mono-xs text-[var(--ink-3)] uppercase w-24 flex-shrink-0">
            Pain Points
          </span>
          <span className="rf-body-sm text-[var(--ink-1)] truncate">
            {cohort.traits.painPoints.join(", ")}
          </span>
        </div>
      </div>

      {/* Footer */}
      <div className="pt-4 border-t border-[var(--border-1)]">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3">
            <span className="rf-body-sm text-[var(--ink-2)]">
              {cohort.campaigns} campaigns
            </span>
          </div>
          <div className="flex items-center gap-1">
            <TrendingUp size={14} className="text-[var(--status-success)]" />
            <span className="rf-mono-xs text-[var(--status-success)]">{cohort.conversionRate}% conv.</span>
          </div>
        </div>

        {/* Tags */}
        <div className="flex flex-wrap gap-2">
          {cohort.tags.map((tag) => (
            <span key={tag} className="rf-tag text-[10px]">
              #{tag}
            </span>
          ))}
        </div>
      </div>
    </Card>
  );
}

// Main Cohorts Page
export default function CohortsPage() {
  const pageRef = useRef<HTMLDivElement>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [sizeFilter, setSizeFilter] = useState<"all" | "small" | "medium" | "large">("all");
  const [engagementFilter, setEngagementFilter] = useState<"all" | "high" | "medium" | "low">("all");
  const [recencyFilter, setRecencyFilter] = useState<"all" | "active" | "recent" | "dormant">("all");

  // Filter cohorts
  const filteredCohorts = mockCohorts.filter((cohort) => {
    // Search filter
    if (searchQuery && !cohort.name.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }

    // Size filter
    if (sizeFilter !== "all") {
      if (sizeFilter === "small" && cohort.size >= 5000) return false;
      if (sizeFilter === "medium" && (cohort.size < 5000 || cohort.size >= 10000)) return false;
      if (sizeFilter === "large" && cohort.size < 10000) return false;
    }

    // Engagement filter
    if (engagementFilter !== "all") {
      if (engagementFilter === "high" && cohort.engagementScore < 70) return false;
      if (engagementFilter === "medium" && (cohort.engagementScore < 40 || cohort.engagementScore >= 70)) return false;
      if (engagementFilter === "low" && cohort.engagementScore >= 40) return false;
    }

    // Recency filter
    if (recencyFilter !== "all" && cohort.recency !== recencyFilter) {
      return false;
    }

    return true;
  });

  // GSAP Entrance Animation
  useEffect(() => {
    const ctx = gsap.context(() => {
      const tl = gsap.timeline({ defaults: { ease: "power2.out" } });

      // Header entrance
      tl.fromTo(
        ".cohorts-header",
        { y: -20, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.5 }
      );

      // Stats cards
      tl.fromTo(
        ".stats-card",
        { y: 20, opacity: 0, scale: 0.95 },
        { y: 0, opacity: 1, scale: 1, duration: 0.4, stagger: 0.08 },
        "-=0.3"
      );

      // Filter bar
      tl.fromTo(
        ".filter-bar",
        { y: 10, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.3 },
        "-=0.2"
      );

      // Cohort cards
      tl.fromTo(
        ".cohort-card",
        { y: 30, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.5, stagger: 0.1 },
        "-=0.2"
      );
    }, pageRef);

    return () => ctx.revert();
  }, []);

  const stats = [
    { label: "Total Audience", value: formatNumber(mockStats.totalAudience), icon: Users, trend: 12 },
    { label: "Avg Engagement", value: `${mockStats.avgEngagement}%`, icon: Activity, trend: 5 },
    { label: "Active Cohorts", value: mockStats.activeCohorts.toString(), icon: Target, trend: 0 },
    { label: "Campaigns Running", value: mockStats.campaignsRunning.toString(), icon: TrendingUp, trend: 8 },
  ];

  return (
    <Layout mode="live" activeNavItem="cohorts">
      <div ref={pageRef} className="h-full overflow-y-auto">
        <div className="max-w-[1200px] mx-auto p-6 pb-12">
          {/* Header */}
          <header className="cohorts-header mb-6">
            <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
              <div>
                <h1 className="rf-h2 mb-1">Cohorts</h1>
                <p className="rf-body text-[var(--ink-2)]">
                  Audience segments and ICPs
                </p>
              </div>
              <div className="flex items-center gap-3">
                <Button variant="primary" size="sm">
                  <Plus size={14} />
                  Add Cohort
                </Button>
              </div>
            </div>
          </header>

          {/* Stats Row */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            {stats.map((stat) => {
              const Icon = stat.icon;
              return (
                <Card key={stat.label} className="stats-card">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="rf-label text-[var(--ink-3)] mb-1">{stat.label}</p>
                      <p className="rf-h2" style={{ fontFamily: 'var(--font-mono)' }}>{stat.value}</p>
                    </div>
                    <div className="w-10 h-10 rounded-[var(--radius-sm)] bg-[var(--bg-canvas)] flex items-center justify-center">
                      <Icon size={20} className="text-[var(--ink-2)]" />
                    </div>
                  </div>
                  {stat.trend > 0 && (
                    <div className="mt-3 flex items-center gap-1">
                      <TrendingUp size={14} className="text-[var(--status-success)]" />
                      <span className="rf-mono-xs text-[var(--status-success)]">+{stat.trend}%</span>
                      <span className="rf-mono-xs text-[var(--ink-3)]">vs last month</span>
                    </div>
                  )}
                </Card>
              );
            })}
          </div>

          {/* Filter Bar */}
          <div className="filter-bar mb-6 p-4 bg-[var(--bg-surface)] border border-[var(--border-1)] rounded-[var(--radius-md)]">
            <div className="flex flex-col lg:flex-row lg:items-center gap-4">
              {/* Search */}
              <div className="relative flex-1">
                <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--ink-3)]" />
                <input
                  type="text"
                  placeholder="Search cohorts..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full h-10 pl-10 pr-4 bg-[var(--bg-canvas)] border border-[var(--border-1)] rounded-[var(--radius-sm)] text-[14px] focus:outline-none focus:border-[var(--ink-1)]"
                />
              </div>

              {/* Filter Dropdowns */}
              <div className="flex items-center gap-3 flex-wrap">
                {/* Size Filter */}
                <select
                  value={sizeFilter}
                  onChange={(e) => setSizeFilter(e.target.value as typeof sizeFilter)}
                  className="h-10 px-3 bg-[var(--bg-canvas)] border border-[var(--border-1)] rounded-[var(--radius-sm)] text-[14px] text-[var(--ink-1)]"
                >
                  <option value="all">All Sizes</option>
                  <option value="small">Small (&lt;5K)</option>
                  <option value="medium">Medium (5K-10K)</option>
                  <option value="large">Large (&gt;10K)</option>
                </select>

                {/* Engagement Filter */}
                <select
                  value={engagementFilter}
                  onChange={(e) => setEngagementFilter(e.target.value as typeof engagementFilter)}
                  className="h-10 px-3 bg-[var(--bg-canvas)] border border-[var(--border-1)] rounded-[var(--radius-sm)] text-[14px] text-[var(--ink-1)]"
                >
                  <option value="all">All Engagement</option>
                  <option value="high">High (&gt;70%)</option>
                  <option value="medium">Medium (40-70%)</option>
                  <option value="low">Low (&lt;40%)</option>
                </select>

                {/* Recency Filter */}
                <select
                  value={recencyFilter}
                  onChange={(e) => setRecencyFilter(e.target.value as typeof recencyFilter)}
                  className="h-10 px-3 bg-[var(--bg-canvas)] border border-[var(--border-1)] rounded-[var(--radius-sm)] text-[14px] text-[var(--ink-1)]"
                >
                  <option value="all">All Activity</option>
                  <option value="active">Active</option>
                  <option value="recent">Recent</option>
                  <option value="dormant">Dormant</option>
                </select>
              </div>
            </div>
          </div>

          {/* Cohorts Grid */}
          {filteredCohorts.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredCohorts.map((cohort, index) => (
                <CohortCard key={cohort.id} cohort={cohort} index={index} />
              ))}
            </div>
          ) : (
            /* Empty State */
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <div className="w-16 h-16 rounded-full bg-[var(--bg-surface)] flex items-center justify-center mb-4">
                <Users size={32} className="text-[var(--ink-3)]" />
              </div>
              <h3 className="rf-h4 mb-2">No cohorts defined</h3>
              <p className="rf-body-sm text-[var(--ink-2)] max-w-sm mb-6">
                Define your ideal customer profiles to unlock targeted campaigns
              </p>
              <Button variant="primary">
                <Plus size={16} />
                Create First Cohort
              </Button>
            </div>
          )}

          {/* Empty search state */}
          {filteredCohorts.length === 0 && (searchQuery || sizeFilter !== "all" || engagementFilter !== "all" || recencyFilter !== "all") && (
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <div className="w-16 h-16 rounded-full bg-[var(--bg-surface)] flex items-center justify-center mb-4">
                <Search size={32} className="text-[var(--ink-3)]" />
              </div>
              <h3 className="rf-h4 mb-2">No cohorts found</h3>
              <p className="rf-body-sm text-[var(--ink-2)] mb-6">
                Try adjusting your filters or search terms
              </p>
              <Button 
                variant="secondary" 
                onClick={() => {
                  setSearchQuery("");
                  setSizeFilter("all");
                  setEngagementFilter("all");
                  setRecencyFilter("all");
                }}
              >
                Clear Filters
              </Button>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
