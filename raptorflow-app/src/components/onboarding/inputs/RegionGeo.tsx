'use client';

import React from 'react';
import { Input } from '@/components/ui/input';
import { Check } from 'lucide-react';
import { cn } from '@/lib/utils';
import { RegionCode } from '@/lib/foundation';
import { QuestionOption } from '@/lib/questionFlowData';

interface RegionGeoProps {
    value: {
        basedIn: string;
        sellsTo: RegionCode[];
    };
    onChange: (value: { basedIn: string; sellsTo: RegionCode[] }) => void;
    options: QuestionOption[];
}

const defaultValue = { basedIn: '', sellsTo: [] as RegionCode[] };

export function RegionGeo({ value = defaultValue, onChange, options }: RegionGeoProps) {
    const safeValue = { ...defaultValue, ...value };

    const toggleRegion = (region: string) => {
        const regionCode = region as RegionCode;
        if (safeValue.sellsTo.includes(regionCode)) {
            onChange({ ...safeValue, sellsTo: safeValue.sellsTo.filter(r => r !== regionCode) });
        } else {
            onChange({ ...safeValue, sellsTo: [...safeValue.sellsTo, regionCode] });
        }
    };

    return (
        <div className="space-y-6">
            {/* Based In */}
            <div>
                <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-2 block">
                    Where are you based?
                </label>
                <Input
                    placeholder="e.g., Mumbai, India"
                    value={safeValue.basedIn}
                    onChange={(e) => onChange({ ...safeValue, basedIn: e.target.value })}
                    className="h-12 text-base bg-background border-2 focus-visible:ring-0 focus-visible:border-primary"
                />
            </div>

            {/* Sells To */}
            <div>
                <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-3 block">
                    Where do you sell?
                </label>
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
                    {options.map((opt) => {
                        const isSelected = safeValue.sellsTo.includes(opt.value as RegionCode);
                        return (
                            <div
                                key={opt.value}
                                onClick={() => toggleRegion(opt.value)}
                                className={cn(
                                    "relative p-4 rounded-xl border-2 cursor-pointer transition-all text-center",
                                    isSelected
                                        ? "border-primary bg-primary/5"
                                        : "border-border hover:border-primary/30"
                                )}
                            >
                                <span className={cn(
                                    "font-medium",
                                    isSelected ? "text-primary" : "text-foreground"
                                )}>
                                    {opt.label}
                                </span>
                                {isSelected && (
                                    <div className="absolute top-2 right-2 w-4 h-4 bg-primary rounded-full flex items-center justify-center">
                                        <Check className="h-2.5 w-2.5 text-primary-foreground" />
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}
