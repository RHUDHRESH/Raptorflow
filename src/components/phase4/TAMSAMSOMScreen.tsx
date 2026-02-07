'use client';

import React from 'react';
import { TAMSAMSOM } from '@/lib/foundation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ArrowRight, TrendingUp, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface TAMSAMSOMScreenProps {
    data: TAMSAMSOM;
    onChange: (data: TAMSAMSOM) => void;
    onContinue: () => void;
}

function formatCurrency(value: number, currency: string): string {
    if (value >= 1_000_000_000) return `$${(value / 1_000_000_000).toFixed(1)}B`;
    if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(0)}M`;
    if (value >= 1_000) return `$${(value / 1_000).toFixed(0)}K`;
    return `$${value}`;
}

function MarketCard({
    label,
    value,
    currency,
    formula,
    context,
    color,
}: {
    label: string;
    value: number;
    currency: string;
    formula: string;
    context: string;
    color: string;
}) {
    return (
        <div className={cn("rounded-xl border-2 p-6", color)}>
            <div className="flex items-center justify-between mb-4">
                <span className="text-sm font-medium uppercase tracking-wider opacity-70">{label}</span>
                <TrendingUp className="h-5 w-5 opacity-50" />
            </div>
            <div className="text-4xl font-bold mb-2">
                {formatCurrency(value, currency)}
            </div>
            <p className="text-sm mb-3 opacity-80">{context}</p>
            <div className="pt-3 border-t border-current/10">
                <p className="text-xs opacity-70">{formula}</p>
            </div>
        </div>
    );
}

export function TAMSAMSOMScreen({ data, onChange, onContinue }: TAMSAMSOMScreenProps) {
    const updateAssumption = (index: number, value: string) => {
        const newAssumptions = [...data.assumptions];
        newAssumptions[index] = value;
        onChange({ ...data, assumptions: newAssumptions });
    };

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="text-center space-y-2">
                <h1 className="text-3xl font-serif font-bold text-foreground">
                    TAM / SAM / SOM
                </h1>
                <p className="text-muted-foreground max-w-lg mx-auto">
                    Market sizing tied to your category and segment choices. All assumptions are explicit.
                </p>
            </div>

            {/* Market Cards */}
            <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
                <MarketCard
                    label="TAM"
                    value={data.tam.value}
                    currency={data.tam.currency}
                    formula={data.tam.formula}
                    context={`Category: ${data.tam.category || 'Selected category'}`}
                    color="border-blue-200 bg-blue-50/50 dark:border-blue-900 dark:bg-blue-950/20 text-blue-700 dark:text-blue-300"
                />
                <MarketCard
                    label="SAM"
                    value={data.sam.value}
                    currency={data.sam.currency}
                    formula={data.sam.formula}
                    context={`Segment: ${data.sam.segment || 'Primary segment'}`}
                    color="border-purple-200 bg-purple-50/50 dark:border-purple-900 dark:bg-purple-950/20 text-purple-700 dark:text-purple-300"
                />
                <MarketCard
                    label="SOM"
                    value={data.som.value}
                    currency={data.som.currency}
                    formula={data.som.formula}
                    context={data.som.reachability || 'Current reach'}
                    color="border-green-200 bg-green-50/50 dark:border-green-900 dark:bg-green-950/20 text-green-700 dark:text-green-300"
                />
            </div>

            {/* Funnel Visualization */}
            <div className="max-w-md mx-auto text-center">
                <div className="relative h-48">
                    {/* TAM */}
                    <div className="absolute inset-x-0 top-0 h-12 bg-blue-200/50 dark:bg-blue-900/30 rounded-t-xl" />
                    {/* SAM */}
                    <div className="absolute inset-x-8 top-12 h-12 bg-purple-200/50 dark:bg-purple-900/30" />
                    {/* SOM */}
                    <div className="absolute inset-x-16 top-24 h-12 bg-green-200/50 dark:bg-green-900/30 rounded-b-xl" />

                    {/* Labels */}
                    <div className="absolute right-0 top-3 text-xs text-blue-700 dark:text-blue-400">TAM</div>
                    <div className="absolute right-0 top-[60px] text-xs text-purple-700 dark:text-purple-400">SAM</div>
                    <div className="absolute right-0 top-[108px] text-xs text-green-700 dark:text-green-400">SOM</div>
                </div>
            </div>

            {/* Assumptions */}
            <div className="max-w-2xl mx-auto">
                <div className="flex items-center gap-2 mb-4">
                    <AlertCircle className="h-4 w-4 text-amber-500" />
                    <h3 className="font-semibold text-sm">Assumptions (editable)</h3>
                </div>
                <div className="space-y-2">
                    {data.assumptions.map((assumption, i) => (
                        <Input
                            key={i}
                            value={assumption}
                            onChange={(e) => updateAssumption(i, e.target.value)}
                            className="text-sm"
                        />
                    ))}
                </div>
                <p className="text-xs text-muted-foreground mt-2">
                    When category changes → TAM changes. When segment changes → SAM changes.
                </p>
            </div>

            {/* Continue Button */}
            <div className="flex justify-center pt-4">
                <Button size="lg" onClick={onContinue} className="px-8 py-6 text-lg rounded-xl">
                    Continue <ArrowRight className="h-5 w-5 ml-2" />
                </Button>
            </div>
        </div>
    );
}
