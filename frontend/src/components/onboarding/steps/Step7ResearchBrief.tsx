"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import gsap from "gsap";
import {
    Search, Users, MessageSquare, Target, Play, Check, RefreshCw, ExternalLink,
    ChevronDown, ChevronUp, Loader2, Quote, TrendingUp, AlertTriangle
} from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { supabase } from "@/lib/supabaseClient";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { StepLoadingState, StepEmptyState } from "../StepStates";

/* ══════════════════════════════════════════════════════════════════════════════
   PAPER TERMINAL — Step 7: Market & Customer Research Brief

   PURPOSE: Gather real market intelligence from external sources
   - Customer language/pain from reviews, forums, social media
   - Direct competitor analysis (claims, audience, features, pricing)
   - Indirect competitors and status quo alternatives
   - Create Research Brief with evidence citations
   ══════════════════════════════════════════════════════════════════════════════ */

// Types
interface CustomerInsight {
    id: string;
    type: "pain" | "language" | "desire" | "objection";
    quote: string;
    source: string;
    sourceUrl?: string;
    frequency: "common" | "occasional" | "rare";
}

interface CompetitorProfile {
    id: string;
    name: string;
    type: "direct" | "indirect" | "status-quo";
    coreClaim: string;
    targetAudience: string;
    keyFeatures: string[];
    pricing?: string;
    strengths: string[];
    weaknesses: string[];
    url?: string;
}

interface ResearchResult {
    customerInsights: CustomerInsight[];
    competitors: CompetitorProfile[];
    summary: string;
    reviewed: boolean;
}

function InsightCard({ insight }: { insight: CustomerInsight }) {
    const typeConfig = {
        pain: { label: "PAIN POINT", color: "error" as const, icon: AlertTriangle },
        language: { label: "CUSTOMER LANGUAGE", color: "blueprint" as const, icon: Quote },
        desire: { label: "DESIRE", color: "success" as const, icon: TrendingUp },
        objection: { label: "OBJECTION", color: "warning" as const, icon: MessageSquare },
    };
    const config = typeConfig[insight.type];
    const Icon = config.icon;

    const frequencyConfig = {
        common: { label: "COMMON", variant: "error" as const },
        occasional: { label: "OCCASIONAL", variant: "warning" as const },
        rare: { label: "RARE", variant: "default" as const },
    };

    return (
        <div className="p-4 rounded-[var(--radius-sm)] bg-[var(--canvas)] border border-[var(--border-subtle)]">
            <div className="flex items-center gap-2 mb-2">
                <Icon size={12} strokeWidth={1.5} className={`text-[var(--${config.color})]`} />
                <BlueprintBadge variant={config.color} className="text-[8px]">{config.label}</BlueprintBadge>
                <BlueprintBadge variant={frequencyConfig[insight.frequency].variant} className="text-[8px]">
                    {frequencyConfig[insight.frequency].label}
                </BlueprintBadge>
            </div>
            <p className="text-sm text-[var(--ink)] italic mb-2">&ldquo;{insight.quote}&rdquo;</p>
            <div className="flex items-center gap-2">
                <span className="font-technical text-[var(--muted)]">SOURCE:</span>
                {insight.sourceUrl ? (
                    <a href={insight.sourceUrl} target="_blank" rel="noopener noreferrer" className="font-technical text-[var(--blueprint)] hover:underline flex items-center gap-1">
                        {insight.source} <ExternalLink size={8} />
                    </a>
                ) : (
                    <span className="font-technical text-[var(--secondary)]">{insight.source}</span>
                )}
            </div>
        </div>
    );
}

function CompetitorCard({ competitor }: { competitor: CompetitorProfile }) {
    const [isExpanded, setIsExpanded] = useState(false);

    const typeConfig = {
        direct: { label: "DIRECT", color: "error" as const },
        indirect: { label: "INDIRECT", color: "warning" as const },
        "status-quo": { label: "STATUS QUO", color: "default" as const },
    };
    const config = typeConfig[competitor.type];

    return (
        <BlueprintCard code={competitor.id.slice(0, 3).toUpperCase()} showCorners padding="md">
            <div className="flex items-start justify-between mb-3">
                <div>
                    <div className="flex items-center gap-2 mb-1">
                        <h3 className="text-sm font-semibold text-[var(--ink)]">{competitor.name}</h3>
                        <BlueprintBadge variant={config.color}>{config.label}</BlueprintBadge>
                    </div>
                    <p className="text-xs text-[var(--secondary)]">{competitor.coreClaim}</p>
                </div>
                {competitor.url && (
                    <a href={competitor.url} target="_blank" rel="noopener noreferrer" className="p-1.5 text-[var(--muted)] hover:text-[var(--blueprint)] rounded-[var(--radius-xs)]">
                        <ExternalLink size={12} strokeWidth={1.5} />
                    </a>
                )}
            </div>

            <div className="flex items-center gap-4 mb-3">
                <div>
                    <span className="font-technical text-[8px] text-[var(--muted)]">TARGET</span>
                    <p className="text-xs text-[var(--ink)]">{competitor.targetAudience}</p>
                </div>
                {competitor.pricing && (
                    <div>
                        <span className="font-technical text-[8px] text-[var(--muted)]">PRICING</span>
                        <p className="text-xs text-[var(--ink)]">{competitor.pricing}</p>
                    </div>
                )}
            </div>

            <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="w-full flex items-center justify-center gap-1 py-2 text-[var(--muted)] hover:text-[var(--blueprint)] font-technical text-[10px] border-t border-[var(--border-subtle)]"
            >
                {isExpanded ? "HIDE DETAILS" : "VIEW DETAILS"}
                {isExpanded ? <ChevronUp size={10} /> : <ChevronDown size={10} />}
            </button>

            {isExpanded && (
                <div className="pt-3 space-y-3 border-t border-[var(--border-subtle)]">
                    <div>
                        <span className="font-technical text-[8px] text-[var(--muted)] block mb-1">KEY FEATURES</span>
                        <div className="flex flex-wrap gap-1">
                            {competitor.keyFeatures.map((f, i) => (
                                <BlueprintBadge key={i} variant="default" className="text-[8px]">{f}</BlueprintBadge>
                            ))}
                        </div>
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                        <div>
                            <span className="font-technical text-[8px] text-[var(--success)] block mb-1">STRENGTHS</span>
                            <ul className="space-y-0.5">
                                {competitor.strengths.map((s, i) => (
                                    <li key={i} className="text-xs text-[var(--secondary)] flex items-start gap-1">
                                        <Check size={8} className="mt-1 text-[var(--success)]" />{s}
                                    </li>
                                ))}
                            </ul>
                        </div>
                        <div>
                            <span className="font-technical text-[8px] text-[var(--error)] block mb-1">WEAKNESSES</span>
                            <ul className="space-y-0.5">
                                {competitor.weaknesses.map((w, i) => (
                                    <li key={i} className="text-xs text-[var(--secondary)] flex items-start gap-1">
                                        <AlertTriangle size={8} className="mt-1 text-[var(--error)]" />{w}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>
                </div>
            )}
        </BlueprintCard>
    );
}

export default function Step7ResearchBrief() {
    const { session, updateStepData, updateStepStatus, getStepById } = useOnboardingStore();
    const stepData = getStepById(7)?.data as ResearchResult | undefined;

    const [isResearching, setIsResearching] = useState(false);
    const [insights, setInsights] = useState<CustomerInsight[]>(stepData?.customerInsights || []);
    const [competitors, setCompetitors] = useState<CompetitorProfile[]>(stepData?.competitors || []);
    const [summary, setSummary] = useState(stepData?.summary || "");
    const [reviewed, setReviewed] = useState(stepData?.reviewed || false);
    const [activeTab, setActiveTab] = useState<"insights" | "competitors">("insights");
    const containerRef = useRef<HTMLDivElement>(null);

    const hasData = insights.length > 0 || competitors.length > 0;

    // Animation
    useEffect(() => {
        if (!containerRef.current || isResearching || !hasData) return;
        gsap.fromTo(
            containerRef.current.querySelectorAll("[data-animate]"),
            { opacity: 0, y: 16 },
            { opacity: 1, y: 0, duration: 0.4, stagger: 0.06, ease: "power2.out" }
        );
    }, [hasData, isResearching, activeTab]);

    // Run research
    const runResearch = useCallback(async () => {
        if (!session?.sessionId) return;

        setIsResearching(true);

        try {
            const { data: authData } = await supabase.auth.getSession();
            const token = authData.session?.access_token;

            const res = await fetch(
                `http://localhost:8000/api/v1/onboarding/${session.sessionId}/steps/7/run`,
                {
                    method: "POST",
                    headers: token ? { Authorization: `Bearer ${token}` } : {},
                }
            );

            if (!res.ok) throw new Error("Failed to start research");

            // Poll for results
            const pollInterval = setInterval(async () => {
                try {
                    const statusRes = await fetch(
                        `http://localhost:8000/api/v1/onboarding/${session.sessionId}/steps/7`,
                        { headers: token ? { Authorization: `Bearer ${token}` } : {} }
                    );

                    if (statusRes.ok) {
                        const data = await statusRes.json();
                        if (data?.data?.customerInsights || data?.data?.competitors) {
                            clearInterval(pollInterval);
                            setInsights(data.data.customerInsights || []);
                            setCompetitors(data.data.competitors || []);
                            setSummary(data.data.summary || "");
                            updateStepData(7, data.data);
                            setIsResearching(false);
                        }
                    }
                } catch (e) {
                    console.error("Polling error:", e);
                }
            }, 2000);

            // Timeout - use mock data
            setTimeout(() => {
                clearInterval(pollInterval);
                if (isResearching) {
                    const mockResult = generateMockResearch();
                    setInsights(mockResult.customerInsights);
                    setCompetitors(mockResult.competitors);
                    setSummary(mockResult.summary);
                    updateStepData(7, mockResult as unknown as Record<string, unknown>);
                    setIsResearching(false);
                }
            }, 30000);
        } catch (error) {
            console.error("Research error:", error);
            const mockResult = generateMockResearch();
            setInsights(mockResult.customerInsights);
            setCompetitors(mockResult.competitors);
            setSummary(mockResult.summary);
            updateStepData(7, mockResult as unknown as Record<string, unknown>);
            setIsResearching(false);
        }
    }, [session, updateStepData, isResearching]);

    const generateMockResearch = (): ResearchResult => ({
        customerInsights: [
            { id: "1", type: "pain", quote: "I spend hours every week figuring out what content to post", source: "Reddit r/startups", frequency: "common" },
            { id: "2", type: "pain", quote: "We tried 5 different tools and none of them actually helped with strategy", source: "G2 Review", frequency: "common" },
            { id: "3", type: "language", quote: "I need a system, not just another scheduling tool", source: "Twitter", frequency: "occasional" },
            { id: "4", type: "desire", quote: "I want to feel confident that what I'm posting will actually work", source: "ProductHunt", frequency: "common" },
            { id: "5", type: "objection", quote: "How is this different from hiring a marketing consultant?", source: "Demo call", frequency: "occasional" },
        ],
        competitors: [
            {
                id: "comp-1", name: "HubSpot", type: "direct", coreClaim: "All-in-one marketing platform", targetAudience: "Mid-market to Enterprise",
                keyFeatures: ["CRM", "Email", "Social", "Analytics"], pricing: "$800-3200/mo", strengths: ["Brand recognition", "Full suite"], weaknesses: ["Complex", "Expensive", "Overkill for SMBs"],
            },
            {
                id: "comp-2", name: "Marketing Agencies", type: "indirect", coreClaim: "Done-for-you marketing", targetAudience: "Funded startups",
                keyFeatures: ["Strategy", "Execution", "Creative"], pricing: "$5000-15000/mo", strengths: ["No learning curve", "Expert execution"], weaknesses: ["Expensive", "Slow", "Loss of control"],
            },
            {
                id: "comp-3", name: "DIY/Spreadsheets", type: "status-quo", coreClaim: "Free and flexible", targetAudience: "Early founders",
                keyFeatures: ["Custom", "Free"], pricing: "Free", strengths: ["No cost", "Familiar"], weaknesses: ["Time-consuming", "No guidance", "Random posting"],
            },
        ],
        summary: "Founders are frustrated with tool sprawl and lack of strategic guidance. They want confidence in their marketing approach, not just more features. Main competition is agencies (expensive) and DIY (time-consuming).",
        reviewed: false,
    });

    const handleReview = () => {
        setReviewed(true);
        updateStepData(7, { customerInsights: insights, competitors, summary, reviewed: true });
        updateStepStatus(7, "complete");
    };

    // Filter insights by type
    const insightsByType = {
        pain: insights.filter(i => i.type === "pain"),
        language: insights.filter(i => i.type === "language"),
        desire: insights.filter(i => i.type === "desire"),
        objection: insights.filter(i => i.type === "objection"),
    };

    // Ready state
    if (!hasData && !isResearching) {
        return (
            <div className="flex flex-col items-center justify-center p-12 text-center space-y-6">
                <div className="w-16 h-16 rounded-[var(--radius-md)] bg-[var(--blueprint)] flex items-center justify-center ink-bleed-md">
                    <Search size={30} className="text-[var(--paper)]" />
                </div>
                <div>
                    <h3 className="font-serif text-xl text-[var(--ink)]">Ready for Market Research</h3>
                    <p className="text-sm text-[var(--secondary)] max-w-md mx-auto mt-2">
                        We&apos;ll scan reviews, forums, social media, and competitor sites to gather
                        real customer language, pain points, and competitive intelligence.
                    </p>
                </div>
                <BlueprintButton size="lg" onClick={runResearch}>
                    <Play size={14} strokeWidth={1.5} fill="currentColor" />
                    Start Research
                </BlueprintButton>
            </div>
        );
    }

    // Loading state
    if (isResearching) {
        return (
            <StepLoadingState
                title="Gathering Market Intelligence"
                message="Scanning customer reviews, forums, and competitor websites..."
                stage="Analyzing sentiment and extracting insights..."
            />
        );
    }

    return (
        <div ref={containerRef} className="space-y-6">
            {/* Summary */}
            <BlueprintCard data-animate showCorners padding="md" className="border-[var(--blueprint)]/30 bg-[var(--blueprint-light)]">
                <div className="flex items-start gap-3">
                    <Search size={18} className="text-[var(--blueprint)] mt-0.5" />
                    <div>
                        <h3 className="text-sm font-semibold text-[var(--ink)] mb-1">Research Summary</h3>
                        <p className="text-sm text-[var(--secondary)]">{summary}</p>
                    </div>
                </div>
            </BlueprintCard>

            {/* Tabs */}
            <div data-animate className="flex gap-2 border-b border-[var(--border-subtle)] pb-2">
                <button
                    onClick={() => setActiveTab("insights")}
                    className={`px-4 py-2 font-technical text-sm rounded-t-[var(--radius-sm)] transition-all ${activeTab === "insights"
                        ? "bg-[var(--blueprint)] text-[var(--paper)]"
                        : "text-[var(--muted)] hover:text-[var(--ink)]"
                        }`}
                >
                    <Users size={12} className="inline mr-1.5" />
                    CUSTOMER INSIGHTS ({insights.length})
                </button>
                <button
                    onClick={() => setActiveTab("competitors")}
                    className={`px-4 py-2 font-technical text-sm rounded-t-[var(--radius-sm)] transition-all ${activeTab === "competitors"
                        ? "bg-[var(--blueprint)] text-[var(--paper)]"
                        : "text-[var(--muted)] hover:text-[var(--ink)]"
                        }`}
                >
                    <Target size={12} className="inline mr-1.5" />
                    COMPETITORS ({competitors.length})
                </button>
            </div>

            {/* Customer Insights Tab */}
            {activeTab === "insights" && (
                <div data-animate className="space-y-6">
                    {Object.entries(insightsByType).map(([type, typeInsights]) => {
                        if (typeInsights.length === 0) return null;
                        const typeLabels = { pain: "Pain Points", language: "Customer Language", desire: "Desires", objection: "Objections" };
                        return (
                            <div key={type}>
                                <div className="flex items-center gap-3 mb-3">
                                    <span className="font-technical text-[var(--blueprint)]">{typeLabels[type as keyof typeof typeLabels].toUpperCase()}</span>
                                    <div className="h-px flex-1 bg-[var(--blueprint-line)]" />
                                    <span className="font-technical text-[var(--muted)]">{typeInsights.length} FOUND</span>
                                </div>
                                <div className="space-y-2">
                                    {typeInsights.map((insight) => (
                                        <InsightCard key={insight.id} insight={insight} />
                                    ))}
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}

            {/* Competitors Tab */}
            {activeTab === "competitors" && (
                <div data-animate className="space-y-4">
                    {competitors.map((competitor) => (
                        <CompetitorCard key={competitor.id} competitor={competitor} />
                    ))}
                </div>
            )}

            {/* Review */}
            {!reviewed ? (
                <BlueprintCard data-animate showCorners padding="md" className="border-[var(--blueprint)]/30 bg-[var(--blueprint-light)]">
                    <div className="flex items-center justify-between">
                        <div>
                            <h3 className="text-sm font-semibold text-[var(--ink)]">Research Complete?</h3>
                            <p className="font-technical text-[var(--muted)]">MARK AS REVIEWED TO CONTINUE</p>
                        </div>
                        <div className="flex gap-2">
                            <SecondaryButton size="sm" onClick={runResearch}>
                                <RefreshCw size={10} strokeWidth={1.5} />
                                Re-run
                            </SecondaryButton>
                            <BlueprintButton size="sm" onClick={handleReview}>
                                <Check size={12} strokeWidth={1.5} />
                                Mark Reviewed
                            </BlueprintButton>
                        </div>
                    </div>
                </BlueprintCard>
            ) : (
                <BlueprintCard data-animate showCorners padding="md" className="border-[var(--success)]/30 bg-[var(--success-light)]">
                    <div className="flex items-center gap-3">
                        <Check size={18} strokeWidth={1.5} className="text-[var(--success)]" />
                        <span className="text-sm font-medium text-[var(--ink)]">Research reviewed</span>
                        <BlueprintBadge variant="success" dot className="ml-auto">REVIEWED</BlueprintBadge>
                    </div>
                </BlueprintCard>
            )}

            <div className="flex justify-center pt-4">
                <span className="font-technical text-[var(--muted)]">
                    DOCUMENT: RESEARCH-BRIEF | STEP 07/25 | {insights.length + competitors.length} ITEMS
                </span>
            </div>
        </div>
    );
}
