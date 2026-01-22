"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import gsap from "gsap";
import {
    TrendingUp, Check, AlertTriangle, Eye, Palette, MessageSquare, Shield, Sparkles,
    Loader2, Play, RefreshCw, X, Wrench, ArrowRight, CheckCircle, XCircle, Upload, Plus
} from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { supabase } from "@/lib/supabaseClient";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { BlueprintProgress } from "@/components/ui/BlueprintProgress";
import { StepLoadingState, StepEmptyState } from "../StepStates";

/* ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
   PAPER TERMINAL ΓÇö Step 5: Brand Audit

   PURPOSE: Evaluate existing brand assets.
   - "Quiet Luxury" Refactor: Eliminate colorful backgrounds ("fruit salad").
   - Use rigorous lines, serif headings, and minimal color indicators.
   ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ */

// Types
interface AuditDimension {
    id: string;
    name: string;
    score: number;
    status: "green" | "yellow" | "red";
    notes: string[];
    code: string;
    icon: string;
}

interface BrandItem {
    id: string;
    name: string;
    category: string;
    action: "keep" | "fix" | "replace";
    reason: string;
    priority: "high" | "medium" | "low";
}

interface AuditResult {
    dimensions: AuditDimension[];
    brandItems: BrandItem[];
    summary: string;
    overallRating: "green" | "yellow" | "red";
    reviewed: boolean;
}

// Dimension icons mapping
const DIMENSION_ICONS: Record<string, React.ElementType> = {
    "Visual Identity": Palette,
    "Message Clarity": MessageSquare,
    "Proof & Credibility": Shield,
    "Differentiation": Sparkles,
    "Consistency": Eye,
    "Sentiment": TrendingUp,
};

function ScoreBar({ score, status }: { score: number; status: "green" | "yellow" | "red" }) {
    const colors = {
        green: "bg-[var(--success)]",
        yellow: "bg-[var(--warning)]",
        red: "bg-[var(--error)]",
    };
    return (
        <div className="flex items-center gap-3">
            <div className="flex-1 h-[2px] bg-[var(--border-subtle)] overflow-hidden">
                <div className={`h-full ${colors[status]} transition-all duration-700 ease-out`} style={{ width: `${score}%` }} />
            </div>
            <span className="font-serif text-lg text-[var(--ink)] tabular-nums w-8 text-right">{score}</span>
        </div>
    );
}

function DimensionCard({ dimension }: { dimension: AuditDimension }) {
    const Icon = DIMENSION_ICONS[dimension.name] || Eye;
    const statusConfig = {
        green: { color: "text-[var(--success)]", badge: "success" as const, label: "STRONG" },
        yellow: { color: "text-[var(--warning)]", badge: "warning" as const, label: "NEEDS WORK" },
        red: { color: "text-[var(--error)]", badge: "error" as const, label: "WEAK" },
    };
    const config = statusConfig[dimension.status];

    return (
        <div className="py-4 border-b border-[var(--border-subtle)] last:border-0 group hover:bg-[var(--canvas)] transition-colors px-4 -mx-4">
            <div className="flex items-center gap-4 mb-3">
                <div className="w-8 h-8 flex items-center justify-center rounded-full border border-[var(--border)] group-hover:border-[var(--ink)] transition-colors text-[var(--muted)] group-hover:text-[var(--ink)]">
                    <Icon size={14} strokeWidth={1.5} />
                </div>
                <div className="flex-1">
                    <div className="flex items-baseline justify-between mb-1">
                        <h3 className="text-base font-serif text-[var(--ink)]">{dimension.name}</h3>
                        <span className="font-technical text-[10px] tracking-widest text-[var(--muted)]">{config.label}</span>
                    </div>
                    <ScoreBar score={dimension.score} status={dimension.status} />
                </div>
            </div>

            {dimension.notes.length > 0 && (
                <div className="pl-12">
                    <ul className="space-y-1">
                        {dimension.notes.map((note, i) => (
                            <li key={i} className="flex items-start gap-2 text-xs text-[var(--secondary)]">
                                <span className="mt-1 w-1 h-1 rounded-full bg-[var(--border)]" />
                                {note}
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}

function BrandItemRow({
    item,
    onChangeAction
}: {
    item: BrandItem;
    onChangeAction: (id: string, action: "keep" | "fix" | "replace") => void;
}) {
    const actionConfig = {
        keep: { color: "text-[var(--success)]", icon: CheckCircle, label: "KEEP" },
        fix: { color: "text-[var(--warning)]", icon: Wrench, label: "FIX" },
        replace: { color: "text-[var(--error)]", icon: XCircle, label: "REPLACE" },
    };
    const config = actionConfig[item.action];

    // Determine row style based on action - much more subtle now
    const borderClass =
        item.action === "keep" ? "border-l-2 border-l-[var(--success)]" :
            item.action === "fix" ? "border-l-2 border-l-[var(--warning)]" :
                "border-l-2 border-l-[var(--error)]";

    return (
        <div className={`flex items-start gap-4 p-4 bg-[var(--paper)] border border-[var(--border-subtle)] ${borderClass} hover:shadow-sm transition-all`}>
            <div className="flex-1 min-w-0">
                <div className="flex items-baseline justify-between mb-1">
                    <span className="text-sm font-medium text-[var(--ink)]">{item.name}</span>
                    <span className="font-technical text-[8px] text-[var(--muted)] uppercase tracking-widest">{item.category}</span>
                </div>
                <p className="text-xs text-[var(--secondary)] italic font-serif leading-relaxed mb-3">&ldquo;{item.reason}&rdquo;</p>

                <div className="flex gap-2">
                    {(["keep", "fix", "replace"] as const).map((action) => (
                        <button
                            key={action}
                            onClick={() => onChangeAction(item.id, action)}
                            className={`px-3 py-1 font-technical text-[10px] tracking-wider uppercase transition-all ${item.action === action
                                ? `bg-[var(--ink)] text-[var(--paper)]`
                                : "bg-transparent text-[var(--muted)] hover:text-[var(--ink)] box-border border border-transparent hover:border-[var(--border)]"
                                }`}
                        >
                            {action}
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
}

export default function Step5BrandAudit() {
    const { session, updateStepData, updateStepStatus, getStepById } = useOnboardingStore();
    const stepData = getStepById(5)?.data as AuditResult | undefined;

    const [isRunning, setIsRunning] = useState(false);
    const [dimensions, setDimensions] = useState<AuditDimension[]>(stepData?.dimensions || []);
    const [brandItems, setBrandItems] = useState<BrandItem[]>(stepData?.brandItems || []);
    const [summary, setSummary] = useState(stepData?.summary || "");
    const [overallRating, setOverallRating] = useState<"green" | "yellow" | "red">(stepData?.overallRating || "yellow");
    const [reviewed, setReviewed] = useState(stepData?.reviewed || false);
    const containerRef = useRef<HTMLDivElement>(null);

    const hasData = dimensions.length > 0;
    const overallScore = dimensions.length > 0 ? Math.round(dimensions.reduce((sum, d) => sum + d.score, 0) / dimensions.length) : 0;

    // Animation
    useEffect(() => {
        if (!containerRef.current || isRunning || !hasData) return;
        gsap.fromTo(
            containerRef.current.querySelectorAll("[data-animate]"),
            { opacity: 0, y: 16 },
            { opacity: 1, y: 0, duration: 0.6, stagger: 0.08, ease: "power2.out" }
        );
    }, [hasData, isRunning]);

    // Run audit (API call with fallback)
    const runAudit = useCallback(async () => {
        if (!session?.sessionId) return;
        setIsRunning(true);
        try {
            // Get evidence from previous step
            const step1Data = getStepById(1)?.data as { evidence?: any[] } | undefined;
            const evidenceList = step1Data?.evidence || [];

            const response = await fetch('/api/onboarding/brand-audit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    session_id: session.sessionId,
                    evidence_list: evidenceList 
                }),
            });

            if (response.ok) {
                const result = await response.json();
                setDimensions(result.dimensions);
                setBrandItems(result.brandItems);
                setSummary(result.summary);
                setOverallRating(result.overallRating);
                updateStepData(5, result as unknown as Record<string, unknown>);
            } else {
                // Fallback to mock data
                const mockResult = generateMockAudit();
                setDimensions(mockResult.dimensions);
                setBrandItems(mockResult.brandItems);
                setSummary(mockResult.summary);
                setOverallRating(mockResult.overallRating);
                updateStepData(5, mockResult as unknown as Record<string, unknown>);
            }

        } catch (error) {
            console.error("Audit error:", error);
            // Fallback to mock data
            const mockResult = generateMockAudit();
            setDimensions(mockResult.dimensions);
            setBrandItems(mockResult.brandItems);
            setSummary(mockResult.summary);
            setOverallRating(mockResult.overallRating);
            updateStepData(5, mockResult as unknown as Record<string, unknown>);
        } finally {
            setIsRunning(false);
        }
    }, [session, updateStepData, getStepById]);

    const generateMockAudit = (): AuditResult => ({
        dimensions: [
            { id: "1", name: "Visual Identity", score: 75, status: "yellow", notes: ["Inconsistent color usage on social", "Logo resolution low on landing page"], code: "AUD-01", icon: "palette" },
            { id: "2", name: "Message Clarity", score: 58, status: "yellow", notes: ["Technical jargon in H1", "Value prop buried below fold"], code: "AUD-02", icon: "message" },
            { id: "3", name: "Proof & Credibility", score: 45, status: "red", notes: ["Zero testimonials visible", "No data-backed claims"], code: "AUD-03", icon: "shield" },
            { id: "4", name: "Differentiation", score: 65, status: "yellow", notes: ["Similar to Competitor X", "Unique mechanism not highlighted"], code: "AUD-04", icon: "sparkles" },
            { id: "5", name: "Consistency", score: 80, status: "green", notes: ["Tone of voice is distinct and consistent"], code: "AUD-05", icon: "eye" },
        ],
        brandItems: [
            { id: "1", name: "Website Hero", category: "web", action: "fix", reason: "Headline focuses on features, not outcomes.", priority: "high" },
            { id: "2", name: "Brand Colors", category: "visual", action: "keep", reason: "Distinctive and accessible palette.", priority: "low" },
            { id: "3", name: "LinkedIn Bio", category: "social", action: "fix", reason: "Disconnect from website messaging.", priority: "medium" },
            { id: "4", name: "Sales Deck", category: "sales", action: "replace", reason: "Uses old pricing model and deprecated logo.", priority: "high" },
        ],
        summary: "Your brand foundational elements are present but lack strategic alignment. Visuals are decent, but credibility is a major weakness.",
        overallRating: "yellow",
        reviewed: false,
    });

    const handleChangeAction = (id: string, action: "keep" | "fix" | "replace") => {
        const updated = brandItems.map(item => item.id === id ? { ...item, action } : item);
        setBrandItems(updated);
        updateStepData(5, { dimensions, brandItems: updated, summary, overallRating });
    };

    const handleAcknowledge = () => {
        setReviewed(true);
        updateStepData(5, { dimensions, brandItems, summary, overallRating, reviewed: true });
        updateStepStatus(5, "complete");
    };

    // Stats
    const keepCount = brandItems.filter(i => i.action === "keep").length;
    const fixCount = brandItems.filter(i => i.action === "fix").length;
    const replaceCount = brandItems.filter(i => i.action === "replace").length;

    // Ready to audit state
    if (!hasData && !isRunning) {
        return (
            <div className="flex flex-col items-center justify-center p-24 text-center space-y-8 animate-in fade-in duration-700">
                <div className="w-24 h-24 rounded-full bg-[var(--canvas)] border border-[var(--blueprint)] flex items-center justify-center">
                    <Sparkles size={32} strokeWidth={1} className="text-[var(--blueprint)]" />
                </div>
                <div>
                    <h3 className="font-serif text-3xl text-[var(--ink)] mb-3">Brownfield Assessment</h3>
                    <p className="text-[var(--secondary)] max-w-lg mx-auto leading-relaxed">
                        We will analyze which parts of your current brand act as <span className="text-[var(--ink)] font-medium">accelerators</span> and which act as <span className="text-[var(--ink)] font-medium">anchors</span>.
                    </p>
                </div>
                <BlueprintButton size="lg" onClick={runAudit} className="px-8">
                    <Play size={14} fill="currentColor" />
                    <span>Run Diagnostic</span>
                </BlueprintButton>
            </div>
        );
    }

    // Loading state
    if (isRunning) {
        return (
            <StepLoadingState
                title="Auditing Brand Assets"
                message="Evaluating visual identity and messaging coherence..."
                stage="Scanning digital footprint..."
            />
        );
    }

    return (
        <div ref={containerRef} className="max-w-4xl mx-auto space-y-12">
            {/* Header Section */}
            <div data-animate className="flex items-start justify-between border-b border-[var(--border-subtle)] pb-8">
                <div>
                    <h2 className="font-serif text-3xl text-[var(--ink)] mb-2">Audit Report</h2>
                    <p className="text-[var(--secondary)] max-w-lg">{summary}</p>
                </div>
                <div className="text-right">
                    <div className="flex flex-col items-end">
                        <span className="font-serif text-6xl text-[var(--ink)] leading-none">{overallScore}</span>
                        <span className="font-technical text-xs tracking-widest text-[var(--muted)] mt-1">BRAND HEALTH SCORE</span>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-12 gap-12">
                {/* Main Content: Dimensions */}
                <div className="md:col-span-7 space-y-8">
                    <div data-animate>
                        <h3 className="font-technical text-xs font-bold text-[var(--muted)] uppercase tracking-widest mb-6">Performance Dimensions</h3>
                        <div className="bg-[var(--paper)] border border-[var(--border-subtle)] px-6">
                            {dimensions.map((dim) => (
                                <DimensionCard key={dim.id} dimension={dim} />
                            ))}
                        </div>
                    </div>

                    <div data-animate>
                        <h3 className="font-technical text-xs font-bold text-[var(--muted)] uppercase tracking-widest mb-6">Action Plan</h3>
                        <div className="space-y-3">
                            {brandItems.map((item) => (
                                <BrandItemRow key={item.id} item={item} onChangeAction={handleChangeAction} />
                            ))}
                        </div>
                    </div>
                </div>

                {/* Sidebar: Summary & Tools */}
                <div className="md:col-span-5 space-y-8">
                    <BlueprintCard data-animate title="Your Inventory" code="INV" showCorners padding="md">
                        <div className="space-y-4">
                            <div className="flex justify-between items-center py-2 border-b border-[var(--border-subtle)]">
                                <span className="text-sm text-[var(--secondary)]">Assets to Keep</span>
                                <span className="font-serif text-[var(--success)]">{keepCount}</span>
                            </div>
                            <div className="flex justify-between items-center py-2 border-b border-[var(--border-subtle)]">
                                <span className="text-sm text-[var(--secondary)]">Assets to Fix</span>
                                <span className="font-serif text-[var(--warning)]">{fixCount}</span>
                            </div>
                            <div className="flex justify-between items-center py-2 border-b border-[var(--border-subtle)]">
                                <span className="text-sm text-[var(--secondary)]">Assets to Drop</span>
                                <span className="font-serif text-[var(--error)]">{replaceCount}</span>
                            </div>
                        </div>
                    </BlueprintCard>

                    <div data-animate className="p-6 bg-[var(--canvas)] border border-[var(--border)] rounded-[1px]">
                        <h4 className="font-serif text-lg text-[var(--ink)] mb-2">Missing Evidence?</h4>
                        <p className="text-xs text-[var(--secondary)] mb-4 leading-relaxed">
                            Low credibility scores often come from a lack of uploaded proof. Add case studies to boost your score.
                        </p>
                        <SecondaryButton
                            onClick={() => window.history.pushState({}, '', '/onboarding?step=1')}
                            className="w-full text-xs"
                        >
                            <Upload size={12} /> Add Evidence
                        </SecondaryButton>
                    </div>

                    {!reviewed ? (
                        <div data-animate className="pt-4 border-t border-[var(--border-subtle)]">
                            <BlueprintButton onClick={handleAcknowledge} className="w-full justify-center">
                                <Check size={14} /> Accept Findings
                            </BlueprintButton>
                            <button onClick={runAudit} className="w-full text-center mt-3 text-[10px] font-technical text-[var(--muted)] hover:text-[var(--ink)] hover:underline uppercase transition-all">
                                Re-run Audit
                            </button>
                        </div>
                    ) : (
                        <div data-animate className="flex items-center justify-center gap-2 p-3 bg-[var(--success)]/5 border border-[var(--success)]/20 text-[var(--success)] text-xs font-medium">
                            <Check size={14} /> Audit Acknowledged
                        </div>
                    )}
                </div>
            </div>

            <div className="flex justify-center pt-8 border-t border-[var(--border-subtle)]">
                <span className="font-technical text-[10px] text-[var(--muted)] uppercase tracking-widest">
                    Generated {new Date().toLocaleDateString()} ΓÇó RaptorFlow Intelligence
                </span>
            </div>
        </div>
    );
}
