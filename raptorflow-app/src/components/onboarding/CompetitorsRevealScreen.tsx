'use client';

import React, { useEffect, useRef, useState } from 'react';
import { DerivedCompetitive } from '@/lib/foundation';
import { ArrowRight, X, Shield, Zap, AlertTriangle, Target } from 'lucide-react';
import { Button } from '@/components/ui/button';
import styles from './QuestionFlow.module.css';
import gsap from 'gsap';

interface CompetitorsRevealScreenProps {
    competitive: DerivedCompetitive;
    onContinue: () => void;
}

type CompetitorDetail = {
    type: 'status-quo' | 'indirect' | 'direct';
    name: string;
    data: any;
};

export function CompetitorsRevealScreen({ competitive, onContinue }: CompetitorsRevealScreenProps) {
    const [selectedCompetitor, setSelectedCompetitor] = useState<CompetitorDetail | null>(null);

    const containerRef = useRef<HTMLDivElement>(null);
    const leftPanelRef = useRef<HTMLDivElement>(null);
    const statusQuoRef = useRef<HTMLDivElement>(null);
    const wedgeRef = useRef<HTMLDivElement>(null);
    const indirectRef = useRef<HTMLDivElement>(null);
    const directRef = useRef<HTMLDivElement>(null);
    const actionRef = useRef<HTMLDivElement>(null);
    const drawerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!containerRef.current) return;

        const tl = gsap.timeline();

        gsap.set(leftPanelRef.current, { x: -80, opacity: 0 });
        gsap.set(statusQuoRef.current, { y: 20, opacity: 0 });
        gsap.set(wedgeRef.current, { y: 40, opacity: 0, scale: 0.98 });
        gsap.set(indirectRef.current, { y: 30, opacity: 0 });
        gsap.set(directRef.current, { y: 30, opacity: 0 });
        gsap.set(actionRef.current, { y: 20, opacity: 0 });

        tl.to(leftPanelRef.current, { x: 0, opacity: 1, duration: 0.7, ease: 'power3.out' })
            .to(statusQuoRef.current, { y: 0, opacity: 1, duration: 0.5, ease: 'power2.out' }, '-=0.3')
            .to(wedgeRef.current, { y: 0, opacity: 1, scale: 1, duration: 0.7, ease: 'power3.out' }, '-=0.2')
            .to(indirectRef.current, { y: 0, opacity: 1, duration: 0.5, ease: 'power2.out' }, '-=0.3');

        if (indirectRef.current) {
            const cards = indirectRef.current.querySelectorAll('.competitor-card');
            gsap.set(cards, { x: 20, opacity: 0 });
            tl.to(cards, { x: 0, opacity: 1, duration: 0.4, stagger: 0.1, ease: 'power2.out' }, '-=0.3');
        }

        tl.to(directRef.current, { y: 0, opacity: 1, duration: 0.5, ease: 'power2.out' }, '-=0.2');

        if (directRef.current) {
            const cards = directRef.current.querySelectorAll('.competitor-card');
            gsap.set(cards, { x: 20, opacity: 0 });
            tl.to(cards, { x: 0, opacity: 1, duration: 0.4, stagger: 0.1, ease: 'power2.out' }, '-=0.3');
        }

        tl.to(actionRef.current, { y: 0, opacity: 1, duration: 0.4, ease: 'power2.out' }, '-=0.2');

        return () => { tl.kill(); };
    }, []);

    // Drawer animation
    useEffect(() => {
        if (!drawerRef.current) return;

        if (selectedCompetitor) {
            gsap.set(drawerRef.current, { x: '100%', opacity: 0 });
            gsap.to(drawerRef.current, { x: '0%', opacity: 1, duration: 0.4, ease: 'power3.out' });

            const items = drawerRef.current.querySelectorAll('.drawer-section');
            gsap.set(items, { y: 20, opacity: 0 });
            gsap.to(items, { y: 0, opacity: 1, duration: 0.3, stagger: 0.08, ease: 'power2.out', delay: 0.2 });
        } else {
            gsap.to(drawerRef.current, { x: '100%', opacity: 0, duration: 0.3, ease: 'power2.in' });
        }
    }, [selectedCompetitor]);

    const openStatusQuo = () => {
        setSelectedCompetitor({ type: 'status-quo', name: competitive.statusQuo.name, data: competitive.statusQuo });
    };

    const openIndirect = (comp: any) => {
        setSelectedCompetitor({ type: 'indirect', name: comp.name, data: comp });
    };

    const openDirect = (comp: any) => {
        setSelectedCompetitor({ type: 'direct', name: comp.name, data: comp });
    };

    return (
        <div ref={containerRef} className={styles.flowContainer}>
            <div ref={leftPanelRef} className={styles.leftPanel}>
                <div className="w-full h-full flex flex-col">
                    <div className={styles.logoArea}>
                        <div className="w-6 h-6 bg-white rounded flex-shrink-0" />
                        <span className={styles.logoText}>RAPTORFLOW</span>
                    </div>
                    <div className={styles.sectionInfo}>
                        <span className="text-xs font-mono uppercase tracking-[0.2em] text-white/40 mb-4 block">Your Market Intelligence</span>
                        <h2 className="font-serif text-4xl text-white tracking-tight mb-3">Competitors</h2>
                        <p className="text-sm text-white/50 leading-relaxed">Know thy battlefield.</p>
                    </div>
                    <button
                        ref={statusQuoRef}
                        onClick={openStatusQuo}
                        className="mt-12 py-6 border-t border-white/10 text-left hover:bg-white/5 transition-colors rounded-xl px-4 -mx-4"
                    >
                        <span className="text-xs font-mono uppercase tracking-[0.15em] text-white/40 mb-4 block">The Real Enemy</span>
                        <p className="font-semibold text-white text-lg">{competitive.statusQuo.name}</p>
                        <p className="text-sm text-white/50 mt-1">{competitive.statusQuo.toleratedPain}</p>
                        <p className="text-xs text-white/30 mt-3">Click to see why they matter →</p>
                    </button>
                    <div className="mt-auto pt-8 border-t border-white/10">
                        <span className="text-xs font-mono uppercase tracking-wider text-white/30">{competitive.direct.length + competitive.indirect.length} alternatives mapped</span>
                    </div>
                </div>
            </div>

            <div className={styles.rightPanel}>
                <div className="flex-1 flex flex-col max-w-[680px] mx-auto w-full px-16 py-16 overflow-y-auto">
                    <div>
                        <div ref={wedgeRef} className="mb-12 p-8 border-2 border-[#2D3538] rounded-2xl">
                            <span className="text-xs font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-3 block">Your Wedge</span>
                            <p className="font-serif text-2xl text-[#2D3538]">{competitive.statusQuo.yourWedge}</p>
                        </div>

                        <div ref={indirectRef} className="mb-10">
                            <h3 className="text-xs font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-6 flex items-center gap-2">
                                <AlertTriangle className="w-4 h-4" /> Indirect Competitors
                            </h3>
                            <div className="space-y-4">
                                {competitive.indirect.map((comp, i) => (
                                    <button
                                        key={i}
                                        onClick={() => openIndirect(comp)}
                                        className="competitor-card w-full text-left p-5 border border-[#E5E6E3] rounded-xl hover:border-[#2D3538] hover:bg-[#FAFAF8] transition-all group cursor-pointer"
                                    >
                                        <div className="flex items-start justify-between">
                                            <div>
                                                <p className="font-medium text-[#2D3538]">{comp.name}</p>
                                                <p className="text-sm text-[#9D9F9F] mt-1">{comp.mechanism}</p>
                                            </div>
                                            <span className="text-xs font-mono text-[#9D9F9F]">{comp.priceRange}</span>
                                        </div>
                                        <p className="text-xs text-[#C0C1BE] mt-3 group-hover:text-[#5B5F61] transition-colors">Click to see why they matter →</p>
                                    </button>
                                ))}
                            </div>
                        </div>

                        {competitive.direct.length > 0 && (
                            <div ref={directRef} className="mb-10">
                                <h3 className="text-xs font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-6 flex items-center gap-2">
                                    <Target className="w-4 h-4" /> Direct Competitors
                                </h3>
                                <div className="space-y-4">
                                    {competitive.direct.map((comp, i) => (
                                        <button
                                            key={i}
                                            onClick={() => openDirect(comp)}
                                            className="competitor-card w-full text-left p-5 border border-[#E5E6E3] rounded-xl hover:border-[#2D3538] hover:bg-[#FAFAF8] transition-all group cursor-pointer"
                                        >
                                            <div className="flex items-start justify-between">
                                                <div>
                                                    <p className="font-medium text-[#2D3538]">{comp.name}</p>
                                                    <p className="text-sm text-[#9D9F9F] mt-1">{comp.positioning}</p>
                                                </div>
                                                <span className="text-xs font-mono text-[#9D9F9F] capitalize">{comp.featureOverlap} overlap</span>
                                            </div>
                                            <p className="text-xs text-[#C0C1BE] mt-3 group-hover:text-[#5B5F61] transition-colors">Click to see comparison →</p>
                                        </button>
                                    ))}
                                </div>
                            </div>
                        )}

                        <div ref={actionRef} className="flex items-center justify-end pt-8 border-t border-[#E5E6E3]">
                            <Button onClick={onContinue} className="bg-[#2D3538] hover:bg-[#1A1D1E] text-white px-8 py-6 rounded-xl font-medium transition-all hover:scale-[1.02]">
                                Continue <ArrowRight className="ml-2 h-4 w-4" />
                            </Button>
                        </div>
                    </div>
                </div>

                {/* Detail Drawer */}
                <div
                    ref={drawerRef}
                    className={`fixed inset-y-0 right-0 w-[480px] bg-white border-l border-[#E5E6E3] shadow-2xl z-50 overflow-y-auto ${!selectedCompetitor ? 'pointer-events-none' : ''}`}
                    style={{ transform: 'translateX(100%)' }}
                >
                    {selectedCompetitor && (
                        <div className="p-10">
                            <div className="flex items-center justify-between mb-10">
                                <div>
                                    <span className="text-xs font-mono uppercase tracking-wider text-[#9D9F9F] block mb-1">
                                        {selectedCompetitor.type === 'status-quo' ? 'Status Quo' : selectedCompetitor.type === 'indirect' ? 'Indirect' : 'Direct'}
                                    </span>
                                    <h2 className="font-serif text-2xl text-[#2D3538]">{selectedCompetitor.name}</h2>
                                </div>
                                <button
                                    onClick={() => setSelectedCompetitor(null)}
                                    className="p-2 rounded-lg hover:bg-[#F3F4EE] transition-colors"
                                >
                                    <X className="w-5 h-5 text-[#9D9F9F]" />
                                </button>
                            </div>

                            {selectedCompetitor.type === 'status-quo' && (
                                <>
                                    <div className="drawer-section mb-10">
                                        <h3 className="text-xs font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-4 flex items-center gap-2">
                                            <AlertTriangle className="w-4 h-4" /> Why This Matters
                                        </h3>
                                        <p className="text-[#2D3538] leading-relaxed">
                                            This is what your prospects are doing <strong>today</strong>. They've tolerated this pain because change feels risky. Your job is to make switching feel safer than staying.
                                        </p>
                                    </div>

                                    <div className="drawer-section mb-10">
                                        <h3 className="text-xs font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-4">Current Patches</h3>
                                        <div className="space-y-3">
                                            {selectedCompetitor.data.manualPatches.map((patch: string, i: number) => (
                                                <div key={i} className="p-4 bg-[#FAFAF8] rounded-xl border border-[#E5E6E3]">
                                                    <p className="text-[#5B5F61]">{patch}</p>
                                                </div>
                                            ))}
                                        </div>
                                    </div>

                                    <div className="drawer-section mb-10">
                                        <h3 className="text-xs font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-4">Tolerated Pain</h3>
                                        <p className="text-[#2D3538] italic">{selectedCompetitor.data.toleratedPain}</p>
                                    </div>

                                    <div className="drawer-section p-6 bg-[#2D3538] rounded-2xl">
                                        <h3 className="text-xs font-mono uppercase tracking-[0.15em] text-white/60 mb-4 flex items-center gap-2">
                                            <Zap className="w-4 h-4" /> Your Wedge
                                        </h3>
                                        <p className="font-serif text-xl text-white">{selectedCompetitor.data.yourWedge}</p>
                                    </div>
                                </>
                            )}

                            {selectedCompetitor.type === 'indirect' && (
                                <>
                                    <div className="drawer-section mb-10">
                                        <h3 className="text-xs font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-4">Why This Matters</h3>
                                        <p className="text-[#2D3538] leading-relaxed">
                                            Your prospects might choose this alternative even though it's not direct competition. Understanding why helps you position against the <em>job</em> they're hiring it for.
                                        </p>
                                    </div>

                                    <div className="drawer-section mb-10">
                                        <h3 className="text-xs font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-4">How They Compete</h3>
                                        <p className="text-[#2D3538]">{selectedCompetitor.data.mechanism}</p>
                                    </div>

                                    <div className="drawer-section mb-10">
                                        <h3 className="text-xs font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-4">Price Range</h3>
                                        <p className="font-serif text-2xl text-[#2D3538]">{selectedCompetitor.data.priceRange}</p>
                                    </div>

                                    <div className="drawer-section mb-10">
                                        <h3 className="text-xs font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-4">Their Weakness</h3>
                                        <p className="text-[#5B5F61] italic">{selectedCompetitor.data.weakness}</p>
                                    </div>

                                    <div className="drawer-section p-6 bg-[#2D3538] rounded-2xl">
                                        <h3 className="text-xs font-mono uppercase tracking-[0.15em] text-white/60 mb-4 flex items-center gap-2">
                                            <Shield className="w-4 h-4" /> Your Edge
                                        </h3>
                                        <p className="font-serif text-xl text-white">{selectedCompetitor.data.yourEdge}</p>
                                    </div>
                                </>
                            )}

                            {selectedCompetitor.type === 'direct' && (
                                <>
                                    <div className="drawer-section mb-10">
                                        <h3 className="text-xs font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-4">Why This Matters</h3>
                                        <p className="text-[#2D3538] leading-relaxed">
                                            This is head-to-head competition. You'll encounter them in deals, on comparison lists, and in prospect conversations. Know them deeply.
                                        </p>
                                    </div>

                                    <div className="drawer-section mb-10">
                                        <h3 className="text-xs font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-4">Their Positioning</h3>
                                        <p className="text-[#2D3538]">{selectedCompetitor.data.positioning}</p>
                                    </div>

                                    <div className="drawer-section mb-10">
                                        <h3 className="text-xs font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-4">Feature Overlap</h3>
                                        <div className="flex items-center gap-4">
                                            <div className="flex-1 h-2 bg-[#E5E6E3] rounded-full overflow-hidden">
                                                <div
                                                    className="h-full bg-[#2D3538] rounded-full"
                                                    style={{ width: selectedCompetitor.data.featureOverlap === 'high' ? '80%' : selectedCompetitor.data.featureOverlap === 'medium' ? '50%' : '25%' }}
                                                />
                                            </div>
                                            <span className="text-sm font-mono text-[#9D9F9F] capitalize">{selectedCompetitor.data.featureOverlap}</span>
                                        </div>
                                    </div>

                                    <div className="drawer-section mb-10">
                                        <h3 className="text-xs font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-4">Their Weakness</h3>
                                        <p className="text-[#5B5F61] italic">{selectedCompetitor.data.weakness}</p>
                                    </div>

                                    <div className="drawer-section p-6 bg-[#2D3538] rounded-2xl">
                                        <h3 className="text-xs font-mono uppercase tracking-[0.15em] text-white/60 mb-4 flex items-center gap-2">
                                            <Shield className="w-4 h-4" /> Your Edge
                                        </h3>
                                        <p className="font-serif text-xl text-white">{selectedCompetitor.data.yourEdge}</p>
                                    </div>
                                </>
                            )}
                        </div>
                    )}
                </div>

                {/* Backdrop */}
                {selectedCompetitor && (
                    <div
                        className="fixed inset-0 bg-black/20 z-40"
                        onClick={() => setSelectedCompetitor(null)}
                    />
                )}
            </div>
        </div>
    );
}
