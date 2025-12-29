'use client';

import React, { useState } from 'react';
import { cn } from '@/lib/utils';
import { Sparkles, Zap, MessageSquare, RefreshCw } from 'lucide-react';

interface CaptionSuggestion {
  id: string;
  text: string;
  style: 'funny' | 'relatable' | 'provocative' | 'informative';
  score?: number;
}

interface CaptionSuggestionsProps {
  imageDescription?: string;
  onSelect?: (caption: string) => void;
  className?: string;
}

// Mock caption generator - would call AI in production
function generateCaptions(description: string): CaptionSuggestion[] {
  return [
    {
      id: 'cap-1',
      text: 'When the coffee kicks in and you finally understand the codebase 💀',
      style: 'funny',
      score: 85,
    },
    {
      id: 'cap-2',
      text: "POV: You're explaining your startup to your parents for the 47th time",
      style: 'relatable',
      score: 78,
    },
    {
      id: 'cap-3',
      text: "Most founders won't tell you this, but...",
      style: 'provocative',
      score: 72,
    },
    {
      id: 'cap-4',
      text: "The #1 mistake that's killing your marketing: [Thread] 🧵",
      style: 'informative',
      score: 68,
    },
  ];
}

const STYLE_ICONS = {
  funny: '😂',
  relatable: '🤝',
  provocative: '🔥',
  informative: '📚',
};

const STYLE_LABELS = {
  funny: 'Funny',
  relatable: 'Relatable',
  provocative: 'Provocative',
  informative: 'Informative',
};

export function CaptionSuggestions({
  imageDescription = '',
  onSelect,
  className,
}: CaptionSuggestionsProps) {
  const [captions, setCaptions] = useState<CaptionSuggestion[]>(() =>
    generateCaptions(imageDescription)
  );
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [filter, setFilter] = useState<CaptionSuggestion['style'] | 'all'>(
    'all'
  );

  const handleRegenerate = async () => {
    setIsGenerating(true);
    await new Promise((r) => setTimeout(r, 1000));
    setCaptions(generateCaptions(imageDescription));
    setIsGenerating(false);
  };

  const handleSelect = (caption: CaptionSuggestion) => {
    setSelectedId(caption.id);
    onSelect?.(caption.text);
  };

  const filteredCaptions =
    filter === 'all' ? captions : captions.filter((c) => c.style === filter);

  return (
    <div className={cn('space-y-4', className)}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <MessageSquare className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm font-medium">Caption Ideas</span>
        </div>
        <button
          onClick={handleRegenerate}
          disabled={isGenerating}
          className={cn(
            'flex items-center gap-1.5 px-2.5 py-1 rounded-lg',
            'text-xs hover:bg-muted transition-colors',
            isGenerating && 'opacity-50'
          )}
        >
          <RefreshCw
            className={cn('h-3 w-3', isGenerating && 'animate-spin')}
          />
          {isGenerating ? 'Generating...' : 'Refresh'}
        </button>
      </div>

      {/* Style filter */}
      <div className="flex items-center gap-1 flex-wrap">
        <button
          onClick={() => setFilter('all')}
          className={cn(
            'px-2.5 py-1 rounded-full text-xs transition-colors',
            filter === 'all'
              ? 'bg-foreground text-background'
              : 'bg-muted hover:bg-muted/80'
          )}
        >
          All
        </button>
        {(['funny', 'relatable', 'provocative', 'informative'] as const).map(
          (style) => (
            <button
              key={style}
              onClick={() => setFilter(style)}
              className={cn(
                'px-2.5 py-1 rounded-full text-xs transition-colors',
                filter === style
                  ? 'bg-foreground text-background'
                  : 'bg-muted hover:bg-muted/80'
              )}
            >
              {STYLE_ICONS[style]} {STYLE_LABELS[style]}
            </button>
          )
        )}
      </div>

      {/* Captions list */}
      <div className="space-y-2">
        {filteredCaptions.map((caption) => (
          <button
            key={caption.id}
            onClick={() => handleSelect(caption)}
            className={cn(
              'w-full p-3 rounded-xl text-left transition-all',
              'border',
              selectedId === caption.id
                ? 'border-foreground/30 bg-foreground/5'
                : 'border-border/60 hover:border-foreground/20 bg-card'
            )}
          >
            <div className="flex items-start gap-3">
              <span className="text-lg shrink-0">
                {STYLE_ICONS[caption.style]}
              </span>
              <div className="flex-1 min-w-0">
                <p className="text-sm">{caption.text}</p>
                <div className="flex items-center gap-2 mt-2">
                  <span className="text-xs text-muted-foreground">
                    {STYLE_LABELS[caption.style]}
                  </span>
                  {caption.score && (
                    <>
                      <span className="text-muted-foreground/40">·</span>
                      <span
                        className={cn(
                          'text-xs font-medium',
                          caption.score >= 75 && 'text-green-500',
                          caption.score >= 50 &&
                            caption.score < 75 &&
                            'text-amber-500',
                          caption.score < 50 && 'text-red-500'
                        )}
                      >
                        {caption.score}% viral potential
                      </span>
                    </>
                  )}
                </div>
              </div>
              {selectedId === caption.id && (
                <Zap className="h-4 w-4 text-amber-500 shrink-0" />
              )}
            </div>
          </button>
        ))}
      </div>

      {/* Custom caption input */}
      <div className="pt-2">
        <p className="text-xs text-muted-foreground mb-2">Or write your own:</p>
        <textarea
          placeholder="Type a custom caption..."
          className={cn(
            'w-full p-3 rounded-lg resize-none',
            'border border-border/60 bg-card',
            'text-sm placeholder:text-muted-foreground/40',
            'focus:outline-none focus:border-foreground/30'
          )}
          rows={2}
          onBlur={(e) => {
            if (e.target.value.trim()) {
              onSelect?.(e.target.value.trim());
            }
          }}
        />
      </div>
    </div>
  );
}
