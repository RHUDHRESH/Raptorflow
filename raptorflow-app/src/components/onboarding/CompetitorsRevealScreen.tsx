'use client';

import React, { useEffect, useRef } from 'react';
import { DerivedCompetitive } from '@/lib/foundation';
import { ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import styles from './QuestionFlow.module.css';
import gsap from 'gsap';

interface CompetitorsRevealScreenProps {
    competitive: DerivedCompetitive;
    onContinue: () => void;
}

export function CompetitorsRevealScreen({ competitive, onContinue }: CompetitorsRevealScreenProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const leftPanelRef = useRef<HTMLDivElement>(null);
    const statusQuoRef = useRef<HTMLDivElement>(null);
    const wedgeRef = useRef<HTMLDivElement>(null);
    const indirectRef = useRef<HTMLDivElement>(null);
    const directRef = useRef<HTMLDivElement>(null);
    const actionRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!containerRef.current) return;

        const tl = gsap.timeline();

        // Set initial states
        gsap.set(leftPanelRef.current, { x: -80, opacity: 0 });
        gsap.set(statusQuoRef.current, { y: 20, opacity: 0 });
        gsap.set(wedgeRef.current, { y: 40, opacity: 0, scale: 0.98 });
        gsap.set(indirectRef.current, { y: 30, opacity: 0 });
        gsap.set(directRef.current, { y: 30, opacity: 0 });
        gsap.set(actionRef.current, { y: 20, opacity: 0 });

        // Animate sequence
        tl.to(leftPanelRef.current, {
            x: 0,
            opacity: 1,
            duration: 0.7,
            ease: 'power3.out'
        })
            .to(statusQuoRef.current, {
                y: 0,
                opacity: 1,
                duration: 0.5,
                ease: 'power2.out'
            }, '-=0.3')
            .to(wedgeRef.current, {
                y: 0,
                opacity: 1,
                scale: 1,
                duration: 0.7,
                ease: 'power3.out'
            }, '-=0.2')
            .to(indirectRef.current, {
                y: 0,
                opacity: 1,
                duration: 0.5,
                ease: 'power2.out'
            }, '-=0.3');

        // Stagger indirect competitor cards
        if (indirectRef.current) {
            const cards = indirectRef.current.querySelectorAll('.competitor-card');
            gsap.set(cards, { x: 20, opacity: 0 });
            tl.to(cards, {
                x: 0,
                opacity: 1,
                duration: 0.4,
                stagger: 0.1,
                ease: 'power2.out'
            }, '-=0.3');
        }

        tl.to(directRef.current, {
            y: 0,
            opacity: 1,
            duration: 0.5,
            ease: 'power2.out'
        }, '-=0.2');

        // Stagger direct competitor cards
        if (directRef.current) {
            const cards = directRef.current.querySelectorAll('.competitor-card');
            gsap.set(cards, { x: 20, opacity: 0 });
            tl.to(cards, {
                x: 0,
                opacity: 1,
                duration: 0.4,
                stagger: 0.1,
                ease: 'power2.out'
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
                            Competitors
                        </h2>
                        <p className="text-sm text-white/50 leading-relaxed">
                            Know thy battlefield.
                        </p>
                    </div>

                    {/* Status Quo */}
                    <div ref={statusQuoRef} className="mt-12 py-6 border-t border-white/10">
                        <span className="text-xs font-mono uppercase tracking-[0.15em] text-white/40 mb-4 block">
                            The Real Enemy
                        </span>
                        <p className="font-semibold text-white text-lg">{competitive.statusQuo.name}</p>
                        <p className="text-sm text-white/50 mt-1">{competitive.statusQuo.toleratedPain}</p>
                    </div>

                    <div className="mt-auto pt-8 border-t border-white/10">
                        <span className="text-xs font-mono uppercase tracking-wider text-white/30">
                            {competitive.direct.length + competitive.indirect.length} alternatives mapped
                        </span>
                    </div>
                </div>
            </div>

            {/* Right Panel */}
            <div className={styles.rightPanel}>
                <div className="flex-1 flex flex-col max-w-[680px] mx-auto w-full px-16 py-16 overflow-y-auto">
                    <div>
                        {/* Your Wedge */}
                        <div ref={wedgeRef} className="mb-12 p-8 border-2 border-[#2D3538] rounded-2xl">
                            <span className="text-xs font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-3 block">
                                Your Wedge
                            </span>
                            <p className="font-serif text-2xl text-[#2D3538]">
                                {competitive.statusQuo.yourWedge}
                            </p>
                        </div>

                        {/* Indirect */}
                        <div ref={indirectRef} className="mb-10">
                            <h3 className="text-xs font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-6">
                                Indirect Competitors
                            </h3>
                            <div className="space-y-4">
                                {competitive.indirect.map((comp, i) => (
                                    <div key={i} className="competitor-card p-5 border border-[#E5E6E3] rounded-xl">
                                        <div className="flex items-start justify-between">
                                            <div>
                                                <p className="font-medium text-[#2D3538]">{comp.name}</p>
                                                <p className="text-sm text-[#9D9F9F] mt-1">{comp.mechanism}</p>
                                            </div>
                                            <span className="text-xs font-mono text-[#9D9F9F]">{comp.priceRange}</span>
                                        </div>
                                        <div className="mt-4 pt-4 border-t border-[#E5E6E3]">
                                            <span className="text-xs text-[#9D9F9F]">Your Edge: </span>
                                            <span className="text-sm text-[#2D3538]">{comp.yourEdge}</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Direct */}
                        {competitive.direct.length > 0 && (
                            <div ref={directRef} className="mb-10">
                                <h3 className="text-xs font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-6">
                                    Direct Competitors
                                </h3>
                                <div className="space-y-4">
                                    {competitive.direct.map((comp, i) => (
                                        <div key={i} className="competitor-card p-5 border border-[#E5E6E3] rounded-xl">
                                            <div className="flex items-start justify-between">
                                                <div>
                                                    <p className="font-medium text-[#2D3538]">{comp.name}</p>
                                                    <p className="text-sm text-[#9D9F9F] mt-1">{comp.positioning}</p>
                                                </div>
                                                <span className="text-xs font-mono text-[#9D9F9F] capitalize">{comp.featureOverlap} overlap</span>
                                            </div>
                                            <div className="mt-4 pt-4 border-t border-[#E5E6E3]">
                                                <span className="text-xs text-[#9D9F9F]">Your Edge: </span>
                                                <span className="text-sm text-[#2D3538]">{comp.yourEdge}</span>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

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
