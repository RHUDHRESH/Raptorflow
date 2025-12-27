'use client';

import React, { useState } from 'react';
import { Signal7Soundbite, Signal7Type, AwarenessStage } from '@/lib/foundation';
import { RefreshCw, Copy, ChevronDown, ChevronUp, Zap, Target, AlertTriangle, Lightbulb, Shield, Award, ArrowRight } from 'lucide-react';
import { toast } from 'sonner';

interface Props {
    soundbites: Signal7Soundbite[];
    onRegenerate: (id: string, punchLevel: number) => void;
    onUpdate: (soundbites: Signal7Soundbite[]) => void;
}

const TYPE_CONFIG: Record<Signal7Type, {
    icon: React.ReactNode;
    label: string;
    color: string;
}> = {
    'status-quo-enemy': { icon: <AlertTriangle className="w-4 h-4" />, label: 'Status Quo Enemy', color: 'text-red-500' },
    'problem-agitate': { icon: <Zap className="w-4 h-4" />, label: 'Problem + Agitate', color: 'text-amber-500' },
    'outcome': { icon: <Target className="w-4 h-4" />, label: 'Outcome', color: 'text-blue-500' },
    'mechanism': { icon: <Lightbulb className="w-4 h-4" />, label: 'Mechanism', color: 'text-purple-500' },
    'objection-kill': { icon: <Shield className="w-4 h-4" />, label: 'Objection Kill', color: 'text-green-500' },
    'proof': { icon: <Award className="w-4 h-4" />, label: 'Proof', color: 'text-cyan-500' },
    'cta': { icon: <ArrowRight className="w-4 h-4" />, label: 'CTA', color: 'text-[#2D3538]' }
};

const AWARENESS_BADGES: Record<AwarenessStage, string> = {
    'unaware': 'bg-red-100 text-red-700',
    'problem': 'bg-amber-100 text-amber-700',
    'solution': 'bg-blue-100 text-blue-700',
    'product': 'bg-purple-100 text-purple-700',
    'most': 'bg-green-100 text-green-700'
};

export function PrecisionSoundbites({ soundbites, onRegenerate, onUpdate }: Props) {
    const [expandedId, setExpandedId] = useState<string | null>(null);

    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text);
        toast.success('Copied to clipboard');
    };

    const updatePunchLevel = (id: string, level: number) => {
        const updated = soundbites.map(s =>
            s.id === id ? { ...s, punchLevel: level } : s
        );
        onUpdate(updated);
    };

    const getScoreColor = (score: number) => {
        if (score >= 4) return 'text-green-500';
        if (score >= 3) return 'text-amber-500';
        return 'text-red-500';
    };

    if (!soundbites || soundbites.length === 0) {
        return (
            <div className="flex items-center justify-center h-64 bg-[#FAFAF8] rounded-2xl">
                <p className="text-[#9D9F9F]">Generating soundbites...</p>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {/* Legend */}
            <div className="flex items-center gap-4 text-xs text-[#9D9F9F]">
                <span className="font-mono uppercase tracking-wider">SIGNAL-7 Soundbites</span>
                <span>•</span>
                <span>{soundbites.length} lines</span>
            </div>

            {/* Soundbite Cards */}
            {soundbites.map((sb, index) => {
                const config = TYPE_CONFIG[sb.type];
                const isExpanded = expandedId === sb.id;

                return (
                    <div
                        key={sb.id}
                        className="bg-white border border-[#E5E6E3] rounded-2xl overflow-hidden group"
                    >
                        {/* Card Header */}
                        <div className="flex items-start gap-4 p-6">
                            {/* Type Badge */}
                            <div className={`flex items-center gap-2 ${config.color}`}>
                                {config.icon}
                            </div>

                            {/* Main Content */}
                            <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2 mb-2">
                                    <span className="text-[10px] font-mono uppercase tracking-[0.1em] text-[#9D9F9F]">
                                        #{index + 1} {config.label}
                                    </span>
                                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${AWARENESS_BADGES[sb.awarenessStage]}`}>
                                        {sb.awarenessStage}
                                    </span>
                                </div>

                                <p className="text-[#2D3538] font-medium mb-3">
                                    "{sb.text}"
                                </p>

                                <div className="text-xs text-[#9D9F9F]">
                                    <span className="font-medium">Purpose:</span> {sb.purpose}
                                </div>
                            </div>

                            {/* Actions */}
                            <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                <button
                                    onClick={() => copyToClipboard(sb.text)}
                                    className="p-2 hover:bg-[#F3F4EE] rounded-lg transition-colors"
                                >
                                    <Copy className="w-4 h-4 text-[#5B5F61]" />
                                </button>
                                <button
                                    onClick={() => onRegenerate(sb.id, sb.punchLevel)}
                                    className="p-2 hover:bg-[#F3F4EE] rounded-lg transition-colors"
                                >
                                    <RefreshCw className="w-4 h-4 text-[#5B5F61]" />
                                </button>
                            </div>
                        </div>

                        {/* Expand/Collapse */}
                        <button
                            onClick={() => setExpandedId(isExpanded ? null : sb.id)}
                            className="w-full flex items-center justify-center gap-2 py-2 bg-[#FAFAF8] border-t border-[#E5E6E3] text-xs text-[#9D9F9F] hover:bg-[#F3F4EE] transition-colors"
                        >
                            {isExpanded ? (
                                <>Less <ChevronUp className="w-3 h-3" /></>
                            ) : (
                                <>Scores & Controls <ChevronDown className="w-3 h-3" /></>
                            )}
                        </button>

                        {/* Expanded Content */}
                        {isExpanded && (
                            <div className="p-6 border-t border-[#E5E6E3] bg-[#FAFAF8] space-y-4">
                                {/* Punch Level Slider */}
                                <div>
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="text-xs font-mono uppercase text-[#9D9F9F]">
                                            Punch Level
                                        </span>
                                        <span className="text-xs text-[#5B5F61]">
                                            {sb.punchLevel <= 2 ? 'Precise' : sb.punchLevel >= 4 ? 'Punchy' : 'Balanced'}
                                        </span>
                                    </div>
                                    <input
                                        type="range"
                                        min={1}
                                        max={5}
                                        value={sb.punchLevel}
                                        onChange={e => updatePunchLevel(sb.id, parseInt(e.target.value))}
                                        className="w-full accent-[#2D3538]"
                                    />
                                    <div className="flex justify-between text-[10px] text-[#C0C1BE]">
                                        <span>Precise</span>
                                        <span>Punchy</span>
                                    </div>
                                </div>

                                {/* Rigor Scores */}
                                <div>
                                    <span className="text-xs font-mono uppercase text-[#9D9F9F] block mb-2">
                                        Rigor Scores
                                    </span>
                                    <div className="grid grid-cols-5 gap-2">
                                        {[
                                            { label: 'Specificity', value: sb.scores.specificity },
                                            { label: 'Proof', value: sb.scores.proof },
                                            { label: 'Differentiation', value: sb.scores.differentiation },
                                            { label: 'Awareness Fit', value: sb.scores.awarenessFit },
                                            { label: 'Clarity', value: sb.scores.cognitiveLoad }
                                        ].map(score => (
                                            <div key={score.label} className="text-center">
                                                <div className={`text-lg font-medium ${getScoreColor(score.value)}`}>
                                                    {score.value}/5
                                                </div>
                                                <div className="text-[10px] text-[#9D9F9F]">
                                                    {score.label}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {/* Proof Needed */}
                                <div className="bg-white rounded-xl p-4 border border-[#E5E6E3]">
                                    <span className="text-xs font-mono uppercase text-[#9D9F9F] block mb-1">
                                        Proof Needed
                                    </span>
                                    <p className="text-sm text-[#2D3538]">{sb.proofNeeded}</p>
                                </div>

                                {/* VoC Anchors */}
                                {sb.vocAnchors.length > 0 && (
                                    <div>
                                        <span className="text-xs font-mono uppercase text-[#9D9F9F] block mb-2">
                                            VoC Anchors Used
                                        </span>
                                        <div className="flex gap-2">
                                            {sb.vocAnchors.map(id => (
                                                <span key={id} className="px-2 py-1 bg-[#2D3538] text-white text-xs rounded-lg">
                                                    VoC #{id.slice(-4)}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                );
            })}
        </div>
    );
}
