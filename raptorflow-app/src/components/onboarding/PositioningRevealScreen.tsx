'use client';

import React, { useEffect, useRef } from 'react';
import { DerivedPositioning } from '@/lib/foundation';
import { ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import styles from './QuestionFlow.module.css';
import gsap from 'gsap';

interface PositioningRevealScreenProps {
    positioning: DerivedPositioning;
    onContinue: () => void;
}

export function PositioningRevealScreen({ positioning, onContinue }: PositioningRevealScreenProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const leftPanelRef = useRef<HTMLDivElement>(null);
    const oneThingRef = useRef<HTMLParagraphElement>(null);
    const statementRef = useRef<HTMLDivElement>(null);
    const matrixRef = useRef<HTMLDivElement>(null);
    const actionRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!containerRef.current) return;

        const tl = gsap.timeline();

        // Set initial states
        gsap.set(leftPanelRef.current, { x: -80, opacity: 0 });
        gsap.set(oneThingRef.current, { y: 20, opacity: 0 });
        gsap.set(statementRef.current, { y: 40, opacity: 0, scale: 0.98 });
        gsap.set(matrixRef.current, { y: 40, opacity: 0 });
        gsap.set(actionRef.current, { y: 20, opacity: 0 });

        // Animate sequence
        tl.to(leftPanelRef.current, {
            x: 0,
            opacity: 1,
            duration: 0.7,
            ease: 'power3.out'
        })
            .to(oneThingRef.current, {
                y: 0,
                opacity: 1,
                duration: 0.6,
                ease: 'power2.out'
            }, '-=0.3')
            .to(statementRef.current, {
                y: 0,
                opacity: 1,
                scale: 1,
                duration: 0.8,
                ease: 'power3.out'
            }, '-=0.2')
            .to(matrixRef.current, {
                y: 0,
                opacity: 1,
                duration: 0.7,
                ease: 'power2.out'
            }, '-=0.4');

        // Animate matrix positions with delay
        if (matrixRef.current) {
            const positions = matrixRef.current.querySelectorAll('.matrix-position');
            gsap.set(positions, { scale: 0, opacity: 0 });
            tl.to(positions, {
                scale: 1,
                opacity: 1,
                duration: 0.4,
                stagger: 0.15,
                ease: 'back.out(1.7)'
            }, '-=0.3');
        }

        tl.to(actionRef.current, {
            y: 0,
            opacity: 1,
            duration: 0.4,
            ease: 'power2.out'
        }, '-=0.2');

        return () => { tl.kill(); };
    }, []);

    return (
        <div ref={containerRef} className={styles.flowContainer}>
            {/* Left Panel */}
            <div ref={leftPanelRef} className={styles.leftPanel}>
                <div className="w-full h-full flex flex-col">
                    <div className={styles.logoArea}>
                        <div className="w-6 h-6 bg-white rounded flex-shrink-0" />
                        <span className={styles.logoText}>RAPTORFLOW</span>
                    </div>

                    <div className={styles.sectionInfo}>
                        <span className="text-xs font-mono uppercase tracking-[0.2em] text-white/40 mb-4 block">
                            Your Market Intelligence
                        </span>
                        <h2 className="font-serif text-4xl text-white tracking-tight mb-3">
                            Positioning
                        </h2>
                        <p className="text-sm text-white/50 leading-relaxed">
                            Where you stand. Where you win.
                        </p>
                    </div>

                    {/* The One Thing */}
                    <div className="mt-12 py-6 border-t border-white/10">
                        <span className="text-xs font-mono uppercase tracking-[0.15em] text-white/40 mb-4 block">
                            Your One Thing
                        </span>
                        <p ref={oneThingRef} className="font-serif text-2xl text-white leading-snug italic">
                            "{positioning.oneThing}"
                        </p>
                    </div>

                    <div className="mt-auto pt-8 border-t border-white/10">
                        <div className="flex items-center justify-between">
                            <span className="text-xs font-mono uppercase tracking-wider text-white/30">
                                Defensibility
                            </span>
                            <span className="text-sm text-white/60 capitalize">{positioning.defensibility}</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Right Panel */}
            <div className={styles.rightPanel}>
                <div className="flex-1 flex flex-col max-w-[680px] mx-auto w-full px-16 py-16">
                    <div>
                        {/* Positioning Statement */}
                        <div ref={statementRef} className="mb-16">
                            <h3 className="text-xs font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-6">
                                Positioning Statement
                            </h3>
                            <div className="p-8 border border-[#E5E6E3] rounded-2xl bg-[#FAFAF8]">
                                <p className="font-serif text-2xl text-[#2D3538] leading-relaxed">
                                    For <span className="underline decoration-[#C0C1BE] decoration-2 underline-offset-4">{positioning.statement.forWhom}</span>,{' '}
                                    <strong>{positioning.statement.company}</strong> is the{' '}
                                    <span className="underline decoration-[#C0C1BE] decoration-2 underline-offset-4">{positioning.statement.category}</span> that{' '}
                                    {positioning.statement.differentiator}.
                                </p>
                                <p className="font-serif text-lg text-[#5B5F61] mt-4">
                                    Unlike {positioning.statement.unlikeCompetitor}, we {positioning.statement.because}.
                                </p>
                            </div>
                        </div>

                        {/* Competitive Matrix */}
                        <div ref={matrixRef} className="mb-16">
                            <h3 className="text-xs font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-6">
                                Competitive Landscape
                            </h3>
                            <div className="relative h-72 border border-[#E5E6E3] rounded-2xl bg-[#FAFAF8] p-6">
                                {/* Axes */}
                                <div className="absolute bottom-4 left-1/2 -translate-x-1/2 text-xs font-mono text-[#9D9F9F] uppercase tracking-wider">
                                    {positioning.matrix.xAxis.label}
                                </div>
                                <div className="absolute left-4 top-1/2 -translate-y-1/2 -rotate-90 text-xs font-mono text-[#9D9F9F] uppercase tracking-wider whitespace-nowrap">
                                    {positioning.matrix.yAxis.label}
                                </div>

                                {/* Grid lines */}
                                <div className="absolute inset-12 border border-dashed border-[#E5E6E3]" />
                                <div className="absolute left-1/2 top-12 bottom-12 w-px border-l border-dashed border-[#E5E6E3]" />
                                <div className="absolute top-1/2 left-12 right-12 h-px border-t border-dashed border-[#E5E6E3]" />

                                {/* Positions */}
                                {positioning.matrix.positions.map((pos, i) => (
                                    <div
                                        key={i}
                                        className={`matrix-position absolute flex flex-col items-center ${pos.isYou ? 'z-10' : 'z-0'
                                            }`}
                                        style={{
                                            left: `${pos.x * 70 + 15}%`,
                                            bottom: `${pos.y * 70 + 15}%`,
                                        }}
                                    >
                                        <div className={`rounded-full transition-all ${pos.isYou
                                                ? 'w-5 h-5 bg-[#2D3538] ring-4 ring-[#2D3538]/10'
                                                : 'w-3 h-3 bg-[#C0C1BE]'
                                            }`} />
                                        <span className={`text-xs mt-2 whitespace-nowrap ${pos.isYou ? 'font-semibold text-[#2D3538]' : 'text-[#9D9F9F]'
                                            }`}>
                                            {pos.name}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Action */}
                        <div ref={actionRef} className="flex items-center justify-end pt-8 border-t border-[#E5E6E3]">
                            <Button
                                onClick={onContinue}
                                className="bg-[#2D3538] hover:bg-[#1A1D1E] text-white px-8 py-6 rounded-xl font-medium transition-all hover:scale-[1.02]"
                            >
                                Continue <ArrowRight className="ml-2 h-4 w-4" />
                            </Button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
