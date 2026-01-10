"use client";

import { useState, useRef, useEffect, useLayoutEffect } from "react";
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
    Flame,
    ArrowRight,
    Search,
    ChevronRight,
    X,
    Terminal
} from "lucide-react";
import { cn } from "@/lib/utils";
import { BlueprintButton } from "@/components/ui/BlueprintButton";

/* ══════════════════════════════════════════════════════════════════════════════
   BLACK BOX V3 — "QUIET LUXURY" + "WOW" ANIMATIONS
   Strict token adherence. No blobs. High-end motion.
   ══════════════════════════════════════════════════════════════════════════════ */

// ——— TYPES ———
type Step = "focus" | "outcome" | "volatility" | "processing" | "output";

// ——— CONSTANTS ———
const FOCUS_AREAS = [
    { id: "acquisition", label: "Acquisition", desc: "Pipeline & Leads", icon: TrendingUp },
    { id: "retention", label: "Retention", desc: "LTV & Churn", icon: Shield },
    { id: "monetization", label: "Revenue", desc: "Cash Flow & Yield", icon: Target },
    { id: "brand", label: "Brand Equity", desc: "Positioning & PR", icon: Crown },
    { id: "viral", label: "Virality", desc: "Network Effects", icon: Zap },
];

const OUTCOMES = [
    { id: "cash", label: "Immediate Cash Injection" },
    { id: "traffic", label: "Volume Spike" },
    { id: "domination", label: "Market Domination" },
    { id: "loyalty", label: "Cult Loyalty" },
    { id: "position", label: "Category Definition" },
];

const RISK_LEVELS = [
    { level: 1, label: "Safe Bet", desc: "Zero downside. Guaranteed small win." },
    { level: 2, label: "Standard", desc: "Industry best practice. Reliable." },
    { level: 3, label: "Optimized", desc: "Slightly aggressive. Good ROI." },
    { level: 4, label: "Bold", desc: "Noticeable differentiation." },
    { level: 5, label: "Aggressive", desc: "Competitors will notice." },
    { level: 6, label: "High Stakes", desc: "Risk of polarization." },
    { level: 7, label: "Radical", desc: "Breaking standard conventions." },
    { level: 8, label: "Market Shock", desc: "Experimental. Unpredictable." },
    { level: 9, label: "Career Ending", desc: "Reputational hazard." },
    { level: 10, label: "Career Ending", desc: "Burn the boats." },
];

// ——— ANIMATION UTILS ———

// Text Scramble Effect
const ScrambleText = ({ text, className, delay = 0 }: { text: string; className?: string; delay?: number }) => {
    const elementRef = useRef<HTMLSpanElement>(null);
    const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&";

    useEffect(() => {
        const el = elementRef.current;
        if (!el) return;

        let iteration = 0;
        const interval = setInterval(() => {
            el.innerText = text
                .split("")
                .map((letter, index) => {
                    if (index < iteration) {
                        return text[index];
                    }
                    return chars[Math.floor(Math.random() * chars.length)];
                })
                .join("");

            if (iteration >= text.length) {
                clearInterval(interval);
            }
            iteration += 1 / 3;
        }, 30);

        return () => clearInterval(interval);
    }, [text]);

    return <span ref={elementRef} className={className}>{text}</span>;
}

// ——— COMPONENTS ———

export default function BlackboxPage() {
    const router = useRouter();
    const containerRef = useRef<HTMLDivElement>(null);
    const contentRef = useRef<HTMLDivElement>(null);
    const [step, setStep] = useState<Step>("focus");
    const [volatility, setVolatility] = useState<number>(5);
    const [focus, setFocus] = useState<string>("");
    const [outcome, setOutcome] = useState<string>("");
    const [progress, setProgress] = useState(0);

    // Initial Entry Animation
    useLayoutEffect(() => {
        const ctx = gsap.context(() => {
            gsap.fromTo(containerRef.current,
                { opacity: 0 },
                { opacity: 1, duration: 1, ease: "power2.out" }
            );

            // Draw grid lines (Visual Adition #34)
            gsap.fromTo(".bg-grid-line",
                { scaleX: 0, transformOrigin: "center" },
                { scaleX: 1, duration: 1.5, ease: "expo.out", stagger: 0.1 }
            );
        }, containerRef);
        return () => ctx.revert();
    }, []);

    // Step Transition Orchestration (Visual Addition #27)
    const changeStep = (nextStep: Step) => {
        const tl = gsap.timeline();

        // Exit current
        tl.to(contentRef.current, {
            opacity: 0,
            y: -20,
            duration: 0.3,
            ease: "power2.in",
            onComplete: () => {
                setStep(nextStep);
                // Reset for entry
                gsap.set(contentRef.current, { y: 20 });
            }
        });

        // Enter next
        tl.to(contentRef.current, {
            opacity: 1,
            y: 0,
            duration: 0.5,
            ease: "power2.out",
            delay: 0.1 // small pause
        });
    };

    const handleFocusSelect = (label: string) => {
        setFocus(label);
        changeStep("outcome");
    };

    const handleOutcomeSelect = (label: string) => {
        setOutcome(label);
        changeStep("volatility");
    };

    // Processing Sequence (Visual Addition #28: Mechanical Loader)
    const handleGenerate = () => {
        // Flash Effect (Visual Addition #33)
        gsap.to(containerRef.current, {
            backgroundColor: "white",
            duration: 0.1,
            yoyo: true,
            repeat: 1,
            // onComplete: DISABLED - TypeScript issue
        });

        changeStep("processing");

        // Mechanical Progress
        let p = 0;
        const interval = setInterval(() => {
            // Non-linear chunks
            p += Math.random() * 15;
            if (p > 100) {
                p = 100;
                clearInterval(interval);
                setTimeout(() => changeStep("output"), 500);
            }
            setProgress(p);
        }, 150);
    };

    const handleReset = () => {
        setStep("focus");
        setFocus("");
        setOutcome("");
        setVolatility(5);
        setProgress(0);
        changeStep("focus");
    };

    const handleCreateMove = () => {
        // "Stamp" Effect logic would go here visually, then route
        const query = new URLSearchParams({
            source: 'blackbox',
            context: `Strategy: ${focus} -> ${outcome}\nRisk Level: ${volatility}/10 (${RISK_LEVELS[volatility - 1].label})`,
            tag: 'BlackBox'
        }).toString();
        router.push(`/moves?${query}`);
    };

    // Calculate breadcrumb step index
    const stepIndex = ["focus", "outcome", "volatility", "processing", "output"].indexOf(step) + 1;

    return (
        <div ref={containerRef} className="relative min-h-screen w-full bg-[var(--canvas)] flex flex-col items-center pt-24 pb-12 overflow-hidden">

            {/* BACKGROUND GRID (Fix #1: Remove blobs, strict grid) */}
            <div className="absolute inset-0 pointer-events-none z-0 flex justify-center">
                <div className="w-full max-w-[1200px] h-full relative border-x border-[var(--structure-subtle)]">
                    {/* Horizontal Lines */}
                    {[...Array(20)].map((_, i) => (
                        <div key={`h-${i}`} className="bg-grid-line absolute w-full h-[1px] bg-[var(--structure-subtle)]" style={{ top: `${(i + 1) * 5}%` }} />
                    ))}
                    {/* Vertical Lines */}
                    {[...Array(12)].map((_, i) => (
                        <div key={`v-${i}`} className="bg-grid-line absolute h-full w-[1px] bg-[var(--structure-subtle)]" style={{ left: `${(i + 1) * 8.33}%` }} />
                    ))}
                </div>
            </div>

            {/* HEADER & BREADCRUMBS */}
            <div className="relative z-10 w-full max-w-4xl px-8 mb-16 flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <div className="w-10 h-10 border border-[var(--structure)] bg-[var(--paper)] flex items-center justify-center rounded-[var(--radius)]">
                        <Terminal size={18} className="text-[var(--ink)]" strokeWidth={1.5} />
                    </div>
                    <div>
                        <h1 className="font-editorial text-2xl text-[var(--ink)] leading-none mb-1">Black Box Engine</h1>
                        <div className="font-technical text-[10px] text-[var(--ink-muted)] tracking-widest uppercase">
                            SYS.BLACKBOX // STRATEGY GEN
                        </div>
                    </div>
                </div>

                {/* Progress (Fix #13: Technical Step x/y) */}
                {step !== 'output' && (
                    <div className="flex items-center gap-4">
                        {step !== 'focus' && (
                            <button
                                onClick={() => {
                                    if (step === 'outcome') setStep('focus');
                                    if (step === 'volatility') setStep('outcome');
                                }}
                                className="font-technical text-[10px] text-[var(--ink-muted)] hover:text-[var(--ink)] uppercase tracking-widest flex items-center gap-2 transition-colors"
                            >
                                <ArrowRight className="rotate-180" size={12} /> BACK
                            </button>
                        )}
                        <div className="font-technical text-[10px] text-[var(--ink)] border border-[var(--structure)] px-3 py-1 bg-[var(--paper)] rounded-full">
                            STEP 0{Math.min(stepIndex, 4)} / 04
                        </div>
                    </div>
                )}
            </div>

            {/* MAIN CONTENT STAGE */}
            <div ref={contentRef} className="relative z-10 w-full max-w-4xl px-8 min-h-[400px] flex flex-col items-center justify-center">

                {/* STEP 1: FOCUS */}
                {step === "focus" && (
                    <div className="w-full">
                        <div className="text-center mb-12">
                            <h2 className="font-editorial text-4xl text-[var(--ink)] mb-3">Select Operational Theater</h2>
                            <p className="text-[var(--ink-secondary)] max-w-md mx-auto">Where will this strategic move be deployed?</p>
                        </div>
                        <div className="grid grid-cols-5 gap-4">
                            {FOCUS_AREAS.map((item, i) => (
                                <button
                                    key={item.id}
                                    onClick={() => handleFocusSelect(item.label)}
                                    onMouseEnter={(e) => {
                                        // Addition #22: Hover Lift
                                        gsap.to(e.currentTarget, { y: -4, duration: 0.3, ease: "power2.out" });
                                    }}
                                    onMouseLeave={(e) => {
                                        gsap.to(e.currentTarget, { y: 0, duration: 0.3, ease: "power2.out" });
                                    }}
                                    // Fix #9: radius variable, Fix #4: Borders only
                                    className="group relative flex flex-col items-center p-8 bg-[var(--paper)] border border-[var(--structure)] rounded-[var(--radius)] hover:border-[var(--ink)] transition-colors text-center overflow-hidden"
                                >
                                    {/* Addition #31: Cursor Spotlight (simplified as hover bg) */}
                                    <div className="absolute inset-0 bg-[var(--surface-subtle)] opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

                                    <div className="relative z-10 w-12 h-12 rounded-full border border-[var(--structure-subtle)] bg-[var(--canvas)] flex items-center justify-center text-[var(--ink)] mb-4 group-hover:scale-110 transition-transform duration-500">
                                        <item.icon size={20} strokeWidth={1.5} />
                                    </div>
                                    <h3 className="relative z-10 font-medium text-[var(--ink)] mb-1">{item.label}</h3>
                                    <p className="relative z-10 font-sans text-xs text-[var(--ink-muted)]">{item.desc}</p>
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {/* STEP 2: OUTCOME */}
                {step === "outcome" && (
                    <div className="w-full max-w-2xl">
                        <div className="text-center mb-12">
                            <h2 className="font-editorial text-4xl text-[var(--ink)] mb-3">Define Victory Condition</h2>
                            <p className="text-[var(--ink-secondary)]">Focus Area: <span className="font-medium text-[var(--ink)] border-b border-[var(--structure)]">{focus}</span></p>
                        </div>
                        <div className="flex flex-col gap-3">
                            {OUTCOMES.map((item, i) => (
                                <button
                                    key={item.id}
                                    onClick={() => handleOutcomeSelect(item.label)}
                                    // Fix #22: Hover Lift & #4: Borders
                                    className="group relative w-full flex items-center justify-between p-6 bg-[var(--paper)] border border-[var(--structure)] rounded-[var(--radius)] hover:border-[var(--ink)] transition-all hover:-translate-y-1"
                                >
                                    <span className="font-medium text-[var(--ink)] text-lg">{item.label}</span>
                                    <div className="w-8 h-8 rounded-full border border-[var(--structure)] flex items-center justify-center group-hover:bg-[var(--ink)] group-hover:text-[var(--paper)] transition-colors">
                                        <ArrowRight size={14} className="opacity-0 group-hover:opacity-100 transition-opacity" />
                                    </div>
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {/* STEP 3: VOLATILITY (Custom Slider) */}
                {step === "volatility" && (
                    <div className="w-full max-w-3xl">
                        <div className="text-center mb-12">
                            <h2 className="font-editorial text-4xl text-[var(--ink)] mb-3">Calibrate Risk Tolerance</h2>
                            <p className="text-[var(--ink-secondary)]">Higher volatility correlates with asymmetric upside.</p>
                        </div>

                        <div className="bg-[var(--paper)] border border-[var(--structure)] rounded-[var(--radius)] p-12 relative overflow-hidden">
                            {/* Addition #32: Shake Warning */}
                            {volatility >= 9 && (
                                <div className="absolute inset-0 pointer-events-none border-4 border-red-500/10 animate-pulse rounded-[var(--radius)]" />
                            )}

                            <div className="flex flex-col items-center">
                                {/* Addition #24: Number Ticker (Visual) */}
                                <div className="mb-8 text-center">
                                    <div className={cn(
                                        "font-data text-9xl font-bold tracking-tighter transition-colors duration-300",
                                        // Fix #19: Muted/Ink scales, strictly not neon
                                        volatility <= 3 ? "text-[var(--success)]" :
                                            volatility <= 6 ? "text-[var(--warning)]" :
                                                volatility <= 8 ? "text-[var(--ink-secondary)]" :
                                                    "text-[var(--error)]"
                                    )}>
                                        {volatility}
                                    </div>
                                    <div className="font-editorial text-2xl mt-2 text-[var(--ink)]">
                                        {RISK_LEVELS[volatility - 1].label}
                                    </div>
                                    <div className="font-sans text-sm text-[var(--ink-muted)] mt-1">
                                        {RISK_LEVELS[volatility - 1].desc}
                                    </div>
                                </div>

                                {/* Fix #10: Custom DOM Slider */}
                                <div className="w-full max-w-lg mb-12 relative h-12 flex items-center cursor-pointer group"
                                    onMouseMove={(e) => {
                                        // Simple drag logic placeholder for prototype
                                        const rect = e.currentTarget.getBoundingClientRect();
                                        const x = e.clientX - rect.left;
                                        const percent = x / rect.width;
                                        const level = Math.ceil(percent * 10);
                                        if (e.buttons === 1 && level >= 1 && level <= 10) setVolatility(level);
                                    }}
                                    onMouseDown={(e) => {
                                        const rect = e.currentTarget.getBoundingClientRect();
                                        const x = e.clientX - rect.left;
                                        const percent = x / rect.width;
                                        const level = Math.ceil(percent * 10);
                                        if (level >= 1 && level <= 10) setVolatility(level);
                                    }}
                                >
                                    {/* Track */}
                                    <div className="absolute w-full h-1 bg-[var(--structure-subtle)] rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-[var(--ink)] transition-all duration-100 ease-linear"
                                            style={{ width: `${volatility * 10}%` }}
                                        />
                                    </div>

                                    {/* Ticks (Visual Addition #25) */}
                                    <div className="absolute inset-0 flex justify-between px-[2%]">
                                        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(n => (
                                            <div key={n}
                                                className={cn(
                                                    "w-px h-3 mt-0.5 transition-colors duration-300",
                                                    n <= volatility ? "bg-[var(--ink)]" : "bg-[var(--structure)]"
                                                )}
                                            />
                                        ))}
                                    </div>

                                    {/* Thumb */}
                                    <div
                                        className="absolute w-4 h-4 bg-[var(--paper)] border-2 border-[var(--ink)] rounded-full shadow-sm transition-all duration-100 ease-linear top-1/2 -translate-y-1/2 -translate-x-1/2"
                                        style={{ left: `${volatility * 10}%` }}
                                    />
                                </div>
                            </div>

                            <div className="flex justify-center">
                                {/* Fix #5: Primary Button is Ink */}
                                <BlueprintButton
                                    onClick={handleGenerate}
                                    className="px-12 h-14 text-base"
                                >
                                    <Sparkles size={18} />
                                    Generate Strategy
                                </BlueprintButton>
                            </div>
                        </div>
                    </div>
                )}

                {/* STEP 4: PROCESSING (MECHANICAL) */}
                {step === "processing" && (
                    <div className="w-full max-w-lg text-center">
                        <h2 className="font-editorial text-2xl text-[var(--ink)] mb-8">
                            <ScrambleText text="Synthesizing Strategy..." />
                        </h2>

                        {/* Addition #28: Mechanical Loader */}
                        <div className="w-full h-2 bg-[var(--structure-subtle)] overflow-hidden rounded-full mb-4">
                            <div
                                className="h-full bg-[var(--ink)] transition-all duration-150 ease-linear"
                                style={{ width: `${progress}%` }}
                            />
                        </div>

                        {/* Addition #40: Scanning Text */}
                        <div className="flex justify-between font-mono text-xs text-[var(--ink-muted)]">
                            <span>VECTORS: {Math.round(progress * 13.4)}</span>
                            <span>PRECISION: 99.8%</span>
                        </div>
                    </div>
                )}

                {/* STEP 5: OUTPUT */}
                {step === "output" && (
                    <div className="w-full max-w-3xl">
                        {/* Fix #14: Padding luxury */}
                        <div className="bg-[var(--paper)] border border-[var(--structure)] rounded-[var(--radius)] overflow-hidden relative">

                            {/* Header */}
                            <div className="p-8 border-b border-[var(--structure)] bg-[var(--surface)]">
                                <div className="flex items-start justify-between mb-4">
                                    <div>
                                        {/* Addition #29: Text Scramble */}
                                        <div className="font-technical text-[var(--ink-muted)] mb-2">STRATEGY_ID: X99-ALPHA</div>
                                        <h2 className="font-editorial text-3xl text-[var(--ink)]">
                                            The "Pattern Break"
                                        </h2>
                                    </div>
                                    <div className="flex flex-col items-end">
                                        <div className="px-3 py-1 border border-[var(--ink)] text-[var(--ink)] text-xs font-bold uppercase rounded-full">
                                            Level {volatility} Risk
                                        </div>
                                    </div>
                                </div>
                                <p className="text-[var(--ink-secondary)] leading-relaxed max-w-xl">
                                    Leveraging <span className="font-medium text-[var(--ink)]">{focus}</span> to achieve <span className="font-medium text-[var(--ink)]">{outcome}</span>.
                                    This move is designed to disrupt standard market cadence.
                                </p>
                            </div>

                            {/* Content - "Receipt" style (Addition #30ish) */}
                            <div className="p-8 space-y-8">
                                {[
                                    { title: "The Hook", desc: "Release a contrarian data point that invalidates the competitor's main claim." },
                                    { title: "The Pivot", desc: "Offer your solution not as a 'better' alternative, but as the 'only' logical path forward." },
                                    { title: "The Close", desc: "Limit access to the first 50 customers to create artificial scarcity." }
                                ].map((phase, i) => (
                                    <div key={i} className="flex gap-6 group">
                                        <div className="flex-shrink-0 w-8 h-8 rounded-full border border-[var(--structure)] flex items-center justify-center font-mono text-xs text-[var(--ink)] group-hover:bg-[var(--ink)] group-hover:text-[var(--paper)] transition-colors">
                                            0{i + 1}
                                        </div>
                                        <div className="pt-1">
                                            <h4 className="font-bold text-[var(--ink)] mb-2">{phase.title}</h4>
                                            <p className="text-sm text-[var(--ink-secondary)] leading-relaxed">{phase.desc}</p>
                                        </div>
                                    </div>
                                ))}
                            </div>

                            {/* Actions (Fix #20: Footer alignment) */}
                            <div className="p-6 border-t border-[var(--structure)] bg-[var(--surface-subtle)] flex items-center gap-4">
                                <button
                                    onClick={handleReset}
                                    className="px-6 h-12 rounded-[var(--radius)] border border-[var(--structure)] text-[var(--ink)] font-medium hover:border-[var(--ink)] transition-colors text-sm uppercase tracking-wide"
                                >
                                    Discard
                                </button>
                                <BlueprintButton
                                    onClick={handleCreateMove}
                                    className="flex-1 h-12 text-sm"
                                >
                                    <CheckCircle2 size={16} />
                                    Accept & Execute
                                </BlueprintButton>
                            </div>
                        </div>

                        {/* Addition #38 warning */}
                        {volatility >= 9 && (
                            <div className="mt-6 flex items-center justify-center gap-2 text-[var(--error)] animate-pulse">
                                <Flame size={14} />
                                <span className="font-mono text-xs font-bold uppercase">Execute with extreme caution</span>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
