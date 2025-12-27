'use client';

import React, { useState } from 'react';
import {
    Check,
    AlertTriangle,
    AlertCircle,
    X,
    ChevronRight,
    HelpCircle,
    Sparkles
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Phase4Data, CategoryCandidate, PricingPosture } from '@/lib/foundation';

interface MarketFrameScreenProps {
    phase4: Phase4Data;
    onUpdate: (updates: Partial<Phase4Data>) => void;
    onContinue: () => void;
    onBack: () => void;
}

const PRICING_POSTURES: { value: PricingPosture; label: string; description: string }[] = [
    { value: 'premium', label: 'Premium', description: 'Top 20% pricing, luxury positioning' },
    { value: 'mid', label: 'Mid-Market', description: 'Competitive pricing, value for money' },
    { value: 'volume', label: 'Volume', description: 'Lower pricing, high volume play' },
];

const RISK_LABELS: Record<string, { label: string; color: string }> = {
    'too-broad': { label: 'Too Broad', color: 'text-amber-600 bg-amber-50' },
    'too-weird': { label: 'Too Niche', color: 'text-purple-600 bg-purple-50' },
    'too-crowded': { label: 'Crowded', color: 'text-red-600 bg-red-50' },
    'ok': { label: 'Clear Path', color: 'text-green-600 bg-green-50' },
};

export function MarketFrameScreen({
    phase4,
    onUpdate,
    onContinue,
    onBack
}: MarketFrameScreenProps) {
    const [selectedCategoryId, setSelectedCategoryId] = useState<string>(
        phase4.categoryCandidates?.find(c => c.isSelected)?.id || ''
    );
    const [antiCategoryInput, setAntiCategoryInput] = useState('');

    const handleCategorySelect = (categoryId: string) => {
        setSelectedCategoryId(categoryId);
        const updatedCandidates = phase4.categoryCandidates?.map(c => ({
            ...c,
            isSelected: c.id === categoryId
        }));
        const selectedCategory = updatedCandidates?.find(c => c.id === categoryId);

        onUpdate({
            categoryCandidates: updatedCandidates,
            marketCategory: selectedCategory ? {
                primary: selectedCategory.name,
                altLabels: [],
                whyThisContext: selectedCategory.buyerExpectations,
                risk: selectedCategory.risk
            } : phase4.marketCategory
        });
    };

    const handleAddAntiCategory = () => {
        if (!antiCategoryInput.trim()) return;
        onUpdate({
            antiCategories: [...(phase4.antiCategories || []), antiCategoryInput.trim()]
        });
        setAntiCategoryInput('');
    };

    const handleRemoveAntiCategory = (tag: string) => {
        onUpdate({
            antiCategories: phase4.antiCategories?.filter(t => t !== tag)
        });
    };

    const handlePricingPostureChange = (posture: PricingPosture) => {
        onUpdate({ pricingPosture: posture });
    };

    // Generate mock category candidates if none exist
    const categoryCandidates = phase4.categoryCandidates?.length
        ? phase4.categoryCandidates
        : [
            {
                id: 'cat-1',
                name: 'Marketing Operating System',
                definition: 'A unified platform that orchestrates all marketing activities from a single source of truth.',
                buyerExpectations: ['Strategic planning', 'Multi-channel execution', 'Performance tracking'],
                comparisonSet: ['HubSpot Marketing Hub', 'Marketo', 'Custom internal tools'],
                risks: ['New category creation required', 'May need market education'],
                risk: 'too-weird' as const,
                isSelected: false
            },
            {
                id: 'cat-2',
                name: 'Marketing Automation Platform',
                definition: 'Software that automates repetitive marketing tasks and workflows.',
                buyerExpectations: ['Email automation', 'Lead scoring', 'Campaign management'],
                comparisonSet: ['HubSpot', 'Mailchimp', 'ActiveCampaign', 'Klaviyo'],
                risks: ['Feature matrix competition', 'Price pressure from incumbents'],
                risk: 'too-crowded' as const,
                isSelected: false
            },
            {
                id: 'cat-3',
                name: 'GTM Intelligence Platform',
                definition: 'AI-powered system that provides strategic insights for go-to-market execution.',
                buyerExpectations: ['Market intelligence', 'Competitive analysis', 'Strategic recommendations'],
                comparisonSet: ['Gong', 'Chorus', '6sense'],
                risks: ['Enterprise-focused expectations', 'Long sales cycle'],
                risk: 'ok' as const,
                isSelected: false
            }
        ];

    return (
        <div className="space-y-8">
            {/* Header Context */}
            <div className="bg-[#F3F4EE] rounded-2xl p-6 border border-[#E5E6E3]">
                <div className="flex items-start gap-3">
                    <HelpCircle className="w-5 h-5 text-[#5B5F61] mt-0.5" />
                    <div>
                        <p className="text-sm text-[#2D3538]">
                            <strong>Why this matters:</strong> Category choice determines who you're compared against,
                            what buyers expect, and which budget you're competing for.
                        </p>
                        <div className="mt-3 flex flex-wrap gap-4 text-xs text-[#5B5F61]">
                            <span>• "When a buyer explains you to their boss, what do they call you?"</span>
                            <span>• "What budget line item would this come from?"</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Category Candidates */}
            <div>
                <h3 className="font-serif text-xl text-[#2D3538] mb-4">What are you?</h3>
                <p className="text-sm text-[#5B5F61] mb-6">
                    Based on your inputs, we see three possible category frames. Pick one.
                </p>

                <div className="space-y-4">
                    {categoryCandidates.map((category, index) => {
                        const isSelected = selectedCategoryId === category.id;
                        const riskInfo = RISK_LABELS[category.risk];

                        return (
                            <button
                                key={category.id}
                                onClick={() => handleCategorySelect(category.id)}
                                className={`w-full text-left bg-white border-2 rounded-2xl p-6 transition-all ${isSelected
                                        ? 'border-[#2D3538] shadow-sm'
                                        : 'border-[#E5E6E3] hover:border-[#C0C1BE]'
                                    }`}
                            >
                                <div className="flex items-start gap-4">
                                    <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${isSelected ? 'bg-[#2D3538] text-white' : 'bg-[#F3F4EE] text-[#2D3538]'
                                        }`}>
                                        {isSelected ? <Check className="w-5 h-5" /> : <span className="font-serif">{String.fromCharCode(65 + index)}</span>}
                                    </div>

                                    <div className="flex-1">
                                        <div className="flex items-center gap-3 mb-2">
                                            <h4 className="font-serif text-lg text-[#2D3538]">{category.name}</h4>
                                            <span className={`text-[10px] font-mono uppercase px-2 py-0.5 rounded ${riskInfo.color}`}>
                                                {riskInfo.label}
                                            </span>
                                        </div>

                                        <p className="text-sm text-[#5B5F61] mb-4">{category.definition}</p>

                                        <div className="grid grid-cols-2 gap-4 text-xs">
                                            <div>
                                                <span className="text-[#9D9F9F] uppercase tracking-wider">Buyers expect:</span>
                                                <ul className="mt-1 space-y-0.5">
                                                    {category.buyerExpectations.slice(0, 3).map((exp, i) => (
                                                        <li key={i} className="text-[#2D3538]">• {exp}</li>
                                                    ))}
                                                </ul>
                                            </div>
                                            <div>
                                                <span className="text-[#9D9F9F] uppercase tracking-wider">Compared against:</span>
                                                <ul className="mt-1 space-y-0.5">
                                                    {category.comparisonSet.slice(0, 3).map((comp, i) => (
                                                        <li key={i} className="text-[#2D3538]">• {comp}</li>
                                                    ))}
                                                </ul>
                                            </div>
                                        </div>

                                        {category.risks.length > 0 && (
                                            <div className="mt-4 flex items-start gap-2 text-xs text-amber-700 bg-amber-50 rounded-lg px-3 py-2">
                                                <AlertTriangle className="w-3.5 h-3.5 mt-0.5 flex-shrink-0" />
                                                <span>{category.risks[0]}</span>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </button>
                        );
                    })}
                </div>
            </div>

            {/* Anti-Category Tags */}
            <div>
                <h3 className="font-serif text-xl text-[#2D3538] mb-2">What you're NOT</h3>
                <p className="text-sm text-[#5B5F61] mb-4">
                    Explicitly exclude categories to prevent positioning confusion.
                </p>

                <div className="flex flex-wrap gap-2 mb-4">
                    {(phase4.antiCategories || []).map((tag) => (
                        <span
                            key={tag}
                            className="inline-flex items-center gap-1.5 bg-[#2D3538] text-white px-3 py-1.5 rounded-full text-sm"
                        >
                            NOT {tag}
                            <button
                                onClick={() => handleRemoveAntiCategory(tag)}
                                className="hover:bg-white/20 rounded-full p-0.5"
                            >
                                <X className="w-3 h-3" />
                            </button>
                        </span>
                    ))}
                </div>

                <div className="flex gap-2">
                    <input
                        type="text"
                        value={antiCategoryInput}
                        onChange={(e) => setAntiCategoryInput(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleAddAntiCategory()}
                        placeholder="e.g., CRM, agency, scheduler"
                        className="flex-1 px-4 py-3 bg-white border border-[#E5E6E3] rounded-xl text-sm focus:outline-none focus:border-[#2D3538]"
                    />
                    <Button
                        onClick={handleAddAntiCategory}
                        variant="outline"
                        className="border-[#2D3538] text-[#2D3538]"
                    >
                        Add
                    </Button>
                </div>
            </div>

            {/* Pricing Posture */}
            <div>
                <h3 className="font-serif text-xl text-[#2D3538] mb-2">Pricing Posture</h3>
                <p className="text-sm text-[#5B5F61] mb-4">
                    Where do you position on price? This affects category expectations.
                </p>

                <div className="grid grid-cols-3 gap-4">
                    {PRICING_POSTURES.map((posture) => (
                        <button
                            key={posture.value}
                            onClick={() => handlePricingPostureChange(posture.value)}
                            className={`p-4 rounded-xl border-2 text-left transition-all ${phase4.pricingPosture === posture.value
                                    ? 'border-[#2D3538] bg-[#2D3538] text-white'
                                    : 'border-[#E5E6E3] bg-white hover:border-[#C0C1BE]'
                                }`}
                        >
                            <span className={`text-sm font-medium ${phase4.pricingPosture === posture.value ? 'text-white' : 'text-[#2D3538]'
                                }`}>
                                {posture.label}
                            </span>
                            <p className={`text-xs mt-1 ${phase4.pricingPosture === posture.value ? 'text-white/70' : 'text-[#5B5F61]'
                                }`}>
                                {posture.description}
                            </p>
                        </button>
                    ))}
                </div>
            </div>

            {/* Downstream Impact */}
            {selectedCategoryId && (
                <div className="bg-[#F3F4EE] rounded-2xl p-6 border border-[#E5E6E3]">
                    <div className="flex items-center gap-2 mb-4">
                        <Sparkles className="w-4 h-4 text-[#5B5F61]" />
                        <span className="text-[10px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F]">
                            What changes downstream
                        </span>
                    </div>

                    <div className="grid grid-cols-3 gap-4 text-sm">
                        <div>
                            <span className="text-[#9D9F9F] text-xs">Competitor queries</span>
                            <p className="text-[#2D3538] mt-1">
                                Will search for {categoryCandidates.find(c => c.id === selectedCategoryId)?.comparisonSet?.length || 0} competitors
                            </p>
                        </div>
                        <div>
                            <span className="text-[#9D9F9F] text-xs">Perceptual map axes</span>
                            <p className="text-[#2D3538] mt-1">
                                Will suggest category-specific axes
                            </p>
                        </div>
                        <div>
                            <span className="text-[#9D9F9F] text-xs">Copy tone</span>
                            <p className="text-[#2D3538] mt-1">
                                {phase4.pricingPosture === 'premium' ? 'Luxury, exclusive' :
                                    phase4.pricingPosture === 'mid' ? 'Professional, confident' :
                                        'Accessible, friendly'}
                            </p>
                        </div>
                    </div>
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
                    disabled={!selectedCategoryId}
                    className="bg-[#2D3538] hover:bg-[#1A1D1E] text-white px-8"
                >
                    Continue <ChevronRight className="w-4 h-4 ml-1" />
                </Button>
            </div>
        </div>
    );
}
