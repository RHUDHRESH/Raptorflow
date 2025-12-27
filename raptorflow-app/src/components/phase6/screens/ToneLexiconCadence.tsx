'use client';

import React from 'react';
import { VoiceSpec, ToneDial, CadenceStyle } from '@/lib/foundation';
import { Mic, Plus, X, Volume2 } from 'lucide-react';

interface Props {
    voiceSpec: VoiceSpec | undefined;
    onUpdate: (spec: VoiceSpec) => void;
}

const TONE_OPTIONS: { value: ToneDial; label: string; description: string }[] = [
    { value: 'clinical', label: 'Clinical', description: 'Precise, data-driven, no fluff' },
    { value: 'confident', label: 'Confident', description: 'Assured but not arrogant' },
    { value: 'bold', label: 'Bold', description: 'Strong claims, direct language' },
    { value: 'provocative', label: 'Provocative', description: 'Challenge assumptions, contrarian' }
];

const CADENCE_OPTIONS: { value: CadenceStyle; label: string; example: string }[] = [
    { value: 'short', label: 'Short', example: 'Stop guessing. Start executing.' },
    { value: 'medium', label: 'Medium', example: 'You deserve a marketing system that actually works.' },
    { value: 'punchy', label: 'Punchy', example: 'Marketing. Finally under control. No more chaos. Just clarity.' }
];

export function ToneLexiconCadence({ voiceSpec, onUpdate }: Props) {
    if (!voiceSpec) {
        return (
            <div className="flex items-center justify-center h-64 bg-[#FAFAF8] rounded-2xl">
                <p className="text-[#9D9F9F]">Loading voice spec...</p>
            </div>
        );
    }

    const addWord = (list: 'alwaysUse' | 'neverUse', word: string) => {
        if (!word.trim()) return;
        const updated = [...voiceSpec[list], word.trim()];
        onUpdate({ ...voiceSpec, [list]: updated });
    };

    const removeWord = (list: 'alwaysUse' | 'neverUse', index: number) => {
        const updated = voiceSpec[list].filter((_, i) => i !== index);
        onUpdate({ ...voiceSpec, [list]: updated });
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="bg-[#FAFAF8] border border-[#E5E6E3] rounded-2xl p-6">
                <div className="flex items-center gap-3 mb-2">
                    <Volume2 className="w-5 h-5 text-[#2D3538]" />
                    <h3 className="font-medium text-[#2D3538]">Tone, Lexicon & Cadence</h3>
                </div>
                <p className="text-sm text-[#5B5F61]">
                    This is how you stop sounding generic. Define your voice rules.
                </p>
            </div>

            {/* Tone Dial */}
            <div className="bg-white border border-[#E5E6E3] rounded-2xl p-6">
                <span className="text-[11px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F] block mb-4">
                    Tone Dial
                </span>
                <div className="grid grid-cols-4 gap-3">
                    {TONE_OPTIONS.map(tone => (
                        <button
                            key={tone.value}
                            onClick={() => onUpdate({ ...voiceSpec, toneDial: tone.value })}
                            className={`text-left p-4 rounded-xl border transition-all ${voiceSpec.toneDial === tone.value
                                    ? 'bg-[#2D3538] border-[#2D3538] text-white'
                                    : 'bg-white border-[#E5E6E3] hover:border-[#2D3538]'
                                }`}
                        >
                            <div className={`font-medium text-sm mb-1 ${voiceSpec.toneDial === tone.value ? 'text-white' : 'text-[#2D3538]'
                                }`}>
                                {tone.label}
                            </div>
                            <div className={`text-xs ${voiceSpec.toneDial === tone.value ? 'text-white/70' : 'text-[#9D9F9F]'
                                }`}>
                                {tone.description}
                            </div>
                        </button>
                    ))}
                </div>
            </div>

            {/* Lexicon Rules */}
            <div className="grid grid-cols-2 gap-4">
                {/* Always Use */}
                <div className="bg-white border border-[#E5E6E3] rounded-2xl p-6">
                    <span className="text-[11px] font-mono uppercase tracking-[0.15em] text-green-600 block mb-4">
                        We Say ✓
                    </span>
                    <div className="flex flex-wrap gap-2 mb-4">
                        {voiceSpec.alwaysUse.map((word, i) => (
                            <span
                                key={i}
                                className="flex items-center gap-1 px-3 py-1.5 bg-green-50 border border-green-200 rounded-lg text-sm text-green-700"
                            >
                                {word}
                                <button onClick={() => removeWord('alwaysUse', i)} className="hover:bg-green-100 rounded p-0.5">
                                    <X className="w-3 h-3" />
                                </button>
                            </span>
                        ))}
                    </div>
                    <div className="flex gap-2">
                        <input
                            type="text"
                            placeholder="Add word..."
                            className="flex-1 px-3 py-2 bg-[#FAFAF8] border border-[#E5E6E3] rounded-lg text-sm focus:outline-none focus:ring-1 focus:ring-green-500/20"
                            onKeyDown={e => {
                                if (e.key === 'Enter') {
                                    addWord('alwaysUse', (e.target as HTMLInputElement).value);
                                    (e.target as HTMLInputElement).value = '';
                                }
                            }}
                        />
                        <button
                            onClick={() => {
                                const input = document.querySelector('input[placeholder="Add word..."]') as HTMLInputElement;
                                if (input) {
                                    addWord('alwaysUse', input.value);
                                    input.value = '';
                                }
                            }}
                            className="p-2 bg-green-50 border border-green-200 rounded-lg hover:bg-green-100 transition-colors"
                        >
                            <Plus className="w-4 h-4 text-green-600" />
                        </button>
                    </div>
                </div>

                {/* Never Use */}
                <div className="bg-white border border-[#E5E6E3] rounded-2xl p-6">
                    <span className="text-[11px] font-mono uppercase tracking-[0.15em] text-red-600 block mb-4">
                        We Never Say ✗
                    </span>
                    <div className="flex flex-wrap gap-2 mb-4">
                        {voiceSpec.neverUse.map((word, i) => (
                            <span
                                key={i}
                                className="flex items-center gap-1 px-3 py-1.5 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700"
                            >
                                {word}
                                <button onClick={() => removeWord('neverUse', i)} className="hover:bg-red-100 rounded p-0.5">
                                    <X className="w-3 h-3" />
                                </button>
                            </span>
                        ))}
                    </div>
                    <div className="flex gap-2">
                        <input
                            type="text"
                            placeholder="Add banned word..."
                            className="flex-1 px-3 py-2 bg-[#FAFAF8] border border-[#E5E6E3] rounded-lg text-sm focus:outline-none focus:ring-1 focus:ring-red-500/20"
                            onKeyDown={e => {
                                if (e.key === 'Enter') {
                                    addWord('neverUse', (e.target as HTMLInputElement).value);
                                    (e.target as HTMLInputElement).value = '';
                                }
                            }}
                        />
                        <button
                            onClick={() => {
                                const input = document.querySelector('input[placeholder="Add banned word..."]') as HTMLInputElement;
                                if (input) {
                                    addWord('neverUse', input.value);
                                    input.value = '';
                                }
                            }}
                            className="p-2 bg-red-50 border border-red-200 rounded-lg hover:bg-red-100 transition-colors"
                        >
                            <Plus className="w-4 h-4 text-red-600" />
                        </button>
                    </div>
                </div>
            </div>

            {/* Cadence */}
            <div className="bg-white border border-[#E5E6E3] rounded-2xl p-6">
                <span className="text-[11px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F] block mb-4">
                    Sentence Cadence
                </span>
                <div className="grid grid-cols-3 gap-3">
                    {CADENCE_OPTIONS.map(cadence => (
                        <button
                            key={cadence.value}
                            onClick={() => onUpdate({ ...voiceSpec, cadenceStyle: cadence.value })}
                            className={`text-left p-4 rounded-xl border transition-all ${voiceSpec.cadenceStyle === cadence.value
                                    ? 'bg-[#2D3538] border-[#2D3538]'
                                    : 'bg-white border-[#E5E6E3] hover:border-[#2D3538]'
                                }`}
                        >
                            <div className={`font-medium text-sm mb-2 ${voiceSpec.cadenceStyle === cadence.value ? 'text-white' : 'text-[#2D3538]'
                                }`}>
                                {cadence.label}
                            </div>
                            <div className={`text-xs italic ${voiceSpec.cadenceStyle === cadence.value ? 'text-white/70' : 'text-[#9D9F9F]'
                                }`}>
                                "{cadence.example}"
                            </div>
                        </button>
                    ))}
                </div>
            </div>

            {/* Brand Voice Examples */}
            <div className="bg-[#2D3538] rounded-2xl p-6">
                <span className="text-[11px] font-mono uppercase tracking-[0.15em] text-white/50 block mb-4">
                    Brand Voice Examples
                </span>
                <ul className="space-y-2">
                    {voiceSpec.brandVoiceExamples.map((example, i) => (
                        <li key={i} className="text-white text-sm">
                            "{example}"
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    );
}
