'use client';

import React from 'react';
import { AwarenessStageContent, AwarenessStage } from '@/lib/foundation';
import { Eye, Check, MessageCircle, Ban, Lightbulb } from 'lucide-react';

interface Props {
    ladder: AwarenessStageContent[];
    onUpdate: (ladder: AwarenessStageContent[]) => void;
}

const STAGE_LABELS: Record<AwarenessStage, string> = {
    'unaware': 'Unaware',
    'problem': 'Problem-Aware',
    'solution': 'Solution-Aware',
    'product': 'Product-Aware',
    'most': 'Most Aware'
};

const STAGE_COLORS: Record<AwarenessStage, string> = {
    'unaware': 'border-l-red-400',
    'problem': 'border-l-amber-400',
    'solution': 'border-l-blue-400',
    'product': 'border-l-purple-400',
    'most': 'border-l-green-400'
};

export function AwarenessLadderTuner({ ladder, onUpdate }: Props) {
    if (!ladder || ladder.length === 0) {
        return (
            <div className="flex items-center justify-center h-64 bg-[#FAFAF8] rounded-2xl">
                <p className="text-[#9D9F9F]">Loading awareness ladder...</p>
            </div>
        );
    }

    const toggleFocus = (stage: AwarenessStage) => {
        const updated = ladder.map(s =>
            s.stage === stage ? { ...s, isFocused: !s.isFocused } : s
        );
        onUpdate(updated);
    };

    const updateField = (stage: AwarenessStage, field: keyof AwarenessStageContent, value: string) => {
        const updated = ladder.map(s =>
            s.stage === stage ? { ...s, [field]: value } : s
        );
        onUpdate(updated);
    };

    const focusedCount = ladder.filter(s => s.isFocused).length;

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="bg-[#FAFAF8] border border-[#E5E6E3] rounded-2xl p-6">
                <div className="flex items-center gap-3 mb-2">
                    <Eye className="w-5 h-5 text-[#2D3538]" />
                    <h3 className="font-medium text-[#2D3538]">Awareness Ladder</h3>
                </div>
                <p className="text-sm text-[#5B5F61]">
                    Same product, different mental states. Pick 2 stages to focus on first.
                    Your messaging should adapt to where they are in their journey.
                </p>
                <div className="mt-3 flex items-center gap-2">
                    <span className={`text-xs font-mono ${focusedCount >= 2 ? 'text-[#2D3538]' : 'text-[#9D9F9F]'}`}>
                        {focusedCount}/2 stages selected
                    </span>
                    {focusedCount >= 2 && <Check className="w-4 h-4 text-[#2D3538]" />}
                </div>
            </div>

            {/* Ladder Steps */}
            <div className="space-y-3">
                {ladder.map((stageContent, index) => (
                    <div
                        key={stageContent.stage}
                        className={`bg-white border-l-4 ${STAGE_COLORS[stageContent.stage]} border border-[#E5E6E3] rounded-xl overflow-hidden transition-all ${stageContent.isFocused ? 'ring-2 ring-[#2D3538]/20' : ''
                            }`}
                    >
                        {/* Header */}
                        <button
                            onClick={() => toggleFocus(stageContent.stage)}
                            className="w-full flex items-center justify-between p-4 hover:bg-[#FAFAF8] transition-colors"
                        >
                            <div className="flex items-center gap-4">
                                <div className={`w-8 h-8 rounded-lg flex items-center justify-center text-sm font-mono ${stageContent.isFocused
                                        ? 'bg-[#2D3538] text-white'
                                        : 'bg-[#F3F4EE] text-[#5B5F61]'
                                    }`}>
                                    {index + 1}
                                </div>
                                <span className="font-medium text-[#2D3538]">
                                    {STAGE_LABELS[stageContent.stage]}
                                </span>
                            </div>
                            <div className={`px-3 py-1 rounded-full text-xs ${stageContent.isFocused
                                    ? 'bg-[#2D3538] text-white'
                                    : 'bg-[#F3F4EE] text-[#5B5F61]'
                                }`}>
                                {stageContent.isFocused ? 'Focused' : 'Click to focus'}
                            </div>
                        </button>

                        {/* Content */}
                        <div className={`grid grid-cols-3 gap-4 px-4 pb-4 ${stageContent.isFocused ? '' : 'opacity-60'
                            }`}>
                            {/* What they're thinking */}
                            <div className="space-y-2">
                                <div className="flex items-center gap-2">
                                    <Lightbulb className="w-3 h-3 text-[#9D9F9F]" />
                                    <span className="text-[10px] font-mono uppercase text-[#9D9F9F]">
                                        What They Think
                                    </span>
                                </div>
                                <input
                                    type="text"
                                    value={stageContent.whatTheyThinking}
                                    onChange={e => updateField(stageContent.stage, 'whatTheyThinking', e.target.value)}
                                    className="w-full px-3 py-2 bg-[#FAFAF8] border border-[#E5E6E3] rounded-lg text-sm text-[#2D3538] focus:outline-none focus:ring-1 focus:ring-[#2D3538]/20"
                                />
                            </div>

                            {/* What to say */}
                            <div className="space-y-2">
                                <div className="flex items-center gap-2">
                                    <MessageCircle className="w-3 h-3 text-green-500" />
                                    <span className="text-[10px] font-mono uppercase text-[#9D9F9F]">
                                        What to Say
                                    </span>
                                </div>
                                <input
                                    type="text"
                                    value={stageContent.whatToSay}
                                    onChange={e => updateField(stageContent.stage, 'whatToSay', e.target.value)}
                                    className="w-full px-3 py-2 bg-[#FAFAF8] border border-[#E5E6E3] rounded-lg text-sm text-[#2D3538] focus:outline-none focus:ring-1 focus:ring-[#2D3538]/20"
                                />
                            </div>

                            {/* What not to say */}
                            <div className="space-y-2">
                                <div className="flex items-center gap-2">
                                    <Ban className="w-3 h-3 text-red-400" />
                                    <span className="text-[10px] font-mono uppercase text-[#9D9F9F]">
                                        What NOT to Say
                                    </span>
                                </div>
                                <input
                                    type="text"
                                    value={stageContent.whatNotToSay}
                                    onChange={e => updateField(stageContent.stage, 'whatNotToSay', e.target.value)}
                                    className="w-full px-3 py-2 bg-[#FAFAF8] border border-[#E5E6E3] rounded-lg text-sm text-[#2D3538] focus:outline-none focus:ring-1 focus:ring-[#2D3538]/20"
                                />
                            </div>

                            {/* Sample line - full width */}
                            <div className="col-span-3 bg-[#2D3538] rounded-xl p-4">
                                <span className="text-[10px] font-mono uppercase text-white/50 block mb-2">
                                    Sample Line
                                </span>
                                <p className="text-white text-sm">
                                    "{stageContent.sampleLine}"
                                </p>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
