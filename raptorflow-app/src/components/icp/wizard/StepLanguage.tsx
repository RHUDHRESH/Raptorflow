import React from 'react';
import { IcpPsycholinguistics } from '@/types/icp-types';

interface StepLanguageProps {
    data: IcpPsycholinguistics;
    onChange: (data: Partial<IcpPsycholinguistics>) => void;
}

const MINDSET_TRAITS = [
    "Skeptical of agencies",
    "DIY mindset",
    "Hates marketing jargon",
    "Responds to numbers",
    "Emotion-driven",
    "Brand-conscious",
    "Risk-averse"
];

const PROOF_PREFERENCES = [
    { value: 'case-study', label: 'Case Studies', desc: 'Narrative success stories' },
    { value: 'data', label: 'Hard Data', desc: 'Numbers, charts, ROI' },
    { value: 'authority', label: 'Authority', desc: 'Expert endorsements, awards' },
    { value: 'social', label: 'Social Proof', desc: 'Reviews, G2 badges' },
];

const TONE_PREFERENCES = [
    "Calm", "Direct", "Bold", "Empathetic", "Technical", "Urgent"
];

export default function StepLanguage({ data, onChange }: StepLanguageProps) {

    const toggleList = (current: string[], item: string, field: keyof IcpPsycholinguistics) => {
        const newVal = current.includes(item)
            ? current.filter(i => i !== item)
            : [...current, item];
        onChange({ [field]: newVal });
    };

    return (
        <div className="space-y-12">
            <div className="text-center space-y-4">
                <h1 className="font-serif text-4xl text-[#2D3538] leading-tight">
                    Language & Behavior.
                </h1>
                <p className="text-[#5B5F61] text-lg max-w-md mx-auto">
                    This is the secret weapon. How do we speak so they actually listen?
                </p>
            </div>

            {/* Mindset Traits */}
            <div className="space-y-4">
                <label className="block text-sm font-semibold uppercase tracking-wider text-[#9D9F9F]">
                    Psychographics & Mindset (Pick 3-5)
                </label>
                <div className="flex flex-wrap gap-3">
                    {MINDSET_TRAITS.map((trait) => (
                        <button
                            key={trait}
                            onClick={() => toggleList(data.mindsetTraits, trait, 'mindsetTraits')}
                            className={`px-5 py-3 rounded-full border transition-all
                ${data.mindsetTraits.includes(trait)
                                    ? 'bg-[#2D3538] text-white border-[#2D3538] shadow-md transform scale-105'
                                    : 'bg-white text-[#5B5F61] border-[#C0C1BE] hover:border-[#5B5F61]'
                                }`}
                        >
                            {trait}
                        </button>
                    ))}
                </div>
            </div>

            {/* Proof Style */}
            <div className="space-y-4">
                <label className="block text-sm font-semibold uppercase tracking-wider text-[#9D9F9F]">
                    Proof Preference
                </label>
                <div className="grid grid-cols-2 gap-4">
                    {PROOF_PREFERENCES.map((pref) => (
                        <button
                            key={pref.value}
                            onClick={() => toggleList(data.proofPreference, pref.value, 'proofPreference')}
                            className={`p-4 rounded-xl border text-left transition-all
                ${data.proofPreference.includes(pref.value)
                                    ? 'border-[#2D3538] bg-white ring-1 ring-[#2D3538]'
                                    : 'border-[#C0C1BE]/50 hover:border-[#5B5F61]'
                                }`}
                        >
                            <div className="font-semibold text-[#2D3538]">{pref.label}</div>
                            <div className="text-sm text-[#5B5F61]">{pref.desc}</div>
                        </button>
                    ))}
                </div>
            </div>

            {/* Tone */}
            <div className="space-y-4">
                <label className="block text-sm font-semibold uppercase tracking-wider text-[#9D9F9F]">
                    Tone Preference
                </label>
                <div className="flex flex-wrap gap-2">
                    {TONE_PREFERENCES.map((tone) => (
                        <button
                            key={tone}
                            onClick={() => toggleList(data.tonePreference, tone, 'tonePreference')}
                            className={`px-4 py-2 rounded-lg border text-sm font-medium transition-all
                ${data.tonePreference.includes(tone)
                                    ? 'bg-[#E9ECE6] text-[#2D3538] border-[#2D3538]'
                                    : 'bg-transparent text-[#5B5F61] border-[#C0C1BE]/50 hover:border-[#9D9F9F]'
                                }`}
                        >
                            {tone}
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
}
