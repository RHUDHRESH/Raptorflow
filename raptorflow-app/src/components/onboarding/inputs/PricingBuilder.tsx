'use client';

import React from 'react';
import { Input } from '@/components/ui/input';
import { cn } from '@/lib/utils';
import { ValueMetric, PricingMode } from '@/lib/foundation';
import { QuestionOption } from '@/lib/questionFlowData';

interface PricingBuilderProps {
    value: ValueMetric;
    onChange: (value: ValueMetric) => void;
    options: QuestionOption[];
}

const defaultValue: ValueMetric = {
    pricingMode: 'monthly',
    priceRangeMin: undefined,
    priceRangeMax: undefined,
    currency: 'USD',
};

export function PricingBuilder({ value = defaultValue, onChange, options }: PricingBuilderProps) {
    const safeValue = { ...defaultValue, ...value };

    const setPricingMode = (mode: PricingMode) => {
        onChange({ ...safeValue, pricingMode: mode });
    };

    return (
        <div className="space-y-6">
            {/* Pricing Mode */}
            <div>
                <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-3 block">
                    Pricing Model
                </label>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                    {options.map((opt) => (
                        <div
                            key={opt.value}
                            onClick={() => setPricingMode(opt.value as PricingMode)}
                            className={cn(
                                "p-4 rounded-xl border-2 cursor-pointer transition-all text-center",
                                safeValue.pricingMode === opt.value
                                    ? "border-primary bg-primary/5"
                                    : "border-border hover:border-primary/30"
                            )}
                        >
                            <span className={cn(
                                "font-medium",
                                safeValue.pricingMode === opt.value ? "text-primary" : "text-foreground"
                            )}>
                                {opt.label}
                            </span>
                        </div>
                    ))}
                </div>
            </div>

            {/* Price Range */}
            <div>
                <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-3 block">
                    Typical Price Range
                </label>
                <div className="flex items-center gap-4">
                    <div className="flex-1">
                        <div className="relative">
                            <span className="absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground">$</span>
                            <Input
                                type="number"
                                placeholder="Min"
                                value={safeValue.priceRangeMin ?? ''}
                                onChange={(e) => onChange({ ...safeValue, priceRangeMin: e.target.value ? Number(e.target.value) : undefined })}
                                className="h-12 pl-8 text-base bg-background border-2 focus-visible:ring-0 focus-visible:border-primary"
                            />
                        </div>
                    </div>
                    <span className="text-muted-foreground">to</span>
                    <div className="flex-1">
                        <div className="relative">
                            <span className="absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground">$</span>
                            <Input
                                type="number"
                                placeholder="Max"
                                value={safeValue.priceRangeMax ?? ''}
                                onChange={(e) => onChange({ ...safeValue, priceRangeMax: e.target.value ? Number(e.target.value) : undefined })}
                                className="h-12 pl-8 text-base bg-background border-2 focus-visible:ring-0 focus-visible:border-primary"
                            />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
