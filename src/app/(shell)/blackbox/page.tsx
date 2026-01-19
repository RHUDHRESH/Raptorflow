"use client";

import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import gsap from "gsap";
import {
    Target,
    Zap,
    TrendingUp,
    Shield,
    Crown,
    CheckCircle2,
    Sparkles,
    AlertTriangle,
    ArrowRight,
    ArrowLeft,
    Loader2,
    ExternalLink
} from "lucide-react";
import { cn } from "@/lib/utils";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { useMovesStore } from "@/stores/movesStore";
import { useAuth } from "@/components/auth/AuthProvider";
import { useFoundationStore } from "@/stores/foundationStore";

/* ════════════════════════════════════════════════════════════════════════════
   BLACK BOX ENGINE — Quiet Luxury Redesign
   Matches Moves page styling with clean cards and consistent tokens
   ══════════════════════════════════════════════════════════════════════════ */

type Step = "focus" | "outcome" | "volatility" | "processing" | "output";

interface Outcome {
    id: string;
    label: string;
    desc: string;
    icon: React.ElementType;
    category: string;
}

const OUTCOMES: Outcome[] = [
    {
        id: "market-domination",
        label: "Market Domination",
        desc: "Aggressive expansion with overwhelming force",
        icon: Target,
        category: "capture"
    },
    {
        id: "brand-immortality",
        label: "Brand Immortality",
        desc: "Create legacy that cannot be erased",
        icon: Crown,
        category: "authority"
    },
    {
        id: "viral-spiral",
        label: "Viral Spiral",
        desc: "Exponential growth through network effects",
        icon: TrendingUp,
        category: "rally"
    },
    {
        id: "fortress-position",
        label: "Fortress Position",
        desc: "Defensible moat with recurring revenue",
        icon: Shield,
        category: "deepen"
    }
];

export default function BlackBoxPage() {
    const router = useRouter();
    const containerRef = useRef<HTMLDivElement>(null);
    const [mounted, setMounted] = useState(false);
    const [step, setStep] = useState<Step>("focus");
    const [selectedOutcome, setSelectedOutcome] = useState<Outcome | null>(null);
    const [volatility, setVolatility] = useState(5);
    const [generatedStrategy, setGeneratedStrategy] = useState<any>(null);
    const [createdMoveId, setCreatedMoveId] = useState<string | null>(null);

    // Auth Integration
    const { user, profile } = useAuth();
    const { createMoveFromBlackBox } = useMovesStore();
    const { messaging } = useFoundationStore();

    useEffect(() => {
        setMounted(true);
    }, []);

    useEffect(() => {
        if (!containerRef.current || !mounted) return;
        gsap.fromTo(containerRef.current, { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.4, ease: "power2.out" });
    }, [mounted]);

    const handleOutcomeSelect = (outcomeId: string) => {
        const outcome = OUTCOMES.find(o => o.id === outcomeId);
        if (outcome) {
            setSelectedOutcome(outcome);
            setStep("volatility");
        }
    };

    const handleGenerate = async () => {
        if (!user?.id || !selectedOutcome) return;
        setStep("processing");

        try {
            const workspaceId = profile?.workspace_id;
            if (!workspaceId) {
                console.error("No workspace ID found");
                alert("Please complete onboarding setup first (Workspace ID missing)");
                setStep("focus");
                return;
            }

            const businessContext = messaging
                ? `Company: ${messaging.oneLiner}. Target: ${messaging.positioningStatement.target}. Strategy: ${messaging.positioningStatement.keyBenefit}`
                : "Aggressive growth strategy needed.";

            // Map frontend category to backend focus area
            const categoryMap: Record<string, string> = {
                "capture": "acquisition",
                "authority": "brand_equity",
                "rally": "virality",
                "deepen": "retention"
            };

            const backendFocusArea = categoryMap[selectedOutcome.category] || "revenue";

            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/blackbox/generate`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    // Add auth header if needed, but Supabase client handles it usually. 
                    // However, for fetch to backend we might need token.
                    // Let's assume Backend validates via Supabase token or just accepts it for now.
                    // If backend requires Bearer token:
                    // "Authorization": `Bearer ${session?.access_token}`
                },
                body: JSON.stringify({
                    focus_area: backendFocusArea,
                    business_context: businessContext,
                    risk_tolerance: volatility,
                    workspace_id: workspaceId,
                    user_id: user.id
                })
            });

            if (!response.ok) {
                throw new Error("Failed to generate strategy");
            }

            const data = await response.json();

            if (data.success) {
                setGeneratedStrategy({
                    title: data.strategy_name,
                    description: data.expected_upside, // Using expected upside as description or summary
                    risk: data.risk_level > 7 ? "High" : data.risk_level > 4 ? "Medium" : "Low",
                    expectedImpact: data.expected_upside,
                    timeline: "4-6 weeks", // Default or parsed from implementation_steps
                    steps: data.implementation_steps || []
                });
                setStep("output");
            } else {
                throw new Error(data.error || "Unknown generation error");
            }
        } catch (e) {
            console.error(e);
            // Fallback for demo if API fails
            setGeneratedStrategy({
                title: "Emergency Protocol (Offline)",
                description: "API Connection Failed. Using backup protocol.",
                risk: "High",
                expectedImpact: "Unknown",
                timeline: "Immediate",
                steps: ["Check network connection", "Retry generation", "Contact support"]
            });
            setStep("output");
        }
    };

    const handleCreateMove = async () => {
        if (!selectedOutcome || !generatedStrategy || !user?.id) return;
        const workspaceId = profile?.workspace_id;

        // Create move using the store
        const moveId = await createMoveFromBlackBox({
            focusArea: selectedOutcome.label,
            desiredOutcome: generatedStrategy.description,
            volatilityLevel: volatility,
            name: generatedStrategy.title,
            steps: generatedStrategy.steps || []
        }, user.id, workspaceId);

        setCreatedMoveId(moveId);
    };

    const handleViewMove = () => {
        if (createdMoveId) {
            router.push(`/moves?highlight=${createdMoveId}`);
        }
    };

    const handleReset = () => {
        setStep("focus");
        setSelectedOutcome(null);
        setVolatility(5);
        setGeneratedStrategy(null);
        setCreatedMoveId(null);
    };

    const handleBack = () => {
        if (step === "volatility") setStep("focus");
        if (step === "output") setStep("volatility");
    };

    const stepIndex = ["focus", "volatility", "processing", "output"].indexOf(step);
    const totalSteps = 3; // focus, volatility, output (processing is transitional)

    if (!mounted) return null;

    return (
        <div ref={containerRef} className="min-h-screen bg-[var(--canvas)]" style={{ opacity: 0 }}>
            {/* Page Header - Quiet Luxury */}
            <div className="border-b border-[var(--border)] bg-[var(--paper)]">
                <div className="max-w-4xl mx-auto px-6 py-6">
                    <div className="flex items-start justify-between">
                        <div>
                            <h1 className="font-serif text-3xl text-[var(--ink)]">
                                Black Box Engine
                            </h1>
                            <p className="text-sm text-[var(--muted)] mt-1">
                                Strategic outcome generator — define ambition, receive precision
                            </p>
                        </div>

                        {/* Progress Indicator */}
                        <div className="flex items-center gap-4">
                            {step !== "focus" && step !== "processing" && (
                                <button
                                    onClick={handleBack}
                                    className="flex items-center gap-2 text-sm text-[var(--muted)] hover:text-[var(--ink)] transition-colors"
                                >
                                    <ArrowLeft size={14} />
                                    Back
                                </button>
                            )}
                            <div className="flex items-center gap-1.5">
                                {[0, 1, 2].map((i) => (
                                    <div
                                        key={i}
                                        className={cn(
                                            "w-2 h-2 rounded-full transition-colors",
                                            i <= Math.min(stepIndex, 2) ? "bg-[var(--ink)]" : "bg-[var(--border)]"
                                        )}
                                    />
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="max-w-4xl mx-auto px-6 py-12">

                {/* STEP 1: FOCUS / OUTCOME SELECTION */}
                {step === "focus" && (
                    <div className="max-w-3xl mx-auto">
                        <div className="text-center mb-12">
                            <h2 className="font-serif text-2xl text-[var(--ink)] mb-3">Define Your Ambition</h2>
                            <p className="text-[var(--muted)]">
                                What impossible outcome will you make inevitable?
                            </p>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {OUTCOMES.map((outcome) => {
                                const IconComponent = outcome.icon;
                                return (
                                    <BlueprintCard
                                        key={outcome.id}
                                        showCorners
                                        padding="lg"
                                        className="cursor-pointer hover:border-[var(--ink)] transition-all group"
                                        onClick={() => handleOutcomeSelect(outcome.id)}
                                    >
                                        <div className="flex items-start gap-4">
                                            <div className="w-12 h-12 rounded-[var(--radius)] bg-[var(--surface)] border border-[var(--border)] flex items-center justify-center text-[var(--muted)] group-hover:text-[var(--ink)] group-hover:border-[var(--ink)] transition-all">
                                                <IconComponent size={20} />
                                            </div>
                                            <div className="flex-1">
                                                <h3 className="font-medium text-[var(--ink)] mb-1 group-hover:text-[var(--ink)]">{outcome.label}</h3>
                                                <p className="text-sm text-[var(--muted)]">{outcome.desc}</p>
                                            </div>
                                        </div>
                                    </BlueprintCard>
                                );
                            })}
                        </div>
                    </div>
                )}

                {/* STEP 2: VOLATILITY */}
                {step === "volatility" && selectedOutcome && (
                    <div className="max-w-2xl mx-auto">
                        <div className="text-center mb-12">
                            <h2 className="font-serif text-2xl text-[var(--ink)] mb-3">Set Volatility</h2>
                            <p className="text-[var(--muted)]">
                                How aggressive should this strategy be?
                            </p>
                        </div>

                        <BlueprintCard showCorners padding="lg">
                            {/* Selected Outcome */}
                            <div className="flex items-center gap-3 mb-8 pb-6 border-b border-[var(--border)]">
                                <div className="w-10 h-10 rounded-full bg-[var(--ink)] text-white flex items-center justify-center">
                                    <selectedOutcome.icon size={18} />
                                </div>
                                <div>
                                    <div className="font-medium text-[var(--ink)]">{selectedOutcome.label}</div>
                                    <div className="text-xs text-[var(--muted)]">{selectedOutcome.category}</div>
                                </div>
                            </div>

                            {/* Volatility Slider */}
                            <div className="mb-8">
                                <div className="flex justify-between items-center mb-4">
                                    <span className="text-xs font-medium text-[var(--muted)] uppercase tracking-wide">Conservative</span>
                                    <span className="text-xs font-medium text-[var(--muted)] uppercase tracking-wide">Aggressive</span>
                                </div>

                                <input
                                    type="range"
                                    min="1"
                                    max="10"
                                    value={volatility}
                                    onChange={(e) => setVolatility(Number(e.target.value))}
                                    className="w-full h-2 bg-[var(--border)] rounded-lg appearance-none cursor-pointer"
                                    style={{
                                        background: `linear-gradient(to right, var(--ink) 0%, var(--ink) ${volatility * 10}%, var(--border) ${volatility * 10}%, var(--border) 100%)`
                                    }}
                                />

                                <div className="flex justify-between mt-2">
                                    {[...Array(10)].map((_, i) => (
                                        <div key={i} className={cn("w-1 h-1 rounded-full", i < volatility ? "bg-[var(--ink)]" : "bg-[var(--border)]")} />
                                    ))}
                                </div>
                            </div>

                            <div className="text-center py-4 bg-[var(--surface)] rounded-[var(--radius)] border border-[var(--border)]">
                                <div className="text-2xl font-bold text-[var(--ink)] mb-1">Level {volatility}</div>
                                <div className="text-sm text-[var(--muted)]">
                                    {volatility <= 3 && "Steady growth with minimal risk"}
                                    {volatility > 3 && volatility <= 6 && "Balanced approach with moderate risk"}
                                    {volatility > 6 && volatility <= 8 && "Aggressive expansion with calculated risk"}
                                    {volatility > 8 && "Maximum disruption with high risk/reward"}
                                </div>
                            </div>

                            {/* Generate Button */}
                            <div className="mt-8 flex justify-center">
                                <button
                                    onClick={handleGenerate}
                                    className="flex items-center gap-2 px-8 py-3 bg-[var(--ink)] text-white rounded-[var(--radius)] hover:bg-[var(--ink)]/90 transition-all font-medium"
                                >
                                    <Sparkles size={16} />
                                    Generate Strategy
                                </button>
                            </div>
                        </BlueprintCard>
                    </div>
                )}

                {/* STEP 3: PROCESSING */}
                {step === "processing" && (
                    <div className="max-w-md mx-auto text-center py-16">
                        <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-[var(--surface)] border border-[var(--border)] flex items-center justify-center">
                            <Loader2 size={24} className="text-[var(--muted)] animate-spin" />
                        </div>
                        <h2 className="font-serif text-xl text-[var(--ink)] mb-3">Generating Strategy</h2>
                        <p className="text-[var(--muted)] mb-8">
                            Synthesizing pathways and calculating optimal vectors...
                        </p>

                        <div className="space-y-3 text-left max-w-xs mx-auto">
                            <div className="flex items-center gap-3">
                                <div className="w-2 h-2 rounded-full bg-[var(--ink)] animate-pulse" />
                                <span className="text-sm text-[var(--ink)]">Analyzing market conditions</span>
                            </div>
                            <div className="flex items-center gap-3">
                                <div className="w-2 h-2 rounded-full bg-[var(--ink)] animate-pulse" style={{ animationDelay: '0.2s' }} />
                                <span className="text-sm text-[var(--ink)]">Calculating risk vectors</span>
                            </div>
                            <div className="flex items-center gap-3">
                                <div className="w-2 h-2 rounded-full bg-[var(--ink)] animate-pulse" style={{ animationDelay: '0.4s' }} />
                                <span className="text-sm text-[var(--ink)]">Optimizing resource allocation</span>
                            </div>
                        </div>
                    </div>
                )}

                {/* STEP 4: OUTPUT */}
                {step === "output" && generatedStrategy && (
                    <div className="max-w-3xl mx-auto">
                        <div className="text-center mb-12">
                            <div className="w-12 h-12 mx-auto mb-4 rounded-full bg-green-100 border border-green-200 flex items-center justify-center">
                                <CheckCircle2 size={20} className="text-green-600" />
                            </div>
                            <h2 className="font-serif text-2xl text-[var(--ink)] mb-2">Strategy Generated</h2>
                            <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-green-100 text-green-700 text-sm font-medium rounded-full">
                                <CheckCircle2 size={12} />
                                Ready for Execution
                            </span>
                        </div>

                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                            {/* Strategy Summary */}
                            <BlueprintCard showCorners padding="lg">
                                <h3 className="font-semibold text-[var(--ink)] mb-4">{generatedStrategy.title}</h3>
                                <p className="text-sm text-[var(--muted)] mb-6">{generatedStrategy.description}</p>

                                <div className="space-y-3">
                                    <div className="flex justify-between items-center py-2 border-b border-[var(--border)]">
                                        <span className="text-sm text-[var(--muted)]">Risk Level</span>
                                        <span className={cn(
                                            "px-2.5 py-0.5 rounded-full text-xs font-medium",
                                            generatedStrategy.risk === "Low" && "bg-green-100 text-green-700",
                                            generatedStrategy.risk === "Medium" && "bg-amber-100 text-amber-700",
                                            generatedStrategy.risk === "High" && "bg-red-100 text-red-700"
                                        )}>
                                            {generatedStrategy.risk}
                                        </span>
                                    </div>
                                    <div className="flex justify-between items-center py-2 border-b border-[var(--border)]">
                                        <span className="text-sm text-[var(--muted)]">Expected Impact</span>
                                        <span className="text-sm font-medium text-[var(--ink)]">{generatedStrategy.expectedImpact}</span>
                                    </div>
                                    <div className="flex justify-between items-center py-2">
                                        <span className="text-sm text-[var(--muted)]">Timeline</span>
                                        <span className="text-sm font-medium text-[var(--ink)]">{generatedStrategy.timeline}</span>
                                    </div>
                                </div>
                            </BlueprintCard>

                            {/* Execution Plan */}
                            <BlueprintCard showCorners padding="lg">
                                <h3 className="font-semibold text-[var(--ink)] mb-4">Execution Plan</h3>
                                <div className="space-y-4">
                                    <div className="flex items-start gap-3">
                                        <div className="w-6 h-6 rounded-full bg-[var(--ink)] flex items-center justify-center text-white text-xs font-bold shrink-0">1</div>
                                        <div>
                                            <div className="font-medium text-[var(--ink)] text-sm mb-0.5">Market Preparation</div>
                                            <div className="text-xs text-[var(--muted)]">Establish foundation and reconnaissance</div>
                                        </div>
                                    </div>
                                    <div className="flex items-start gap-3">
                                        <div className="w-6 h-6 rounded-full bg-[var(--border)] flex items-center justify-center text-[var(--muted)] text-xs font-bold shrink-0">2</div>
                                        <div>
                                            <div className="font-medium text-[var(--ink)] text-sm mb-0.5">Strategic Deployment</div>
                                            <div className="text-xs text-[var(--muted)]">Execute primary initiatives</div>
                                        </div>
                                    </div>
                                    <div className="flex items-start gap-3">
                                        <div className="w-6 h-6 rounded-full bg-[var(--border)] flex items-center justify-center text-[var(--muted)] text-xs font-bold shrink-0">3</div>
                                        <div>
                                            <div className="font-medium text-[var(--ink)] text-sm mb-0.5">Optimization & Scale</div>
                                            <div className="text-xs text-[var(--muted)]">Refine and expand successful elements</div>
                                        </div>
                                    </div>
                                </div>
                            </BlueprintCard>
                        </div>

                        {/* Actions */}
                        <div className="flex justify-center gap-4">
                            {!createdMoveId ? (
                                <>
                                    <button
                                        onClick={handleReset}
                                        className="px-6 py-2.5 border border-[var(--border)] text-[var(--ink)] rounded-[var(--radius)] hover:border-[var(--ink)] transition-colors font-medium text-sm"
                                    >
                                        Discard
                                    </button>
                                    <button
                                        onClick={handleCreateMove}
                                        className="flex items-center gap-2 px-6 py-2.5 bg-[var(--ink)] text-white rounded-[var(--radius)] hover:bg-[var(--ink)]/90 transition-all font-medium text-sm"
                                    >
                                        <CheckCircle2 size={14} />
                                        Accept & Create Move
                                    </button>
                                </>
                            ) : (
                                <>
                                    <button
                                        onClick={handleReset}
                                        className="px-6 py-2.5 border border-[var(--border)] text-[var(--ink)] rounded-[var(--radius)] hover:border-[var(--ink)] transition-colors font-medium text-sm"
                                    >
                                        Create Another
                                    </button>
                                    <button
                                        onClick={handleViewMove}
                                        className="flex items-center gap-2 px-6 py-2.5 bg-green-600 text-white rounded-[var(--radius)] hover:bg-green-700 transition-all font-medium text-sm"
                                    >
                                        <ExternalLink size={14} />
                                        View Created Move
                                    </button>
                                </>
                            )}
                        </div>

                        {/* Success Message */}
                        {createdMoveId && (
                            <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-[var(--radius)] text-center">
                                <div className="flex items-center justify-center gap-2 text-green-700 font-medium">
                                    <CheckCircle2 size={16} />
                                    Move created successfully!
                                </div>
                                <p className="text-sm text-green-600 mt-1">
                                    Your strategy has been converted to an actionable move.
                                </p>
                            </div>
                        )}

                        {/* High Volatility Warning */}
                        {volatility >= 9 && (
                            <div className="mt-6 flex items-center justify-center gap-2 text-amber-600">
                                <AlertTriangle size={14} />
                                <span className="text-xs font-medium uppercase tracking-wide">Execute with extreme caution</span>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
