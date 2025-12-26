'use client';

import React from 'react';
import { MarketCategory } from '@/lib/foundation';
import { Button } from '@/components/ui/button';
import { Check, AlertTriangle, ArrowRight } from 'lucide-react';
import { cn } from '@/lib/utils';

interface CategoryPickerProps {
    options: MarketCategory[];
    selected: MarketCategory;
    onSelect: (category: MarketCategory) => void;
    onContinue: () => void;
}

function RiskBadge({ risk }: { risk?: string }) {
    if (!risk || risk === 'ok') return null;

    const config: Record<string, { color: string; label: string }> = {
        'too-broad': { color: 'text-amber-600 bg-amber-100', label: 'Too Broad' },
        'too-weird': { color: 'text-purple-600 bg-purple-100', label: 'Too Weird' },
        'too-crowded': { color: 'text-red-600 bg-red-100', label: 'Too Crowded' },
    };

    const { color, label } = config[risk] || { color: '', label: '' };

    return (
        <span className={cn("text-xs px-2 py-0.5 rounded-full", color)}>
            <AlertTriangle className="h-3 w-3 inline mr-1" />
            {label}
        </span>
    );
}

function CategoryCard({
    category,
    isSelected,
    onSelect,
}: {
    category: MarketCategory;
    isSelected: boolean;
    onSelect: () => void;
}) {
    return (
        <button
            onClick={onSelect}
            className={cn(
                "w-full text-left p-5 rounded-xl border-2 transition-all",
                isSelected
                    ? "border-primary bg-primary/5 ring-2 ring-primary/20"
                    : "border-border bg-card hover:border-primary/30"
            )}
        >
            <div className="flex items-start justify-between gap-3">
                <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                        <h3 className="text-lg font-semibold">{category.primary}</h3>
                        <RiskBadge risk={category.risk} />
                    </div>

                    {category.altLabels.length > 0 && (
                        <p className="text-sm text-muted-foreground mb-3">
                            Also: {category.altLabels.join(', ')}
                        </p>
                    )}

                    <div className="space-y-1">
                        {category.whyThisContext.map((reason, i) => (
                            <p key={i} className="text-sm text-muted-foreground flex items-center gap-2">
                                <Check className="h-3 w-3 text-green-500" />
                                {reason}
                            </p>
                        ))}
                    </div>
                </div>

                <div className={cn(
                    "w-6 h-6 rounded-full border-2 flex items-center justify-center flex-shrink-0",
                    isSelected ? "border-primary bg-primary" : "border-muted"
                )}>
                    {isSelected && <Check className="h-4 w-4 text-primary-foreground" />}
                </div>
            </div>
        </button>
    );
}

export function CategoryPicker({ options, selected, onSelect, onContinue }: CategoryPickerProps) {
    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="text-center space-y-2">
                <h1 className="text-3xl font-serif font-bold text-foreground">
                    Market Category
                </h1>
                <p className="text-muted-foreground max-w-lg mx-auto">
                    What category makes your value most obvious to buyers? This is Dunford Component #5.
                </p>
            </div>

            {/* Category Cards */}
            <div className="grid gap-4 max-w-2xl mx-auto">
                {options.map((cat) => (
                    <CategoryCard
                        key={cat.primary}
                        category={cat}
                        isSelected={cat.primary === selected.primary}
                        onSelect={() => onSelect(cat)}
                    />
                ))}
            </div>

            {/* Continue Button */}
            <div className="flex justify-center pt-4">
                <Button
                    size="lg"
                    onClick={onContinue}
                    disabled={!selected.primary}
                    className="px-8 py-6 text-lg rounded-xl"
                >
                    Continue <ArrowRight className="h-5 w-5 ml-2" />
                </Button>
            </div>
        </div>
    );
}
