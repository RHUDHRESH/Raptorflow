'use client';

import React from 'react';
import { HelpCircle, Info } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';

interface AwarenessMatrixProps {
    matrix: {
        unaware: string;
        problem: string;
        solution: string;
        product: string;
        most: string;
    };
    onChange: (field: string, value: string) => void;
}

interface TierInputProps {
    id: string;
    label: string;
    description: string;
    strategy: string;
    value: string;
    placeholder: string;
    onChange: (val: string) => void;
}

function TierInput({ id, label, description, strategy, value, placeholder, onChange }: TierInputProps) {
    return (
        <div className="group space-y-3">
            <div className="flex justify-between items-start">
                <div className="space-y-1">
                    <label htmlFor={id} className="text-sm font-semibold uppercase tracking-wider text-[#2D3538]">
                        {label}
                    </label>
                    <p className="text-xs text-[#5B5F61] italic">{description}</p>
                </div>
                <TooltipProvider>
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <button className="text-[#9D9F9F] hover:text-[#2D3538] transition-colors">
                                <HelpCircle className="w-4 h-4" />
                            </button>
                        </TooltipTrigger>
                        <TooltipContent side="left" className="max-w-[200px] bg-[#2D3538] text-white border-none p-3 text-[11px]">
                            <p><strong>Strategy:</strong> {strategy}</p>
                        </TooltipContent>
                    </Tooltip>
                </TooltipProvider>
            </div>
            <textarea
                id={id}
                value={value}
                onChange={(e) => onChange(e.target.value)}
                placeholder={placeholder}
                className="w-full min-h-[80px] p-4 rounded-xl border border-[#C0C1BE] bg-white focus:border-[#2D3538] focus:ring-1 focus:ring-[#2D3538] outline-none transition-all resize-none text-sm leading-relaxed"
            />
        </div>
    );
}

export function AwarenessMatrix({ matrix, onChange }: AwarenessMatrixProps) {
    return (
        <div className="space-y-10 py-4">
            <div className="grid grid-cols-1 gap-8">
                <TierInput
                    id="unaware"
                    label="01 / Unaware"
                    description="They don't know they have a problem."
                    strategy="Problem revelation & education. Hook with unstated consequences."
                    value={matrix.unaware}
                    placeholder="e.g. 'Show them how manual data entry is actually costing them 3 hours a day in lost strategy time.'"
                    onChange={(val) => onChange('unaware', val)}
                />

                <TierInput
                    id="problem"
                    label="02 / Problem-Aware"
                    description="They know the pain, but not the solution."
                    strategy="Pain amplification & agitation. Make the current state feel unbearable."
                    value={matrix.problem}
                    placeholder="e.g. 'Highlight the risk of data silos and the inevitable human error in manual syncing.'"
                    onChange={(val) => onChange('problem', val)}
                />

                <TierInput
                    id="solution"
                    label="03 / Solution-Aware"
                    description="They know solutions exist, but not yours."
                    strategy="Mechanism & differentiation. Explain why your unique logic is better."
                    value={matrix.solution}
                    placeholder="e.g. 'Introduce the Unified Architecture that syncs data across 5 channels in real-time.'"
                    onChange={(val) => onChange('solution', val)}
                />

                <TierInput
                    id="product"
                    label="04 / Product-Aware"
                    description="They know your product, but aren't sure yet."
                    strategy="Objection handling & proof. Address skepticism with data/stats."
                    value={matrix.product}
                    placeholder="e.g. 'Guarantee 14-day migration or 3 months free. Show 89% success rate.'"
                    onChange={(val) => onChange('product', val)}
                />

                <TierInput
                    id="most"
                    label="05 / Most-Aware"
                    description="They are on the edge of buying."
                    strategy="Urgency & Commitment. One-click action with an irresistible offer."
                    value={matrix.most}
                    placeholder="e.g. 'Flash offer: 3 months free for startups signing before Friday.'"
                    onChange={(val) => onChange('most', val)}
                />
            </div>

            {/* Strategic Insight */}
            <div className="bg-[#F3F4EE] border border-[#C0C1BE] p-6 rounded-xl flex gap-4 items-center">
                <div className="w-8 h-8 rounded-full bg-[#2D3538] flex items-center justify-center flex-shrink-0 text-white">
                    <Info className="w-4 h-4" />
                </div>
                <p className="text-[12px] text-[#5B5F61] leading-relaxed italic">
                    The Matrix ensures you never speak to a 'Most-Aware' prospect with 'Unaware' messaging.
                    <span className="font-semibold text-[#2D3538]"> Precision is surgical resonance.</span>
                </p>
            </div>
        </div>
    );
}
