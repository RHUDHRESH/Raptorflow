'use client';

import React, { useState } from 'react';
import { Package, Clock, Shield, AlertCircle, Plus, X, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { OfferProfile, DeliveryModeType } from '@/lib/foundation';

interface OfferPackagingProps {
    offerProfile: OfferProfile | undefined;
    onUpdate: (profile: OfferProfile) => void;
    onContinue: () => void;
    onBack: () => void;
}

const DELIVERY_MODES: Array<{ id: DeliveryModeType; label: string; description: string; icon: React.ElementType }> = [
    {
        id: 'diy',
        label: 'DIY (Self-Serve)',
        description: 'Customer does it themselves with your tool/content',
        icon: Package
    },
    {
        id: 'done-with-you',
        label: 'Done With You',
        description: 'Collaborative work with guidance and support',
        icon: Shield
    },
    {
        id: 'done-for-you',
        label: 'Done For You',
        description: 'Full-service delivery, customer is hands-off',
        icon: Clock
    },
];

const RISK_POLICIES = [
    { id: 'pilot', label: 'Pilot Program', description: 'Try before committing fully' },
    { id: 'milestone-billing', label: 'Milestone Billing', description: 'Pay as milestones are hit' },
    { id: 'guarantee', label: 'Money-Back Guarantee', description: 'Full or partial refund policy' },
    { id: 'none', label: 'No Special Policy', description: "Standard terms, no special offer" },
];

export function OfferPackaging({
    offerProfile,
    onUpdate,
    onContinue,
    onBack,
}: OfferPackagingProps) {
    const [newPrerequisite, setNewPrerequisite] = useState('');

    const profile: OfferProfile = offerProfile || {
        deliveryMode: 'done-with-you',
        timeToFirstValue: 7,
        successPrerequisites: [],
        riskPolicy: 'none',
    };

    const handleDeliveryModeChange = (mode: DeliveryModeType) => {
        onUpdate({ ...profile, deliveryMode: mode });
    };

    const handleTTFVChange = (days: number) => {
        onUpdate({ ...profile, timeToFirstValue: days });
    };

    const handleRiskPolicyChange = (policy: OfferProfile['riskPolicy']) => {
        onUpdate({ ...profile, riskPolicy: policy });
    };

    const handleAddPrerequisite = () => {
        if (!newPrerequisite.trim()) return;
        onUpdate({
            ...profile,
            successPrerequisites: [...profile.successPrerequisites, newPrerequisite.trim()],
        });
        setNewPrerequisite('');
    };

    const handleRemovePrerequisite = (index: number) => {
        onUpdate({
            ...profile,
            successPrerequisites: profile.successPrerequisites.filter((_, i) => i !== index),
        });
    };

    // Format TTFV display
    const formatTTFV = (days: number): string => {
        if (days === 0) return 'Instant';
        if (days === 1) return 'Same day';
        if (days <= 7) return `${days} days`;
        if (days <= 14) return '1-2 weeks';
        if (days <= 30) return '2-4 weeks';
        return '1-3 months';
    };

    return (
        <div className="space-y-10">
            {/* Info Banner */}
            <div className="flex items-center gap-3 bg-[#2D3538]/5 rounded-xl px-5 py-4">
                <AlertCircle className="w-5 h-5 text-[#5B5F61] flex-shrink-0" />
                <p className="text-[14px] text-[#5B5F61]">
                    This is not a full pricing strategy — just enough to ensure your positioning doesn't promise the wrong thing.
                </p>
            </div>

            {/* Delivery Mode */}
            <div>
                <h3 className="font-medium text-[#2D3538] text-[18px] mb-2">Offer Shape</h3>
                <p className="text-[13px] text-[#5B5F61] mb-6">How do you deliver value?</p>

                <div className="grid grid-cols-3 gap-4">
                    {DELIVERY_MODES.map((mode) => {
                        const Icon = mode.icon;
                        const isSelected = profile.deliveryMode === mode.id;

                        return (
                            <button
                                key={mode.id}
                                onClick={() => handleDeliveryModeChange(mode.id)}
                                className={`relative text-left p-6 rounded-2xl border-2 transition-all ${isSelected
                                        ? 'border-[#2D3538] bg-white'
                                        : 'border-[#E5E6E3] bg-white hover:border-[#C0C1BE]'
                                    }`}
                            >
                                {isSelected && (
                                    <div className="absolute top-4 right-4 w-5 h-5 bg-[#2D3538] rounded-full flex items-center justify-center">
                                        <Check className="w-3 h-3 text-white" />
                                    </div>
                                )}
                                <Icon className={`w-6 h-6 mb-3 ${isSelected ? 'text-[#2D3538]' : 'text-[#9D9F9F]'}`} />
                                <h4 className="font-medium text-[#2D3538] mb-1">{mode.label}</h4>
                                <p className="text-[12px] text-[#5B5F61]">{mode.description}</p>
                            </button>
                        );
                    })}
                </div>
            </div>

            {/* Time to First Value */}
            <div className="bg-[#FAFAF8] rounded-2xl p-6">
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h3 className="font-medium text-[#2D3538] text-[18px]">Time to First Value</h3>
                        <p className="text-[13px] text-[#5B5F61] mt-1">
                            How quickly does your customer see results?
                        </p>
                    </div>
                    <div className="text-right">
                        <span className="text-[28px] font-serif text-[#2D3538]">
                            {formatTTFV(profile.timeToFirstValue)}
                        </span>
                    </div>
                </div>

                <Slider
                    value={[profile.timeToFirstValue]}
                    onValueChange={([v]) => handleTTFVChange(v)}
                    min={0}
                    max={90}
                    step={1}
                    className="w-full"
                />

                <div className="flex justify-between mt-2 text-[11px] text-[#9D9F9F]">
                    <span>Instant</span>
                    <span>Same day</span>
                    <span>1 week</span>
                    <span>1 month</span>
                    <span>3 months</span>
                </div>
            </div>

            {/* Risk Reversal */}
            <div>
                <h3 className="font-medium text-[#2D3538] text-[18px] mb-2">Risk Reversal</h3>
                <p className="text-[13px] text-[#5B5F61] mb-6">
                    Do you offer any de-risking options? (Skip if not applicable)
                </p>

                <div className="grid grid-cols-2 gap-3">
                    {RISK_POLICIES.map((policy) => {
                        const isSelected = profile.riskPolicy === policy.id;

                        return (
                            <button
                                key={policy.id}
                                onClick={() => handleRiskPolicyChange(policy.id as OfferProfile['riskPolicy'])}
                                className={`text-left px-5 py-4 rounded-xl border transition-all ${isSelected
                                        ? 'border-[#2D3538] bg-white'
                                        : 'border-[#E5E6E3] bg-white hover:border-[#C0C1BE]'
                                    }`}
                            >
                                <div className="flex items-center gap-3">
                                    <div className={`w-4 h-4 rounded-full border-2 flex items-center justify-center ${isSelected ? 'border-[#2D3538] bg-[#2D3538]' : 'border-[#C0C1BE]'
                                        }`}>
                                        {isSelected && <Check className="w-2.5 h-2.5 text-white" />}
                                    </div>
                                    <div>
                                        <h4 className="font-medium text-[#2D3538] text-[14px]">{policy.label}</h4>
                                        <p className="text-[11px] text-[#5B5F61]">{policy.description}</p>
                                    </div>
                                </div>
                            </button>
                        );
                    })}
                </div>
            </div>

            {/* Success Prerequisites */}
            <div>
                <h3 className="font-medium text-[#2D3538] text-[18px] mb-2">What Must Be True for Success?</h3>
                <p className="text-[13px] text-[#5B5F61] mb-4">
                    List 3-7 prerequisites that customers need for your solution to work.
                </p>

                <div className="space-y-2 mb-4">
                    {profile.successPrerequisites.map((prereq, index) => (
                        <div
                            key={index}
                            className="group flex items-center gap-3 bg-white border border-[#E5E6E3] rounded-xl px-4 py-3"
                        >
                            <div className="w-6 h-6 rounded-full bg-[#F3F4EE] flex items-center justify-center text-[11px] font-mono text-[#5B5F61]">
                                {index + 1}
                            </div>
                            <span className="flex-1 text-[14px] text-[#2D3538]">{prereq}</span>
                            <button
                                onClick={() => handleRemovePrerequisite(index)}
                                className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-[#F3F4EE] rounded-lg"
                            >
                                <X className="w-4 h-4 text-[#9D9F9F]" />
                            </button>
                        </div>
                    ))}
                </div>

                <div className="flex items-center gap-2">
                    <input
                        type="text"
                        value={newPrerequisite}
                        onChange={(e) => setNewPrerequisite(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleAddPrerequisite()}
                        placeholder="e.g., 'Must have a website' or 'Team of 2+ marketers'"
                        className="flex-1 bg-white border border-[#E5E6E3] rounded-xl px-4 py-3 text-[14px] text-[#2D3538] placeholder:text-[#9D9F9F]"
                    />
                    <Button
                        onClick={handleAddPrerequisite}
                        variant="outline"
                        size="icon"
                        className="h-12 w-12 rounded-xl border-[#E5E6E3]"
                    >
                        <Plus className="w-4 h-4" />
                    </Button>
                </div>

                {profile.successPrerequisites.length < 3 && (
                    <p className="text-[12px] text-[#F59E0B] mt-2">
                        Add at least {3 - profile.successPrerequisites.length} more prerequisite(s)
                    </p>
                )}
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
                    disabled={profile.successPrerequisites.length < 3}
                    className="bg-[#2D3538] hover:bg-[#1A1D1E] disabled:bg-[#9D9F9F] text-white px-10 py-6 rounded-2xl text-[15px] font-medium"
                >
                    Continue
                </Button>
            </div>
        </div>
    );
}
