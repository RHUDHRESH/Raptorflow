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
import { FoundationSkeleton } from "@/components/ui/DashboardSkeletons";
import { useFoundationStore } from "@/stores/foundationStore";
import { RICPDetailModal } from "@/components/foundation/RICPDetailModal";
import { MessagingDetailModal } from "@/components/foundation/MessagingDetailModal";
import { GlossaryTerm } from "@/components/foundation/StrategicGlossary";
import { BlueprintEmptyState } from "@/components/ui/BlueprintEmptyState";
import { RICP, CoreMessaging, MARKET_SOPHISTICATION_LABELS } from "@/types/foundation";
import { useWorkspace } from "@/components/workspace/WorkspaceProvider";
import { toast } from "sonner";

/* ══════════════════════════════════════════════════════════════════════════════
   FOUNDATION PAGE — RICP & Messaging System
   Marketing fundamentals: positioning, ICPs/Cohorts, messaging, channels
   ══════════════════════════════════════════════════════════════════════════════ */

export default function FoundationPage() {
  const pageRef = useRef<HTMLDivElement>(null);

  const { workspaceId } = useWorkspace();

  const { ricps, messaging, channels, fetchFoundation, updateRICP, updateMessaging, addRICP, isLoading, error } = useFoundationStore();

  // Modal state
  const [selectedRICP, setSelectedRICP] = useState<RICP | null>(null);
  const [isMessagingOpen, setIsMessagingOpen] = useState(false);
  const [isCreateRICPOpen, setIsCreateRICPOpen] = useState(false);

  useEffect(() => {
    if (!pageRef.current) return;
    const header = pageRef.current.querySelector("[data-header]");
    if (header) gsap.fromTo(header, { opacity: 0, y: -12 }, { opacity: 1, y: 0, duration: 0.5 });
  }, []);

  // Fetch data on mount/auth
  useEffect(() => {
    if (!workspaceId) return;
    fetchFoundation(workspaceId);
  }, [workspaceId, fetchFoundation]);

  useEffect(() => {
    if (error) toast.error(error);
  }, [error]);

  if (isLoading) {
    return <FoundationSkeleton />;
  }

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
              Your marketing fundamentals — positioning, ICPs, messaging, and channels.
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
            <SecondaryButton className="h-9 text-xs" onClick={() => setIsCreateRICPOpen(true)}>
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
              <div className="col-span-full">
                <BlueprintEmptyState
                  title="No ICPs defined yet"
                  description="Create your first Rich ICP to start targeting. This serves as the foundation for all AI content generation."
                  code="FNDN-RICP-00"
                  action={{
                    label: "Create First ICP",
                    onClick: () => setIsCreateRICPOpen(true)
                  }}
                />
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
                      <GlossaryTerm termKey="STORYBRAND" />
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
                <span className="text-[var(--ink-muted)] group-hover:text-[var(--blueprint)] group-hover:translate-x-1 transition-all mt-2 text-xl">→</span>
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
                      {channel.priority === 'primary' && <span className="ml-1.5 text-xs opacity-70">★</span>}
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

      <CreateRICPModal
        isOpen={isCreateRICPOpen}
        onClose={() => setIsCreateRICPOpen(false)}
        onCreate={async (ricp) => {
          if (!workspaceId) {
            toast.error("Workspace not initialized");
            return;
          }
          try {
            await addRICP(ricp, workspaceId);
            toast.success("ICP created");
            setIsCreateRICPOpen(false);
            setSelectedRICP(ricp);
          } catch (err: any) {
            toast.error(err?.message || "Failed to create ICP");
          }
        }}
      />

      {/* RICP Detail Modal */}
      {selectedRICP && workspaceId && (
        <RICPDetailModal
          ricp={selectedRICP}
          isOpen={true}
          onClose={() => setSelectedRICP(null)}
          onUpdate={(updates) => updateRICP(selectedRICP.id, updates, workspaceId)}
        />
      )}

      {/* Messaging Detail Modal */}
      {messaging && workspaceId && (
        <MessagingDetailModal
          messaging={messaging}
          isOpen={isMessagingOpen}
          onClose={() => setIsMessagingOpen(false)}
          onUpdate={(updates) => updateMessaging(updates, workspaceId)}
        />
      )}
    </div>
  );
}

/* ══════════════════════════════════════════════════════════════════════════════
   RICP CARD COMPONENT
   ══════════════════════════════════════════════════════════════════════════════ */

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
          {ricp.avatar || "👤"}
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
        <span className="group-hover:translate-x-1 transition-transform text-xs">→</span>
      </div>
    </div>
  );
}

type CreateRICPModalProps = {
  isOpen: boolean;
  onClose: () => void;
  onCreate: (ricp: RICP) => Promise<void> | void;
};

function CreateRICPModal({ isOpen, onClose, onCreate }: CreateRICPModalProps) {
  const [name, setName] = useState("");
  const [personaName, setPersonaName] = useState("");
  const [role, setRole] = useState("");
  const [stage, setStage] = useState("");
  const [location, setLocation] = useState("");
  const [marketSophistication, setMarketSophistication] = useState<1 | 2 | 3 | 4 | 5>(3);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen) return;
    setName("");
    setPersonaName("");
    setRole("");
    setStage("");
    setLocation("");
    setMarketSophistication(3);
    setError(null);
  }, [isOpen]);

  if (!isOpen) return null;

  async function handleCreate() {
    const trimmedName = name.trim();
    const trimmedRole = role.trim();
    const trimmedStage = stage.trim();
    if (!trimmedName) {
      setError("Name is required");
      return;
    }
    if (!trimmedRole) {
      setError("Role is required");
      return;
    }
    if (!trimmedStage) {
      setError("Stage is required");
      return;
    }

    setIsSubmitting(true);
    setError(null);
    try {
      const ricp: RICP = {
        id: crypto.randomUUID(),
        name: trimmedName,
        personaName: personaName.trim() || undefined,
        avatar: "👤",
        demographics: {
          ageRange: "",
          income: "",
          location: location.trim(),
          role: trimmedRole,
          stage: trimmedStage,
        },
        psychographics: {
          beliefs: "",
          identity: "",
          becoming: "",
          fears: "",
          values: [],
          hangouts: [],
          contentConsumed: [],
          whoTheyFollow: [],
          language: [],
          timing: [],
          triggers: [],
        },
        marketSophistication,
        painPoints: [],
        goals: [],
        objections: [],
      };

      await onCreate(ricp);
    } catch (e: any) {
      setError(e?.message || "Failed to create ICP");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="fixed inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose} />
      <div className="relative w-full max-w-lg bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-lg)] p-6 shadow-2xl">
        <div className="flex items-start justify-between gap-4 mb-4">
          <div>
            <h3 className="font-serif text-xl text-[var(--ink)]">Create ICP</h3>
            <p className="text-sm text-[var(--ink-muted)]">This is stored in Foundation and scoped to your workspace.</p>
          </div>
          <button
            className="px-3 py-1.5 text-sm rounded-[var(--radius)] border border-[var(--border)]"
            onClick={onClose}
            disabled={isSubmitting}
          >
            Close
          </button>
        </div>

        <div className="grid gap-4">
          <label className="grid gap-2">
            <span className="text-sm font-medium text-[var(--ink)]">Name</span>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3 py-2 rounded-[var(--radius)] border border-[var(--border)] bg-[var(--surface)]"
              placeholder="e.g. Bootstrap B2B Founder"
            />
          </label>

          <label className="grid gap-2">
            <span className="text-sm font-medium text-[var(--ink)]">Persona (optional)</span>
            <input
              value={personaName}
              onChange={(e) => setPersonaName(e.target.value)}
              className="w-full px-3 py-2 rounded-[var(--radius)] border border-[var(--border)] bg-[var(--surface)]"
              placeholder="e.g. Sam the Solo Founder"
            />
          </label>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <label className="grid gap-2">
              <span className="text-sm font-medium text-[var(--ink)]">Role</span>
              <input
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="w-full px-3 py-2 rounded-[var(--radius)] border border-[var(--border)] bg-[var(--surface)]"
                placeholder="e.g. Founder"
              />
            </label>

            <label className="grid gap-2">
              <span className="text-sm font-medium text-[var(--ink)]">Stage</span>
              <input
                value={stage}
                onChange={(e) => setStage(e.target.value)}
                className="w-full px-3 py-2 rounded-[var(--radius)] border border-[var(--border)] bg-[var(--surface)]"
                placeholder="e.g. Pre-PMF"
              />
            </label>
          </div>

          <label className="grid gap-2">
            <span className="text-sm font-medium text-[var(--ink)]">Location (optional)</span>
            <input
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="w-full px-3 py-2 rounded-[var(--radius)] border border-[var(--border)] bg-[var(--surface)]"
              placeholder="e.g. United States"
            />
          </label>

          <label className="grid gap-2">
            <span className="text-sm font-medium text-[var(--ink)]">Market Sophistication</span>
            <select
              value={marketSophistication}
              onChange={(e) => setMarketSophistication(Number(e.target.value) as any)}
              className="w-full px-3 py-2 rounded-[var(--radius)] border border-[var(--border)] bg-[var(--surface)]"
            >
              <option value={1}>1 - First to Market</option>
              <option value={2}>2 - Competition Arrives</option>
              <option value={3}>3 - Feature Wars</option>
              <option value={4}>4 - Market Saturation</option>
              <option value={5}>5 - Identity/Belief</option>
            </select>
          </label>

          {error ? <div className="text-sm text-[var(--error)]">{error}</div> : null}

          <div className="flex items-center gap-3 pt-2">
            <button
              onClick={() => void handleCreate()}
              disabled={isSubmitting}
              className="px-4 py-2 rounded-[var(--radius)] bg-[var(--ink)] text-white text-sm font-medium disabled:opacity-50"
            >
              {isSubmitting ? "Creating..." : "Create"}
            </button>
            <button
              onClick={onClose}
              disabled={isSubmitting}
              className="px-4 py-2 rounded-[var(--radius)] border border-[var(--border)] text-sm font-medium"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
