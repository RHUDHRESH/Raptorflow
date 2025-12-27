'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Playfair_Display } from 'next/font/google';
import { Sparkles, Check, Edit3, RotateCcw, AlertCircle, Lock, ArrowRight, Zap, Quote, Shield, Target, Award, Clock } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Soundbite, SoundbiteType } from '@/lib/foundation';

const playfair = Playfair_Display({ subsets: ['latin'] });

interface SoundbiteStudioProps {
    soundbites: Soundbite[];
    onGenerate: () => Promise<void>;
    onUpdate: (id: string, text: string) => void;
    onLock: (id: string) => void;
    onSelectVariation: (id: string, text: string) => void;
    isGenerating: boolean;
}

const TYPE_CONFIG: Partial<Record<SoundbiteType, { label: string; icon: React.ReactNode; strategy: string }>> = {
    'problem-reveal': {
        label: '01 / Problem Revelation',
        icon: <Zap className="w-4 h-4" />,
        strategy: 'Hook the unaware with specific, unstated pain.'
    },
    'agitate': {
        label: '02 / Agitation',
        icon: <AlertCircle className="w-4 h-4" />,
        strategy: 'Amplify the emotional consequence of inaction.'
    },
    'mechanism': {
        label: '03 / Mechanism',
        icon: <RotateCcw className="w-4 h-4" />,
        strategy: 'Explain your unique logic that solves the problem.'
    },
    'objection-kill': {
        label: '04 / Objection Handling',
        icon: <Shield className="w-4 h-4" />,
        strategy: 'Address skepticism with proof and logic.'
    },
    'transformation': {
        label: '05 / Transformation',
        icon: <Target className="w-4 h-4" />,
        strategy: 'Paint the happy ending with a specific timeframe.'
    },
    'positioning': {
        label: '06 / Positioning',
        icon: <Award className="w-4 h-4" />,
        strategy: 'Status-based positioning. Who uses you?'
    },
    'urgency': {
        label: '07 / Urgency',
        icon: <Clock className="w-4 h-4" />,
        strategy: 'Authentic scarcity and a clear next step.'
    },
};

function VariationCard({ text, isSelected, onSelect }: { text: string; isSelected: boolean; onSelect: () => void }) {
    return (
        <button
            onClick={onSelect}
            className={cn(
                "p-6 rounded-xl border-2 text-left transition-all duration-300 relative group",
                isSelected
                    ? "bg-[#2D3538] text-white border-[#2D3538] shadow-lg scale-[1.02]"
                    : "bg-white text-[#2D3538] border-[#C0C1BE] hover:border-[#2D3538] opacity-60 hover:opacity-100"
            )}
        >
            <div className="flex justify-between items-start mb-4">
                <span className={cn(
                    "text-[10px] font-mono uppercase tracking-widest",
                    isSelected ? "text-white/40" : "opacity-40"
                )}>
                    AI Variation
                </span>
                {isSelected && <Check className="w-4 h-4 text-emerald-400" />}
            </div>
            <p className="text-[15px] font-serif italic leading-relaxed">"{text}"</p>
        </button>
    );
}

export function SoundbiteStudio({ soundbites, onGenerate, onUpdate, onLock, onSelectVariation, isGenerating }: SoundbiteStudioProps) {
    const [editingId, setEditingId] = useState<string | null>(null);
    const [viewingVariationsId, setViewingVariationsId] = useState<string | null>(null);

    // Sequential unlocking logic
    const isUnlocked = (index: number) => {
        if (index === 0) return true;
        // Check if the previous soundbite is locked
        return soundbites[index - 1]?.isLocked;
    };

    return (
        <div className="space-y-12 py-4">
            {/* Engine Header */}
            <div className="flex justify-between items-center bg-[#2D3538] text-white p-10 rounded-2xl shadow-2xl relative overflow-hidden">
                {/* Visual texture */}
                <div className="absolute inset-0 opacity-[0.03] pointer-events-none">
                    <Zap className="w-full h-full -rotate-12 scale-150" />
                </div>

                <div className="flex items-center gap-8 relative z-10">
                    <div className="w-16 h-16 rounded-full bg-white/10 flex items-center justify-center relative">
                        <Sparkles className={cn("w-8 h-8", isGenerating && "animate-pulse")} />
                        {isGenerating && (
                            <motion.div
                                className="absolute inset-0 border-2 border-white rounded-full"
                                animate={{ scale: [1, 1.3, 1], opacity: [1, 0, 1] }}
                                transition={{ duration: 2, repeat: Infinity }}
                            />
                        )}
                    </div>
                    <div>
                        <h3 className={`${playfair.className} text-3xl mb-1`}>Precision Synthesis Studio</h3>
                        <p className="text-white/40 text-xs font-mono uppercase tracking-widest">Forging your final 7 resonance vectors</p>
                    </div>
                </div>
                <button
                    onClick={onGenerate}
                    disabled={isGenerating}
                    className="flex items-center gap-3 bg-white text-[#2D3538] px-10 py-5 rounded-xl font-bold hover:bg-white/90 transition-all disabled:opacity-20 relative z-10"
                >
                    {soundbites.length > 0 ? 'Regenerate Pipeline' : 'Start Synthesis'}
                    <Zap className="w-4 h-4" />
                </button>
            </div>

            {/* Studio Grid */}
            <div className="grid grid-cols-1 gap-8">
                {soundbites.length === 0 && !isGenerating && (
                    <div className="py-32 text-center border-2 border-dashed border-[#C0C1BE] rounded-3xl opacity-30 flex flex-col items-center gap-6">
                        <Zap className="w-12 h-12" />
                        <div className="space-y-2">
                            <p className={`${playfair.className} text-2xl`}>Engine Standby</p>
                            <span className="text-[10px] font-mono uppercase tracking-widest">Required: Phase 03 - 05 Completion</span>
                        </div>
                    </div>
                )}

                {soundbites.map((sb, idx) => {
                    const config = TYPE_CONFIG[sb.type as SoundbiteType] || {
                        label: sb.type,
                        icon: <Zap className="w-4 h-4" />,
                        strategy: 'Strategy pending...'
                    };
                    const isEditing = editingId === sb.id;
                    const unlocked = isUnlocked(idx);
                    const showVariations = viewingVariationsId === sb.id;

                    return (
                        <div
                            key={sb.id}
                            className={cn(
                                "group border rounded-3xl transition-all duration-700 overflow-hidden",
                                !unlocked ? "opacity-20 grayscale pointer-events-none" : "",
                                sb.isLocked
                                    ? "bg-[#F3F4EE]/50 border-[#C0C1BE]"
                                    : "bg-white border-[#C0C1BE] hover:border-[#2D3538] shadow-lg"
                            )}
                        >
                            <div className="flex items-stretch min-h-[160px]">
                                {/* Type Sidebar */}
                                <div className={cn(
                                    "w-20 flex flex-col items-center justify-center border-r transition-colors",
                                    sb.isLocked ? "border-[#C0C1BE] bg-white/50" : "border-[#C0C1BE] bg-[#F3F4EE]/30"
                                )}>
                                    <div className={cn(
                                        "transition-all duration-500",
                                        sb.isLocked ? "text-emerald-600 scale-110" : "opacity-40"
                                    )}>
                                        {sb.isLocked ? <Check className="w-6 h-6" /> : config.icon}
                                    </div>
                                </div>

                                {/* Content Area */}
                                <div className="flex-1 p-10 flex flex-col justify-center">
                                    <div className="flex justify-between items-start mb-6">
                                        <div className="space-y-1">
                                            <div className="flex items-center gap-3">
                                                <span className="text-[11px] font-mono uppercase tracking-[0.3em] opacity-40 font-bold">{config.label}</span>
                                                {sb.isLocked && (
                                                    <span className="text-[9px] font-mono uppercase bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded-full">Validated</span>
                                                )}
                                            </div>
                                            <p className="text-[12px] text-[#5B5F61] italic">{config.strategy}</p>
                                        </div>
                                        <div className="flex gap-3">
                                            {!sb.isLocked && (
                                                <>
                                                    <button
                                                        onClick={() => setViewingVariationsId(showVariations ? null : sb.id)}
                                                        className="p-2.5 rounded-xl hover:bg-[#F3F4EE] opacity-20 group-hover:opacity-100 transition-all"
                                                        title="Compare Variations"
                                                    >
                                                        <RotateCcw className="w-4 h-4" />
                                                    </button>
                                                    <button
                                                        onClick={() => setEditingId(isEditing ? null : sb.id)}
                                                        className="p-2.5 rounded-xl hover:bg-[#F3F4EE] opacity-20 group-hover:opacity-100 transition-all"
                                                        title="Manual Refine"
                                                    >
                                                        <Edit3 className="w-4 h-4" />
                                                    </button>
                                                </>
                                            )}
                                            <button
                                                onClick={() => onLock(sb.id)}
                                                className={cn(
                                                    "p-2.5 rounded-xl transition-all",
                                                    sb.isLocked
                                                        ? "text-emerald-600 bg-emerald-50"
                                                        : "opacity-20 group-hover:opacity-100 hover:bg-[#F3F4EE]"
                                                )}
                                            >
                                                {sb.isLocked ? <Check className="w-4 h-4" /> : <Lock className="w-4 h-4" />}
                                            </button>
                                        </div>
                                    </div>

                                    <AnimatePresence mode="wait">
                                        {showVariations ? (
                                            <motion.div
                                                initial={{ opacity: 0, y: 10 }}
                                                animate={{ opacity: 1, y: 0 }}
                                                exit={{ opacity: 0, y: -10 }}
                                                className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4"
                                            >
                                                <VariationCard
                                                    text={sb.text}
                                                    isSelected={true}
                                                    onSelect={() => { }}
                                                />
                                                {(sb.alternatives || []).map((alt, i) => (
                                                    <VariationCard
                                                        key={i}
                                                        text={alt}
                                                        isSelected={false}
                                                        onSelect={() => {
                                                            onSelectVariation(sb.id, alt);
                                                            setViewingVariationsId(null);
                                                        }}
                                                    />
                                                ))}
                                            </motion.div>
                                        ) : isEditing ? (
                                            <motion.textarea
                                                initial={{ opacity: 0 }}
                                                animate={{ opacity: 1 }}
                                                autoFocus
                                                value={sb.text}
                                                onChange={(e) => onUpdate(sb.id, e.target.value)}
                                                className="w-full bg-transparent border-none outline-none text-xl font-serif italic text-[#2D3538] leading-relaxed resize-none p-0 focus:ring-0"
                                                rows={2}
                                            />
                                        ) : (
                                            <motion.p
                                                initial={{ opacity: 0 }}
                                                animate={{ opacity: 1 }}
                                                className={cn(
                                                    "text-xl font-serif italic leading-relaxed",
                                                    sb.isLocked ? "text-[#2D3538]/60" : "text-[#2D3538]"
                                                )}
                                            >
                                                "{sb.text}"
                                            </motion.p>
                                        )}
                                    </AnimatePresence>
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
