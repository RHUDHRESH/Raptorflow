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
import { PageHeader, PageFooter } from "@/components/ui/PageHeader";

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
      if (sections && sections.length > 0) {
        gsap.fromTo(sections,
          { opacity: 0, y: 30 },
          { opacity: 1, y: 0, duration: 0.8, stagger: 0.2, ease: "power3.out", delay: 0.2 }
        );
      }
    }, pageRef);

    return () => ctx.revert();
  }, []);

  const handleWizardComplete = (data: MoveBriefData) => {
    // Convert brief data to full Move object
    const newMove: Move = {
      id: `mov-${Date.now()}`,
      name: data.name,
      category: data.category,
      status: 'active', // Auto-start
      tone: data.tone,
      duration: data.duration,
      context: "Generated via Wizard",
      goal: data.goal,
      createdAt: new Date().toISOString(),
      startDate: new Date().toISOString(),
      progress: 0,
      execution: data.execution || [],
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

        {/* Page Header */}
        <div ref={headerRef} className="relative z-10 mb-8">
          <PageHeader
            moduleCode="MOVES"
            descriptor="EXECUTION CENTER"
            title="Strategic Moves"
            subtitle="Plan, execute, and track high-impact marketing campaigns."
            actions={
              <div className="flex gap-3">
                {/* Global Search */}
                <div className="relative group">
                  <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--muted)] group-focus-within:text-[var(--blueprint)] transition-colors" />
                  <input
                    type="text"
                    placeholder="Search moves..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius)] pl-10 pr-8 py-2 text-sm w-48 focus:w-64 focus:outline-none focus:ring-1 focus:ring-[var(--blueprint)] focus:border-[var(--blueprint)] transition-all shadow-sm"
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
                <SecondaryButton onClick={() => setShowCalendar(!showCalendar)}>
                  <CalendarIcon size={16} />
                  {showCalendar ? "Hide Calendar" : "Calendar"}
                </SecondaryButton>
                <BlueprintButton onClick={() => setIsWizardOpen(true)}>
                  <Plus size={16} />
                  New Move
                </BlueprintButton>
              </div>
            }
          />
        </div>

        {/* TOP: DAILY TASKS */}
        <section data-animate-section>
          <DailyTaskBoard moves={moves} searchQuery={searchQuery} />
        </section>

        {/* DIVIDER - Elegant */}
        <div className="h-px bg-gradient-to-r from-transparent via-[var(--border)] to-transparent opacity-50 my-16" />

        {/* GALLERY GRID */}
        <section data-animate-section className="min-h-[500px]">
          <MoveGallery moves={moves} searchQuery={searchQuery} />
        </section>

        {/* BOTTOM: INTEL CENTER */}
        <section data-animate-section>
          <MoveIntelCenter />
        </section>

        <PageFooter document="MOVES_EXECUTION_PROTOCOL" />
      </div>

      {/* Wizard Modal - Centered */}
      <BlueprintModal
        isOpen={isWizardOpen}
        onClose={() => setIsWizardOpen(false)}
        title="Initialize New Move"
        size="xl"
      >
        <MoveCreateWizard onComplete={handleWizardComplete} onCancel={() => setIsWizardOpen(false)} />
      </BlueprintModal>

      {/* Calendar Modal */}
      <BlueprintModal
        isOpen={showCalendar}
        onClose={() => setShowCalendar(false)}
        title="Campaign Calendar"
        size="xl"
      >
        <MovesCalendar
          moves={moves}
          onSelectMove={(move) => {
            setSelectedMoveFromCalendar(move);
            setShowCalendar(false);
          }}
        />
      </BlueprintModal>

    </div>
  );
}
