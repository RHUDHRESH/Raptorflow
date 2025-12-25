'use client';

import React, { useEffect, useRef, useState } from 'react';
import { DerivedMarket } from '@/lib/foundation';
import { ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import styles from './QuestionFlow.module.css';
import gsap from 'gsap';

interface MarketRevealScreenProps {
    market: DerivedMarket;
    onComplete: () => void;
}

// Animated counter hook
function useCounter(target: number, duration: number = 2, trigger: boolean = true) {
    const [value, setValue] = useState(0);

    useEffect(() => {
        if (!trigger) return;

        const obj = { val: 0 };
        gsap.to(obj, {
            val: target,
            duration,
            ease: 'power2.out',
            onUpdate: () => setValue(Math.floor(obj.val))
        });
    }, [target, duration, trigger]);

    return value;
}

function formatCurrency(value: number): string {
    if (value >= 1_000_000_000) return `$${(value / 1_000_000_000).toFixed(1)}B`;
    if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(0)}M`;
    if (value >= 1_000) return `$${(value / 1_000).toFixed(0)}K`;
    return `$${value}`;
}

export function MarketRevealScreen({ market, onComplete }: MarketRevealScreenProps) {
    const [animationStarted, setAnimationStarted] = useState(false);
    const containerRef = useRef<HTMLDivElement>(null);
    const leftPanelRef = useRef<HTMLDivElement>(null);
    const somHighlightRef = useRef<HTMLDivElement>(null);
    const metricsRef = useRef<HTMLDivElement>(null);
    const pathRef = useRef<HTMLDivElement>(null);
    const actionRef = useRef<HTMLDivElement>(null);

    // Animated counters for the big numbers
    const tamValue = useCounter(market.tam.value, 2.5, animationStarted);
    const samValue = useCounter(market.sam.value, 2, animationStarted);
    const somValue = useCounter(market.som.value, 1.5, animationStarted);
    const customersValue = useCounter(market.pathToSom.customersNeeded, 2, animationStarted);
    const leadsValue = useCounter(market.pathToSom.leadsPerMonth, 2, animationStarted);

    useEffect(() => {
        if (!containerRef.current) return;

        const tl = gsap.timeline({
            onStart: () => setAnimationStarted(true)
        });

        // Set initial states
        gsap.set(leftPanelRef.current, { x: -80, opacity: 0 });
        gsap.set(somHighlightRef.current, { y: 30, opacity: 0 });
        gsap.set(metricsRef.current, { y: 50, opacity: 0 });
        gsap.set(pathRef.current, { y: 40, opacity: 0 });
        gsap.set(actionRef.current, { y: 20, opacity: 0 });

        // Animate sequence
        tl.to(leftPanelRef.current, {
            x: 0,
            opacity: 1,
            duration: 0.7,
            ease: 'power3.out'
        })
            .to(somHighlightRef.current, {
                y: 0,
                opacity: 1,
                duration: 0.8,
                ease: 'power3.out'
            }, '-=0.3')
            .to(metricsRef.current, {
                y: 0,
                opacity: 1,
                duration: 0.7,
                ease: 'power2.out'
            }, '-=0.4');

        // Stagger the metric cards
        if (metricsRef.current) {
            const cards = metricsRef.current.querySelectorAll('.metric-card');
            gsap.set(cards, { y: 30, opacity: 0, scale: 0.95 });
            tl.to(cards, {
                y: 0,
                opacity: 1,
                scale: 1,
                duration: 0.5,
                stagger: 0.12,
                ease: 'power2.out'
            }, '-=0.5');
        }

        tl.to(pathRef.current, {
            y: 0,
            opacity: 1,
            duration: 0.6,
            ease: 'power2.out'
        }, '-=0.2')
            .to(actionRef.current, {
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
                            Market Size
                        </h2>
                        <p className="text-sm text-white/50 leading-relaxed">
                            Your addressable opportunity.
                        </p>
                    </div>

                    {/* SOM Highlight */}
                    <div ref={somHighlightRef} className="mt-12 py-6 border-t border-white/10">
                        <span className="text-xs font-mono uppercase tracking-[0.15em] text-white/40 mb-4 block">
                            Your 3-Year Target
                        </span>
                        <p className="font-serif text-5xl text-white">
                            {formatCurrency(somValue)}
                        </p>
                        <p className="text-sm text-white/50 mt-2">{market.som.timeline}</p>
                    </div>

                    <div className="mt-auto pt-8 border-t border-white/10">
                        <span className="text-xs font-mono uppercase tracking-wider text-white/30">
                            Foundation Complete
                        </span>
                    </div>
                </div>
            </div>

            {/* Right Panel */}
            <div className={styles.rightPanel}>
                <div className="flex-1 flex flex-col max-w-[680px] mx-auto w-full px-16 py-16">
                    <div>
                        {/* TAM SAM SOM */}
                        <div ref={metricsRef} className="grid grid-cols-3 gap-6 mb-16">
                            <div className="metric-card text-center py-8 border border-[#E5E6E3] rounded-2xl">
                                <span className="text-xs font-mono uppercase tracking-[0.15em] text-[#9D9F9F]">TAM</span>
                                <p className="font-serif text-3xl text-[#2D3538] mt-3">{formatCurrency(tamValue)}</p>
                                <span className="text-xs font-mono text-[#9D9F9F] mt-2 inline-block capitalize">{market.tam.confidence}</span>
                            </div>
                            <div className="metric-card text-center py-8 border border-[#E5E6E3] rounded-2xl">
                                <span className="text-xs font-mono uppercase tracking-[0.15em] text-[#9D9F9F]">SAM</span>
                                <p className="font-serif text-3xl text-[#2D3538] mt-3">{formatCurrency(samValue)}</p>
                                <span className="text-xs font-mono text-[#9D9F9F] mt-2 inline-block capitalize">{market.sam.confidence}</span>
                            </div>
                            <div className="metric-card text-center py-8 border-2 border-[#2D3538] rounded-2xl bg-[#FAFAF8]">
                                <span className="text-xs font-mono uppercase tracking-[0.15em] text-[#2D3538]">SOM</span>
                                <p className="font-serif text-3xl text-[#2D3538] mt-3">{formatCurrency(somValue)}</p>
                                <span className="text-xs font-mono text-[#5B5F61] mt-2 inline-block">{market.som.timeline}</span>
                            </div>
                        </div>

                        {/* Path to SOM */}
                        <div ref={pathRef} className="mb-12 p-8 border border-[#E5E6E3] rounded-2xl">
                            <h3 className="text-xs font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-6">
                                Path to SOM
                            </h3>
                            <div className="grid grid-cols-2 gap-8">
                                <div>
                                    <span className="text-sm text-[#9D9F9F]">Customers Needed</span>
                                    <p className="font-serif text-2xl text-[#2D3538]">{customersValue.toLocaleString()}</p>
                                </div>
                                <div>
                                    <span className="text-sm text-[#9D9F9F]">Leads per Month</span>
                                    <p className="font-serif text-2xl text-[#2D3538]">{leadsValue.toLocaleString()}</p>
                                </div>
                                <div>
                                    <span className="text-sm text-[#9D9F9F]">Win Rate</span>
                                    <p className="font-serif text-2xl text-[#2D3538]">{(market.pathToSom.winRate * 100).toFixed(0)}%</p>
                                </div>
                                <div>
                                    <span className="text-sm text-[#9D9F9F]">Top Channels</span>
                                    <p className="text-[#2D3538]">
                                        {market.pathToSom.channelMix.slice(0, 2).map(ch => ch.channel).join(', ')}
                                    </p>
                                </div>
                            </div>
                        </div>

                        {/* Action - Final */}
                        <div ref={actionRef} className="flex items-center justify-end pt-8 border-t border-[#E5E6E3]">
                            <Button
                                onClick={onComplete}
                                className="bg-[#2D3538] hover:bg-[#1A1D1E] text-white px-10 py-6 rounded-xl font-medium transition-all hover:scale-[1.02]"
                            >
                                Launch Dashboard <ArrowRight className="ml-2 h-4 w-4" />
                            </Button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
