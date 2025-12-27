'use client';

import React, { useState } from 'react';
import { Link2, Plus, X, Check, AlertCircle, ChevronDown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { VPCData, VPCPain, VPCGain, VPCReliever, VPCCreator } from '@/lib/foundation';
import { v4 as uuidv4 } from 'uuid';

interface VPCSolutionMapProps {
    vpc: VPCData;
    proofArtifacts?: Array<{ id: string; title: string }>;
    onUpdate: (vpc: VPCData) => void;
    onContinue: () => void;
    onBack: () => void;
}

// Fit meter component
function FitMeter({ score, gaps }: { score: number; gaps: string[] }) {
    const color = score >= 70 ? '#22C55E' : score >= 40 ? '#F59E0B' : '#EF4444';

    return (
        <div className="bg-white border border-[#E5E6E3] rounded-2xl p-6">
            <div className="flex items-center justify-between mb-4">
                <span className="text-[11px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F]">
                    Fit Coverage
                </span>
                <span className="text-[24px] font-serif font-medium" style={{ color }}>
                    {score}%
                </span>
            </div>
            <div className="h-2 bg-[#E5E6E3] rounded-full overflow-hidden mb-4">
                <div
                    className="h-full rounded-full transition-all duration-500"
                    style={{ width: `${score}%`, backgroundColor: color }}
                />
            </div>
            {gaps.length > 0 && (
                <div className="flex items-center gap-2 text-[12px] text-[#F59E0B]">
                    <AlertCircle className="w-4 h-4" />
                    <span>{gaps.length} pains not addressed</span>
                </div>
            )}
        </div>
    );
}

// Pain Reliever card
function RelieverCard({
    reliever,
    pain,
    onRemove,
    onLinkPain,
    availablePains,
}: {
    reliever: VPCReliever;
    pain?: VPCPain;
    onRemove: () => void;
    onLinkPain: (painId: string) => void;
    availablePains: VPCPain[];
}) {
    const [showDropdown, setShowDropdown] = useState(false);

    return (
        <div className="group bg-white border border-[#E5E6E3] rounded-xl p-4 hover:shadow-sm transition-all">
            <div className="flex items-start gap-3">
                <div className="flex-1 min-w-0">
                    <p className="text-[14px] text-[#2D3538] mb-2">{reliever.text}</p>

                    {/* Linked Pain */}
                    <div className="relative">
                        <button
                            onClick={() => setShowDropdown(!showDropdown)}
                            className="flex items-center gap-2 text-[12px] text-[#5B5F61] hover:text-[#2D3538] transition-colors"
                        >
                            <Link2 className="w-3.5 h-3.5" />
                            {pain ? (
                                <span className="truncate max-w-[200px]">Addresses: {pain.text}</span>
                            ) : (
                                <span className="text-[#F59E0B]">Link to pain</span>
                            )}
                            <ChevronDown className="w-3 h-3" />
                        </button>

                        {showDropdown && (
                            <div className="absolute top-full left-0 mt-2 w-[300px] bg-white border border-[#E5E6E3] rounded-xl shadow-lg z-10 max-h-[200px] overflow-y-auto">
                                {availablePains.map((p) => (
                                    <button
                                        key={p.id}
                                        onClick={() => {
                                            onLinkPain(p.id);
                                            setShowDropdown(false);
                                        }}
                                        className={`w-full text-left px-4 py-3 text-[13px] hover:bg-[#F3F4EE] transition-colors ${p.id === reliever.painId ? 'bg-[#F3F4EE]' : ''
                                            }`}
                                    >
                                        <span className="text-[#2D3538]">{p.text}</span>
                                    </button>
                                ))}
                                {availablePains.length === 0 && (
                                    <div className="px-4 py-3 text-[13px] text-[#9D9F9F]">
                                        No pains available
                                    </div>
                                )}
                            </div>
                        )}
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

// Gain Creator card
function CreatorCard({
    creator,
    gain,
    onRemove,
    onLinkGain,
    availableGains,
}: {
    creator: VPCCreator;
    gain?: VPCGain;
    onRemove: () => void;
    onLinkGain: (gainId: string) => void;
    availableGains: VPCGain[];
}) {
    const [showDropdown, setShowDropdown] = useState(false);

    return (
        <div className="group bg-white border border-[#E5E6E3] rounded-xl p-4 hover:shadow-sm transition-all">
            <div className="flex items-start gap-3">
                <div className="flex-1 min-w-0">
                    <p className="text-[14px] text-[#2D3538] mb-2">{creator.text}</p>

                    {/* Linked Gain */}
                    <div className="relative">
                        <button
                            onClick={() => setShowDropdown(!showDropdown)}
                            className="flex items-center gap-2 text-[12px] text-[#5B5F61] hover:text-[#2D3538] transition-colors"
                        >
                            <Link2 className="w-3.5 h-3.5" />
                            {gain ? (
                                <span className="truncate max-w-[200px]">Creates: {gain.text}</span>
                            ) : (
                                <span className="text-[#F59E0B]">Link to gain</span>
                            )}
                            <ChevronDown className="w-3 h-3" />
                        </button>

                        {showDropdown && (
                            <div className="absolute top-full left-0 mt-2 w-[300px] bg-white border border-[#E5E6E3] rounded-xl shadow-lg z-10 max-h-[200px] overflow-y-auto">
                                {availableGains.map((g) => (
                                    <button
                                        key={g.id}
                                        onClick={() => {
                                            onLinkGain(g.id);
                                            setShowDropdown(false);
                                        }}
                                        className={`w-full text-left px-4 py-3 text-[13px] hover:bg-[#F3F4EE] transition-colors ${g.id === creator.gainId ? 'bg-[#F3F4EE]' : ''
                                            }`}
                                    >
                                        <span className="text-[#2D3538]">{g.text}</span>
                                    </button>
                                ))}
                                {availableGains.length === 0 && (
                                    <div className="px-4 py-3 text-[13px] text-[#9D9F9F]">
                                        No gains available
                                    </div>
                                )}
                            </div>
                        )}
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

export function VPCSolutionMap({
    vpc,
    proofArtifacts = [],
    onUpdate,
    onContinue,
    onBack,
}: VPCSolutionMapProps) {
    const [newReliever, setNewReliever] = useState('');
    const [newCreator, setNewCreator] = useState('');
    const [isAddingReliever, setIsAddingReliever] = useState(false);
    const [isAddingCreator, setIsAddingCreator] = useState(false);

    const handleAddReliever = () => {
        if (!newReliever.trim()) return;
        const reliever: VPCReliever = {
            id: uuidv4(),
            text: newReliever.trim(),
            painId: '',
        };
        onUpdate({
            ...vpc,
            valueMap: {
                ...vpc.valueMap,
                painRelievers: [...vpc.valueMap.painRelievers, reliever],
            },
        });
        setNewReliever('');
        setIsAddingReliever(false);
    };

    const handleRemoveReliever = (id: string) => {
        onUpdate({
            ...vpc,
            valueMap: {
                ...vpc.valueMap,
                painRelievers: vpc.valueMap.painRelievers.filter((r) => r.id !== id),
            },
        });
    };

    const handleLinkRelieverPain = (relieverId: string, painId: string) => {
        onUpdate({
            ...vpc,
            valueMap: {
                ...vpc.valueMap,
                painRelievers: vpc.valueMap.painRelievers.map((r) =>
                    r.id === relieverId ? { ...r, painId } : r
                ),
            },
        });
    };

    const handleAddCreator = () => {
        if (!newCreator.trim()) return;
        const creator: VPCCreator = {
            id: uuidv4(),
            text: newCreator.trim(),
            gainId: '',
        };
        onUpdate({
            ...vpc,
            valueMap: {
                ...vpc.valueMap,
                gainCreators: [...vpc.valueMap.gainCreators, creator],
            },
        });
        setNewCreator('');
        setIsAddingCreator(false);
    };

    const handleRemoveCreator = (id: string) => {
        onUpdate({
            ...vpc,
            valueMap: {
                ...vpc.valueMap,
                gainCreators: vpc.valueMap.gainCreators.filter((c) => c.id !== id),
            },
        });
    };

    const handleLinkCreatorGain = (creatorId: string, gainId: string) => {
        onUpdate({
            ...vpc,
            valueMap: {
                ...vpc.valueMap,
                gainCreators: vpc.valueMap.gainCreators.map((c) =>
                    c.id === creatorId ? { ...c, gainId } : c
                ),
            },
        });
    };

    return (
        <div className="space-y-8">
            {/* Fit Meter */}
            <FitMeter score={vpc.fitCoverage.score} gaps={vpc.fitCoverage.gaps} />

            {/* Products & Services */}
            <div className="bg-[#FAFAF8] rounded-2xl p-6">
                <h3 className="text-[11px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-4">
                    Products & Services
                </h3>
                <div className="flex flex-wrap gap-2">
                    {vpc.valueMap.productsServices.map((ps, index) => (
                        <span
                            key={index}
                            className="inline-flex items-center bg-white border border-[#E5E6E3] rounded-xl px-4 py-2 text-[14px] text-[#2D3538]"
                        >
                            {ps}
                        </span>
                    ))}
                    {vpc.valueMap.productsServices.length === 0 && (
                        <span className="text-[14px] text-[#9D9F9F]">No products/services defined</span>
                    )}
                </div>
            </div>

            {/* Two Column Layout */}
            <div className="grid grid-cols-2 gap-6">
                {/* Pain Relievers */}
                <div className="space-y-4">
                    <div className="flex items-center justify-between">
                        <h3 className="font-medium text-[#2D3538]">Pain Relievers</h3>
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setIsAddingReliever(!isAddingReliever)}
                            className="text-[#5B5F61] hover:text-[#2D3538]"
                        >
                            <Plus className="w-4 h-4 mr-1" />
                            Add
                        </Button>
                    </div>

                    {isAddingReliever && (
                        <div className="flex items-center gap-2">
                            <input
                                type="text"
                                value={newReliever}
                                onChange={(e) => setNewReliever(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleAddReliever()}
                                placeholder="How does your solution relieve pain?"
                                autoFocus
                                className="flex-1 bg-white border border-[#E5E6E3] rounded-xl px-4 py-3 text-[14px]"
                            />
                            <Button onClick={handleAddReliever} size="sm" className="bg-[#2D3538] text-white">
                                Add
                            </Button>
                        </div>
                    )}

                    <div className="space-y-3">
                        {vpc.valueMap.painRelievers.map((reliever) => (
                            <RelieverCard
                                key={reliever.id}
                                reliever={reliever}
                                pain={vpc.customerProfile.pains.find((p) => p.id === reliever.painId)}
                                onRemove={() => handleRemoveReliever(reliever.id)}
                                onLinkPain={(painId) => handleLinkRelieverPain(reliever.id, painId)}
                                availablePains={vpc.customerProfile.pains}
                            />
                        ))}
                        {vpc.valueMap.painRelievers.length === 0 && !isAddingReliever && (
                            <div className="text-center py-8 text-[#9D9F9F] text-[14px] bg-[#FAFAF8] rounded-xl">
                                No pain relievers defined
                            </div>
                        )}
                    </div>
                </div>

                {/* Gain Creators */}
                <div className="space-y-4">
                    <div className="flex items-center justify-between">
                        <h3 className="font-medium text-[#2D3538]">Gain Creators</h3>
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setIsAddingCreator(!isAddingCreator)}
                            className="text-[#5B5F61] hover:text-[#2D3538]"
                        >
                            <Plus className="w-4 h-4 mr-1" />
                            Add
                        </Button>
                    </div>

                    {isAddingCreator && (
                        <div className="flex items-center gap-2">
                            <input
                                type="text"
                                value={newCreator}
                                onChange={(e) => setNewCreator(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleAddCreator()}
                                placeholder="How does your solution create gains?"
                                autoFocus
                                className="flex-1 bg-white border border-[#E5E6E3] rounded-xl px-4 py-3 text-[14px]"
                            />
                            <Button onClick={handleAddCreator} size="sm" className="bg-[#2D3538] text-white">
                                Add
                            </Button>
                        </div>
                    )}

                    <div className="space-y-3">
                        {vpc.valueMap.gainCreators.map((creator) => (
                            <CreatorCard
                                key={creator.id}
                                creator={creator}
                                gain={vpc.customerProfile.gains.find((g) => g.id === creator.gainId)}
                                onRemove={() => handleRemoveCreator(creator.id)}
                                onLinkGain={(gainId) => handleLinkCreatorGain(creator.id, gainId)}
                                availableGains={vpc.customerProfile.gains}
                            />
                        ))}
                        {vpc.valueMap.gainCreators.length === 0 && !isAddingCreator && (
                            <div className="text-center py-8 text-[#9D9F9F] text-[14px] bg-[#FAFAF8] rounded-xl">
                                No gain creators defined
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Unlinked Warning */}
            {(vpc.valueMap.painRelievers.some((r) => !r.painId) ||
                vpc.valueMap.gainCreators.some((c) => !c.gainId)) && (
                    <div className="flex items-center gap-3 bg-[#F59E0B]/10 rounded-xl px-5 py-4">
                        <AlertCircle className="w-5 h-5 text-[#F59E0B] flex-shrink-0" />
                        <p className="text-[14px] text-[#5B5F61]">
                            Some items are not linked — features without customer purpose may not resonate.
                        </p>
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
