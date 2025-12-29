'use client';

import React, { useState } from 'react';
import { SoundbiteVariants, Soundbite, SoundbiteType } from '@/lib/foundation';
import { Button } from '@/components/ui/button';
import { ArrowRight, Copy, Check, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';

interface VariantsFactoryProps {
  soundbites: Soundbite[];
  variants: SoundbiteVariants[];
  onContinue: () => void;
}

const TYPE_LABELS: Partial<Record<SoundbiteType, string>> = {
  'problem-reveal': 'Problem Reveal',
  agitate: 'Agitate',
  'jtbd-progress': 'JTBD Progress',
  mechanism: 'Mechanism',
  'proof-punch': 'Proof Punch',
  'objection-kill': 'Objection Kill',
  action: 'Action',
};

function CopyableText({ text, label }: { text: string; label: string }) {
  const [copied, setCopied] = useState(false);

  const copy = async () => {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    toast.success(`${label} copied`);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div className="group relative bg-muted/50 rounded-lg p-3 hover:bg-muted transition-colors">
      <p className="text-sm pr-8">{text}</p>
      <button
        onClick={copy}
        className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity"
      >
        {copied ? (
          <Check className="h-4 w-4 text-green-500" />
        ) : (
          <Copy className="h-4 w-4 text-muted-foreground" />
        )}
      </button>
    </div>
  );
}

function VariantSection({ title, items }: { title: string; items: string[] }) {
  return (
    <div>
      <h4 className="text-sm font-medium text-muted-foreground mb-2">
        {title}
      </h4>
      <div className="space-y-2">
        {items.map((item, i) => (
          <CopyableText key={i} text={item} label={title} />
        ))}
      </div>
    </div>
  );
}

export function VariantsFactory({
  soundbites,
  variants,
  onContinue,
}: VariantsFactoryProps) {
  const [selectedIdx, setSelectedIdx] = useState(0);

  const selectedSb = soundbites[selectedIdx];
  const selectedVariant = variants.find(
    (v) => v.soundbiteId === selectedSb?.id
  );

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-serif font-bold text-foreground">
          Variants Factory
        </h1>
        <p className="text-muted-foreground max-w-lg mx-auto">
          Channel-ready versions of each soundbite. Click to copy.
        </p>
      </div>

      {/* Soundbite Selector */}
      <div className="flex flex-wrap justify-center gap-2">
        {soundbites.map((sb, i) => (
          <button
            key={sb.id}
            onClick={() => setSelectedIdx(i)}
            className={cn(
              'px-3 py-2 rounded-lg text-sm transition-colors',
              selectedIdx === i
                ? 'bg-primary text-primary-foreground'
                : 'bg-muted text-muted-foreground hover:text-foreground'
            )}
          >
            {TYPE_LABELS[sb.type]}
          </button>
        ))}
      </div>

      {/* Source Soundbite */}
      {selectedSb && (
        <div className="max-w-2xl mx-auto bg-card border rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles className="h-4 w-4 text-primary" />
            <span className="text-sm font-medium">Source Soundbite</span>
          </div>
          <p className="text-sm">{selectedSb.text}</p>
        </div>
      )}

      {/* Variants Grid */}
      {selectedVariant && (
        <div className="max-w-3xl mx-auto space-y-6">
          {/* Landing Hero */}
          <div>
            <h4 className="text-sm font-medium text-muted-foreground mb-2">
              Landing Hero
            </h4>
            <CopyableText
              text={selectedVariant.landingHero}
              label="Landing Hero"
            />
          </div>

          {/* Subhead */}
          <div>
            <h4 className="text-sm font-medium text-muted-foreground mb-2">
              Subhead
            </h4>
            <CopyableText text={selectedVariant.subhead} label="Subhead" />
          </div>

          {/* Ad Hooks */}
          <VariantSection title="Ad Hooks" items={selectedVariant.adHooks} />

          {/* Email Subjects */}
          <VariantSection
            title="Email Subject Lines"
            items={selectedVariant.emailSubjects}
          />

          {/* Sales Opener */}
          <div>
            <h4 className="text-sm font-medium text-muted-foreground mb-2">
              Sales Opener
            </h4>
            <CopyableText
              text={selectedVariant.salesOpener}
              label="Sales Opener"
            />
          </div>

          {/* LinkedIn Opener */}
          <div>
            <h4 className="text-sm font-medium text-muted-foreground mb-2">
              LinkedIn Opener
            </h4>
            <CopyableText
              text={selectedVariant.linkedInOpener}
              label="LinkedIn Opener"
            />
          </div>
        </div>
      )}

      {/* Continue Button */}
      <div className="flex justify-center pt-4">
        <Button
          size="lg"
          onClick={onContinue}
          className="px-8 py-6 text-lg rounded-xl"
        >
          Continue <ArrowRight className="h-5 w-5 ml-2" />
        </Button>
      </div>
    </div>
  );
}
