'use client';

import React, { useState, useEffect } from 'react';
import { useIcpStore } from '@/lib/icp-store';
import { useRouter } from 'next/navigation';
import {
    Users, AlertTriangle, MessageSquare, Ban,
    Sparkles, ArrowRight, ShieldCheck
} from 'lucide-react';
import { toast } from 'sonner';
import { Icp } from '@/types/icp-types';
import ICPEvolutionProposal from './ICPEvolutionProposal';

export default function ICPPage() {
    const router = useRouter();
    const getPrimaryIcp = useIcpStore((state: any) => state.getPrimaryIcp);
    const updateIcp = useIcpStore((state: any) => state.updateIcp);
    const icp = getPrimaryIcp();

    const [prompt, setPrompt] = useState('');
    const [showProposal, setShowProposal] = useState(false);
    const [mockProposal, setMockProposal] = useState<Partial<Icp> | null>(null);

    // Hydration fix for zustand persist
    const [mounted, setMounted] = useState(false);
    useEffect(() => {
        setMounted(true);
    }, []);

    if (!mounted) return null;

    if (!icp) {
        return (
            <div className="flex flex-col items-center justify-center min-h-screen bg-[#F3F4EE] space-y-4">
                <h1 className="font-serif text-3xl text-[#2D3538]">No Targeting Active</h1>
                <p className="text-[#5B5F61]">You haven't defined your Ideal Customer Profile yet.</p>
                <button
                    onClick={() => router.push('/icp/new')}
                    className="bg-[#2D3538] text-white px-6 py-2 rounded-xl"
                >
                    Start Wizard
                </button>
            </div>
        )
    }

    const handlePromptSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!prompt.trim()) return;

        // MOCK SIMULATION OF MATRIX
        // In real app, this goes to an agent which returns the diff
        const mockDiff: Partial<Icp> = {
            psycholinguistics: {
                ...icp.psycholinguistics,
                tonePreference: ['Technical', 'Data-Driven', 'Direct'] // Changed tone
            }
        };

        setMockProposal(mockDiff);
        setShowProposal(true);
    };

    const handleAcceptProposal = () => {
        if (icp && mockProposal) {
            updateIcp(icp.id, {
                ...mockProposal,
                confidenceScore: Math.min(0.99, icp.confidenceScore + 0.05)
            });
            toast.success("Targeting updated.", {
                description: "Muse will now adapt to the new constraints."
            });
            setShowProposal(false);
            setPrompt('');
        }
    };

    return (
        <div className="min-h-screen bg-[#F3F4EE] pb-32">
            {/* Header */}
            <header className="px-8 py-12 border-b border-[#C0C1BE]/30 bg-[#F3F4EE]">
                <div className="max-w-5xl mx-auto flex items-end justify-between">
                    <div>
                        <h1 className="font-serif text-5xl text-[#2D3538] mb-4">Targeting</h1>
                        <p className="text-[#5B5F61] max-w-xl">
                            This is who RaptorFlow is optimizing for right now.
                        </p>
                    </div>
                    <div className="flex items-center gap-6">
                        <div className="text-right">
                            <div className="text-sm font-semibold uppercase tracking-wider text-[#9D9F9F]">Confidence</div>
                            <div className="font-serif text-3xl text-[#2D3538]">{(icp.confidenceScore * 100).toFixed(0)}%</div>
                        </div>
                        <div className="text-right border-l border-[#C0C1BE] pl-6">
                            <div className="text-sm font-semibold uppercase tracking-wider text-[#9D9F9F]">Status</div>
                            <div className="flex items-center gap-2 font-medium text-[#2D3538] mt-1">
                                <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
                                Active
                            </div>
                        </div>
                    </div>
                </div>
            </header>

            {/* Content */}
            <main className="max-w-5xl mx-auto px-8 py-12 space-y-16">

                {/* Section 1: Who This Is For (Firmographics) */}
                <section className="grid grid-cols-1 md:grid-cols-12 gap-8">
                    <div className="md:col-span-4">
                        <h2 className="font-serif text-2xl text-[#2D3538] flex items-center gap-2">
                            <Users className="w-5 h-5 text-[#9D9F9F]" />
                            Who This Is For
                        </h2>
                    </div>
                    <div className="md:col-span-8 grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="bg-white p-6 rounded-2xl border border-[#C0C1BE]/30">
                            <h3 className="text-xs uppercase font-bold tracking-widest text-[#9D9F9F] mb-4">Context</h3>
                            <ul className="space-y-3">
                                {icp.firmographics.companyType.map((t: string) => (
                                    <li key={t} className="flex items-center gap-2 text-[#2D3538]">
                                        <div className="w-1.5 h-1.5 bg-[#2D3538] rounded-full" />
                                        {t === 'saas' ? 'SaaS Company' :
                                            t === 'd2c' ? 'Direct to Consumer' :
                                                t === 'agency' ? 'Agency / Service' : 'Service Business'}
                                    </li>
                                ))}
                                {icp.firmographics.salesMotion.map((t: string) => (
                                    <li key={t} className="flex items-center gap-2 text-[#2D3538]">
                                        <div className="w-1.5 h-1.5 bg-[#2D3538] rounded-full" />
                                        {t} Motion
                                    </li>
                                ))}
                            </ul>
                        </div>
                        <div className="bg-white p-6 rounded-2xl border border-[#C0C1BE]/30">
                            <h3 className="text-xs uppercase font-bold tracking-widest text-[#9D9F9F] mb-4">Buyer Reality</h3>
                            <div className="space-y-4">
                                <div>
                                    <div className="text-sm text-[#5B5F61]">Budget Comfort</div>
                                    <div className="font-medium text-[#2D3538]">{icp.firmographics.budgetComfort.join(', ') || 'Not specified'}</div>
                                </div>
                                <div>
                                    <div className="text-sm text-[#5B5F61]">Decision Maker</div>
                                    <div className="font-medium text-[#2D3538]">{icp.firmographics.decisionMaker.join(', ') || 'Unknown'}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>

                {/* Section 2: Why They Buy (Pain) */}
                <section className="grid grid-cols-1 md:grid-cols-12 gap-8 border-t border-[#C0C1BE]/30 pt-12">
                    <div className="md:col-span-4">
                        <h2 className="font-serif text-2xl text-[#2D3538] flex items-center gap-2">
                            <AlertTriangle className="w-5 h-5 text-[#9D9F9F]" />
                            Why They Buy
                        </h2>
                    </div>
                    <div className="md:col-span-8">
                        <div className="bg-white p-6 rounded-2xl border border-[#C0C1BE]/30">
                            <div className="flex justify-between items-start mb-6">
                                <h3 className="text-xs uppercase font-bold tracking-widest text-[#9D9F9F]">Core Pains</h3>
                                <span className={`px-2 py-1 rounded text-xs font-medium uppercase
                                ${icp.painMap.urgencyLevel === 'now' ? 'bg-red-50 text-red-700' :
                                        icp.painMap.urgencyLevel === 'soon' ? 'bg-amber-50 text-amber-700' : 'bg-gray-100 text-gray-600'}`}>
                                    Urgency: {icp.painMap.urgencyLevel}
                                </span>
                            </div>
                            <div className="space-y-4">
                                {icp.painMap.primaryPains.map((pain: string, idx: number) => (
                                    <div key={pain} className="flex items-start gap-4">
                                        <div className="w-6 h-6 rounded-full bg-[#2D3538] text-white flex items-center justify-center font-serif text-sm px-2">
                                            {idx + 1}
                                        </div>
                                        <span className="text-lg text-[#2D3538] pt-0.5">{pain}</span>
                                    </div>
                                ))}
                            </div>
                            {icp.painMap.triggerEvents.length > 0 && (
                                <div className="mt-8 pt-6 border-t border-dashed border-[#C0C1BE]">
                                    <h4 className="text-xs uppercase font-bold tracking-widest text-[#9D9F9F] mb-3">Trigger Events</h4>
                                    <div className="flex flex-wrap gap-2">
                                        {icp.painMap.triggerEvents.map((t: string) => (
                                            <span key={t} className="px-3 py-1 bg-[#F3F4EE] text-[#5B5F61] rounded-full text-sm">
                                                {t}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </section>

                {/* Section 3: How They Respond (Language) */}
                <section className="grid grid-cols-1 md:grid-cols-12 gap-8 border-t border-[#C0C1BE]/30 pt-12">
                    <div className="md:col-span-4">
                        <h2 className="font-serif text-2xl text-[#2D3538] flex items-center gap-2">
                            <MessageSquare className="w-5 h-5 text-[#9D9F9F]" />
                            How They Respond
                        </h2>
                    </div>
                    <div className="md:col-span-8 grid grid-cols-1 md:grid-cols-2 gap-6">
                        {/* Tone */}
                        <div className="bg-white p-6 rounded-2xl border border-[#C0C1BE]/30 flex flex-col justify-between">
                            <h3 className="text-xs uppercase font-bold tracking-widest text-[#9D9F9F] mb-4">Tone & Vibe</h3>
                            <div className="flex flex-wrap gap-2">
                                {icp.psycholinguistics.tonePreference.map((t: string) => (
                                    <span key={t} className="px-3 py-1 bg-[#E9ECE6] text-[#2D3538] rounded-lg text-sm font-medium">
                                        {t}
                                    </span>
                                ))}
                                {icp.psycholinguistics.mindsetTraits.map((t: string) => (
                                    <span key={t} className="px-3 py-1 border border-[#C0C1BE] text-[#5B5F61] rounded-lg text-sm">
                                        {t}
                                    </span>
                                ))}
                            </div>
                        </div>
                        {/* Proof */}
                        <div className="bg-white p-6 rounded-2xl border border-[#C0C1BE]/30">
                            <h3 className="text-xs uppercase font-bold tracking-widest text-[#9D9F9F] mb-4">Proof Signals</h3>
                            <div className="space-y-2">
                                {icp.psycholinguistics.proofPreference.map((p: string) => (
                                    <div key={p} className="flex items-center gap-2 text-[#2D3538]">
                                        <ShieldCheck className="w-4 h-4 text-[#9D9F9F]" />
                                        <span className="capitalize">{p}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </section>

                {/* Section 4: Disqualifiers */}
                <section className="grid grid-cols-1 md:grid-cols-12 gap-8 border-t border-[#C0C1BE]/30 pt-12">
                    <div className="md:col-span-4">
                        <h2 className="font-serif text-2xl text-[#2D3538] flex items-center gap-2">
                            <Ban className="w-5 h-5 text-[#9D9F9F]" />
                            Disqualifiers
                        </h2>
                        <p className="text-sm text-[#5B5F61] mt-2">Explicit exclusions.</p>
                    </div>
                    <div className="md:col-span-8">
                        <div className="bg-red-50/30 p-6 rounded-2xl border border-red-100">
                            <div className="flex flex-wrap gap-2">
                                {[
                                    ...icp.disqualifiers.excludedCompanyTypes,
                                    ...icp.disqualifiers.excludedBehaviors,
                                    ...icp.disqualifiers.excludedGeographies
                                ].map((exc: string) => (
                                    <span key={exc} className="px-3 py-1 bg-white text-red-900 border border-red-100 rounded text-sm">
                                        {exc}
                                    </span>
                                ))}
                                {![...icp.disqualifiers.excludedCompanyTypes, ...icp.disqualifiers.excludedBehaviors].length && (
                                    <span className="text-gray-400 italic">No specific disqualifiers set.</span>
                                )}
                            </div>
                        </div>
                    </div>
                </section>

            </main>

            {/* Floating Prompt Input */}
            <div className="fixed bottom-0 inset-x-0 p-6 pointer-events-none">
                <div className="max-w-3xl mx-auto pointer-events-auto">
                    <form
                        onSubmit={handlePromptSubmit}
                        className="bg-white rounded-2xl shadow-xl border border-[#C0C1BE]/30 p-2 flex items-center gap-2"
                    >
                        <div className="w-10 h-10 rounded-xl bg-[#F3F4EE] flex items-center justify-center text-[#2D3538]">
                            <Sparkles className="w-5 h-5" />
                        </div>
                        <input
                            type="text"
                            value={prompt}
                            onChange={(e) => setPrompt(e.target.value)}
                            placeholder="Want to refine targeting? E.g. 'We are moving upmarket to Enterprise'"
                            className="flex-1 bg-transparent border-none focus:ring-0 text-[#2D3538] placeholder-[#9D9F9F] h-full py-2 px-2"
                        />
                        <button
                            type="submit"
                            disabled={!prompt.trim()}
                            className="bg-[#2D3538] text-white px-4 py-2 rounded-xl disabled:opacity-50 disabled:cursor-not-allowed hover:bg-black transition-colors"
                        >
                            <ArrowRight className="w-4 h-4" />
                        </button>
                    </form>
                </div>
            </div>

            {showProposal && mockProposal && (
                <ICPEvolutionProposal
                    currentIcp={icp}
                    proposedChanges={mockProposal}
                    impact={{
                        confidenceDelta: 0.05,
                        reason: prompt
                    }}
                    onAccept={handleAcceptProposal}
                    onReject={() => setShowProposal(false)}
                />
            )}
        </div>
    );
}
