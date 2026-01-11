"use client";

import { useRef, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import gsap from "gsap";
import {
  Plus,
  ChevronLeft,
  ChevronRight,
  Zap,
  Calendar,
  TrendingUp,
  Sparkles,
  ArrowRight,
  MoreHorizontal,
  Check
} from "lucide-react";

import { BlueprintKPI, KPIGrid } from "@/components/ui/BlueprintKPI";
import { BlueprintCard, CardFooter } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { BlueprintProgress } from "@/components/ui/BlueprintProgress";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { BlueprintAvatar, AvatarGroup } from "@/components/ui/BlueprintAvatar";
import { BlueprintEmptyState } from "@/components/ui/BlueprintEmptyState";
import { BlueprintChart } from "@/components/ui/BlueprintChart";

import { useMovesStore } from "@/stores/movesStore";
import { useCampaignStore } from "@/stores/campaignStore";
import { useMuseStore } from "@/stores/museStore";

/* ══════════════════════════════════════════════════════════════════════════════
   PAPER TERMINAL — Dashboard
   The command center for marketing operations (Data-Driven)
   ══════════════════════════════════════════════════════════════════════════════ */

// --- Static Visuals ---
const AVATARS = [
  { initials: "BM" }, { initials: "SK" }, { initials: "JD" }
];

const CHART_DATA = [
  { label: "Mon", value: 42, code: "D1" },
  { label: "Tue", value: 65, code: "D2" },
  { label: "Wed", value: 35, code: "D3" },
  { label: "Thu", value: 78, code: "D4" },
  { label: "Fri", value: 52, code: "D5" },
  { label: "Sat", value: 45, code: "D6" },
];

function DashboardPageContent() {
  const pageRef = useRef<HTMLDivElement>(null);
  const router = useRouter();
  const [mounted, setMounted] = useState(false);

  // Store Access
  const { moves } = useMovesStore();
  const { campaigns } = useCampaignStore();
  const { assets } = useMuseStore();

  // Derived Metrics
  const activeMoves = moves.filter(m => m.status === 'active' || m.status === 'draft');
  const completedMoves = moves.filter(m => m.status === 'completed' || m.status === 'paused');
  const completionRate = moves.length > 0 ? Math.round((completedMoves.length / moves.length) * 100) : 0;

  // Sort moves by date or priority (simulated by generic sort or recent additions)
  const recentMoves = [...moves].reverse().slice(0, 5);
  const activeCampaigns = campaigns.filter(c => c.status === 'Active');
  const latestAsset = assets.length > 0 ? assets[0] : null;

  useEffect(() => {
    setMounted(true);
    if (!pageRef.current) return;

    // Staggered Entry Animation
    const tl = gsap.timeline({ defaults: { ease: "power2.out" } });
    tl.fromTo("[data-header]", { opacity: 0, y: -10 }, { opacity: 1, y: 0, duration: 0.5 })
      .fromTo("[data-kpi]", { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.4, stagger: 0.1 }, "-=0.2")
      .fromTo("[data-section]", { opacity: 0, y: 15 }, { opacity: 1, y: 0, duration: 0.5, stagger: 0.15 }, "-=0.2");

  }, []);

  if (!mounted) return <div className="min-h-screen bg-[var(--canvas)]" />;

  return (
    <div ref={pageRef} className="relative w-full max-w-[1800px] mx-auto pb-12 px-6 lg:px-10">
      {/* Backgrounds */}
      <div className="fixed inset-0 pointer-events-none z-0" style={{ backgroundImage: "url('/textures/paper-grain.png')", opacity: 0.04, mixBlendMode: "multiply" }} />
      <div className="fixed inset-0 blueprint-grid pointer-events-none z-0 opacity-30" />

      <div className="relative z-10 space-y-8">
        {/* Header */}
        <div data-header className="flex justify-between items-start" style={{ opacity: 0 }}>
          <div className="space-y-2">
            <div className="flex items-center gap-4">
              <span className="font-technical text-[var(--blueprint)]">SYS.DASHBOARD</span>
              <div className="h-px w-8 bg-[var(--structure)]" />
              <span className="font-technical text-[var(--ink-muted)]">TURNKEY</span>
            </div>
            <h1 className="font-serif text-4xl text-[var(--ink)]">Marketing Command</h1>
            <p className="text-sm text-[var(--ink-secondary)] max-w-lg">
              System status, active moves, and strategic oversight.
            </p>
          </div>
          <div className="flex gap-3">
            <SecondaryButton onClick={() => router.push('/muse')}>
              <Sparkles size={14} /> Ask Muse
            </SecondaryButton>
            <BlueprintButton label="BTN-NEW" onClick={() => router.push('/moves?create=true')}>
              <Plus size={16} strokeWidth={1.5} /> New Move
            </BlueprintButton>
          </div>
        </div>

        {/* KPIs */}
        <div data-kpi>
          <KPIGrid columns={4}>
            <BlueprintKPI
              label="Active Moves"
              value={String(activeMoves.length)}
              code="KPI-MOV"
              trend="neutral"
            />
            <BlueprintKPI
              label="Rate Limit"
              value={String(completionRate) + "%"}
              code="KPI-VEL"
              trend={completionRate > 50 ? "up" : "neutral"}
              trendValue="Completion"
            />
            <BlueprintKPI
              label="Active Campaigns"
              value={String(activeCampaigns.length)}
              code="KPI-CMP"
              unit="Running"
            />
            <BlueprintCard code="TEAM" padding="md" showCorners className="flex flex-col justify-center">
              <div className="flex items-center justify-between">
                <span className="text-xs font-technical text-[var(--muted)]">OPERATORS</span>
                <div className="flex -space-x-2">
                  <AvatarGroup avatars={AVATARS} />
                </div>
              </div>
            </BlueprintCard>
          </KPIGrid>
        </div>

        {/* Main Content Area */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

          {/* Left Col: Timeline/Campaigns */}
          <div className="lg:col-span-2 space-y-8">
            {/* Campaign Status */}
            <div data-section>
              <div className="flex items-center gap-3 mb-4">
                <span className="font-technical text-[var(--blueprint)]">FIG. 02</span>
                <div className="h-px flex-1 bg-[var(--blueprint-line)]" />
                <span className="font-technical text-[var(--muted)]">CAMPAIGN STATUS</span>
              </div>

              {activeCampaigns.length > 0 ? (
                <BlueprintCard padding="none" showCorners code="CMP-OVR">
                  <div className="divide-y divide-[var(--border-subtle)]">
                    {activeCampaigns.slice(0, 3).map((campaign, i) => (
                      <div key={campaign.id} className="p-5 hover:bg-[var(--canvas)] transition-colors cursor-pointer" onClick={() => router.push('/campaigns')}>
                        <div className="flex justify-between items-center mb-2">
                          <h3 className="text-sm font-semibold text-[var(--ink)]">{campaign.name}</h3>
                          <BlueprintBadge variant="blueprint" size="sm" dot>ACTIVE</BlueprintBadge>
                        </div>
                        <div className="flex items-center gap-4">
                          <div className="flex-1">
                            <BlueprintProgress value={Math.random() * 60 + 20} size="sm" />
                            {/* Note: Real progress calc would require tasks count in campaign, using mock random for "feel" if data missing */}
                          </div>
                          <span className="font-technical text-[9px] text-[var(--muted)]">ON TRACK</span>
                        </div>
                      </div>
                    ))}
                  </div>
                  <CardFooter>
                    <button onClick={() => router.push('/campaigns')} className="flex items-center gap-2 font-technical text-[var(--muted)] hover:text-[var(--blueprint)] transition-colors text-xs">
                      VIEW ALL CAMPAIGNS <ArrowRight size={10} />
                    </button>
                  </CardFooter>
                </BlueprintCard>
              ) : (
                <BlueprintEmptyState
                  title="No Active Campaigns"
                  code="EMPTY"
                  action={{ label: "Launch Campaign", onClick: () => router.push('/campaigns?view=WIZARD') }}
                />
              )}
            </div>

            {/* Activity Chart */}
            <div data-section>
              <BlueprintChart
                data={CHART_DATA}
                figure="FIG. 03"
                title="Execution Velocity"
                height={200}
              />
            </div>
          </div>

          {/* Right Col: Quick Actions & Recent Moves */}
          <div className="space-y-8">

            {/* Quick Actions */}
            <div data-section>
              <div className="flex items-center gap-3 mb-4">
                <span className="font-technical text-[var(--blueprint)]">FIG. 04</span>
                <div className="h-px flex-1 bg-[var(--blueprint-line)]" />
                <span className="font-technical text-[var(--muted)]">ACTIONS</span>
              </div>
              <div className="grid grid-cols-2 gap-4">
                {[
                  { label: "New Move", icon: Zap, path: "/moves" },
                  { label: "Calendar", icon: Calendar, path: "/moves" },
                  { label: "Matrix", icon: TrendingUp, path: "/matrix" },
                  { label: "Muse", icon: Sparkles, path: "/muse" },
                ].map((action, i) => {
                  const Icon = action.icon;
                  return (
                    <button
                      key={i}
                      onClick={() => router.push(action.path)}
                      className="flex flex-col items-center justify-center p-4 bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius)] hover:border-[var(--blueprint)] hover:bg-[var(--blueprint-light)]/10 transition-all group"
                    >
                      <Icon size={20} className="text-[var(--muted)] mb-2 group-hover:text-[var(--blueprint)] transition-colors" />
                      <span className="text-xs font-medium text-[var(--ink)]">{action.label}</span>
                    </button>
                  )
                })}
              </div>
            </div>

            {/* Recent Moves */}
            <div data-section>
              <div className="flex items-center gap-3 mb-4">
                <span className="font-technical text-[var(--blueprint)]">FIG. 05</span>
                <div className="h-px flex-1 bg-[var(--blueprint-line)]" />
                <span className="font-technical text-[var(--muted)]">RECENT MOVES</span>
              </div>
              <BlueprintCard padding="none" code="REC-MOV" showCorners>
                {recentMoves.length > 0 ? (
                  <div className="divide-y divide-[var(--border-subtle)]">
                    {recentMoves.map((move, i) => (
                      <div key={move.id} onClick={() => router.push('/moves')} className="p-3 flex items-center gap-3 hover:bg-[var(--canvas)] cursor-pointer group transition-colors">
                        <div className={`w-2 h-2 rounded-full ${move.status === 'completed' ? 'bg-[var(--success)]' : move.status === 'active' ? 'bg-[var(--blueprint)]' : 'bg-[var(--orange)]'}`} />
                        <div className="flex-1 min-w-0">
                          <p className={`text-xs font-medium truncate ${move.status === 'completed' ? 'text-[var(--muted)] line-through' : move.status === 'active' ? 'text-[var(--ink)]' : 'text-[var(--orange)]'}`}>
                            {move.name}
                          </p>
                        </div>
                        {move.status === 'completed' && <Check size={12} className="text-[var(--success)]" />}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="p-6 text-center">
                    <p className="text-xs text-[var(--muted)] italic mb-3">No moves recorded yet.</p>
                    <SecondaryButton size="sm" onClick={() => router.push('/moves')}>Initialize Moves</SecondaryButton>
                  </div>
                )}
              </BlueprintCard>
            </div>

            {/* AI Insight */}
            {latestAsset && (
              <div data-section>
                <BlueprintCard
                  showCorners
                  padding="md"
                  className="border-[var(--blueprint)]/30 bg-gradient-to-br from-[var(--blueprint-light)] via-[var(--paper)] to-[var(--paper)]"
                >
                  <div className="flex items-start gap-3">
                    <div className="p-2 bg-[var(--blueprint)] rounded-[var(--radius-sm)] text-white">
                      <Sparkles size={16} />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-technical text-[var(--blueprint)]">LATEST INSIGHT</span>
                        <span className="text-[9px] font-mono text-[var(--muted)]">MUSE</span>
                      </div>
                      <h4 className="text-sm font-semibold text-[var(--ink)] line-clamp-1">{latestAsset.title}</h4>
                      <p className="text-xs text-[var(--ink-secondary)] line-clamp-2 mt-1 mb-3">
                        {latestAsset.content}
                      </p>
                      <button onClick={() => router.push('/muse')} className="text-xs font-bold text-[var(--blueprint)] hover:underline flex items-center gap-1">
                        Continue in Muse <ArrowRight size={10} />
                      </button>
                    </div>
                  </div>
                </BlueprintCard>
              </div>
            )}

          </div>
        </div>

        {/* Footer */}
        <div className="flex justify-center pt-8">
          <span className="font-technical text-[var(--muted)]">
            SYSTEM: OPERATIONAL | REVISION: {new Date().toISOString().split('T')[0]}
          </span>
        </div>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  return <DashboardPageContent />;
}
