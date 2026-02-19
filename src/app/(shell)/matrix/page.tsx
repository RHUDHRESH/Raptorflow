"use client";

import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { Layout } from "@/components/raptor/shell/Layout";
import { Card } from "@/components/raptor/ui/Card";
import { Button } from "@/components/raptor/ui/Button";
import { Badge } from "@/components/raptor/ui/Badge";
import { Tag } from "@/components/raptor/ui/Tag";
import {
  AlertCircle,
  AlertTriangle,
  CheckCircle2,
  HelpCircle,
  MoreHorizontal,
  RefreshCw,
  User,
  Clock,
  ArrowRight,
  Loader2,
} from "lucide-react";
import { useWorkspace } from "@/components/workspace/WorkspaceProvider";
import { movesService } from "@/services/moves.service";
import { campaignsService } from "@/services/campaigns.service";

// ═══════════════════════════════════════════════════════════════════════════════
// MATRIX PAGE — Status Dashboard
// "What's happening across all initiatives"
// ═══════════════════════════════════════════════════════════════════════════════

interface InitiativeItem {
  id: string;
  name: string;
  type: "move" | "campaign";
  status: "on-track" | "stuck" | "at-risk" | "needs-decision";
  owner: string;
  lastUpdate: Date;
  healthScore: number;
  blockers?: string[];
}

interface StatusCount {
  onTrack: number;
  stuck: number;
  atRisk: number;
  needsDecision: number;
}



// Status Card Component
function StatusCard({
  title,
  count,
  variant,
  icon: Icon,
}: {
  title: string;
  count: number;
  variant: "success" | "error" | "warning" | "default";
  icon: React.ElementType;
}) {
  const variantStyles = {
    success: {
      border: "border-l-[var(--status-success)]",
      bg: "bg-[var(--status-success-bg)]",
      text: "text-[var(--status-success)]",
    },
    error: {
      border: "border-l-[var(--status-error)]",
      bg: "bg-[var(--status-error-bg)]",
      text: "text-[var(--status-error)]",
    },
    warning: {
      border: "border-l-[var(--status-warning)]",
      bg: "bg-[var(--status-warning-bg)]",
      text: "text-[var(--status-warning)]",
    },
    default: {
      border: "border-l-[var(--ink-1)]",
      bg: "bg-[var(--bg-surface)]",
      text: "text-[var(--ink-1)]",
    },
  };

  const style = variantStyles[variant];

  return (
    <Card
      className={`status-card border-l-4 ${style.border}`}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="rf-label text-[var(--ink-3)] mb-1">{title}</p>
          <p className={`rf-h2 ${style.text}`}>{count}</p>
        </div>
        <div className={`w-10 h-10 rounded-[var(--radius-sm)] ${style.bg} flex items-center justify-center`}>
          <Icon size={20} className={style.text} />
        </div>
      </div>
    </Card>
  );
}

// Initiative Card Component
function InitiativeCard({
  item,
}: {
  item: InitiativeItem;
}) {
  const statusConfig = {
    "on-track": {
      border: "border-l-[var(--status-success)]",
      badge: <Badge variant="success">On Track</Badge>,
      icon: CheckCircle2,
    },
    stuck: {
      border: "border-l-[var(--status-error)]",
      badge: <Badge variant="error">Stuck</Badge>,
      icon: AlertCircle,
    },
    "at-risk": {
      border: "border-l-[var(--status-warning)]",
      badge: <Badge variant="warning">At Risk</Badge>,
      icon: AlertTriangle,
    },
    "needs-decision": {
      border: "border-l-[var(--ink-1)]",
      badge: <Badge variant="default">Needs Decision</Badge>,
      icon: HelpCircle,
    },
  };

  const config = statusConfig[item.status];
  const StatusIcon = config.icon;

  const formatDate = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days === 0) return "Today";
    if (days === 1) return "Yesterday";
    return `${days} days ago`;
  };

  return (
    <Card
      className={`initiative-card border-l-4 ${config.border} cursor-pointer transition-all duration-200 hover:shadow-sm`}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <span
            className={`px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide rounded-[8px] ${item.type === "move"
                ? "bg-[var(--bg-canvas)] text-[var(--ink-2)]"
                : "bg-[var(--status-info-bg)] text-[var(--status-info)]"
              }`}
          >
            {item.type}
          </span>
          {config.badge}
        </div>
        <button className="p-1 rounded-[var(--radius-sm)] hover:bg-[var(--state-hover)] text-[var(--ink-3)]">
          <MoreHorizontal size={16} />
        </button>
      </div>

      <h3 className="rf-h4 mb-2">{item.name}</h3>

      <div className="flex items-center gap-4 text-[var(--ink-2)] rf-body-sm mb-3">
        <div className="flex items-center gap-1.5">
          <User size={14} />
          <span>{item.owner}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <Clock size={14} />
          <span>{formatDate(item.lastUpdate)}</span>
        </div>
      </div>

      {/* Health Score Bar */}
      <div className="mb-3">
        <div className="flex items-center justify-between mb-1">
          <span className="rf-mono-xs text-[var(--ink-3)]">Health Score</span>
          <span
            className={`rf-mono-xs font-semibold ${item.healthScore >= 70
                ? "text-[var(--status-success)]"
                : item.healthScore >= 40
                  ? "text-[var(--status-warning)]"
                  : "text-[var(--status-error)]"
              }`}
          >
            {item.healthScore}%
          </span>
        </div>
        <div className="w-full h-1.5 bg-[var(--bg-canvas)] rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full ${item.healthScore >= 70
                ? "bg-[var(--status-success)]"
                : item.healthScore >= 40
                  ? "bg-[var(--status-warning)]"
                  : "bg-[var(--status-error)]"
              }`}
            style={{ width: `${item.healthScore}%` }}
          />
        </div>
      </div>

      {/* Blockers */}
      {item.blockers && item.blockers.length > 0 && (
        <div className="mt-3 pt-3 border-t border-[var(--border-1)]">
          <div className="flex items-start gap-2">
            <StatusIcon size={14} className="text-[var(--status-error)] mt-0.5 flex-shrink-0" />
            <div className="space-y-1">
              {item.blockers.map((blocker, i) => (
                <p key={i} className="rf-body-sm text-[var(--ink-2)]">
                  {blocker}
                </p>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Quick Action */}
      <div className="mt-4 pt-3 border-t border-[var(--border-1)] flex items-center justify-between">
        <Button variant="tertiary" size="sm">
          View Details
        </Button>
        <Button variant="secondary" size="sm">
          Take Action
          <ArrowRight size={14} />
        </Button>
      </div>
    </Card>
  );
}

// Main Matrix Page
export default function MatrixPage() {
  const { workspaceId } = useWorkspace();
  const pageRef = useRef<HTMLDivElement>(null);
  const [initiatives, setInitiatives] = useState<InitiativeItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<"all" | InitiativeItem["status"]>("all");

  // Fetch and derive initiatives from moves + campaigns
  useEffect(() => {
    if (!workspaceId) return;
    let cancelled = false;
    setLoading(true);
    setError(null);

    Promise.allSettled([
      movesService.list(workspaceId),
      campaignsService.list(workspaceId),
    ]).then(([movesResult, campaignsResult]) => {
      if (cancelled) return;

      const moves = movesResult.status === "fulfilled" ? movesResult.value : [];
      const campaigns = campaignsResult.status === "fulfilled" ? campaignsResult.value : [];

      const statusMap = (s: string): InitiativeItem["status"] => {
        if (s === "active" || s === "completed") return "on-track";
        if (s === "paused") return "stuck";
        if (s === "draft") return "needs-decision";
        return "on-track";
      };

      const items: InitiativeItem[] = [
        ...moves.map((m) => ({
          id: m.id,
          name: m.name,
          type: "move" as const,
          status: statusMap(m.status),
          owner: "-",
          lastUpdate: m.createdAt ? new Date(m.createdAt) : new Date(),
          healthScore: m.progress ?? 50,
        })),
        ...campaigns.map((c) => ({
          id: c.id,
          name: c.title,
          type: "campaign" as const,
          status: statusMap(c.status),
          owner: "-",
          lastUpdate: c.created_at ? new Date(c.created_at) : new Date(),
          healthScore: 70,
        })),
      ];

      setInitiatives(items);
      setLoading(false);
    }).catch((err) => {
      if (!cancelled) {
        setError(err?.message ?? "Failed to load matrix");
        setLoading(false);
      }
    });

    return () => { cancelled = true; };
  }, [workspaceId]);

  // Filter initiatives
  const filteredInitiatives =
    filter === "all"
      ? initiatives
      : initiatives.filter((item) => item.status === filter);

  // Derive status counts
  const statusCount: StatusCount = {
    onTrack: initiatives.filter((i) => i.status === "on-track").length,
    stuck: initiatives.filter((i) => i.status === "stuck").length,
    atRisk: initiatives.filter((i) => i.status === "at-risk").length,
    needsDecision: initiatives.filter((i) => i.status === "needs-decision").length,
  };

  // GSAP Entrance Animation
  useEffect(() => {
    if (loading) return;
    const ctx = gsap.context(() => {
      const tl = gsap.timeline({ defaults: { ease: "power2.out" } });

      tl.fromTo(
        ".matrix-header",
        { y: -20, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.5 }
      );

      tl.fromTo(
        ".status-card",
        { y: 30, opacity: 0, scale: 0.95 },
        { y: 0, opacity: 1, scale: 1, duration: 0.4, stagger: 0.1 },
        "-=0.2"
      );

      tl.fromTo(
        ".initiative-card",
        { x: -20, opacity: 0 },
        { x: 0, opacity: 1, duration: 0.3, stagger: 0.08 },
        "-=0.2"
      );
    }, pageRef);

    return () => ctx.revert();
  }, [filter, loading]);

  const statusCards = [
    {
      title: "On Track",
      count: statusCount.onTrack,
      variant: "success" as const,
      icon: CheckCircle2,
      filterKey: "on-track" as const,
    },
    {
      title: "Stuck",
      count: statusCount.stuck,
      variant: "error" as const,
      icon: AlertCircle,
      filterKey: "stuck" as const,
    },
    {
      title: "At Risk",
      count: statusCount.atRisk,
      variant: "warning" as const,
      icon: AlertTriangle,
      filterKey: "at-risk" as const,
    },
    {
      title: "Needs Decision",
      count: statusCount.needsDecision,
      variant: "default" as const,
      icon: HelpCircle,
      filterKey: "needs-decision" as const,
    },
  ];

  // Loading State
  if (loading) {
    return (
      <Layout mode="live" activeNavItem="matrix">
        <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
          <Loader2 size={32} className="animate-spin text-[#847C82]" />
          <p className="text-[14px] text-[#847C82]">Loading matrix…</p>
        </div>
      </Layout>
    );
  }

  // Error State
  if (error) {
    return (
      <Layout mode="live" activeNavItem="matrix">
        <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
          <AlertCircle size={32} className="text-[#8B3D3D]" />
          <p className="text-[14px] text-[#8B3D3D]">{error}</p>
          <Button variant="secondary" onClick={() => window.location.reload()}>Retry</Button>
        </div>
      </Layout>
    );
  }

  return (
    <Layout mode="live" activeNavItem="matrix">
      <div ref={pageRef} className="h-full overflow-y-auto">
        <div className="max-w-[1200px] mx-auto p-6 pb-12">
          {/* Header */}
          <header className="matrix-header mb-8">
            <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
              <div>
                <h1 className="rf-h2 mb-1">Matrix</h1>
                <p className="rf-body text-[var(--ink-2)]">
                  What&apos;s happening across all initiatives
                </p>
              </div>
              <div className="flex items-center gap-3">
                <Button variant="secondary" size="sm">
                  <RefreshCw size={14} />
                  Refresh
                </Button>
                <Button variant="primary" size="sm">Export Report</Button>
              </div>
            </div>
          </header>

          {/* Status Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            {statusCards.map((card) => (
              <div
                key={card.title}
                onClick={() =>
                  setFilter(
                    filter === card.filterKey ? "all" : card.filterKey
                  )
                }
                className={`cursor-pointer transition-all ${filter === card.filterKey ? "ring-2 ring-[var(--ink-1)] rounded-[var(--radius-md)]" : ""}`}
              >
                <StatusCard
                  title={card.title}
                  count={card.count}
                  variant={card.variant}
                  icon={card.icon}
                />
              </div>
            ))}
          </div>

          {/* Filters */}
          <div className="flex items-center gap-4 mb-6">
            <span className="rf-label text-[var(--ink-3)]">Filter:</span>
            <div className="flex items-center gap-2">
              {["all", "on-track", "stuck", "at-risk", "needs-decision"].map(
                (f) => (
                  <button
                    key={f}
                    onClick={() => setFilter(f as typeof filter)}
                    className={`px-3 py-1.5 rounded-[var(--radius-sm)] text-[14px] font-medium transition-colors ${filter === f
                        ? "bg-[var(--ink-1)] text-[var(--ink-inverse)]"
                        : "bg-[var(--bg-surface)] text-[var(--ink-2)] hover:bg-[var(--state-hover)]"
                      }`}
                  >
                    {f === "all"
                      ? "All"
                      : f
                        .split("-")
                        .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
                        .join(" ")}
                  </button>
                )
              )}
            </div>
          </div>

          {/* Initiative Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredInitiatives.map((item) => (
              <InitiativeCard key={item.id} item={item} />
            ))}
          </div>

          {/* Empty State */}
          {filteredInitiatives.length === 0 && (
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <div className="w-16 h-16 rounded-full bg-[var(--bg-surface)] flex items-center justify-center mb-4">
                <CheckCircle2 size={32} className="text-[var(--ink-3)]" />
              </div>
              <h3 className="rf-h4 mb-2">No initiatives found</h3>
              <p className="rf-body-sm text-[var(--ink-2)]">
                Try adjusting your filters or create a new initiative.
              </p>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
