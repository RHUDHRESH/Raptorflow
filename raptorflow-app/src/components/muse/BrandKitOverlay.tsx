'use client';

import React from 'react';
import { cn } from '@/lib/utils';
import { Palette, Check } from 'lucide-react';

interface BrandKitOverlayProps {
  onApply?: () => void;
  className?: string;
}

// Mock brand kit data - would come from Foundation
const BRAND_KIT = {
  primaryColor: '#2D3538',
  secondaryColor: '#5B5F61',
  accentColor: '#D7C9AE',
  fontFamily: 'Inter',
  logoUrl: '/logo.png',
};

const CROP_PRESETS = [
  {
    id: 'square',
    label: 'Square',
    ratio: '1:1',
    width: 1080,
    height: 1080,
    platform: 'Instagram',
  },
  {
    id: 'landscape',
    label: 'Landscape',
    ratio: '16:9',
    width: 1920,
    height: 1080,
    platform: 'YouTube',
  },
  {
    id: 'portrait',
    label: 'Portrait',
    ratio: '4:5',
    width: 1080,
    height: 1350,
    platform: 'Instagram',
  },
  {
    id: 'stories',
    label: 'Stories',
    ratio: '9:16',
    width: 1080,
    height: 1920,
    platform: 'IG/TikTok',
  },
  {
    id: 'linkedin',
    label: 'LinkedIn',
    ratio: '1.91:1',
    width: 1200,
    height: 628,
    platform: 'LinkedIn',
  },
  {
    id: 'twitter',
    label: 'Twitter',
    ratio: '16:9',
    width: 1600,
    height: 900,
    platform: 'Twitter',
  },
];

export function BrandKitOverlay({ onApply, className }: BrandKitOverlayProps) {
  const [applied, setApplied] = React.useState(false);

  const handleApply = () => {
    setApplied(true);
    onApply?.();
    setTimeout(() => setApplied(false), 2000);
  };

  return (
    <div className={cn('space-y-4', className)}>
      {/* Header */}
      <div className="flex items-center gap-2">
        <Palette className="h-4 w-4 text-muted-foreground" />
        <span className="text-sm font-medium">Brand Kit</span>
      </div>

      {/* Colors */}
      <div className="space-y-2">
        <p className="text-xs text-muted-foreground uppercase tracking-wide">
          Colors
        </p>
        <div className="flex items-center gap-2">
          <div
            className="w-8 h-8 rounded-lg border border-border/60 cursor-pointer hover:scale-110 transition-transform"
            style={{ backgroundColor: BRAND_KIT.primaryColor }}
            title="Primary"
          />
          <div
            className="w-8 h-8 rounded-lg border border-border/60 cursor-pointer hover:scale-110 transition-transform"
            style={{ backgroundColor: BRAND_KIT.secondaryColor }}
            title="Secondary"
          />
          <div
            className="w-8 h-8 rounded-lg border border-border/60 cursor-pointer hover:scale-110 transition-transform"
            style={{ backgroundColor: BRAND_KIT.accentColor }}
            title="Accent"
          />
        </div>
      </div>

      {/* Font */}
      <div className="space-y-2">
        <p className="text-xs text-muted-foreground uppercase tracking-wide">
          Typography
        </p>
        <p className="text-sm" style={{ fontFamily: BRAND_KIT.fontFamily }}>
          {BRAND_KIT.fontFamily}
        </p>
      </div>

      {/* Apply button */}
      <button
        onClick={handleApply}
        disabled={applied}
        className={cn(
          'w-full h-9 rounded-lg',
          'flex items-center justify-center gap-2',
          'text-sm font-medium transition-all',
          applied
            ? 'bg-green-500 text-white'
            : 'bg-foreground text-background hover:opacity-90'
        )}
      >
        {applied ? (
          <>
            <Check className="h-4 w-4" />
            Applied!
          </>
        ) : (
          'Apply Brand Kit'
        )}
      </button>
    </div>
  );
}

// Smart crop presets for visual editor
interface SmartCropPresetsProps {
  onSelect?: (preset: (typeof CROP_PRESETS)[0]) => void;
  selected?: string;
  className?: string;
}

export function SmartCropPresets({
  onSelect,
  selected,
  className,
}: SmartCropPresetsProps) {
  return (
    <div className={cn('space-y-3', className)}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
          Smart Crop
        </span>
      </div>

      {/* Presets grid */}
      <div className="grid grid-cols-2 gap-2">
        {CROP_PRESETS.map((preset) => (
          <button
            key={preset.id}
            onClick={() => onSelect?.(preset)}
            className={cn(
              'flex flex-col items-center gap-1 p-2 rounded-lg',
              'border text-xs transition-colors',
              selected === preset.id
                ? 'border-foreground bg-foreground/5'
                : 'border-border/60 hover:border-foreground/30'
            )}
          >
            {/* Aspect ratio preview */}
            <div
              className={cn(
                'bg-muted rounded',
                preset.id === 'square' && 'w-6 h-6',
                preset.id === 'landscape' && 'w-8 h-5',
                preset.id === 'portrait' && 'w-5 h-6',
                preset.id === 'stories' && 'w-4 h-7',
                preset.id === 'linkedin' && 'w-8 h-4',
                preset.id === 'twitter' && 'w-8 h-5'
              )}
            />
            <span className="font-medium">{preset.label}</span>
            <span className="text-muted-foreground">{preset.platform}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
