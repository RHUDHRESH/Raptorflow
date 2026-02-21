"use client";

import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { Layout } from "@/components/raptor/shell/Layout";
import { Card } from "@/components/raptor/ui/Card";
import { Button } from "@/components/raptor/ui/Button";
import { Badge } from "@/components/raptor/ui/Badge";
import { Progress } from "@/components/raptor/ui/Progress";
import { Table, type Column } from "@/components/raptor/ui/Table";
import { Tabs } from "@/components/raptor/ui/Tabs";
import {
  Megaphone,
  Target,
  CheckCircle2,
  Clock,
  TrendingUp,
  AlertCircle,
  Plus,
  Filter,
  MoreHorizontal,
  ArrowRight,
  Link as LinkIcon,
  ChevronDown,
  ChevronUp,
  LayoutGrid,
  List,
  CalendarDays,
  Loader2,
} from "lucide-react";
import { useWorkspace } from "@/components/workspace/WorkspaceProvider";
import { campaignsService, type ApiCampaign } from "@/services/campaigns.service";

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════════

interface Phase {
  id: string;
  name: string;
  startDate: Date;
  endDate: Date;
  status: "pending" | "active" | "completed";
}

interface Task {
  id: string;
  title: string;
  phaseId: string;
  status: "todo" | "in-progress" | "done";
  assignedTo?: string;
  dueDate?: Date;
  hypothesis?: string;
}

interface Campaign {
  id: string;
  name: string;
  moveId: string;
  moveName: string;
  status: "draft" | "active" | "paused" | "completed";
  objective: string;
  metric: {
    name: string;
    target: number;
    current: number;
    unit: string;
  };
  timeline: {
    startDate: Date;
    endDate: Date;
    phases: Phase[];
  };
  tasks: Task[];
  hypothesis: string;
  deadline: Date;
}

// ═══════════════════════════════════════════════════════════════════════════════
// ADAPTER: Backend ApiCampaign → Frontend Campaign
// ═══════════════════════════════════════════════════════════════════════════════

function apiToCampaign(api: ApiCampaign): Campaign {
  const now = new Date();
  const created = api.created_at ? new Date(api.created_at) : now;
  const deadline = new Date(created.getTime() + 90 * 24 * 60 * 60 * 1000);
  return {
    id: api.id,
    name: api.title,
    moveId: "",
    moveName: "",
    status: (api.status as Campaign["status"]) ?? "draft",
    objective: api.objective ?? api.description ?? "",
    metric: { name: "Progress", target: 100, current: 0, unit: "%" },
    timeline: {
      startDate: created,
      endDate: deadline,
      phases: [
        { id: "p1", name: "Plan", startDate: created, endDate: deadline, status: api.status === "active" ? "active" : "pending" },
      ],
    },
    tasks: [],
    hypothesis: api.description ?? "",
    deadline,
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// UTILS
// ═══════════════════════════════════════════════════════════════════════════════

function getStatusVariant(status: string): "default" | "success" | "warning" | "error" | "info" {
  switch (status) {
    case "active":
      return "success";
    case "completed":
      return "info";
    case "paused":
      return "warning";
    case "draft":
      return "default";
    default:
      return "default";
  }
}

function calculateProgress(campaign: Campaign): number {
  const completedPhases = campaign.timeline.phases.filter((p) => p.status === "completed").length;
  return Math.round((completedPhases / campaign.timeline.phases.length) * 100);
}

function formatDate(date: Date): string {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(date);
}

function getDaysUntil(date: Date): number {
  const now = new Date();
  const diff = date.getTime() - now.getTime();
  return Math.ceil(diff / (1000 * 60 * 60 * 24));
}

// ═══════════════════════════════════════════════════════════════════════════════
// COMPONENTS
// ═══════════════════════════════════════════════════════════════════════════════

function PhaseIndicator({ phases, activePhase }: { phases: Phase[]; activePhase: string }) {
  const pulseRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (pulseRef.current) {
      gsap.to(pulseRef.current, {
        scale: 1.2,
        opacity: 0.5,
        duration: 1.5,
        repeat: -1,
        yoyo: true,
        ease: "power1.inOut",
      });
    }
  }, []);

  return (
    <div className="flex items-center gap-1">
      {phases.map((phase, index) => {
        const isCompleted = phase.status === "completed";
        const isActive = phase.status === "active";
        const isLast = index === phases.length - 1;

        return (
          <div key={phase.id} className="flex items-center">
            <div className="flex flex-col items-center gap-1">
              <div
                className={`
                  relative w-3 h-3 rounded-full border-2 transition-all duration-300
                  ${isCompleted ? "bg-[var(--rf-charcoal)] border-[var(--rf-charcoal)]" : ""}
                  ${isActive ? "bg-[var(--rf-charcoal)] border-[var(--rf-charcoal)]" : ""}
                  ${!isCompleted && !isActive ? "bg-transparent border-[var(--border-2)]" : ""}
                `}
              >
                {isActive && (
                  <div
                    ref={pulseRef}
                    className="absolute inset-0 rounded-full bg-[var(--rf-charcoal)] opacity-30"
                  />
                )}
                {isCompleted && (
                  <svg
                    className="absolute inset-0 w-full h-full p-0.5 text-[var(--rf-ivory)]"
                    viewBox="0 0 12 12"
                    fill="none"
                  >
                    <path
                      d="M2 6L5 9L10 3"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                )}
              </div>
              <span className="text-[10px] text-[var(--ink-3)] font-medium whitespace-nowrap">
                {phase.name}
              </span>
            </div>
            {!isLast && (
              <div
                className={`
                  w-6 h-0.5 mx-1 transition-all duration-300
                  ${isCompleted ? "bg-[var(--rf-charcoal)]" : "bg-[var(--bg-canvas)]"}
                `}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}

function TaskCheckbox({
  task,
  onToggle,
}: {
  task: Task;
  onToggle: (taskId: string) => void;
}) {
  const checkRef = useRef<SVGSVGElement>(null);
  const textRef = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    if (task.status === "done" && checkRef.current) {
      gsap.fromTo(
        checkRef.current,
        { scale: 0, opacity: 0 },
        { scale: 1, opacity: 1, duration: 0.3, ease: "back.out(1.7)" }
      );
    }
  }, [task.status]);

  const isDone = task.status === "done";

  return (
    <label className="flex items-center gap-3 cursor-pointer group py-2">
      <div
        className={`
          relative w-5 h-5 rounded border-2 flex items-center justify-center
          transition-all duration-200
          ${isDone ? "bg-[var(--rf-charcoal)] border-[var(--rf-charcoal)]" : "bg-transparent border-[var(--border-2)] group-hover:border-[var(--rf-charcoal)]"}
        `}
        onClick={() => onToggle(task.id)}
      >
        {isDone && (
          <svg
            ref={checkRef}
            className="w-3 h-3 text-[var(--rf-ivory)]"
            viewBox="0 0 12 12"
            fill="none"
          >
            <path
              d="M2 6L5 9L10 3"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        )}
      </div>
      <span
        ref={textRef}
        className={`
          text-[14px] transition-all duration-300
          ${isDone ? "text-[var(--ink-3)] line-through" : "text-[var(--ink-1)]"}
        `}
      >
        {task.title}
      </span>
    </label>
  );
}

function CampaignCard({
  campaign,
  isExpanded,
  onToggle,
}: {
  campaign: Campaign;
  isExpanded: boolean;
  onToggle: () => void;
}) {
  const cardRef = useRef<HTMLDivElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);
  const progress = calculateProgress(campaign);
  const metricProgress = Math.round((campaign.metric.current / campaign.metric.target) * 100);
  const daysUntil = getDaysUntil(campaign.deadline);

  useEffect(() => {
    if (contentRef.current) {
      if (isExpanded) {
        gsap.to(contentRef.current, {
          height: "auto",
          opacity: 1,
          duration: 0.4,
          ease: "power2.out",
        });
      } else {
        gsap.to(contentRef.current, {
          height: 0,
          opacity: 0,
          duration: 0.3,
          ease: "power2.in",
        });
      }
    }
  }, [isExpanded]);

  const handleTaskToggle = (taskId: string) => {
    // In real implementation, this would update the store
    console.log("Toggle task:", taskId);
  };

  const activePhase = campaign.timeline.phases.find((p) => p.status === "active") ||
    campaign.timeline.phases[campaign.timeline.phases.length - 1];
  const activePhaseIndex = campaign.timeline.phases.findIndex((p) => p.id === activePhase?.id) + 1;

  return (
    <Card
      variant="interactive"
      padding="lg"
      className={`campaign-card transition-all duration-300 ${isExpanded ? "ring-2 ring-[var(--rf-charcoal)]" : ""}`}
      onClick={onToggle}
    >
      {/* Main Card Content */}
      <div className="flex flex-col lg:flex-row lg:items-center gap-6">
        {/* Left: Status + Name */}
        <div className="flex items-start gap-4 lg:w-[280px] flex-shrink-0">
          <div
            className={`
              w-2.5 h-2.5 rounded-full mt-2 flex-shrink-0
              ${campaign.status === "active" ? "bg-[var(--status-success)]" : ""}
              ${campaign.status === "completed" ? "bg-[var(--status-info)]" : ""}
              ${campaign.status === "paused" ? "bg-[var(--status-warning)]" : ""}
              ${campaign.status === "draft" ? "bg-[#847C82]" : ""}
            `}
          />
          <div>
            <h3 className="text-[18px] font-semibold text-[var(--ink-1)] font-['DM_Sans',system-ui,sans-serif]">
              {campaign.name}
            </h3>
            <div className="flex items-center gap-2 mt-1">
              <Badge variant={getStatusVariant(campaign.status)} size="sm">
                {campaign.status}
              </Badge>
              <span className="text-[12px] text-[var(--ink-3)]">→</span>
              <span className="text-[12px] text-[var(--ink-2)]">{campaign.moveName}</span>
            </div>
          </div>
        </div>

        {/* Center: Progress + Phases */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[12px] text-[var(--ink-3)]">
              Phase {activePhaseIndex} of {campaign.timeline.phases.length}: {activePhase?.name}
            </span>
            <span className="text-[12px] font-medium text-[var(--ink-1)]">{progress}%</span>
          </div>
          <div className="mb-4">
            <Progress value={progress} size="sm" />
          </div>
          <PhaseIndicator phases={campaign.timeline.phases} activePhase={activePhase?.id || ""} />
        </div>

        {/* Right: Metric + Deadline */}
        <div className="lg:w-[200px] flex-shrink-0 flex flex-col items-end gap-2">
          <div className="text-right">
            <div className="flex items-baseline gap-1 justify-end">
              <span className="text-[24px] font-bold text-[var(--ink-1)]">
                {campaign.metric.current}
              </span>
              <span className="text-[14px] text-[var(--ink-3)]">/ {campaign.metric.target}</span>
            </div>
            <div className="text-[12px] text-[var(--ink-2)]">{campaign.metric.name}</div>
          </div>
          <div className="flex items-center gap-1.5 text-[12px] text-[var(--ink-3)]">
            <Clock size={12} />
            <span>
              {daysUntil > 0 ? `${daysUntil} days left` : daysUntil === 0 ? "Due today" : `${Math.abs(daysUntil)} days overdue`}
            </span>
          </div>
        </div>

        {/* Expand Icon */}
        <div className="hidden lg:flex items-center justify-center w-8 h-8">
          {isExpanded ? <ChevronUp size={20} className="text-[var(--ink-3)]" /> : <ChevronDown size={20} className="text-[var(--ink-3)]" />}
        </div>
      </div>

      {/* Expanded Content */}
      <div ref={contentRef} className="overflow-hidden" style={{ height: 0, opacity: 0 }}>
        <div className="pt-6 mt-6 border-t border-[var(--border-1)]">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Left: Details */}
            <div className="space-y-4">
              <div>
                <h4 className="text-[12px] font-semibold uppercase tracking-wide text-[var(--ink-3)] mb-2">
                  Objective
                </h4>
                <p className="text-[14px] text-[var(--ink-1)]">{campaign.objective}</p>
              </div>
              <div>
                <h4 className="text-[12px] font-semibold uppercase tracking-wide text-[var(--ink-3)] mb-2">
                  Hypothesis
                </h4>
                <p className="text-[14px] text-[var(--ink-2)] italic">"{campaign.hypothesis}"</p>
              </div>
              <div className="flex items-center gap-4">
                <div>
                  <h4 className="text-[12px] font-semibold uppercase tracking-wide text-[var(--ink-3)] mb-1">
                    Start Date
                  </h4>
                  <p className="text-[14px] text-[var(--ink-1)]">{formatDate(campaign.timeline.startDate)}</p>
                </div>
                <div>
                  <h4 className="text-[12px] font-semibold uppercase tracking-wide text-[var(--ink-3)] mb-1">
                    Deadline
                  </h4>
                  <p className="text-[14px] text-[var(--ink-1)]">{formatDate(campaign.deadline)}</p>
                </div>
              </div>
            </div>

            {/* Right: Tasks */}
            <div>
              <h4 className="text-[12px] font-semibold uppercase tracking-wide text-[var(--ink-3)] mb-3">
                Tasks
              </h4>
              <div className="space-y-1">
                {campaign.tasks.map((task) => (
                  <TaskCheckbox key={task.id} task={task} onToggle={handleTaskToggle} />
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
}

function StatsCard({
  label,
  value,
  trend,
  icon: Icon,
}: {
  label: string;
  value: string | number;
  trend?: { value: string; positive: boolean };
  icon: React.ElementType;
}) {
  return (
    <Card padding="md" className="stats-card">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-[12px] text-[var(--ink-3)] uppercase tracking-wide mb-1">{label}</p>
          <p className="text-[28px] font-bold text-[var(--ink-1)]">{value}</p>
          {trend && (
            <div className={`flex items-center gap-1 mt-1 ${trend.positive ? "text-[var(--status-success)]" : "text-[var(--status-warning)]"}`}>
              <TrendingUp size={14} />
              <span className="text-[12px] font-medium">{trend.value}</span>
            </div>
          )}
        </div>
        <div className="p-2 bg-[var(--bg-canvas)] rounded-[10px]">
          <Icon size={20} className="text-[var(--ink-2)]" />
        </div>
      </div>
    </Card>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// MAIN PAGE
// ═══════════════════════════════════════════════════════════════════════════════

export default function CampaignsPage() {
  const { workspaceId } = useWorkspace();
  const pageRef = useRef<HTMLDivElement>(null);
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<"timeline" | "list">("timeline");
  const [expandedCampaign, setExpandedCampaign] = useState<string | null>(null);
  const [filterStatus, setFilterStatus] = useState<string>("all");

  // Fetch campaigns from API
  useEffect(() => {
    if (!workspaceId) return;
    let cancelled = false;
    setLoading(true);
    setError(null);

    campaignsService
      .list(workspaceId)
      .then((data) => {
        if (!cancelled) setCampaigns(data.map(apiToCampaign));
      })
      .catch((err) => {
        if (!cancelled) setError(err?.message ?? "Failed to load campaigns");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => { cancelled = true; };
  }, [workspaceId]);

  // Stats
  const activeCount = campaigns.filter((c) => c.status === "active").length;
  const draftCount = campaigns.filter((c) => c.status === "draft").length;
  const completedCount = campaigns.filter((c) => c.status === "completed").length;
  const totalCount = campaigns.length;

  // Filter campaigns
  const filteredCampaigns = campaigns.filter((c) => {
    if (filterStatus === "all") return true;
    return c.status === filterStatus;
  });

  // Entrance animations
  useEffect(() => {
    if (loading) return;
    const tl = gsap.timeline({ defaults: { ease: "power2.out" } });

    tl.fromTo(
      ".campaigns-header",
      { y: -20, opacity: 0 },
      { y: 0, opacity: 1, duration: 0.5 }
    )
      .fromTo(
        ".stats-row",
        { y: 20, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.4 },
        "-=0.3"
      )
      .fromTo(
        ".campaign-card",
        { x: -30, opacity: 0 },
        { x: 0, opacity: 1, duration: 0.5, stagger: 0.12 },
        "-=0.2"
      );

    return () => {
      tl.kill();
    };
  }, [filterStatus, loading]);

  const handleCampaignToggle = (campaignId: string) => {
    setExpandedCampaign(expandedCampaign === campaignId ? null : campaignId);
  };

  // Table columns for list view
  const tableColumns: Column<Campaign>[] = [
    {
      key: "name",
      header: "Campaign",
      width: "30%",
      render: (row: Campaign) => (
        <div>
          <p className="font-semibold text-[var(--ink-1)]">{row.name}</p>
          <p className="text-[12px] text-[var(--ink-3)]">{row.objective}</p>
        </div>
      ),
    },
    {
      key: "moveName",
      header: "Move",
      width: "20%",
    },
    {
      key: "status",
      header: "Status",
      width: "12%",
      render: (row: Campaign) => (
        <Badge variant={getStatusVariant(row.status)} size="sm">
          {row.status}
        </Badge>
      ),
    },
    {
      key: "progress",
      header: "Progress",
      width: "15%",
      render: (row: Campaign) => (
        <div className="flex items-center gap-2">
          <div className="flex-1 h-2 bg-[var(--bg-canvas)] rounded-full overflow-hidden">
            <div
              className="h-full bg-[var(--rf-charcoal)] rounded-full"
              style={{ width: `${calculateProgress(row)}%` }}
            />
          </div>
          <span className="text-[12px] text-[var(--ink-3)]">{calculateProgress(row)}%</span>
        </div>
      ),
    },
    {
      key: "metric",
      header: "Metric",
      width: "15%",
      align: "right" as const,
      render: (row: Campaign) => (
        <div className="text-right">
          <p className="text-[14px] font-semibold text-[var(--ink-1)]">
            {row.metric.current} / {row.metric.target}
          </p>
          <p className="text-[11px] text-[var(--ink-3)]">{row.metric.name}</p>
        </div>
      ),
    },
    {
      key: "deadline",
      header: "Deadline",
      width: "15%",
      align: "right" as const,
      render: (row: Campaign) => (
        <div className="text-right">
          <p className="text-[14px] text-[var(--ink-1)]">{formatDate(row.deadline)}</p>
          <p className="text-[11px] text-[var(--ink-3)]">
            {getDaysUntil(row.deadline) > 0
              ? `${getDaysUntil(row.deadline)} days left`
              : "Overdue"}
          </p>
        </div>
      ),
    },
  ];

  // ── Loading State ──
  if (loading) {
    return (
      <Layout mode="draft" activeNavItem="campaigns">
        <div className="p-6 lg:p-8 max-w-[1400px] mx-auto flex flex-col items-center justify-center min-h-[60vh] gap-4">
          <Loader2 size={32} className="animate-spin text-[var(--ink-3)]" />
          <p className="text-[14px] text-[var(--ink-3)]">Loading campaigns…</p>
        </div>
      </Layout>
    );
  }

  // ── Error State ──
  if (error) {
    return (
      <Layout mode="draft" activeNavItem="campaigns">
        <div className="p-6 lg:p-8 max-w-[1400px] mx-auto flex flex-col items-center justify-center min-h-[60vh] gap-4">
          <AlertCircle size={32} className="text-[var(--status-error)]" />
          <p className="text-[14px] text-[var(--status-error)]">{error}</p>
          <Button variant="secondary" onClick={() => window.location.reload()}>Retry</Button>
        </div>
      </Layout>
    );
  }

  return (
    <Layout mode="draft" activeNavItem="campaigns">
      <div ref={pageRef} className="p-6 lg:p-8 max-w-[1400px] mx-auto">
        {/* Header */}
        <header className="campaigns-header mb-8">
          <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-4">
            <div>
              <h1 className="rf-h2 text-[var(--ink-1)] mb-2">Campaigns</h1>
              <p className="rf-body text-[var(--ink-2)]">Outcome-linked execution plans</p>
            </div>
            <div className="flex items-center gap-3">
              <div className="relative">
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="rf-input pr-10 w-40 appearance-none cursor-pointer"
                >
                  <option value="all">All Status</option>
                  <option value="active">Active</option>
                  <option value="draft">Draft</option>
                  <option value="paused">Paused</option>
                  <option value="completed">Completed</option>
                </select>
                <Filter size={16} className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--ink-3)] pointer-events-none" />
              </div>
              <Button variant="primary" leftIcon={<Plus size={16} />}>
                Create Campaign
              </Button>
            </div>
          </div>
        </header>

        {/* Stats Row */}
        <div className="stats-row grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatsCard
            label="Active"
            value={activeCount}
            icon={Megaphone}
            trend={{ value: "+2 this month", positive: true }}
          />
          <StatsCard label="Draft" value={draftCount} icon={Clock} />
          <StatsCard label="Completed" value={completedCount} icon={CheckCircle2} />
          <StatsCard label="Total" value={totalCount} icon={Target} />
        </div>

        {/* View Toggle */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-1 p-1 bg-[var(--bg-canvas)] rounded-[10px]">
            <button
              onClick={() => setViewMode("timeline")}
              className={`
                flex items-center gap-2 px-3 py-1.5 rounded-[8px] text-[14px] font-medium transition-all
                ${viewMode === "timeline" ? "bg-[var(--bg-surface)] text-[var(--ink-1)] shadow-sm" : "text-[var(--ink-3)] hover:text-[var(--ink-2)]"}
              `}
            >
              <LayoutGrid size={14} />
              Timeline
            </button>
            <button
              onClick={() => setViewMode("list")}
              className={`
                flex items-center gap-2 px-3 py-1.5 rounded-[8px] text-[14px] font-medium transition-all
                ${viewMode === "list" ? "bg-[var(--bg-surface)] text-[var(--ink-1)] shadow-sm" : "text-[var(--ink-3)] hover:text-[var(--ink-2)]"}
              `}
            >
              <List size={14} />
              List
            </button>
          </div>
          <span className="text-[12px] text-[var(--ink-3)]">
            Showing {filteredCampaigns.length} campaigns
          </span>
        </div>

        {/* Campaign Views */}
        {viewMode === "timeline" ? (
          <div className="space-y-4">
            {filteredCampaigns.map((campaign) => (
              <CampaignCard
                key={campaign.id}
                campaign={campaign}
                isExpanded={expandedCampaign === campaign.id}
                onToggle={() => handleCampaignToggle(campaign.id)}
              />
            ))}
          </div>
        ) : (
          <Card padding="none">
            <Table data={filteredCampaigns} columns={tableColumns} zebra />
          </Card>
        )}

        {/* Empty State */}
        {filteredCampaigns.length === 0 && (
          <Card padding="lg" className="text-center py-16">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-[var(--bg-canvas)] flex items-center justify-center">
              <Megaphone size={24} className="text-[var(--ink-3)]" />
            </div>
            <h3 className="text-[18px] font-semibold text-[var(--ink-1)] mb-2">No campaigns found</h3>
            <p className="text-[14px] text-[var(--ink-3)] mb-6">
              Try adjusting your filters or create a new campaign.
            </p>
            <Button variant="secondary" onClick={() => setFilterStatus("all")}>
              Clear Filters
            </Button>
          </Card>
        )}
      </div>
    </Layout>
  );
}
