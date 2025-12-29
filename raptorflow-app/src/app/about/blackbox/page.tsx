'use client';

import Link from 'next/link';
import { MarketingLayout } from '@/components/marketing/MarketingLayout';
import { Button } from '@/components/ui/button';
import {
  ArrowRight,
  FlaskConical,
  TrendingUp,
  Brain,
  Target,
  RotateCcw,
  CheckCircle2,
} from 'lucide-react';

/**
 * Blackbox Product Page — Editorial Style
 * Scientific Laboratory / Monochrome / Learning Narrative
 */
export default function BlackboxProductPage() {
  return (
    <MarketingLayout>
      {/* Hero — The Laboratory */}
      <section className="relative min-h-[80vh] flex items-center justify-center overflow-hidden">
        {/* Scientific Pattern */}
        <div className="absolute inset-0 -z-10">
          {/* Petri dish circles */}
          <div className="absolute top-1/4 right-1/4 w-[200px] h-[200px] rounded-full border border-foreground/5" />
          <div className="absolute bottom-1/3 left-1/3 w-[150px] h-[150px] rounded-full border border-foreground/5" />
          <div className="absolute top-1/2 left-1/4 w-[100px] h-[100px] rounded-full border border-foreground/5" />
          {/* Flowing experiment lines */}
          <svg
            className="absolute inset-0 w-full h-full opacity-[0.04]"
            viewBox="0 0 1000 1000"
            preserveAspectRatio="none"
          >
            <path
              d="M100,500 C300,300 400,700 600,500 S800,300 900,500"
              stroke="currentColor"
              strokeWidth="2"
              fill="none"
            />
            <path
              d="M100,600 C300,400 400,800 600,600 S800,400 900,600"
              stroke="currentColor"
              strokeWidth="1"
              fill="none"
            />
            {/* Data points */}
            <circle cx="300" cy="400" r="4" fill="currentColor" />
            <circle cx="500" cy="550" r="4" fill="currentColor" />
            <circle cx="700" cy="450" r="4" fill="currentColor" />
          </svg>
        </div>

        <div className="mx-auto max-w-7xl px-6 lg:px-8 py-24 lg:py-32">
          <div className="max-w-4xl">
            <p className="text-[10px] font-semibold uppercase tracking-[0.3em] text-muted-foreground mb-12">
              The Intelligence Engine
            </p>

            <h1 className="font-display text-6xl md:text-7xl lg:text-8xl font-normal tracking-tight text-foreground leading-[0.9] mb-8">
              Prove what
              <br />
              <span className="italic text-muted-foreground">
                actually
              </span>{' '}
              works.
            </h1>

            <p className="text-xl md:text-2xl text-muted-foreground leading-relaxed max-w-2xl font-light mb-16">
              Blackbox is your experimentation engine. Track outcomes, extract
              learnings, and harden your strategy through evidence—not opinions.
            </p>

            <Button
              asChild
              size="lg"
              className="h-14 px-10 text-base rounded-full group"
            >
              <Link href="/blackbox">
                Enter Blackbox
                <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Pull Quote */}
      <section className="border-y border-foreground/10 bg-foreground text-background">
        <div className="mx-auto max-w-7xl px-6 lg:px-8 py-20 lg:py-28">
          <blockquote className="max-w-4xl">
            <p className="font-display text-3xl md:text-4xl lg:text-5xl font-normal leading-tight">
              &ldquo;Marketing without measurement is just
              <em className="not-italic border-b-2 border-background/50">
                {' '}
                expensive guessing
              </em>
              .&rdquo;
            </p>
          </blockquote>
        </div>
      </section>

      {/* The Problem */}
      <section className="py-24 lg:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="grid lg:grid-cols-12 gap-16 items-start">
            <div className="lg:col-span-4">
              <p className="text-[10px] font-semibold uppercase tracking-[0.3em] text-muted-foreground mb-4">
                The Gamble
              </p>
              <h2 className="font-display text-4xl md:text-5xl font-normal tracking-tight">
                Hope is not
                <br />a strategy.
              </h2>
            </div>
            <div className="lg:col-span-7 lg:col-start-6">
              <div className="prose prose-lg text-muted-foreground space-y-6">
                <p className="text-xl leading-relaxed">
                  You launched that campaign. You shipped those posts. You
                  changed the landing page headline. But did any of it
                  <em>actually</em> work?
                </p>
                <p className="text-lg leading-relaxed">
                  Marketing by gut feel. A/B testing that never happens because
                  &ldquo;we don&apos;t have time.&rdquo; Decisions based on the
                  loudest voice in the room instead of the clearest data. Every
                  quarter starts from scratch because nothing compounds.
                </p>
                <p className="text-xl leading-relaxed font-medium text-foreground">
                  You need a system that learns—and remembers.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* The Learning Loop */}
      <section className="border-y border-foreground/10 py-24 lg:py-32 bg-muted/20">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="max-w-xl mb-20">
            <p className="text-[10px] font-semibold uppercase tracking-[0.3em] text-muted-foreground mb-4">
              The Loop
            </p>
            <h2 className="font-display text-4xl md:text-5xl font-normal tracking-tight">
              Every experiment
              <br />
              feeds the next.
            </h2>
          </div>

          {/* Circular Flow Visualization */}
          <div className="relative max-w-4xl mx-auto">
            {/* Central insight */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-10 hidden lg:block">
              <div className="h-32 w-32 rounded-full bg-foreground flex items-center justify-center">
                <Brain className="h-10 w-10 text-background" />
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-8 lg:gap-16">
              {/* Hypothesis */}
              <div className="p-8 rounded-2xl border border-foreground/10 bg-background">
                <div className="flex items-center gap-4 mb-6">
                  <span className="font-mono text-4xl font-light text-foreground/20">
                    01
                  </span>
                  <Target className="h-6 w-6 text-foreground" />
                </div>
                <h3 className="font-display text-2xl mb-4">Hypothesize</h3>
                <p className="text-muted-foreground leading-relaxed">
                  Define what you want to test. &ldquo;CTA variant A will
                  outperform B&rdquo; — &ldquo;Video posts drive more engagement
                  than static&rdquo; — &ldquo;Pain-focused messaging converts
                  better than aspiration.&rdquo;
                </p>
              </div>

              {/* Execute */}
              <div className="p-8 rounded-2xl border border-foreground/10 bg-background">
                <div className="flex items-center gap-4 mb-6">
                  <span className="font-mono text-4xl font-light text-foreground/20">
                    02
                  </span>
                  <FlaskConical className="h-6 w-6 text-foreground" />
                </div>
                <h3 className="font-display text-2xl mb-4">Execute</h3>
                <p className="text-muted-foreground leading-relaxed">
                  Run the experiment in the real world. Blackbox tracks
                  everything automatically—or you check in manually. Either way,
                  the data gets captured.
                </p>
              </div>

              {/* Learn */}
              <div className="p-8 rounded-2xl border border-foreground/10 bg-background">
                <div className="flex items-center gap-4 mb-6">
                  <span className="font-mono text-4xl font-light text-foreground/20">
                    03
                  </span>
                  <TrendingUp className="h-6 w-6 text-foreground" />
                </div>
                <h3 className="font-display text-2xl mb-4">Learn</h3>
                <p className="text-muted-foreground leading-relaxed">
                  AI synthesizes what worked and why. Not just &ldquo;A beat
                  B&rdquo;—but the strategic insight behind it. Learnings you
                  can actually apply.
                </p>
              </div>

              {/* Apply */}
              <div className="p-8 rounded-2xl border border-foreground/10 bg-background">
                <div className="flex items-center gap-4 mb-6">
                  <span className="font-mono text-4xl font-light text-foreground/20">
                    04
                  </span>
                  <RotateCcw className="h-6 w-6 text-foreground" />
                </div>
                <h3 className="font-display text-2xl mb-4">Apply</h3>
                <p className="text-muted-foreground leading-relaxed">
                  Strategic pivots feed back into your Foundation, your
                  campaigns, your Muse generations. The system gets smarter.
                  Your marketing compounds.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Evidence Section */}
      <section className="py-24 lg:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div>
              <p className="text-[10px] font-semibold uppercase tracking-[0.3em] text-muted-foreground mb-4">
                Evidence
              </p>
              <h2 className="font-display text-4xl md:text-5xl font-normal tracking-tight mb-8">
                Decisions backed
                <br />
                by proof.
              </h2>
              <p className="text-lg text-muted-foreground leading-relaxed mb-8">
                Every learning in Blackbox is traceable. See the raw data, the
                experiment that generated it, the outcome that proved it. No
                black boxes in your Blackbox.
              </p>
              <ul className="space-y-4">
                {[
                  'Full experiment history',
                  'Statistical confidence scoring',
                  'Outcome attribution tracking',
                  'Strategic recommendation engine',
                ].map((item) => (
                  <li key={item} className="flex items-center gap-3">
                    <CheckCircle2 className="h-5 w-5 text-foreground flex-shrink-0" />
                    <span className="text-muted-foreground">{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Evidence Card */}
            <div className="space-y-4">
              <div className="p-6 rounded-2xl border border-foreground/10 bg-muted/30">
                <div className="flex items-center gap-2 mb-4">
                  <div className="h-2 w-2 rounded-full bg-green-500" />
                  <span className="text-xs font-mono uppercase text-muted-foreground">
                    Strategic Learning
                  </span>
                </div>
                <p className="font-display text-lg mb-4">
                  &ldquo;Pain-focused headlines outperform aspiration-focused by
                  34% for early-stage founder cohort.&rdquo;
                </p>
                <div className="text-xs text-muted-foreground space-y-1">
                  <div>Source: A/B Test #147 • Landing Page Headlines</div>
                  <div>Confidence: 94% • Sample: 2,847 sessions</div>
                </div>
              </div>
              <div className="p-6 rounded-2xl border border-foreground/10 bg-muted/30">
                <div className="flex items-center gap-2 mb-4">
                  <div className="h-2 w-2 rounded-full bg-amber-500" />
                  <span className="text-xs font-mono uppercase text-muted-foreground">
                    Tactical Insight
                  </span>
                </div>
                <p className="font-display text-lg mb-4">
                  &ldquo;Video content drives 2.3x engagement on LinkedIn, but
                  static carousels convert 1.5x better.&rdquo;
                </p>
                <div className="text-xs text-muted-foreground space-y-1">
                  <div>Source: Q4 Content Performance Review</div>
                  <div>Confidence: 87% • Sample: 48 posts</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Flywheel Visualization */}
      <section className="border-y border-foreground/10 bg-foreground text-background py-24">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="max-w-3xl mx-auto text-center">
            <p className="text-[10px] font-semibold uppercase tracking-[0.3em] text-background/60 mb-4">
              The Flywheel
            </p>
            <h2 className="font-display text-4xl md:text-5xl font-normal tracking-tight mb-12">
              Marketing that
              <br />
              gets smarter every week.
            </h2>
            <div className="grid grid-cols-3 gap-8">
              <div>
                <div className="font-mono text-5xl font-light mb-2">↻</div>
                <div className="text-sm text-background/60">
                  Experiments run
                </div>
              </div>
              <div>
                <div className="font-mono text-5xl font-light mb-2">→</div>
                <div className="text-sm text-background/60">
                  Learnings extracted
                </div>
              </div>
              <div>
                <div className="font-mono text-5xl font-light mb-2">↑</div>
                <div className="text-sm text-background/60">
                  Strategy hardens
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Second Pull Quote */}
      <section className="py-24 lg:py-28">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <blockquote className="max-w-3xl mx-auto text-center">
            <p className="font-display text-2xl md:text-3xl lg:text-4xl font-normal leading-tight text-muted-foreground">
              Stop asking{' '}
              <span className="text-foreground">
                &ldquo;did that work?&rdquo;
              </span>
              <br />
              Start <em className="not-italic">knowing</em>.
            </p>
          </blockquote>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-24 lg:py-32 border-t border-foreground/10">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="max-w-2xl mx-auto text-center">
            <h2 className="font-display text-4xl md:text-5xl lg:text-6xl font-normal tracking-tight mb-8">
              Start proving
              <br />
              what works.
            </h2>
            <p className="text-lg text-muted-foreground mb-12">
              Evidence-backed marketing decisions. Strategic learnings that
              compound.
            </p>
            <Button
              asChild
              size="lg"
              className="h-14 px-10 text-base rounded-full group"
            >
              <Link href="/blackbox">
                Enter Blackbox
                <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </Link>
            </Button>
          </div>
        </div>
      </section>
    </MarketingLayout>
  );
}
