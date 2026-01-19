"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import gsap from "gsap";
import { Users, Sparkles, ArrowRight, ArrowLeft, CheckCircle, Target, Briefcase, MapPin, Brain, Clock, Eye, Loader2 } from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { StepLoadingState } from "../StepStates";
import { cn } from "@/lib/utils";

/* ══════════════════════════════════════════════════════════════════════════════
   PAPER TERMINAL — Step 15: ICP Profiles (Deep Research)
   
   PURPOSE: "No Scroll" ICP Selector + Rich Detail View.
   - Horizontal "Player Cards" for selection phase.
   - Full-Screen Detail View with deep psychographics/demographics.
   - Data derived from Strategy (Step 9/13).
   ══════════════════════════════════════════════════════════════════════════════ */

interface ICPProfile {
    id: string;
    name: string;
    tagline: string;
    role: string;
    stage: string;
    matchScore: number;
    // Deep Context
    demographics: { age: string; income: string; base: string; };
    psychographics: {
        beliefs: string[];
        fears: string[];
        values: string[];
        becoming: string; // "Who they want to become"
    };
    behaviors: {
        triggers: string[];
        hangouts: string[];
        follows: string[];
    };
    sophistication: { stage: number; label: string; why: string; };
}

function ProfileCard({ profile, isPrimary, isSecondary, onSelect, onDetails }: any) {
    return (
        <div
            onClick={onDetails}
            className={cn(
                "group relative p-5 rounded border transition-all duration-300 cursor-pointer flex flex-col h-full bg-[var(--paper)]",
                isPrimary ? "border-[var(--blueprint)] shadow-lg ring-1 ring-[var(--blueprint)]" :
                    isSecondary ? "border-[var(--success)] shadow-md" :
                        "border-[var(--border)] hover:border-[var(--blueprint)] hover:shadow-md"
            )}
        >
            <div className="flex justify-between items-start mb-3">
                <div className="w-10 h-10 rounded bg-[var(--canvas)] flex items-center justify-center text-[var(--ink)] font-serif text-lg">
                    {profile.matchScore}
                </div>
                {isPrimary && <BlueprintBadge variant="blueprint">PRIMARY</BlueprintBadge>}
                {isSecondary && <BlueprintBadge variant="success">SECONDARY</BlueprintBadge>}
            </div>

            <div className="flex-1 space-y-1">
                <h3 className="font-serif text-lg text-[var(--ink)] leading-tight group-hover:text-[var(--blueprint)] transition-colors">
                    {profile.name}
                </h3>
                <p className="text-[10px] text-[var(--secondary)] line-clamp-3 leading-relaxed">
                    {profile.tagline}
                </p>
            </div>

            <div className="mt-4 pt-4 border-t border-[var(--border-subtle)] space-y-2">
                <div className="flex items-center gap-2 text-[10px] text-[var(--muted)]">
                    <Briefcase size={12} /> {profile.role}
                </div>
                <div className="flex items-center gap-2 text-[10px] text-[var(--muted)]">
                    <Target size={12} /> {profile.stage}
                </div>
            </div>

            <div className="absolute inset-x-0 bottom-0 py-2 bg-[var(--canvas)] text-center text-[9px] font-technical text-[var(--blueprint)] opacity-0 group-hover:opacity-100 transition-opacity uppercase tracking-widest border-t border-[var(--border-subtle)]">
                Click for Dossier
            </div>
        </div>
    );
}

// ═══════════════════════════════════════════════════════════════════════════════
// FULL SCREEN DETAIL OVERLAY
// ═══════════════════════════════════════════════════════════════════════════════
function DetailOverlay({ profile, onClose, onSetPrimary, onSetSecondary, isPrimary, isSecondary }: any) {
    useEffect(() => {
        gsap.fromTo("#detail-content", { y: 20, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3 });
    }, []);

    return (
        <div className="absolute inset-0 z-50 bg-[var(--canvas)] overflow-y-auto">
            <div id="detail-content" className="max-w-4xl mx-auto p-8 min-h-full flex flex-col">

                {/* Header Nav */}
                <div className="flex justify-between items-start mb-8 border-b border-[var(--border-subtle)] pb-6">
                    <div>
                        <button onClick={onClose} className="flex items-center gap-2 text-[var(--muted)] hover:text-[var(--ink)] mb-4 text-xs tracking-widest font-technical uppercase">
                            <ArrowLeft size={12} /> Back to Selection
                        </button>
                        <h1 className="font-serif text-4xl text-[var(--ink)] mb-2 flex items-center gap-3">
                            {profile.name}
                            {isPrimary && <BlueprintBadge variant="blueprint">PRIMARY</BlueprintBadge>}
                            {isSecondary && <BlueprintBadge variant="success">SECONDARY</BlueprintBadge>}
                        </h1>
                        <p className="text-lg text-[var(--secondary)] italic font-serif">"{profile.tagline}"</p>
                    </div>
                    <div className="flex gap-3">
                        <BlueprintButton onClick={onSetPrimary} disabled={isPrimary} className={isPrimary ? "opacity-50" : ""}>
                            {isPrimary ? "Primary Selected" : "Set as Primary"}
                        </BlueprintButton>
                        <SecondaryButton onClick={onSetSecondary} disabled={isSecondary}>
                            {isSecondary ? "Secondary Selected" : "Set as Secondary"}
                        </SecondaryButton>
                    </div>
                </div>

                {/* 3-Column Grid High Density */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">

                    {/* Col 1: WHO THEY ARE */}
                    <div className="space-y-6">
                        <h3 className="font-technical text-[10px] uppercase tracking-widest text-[var(--blueprint)] border-b pb-2">01 — Identity & Demographics</h3>

                        <div className="grid grid-cols-2 gap-4 text-sm">
                            <div>
                                <span className="block text-[var(--muted)] text-[10px] uppercase">Role</span>
                                <span className="font-medium">{profile.role}</span>
                            </div>
                            <div>
                                <span className="block text-[var(--muted)] text-[10px] uppercase">Stage</span>
                                <span className="font-medium">{profile.stage}</span>
                            </div>
                            <div>
                                <span className="block text-[var(--muted)] text-[10px] uppercase">Age / Base</span>
                                <span className="font-medium">{profile.demographics.age}, {profile.demographics.base}</span>
                            </div>
                            <div>
                                <span className="block text-[var(--muted)] text-[10px] uppercase">Income</span>
                                <span className="font-medium">{profile.demographics.income}</span>
                            </div>
                        </div>

                        <div className="bg-[var(--paper)] p-4 border border-[var(--border-subtle)] rounded">
                            <span className="block text-[var(--muted)] text-[10px] uppercase mb-2 flex items-center gap-2"><Sparkles size={12} /> Who They Want To Become</span>
                            <p className="text-sm font-serif italic text-[var(--ink)] leading-relaxed">
                                {profile.psychographics.becoming}
                            </p>
                        </div>
                    </div>

                    {/* Col 2: PSYCHOGRAPHICS */}
                    <div className="space-y-6">
                        <h3 className="font-technical text-[10px] uppercase tracking-widest text-[var(--blueprint)] border-b pb-2">02 — The Inner Game</h3>

                        <div>
                            <span className="block text-[var(--muted)] text-[10px] uppercase mb-2">Core Beliefs</span>
                            <ul className="space-y-2">
                                {profile.psychographics.beliefs.map((b: string, i: number) => (
                                    <li key={i} className="text-sm border-l-2 border-[var(--blueprint)] pl-3 text-[var(--ink)]">{b}</li>
                                ))}
                            </ul>
                        </div>

                        <div>
                            <span className="block text-[var(--muted)] text-[10px] uppercase mb-2 text-[var(--error)]">Fears & Anxieties</span>
                            <ul className="space-y-2">
                                {profile.psychographics.fears.map((f: string, i: number) => (
                                    <li key={i} className="text-sm text-[var(--secondary)]">• {f}</li>
                                ))}
                            </ul>
                        </div>
                    </div>

                    {/* Col 3: BEHAVIORS & MARKET */}
                    <div className="space-y-6">
                        <h3 className="font-technical text-[10px] uppercase tracking-widest text-[var(--blueprint)] border-b pb-2">03 — Behavior & Context</h3>

                        <div>
                            <span className="block text-[var(--muted)] text-[10px] uppercase mb-2">Market Sophistication</span>
                            <div className="flex items-center gap-3">
                                <div className="w-8 h-8 rounded-full bg-[var(--ink)] text-[var(--paper)] flex items-center justify-center font-serif">
                                    {profile.sophistication.stage}
                                </div>
                                <div>
                                    <div className="font-bold text-sm">{profile.sophistication.label}</div>
                                    <div className="text-[10px] text-[var(--secondary)] leading-tight">{profile.sophistication.why}</div>
                                </div>
                            </div>
                        </div>

                        <div>
                            <span className="block text-[var(--muted)] text-[10px] uppercase mb-2">Triggers</span>
                            <div className="flex flex-wrap gap-2">
                                {profile.behaviors.triggers.map((t: string, i: number) => (
                                    <span key={i} className="px-2 py-1 bg-[var(--warning)]/10 text-[var(--ink)] text-[10px] rounded border border-[var(--warning)]/20">{t}</span>
                                ))}
                            </div>
                        </div>

                        <div>
                            <span className="block text-[var(--muted)] text-[10px] uppercase mb-2">Hangouts & Follows</span>
                            <p className="text-xs text-[var(--secondary)]">
                                {profile.behaviors.hangouts.join(", ")}
                                <br />
                                <span className="opacity-70">Follows: {profile.behaviors.follows.join(", ")}</span>
                            </p>
                        </div>
                    </div>

                </div>

            </div>
        </div>
    );
}


export default function Step15ICPProfiles() {
    const { updateStepData, updateStepStatus, getStepById } = useOnboardingStore();
    const stepData = getStepById(16)?.data as any; // Map to 16 logically

    const [isGenerating, setIsGenerating] = useState(false);
    const [profiles, setProfiles] = useState<ICPProfile[]>(stepData?.profiles || []);
    const [primaryICP, setPrimaryICP] = useState<string | null>(stepData?.primaryICP || null);
    const [secondaryICP, setSecondaryICP] = useState<string | null>(stepData?.secondaryICP || null);
    const [confirmed, setConfirmed] = useState(stepData?.confirmed || false);
    const [viewingProfile, setViewingProfile] = useState<ICPProfile | null>(null); // For overlay
    const containerRef = useRef<HTMLDivElement>(null);

    // Deep Rich Mock Data (Context: "David vs Goliath" / "Founder Marketing")
    const mockProfiles: ICPProfile[] = [
        {
            id: "1",
            name: "The Scaling SaaS Founder",
            tagline: "Technical genius scaling from $1M to $5M but stuck in 'Founder-Led Sales' hell.",
            role: "Founder / CEO",
            stage: "Series A / Scaling",
            matchScore: 94,
            demographics: { age: "28-42", income: "$150k+", base: "Austin, SF, London, Remote" },
            psychographics: {
                beliefs: ["Data > Intuition", "Marketing is an engineering problem", "I need a system, not an agency"],
                fears: ["Hiring a VP of Marketing who does nothing", "Competitors out-raising them", "Product is great but nobody knows"],
                values: ["Efficiency", "Autonomy", "Speed"],
                becoming: "The 'Visionary Operator' who isn't stuck in the weeds anymore."
            },
            behaviors: {
                triggers: ["Missed Quarter Target", "Failed Agency Hire", "Competitor Launch"],
                hangouts: ["Hacker News", "SaaStr", "Twitter/X (Tech Twitter)"],
                follows: ["Jason Lemkin", "Lenny Rachitsky", "Paul Graham"]
            },
            sophistication: { stage: 4, label: "Product Aware", why: "Knows they need 'Positioning' but thinks it's fluff. Wants a tool to fix it." }
        },
        {
            id: "2",
            name: "The Solo Builder",
            tagline: "Bootstrapped indie hacker building in public, terrified of 'Salesy' marketing.",
            role: "Indie Founder",
            stage: "Pre-Revenue / $10k MRR",
            matchScore: 78,
            demographics: { age: "22-35", income: "$50k-$120k", base: "Digital Nomad / Global" },
            psychographics: {
                beliefs: ["Product Quality is everything", "Marketing = Lying", "If I build it, they will come (hopefully)"],
                fears: ["Looking 'Cringe'", "Wasting time on blogs nobody reads", "Zero users"],
                values: ["Freedom", "Craft", "Transparency"],
                becoming: "The 'Cult Leader' with a raving fan base of early adopters."
            },
            behaviors: {
                triggers: ["Project Launch Day", "Zero Upvotes on PH", "Stuck at $0 MRR"],
                hangouts: ["IndieHackers.com", "Discord Communities", "Reddit r/SaaS"],
                follows: ["Pieter Levels", "Danny Postma"]
            },
            sophistication: { stage: 2, label: "Problem Aware", why: "Knows they suck at marketing. Doesn't know a 'System' exists." }
        },
        {
            id: "3",
            name: "The Agency Owner",
            tagline: "Selling strategy to clients but treats their own marketing like a cobbler's children.",
            role: "Owner / Principal",
            stage: "Established (10+ Staff)",
            matchScore: 88,
            demographics: { age: "35-50", income: "$200k+", base: "NY, LA, Chicago" },
            psychographics: {
                beliefs: ["My work speaks for itself (it doesn't)", "Referrals are enough (until they dry up)", "I don't have time"],
                fears: ["Feast or Famine cycle", "Being commoditized by AI", "Irrelevance"],
                values: ["Reputation", "Creativity", "Relationships"],
                becoming: "The 'Thought Leader' who turns away business."
            },
            behaviors: {
                triggers: ["Lost a big pitch", "Referral pipeline dried up", "Client retention dip"],
                hangouts: ["LinkedIn", "Agency Slack Groups", "Clutch.co"],
                follows: ["Chris Do", "Gary Vaynerchuk"]
            },
            sophistication: { stage: 3, label: "Solution Aware", why: "Looking for 'Lead Gen' services but actually needs Positioning." }
        },
    ];

    useEffect(() => {
        if (profiles.length === 0 && !isGenerating) {
            generateICPs();
        }
    }, [profiles.length, isGenerating]);

    const generateICPs = useCallback(async () => {
        setIsGenerating(true);
        try {
            const foundationData = getStepById(0)?.data as { company_info?: any } | undefined;
            const positioningData = getStepById(12)?.data as { positioning?: any } | undefined;
            
            const response = await fetch('/api/onboarding/icp-deep', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: 'demo',
                    company_info: foundationData?.company_info || {},
                    positioning: positioningData?.positioning || {},
                    count: 3
                })
            });
            
            const data = await response.json();
            if (data.success && data.icp_profiles?.profiles) {
                const aiProfiles: ICPProfile[] = data.icp_profiles.profiles.map((profile: any, i: number) => ({
                    id: profile.id || `icp-${i}`,
                    name: profile.name,
                    tagline: profile.description,
                    role: profile.firmographics?.stage || "Unknown",
                    stage: profile.firmographics?.revenue_range || "Unknown",
                    matchScore: 85 - (i * 5), // Decrease score for secondary profiles
                    demographics: { 
                        age: "25-45", 
                        income: profile.firmographics?.revenue_range || "Unknown", 
                        base: profile.firmographics?.geography || "Global" 
                    },
                    psychographics: {
                        beliefs: profile.pain_points?.slice(0, 2).map((p: any) => p.description) || [],
                        fears: profile.pain_points?.slice(2, 4).map((p: any) => p.description) || [],
                        values: ["Growth", "Efficiency", "Results"],
                        becoming: "The successful operator who achieves their goals"
                    },
                    behaviors: {
                        triggers: profile.trigger_events?.slice(0, 2).map((t: any) => t.event) || [],
                        hangouts: ["LinkedIn", "Industry Forums"],
                        follows: ["Industry Leaders"]
                    },
                    sophistication: { 
                        stage: 3, 
                        label: "Solution Aware", 
                        why: "Understands the problem space and looking for solutions" 
                    }
                }));
                
                setProfiles(aiProfiles);
                updateStepData(16, { profiles: aiProfiles, confirmed: false });
            }
        } catch (err) {
            console.error('Failed to generate ICPs:', err);
            // Fallback to mock profiles
            setTimeout(() => {
                setProfiles(mockProfiles);
                updateStepData(16, { profiles: mockProfiles, confirmed: false });
            }, 1200);
        } finally {
            setIsGenerating(false);
        }
    }, [getStepById, updateStepData]);

    const handleSelectPrimary = (id: string) => {
        if (secondaryICP === id) setSecondaryICP(null);
        setPrimaryICP(id);
    };

    const handleSelectSecondary = (id: string) => {
        if (primaryICP === id) setPrimaryICP(null);
        setSecondaryICP(id);
    };

    const handleConfirm = () => {
        if (!primaryICP) return;
        setConfirmed(true);
        updateStepData(16, { profiles, primaryICP, secondaryICP, confirmed: true });
        updateStepStatus(16, "complete");
    };

    if (isGenerating) return <StepLoadingState title="Profiling Market" message="Identifying high-value segments..." />;

    return (
        <>
            <div ref={containerRef} className="h-full flex flex-col">

                <div className="text-center space-y-2 mb-6 shrink-0">
                    <span className="font-technical text-[10px] tracking-[0.2em] text-[var(--blueprint)] uppercase">Step 15 / 24</span>
                    <h2 className="font-serif text-2xl text-[var(--ink)]">Target Identification</h2>
                    <p className="font-serif text-[var(--secondary)] italic text-sm">"Who are we solving this for?"</p>
                </div>

                {/* Horizontal Grid */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-stretch px-4">
                    {profiles.map((p) => (
                        <div key={p.id} className="h-full animate-in">
                            <ProfileCard
                                profile={p}
                                isPrimary={primaryICP === p.id}
                                isSecondary={secondaryICP === p.id}
                                onDetails={() => setViewingProfile(p)} // Open Overlay
                            />
                        </div>
                    ))}
                </div>

                {/* Footer Action */}
                <div className="mt-auto pt-8 flex justify-center h-20 shrink-0">
                    {primaryICP && !confirmed && (
                        <div className="animate-in zoom-in">
                            <BlueprintButton onClick={handleConfirm} size="lg" className="px-12">
                                <Target size={14} /> Confirm Primary Target
                            </BlueprintButton>
                        </div>
                    )}
                    {confirmed && (
                        <div className="flex items-center gap-2 text-[var(--success)] animate-in">
                            <div className="flex flex-col items-center">
                                <CheckCircle size={24} />
                                <span className="font-medium text-xs mt-1">Target Locked</span>
                            </div>
                        </div>
                    )}
                </div>

            </div>

            {/* DETAIL OVERLAY */}
            {viewingProfile && (
                <DetailOverlay
                    profile={viewingProfile}
                    onClose={() => setViewingProfile(null)}
                    isPrimary={primaryICP === viewingProfile.id}
                    isSecondary={secondaryICP === viewingProfile.id}
                    onSetPrimary={() => handleSelectPrimary(viewingProfile.id)}
                    onSetSecondary={() => handleSelectSecondary(viewingProfile.id)}
                />
            )}
        </>
    );
}
