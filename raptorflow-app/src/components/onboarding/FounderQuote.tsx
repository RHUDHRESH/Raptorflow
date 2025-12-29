'use client';

import React, { useState } from 'react';
import { FoundationData } from '@/lib/foundation';
import { cn } from '@/lib/utils';
import { Quote, Copy, Twitter, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface FounderQuoteProps {
  data: FoundationData;
  className?: string;
}

/**
 * Generates a shareable founder quote from messaging pillars
 */
export function FounderQuote({ data, className }: FounderQuoteProps) {
  const [copied, setCopied] = useState(false);

  const { beliefPillar, promisePillar, proofPillar } = data.messaging || {};

  // Only show if we have at least one pillar
  const hasContent = beliefPillar || promisePillar || proofPillar;

  if (!hasContent) return null;

  const quoteText = [
    beliefPillar && `We believe ${beliefPillar.toLowerCase()}.`,
    promisePillar && `We promise ${promisePillar.toLowerCase()}.`,
    proofPillar && `We prove it by ${proofPillar.toLowerCase()}.`,
  ]
    .filter(Boolean)
    .join(' ');

  const handleCopy = async () => {
    await navigator.clipboard.writeText(quoteText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleTweet = () => {
    const tweetUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(quoteText)}`;
    window.open(tweetUrl, '_blank');
  };

  return (
    <div
      className={cn(
        'bg-card border border-border rounded-2xl p-6 relative',
        className
      )}
    >
      {/* Quote icon */}
      <div className="absolute -top-3 left-6 bg-primary text-primary-foreground rounded-lg p-2">
        <Quote className="h-4 w-4" />
      </div>

      <div className="pt-4">
        <p className="font-serif text-lg leading-relaxed text-foreground italic">
          "{quoteText}"
        </p>

        <div className="mt-4 pt-4 border-t border-border flex items-center justify-between">
          <span className="text-xs text-muted-foreground">
            — {data.business?.name || 'Founder'}
          </span>

          <div className="flex gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleCopy}
              className="h-8 px-3 text-xs gap-1.5"
            >
              {copied ? (
                <Check className="h-3 w-3" />
              ) : (
                <Copy className="h-3 w-3" />
              )}
              {copied ? 'Copied!' : 'Copy'}
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleTweet}
              className="h-8 px-3 text-xs gap-1.5"
            >
              <Twitter className="h-3 w-3" /> Tweet
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
