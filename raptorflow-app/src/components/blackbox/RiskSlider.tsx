'use client';

import React from 'react';
import { cn } from '@/lib/utils';
import { RiskLevel } from '@/lib/blackbox-types';
import { Shield, Flame, Zap } from 'lucide-react';

interface RiskSliderProps {
    value: RiskLevel | null;
    onChange: (value: RiskLevel) => void;
}

const OPTIONS = [
    { id: 'safe' as RiskLevel, label: 'Safe', sub: 'Proven tactics', icon: Shield },
    { id: 'spicy' as RiskLevel, label: 'Spicy', sub: 'Push boundaries', icon: Flame },
    { id: 'unreasonable' as RiskLevel, label: 'Unreasonable', sub: 'Full send', icon: Zap },
];

export function RiskSlider({ value, onChange }: RiskSliderProps) {
    return (
        <div className="w-full space-y-4 text-center">
            <div>
                <h2 className="text-xl font-semibold mb-1 font-sans">How weird can we get?</h2>
                <p className="text-sm text-zinc-500 font-sans">Choose your risk budget.</p>
            </div>
            <div className="flex flex-col gap-2 max-w-xs mx-auto">
                {OPTIONS.map((opt) => {
                    const Icon = opt.icon;
                    const isSelected = value === opt.id;
                    return (
                        <button
                            key={opt.id}
                            onClick={() => onChange(opt.id)}
                            className={cn(
                                "flex items-center gap-3 p-4 rounded-xl border-2 text-left transition-all",
                                isSelected
                                    ? "bg-zinc-900 border-zinc-900 text-white dark:bg-white dark:border-white dark:text-zinc-900"
                                    : "border-zinc-200 hover:border-zinc-400 dark:border-zinc-800"
                            )}
                        >
                            <Icon className={cn("w-5 h-5 shrink-0", !isSelected && "text-zinc-400")} />
                            <div>
                                <span className="text-sm font-medium font-sans">{opt.label}</span>
                                <span className={cn("text-xs ml-2 font-sans", isSelected ? "opacity-70" : "text-zinc-400")}>{opt.sub}</span>
                            </div>
                        </button>
                    );
                })}
            </div>
        </div>
    );
}
