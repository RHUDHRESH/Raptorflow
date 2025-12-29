'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';

interface Industry {
  id: string;
  label: string;
  before: BeforeState;
  after: AfterState;
}

interface BeforeState {
  time: string;
  tools: string;
  content: string;
  leads: string;
  feeling: string;
}

interface AfterState {
  time: string;
  tools: string;
  content: string;
  leads: string;
  feeling: string;
}

const industries: Industry[] = [
  {
    id: 'saas',
    label: 'SaaS / Tech',
    before: {
      time: '8-12 hours/week on marketing',
      tools: '5-7 disconnected tools',
      content: 'Random posts when inspired',
      leads: 'Unpredictable pipeline',
      feeling: 'Overwhelmed and guessing',
    },
    after: {
      time: '2-3 hours/week (automated)',
      tools: '1 unified system',
      content: '7 strategic Moves per week',
      leads: 'Predictable pipeline growth',
      feeling: 'Confident and systematic',
    },
  },
  {
    id: 'agency',
    label: 'Agency / Consulting',
    before: {
      time: '0 hours (too busy with clients)',
      tools: 'Client tools, not your own',
      content: 'None for yourself',
      leads: 'Feast or famine cycles',
      feeling: 'Hypocritical cobbler',
    },
    after: {
      time: '2 hours/week (your own marketing)',
      tools: 'Your own RaptorFlow instance',
      content: 'Consistent thought leadership',
      leads: 'Steady inbound inquiries',
      feeling: 'Practicing what you preach',
    },
  },
  {
    id: 'ecommerce',
    label: 'E-commerce / DTC',
    before: {
      time: '10+ hours on paid ads',
      tools: 'Meta Ads, Google, email chaos',
      content: 'Product posts only',
      leads: 'High CAC, low LTV',
      feeling: 'Racing to the bottom',
    },
    after: {
      time: '4 hours on organic + paid',
      tools: 'Unified brand + campaign system',
      content: 'Story-driven content engine',
      leads: 'Lower CAC, community-driven',
      feeling: 'Building a brand, not just selling',
    },
  },
  {
    id: 'b2b',
    label: 'B2B / Enterprise',
    before: {
      time: '5+ hours on sales enablement',
      tools: 'CRM, LinkedIn, random PDFs',
      content: 'Outdated case studies',
      leads: 'Long cycles, no nurture',
      feeling: 'Sales team has no cover',
    },
    after: {
      time: '3 hours on strategic content',
      tools: 'Foundation feeds everything',
      content: 'Buyer education journeys',
      leads: 'Warmer leads, shorter cycles',
      feeling: 'Marketing and sales aligned',
    },
  },
];

const metrics = [
  { label: 'Time spent', key: 'time' as const },
  { label: 'Tools used', key: 'tools' as const },
  { label: 'Content output', key: 'content' as const },
  { label: 'Pipeline', key: 'leads' as const },
  { label: 'How it feels', key: 'feeling' as const },
];

export function BeforeAfterGenerator() {
  const [selectedIndustry, setSelectedIndustry] = useState<string | null>(null);
  const [showResult, setShowResult] = useState(false);

  const handleSelect = (industryId: string) => {
    setSelectedIndustry(industryId);
    setShowResult(true);
  };

  const handleReset = () => {
    setSelectedIndustry(null);
    setShowResult(false);
  };

  const industry = industries.find((i) => i.id === selectedIndustry);

  if (showResult && industry) {
    return (
      <div className="w-full max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <div className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-2">
            Your Transformation Preview
          </div>
          <h3 className="font-display text-2xl lg:text-3xl font-medium">
            {industry.label} → RaptorFlow
          </h3>
        </div>

        {/* Comparison Table */}
        <div className="rounded-2xl border border-border overflow-hidden">
          <div className="grid grid-cols-3 bg-muted/50">
            <div className="p-4 text-sm font-medium text-muted-foreground">
              Metric
            </div>
            <div className="p-4 text-sm font-medium text-center text-destructive/80">
              Before
            </div>
            <div className="p-4 text-sm font-medium text-center text-green-600">
              After 90 Days
            </div>
          </div>

          {metrics.map((metric, index) => (
            <div
              key={metric.key}
              className={`grid grid-cols-3 ${index % 2 === 0 ? 'bg-card' : 'bg-muted/30'}`}
            >
              <div className="p-4 text-sm font-medium">{metric.label}</div>
              <div className="p-4 text-sm text-center text-muted-foreground">
                {industry.before[metric.key]}
              </div>
              <div className="p-4 text-sm text-center font-medium">
                {industry.after[metric.key]}
              </div>
            </div>
          ))}
        </div>

        {/* Visual Timeline */}
        <div className="mt-8 relative">
          <div className="absolute left-1/2 top-0 bottom-0 w-0.5 bg-border -translate-x-1/2" />

          <div className="relative flex items-center justify-between">
            {/* Day 0 */}
            <div className="w-1/3 pr-8 text-right">
              <div className="text-sm font-semibold">Day 0</div>
              <div className="text-xs text-muted-foreground">
                Start your Foundation
              </div>
            </div>
            <div className="absolute left-1/2 -translate-x-1/2 h-4 w-4 rounded-full bg-foreground" />
            <div className="w-1/3 pl-8">
              <div className="text-sm text-muted-foreground">10 min setup</div>
            </div>
          </div>

          <div className="h-16" />

          <div className="relative flex items-center justify-between">
            <div className="w-1/3 pr-8 text-right">
              <div className="text-sm font-semibold">Week 1</div>
              <div className="text-xs text-muted-foreground">
                First Moves shipped
              </div>
            </div>
            <div className="absolute left-1/2 -translate-x-1/2 h-4 w-4 rounded-full bg-foreground/70" />
            <div className="w-1/3 pl-8">
              <div className="text-sm text-muted-foreground">7 pieces live</div>
            </div>
          </div>

          <div className="h-16" />

          <div className="relative flex items-center justify-between">
            <div className="w-1/3 pr-8 text-right">
              <div className="text-sm font-semibold">Day 90</div>
              <div className="text-xs text-muted-foreground">
                Campaign complete
              </div>
            </div>
            <div className="absolute left-1/2 -translate-x-1/2 h-4 w-4 rounded-full bg-green-600" />
            <div className="w-1/3 pl-8">
              <div className="text-sm font-medium text-green-600">
                90+ pieces, system running
              </div>
            </div>
          </div>
        </div>

        {/* CTAs */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center mt-10">
          <Button size="lg" className="h-14 px-8 text-base rounded-xl">
            Start My Transformation — Free
          </Button>
          <Button
            variant="outline"
            size="lg"
            className="h-14 px-8 text-base rounded-xl"
            onClick={handleReset}
          >
            Try Another Industry
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div className="text-center mb-8">
        <div className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-2">
          Preview Your Future
        </div>
        <h3 className="font-display text-2xl lg:text-3xl font-medium mb-2">
          What would your 90 days look like?
        </h3>
        <p className="text-muted-foreground">
          Select your industry to see your personalized transformation
        </p>
      </div>

      <div className="grid sm:grid-cols-2 gap-4">
        {industries.map((industry) => (
          <button
            key={industry.id}
            onClick={() => handleSelect(industry.id)}
            className="p-6 rounded-xl border border-border bg-card text-left hover:border-foreground/50 hover:bg-muted/50 transition-all duration-200 group"
          >
            <div className="font-semibold text-lg group-hover:translate-x-1 transition-transform">
              {industry.label}
            </div>
            <div className="text-sm text-muted-foreground mt-1">
              See your before → after
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
