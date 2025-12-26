'use client';

import React, { useRef, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import gsap from 'gsap';

export interface PhaseStep {
    id: string;
    label: string;
}

interface PhaseScreenProps {
    /** Phase number (3, 4, 5, or 6) */
    phaseNumber: number;
    /** Phase title displayed in sidebar */
    phaseTitle: string;
    /** Current step ID */
    currentStepId: string;
    /** All steps for this phase */
    steps: PhaseStep[];
    /** Main content title (serif, large) */
    title: string;
    /** Optional subtitle below title */
    subtitle?: string;
    /** Main content */
    children: React.ReactNode;
    /** Called when back is pressed */
    onBack?: () => void;
    /** Called when a step is clicked in navigator */
    onStepClick?: (stepId: string) => void;
    /** Show continue button */
    showContinue?: boolean;
    /** Continue button text */
    continueText?: string;
    /** Called when continue is pressed */
    onContinue?: () => void;
    /** Disable continue button */
    continueDisabled?: boolean;
}

export function PhaseScreen({
    phaseNumber,
    phaseTitle,
    currentStepId,
    steps,
    title,
    subtitle,
    children,
    onBack,
    onStepClick,
    showContinue = true,
    continueText = 'Continue',
    onContinue,
    continueDisabled = false,
}: PhaseScreenProps) {
    const router = useRouter();
    const containerRef = useRef<HTMLDivElement>(null);
    const sidebarRef = useRef<HTMLDivElement>(null);
    const canvasRef = useRef<HTMLDivElement>(null);
    const titleRef = useRef<HTMLHeadingElement>(null);
    const subtitleRef = useRef<HTMLParagraphElement>(null);
    const contentRef = useRef<HTMLDivElement>(null);
    const [hasAnimated, setHasAnimated] = useState(false);

    const currentIndex = steps.findIndex(s => s.id === currentStepId);
    const progress = ((currentIndex + 1) / steps.length) * 100;

    // Initial page animation
    useEffect(() => {
        if (!containerRef.current || hasAnimated) return;

        const tl = gsap.timeline({
            onComplete: () => setHasAnimated(true),
            defaults: { ease: 'power3.out' }
        });

        // Set initial states
        gsap.set(sidebarRef.current, { x: -80, opacity: 0 });
        gsap.set(canvasRef.current, { opacity: 0 });
        gsap.set(titleRef.current, { y: 40, opacity: 0 });
        gsap.set(subtitleRef.current, { y: 20, opacity: 0 });
        gsap.set(contentRef.current, { y: 30, opacity: 0 });

        // Animate in
        tl.to(sidebarRef.current, { x: 0, opacity: 1, duration: 0.7 })
            .to(canvasRef.current, { opacity: 1, duration: 0.5 }, '-=0.4')
            .to(titleRef.current, { y: 0, opacity: 1, duration: 0.6 }, '-=0.3')
            .to(subtitleRef.current, { y: 0, opacity: 1, duration: 0.4 }, '-=0.3')
            .to(contentRef.current, { y: 0, opacity: 1, duration: 0.5 }, '-=0.2');

        return () => { tl.kill(); };
    }, [hasAnimated]);

    // Content transition on step change
    useEffect(() => {
        if (!hasAnimated || !contentRef.current) return;

        const tl = gsap.timeline({ defaults: { ease: 'power2.out' } });

        tl.fromTo(
            [titleRef.current, subtitleRef.current, contentRef.current],
            { opacity: 0, y: 20 },
            { opacity: 1, y: 0, duration: 0.4, stagger: 0.08 }
        );

        return () => { tl.kill(); };
    }, [currentStepId, hasAnimated]);

    const handleBack = () => {
        if (onBack) {
            onBack();
        } else {
            router.back();
        }
    };

    return (
        <div ref={containerRef} className="flex h-screen overflow-hidden bg-[#F3F4EE]">
            {/* Sidebar */}
            <aside
                ref={sidebarRef}
                className="w-[320px] flex-shrink-0 bg-[#0E1112] text-white flex flex-col"
            >
                {/* Logo */}
                <div className="flex items-center gap-3 px-8 py-8 border-b border-white/10">
                    <div className="w-7 h-7 bg-white rounded-sm flex-shrink-0" />
                    <span className="text-[11px] font-mono uppercase tracking-[0.25em] text-white/50">
                        RaptorFlow
                    </span>
                </div>

                {/* Phase Info */}
                <div className="px-8 py-10">
                    <span className="text-[11px] font-mono uppercase tracking-[0.25em] text-white/30 block mb-2">
                        Phase {phaseNumber}
                    </span>
                    <h2 className="font-serif text-[28px] text-white tracking-tight leading-tight">
                        {phaseTitle}
                    </h2>
                </div>

                {/* Progress Bar */}
                <div className="px-8 mb-8">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-[11px] font-mono uppercase tracking-[0.15em] text-white/30">
                            Progress
                        </span>
                        <span className="text-[11px] font-mono text-white/50">
                            {currentIndex + 1} / {steps.length}
                        </span>
                    </div>
                    <div className="h-[3px] bg-white/10 rounded-full overflow-hidden">
                        <div
                            className="h-full bg-white/70 transition-all duration-700 ease-out"
                            style={{ width: `${progress}%` }}
                        />
                    </div>
                </div>

                {/* Step Navigator */}
                <div className="flex-1 px-8 overflow-y-auto">
                    <div className="space-y-1">
                        {steps.map((step, index) => {
                            const isActive = step.id === currentStepId;
                            const isCompleted = index < currentIndex;

                            return (
                                <button
                                    key={step.id}
                                    onClick={() => onStepClick?.(step.id)}
                                    disabled={index > currentIndex}
                                    className={`w-full flex items-center gap-3 py-3 px-4 rounded-xl text-left transition-all duration-200 ${isActive
                                            ? 'bg-white/10'
                                            : 'hover:bg-white/5 disabled:opacity-30 disabled:cursor-not-allowed'
                                        }`}
                                >
                                    <div className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-mono ${isCompleted
                                            ? 'bg-white/20 text-white'
                                            : isActive
                                                ? 'bg-white text-[#0E1112]'
                                                : 'border border-white/20 text-white/40'
                                        }`}>
                                        {isCompleted ? <Check className="w-3 h-3" /> : index + 1}
                                    </div>
                                    <span className={`text-sm ${isActive ? 'text-white font-medium' : 'text-white/50'
                                        }`}>
                                        {step.label}
                                    </span>
                                </button>
                            );
                        })}
                    </div>
                </div>

                {/* Back Button */}
                <div className="px-8 py-6 border-t border-white/10">
                    <button
                        onClick={handleBack}
                        className="flex items-center gap-2 text-white/40 hover:text-white transition-colors text-sm"
                    >
                        <ArrowLeft className="w-4 h-4" />
                        <span>Back</span>
                    </button>
                </div>
            </aside>

            {/* Main Canvas */}
            <main
                ref={canvasRef}
                className="flex-1 overflow-y-auto"
            >
                <div className="min-h-full flex flex-col max-w-[800px] mx-auto px-16 py-16">
                    {/* Title Section */}
                    <div className="mb-12">
                        <h1
                            ref={titleRef}
                            className="font-serif text-[48px] text-[#2D3538] tracking-[-0.02em] leading-[1.1] mb-4"
                        >
                            {title}
                        </h1>
                        {subtitle && (
                            <p
                                ref={subtitleRef}
                                className="text-[18px] text-[#5B5F61] leading-relaxed max-w-[600px]"
                            >
                                {subtitle}
                            </p>
                        )}
                    </div>

                    {/* Content Area */}
                    <div ref={contentRef} className="flex-1">
                        {children}
                    </div>

                    {/* Continue Button */}
                    {showContinue && (
                        <div className="pt-12 mt-auto flex justify-end border-t border-[#E5E6E3]">
                            <Button
                                onClick={onContinue}
                                disabled={continueDisabled}
                                className="bg-[#2D3538] hover:bg-[#1A1D1E] disabled:bg-[#9D9F9F] text-white px-10 py-7 rounded-2xl text-[16px] font-medium transition-all duration-200 hover:scale-[1.02] active:scale-[0.98]"
                            >
                                {continueText}
                            </Button>
                        </div>
                    )}
                </div>
            </main>
        </div>
    );
}
