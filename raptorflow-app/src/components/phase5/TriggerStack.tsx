'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
    Zap, TrendingUp, Briefcase, DollarSign, RefreshCw,
    Shield, Plus, Check, X, ExternalLink, Search
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { TriggerSignal, IntentSignal } from '@/lib/foundation';

interface TriggerStackProps {
    triggers: TriggerSignal[];
    intentSignals: IntentSignal[];
    onUpdateTrigger: (id: string, updates: Partial<TriggerSignal>) => void;
    onAddTrigger: (trigger: Omit<TriggerSignal, 'id'>) => void;
    onConfirmTop3: (ids: string[]) => void;
    confirmedIds: string[];
}

const TRIGGER_TEMPLATES: Omit<TriggerSignal, 'id' | 'isConfirmed'>[] = [
    {
        name: 'New Marketing Hire',
        description: 'Company hires Head of Marketing, CMO, or Marketing Manager',
        strength: 5,
        detectionMethods: ['LinkedIn job posts', 'LinkedIn profile changes', 'Company news'],
        intentKeywords: ['hiring marketing', 'head of marketing', 'marketing manager']
    },
    {
        name: 'Funding Round',
        description: 'Company raises Seed, Series A, B, or growth capital',
        strength: 5,
        detectionMethods: ['Crunchbase alerts', 'TechCrunch', 'LinkedIn announcements'],
        intentKeywords: ['raised funding', 'series a', 'seed round', 'growth capital']
    },
    {
        name: 'Revenue Plateau',
        description: 'Signs of stalled growth or pivot discussions',
        strength: 4,
        detectionMethods: ['Founder tweets', 'Podcast appearances', 'Blog posts'],
        intentKeywords: ['growth challenge', 'pivot', 'new direction', 'next phase']
    },
    {
        name: 'Product Launch',
        description: 'Upcoming or recent product/feature launch needing marketing',
        strength: 4,
        detectionMethods: ['Product Hunt', 'Press releases', 'Social announcements'],
        intentKeywords: ['launching', 'new product', 'coming soon', 'beta']
    },
    {
        name: 'Tool Migration',
        description: 'Switching marketing stack or evaluating alternatives',
        strength: 3,
        detectionMethods: ['G2/Capterra reviews', 'Community discussions', 'Job posts'],
        intentKeywords: ['looking for alternative', 'switching from', 'replacing']
    },
    {
        name: 'Compliance Deadline',
        description: 'Regulatory or industry compliance requirements approaching',
        strength: 3,
        detectionMethods: ['Industry news', 'Regulatory calendars', 'LinkedIn discussions'],
        intentKeywords: ['compliance', 'regulation', 'deadline', 'requirement']
    }
];

const STRENGTH_COLORS = {
    5: 'bg-green-500',
    4: 'bg-green-400',
    3: 'bg-yellow-500',
    2: 'bg-yellow-400',
    1: 'bg-red-400'
};

function TriggerCard({
    trigger,
    isConfirmed,
    onConfirm,
    onUpdate,
    index
}: {
    trigger: TriggerSignal;
    isConfirmed: boolean;
    onConfirm: () => void;
    onUpdate: (updates: Partial<TriggerSignal>) => void;
    index: number;
}) {
    const [isEditing, setIsEditing] = useState(false);

    return (
        <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.05 }}
            className={`bg-white border-2 rounded-2xl overflow-hidden ${isConfirmed ? 'border-[#2D3538]' : 'border-[#E5E6E3]'
                }`}
        >
            {/* Header */}
            <div className="flex items-center justify-between p-5 border-b border-[#E5E6E3]">
                <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-[#F3F4EE] rounded-xl flex items-center justify-center">
                        <Zap className="w-6 h-6 text-[#2D3538]" />
                    </div>
                    <div>
                        <h3 className="font-medium text-[#2D3538]">{trigger.name}</h3>
                        <p className="text-sm text-[#5B5F61]">{trigger.description}</p>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    {/* Strength */}
                    <div className="text-right">
                        <span className="text-[9px] font-mono uppercase text-[#9D9F9F] block">Strength</span>
                        <div className="flex items-center gap-1 mt-1">
                            {[1, 2, 3, 4, 5].map(i => (
                                <div
                                    key={i}
                                    className={`w-2 h-4 rounded-sm ${i <= trigger.strength
                                            ? STRENGTH_COLORS[trigger.strength as keyof typeof STRENGTH_COLORS]
                                            : 'bg-[#E5E6E3]'
                                        }`}
                                />
                            ))}
                        </div>
                    </div>

                    {/* Confirm Toggle */}
                    <button
                        onClick={onConfirm}
                        className={`w-10 h-10 rounded-xl flex items-center justify-center transition-all ${isConfirmed
                                ? 'bg-[#2D3538] text-white'
                                : 'bg-[#F3F4EE] text-[#9D9F9F] hover:bg-[#E5E6E3]'
                            }`}
                    >
                        <Check className="w-5 h-5" />
                    </button>
                </div>
            </div>

            {/* Detection Methods */}
            <div className="p-5 bg-[#FAFAF8]">
                <span className="text-[10px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-3 block">
                    Where to Detect
                </span>
                <div className="flex flex-wrap gap-2">
                    {trigger.detectionMethods.map((method, i) => (
                        <div
                            key={i}
                            className="flex items-center gap-1.5 bg-white border border-[#E5E6E3] rounded-lg px-3 py-1.5"
                        >
                            <Search className="w-3 h-3 text-[#9D9F9F]" />
                            <span className="text-xs text-[#2D3538]">{method}</span>
                        </div>
                    ))}
                </div>
            </div>

            {/* Intent Keywords */}
            <div className="p-5 border-t border-[#E5E6E3]">
                <span className="text-[10px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-3 block">
                    Intent Keywords (for Radar)
                </span>
                <div className="flex flex-wrap gap-2">
                    {trigger.intentKeywords.map((keyword, i) => (
                        <span
                            key={i}
                            className="text-xs bg-[#2D3538] text-white rounded-lg px-3 py-1.5"
                        >
                            "{keyword}"
                        </span>
                    ))}
                </div>
            </div>
        </motion.div>
    );
}

export function TriggerStack({
    triggers,
    intentSignals,
    onUpdateTrigger,
    onAddTrigger,
    onConfirmTop3,
    confirmedIds
}: TriggerStackProps) {
    const [showAddForm, setShowAddForm] = useState(false);
    const [newTrigger, setNewTrigger] = useState({
        name: '',
        description: '',
        strength: 3,
        detectionMethods: [''],
        intentKeywords: ['']
    });

    const handleConfirmToggle = (id: string) => {
        if (confirmedIds.includes(id)) {
            onConfirmTop3(confirmedIds.filter(cid => cid !== id));
        } else if (confirmedIds.length < 3) {
            onConfirmTop3([...confirmedIds, id]);
        }
    };

    const handleAddTrigger = () => {
        onAddTrigger({
            ...newTrigger,
            isConfirmed: false
        });
        setNewTrigger({
            name: '',
            description: '',
            strength: 3,
            detectionMethods: [''],
            intentKeywords: ['']
        });
        setShowAddForm(false);
    };

    // Combine provided triggers with templates if empty
    const displayTriggers = triggers.length > 0
        ? triggers
        : TRIGGER_TEMPLATES.map((t, i) => ({ ...t, id: `template-${i}`, isConfirmed: false }));

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-start gap-3 p-4 bg-[#F3F4EE] rounded-xl flex-1 mr-4">
                    <Zap className="w-5 h-5 text-[#2D3538] flex-shrink-0 mt-0.5" />
                    <p className="text-sm text-[#5B5F61]">
                        <strong className="text-[#2D3538]">Trigger Stack</strong> — Events that create urgency
                        and how RaptorFlow will detect them. Confirm your <strong>top 3</strong> most relevant triggers.
                    </p>
                </div>
                <Button
                    variant="outline"
                    onClick={() => setShowAddForm(!showAddForm)}
                    className="rounded-xl"
                >
                    <Plus className="w-4 h-4 mr-2" />
                    Add Trigger
                </Button>
            </div>

            {/* Selection Status */}
            <div className="flex items-center gap-4 p-4 bg-[#2D3538] rounded-2xl">
                <div className="flex items-center gap-2">
                    {[1, 2, 3].map(i => (
                        <div
                            key={i}
                            className={`w-8 h-8 rounded-lg flex items-center justify-center ${confirmedIds.length >= i ? 'bg-white text-[#2D3538]' : 'bg-white/20 text-white/60'
                                }`}
                        >
                            {confirmedIds.length >= i ? <Check className="w-4 h-4" /> : i}
                        </div>
                    ))}
                </div>
                <span className="text-white/80 text-sm">
                    {confirmedIds.length}/3 triggers confirmed
                </span>
            </div>

            {/* Add Form */}
            {showAddForm && (
                <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    className="bg-white border border-[#E5E6E3] rounded-2xl p-6 space-y-4"
                >
                    <h4 className="font-medium text-[#2D3538]">Add Custom Trigger</h4>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="text-sm text-[#5B5F61] mb-2 block">Trigger Name</label>
                            <input
                                type="text"
                                value={newTrigger.name}
                                onChange={(e) => setNewTrigger({ ...newTrigger, name: e.target.value })}
                                className="w-full border border-[#E5E6E3] rounded-xl px-4 py-2 focus:outline-none focus:border-[#2D3538]"
                                placeholder="e.g., New CEO Appointment"
                            />
                        </div>
                        <div>
                            <label className="text-sm text-[#5B5F61] mb-2 block">Strength (1-5)</label>
                            <input
                                type="number"
                                min={1}
                                max={5}
                                value={newTrigger.strength}
                                onChange={(e) => setNewTrigger({ ...newTrigger, strength: parseInt(e.target.value) || 3 })}
                                className="w-full border border-[#E5E6E3] rounded-xl px-4 py-2 focus:outline-none focus:border-[#2D3538]"
                            />
                        </div>
                    </div>

                    <div>
                        <label className="text-sm text-[#5B5F61] mb-2 block">Description</label>
                        <input
                            type="text"
                            value={newTrigger.description}
                            onChange={(e) => setNewTrigger({ ...newTrigger, description: e.target.value })}
                            className="w-full border border-[#E5E6E3] rounded-xl px-4 py-2 focus:outline-none focus:border-[#2D3538]"
                            placeholder="Describe when this trigger occurs"
                        />
                    </div>

                    <div className="flex justify-end gap-2">
                        <Button variant="outline" onClick={() => setShowAddForm(false)} className="rounded-xl">
                            Cancel
                        </Button>
                        <Button
                            onClick={handleAddTrigger}
                            disabled={!newTrigger.name}
                            className="bg-[#2D3538] hover:bg-[#1A1D1E] text-white rounded-xl"
                        >
                            Add Trigger
                        </Button>
                    </div>
                </motion.div>
            )}

            {/* Trigger Cards */}
            <div className="space-y-4">
                {displayTriggers.map((trigger, index) => (
                    <TriggerCard
                        key={trigger.id}
                        trigger={trigger}
                        isConfirmed={confirmedIds.includes(trigger.id)}
                        onConfirm={() => handleConfirmToggle(trigger.id)}
                        onUpdate={(updates) => onUpdateTrigger(trigger.id, updates)}
                        index={index}
                    />
                ))}
            </div>
        </div>
    );
}
