'use client';

import React from 'react';
import { Phase6Data } from '@/lib/foundation';
import { Lock, Download, Copy, Check, FileJson, FileText, Sparkles, AlertTriangle } from 'lucide-react';
import { toast } from 'sonner';

interface Props {
    phase6: Phase6Data;
    onLock: () => void;
    onExportJSON: () => void;
    onExportPDF: () => void;
}

export function FinalMessagingKit({ phase6, onLock, onExportJSON, onExportPDF }: Props) {
    const copyAll = () => {
        const content = `
# Messaging Kit

## Controlling Idea
${phase6.blueprint?.controllingIdea || 'Not set'}

## 7 Precision Soundbites
${phase6.signal7Soundbites?.map((s, i) => `${i + 1}. [${s.type}] ${s.text}`).join('\n') || 'Not generated'}

## Website Hero
Headline: ${phase6.websiteHero?.headline || 'Not set'}
Subhead: ${phase6.websiteHero?.subhead || 'Not set'}
CTA: ${phase6.websiteHero?.cta || 'Not set'}

## Objection Killers
${phase6.objectionKillers?.map(o => `Q: ${o.objection}\nA: ${o.rebuttal}`).join('\n\n') || 'Not set'}
        `.trim();

        navigator.clipboard.writeText(content);
        toast.success('Full Messaging Kit copied!');
    };

    const proofGaps = phase6.proofSlots?.filter(s => s.status === 'red').length || 0;
    const isReady = proofGaps === 0 && (phase6.qaReport?.sevenSecondTestPass ?? true);

    return (
        <div className="space-y-6">
            {/* Summary Header */}
            <div className={`rounded-3xl p-8 ${isReady ? 'bg-[#2D3538]' : 'bg-amber-500'}`}>
                <div className="flex items-center gap-4 mb-4">
                    {isReady ? (
                        <Sparkles className="w-8 h-8 text-white" />
                    ) : (
                        <AlertTriangle className="w-8 h-8 text-white" />
                    )}
                    <h2 className="font-serif text-[28px] text-white">
                        {isReady ? 'Your Messaging Kit is Ready' : 'Almost There'}
                    </h2>
                </div>
                <p className="text-white/70 text-lg max-w-xl mb-6">
                    {isReady
                        ? '10 deployable assets, ready to paste anywhere.'
                        : `${proofGaps} soundbites need proof before locking.`
                    }
                </p>

                {/* Quick Stats */}
                <div className="flex gap-6 text-white/80 text-sm">
                    <span>✓ 7 Soundbites</span>
                    <span>✓ 5 Channel Packs</span>
                    <span>✓ {phase6.objectionKillers?.length || 3} Objection Killers</span>
                    <span>✓ Voice Rules</span>
                </div>
            </div>

            {/* Controlling Idea */}
            <div className="bg-white border border-[#E5E6E3] rounded-2xl p-6">
                <span className="text-[11px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F] block mb-3">
                    Controlling Idea
                </span>
                <p className="font-serif text-xl text-[#2D3538]">
                    "{phase6.blueprint?.controllingIdea || 'Marketing. Finally under control.'}"
                </p>
            </div>

            {/* 7 Soundbites Summary */}
            <div className="bg-white border border-[#E5E6E3] rounded-2xl p-6">
                <span className="text-[11px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F] block mb-4">
                    7 Precision Soundbites
                </span>
                <div className="space-y-3">
                    {phase6.signal7Soundbites?.slice(0, 7).map((sb, i) => (
                        <div key={sb.id} className="flex items-start gap-3">
                            <span className="w-6 h-6 bg-[#F3F4EE] rounded-lg flex items-center justify-center text-xs font-mono text-[#5B5F61]">
                                {i + 1}
                            </span>
                            <div className="flex-1">
                                <span className="text-[10px] font-mono uppercase text-[#9D9F9F]">
                                    {sb.type.replace(/-/g, ' ')}
                                </span>
                                <p className="text-sm text-[#2D3538]">{sb.text}</p>
                            </div>
                            {phase6.proofSlots?.find(p => p.soundbiteId === sb.id)?.status === 'red' && (
                                <span className="px-2 py-0.5 bg-red-100 text-red-700 text-[10px] rounded-full">
                                    Needs proof
                                </span>
                            )}
                        </div>
                    ))}
                </div>
            </div>

            {/* Objection Killers */}
            <div className="bg-white border border-[#E5E6E3] rounded-2xl p-6">
                <span className="text-[11px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F] block mb-4">
                    Objection Killers
                </span>
                <div className="space-y-4">
                    {phase6.objectionKillers?.map(obj => (
                        <div key={obj.id} className="bg-[#FAFAF8] rounded-xl p-4">
                            <p className="text-sm text-[#5B5F61] mb-2">
                                <strong>Objection:</strong> {obj.objection}
                            </p>
                            <p className="text-sm text-[#2D3538]">
                                <strong>Response:</strong> {obj.rebuttal}
                            </p>
                        </div>
                    ))}
                </div>
            </div>

            {/* Proof Gaps Warning */}
            {proofGaps > 0 && (
                <div className="bg-amber-50 border border-amber-200 rounded-2xl p-6">
                    <div className="flex items-center gap-3 mb-2">
                        <AlertTriangle className="w-5 h-5 text-amber-600" />
                        <span className="font-medium text-amber-700">Proof Gaps</span>
                    </div>
                    <p className="text-sm text-amber-700">
                        {proofGaps} soundbite{proofGaps !== 1 ? 's' : ''} marked as "unproven".
                        Consider adding evidence before locking.
                    </p>
                </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-3">
                <button
                    onClick={onLock}
                    className={`flex-1 flex items-center justify-center gap-3 py-5 rounded-2xl font-medium transition-all ${isReady
                            ? 'bg-[#2D3538] text-white hover:bg-[#1A1D1E]'
                            : 'bg-amber-500 text-white hover:bg-amber-600'
                        }`}
                >
                    <Lock className="w-5 h-5" />
                    Lock as Source of Truth
                </button>
            </div>

            <div className="flex gap-3">
                <button
                    onClick={onExportJSON}
                    className="flex-1 flex items-center justify-center gap-2 py-3 bg-white border border-[#E5E6E3] rounded-xl text-[#5B5F61] hover:border-[#2D3538] transition-colors"
                >
                    <FileJson className="w-4 h-4" />
                    Export JSON
                </button>
                <button
                    onClick={onExportPDF}
                    className="flex-1 flex items-center justify-center gap-2 py-3 bg-white border border-[#E5E6E3] rounded-xl text-[#5B5F61] hover:border-[#2D3538] transition-colors"
                >
                    <FileText className="w-4 h-4" />
                    Export PDF
                </button>
                <button
                    onClick={copyAll}
                    className="flex-1 flex items-center justify-center gap-2 py-3 bg-white border border-[#E5E6E3] rounded-xl text-[#5B5F61] hover:border-[#2D3538] transition-colors"
                >
                    <Copy className="w-4 h-4" />
                    Copy All
                </button>
            </div>
        </div>
    );
}
