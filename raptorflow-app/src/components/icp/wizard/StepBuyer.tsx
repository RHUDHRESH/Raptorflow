import React from 'react';
import { IcpFirmographics, IcpPainMap } from '@/types/icp-types';

interface StepBuyerProps {
    firmographics: IcpFirmographics;
    painMap: IcpPainMap;
    onChangeFirmographics: (data: Partial<IcpFirmographics>) => void;
    onChangePainMap: (data: Partial<IcpPainMap>) => void;
}

const BUDGET_RANGES = [
    { value: 'low', label: '< $1k/mo', desc: 'Price Shoppers' },
    { value: 'medium', label: '$1k - $5k/mo', desc: 'Value Buyers' },
    { value: 'high', label: '$5k - $20k/mo', desc: 'Solution Buyers' },
    { value: 'enterprise', label: '$20k+/mo', desc: 'Strategic Buyers' },
];

const URGENCY_LEVELS = [
    { value: 'now', label: 'Now', desc: 'Bleeding neck (High Confidence)' },
    { value: 'soon', label: 'Soon', desc: 'Within quarter (Normal)' },
    { value: 'someday', label: 'Someday', desc: 'Exploratory (Low Confidence)' },
];

const DECISION_MAKERS = [
    "Founder / CEO",
    "Marketing Leader",
    "Sales Leader",
    "CTO / Product",
    "Individual Contributor"
];

export default function StepBuyer({ firmographics, painMap, onChangeFirmographics, onChangePainMap }: StepBuyerProps) {

    const toggleSelection = (list: string[], item: string, onChange: (d: any) => void, field: string) => {
        const newList = list.includes(item)
            ? list.filter(i => i !== item)
            : [...list, item];
        onChange({ [field]: newList });
    };

    return (
        <div className="space-y-12">
            <div className="text-center space-y-4">
                <h1 className="font-serif text-4xl text-[#2D3538] leading-tight">
                    Buyer Reality Check.
                </h1>
                <p className="text-[#5B5F61] text-lg max-w-md mx-auto">
                    Be honest. Who is signing the check, and can they actually afford you?
                </p>
            </div>

            {/* Budget */}
            <div className="space-y-4">
                <label className="block text-sm font-semibold uppercase tracking-wider text-[#9D9F9F]">
                    Budget Comfort
                </label>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {BUDGET_RANGES.map((b) => (
                        <button
                            key={b.value}
                            onClick={() => toggleSelection(firmographics.budgetComfort, b.value, onChangeFirmographics, 'budgetComfort')}
                            className={`p-4 rounded-xl border text-left transition-all
                ${firmographics.budgetComfort.includes(b.value)
                                    ? 'border-[#2D3538] bg-white ring-1 ring-[#2D3538]'
                                    : 'border-[#C0C1BE]/50 hover:border-[#5B5F61]'
                                }`}
                        >
                            <div className="font-semibold text-[#2D3538]">{b.label}</div>
                            <div className="text-xs text-[#5B5F61] mt-1">{b.desc}</div>
                        </button>
                    ))}
                </div>
            </div>

            {/* Urgency */}
            <div className="space-y-4">
                <label className="block text-sm font-semibold uppercase tracking-wider text-[#9D9F9F]">
                    Urgency (How fast do they convert?)
                </label>
                <div className="grid grid-cols-3 gap-4">
                    {URGENCY_LEVELS.map((u) => (
                        <button
                            key={u.value}
                            onClick={() => onChangePainMap({ urgencyLevel: u.value as any })}
                            className={`p-5 rounded-xl border text-center transition-all ${painMap.urgencyLevel === u.value
                                    ? 'border-[#2D3538] bg-[#2D3538] text-white shadow-md transform scale-[1.02]'
                                    : 'border-[#C0C1BE]/50 bg-white text-[#5B5F61] hover:border-[#2D3538]'
                                }`}
                        >
                            <div className="font-semibold text-lg">{u.label}</div>
                            <div className={`text-xs mt-1 ${painMap.urgencyLevel === u.value ? 'text-gray-300' : 'text-[#9D9F9F]'}`}>
                                {u.desc}
                            </div>
                        </button>
                    ))}
                </div>
            </div>

            {/* Decision Maker */}
            <div className="space-y-4 pt-6">
                <label className="block text-sm font-semibold uppercase tracking-wider text-[#9D9F9F]">
                    Primary Decision Maker
                </label>
                <div className="flex flex-wrap gap-3">
                    {DECISION_MAKERS.map((dm) => (
                        <button
                            key={dm}
                            onClick={() => toggleSelection(firmographics.decisionMaker, dm, onChangeFirmographics, 'decisionMaker')}
                            className={`px-5 py-2.5 rounded-full border text-sm font-medium transition-all
                ${firmographics.decisionMaker.includes(dm)
                                    ? 'bg-white text-[#2D3538] border-[#2D3538] ring-1 ring-[#2D3538]'
                                    : 'bg-[#F3F4EE] border-transparent text-[#5B5F61] hover:bg-[#E5E7E1]'
                                }`}
                        >
                            {dm}
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
}
