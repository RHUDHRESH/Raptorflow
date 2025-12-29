'use client';

import React, { useMemo } from 'react';
import { FoundationData } from '@/lib/foundation';
import { cn } from '@/lib/utils';
import { Palette } from 'lucide-react';

interface BrandAuraProps {
  data: FoundationData;
  className?: string;
}

interface AuraTheme {
  name: string;
  colors: string[];
  font: string;
  mood: string;
}

/**
 * Maps business attributes to visual mood/aura
 */
function getAuraTheme(data: FoundationData): AuraTheme {
  const { stage, revenueModel, teamSize } = data.business || {};
  const { customerType, decisionStyle } = data.cohorts || {};

  // Premium/Enterprise feel
  if (
    customerType === 'b2b' ||
    (Array.isArray(customerType) && customerType.includes('b2b'))
  ) {
    if (stage === 'growth' || stage === 'scaling') {
      return {
        name: 'Enterprise Authority',
        colors: ['#1a1a2e', '#16213e', '#0f3460', '#e94560'],
        font: 'Serif',
        mood: 'Confident & Established',
      };
    }
    return {
      name: 'Professional Trust',
      colors: ['#2C3E50', '#34495E', '#5D6D7E', '#85929E'],
      font: 'Sans-serif',
      mood: 'Reliable & Expert',
    };
  }

  // Consumer/Startup energy
  if (
    customerType === 'b2c' ||
    (Array.isArray(customerType) && customerType.includes('b2c'))
  ) {
    if (stage === 'idea' || stage === 'early') {
      return {
        name: 'Fresh Disruptor',
        colors: ['#667eea', '#764ba2', '#f093fb', '#f5576c'],
        font: 'Modern',
        mood: 'Bold & Innovative',
      };
    }
    return {
      name: 'Approachable Lifestyle',
      colors: ['#11998e', '#38ef7d', '#56ab2f', '#a8e063'],
      font: 'Friendly',
      mood: 'Warm & Inviting',
    };
  }

  // Default
  return {
    name: 'Balanced Neutral',
    colors: ['#2D3538', '#5B5F61', '#9D9F9F', '#C0C1BE'],
    font: 'Clean',
    mood: 'Versatile & Clear',
  };
}

export function BrandAura({ data, className }: BrandAuraProps) {
  const theme = useMemo(() => getAuraTheme(data), [data]);

  const hasEnoughData = data.business?.stage || data.cohorts?.customerType;

  if (!hasEnoughData) return null;

  return (
    <div
      className={cn(
        'bg-card border border-border rounded-2xl p-6 relative overflow-hidden',
        className
      )}
    >
      {/* Background gradient */}
      <div
        className="absolute inset-0 opacity-10"
        style={{
          background: `linear-gradient(135deg, ${theme.colors.join(', ')})`,
        }}
      />

      <div className="relative">
        <div className="flex items-center gap-2 mb-4">
          <div className="h-8 w-8 rounded-lg bg-muted flex items-center justify-center">
            <Palette className="h-4 w-4 text-muted-foreground" />
          </div>
          <div>
            <span className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground block">
              Brand Aura
            </span>
            <span className="text-sm font-medium text-foreground">
              {theme.name}
            </span>
          </div>
        </div>

        {/* Color swatches */}
        <div className="flex gap-2 mb-4">
          {theme.colors.map((color, i) => (
            <div
              key={i}
              className="h-12 flex-1 rounded-xl shadow-sm transition-transform hover:scale-105"
              style={{ backgroundColor: color }}
            />
          ))}
        </div>

        {/* Attributes */}
        <div className="flex justify-between text-xs text-muted-foreground">
          <span>Font: {theme.font}</span>
          <span>Mood: {theme.mood}</span>
        </div>
      </div>
    </div>
  );
}
