"use client";

import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import gsap from "gsap";
import {
  Plus,
  Search,
  Calendar,
  TrendingUp,
  Play,
  Pause,
  LayoutGrid,
  List,
  Flag,
  CheckCircle2,
  Layers,
  ArrowUpRight,
  ArrowLeft
} from "lucide-react";

import { cn } from "@/lib/utils";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { BlueprintEmptyState } from "@/components/ui/BlueprintEmptyState";
import { useCampaignStore, CampaignMove, MoveStatus } from "@/stores/campaignStore";
import { PageHeader, PageFooter } from "@/components/ui/PageHeader";
import { CampaignWizard } from "@/components/campaigns/CampaignWizard";

/* ══════════════════════════════════════════════════════════════════════════════
   CAMPAIGN OS — Strategic Command Center
   Enhanced with summary stats, grid/list toggle, and better cards
   ══════════════════════════════════════════════════════════════════════════════ */

type ViewMode = "grid" | "list";
type FilterStatus = "all" | "active" | "planning" | "completed";

export default function CampaignsPage() {
  const router = useRouter();
  const containerRef = useRef<HTMLDivElement>(null);

  const {
    campaigns,
    view,
    activeCampaignId,
    setView,
    setActiveCampaign,
    updateCampaignMoveStatus,
    addCampaign,
    getActiveCampaign
  } = useCampaignStore();

  // Local UI state
  const [viewMode, setViewMode] = useState<ViewMode>("grid");
  const [filterStatus, setFilterStatus] = useState<FilterStatus>("all");
  const [searchQuery, setSearchQuery] = useState("");

  // Handle URL params for view
  const searchParams = typeof window !== 'undefined' ? new URLSearchParams(window.location.search) : null;

  useEffect(() => {
    if (searchParams?.get("view") === "WIZARD") {
      setView("WIZARD");
    }
  }, [setView]);

  const activeCampaign = getActiveCampaign();
  const [draggedMove, setDraggedMove] = useState<CampaignMove | null>(null);

  // Filter campaigns
  const filteredCampaigns = campaigns.filter(camp => {
    if (filterStatus !== "all" && camp.status.toLowerCase() !== filterStatus.toLowerCase()) return false;
    if (searchQuery && !camp.name.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  // Calculate summary stats
  const stats = {
    total: campaigns.length,
    active: campaigns.filter(c => c.status === "Active").length,
    totalMoves: campaigns.reduce((sum, c) => sum + c.moves.length, 0),
    avgProgress: campaigns.length > 0
      ? Math.round(campaigns.reduce((sum, c) => sum + c.progress, 0) / campaigns.length)
      : 0
  };

  // --- DRAG AND DROP HANDLERS ---
  const handleDragStart = (e: React.DragEvent, move: CampaignMove) => {
    setDraggedMove(move);
    e.dataTransfer.effectAllowed = 'move';
    (e.target as HTMLElement).classList.add('opacity-50');
  };

  const handleDragEnd = (e: React.DragEvent) => {
    setDraggedMove(null);
    (e.target as HTMLElement).classList.remove('opacity-50');
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent, status: MoveStatus) => {
    e.preventDefault();
    if (!draggedMove || !activeCampaign) return;
    if (draggedMove.status === status) return;
    updateCampaignMoveStatus(activeCampaign.id, draggedMove.id, status);
  };

  // --- ENTRY ANIMATION ---
  useEffect(() => {
    if (containerRef.current) {
      gsap.fromTo(
        containerRef.current,
        { opacity: 0, y: 20 },
        { opacity: 1, y: 0, duration: 0.5, ease: "power2.out" }
      );
    }
  }, [view]);

  // CampaignWizard is now imported from @/components/campaigns/CampaignWizard
  const handleWizardComplete = (data: {
    name: string;
    goal: string;
    objective: string;
    duration: string;
    intensity: string;
    icp: string;
    channels: string[];
  }) => {
    const newCampaign = {
      id: `CMP-${Math.floor(Math.random() * 1000)}`,
      name: data.name,
      status: "Active" as const,
      progress: 0,
      goal: data.goal,
      moves: [
        { id: `M-${Date.now()}-1`, title: "Strategy Definition", type: "Positioning", status: "Active" as const, start: "Today", end: "Week 2", items_done: 0, items_total: 3, desc: `Initial strategy alignment based on ${data.objective}` },
        { id: `M-${Date.now()}-2`, title: "Asset Creation", type: "Production", status: "Planned" as const, start: "Week 3", end: "Week 5", items_done: 0, items_total: 10, desc: `Producing content for ${data.channels.join(", ")}` }
      ]
    };
    addCampaign(newCampaign);
    setActiveCampaign(newCampaign.id);
    setView("DETAIL");
  };


  // --- Progress Ring Component ---
  const ProgressRing = ({ progress, size = 48 }: { progress: number; size?: number }) => {
    const radius = (size - 4) / 2;
    const circumference = 2 * Math.PI * radius;
    const strokeDashoffset = circumference - (progress / 100) * circumference;

    return (
      <div className="relative" style={{ width: size, height: size }}>
        <svg className="rotate-[-90deg]" width={size} height={size}>
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="var(--structure-subtle)"
            strokeWidth="3"
            fill="none"
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={progress >= 75 ? "var(--success)" : progress >= 40 ? "var(--blueprint)" : "var(--warning)"}
            strokeWidth="3"
            fill="none"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className="transition-all duration-500"
          />
        </svg>
        <span className="absolute inset-0 flex items-center justify-center font-data text-sm text-[var(--ink)]">
          {progress}%
        </span>
      </div>
    );
  };

  // --- RENDER CONTENT ---
  return (
    <div ref={containerRef} className="h-full flex flex-col relative">
      {/* VIEW: CAMPAIGN LIST */}
      {view === "LIST" && (
        <div className="space-y-6">
          {/* Header */}
          <PageHeader
            moduleCode="CAMPAIGNS"
            descriptor="COMMAND"
            title="Campaigns"
            subtitle="Strategic initiatives and war rooms"
            actions={
              <BlueprintButton onClick={() => setView("WIZARD")}>
                <Plus size={16} /> New Campaign
              </BlueprintButton>
            }
          />

          {/* Summary Stats Bar */}
          <div className="grid grid-cols-4 gap-6">
            <BlueprintCard padding="md" showCorners className="border-[var(--structure)]">
              <div className="flex items-center justify-between">
                <div>
                  <span className="font-technical text-[10px] text-[var(--muted)] uppercase tracking-wider block mb-1">CAMPAIGNS</span>
                  <span className="font-serif text-3xl text-[var(--ink)]">{stats.total}</span>
                  <span className="font-technical text-[9px] text-[var(--secondary)] block mt-1">All time</span>
                </div>
                <div className="w-12 h-12 rounded-xl bg-[var(--surface)] flex items-center justify-center">
                  <Flag size={20} className="text-[var(--ink)]" />
                </div>
              </div>
            </BlueprintCard>
            <BlueprintCard padding="md" showCorners className="border-[var(--blueprint)]/30 bg-[var(--blueprint-light)]">
              <div className="flex items-center justify-between">
                <div>
                  <span className="font-technical text-[10px] text-[var(--blueprint)] uppercase tracking-wider block mb-1">ACTIVE</span>
                  <span className="font-serif text-3xl text-[var(--blueprint)]">{stats.active}</span>
                  <span className="font-technical text-[9px] text-[var(--secondary)] block mt-1">Running now</span>
                </div>
                <div className="w-12 h-12 rounded-xl bg-[var(--blueprint)] flex items-center justify-center">
                  <Play size={20} className="text-[var(--paper)]" />
                </div>
              </div>
            </BlueprintCard>
            <BlueprintCard padding="md" showCorners className="border-[var(--structure)]">
              <div className="flex items-center justify-between">
                <div>
                  <span className="font-technical text-[10px] text-[var(--muted)] uppercase tracking-wider block mb-1">TOTAL MOVES</span>
                  <span className="font-serif text-3xl text-[var(--ink)]">{stats.totalMoves}</span>
                  <span className="font-technical text-[9px] text-[var(--secondary)] block mt-1">Across all campaigns</span>
                </div>
                <div className="w-12 h-12 rounded-xl bg-[var(--surface)] flex items-center justify-center">
                  <Layers size={20} className="text-[var(--ink)]" />
                </div>
              </div>
            </BlueprintCard>
            <BlueprintCard padding="md" showCorners className="border-[var(--success)]/30 bg-[var(--success-light)]">
              <div className="flex items-center justify-between">
                <div>
                  <span className="font-technical text-[10px] text-[var(--success)] uppercase tracking-wider block mb-1">AVG PROGRESS</span>
                  <span className="font-serif text-3xl text-[var(--success)]">{stats.avgProgress}%</span>
                  <span className="font-technical text-[9px] text-[var(--secondary)] block mt-1">Completion rate</span>
                </div>
                <div className="w-12 h-12 rounded-xl bg-[var(--success)] flex items-center justify-center">
                  <TrendingUp size={20} className="text-[var(--paper)]" />
                </div>
              </div>
            </BlueprintCard>
          </div>

          {/* Filters & View Toggle */}
          <div className="p-1 bg-[var(--surface)] border border-[var(--structure)] rounded-[var(--radius)] flex items-center justify-between">
            <div className="flex items-center gap-2">
              {(["all", "active", "planning", "completed"] as FilterStatus[]).map(status => (
                <button
                  key={status}
                  onClick={() => setFilterStatus(status)}
                  className={cn(
                    "px-3 py-1.5 text-xs font-medium border rounded-[var(--radius)] transition-all capitalize",
                    filterStatus === status
                      ? "bg-[var(--ink)] text-[var(--paper)] border-[var(--ink)]"
                      : "bg-transparent text-[var(--ink-secondary)] border-[var(--structure-subtle)] hover:border-[var(--structure)]"
                  )}
                >
                  {status}
                </button>
              ))}
            </div>
            <div className="flex items-center gap-2">
              <div className="relative">
                <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--ink-muted)]" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search campaigns..."
                  className="pl-9 pr-4 py-1.5 text-sm border-none bg-transparent focus:outline-none w-48"
                />
              </div>
              <div className="flex border border-[var(--structure-subtle)] rounded-[var(--radius)] overflow-hidden">
                <button
                  onClick={() => setViewMode("grid")}
                  className={cn(
                    "p-2 transition-colors",
                    viewMode === "grid" ? "bg-[var(--ink)] text-[var(--paper)]" : "bg-[var(--paper)] text-[var(--ink-muted)] hover:text-[var(--ink)]"
                  )}
                >
                  <LayoutGrid size={16} />
                </button>
                <button
                  onClick={() => setViewMode("list")}
                  className={cn(
                    "p-2 transition-colors",
                    viewMode === "list" ? "bg-[var(--ink)] text-[var(--paper)]" : "bg-[var(--paper)] text-[var(--ink-muted)] hover:text-[var(--ink)]"
                  )}
                >
                  <List size={16} />
                </button>
              </div>
            </div>
          </div>

          {/* Campaign Grid/List */}
          {filteredCampaigns.length === 0 ? (
            <BlueprintEmptyState
              title="No Campaigns Found"
              code="EMPTY"
              description={campaigns.length === 0
                ? "Initialize your first strategic initiative to begin tracking."
                : "No campaigns match your current filters."}
              action={campaigns.length === 0 ? { label: "Launch Campaign", onClick: () => setView("WIZARD") } : undefined}
            />
          ) : viewMode === "grid" ? (
            <div className="grid grid-cols-2 gap-4">
              {filteredCampaigns.map(camp => (
                <div
                  key={camp.id}
                  onClick={() => { setActiveCampaign(camp.id); setView("DETAIL"); }}
                  className="group bg-[var(--paper)] border border-[var(--structure)] rounded-[var(--radius)] p-4 cursor-pointer hover:border-[var(--blueprint)] transition-all"
                >
                  <div className="flex items-start gap-4">
                    <ProgressRing progress={camp.progress} />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <BlueprintBadge
                          variant={camp.status === 'Active' ? 'success' : 'default'}
                          size="sm"
                        >
                          {camp.status.toUpperCase()}
                        </BlueprintBadge>
                      </div>
                      <h3 className="font-serif text-lg text-[var(--ink)] group-hover:text-[var(--blueprint)] transition-colors truncate">
                        {camp.name}
                      </h3>
                      <p className="text-xs text-[var(--ink-secondary)] line-clamp-1 mt-1">{camp.goal}</p>
                    </div>
                  </div>
                  <div className="flex items-center justify-between mt-4 pt-4 border-t border-[var(--structure-subtle)]">
                    <div className="flex items-center gap-4">
                      <span className="flex items-center gap-1.5 text-xs text-[var(--ink-muted)]">
                        <Layers size={12} /> {camp.moves.length} moves
                      </span>
                      <span className="flex items-center gap-1.5 text-xs text-[var(--ink-muted)]">
                        <CheckCircle2 size={12} /> {camp.moves.filter(m => m.status === "Completed").length} done
                      </span>
                    </div>
                    <ArrowUpRight size={14} className="text-[var(--ink-muted)] group-hover:text-[var(--blueprint)] transition-colors" />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <BlueprintCard padding="none" className="overflow-hidden">
              <table className="w-full">
                <thead className="bg-[var(--surface)] border-b border-[var(--structure)]">
                  <tr>
                    <th className="px-6 py-3 text-left font-technical text-[10px] text-[var(--ink-muted)] uppercase">Campaign</th>
                    <th className="px-6 py-3 text-left font-technical text-[10px] text-[var(--ink-muted)] uppercase">Status</th>
                    <th className="px-6 py-3 text-center font-technical text-[10px] text-[var(--ink-muted)] uppercase">Moves</th>
                    <th className="px-6 py-3 text-center font-technical text-[10px] text-[var(--ink-muted)] uppercase">Progress</th>
                    <th className="px-6 py-3 text-right font-technical text-[10px] text-[var(--ink-muted)] uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[var(--structure-subtle)]">
                  {filteredCampaigns.map((camp) => (
                    <tr
                      key={camp.id}
                      onClick={() => { setActiveCampaign(camp.id); setView("DETAIL"); }}
                      className="hover:bg-[var(--surface)] cursor-pointer transition-colors group"
                    >
                      <td className="px-6 py-4">
                        <h4 className="font-medium text-sm text-[var(--ink)] group-hover:text-[var(--blueprint)] transition-colors">{camp.name}</h4>
                        <p className="text-xs text-[var(--ink-muted)] truncate max-w-[300px]">{camp.goal}</p>
                      </td>
                      <td className="px-6 py-4">
                        <BlueprintBadge variant={camp.status === 'Active' ? 'success' : 'default'} size="sm">
                          {camp.status}
                        </BlueprintBadge>
                      </td>
                      <td className="px-6 py-4 text-center font-data text-sm text-[var(--ink)]">{camp.moves.length}</td>
                      <td className="px-6 py-4">
                        <div className="flex items-center justify-center gap-2">
                          <div className="w-16 h-1.5 bg-[var(--structure-subtle)] rounded-full overflow-hidden">
                            <div className="h-full bg-[var(--blueprint)] transition-all duration-300" style={{ width: `${camp.progress}%` }} />
                          </div>
                          <span className="font-technical text-[10px] text-[var(--ink-muted)] w-8">{camp.progress}%</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <SecondaryButton size="sm">View</SecondaryButton>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </BlueprintCard>
          )}

          <PageFooter document="CAMPAIGNS-COMMAND" />
        </div>
      )}

      {/* VIEW: CAMPAIGN DETAILS (KANBAN) */}
      {view === "DETAIL" && activeCampaign && (
        <div className="flex flex-col h-[calc(100vh-100px)]">
          {/* Header */}
          <div className="flex items-end justify-between mb-6 pb-4 border-b border-[var(--structure)]">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setView("LIST")}
                className="mb-1 p-2 hover:bg-[var(--surface)] rounded-[var(--radius)] text-[var(--ink-muted)] hover:text-[var(--ink)] transition-colors"
                title="Back to Campaigns"
              >
                <ArrowLeft size={24} />
              </button>

              <div>
                <div className="flex items-center gap-3 mb-1">
                  <span className="font-technical text-[var(--blueprint)]">SYS.CAMPAIGN</span>
                  <div className="h-px w-6 bg-[var(--structure)]" />
                  <span className="font-technical text-[var(--ink-muted)]">CONSOLE</span>
                </div>
                <div className="flex items-center gap-3">
                  <h2 className="font-serif text-3xl text-[var(--ink)]">{activeCampaign.name}</h2>
                  <BlueprintBadge variant="success">ACTIVE</BlueprintBadge>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2 mb-1">
              <SecondaryButton size="sm">
                <Calendar size={14} /> Timeline
              </SecondaryButton>
              <BlueprintButton size="sm" onClick={() => { }}>
                <Plus size={14} /> Add Move
              </BlueprintButton>
            </div>
          </div>

          {/* Kanban Board */}
          <div className="flex-1 overflow-x-auto pb-4">
            <div className="flex items-start gap-6 h-full min-w-max">
              {(['Planned', 'Active', 'Completed'] as MoveStatus[]).map(status => {
                const movesInColumn = activeCampaign.moves.filter(m => m.status === status);
                const isCompletedCol = status === 'Completed';
                const isActiveCol = status === 'Active';

                return (
                  <div
                    key={status}
                    onDragOver={handleDragOver}
                    onDrop={(e) => handleDrop(e, status)}
                    className={cn(
                      "w-96 flex flex-col h-full rounded-[var(--radius)] border border-[var(--structure)] transition-colors",
                      isActiveCol ? "bg-[var(--surface-subtle)]" : "bg-[var(--paper)]"
                    )}
                  >
                    <div className="p-4 border-b border-[var(--structure)] flex justify-between items-center bg-[var(--surface)] rounded-t-[var(--radius)]">
                      <div className="flex items-center gap-2">
                        <div className={cn("w-2 h-2 rounded-full",
                          isActiveCol ? "bg-[var(--blueprint)] animate-pulse" :
                            isCompletedCol ? "bg-[var(--success)]" : "bg-[var(--ink-muted)]"
                        )} />
                        <h3 className="font-technical font-bold text-xs text-[var(--ink)] uppercase tracking-wider">{status}</h3>
                      </div>
                      <span className="text-xs font-mono text-[var(--ink-muted)]">[{movesInColumn.length}]</span>
                    </div>

                    <div className="p-4 flex-1 overflow-y-auto space-y-3">
                      {movesInColumn.map(move => (
                        <div
                          key={move.id}
                          draggable
                          onDragStart={(e) => handleDragStart(e, move)}
                          onDragEnd={handleDragEnd}
                          className={cn(
                            "group relative p-4 bg-[var(--paper)] rounded-[var(--radius)] border border-[var(--structure)] shadow-sm hover:border-[var(--blueprint)] hover:shadow-md transition-all cursor-grab active:cursor-grabbing",
                            isCompletedCol && "opacity-75 hover:opacity-100"
                          )}
                        >
                          <div className="flex justify-between items-start mb-3">
                            <BlueprintBadge variant="default" size="sm">{move.type}</BlueprintBadge>
                          </div>
                          <h4 className="font-bold text-sm text-[var(--ink)] mb-1 group-hover:text-[var(--blueprint)] transition-colors">{move.title}</h4>
                          <p className="text-xs text-[var(--ink-secondary)] mb-4 line-clamp-2 leading-relaxed">{move.desc}</p>

                          <div className="flex items-center justify-between pt-3 border-t border-[var(--structure-subtle)]">
                            <div className="flex items-center gap-1.5 text-[10px] font-mono text-[var(--ink-muted)]">
                              <Calendar size={10} /> {move.start}
                            </div>
                            <button
                              onClick={(e) => {
                                e.preventDefault();
                                router.push(`/moves?highlight=${move.id}`);
                              }}
                              className="text-[10px] font-bold text-[var(--ink)] hover:text-[var(--blueprint)] flex items-center gap-1 transition-colors"
                            >
                              OPEN <ArrowUpRight size={10} />
                            </button>
                          </div>
                        </div>
                      ))}
                      {movesInColumn.length === 0 && (
                        <div className="h-24 border-2 border-dashed border-[var(--structure-subtle)] rounded-[var(--radius)] flex items-center justify-center text-[var(--ink-muted)] text-xs font-mono">
                          DROP HERE
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* VIEW: WIZARD OVERLAY */}
      <CampaignWizard
        isOpen={view === "WIZARD"}
        onClose={() => setView("LIST")}
        onComplete={handleWizardComplete}
      />
    </div>
  );
}
