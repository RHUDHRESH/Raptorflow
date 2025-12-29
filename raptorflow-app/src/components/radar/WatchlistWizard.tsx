'use client';

import React, { useState, useEffect, useRef } from 'react';
import {
  Watchlist,
  WatchlistType,
  AlertType,
  ScanFrequency,
  Competitor,
} from './types';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  ArrowRight,
  ArrowLeft,
  X,
  Check,
  Plus,
  Trash2,
  Users,
  TrendingUp,
  Sparkles,
} from 'lucide-react';
import gsap from 'gsap';

interface WatchlistWizardProps {
  onComplete: (
    watchlist: Omit<Watchlist, 'id' | 'createdAt' | 'updatedAt'>
  ) => void;
  onCancel: () => void;
  existingCompetitors?: string[]; // From Foundation
}

type WizardStep =
  | 'name'
  | 'type'
  | 'competitors'
  | 'signals'
  | 'schedule'
  | 'review';

const STEPS: WizardStep[] = [
  'name',
  'type',
  'competitors',
  'signals',
  'schedule',
  'review',
];

const STEP_INFO: Record<WizardStep, { title: string; subtitle: string }> = {
  name: {
    title: 'Name Your Watchlist',
    subtitle: "Give it a memorable name you'll recognize",
  },
  type: {
    title: 'What Are You Tracking?',
    subtitle: 'This helps us optimize the scanning strategy',
  },
  competitors: {
    title: 'Add Competitors',
    subtitle: 'Who should we keep an eye on?',
  },
  signals: {
    title: 'Signal Types',
    subtitle: 'What changes matter most to you?',
  },
  schedule: {
    title: 'Scan Frequency',
    subtitle: 'How often should we check for updates?',
  },
  review: {
    title: 'Review & Launch',
    subtitle: 'Everything looks good. Ready to start monitoring?',
  },
};

const WATCHLIST_TYPES: {
  value: WatchlistType;
  label: string;
  description: string;
  icon: React.ReactNode;
}[] = [
  {
    value: 'competitors',
    label: 'Competitors',
    description: 'Track direct and indirect competitors',
    icon: <Users className="w-5 h-5" />,
  },
  {
    value: 'trends',
    label: 'Industry Trends',
    description: 'Monitor keywords, topics, and shifts',
    icon: <TrendingUp className="w-5 h-5" />,
  },
  {
    value: 'custom',
    label: 'Custom',
    description: 'Build your own monitoring criteria',
    icon: <Sparkles className="w-5 h-5" />,
  },
];

const SIGNAL_TYPES: { value: AlertType; label: string }[] = [
  { value: 'pricing', label: 'Pricing Changes' },
  { value: 'messaging', label: 'Messaging Updates' },
  { value: 'content', label: 'New Content' },
  { value: 'funding', label: 'Funding News' },
  { value: 'feature', label: 'Feature Launches' },
  { value: 'hiring', label: 'Hiring Activity' },
];

const FREQUENCIES: {
  value: ScanFrequency;
  label: string;
  description: string;
}[] = [
  {
    value: 'hourly',
    label: 'Hourly',
    description: 'For fast-moving markets (higher token cost)',
  },
  {
    value: 'daily',
    label: 'Daily',
    description: 'Recommended for most use cases',
  },
  {
    value: 'weekly',
    label: 'Weekly',
    description: 'For slower-moving industries',
  },
];

export function WatchlistWizard({
  onComplete,
  onCancel,
  existingCompetitors = [],
}: WatchlistWizardProps) {
  const [currentStep, setCurrentStep] = useState<WizardStep>('name');
  const [name, setName] = useState('');
  const [type, setType] = useState<WatchlistType>('competitors');
  const [competitors, setCompetitors] = useState<
    { name: string; website?: string }[]
  >([]);
  const [newCompetitorName, setNewCompetitorName] = useState('');
  const [signals, setSignals] = useState<AlertType[]>(['pricing', 'messaging']);
  const [frequency, setFrequency] = useState<ScanFrequency>('daily');

  const contentRef = useRef<HTMLDivElement>(null);

  // GSAP animation on step change
  useEffect(() => {
    if (contentRef.current) {
      gsap.fromTo(
        contentRef.current,
        { opacity: 0, y: 20 },
        { opacity: 1, y: 0, duration: 0.4, ease: 'power2.out' }
      );
    }
  }, [currentStep]);

  const currentStepIndex = STEPS.indexOf(currentStep);
  const isFirstStep = currentStepIndex === 0;
  const isLastStep = currentStepIndex === STEPS.length - 1;

  const canProceed = (): boolean => {
    switch (currentStep) {
      case 'name':
        return name.trim().length > 0;
      case 'type':
        return true;
      case 'competitors':
        return type !== 'competitors' || competitors.length > 0;
      case 'signals':
        return signals.length > 0;
      case 'schedule':
        return true;
      case 'review':
        return true;
      default:
        return false;
    }
  };

  const goNext = () => {
    if (!canProceed()) return;
    if (isLastStep) {
      handleComplete();
    } else {
      setCurrentStep(STEPS[currentStepIndex + 1]);
    }
  };

  const goBack = () => {
    if (!isFirstStep) {
      setCurrentStep(STEPS[currentStepIndex - 1]);
    }
  };

  const addCompetitor = () => {
    if (newCompetitorName.trim()) {
      setCompetitors([...competitors, { name: newCompetitorName.trim() }]);
      setNewCompetitorName('');
    }
  };

  const removeCompetitor = (index: number) => {
    setCompetitors(competitors.filter((_, i) => i !== index));
  };

  const toggleSignal = (signal: AlertType) => {
    setSignals((prev) =>
      prev.includes(signal)
        ? prev.filter((s) => s !== signal)
        : [...prev, signal]
    );
  };

  const handleComplete = () => {
    const watchlist: Omit<Watchlist, 'id' | 'createdAt' | 'updatedAt'> = {
      name,
      type,
      competitors: competitors.map((c, i) => ({
        id: `temp-${i}`,
        name: c.name,
        website: c.website,
        sources: [],
      })),
      signalTypes: signals,
      scanFrequency: frequency,
      status: 'active',
    };
    onComplete(watchlist);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && canProceed()) {
      e.preventDefault();
      goNext();
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex bg-background">
      {/* Left Panel */}
      <div className="w-[400px] bg-[#1A1D1E] text-white flex flex-col p-12 relative overflow-hidden shrink-0">
        {/* Background Pattern */}
        <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent pointer-events-none" />

        {/* Logo */}
        <div className="flex items-center gap-3 mb-16 relative z-10">
          <div className="w-6 h-6 bg-white rounded" />
          <span className="font-bold text-sm tracking-tight">RAPTORFLOW</span>
        </div>

        {/* Section Info */}
        <div className="mb-auto relative z-10">
          <span className="text-[11px] font-semibold uppercase tracking-[0.15em] text-white/50 block mb-3">
            Step {currentStepIndex + 1} of {STEPS.length}
          </span>
          <h2 className="font-serif text-[36px] leading-[1.1] text-white mb-4">
            {STEP_INFO[currentStep].title}
          </h2>
          <p className="text-sm text-white/60 leading-relaxed max-w-[280px]">
            {STEP_INFO[currentStep].subtitle}
          </p>
        </div>

        {/* Progress Steps */}
        <div className="space-y-3 relative z-10">
          {STEPS.map((step, idx) => {
            const isActive = idx === currentStepIndex;
            const isComplete = idx < currentStepIndex;
            return (
              <div
                key={step}
                className={cn(
                  'flex items-center gap-3 transition-opacity',
                  isActive
                    ? 'opacity-100'
                    : isComplete
                      ? 'opacity-70'
                      : 'opacity-40'
                )}
              >
                <div
                  className={cn(
                    'w-2 h-2 rounded-full transition-all',
                    isActive
                      ? 'w-2.5 h-2.5 bg-white shadow-[0_0_12px_rgba(255,255,255,0.5)]'
                      : 'bg-white'
                  )}
                />
                <span className="text-xs font-medium capitalize">{step}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Right Panel */}
      <div className="flex-1 bg-[#F8F9F7] flex flex-col relative overflow-hidden">
        {/* Close Button */}
        <button
          onClick={onCancel}
          className="absolute top-8 right-8 w-10 h-10 flex items-center justify-center rounded-xl border border-border/60 bg-white hover:bg-secondary transition-colors z-20"
        >
          <X className="w-5 h-5 text-muted-foreground" />
        </button>

        {/* Content */}
        <div className="flex-1 flex items-center justify-center p-16">
          <div
            ref={contentRef}
            className="w-full max-w-[600px]"
            onKeyDown={handleKeyDown}
          >
            {/* Step: Name */}
            {currentStep === 'name' && (
              <div className="space-y-8">
                <Input
                  placeholder="e.g., SaaS Competitors"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="h-16 text-xl px-6 rounded-2xl border-2 border-transparent bg-white shadow-[0_4px_16px_rgba(0,0,0,0.03),0_0_0_1px_#E5E6E3] focus:border-foreground focus:shadow-[0_12px_32px_rgba(45,53,56,0.12)] transition-all"
                  autoFocus
                />
              </div>
            )}

            {/* Step: Type */}
            {currentStep === 'type' && (
              <div className="grid gap-4">
                {WATCHLIST_TYPES.map((t) => (
                  <button
                    key={t.value}
                    onClick={() => setType(t.value)}
                    className={cn(
                      'flex items-center gap-4 p-5 rounded-2xl border text-left transition-all',
                      type === t.value
                        ? 'bg-[#1A1D1E] border-[#1A1D1E] text-white shadow-lg'
                        : 'bg-white border-border/60 hover:border-border hover:shadow-sm'
                    )}
                  >
                    <div
                      className={cn(
                        'w-12 h-12 rounded-xl flex items-center justify-center',
                        type === t.value ? 'bg-white/10' : 'bg-secondary/50'
                      )}
                    >
                      {t.icon}
                    </div>
                    <div>
                      <div className="font-semibold">{t.label}</div>
                      <div
                        className={cn(
                          'text-sm',
                          type === t.value
                            ? 'text-white/60'
                            : 'text-muted-foreground'
                        )}
                      >
                        {t.description}
                      </div>
                    </div>
                    {type === t.value && (
                      <div className="ml-auto w-6 h-6 rounded-full bg-white flex items-center justify-center">
                        <Check className="w-4 h-4 text-[#1A1D1E]" />
                      </div>
                    )}
                  </button>
                ))}
              </div>
            )}

            {/* Step: Competitors */}
            {currentStep === 'competitors' && (
              <div className="space-y-6">
                {/* Suggestions from Foundation */}
                {existingCompetitors.length > 0 && (
                  <div className="p-4 bg-secondary/30 rounded-xl">
                    <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                      From your Foundation
                    </span>
                    <div className="flex flex-wrap gap-2 mt-3">
                      {existingCompetitors.map((comp) => (
                        <button
                          key={comp}
                          onClick={() => {
                            if (!competitors.find((c) => c.name === comp)) {
                              setCompetitors([...competitors, { name: comp }]);
                            }
                          }}
                          className="px-3 py-1.5 bg-white rounded-lg text-sm font-medium hover:bg-secondary transition-colors"
                        >
                          + {comp}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Add New */}
                <div className="flex gap-3">
                  <Input
                    placeholder="Competitor name..."
                    value={newCompetitorName}
                    onChange={(e) => setNewCompetitorName(e.target.value)}
                    onKeyDown={(e) =>
                      e.key === 'Enter' && (e.preventDefault(), addCompetitor())
                    }
                    className="h-12 rounded-xl"
                  />
                  <Button
                    onClick={addCompetitor}
                    className="h-12 px-6 rounded-xl"
                  >
                    <Plus className="w-4 h-4" />
                  </Button>
                </div>

                {/* List */}
                {competitors.length > 0 && (
                  <div className="space-y-2">
                    {competitors.map((comp, idx) => (
                      <div
                        key={idx}
                        className="flex items-center justify-between p-4 bg-white rounded-xl border border-border/40"
                      >
                        <span className="font-medium">{comp.name}</span>
                        <button
                          onClick={() => removeCompetitor(idx)}
                          className="p-2 hover:bg-secondary rounded-lg transition-colors text-muted-foreground hover:text-red-500"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Step: Signals */}
            {currentStep === 'signals' && (
              <div className="grid grid-cols-2 gap-4">
                {SIGNAL_TYPES.map((signal) => (
                  <button
                    key={signal.value}
                    onClick={() => toggleSignal(signal.value)}
                    className={cn(
                      'flex items-center gap-3 p-4 rounded-xl border text-left transition-all',
                      signals.includes(signal.value)
                        ? 'bg-[#1A1D1E] border-[#1A1D1E] text-white'
                        : 'bg-white border-border/60 hover:border-border'
                    )}
                  >
                    <div
                      className={cn(
                        'w-5 h-5 rounded border-2 flex items-center justify-center transition-all',
                        signals.includes(signal.value)
                          ? 'bg-white border-white'
                          : 'border-border'
                      )}
                    >
                      {signals.includes(signal.value) && (
                        <Check className="w-3 h-3 text-[#1A1D1E]" />
                      )}
                    </div>
                    <span className="font-medium text-sm">{signal.label}</span>
                  </button>
                ))}
              </div>
            )}

            {/* Step: Schedule */}
            {currentStep === 'schedule' && (
              <div className="space-y-4">
                {FREQUENCIES.map((freq) => (
                  <button
                    key={freq.value}
                    onClick={() => setFrequency(freq.value)}
                    className={cn(
                      'w-full flex items-center gap-4 p-5 rounded-2xl border text-left transition-all',
                      frequency === freq.value
                        ? 'bg-[#1A1D1E] border-[#1A1D1E] text-white shadow-lg'
                        : 'bg-white border-border/60 hover:border-border'
                    )}
                  >
                    <div
                      className={cn(
                        'w-5 h-5 rounded-full border-2 flex items-center justify-center',
                        frequency === freq.value
                          ? 'border-white bg-white'
                          : 'border-border'
                      )}
                    >
                      {frequency === freq.value && (
                        <div className="w-2 h-2 rounded-full bg-[#1A1D1E]" />
                      )}
                    </div>
                    <div>
                      <div className="font-semibold">{freq.label}</div>
                      <div
                        className={cn(
                          'text-sm',
                          frequency === freq.value
                            ? 'text-white/60'
                            : 'text-muted-foreground'
                        )}
                      >
                        {freq.description}
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}

            {/* Step: Review */}
            {currentStep === 'review' && (
              <div className="bg-white rounded-2xl border border-border/60 overflow-hidden">
                <div className="p-6 space-y-4">
                  <div className="flex items-center justify-between py-3 border-b border-border/40">
                    <span className="text-muted-foreground">Name</span>
                    <span className="font-semibold">{name}</span>
                  </div>
                  <div className="flex items-center justify-between py-3 border-b border-border/40">
                    <span className="text-muted-foreground">Type</span>
                    <span className="font-semibold capitalize">{type}</span>
                  </div>
                  <div className="flex items-center justify-between py-3 border-b border-border/40">
                    <span className="text-muted-foreground">Competitors</span>
                    <span className="font-semibold">{competitors.length}</span>
                  </div>
                  <div className="flex items-center justify-between py-3 border-b border-border/40">
                    <span className="text-muted-foreground">Signals</span>
                    <span className="font-semibold">{signals.join(', ')}</span>
                  </div>
                  <div className="flex items-center justify-between py-3">
                    <span className="text-muted-foreground">Frequency</span>
                    <span className="font-semibold capitalize">
                      {frequency}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="px-16 py-8 border-t border-border/40 flex items-center justify-between">
          <div className="text-xs text-muted-foreground">
            {!isFirstStep && (
              <Button variant="ghost" onClick={goBack} className="gap-2">
                <ArrowLeft className="w-4 h-4" />
                Back
              </Button>
            )}
          </div>
          <Button
            onClick={goNext}
            disabled={!canProceed()}
            className="h-14 px-10 rounded-xl text-[15px] font-semibold gap-3"
          >
            {isLastStep ? 'Launch Watchlist' : 'Continue'}
            <ArrowRight className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
