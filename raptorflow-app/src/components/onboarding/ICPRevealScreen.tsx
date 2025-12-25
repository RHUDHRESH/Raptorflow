'use client';

import React, { useEffect, useRef, useState } from 'react';
import { DerivedICP } from '@/lib/foundation';
import { ArrowRight, X, Users, Brain, ShoppingCart, Target, MessageCircle } from 'lucide-react';
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
    const [showDetailDrawer, setShowDetailDrawer] = useState(false);
    const selectedIcp = icps[selectedIndex];

    const containerRef = useRef<HTMLDivElement>(null);
    const leftPanelRef = useRef<HTMLDivElement>(null);
    const rightPanelRef = useRef<HTMLDivElement>(null);
    const titleRef = useRef<HTMLHeadingElement>(null);
    const descRef = useRef<HTMLParagraphElement>(null);
    const gridRef = useRef<HTMLDivElement>(null);
    const icpListRef = useRef<HTMLDivElement>(null);
    const actionRef = useRef<HTMLDivElement>(null);
    const drawerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!containerRef.current || hasAnimated) return;

        const tl = gsap.timeline({ onComplete: () => setHasAnimated(true) });

        gsap.set(leftPanelRef.current, { x: -100, opacity: 0 });
        gsap.set(rightPanelRef.current, { opacity: 0 });
        gsap.set(titleRef.current, { y: 40, opacity: 0 });
        gsap.set(descRef.current, { y: 20, opacity: 0 });
        gsap.set(actionRef.current, { y: 20, opacity: 0 });

        tl.to(leftPanelRef.current, { x: 0, opacity: 1, duration: 0.8, ease: 'power3.out' })
            .to(rightPanelRef.current, { opacity: 1, duration: 0.6, ease: 'power2.out' }, '-=0.4')
            .to(titleRef.current, { y: 0, opacity: 1, duration: 0.7, ease: 'power3.out' }, '-=0.3')
            .to(descRef.current, { y: 0, opacity: 1, duration: 0.5, ease: 'power2.out' }, '-=0.4');

        if (icpListRef.current) {
            const items = icpListRef.current.querySelectorAll('.icp-item');
            gsap.set(items, { x: -30, opacity: 0 });
            tl.to(items, { x: 0, opacity: 1, duration: 0.4, stagger: 0.1, ease: 'power2.out' }, '-=0.4');
        }

        if (gridRef.current) {
            const gridItems = gridRef.current.querySelectorAll('.grid-item');
            gsap.set(gridItems, { y: 30, opacity: 0 });
            tl.to(gridItems, { y: 0, opacity: 1, duration: 0.5, stagger: 0.08, ease: 'power2.out' }, '-=0.3');
        }

        tl.to(actionRef.current, { y: 0, opacity: 1, duration: 0.4, ease: 'power2.out' }, '-=0.2');

        return () => { tl.kill(); };
    }, [hasAnimated]);

    useEffect(() => {
        if (!hasAnimated || !titleRef.current || !gridRef.current) return;

        const tl = gsap.timeline();
        tl.to([titleRef.current, descRef.current], { opacity: 0, y: -10, duration: 0.15, ease: 'power2.in' })
            .to(gridRef.current?.querySelectorAll('.grid-item') || [], { opacity: 0, y: -10, duration: 0.1, stagger: 0.02, ease: 'power2.in' }, '-=0.1');
        tl.to([titleRef.current, descRef.current], { opacity: 1, y: 0, duration: 0.3, ease: 'power2.out', delay: 0.05 })
            .to(gridRef.current?.querySelectorAll('.grid-item') || [], { opacity: 1, y: 0, duration: 0.3, stagger: 0.05, ease: 'power2.out' }, '-=0.2');
    }, [selectedIndex, hasAnimated]);

    // Drawer animation
    useEffect(() => {
        if (!drawerRef.current) return;

        if (showDetailDrawer) {
            gsap.set(drawerRef.current, { x: '100%', opacity: 0 });
            gsap.to(drawerRef.current, { x: '0%', opacity: 1, duration: 0.4, ease: 'power3.out' });

            const items = drawerRef.current.querySelectorAll('.drawer-section');
            gsap.set(items, { y: 20, opacity: 0 });
            gsap.to(items, { y: 0, opacity: 1, duration: 0.3, stagger: 0.08, ease: 'power2.out', delay: 0.2 });
        } else {
            gsap.to(drawerRef.current, { x: '100%', opacity: 0, duration: 0.3, ease: 'power2.in' });
        }
    }, [showDetailDrawer]);

    const handleSelectIcp = (index: number) => {
        if (index !== selectedIndex) {
            setSelectedIndex(index);
            setShowDetailDrawer(false);
        }
    };

    const openDetailDrawer = () => {
        setShowDetailDrawer(true);
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
                        <h2 className="font-serif text-4xl text-white tracking-tight mb-3">Meet Your Cohorts</h2>
                        <p className="text-sm text-white/50 leading-relaxed">The people who need you most.</p>
                    </div>
                    <div ref={icpListRef} className="mt-12 space-y-2 flex-1">
                        {icps.map((icp, index) => (
                            <button
                                key={icp.id}
                                onClick={() => handleSelectIcp(index)}
                                className={`icp-item w-full text-left py-4 px-5 rounded-xl transition-all duration-300 border ${selectedIndex === index ? 'bg-white/10 border-white/20' : 'bg-transparent border-transparent hover:bg-white/5'
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
                        <p className="text-xs font-mono uppercase tracking-wider text-white/30">Click card to see full profile</p>
                    </div>
                </div>
            </div>

            <div ref={rightPanelRef} className={styles.rightPanel}>
                <div className="flex-1 flex flex-col max-w-[680px] mx-auto w-full px-16 py-16 relative">
                    {selectedIcp && (
                        <div>
                            <div className="mb-12">
                                <h1 ref={titleRef} className="font-serif text-5xl text-[#2D3538] tracking-tight leading-tight mb-4">{selectedIcp.name}</h1>
                                <p ref={descRef} className="text-lg text-[#5B5F61] leading-relaxed max-w-lg">{selectedIcp.description}</p>
                            </div>

                            {/* Clickable Summary Grid */}
                            <div ref={gridRef} className="grid grid-cols-2 gap-6 mb-12">
                                <button
                                    onClick={openDetailDrawer}
                                    className="grid-item group text-left p-6 border border-[#E5E6E3] rounded-2xl hover:border-[#2D3538] hover:bg-[#FAFAF8] transition-all cursor-pointer"
                                >
                                    <div className="flex items-center gap-3 mb-4">
                                        <Target className="w-5 h-5 text-[#9D9F9F] group-hover:text-[#2D3538] transition-colors" />
                                        <h3 className="text-xs font-mono uppercase tracking-[0.15em] text-[#9D9F9F] group-hover:text-[#2D3538] transition-colors">Firmographics</h3>
                                    </div>
                                    <p className="text-[#2D3538] font-medium">{selectedIcp.firmographics.companySize}</p>
                                    <p className="text-sm text-[#9D9F9F] mt-1">{selectedIcp.firmographics.industry.slice(0, 2).join(', ')}</p>
                                    <p className="text-xs text-[#C0C1BE] mt-3 group-hover:text-[#5B5F61] transition-colors">Click to see full profile →</p>
                                </button>

                                <button
                                    onClick={openDetailDrawer}
                                    className="grid-item group text-left p-6 border border-[#E5E6E3] rounded-2xl hover:border-[#2D3538] hover:bg-[#FAFAF8] transition-all cursor-pointer"
                                >
                                    <div className="flex items-center gap-3 mb-4">
                                        <Brain className="w-5 h-5 text-[#9D9F9F] group-hover:text-[#2D3538] transition-colors" />
                                        <h3 className="text-xs font-mono uppercase tracking-[0.15em] text-[#9D9F9F] group-hover:text-[#2D3538] transition-colors">Pain Points</h3>
                                    </div>
                                    <p className="text-[#2D3538] font-medium">{selectedIcp.painMap.primary}</p>
                                    <p className="text-sm text-[#9D9F9F] mt-1 capitalize">Urgency: {selectedIcp.painMap.urgency}</p>
                                    <p className="text-xs text-[#C0C1BE] mt-3 group-hover:text-[#5B5F61] transition-colors">Click to see triggers →</p>
                                </button>

                                <button
                                    onClick={openDetailDrawer}
                                    className="grid-item group text-left p-6 border border-[#E5E6E3] rounded-2xl hover:border-[#2D3538] hover:bg-[#FAFAF8] transition-all cursor-pointer"
                                >
                                    <div className="flex items-center gap-3 mb-4">
                                        <MessageCircle className="w-5 h-5 text-[#9D9F9F] group-hover:text-[#2D3538] transition-colors" />
                                        <h3 className="text-xs font-mono uppercase tracking-[0.15em] text-[#9D9F9F] group-hover:text-[#2D3538] transition-colors">Where They Are</h3>
                                    </div>
                                    <p className="text-[#2D3538] font-medium">{selectedIcp.social.platforms[0]?.name}</p>
                                    <p className="text-sm text-[#9D9F9F] mt-1">{selectedIcp.social.platforms[0]?.timing}</p>
                                    <p className="text-xs text-[#C0C1BE] mt-3 group-hover:text-[#5B5F61] transition-colors">Click to see channels →</p>
                                </button>

                                <button
                                    onClick={openDetailDrawer}
                                    className="grid-item group text-left p-6 border border-[#E5E6E3] rounded-2xl hover:border-[#2D3538] hover:bg-[#FAFAF8] transition-all cursor-pointer"
                                >
                                    <div className="flex items-center gap-3 mb-4">
                                        <ShoppingCart className="w-5 h-5 text-[#9D9F9F] group-hover:text-[#2D3538] transition-colors" />
                                        <h3 className="text-xs font-mono uppercase tracking-[0.15em] text-[#9D9F9F] group-hover:text-[#2D3538] transition-colors">Buying Cycle</h3>
                                    </div>
                                    <p className="text-[#2D3538] font-medium">{selectedIcp.buying.timeline}</p>
                                    <p className="text-sm text-[#9D9F9F] mt-1">{selectedIcp.buying.committee.length} decision makers</p>
                                    <p className="text-xs text-[#C0C1BE] mt-3 group-hover:text-[#5B5F61] transition-colors">Click to see committee →</p>
                                </button>
                            </div>

                            <div ref={actionRef} className="flex items-center justify-between pt-8 border-t border-[#E5E6E3]">
                                <p className="text-xs font-mono text-[#9D9F9F]">{selectedIndex + 1} of {icps.length} cohorts</p>
                                <Button onClick={onContinue} className="bg-[#2D3538] hover:bg-[#1A1D1E] text-white px-8 py-6 rounded-xl font-medium transition-all hover:scale-[1.02]">
                                    Continue <ArrowRight className="ml-2 h-4 w-4" />
                                </Button>
                            </div>
                        </div>
                    )}
                </div>

                {/* Detail Drawer */}
                <div
                    ref={drawerRef}
                    className={`fixed inset-y-0 right-0 w-[480px] bg-white border-l border-[#E5E6E3] shadow-2xl z-50 overflow-y-auto ${!showDetailDrawer ? 'pointer-events-none' : ''}`}
                    style={{ transform: 'translateX(100%)' }}
                >
                    {selectedIcp && (
                        <div className="p-10">
                            <div className="flex items-center justify-between mb-10">
                                <h2 className="font-serif text-2xl text-[#2D3538]">Full Profile</h2>
                                <button
                                    onClick={() => setShowDetailDrawer(false)}
                                    className="p-2 rounded-lg hover:bg-[#F3F4EE] transition-colors"
                                >
                                    <X className="w-5 h-5 text-[#9D9F9F]" />
                                </button>
                            </div>

                            {/* Behavioral Traits */}
                            <div className="drawer-section mb-10">
                                <h3 className="text-xs font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-4 flex items-center gap-2">
                                    <Brain className="w-4 h-4" /> Behavioral Traits
                                </h3>
                                <div className="space-y-4">
                                    {selectedIcp.behavioral.biases.map((bias, i) => (
                                        <div key={i} className="p-4 bg-[#FAFAF8] rounded-xl border border-[#E5E6E3]">
                                            <p className="font-medium text-[#2D3538]">{bias.name}</p>
                                            <p className="text-sm text-[#5B5F61] mt-1">{bias.implication}</p>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* De-Risking Strategies */}
                            <div className="drawer-section mb-10">
                                <h3 className="text-xs font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-4">How to De-Risk</h3>
                                <div className="flex flex-wrap gap-2">
                                    {selectedIcp.behavioral.deRisking.map((strategy, i) => (
                                        <span key={i} className="px-3 py-2 text-sm bg-[#2D3538] text-white rounded-lg">{strategy}</span>
                                    ))}
                                </div>
                            </div>

                            {/* Buying Committee */}
                            <div className="drawer-section mb-10">
                                <h3 className="text-xs font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-4 flex items-center gap-2">
                                    <Users className="w-4 h-4" /> Buying Committee
                                </h3>
                                <div className="space-y-3">
                                    {selectedIcp.buying.committee.map((member, i) => (
                                        <div key={i} className="p-4 border border-[#E5E6E3] rounded-xl">
                                            <p className="font-medium text-[#2D3538]">{member.role}</p>
                                            <p className="text-sm text-[#9D9F9F] mt-1">Focus: {member.focus}</p>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* Proof They Need */}
                            <div className="drawer-section mb-10">
                                <h3 className="text-xs font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-4">Proof They Need</h3>
                                <div className="space-y-2">
                                    {selectedIcp.buying.proofNeeded.map((proof, i) => (
                                        <div key={i} className="flex items-center gap-3 text-[#2D3538]">
                                            <div className="w-1.5 h-1.5 rounded-full bg-[#2D3538]" />
                                            {proof}
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* Blockers */}
                            <div className="drawer-section mb-10">
                                <h3 className="text-xs font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-4">Common Blockers</h3>
                                <div className="space-y-2">
                                    {selectedIcp.buying.blockers.map((blocker, i) => (
                                        <div key={i} className="flex items-center gap-3 text-[#5B5F61]">
                                            <div className="w-1.5 h-1.5 rounded-full bg-[#C0C1BE]" />
                                            {blocker}
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* Peer Authorities */}
                            <div className="drawer-section mb-10">
                                <h3 className="text-xs font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-4">Who They Listen To</h3>
                                <div className="flex flex-wrap gap-2">
                                    {selectedIcp.social.authorities.map((auth, i) => (
                                        <span key={i} className="px-3 py-2 text-sm border border-[#E5E6E3] rounded-lg text-[#5B5F61]">{auth}</span>
                                    ))}
                                </div>
                            </div>

                            {/* All Channels */}
                            <div className="drawer-section">
                                <h3 className="text-xs font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-4">All Channels</h3>
                                <div className="space-y-3">
                                    {selectedIcp.social.platforms.map((platform, i) => (
                                        <div key={i} className="p-4 border border-[#E5E6E3] rounded-xl">
                                            <p className="font-medium text-[#2D3538]">{platform.name}</p>
                                            <p className="text-sm text-[#9D9F9F] mt-1">{platform.timing} • {platform.vibe}</p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {/* Backdrop */}
                {showDetailDrawer && (
                    <div
                        className="fixed inset-0 bg-black/20 z-40"
                        onClick={() => setShowDetailDrawer(false)}
                    />
                )}
            </div>
        </div>
    );
}
