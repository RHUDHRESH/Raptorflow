"use client";

import { useRef, useEffect, useState } from "react";
import { createPortal } from "react-dom";
import gsap from "gsap";
import { Plus, Calendar as CalendarIcon, X, Search } from "lucide-react";

import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { Move, MoveCategory, ExecutionDay, MoveBriefData } from "@/components/moves/types";
import { MoveCreateWizard } from "@/components/moves/MoveCreateWizard";
import { useMovesStore } from "@/stores/movesStore";
import { DailyTaskBoard } from "@/components/moves/DailyTaskBoard";
import { MoveGallery } from "@/components/moves/MoveGallery";
import { MovesCalendar } from "@/components/moves/MovesCalendar";
import { MoveIntelCenter } from "@/components/moves/MoveIntelCenter";
import { BlueprintModal } from "@/components/ui/BlueprintModal";

/* ══════════════════════════════════════════════════════════════════════════════
   MOVES PAGE — RAPTORFLOW EDITION
   Premium layout with centered modals. Original aesthetic preserved.
   ══════════════════════════════════════════════════════════════════════════════ */

export default function MovesPage() {
  const pageRef = useRef<HTMLDivElement>(null);
  const headerRef = useRef<HTMLDivElement>(null);
  const sectionsRef = useRef<HTMLDivElement>(null);

  const [isWizardOpen, setIsWizardOpen] = useState(false);
  const [showCalendar, setShowCalendar] = useState(false);
  const [selectedMoveFromCalendar, setSelectedMoveFromCalendar] = useState<Move | null>(null);
  const [searchQuery, setSearchQuery] = useState("");

  const { moves, addMove } = useMovesStore();

  // Premium entrance animations
  useEffect(() => {
    if (!pageRef.current) return;

    const ctx = gsap.context(() => {
      // Header animation
      if (headerRef.current) {
        gsap.fromTo(headerRef.current,
          { opacity: 0, y: -20 },
          { opacity: 1, y: 0, duration: 0.6, ease: "power3.out" }
        );
      }

      // Staggered section reveals
      const sections = sectionsRef.current?.querySelectorAll('[data-animate-section]');
      if (sections?.length) {
        gsap.fromTo(sections,
          { opacity: 0, y: 30 },
          {
            opacity: 1,
            y: 0,
            duration: 0.5,
            stagger: 0.15,
            ease: "power2.out",
            delay: 0.2
          }
        );
      }
    }, pageRef);

    return () => ctx.revert();
  }, []);

  const handleCreateMove = (data: { category: MoveCategory; context: string; brief: MoveBriefData; execution: ExecutionDay[] }) => {
    const newMove: Move = {
      id: `mov-${Date.now()}`,
      name: data.brief.name,
      category: data.category,
      status: 'draft',
      duration: data.brief.duration,
      goal: data.brief.goal,
      tone: data.brief.tone,
      context: data.context,
      createdAt: new Date().toISOString(),
      progress: 0,
      execution: data.execution,
      icp: "General Audience",
      campaignId: undefined
    };
    addMove(newMove);
    setIsWizardOpen(false);
  };

  const handleOpenWizard = () => {
    setIsWizardOpen(true);
  };

  const handleOpenCalendar = () => {
    setShowCalendar(true);
  };

  return (
    <div ref={pageRef} className="relative max-w-7xl mx-auto px-6 pb-24">
      {/* Background Grid with subtle animation */}
      <div className="fixed inset-0 grid-visible pointer-events-none z-0 opacity-40" />

      {/* Content */}
      <div ref={sectionsRef} className="relative z-10 space-y-12">

        {/* Page Header - Editorial Style */}
        <div ref={headerRef} className="flex justify-between items-start pt-10">
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <div className="w-1 h-10 bg-[var(--blueprint)] rounded-full" />
              <div>
                <h1 className="font-editorial text-4xl text-[var(--ink)] tracking-tight">Moves</h1>
                <p className="text-sm text-[var(--ink-secondary)] mt-1 max-w-md">
                  Your marketing campaigns, broken down into daily execution.
                </p>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Global Search */}
            <div className="relative group mr-2">
              <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--muted)] group-focus-within:text-[var(--blueprint)] transition-colors" />
              <input
                type="text"
                placeholder="Search moves..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius)] pl-10 pr-8 py-2 text-sm w-64 focus:w-80 focus:outline-none focus:ring-1 focus:ring-[var(--blueprint)] focus:border-[var(--blueprint)] transition-all shadow-sm"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery("")}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--muted)] hover:text-[var(--ink)]"
                >
                  <X size={14} />
                </button>
              )}
            </div>

            <SecondaryButton
              onClick={handleOpenCalendar}
              className="group transition-all duration-200 hover:shadow-md"
            >
              <CalendarIcon size={16} className="group-hover:scale-110 transition-transform" />
              Calendar
            </SecondaryButton>
            <BlueprintButton
              onClick={handleOpenWizard}
              className="group transition-all duration-200 hover:shadow-lg hover:scale-[1.02]"
            >
              <Plus size={18} className="group-hover:rotate-90 transition-transform duration-300" />
              New Move
            </BlueprintButton>
          </div>
        </div>

        {/* TOP: DAILY TASKS */}
        <section data-animate-section>
          <DailyTaskBoard moves={moves} searchQuery={searchQuery} />
        </section>

        {/* DIVIDER - Elegant */}
        <div data-animate-section className="relative py-4">
          <div className="absolute inset-0 flex items-center">
            <div className="h-px w-full bg-gradient-to-r from-transparent via-[var(--border)] to-transparent" />
          </div>
          <div className="relative flex justify-center">
            <span className="bg-[var(--canvas)] px-4 font-technical text-[10px] text-[var(--muted)] uppercase tracking-[0.2em]">
              All Moves
            </span>
          </div>
        </div>

        {/* BOTTOM: MOVE GALLERY */}
        <section data-animate-section>
          <MoveGallery moves={moves} searchQuery={searchQuery} />
        </section>
      </div>

      {/* ═══════════════════════════════════════════════════════════════════════
          MODALS - All use fixed positioning for viewport centering
          ═══════════════════════════════════════════════════════════════════════ */}

      {/* Calendar Modal - Fixed & Centered */}
      {showCalendar && createPortal(
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-6">
          {/* Backdrop */}
          <div
            className="absolute inset-0 bg-[var(--ink)]/40 backdrop-blur-md animate-in fade-in duration-200"
            onClick={() => setShowCalendar(false)}
          />

          {/* Modal */}
          <div className="relative w-full max-w-5xl max-h-[75vh] bg-[var(--paper)] rounded-[var(--radius-lg)] border border-[var(--border)] shadow-2xl overflow-hidden animate-in zoom-in-95 fade-in slide-in-from-bottom-4 duration-300">
            {/* Registration marks */}
            <div className="absolute -top-1 -left-1 w-6 h-6 border-t-2 border-l-2 border-[var(--blueprint)] rounded-tl-lg" />
            <div className="absolute -top-1 -right-1 w-6 h-6 border-t-2 border-r-2 border-[var(--blueprint)] rounded-tr-lg" />
            <div className="absolute -bottom-1 -left-1 w-6 h-6 border-b-2 border-l-2 border-[var(--blueprint)] rounded-bl-lg" />
            <div className="absolute -bottom-1 -right-1 w-6 h-6 border-b-2 border-r-2 border-[var(--blueprint)] rounded-br-lg" />

            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-[var(--border)] bg-[var(--surface-subtle)]">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-[var(--blueprint)] rounded-lg flex items-center justify-center text-white">
                  <CalendarIcon size={18} />
                </div>
                <h2 className="font-editorial text-xl text-[var(--ink)]">Calendar View</h2>
              </div>
              <button
                onClick={() => setShowCalendar(false)}
                className="p-2 hover:bg-[var(--surface)] rounded-lg transition-colors text-[var(--muted)] hover:text-[var(--ink)]"
              >
                <X size={20} />
              </button>
            </div>

            {/* Content */}
            <div className="overflow-y-auto max-h-[calc(75vh-80px)] p-6">
              <MovesCalendar
                moves={moves}
                onMoveClick={(move) => {
                  setSelectedMoveFromCalendar(move);
                  setShowCalendar(false);
                }}
              />
            </div>
          </div>
        </div>,
        document.body
      )}

      {/* Create Wizard - Uses its own fixed centering */}
      <MoveCreateWizard
        isOpen={isWizardOpen}
        onClose={() => setIsWizardOpen(false)}
        onComplete={handleCreateMove}
      />

      {/* Move Detail Modal */}
      <BlueprintModal
        isOpen={!!selectedMoveFromCalendar}
        onClose={() => setSelectedMoveFromCalendar(null)}
        title="Move Details"
        code="MOV-DET"
        size="xl"
      >
        {selectedMoveFromCalendar && (
          <div className="py-2">
            <MoveIntelCenter move={selectedMoveFromCalendar} />
          </div>
        )}
      </BlueprintModal>
    </div>
  );
}
