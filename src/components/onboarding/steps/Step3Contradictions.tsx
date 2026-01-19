"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import gsap from "gsap";
import {
    AlertTriangle, AlertCircle, HelpCircle, Check, ChevronDown, ChevronUp,
    Upload, MessageSquare, FileText, Play, RefreshCw, Scale, ShieldAlert,
    ArrowRight, Sparkles, Pencil
} from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { OnboardingStepLayout } from "../OnboardingStepLayout";
import { cn } from "@/lib/utils";

/* ══════════════════════════════════════════════════════════════════════════════
   PHASE 01: FOUNDATION — Step 3: Consistency Audit
   
   "Quiet Luxury: Surgery on Strategy."
   Detecting internal logical violations (e.g. Premium claim vs Low price).
   ══════════════════════════════════════════════════════════════════════════════ */

interface Issue {
    id: string;
    type: "contradiction" | "tier_violation" | "missing_evidence" | "market_mismatch";
    priority: "critical" | "high" | "medium";
    title: string;
    description: string;
    violation: { label: string; value: string }[];
    resolution?: string;
    resolved: boolean;
    code: string;
}

export default function Step3Contradictions() {
    const { session, updateStepData, updateStepStatus, getStepById } = useOnboardingStore();
    const step2Data = getStepById(2)?.data as { facts?: any[] } | undefined;
    const stepData = getStepById(3)?.data as { issues?: Issue[] } | undefined;

    const [issues, setIssues] = useState<Issue[]>(stepData?.issues || []);
    const [isAnalyzing, setIsAnalyzing] = useState(!stepData?.issues);
    const [activeIssue, setActiveIssue] = useState<string | null>(null);
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!stepData?.issues && !issues.length) {
            runContradictionAnalysis();
        } else {
            setIsAnalyzing(false);
        }
    }, [stepData]);

    const runContradictionAnalysis = async () => {
        setIsAnalyzing(true);
        try {
            const response = await fetch('/api/onboarding/contradictions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: session?.sessionId || 'demo',
                    facts: step2Data?.facts || [],
                })
            });
            
            const result = await response.json();
            
            // Map API response to our Issue format
            const apiIssues: Issue[] = (result.contradictions || []).map((c: any, idx: number) => ({
                id: c.id || `${idx + 1}`,
                type: mapContradictionType(c.type),
                priority: mapSeverity(c.severity),
                title: c.description || 'Detected Inconsistency',
                description: c.explanation || 'AI detected a potential contradiction in your data.',
                violation: c.conflicting_facts?.map((fid: string) => ({ label: 'Fact', value: fid })) || [],
                resolution: c.suggested_resolution,
                resolved: false,
                code: c.id || `CONTR-${idx + 1}`,
            }));
            
            const issuesToUse = apiIssues.length > 0 ? apiIssues : generateMockIssues();
            setIssues(issuesToUse);
            updateStepData(3, { issues: issuesToUse });
        } catch (error) {
            console.error('Contradiction analysis error:', error);
            const mockIssues = generateMockIssues();
            setIssues(mockIssues);
            updateStepData(3, { issues: mockIssues });
        }
        setIsAnalyzing(false);
    };

    const mapContradictionType = (type: string): Issue['type'] => {
        const mapping: Record<string, Issue['type']> = {
            'positioning': 'tier_violation',
            'numerical': 'contradiction',
            'semantic': 'market_mismatch',
            'financial': 'tier_violation',
        };
        return mapping[type] || 'contradiction';
    };

    const mapSeverity = (severity: string): Issue['priority'] => {
        const mapping: Record<string, Issue['priority']> = {
            'critical': 'critical',
            'high': 'high',
            'medium': 'medium',
            'low': 'medium',
        };
        return mapping[severity] || 'medium';
    };

    useEffect(() => {
        if (!containerRef.current || isAnalyzing) return;
        gsap.fromTo(
            containerRef.current.querySelectorAll("[data-animate]"),
            { opacity: 0, y: 12 },
            { opacity: 1, y: 0, duration: 0.5, stagger: 0.1, ease: "power2.out" }
        );
    }, [isAnalyzing]);

    const generateMockIssues = (): Issue[] => [
        {
            id: "1", type: "tier_violation", priority: "critical",
            title: "Premium Positioning Violation",
            description: "You claim a 'Premium/Luxury' tier in your manifesto, but your listed pricing (999 INR) aligns with budget mass-market segments. This creates brand friction.",
            violation: [
                { label: "Manifesto Claim", value: "High-end Premium Experience" },
                { label: "Price Evidence", value: "999 INR / Monthly" }
            ],
            resolved: false, code: "VIOL-PREM-01"
        },
        {
            id: "2", type: "market_mismatch", priority: "high",
            title: "Audience vs. Acquisition Mismatch",
            description: "Your target audience is 'Enterprise CTOs', but your acquisition channel is focused on 'TikTok Ads'. These usually do not align for high-ticket B2B sales.",
            violation: [
                { label: "Target ICP", value: "Enterprise-level CTO" },
                { label: "Primary Channel", value: "Short-form Social (TikTok)" }
            ],
            resolved: false, code: "MIS-AUD-04"
        }
    ];

    const handleResolve = (id: string, resolution: string) => {
        const updated = issues.map(i => i.id === id ? { ...i, resolved: true, resolution } : i);
        setIssues(updated);
        updateStepData(3, { issues: updated });
        const criticalUnresolved = updated.filter(i => i.priority === "critical" && !i.resolved);
        if (criticalUnresolved.length === 0) updateStepStatus(3, "complete");
        setActiveIssue(null);
    };

    if (isAnalyzing) {
        return (
            <div className="flex flex-col items-center justify-center p-24 space-y-8 min-h-[500px]">
                <Scale size={40} strokeWidth={1} className="animate-pulse text-[var(--ink)]" />
                <div className="text-center space-y-2">
                    <h3 className="font-serif text-2xl text-[var(--ink)]">Consistency Audit</h3>
                    <p className="text-xs font-technical uppercase tracking-[0.2em] text-[var(--ink-secondary)]">Running cross-check on business logic...</p>
                </div>
            </div>
        );
    }

    const resolvedCount = issues.filter(i => i.resolved).length;

    return (
        <OnboardingStepLayout stepId={3}>
            <div ref={containerRef} className="max-w-[1000px] mx-auto space-y-8">
                {/* Compact Header */}
                <div data-animate className="flex items-end justify-between border-b border-[var(--border-subtle)] pb-6">
                    <div className="space-y-1">
                        <h1 className="font-serif text-3xl text-[var(--ink)] tracking-tight">Consistency & Conflict</h1>
                        <p className="text-[var(--ink-secondary)] text-sm max-w-lg">
                            We've identified logical gaps in your current marketing strategy. Resolve these to ensure your brand promise matches your execution.
                        </p>
                    </div>
                </div>

                {/* Conflict Feed */}
                <div className="space-y-4">
                    {issues.map((issue) => (activeIssue === issue.id || !activeIssue || activeIssue === issue.id) && (
                        <div key={issue.id} data-animate>
                            <BlueprintCard
                                padding="none"
                                className={cn(
                                    "overflow-hidden transition-all duration-300",
                                    issue.resolved ? "opacity-50 grayscale" : "border-[var(--border-subtle)]"
                                )}
                            >
                                <div className="p-6">
                                    <div className="flex items-start justify-between">
                                        <div className="flex gap-4">
                                            <div className={cn(
                                                "w-10 h-10 rounded-xl flex items-center justify-center border",
                                                issue.resolved ? "bg-[var(--success)] border-[var(--success)] text-white" : "bg-white border-[var(--border-subtle)] text-[var(--ink)]"
                                            )}>
                                                {issue.resolved ? <Check size={18} /> : <ShieldAlert size={18} />}
                                            </div>
                                            <div className="space-y-1">
                                                <div className="flex items-center gap-3">
                                                    <h3 className="font-serif text-lg text-[var(--ink)]">{issue.title}</h3>
                                                    {!issue.resolved && <BlueprintBadge variant={issue.priority === 'critical' ? 'error' : 'warning'}>{issue.priority}</BlueprintBadge>}
                                                </div>
                                                <p className="text-sm text-[var(--ink-secondary)] leading-relaxed max-w-2xl">{issue.description}</p>
                                            </div>
                                        </div>
                                        {!issue.resolved && (
                                            <button
                                                onClick={() => setActiveIssue(activeIssue === issue.id ? null : issue.id)}
                                                className="px-4 py-2 text-[10px] font-technical uppercase tracking-widest border border-[var(--border)] rounded-full hover:bg-[var(--ink)] hover:text-white transition-all"
                                            >
                                                {activeIssue === issue.id ? 'Close' : 'Resolve'}
                                            </button>
                                        )}
                                    </div>

                                    {/* Violation Matrix */}
                                    <div className="mt-6 grid grid-cols-2 gap-4">
                                        {issue.violation.map((v, idx) => (
                                            <div key={idx} className="p-4 rounded-xl bg-[var(--canvas)] border border-[var(--border-subtle)]">
                                                <span className="text-[9px] font-technical text-[var(--ink-muted)] uppercase tracking-wider">{v.label}</span>
                                                <p className="text-sm font-medium text-[var(--ink)] mt-1">{v.value}</p>
                                            </div>
                                        ))}
                                    </div>

                                    {/* Resolution UI */}
                                    {activeIssue === issue.id && (
                                        <div className="mt-6 pt-6 border-t border-[var(--border-subtle)] animate-in slide-in-from-top-4 duration-300">
                                            <div className="space-y-4">
                                                <div className="flex items-center gap-2 mb-2">
                                                    <Sparkles size={14} className="text-[var(--ink)]" />
                                                    <span className="text-[11px] font-semibold text-[var(--ink)] uppercase tracking-tight">Strategy Adjustment</span>
                                                </div>
                                                <textarea
                                                    placeholder="Elaborate on why this isn't a conflict, or specify how you'll fix it..."
                                                    className="w-full h-24 p-4 text-sm bg-white border border-[var(--border)] rounded-xl focus:outline-none focus:border-[var(--ink)] transition-colors italic font-serif"
                                                    onChange={(e) => issue.resolution = e.target.value}
                                                />
                                                <div className="flex justify-between items-center">
                                                    <p className="text-[10px] text-[var(--ink-muted)] max-w-md">Your response will be used to calibrate future stages.</p>
                                                    <BlueprintButton onClick={() => handleResolve(issue.id, issue.resolution || "Adjusted strategy")}>
                                                        Confirm Strategic Fix
                                                    </BlueprintButton>
                                                </div>
                                            </div>
                                        </div>
                                    )}

                                    {issue.resolved && (
                                        <div className="mt-4 p-3 bg-[var(--success)]/5 border border-[var(--success)]/20 rounded-lg">
                                            <span className="text-[9px] font-technical text-[var(--success)] uppercase tracking-widest">Resolution</span>
                                            <p className="text-xs italic text-[var(--ink-secondary)] mt-1">"{issue.resolution}"</p>
                                        </div>
                                    )}
                                </div>
                            </BlueprintCard>
                        </div>
                    ))}
                </div>

                {/* Final Check */}
                {resolvedCount === issues.length && issues.length > 0 && (
                    <div data-animate className="p-12 text-center space-y-4 border-2 border-dashed border-[var(--success)]/30 rounded-3xl bg-[var(--success)]/5">
                        <div className="w-16 h-16 bg-[var(--success)] text-white rounded-full flex items-center justify-center mx-auto mb-4">
                            <Check size={32} />
                        </div>
                        <h2 className="font-serif text-3xl text-[var(--ink)]">Strategic Clarity Achieved.</h2>
                        <p className="text-[var(--ink-secondary)] max-w-md mx-auto">All detected internal contradictions have been addressed.</p>
                    </div>
                )}
            </div>
        </OnboardingStepLayout>
    );
}
