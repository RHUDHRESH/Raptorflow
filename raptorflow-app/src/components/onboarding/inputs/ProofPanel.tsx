'use client';

import React from 'react';
import { Check, Shield, MessageCircle } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { cn } from '@/lib/utils';
import { ProofGuardrails, VoiceTone } from '@/lib/foundation';

interface ProofPanelProps {
    value: ProofGuardrails;
    onChange: (value: ProofGuardrails) => void;
}

const proofOptions: { key: keyof ProofGuardrails['proofAssets']; label: string }[] = [
    { key: 'testimonials', label: 'Testimonials' },
    { key: 'caseStudies', label: 'Case Studies' },
    { key: 'numbers', label: 'Numbers / Metrics' },
    { key: 'logos', label: 'Client Logos' },
    { key: 'screenshots', label: 'Screenshots' },
];

const voiceOptions: { value: VoiceTone; label: string }[] = [
    { value: 'calm', label: 'Calm' },
    { value: 'bold', label: 'Bold' },
    { value: 'technical', label: 'Technical' },
    { value: 'friendly', label: 'Friendly' },
    { value: 'luxury', label: 'Luxury' },
    { value: 'playful', label: 'Playful' },
];

const defaultValue: ProofGuardrails = {
    proofAssets: {
        testimonials: false,
        caseStudies: false,
        numbers: false,
        logos: false,
        screenshots: false,
    },
    forbiddenClaims: [],
    voiceTone: 'calm',
    wordsToAvoid: [],
};

export function ProofPanel({ value = defaultValue, onChange }: ProofPanelProps) {
    const safeValue = { ...defaultValue, ...value };

    const toggleProof = (key: keyof ProofGuardrails['proofAssets']) => {
        onChange({
            ...safeValue,
            proofAssets: {
                ...safeValue.proofAssets,
                [key]: !safeValue.proofAssets[key],
            },
        });
    };

    const setVoiceTone = (tone: VoiceTone) => {
        onChange({ ...safeValue, voiceTone: tone });
    };

    const updateForbiddenClaims = (text: string) => {
        onChange({
            ...safeValue,
            forbiddenClaims: text.split('\n').filter(Boolean),
        });
    };

    const updateWordsToAvoid = (text: string) => {
        onChange({
            ...safeValue,
            wordsToAvoid: text.split(',').map(w => w.trim()).filter(Boolean),
        });
    };

    return (
        <div className="space-y-6">
            {/* Panel 1: Proof You Have */}
            <div className="bg-card border-2 border-border rounded-xl p-5">
                <div className="flex items-center gap-2 mb-4">
                    <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center">
                        <Check className="h-4 w-4 text-emerald-500" />
                    </div>
                    <h3 className="font-semibold text-foreground">Proof You Have</h3>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                    {proofOptions.map((opt) => {
                        const isSelected = safeValue.proofAssets[opt.key];
                        return (
                            <div
                                key={opt.key}
                                onClick={() => toggleProof(opt.key)}
                                className={cn(
                                    "flex items-center gap-2 p-3 rounded-lg border-2 cursor-pointer transition-all",
                                    isSelected
                                        ? "border-emerald-500 bg-emerald-500/5"
                                        : "border-border hover:border-primary/30"
                                )}
                            >
                                <div className={cn(
                                    "w-5 h-5 rounded border-2 flex items-center justify-center",
                                    isSelected ? "bg-emerald-500 border-emerald-500" : "border-muted-foreground/30"
                                )}>
                                    {isSelected && <Check className="h-3 w-3 text-white" />}
                                </div>
                                <span className="text-sm font-medium">{opt.label}</span>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Panel 2: Claims You Can't Make */}
            <div className="bg-card border-2 border-border rounded-xl p-5">
                <div className="flex items-center gap-2 mb-4">
                    <div className="w-8 h-8 rounded-lg bg-amber-500/10 flex items-center justify-center">
                        <Shield className="h-4 w-4 text-amber-500" />
                    </div>
                    <h3 className="font-semibold text-foreground">Claims You Can't Make</h3>
                </div>
                <Textarea
                    placeholder="Enter claims you can't make (one per line)&#10;e.g., &quot;Guaranteed results&quot;&#10;e.g., &quot;FDA approved&quot;"
                    value={safeValue.forbiddenClaims.join('\n')}
                    onChange={(e) => updateForbiddenClaims(e.target.value)}
                    className="min-h-[100px] resize-none bg-background border-2 focus-visible:ring-0 focus-visible:border-primary"
                />
                <p className="text-xs text-muted-foreground mt-2">
                    Compliance, legal, or industry sensitivities
                </p>
            </div>

            {/* Panel 3: Brand Voice */}
            <div className="bg-card border-2 border-border rounded-xl p-5">
                <div className="flex items-center gap-2 mb-4">
                    <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center">
                        <MessageCircle className="h-4 w-4 text-blue-500" />
                    </div>
                    <h3 className="font-semibold text-foreground">Brand Voice</h3>
                </div>

                <div className="space-y-4">
                    <div>
                        <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-2 block">
                            Tone
                        </label>
                        <div className="flex flex-wrap gap-2">
                            {voiceOptions.map((opt) => (
                                <button
                                    key={opt.value}
                                    onClick={() => setVoiceTone(opt.value)}
                                    className={cn(
                                        "px-4 py-2 rounded-lg border-2 text-sm font-medium transition-all",
                                        safeValue.voiceTone === opt.value
                                            ? "border-primary bg-primary/5 text-primary"
                                            : "border-border hover:border-primary/30"
                                    )}
                                >
                                    {opt.label}
                                </button>
                            ))}
                        </div>
                    </div>

                    <div>
                        <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-2 block">
                            Words to Avoid
                        </label>
                        <Input
                            placeholder="e.g., disrupt, leverage, synergy (comma-separated)"
                            value={safeValue.wordsToAvoid.join(', ')}
                            onChange={(e) => updateWordsToAvoid(e.target.value)}
                            className="h-11 bg-background border-2 focus-visible:ring-0 focus-visible:border-primary"
                        />
                    </div>
                </div>
            </div>
        </div>
    );
}
