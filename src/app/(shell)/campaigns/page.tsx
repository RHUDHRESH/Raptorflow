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
  ArrowRight,
  ArrowLeft,
  Target,
  Clock,
  MoreHorizontal,
  Trash2,
  Edit3
} from "lucide-react";

import { cn } from "@/lib/utils";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { useCampaignStore, CampaignMove, MoveStatus } from "@/stores/campaignStore";
import { useAuth } from "@/contexts/AuthContext";
import { CampaignWizard } from "@/components/campaigns/CampaignWizard";
import { CampaignTimeline } from "@/components/campaigns/CampaignTimeline";

/* ══════════════════════════════════════════════════════════════════════════════
   CAMPAIGNS — Quiet Luxury Redesign
   Matches Moves page styling for consistent experience
   ══════════════════════════════════════════════════════════════════════════════ */

type ViewTab = "active" | "all" | "completed";

export default function CampaignsPage() {
  const router = useRouter();
  const pageRef = useRef<HTMLDivElement>(null);
  const [mounted, setMounted] = useState(false);

  const {
    campaigns,
    view,
    activeCampaignId,
    setView,
    setActiveCampaign,
    updateCampaignMoveStatus,
    addCampaign,
    createCampaign,
    fetchCampaigns,
    getActiveCampaign
  } = useCampaignStore();

  const { profile } = useAuth();

  const [activeTab, setActiveTab] = useState<ViewTab>("active");
  const [searchQuery, setSearchQuery] = useState("");
  const [draggedMove, setDraggedMove] = useState<CampaignMove | null>(null);
  const [showTimeline, setShowTimeline] = useState(false);

  const activeCampaign = getActiveCampaign();

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (profile?.workspace_id) {
      fetchCampaigns(profile.workspace_id);
    }
  }, [profile?.workspace_id, fetchCampaigns]);

  useEffect(() => {
    if (!pageRef.current || !mounted) return;
    gsap.fromTo(pageRef.current, { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.4, ease: "power2.out" });
  }, [mounted, view]);

  // Filter campaigns based on tab and search
  const filteredCampaigns = campaigns.filter(camp => {
    // Tab filter
    if (activeTab === "active" && camp.status !== "Active") return false;
    if (activeTab === "completed" && camp.status !== "Completed") return false;
    // Search filter
    if (searchQuery && !camp.name.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  // Stats
  const stats = {
    active: campaigns.filter(c => c.status === "Active").length,
    total: campaigns.length,
    completed: campaigns.filter(c => c.status === "Completed").length
  };

  // Drag handlers for kanban
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

  // Wizard completion
  const handleWizardComplete = async (data: {
    name: string;
    goal: string;
    objective: string;
    duration: string;
    intensity: string;
    icp: string;
    channels: string[];
  }) => {
    if (profile?.workspace_id) {
      const created = await createCampaign(data, profile.workspace_id);
      if (created) {
        setActiveCampaign(created.id);
        setView("DETAIL");
        return;
      }
    }
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

  // Progress Ring Component
  const ProgressRing = ({ progress, size = 44 }: { progress: number; size?: number }) => {
    const radius = (size - 4) / 2;
    const circumference = 2 * Math.PI * radius;
    const strokeDashoffset = circumference - (progress / 100) * circumference;

    return (
      <div className="relative" style={{ width: size, height: size }}>
        <svg className="rotate-[-90deg]" width={size} height={size}>
          <circle cx={size / 2} cy={size / 2} r={radius} stroke="var(--border)" strokeWidth="3" fill="none" />
          <circle
            cx={size / 2} cy={size / 2} r={radius}
            stroke={progress >= 75 ? "var(--success)" : progress >= 40 ? "var(--ink)" : "var(--muted)"}
            strokeWidth="3" fill="none"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className="transition-all duration-500"
          />
        </svg>
        <span className="absolute inset-0 flex items-center justify-center text-xs font-medium text-[var(--ink)]">
          {progress}%
        </span>
      </div>
    );
  };

  if (!mounted) return null;

  return (
    <div ref={pageRef} className="min-h-screen bg-[var(--canvas)]" style={{ opacity: 0 }}>
      {/* VIEW: LIST */}
      {view === "LIST" && (
        <>
          {/* Page Header */}
          <div className="border-b border-[var(--border)] bg-[var(--paper)]">
            <div className="max-w-6xl mx-auto px-6 py-6">
              <div className="flex items-start justify-between">
                <div>
                  <h1 className="font-serif text-3xl text-[var(--ink)]">Campaigns</h1>
                  <p className="text-sm text-[var(--muted)] mt-1">Strategic initiatives & 90-day war rooms</p>
                </div>
                <button
                  onClick={() => setView("WIZARD")}
                  className="flex items-center gap-2 px-5 py-2.5 bg-[var(--ink)] text-white rounded-[var(--radius)] hover:bg-[var(--ink)]/90 transition-all font-medium text-sm"
                >
                  <Plus size={16} />
                  New Campaign
                </button>
              </div>

              {/* Tabs */}
              <div className="flex items-center gap-6 mt-6">
                {[
                  { id: "active", label: "Active", count: stats.active },
                  { id: "all", label: "All Campaigns", count: stats.total },
                  { id: "completed", label: "Completed", count: stats.completed }
                ].map(tab => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id as ViewTab)}
                    className={cn(
                      "pb-3 text-sm font-medium border-b-2 transition-colors",
                      activeTab === tab.id
                        ? "text-[var(--ink)] border-[var(--ink)]"
                        : "text-[var(--muted)] border-transparent hover:text-[var(--ink)]"
                    )}
                  >
                    {tab.label}
                    <span className={cn(
                      "ml-2 px-1.5 py-0.5 text-xs rounded",
                      activeTab === tab.id ? "bg-[var(--ink)] text-white" : "bg-[var(--surface)] text-[var(--muted)]"
                    )}>
                      {tab.count}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Search & Content */}
          <div className="max-w-6xl mx-auto px-6 py-8">
            {/* Search Bar */}
            <div className="flex items-center justify-between mb-6">
              <div className="relative">
                <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--muted)]" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search campaigns..."
                  className="pl-10 pr-4 py-2 w-64 text-sm bg-[var(--surface)] border border-[var(--border)] rounded-[var(--radius)] focus:outline-none focus:border-[var(--ink)]"
                />
              </div>
              <div className="flex items-center gap-2 text-sm text-[var(--muted)]">
                <Layers size={14} />
                {filteredCampaigns.length} campaigns
              </div>
            </div>

            {/* Campaign Grid */}
            {filteredCampaigns.length === 0 ? (
              <div className="text-center py-16">
                <div className="w-16 h-16 mx-auto mb-6 rounded-[var(--radius)] bg-[var(--surface)] border border-[var(--border)] flex items-center justify-center">
                  <Flag size={24} className="text-[var(--muted)]" />
                </div>
                <h2 className="font-serif text-xl text-[var(--ink)] mb-2">No campaigns found</h2>
                <p className="text-[var(--muted)] max-w-sm mx-auto mb-6">
                  {campaigns.length === 0
                    ? "Launch your first campaign to start tracking strategic initiatives."
                    : "No campaigns match your current filters."}
                </p>
                {campaigns.length === 0 && (
                  <button
                    onClick={() => setView("WIZARD")}
                    className="flex items-center gap-2 px-5 py-2.5 mx-auto bg-[var(--ink)] text-white rounded-[var(--radius)] hover:bg-[var(--ink)]/90 transition-all font-medium text-sm"
                  >
                    <Plus size={16} />
                    Launch Campaign
                  </button>
                )}
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredCampaigns.map((camp, idx) => (
                  <BlueprintCard
                    key={camp.id}
                    showCorners
                    padding="none"
                    className="cursor-pointer hover:border-[var(--ink)] transition-all group overflow-hidden"
                    onClick={() => { setActiveCampaign(camp.id); setView("DETAIL"); }}
                  >
                    <div className="p-5">
                      <div className="flex items-start gap-4">
                        <ProgressRing progress={camp.progress} />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <BlueprintBadge
                              variant={camp.status === 'Active' ? 'success' : camp.status === 'Completed' ? 'info' : 'default'}
                              size="sm"
                            >
                              {camp.status === 'Active' && <Play size={10} className="mr-1" />}
                              {camp.status}
                            </BlueprintBadge>
                          </div>
                          <h3 className="font-medium text-[var(--ink)] group-hover:text-[var(--ink)] transition-colors truncate">
                            {camp.name}
                          </h3>
                          <p className="text-xs text-[var(--muted)] line-clamp-1 mt-1">{camp.goal}</p>
                        </div>
                      </div>
                    </div>

                    <div className="px-5 py-3 border-t border-[var(--border)] bg-[var(--surface)] flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <span className="flex items-center gap-1.5 text-xs text-[var(--muted)]">
                          <Layers size={12} />
                          {camp.moves.length} moves
                        </span>
                        <span className="flex items-center gap-1.5 text-xs text-[var(--muted)]">
                          <CheckCircle2 size={12} />
                          {camp.moves.filter(m => m.status === "Completed").length} done
                        </span>
                      </div>
                      <ArrowRight size={14} className="text-[var(--muted)] group-hover:text-[var(--ink)] transition-colors" />
                    </div>
                  </BlueprintCard>
                ))}
              </div>
            )}
          </div>
        </>
      )}

      {/* VIEW: DETAIL (KANBAN) */}
      {view === "DETAIL" && activeCampaign && (
        <div className="min-h-screen">
          {/* Header */}
          <div className="border-b border-[var(--border)] bg-[var(--paper)]">
            <div className="max-w-7xl mx-auto px-6 py-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <button
                    onClick={() => setView("LIST")}
                    className="p-2 hover:bg-[var(--surface)] rounded-[var(--radius)] text-[var(--muted)] hover:text-[var(--ink)] transition-colors"
                  >
                    <ArrowLeft size={18} />
                  </button>
                  <div>
                    <div className="flex items-center gap-3 mb-1">
                      <h1 className="font-serif text-2xl text-[var(--ink)]">{activeCampaign.name}</h1>
                      <BlueprintBadge variant="success" size="sm">
                        <Play size={10} className="mr-1" />
                        Active
                      </BlueprintBadge>
                    </div>
                    <p className="text-sm text-[var(--muted)]">{activeCampaign.goal}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setShowTimeline(true)}
                    className="flex items-center gap-2 px-4 py-2 border border-[var(--border)] text-[var(--ink)] rounded-[var(--radius)] hover:border-[var(--ink)] transition-colors text-sm"
                  >
                    <Calendar size={14} />
                    Timeline
                  </button>
                  <button className="flex items-center gap-2 px-4 py-2 bg-[var(--ink)] text-white rounded-[var(--radius)] hover:bg-[var(--ink)]/90 transition-all text-sm font-medium">
                    <Plus size={14} />
                    Add Move
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Kanban Board */}
          <div className="max-w-7xl mx-auto px-6 py-8">
            <div className="flex items-start gap-6 overflow-x-auto pb-4">
              {(['Planned', 'Active', 'Completed'] as MoveStatus[]).map(status => {
                const movesInColumn = activeCampaign.moves.filter(m => m.status === status);
                const isActiveCol = status === 'Active';
                const isCompletedCol = status === 'Completed';

                return (
                  <div
                    key={status}
                    onDragOver={handleDragOver}
                    onDrop={(e) => handleDrop(e, status)}
                    className="w-80 flex-shrink-0"
                  >
                    {/* Column Header */}
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-2">
                        <div className={cn(
                          "w-2 h-2 rounded-full",
                          isActiveCol ? "bg-[var(--ink)] animate-pulse" :
                            isCompletedCol ? "bg-green-500" : "bg-[var(--muted)]"
                        )} />
                        <h3 className="text-sm font-medium text-[var(--ink)] uppercase tracking-wide">{status}</h3>
                      </div>
                      <span className="text-xs text-[var(--muted)]">{movesInColumn.length}</span>
                    </div>

                    {/* Column Content */}
                    <div className="space-y-3">
                      {movesInColumn.map(move => (
                        <div
                          key={move.id}
                          draggable
                          onDragStart={(e) => handleDragStart(e, move)}
                          onDragEnd={handleDragEnd}
                          className={cn(
                            "p-4 bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius)] cursor-grab active:cursor-grabbing hover:border-[var(--ink)] transition-all group",
                            isCompletedCol && "opacity-75 hover:opacity-100"
                          )}
                        >
                          <div className="flex items-start justify-between mb-2">
                            <span className="px-2 py-0.5 text-xs bg-[var(--surface)] border border-[var(--border)] rounded text-[var(--muted)]">
                              {move.type}
                            </span>
                            <button className="opacity-0 group-hover:opacity-100 p-1 hover:bg-[var(--surface)] rounded transition-all">
                              <MoreHorizontal size={14} className="text-[var(--muted)]" />
                            </button>
                          </div>
                          <h4 className="font-medium text-sm text-[var(--ink)] mb-1">{move.title}</h4>
                          <p className="text-xs text-[var(--muted)] line-clamp-2 mb-3">{move.desc}</p>

                          <div className="flex items-center justify-between pt-3 border-t border-[var(--border)]">
                            <div className="flex items-center gap-1.5 text-xs text-[var(--muted)]">
                              <Clock size={12} />
                              {move.start}
                            </div>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                router.push(`/moves?highlight=${move.id}`);
                              }}
                              className="text-xs font-medium text-[var(--ink)] hover:underline flex items-center gap-1"
                            >
                              Open
                              <ArrowRight size={12} />
                            </button>
                          </div>
                        </div>
                      ))}

                      {movesInColumn.length === 0 && (
                        <div className="h-24 border-2 border-dashed border-[var(--border)] rounded-[var(--radius)] flex items-center justify-center text-[var(--muted)] text-xs">
                          Drop moves here
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

      {/* Wizard Overlay */}
      <CampaignWizard
        isOpen={view === "WIZARD"}
        onClose={() => setView("LIST")}
        onComplete={handleWizardComplete}
      />

      {/* Timeline Modal */}
      {showTimeline && activeCampaign && (
        <CampaignTimeline
          campaign={activeCampaign}
          onClose={() => setShowTimeline(false)}
        />
      )}
    </div>
  );
}
