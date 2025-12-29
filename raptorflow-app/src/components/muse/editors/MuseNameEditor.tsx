'use client';

import React, { useState, useCallback } from 'react';
import { cn } from '@/lib/utils';
import {
  X,
  Check,
  Sparkles,
  RefreshCw,
  Lightbulb,
  ThumbsUp,
  ThumbsDown,
  Copy,
} from 'lucide-react';

interface NameEditorProps {
  title?: string;
  initialNames?: NameOption[];
  context?: {
    productDescription?: string;
    targetAudience?: string;
    keywords?: string[];
  };
  onSave?: (selectedName: string) => void;
  onClose?: () => void;
  onChange?: () => void;
  className?: string;
}

interface NameOption {
  id: string;
  name: string;
  type: 'product';
  rationale?: string;
  score?: number; // 0-100
  liked?: boolean;
}

// Mock name generation
function generateMockNames(context?: NameEditorProps['context']): NameOption[] {
  const productNames = [
    { name: 'Velocity', rationale: 'Suggests speed and momentum' },
    { name: 'Catalyst', rationale: 'Implies transformation and acceleration' },
    { name: 'Forge', rationale: 'Evokes creation and craftsmanship' },
    { name: 'Meridian', rationale: 'Feels premium and directional' },
    { name: 'Apex', rationale: 'Connotes leadership and peak performance' },
  ];

  return productNames.map((p, i) => ({
    id: `product-${i}`,
    name: p.name,
    type: 'product' as const,
    rationale: p.rationale,
    score: 70 + Math.floor(Math.random() * 25),
  }));
}

export function MuseNameEditor({
  title = 'Name Ideas',
  initialNames,
  context,
  onSave,
  onClose,
  onChange,
  className,
}: NameEditorProps) {
  const [names, setNames] = useState<NameOption[]>(
    initialNames || generateMockNames(context)
  );
  const [selectedName, setSelectedName] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);

  const handleLike = useCallback((id: string, liked: boolean) => {
    setNames((prev) => prev.map((n) => (n.id === id ? { ...n, liked } : n)));
    onChange?.();
  }, [onChange]);

  const handleRegenerate = useCallback(async () => {
    setIsGenerating(true);
    await new Promise((r) => setTimeout(r, 1500));
    setNames(generateMockNames(context));
    setIsGenerating(false);
  }, [context]);

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <div className={cn('flex flex-col h-full bg-background', className)}>
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-border/40">
        <div className="flex items-center gap-3">
          {onClose && (
            <button
              onClick={onClose}
              className="h-8 w-8 rounded-lg flex items-center justify-center hover:bg-muted transition-colors"
            >
              <X className="h-4 w-4" />
            </button>
          )}
          <div>
            <h1 className="text-lg font-semibold">{title}</h1>
            <p className="text-xs text-muted-foreground">
              Select or refine your perfect name
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleRegenerate}
            disabled={isGenerating}
            className={cn(
              'flex items-center gap-2 h-9 px-4 rounded-lg',
              'border border-border/60 bg-card',
              'text-sm font-medium',
              'hover:bg-muted transition-colors',
              'disabled:opacity-50'
            )}
          >
            <RefreshCw
              className={cn('h-4 w-4', isGenerating && 'animate-spin')}
            />
            Regenerate
          </button>
          <button
            onClick={() => selectedName && onSave?.(selectedName)}
            disabled={!selectedName}
            className={cn(
              'h-9 px-5 rounded-lg',
              'bg-foreground text-background',
              'text-sm font-medium',
              'hover:opacity-90 transition-opacity',
              'disabled:opacity-30 disabled:cursor-not-allowed'
            )}
          >
            <Check className="h-4 w-4 mr-2 inline" />
            Use This Name
          </button>
        </div>
      </div>

      {/* Names Grid */}
      <div className="flex-1 overflow-auto p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-4xl mx-auto">
          {names.map((option) => (
            <div
              key={option.id}
              onClick={() => setSelectedName(option.name)}
              className={cn(
                'group relative p-5 rounded-2xl border cursor-pointer transition-all duration-200',
                selectedName === option.name
                  ? 'border-foreground bg-foreground/5 ring-2 ring-foreground/10'
                  : 'border-border/60 bg-card hover:border-border hover:shadow-sm'
              )}
            >
              {/* Name */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div
                    className={cn(
                      'h-10 w-10 rounded-xl flex items-center justify-center',
                      'bg-amber-500/10'
                    )}
                  >
                    <Lightbulb className="h-5 w-5 text-amber-600" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold tracking-tight">
                      {option.name}
                    </h3>
                    <p className="text-xs text-muted-foreground">
                      Product name
                    </p>
                  </div>
                </div>

                {/* Score badge */}
                {option.score && (
                  <div
                    className={cn(
                      'px-2.5 py-1 rounded-full text-xs font-medium',
                      option.score >= 80
                        ? 'bg-emerald-500/10 text-emerald-600'
                        : option.score >= 60
                          ? 'bg-amber-500/10 text-amber-600'
                          : 'bg-zinc-500/10 text-zinc-500'
                    )}
                  >
                    {option.score}%
                  </div>
                )}
              </div>

              {/* Rationale or availability */}
              {option.rationale && (
                <p className="text-sm text-muted-foreground mb-4">
                  {option.rationale}
                </p>
              )}

              {/* Actions */}
              <div className="flex items-center gap-2 mt-4 pt-4 border-t border-border/40">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleLike(option.id, true);
                  }}
                  className={cn(
                    'h-8 w-8 rounded-lg flex items-center justify-center transition-colors',
                    option.liked === true
                      ? 'bg-emerald-500/10 text-emerald-600'
                      : 'hover:bg-muted text-muted-foreground'
                  )}
                >
                  <ThumbsUp className="h-4 w-4" />
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleLike(option.id, false);
                  }}
                  className={cn(
                    'h-8 w-8 rounded-lg flex items-center justify-center transition-colors',
                    option.liked === false
                      ? 'bg-red-500/10 text-red-500'
                      : 'hover:bg-muted text-muted-foreground'
                  )}
                >
                  <ThumbsDown className="h-4 w-4" />
                </button>
                <div className="flex-1" />
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleCopy(option.name);
                  }}
                  className="h-8 w-8 rounded-lg flex items-center justify-center hover:bg-muted text-muted-foreground transition-colors"
                >
                  <Copy className="h-4 w-4" />
                </button>
              </div>

              {/* Selection indicator */}
              {selectedName === option.name && (
                <div className="absolute top-3 right-3 h-6 w-6 rounded-full bg-foreground flex items-center justify-center">
                  <Check className="h-3.5 w-3.5 text-background" />
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Empty state */}
        {names.length === 0 && (
          <div className="text-center py-16">
            <div className="w-14 h-14 bg-muted/30 rounded-full flex items-center justify-center mx-auto mb-4">
              <Sparkles className="h-7 w-7 text-muted-foreground/50" />
            </div>
            <p className="text-sm font-medium mb-1">No names yet</p>
            <p className="text-xs text-muted-foreground">
              Click Regenerate to create new options
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
