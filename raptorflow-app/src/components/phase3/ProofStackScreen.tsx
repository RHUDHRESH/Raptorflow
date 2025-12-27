'use client';

import React, { useState } from 'react';
import { Upload, Plus, Check, AlertCircle, FileText, Image, BarChart3, Award, MessageSquare, Clock, X, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ProofArtifact, ProofCategory } from '@/lib/foundation';
import { v4 as uuidv4 } from 'uuid';

interface ProofStackScreenProps {
    proofArtifacts: ProofArtifact[];
    onUpdate: (artifacts: ProofArtifact[]) => void;
    onContinue: () => void;
    onBack: () => void;
}

const CATEGORY_CONFIG: Record<ProofCategory, { label: string; icon: React.ElementType; color: string }> = {
    'metrics': { label: 'Metrics', icon: BarChart3, color: '#3B82F6' },
    'case-stories': { label: 'Case Stories', icon: FileText, color: '#22C55E' },
    'testimonials': { label: 'Testimonials', icon: MessageSquare, color: '#8B5CF6' },
    'screenshots': { label: 'Screenshots/Demos', icon: Image, color: '#F59E0B' },
    'credentials': { label: 'Credentials', icon: Award, color: '#EC4899' },
    'not-yet': { label: 'Not Yet', icon: Clock, color: '#9D9F9F' },
};

const STRENGTH_CONFIG = {
    weak: { label: 'Weak', color: '#EF4444', score: 1 },
    medium: { label: 'Medium', color: '#F59E0B', score: 2 },
    strong: { label: 'Strong', color: '#22C55E', score: 3 },
};

// Proof artifact card
function ProofCard({
    artifact,
    onRemove,
    onUpdateStrength,
}: {
    artifact: ProofArtifact;
    onRemove: () => void;
    onUpdateStrength: (strength: 'weak' | 'medium' | 'strong') => void;
}) {
    const config = CATEGORY_CONFIG[artifact.category];
    const Icon = config.icon;
    const strengthConfig = STRENGTH_CONFIG[artifact.strength];

    return (
        <div className="group bg-white border border-[#E5E6E3] rounded-xl p-5 hover:shadow-sm transition-all">
            <div className="flex items-start gap-4">
                <div
                    className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
                    style={{ backgroundColor: `${config.color}15` }}
                >
                    <Icon className="w-5 h-5" style={{ color: config.color }} />
                </div>

                <div className="flex-1 min-w-0">
                    <h4 className="font-medium text-[#2D3538] text-[15px] mb-1">{artifact.title}</h4>
                    {artifact.description && (
                        <p className="text-[13px] text-[#5B5F61] mb-3">{artifact.description}</p>
                    )}

                    {/* Strength selector */}
                    <div className="flex items-center gap-2">
                        <span className="text-[11px] font-mono text-[#9D9F9F] uppercase tracking-[0.1em]">
                            Strength:
                        </span>
                        <div className="flex gap-1">
                            {(['weak', 'medium', 'strong'] as const).map((s) => (
                                <button
                                    key={s}
                                    onClick={() => onUpdateStrength(s)}
                                    className={`px-2 py-1 rounded-lg text-[11px] font-medium transition-all ${artifact.strength === s
                                            ? 'text-white'
                                            : 'text-[#5B5F61] bg-[#F3F4EE] hover:bg-[#E5E6E3]'
                                        }`}
                                    style={{
                                        backgroundColor: artifact.strength === s ? STRENGTH_CONFIG[s].color : undefined,
                                    }}
                                >
                                    {STRENGTH_CONFIG[s].label}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                <button
                    onClick={onRemove}
                    className="opacity-0 group-hover:opacity-100 transition-opacity p-2 hover:bg-[#F3F4EE] rounded-lg"
                >
                    <X className="w-4 h-4 text-[#9D9F9F]" />
                </button>
            </div>
        </div>
    );
}

// Category section
function CategorySection({
    category,
    artifacts,
    onAdd,
    onRemove,
    onUpdateStrength,
}: {
    category: ProofCategory;
    artifacts: ProofArtifact[];
    onAdd: (artifact: Omit<ProofArtifact, 'id'>) => void;
    onRemove: (id: string) => void;
    onUpdateStrength: (id: string, strength: 'weak' | 'medium' | 'strong') => void;
}) {
    const [isAdding, setIsAdding] = useState(false);
    const [newTitle, setNewTitle] = useState('');
    const [newDescription, setNewDescription] = useState('');

    const config = CATEGORY_CONFIG[category];
    const Icon = config.icon;
    const categoryArtifacts = artifacts.filter((a) => a.category === category);

    const handleAdd = () => {
        if (!newTitle.trim()) return;
        onAdd({
            category,
            title: newTitle.trim(),
            description: newDescription.trim() || undefined,
            strength: 'medium',
            supportsClaims: [],
        });
        setNewTitle('');
        setNewDescription('');
        setIsAdding(false);
    };

    return (
        <div className="bg-[#FAFAF8] rounded-2xl p-6">
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                    <div
                        className="w-8 h-8 rounded-lg flex items-center justify-center"
                        style={{ backgroundColor: `${config.color}15` }}
                    >
                        <Icon className="w-4 h-4" style={{ color: config.color }} />
                    </div>
                    <span className="font-medium text-[#2D3538]">{config.label}</span>
                    <span className="text-[12px] text-[#9D9F9F]">({categoryArtifacts.length})</span>
                </div>
                <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setIsAdding(!isAdding)}
                    className="text-[#5B5F61] hover:text-[#2D3538]"
                >
                    <Plus className="w-4 h-4 mr-1" />
                    Add
                </Button>
            </div>

            {isAdding && (
                <div className="space-y-3 mb-4">
                    <input
                        type="text"
                        value={newTitle}
                        onChange={(e) => setNewTitle(e.target.value)}
                        placeholder="Proof title (e.g., '2x revenue increase')"
                        autoFocus
                        className="w-full bg-white border border-[#E5E6E3] rounded-xl px-4 py-3 text-[14px]"
                    />
                    <input
                        type="text"
                        value={newDescription}
                        onChange={(e) => setNewDescription(e.target.value)}
                        placeholder="Optional description..."
                        className="w-full bg-white border border-[#E5E6E3] rounded-xl px-4 py-3 text-[14px]"
                    />
                    <div className="flex gap-2">
                        <Button onClick={handleAdd} size="sm" className="bg-[#2D3538] text-white">
                            Add Proof
                        </Button>
                        <Button onClick={() => setIsAdding(false)} variant="ghost" size="sm">
                            Cancel
                        </Button>
                    </div>
                </div>
            )}

            <div className="space-y-3">
                {categoryArtifacts.map((artifact) => (
                    <ProofCard
                        key={artifact.id}
                        artifact={artifact}
                        onRemove={() => onRemove(artifact.id)}
                        onUpdateStrength={(s) => onUpdateStrength(artifact.id, s)}
                    />
                ))}
                {categoryArtifacts.length === 0 && !isAdding && (
                    <div className="text-center py-6 text-[#9D9F9F] text-[13px]">
                        No {config.label.toLowerCase()} added yet
                    </div>
                )}
            </div>
        </div>
    );
}

export function ProofStackScreen({
    proofArtifacts,
    onUpdate,
    onContinue,
    onBack,
}: ProofStackScreenProps) {
    const handleAdd = (artifact: Omit<ProofArtifact, 'id'>) => {
        onUpdate([...proofArtifacts, { ...artifact, id: uuidv4() }]);
    };

    const handleRemove = (id: string) => {
        onUpdate(proofArtifacts.filter((a) => a.id !== id));
    };

    const handleUpdateStrength = (id: string, strength: 'weak' | 'medium' | 'strong') => {
        onUpdate(
            proofArtifacts.map((a) => (a.id === id ? { ...a, strength } : a))
        );
    };

    // Calculate stats
    const totalProof = proofArtifacts.filter((a) => a.category !== 'not-yet').length;
    const strongProof = proofArtifacts.filter((a) => a.strength === 'strong').length;
    const notYetCount = proofArtifacts.filter((a) => a.category === 'not-yet').length;

    const categories: ProofCategory[] = ['metrics', 'case-stories', 'testimonials', 'screenshots', 'credentials', 'not-yet'];

    return (
        <div className="space-y-8">
            {/* Stats Header */}
            <div className="grid grid-cols-3 gap-4">
                <div className="bg-white border border-[#E5E6E3] rounded-xl p-5 text-center">
                    <span className="text-[32px] font-serif text-[#2D3538]">{totalProof}</span>
                    <p className="text-[12px] text-[#5B5F61] mt-1">Total Proof Items</p>
                </div>
                <div className="bg-white border border-[#E5E6E3] rounded-xl p-5 text-center">
                    <span className="text-[32px] font-serif text-[#22C55E]">{strongProof}</span>
                    <p className="text-[12px] text-[#5B5F61] mt-1">Strong Proof</p>
                </div>
                <div className="bg-white border border-[#E5E6E3] rounded-xl p-5 text-center">
                    <span className="text-[32px] font-serif text-[#F59E0B]">{notYetCount}</span>
                    <p className="text-[12px] text-[#5B5F61] mt-1">To Collect</p>
                </div>
            </div>

            {/* Info */}
            <div className="flex items-center gap-3 bg-[#2D3538]/5 rounded-xl px-5 py-4">
                <AlertCircle className="w-5 h-5 text-[#5B5F61] flex-shrink-0" />
                <p className="text-[14px] text-[#5B5F61]">
                    Claims without proof will be flagged as <span className="font-medium text-[#F59E0B]">"Unproven"</span>.
                    Mark items as "Not Yet" to generate proof collection requests.
                </p>
            </div>

            {/* Category Sections */}
            <div className="grid grid-cols-2 gap-6">
                {categories.map((category) => (
                    <CategorySection
                        key={category}
                        category={category}
                        artifacts={proofArtifacts}
                        onAdd={handleAdd}
                        onRemove={handleRemove}
                        onUpdateStrength={handleUpdateStrength}
                    />
                ))}
            </div>

            {/* Generate Proof Requests */}
            {notYetCount > 0 && (
                <div className="flex items-center justify-center">
                    <Button
                        variant="outline"
                        className="border-[#D7C9AE] text-[#2D3538] hover:bg-[#D7C9AE]/10"
                    >
                        <Sparkles className="w-4 h-4 mr-2" />
                        Generate proof collection requests
                    </Button>
                </div>
            )}

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
                    className="bg-[#2D3538] hover:bg-[#1A1D1E] text-white px-10 py-6 rounded-2xl text-[15px] font-medium"
                >
                    Continue
                </Button>
            </div>
        </div>
    );
}
