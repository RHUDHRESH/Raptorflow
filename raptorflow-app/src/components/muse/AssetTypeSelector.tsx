'use client';

import React from 'react';
import { cn } from '@/lib/utils';
import {
  ASSET_TYPES,
  AssetType,
  AssetCategory,
  AssetTypeConfig,
} from './types';
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

import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

// ... existing imports ...

export function AssetTypeSelector({
  onSelect,
  selectedType,
  className,
}: AssetTypeSelectorProps) {
  return (
    <div className={cn('space-y-4', className)}>
      <Tabs defaultValue="text" className="w-full">
        <TabsList className="w-full grid grid-cols-3 mb-4">
          {CATEGORIES.map((category) => (
            <TabsTrigger key={category.key} value={category.key}>
              {category.label}
            </TabsTrigger>
          ))}
        </TabsList>

        {CATEGORIES.map((category) => (
          <TabsContent
            key={category.key}
            value={category.key}
            className="space-y-4"
          >
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
              {ASSET_TYPES.filter((a) => a.category === category.key).map(
                (item) => (
                  <AssetTypeButton
                    key={item.type}
                    config={item}
                    isSelected={selectedType === item.type}
                    onClick={() => onSelect(item.type)}
                  />
                )
              )}
            </div>
          </TabsContent>
        ))}
      </Tabs>
    </div>
  );
}

function AssetTypeButton({
  config,
  isSelected,
  onClick,
}: {
  config: AssetTypeConfig;
  isSelected: boolean;
  onClick: () => void;
}) {
  const Icon = getIcon(config.icon);

  return (
    <Card
      onClick={onClick}
      className={cn(
        'cursor-pointer transition-all duration-200 hover:shadow-md h-full',
        'hover:border-primary/50 hover:bg-muted/30',
        isSelected
          ? 'border-primary bg-primary/5 ring-1 ring-primary/20'
          : 'border-border/60'
      )}
    >
      <CardContent className="p-4 flex flex-col items-center gap-2.5 text-center h-full justify-center">
        <div
          className={cn(
            'p-2 rounded-lg transition-colors',
            isSelected
              ? 'bg-primary/10 text-primary'
              : 'bg-muted text-muted-foreground'
          )}
        >
          <Icon className="h-5 w-5" />
        </div>
        <span
          className={cn(
            'text-xs font-medium leading-tight',
            isSelected ? 'text-primary' : 'text-foreground'
          )}
        >
          {config.label}
        </span>
      </CardContent>
    </Card>
  );
}

// Quick selector for common asset types (inline chips)
export function AssetTypeChips({
  onSelect,
  className,
}: {
  onSelect: (type: AssetType) => void;
  className?: string;
}) {
  const quickTypes: AssetType[] = [
    'email',
    'social-post',
    'tagline',
    'meme',
    'video-script',
  ];

  return (
    <div className={cn('flex flex-wrap gap-2 justify-center', className)}>
      {quickTypes.map((type) => {
        const config = ASSET_TYPES.find((a) => a.type === type);
        if (!config) return null;
        const Icon = getIcon(config.icon);

        return (
          <Badge
            key={type}
            variant="secondary"
            onClick={() => onSelect(type)}
            className={cn(
              'cursor-pointer hover:bg-secondary/80 gap-1.5 px-3 py-1.5',
              'border border-border/40 transition-all active:scale-95'
            )}
          >
            <Icon className="h-3 w-3 opacity-70" />
            {config.label}
          </Badge>
        );
      })}
    </div>
  );
}
