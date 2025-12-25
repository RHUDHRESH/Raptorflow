'use client';

import React, { useEffect, useRef, useState } from 'react';
import { DerivedICP } from '@/lib/foundation';
import { ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import styles from './QuestionFlow.module.css';
import gsap from 'gsap';

interface ICPRevealScreenProps {
    icps: DerivedICP[];
    onContinue: () => void;
}

export function ICPRevealScreen({ icps, onContinue }: ICPRevealScreenProps) {
    const [selectedIndex, setSelectedIndex] = useState(0);
    const [hasAnimated, setHasAnimated] = useState(false);
    const selectedIcp = icps[selectedIndex];

    // Refs for GSAP
    const containerRef = useRef<HTMLDivElement>(null);
    const leftPanelRef = useRef<HTMLDivElement>(null);
    const rightPanelRef = useRef<HTMLDivElement>(null);
    const titleRef = useRef<HTMLHeadingElement>(null);
    const descRef = useRef<HTMLParagraphElement>(null);
    const gridRef = useRef<HTMLDivElement>(null);
    const icpListRef = useRef<HTMLDivElement>(null);
    const actionRef = useRef<HTMLDivElement>(null);

    // Initial reveal animation
    useEffect(() => {
        if (!containerRef.current || hasAnimated) return;

        const tl = gsap.timeline({
            onComplete: () => setHasAnimated(true)
        });

        // Set initial states
        gsap.set(leftPanelRef.current, { x: -100, opacity: 0 });
        gsap.set(rightPanelRef.current, { opacity: 0 });
        gsap.set(titleRef.current, { y: 40, opacity: 0 });
        gsap.set(descRef.current, { y: 20, opacity: 0 });
        gsap.set(actionRef.current, { y: 20, opacity: 0 });

        // Animated entrance sequence
        tl.to(leftPanelRef.current, {
            x: 0,
            opacity: 1,
            duration: 0.8,
            ease: 'power3.out'
        })
            .to(rightPanelRef.current, {
                opacity: 1,
                duration: 0.6,
                ease: 'power2.out'
            }, '-=0.4')
            .to(titleRef.current, {
                y: 0,
                opacity: 1,
                duration: 0.7,
                ease: 'power3.out'
            }, '-=0.3')
            .to(descRef.current, {
                y: 0,
                opacity: 1,
                duration: 0.5,
                ease: 'power2.out'
            }, '-=0.4');

        // Stagger the ICP list items
        if (icpListRef.current) {
            const items = icpListRef.current.querySelectorAll('.icp-item');
            gsap.set(items, { x: -30, opacity: 0 });
            tl.to(items, {
                x: 0,
                opacity: 1,
                duration: 0.4,
                stagger: 0.1,
                ease: 'power2.out'
            }, '-=0.4');
        }

        // Stagger the grid items
        if (gridRef.current) {
            const gridItems = gridRef.current.querySelectorAll('.grid-item');
            gsap.set(gridItems, { y: 30, opacity: 0 });
            tl.to(gridItems, {
                y: 0,
                opacity: 1,
                duration: 0.5,
                stagger: 0.08,
                ease: 'power2.out'
            }, '-=0.3');
        }

        // Action area
        tl.to(actionRef.current, {
            y: 0,
            opacity: 1,
            duration: 0.4,
            ease: 'power2.out'
        }, '-=0.2');

        return () => {
            tl.kill();
        };
    }, [hasAnimated]);

    // Animation when switching ICPs
    useEffect(() => {
        if (!hasAnimated || !titleRef.current || !gridRef.current) return;

        const tl = gsap.timeline();

        // Quick fade out
        tl.to([titleRef.current, descRef.current], {
            opacity: 0,
            y: -10,
            duration: 0.15,
            ease: 'power2.in'
        })
            .to(gridRef.current?.querySelectorAll('.grid-item') || [], {
                opacity: 0,
                y: -10,
                duration: 0.1,
                stagger: 0.02,
                ease: 'power2.in'
            }, '-=0.1');

        // Then fade in with new content
        tl.to([titleRef.current, descRef.current], {
            opacity: 1,
            y: 0,
            duration: 0.3,
            ease: 'power2.out',
            delay: 0.05
        })
            .to(gridRef.current?.querySelectorAll('.grid-item') || [], {
                opacity: 1,
                y: 0,
                duration: 0.3,
                stagger: 0.05,
                ease: 'power2.out'
            }, '-=0.2');

    }, [selectedIndex, hasAnimated]);

    const handleSelectIcp = (index: number) => {
        if (index !== selectedIndex) {
            setSelectedIndex(index);
        }
    };

    return (
        <div ref={containerRef} className={styles.flowContainer}>
            {/* Left Panel - Dark, Minimal */}
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
                            Meet Your Cohorts
                        </h2>
                        <p className="text-sm text-white/50 leading-relaxed">
                            The people who need you most.
                        </p>
                    </div>

                    {/* ICP List - Minimal */}
                    <div ref={icpListRef} className="mt-12 space-y-2 flex-1">
                        {icps.map((icp, index) => (
                            <button
                                key={icp.id}
                                onClick={() => handleSelectIcp(index)}
                                className={`icp-item w-full text-left py-4 px-5 rounded-xl transition-all duration-300 border ${selectedIndex === index
                                        ? 'bg-white/10 border-white/20'
                                        : 'bg-transparent border-transparent hover:bg-white/5'
                                    }`}
                            >
                                <span className="text-xs font-mono uppercase tracking-wider text-white/40">
                                    {icp.priority === 'primary' ? 'Primary' : 'Secondary'}
                                </span>
                                <p className="font-medium text-white mt-1">{icp.name}</p>
                            </button>
                        ))}
                    </div>

                    <div className="mt-auto pt-8 border-t border-white/10">
                        <p className="text-xs font-mono uppercase tracking-wider text-white/30">
                            Click to explore each cohort
                        </p>
                    </div>
                </div>
            </div>

            {/* Right Panel - Light, Editorial */}
            <div ref={rightPanelRef} className={styles.rightPanel}>
                <div className="flex-1 flex flex-col max-w-[680px] mx-auto w-full px-16 py-16">
                    {selectedIcp && (
                        <div>
                            {/* Header */}
                            <div className="mb-16">
                                <h1
                                    ref={titleRef}
                                    className="font-serif text-5xl text-[#2D3538] tracking-tight leading-tight mb-4"
                                >
                                    {selectedIcp.name}
                                </h1>
                                <p
                                    ref={descRef}
                                    className="text-lg text-[#5B5F61] leading-relaxed max-w-lg"
                                >
                                    {selectedIcp.description}
                                </p>
                            </div>

                            {/* Profile Grid - Monochrome */}
                            <div ref={gridRef} className="grid grid-cols-2 gap-8 mb-16">
                                {/* Firmographics */}
                                <div className="grid-item">
                                    <h3 className="text-xs font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-4">
                                        Firmographics
                                    </h3>
                                    <div className="space-y-4">
                                        <div>
                                            <span className="text-sm text-[#9D9F9F]">Company Size</span>
                                            <p className="text-[#2D3538] font-medium">{selectedIcp.firmographics.companySize}</p>
                                        </div>
                                        <div>
                                            <span className="text-sm text-[#9D9F9F]">Industry</span>
                                            <p className="text-[#2D3538] font-medium">{selectedIcp.firmographics.industry.join(', ')}</p>
                                        </div>
                                        <div>
                                            <span className="text-sm text-[#9D9F9F]">Budget Range</span>
                                            <p className="text-[#2D3538] font-medium">{selectedIcp.firmographics.budget}</p>
                                        </div>
                                    </div>
                                </div>

                                {/* Pain */}
                                <div className="grid-item">
                                    <h3 className="text-xs font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-4">
                                        Core Pain
                                    </h3>
                                    <div className="space-y-4">
                                        <div>
                                            <span className="text-sm text-[#9D9F9F]">Primary</span>
                                            <p className="text-[#2D3538] font-medium">{selectedIcp.painMap.primary}</p>
                                        </div>
                                        <div>
                                            <span className="text-sm text-[#9D9F9F]">Urgency</span>
                                            <p className="text-[#2D3538] font-medium capitalize">{selectedIcp.painMap.urgency}</p>
                                        </div>
                                        <div>
                                            <span className="text-sm text-[#9D9F9F]">Triggers</span>
                                            <p className="text-[#2D3538] font-medium">{selectedIcp.painMap.triggers.slice(0, 2).join(', ')}</p>
                                        </div>
                                    </div>
                                </div>

                                {/* Social */}
                                <div className="grid-item">
                                    <h3 className="text-xs font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-4">
                                        Where They Are
                                    </h3>
                                    <div className="space-y-3">
                                        {selectedIcp.social.platforms.slice(0, 2).map((platform, i) => (
                                            <div key={i}>
                                                <p className="text-[#2D3538] font-medium">{platform.name}</p>
                                                <p className="text-sm text-[#9D9F9F]">{platform.timing}</p>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {/* Buying */}
                                <div className="grid-item">
                                    <h3 className="text-xs font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-4">
                                        Buying Cycle
                                    </h3>
                                    <div className="space-y-4">
                                        <div>
                                            <span className="text-sm text-[#9D9F9F]">Timeline</span>
                                            <p className="text-[#2D3538] font-medium">{selectedIcp.buying.timeline}</p>
                                        </div>
                                        <div>
                                            <span className="text-sm text-[#9D9F9F]">Proof Needed</span>
                                            <p className="text-[#2D3538] font-medium">{selectedIcp.buying.proofNeeded.slice(0, 2).join(', ')}</p>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Action - Minimal */}
                            <div ref={actionRef} className="flex items-center justify-between pt-8 border-t border-[#E5E6E3]">
                                <p className="text-xs font-mono text-[#9D9F9F]">
                                    {selectedIndex + 1} of {icps.length} cohorts
                                </p>
                                <Button
                                    onClick={onContinue}
                                    className="bg-[#2D3538] hover:bg-[#1A1D1E] text-white px-8 py-6 rounded-xl font-medium transition-all hover:scale-[1.02]"
                                >
                                    Continue <ArrowRight className="ml-2 h-4 w-4" />
                                </Button>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
