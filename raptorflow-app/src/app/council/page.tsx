'use client';

import React, { useState } from 'react';
import { BrainCircuit, Sparkles, Target } from 'lucide-react';
import { AppLayout } from '@/components/layout/AppLayout';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { toast } from 'sonner';
import {
  generateCouncilPlan,
  persistCouncilCampaign,
  persistCouncilMoves,
} from '@/lib/api';
import { CouncilMoveSuggestion } from '@/lib/campaigns-types';

export default function CouncilPage() {
  const [mode, setMode] = useState<'move' | 'campaign'>('move');
  const [objective, setObjective] = useState('');
  const [context, setContext] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [plan, setPlan] = useState<any>(null);
  const [moves, setMoves] = useState<CouncilMoveSuggestion[]>([]);

  const handleGenerate = async () => {
    if (!objective.trim() || !context.trim()) {
      toast.error('Provide an objective and context.');
      return;
    }

    setIsLoading(true);
    try {
      const result = await generateCouncilPlan({
        type: mode,
        objective,
        context,
      });
      setPlan(result);
      setMoves(result.view.moves || result.view.campaignMoves || []);
    } catch (error) {
      toast.error('Council generation failed.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleApprove = async () => {
    if (!plan) return;
    try {
      if (mode === 'move') {
        await persistCouncilMoves(plan.raw, moves);
        toast.success('Moves created in Mission Control.');
      } else {
        await persistCouncilCampaign(plan.raw, moves);
        toast.success('Campaign created in Mission Control.');
      }
    } catch (error) {
      toast.error('Unable to save Council output.');
    }
  };

  return (
    <AppLayout>
      <div className="max-w-5xl mx-auto px-6 py-10 space-y-10">
        <header className="space-y-3">
          <p className="text-xs uppercase tracking-[0.3em] text-muted-foreground">
            Expert Council
          </p>
          <h1 className="text-4xl font-display text-foreground">
            Direct the Council.
          </h1>
          <p className="text-muted-foreground">
            Give the Council a clear objective and constraints. It returns a
            focused execution plan you can ship directly into Mission Control.
          </p>
        </header>

        <section className="rounded-3xl border border-border bg-card p-8 space-y-6">
          <div className="flex items-center gap-3">
            <Button
              variant={mode === 'move' ? 'default' : 'secondary'}
              onClick={() => setMode('move')}
              className="h-10"
            >
              Single Move
            </Button>
            <Button
              variant={mode === 'campaign' ? 'default' : 'secondary'}
              onClick={() => setMode('campaign')}
              className="h-10"
            >
              Full Campaign
            </Button>
          </div>

          <div className="space-y-3">
            <label className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">
              Objective
            </label>
            <Input
              value={objective}
              onChange={(e) => setObjective(e.target.value)}
              placeholder="e.g. Book 10 founder calls in 14 days"
              className="h-12"
            />
          </div>

          <div className="space-y-3">
            <label className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">
              Context & Constraints
            </label>
            <Textarea
              value={context}
              onChange={(e) => setContext(e.target.value)}
              placeholder="Audience, channels, constraints, offers..."
              className="min-h-[160px]"
            />
          </div>

          <div className="flex items-center justify-between">
            <p className="text-xs text-muted-foreground">
              The Council uses your Foundation metadata automatically.
            </p>
            <Button onClick={handleGenerate} disabled={isLoading}>
              {isLoading ? 'Generating...' : 'Generate Plan'}
            </Button>
          </div>
        </section>

        {plan?.view && (
          <section className="rounded-3xl border border-border bg-card p-8 space-y-6">
            <div className="flex items-center gap-3">
              <BrainCircuit className="h-5 w-5 text-primary" />
              <h2 className="text-xl font-semibold">Council Output</h2>
            </div>
            <div className="rounded-2xl border border-border bg-muted/30 p-6">
              <p className="text-lg font-medium">
                {plan.view.strategicDecree}
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              {moves.map((move) => (
                <div
                  key={move.id}
                  className="rounded-2xl border border-border p-4 bg-background"
                >
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <Target className="h-3 w-3" />
                    {move.type}
                  </div>
                  <h3 className="text-base font-semibold mt-2">{move.title}</h3>
                  <p className="text-sm text-muted-foreground mt-2">
                    {move.description}
                  </p>
                </div>
              ))}
            </div>

            <div className="flex justify-end">
              <Button onClick={handleApprove} className="gap-2">
                <Sparkles className="h-4 w-4" />
                Approve & Ship to Mission Control
              </Button>
            </div>
          </section>
        )}
      </div>
    </AppLayout>
  );
}
