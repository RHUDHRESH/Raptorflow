'use client';

import React from 'react';
import { Check, ArrowRight, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { GroundworkProvider, useGroundwork } from '@/components/groundwork/GroundworkProvider';
import Link from 'next/link';

function GroundworkCompleteContent() {
  const { state } = useGroundwork();

  // Count completed sections
  const completedSections = Object.values(state.sections).filter((s) => s.completed).length;
  const totalSections = Object.keys(state.sections).length;

  // Mock strategy data (will come from backend in real implementation)
  const strategySummary = {
    bigIdea: 'Your marketing strategy is ready',
    keyMessages: [
      'Focus on your primary audience segments',
      'Leverage your brand energy and voice',
      'Execute with clear goals and metrics',
    ],
    suggestedMoves: [
      {
        id: '1',
        name: 'Launch Campaign',
        goal: 'Get 100 leads in 30 days',
        description: 'A focused campaign to drive initial traction',
      },
      {
        id: '2',
        name: 'Brand Awareness Push',
        goal: 'Increase brand visibility',
        description: 'Build recognition in your target market',
      },
    ],
    icpTags: ['B2B SaaS', 'Startup Founders', 'Marketing Teams'],
  };

  return (
    <div className="min-h-screen bg-rf-bg">
      <div className="max-w-4xl mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-rf-success/10 mb-4">
            <Check className="w-8 h-8 text-rf-success" />
          </div>
          <h1 className="text-4xl font-bold text-rf-ink mb-3">Groundwork Complete</h1>
          <p className="text-lg text-rf-subtle">
            Your strategic foundation is set. Let&apos;s build your marketing strategy.
          </p>
        </div>

        <div className="space-y-6 mb-8">
          <Card className="border-rf-cloud bg-rf-bg">
            <CardHeader>
              <CardTitle className="text-rf-ink flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-rf-primary" />
                ADAPT Strategy Summary
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h3 className="text-sm font-medium text-rf-subtle uppercase tracking-wide mb-2">
                  Big Idea
                </h3>
                <p className="text-rf-ink">{strategySummary.bigIdea}</p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-rf-subtle uppercase tracking-wide mb-2">
                  Key Messages
                </h3>
                <ul className="space-y-2">
                  {strategySummary.keyMessages.map((message, index) => (
                    <li key={index} className="flex items-start gap-2 text-rf-ink">
                      <span className="text-rf-primary mt-1">•</span>
                      <span>{message}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </CardContent>
          </Card>

          <Card className="border-rf-cloud bg-rf-bg">
            <CardHeader>
              <CardTitle className="text-rf-ink">Suggested Moves</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {strategySummary.suggestedMoves.map((move) => (
                <div
                  key={move.id}
                  className="p-4 rounded-lg border border-rf-cloud bg-rf-cloud/30"
                >
                  <h4 className="font-semibold text-rf-ink mb-1">{move.name}</h4>
                  <p className="text-sm text-rf-subtle mb-2">{move.goal}</p>
                  <p className="text-sm text-rf-ink">{move.description}</p>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card className="border-rf-cloud bg-rf-bg">
            <CardHeader>
              <CardTitle className="text-rf-ink">ICP Tags Generated</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {strategySummary.icpTags.map((tag, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 rounded-full bg-rf-cloud text-sm text-rf-ink"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="flex items-center justify-center gap-4">
          <Button asChild size="lg" className="bg-rf-primary text-white hover:bg-rf-primary/90">
            <Link href="/dashboard">
              Launch Your First Move
              <ArrowRight className="w-4 h-4 ml-2" />
            </Link>
          </Button>
          <Button asChild variant="outline" size="lg">
            <Link href="/dashboard">Go to Dashboard</Link>
          </Button>
        </div>
      </div>
    </div>
  );
}

export default function GroundworkCompletePage() {
  return (
    <GroundworkProvider>
      <GroundworkCompleteContent />
    </GroundworkProvider>
  );
}

