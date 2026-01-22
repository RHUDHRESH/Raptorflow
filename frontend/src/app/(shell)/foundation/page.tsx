"use client";

import { useState, useRef, useEffect } from "react";
import gsap from "gsap";
import {
  Target,
  Users,
  MessageSquare,
  Layers,
  Eye,
  ChevronRight,
  Plus
} from "lucide-react";

import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { BlueprintProgress } from "@/components/ui/BlueprintProgress";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { useFoundationStore } from "@/stores/foundationStore";
import { RICPDetailModal } from "@/components/foundation/RICPDetailModal";
import { MessagingDetailModal } from "@/components/foundation/MessagingDetailModal";
import { DeriveCohortModal } from "@/components/foundation/DeriveCohortModal";
import { RICP, CoreMessaging, MARKET_SOPHISTICATION_LABELS } from "@/types/foundation";

/* ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
   FOUNDATION PAGE ΓÇö RICP & Messaging System
   Marketing fundamentals: positioning, ICPs/Cohorts, messaging, channels
   ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ */

export default function FoundationPage() {
  const pageRef = useRef<HTMLDivElement>(null);
  const { ricps, messaging, channels, addRICP, updateRICP, updateMessaging, fetchFoundation } = useFoundationStore();

  // Modal state
  const [selectedRICP, setSelectedRICP] = useState<RICP | null>(null);
  const [isMessagingOpen, setIsMessagingOpen] = useState(false);
  const [isDeriveModalOpen, setIsDeriveModalOpen] = useState(false);

  useEffect(() => {
    fetchFoundation();

    if (!pageRef.current) return;
    const header = pageRef.current.querySelector("[data-header]");
    if (header) gsap.fromTo(header, { opacity: 0, y: -12 }, { opacity: 1, y: 0, duration: 0.5 });
  }, [fetchFoundation]);

  return (
    <div ref={pageRef} className="relative max-w-7xl mx-auto pb-12">
      {/* Background textures */}
      <div className="fixed inset-0 pointer-events-none z-0" style={{ backgroundImage: "url('/textures/paper-grain.png')", backgroundRepeat: "repeat", backgroundSize: "256px 256px", opacity: 0.04, mixBlendMode: "multiply" }} />
      {/* Grid removed for cleaner "Quiet Luxury" look */}
      {/* <div className="fixed inset-0 blueprint-grid pointer-events-none z-0 opacity-30" /> */}

      <div className="relative z-10 space-y-10">
        {/* Header */}
        <div data-header className="flex justify-between items-start" style={{ opacity: 0 }}>
          <div className="space-y-2">
            <div className="flex items-center gap-4">
              <span className="font-technical text-[var(--blueprint)]">SYS.FOUNDATION</span>
              <div className="h-px w-12 bg-[var(--structure)]" />
              <span className="font-technical text-[var(--ink-muted)]">BRAND</span>
            </div>
            <h1 className="font-serif text-4xl text-[var(--ink)]">Brand Foundation</h1>
            <p className="text-sm text-[var(--ink-secondary)] max-w-lg">
              Your marketing fundamentals ΓÇö positioning, ICPs, messaging, and channels.
            </p>
          </div>
        </div>

        {/* Positioning Statement - Always First */}
        <section>
          <div className="flex items-center gap-3 mb-6">
            <span className="font-technical text-[var(--blueprint)]">SYS.POSITIONING</span>
            <div className="h-px w-12 bg-[var(--structure)]" />
            <span className="font-technical text-[var(--ink-muted)]">CORE</span>
            <div className="h-px flex-1 bg-[var(--structure-subtle)]" />
          </div>
          <BlueprintCard showCorners padding="lg" className="group cursor-pointer hover:border-[var(--blueprint)] transition-colors">
            <div className="flex items-start gap-6">
              <div className="w-14 h-14 rounded-[var(--radius)] bg-[var(--blueprint-light)] border border-[var(--blueprint)]/30 flex items-center justify-center shrink-0">
                <Target className="text-[var(--blueprint)]" size={24} strokeWidth={1.5} />
              </div>
              <div className="flex-1">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h2 className="font-serif text-xl text-[var(--ink)]">Positioning Statement</h2>
                    <p className="text-sm text-[var(--secondary)]">Your unique market position</p>
                  </div>
                  <BlueprintBadge variant="success" dot>COMPLETE</BlueprintBadge>
                </div>
                {messaging && (
                  <p className="text-lg text-[var(--ink)] leading-relaxed italic">
                    "{messaging.oneLiner}"
                  </p>
                )}
              </div>
            </div>
          </BlueprintCard>
        </section>

        {/* ICPs / Cohorts Section */}
        <section id="icp">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <span className="font-technical text-[var(--blueprint)]">SYS.COHORTS</span>
              <div className="h-px w-12 bg-[var(--structure)]" />
              <span className="font-technical text-[var(--ink-muted)]">ICP</span>
            </div>
            <SecondaryButton
              className="h-9 text-xs"
              onClick={() => setIsDeriveModalOpen(true)}
            >
              <span>+</span>
              Add Cohort
            </SecondaryButton>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {ricps.map((ricp, index) => (
              <RICPCard
                key={ricp.id}
                ricp={ricp}
                index={index}
                onClick={() => setSelectedRICP(ricp)}
              />
            ))}

            {/* Empty state if no RICPs */}
            {ricps.length === 0 && (
              <div className="col-span-full p-12 border-2 border-dashed border-[var(--structure)] rounded-[var(--radius)] text-center">
                <Users className="mx-auto text-[var(--ink-muted)] mb-4" size={32} strokeWidth={1.5} />
                <h3 className="font-medium text-[var(--ink)] mb-2">No ICPs defined yet</h3>
                <p className="text-sm text-[var(--ink-muted)] mb-4">Create your first Rich ICP to start targeting</p>
                <BlueprintButton onClick={() => setIsDeriveModalOpen(true)}>
                  <span>+</span>
                  Create First ICP
                </BlueprintButton>
              </div>
            )}
          </div>
        </section>

        {/* Core Messaging Section */}
        <section>
          <div className="flex items-center gap-3 mb-6">
            <span className="font-technical text-[var(--blueprint)]">SYS.MESSAGING</span>
            <div className="h-px w-12 bg-[var(--structure)]" />
            <span className="font-technical text-[var(--ink-muted)]">CORE</span>
            <div className="h-px flex-1 bg-[var(--structure-subtle)]" />
          </div>

          {messaging && (
            <BlueprintCard
              showCorners
              padding="lg"
              className="group cursor-pointer hover:border-[var(--blueprint)] transition-colors"
              onClick={() => setIsMessagingOpen(true)}
            >
              <div className="flex items-start gap-6">
                <div className="w-14 h-14 rounded-[var(--radius)] bg-[var(--surface)] border border-[var(--structure)] flex items-center justify-center shrink-0 group-hover:bg-[var(--blueprint-light)] group-hover:border-[var(--blueprint)]/30 transition-colors">
                  <MessageSquare className="text-[var(--ink-muted)] group-hover:text-[var(--blueprint)]" size={24} strokeWidth={1.5} />
                </div>
                <div className="flex-1">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h2 className="font-serif text-xl text-[var(--ink)]">Core Messaging</h2>
                      <p className="text-sm text-[var(--secondary)]">One-liner, positioning, value props, brand voice, StoryBrand</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <BlueprintBadge variant="blueprint">StoryBrand</BlueprintBadge>
                      <div className="flex items-center gap-1">
                        <BlueprintProgress value={messaging.confidence || 0} size="sm" className="w-20" />
                        <span className="text-xs text-[var(--ink-muted)]">{messaging.confidence || 0}%</span>
                      </div>
                    </div>
                  </div>

                  {/* Preview of key elements */}
                  <div className="grid grid-cols-3 gap-4">
                    <div className="p-3 bg-[var(--surface)] rounded-lg border border-[var(--structure-subtle)]">
                      <span className="text-[10px] font-bold text-[var(--ink-muted)] uppercase block mb-1">Value Props</span>
                      <span className="text-sm text-[var(--ink)]">{messaging.valueProps.length}/3 defined</span>
                    </div>
                    <div className="p-3 bg-[var(--surface)] rounded-lg border border-[var(--structure-subtle)]">
                      <span className="text-[10px] font-bold text-[var(--ink-muted)] uppercase block mb-1">Brand Tone</span>
                      <span className="text-sm text-[var(--ink)]">{messaging.brandVoice.tone.slice(0, 2).join(", ")}</span>
                    </div>
                    <div className="p-3 bg-[var(--surface)] rounded-lg border border-[var(--structure-subtle)]">
                      <span className="text-[10px] font-bold text-[var(--ink-muted)] uppercase block mb-1">StoryBrand</span>
                      <span className="text-sm text-[var(--ink)]">7 elements defined</span>
                    </div>
                  </div>
                </div>
                <span className="text-[var(--ink-muted)] group-hover:text-[var(--blueprint)] group-hover:translate-x-1 transition-all mt-2 text-xl">ΓåÆ</span>
              </div>
            </BlueprintCard>
          )}
        </section>

        {/* Channel Strategy Section */}
        <section>
          <div className="flex items-center gap-3 mb-6">
            <span className="font-technical text-[var(--blueprint)]">SYS.CHANNELS</span>
            <div className="h-px w-12 bg-[var(--structure)]" />
            <span className="font-technical text-[var(--ink-muted)]">STRATEGY</span>
            <div className="h-px flex-1 bg-[var(--structure-subtle)]" />
          </div>

          <BlueprintCard showCorners padding="lg">
            <div className="flex items-start gap-6">
              <div className="w-14 h-14 rounded-[var(--radius)] bg-[var(--surface)] border border-[var(--structure)] flex items-center justify-center shrink-0">
                <Layers className="text-[var(--ink-muted)]" size={24} strokeWidth={1.5} />
              </div>
              <div className="flex-1">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h2 className="font-serif text-xl text-[var(--ink)]">Channel Strategy</h2>
                    <p className="text-sm text-[var(--secondary)]">Where you show up and why</p>
                  </div>
                  <BlueprintBadge variant="default" dot>DRAFT</BlueprintBadge>
                </div>

                <div className="flex flex-wrap gap-2">
                  {channels.map(channel => (
                    <span
                      key={channel.id}
                      className={`px-3 py-1.5 text-sm font-medium rounded-lg border ${channel.priority === 'primary'
                        ? 'bg-[var(--ink)] text-[var(--paper)] border-[var(--ink)]'
                        : channel.priority === 'secondary'
                          ? 'bg-[var(--surface)] text-[var(--ink)] border-[var(--structure)]'
                          : 'bg-transparent text-[var(--ink-muted)] border-[var(--structure-subtle)] border-dashed'
                        }`}
                    >
                      {channel.name}
                      {channel.priority === 'primary' && <span className="ml-1.5 text-xs opacity-70">Γÿà</span>}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </BlueprintCard>
        </section>

        {/* Document Footer */}
        <div className="flex justify-center pt-8">
          <span className="font-technical text-[var(--muted)]">
            DOCUMENT: FOUNDATION-BRAND | REVISION: {new Date().toISOString().split('T')[0]}
          </span>
        </div>
      </div>

      {/* RICP Detail Modal */}
      {selectedRICP && (
        <RICPDetailModal
          ricp={selectedRICP}
          isOpen={true}
          onClose={() => setSelectedRICP(null)}
          onUpdate={(updates) => updateRICP(selectedRICP.id, updates)}
        />
      )}

      {/* Messaging Detail Modal */}
      {messaging && (
        <MessagingDetailModal
          messaging={messaging}
          isOpen={isMessagingOpen}
          onClose={() => setIsMessagingOpen(false)}
          onUpdate={updateMessaging}
        />
      )}

      {/* Derive Cohort Modal */}
      <DeriveCohortModal
        isOpen={isDeriveModalOpen}
        onClose={() => setIsDeriveModalOpen(false)}
        onDerived={(ricp) => {
          addRICP(ricp);
          setSelectedRICP(ricp); // Open detail modal immediately
        }}
      />
    </div>
  );
}

/* ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
   RICP CARD COMPONENT
   ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ */

interface RICPCardProps {
  ricp: RICP;
  index: number;
  onClick: () => void;
}

function RICPCard({ ricp, index, onClick }: RICPCardProps) {
  const cardRef = useRef<HTMLDivElement>(null);
  const sophisticationLabel = MARKET_SOPHISTICATION_LABELS[ricp.marketSophistication];

  useEffect(() => {
    if (!cardRef.current) return;
    gsap.fromTo(
      cardRef.current,
      { opacity: 0, y: 16 },
      { opacity: 1, y: 0, duration: 0.4, delay: 0.2 + index * 0.08, ease: "power2.out" }
    );
  }, [index]);

  return (
    <div
      ref={cardRef}
      onClick={onClick}
      className="group p-5 bg-[var(--paper)] border border-[var(--structure)] rounded-[var(--radius)] cursor-pointer hover:border-[var(--blueprint)] hover:shadow-lg transition-all"
      style={{ opacity: 0 }}
    >
      {/* Header */}
      <div className="flex items-start gap-4 mb-4">
        <div className="w-12 h-12 rounded-xl bg-[var(--surface)] border border-[var(--structure)] flex items-center justify-center text-2xl group-hover:bg-[var(--blueprint-light)] group-hover:border-[var(--blueprint)]/30 transition-colors">
          {ricp.avatar || "≡ƒæñ"}
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-[var(--ink)] truncate">{ricp.name}</h3>
          {ricp.personaName && (
            <p className="text-xs text-[var(--ink-muted)]">Persona: {ricp.personaName}</p>
          )}
        </div>
      </div>

      {/* Quick Info */}
      <div className="space-y-2 mb-4">
        <div className="flex items-center gap-2 text-xs text-[var(--ink-secondary)]">
          <span className="font-medium text-[var(--ink-muted)]">Role:</span>
          <span className="truncate">{ricp.demographics.role}</span>
        </div>
        <div className="flex items-center gap-2 text-xs text-[var(--ink-secondary)]">
          <span className="font-medium text-[var(--ink-muted)]">Stage:</span>
          <span>{ricp.demographics.stage}</span>
        </div>
      </div>

      {/* Market Sophistication */}
      <div className="flex items-center justify-between pt-3 border-t border-[var(--structure-subtle)]">
        <div className="flex items-center gap-2">
          <span className="w-6 h-6 rounded-full bg-[var(--ink)] text-[var(--paper)] text-xs font-bold flex items-center justify-center">
            {ricp.marketSophistication}
          </span>
          <span className="text-xs text-[var(--ink-muted)]">{sophisticationLabel.name}</span>
        </div>
        {ricp.confidence && (
          <span className="text-xs text-[var(--ink-muted)]">{ricp.confidence}%</span>
        )}
      </div>

      {/* View indicator */}
      <div className="flex items-center justify-center gap-1 mt-4 pt-3 border-t border-[var(--structure-subtle)] text-[var(--ink-muted)] group-hover:text-[var(--blueprint)] transition-colors">
        <Eye size={16} strokeWidth={1.5} />
        <span className="text-xs font-medium">View Full RICP</span>
        <span className="group-hover:translate-x-1 transition-transform text-xs">ΓåÆ</span>
      </div>
    </div>
  );
}
