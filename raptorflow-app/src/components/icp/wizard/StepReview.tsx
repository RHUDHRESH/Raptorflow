import React, { useState } from 'react';
import { Icp } from '@/types/icp-types';

interface StepReviewProps {
    data: Partial<Icp>;
    onChange: (updates: Partial<Icp>) => void;
}

export default function StepReview({ data, onChange }: StepReviewProps) {
    const [name, setName] = useState(data.name || 'My Ideal Customer Profile');

    return (
        <div className="space-y-12">
            <div className="text-center space-y-4">
                <h1 className="font-serif text-4xl text-[#2D3538] leading-tight">
                    Review & Lock.
                </h1>
                <p className="text-[#5B5F61] text-lg max-w-md mx-auto">
                    Sanity check. Does this look like a real market segment?
                </p>
            </div>

            <div className="bg-white rounded-3xl border border-[#C0C1BE]/50 p-8 shadow-sm space-y-8">

                {/* Name Input */}
                <div className="space-y-2">
                    <label className="text-xs uppercase font-bold tracking-widest text-[#9D9F9F]">ICP Name</label>
                    <input
                        type="text"
                        value={name}
                        onChange={(e) => {
                            setName(e.target.value);
                            onChange({ name: e.target.value });
                        }}
                        className="w-full text-2xl font-serif text-[#2D3538] border-b border-[#C0C1BE] pb-2 focus:outline-none focus:border-[#2D3538] bg-transparent"
                    />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    {/* Context */}
                    <div className="space-y-3">
                        <h3 className="text-sm font-semibold uppercase text-[#9D9F9F]">Context</h3>
                        <ul className="space-y-1 text-sm text-[#2D3538]">
                            {data.firmographics?.companyType.length ? data.firmographics.companyType.map(t => <li key={t}>• {t}</li>) : <li className="text-gray-400 italic">None selected</li>}
                            {data.firmographics?.salesMotion.length ? data.firmographics.salesMotion.map(t => <li key={t}>• {t}</li>) : null}
                            {data.firmographics?.budgetComfort.length ? data.firmographics.budgetComfort.map(b => <li key={b}>• Budget: {b}</li>) : null}
                        </ul>
                    </div>

                    {/* Pain */}
                    <div className="space-y-3">
                        <h3 className="text-sm font-semibold uppercase text-[#9D9F9F]">Core Pain</h3>
                        <ul className="space-y-1 text-sm text-[#2D3538]">
                            {data.painMap?.primaryPains.length ? data.painMap.primaryPains.map(p => <li key={p}>• {p}</li>) : <li className="text-gray-400 italic">None selected</li>}
                            {data.painMap?.urgencyLevel && <li>• Urgency: <span className="font-medium capitalize">{data.painMap.urgencyLevel}</span></li>}
                        </ul>
                    </div>

                    {/* Language */}
                    <div className="space-y-3">
                        <h3 className="text-sm font-semibold uppercase text-[#9D9F9F]">Language</h3>
                        <div className="flex flex-wrap gap-2">
                            {data.psycholinguistics?.tonePreference.map(t => (
                                <span key={t} className="px-2 py-1 bg-[#F3F4EE] rounded text-xs">{t}</span>
                            ))}
                            {data.psycholinguistics?.mindsetTraits.map(t => (
                                <span key={t} className="px-2 py-1 bg-[#F3F4EE] rounded text-xs">{t}</span>
                            ))}
                        </div>
                    </div>

                    {/* Exclusions */}
                    {data.disqualifiers && (
                        <div className="space-y-3">
                            <h3 className="text-sm font-semibold uppercase text-red-800/60">Disqualifiers</h3>
                            <div className="flex flex-wrap gap-2">
                                {data.disqualifiers.excludedCompanyTypes.map(t => (
                                    <span key={t} className="px-2 py-1 bg-red-50 text-red-900 rounded text-xs border border-red-100">{t}</span>
                                ))}
                                {data.disqualifiers.excludedBehaviors.map(t => (
                                    <span key={t} className="px-2 py-1 bg-red-50 text-red-900 rounded text-xs border border-red-100">{t}</span>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
