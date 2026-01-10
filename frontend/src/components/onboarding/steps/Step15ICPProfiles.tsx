"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import gsap from "gsap";
import { Check, Users, RefreshCw, Sparkles, ArrowLeft, MapPin, Brain, Eye, Clock, ChevronRight } from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { supabase } from "@/lib/supabaseClient";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { StepLoadingState } from "../StepStates";

/* ══════════════════════════════════════════════════════════════════════════════
   PAPER TERMINAL — Step 15: ICP Profiles

   RAPTORFLOW STYLE — Full-page detail view, not a modal
   Uses BlueprintCard, proper typography, no boxy overlays
   ══════════════════════════════════════════════════════════════════════════════ */

interface ICPProfile {
    id: string;
    name: string;
    tagline: string;
    code: string;
    demographics: { age: string; income: string; location: string; role: string; stage: string; };
    psychographics: { beliefs: string[]; identity: string; becoming: string; fears: string[]; values: string[]; };
    behaviors: { hangouts: string[]; consumption: string[]; follows: string[]; language: string[]; timing: string; triggers: string[]; };
    marketSophistication: { stage: number; name: string; reasoning: string; };
    scores: { painIntensity: number; willingnessToPay: number; accessibility: number; productFit: number; };
}

interface ICPResult {
    profiles: ICPProfile[];
    primaryICP: string | null;
    secondaryICP: string | null;
    confirmed: boolean;
}

const SOPHISTICATION_STAGES = [
    { stage: 1, name: "Unaware", desc: "Don't know they have a problem" },
    { stage: 2, name: "Problem Aware", desc: "Know the problem, not solutions" },
    { stage: 3, name: "Solution Aware", desc: "Know solutions exist, evaluating" },
    { stage: 4, name: "Product Aware", desc: "Know your product, comparing" },
    { stage: 5, name: "Most Aware", desc: "Ready to buy, need final push" },
];

// ═══════════════════════════════════════════════════════════════════════════════
// FULL DETAIL VIEW — Replaces the entire step content when viewing a profile
// ═══════════════════════════════════════════════════════════════════════════════
function ICPDetailView({
    profile,
    onBack,
    isPrimary,
    isSecondary,
    onSetPrimary,
    onSetSecondary
}: {
    profile: ICPProfile;
    onBack: () => void;
    isPrimary: boolean;
    isSecondary: boolean;
    onSetPrimary: () => void;
    onSetSecondary: () => void;
}) {
    const containerRef = useRef<HTMLDivElement>(null);
    const avgScore = Math.round((profile.scores.painIntensity + profile.scores.willingnessToPay + profile.scores.accessibility + profile.scores.productFit) / 4);

    useEffect(() => {
        if (!containerRef.current) return;
        gsap.fromTo(containerRef.current.querySelectorAll("[data-animate]"), { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.4, stagger: 0.05, ease: "power2.out" });
    }, []);

    return (
        <div ref={containerRef} className="space-y-8">
            {/* Back Button + Header */}
            <div data-animate>
                <button onClick={onBack} className="flex items-center gap-2 text-[var(--secondary)] hover:text-[var(--ink)] mb-6 transition-colors">
                    <ArrowLeft size={16} />
                    <span className="font-technical text-[10px]">BACK TO ALL PROFILES</span>
                </button>

                <div className="flex items-start justify-between">
                    <div>
                        <div className="flex items-center gap-3 mb-2">
                            <span className="font-technical text-[var(--blueprint)]">{profile.code}</span>
                            {isPrimary && <BlueprintBadge variant="blueprint">★ PRIMARY ICP</BlueprintBadge>}
                            {isSecondary && <BlueprintBadge variant="success">SECONDARY ICP</BlueprintBadge>}
                        </div>
                        <h1 className="font-serif text-3xl text-[var(--ink)] mb-2">{profile.name}</h1>
                        <p className="text-[var(--secondary)] max-w-xl">{profile.tagline}</p>
                    </div>
                    <div className="text-center">
                        <div className="w-20 h-20 rounded-2xl bg-[var(--ink)] flex flex-col items-center justify-center text-[var(--paper)]">
                            <span className="text-3xl font-serif">{avgScore}</span>
                            <span className="font-technical text-[8px] opacity-70">FIT SCORE</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Selection Actions */}
            <div data-animate className="flex gap-3">
                <BlueprintButton onClick={onSetPrimary} disabled={isPrimary} className={isPrimary ? "opacity-50" : ""}>
                    {isPrimary ? "★ Primary ICP" : "Set as Primary"}
                </BlueprintButton>
                <SecondaryButton onClick={onSetSecondary} disabled={isSecondary || isPrimary}>
                    {isSecondary ? "Secondary ICP" : "Set as Secondary"}
                </SecondaryButton>
            </div>

            {/* ═══════════════════════════════════════════════════════════════════════════ */}
            {/* DEMOGRAPHICS SECTION */}
            {/* ═══════════════════════════════════════════════════════════════════════════ */}
            <BlueprintCard data-animate figure="FIG. 01" title="Demographics" code="DEMO" showCorners padding="lg">
                <p className="text-sm text-[var(--secondary)] mb-6">
                    Who is this person? Basic facts about their life and work situation.
                </p>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                    {[
                        { label: "Age Range", value: profile.demographics.age, icon: "👤" },
                        { label: "Income", value: profile.demographics.income, icon: "💰" },
                        { label: "Location", value: profile.demographics.location, icon: "📍" },
                        { label: "Role", value: profile.demographics.role, icon: "💼" },
                        { label: "Stage", value: profile.demographics.stage, icon: "🚀" },
                    ].map((item) => (
                        <div key={item.label} className="p-4 rounded-xl bg-[var(--canvas)] text-center">
                            <span className="text-2xl mb-2 block">{item.icon}</span>
                            <span className="text-sm font-medium text-[var(--ink)] block">{item.value}</span>
                            <span className="font-technical text-[8px] text-[var(--muted)]">{item.label.toUpperCase()}</span>
                        </div>
                    ))}
                </div>
            </BlueprintCard>

            {/* ═══════════════════════════════════════════════════════════════════════════ */}
            {/* PSYCHOGRAPHICS SECTION */}
            {/* ═══════════════════════════════════════════════════════════════════════════ */}
            <BlueprintCard data-animate figure="FIG. 02" title="Psychographics" code="PSYCH" showCorners padding="lg">
                <p className="text-sm text-[var(--secondary)] mb-6">
                    What's going on in their head? Their beliefs, identity, aspirations, fears, and values drive their decisions.
                </p>

                <div className="grid md:grid-cols-2 gap-6">
                    {/* Identity */}
                    <div className="p-5 rounded-xl bg-[var(--canvas)] border border-[var(--border-subtle)]">
                        <span className="font-technical text-[9px] text-[var(--blueprint)] block mb-2">WHO THEY ARE</span>
                        <p className="text-[var(--ink)]">{profile.psychographics.identity}</p>
                    </div>

                    {/* Becoming */}
                    <div className="p-5 rounded-xl bg-[var(--canvas)] border border-[var(--border-subtle)]">
                        <span className="font-technical text-[9px] text-[var(--success)] block mb-2">WHO THEY WANT TO BECOME</span>
                        <p className="text-[var(--ink)]">{profile.psychographics.becoming}</p>
                    </div>
                </div>

                <div className="grid md:grid-cols-3 gap-4 mt-6">
                    {/* Beliefs */}
                    <div>
                        <span className="font-technical text-[9px] text-[var(--muted)] block mb-3">CORE BELIEFS</span>
                        <div className="space-y-2">
                            {profile.psychographics.beliefs.map((b, i) => (
                                <div key={i} className="p-3 rounded-lg bg-[var(--paper)] border border-[var(--border-subtle)] text-sm text-[var(--ink)]">
                                    "{b}"
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Fears */}
                    <div>
                        <span className="font-technical text-[9px] text-[var(--error)] block mb-3">FEARS & ANXIETIES</span>
                        <div className="space-y-2">
                            {profile.psychographics.fears.map((f, i) => (
                                <div key={i} className="p-3 rounded-lg bg-[var(--error-light)] border border-[var(--error)]/20 text-sm text-[var(--error)]">
                                    {f}
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Values */}
                    <div>
                        <span className="font-technical text-[9px] text-[var(--success)] block mb-3">VALUES</span>
                        <div className="space-y-2">
                            {profile.psychographics.values.map((v, i) => (
                                <div key={i} className="p-3 rounded-lg bg-[var(--success-light)] border border-[var(--success)]/20 text-sm text-[var(--success)]">
                                    {v}
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </BlueprintCard>

            {/* ═══════════════════════════════════════════════════════════════════════════ */}
            {/* BEHAVIORS SECTION */}
            {/* ═══════════════════════════════════════════════════════════════════════════ */}
            <BlueprintCard data-animate figure="FIG. 03" title="Behaviors" code="BEHAV" showCorners padding="lg">
                <p className="text-sm text-[var(--secondary)] mb-6">
                    What do they do? Where they spend time, what they consume, who they follow, and what triggers them to act.
                </p>

                <div className="space-y-6">
                    {/* Where They Hang Out */}
                    <div>
                        <span className="font-technical text-[9px] text-[var(--muted)] block mb-3">WHERE THEY HANG OUT</span>
                        <div className="flex flex-wrap gap-2">
                            {profile.behaviors.hangouts.map((h, i) => (
                                <span key={i} className="px-4 py-2 rounded-full bg-[var(--blueprint-light)] text-[var(--blueprint)] text-sm font-medium">{h}</span>
                            ))}
                        </div>
                    </div>

                    {/* Content Consumption */}
                    <div>
                        <span className="font-technical text-[9px] text-[var(--muted)] block mb-3">CONTENT THEY CONSUME</span>
                        <div className="grid md:grid-cols-3 gap-3">
                            {profile.behaviors.consumption.map((c, i) => (
                                <div key={i} className="p-3 rounded-lg bg-[var(--canvas)] text-sm text-[var(--ink)]">• {c}</div>
                            ))}
                        </div>
                    </div>

                    {/* Who They Follow */}
                    <div>
                        <span className="font-technical text-[9px] text-[var(--muted)] block mb-3">WHO THEY FOLLOW</span>
                        <div className="flex flex-wrap gap-2">
                            {profile.behaviors.follows.map((f, i) => (
                                <span key={i} className="px-3 py-1.5 rounded-full bg-[var(--canvas)] text-[var(--ink)] text-sm">@{f}</span>
                            ))}
                        </div>
                    </div>

                    {/* Language */}
                    <div>
                        <span className="font-technical text-[9px] text-[var(--muted)] block mb-3">LANGUAGE THEY USE</span>
                        <div className="flex flex-wrap gap-2">
                            {profile.behaviors.language.map((l, i) => (
                                <span key={i} className="px-3 py-1.5 rounded-lg bg-[var(--warning-light)] text-[var(--warning)] text-sm italic">"{l}"</span>
                            ))}
                        </div>
                    </div>

                    <div className="grid md:grid-cols-2 gap-4">
                        {/* Timing */}
                        <div className="p-4 rounded-xl bg-[var(--canvas)]">
                            <span className="font-technical text-[9px] text-[var(--muted)] block mb-2">WHEN THEY'RE ACTIVE</span>
                            <p className="text-[var(--ink)]">{profile.behaviors.timing}</p>
                        </div>

                        {/* Triggers */}
                        <div className="p-4 rounded-xl bg-[var(--canvas)]">
                            <span className="font-technical text-[9px] text-[var(--error)] block mb-2">PURCHASE TRIGGERS</span>
                            <ul className="space-y-1">
                                {profile.behaviors.triggers.map((t, i) => (
                                    <li key={i} className="text-sm text-[var(--ink)]">→ {t}</li>
                                ))}
                            </ul>
                        </div>
                    </div>
                </div>
            </BlueprintCard>

            {/* ═══════════════════════════════════════════════════════════════════════════ */}
            {/* MARKET SOPHISTICATION SECTION */}
            {/* ═══════════════════════════════════════════════════════════════════════════ */}
            <BlueprintCard data-animate figure="FIG. 04" title="Market Sophistication" code="STAGE" showCorners padding="lg">
                <p className="text-sm text-[var(--secondary)] mb-6">
                    How aware are they of their problem and existing solutions? This determines how you speak to them.
                </p>

                {/* Stage Visual */}
                <div className="flex items-center gap-2 mb-8">
                    {SOPHISTICATION_STAGES.map((s) => (
                        <div key={s.stage} className="flex-1">
                            <div className={`h-3 rounded-full transition-all ${s.stage <= profile.marketSophistication.stage ? "bg-[var(--ink)]" : "bg-[var(--border)]"}`} />
                            <div className="mt-2 text-center">
                                <span className={`font-technical text-[9px] ${s.stage === profile.marketSophistication.stage ? "text-[var(--ink)]" : "text-[var(--muted)]"}`}>
                                    {s.stage}
                                </span>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Current Stage Highlight */}
                <div className="p-6 rounded-2xl bg-[var(--ink)] text-[var(--paper)] mb-6">
                    <div className="flex items-center gap-4 mb-4">
                        <span className="text-5xl font-serif">{profile.marketSophistication.stage}</span>
                        <div>
                            <span className="font-technical text-[10px] opacity-70">STAGE</span>
                            <h3 className="font-serif text-xl">{profile.marketSophistication.name}</h3>
                        </div>
                    </div>
                    <p className="text-[var(--paper)]/80 leading-relaxed">{profile.marketSophistication.reasoning}</p>
                </div>

                {/* All Stages Reference */}
                <div className="grid grid-cols-5 gap-3">
                    {SOPHISTICATION_STAGES.map((s) => (
                        <div key={s.stage} className={`p-3 rounded-xl text-center ${s.stage === profile.marketSophistication.stage ? "bg-[var(--blueprint-light)] ring-2 ring-[var(--blueprint)]" : "bg-[var(--canvas)]"}`}>
                            <span className="font-serif text-lg text-[var(--ink)]">{s.stage}</span>
                            <p className={`font-technical text-[8px] ${s.stage === profile.marketSophistication.stage ? "text-[var(--blueprint)]" : "text-[var(--muted)]"}`}>{s.name.toUpperCase()}</p>
                        </div>
                    ))}
                </div>
            </BlueprintCard>

            {/* Footer */}
            <div className="flex justify-center pt-4">
                <span className="font-technical text-[var(--muted)]">ICP-PROFILE • {profile.code}</span>
            </div>
        </div>
    );
}

// ═══════════════════════════════════════════════════════════════════════════════
// MAIN COMPONENT
// ═══════════════════════════════════════════════════════════════════════════════
export default function Step15ICPProfiles() {
    const { session, updateStepData, updateStepStatus, getStepById } = useOnboardingStore();
    const stepData = getStepById(15)?.data as ICPResult | undefined;

    const [isGenerating, setIsGenerating] = useState(false);
    const [profiles, setProfiles] = useState<ICPProfile[]>(stepData?.profiles || []);
    const [primaryICP, setPrimaryICP] = useState<string | null>(stepData?.primaryICP || null);
    const [secondaryICP, setSecondaryICP] = useState<string | null>(stepData?.secondaryICP || null);
    const [confirmed, setConfirmed] = useState(stepData?.confirmed || false);
    const [viewingProfile, setViewingProfile] = useState<ICPProfile | null>(null);
    const containerRef = useRef<HTMLDivElement>(null);

    const hasData = profiles.length > 0;

    useEffect(() => {
        if (!containerRef.current || isGenerating || viewingProfile) return;
        gsap.fromTo(containerRef.current.querySelectorAll("[data-animate]"), { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.5, stagger: 0.08, ease: "power2.out" });
    }, [hasData, isGenerating, viewingProfile]);

    const generateICPs = useCallback(async () => {
        setIsGenerating(true);
        setTimeout(() => {
            const mock = generateMockICPs();
            setProfiles(mock);
            updateStepData(15, { profiles: mock });
            setIsGenerating(false);
        }, 1500);
    }, [updateStepData]);

    const generateMockICPs = (): ICPProfile[] => [
        {
            id: "1", name: "Scaling SaaS Founder", tagline: "B2B SaaS founders at $1-5M ARR scaling their first marketing team", code: "ICP-01",
            demographics: { age: "28-42", income: "$150K-$500K", location: "US, UK, Australia", role: "Founder / CEO", stage: "Series A / B" },
            psychographics: {
                beliefs: ["Growth solves everything", "Marketing should be systematic", "Data beats intuition"],
                identity: "Technical founder who built something people want but struggles to tell the story",
                becoming: "The founder who cracked growth and can now focus on product",
                fears: ["Hiring wrong", "Burning runway", "Competitors outpacing"],
                values: ["Efficiency", "Transparency", "Speed"]
            },
            behaviors: {
                hangouts: ["Twitter/X", "LinkedIn", "Indie Hackers"],
                consumption: ["Podcasts during commute", "Twitter threads", "Long-form case studies"],
                follows: ["paulg", "patrickc", "lennysan"],
                language: ["product-market fit", "ARR", "burn rate", "GTM motion"],
                timing: "Early morning or late night (founder hours)",
                triggers: ["Missed growth target", "Failed marketing hire", "Board pressure"]
            },
            marketSophistication: { stage: 3, name: "Solution Aware", reasoning: "They know they need better positioning and have probably tried agencies. They're evaluating tools that systematize the process." },
            scores: { painIntensity: 95, willingnessToPay: 80, accessibility: 75, productFit: 90 },
        },
        {
            id: "2", name: "Solo Technical Founder", tagline: "Developer-founders launching first product without marketing experience", code: "ICP-02",
            demographics: { age: "24-35", income: "$80K-$150K", location: "Global (remote)", role: "Solo Founder", stage: "Pre-seed" },
            psychographics: {
                beliefs: ["Build it and they will come", "Marketing is manipulative", "Product quality matters most"],
                identity: "Builder who can code anything but feels lost when it comes to selling",
                becoming: "A founder who can confidently talk about their product",
                fears: ["Looking salesy", "Wasting time", "Never finding customers"],
                values: ["Authenticity", "Craftsmanship", "Independence"]
            },
            behaviors: {
                hangouts: ["Hacker News", "Reddit", "Discord"],
                consumption: ["YouTube tutorials", "Blog posts", "Tweet threads"],
                follows: ["levelsio", "tdinh_me", "marc_louvion"],
                language: ["ship it", "MRR", "ramen profitable"],
                timing: "Evenings and weekends",
                triggers: ["Launch failing", "Seeing peers succeed", "Feeling stuck"]
            },
            marketSophistication: { stage: 2, name: "Problem Aware", reasoning: "They know marketing is their weakness but haven't found a solution that fits their technical mindset." },
            scores: { painIntensity: 85, willingnessToPay: 60, accessibility: 90, productFit: 70 },
        },
        {
            id: "3", name: "Agency Owner", tagline: "Marketing agency owners seeking positioning tools for client work", code: "ICP-03",
            demographics: { age: "30-50", income: "$200K-$1M", location: "US, Canada, UK", role: "Agency Owner", stage: "Established" },
            psychographics: {
                beliefs: ["Client results drive referrals", "Process creates scale", "Tools multiply output"],
                identity: "Strategic thinker tired of reinventing the wheel for every client",
                becoming: "An agency delivering predictable, premium positioning at scale",
                fears: ["Scope creep", "Commoditization", "Losing talent"],
                values: ["Quality", "Relationships", "Profitability"]
            },
            behaviors: {
                hangouts: ["LinkedIn", "Agency Slack groups", "Conferences"],
                consumption: ["Industry reports", "Agency podcasts", "Business books"],
                follows: ["chrisdo", "blairends", "davidcbaker"],
                language: ["retainer", "SOW", "client success"],
                timing: "Business hours, between calls",
                triggers: ["Big client RFP", "Need to train strategist", "Want to productize"]
            },
            marketSophistication: { stage: 4, name: "Product Aware", reasoning: "They've used multiple tools and frameworks. Comparing RaptorFlow against current process. Need clear differentiation." },
            scores: { painIntensity: 70, willingnessToPay: 90, accessibility: 65, productFit: 75 },
        },
    ];

    const handleSetPrimary = (id: string) => {
        if (secondaryICP === id) setSecondaryICP(null);
        setPrimaryICP(id);
        updateStepData(15, { profiles, primaryICP: id, secondaryICP: secondaryICP === id ? null : secondaryICP });
    };

    const handleSetSecondary = (id: string) => {
        setSecondaryICP(id);
        updateStepData(15, { profiles, primaryICP, secondaryICP: id });
    };

    const handleConfirm = () => {
        if (!primaryICP) return;
        setConfirmed(true);
        updateStepData(15, { profiles, primaryICP, secondaryICP, confirmed: true });
        updateStepStatus(15, "complete");
    };

    const getAvgScore = (scores: ICPProfile["scores"]) => Math.round((scores.painIntensity + scores.willingnessToPay + scores.accessibility + scores.productFit) / 4);

    // Show detail view
    if (viewingProfile) {
        return (
            <ICPDetailView
                profile={viewingProfile}
                onBack={() => setViewingProfile(null)}
                isPrimary={primaryICP === viewingProfile.id}
                isSecondary={secondaryICP === viewingProfile.id}
                onSetPrimary={() => handleSetPrimary(viewingProfile.id)}
                onSetSecondary={() => handleSetSecondary(viewingProfile.id)}
            />
        );
    }

    // Empty state
    if (!hasData && !isGenerating) {
        return (
            <div className="flex flex-col items-center justify-center py-20 text-center">
                <div className="w-16 h-16 rounded-2xl bg-[var(--ink)] flex items-center justify-center mb-6">
                    <Users size={28} className="text-[var(--paper)]" />
                </div>
                <h3 className="font-serif text-2xl text-[var(--ink)] mb-2">Deep ICP Research</h3>
                <p className="text-sm text-[var(--secondary)] max-w-sm mb-8">
                    Generate detailed profiles with demographics, psychographics, behaviors, and market sophistication.
                </p>
                <BlueprintButton size="lg" onClick={generateICPs}>
                    <Sparkles size={14} />Generate ICP Profiles
                </BlueprintButton>
            </div>
        );
    }

    if (isGenerating) {
        return <StepLoadingState title="Researching ICPs" message="Building detailed customer profiles..." />;
    }

    // Main list view
    return (
        <div ref={containerRef} className="space-y-8">
            {/* Header */}
            <div data-animate className="text-center">
                <h2 className="font-serif text-3xl text-[var(--ink)] mb-2">Your Ideal Customers</h2>
                <p className="text-[var(--secondary)]">Click a profile to explore the full research. Select your primary target.</p>
            </div>

            {/* Profile Cards */}
            <div data-animate className="space-y-4">
                {profiles.map((profile) => {
                    const isPrimary = primaryICP === profile.id;
                    const isSecondary = secondaryICP === profile.id;
                    const score = getAvgScore(profile.scores);

                    return (
                        <BlueprintCard
                            key={profile.id}
                            code={profile.code}
                            showCorners
                            padding="lg"
                            className={`cursor-pointer transition-all hover:shadow-md ${isPrimary ? "ring-2 ring-[var(--blueprint)] bg-[var(--blueprint-light)]" : isSecondary ? "ring-2 ring-[var(--success)]" : ""}`}
                            onClick={() => setViewingProfile(profile)}
                        >
                            <div className="flex items-center gap-6">
                                <div className="w-16 h-16 rounded-xl bg-[var(--ink)] flex flex-col items-center justify-center text-[var(--paper)] flex-shrink-0">
                                    <span className="text-2xl font-serif">{score}</span>
                                    <span className="font-technical text-[7px] opacity-70">SCORE</span>
                                </div>
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-3 mb-1">
                                        <h3 className="font-serif text-xl text-[var(--ink)]">{profile.name}</h3>
                                        {isPrimary && <BlueprintBadge variant="blueprint">PRIMARY</BlueprintBadge>}
                                        {isSecondary && <BlueprintBadge variant="success">SECONDARY</BlueprintBadge>}
                                    </div>
                                    <p className="text-sm text-[var(--secondary)] mb-2">{profile.tagline}</p>
                                    <span className="font-technical text-[9px] text-[var(--muted)]">
                                        STAGE {profile.marketSophistication.stage}: {profile.marketSophistication.name.toUpperCase()}
                                    </span>
                                </div>
                                <ChevronRight size={20} className="text-[var(--muted)] flex-shrink-0" />
                            </div>
                        </BlueprintCard>
                    );
                })}
            </div>

            {/* Actions */}
            <div data-animate className="flex gap-3">
                <SecondaryButton onClick={generateICPs} className="flex-1">
                    <RefreshCw size={12} />Regenerate
                </SecondaryButton>
                {primaryICP && !confirmed && (
                    <BlueprintButton onClick={handleConfirm} className="flex-1">
                        <Check size={14} />Confirm Selection
                    </BlueprintButton>
                )}
            </div>

            {confirmed && (
                <BlueprintCard data-animate showCorners padding="lg" className="border-[var(--success)] bg-[var(--success-light)]">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-[var(--success)] flex items-center justify-center">
                            <Check size={20} className="text-[var(--paper)]" />
                        </div>
                        <div>
                            <span className="font-serif text-lg text-[var(--ink)]">ICPs Confirmed</span>
                            <p className="font-technical text-[10px] text-[var(--secondary)]">Your targeting is locked</p>
                        </div>
                    </div>
                </BlueprintCard>
            )}

            <div className="flex justify-center pt-4">
                <span className="font-technical text-[var(--muted)]">ICP-PROFILES • STEP 15/25</span>
            </div>
        </div>
    );
}
