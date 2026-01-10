"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { Compass, ArrowRight, Play } from "lucide-react";
import { BlueprintButton } from "@/components/ui/BlueprintButton";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";

interface WelcomeScreenProps {
    onNext: () => void;
}

export function WelcomeScreen({ onNext }: WelcomeScreenProps) {
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const tl = gsap.timeline({ defaults: { ease: "power2.out" } });

        // Initial setup
        gsap.set("[data-anim]", { opacity: 0, y: 20 });
        gsap.set(".blueprint-line", { scaleX: 0 });

        // Animation sequence
        tl.to(".blueprint-line", { scaleX: 1, duration: 1.2, ease: "power3.inOut" })
            .to("[data-anim]", { opacity: 1, y: 0, stagger: 0.15, duration: 0.8 }, "-=0.8");

    }, []);

    return (
        <div ref={containerRef} className="max-w-4xl mx-auto w-full px-6 flex flex-col items-center text-center relative z-10">

            {/* Architectural Header */}
            <div data-anim className="mb-12 relative">
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[200%] h-px bg-[var(--blueprint-line)] blueprint-line origin-center" />
                <div className="relative inline-flex flex-col items-center bg-[var(--canvas)] px-8 py-4">
                    <div className="h-16 w-16 mb-6 rounded-[var(--radius-md)] bg-[var(--ink)] text-[var(--paper)] flex items-center justify-center ink-bleed-md">
                        <Compass size={32} strokeWidth={1.5} />
                    </div>
                    <div className="flex items-center gap-3 text-xs font-technical text-[var(--blueprint)] tracking-widest uppercase mb-2">
                        <span>System Initialization</span>
                        <div className="h-px w-4 bg-[var(--blueprint)]" />
                        <span>V 1.0.0</span>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <h1 data-anim className="font-editorial text-5xl md:text-6xl text-[var(--ink)] mb-6 leading-[1.1]">
                Welcome to<br />
                <span className="italic">RaptorFlow</span>
            </h1>

            <p data-anim className="text-xl text-[var(--secondary)] max-w-2xl leading-relaxed mb-12">
                We are building your founder operating system.
                This brief calibration will customize your workspace, strategy, and AI models.
            </p>

            <div data-anim className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-3xl mb-12">
                {[
                    { title: "Define Core", desc: "Establish your brand's immutable laws." },
                    { title: "Target Market", desc: "Identify your ideal customer profile." },
                    { title: "Build Strategy", desc: "Generate your 90-day execution plan." }
                ].map((step, i) => (
                    <BlueprintCard key={i} padding="md" showCorners className="text-left group hover:border-[var(--blueprint)] transition-colors">
                        <div className="flex items-center gap-2 mb-2 font-technical text-[var(--muted)] text-xs">
                            <div className="w-5 h-5 rounded-full border border-[var(--border)] flex items-center justify-center group-hover:border-[var(--blueprint)] group-hover:text-[var(--blueprint)]">
                                {i + 1}
                            </div>
                            <span>STEP 0{i + 1}</span>
                        </div>
                        <h3 className="font-medium text-[var(--ink)] mb-1">{step.title}</h3>
                        <p className="text-sm text-[var(--secondary)]">{step.desc}</p>
                    </BlueprintCard>
                ))}
            </div>

            {/* Action Area */}
            <div data-anim className="flex flex-col items-center gap-6">
                <BlueprintButton size="lg" onClick={onNext} className="group min-w-[240px]">
                    Begin Calibration
                    <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
                </BlueprintButton>

                <div className="flex items-center gap-2 text-xs text-[var(--muted)] font-technical">
                    <Play size={10} fill="currentColor" />
                    <span>ESTIMATED TIME: 2 MIN 30 SEC</span>
                </div>
            </div>

            {/* Background elements (local to component for portability) */}
            <div className="fixed inset-0 pointer-events-none z-0">
                <div className="absolute top-[20%] left-[10%] w-px h-32 bg-gradient-to-b from-transparent via-[var(--blueprint-line)] to-transparent opacity-50" />
                <div className="absolute bottom-[20%] right-[10%] w-px h-32 bg-gradient-to-b from-transparent via-[var(--blueprint-line)] to-transparent opacity-50" />
            </div>
        </div>
    );
}
