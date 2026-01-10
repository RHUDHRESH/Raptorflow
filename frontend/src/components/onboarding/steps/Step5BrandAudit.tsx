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

/* ══════════════════════════════════════════════════════════════════════════════
   PAPER TERMINAL — Step 5: Brand Audit (Brownfield Assessment)

   PURPOSE: Evaluate existing brand assets for alignment with validated positioning
   - Visual consistency (logo, colors, style)
   - Message clarity vs confirmed value prop
   - Proof usage and differentiation
   - Generate Green/Yellow/Red rating
   - List: Keep, Fix, Replace items
   ══════════════════════════════════════════════════════════════════════════════ */

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
            <div className="w-24 h-2 bg-[var(--canvas)] rounded-full overflow-hidden border border-[var(--border-subtle)]">
                <div className={`h-full ${colors[status]} rounded-full transition-all duration-500`} style={{ width: `${score}%` }} />
            </div>
            <span className="font-technical text-[var(--ink)] w-8">{score}</span>
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
        <BlueprintCard code={dimension.code} showCorners padding="md">
            <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-[var(--radius-sm)] bg-[var(--canvas)] border border-[var(--border)] flex items-center justify-center ${config.color}`}>
                        <Icon size={18} strokeWidth={1.5} />
                    </div>
                    <div>
                        <h3 className="text-sm font-semibold text-[var(--ink)]">{dimension.name}</h3>
                        <BlueprintBadge variant={config.badge} dot>{config.label}</BlueprintBadge>
                    </div>
                </div>
                <ScoreBar score={dimension.score} status={dimension.status} />
            </div>
            {dimension.notes.length > 0 && (
                <div className="pt-3 border-t border-[var(--border-subtle)]">
                    <ul className="space-y-1">
                        {dimension.notes.map((note, i) => (
                            <li key={i} className="flex items-start gap-2 text-sm text-[var(--secondary)]">
                                <AlertTriangle size={10} strokeWidth={1.5} className="mt-1 text-[var(--warning)] flex-shrink-0" />
                                {note}
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </BlueprintCard>
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
        keep: { color: "text-[var(--success)]", bg: "bg-[var(--success-light)]", icon: CheckCircle, label: "KEEP" },
        fix: { color: "text-[var(--warning)]", bg: "bg-[var(--warning-light)]", icon: Wrench, label: "FIX" },
        replace: { color: "text-[var(--error)]", bg: "bg-[var(--error-light)]", icon: XCircle, label: "REPLACE" },
    };
    const config = actionConfig[item.action];
    const ActionIcon = config.icon;

    return (
        <div className={`flex items-center gap-4 p-4 rounded-[var(--radius-sm)] border ${config.bg} border-[var(--border-subtle)]`}>
            <div className={`w-8 h-8 rounded-[var(--radius-xs)] ${config.bg} flex items-center justify-center ${config.color}`}>
                <ActionIcon size={16} strokeWidth={1.5} />
            </div>
            <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-0.5">
                    <span className="text-sm font-medium text-[var(--ink)]">{item.name}</span>
                    <span className="font-technical text-[8px] text-[var(--muted)]">{item.category.toUpperCase()}</span>
                    {item.priority === "high" && (
                        <BlueprintBadge variant="error" className="text-[8px]">HIGH</BlueprintBadge>
                    )}
                </div>
                <p className="text-xs text-[var(--secondary)] truncate">{item.reason}</p>
            </div>
            <div className="flex gap-1">
                {(["keep", "fix", "replace"] as const).map((action) => (
                    <button
                        key={action}
                        onClick={() => onChangeAction(item.id, action)}
                        className={`px-2 py-1 font-technical text-[10px] rounded-[var(--radius-xs)] transition-all ${item.action === action
                            ? `${actionConfig[action].bg} ${actionConfig[action].color} border border-current`
                            : "bg-[var(--canvas)] text-[var(--muted)] hover:text-[var(--ink)]"
                            }`}
                    >
                        {action.toUpperCase()}
                    </button>
                ))}
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
            { opacity: 1, y: 0, duration: 0.4, stagger: 0.06, ease: "power2.out" }
        );
    }, [hasData, isRunning]);

    // Run audit
    const runAudit = useCallback(async () => {
        if (!session?.sessionId) return;

        setIsRunning(true);

        try {
            const { data: authData } = await supabase.auth.getSession();
            const token = authData.session?.access_token;

            const res = await fetch(
                `http://localhost:8000/api/v1/onboarding/${session.sessionId}/steps/5/run`,
                {
                    method: "POST",
                    headers: token ? { Authorization: `Bearer ${token}` } : {},
                }
            );

            if (!res.ok) throw new Error("Failed to start audit");

            // Poll for results
            const pollInterval = setInterval(async () => {
                try {
                    const statusRes = await fetch(
                        `http://localhost:8000/api/v1/onboarding/${session.sessionId}/steps/5`,
                        { headers: token ? { Authorization: `Bearer ${token}` } : {} }
                    );

                    if (statusRes.ok) {
                        const data = await statusRes.json();
                        if (data?.data?.dimensions) {
                            clearInterval(pollInterval);
                            setDimensions(data.data.dimensions);
                            setBrandItems(data.data.brandItems || []);
                            setSummary(data.data.summary || "");
                            setOverallRating(data.data.overallRating || "yellow");
                            updateStepData(5, data.data);
                            setIsRunning(false);
                        }
                    }
                } catch (e) {
                    console.error("Polling error:", e);
                }
            }, 2000);

            // Timeout - use mock data
            setTimeout(() => {
                clearInterval(pollInterval);
                if (isRunning) {
                    const mockResult = generateMockAudit();
                    setDimensions(mockResult.dimensions);
                    setBrandItems(mockResult.brandItems);
                    setSummary(mockResult.summary);
                    setOverallRating(mockResult.overallRating);
                    updateStepData(5, mockResult as unknown as Record<string, unknown>);
                    setIsRunning(false);
                }
            }, 30000);
        } catch (error) {
            console.error("Audit error:", error);
            // Use mock data as fallback
            const mockResult = generateMockAudit();
            setDimensions(mockResult.dimensions);
            setBrandItems(mockResult.brandItems);
            setSummary(mockResult.summary);
            setOverallRating(mockResult.overallRating);
            updateStepData(5, mockResult as unknown as Record<string, unknown>);
            setIsRunning(false);
        }
    }, [session, updateStepData, isRunning]);

    const generateMockAudit = (): AuditResult => ({
        dimensions: [
            { id: "1", name: "Visual Identity", score: 75, status: "yellow", notes: ["Brand colors could be more consistently applied", "Consider adding visual style guidelines"], code: "AUD-01", icon: "palette" },
            { id: "2", name: "Message Clarity", score: 58, status: "yellow", notes: ["Value proposition not immediately clear", "Technical jargon may confuse prospects"], code: "AUD-02", icon: "message" },
            { id: "3", name: "Proof & Credibility", score: 45, status: "red", notes: ["Limited social proof visible", "No case studies linked", "Consider adding more testimonials"], code: "AUD-03", icon: "shield" },
            { id: "4", name: "Differentiation", score: 65, status: "yellow", notes: ["Unique angle exists but not prominently featured"], code: "AUD-04", icon: "sparkles" },
            { id: "5", name: "Consistency", score: 80, status: "green", notes: ["Good consistency in tone across channels"], code: "AUD-05", icon: "eye" },
        ],
        brandItems: [
            { id: "1", name: "Website Hero Section", category: "web", action: "fix", reason: "Value prop unclear - needs rewrite", priority: "high" },
            { id: "2", name: "Brand Colors", category: "visual", action: "keep", reason: "Strong and consistent across materials", priority: "low" },
            { id: "3", name: "Social Media Bios", category: "social", action: "fix", reason: "Inconsistent messaging across platforms", priority: "medium" },
            { id: "4", name: "Pitch Deck", category: "sales", action: "replace", reason: "Outdated stats and messaging", priority: "high" },
            { id: "5", name: "Email Signature", category: "comms", action: "fix", reason: "Missing value prop and social links", priority: "low" },
        ],
        summary: "Your brand shows good visual consistency but struggles with message clarity and credibility proof. Priority actions: rewrite website hero, update pitch deck, add social proof.",
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
            <div className="flex flex-col items-center justify-center p-12 text-center space-y-6">
                <div className="w-16 h-16 rounded-[var(--radius-md)] bg-[var(--blueprint)] flex items-center justify-center ink-bleed-md">
                    <Sparkles size={30} className="text-[var(--paper)]" />
                </div>
                <div>
                    <h3 className="font-serif text-xl text-[var(--ink)]">Ready for Brand Audit</h3>
                    <p className="text-sm text-[var(--secondary)] max-w-md mx-auto mt-2">
                        We&apos;ll analyze your brand assets for visual consistency, message clarity,
                        proof usage, and differentiation against your validated positioning.
                    </p>
                </div>
                <BlueprintButton size="lg" onClick={runAudit}>
                    <Play size={14} strokeWidth={1.5} fill="currentColor" />
                    Run Brand Audit
                </BlueprintButton>
            </div>
        );
    }

    // Loading state
    if (isRunning) {
        return (
            <StepLoadingState
                title="Analyzing Brand Assets"
                message="Evaluating visual identity, messaging, and proof points..."
                stage="Scanning web presence and uploaded materials..."
            />
        );
    }

    const ratingConfig = {
        green: { color: "text-[var(--success)]", bg: "bg-[var(--success-light)]", label: "HEALTHY", border: "border-[var(--success)]" },
        yellow: { color: "text-[var(--warning)]", bg: "bg-[var(--warning-light)]", label: "NEEDS WORK", border: "border-[var(--warning)]" },
        red: { color: "text-[var(--error)]", bg: "bg-[var(--error-light)]", label: "AT RISK", border: "border-[var(--error)]" },
    };

    return (
        <div ref={containerRef} className="space-y-6">
            {/* Overall Score Card */}
            <BlueprintCard data-animate figure="FIG. 01" title="Brand Health Score" code="SCORE" showCorners variant="elevated" padding="lg">
                <div className="flex items-center justify-between">
                    <div className="flex-1">
                        <p className="text-sm text-[var(--secondary)] mb-2">{summary}</p>
                    </div>
                    <div className="flex items-center gap-4">
                        <div className={`text-5xl font-bold ${ratingConfig[overallRating].color}`}>{overallScore}</div>
                        <div className="text-left">
                            <span className="font-technical text-[var(--muted)]">/ 100</span>
                            <BlueprintBadge variant={overallRating === "green" ? "success" : overallRating === "yellow" ? "warning" : "error"} dot className="block mt-1">
                                {ratingConfig[overallRating].label}
                            </BlueprintBadge>
                        </div>
                    </div>
                </div>
                <BlueprintProgress value={overallScore} className="mt-4" />
            </BlueprintCard>

            {/* Dimensions */}
            <div data-animate>
                <div className="flex items-center gap-3 mb-4">
                    <span className="font-technical text-[var(--blueprint)]">FIG. 02</span>
                    <div className="h-px flex-1 bg-[var(--blueprint-line)]" />
                    <span className="font-technical text-[var(--muted)]">DIMENSIONS</span>
                </div>
                <div className="grid grid-cols-1 gap-3">
                    {dimensions.map((dim) => (
                        <DimensionCard key={dim.id} dimension={dim} />
                    ))}
                </div>
            </div>

            {/* Keep / Fix / Replace Items */}
            <BlueprintCard data-animate figure="FIG. 03" title="Action Items" code="ITEMS" showCorners padding="md">
                <div className="flex items-center gap-6 mb-4 pb-4 border-b border-[var(--border-subtle)]">
                    <div className="flex items-center gap-2">
                        <CheckCircle size={14} className="text-[var(--success)]" />
                        <span className="font-technical text-[var(--success)]">{keepCount} KEEP</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <Wrench size={14} className="text-[var(--warning)]" />
                        <span className="font-technical text-[var(--warning)]">{fixCount} FIX</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <XCircle size={14} className="text-[var(--error)]" />
                        <span className="font-technical text-[var(--error)]">{replaceCount} REPLACE</span>
                    </div>
                </div>
                <div className="space-y-2">
                    {brandItems.map((item) => (
                        <BrandItemRow key={item.id} item={item} onChangeAction={handleChangeAction} />
                    ))}
                </div>
            </BlueprintCard>

            {/* Upload Missing Evidence - For users who forgot proof/testimonials */}
            <BlueprintCard data-animate figure="FIG. 04" title="Improve Your Score" code="UPLOAD" showCorners padding="md">
                <div className="flex items-start gap-4">
                    <div className="w-10 h-10 rounded-[var(--radius-sm)] bg-[var(--canvas)] border border-[var(--border)] flex items-center justify-center flex-shrink-0">
                        <Upload size={18} strokeWidth={1.5} className="text-[var(--blueprint)]" />
                    </div>
                    <div className="flex-1">
                        <h4 className="text-sm font-semibold text-[var(--ink)] mb-1">Missing Evidence?</h4>
                        <p className="text-xs text-[var(--secondary)] mb-3">
                            If you forgot to upload market research, case studies, or testimonials in Step 1,
                            you can add them now to improve your proof & credibility score.
                        </p>
                        <div className="flex flex-wrap gap-2">
                            <button
                                onClick={() => window.history.pushState({}, '', '/onboarding?step=1')}
                                className="inline-flex items-center gap-2 px-3 py-2 text-xs font-technical text-[var(--blueprint)] bg-[var(--blueprint-light)] rounded-[var(--radius-sm)] hover:bg-[var(--blueprint)]/20 transition-all"
                            >
                                <Plus size={10} strokeWidth={1.5} />Add Case Studies
                            </button>
                            <button
                                onClick={() => window.history.pushState({}, '', '/onboarding?step=1')}
                                className="inline-flex items-center gap-2 px-3 py-2 text-xs font-technical text-[var(--blueprint)] bg-[var(--blueprint-light)] rounded-[var(--radius-sm)] hover:bg-[var(--blueprint)]/20 transition-all"
                            >
                                <Plus size={10} strokeWidth={1.5} />Add Testimonials
                            </button>
                            <button
                                onClick={() => window.history.pushState({}, '', '/onboarding?step=1')}
                                className="inline-flex items-center gap-2 px-3 py-2 text-xs font-technical text-[var(--blueprint)] bg-[var(--blueprint-light)] rounded-[var(--radius-sm)] hover:bg-[var(--blueprint)]/20 transition-all"
                            >
                                <Plus size={10} strokeWidth={1.5} />Add Market Research
                            </button>
                        </div>
                        <p className="font-technical text-[8px] text-[var(--muted)] mt-3">
                            After adding evidence, click &quot;Re-run&quot; to update your audit scores
                        </p>
                    </div>
                </div>
            </BlueprintCard>

            {/* Acknowledge */}
            {!reviewed ? (
                <BlueprintCard data-animate showCorners padding="md" className="border-[var(--blueprint)]/30 bg-[var(--blueprint-light)]">
                    <div className="flex items-center justify-between">
                        <div>
                            <h3 className="text-sm font-semibold text-[var(--ink)]">Review Complete?</h3>
                            <p className="font-technical text-[var(--muted)]">ACKNOWLEDGE FINDINGS TO CONTINUE</p>
                        </div>
                        <div className="flex gap-2">
                            <SecondaryButton size="sm" onClick={runAudit}>
                                <RefreshCw size={10} strokeWidth={1.5} />
                                Re-run
                            </SecondaryButton>
                            <BlueprintButton size="sm" onClick={handleAcknowledge}>
                                <Check size={12} strokeWidth={1.5} />
                                Acknowledge
                            </BlueprintButton>
                        </div>
                    </div>
                </BlueprintCard>
            ) : (
                <BlueprintCard data-animate showCorners padding="md" className="border-[var(--success)]/30 bg-[var(--success-light)]">
                    <div className="flex items-center gap-3">
                        <Check size={18} strokeWidth={1.5} className="text-[var(--success)]" />
                        <span className="text-sm font-medium text-[var(--ink)]">Audit reviewed and acknowledged</span>
                        <BlueprintBadge variant="success" dot className="ml-auto">ACKNOWLEDGED</BlueprintBadge>
                    </div>
                </BlueprintCard>
            )}

            <div className="flex justify-center pt-4">
                <span className="font-technical text-[var(--muted)]">
                    DOCUMENT: BRAND-AUDIT | STEP 05/25 | {brandItems.length} ITEMS
                </span>
            </div>
        </div>
    );
}
