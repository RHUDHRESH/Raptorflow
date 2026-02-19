"use client";

import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { Layout } from "@/components/raptor/shell/Layout";
import { Card } from "@/components/raptor/ui/Card";
import { Button } from "@/components/raptor/ui/Button";
import { Badge } from "@/components/raptor/ui/Badge";
import { Tag } from "@/components/raptor/ui/Tag";
import { Progress } from "@/components/raptor/ui/Progress";
import { Modal } from "@/components/raptor/ui/Modal";
import { MovesCalendar, CalendarMove } from "@/components/moves/MovesCalendar";
import {
  Zap,
  Target,
  TrendingUp,
  Clock,
  AlertTriangle,
  CheckCircle2,
  Plus,
  Filter,
  ArrowRight,
  Calendar as CalendarIcon,
  List,
  X,
  HelpCircle,
  TrendingDown,
  Minus,
  Play,
  Pause,
  Eye,
  Loader2,
  AlertCircle,
} from "lucide-react";
import { useWorkspace } from "@/components/workspace/WorkspaceProvider";
import { movesService, type Move as ApiMove } from "@/services/moves.service";

/* ═══════════════════════════════════════════════════════════════════════════════
   MOVES PAGE — "Choose Battles" Loop
   System proposes 3-5 moves max (ranked) → User commits to 1-2 moves
   ═══════════════════════════════════════════════════════════════════════════════ */

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════════

interface ProposedMove {
  id: string;
  title: string;
  category: "growth" | "retention" | "positioning" | "conversion";
  expectedPayoff: string;
  effort: "low" | "medium" | "high";
  risk: "low" | "medium" | "high";
  confidence: "high" | "medium" | "low";
  reasoning: string;
}

interface ActiveMove {
  id: string;
  title: string;
  category: "growth" | "retention" | "positioning" | "conversion";
  status: "active" | "paused" | "completed";
  progress: number;
  startDate: Date;
  endDate: Date;
  goal: string;
  campaignsCount: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// ADAPTERS: ApiMove → Frontend types
// ═══════════════════════════════════════════════════════════════════════════════

function apiToProposed(api: ApiMove): ProposedMove {
  return {
    id: api.id,
    title: api.name,
    category: (api.category as ProposedMove["category"]) ?? "growth",
    expectedPayoff: api.goal ?? "",
    effort: "medium",
    risk: "medium",
    confidence: "medium",
    reasoning: api.context ?? api.goal ?? "",
  };
}

function apiToActive(api: ApiMove): ActiveMove {
  const now = new Date();
  const start = api.createdAt ? new Date(api.createdAt) : (api.startDate ? new Date(api.startDate) : now);
  const end = api.endDate ? new Date(api.endDate) : new Date(start.getTime() + (api.duration ?? 14) * 24 * 60 * 60 * 1000);
  return {
    id: api.id,
    title: api.name,
    category: (api.category as ActiveMove["category"]) ?? "growth",
    status: (api.status as ActiveMove["status"]) ?? "active",
    progress: api.progress ?? 0,
    startDate: start,
    endDate: end,
    goal: api.goal ?? "",
    campaignsCount: 0,
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// CATEGORY CONFIG
// ═══════════════════════════════════════════════════════════════════════════════

const CATEGORY_CONFIG: Record<string, { icon: React.ReactNode; label: string; color: string }> = {
  growth: { icon: <TrendingUp size={16} />, label: "Growth", color: "#2A2529" },
  retention: { icon: <CheckCircle2 size={16} />, label: "Retention", color: "#5C565B" },
  positioning: { icon: <Target size={16} />, label: "Positioning", color: "#D2CCC0" },
  conversion: { icon: <Zap size={16} />, label: "Conversion", color: "#847C82" },
};

const EFFORT_BADGES: Record<string, { label: string; color: string }> = {
  low: { label: "Low Effort", color: "#E8F0E9" },
  medium: { label: "Medium Effort", color: "#F5F0E6" },
  high: { label: "High Effort", color: "#F5E6E6" },
};

const RISK_BADGES: Record<string, { label: string; color: string; textColor: string }> = {
  low: { label: "Low Risk", color: "#E8F0E9", textColor: "#3D5A42" },
  medium: { label: "Medium Risk", color: "#F5F0E6", textColor: "#8B6B3D" },
  high: { label: "High Risk", color: "#F5E6E6", textColor: "#8B3D3D" },
};

const CONFIDENCE_BADGES: Record<string, { label: string; variant: "success" | "warning" | "info" }> = {
  high: { label: "High Confidence", variant: "success" },
  medium: { label: "Medium Confidence", variant: "warning" },
  low: { label: "Low Confidence", variant: "info" },
};

// ═══════════════════════════════════════════════════════════════════════════════
// MAIN PAGE COMPONENT
// ═══════════════════════════════════════════════════════════════════════════════

export default function MovesPage() {
  const { workspaceId } = useWorkspace();
  const pageRef = useRef<HTMLDivElement>(null);
  const proposedSectionRef = useRef<HTMLDivElement>(null);
  const activeSectionRef = useRef<HTMLDivElement>(null);

  const [allMoves, setAllMoves] = useState<ApiMove[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<"list" | "calendar">("list");
  const [selectedMove, setSelectedMove] = useState<ActiveMove | null>(null);
  const [showingReasoning, setShowingReasoning] = useState<string | null>(null);
  const [committedIds, setCommittedIds] = useState<string[]>([]);
  const [dismissedIds, setDismissedIds] = useState<string[]>([]);

  // Fetch moves from API
  useEffect(() => {
    if (!workspaceId) return;
    let cancelled = false;
    setLoading(true);
    setError(null);

    movesService
      .list(workspaceId)
      .then((data) => {
        if (!cancelled) setAllMoves(data);
      })
      .catch((err) => {
        if (!cancelled) setError(err?.message ?? "Failed to load moves");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => { cancelled = true; };
  }, [workspaceId]);

  // Split into proposed vs active based on status
  const proposedMoves = allMoves
    .filter((m) => m.status === "proposed" || m.status === "draft")
    .filter((m) => !committedIds.includes(m.id) && !dismissedIds.includes(m.id))
    .map(apiToProposed);

  // Active moves = already active + newly committed proposed
  const activeMoves = [
    ...allMoves
      .filter((m) => ["active", "paused", "completed"].includes(m.status))
      .map(apiToActive),
    ...allMoves
      .filter((m) => committedIds.includes(m.id))
      .map(apiToActive),
  ];

  // Convert active moves to calendar format
  const calendarMoves: CalendarMove[] = activeMoves.map((move) => ({
    id: move.id,
    title: move.title,
    startDate: move.startDate,
    endDate: move.endDate,
    status: move.status,
    category: move.category,
    color: CATEGORY_CONFIG[move.category]?.color,
  }));

  // GSAP: Page entrance animation
  useEffect(() => {
    if (loading) return;
    const ctx = gsap.context(() => {
      const tl = gsap.timeline({ defaults: { ease: "power2.out" } });

      tl.fromTo(
        ".moves-header",
        { y: -20, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.5 }
      )
        .fromTo(
          ".proposed-section",
          { x: -30, opacity: 0 },
          { x: 0, opacity: 1, duration: 0.5 },
          "-=0.3"
        )
        .fromTo(
          ".proposed-card",
          { y: 20, opacity: 0, scale: 0.95 },
          { y: 0, opacity: 1, scale: 1, duration: 0.4, stagger: 0.1 },
          "-=0.3"
        )
        .fromTo(
          ".active-section",
          { y: 30, opacity: 0 },
          { y: 0, opacity: 1, duration: 0.5 },
          "-=0.2"
        );
    }, pageRef);

    return () => ctx.revert();
  }, [loading]);

  // GSAP: Commit animation
  const handleCommit = (moveId: string, cardEl: HTMLElement | null) => {
    if (!cardEl) return;

    const ctx = gsap.context(() => {
      // Animate card shrinking and moving
      gsap.to(cardEl, {
        scale: 0.8,
        opacity: 0,
        x: activeSectionRef.current ? activeSectionRef.current.getBoundingClientRect().left - cardEl.getBoundingClientRect().left : 0,
        y: activeSectionRef.current ? activeSectionRef.current.getBoundingClientRect().top - cardEl.getBoundingClientRect().top : 0,
        duration: 0.5,
        ease: "power2.inOut",
        onComplete: () => {
          setCommittedIds((prev) => [...prev, moveId]);

          // Flash active section
          if (activeSectionRef.current) {
            gsap.fromTo(
              activeSectionRef.current,
              { backgroundColor: "rgba(42, 37, 41, 0.05)" },
              { backgroundColor: "transparent", duration: 0.6, ease: "power2.out" }
            );
          }
        },
      });
    });

    return () => ctx.revert();
  };

  // GSAP: Dismiss animation
  const handleDismiss = (moveId: string, cardEl: HTMLElement | null) => {
    if (!cardEl) return;

    const ctx = gsap.context(() => {
      gsap.to(cardEl, {
        x: 100,
        opacity: 0,
        duration: 0.3,
        ease: "power2.in",
        onComplete: () => {
          setDismissedIds((prev) => [...prev, moveId]);
        },
      });
    });

    return () => ctx.revert();
  };

  const daysRemaining = (endDate: Date) => {
    const diff = Math.ceil((endDate.getTime() - Date.now()) / (1000 * 60 * 60 * 24));
    return diff > 0 ? `${diff} days left` : "Overdue";
  };

  // ── Loading State ──
  if (loading) {
    return (
      <Layout activeNavItem="moves">
        <div className="p-6 max-w-[1400px] mx-auto flex flex-col items-center justify-center min-h-[60vh] gap-4">
          <Loader2 size={32} className="animate-spin text-[#847C82]" />
          <p className="text-[14px] text-[#847C82]">Loading moves…</p>
        </div>
      </Layout>
    );
  }

  // ── Error State ──
  if (error) {
    return (
      <Layout activeNavItem="moves">
        <div className="p-6 max-w-[1400px] mx-auto flex flex-col items-center justify-center min-h-[60vh] gap-4">
          <AlertCircle size={32} className="text-[#8B3D3D]" />
          <p className="text-[14px] text-[#8B3D3D]">{error}</p>
          <Button variant="secondary" onClick={() => window.location.reload()}>Retry</Button>
        </div>
      </Layout>
    );
  }

  return (
    <Layout activeNavItem="moves">
      <div ref={pageRef} className="p-6 max-w-[1400px] mx-auto">
        {/* Header */}
        <header className="moves-header flex flex-col md:flex-row md:items-end justify-between gap-4 mb-8">
          <div>
            <h1 className="text-[32px] font-bold text-[#2A2529] font-['DM_Sans',system-ui,sans-serif] leading-[40px]">
              Moves
            </h1>
            <p className="text-[16px] text-[#5C565B] mt-1 font-['DM_Sans',system-ui,sans-serif]">
              Strategic initiatives ranked by expected payoff
            </p>
          </div>

          <div className="flex items-center gap-3">
            {/* View Toggle */}
            <div className="flex border border-[#D2CCC0] rounded-[10px] overflow-hidden bg-[#F7F5EF]">
              <button
                onClick={() => setViewMode("list")}
                className={`flex items-center gap-2 px-3 py-2 text-[13px] font-medium transition-colors ${viewMode === "list"
                  ? "bg-[#2A2529] text-[#F3F0E7]"
                  : "text-[#5C565B] hover:text-[#2A2529]"
                  }`}
              >
                <List size={16} />
                List
              </button>
              <button
                onClick={() => setViewMode("calendar")}
                className={`flex items-center gap-2 px-3 py-2 text-[13px] font-medium transition-colors ${viewMode === "calendar"
                  ? "bg-[#2A2529] text-[#F3F0E7]"
                  : "text-[#5C565B] hover:text-[#2A2529]"
                  }`}
              >
                <CalendarIcon size={16} />
                Calendar
              </button>
            </div>

            <Button variant="secondary" leftIcon={<Filter size={16} />}>
              Filter
            </Button>
            <Button variant="primary" leftIcon={<Plus size={16} />}>
              Create Move
            </Button>
          </div>
        </header>

        {/* Proposed Moves (AI Suggestions) */}
        {proposedMoves.length > 0 && (
          <section ref={proposedSectionRef} className="proposed-section mb-10">
            <div className="flex items-center gap-3 mb-4">
              <Zap size={20} className="text-[#2A2529]" />
              <h2 className="text-[20px] font-semibold text-[#2A2529] font-['DM_Sans',system-ui,sans-serif]">
                Proposed Moves
              </h2>
              <Badge variant="info" size="sm">
                AI Suggested
              </Badge>
              <span className="text-[13px] text-[#847C82] ml-2">
                Commit to 1-2 moves max
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {proposedMoves.slice(0, 4).map((move) => (
                <ProposedMoveCard
                  key={move.id}
                  move={move}
                  showingReasoning={showingReasoning === move.id}
                  onShowReasoning={() => setShowingReasoning(showingReasoning === move.id ? null : move.id)}
                  onCommit={(el) => handleCommit(move.id, el)}
                  onDismiss={(el) => handleDismiss(move.id, el)}
                />
              ))}
            </div>
          </section>
        )}

        {/* Active Moves */}
        <section ref={activeSectionRef} className="active-section">
          <div className="flex items-center gap-3 mb-4">
            <Target size={20} className="text-[#2A2529]" />
            <h2 className="text-[20px] font-semibold text-[#2A2529] font-['DM_Sans',system-ui,sans-serif]">
              Active Moves
            </h2>
            <Badge variant="success" size="sm">
              {activeMoves.length} Active
            </Badge>
          </div>

          {viewMode === "list" ? (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {activeMoves.map((move) => (
                <ActiveMoveCard
                  key={move.id}
                  move={move}
                  daysRemaining={daysRemaining(move.endDate)}
                  onClick={() => setSelectedMove(move)}
                />
              ))}
            </div>
          ) : (
            <Card padding="lg">
              <MovesCalendar
                moves={calendarMoves}
                onMoveClick={(id) => {
                  const move = activeMoves.find((m) => m.id === id);
                  if (move) setSelectedMove(move);
                }}
              />
            </Card>
          )}
        </section>
      </div>

      {/* Move Detail Modal */}
      <MoveDetailModal
        move={selectedMove}
        onClose={() => setSelectedMove(null)}
      />
    </Layout>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// PROPOSED MOVE CARD
// ═══════════════════════════════════════════════════════════════════════════════

interface ProposedMoveCardProps {
  move: ProposedMove;
  showingReasoning: boolean;
  onShowReasoning: () => void;
  onCommit: (el: HTMLElement | null) => void;
  onDismiss: (el: HTMLElement | null) => void;
}

function ProposedMoveCard({
  move,
  showingReasoning,
  onShowReasoning,
  onCommit,
  onDismiss,
}: ProposedMoveCardProps) {
  const cardRef = useRef<HTMLDivElement>(null);
  const [cardEl, setCardEl] = useState<HTMLElement | null>(null);

  useEffect(() => {
    if (cardRef.current) {
      setCardEl(cardRef.current);
    }
  }, []);

  // GSAP: Card hover lift
  const handleMouseEnter = () => {
    if (!cardRef.current) return;
    gsap.to(cardRef.current, {
      y: -4,
      boxShadow: "0 8px 24px rgba(42, 37, 41, 0.08)",
      duration: 0.2,
      ease: "power2.out",
    });
  };

  const handleMouseLeave = () => {
    if (!cardRef.current) return;
    gsap.to(cardRef.current, {
      y: 0,
      boxShadow: "0 1px 3px rgba(42, 37, 41, 0.04)",
      duration: 0.2,
      ease: "power2.out",
    });
  };

  const category = CATEGORY_CONFIG[move.category];
  const effort = EFFORT_BADGES[move.effort];
  const risk = RISK_BADGES[move.risk];
  const confidence = CONFIDENCE_BADGES[move.confidence];

  return (
    <div
      ref={cardRef}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      className="proposed-card bg-[#F7F5EF] border border-[#E3DED3] rounded-[14px] p-4 relative overflow-hidden"
      style={{ boxShadow: "0 1px 3px rgba(42, 37, 41, 0.04)" }}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div
          className="w-8 h-8 rounded-[8px] flex items-center justify-center"
          style={{ backgroundColor: `${category.color}15`, color: category.color }}
        >
          {category.icon}
        </div>
        <button
          onClick={onShowReasoning}
          className="p-1.5 text-[#847C82] hover:text-[#2A2529] hover:bg-[#EFEDE6] rounded-[8px] transition-colors"
          title="Why this move?"
        >
          <HelpCircle size={16} />
        </button>
      </div>

      {/* Title */}
      <h3 className="text-[16px] font-semibold text-[#2A2529] mb-2 font-['DM_Sans',system-ui,sans-serif] line-clamp-2">
        {move.title}
      </h3>

      {/* Expected Payoff */}
      <div className="mb-3">
        <span className="text-[24px] font-bold text-[#2A2529] font-['DM_Sans',system-ui,sans-serif]">
          {move.expectedPayoff}
        </span>
      </div>

      {/* Tags */}
      <div className="flex flex-wrap gap-2 mb-3">
        <span
          className="px-2 py-1 text-[10px] font-medium rounded-[6px] uppercase tracking-wide"
          style={{ backgroundColor: effort.color, color: "#2A2529" }}
        >
          {effort.label}
        </span>
        <span
          className="px-2 py-1 text-[10px] font-medium rounded-[6px] uppercase tracking-wide"
          style={{ backgroundColor: risk.color, color: risk.textColor }}
        >
          {risk.label}
        </span>
      </div>

      {/* Reasoning Tooltip */}
      {showingReasoning && (
        <div className="mb-3 p-3 bg-[#EFEDE6] rounded-[10px] text-[12px] text-[#5C565B] font-['DM_Sans',system-ui,sans-serif]">
          <div className="flex items-center gap-1 mb-1">
            <Zap size={12} className="text-[#8B6B3D]" />
            <span className="font-semibold text-[#2A2529]">Why this?</span>
          </div>
          {move.reasoning}
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between pt-3 border-t border-[#E3DED3]">
        <Badge variant={confidence.variant} size="sm">
          {confidence.label}
        </Badge>
        <div className="flex items-center gap-2">
          <button
            onClick={() => onDismiss(cardEl)}
            className="p-2 text-[#847C82] hover:text-[#8B3D3D] hover:bg-[#F5E6E6] rounded-[8px] transition-colors"
            title="Dismiss"
          >
            <X size={16} />
          </button>
          <Button size="sm" onClick={() => onCommit(cardEl)}>
            Commit
          </Button>
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// ACTIVE MOVE CARD
// ═══════════════════════════════════════════════════════════════════════════════

interface ActiveMoveCardProps {
  move: ActiveMove;
  daysRemaining: string;
  onClick: () => void;
}

function ActiveMoveCard({ move, daysRemaining, onClick }: ActiveMoveCardProps) {
  const cardRef = useRef<HTMLDivElement>(null);
  const progressRef = useRef<HTMLDivElement>(null);

  // GSAP: Progress bar animation on mount
  useEffect(() => {
    if (!progressRef.current) return;

    gsap.fromTo(
      progressRef.current,
      { width: "0%" },
      { width: `${move.progress}%`, duration: 0.8, ease: "power2.out", delay: 0.3 }
    );
  }, [move.progress]);

  // GSAP: Card hover
  const handleMouseEnter = () => {
    if (!cardRef.current) return;
    gsap.to(cardRef.current, {
      y: -2,
      boxShadow: "0 8px 24px rgba(42, 37, 41, 0.08)",
      duration: 0.2,
      ease: "power2.out",
    });
  };

  const handleMouseLeave = () => {
    if (!cardRef.current) return;
    gsap.to(cardRef.current, {
      y: 0,
      boxShadow: "0 1px 3px rgba(42, 37, 41, 0.04)",
      duration: 0.2,
      ease: "power2.out",
    });
  };

  const category = CATEGORY_CONFIG[move.category];

  const statusVariants: Record<string, { variant: "success" | "warning" | "default" | "info"; label: string; icon: React.ReactNode }> = {
    active: { variant: "success", label: "Active", icon: <Play size={12} /> },
    paused: { variant: "warning", label: "Paused", icon: <Pause size={12} /> },
    completed: { variant: "default", label: "Completed", icon: <CheckCircle2 size={12} /> },
  };

  const status = statusVariants[move.status];

  return (
    <div
      ref={cardRef}
      onClick={onClick}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      className="bg-[#F7F5EF] border border-[#E3DED3] rounded-[14px] p-5 cursor-pointer transition-colors hover:border-[#D2CCC0]"
      style={{ boxShadow: "0 1px 3px rgba(42, 37, 41, 0.04)" }}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-2">
          <Badge variant={status.variant} size="sm">
            <span className="flex items-center gap-1">
              {status.icon}
              {status.label}
            </span>
          </Badge>
          <div
            className="w-6 h-6 rounded-[6px] flex items-center justify-center"
            style={{ backgroundColor: `${category.color}15`, color: category.color }}
          >
            {category.icon}
          </div>
        </div>
        <button
          onClick={(e) => {
            e.stopPropagation();
            onClick();
          }}
          className="p-2 text-[#847C82] hover:text-[#2A2529] hover:bg-[#EFEDE6] rounded-[8px] transition-colors"
        >
          <Eye size={16} />
        </button>
      </div>

      {/* Title & Goal */}
      <h3 className="text-[18px] font-semibold text-[#2A2529] mb-1 font-['DM_Sans',system-ui,sans-serif]">
        {move.title}
      </h3>
      <p className="text-[14px] text-[#5C565B] mb-4 font-['DM_Sans',system-ui,sans-serif] line-clamp-1">
        {move.goal}
      </p>

      {/* Progress */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-[12px] text-[#847C82] font-['DM_Sans',system-ui,sans-serif]">Progress</span>
          <span className="text-[12px] font-semibold text-[#2A2529] font-['DM_Sans',system-ui,sans-serif]">
            {move.progress}%
          </span>
        </div>
        <div className="h-2 bg-[#EFEDE6] rounded-full overflow-hidden">
          <div
            ref={progressRef}
            className="h-full rounded-full transition-all"
            style={{
              width: "0%",
              backgroundColor: category.color
            }}
          />
        </div>
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between pt-3 border-t border-[#E3DED3]">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5 text-[12px] text-[#847C82]">
            <Clock size={14} />
            <span className="font-['DM_Sans',system-ui,sans-serif]">{daysRemaining}</span>
          </div>
          <div className="flex items-center gap-1.5 text-[12px] text-[#847C82]">
            <Target size={14} />
            <span className="font-['DM_Sans',system-ui,sans-serif]">{move.campaignsCount} campaigns</span>
          </div>
        </div>
        <ArrowRight size={16} className="text-[#D2CCC0]" />
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// MOVE DETAIL MODAL
// ═══════════════════════════════════════════════════════════════════════════════

interface MoveDetailModalProps {
  move: ActiveMove | null;
  onClose: () => void;
}

function MoveDetailModal({ move, onClose }: MoveDetailModalProps) {
  const contentRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!move || !contentRef.current) return;

    gsap.fromTo(
      contentRef.current.children,
      { y: 20, opacity: 0 },
      { y: 0, opacity: 1, duration: 0.4, stagger: 0.05, ease: "power2.out" }
    );
  }, [move]);

  if (!move) return null;

  const category = CATEGORY_CONFIG[move.category];

  const milestones = [
    { day: 1, title: "Kickoff & Setup", completed: true },
    { day: 7, title: "First Milestone", completed: move.progress >= 30 },
    { day: 14, title: "Mid-point Review", completed: move.progress >= 50 },
    { day: 21, title: "Final Push", completed: move.progress >= 80 },
    { day: 30, title: "Launch", completed: move.progress >= 100 },
  ];

  return (
    <Modal
      isOpen={!!move}
      onClose={onClose}
      title={move.title}
      size="lg"
      footer={
        <div className="flex items-center justify-between w-full">
          <Button variant="secondary" onClick={onClose}>
            Close
          </Button>
          <div className="flex items-center gap-2">
            {move.status === "active" ? (
              <Button variant="secondary" leftIcon={<Pause size={16} />}>
                Pause
              </Button>
            ) : (
              <Button variant="secondary" leftIcon={<Play size={16} />}>
                Resume
              </Button>
            )}
            <Button variant="primary">Edit Move</Button>
          </div>
        </div>
      }
    >
      <div ref={contentRef} className="space-y-6">
        {/* Status & Category */}
        <div className="flex items-center gap-3">
          <Badge variant={move.status === "active" ? "success" : move.status === "paused" ? "warning" : "default"}>
            {move.status}
          </Badge>
          <Tag active>
            <span className="flex items-center gap-1.5">
              {category.icon}
              {category.label}
            </span>
          </Tag>
        </div>

        {/* Goal */}
        <div>
          <h4 className="text-[12px] font-semibold text-[#847C82] uppercase tracking-wide mb-2 font-['DM_Sans',system-ui,sans-serif]">
            Goal
          </h4>
          <p className="text-[16px] text-[#2A2529] font-['DM_Sans',system-ui,sans-serif]">
            {move.goal}
          </p>
        </div>

        {/* Timeline */}
        <div>
          <h4 className="text-[12px] font-semibold text-[#847C82] uppercase tracking-wide mb-3 font-['DM_Sans',system-ui,sans-serif]">
            Timeline
          </h4>
          <div className="flex items-center gap-2 mb-4">
            <div className="flex items-center gap-2 px-3 py-2 bg-[#EFEDE6] rounded-[8px]">
              <CalendarIcon size={16} className="text-[#5C565B]" />
              <span className="text-[14px] text-[#2A2529] font-['DM_Sans',system-ui,sans-serif]">
                {move.startDate.toLocaleDateString()} — {move.endDate.toLocaleDateString()}
              </span>
            </div>
            <div className="flex items-center gap-2 px-3 py-2 bg-[#EFEDE6] rounded-[8px]">
              <Clock size={16} className="text-[#5C565B]" />
              <span className="text-[14px] text-[#2A2529] font-['DM_Sans',system-ui,sans-serif]">
                {Math.ceil((move.endDate.getTime() - move.startDate.getTime()) / (1000 * 60 * 60 * 24))} days
              </span>
            </div>
          </div>

          {/* Milestones */}
          <div className="space-y-2">
            {milestones.map((milestone, index) => (
              <div
                key={index}
                className="flex items-center gap-3 p-3 bg-[#F7F5EF] rounded-[10px] border border-[#E3DED3]"
              >
                <div
                  className={`w-6 h-6 rounded-full flex items-center justify-center ${milestone.completed ? "bg-[#3D5A42] text-white" : "bg-[#EFEDE6] text-[#847C82]"
                    }`}
                >
                  {milestone.completed ? <CheckCircle2 size={14} /> : <span className="text-[10px]">{milestone.day}</span>}
                </div>
                <span
                  className={`text-[14px] font-['DM_Sans',system-ui,sans-serif] ${milestone.completed ? "text-[#2A2529]" : "text-[#847C82]"
                    }`}
                >
                  {milestone.title}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Linked Campaigns */}
        <div>
          <h4 className="text-[12px] font-semibold text-[#847C82] uppercase tracking-wide mb-3 font-['DM_Sans',system-ui,sans-serif]">
            Linked Campaigns ({move.campaignsCount})
          </h4>
          <div className="grid grid-cols-1 gap-2">
            {move.campaignsCount > 0 ? (
              <>
                <div className="flex items-center gap-3 p-3 bg-[#F7F5EF] rounded-[10px] border border-[#E3DED3] hover:border-[#D2CCC0] cursor-pointer transition-colors">
                  <Target size={16} className="text-[#5C565B]" />
                  <span className="text-[14px] text-[#2A2529] font-['DM_Sans',system-ui,sans-serif]">
                    Campaign Alpha
                  </span>
                  <ArrowRight size={14} className="ml-auto text-[#847C82]" />
                </div>
                <div className="flex items-center gap-3 p-3 bg-[#F7F5EF] rounded-[10px] border border-[#E3DED3] hover:border-[#D2CCC0] cursor-pointer transition-colors">
                  <Target size={16} className="text-[#5C565B]" />
                  <span className="text-[14px] text-[#2A2529] font-['DM_Sans',system-ui,sans-serif]">
                    Campaign Beta
                  </span>
                  <ArrowRight size={14} className="ml-auto text-[#847C82]" />
                </div>
              </>
            ) : (
              <div className="p-4 text-center border border-dashed border-[#D2CCC0] rounded-[10px]">
                <p className="text-[14px] text-[#847C82] font-['DM_Sans',system-ui,sans-serif]">
                  No campaigns linked yet
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Evidence Panel */}
        <div>
          <h4 className="text-[12px] font-semibold text-[#847C82] uppercase tracking-wide mb-3 font-['DM_Sans',system-ui,sans-serif]">
            Evidence
          </h4>
          <div className="p-4 bg-[#F7F5EF] rounded-[10px] border border-[#E3DED3]">
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-[8px] bg-[#E6F0F5] flex items-center justify-center shrink-0">
                <TrendingUp size={16} className="text-[#3D5A6B]" />
              </div>
              <div>
                <p className="text-[14px] text-[#2A2529] font-['DM_Sans',system-ui,sans-serif] mb-1">
                  Progress tracking active
                </p>
                <p className="text-[12px] text-[#847C82] font-['DM_Sans',system-ui,sans-serif]">
                  {move.progress}% complete — {move.progress > 50 ? "On track" : "Just started"}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Assumptions Panel */}
        <div>
          <h4 className="text-[12px] font-semibold text-[#847C82] uppercase tracking-wide mb-3 font-['DM_Sans',system-ui,sans-serif]">
            Key Assumptions
          </h4>
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-[14px] text-[#5C565B] font-['DM_Sans',system-ui,sans-serif]">
              <AlertTriangle size={14} className="text-[#8B6B3D]" />
              <span>Target audience engagement rate stays above 3%</span>
            </div>
            <div className="flex items-center gap-2 text-[14px] text-[#5C565B] font-['DM_Sans',system-ui,sans-serif]">
              <AlertTriangle size={14} className="text-[#8B6B3D]" />
              <span>Content production capacity remains consistent</span>
            </div>
          </div>
        </div>
      </div>
    </Modal>
  );
}
