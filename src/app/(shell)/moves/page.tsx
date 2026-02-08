"use client";

import { useState, useEffect, useRef } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { Plus, Calendar as CalendarIcon, Search, X, LayoutGrid, ListTodo, Zap } from "lucide-react";

import { Move, MoveCategory, ExecutionDay, MoveBriefData } from "@/components/moves/types";
import { MoveCreateWizard } from "@/components/moves/MoveCreateWizard";
import { useMovesStore } from "@/stores/movesStore";
import { TodaysAgenda } from "@/components/moves/TodaysAgenda";
import { MoveGallery } from "@/components/moves/MoveGallery";
import { MovesCalendarPro } from "@/components/moves/MovesCalendarPro";
import { BlueprintModal } from "@/components/ui/BlueprintModal";
import { MoveIntelCenter } from "@/components/moves/MoveIntelCenter";
import { MovesSkeleton } from "@/components/ui/DashboardSkeletons";
import { cn } from "@/lib/utils";
import { useWorkspace } from "@/components/workspace/WorkspaceProvider";
import { toast } from "sonner";
import { useBCMStore } from "@/stores/bcmStore";

/* ══════════════════════════════════════════════════════════════════════════════
   MOVES PAGE — QUIET LUXURY REDESIGN
   Clean tabbed layout with Today's Agenda, Gallery, and Calendar views
   ══════════════════════════════════════════════════════════════════════════════ */

type ViewTab = 'agenda' | 'gallery' | 'calendar';

export default function MovesPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();
  const didAttemptFetchRef = useRef(false);
  const missingMoveToastRef = useRef<string | null>(null);

  const [isWizardOpen, setIsWizardOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [mounted, setMounted] = useState(false);
  const [selectedMove, setSelectedMove] = useState<Move | null>(null);
  const [activeTab, setActiveTab] = useState<ViewTab>('agenda');

  const { workspaceId } = useWorkspace();
  const { manifest: bcm, fetchBCM } = useBCMStore();

  const { moves, addMove, fetchMoves, isLoading, error } = useMovesStore();

  useEffect(() => {
    setMounted(true);
    if (!workspaceId) return;
    didAttemptFetchRef.current = true;
    fetchMoves(workspaceId);
    fetchBCM(workspaceId);
  }, [workspaceId, fetchMoves]);

  useEffect(() => {
    if (error) toast.error(error);
  }, [error]);

  const linkedCampaignId = searchParams?.get("campaignId") || undefined;
  const autoOpenWizard =
    searchParams?.get("new") === "1" ||
    (searchParams?.get("create") || "").toLowerCase() === "true";
  const linkedMoveId = searchParams?.get("moveId") || undefined;

  useEffect(() => {
    if (!mounted) return;
    if (autoOpenWizard) setIsWizardOpen(true);
  }, [autoOpenWizard, mounted]);

  useEffect(() => {
    if (!mounted) return;
    if (!workspaceId) return;
    if (!linkedMoveId) return;
    if (error) return;

    const found = moves.find((m) => m.id === linkedMoveId);
    if (found) {
      missingMoveToastRef.current = null;
      setSelectedMove(found);
      return;
    }

    if (isLoading) return;
    if (!didAttemptFetchRef.current) return;
    if (missingMoveToastRef.current === linkedMoveId) return;

    missingMoveToastRef.current = linkedMoveId;
    toast.error("Move not found.");
  }, [mounted, workspaceId, linkedMoveId, moves, isLoading, error]);

  const clearMoveIdFromUrl = () => {
    const params = new URLSearchParams(searchParams?.toString());
    if (!params.has("moveId")) return;
    params.delete("moveId");
    const qs = params.toString();
    router.replace(qs ? `${pathname}?${qs}` : pathname);
  };

  // Calculate stats
  const stats = {
    total: moves.length,
    active: moves.filter(m => m.status === 'active').length,
    draft: moves.filter(m => m.status === 'draft').length,
    completed: moves.filter(m => m.status === 'completed').length,
  };

  // Filter moves for gallery
  const filteredMoves = moves.filter(m =>
    searchQuery === "" ||
    m.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    m.category.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleWizardComplete = async (data: { category: MoveCategory; context: string; brief: MoveBriefData; execution: ExecutionDay[] }) => {
    if (!workspaceId) return;

    const newMove: Move = {
      id: crypto.randomUUID(),
      name: data.brief.name,
      category: data.category,
      status: 'active',
      tone: data.brief.tone,
      duration: data.brief.duration,
      context: data.context,
      goal: data.brief.goal,
      createdAt: new Date().toISOString(),
      startDate: new Date().toISOString(),
      progress: 0,
      execution: data.execution || [],
      icp: data.brief.icp || "General Audience",
      metrics: data.brief.metrics || [],
      campaignId: linkedCampaignId,
      workspaceId: workspaceId
    };

    await addMove(newMove, workspaceId);
    setIsWizardOpen(false);
  };

  const handleMoveClick = (move: Move) => {
    setSelectedMove(move);
  };

  const tabs = [
    { id: 'agenda' as const, label: "Today's Agenda", icon: <ListTodo size={14} /> },
    { id: 'gallery' as const, label: 'All Moves', icon: <LayoutGrid size={14} /> },
    { id: 'calendar' as const, label: 'Calendar', icon: <CalendarIcon size={14} /> },
  ];

  if (!mounted) return null;

  if (isLoading) {
    return <MovesSkeleton />;
  }

  return (
    <div className="min-h-screen bg-[var(--canvas)]">
      {/* Page Header - Quiet Luxury */}
      <div className="border-b border-[var(--border)] bg-[var(--paper)]">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h1 className="font-serif text-3xl text-[var(--ink)]">
                Strategic Moves
              </h1>
              <p className="text-sm text-[var(--muted)] mt-1">
                Your execution headquarters — {stats.active} active, {stats.draft} drafts, {stats.completed} completed
                {bcm?.foundation?.company && (
                  <span className="ml-2 text-xs opacity-60">| {bcm.foundation.company}</span>
                )}
              </p>
              {bcm?.icps && bcm.icps.length > 0 && (
                <div className="flex gap-2 mt-2">
                  {bcm.icps.map((icp, i) => (
                    <span key={i} className="text-[10px] px-2 py-0.5 rounded-full bg-[var(--surface)] border border-[var(--border)] text-[var(--muted)]">
                      {icp.name}
                    </span>
                  ))}
                </div>
              )}
            </div>


          </div>

          {/* Action Bar */}
          <div className="flex items-center gap-3 mt-6">
              {/* Search - Only show in Gallery view */}
              {activeTab === 'gallery' && (
                <div className="relative">
                  <div className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--muted)]">
                    <Search className="w-4 h-4" />
                  </div>
                  <input
                    type="text"
                    placeholder="Search moves..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-64 pl-9 pr-9 py-2 bg-[var(--surface)] border border-[var(--border)] rounded-[var(--radius)] text-sm text-[var(--ink)] placeholder:text-[var(--muted)] focus:outline-none focus:border-[var(--ink)] transition-all"
                  />
                  {searchQuery && (
                    <button
                      onClick={() => setSearchQuery("")}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--muted)] hover:text-[var(--ink)] p-0.5"
                    >
                      <X className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>
              )}

              {/* New Move Button */}
              <button
                onClick={() => setIsWizardOpen(true)}
                className="flex items-center gap-2 px-4 py-2 bg-[var(--ink)] text-white rounded-[var(--radius)] hover:bg-[var(--ink)]/90 transition-all font-medium text-sm"
              >
                <Plus className="w-4 h-4" />
                <span>New Move</span>
              </button>
            </div>

          {/* Tab Navigation */}
          <div className="flex items-center gap-1 mt-6 border-b border-[var(--border)] -mb-px">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={cn(
                  "flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 transition-all",
                  activeTab === tab.id
                    ? "border-[var(--ink)] text-[var(--ink)]"
                    : "border-transparent text-[var(--muted)] hover:text-[var(--ink)] hover:border-[var(--border)]"
                )}
              >
                {tab.icon}
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">

        {isLoading && (
          <div className="text-center py-12 text-[var(--muted)]">
            Loading moves...
          </div>
        )}

        {/* Today's Agenda View */}
        {!isLoading && activeTab === 'agenda' && (
          <div className="max-w-3xl">
            <TodaysAgenda onMoveClick={handleMoveClick} />
          </div>
        )}

        {/* Gallery View */}
        {!isLoading && activeTab === 'gallery' && (
          <MoveGallery moves={filteredMoves} searchQuery={searchQuery} />
        )}

        {/* Calendar View */}
        {!isLoading && activeTab === 'calendar' && (
          <MovesCalendarPro
            moves={moves}
            onMoveClick={handleMoveClick}
            onCreateMove={() => setIsWizardOpen(true)}
          />
        )}
      </div>

      {/* Wizard Modal */}
      <MoveCreateWizard
        isOpen={isWizardOpen}
        onClose={() => setIsWizardOpen(false)}
        onComplete={handleWizardComplete}
      />

      {/* Move Detail Modal */}
      <BlueprintModal
        isOpen={!!selectedMove}
        onClose={() => {
          setSelectedMove(null);
          clearMoveIdFromUrl();
        }}
        title={selectedMove?.name || "Move Details"}
        size="lg"
      >
        {selectedMove && <MoveIntelCenter move={selectedMove} />}
      </BlueprintModal>
    </div>
  );
}
