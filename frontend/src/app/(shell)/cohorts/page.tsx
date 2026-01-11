"use client";

import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import gsap from "gsap";
import {
  Plus,
  Search,
  Users,
  TrendingUp,
  TrendingDown,
  ChevronRight,
  Edit2,
  Trash2,
  Target
} from "lucide-react";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { BlueprintEmptyState } from "@/components/ui/BlueprintEmptyState";

/* ══════════════════════════════════════════════════════════════════════════════
   PAPER TERMINAL — Cohorts Page
   Audience segmentation and targeting
   ══════════════════════════════════════════════════════════════════════════════ */

const COHORTS = [
  { id: "1", name: "Enterprise Decision Makers", description: "C-level and VP-level at 500+ companies", size: 2847, growth: 12.5, code: "COH-01", attributes: ["Enterprise", "Decision Maker", "B2B"] },
  { id: "2", name: "High-Intent Visitors", description: "Visited pricing 3+ times in 30 days", size: 1203, growth: 8.2, code: "COH-02", attributes: ["High Intent", "Pricing Interest"] },
  { id: "3", name: "SaaS Founders", description: "Founders at B2B SaaS, Series A-B", size: 892, growth: -2.1, code: "COH-03", attributes: ["Founder", "SaaS"] },
  { id: "4", name: "Marketing Leaders", description: "CMOs, VPs of Marketing, Heads of Growth", size: 567, growth: 5.8, code: "COH-04", attributes: ["Marketing", "Leadership"] },
];

function CohortCard({ cohort, index }: { cohort: typeof COHORTS[0]; index: number }) {
  const router = useRouter();
  const cardRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!cardRef.current) return;
    gsap.fromTo(cardRef.current, { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.4, delay: 0.2 + index * 0.08 });
  }, [index]);

  return (
    <BlueprintCard ref={cardRef} code={cohort.code} showCorners showMeasurements padding="lg" className="group cursor-pointer hover:border-[var(--blueprint)] transition-colors" style={{ opacity: 0 }}>
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="text-base font-semibold text-[var(--ink)] group-hover:text-[var(--blueprint)] transition-colors">{cohort.name}</h3>
          </div>
          <p className="text-xs text-[var(--muted)]">{cohort.description}</p>
        </div>
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button className="p-1.5 rounded-[var(--radius-sm)] text-[var(--muted)] hover:bg-[var(--canvas)] transition-colors"><Edit2 size={12} strokeWidth={1.5} /></button>
          <button className="p-1.5 rounded-[var(--radius-sm)] text-[var(--muted)] hover:bg-[var(--error-light)] hover:text-[var(--error)] transition-colors"><Trash2 size={12} strokeWidth={1.5} /></button>
        </div>
      </div>

      {/* Metrics */}
      <div className="flex items-center gap-6 mb-4">
        <div><span className="font-technical text-[var(--muted)]">SIZE</span><div className="flex items-baseline gap-1"><span className="text-lg font-semibold text-[var(--ink)]">{cohort.size.toLocaleString()}</span><span className="font-technical text-[var(--muted)]">CONTACTS</span></div></div>
        <div className="h-8 w-px bg-[var(--border-subtle)]" />
        <div><span className="font-technical text-[var(--muted)]">GROWTH</span><div className="flex items-center gap-1">{cohort.growth > 0 ? <TrendingUp size={14} strokeWidth={1.5} className="text-[var(--success)]" /> : <TrendingDown size={14} strokeWidth={1.5} className="text-[var(--error)]" />}<span className={`text-lg font-semibold ${cohort.growth > 0 ? "text-[var(--success)]" : "text-[var(--error)]"}`}>{cohort.growth > 0 ? "+" : ""}{cohort.growth}%</span></div></div>
      </div>

      {/* Attributes */}
      <div className="flex flex-wrap gap-1.5 mb-4">{cohort.attributes.map((a, i) => <BlueprintBadge key={i} variant="default">{a}</BlueprintBadge>)}</div>

      {/* Footer / Actions */}
      <div className="flex items-center justify-between pt-3 border-t border-[var(--border-subtle)]">
        <span className="font-technical text-[var(--muted)]">UPDATED 2H AGO</span>
        <div className="flex gap-2">
          <button
            onClick={(e) => { e.stopPropagation(); router.push('/campaigns?view=WIZARD&cohort=' + cohort.id) }}
            className="flex items-center gap-1 font-technical text-[var(--blueprint)] hover:underline transition-colors text-xs"
          >
            <Target size={12} /> TARGET IN CAMPAIGN
          </button>
          <button className="flex items-center gap-1 font-technical text-[var(--muted)] hover:text-[var(--ink)] transition-colors">DETAILS <ChevronRight size={10} strokeWidth={1.5} /></button>
        </div>
      </div>
    </BlueprintCard>
  );
}

export default function CohortsPage() {
  const router = useRouter();
  const pageRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!pageRef.current) return;
    const header = pageRef.current.querySelector("[data-header]");
    if (header) gsap.fromTo(header, { opacity: 0, y: -12 }, { opacity: 1, y: 0, duration: 0.5 });
  }, []);

  return (
    <div ref={pageRef} className="relative max-w-7xl mx-auto pb-12">
      {/* Backgrounds */}
      <div className="fixed inset-0 pointer-events-none z-0" style={{ backgroundImage: "url('/textures/paper-grain.png')", backgroundRepeat: "repeat", backgroundSize: "256px 256px", opacity: 0.04, mixBlendMode: "multiply" }} />
      <div className="fixed inset-0 blueprint-grid pointer-events-none z-0 opacity-30" />

      <div className="relative z-10 space-y-8">
        {/* Header */}
        <div data-header className="flex justify-between items-start" style={{ opacity: 0 }}>
          <div className="space-y-2"><div className="flex items-center gap-4"><span className="font-technical text-[var(--blueprint)]">FIG. 01</span><div className="h-px w-8 bg-[var(--blueprint-line)]" /><span className="font-technical text-[var(--muted)]">COHORTS</span></div><h1 className="font-serif text-4xl text-[var(--ink)]">Audience Cohorts</h1><p className="text-sm text-[var(--secondary)] max-w-lg">Segment your audience into targeted groups.</p></div>
          <BlueprintButton label="BTN-NEW"><Plus size={16} strokeWidth={1.5} />New Cohort</BlueprintButton>
        </div>

        {/* Controls */}
        <div className="flex items-center justify-end">
          <div className="flex items-center gap-3">
            <div className="relative"><Search size={14} strokeWidth={1.5} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--muted)]" /><input type="text" placeholder="Search..." className="w-64 h-9 pl-9 pr-4 text-sm bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-sm)] text-[var(--ink)] placeholder:text-[var(--placeholder)] focus:outline-none focus:border-[var(--blueprint)] transition-all" /></div>
          </div>
        </div>

        {/* List */}
        <div>
          <div className="flex items-center gap-3 mb-4"><span className="font-technical text-[var(--blueprint)]">FIG. 02</span><div className="h-px flex-1 bg-[var(--blueprint-line)]" /><span className="font-technical text-[var(--muted)]">{COHORTS.length.toString().padStart(2, "0")} COHORTS</span></div>
          {COHORTS.length > 0 ? <div className="grid grid-cols-1 md:grid-cols-2 gap-5">{COHORTS.map((c, i) => <CohortCard key={c.id} cohort={c} index={i} />)}</div> : <BlueprintEmptyState title="No cohorts found" code="EMPTY" action={{ label: "Create", onClick: () => { } }} />}
        </div>

        <div className="flex justify-center pt-8"><span className="font-technical text-[var(--muted)]">DOCUMENT: COHORTS-AUDIENCE | REVISION: {new Date().toISOString().split('T')[0]}</span></div>
      </div>
    </div>
  );
}
