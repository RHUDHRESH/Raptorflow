'use client';

import React, { useEffect, useRef, useState } from 'react';
import { DerivedSoundbites } from '@/lib/foundation';
import { ArrowRight, Copy, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import styles from './QuestionFlow.module.css';
import gsap from 'gsap';

interface MessagingRevealScreenProps {
    soundbites: DerivedSoundbites;
    onContinue: () => void;
}

export function MessagingRevealScreen({ soundbites, onContinue }: MessagingRevealScreenProps) {
    const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
    const containerRef = useRef<HTMLDivElement>(null);
    const leftPanelRef = useRef<HTMLDivElement>(null);
    const oneLinerRef = useRef<HTMLParagraphElement>(null);
    const soundbitesRef = useRef<HTMLDivElement>(null);
    const actionRef = useRef<HTMLDivElement>(null);

    const handleCopy = (text: string, index: number) => {
        navigator.clipboard.writeText(text);
        setCopiedIndex(index);
        setTimeout(() => setCopiedIndex(null), 2000);
    };

    useEffect(() => {
        if (!containerRef.current) return;

        const tl = gsap.timeline();

        gsap.set(leftPanelRef.current, { x: -80, opacity: 0 });
        gsap.set(oneLinerRef.current, { y: 20, opacity: 0 });
        gsap.set(actionRef.current, { y: 20, opacity: 0 });

        tl.to(leftPanelRef.current, { x: 0, opacity: 1, duration: 0.7, ease: 'power3.out' })
            .to(oneLinerRef.current, { y: 0, opacity: 1, duration: 0.6, ease: 'power2.out' }, '-=0.3');

        if (soundbitesRef.current) {
            const cards = soundbitesRef.current.querySelectorAll('.soundbite-card');
            gsap.set(cards, { y: 30, opacity: 0 });
            tl.to(cards, { y: 0, opacity: 1, duration: 0.4, stagger: 0.1, ease: 'power2.out' }, '-=0.2');
        }

        tl.to(actionRef.current, { y: 0, opacity: 1, duration: 0.4, ease: 'power2.out' }, '-=0.2');

        return () => { tl.kill(); };
    }, []);

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
                        <h2 className="font-serif text-4xl text-white tracking-tight mb-3">Messaging</h2>
                        <p className="text-sm text-white/50 leading-relaxed">Words that convert.</p>
                    </div>
                    <div className="mt-12 py-6 border-t border-white/10">
                        <span className="text-xs font-mono uppercase tracking-[0.15em] text-white/40 mb-4 block">Your One-Liner</span>
                        <p ref={oneLinerRef} className="font-serif text-xl text-white leading-snug italic">"{soundbites.oneLiner}"</p>
                    </div>
                    <div className="mt-auto pt-8 border-t border-white/10">
                        <span className="text-xs font-mono uppercase tracking-wider text-white/30">{soundbites.soundbites.length} soundbites ready</span>
                    </div>
                </div>
            </div>
            <div className={styles.rightPanel}>
                <div className="flex-1 flex flex-col max-w-[680px] mx-auto w-full px-16 py-16 overflow-y-auto">
                    <div>
                        <h3 className="text-xs font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-8">Tactical Soundbites</h3>
                        <div ref={soundbitesRef} className="space-y-6 mb-12">
                            {soundbites.soundbites.map((bite, i) => (
                                <div key={i} className="soundbite-card group p-6 border border-[#E5E6E3] rounded-xl hover:border-[#C0C1BE] transition-colors">
                                    <div className="flex items-start justify-between mb-3">
                                        <div className="flex items-center gap-3">
                                            <span className="text-xs font-mono uppercase tracking-wider text-[#9D9F9F] border border-[#E5E6E3] px-2 py-1 rounded">{bite.type}</span>
                                            <span className="text-xs text-[#9D9F9F]">→ {bite.useCase}</span>
                                        </div>
                                        <button onClick={() => handleCopy(bite.text, i)} className="opacity-0 group-hover:opacity-100 transition-opacity p-2 rounded-lg hover:bg-[#F3F4EE]">
                                            {copiedIndex === i ? <Check className="w-4 h-4 text-[#2D3538]" /> : <Copy className="w-4 h-4 text-[#9D9F9F]" />}
                                        </button>
                                    </div>
                                    <p className="font-serif text-lg text-[#2D3538] leading-relaxed">"{bite.text}"</p>
                                </div>
                            ))}
                        </div>
                        <div ref={actionRef} className="flex items-center justify-end pt-8 border-t border-[#E5E6E3]">
                            <Button onClick={onContinue} className="bg-[#2D3538] hover:bg-[#1A1D1E] text-white px-8 py-6 rounded-xl font-medium transition-all hover:scale-[1.02]">
                                Continue <ArrowRight className="ml-2 h-4 w-4" />
                            </Button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
