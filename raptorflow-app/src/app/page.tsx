'use client';

import Link from 'next/link';
import { MarketingLayout } from '@/components/marketing/MarketingLayout';
import { Button } from '@/components/ui/button';
import { ChaosDiagnostic } from '@/components/marketing/ChaosDiagnostic';
import { PositioningPlayground } from '@/components/marketing/PositioningPlayground';
import { SystemFlowDiagram } from '@/components/marketing/SystemFlowDiagram';
import { ChaosToClarity } from '@/components/marketing/ChaosToClarity';
import { BeforeAfterGenerator } from '@/components/marketing/BeforeAfterGenerator';
import { ModulesSpectacle } from '@/components/marketing/ModulesSpectacle';

// Stats
const stats = [
  { value: '10', unit: 'min', label: 'to build your 90-day plan' },
  { value: '1', unit: 'system', label: 'instead of 5+ tools' },
  { value: '7', unit: 'moves', label: 'shipped every week' },
];

export default function LandingPage() {
  return (
    <MarketingLayout>
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="mx-auto max-w-7xl px-6 lg:px-8 py-24 lg:py-32">
          <div className="mx-auto max-w-3xl text-center">
            {/* Eyebrow */}
            <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-6">
              The Founder Marketing Operating System
            </p>

            {/* Main Headline */}
            <h1 className="font-display text-5xl lg:text-7xl font-medium tracking-tight text-foreground mb-6">
              Marketing.
              <br />
              <span className="text-muted-foreground">Finally under control.</span>
            </h1>

            {/* Subheadline */}
            <p className="text-lg lg:text-xl text-muted-foreground leading-relaxed mb-10 max-w-2xl mx-auto">
              Turn messy business context into clear positioning and a 90-day marketing war plan—then ship weekly Moves that drive revenue.
            </p>

            {/* CTAs */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Button asChild size="lg" className="h-14 px-8 text-base rounded-xl">
                <Link href="/login">Get Started Free</Link>
              </Button>
              <Button asChild variant="outline" size="lg" className="h-14 px-8 text-base rounded-xl">
                <Link href="#try-it">Try It Now — No Signup</Link>
              </Button>
            </div>

            {/* Trust line */}
            <p className="mt-8 text-sm text-muted-foreground">
              No credit card required. Start in 2 minutes.
            </p>
          </div>
        </div>

        {/* Gradient background */}
        <div className="absolute inset-0 -z-10 overflow-hidden">
          <div className="absolute left-1/2 top-0 -translate-x-1/2 -translate-y-1/2 h-[600px] w-[600px] rounded-full bg-gradient-to-br from-foreground/5 to-transparent blur-3xl" />
        </div>
      </section>

      {/* Pain Point Quote */}
      <section className="border-y border-border bg-muted/30">
        <div className="mx-auto max-w-7xl px-6 lg:px-8 py-16">
          <blockquote className="mx-auto max-w-3xl text-center">
            <p className="text-2xl lg:text-3xl font-display font-medium text-foreground leading-relaxed">
              &quot;If your marketing is confusing, you are losing—silently.&quot;
            </p>
          </blockquote>
        </div>
      </section>

      {/* 🚀 MOONSHOT: Chaos to Clarity Animation */}
      <section className="py-24 lg:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center mb-12">
            <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-4">
              The Transformation
            </p>
            <h2 className="font-display text-4xl lg:text-5xl font-medium tracking-tight">
              Watch the chaos organize
            </h2>
            <p className="mt-4 text-lg text-muted-foreground">
              Click to see what happens when you stop guessing and start systematizing.
            </p>
          </div>
          <ChaosToClarity />
        </div>
      </section>

      {/* 🚀 MOONSHOT: AI Demo Widget */}
      <section id="try-it" className="py-24 lg:py-32 border-y border-border bg-muted/30">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center mb-12">
            <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-4">
              Try It Now
            </p>
            <h2 className="font-display text-4xl lg:text-5xl font-medium tracking-tight">
              Positioning Playground
            </h2>
            <p className="mt-4 text-lg text-muted-foreground">
              Describe your business. Get your positioning, ICP, and first Moves instantly.
            </p>
          </div>
          <PositioningPlayground />
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="grid grid-cols-3 gap-8">
            {stats.map((stat) => (
              <div key={stat.label} className="text-center">
                <div className="flex items-baseline justify-center gap-1">
                  <span className="font-mono text-4xl lg:text-5xl font-semibold tracking-tight">{stat.value}</span>
                  <span className="text-lg text-muted-foreground">{stat.unit}</span>
                </div>
                <p className="mt-2 text-sm text-muted-foreground">{stat.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 🚀 MOONSHOT: System Flow Diagram */}
      <section className="py-24 lg:py-32 border-y border-border">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center mb-12">
            <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-4">
              The System
            </p>
            <h2 className="font-display text-4xl lg:text-5xl font-medium tracking-tight">
              Everything connects
            </h2>
            <p className="mt-4 text-lg text-muted-foreground">
              Not 8 separate tools. One unified system where every piece feeds the next.
            </p>
          </div>
          <SystemFlowDiagram />
        </div>
      </section>

      {/* How It Works */}
      <section className="py-24 lg:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center mb-16">
            <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-4">
              The Process
            </p>
            <h2 className="font-display text-4xl lg:text-5xl font-medium tracking-tight">
              Clarify. Build. Run.
            </h2>
            <p className="mt-4 text-lg text-muted-foreground">
              Three steps to marketing that compounds instead of resetting every Monday.
            </p>
          </div>

          <div className="grid lg:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {[
              {
                step: '01',
                title: 'Clarify',
                description: 'Intake → ICP → positioning → proof. We turn your messy context into crystal-clear strategy.',
              },
              {
                step: '02',
                title: 'Build',
                description: '90-day war plan → weekly Moves → assets. Every piece connects to your positioning.',
              },
              {
                step: '03',
                title: 'Run',
                description: 'Publish → track → tweak. Results compound because every week builds on the last.',
              },
            ].map((item) => (
              <div key={item.step} className="relative">
                <div className="text-6xl font-mono font-bold text-muted/30 mb-4">{item.step}</div>
                <h3 className="text-xl font-semibold mb-2">{item.title}</h3>
                <p className="text-muted-foreground leading-relaxed">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 🚀 MOONSHOT: Chaos Diagnostic Quiz */}
      <section className="py-24 lg:py-32 border-y border-border bg-muted/30">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center mb-12">
            <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-4">
              Self-Assessment
            </p>
            <h2 className="font-display text-4xl lg:text-5xl font-medium tracking-tight">
              What is your Marketing Chaos Score?
            </h2>
            <p className="mt-4 text-lg text-muted-foreground">
              6 questions. 60 seconds. Get your personalized diagnosis.
            </p>
          </div>
          <ChaosDiagnostic />
        </div>
      </section>

      {/* 🎯 SPECTACLE: Interactive Modules Showcase */}
      <ModulesSpectacle />

      {/* 🚀 MOONSHOT: Before/After Transformation Generator */}
      <section className="py-24 lg:py-32 border-y border-border bg-muted/30">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <BeforeAfterGenerator />
        </div>
      </section>

      {/* Testimonial / Quote */}
      <section className="py-24 lg:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-3xl text-center">
            <blockquote>
              <p className="font-display text-3xl lg:text-4xl font-medium leading-relaxed text-foreground">
                &quot;You should not have to guess your marketing.
                <br />
                <span className="text-muted-foreground">With RaptorFlow, you will not.&quot;</span>
              </p>
            </blockquote>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="border-t border-border bg-foreground text-background">
        <div className="mx-auto max-w-7xl px-6 lg:px-8 py-24">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="font-display text-4xl lg:text-5xl font-medium tracking-tight mb-6">
              Stop trying marketing.
              <br />
              Start running a machine.
            </h2>
            <p className="text-lg text-background/70 mb-10">
              Give us your messy context. We will turn it into a plan you can actually execute.
            </p>
            <Button asChild size="lg" variant="secondary" className="h-14 px-8 text-base rounded-xl">
              <Link href="/login">Get Started Free</Link>
            </Button>
          </div>
        </div>
      </section>
    </MarketingLayout>
  );
}
