"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ArrowRight, BookOpen, Brain, TrendingUp, Lightbulb } from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { BlueprintButton } from "@/components/ui/BlueprintButton";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { cn } from "@/lib/utils";

/* ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
   PAPER TERMINAL ΓÇö Step 16: Buying Process (Education)

   PURPOSE: "Show & Tell" - Educate user on how their customer buys.
   - Market Sophistication visualizer.
   - User Journey Steps.
   - No Inputs, just "Continue".
   ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ */

const BUYING_STAGES = [
    { id: 1, label: "Unaware", desc: "Don't know they have a problem." },
    { id: 2, label: "Problem Aware", desc: "Know the pain, seeking names for it." },
    { id: 3, label: "Solution Aware", desc: "Comparing categories (e.g., Agency vs SaaS)." },
    { id: 4, label: "Product Aware", desc: "Comparing You vs Competitors." },
    { id: 5, label: "Most Aware", desc: "Ready to buy, need an offer." },
];

export default function Step15BuyingProcess() {
    const { updateStepStatus } = useOnboardingStore();
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!containerRef.current) return;
        gsap.fromTo(containerRef.current.querySelectorAll("[data-animate]"),
            { opacity: 0, y: 16 },
            { opacity: 1, y: 0, duration: 0.6, stagger: 0.1, ease: "power2.out" }
        );
    }, []);

    const handleContinue = () => {
        updateStepStatus(16, "complete");
    };

    return (
        <div ref={containerRef} className="h-full flex flex-col max-w-5xl mx-auto space-y-8 pb-8">

            {/* Header */}
            <div data-animate className="text-center space-y-3 shrink-0">
                <span className="font-technical text-[10px] tracking-[0.2em] text-[var(--blueprint)] uppercase">Step 16 / 23</span>
                <h2 className="font-serif text-3xl text-[var(--ink)]">The Buying Logic</h2>
                <div className="flex items-center justify-center gap-2 text-[var(--secondary)]">
                    <BookOpen size={14} />
                    <span className="font-serif italic text-sm">"Understanding how your customer's brain makes the leap."</span>
                </div>
            </div>

            {/* Main Educational Content - Split Grid */}
            <div className="flex-1 min-h-0 grid grid-cols-1 md:grid-cols-2 gap-8 items-start">

                {/* Left: Market Sophistication */}
                <BlueprintCard data-animate figure="FIG. A" title="Market Sophistication" code="LVL" showCorners padding="lg" className="h-full">
                    <div className="flex items-start gap-3 mb-6">
                        <div className="p-2 bg-[var(--blueprint-light)] rounded-lg text-[var(--blueprint)]">
                            <Brain size={20} />
                        </div>
                        <div>
                            <p className="text-sm text-[var(--ink)] leading-relaxed">
                                Your market isn't a monolith. They are at different stages of awareness.
                                We tailor messaging to <strong>meet them where they are</strong>.
                            </p>
                        </div>
                    </div>

                    <div className="space-y-4 relative">
                        <div className="absolute left-[15px] top-4 bottom-4 w-0.5 bg-[var(--border)]" />
                        {BUYING_STAGES.map((stage) => (
                            <div key={stage.id} className="relative pl-10 group">
                                <div className="absolute left-0 top-1 w-8 h-8 rounded-full bg-[var(--canvas)] border border-[var(--border)] flex items-center justify-center font-technical text-[10px] text-[var(--muted)] group-hover:border-[var(--blueprint)] group-hover:text-[var(--blueprint)] transition-colors z-10">
                                    {stage.id}
                                </div>
                                <div className="p-3 rounded border border-[var(--border-subtle)] bg-[var(--canvas)] group-hover:shadow-sm transition-shadow">
                                    <h4 className="font-serif text-sm text-[var(--ink)] font-medium mb-1">{stage.label}</h4>
                                    <p className="text-xs text-[var(--secondary)]">{stage.desc}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </BlueprintCard>

                {/* Right: The Shift */}
                <div className="space-y-6">
                    <BlueprintCard data-animate figure="FIG. B" title="The Cognitive Shift" code="SHIFT" showCorners padding="lg">
                        <div className="flex items-start gap-3 mb-4">
                            <div className="p-2 bg-[var(--success-light)] rounded-lg text-[var(--success)]">
                                <TrendingUp size={20} />
                            </div>
                            <p className="text-sm text-[var(--ink)]">
                                We help them cross the chasm from <strong>"Problem Aware"</strong> to <strong>"Product Aware"</strong>.
                            </p>
                        </div>

                        <div className="p-6 bg-[var(--ink)] text-[var(--paper)] rounded-lg text-center space-y-4">
                            <div className="text-sm font-technical opacity-70 uppercase tracking-widest">Your Strategy</div>
                            <h3 className="text-2xl font-serif">Education First</h3>
                            <p className="text-sm opacity-80 leading-relaxed">
                                Since you chose a <strong>Category Creator</strong> strategy, you cannot just sell features.
                                You must first sell the <strong>Problem</strong> and the <strong>New Way</strong>.
                            </p>
                        </div>
                    </BlueprintCard>

                    <BlueprintCard data-animate figure="FIG. C" title="Key Takeaway" code="KEY" showCorners padding="lg" className="bg-[var(--blueprint-light)] border-[var(--blueprint)]/30">
                        <div className="flex gap-4">
                            <Lightbulb size={24} className="text-[var(--blueprint)] shrink-0" />
                            <div>
                                <h4 className="font-serif text-lg text-[var(--ink)] mb-2">Don't Sell Too Early</h4>
                                <p className="text-sm text-[var(--secondary)]">
                                    Trying to close a "Problem Aware" customer with a "Buy Now" offer will fail.
                                    We will build messaging that educates them first.
                                </p>
                            </div>
                        </div>
                    </BlueprintCard>
                </div>
            </div>

            {/* Footer */}
            <div data-animate className="flex justify-center pt-6">
                <BlueprintButton onClick={handleContinue} size="lg" className="px-12">
                    <span>Understood, Let's Build Messaging</span> <ArrowRight size={14} />
                </BlueprintButton>
            </div>
        </div>
    );
}
