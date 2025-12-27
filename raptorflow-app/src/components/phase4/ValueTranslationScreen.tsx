'use client';

import React, { useState } from 'react';
import {
    ChevronRight,
    ArrowRight,
    DollarSign,
    Heart,
    Users,
    Check,
    AlertCircle,
    Plus
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Phase4Data, UniqueAttribute, ValueClaim, ValueType, ProofHookType } from '@/lib/foundation';
import { v4 as uuidv4 } from 'uuid';

interface ValueTranslationScreenProps {
    phase4: Phase4Data;
    onUpdate: (updates: Partial<Phase4Data>) => void;
    onContinue: () => void;
    onBack: () => void;
}

const VALUE_TYPES: { type: ValueType; label: string; icon: React.ReactNode; description: string }[] = [
    { type: 'functional', label: 'Functional', icon: <DollarSign className="w-4 h-4" />, description: 'Time, money, or risk' },
    { type: 'emotional', label: 'Emotional', icon: <Heart className="w-4 h-4" />, description: 'Control, confidence, relief' },
    { type: 'social', label: 'Social', icon: <Users className="w-4 h-4" />, description: 'Status, competence signal' },
];

const PROOF_HOOKS: { type: ProofHookType; label: string }[] = [
    { type: 'metric', label: 'Metric' },
    { type: 'quote', label: 'Customer Quote' },
    { type: 'demo', label: 'Demo Artifact' },
    { type: 'benchmark', label: 'Benchmark' },
];

export function ValueTranslationScreen({
    phase4,
    onUpdate,
    onContinue,
    onBack
}: ValueTranslationScreenProps) {
    const [selectedAttributeId, setSelectedAttributeId] = useState<string | null>(null);
    const [generatedClaims, setGeneratedClaims] = useState<ValueClaim[]>([]);

    const attributes = phase4.uniqueAttributes?.slice(0, 8) || [];
    const valueClaims = phase4.valueClaims || [];

    // Generate claims for an attribute
    const generateClaimsForAttribute = (attr: UniqueAttribute) => {
        const claims: ValueClaim[] = [
            {
                id: uuidv4(),
                attributeId: attr.id,
                claimText: `Save hours every week with ${attr.attribute.toLowerCase()}`,
                valueType: 'functional',
                riskLevel: 'low',
                evidenceIds: [],
                isSelected: false
            },
            {
                id: uuidv4(),
                attributeId: attr.id,
                claimText: `Finally feel in control with ${attr.attribute.toLowerCase()}`,
                valueType: 'emotional',
                riskLevel: 'medium',
                evidenceIds: [],
                isSelected: false
            },
            {
                id: uuidv4(),
                attributeId: attr.id,
                claimText: `Look like a strategic leader with ${attr.attribute.toLowerCase()}`,
                valueType: 'social',
                riskLevel: 'high',
                evidenceIds: [],
                isSelected: false
            },
        ];
        setGeneratedClaims(claims);
    };

    const handleAttributeClick = (attr: UniqueAttribute) => {
        setSelectedAttributeId(attr.id);
        // Check if claims already exist for this attribute
        const existingClaims = valueClaims.filter(c => c.attributeId === attr.id);
        if (existingClaims.length > 0) {
            setGeneratedClaims(existingClaims);
        } else {
            generateClaimsForAttribute(attr);
        }
    };

    const handleSelectClaim = (claimId: string) => {
        const updated = generatedClaims.map(c => ({
            ...c,
            isSelected: c.id === claimId ? !c.isSelected : c.isSelected
        }));
        setGeneratedClaims(updated);
    };

    const handleProofHookChange = (claimId: string, hookType: ProofHookType) => {
        const updated = generatedClaims.map(c =>
            c.id === claimId ? { ...c, proofHook: hookType } : c
        );
        setGeneratedClaims(updated);
    };

    const handleSaveClaims = () => {
        const selectedClaims = generatedClaims.filter(c => c.isSelected);
        const existingOtherClaims = valueClaims.filter(c => c.attributeId !== selectedAttributeId);
        onUpdate({ valueClaims: [...existingOtherClaims, ...selectedClaims] });
        setSelectedAttributeId(null);
        setGeneratedClaims([]);
    };

    const getClaimsForAttribute = (attrId: string) => {
        return valueClaims.filter(c => c.attributeId === attrId);
    };

    const getRiskColor = (risk: string) => {
        switch (risk) {
            case 'low': return 'bg-green-100 text-green-700';
            case 'medium': return 'bg-amber-100 text-amber-700';
            case 'high': return 'bg-red-100 text-red-700';
            default: return 'bg-gray-100 text-gray-700';
        }
    };

    return (
        <div className="space-y-6">
            {/* Header Info */}
            <div className="bg-[#F3F4EE] rounded-2xl p-5 border border-[#E5E6E3]">
                <p className="text-sm text-[#5B5F61]">
                    <strong>Dunford Step:</strong> Customers don't care about features —
                    they care what it does for them. Translate each attribute into customer value.
                </p>
            </div>

            <div className="grid grid-cols-5 gap-6">
                {/* Left: Attributes List */}
                <div className="col-span-2 space-y-3">
                    <h3 className="font-serif text-lg text-[#2D3538] mb-4">Your Attributes</h3>

                    {attributes.map((attr) => {
                        const claims = getClaimsForAttribute(attr.id);
                        const isSelected = selectedAttributeId === attr.id;

                        return (
                            <button
                                key={attr.id}
                                onClick={() => handleAttributeClick(attr)}
                                className={`w-full text-left bg-white border-2 rounded-xl p-4 transition-all ${isSelected
                                        ? 'border-[#2D3538] shadow-sm'
                                        : 'border-[#E5E6E3] hover:border-[#C0C1BE]'
                                    }`}
                            >
                                <div className="flex items-start gap-3">
                                    <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${claims.length > 0 ? 'bg-green-100' : 'bg-[#F3F4EE]'
                                        }`}>
                                        {claims.length > 0 ? (
                                            <Check className="w-4 h-4 text-green-600" />
                                        ) : (
                                            <Plus className="w-4 h-4 text-[#9D9F9F]" />
                                        )}
                                    </div>
                                    <div className="flex-1">
                                        <p className="text-sm text-[#2D3538] font-medium">{attr.attribute}</p>
                                        <p className="text-xs text-[#5B5F61] mt-1">
                                            {claims.length > 0 ? `${claims.length} value claims` : 'No claims yet'}
                                        </p>
                                    </div>
                                    <ArrowRight className={`w-4 h-4 ${isSelected ? 'text-[#2D3538]' : 'text-[#9D9F9F]'}`} />
                                </div>
                            </button>
                        );
                    })}

                    {attributes.length === 0 && (
                        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-sm text-amber-700">
                            No attributes defined. Go back to add unique attributes first.
                        </div>
                    )}
                </div>

                {/* Right: Value Constructor */}
                <div className="col-span-3">
                    {selectedAttributeId ? (
                        <div className="bg-white border border-[#E5E6E3] rounded-2xl p-6">
                            <h3 className="font-serif text-lg text-[#2D3538] mb-2">Value Claims</h3>
                            <p className="text-sm text-[#5B5F61] mb-6">
                                Select 1-2 strongest value claims for this attribute
                            </p>

                            {/* Value Type Sections */}
                            <div className="space-y-6">
                                {VALUE_TYPES.map((vt) => {
                                    const typeClaims = generatedClaims.filter(c => c.valueType === vt.type);

                                    return (
                                        <div key={vt.type}>
                                            <div className="flex items-center gap-2 mb-3">
                                                <div className={`w-6 h-6 rounded-full flex items-center justify-center ${vt.type === 'functional' ? 'bg-blue-100 text-blue-600' :
                                                        vt.type === 'emotional' ? 'bg-pink-100 text-pink-600' :
                                                            'bg-purple-100 text-purple-600'
                                                    }`}>
                                                    {vt.icon}
                                                </div>
                                                <span className="text-sm font-medium text-[#2D3538]">{vt.label}</span>
                                                <span className="text-xs text-[#9D9F9F]">{vt.description}</span>
                                            </div>

                                            <div className="space-y-2 pl-8">
                                                {typeClaims.map((claim) => (
                                                    <div
                                                        key={claim.id}
                                                        className={`border-2 rounded-xl p-4 transition-all ${claim.isSelected
                                                                ? 'border-[#2D3538] bg-[#F3F4EE]'
                                                                : 'border-[#E5E6E3] hover:border-[#C0C1BE]'
                                                            }`}
                                                    >
                                                        <div className="flex items-start gap-3">
                                                            <button
                                                                onClick={() => handleSelectClaim(claim.id)}
                                                                className={`w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0 mt-0.5 ${claim.isSelected
                                                                        ? 'bg-[#2D3538] border-[#2D3538] text-white'
                                                                        : 'border-[#C0C1BE]'
                                                                    }`}
                                                            >
                                                                {claim.isSelected && <Check className="w-3 h-3" />}
                                                            </button>

                                                            <div className="flex-1">
                                                                <p className="text-sm text-[#2D3538]">{claim.claimText}</p>

                                                                {claim.isSelected && (
                                                                    <div className="mt-3 flex items-center gap-2">
                                                                        <span className="text-[10px] font-mono uppercase text-[#9D9F9F]">
                                                                            Proof hook:
                                                                        </span>
                                                                        <div className="flex gap-1">
                                                                            {PROOF_HOOKS.map((hook) => (
                                                                                <button
                                                                                    key={hook.type}
                                                                                    onClick={() => handleProofHookChange(claim.id, hook.type)}
                                                                                    className={`text-[10px] px-2 py-1 rounded transition-colors ${claim.proofHook === hook.type
                                                                                            ? 'bg-[#2D3538] text-white'
                                                                                            : 'bg-[#E5E6E3] text-[#5B5F61] hover:bg-[#C0C1BE]'
                                                                                        }`}
                                                                                >
                                                                                    {hook.label}
                                                                                </button>
                                                                            ))}
                                                                        </div>
                                                                    </div>
                                                                )}
                                                            </div>

                                                            <span className={`text-[10px] px-2 py-0.5 rounded ${getRiskColor(claim.riskLevel)}`}>
                                                                {claim.riskLevel}
                                                            </span>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>

                            {/* Save Button */}
                            <div className="mt-6 flex justify-end">
                                <Button
                                    onClick={handleSaveClaims}
                                    disabled={generatedClaims.filter(c => c.isSelected).length === 0}
                                    className="bg-[#2D3538] hover:bg-[#1A1D1E] text-white"
                                >
                                    Save Selected Claims
                                </Button>
                            </div>
                        </div>
                    ) : (
                        <div className="bg-[#F3F4EE] border border-[#E5E6E3] rounded-2xl p-10 text-center">
                            <ArrowRight className="w-8 h-8 text-[#C0C1BE] mx-auto mb-4" />
                            <p className="text-sm text-[#5B5F61]">
                                Select an attribute to generate value claims
                            </p>
                        </div>
                    )}
                </div>
            </div>

            {/* Summary */}
            <div className="bg-[#F3F4EE] rounded-2xl p-5 border border-[#E5E6E3]">
                <div className="flex items-center justify-between">
                    <span className="text-sm text-[#5B5F61]">
                        {valueClaims.length} value claims across {new Set(valueClaims.map(c => c.attributeId)).size} attributes
                    </span>
                    {valueClaims.filter(c => !c.proofHook).length > 0 && (
                        <span className="text-xs text-amber-600 flex items-center gap-1">
                            <AlertCircle className="w-3 h-3" />
                            {valueClaims.filter(c => !c.proofHook).length} claims need proof hooks
                        </span>
                    )}
                </div>
            </div>

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
