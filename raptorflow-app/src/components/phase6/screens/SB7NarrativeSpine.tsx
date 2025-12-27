'use client';

import React from 'react';
import { SB7Spine, GuideVibe, NarrativeVariant } from '@/lib/foundation';
import { User, Target, AlertTriangle, Compass, ListOrdered, Sparkles, CheckCircle, XCircle, Edit3 } from 'lucide-react';

interface Props {
    sb7Spine: SB7Spine | undefined;
    onUpdate: (spine: SB7Spine) => void;
}

const GUIDE_VIBES: { value: GuideVibe; label: string; description: string }[] = [
    { value: 'expert', label: 'Expert', description: 'Authority-driven. "I have done this 1000 times."' },
    { value: 'ally', label: 'Ally', description: 'Partnership-focused. "We are in this together."' },
    { value: 'operator', label: 'Operator', description: 'Get-it-done. "Here is the system. Use it."' },
    { value: 'contrarian', label: 'Contrarian', description: 'Challenge the status quo. "Everyone else is wrong."' }
];

export function SB7NarrativeSpine({ sb7Spine, onUpdate }: Props) {
    if (!sb7Spine) {
        return (
            <div className="flex items-center justify-center h-64 bg-[#FAFAF8] rounded-2xl">
                <p className="text-[#9D9F9F]">Generating narrative spine...</p>
            </div>
        );
    }

    const updateField = (field: keyof SB7Spine, value: string | string[] | GuideVibe | NarrativeVariant) => {
        onUpdate({ ...sb7Spine, [field]: value });
    };

    return (
        <div className="space-y-6">
            {/* Narrative Variant Toggle */}
            <div className="flex gap-2 p-1 bg-[#F3F4EE] rounded-xl w-fit">
                <button
                    onClick={() => updateField('narrativeVariant', 'escape-chaos')}
                    className={`px-4 py-2 text-sm rounded-lg transition-all ${sb7Spine.narrativeVariant === 'escape-chaos'
                        ? 'bg-white text-[#2D3538] shadow-sm'
                        : 'text-[#5B5F61]'
                        }`}
                >
                    🔥 Escape the Chaos
                </button>
                <button
                    onClick={() => updateField('narrativeVariant', 'become-operator')}
                    className={`px-4 py-2 text-sm rounded-lg transition-all ${sb7Spine.narrativeVariant === 'become-operator'
                        ? 'bg-white text-[#2D3538] shadow-sm'
                        : 'text-[#5B5F61]'
                        }`}
                >
                    🎯 Become the Operator
                </button>
            </div>

            {/* SB7 Card Grid */}
            <div className="grid grid-cols-2 gap-4">
                {/* Character */}
                <SB7Field
                    icon={<User className="w-4 h-4" />}
                    label="Character (The Hero)"
                    value={sb7Spine.character}
                    onChange={v => updateField('character', v)}
                    hint="Your ICP—the hero of this story"
                />

                {/* Wants */}
                <SB7Field
                    icon={<Target className="w-4 h-4" />}
                    label="Wants (The Goal)"
                    value={sb7Spine.wants}
                    onChange={v => updateField('wants', v)}
                    hint="What they're trying to achieve"
                />

                {/* Problem External */}
                <SB7Field
                    icon={<AlertTriangle className="w-4 h-4" />}
                    label="Problem (External)"
                    value={sb7Spine.problemExternal}
                    onChange={v => updateField('problemExternal', v)}
                    hint="The tangible obstacle"
                />

                {/* Problem Internal */}
                <SB7Field
                    icon={<AlertTriangle className="w-4 h-4" />}
                    label="Problem (Internal)"
                    value={sb7Spine.problemInternal}
                    onChange={v => updateField('problemInternal', v)}
                    hint="How it makes them feel"
                />

                {/* Problem Philosophical */}
                <SB7Field
                    icon={<AlertTriangle className="w-4 h-4" />}
                    label="Problem (Philosophical)"
                    value={sb7Spine.problemPhilosophical}
                    onChange={v => updateField('problemPhilosophical', v)}
                    hint="Why this is just wrong"
                    span2
                />

                {/* Guide */}
                <SB7Field
                    icon={<Compass className="w-4 h-4" />}
                    label="Guide (You)"
                    value={sb7Spine.guide}
                    onChange={v => updateField('guide', v)}
                    hint="Your brand as the guide"
                />

                {/* Plan */}
                <SB7Field
                    icon={<ListOrdered className="w-4 h-4" />}
                    label="Plan (3 Steps)"
                    value={sb7Spine.plan.join(', ')}
                    onChange={v => updateField('plan', v.split(',').map(s => s.trim()))}
                    hint="Comma-separated steps"
                />

                {/* CTA Direct */}
                <SB7Field
                    icon={<Sparkles className="w-4 h-4" />}
                    label="CTA (Direct)"
                    value={sb7Spine.ctaDirect}
                    onChange={v => updateField('ctaDirect', v)}
                    hint="The main action"
                />

                {/* CTA Transitional */}
                <SB7Field
                    icon={<Sparkles className="w-4 h-4" />}
                    label="CTA (Transitional)"
                    value={sb7Spine.ctaTransitional}
                    onChange={v => updateField('ctaTransitional', v)}
                    hint="Lower commitment option"
                />

                {/* Success */}
                <SB7Field
                    icon={<CheckCircle className="w-4 h-4" />}
                    label="Success"
                    value={sb7Spine.success}
                    onChange={v => updateField('success', v)}
                    hint="What happens when they win"
                />

                {/* Failure */}
                <SB7Field
                    icon={<XCircle className="w-4 h-4" />}
                    label="Failure Avoided"
                    value={sb7Spine.failure}
                    onChange={v => updateField('failure', v)}
                    hint="What happens if they don't act"
                />
            </div>

            {/* Guide Vibe Selector */}
            <div className="bg-[#FAFAF8] border border-[#E5E6E3] rounded-2xl p-6">
                <span className="text-[11px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F] block mb-4">
                    Guide Vibe
                </span>
                <div className="grid grid-cols-4 gap-3">
                    {GUIDE_VIBES.map(vibe => (
                        <button
                            key={vibe.value}
                            onClick={() => updateField('guideVibe', vibe.value)}
                            className={`text-left p-4 rounded-xl border transition-all ${sb7Spine.guideVibe === vibe.value
                                ? 'bg-[#2D3538] border-[#2D3538] text-white'
                                : 'bg-white border-[#E5E6E3] hover:border-[#2D3538]'
                                }`}
                        >
                            <div className={`font-medium text-sm mb-1 ${sb7Spine.guideVibe === vibe.value ? 'text-white' : 'text-[#2D3538]'
                                }`}>
                                {vibe.label}
                            </div>
                            <div className={`text-xs ${sb7Spine.guideVibe === vibe.value ? 'text-white/70' : 'text-[#9D9F9F]'
                                }`}>
                                {vibe.description}
                            </div>
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
}

function SB7Field({
    icon,
    label,
    value,
    onChange,
    hint,
    span2 = false
}: {
    icon: React.ReactNode;
    label: string;
    value: string;
    onChange: (v: string) => void;
    hint: string;
    span2?: boolean;
}) {
    return (
        <div className={`bg-white border border-[#E5E6E3] rounded-xl p-4 group ${span2 ? 'col-span-2' : ''}`}>
            <div className="flex items-center gap-2 mb-2">
                <span className="text-[#9D9F9F]">{icon}</span>
                <span className="text-[10px] font-mono uppercase tracking-[0.1em] text-[#9D9F9F]">
                    {label}
                </span>
            </div>
            <input
                type="text"
                value={value}
                onChange={e => onChange(e.target.value)}
                className="w-full bg-transparent text-[#2D3538] text-sm focus:outline-none"
                placeholder={hint}
            />
            <div className="text-[10px] text-[#C0C1BE] mt-1 opacity-0 group-hover:opacity-100 transition-opacity">
                {hint}
            </div>
        </div>
    );
}
