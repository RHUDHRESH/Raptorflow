'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { loadFoundationDB, FoundationData } from '@/lib/foundation';
import { Button } from '@/components/ui/button';
import {
    Check, Copy, ChevronDown, ChevronUp, ArrowRight,
    Sparkles, Target, Users, MessageSquare, Zap, Star,
    Download, ExternalLink
} from 'lucide-react';
import { toast } from 'sonner';
import gsap from 'gsap';

function copyToClipboard(text: string, label: string) {
    navigator.clipboard.writeText(text);
    toast.success(`${label} copied!`);
}

export function FoundationResults() {
    const router = useRouter();
    const containerRef = useRef<HTMLDivElement>(null);
    const [foundation, setFoundation] = useState<FoundationData | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [expandedSection, setExpandedSection] = useState<string | null>('positioning');

    useEffect(() => {
        const loadData = async () => {
            try {
                const data = await loadFoundationDB();
                setFoundation(data);
                setIsLoading(false);
            } catch (error) {
                console.error('Error loading foundation:', error);
                setIsLoading(false);
            }
        };
        loadData();
    }, []);

    // Stagger animation on load
    useEffect(() => {
        if (!isLoading && containerRef.current) {
            const cards = containerRef.current.querySelectorAll('.result-card');
            gsap.fromTo(cards,
                { opacity: 0, y: 30 },
                { opacity: 1, y: 0, duration: 0.6, stagger: 0.1, ease: 'power3.out' }
            );
        }
    }, [isLoading]);

    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-[#F3F4EE]">
                <div className="w-12 h-12 border-[3px] border-[#2D3538] border-t-transparent rounded-full animate-spin" />
            </div>
        );
    }

    const phase3 = foundation?.phase3;
    const phase4 = foundation?.phase4;
    const phase5 = foundation?.phase5;
    const phase6 = foundation?.phase6;

    const positioningStatement = phase4?.positioningStatement || '';
    const coreMessage = phase6?.blueprint?.controllingIdea || phase6?.blueprint?.coreMessage || '';
    const primaryICP = phase5?.icps?.[0];
    const primaryClaim = phase3?.claims?.find(c => c.id === phase3?.primaryClaimId)?.promise || phase3?.claims?.[0]?.promise || '';

    return (
        <div className="min-h-screen bg-[#F3F4EE]" ref={containerRef}>
            {/* Hero Header */}
            <div className="bg-[#2D3538] text-white py-20 px-8">
                <div className="max-w-4xl mx-auto text-center">
                    <div className="flex justify-center gap-2 mb-6">
                        {[1, 2, 3, 4, 5, 6].map(i => (
                            <div key={i} className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
                                <Check className="w-4 h-4 text-white" />
                            </div>
                        ))}
                    </div>
                    <h1 className="font-serif text-[48px] leading-[1.1] mb-4">
                        Your Marketing Foundation
                    </h1>
                    <p className="text-white/60 text-lg max-w-xl mx-auto">
                        Everything you need to communicate with clarity and close with confidence.
                    </p>
                </div>
            </div>

            {/* Main Content */}
            <div className="max-w-4xl mx-auto px-8 py-16 space-y-8">

                {/* HERO CARD: Positioning Statement */}
                <div className="result-card bg-white border border-[#E5E6E3] rounded-3xl p-10 shadow-sm relative group overflow-hidden">
                    <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-[#2D3538] to-[#5B5F61]" />
                    <div className="flex items-center gap-2 mb-6">
                        <Target className="w-5 h-5 text-[#9D9F9F]" />
                        <span className="text-[11px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F]">
                            Positioning Statement
                        </span>
                    </div>
                    <p className="font-serif text-[28px] text-[#2D3538] leading-[1.4] mb-6">
                        "{positioningStatement || 'Complete Phase 4 to generate your positioning statement.'}"
                    </p>
                    {positioningStatement && (
                        <button
                            onClick={() => copyToClipboard(positioningStatement, 'Positioning statement')}
                            className="flex items-center gap-2 text-sm text-[#9D9F9F] hover:text-[#2D3538] transition-colors"
                        >
                            <Copy className="w-4 h-4" /> Copy to clipboard
                        </button>
                    )}
                </div>

                {/* Two Column Grid */}
                <div className="grid grid-cols-2 gap-6">

                    {/* Core Message */}
                    <div className="result-card bg-[#2D3538] rounded-2xl p-8 text-white relative group">
                        <div className="flex items-center gap-2 mb-4">
                            <Sparkles className="w-4 h-4 text-white/50" />
                            <span className="text-[10px] font-mono uppercase tracking-[0.15em] text-white/50">
                                Core Message
                            </span>
                        </div>
                        <p className="font-serif text-xl leading-[1.4]">
                            "{coreMessage || 'Complete Phase 6 to generate.'}"
                        </p>
                        {coreMessage && (
                            <button
                                onClick={() => copyToClipboard(coreMessage, 'Core message')}
                                className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity p-2 hover:bg-white/10 rounded-lg"
                            >
                                <Copy className="w-4 h-4 text-white/60" />
                            </button>
                        )}
                    </div>

                    {/* Primary Claim */}
                    <div className="result-card bg-white border border-[#E5E6E3] rounded-2xl p-8 relative group">
                        <div className="flex items-center gap-2 mb-4">
                            <Star className="w-4 h-4 text-[#9D9F9F]" />
                            <span className="text-[10px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F]">
                                Primary Claim
                            </span>
                        </div>
                        <p className="font-serif text-xl text-[#2D3538] leading-[1.4]">
                            "{primaryClaim || 'Complete Phase 3 to generate.'}"
                        </p>
                        {primaryClaim && (
                            <button
                                onClick={() => copyToClipboard(primaryClaim, 'Primary claim')}
                                className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity p-2 hover:bg-[#F3F4EE] rounded-lg"
                            >
                                <Copy className="w-4 h-4 text-[#9D9F9F]" />
                            </button>
                        )}
                    </div>
                </div>

                {/* Primary ICP */}
                {primaryICP && (
                    <div className="result-card bg-white border border-[#E5E6E3] rounded-2xl overflow-hidden">
                        <button
                            onClick={() => setExpandedSection(expandedSection === 'icp' ? null : 'icp')}
                            className="w-full flex items-center justify-between p-6 hover:bg-[#FAFAF8] transition-colors"
                        >
                            <div className="flex items-center gap-3">
                                <div className="w-10 h-10 bg-[#2D3538] rounded-full flex items-center justify-center">
                                    <Users className="w-5 h-5 text-white" />
                                </div>
                                <div className="text-left">
                                    <span className="text-[10px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F] block">
                                        Primary ICP
                                    </span>
                                    <span className="font-medium text-[#2D3538]">{primaryICP.name}</span>
                                </div>
                            </div>
                            {expandedSection === 'icp' ? (
                                <ChevronUp className="w-5 h-5 text-[#9D9F9F]" />
                            ) : (
                                <ChevronDown className="w-5 h-5 text-[#9D9F9F]" />
                            )}
                        </button>

                        {expandedSection === 'icp' && (
                            <div className="p-6 pt-0 grid grid-cols-2 gap-4">
                                <div className="bg-[#FAFAF8] rounded-xl p-5">
                                    <span className="text-[10px] font-mono uppercase text-[#9D9F9F] block mb-3">
                                        Triggers
                                    </span>
                                    <ul className="space-y-2">
                                        {(primaryICP.triggers || []).slice(0, 3).map((t, i) => (
                                            <li key={i} className="text-sm text-[#2D3538] flex items-start gap-2">
                                                <div className="w-1 h-1 bg-[#2D3538] rounded-full mt-2" />
                                                {t}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                                <div className="bg-[#FAFAF8] rounded-xl p-5">
                                    <span className="text-[10px] font-mono uppercase text-[#9D9F9F] block mb-3">
                                        Objections
                                    </span>
                                    <ul className="space-y-2">
                                        {(primaryICP.objections || []).slice(0, 3).map((o, i) => (
                                            <li key={i} className="text-sm text-[#2D3538] flex items-start gap-2">
                                                <div className="w-1 h-1 bg-[#2D3538] rounded-full mt-2" />
                                                {o}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {/* Differentiators */}
                {phase3?.differentiators && phase3.differentiators.length > 0 && (
                    <div className="result-card bg-white border border-[#E5E6E3] rounded-2xl overflow-hidden">
                        <button
                            onClick={() => setExpandedSection(expandedSection === 'diff' ? null : 'diff')}
                            className="w-full flex items-center justify-between p-6 hover:bg-[#FAFAF8] transition-colors"
                        >
                            <div className="flex items-center gap-3">
                                <div className="w-10 h-10 bg-[#F3F4EE] rounded-full flex items-center justify-center">
                                    <Zap className="w-5 h-5 text-[#2D3538]" />
                                </div>
                                <div className="text-left">
                                    <span className="text-[10px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F] block">
                                        Differentiators
                                    </span>
                                    <span className="font-medium text-[#2D3538]">{phase3.differentiators.length} unique capabilities</span>
                                </div>
                            </div>
                            {expandedSection === 'diff' ? (
                                <ChevronUp className="w-5 h-5 text-[#9D9F9F]" />
                            ) : (
                                <ChevronDown className="w-5 h-5 text-[#9D9F9F]" />
                            )}
                        </button>

                        {expandedSection === 'diff' && (
                            <div className="p-6 pt-0 space-y-3">
                                {phase3.differentiators.map((diff, i) => (
                                    <div key={diff.id || i} className="bg-[#FAFAF8] rounded-xl p-5 group relative">
                                        <div className="flex items-center gap-2 mb-2">
                                            <span className="text-[10px] font-mono text-[#9D9F9F]">#{i + 1}</span>
                                            <div className={`w-2 h-2 rounded-full ${diff.status === 'proven' ? 'bg-[#2D3538]' : 'bg-[#C0C1BE]'}`} />
                                            <span className="text-[10px] font-mono uppercase text-[#9D9F9F]">{diff.status}</span>
                                        </div>
                                        <p className="font-medium text-[#2D3538]">{diff.capability}</p>
                                        {diff.mechanism && <p className="text-sm text-[#5B5F61] mt-1">{diff.mechanism}</p>}
                                        <button
                                            onClick={() => copyToClipboard(`${diff.capability}: ${diff.mechanism}`, 'Differentiator')}
                                            className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity p-1.5 hover:bg-white rounded-lg"
                                        >
                                            <Copy className="w-3.5 h-3.5 text-[#9D9F9F]" />
                                        </button>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}

                {/* Soundbites */}
                {phase6?.soundbites && phase6.soundbites.length > 0 && (
                    <div className="result-card bg-white border border-[#E5E6E3] rounded-2xl overflow-hidden">
                        <button
                            onClick={() => setExpandedSection(expandedSection === 'sound' ? null : 'sound')}
                            className="w-full flex items-center justify-between p-6 hover:bg-[#FAFAF8] transition-colors"
                        >
                            <div className="flex items-center gap-3">
                                <div className="w-10 h-10 bg-[#F3F4EE] rounded-full flex items-center justify-center">
                                    <MessageSquare className="w-5 h-5 text-[#2D3538]" />
                                </div>
                                <div className="text-left">
                                    <span className="text-[10px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F] block">
                                        Soundbites
                                    </span>
                                    <span className="font-medium text-[#2D3538]">{phase6.soundbites.length} ready-to-use messages</span>
                                </div>
                            </div>
                            {expandedSection === 'sound' ? (
                                <ChevronUp className="w-5 h-5 text-[#9D9F9F]" />
                            ) : (
                                <ChevronDown className="w-5 h-5 text-[#9D9F9F]" />
                            )}
                        </button>

                        {expandedSection === 'sound' && (
                            <div className="p-6 pt-0 space-y-3">
                                {phase6.soundbites.slice(0, 5).map((sb: any, i) => (
                                    <div key={sb.id || i} className="bg-[#FAFAF8] rounded-xl p-5 group relative">
                                        <span className="text-[10px] font-mono uppercase text-[#9D9F9F] block mb-2">
                                            {sb.context || `Soundbite ${i + 1}`}
                                        </span>
                                        <p className="text-[#2D3538]">"{sb.copy || sb.text}"</p>
                                        <button
                                            onClick={() => copyToClipboard(sb.copy || sb.text || '', 'Soundbite')}
                                            className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity p-1.5 hover:bg-white rounded-lg"
                                        >
                                            <Copy className="w-3.5 h-3.5 text-[#9D9F9F]" />
                                        </button>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}

                {/* Actions Bar */}
                <div className="flex items-center justify-between pt-8 border-t border-[#E5E6E3]">
                    <button
                        onClick={() => router.push('/foundation')}
                        className="text-[#5B5F61] hover:text-[#2D3538] transition-colors text-sm flex items-center gap-2"
                    >
                        Edit Foundation <ExternalLink className="w-4 h-4" />
                    </button>
                    <Button
                        onClick={() => router.push('/dashboard')}
                        className="bg-[#2D3538] hover:bg-[#1A1D1E] text-white px-8 py-6 rounded-xl"
                    >
                        Go to Dashboard <ArrowRight className="ml-2 h-5 w-5" />
                    </Button>
                </div>
            </div>
        </div>
    );
}
