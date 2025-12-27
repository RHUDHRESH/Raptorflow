'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowRight, ChevronRight, FileText, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet';

export interface ValueLabStep {
    id: string;
    label: string;
    description: string;
}

const VALUE_LAB_STEPS: ValueLabStep[] = [
    { id: 'intake', label: 'Review Inputs', description: 'Check what we extracted' },
    { id: 'jtbd', label: 'Customer Goal', description: 'What are they trying to achieve?' },
    { id: 'vpc-customer', label: 'Their World', description: 'Jobs, pains, and desires' },
    { id: 'vpc-solution', label: 'Your Solution', description: 'How you help them win' },
    { id: 'proof', label: 'Proof Library', description: 'Evidence for your claims' },
    { id: 'canvas', label: 'Competitive Edge', description: 'Where you stand out' },
    { id: 'errc', label: 'Strategic Moves', description: 'What to change to win' },
    { id: 'claims', label: 'Your Claims', description: 'Value propositions' },
    { id: 'offer', label: 'How You Deliver', description: 'Delivery model & timeline' },
    { id: 'review', label: 'Lock & Continue', description: 'Confirm and move on' },
];

interface EvidenceSnippet {
    source: string;
    quote: string;
}

interface ValueLabLandingProps {
    onStart: () => void;
    evidenceSnippets?: EvidenceSnippet[];
    completedSteps?: string[];
}

export function ValueLabLanding({
    onStart,
    evidenceSnippets = [],
    completedSteps = []
}: ValueLabLandingProps) {
    const router = useRouter();
    const [drawerOpen, setDrawerOpen] = useState(false);

    return (
        <div className="min-h-screen bg-[#F3F4EE] flex">
            {/* Left Rail - Stepper */}
            <aside className="w-[340px] flex-shrink-0 bg-[#0E1112] text-white p-8 flex flex-col">
                {/* Header */}
                <div className="mb-12">
                    <span className="text-[11px] font-mono uppercase tracking-[0.25em] text-white/30 block mb-2">
                        Phase 3
                    </span>
                    <h2 className="font-serif text-[32px] text-white tracking-tight leading-tight">
                        Value Lab
                    </h2>
                </div>

                {/* Steps */}
                <div className="flex-1 space-y-1 overflow-y-auto">
                    {VALUE_LAB_STEPS.map((step, index) => {
                        const isCompleted = completedSteps.includes(step.id);
                        return (
                            <div
                                key={step.id}
                                className={`flex items-start gap-4 py-3 px-4 rounded-xl transition-all ${isCompleted ? 'bg-white/5' : ''
                                    }`}
                            >
                                <div className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 text-[11px] font-mono ${isCompleted
                                    ? 'bg-white/20 text-white'
                                    : 'border border-white/20 text-white/40'
                                    }`}>
                                    {isCompleted ? <Check className="w-3.5 h-3.5" /> : index + 1}
                                </div>
                                <div className="flex-1 min-w-0">
                                    <span className={`text-sm block ${isCompleted ? 'text-white' : 'text-white/50'}`}>
                                        {step.label}
                                    </span>
                                    <span className="text-[11px] text-white/30 block truncate">
                                        {step.description}
                                    </span>
                                </div>
                            </div>
                        );
                    })}
                </div>

                {/* Back link */}
                <div className="pt-6 border-t border-white/10">
                    <button
                        onClick={() => router.push('/foundation')}
                        className="flex items-center gap-2 text-white/40 hover:text-white transition-colors text-sm"
                    >
                        <span>← Back to Foundation</span>
                    </button>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 flex items-center justify-center p-16">
                <div className="max-w-[560px] text-center">
                    {/* Phase Badge */}
                    <div className="inline-flex items-center gap-2 bg-[#2D3538]/5 rounded-full px-4 py-2 mb-8">
                        <span className="text-[11px] font-mono uppercase tracking-[0.15em] text-[#5B5F61]">
                            Phase 3 of 6
                        </span>
                    </div>

                    {/* Title */}
                    <h1 className="font-serif text-[52px] text-[#2D3538] tracking-[-0.02em] leading-[1.1] mb-6">
                        Value Lab
                    </h1>

                    {/* Subtitle */}
                    <p className="text-[18px] text-[#5B5F61] leading-relaxed mb-12 max-w-[480px] mx-auto">
                        Let's turn everything you've told us into a <span className="font-medium text-[#2D3538]">clear, provable value proposition</span>.
                        You'll define what makes you different and why customers should choose you.
                    </p>

                    {/* What you'll get */}
                    <div className="flex items-center justify-center gap-6 mb-12 text-[13px] text-[#5B5F61]">
                        <div className="flex items-center gap-2">
                            <span className="w-2 h-2 rounded-full bg-[#22C55E]" />
                            <span>Value proposition</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <span className="w-2 h-2 rounded-full bg-[#3B82F6]" />
                            <span>Competitive positioning</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <span className="w-2 h-2 rounded-full bg-[#F59E0B]" />
                            <span>Offer clarity</span>
                        </div>
                    </div>

                    {/* CTAs */}
                    <div className="flex items-center justify-center gap-4">
                        <Button
                            onClick={onStart}
                            className="bg-[#2D3538] hover:bg-[#1A1D1E] text-white px-10 py-7 rounded-2xl text-[16px] font-medium transition-all duration-200 hover:scale-[1.02] active:scale-[0.98] group"
                        >
                            Start Phase 3
                            <ArrowRight className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
                        </Button>

                        {/* View Extracted Notes */}
                        <Sheet open={drawerOpen} onOpenChange={setDrawerOpen}>
                            <SheetTrigger asChild>
                                <Button
                                    variant="ghost"
                                    className="text-[#5B5F61] hover:text-[#2D3538] hover:bg-[#2D3538]/5 px-6 py-7 rounded-2xl text-[15px]"
                                >
                                    <FileText className="mr-2 h-4 w-4" />
                                    View extracted notes
                                </Button>
                            </SheetTrigger>
                            <SheetContent className="w-[480px] bg-white border-l border-[#E5E6E3]">
                                <SheetHeader className="mb-8">
                                    <SheetTitle className="font-serif text-[24px] text-[#2D3538]">
                                        Extracted Notes
                                    </SheetTitle>
                                </SheetHeader>
                                <div className="space-y-6">
                                    {evidenceSnippets.length > 0 ? (
                                        evidenceSnippets.map((snippet, index) => (
                                            <div key={index} className="border-l-2 border-[#D7C9AE] pl-4">
                                                <p className="text-[14px] text-[#2D3538] leading-relaxed mb-2">
                                                    "{snippet.quote}"
                                                </p>
                                                <span className="text-[11px] font-mono uppercase tracking-[0.1em] text-[#9D9F9F]">
                                                    {snippet.source}
                                                </span>
                                            </div>
                                        ))
                                    ) : (
                                        <div className="text-center py-12">
                                            <p className="text-[#5B5F61] mb-2">No extracted notes yet.</p>
                                            <p className="text-[13px] text-[#9D9F9F]">
                                                Notes will be extracted from your uploads and links.
                                            </p>
                                        </div>
                                    )}
                                </div>
                            </SheetContent>
                        </Sheet>
                    </div>

                    {/* Time estimate */}
                    <p className="text-[13px] text-[#9D9F9F] mt-8">
                        Typically takes 10-15 minutes
                    </p>
                </div>
            </main>
        </div>
    );
}
