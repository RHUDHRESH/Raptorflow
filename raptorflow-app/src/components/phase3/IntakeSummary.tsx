'use client';

import React from 'react';
import { Check, AlertCircle, Info, ChevronDown, ChevronUp } from 'lucide-react';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { Switch } from '@/components/ui/switch';
import { Button } from '@/components/ui/button';
import { IntakeSummaryItem, SourceConfidence } from '@/lib/foundation';

interface IntakeSummaryProps {
    items: IntakeSummaryItem[];
    onItemEdit: (id: string, text: string) => void;
    onToggleAssumption: (id: string) => void;
    onConfirm: () => void;
    onBack: () => void;
}

const SECTION_LABELS: Record<string, string> = {
    company: 'Company & Offer',
    pricing: 'Pricing & Model',
    stack: 'Current Stack & Workflow',
    pains: 'Top Pains',
    constraints: 'Constraints & Taboos',
    proof: 'Proof Available',
};

const CONFIDENCE_COLORS: Record<SourceConfidence, { bg: string; text: string; label: string }> = {
    high: { bg: 'bg-[#2D3538]', text: 'text-white', label: 'High' },
    medium: { bg: 'bg-[#F59E0B]', text: 'text-white', label: 'Med' },
    low: { bg: 'bg-[#9D9F9F]', text: 'text-white', label: 'Low' },
};

function ConfidenceMeter({ confidence }: { confidence: SourceConfidence }) {
    const config = CONFIDENCE_COLORS[confidence];
    return (
        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-mono uppercase tracking-[0.1em] ${config.bg} ${config.text}`}>
            {config.label}
        </span>
    );
}

interface SectionCardProps {
    section: string;
    items: IntakeSummaryItem[];
    onItemEdit: (id: string, text: string) => void;
    onToggleAssumption: (id: string) => void;
}

function SectionCard({ section, items, onItemEdit, onToggleAssumption }: SectionCardProps) {
    const [expanded, setExpanded] = React.useState(true);

    return (
        <div className="bg-white border border-[#E5E6E3] rounded-2xl overflow-hidden">
            <button
                onClick={() => setExpanded(!expanded)}
                className="w-full flex items-center justify-between px-6 py-5 hover:bg-[#FAFAF8] transition-colors"
            >
                <span className="font-medium text-[#2D3538]">{SECTION_LABELS[section] || section}</span>
                <div className="flex items-center gap-3">
                    <span className="text-[12px] text-[#9D9F9F]">{items.length} items</span>
                    {expanded ? (
                        <ChevronUp className="w-4 h-4 text-[#9D9F9F]" />
                    ) : (
                        <ChevronDown className="w-4 h-4 text-[#9D9F9F]" />
                    )}
                </div>
            </button>

            {expanded && (
                <div className="px-6 pb-5 space-y-4">
                    {items.map((item) => (
                        <div key={item.id} className="group">
                            <div className="flex items-start gap-4">
                                {/* Label & Confidence */}
                                <div className="flex-shrink-0 w-[140px]">
                                    <span className="text-[12px] text-[#5B5F61] block mb-1">{item.label}</span>
                                    <div className="flex items-center gap-2">
                                        <ConfidenceMeter confidence={item.sourceConfidence} />
                                        {item.sourceQuotes.length > 0 && (
                                            <TooltipProvider>
                                                <Tooltip>
                                                    <TooltipTrigger>
                                                        <Info className="w-3.5 h-3.5 text-[#9D9F9F] hover:text-[#5B5F61]" />
                                                    </TooltipTrigger>
                                                    <TooltipContent side="right" className="max-w-[300px] bg-[#2D3538] text-white p-4 rounded-xl">
                                                        <p className="text-[11px] font-mono uppercase tracking-[0.1em] text-white/50 mb-2">
                                                            Source Quote
                                                        </p>
                                                        <p className="text-[13px] leading-relaxed">
                                                            "{item.sourceQuotes[0]}"
                                                        </p>
                                                    </TooltipContent>
                                                </Tooltip>
                                            </TooltipProvider>
                                        )}
                                    </div>
                                </div>

                                {/* Editable Text */}
                                <div className="flex-1">
                                    <input
                                        type="text"
                                        value={item.text}
                                        onChange={(e) => onItemEdit(item.id, e.target.value)}
                                        className="w-full bg-[#FAFAF8] border border-[#E5E6E3] rounded-xl px-4 py-3 text-[#2D3538] text-[15px] focus:outline-none focus:ring-2 focus:ring-[#2D3538]/10 focus:border-[#2D3538]/30 transition-all"
                                    />
                                </div>

                                {/* Assumption Toggle */}
                                <div className="flex-shrink-0 flex items-center gap-2">
                                    <span className="text-[11px] text-[#9D9F9F]">Assumption</span>
                                    <Switch
                                        checked={item.isAssumption}
                                        onCheckedChange={() => onToggleAssumption(item.id)}
                                        className="data-[state=checked]:bg-[#F59E0B]"
                                    />
                                </div>
                            </div>
                        </div>
                    ))}

                    {items.length === 0 && (
                        <div className="text-center py-6 text-[#9D9F9F] text-[14px]">
                            No data extracted for this section
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

export function IntakeSummary({ items, onItemEdit, onToggleAssumption, onConfirm, onBack }: IntakeSummaryProps) {
    // Group items by section
    const groupedItems = React.useMemo(() => {
        const groups: Record<string, IntakeSummaryItem[]> = {};
        items.forEach((item) => {
            if (!groups[item.section]) {
                groups[item.section] = [];
            }
            groups[item.section].push(item);
        });
        return groups;
    }, [items]);

    const sectionOrder = ['company', 'pricing', 'stack', 'pains', 'constraints', 'proof'];
    const assumptionCount = items.filter((i) => i.isAssumption).length;
    const highConfidenceCount = items.filter((i) => i.sourceConfidence === 'high').length;

    return (
        <div className="space-y-8">
            {/* Header Stats */}
            <div className="flex items-center gap-8">
                <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-[#2D3538]" />
                    <span className="text-[13px] text-[#5B5F61]">
                        {highConfidenceCount} high confidence
                    </span>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-[#F59E0B]" />
                    <span className="text-[13px] text-[#5B5F61]">
                        {assumptionCount} marked as assumptions
                    </span>
                </div>
            </div>

            {/* Section Cards */}
            <div className="space-y-4">
                {sectionOrder.map((section) => (
                    <SectionCard
                        key={section}
                        section={section}
                        items={groupedItems[section] || []}
                        onItemEdit={onItemEdit}
                        onToggleAssumption={onToggleAssumption}
                    />
                ))}
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
                    onClick={onConfirm}
                    className="bg-[#2D3538] hover:bg-[#1A1D1E] text-white px-10 py-6 rounded-2xl text-[15px] font-medium"
                >
                    Confirm & Continue
                </Button>
            </div>
        </div>
    );
}
