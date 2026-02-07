'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Playfair_Display } from 'next/font/google';
import { ArrowLeft, ArrowRight } from 'lucide-react';
import { useRouter } from 'next/navigation';

const playfair = Playfair_Display({ subsets: ['latin'] });

interface OnboardingScaffoldProps {
    phase: 3 | 4 | 5 | 6;
    title: string;
    subtitle: string;
    children: React.ReactNode;
    onBack?: () => void;
    onContinue?: () => void;
    isLoading?: boolean;
    isSaving?: boolean;
}

export function OnboardingScaffold({
    phase,
    title,
    subtitle,
    children,
    onBack,
    onContinue,
    isLoading = false,
    isSaving = false,
}: OnboardingScaffoldProps) {
    const router = useRouter();

    const phases = [
        { id: 3, label: 'Foundation' },
        { id: 4, label: 'Agitation' },
        { id: 5, label: 'Mechanism' },
        { id: 6, label: 'Soundbites' },
    ];

    return (
        <div className="min-h-screen bg-[#F3F4EE] text-[#2D3538] flex flex-col font-sans">
            {/* Minimal Header */}
            <header className="h-20 border-b border-[#C0C1BE] flex items-center justify-between px-8 bg-white/50 backdrop-blur-md sticky top-0 z-50">
                <div className="flex items-center gap-4">
                    <div className="w-8 h-8 bg-[#2D3538] rounded flex items-center justify-center">
                        <span className="text-white font-serif font-bold text-lg italic">R</span>
                    </div>
                    <span className="font-mono text-xs tracking-widest uppercase opacity-50">
                        RaptorFlow / Precision 3.0
                    </span>
                </div>

                <nav className="flex gap-8 items-center">
                    {phases.map((p) => (
                        <div
                            key={p.id}
                            className={`flex flex-col items-center gap-1 transition-opacity ${
                                phase === p.id ? 'opacity-100' : 'opacity-30'
                            }`}
                        >
                            <span className="text-[10px] font-mono uppercase tracking-tighter">
                                Phase 0{p.id}
                            </span>
                            <span className="text-xs font-medium">{p.label}</span>
                            {phase === p.id && (
                                <motion.div
                                    layoutId="activePhase"
                                    className="h-0.5 w-full bg-[#2D3538] rounded-full"
                                />
                            )}
                        </div>
                    ))}
                </nav>

                <div className="w-32 flex justify-end">
                    {isSaving && (
                        <span className="text-[10px] font-mono uppercase animate-pulse">
                            Syncing...
                        </span>
                    )}
                </div>
            </header>

            <main className="flex-1 max-w-5xl w-full mx-auto px-8 py-16">
                <AnimatePresence mode="wait">
                    <motion.div
                        key={phase}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
                    >
                        {/* Page Header */}
                        <div className="mb-16 text-center">
                            <h1 className={`${playfair.className} text-[56px] leading-tight mb-4 tracking-tight`}>
                                {title}
                            </h1>
                            <p className="text-[18px] text-[#5B5F61] max-w-2xl mx-auto leading-relaxed">
                                {subtitle}
                            </p>
                        </div>

                        {/* Content Area */}
                        <div className="bg-white border border-[#C0C1BE] rounded-[16px] p-12 shadow-sm min-h-[400px] flex flex-col">
                            {isLoading ? (
                                <div className="flex-1 flex items-center justify-center">
                                    <div className="w-12 h-12 border-2 border-[#2D3538] border-t-transparent rounded-full animate-spin" />
                                </div>
                            ) : (
                                children
                            )}
                        </div>

                        {/* Navigation Footer */}
                        {!isLoading && (
                            <div className="mt-12 flex justify-between items-center">
                                <button
                                    onClick={onBack || (() => router.back())}
                                    className="flex items-center gap-2 text-sm font-medium hover:opacity-60 transition-opacity"
                                >
                                    <ArrowLeft className="w-4 h-4" />
                                    <span>Back</span>
                                </button>

                                <button
                                    onClick={onContinue}
                                    disabled={isSaving}
                                    className="bg-[#2D3538] text-white px-10 py-4 rounded-[14px] flex items-center gap-3 hover:bg-[#1A1D1E] transition-all disabled:opacity-50 group"
                                >
                                    <span className="font-medium">Continue to Phase 0{phase + 1}</span>
                                    <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
                                </button>
                            </div>
                        )}
                    </motion.div>
                </AnimatePresence>
            </main>

            <footer className="py-8 border-t border-[#C0C1BE] mt-auto">
                <div className="max-w-5xl mx-auto px-8 flex justify-between items-center text-[11px] font-mono uppercase tracking-widest text-[#9D9F9F]">
                    <span>Last Updated: {new Date().toLocaleDateString()}</span>
                    <span>Confidence: High</span>
                </div>
            </footer>
        </div>
    );
}
