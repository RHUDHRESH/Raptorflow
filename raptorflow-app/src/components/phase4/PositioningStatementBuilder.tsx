'use client';

import React, { useState } from 'react';
import {
    ChevronRight,
    Check,
    Edit3,
    Sparkles,
    AlertCircle,
    Lock,
    FileText
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Phase4Data, PositioningStatementVariant, StatementStyle } from '@/lib/foundation';
import { v4 as uuidv4 } from 'uuid';

interface PositioningStatementBuilderProps {
    phase4: Phase4Data;
    onUpdate: (updates: Partial<Phase4Data>) => void;
    onContinue: () => void;
    onBack: () => void;
}

const STATEMENT_STYLES: { style: StatementStyle; label: string; description: string }[] = [
    {
        style: 'dunford',
        label: 'Dunford',
        description: 'Precise, defensible positioning formula'
    },
    {
        style: 'ries',
        label: 'Ries',
        description: 'Own one word in the mind'
    },
    {
        style: 'godin',
        label: 'Godin',
        description: 'Remarkable to the right people'
    },
];

export function PositioningStatementBuilder({
    phase4,
    onUpdate,
    onContinue,
    onBack
}: PositioningStatementBuilderProps) {
    const [activeStyle, setActiveStyle] = useState<StatementStyle>('dunford');
    const [isEditing, setIsEditing] = useState(false);

    // Build statement components from phase4 data
    const primarySegment = phase4.whoCareSegments?.find(s => s.rank === 'primary');
    const statusQuo = phase4.competitiveAlternatives?.statusQuo?.[0]?.name;
    const primaryValue = phase4.valueClaims?.find(c => c.isSelected)?.claimText || phase4.differentiatedValue?.[0]?.value;
    const category = phase4.marketCategory?.primary;
    const oneThing = phase4.oneThing || phase4.uniqueAttributes?.[0]?.attribute;

    // Generate or get variants
    const getVariants = (): PositioningStatementVariant[] => {
        if (phase4.statementVariants?.length) return phase4.statementVariants;

        return [
            {
                id: uuidv4(),
                style: 'dunford',
                text: `For ${primarySegment?.name || '[target segment]'}, who struggle with ${statusQuo || '[status quo]'}, ${category || '[product]'} is a ${category || '[category]'} that delivers ${primaryValue || '[value]'}, unlike ${statusQuo || '[alternative]'}, because ${oneThing || '[mechanism]'}.`,
                components: {
                    forWhom: primarySegment?.name,
                    category: category,
                    value: primaryValue,
                    unlike: statusQuo,
                    because: oneThing
                },
                proofCoverage: 65,
                isCanonical: false
            },
            {
                id: uuidv4(),
                style: 'ries',
                text: `The ${oneThing || '[one thing]'} ${category || 'solution'}.`,
                components: {
                    ownedWord: oneThing,
                    category: category
                },
                proofCoverage: 45,
                isCanonical: false
            },
            {
                id: uuidv4(),
                style: 'godin',
                text: `For ${primarySegment?.name || '[tribe]'} who refuse to settle for ${statusQuo || '[status quo]'}, finally a ${category || 'solution'} that's ${oneThing || 'remarkable'}.`,
                components: {
                    remarkableTo: primarySegment?.name,
                    remarkableHow: oneThing
                },
                proofCoverage: 50,
                isCanonical: false
            }
        ];
    };

    const variants = getVariants();
    const activeVariant = variants.find(v => v.style === activeStyle) || variants[0];
    const canonicalVariant = variants.find(v => v.isCanonical);

    const handleUpdateVariant = (variantId: string, text: string) => {
        const updated = variants.map(v =>
            v.id === variantId ? { ...v, text } : v
        );
        onUpdate({ statementVariants: updated });
    };

    const handleLockAsCanonical = (variantId: string) => {
        const updated = variants.map(v => ({
            ...v,
            isCanonical: v.id === variantId
        }));
        const canonical = updated.find(v => v.isCanonical);
        onUpdate({
            statementVariants: updated,
            positioningStatement: canonical?.text || '',
            canonicalStatementId: variantId,
            oneThing: activeVariant.components.ownedWord || activeVariant.components.because
        });
    };

    const handleTighten = () => {
        // Remove weak words and adjectives
        const weakWords = ['very', 'really', 'actually', 'basically', 'literally', 'honestly', 'amazing', 'incredible', 'revolutionary'];
        let tightened = activeVariant.text;
        weakWords.forEach(word => {
            const regex = new RegExp(`\\b${word}\\b\\s*`, 'gi');
            tightened = tightened.replace(regex, '');
        });
        handleUpdateVariant(activeVariant.id, tightened);
    };

    const getProofWarnings = () => {
        const warnings: string[] = [];
        if (!primarySegment) warnings.push('No primary segment selected');
        if (!category) warnings.push('No category selected');
        if (!primaryValue) warnings.push('No value claims selected');
        if (!statusQuo) warnings.push('No alternatives defined');
        return warnings;
    };

    const proofWarnings = getProofWarnings();

    return (
        <div className="space-y-6">
            {/* Header Info */}
            <div className="bg-[#F3F4EE] rounded-2xl p-5 border border-[#E5E6E3]">
                <p className="text-sm text-[#5B5F61]">
                    <strong>Important:</strong> Positioning is not your tagline or slogan —
                    it's the foundation beneath all messaging. This statement won't appear on your website;
                    it guides everything that does.
                </p>
            </div>

            {/* Style Tabs */}
            <div className="flex gap-2 p-1 bg-[#F3F4EE] rounded-xl">
                {STATEMENT_STYLES.map(({ style, label, description }) => (
                    <button
                        key={style}
                        onClick={() => setActiveStyle(style)}
                        className={`flex-1 px-4 py-3 rounded-lg transition-all text-left ${activeStyle === style
                                ? 'bg-white text-[#2D3538] shadow-sm'
                                : 'text-[#5B5F61] hover:text-[#2D3538]'
                            }`}
                    >
                        <span className="block text-sm font-medium">{label}</span>
                        <span className="block text-xs text-[#9D9F9F] mt-0.5">{description}</span>
                    </button>
                ))}
            </div>

            {/* Statement Display */}
            <div className={`rounded-3xl p-10 transition-all ${activeVariant.isCanonical
                    ? 'bg-[#2D3538]'
                    : 'bg-white border border-[#E5E6E3]'
                }`}>
                {/* Lock Badge */}
                {activeVariant.isCanonical && (
                    <div className="flex items-center gap-2 mb-4">
                        <Lock className="w-4 h-4 text-white/60" />
                        <span className="text-[10px] font-mono uppercase tracking-[0.15em] text-white/60">
                            Canonical Statement
                        </span>
                    </div>
                )}

                {/* Statement Text */}
                {isEditing ? (
                    <textarea
                        value={activeVariant.text}
                        onChange={(e) => handleUpdateVariant(activeVariant.id, e.target.value)}
                        onBlur={() => setIsEditing(false)}
                        autoFocus
                        className={`w-full font-serif text-[24px] leading-[1.5] bg-transparent border-none focus:outline-none resize-none ${activeVariant.isCanonical ? 'text-white' : 'text-[#2D3538]'
                            }`}
                        rows={4}
                    />
                ) : (
                    <p
                        onClick={() => setIsEditing(true)}
                        className={`font-serif text-[24px] leading-[1.5] cursor-text ${activeVariant.isCanonical ? 'text-white' : 'text-[#2D3538]'
                            }`}
                    >
                        "{activeVariant.text}"
                    </p>
                )}

                {/* Proof Coverage */}
                <div className="mt-6 flex items-center gap-4">
                    <div className="flex-1">
                        <div className="flex items-center justify-between mb-1">
                            <span className={`text-xs ${activeVariant.isCanonical ? 'text-white/60' : 'text-[#9D9F9F]'}`}>
                                Proof Coverage
                            </span>
                            <span className={`text-xs font-mono ${activeVariant.isCanonical ? 'text-white' : 'text-[#2D3538]'}`}>
                                {activeVariant.proofCoverage}%
                            </span>
                        </div>
                        <div className={`h-1.5 rounded-full overflow-hidden ${activeVariant.isCanonical ? 'bg-white/20' : 'bg-[#E5E6E3]'}`}>
                            <div
                                className={`h-full rounded-full ${activeVariant.proofCoverage > 70 ? 'bg-green-500' :
                                        activeVariant.proofCoverage > 50 ? 'bg-amber-500' :
                                            'bg-red-500'
                                    }`}
                                style={{ width: `${activeVariant.proofCoverage}%` }}
                            />
                        </div>
                    </div>
                </div>

                {/* Actions */}
                <div className="mt-6 flex items-center gap-3">
                    <button
                        onClick={() => setIsEditing(true)}
                        className={`flex items-center gap-1.5 text-sm ${activeVariant.isCanonical ? 'text-white/80 hover:text-white' : 'text-[#5B5F61] hover:text-[#2D3538]'
                            }`}
                    >
                        <Edit3 className="w-4 h-4" /> Edit
                    </button>
                    <button
                        onClick={handleTighten}
                        className={`flex items-center gap-1.5 text-sm ${activeVariant.isCanonical ? 'text-white/80 hover:text-white' : 'text-[#5B5F61] hover:text-[#2D3538]'
                            }`}
                    >
                        <Sparkles className="w-4 h-4" /> Tighten
                    </button>
                    {!activeVariant.isCanonical && (
                        <button
                            onClick={() => handleLockAsCanonical(activeVariant.id)}
                            className="flex items-center gap-1.5 text-sm ml-auto bg-[#2D3538] text-white px-4 py-2 rounded-lg hover:bg-[#1A1D1E]"
                        >
                            <Lock className="w-4 h-4" /> Lock as Canonical
                        </button>
                    )}
                </div>
            </div>

            {/* Proof Warnings */}
            {proofWarnings.length > 0 && (
                <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
                    <div className="flex items-start gap-3">
                        <AlertCircle className="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" />
                        <div>
                            <p className="text-sm text-amber-800 font-medium">
                                Claims without evidence
                            </p>
                            <ul className="mt-2 space-y-1">
                                {proofWarnings.map((warning, i) => (
                                    <li key={i} className="text-xs text-amber-700">• {warning}</li>
                                ))}
                            </ul>
                        </div>
                    </div>
                </div>
            )}

            {/* Template Reference (Dunford only) */}
            {activeStyle === 'dunford' && (
                <div className="bg-[#F3F4EE] rounded-xl p-5 border border-[#E5E6E3]">
                    <div className="flex items-center gap-2 mb-3">
                        <FileText className="w-4 h-4 text-[#5B5F61]" />
                        <span className="text-[10px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F]">
                            Dunford Formula
                        </span>
                    </div>
                    <p className="text-sm text-[#5B5F61] font-mono">
                        For <span className="text-[#2D3538]">[WHO CARES segment]</span>, <br />
                        who struggle with <span className="text-[#2D3538]">[PROBLEM / STATUS QUO]</span>, <br />
                        <span className="text-[#2D3538]">[PRODUCT]</span> is a <span className="text-[#2D3538]">[CATEGORY]</span>, <br />
                        that delivers <span className="text-[#2D3538]">[PRIMARY VALUE]</span>, <br />
                        unlike <span className="text-[#2D3538]">[PRIMARY ALTERNATIVE]</span>, <br />
                        because <span className="text-[#2D3538]">[UNIQUE MECHANISM + PROOF]</span>.
                    </p>
                </div>
            )}

            {/* Navigation */}
            <div className="flex justify-between pt-6 border-t border-[#E5E6E3]">
                <Button
                    variant="ghost"
                    onClick={onBack}
                    className="text-[#5B5F61]"
                >
                    Back
                </Button>
                <Button
                    onClick={onContinue}
                    className="bg-[#2D3538] hover:bg-[#1A1D1E] text-white px-8"
                >
                    Continue <ChevronRight className="w-4 h-4 ml-1" />
                </Button>
            </div>
        </div>
    );
}
