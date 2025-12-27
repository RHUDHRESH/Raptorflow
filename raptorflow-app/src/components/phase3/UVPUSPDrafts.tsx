'use client';

import React, { useState } from 'react';
import { Star, Check, AlertCircle, Copy, RefreshCw, Lock, Unlock, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { UVPDraft, USPDraft } from '@/lib/foundation';
import { toast } from 'sonner';

interface UVPUSPDraftsProps {
    uvpDrafts: UVPDraft[];
    uspDrafts: USPDraft[];
    mechanismLine: string;
    onUpdateUVP: (drafts: UVPDraft[]) => void;
    onUpdateUSP: (drafts: USPDraft[]) => void;
    onUpdateMechanism: (line: string) => void;
    onRegenerate: (type: 'uvp' | 'usp', broader?: boolean) => void;
    onContinue: () => void;
    onBack: () => void;
}

// Score badge
function ScoreBadge({ label, score, maxScore = 100 }: { label: string; score: number; maxScore?: number }) {
    const percentage = (score / maxScore) * 100;
    const color = percentage >= 70 ? '#22C55E' : percentage >= 40 ? '#F59E0B' : '#EF4444';

    return (
        <div className="flex items-center gap-2">
            <span className="text-[10px] font-mono uppercase tracking-[0.1em] text-[#9D9F9F]">{label}</span>
            <div className="flex items-center gap-1">
                <div className="w-12 h-1.5 bg-[#E5E6E3] rounded-full overflow-hidden">
                    <div
                        className="h-full rounded-full"
                        style={{ width: `${percentage}%`, backgroundColor: color }}
                    />
                </div>
                <span className="text-[10px] font-mono" style={{ color }}>{score}</span>
            </div>
        </div>
    );
}

// UVP Card
function UVPCard({
    draft,
    isPrimary,
    onSelect,
    onEdit,
}: {
    draft: UVPDraft;
    isPrimary: boolean;
    onSelect: () => void;
    onEdit: (text: string) => void;
}) {
    const [isEditing, setIsEditing] = useState(false);
    const [editText, setEditText] = useState(draft.text);

    const handleSave = () => {
        onEdit(editText);
        setIsEditing(false);
    };

    const copyToClipboard = () => {
        navigator.clipboard.writeText(draft.text);
        toast.success('UVP copied!');
    };

    return (
        <div
            className={`group relative rounded-2xl p-6 transition-all cursor-pointer ${isPrimary
                    ? 'bg-[#2D3538] text-white'
                    : 'bg-white border-2 border-[#E5E6E3] hover:border-[#C0C1BE]'
                }`}
            onClick={() => !isEditing && onSelect()}
        >
            {/* Primary badge */}
            {isPrimary && (
                <div className="absolute -top-2 -right-2 w-6 h-6 bg-white rounded-full flex items-center justify-center shadow-md">
                    <Star className="w-3.5 h-3.5 text-[#2D3538] fill-[#2D3538]" />
                </div>
            )}

            {/* Content */}
            {isEditing ? (
                <div onClick={(e) => e.stopPropagation()}>
                    <textarea
                        value={editText}
                        onChange={(e) => setEditText(e.target.value)}
                        className="w-full bg-transparent border-none text-[15px] leading-relaxed resize-none focus:outline-none"
                        rows={3}
                        autoFocus
                    />
                    <div className="flex gap-2 mt-3">
                        <Button size="sm" onClick={handleSave} className="bg-white text-[#2D3538]">
                            Save
                        </Button>
                        <Button size="sm" variant="ghost" onClick={() => setIsEditing(false)} className="text-white/60">
                            Cancel
                        </Button>
                    </div>
                </div>
            ) : (
                <>
                    <p className={`text-[15px] leading-relaxed mb-4 ${isPrimary ? 'text-white' : 'text-[#2D3538]'}`}>
                        {draft.text}
                    </p>

                    {/* Badges */}
                    <div className="flex items-center gap-4 mb-4">
                        <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-lg text-[10px] font-mono uppercase ${draft.proofAttached
                                ? (isPrimary ? 'bg-white/20 text-white' : 'bg-[#22C55E]/10 text-[#22C55E]')
                                : (isPrimary ? 'bg-[#EF4444]/30 text-white' : 'bg-[#EF4444]/10 text-[#EF4444]')
                            }`}>
                            {draft.proofAttached ? <Check className="w-3 h-3" /> : <AlertCircle className="w-3 h-3" />}
                            {draft.proofAttached ? 'Proof ✓' : 'No Proof'}
                        </span>
                    </div>

                    {/* Scores */}
                    <div className="flex items-center gap-4">
                        <ScoreBadge label="Diff" score={draft.differentiationScore} />
                        <ScoreBadge label="Clarity" score={draft.clarityScore} />
                    </div>

                    {/* Actions */}
                    <div className="absolute top-4 right-4 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button
                            onClick={(e) => { e.stopPropagation(); setIsEditing(true); }}
                            className={`p-2 rounded-lg ${isPrimary ? 'hover:bg-white/10' : 'hover:bg-[#F3F4EE]'}`}
                        >
                            <span className="text-[11px]">Edit</span>
                        </button>
                        <button
                            onClick={(e) => { e.stopPropagation(); copyToClipboard(); }}
                            className={`p-2 rounded-lg ${isPrimary ? 'hover:bg-white/10' : 'hover:bg-[#F3F4EE]'}`}
                        >
                            <Copy className="w-4 h-4" />
                        </button>
                    </div>
                </>
            )}
        </div>
    );
}

// USP Card
function USPCard({
    draft,
    isPrimary,
    onSelect,
}: {
    draft: USPDraft;
    isPrimary: boolean;
    onSelect: () => void;
}) {
    const gates = [
        { label: 'Specific', passed: draft.isSpecific },
        { label: 'Unique', passed: draft.isUnique },
        { label: 'Moves Buyers', passed: draft.movesBuyers },
    ];

    const passedGates = gates.filter((g) => g.passed).length;

    return (
        <div
            className={`group relative rounded-2xl p-6 transition-all cursor-pointer ${isPrimary
                    ? 'bg-[#2D3538] text-white'
                    : 'bg-white border-2 border-[#E5E6E3] hover:border-[#C0C1BE]'
                }`}
            onClick={onSelect}
        >
            {isPrimary && (
                <div className="absolute -top-2 -right-2 w-6 h-6 bg-white rounded-full flex items-center justify-center shadow-md">
                    <Star className="w-3.5 h-3.5 text-[#2D3538] fill-[#2D3538]" />
                </div>
            )}

            <p className={`text-[15px] leading-relaxed mb-4 ${isPrimary ? 'text-white' : 'text-[#2D3538]'}`}>
                {draft.text}
            </p>

            {/* Reeves Gates */}
            <div className="flex items-center gap-2">
                <span className={`text-[10px] font-mono uppercase tracking-[0.1em] ${isPrimary ? 'text-white/50' : 'text-[#9D9F9F]'}`}>
                    Reeves Gates:
                </span>
                <div className="flex gap-1">
                    {gates.map((gate) => (
                        <span
                            key={gate.label}
                            className={`px-2 py-0.5 rounded text-[10px] font-mono ${gate.passed
                                    ? (isPrimary ? 'bg-white/20 text-white' : 'bg-[#22C55E]/10 text-[#22C55E]')
                                    : (isPrimary ? 'bg-white/10 text-white/40' : 'bg-[#E5E6E3] text-[#9D9F9F]')
                                }`}
                        >
                            {gate.label}
                        </span>
                    ))}
                </div>
                <span className={`text-[11px] font-medium ${passedGates === 3 ? 'text-[#22C55E]' : 'text-[#F59E0B]'}`}>
                    {passedGates}/3
                </span>
            </div>
        </div>
    );
}

export function UVPUSPDrafts({
    uvpDrafts,
    uspDrafts,
    mechanismLine,
    onUpdateUVP,
    onUpdateUSP,
    onUpdateMechanism,
    onRegenerate,
    onContinue,
    onBack,
}: UVPUSPDraftsProps) {
    const [vocabularyLocked, setVocabularyLocked] = useState(false);

    const handleSelectUVP = (id: string) => {
        onUpdateUVP(
            uvpDrafts.map((d) => ({ ...d, isPrimary: d.id === id }))
        );
    };

    const handleEditUVP = (id: string, text: string) => {
        onUpdateUVP(
            uvpDrafts.map((d) => (d.id === id ? { ...d, text } : d))
        );
    };

    const handleSelectUSP = (id: string) => {
        onUpdateUSP(
            uspDrafts.map((d) => ({ ...d, isPrimary: d.id === id }))
        );
    };

    const primaryUVP = uvpDrafts.find((d) => d.isPrimary);
    const primaryUSP = uspDrafts.find((d) => d.isPrimary);

    return (
        <div className="space-y-10">
            {/* UVP Section */}
            <div>
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h3 className="font-medium text-[#2D3538] text-[18px]">Value Proposition (UVP)</h3>
                        <p className="text-[13px] text-[#5B5F61] mt-1">
                            Select your primary UVP — anchored to job, pain, and gain.
                        </p>
                    </div>
                    <div className="flex gap-2">
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => onRegenerate('uvp')}
                            className="text-[#5B5F61]"
                        >
                            <RefreshCw className="w-4 h-4 mr-1" />
                            Regenerate
                        </Button>
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => onRegenerate('uvp', true)}
                            className="text-[#5B5F61]"
                        >
                            <Sparkles className="w-4 h-4 mr-1" />
                            Broader
                        </Button>
                    </div>
                </div>

                <div className="grid grid-cols-3 gap-4">
                    {uvpDrafts.map((draft) => (
                        <UVPCard
                            key={draft.id}
                            draft={draft}
                            isPrimary={draft.isPrimary}
                            onSelect={() => handleSelectUVP(draft.id)}
                            onEdit={(text) => handleEditUVP(draft.id, text)}
                        />
                    ))}
                </div>
            </div>

            {/* USP Section */}
            <div>
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h3 className="font-medium text-[#2D3538] text-[18px]">Unique Selling Proposition (USP)</h3>
                        <p className="text-[13px] text-[#5B5F61] mt-1">
                            Specific benefit + uniqueness vs. alternatives (Reeves gates).
                        </p>
                    </div>
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={() => onRegenerate('usp')}
                        className="text-[#5B5F61]"
                    >
                        <RefreshCw className="w-4 h-4 mr-1" />
                        Regenerate
                    </Button>
                </div>

                <div className="grid grid-cols-3 gap-4">
                    {uspDrafts.map((draft) => (
                        <USPCard
                            key={draft.id}
                            draft={draft}
                            isPrimary={draft.isPrimary}
                            onSelect={() => handleSelectUSP(draft.id)}
                        />
                    ))}
                </div>
            </div>

            {/* Mechanism Line */}
            <div className="bg-[#FAFAF8] rounded-2xl p-6">
                <h3 className="text-[11px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-4">
                    Mechanism Line
                </h3>
                <div className="flex items-center gap-4">
                    <span className="text-[15px] text-[#5B5F61]">We do it by:</span>
                    <input
                        type="text"
                        value={mechanismLine}
                        onChange={(e) => onUpdateMechanism(e.target.value)}
                        placeholder="Explain how your solution works..."
                        className="flex-1 bg-white border border-[#E5E6E3] rounded-xl px-4 py-3 text-[15px] text-[#2D3538]"
                    />
                </div>
            </div>

            {/* Lock Vocabulary */}
            <div className="flex items-center justify-center">
                <Button
                    variant="outline"
                    onClick={() => setVocabularyLocked(!vocabularyLocked)}
                    className={vocabularyLocked ? 'border-[#2D3538] text-[#2D3538]' : 'text-[#5B5F61]'}
                >
                    {vocabularyLocked ? <Lock className="w-4 h-4 mr-2" /> : <Unlock className="w-4 h-4 mr-2" />}
                    {vocabularyLocked ? 'Vocabulary Locked' : 'Lock Vocabulary (ban fluffy words)'}
                </Button>
            </div>

            {/* Actions */}
            <div className="flex items-center justify-between pt-8 border-t border-[#E5E6E3]">
                <Button
                    variant="ghost"
                    onClick={onBack}
                    className="text-[#5B5F61] hover:text-[#2D3538]"
                >
                    ← Back
                </Button>
                <Button
                    onClick={onContinue}
                    disabled={!primaryUVP || !primaryUSP}
                    className="bg-[#2D3538] hover:bg-[#1A1D1E] disabled:bg-[#9D9F9F] text-white px-10 py-6 rounded-2xl text-[15px] font-medium"
                >
                    Continue
                </Button>
            </div>
        </div>
    );
}
