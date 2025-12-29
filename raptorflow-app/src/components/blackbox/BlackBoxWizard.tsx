'use client';

import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { GoalSelector } from './GoalSelector';
import { RiskSlider } from './RiskSlider';
import { ExperimentBuilder } from './ExperimentBuilder';
import {
  GoalType,
  GoalSelection,
  RiskLevel,
  ChannelType,
  Experiment,
  ExperimentStatus,
} from '@/lib/blackbox-types';
import {
  ArrowLeft,
  ArrowRight,
  Sparkles,
  Box,
  X,
  Mail,
  Linkedin,
  Twitter,
  Video,
  Globe,
  Instagram,
  Music2,
  Facebook,
  Search,
  FileText,
  Mic,
  CheckCircle2,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { generateExperiments } from '@/lib/blackbox/generator';
import { toast } from 'sonner';
import { Input } from '@/components/ui/input';

interface BlackBoxWizardProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onComplete: (experiments: Experiment[]) => void;
}

type WizardStep =
  | 'goal'
  | 'risk'
  | 'channel'
  | 'building'
  | 'generating'
  | 'results';

const CHANNELS = [
  { id: 'email' as ChannelType, label: 'Email', icon: Mail },
  { id: 'linkedin' as ChannelType, label: 'LinkedIn', icon: Linkedin },
  { id: 'twitter' as ChannelType, label: 'Twitter/X', icon: Twitter },
  { id: 'instagram' as ChannelType, label: 'Instagram', icon: Instagram },
  { id: 'tiktok' as ChannelType, label: 'TikTok', icon: Music2 },
  { id: 'youtube' as ChannelType, label: 'YouTube', icon: Video },
  { id: 'facebook' as ChannelType, label: 'Facebook', icon: Facebook },
  { id: 'google_ads' as ChannelType, label: 'Google Ads', icon: Search },
  { id: 'website' as ChannelType, label: 'Website', icon: Globe },
  { id: 'blog' as ChannelType, label: 'Blog/SEO', icon: FileText },
  { id: 'podcast' as ChannelType, label: 'Podcast', icon: Mic },
  { id: 'other' as ChannelType, label: 'Other', icon: Globe },
];

export function BlackBoxWizard({
  open,
  onOpenChange,
  onComplete,
}: BlackBoxWizardProps) {
  const [step, setStep] = useState<WizardStep>('goal');
  const [goals, setGoals] = useState<GoalSelection | null>(null);
  const [risk, setRisk] = useState<RiskLevel | null>(null);
  const [channel, setChannel] = useState<ChannelType | null>(null);
  const [otherChannelText, setOtherChannelText] = useState('');
  const [generatedExperiments, setGeneratedExperiments] = useState<
    Experiment[]
  >([]);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (open) {
      setStep('goal');
      setGoals(null);
      setRisk(null);
      setChannel(null);
      setOtherChannelText('');
      setGeneratedExperiments([]);
      setProgress(0);
    }
  }, [open]);

  const handleGenerate = () => {
    if (!goals || !risk || !channel) return;
    if (channel === 'other' && !otherChannelText.trim()) {
      toast.error('Please specify the channel name');
      return;
    }

    setStep('generating');
    setProgress(0);

    const interval = setInterval(() => {
      setProgress((prev) =>
        prev >= 100 ? (clearInterval(interval), 100) : prev + 12
      );
    }, 150);

    setTimeout(() => {
      clearInterval(interval);

      // Use real generator with primary goal
      const experiments = generateExperiments(
        {
          goal: goals.primary,
          risk_level: risk,
          channel,
        },
        3
      );

      setGeneratedExperiments(experiments);
      setStep('results');
    }, 1800);
  };

  const handleNext = () => {
    if (step === 'goal' && goals) setStep('risk');
    else if (step === 'risk' && risk) setStep('channel');
    else if (step === 'channel' && channel) setStep('building');
  };

  const handleBack = () => {
    if (step === 'risk') setStep('goal');
    else if (step === 'channel') setStep('risk');
    else if (step === 'building') setStep('channel');
  };

  const handleManualComplete = (exp: Experiment) => {
    setGeneratedExperiments([exp]);
    setStep('results');
  };

  const handleComplete = () => {
    onComplete(generatedExperiments);
    onOpenChange(false);
  };

  const canProceed =
    (step === 'goal' && !!goals) ||
    (step === 'risk' && !!risk) ||
    (step === 'channel' &&
      !!channel &&
      (channel !== 'other' || otherChannelText.trim()));

  const stepNum =
    step === 'goal' ? 1 : step === 'risk' ? 2 : step === 'channel' ? 3 : 4;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        className={cn(
          'p-0 gap-0 bg-white dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 shadow-xl rounded-2xl overflow-hidden transition-all duration-500',
          step === 'building' ? 'max-w-6xl' : 'max-w-2xl'
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-zinc-100 dark:border-zinc-900">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-zinc-900 dark:bg-white flex items-center justify-center">
              <Box className="w-4 h-4 text-white dark:text-zinc-900" />
            </div>
            <div>
              <h3 className="font-semibold text-sm font-sans">
                {step === 'building' ? 'Experiment Design' : 'New Black Box'}
              </h3>
              <p className="text-[10px] text-zinc-400 font-sans uppercase tracking-widest">
                {step === 'generating'
                  ? 'Generating...'
                  : step === 'results'
                    ? 'Ready'
                    : `Phase ${stepNum} of 4`}
              </p>
            </div>
          </div>
          <button
            onClick={() => onOpenChange(false)}
            className="w-6 h-6 rounded flex items-center justify-center hover:bg-zinc-100 dark:hover:bg-zinc-900"
          >
            <X className="w-4 h-4 text-zinc-400" />
          </button>
        </div>

        {/* Progress */}
        <div className="h-0.5 bg-zinc-100 dark:bg-zinc-900">
          <div
            className="h-full bg-stone-800 dark:bg-white transition-all duration-700"
            style={{
              width:
                step === 'results'
                  ? '100%'
                  : step === 'generating'
                    ? `${progress}%`
                    : `${stepNum * 25}%`,
            }}
          />
        </div>

        {/* Content */}
        <div
          className={cn(
            'flex items-center justify-center overflow-y-auto custom-scrollbar',
            step === 'building' ? 'p-8 max-h-[85vh]' : 'p-6 min-h-[380px]'
          )}
        >
          {step === 'goal' && (
            <GoalSelector selectedGoals={goals} onSelect={setGoals} />
          )}
          {step === 'risk' && <RiskSlider value={risk} onChange={setRisk} />}

          {step === 'channel' && (
            <div className="w-full space-y-5 text-center">
              <div>
                <h2 className="text-xl font-semibold mb-1 font-sans">
                  Where will you run these?
                </h2>
                <p className="text-sm text-zinc-500 font-sans">
                  Pick your primary channel.
                </p>
              </div>
              <div className="grid grid-cols-4 gap-2 max-w-lg mx-auto">
                {CHANNELS.map((ch) => {
                  const Icon = ch.icon;
                  return (
                    <button
                      key={ch.id}
                      onClick={() => setChannel(ch.id)}
                      className={cn(
                        'flex flex-col items-center gap-1.5 p-3 rounded-xl border-2 transition-all',
                        channel === ch.id
                          ? 'bg-zinc-900 border-zinc-900 text-white dark:bg-white dark:text-zinc-900'
                          : 'border-zinc-200 hover:border-zinc-400 dark:border-zinc-800 text-zinc-600 dark:text-zinc-400'
                      )}
                    >
                      <Icon className="w-5 h-5" />
                      <span className="text-[11px] font-medium font-sans">
                        {ch.label}
                      </span>
                    </button>
                  );
                })}
              </div>

              {/* Other channel text input */}
              {channel === 'other' && (
                <div className="max-w-sm mx-auto">
                  <Input
                    placeholder="Enter channel name (e.g., WhatsApp, Slack, Discord)"
                    value={otherChannelText}
                    onChange={(e) => setOtherChannelText(e.target.value)}
                    className="text-center"
                  />
                </div>
              )}
            </div>
          )}

          {step === 'building' && goals && channel && risk && (
            <ExperimentBuilder
              goal={goals.primary}
              channel={channel}
              risk={risk}
              onComplete={handleManualComplete}
            />
          )}

          {step === 'generating' && (
            <div className="text-center space-y-4">
              <div className="w-14 h-14 mx-auto rounded-xl bg-zinc-900 dark:bg-white flex items-center justify-center">
                <Sparkles className="w-7 h-7 text-white dark:text-zinc-900 animate-pulse" />
              </div>
              <p className="text-sm text-zinc-500 font-sans">
                Generating experiments...
              </p>
            </div>
          )}

          {step === 'results' && (
            <div className="w-full space-y-4 max-h-[500px] overflow-y-auto">
              <div className="text-center sticky top-0 bg-white dark:bg-zinc-950 pb-2">
                <h2 className="text-xl font-semibold mb-1 font-sans">
                  Your Experiments
                </h2>
                <p className="text-sm text-zinc-500 font-sans">
                  {generatedExperiments.length} ready-to-run experiments for{' '}
                  <span className="font-medium text-zinc-700 dark:text-zinc-300">
                    {goals?.primary}
                  </span>
                </p>
              </div>
              <div className="space-y-4">
                {generatedExperiments.map((e, i) => (
                  <div
                    key={e.id}
                    className="p-4 bg-zinc-50 dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800"
                  >
                    {/* Header */}
                    <div className="flex items-start gap-3 mb-3">
                      <span className="w-7 h-7 rounded-lg bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 flex items-center justify-center text-sm font-bold font-mono flex-shrink-0">
                        {i + 1}
                      </span>
                      <div className="flex-1">
                        <h3 className="text-base font-semibold font-sans">
                          {e.title}
                        </h3>
                        <p className="text-[10px] text-zinc-400 uppercase tracking-wide font-sans">
                          {e.principle.replace('_', ' ')} • {e.duration_days}{' '}
                          days
                        </p>
                      </div>
                    </div>

                    {/* Hypothesis */}
                    <div className="mb-3 p-3 bg-white dark:bg-zinc-950 rounded-lg border border-zinc-100 dark:border-zinc-800">
                      <p className="text-xs text-zinc-400 uppercase tracking-wide mb-1 font-sans">
                        Hypothesis
                      </p>
                      <p className="text-sm font-sans text-zinc-700 dark:text-zinc-300">
                        {e.hypothesis}
                      </p>
                    </div>

                    {/* Control vs Variant */}
                    <div className="grid grid-cols-2 gap-2 mb-3">
                      <div className="p-2 bg-white dark:bg-zinc-950 rounded-lg border border-zinc-100 dark:border-zinc-800">
                        <p className="text-[10px] text-red-500 uppercase tracking-wide mb-1 font-sans">
                          Control (A)
                        </p>
                        <p className="text-xs font-sans text-zinc-600 dark:text-zinc-400">
                          {e.control}
                        </p>
                      </div>
                      <div className="p-2 bg-white dark:bg-zinc-950 rounded-lg border border-zinc-100 dark:border-zinc-800">
                        <p className="text-[10px] text-green-500 uppercase tracking-wide mb-1 font-sans">
                          Variant (B)
                        </p>
                        <p className="text-xs font-sans text-zinc-600 dark:text-zinc-400">
                          {e.variant}
                        </p>
                      </div>
                    </div>

                    {/* Metrics row */}
                    <div className="flex gap-2 mb-3">
                      <div className="flex-1 p-2 bg-white dark:bg-zinc-950 rounded-lg border border-zinc-100 dark:border-zinc-800 text-center">
                        <p className="text-[10px] text-zinc-400 uppercase tracking-wide font-sans">
                          Metric
                        </p>
                        <p className="text-xs font-medium font-sans">
                          {e.success_metric}
                        </p>
                      </div>
                      <div className="flex-1 p-2 bg-white dark:bg-zinc-950 rounded-lg border border-zinc-100 dark:border-zinc-800 text-center">
                        <p className="text-[10px] text-zinc-400 uppercase tracking-wide font-sans">
                          Sample
                        </p>
                        <p className="text-xs font-medium font-sans">
                          {e.sample_size}
                        </p>
                      </div>
                    </div>

                    {/* Action Steps */}
                    <details className="group">
                      <summary className="text-xs text-zinc-500 cursor-pointer hover:text-zinc-700 dark:hover:text-zinc-300 font-sans flex items-center gap-1">
                        <span className="group-open:rotate-90 transition-transform">
                          ▶
                        </span>
                        {e.action_steps.length} Action Steps
                      </summary>
                      <ol className="mt-2 space-y-1 pl-4 text-xs text-zinc-600 dark:text-zinc-400 font-sans list-decimal list-inside">
                        {e.action_steps.map((step, si) => (
                          <li key={si} className="leading-relaxed">
                            {step}
                          </li>
                        ))}
                      </ol>
                    </details>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        {step !== 'building' && (
          <div className="flex items-center justify-between px-6 py-4 border-t border-zinc-100 dark:border-zinc-900 bg-zinc-50/50 dark:bg-zinc-900/50">
            <Button
              variant="ghost"
              onClick={handleBack}
              disabled={step === 'goal' || step === 'generating'}
              className={cn(
                'rounded-lg font-sans',
                step === 'goal' && 'invisible'
              )}
            >
              <ArrowLeft className="w-4 h-4 mr-1" /> Back
            </Button>

            {step !== 'results' && step !== 'generating' && (
              <Button
                onClick={handleNext}
                disabled={!canProceed}
                className="rounded-lg bg-zinc-900 text-white hover:bg-zinc-800 dark:bg-white dark:text-zinc-900 px-5 font-sans"
              >
                {step === 'channel' ? 'Next' : 'Next'}{' '}
                <ArrowRight className="w-4 h-4 ml-1" />
              </Button>
            )}

            {step === 'results' && (
              <Button
                onClick={handleComplete}
                className="rounded-lg bg-zinc-900 text-white hover:bg-zinc-800 dark:bg-white dark:text-zinc-900 px-5 font-sans"
              >
                <Sparkles className="w-4 h-4 mr-1.5" /> Start Experiments
              </Button>
            )}
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
