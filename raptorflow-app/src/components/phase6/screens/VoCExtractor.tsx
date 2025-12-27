'use client';

import React, { useState } from 'react';
import { Phase6Data, VoCPhrase } from '@/lib/foundation';
import { Plus, X, Lock, Unlock, MessageSquare, Upload, Link } from 'lucide-react';
import { toast } from 'sonner';

interface Props {
    phase6: Phase6Data;
    onUpdatePhrases: (phrases: VoCPhrase[]) => void;
}

export function VoCExtractor({ phase6, onUpdatePhrases }: Props) {
    const [newPhrase, setNewPhrase] = useState('');
    const phrases = phase6.vocPhrases || [];
    const lockedPhrases = phrases.filter(p => p.isLocked);

    const addManualPhrase = () => {
        if (!newPhrase.trim()) return;
        const phrase: VoCPhrase = {
            id: crypto.randomUUID(),
            text: newPhrase.trim(),
            source: 'manual',
            category: 'general',
            isLocked: false
        };
        onUpdatePhrases([...phrases, phrase]);
        setNewPhrase('');
        toast.success('Phrase added');
    };

    const toggleLock = (id: string) => {
        const updated = phrases.map(p =>
            p.id === id ? { ...p, isLocked: !p.isLocked } : p
        );
        onUpdatePhrases(updated);
    };

    const removePhrase = (id: string) => {
        onUpdatePhrases(phrases.filter(p => p.id !== id));
    };

    const getCategoryLabel = (cat: VoCPhrase['category']) => {
        const labels = {
            'tired-of': 'Tired Of',
            'lose-time': 'Lose Time',
            'dont-trust': 'Don\'t Trust',
            'need': 'Need',
            'general': 'General'
        };
        return labels[cat] || cat;
    };

    const getCategoryColor = (cat: VoCPhrase['category']) => {
        const colors = {
            'tired-of': 'bg-red-50 text-red-700 border-red-200',
            'lose-time': 'bg-amber-50 text-amber-700 border-amber-200',
            'dont-trust': 'bg-purple-50 text-purple-700 border-purple-200',
            'need': 'bg-blue-50 text-blue-700 border-blue-200',
            'general': 'bg-[#F3F4EE] text-[#5B5F61] border-[#E5E6E3]'
        };
        return colors[cat] || colors.general;
    };

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="bg-[#FAFAF8] border border-[#E5E6E3] rounded-2xl p-6">
                <div className="flex items-center gap-3 mb-2">
                    <MessageSquare className="w-5 h-5 text-[#2D3538]" />
                    <h3 className="font-medium text-[#2D3538]">Voice of Customer</h3>
                </div>
                <p className="text-sm text-[#5B5F61]">
                    Stop sounding like a founder. Start sounding like your buyer.
                    Lock at least 5 phrases to anchor your messaging in reality.
                </p>
            </div>

            {/* Progress */}
            <div className="flex items-center gap-4">
                <div className="flex-1 h-2 bg-[#E5E6E3] rounded-full overflow-hidden">
                    <div
                        className={`h-full rounded-full transition-all ${lockedPhrases.length >= 5 ? 'bg-[#2D3538]' : 'bg-[#9D9F9F]'
                            }`}
                        style={{ width: `${Math.min(100, (lockedPhrases.length / 5) * 100)}%` }}
                    />
                </div>
                <span className={`text-sm font-mono ${lockedPhrases.length >= 5 ? 'text-[#2D3538]' : 'text-[#9D9F9F]'
                    }`}>
                    {lockedPhrases.length}/5 locked
                </span>
            </div>

            {/* Phrase Chips */}
            <div className="space-y-3">
                <span className="text-[11px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F]">
                    Extracted Phrases
                </span>
                <div className="flex flex-wrap gap-2">
                    {phrases.map(phrase => (
                        <div
                            key={phrase.id}
                            className={`group relative flex items-center gap-2 px-4 py-2 rounded-xl border transition-all ${phrase.isLocked
                                    ? 'bg-[#2D3538] border-[#2D3538] text-white'
                                    : getCategoryColor(phrase.category)
                                }`}
                        >
                            <span className="text-sm">"{phrase.text}"</span>
                            <div className="flex items-center gap-1 ml-1">
                                <button
                                    onClick={() => toggleLock(phrase.id)}
                                    className={`p-1 rounded transition-opacity ${phrase.isLocked
                                            ? 'opacity-100 hover:opacity-80'
                                            : 'opacity-0 group-hover:opacity-100'
                                        }`}
                                >
                                    {phrase.isLocked
                                        ? <Lock className="w-3 h-3" />
                                        : <Unlock className="w-3 h-3" />
                                    }
                                </button>
                                {!phrase.isLocked && (
                                    <button
                                        onClick={() => removePhrase(phrase.id)}
                                        className="p-1 rounded opacity-0 group-hover:opacity-100 transition-opacity hover:bg-black/5"
                                    >
                                        <X className="w-3 h-3" />
                                    </button>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Add Manual Phrase */}
            <div className="bg-white border border-[#E5E6E3] rounded-2xl p-6">
                <span className="text-[11px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F] block mb-3">
                    Add Your Own
                </span>
                <div className="flex gap-3">
                    <input
                        type="text"
                        value={newPhrase}
                        onChange={e => setNewPhrase(e.target.value)}
                        onKeyDown={e => e.key === 'Enter' && addManualPhrase()}
                        placeholder="Our customers always say..."
                        className="flex-1 px-4 py-3 bg-[#FAFAF8] border border-[#E5E6E3] rounded-xl text-[#2D3538] placeholder:text-[#9D9F9F] focus:outline-none focus:ring-2 focus:ring-[#2D3538]/20"
                    />
                    <button
                        onClick={addManualPhrase}
                        className="px-6 py-3 bg-[#2D3538] text-white rounded-xl hover:bg-[#1A1D1E] transition-colors flex items-center gap-2"
                    >
                        <Plus className="w-4 h-4" />
                        Add
                    </button>
                </div>
            </div>

            {/* Locked Phrases Summary */}
            {lockedPhrases.length > 0 && (
                <div className="bg-[#2D3538] rounded-2xl p-6">
                    <span className="text-[11px] font-mono uppercase tracking-[0.15em] text-white/50 block mb-4">
                        Locked for Messaging ({lockedPhrases.length})
                    </span>
                    <ul className="space-y-2">
                        {lockedPhrases.map(p => (
                            <li key={p.id} className="flex items-center gap-2 text-white text-sm">
                                <Lock className="w-3 h-3 text-white/50" />
                                "{p.text}"
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}
