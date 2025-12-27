'use client';

import React from 'react';
import {
    ChevronRight,
    Target,
    DollarSign,
    Zap,
    AlertTriangle,
    Star,
    XCircle,
    HelpCircle
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Phase4Data, WhoCareSegment } from '@/lib/foundation';
import { v4 as uuidv4 } from 'uuid';

interface WhoCareScreenProps {
    phase4: Phase4Data;
    onUpdate: (updates: Partial<Phase4Data>) => void;
    onContinue: () => void;
    onBack: () => void;
}

export function WhoCareScreen({
    phase4,
    onUpdate,
    onContinue,
    onBack
}: WhoCareScreenProps) {
    // Generate default segments if none exist
    const segments: WhoCareSegment[] = phase4.whoCareSegments?.length
        ? phase4.whoCareSegments
        : [
            {
                id: uuidv4(),
                name: 'Founder-led SMB',
                valueAlignment: ['Needs system, not chaos', 'Limited time/budget', 'Wants control'],
                triggerEvents: ['Missed revenue target', 'Competitor threat', 'Funding round'],
                budgetPlausibility: 'high',
                salesFriction: 'low',
                rank: 'unranked'
            },
            {
                id: uuidv4(),
                name: 'D2C Brand Marketing Manager',
                valueAlignment: ['Content velocity needed', 'Multi-channel coordination', 'Prove ROI'],
                triggerEvents: ['Product launch', 'Seasonal peak', 'Budget approval'],
                budgetPlausibility: 'medium',
                salesFriction: 'medium',
                rank: 'unranked'
            },
            {
                id: uuidv4(),
                name: 'Agency Owner',
                valueAlignment: ['Client retention', 'Margin improvement', 'Scale operations'],
                triggerEvents: ['New client win', 'Team expansion', 'Tech migration'],
                budgetPlausibility: 'high',
                salesFriction: 'medium',
                rank: 'unranked'
            },
            {
                id: uuidv4(),
                name: 'B2B SaaS Marketing Ops',
                valueAlignment: ['Pipeline contribution', 'Attribution clarity', 'Cross-team alignment'],
                triggerEvents: ['Reorg', 'New leadership', 'Tech consolidation'],
                budgetPlausibility: 'high',
                salesFriction: 'high',
                rank: 'unranked'
            },
        ];

    const handleRankChange = (segmentId: string, rank: WhoCareSegment['rank']) => {
        // If setting as primary, unset other primaries
        let updated = segments.map(s => {
            if (s.id === segmentId) {
                return { ...s, rank };
            }
            if (rank === 'primary' && s.rank === 'primary') {
                return { ...s, rank: 'secondary' as const };
            }
            return s;
        });

        onUpdate({ whoCareSegments: updated });
    };

    const primarySegment = segments.find(s => s.rank === 'primary');
    const secondarySegments = segments.filter(s => s.rank === 'secondary');
    const avoidSegments = segments.filter(s => s.rank === 'avoid');

    const getBudgetIcon = (plausibility: string) => {
        switch (plausibility) {
            case 'high': return <span className="text-green-600">$$$</span>;
            case 'medium': return <span className="text-amber-600">$$</span>;
            case 'low': return <span className="text-red-600">$</span>;
            default: return null;
        }
    };

    const getFrictionLabel = (friction: string) => {
        switch (friction) {
            case 'low': return { label: 'Fast close', color: 'text-green-600' };
            case 'medium': return { label: 'Some friction', color: 'text-amber-600' };
            case 'high': return { label: 'Long cycle', color: 'text-red-600' };
            default: return { label: '', color: '' };
        }
    };

    return (
        <div className="space-y-6">
            {/* Header Info */}
            <div className="bg-[#F3F4EE] rounded-2xl p-5 border border-[#E5E6E3]">
                <p className="text-sm text-[#5B5F61]">
                    <strong>Dunford Step:</strong> Identify who really cares about the value.
                    Not everyone is your customer — focus on the segments that care most.
                </p>
            </div>

            {/* Selection Summary */}
            <div className="grid grid-cols-3 gap-4">
                <div className={`rounded-xl p-4 border-2 ${primarySegment ? 'bg-[#2D3538] border-[#2D3538]' : 'bg-white border-dashed border-[#C0C1BE]'}`}>
                    <div className="flex items-center gap-2 mb-2">
                        <Star className={`w-4 h-4 ${primarySegment ? 'text-white' : 'text-[#9D9F9F]'}`} />
                        <span className={`text-[10px] font-mono uppercase tracking-wider ${primarySegment ? 'text-white/70' : 'text-[#9D9F9F]'}`}>
                            Primary
                        </span>
                    </div>
                    <p className={`text-sm font-medium ${primarySegment ? 'text-white' : 'text-[#9D9F9F]'}`}>
                        {primarySegment?.name || 'Select primary segment'}
                    </p>
                </div>

                <div className={`rounded-xl p-4 border ${secondarySegments.length > 0 ? 'bg-white border-[#2D3538]' : 'bg-white border-dashed border-[#C0C1BE]'}`}>
                    <div className="flex items-center gap-2 mb-2">
                        <Target className="w-4 h-4 text-[#5B5F61]" />
                        <span className="text-[10px] font-mono uppercase tracking-wider text-[#9D9F9F]">
                            Secondary
                        </span>
                    </div>
                    <p className="text-sm text-[#2D3538]">
                        {secondarySegments.length > 0
                            ? secondarySegments.map(s => s.name).join(', ')
                            : 'Select secondary segments'}
                    </p>
                </div>

                <div className={`rounded-xl p-4 border ${avoidSegments.length > 0 ? 'bg-red-50 border-red-200' : 'bg-white border-dashed border-[#C0C1BE]'}`}>
                    <div className="flex items-center gap-2 mb-2">
                        <XCircle className={`w-4 h-4 ${avoidSegments.length > 0 ? 'text-red-500' : 'text-[#9D9F9F]'}`} />
                        <span className={`text-[10px] font-mono uppercase tracking-wider ${avoidSegments.length > 0 ? 'text-red-500' : 'text-[#9D9F9F]'}`}>
                            Avoid
                        </span>
                    </div>
                    <p className={`text-sm ${avoidSegments.length > 0 ? 'text-red-700' : 'text-[#9D9F9F]'}`}>
                        {avoidSegments.length > 0
                            ? avoidSegments.map(s => s.name).join(', ')
                            : 'Mark segments to avoid'}
                    </p>
                </div>
            </div>

            {/* Segment Cards */}
            <div className="grid grid-cols-2 gap-4">
                {segments.map((segment) => {
                    const frictionInfo = getFrictionLabel(segment.salesFriction);

                    return (
                        <div
                            key={segment.id}
                            className={`bg-white border-2 rounded-2xl p-5 transition-all ${segment.rank === 'primary' ? 'border-[#2D3538] shadow-sm' :
                                    segment.rank === 'avoid' ? 'border-red-300 bg-red-50/50' :
                                        segment.rank === 'secondary' ? 'border-[#C0C1BE]' :
                                            'border-[#E5E6E3]'
                                }`}
                        >
                            {/* Header */}
                            <div className="flex items-start justify-between mb-4">
                                <div>
                                    <h4 className="font-serif text-lg text-[#2D3538]">{segment.name}</h4>
                                    <div className="flex items-center gap-3 mt-1">
                                        <span className="text-xs text-[#5B5F61] flex items-center gap-1">
                                            <DollarSign className="w-3 h-3" />
                                            Budget: {getBudgetIcon(segment.budgetPlausibility)}
                                        </span>
                                        <span className={`text-xs flex items-center gap-1 ${frictionInfo.color}`}>
                                            <Zap className="w-3 h-3" />
                                            {frictionInfo.label}
                                        </span>
                                    </div>
                                </div>

                                {segment.rank === 'primary' && (
                                    <Star className="w-5 h-5 text-[#2D3538] fill-[#2D3538]" />
                                )}
                            </div>

                            {/* Value Alignment */}
                            <div className="mb-4">
                                <span className="text-[10px] font-mono uppercase tracking-wider text-[#9D9F9F] block mb-2">
                                    Why they care
                                </span>
                                <ul className="space-y-1">
                                    {segment.valueAlignment.map((item, i) => (
                                        <li key={i} className="text-xs text-[#5B5F61] flex items-start gap-2">
                                            <span className="text-[#2D3538]">•</span>
                                            {item}
                                        </li>
                                    ))}
                                </ul>
                            </div>

                            {/* Trigger Events */}
                            <div className="mb-4">
                                <span className="text-[10px] font-mono uppercase tracking-wider text-[#9D9F9F] block mb-2">
                                    Trigger events
                                </span>
                                <div className="flex flex-wrap gap-1">
                                    {segment.triggerEvents.map((trigger, i) => (
                                        <span key={i} className="text-[10px] bg-[#F3F4EE] text-[#5B5F61] px-2 py-1 rounded">
                                            {trigger}
                                        </span>
                                    ))}
                                </div>
                            </div>

                            {/* Rank Buttons */}
                            <div className="flex gap-2 pt-4 border-t border-[#E5E6E3]">
                                <button
                                    onClick={() => handleRankChange(segment.id, 'primary')}
                                    className={`flex-1 py-2 rounded-lg text-xs font-medium transition-colors ${segment.rank === 'primary'
                                            ? 'bg-[#2D3538] text-white'
                                            : 'bg-[#F3F4EE] text-[#5B5F61] hover:bg-[#E5E6E3]'
                                        }`}
                                >
                                    Primary
                                </button>
                                <button
                                    onClick={() => handleRankChange(segment.id, 'secondary')}
                                    className={`flex-1 py-2 rounded-lg text-xs font-medium transition-colors ${segment.rank === 'secondary'
                                            ? 'bg-[#2D3538] text-white'
                                            : 'bg-[#F3F4EE] text-[#5B5F61] hover:bg-[#E5E6E3]'
                                        }`}
                                >
                                    Secondary
                                </button>
                                <button
                                    onClick={() => handleRankChange(segment.id, 'avoid')}
                                    className={`flex-1 py-2 rounded-lg text-xs font-medium transition-colors ${segment.rank === 'avoid'
                                            ? 'bg-red-500 text-white'
                                            : 'bg-[#F3F4EE] text-[#5B5F61] hover:bg-red-50'
                                        }`}
                                >
                                    Avoid
                                </button>
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Downstream Info */}
            {primarySegment && (
                <div className="bg-[#F3F4EE] rounded-2xl p-5 border border-[#E5E6E3]">
                    <div className="flex items-center gap-2 mb-3">
                        <HelpCircle className="w-4 h-4 text-[#5B5F61]" />
                        <span className="text-[10px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F]">
                            What this means
                        </span>
                    </div>
                    <p className="text-sm text-[#5B5F61]">
                        <strong>{primarySegment.name}</strong> becomes your "For whom" in positioning statements.
                        Their trigger events ({primarySegment.triggerEvents.slice(0, 2).join(', ')})
                        will shape campaign timing. Phase 5 will deep-dive into this ICP.
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
                    disabled={!primarySegment}
                    className="bg-[#2D3538] hover:bg-[#1A1D1E] text-white px-8"
                >
                    Continue <ChevronRight className="w-4 h-4 ml-1" />
                </Button>
            </div>
        </div>
    );
}
