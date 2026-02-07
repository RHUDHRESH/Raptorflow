<<<<<<< HEAD:src/components/onboarding/WelcomeScreen.tsx
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
            <h1 data-anim className="font-serif text-5xl md:text-6xl text-[var(--ink)] mb-6 leading-[1.1]">
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
=======
'use client';

import React, { useEffect, useRef, useState } from 'react';
import { ArrowRight } from 'lucide-react';
import gsap from 'gsap';

interface WelcomeScreenProps {
    onStart: () => void;
}

export function WelcomeScreen({ onStart }: WelcomeScreenProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const titleRef = useRef<HTMLHeadingElement>(null);
    const subtitleRef = useRef<HTMLParagraphElement>(null);
    const ctaRef = useRef<HTMLButtonElement>(null);
    const particlesRef = useRef<HTMLDivElement>(null);
    const [isExiting, setIsExiting] = useState(false);

    // Cinematic entrance animation
    useEffect(() => {
        if (!containerRef.current) return;

        const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });

        // Set initial states
        gsap.set(titleRef.current, { opacity: 0, y: 60 });
        gsap.set(subtitleRef.current, { opacity: 0, y: 40 });
        gsap.set(ctaRef.current, { opacity: 0, y: 30, scale: 0.95 });

        // Animate in sequence
        tl.to(titleRef.current, { opacity: 1, y: 0, duration: 1.2 }, 0.5)
            .to(subtitleRef.current, { opacity: 1, y: 0, duration: 0.8 }, 1.0)
            .to(ctaRef.current, { opacity: 1, y: 0, scale: 1, duration: 0.6 }, 1.3);

        return () => { tl.kill(); };
    }, []);

    // Exit animation
    const handleStart = () => {
        if (isExiting) return;
        setIsExiting(true);

        const tl = gsap.timeline({
            defaults: { ease: 'power3.inOut' },
            onComplete: onStart,
        });

        // Fade everything out dramatically
        tl.to([titleRef.current, subtitleRef.current], {
            opacity: 0,
            y: -30,
            duration: 0.5,
            stagger: 0.1
        })
            .to(ctaRef.current, {
                opacity: 0,
                scale: 0.9,
                duration: 0.3
            }, '-=0.3')
            .to(containerRef.current, {
                opacity: 0,
                duration: 0.4
            }, '-=0.2');
    };

    return (
        <div
            ref={containerRef}
            className="fixed inset-0 bg-[#0E1112] z-50 flex flex-col items-center justify-center overflow-hidden"
        >
            {/* Ambient particles */}
            <div ref={particlesRef} className="absolute inset-0 pointer-events-none">
                {Array.from({ length: 40 }).map((_, i) => (
                    <div
                        key={i}
                        className="absolute rounded-full bg-white/5"
                        style={{
                            left: `${Math.random() * 100}%`,
                            top: `${Math.random() * 100}%`,
                            width: `${2 + Math.random() * 4}px`,
                            height: `${2 + Math.random() * 4}px`,
                            animation: `subtleFloat ${8 + Math.random() * 12}s ease-in-out infinite`,
                            animationDelay: `${Math.random() * 5}s`,
                        }}
                    />
                ))}
            </div>

            {/* Gradient glow */}
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                <div className="w-[600px] h-[600px] bg-white/[0.02] rounded-full blur-[100px]" />
            </div>

            {/* Content */}
            <div className="relative z-10 max-w-[600px] text-center px-8">
                {/* Logo mark */}
                <div className="inline-flex items-center gap-3 mb-16 opacity-40">
                    <div className="w-5 h-5 bg-white rounded-sm" />
                    <span className="text-[10px] font-mono uppercase tracking-[0.3em] text-white/50">
                        RaptorFlow
                    </span>
                </div>

                {/* Title - Revealed word by word */}
                <h1
                    ref={titleRef}
                    className="font-serif text-[64px] leading-[1.05] text-white tracking-[-0.03em] mb-8"
                >
                    Build Your<br />
                    <span className="text-white/60">Marketing Foundation</span>
                </h1>

                {/* Subtitle */}
                <p
                    ref={subtitleRef}
                    className="text-[18px] text-white/50 leading-relaxed mb-16 max-w-[440px] mx-auto"
                >
                    10 minutes of focused input will power months of strategic clarity.
                </p>

                {/* CTA */}
                <button
                    ref={ctaRef}
                    onClick={handleStart}
                    disabled={isExiting}
                    className="group inline-flex items-center gap-4 bg-white text-[#0E1112] px-12 py-5 rounded-2xl font-medium text-[16px] transition-all duration-300 hover:scale-[1.02] hover:shadow-[0_0_60px_rgba(255,255,255,0.15)] disabled:opacity-50"
                >
                    <span>Begin the Process</span>
                    <ArrowRight className="w-5 h-5 transition-transform group-hover:translate-x-1" />
                </button>

                {/* Keyboard hint */}
                <p className="mt-8 text-[12px] text-white/20 font-mono">
                    Press Enter to start
                </p>
            </div>

            {/* Floating animation keyframes */}
            <style jsx>{`
                @keyframes subtleFloat {
                    0%, 100% { transform: translateY(0) translateX(0); }
                    25% { transform: translateY(-20px) translateX(10px); }
                    50% { transform: translateY(-10px) translateX(-5px); }
                    75% { transform: translateY(-25px) translateX(5px); }
                }
            `}</style>
        </div>
    );
}
>>>>>>> origin/codex/integrate-radar-feature-with-backend-dv6q26:raptorflow-app/src/components/onboarding/WelcomeScreen.tsx
