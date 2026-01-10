"use client";

import { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import gsap from "gsap";
import {
    ArrowLeft,
    Calendar,
    Target,
    TrendingUp,
    MoreHorizontal,
    Plus,
    CheckSquare
} from "lucide-react";

import { useCampaignStore } from "@/stores/campaignStore";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { BlueprintProgress } from "@/components/ui/BlueprintProgress";
import { BlueprintKPI, KPIGrid } from "@/components/ui/BlueprintKPI";

export default function CampaignDetailPage({ params }: { params: { id: string } }) {
    const router = useRouter();
    const pageRef = useRef<HTMLDivElement>(null);
    const { campaigns } = useCampaignStore();
    const [campaign, setCampaign] = useState<any>(null); // Using any to avoid strict type need here, assuming standard shape
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Simulate fetch or find in store
        const found = campaigns.find(c => c.id === params.id) ||
            campaigns.find(c => c.id === "1") || // Fallback for demo if ID doesn't match
            null;

        if (found) {
            setCampaign(found);
            setLoading(false);
        } else {
            // If strictly not found, maybe redirect or show 404 component
            // For now, demo mock if store empty?
            // Actually, showing loading state is safer.
            setLoading(false);
        }
    }, [campaigns, params.id]);

    useEffect(() => {
        if (!pageRef.current || loading || !campaign) return;
        gsap.fromTo("[data-anim]", { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.4, stagger: 0.1 });
    }, [loading, campaign]);

    if (loading) return <div className="p-12 text-center text-[var(--muted)]">Loading campaign data...</div>;

    if (!campaign) return (
        <div className="p-12 text-center space-y-4">
            <h2 className="text-xl font-bold text-[var(--ink)]">Campaign Not Found</h2>
            <SecondaryButton onClick={() => router.push('/campaigns')}>Return to List</SecondaryButton>
        </div>
    );

    return (
        <div ref={pageRef} className="max-w-6xl mx-auto pb-12">
            <button onClick={() => router.back()} className="flex items-center gap-2 text-sm text-[var(--muted)] hover:text-[var(--ink)] mb-6 transition-colors">
                <ArrowLeft size={16} /> Back to Campaigns
            </button>

            {/* Header */}
            <div className="flex justify-between items-start mb-8" data-anim>
                <div className="space-y-2">
                    <div className="flex items-center gap-3">
                        <BlueprintBadge variant="blueprint" size="sm" dot>{campaign.status?.toUpperCase() || "ACTIVE"}</BlueprintBadge>
                        <span className="font-mono text-xs text-[var(--muted)]">ID: {campaign.id}</span>
                    </div>
                    <h1 className="font-editorial text-4xl text-[var(--ink)]">{campaign.title}</h1>
                    <p className="text-lg text-[var(--secondary)] max-w-2xl">{campaign.objective || "Dominating the market through strategic content and targeted outreach."}</p>
                </div>
                <div className="flex gap-3">
                    <SecondaryButton><MoreHorizontal size={16} /></SecondaryButton>
                    <BlueprintButton><Plus size={16} /> Add Move</BlueprintButton>
                </div>
            </div>

            {/* Metrics */}
            <div data-anim className="mb-8">
                <KPIGrid columns={4}>
                    <BlueprintKPI label="Progress" value="42%" code="PRG" unit="On Track" />
                    <BlueprintKPI label="Moves" value="12" code="MOV" trend="up" trendValue="+3" />
                    <BlueprintKPI label="Budget Used" value="$2.4k" code="BDG" unit="/ $5k" />
                    <BlueprintKPI label="ROI Est." value="3.5x" code="ROI" trend="up" trendValue="High" />
                </KPIGrid>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8" data-anim>
                {/* Main Content: Moves List? */}
                <div className="lg:col-span-2 space-y-8">
                    <BlueprintCard title="Execution Plan" code="EXEC" padding="md" showCorners>
                        <div className="space-y-1 mb-4">
                            <div className="flex justify-between text-xs text-[var(--muted)] font-technical">
                                <span>TIMELINE</span>
                                <span>WEEK 4 / 12</span>
                            </div>
                            <BlueprintProgress value={33} size="md" />
                        </div>

                        <h3 className="text-sm font-semibold text-[var(--ink)] mb-3 mt-6">Next Up</h3>
                        <div className="space-y-3">
                            {[1, 2, 3].map((i) => (
                                <div key={i} className="flex items-start gap-3 p-3 border border-[var(--border-subtle)] rounded-[var(--radius-sm)] bg-[var(--canvas)] hover:border-[var(--blueprint)] transition-colors cursor-pointer" onClick={() => router.push('/moves')}>
                                    <div className="mt-0.5"><CheckSquare size={16} className="text-[var(--muted)]" /></div>
                                    <div>
                                        <h4 className="text-sm font-medium text-[var(--ink)]">Direct Outreach to Top 50 Leads</h4>
                                        <p className="text-xs text-[var(--secondary)]">Using "Founder Story" template</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </BlueprintCard>
                </div>

                {/* Sidebar: Context */}
                <div className="space-y-6">
                    <BlueprintCard title="Strategic Context" code="CTX" padding="md" showCorners>
                        <div className="space-y-4">
                            <div>
                                <span className="text-xs font-technical text-[var(--muted)] block mb-1">TARGET AUDIENCE</span>
                                <BlueprintBadge variant="default">SaaS Founders</BlueprintBadge>
                            </div>
                            <div>
                                <span className="text-xs font-technical text-[var(--muted)] block mb-1">KEY CHANNEL</span>
                                <BlueprintBadge variant="default">LinkedIn</BlueprintBadge>
                            </div>
                            <div>
                                <span className="text-xs font-technical text-[var(--muted)] block mb-1">DATES</span>
                                <span className="text-sm text-[var(--ink)]">Jan 01 - Mar 31</span>
                            </div>
                        </div>
                    </BlueprintCard>
                </div>
            </div>
        </div>
    );
}
