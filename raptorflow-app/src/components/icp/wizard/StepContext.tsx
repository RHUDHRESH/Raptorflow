import React from 'react';
import { IcpCompanyType, IcpFirmographics, IcpSalesMotion } from '@/types/icp-types';

interface StepContextProps {
    data: IcpFirmographics;
    onChange: (data: Partial<IcpFirmographics>) => void;
}

const BUSINESS_TYPES: { value: IcpCompanyType; label: string; desc: string }[] = [
    { value: 'saas', label: 'SaaS', desc: 'Subscription software' },
    { value: 'd2c', label: 'D2C', desc: 'Direct consumer physical goods' },
    { value: 'agency', label: 'Agency', desc: 'Service provider / Consult' },
    { value: 'service', label: 'Service', desc: 'Local or Professional services' },
];

const SALES_MOTIONS: { value: IcpSalesMotion; label: string; desc: string }[] = [
    { value: 'self-serve', label: 'Self-Serve', desc: 'Product-led, no humans' },
    { value: 'demo-led', label: 'Demo-Led', desc: 'Sales calls required' },
    { value: 'sales-assisted', label: 'Sales-Assisted', desc: 'Hybrid model' },
];

export default function StepContext({ data, onChange }: StepContextProps) {
    const toggleSelection = <T extends string>(
        current: T[],
        value: T,
        key: keyof IcpFirmographics
    ) => {
        const newSet = current.includes(value)
            ? current.filter(i => i !== value)
            : [...current, value];
        onChange({ [key]: newSet });
    };

    return (
        <div className="space-y-12">
            <div className="text-center space-y-4">
                <h1 className="font-serif text-4xl text-[#2D3538] leading-tight">
                    First, let’s compress the context.
                </h1>
                <p className="text-[#5B5F61] text-lg max-w-md mx-auto">
                    We strip away the noise. What are the hard constraints of your business model?
                </p>
            </div>

            <div className="space-y-8">
                {/* Business Type */}
                <div className="space-y-4">
                    <label className="block text-sm font-semibold uppercase tracking-wider text-[#9D9F9F]">
                        Business Model
                    </label>
                    <div className="grid grid-cols-2 gap-4">
                        {BUSINESS_TYPES.map((type) => (
                            <button
                                key={type.value}
                                onClick={() => toggleSelection(data.companyType, type.value, 'companyType')}
                                className={`flex flex-col items-start p-5 rounded-2xl border transition-all text-left
                  ${data.companyType.includes(type.value)
                                        ? 'border-[#2D3538] bg-white ring-1 ring-[#2D3538] shadow-sm'
                                        : 'border-[#C0C1BE]/50 bg-transparent hover:border-[#2D3538]/50 hover:bg-white/50'
                                    }`}
                            >
                                <div className="font-medium text-lg mb-1">{type.label}</div>
                                <div className="text-sm text-[#5B5F61]">{type.desc}</div>
                            </button>
                        ))}
                    </div>
                </div>

                {/* Sales Motion */}
                <div className="space-y-4">
                    <label className="block text-sm font-semibold uppercase tracking-wider text-[#9D9F9F]">
                        Sales Motion
                    </label>
                    <div className="grid grid-cols-3 gap-4">
                        {SALES_MOTIONS.map((motion) => (
                            <button
                                key={motion.value}
                                onClick={() => toggleSelection(data.salesMotion, motion.value, 'salesMotion')}
                                className={`flex flex-col items-start p-5 rounded-2xl border transition-all text-left
                  ${data.salesMotion.includes(motion.value)
                                        ? 'border-[#2D3538] bg-white ring-1 ring-[#2D3538] shadow-sm'
                                        : 'border-[#C0C1BE]/50 bg-transparent hover:border-[#2D3538]/50 hover:bg-white/50'
                                    }`}
                            >
                                <div className="font-medium text-lg mb-1">{motion.label}</div>
                                <div className="text-sm text-[#5B5F61]">{motion.desc}</div>
                            </button>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
