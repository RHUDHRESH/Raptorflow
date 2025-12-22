'use client';

import React from 'react';
import { cn } from '@/lib/utils';
import { ASSET_TYPES, AssetType, AssetCategory, AssetTypeConfig } from './types';
import * as LucideIcons from 'lucide-react';
import { LucideIcon } from 'lucide-react';

interface AssetTypeSelectorProps {
    onSelect: (type: AssetType) => void;
    selectedType?: AssetType;
    className?: string;
}

const CATEGORIES: { key: AssetCategory; label: string }[] = [
    { key: 'text', label: 'Text Assets' },
    { key: 'visual', label: 'Visual Assets' },
    { key: 'strategy', label: 'Strategy' },
];

function getIcon(iconName: string): LucideIcon {
    const icons = LucideIcons as unknown as Record<string, LucideIcon>;
    return icons[iconName] || LucideIcons.FileText;
}

export function AssetTypeSelector({ onSelect, selectedType, className }: AssetTypeSelectorProps) {
    return (
        <div className={cn('space-y-8', className)}>
            {CATEGORIES.map(category => {
                const items = ASSET_TYPES.filter(a => a.category === category.key);
                if (items.length === 0) return null;

                return (
                    <div key={category.key} className="space-y-3">
                        <p className="text-xs font-medium uppercase tracking-widest text-muted-foreground">
                            {category.label}
                        </p>
                        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
                            {items.map(item => (
                                <AssetTypeButton
                                    key={item.type}
                                    config={item}
                                    isSelected={selectedType === item.type}
                                    onClick={() => onSelect(item.type)}
                                />
                            ))}
                        </div>
                    </div>
                );
            })}
        </div>
    );
}

function AssetTypeButton({
    config,
    isSelected,
    onClick
}: {
    config: AssetTypeConfig;
    isSelected: boolean;
    onClick: () => void;
}) {
    const Icon = getIcon(config.icon);

    return (
        <button
            onClick={onClick}
            className={cn(
                'flex flex-col items-center gap-2 p-4 rounded-xl border transition-all duration-200',
                'hover:border-foreground/20 hover:bg-muted/30',
                isSelected
                    ? 'border-foreground bg-foreground/5'
                    : 'border-border/60 bg-card'
            )}
        >
            <Icon className={cn(
                'h-5 w-5 transition-colors',
                isSelected ? 'text-foreground' : 'text-muted-foreground'
            )} />
            <span className={cn(
                'text-xs font-medium transition-colors',
                isSelected ? 'text-foreground' : 'text-muted-foreground'
            )}>
                {config.label}
            </span>
        </button>
    );
}

// Quick selector for common asset types (inline chips)
export function AssetTypeChips({
    onSelect,
    className
}: {
    onSelect: (type: AssetType) => void;
    className?: string;
}) {
    const quickTypes: AssetType[] = ['email', 'social-post', 'tagline', 'meme', 'video-script'];

    return (
        <div className={cn('flex flex-wrap gap-2 justify-center', className)}>
            {quickTypes.map(type => {
                const config = ASSET_TYPES.find(a => a.type === type);
                if (!config) return null;
                const Icon = getIcon(config.icon);

                return (
                    <button
                        key={type}
                        onClick={() => onSelect(type)}
                        className={cn(
                            'flex items-center gap-1.5 px-3 py-1.5 rounded-full',
                            'border border-border/60 bg-card',
                            'text-xs font-medium text-muted-foreground',
                            'hover:border-foreground/20 hover:text-foreground hover:bg-muted/30',
                            'transition-all duration-200'
                        )}
                    >
                        <Icon className="h-3.5 w-3.5" />
                        {config.label}
                    </button>
                );
            })}
        </div>
    );
}
