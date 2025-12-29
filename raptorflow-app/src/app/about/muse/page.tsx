'use client';

import Link from 'next/link';
import { MarketingLayout } from '@/components/marketing/MarketingLayout';
import { Button } from '@/components/ui/button';
import {
  ArrowRight,
  Sparkles,
  Layers,
  Wand2,
  FileText,
  Palette,
} from 'lucide-react';

/**
 * Muse Product Page — Editorial Style
 * "Very New York" / Monochrome / Artistic / Non-boxy
 */
export default function MuseProductPage() {
  return (
    <MarketingLayout>
      {/* Hero — Full Bleed Editorial */}
      <section className="relative min-h-[80vh] flex items-center justify-center overflow-hidden">
        {/* Artistic Background Pattern */}
        <div className="absolute inset-0 -z-10">
          <div className="absolute top-1/4 left-1/4 w-[600px] h-[600px] rounded-full border border-foreground/5" />
          <div className="absolute top-1/3 left-1/3 w-[400px] h-[400px] rounded-full border border-foreground/5" />
          <div className="absolute bottom-1/4 right-1/4 w-[300px] h-[300px] rounded-full border border-foreground/10" />
          {/* Flowing lines */}
          <svg
            className="absolute inset-0 w-full h-full opacity-[0.03]"
            viewBox="0 0 1000 1000"
            preserveAspectRatio="none"
          >
            <path
              d="M0,500 Q250,200 500,500 T1000,500"
              stroke="currentColor"
              strokeWidth="2"
              fill="none"
            />
            <path
              d="M0,600 Q250,300 500,600 T1000,600"
              stroke="currentColor"
              strokeWidth="1"
              fill="none"
            />
          </svg>
        </div>

        <div className="mx-auto max-w-7xl px-6 lg:px-8 py-24 lg:py-32">
          <div className="max-w-4xl">
            {/* Eyebrow */}
            <p className="text-[10px] font-semibold uppercase tracking-[0.3em] text-muted-foreground mb-12">
              The Creative Engine
            </p>

            {/* Main Title — Large Serif */}
            <h1 className="font-display text-6xl md:text-7xl lg:text-8xl font-normal tracking-tight text-foreground leading-[0.9] mb-8">
              Where strategy
              <br />
              <span className="italic text-muted-foreground">becomes</span>{' '}
              creation.
            </h1>

            {/* Subtitle — Editorial Prose */}
            <p className="text-xl md:text-2xl text-muted-foreground leading-relaxed max-w-2xl font-light mb-16">
              Muse doesn&apos;t just generate content. It understands your
              brand, speaks to your people, and creates assets that convert.
            </p>

            <Button
              asChild
              size="lg"
              className="h-14 px-10 text-base rounded-full group"
            >
              <Link href="/muse">
                Enter Muse
                <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Pull Quote — Breaking Section */}
      <section className="border-y border-foreground/10 bg-foreground text-background">
        <div className="mx-auto max-w-7xl px-6 lg:px-8 py-20 lg:py-28">
          <blockquote className="max-w-4xl">
            <p className="font-display text-3xl md:text-4xl lg:text-5xl font-normal leading-tight">
              &ldquo;AI that actually sounds like{' '}
              <em className="not-italic border-b-2 border-background/50">
                you
              </em>
              — because it&apos;s trained on your positioning, your voice, your
              strategy.&rdquo;
            </p>
          </blockquote>
        </div>
      </section>

      {/* The Problem — Editorial Prose */}
      <section className="py-24 lg:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="grid lg:grid-cols-12 gap-16 items-start">
            <div className="lg:col-span-4">
              <p className="text-[10px] font-semibold uppercase tracking-[0.3em] text-muted-foreground mb-4">
                The Void
              </p>
              <h2 className="font-display text-4xl md:text-5xl font-normal tracking-tight">
                Content without
                <br />
                context is noise.
              </h2>
            </div>
            <div className="lg:col-span-7 lg:col-start-6">
              <div className="prose prose-lg text-muted-foreground space-y-6">
                <p className="text-xl leading-relaxed">
                  You&apos;ve tried ChatGPT. Copied prompts from Twitter
                  threads. Paid for AI writing tools that produce content
                  indistinguishable from every other company in your space.
                </p>
                <p className="text-lg leading-relaxed">
                  The output sounds generic because the input is generic. AI
                  doesn&apos;t know your positioning. It doesn&apos;t understand
                  your customer&apos;s midnight fears. It can&apos;t feel the
                  difference between your voice and your competitor&apos;s.
                </p>
                <p className="text-xl leading-relaxed font-medium text-foreground">
                  Until now.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works — Flowing Steps */}
      <section className="border-y border-foreground/10 py-24 lg:py-32 bg-muted/20">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="max-w-xl mb-20">
            <p className="text-[10px] font-semibold uppercase tracking-[0.3em] text-muted-foreground mb-4">
              The Process
            </p>
            <h2 className="font-display text-4xl md:text-5xl font-normal tracking-tight">
              From thought to asset,
              <br />
              in moments.
            </h2>
          </div>

          {/* Flowing Steps — Non-Grid Layout */}
          <div className="space-y-20">
            {/* Step 1 */}
            <div className="flex flex-col md:flex-row gap-8 md:gap-16 items-start">
              <div className="md:w-32 flex-shrink-0">
                <span className="font-display text-7xl text-foreground/10">
                  01
                </span>
              </div>
              <div className="flex-1 max-w-xl">
                <div className="h-12 w-12 rounded-full bg-foreground/5 flex items-center justify-center mb-6">
                  <Wand2 className="h-5 w-5 text-foreground" />
                </div>
                <h3 className="font-display text-2xl mb-4">
                  Describe what you need
                </h3>
                <p className="text-muted-foreground leading-relaxed">
                  &ldquo;LinkedIn post announcing our product launch&rdquo; —
                  &ldquo;Email sequence for cold outreach&rdquo; —
                  &ldquo;Landing page headline variants&rdquo;
                </p>
              </div>
            </div>

            {/* Step 2 */}
            <div className="flex flex-col md:flex-row gap-8 md:gap-16 items-start md:ml-24">
              <div className="md:w-32 flex-shrink-0">
                <span className="font-display text-7xl text-foreground/10">
                  02
                </span>
              </div>
              <div className="flex-1 max-w-xl">
                <div className="h-12 w-12 rounded-full bg-foreground/5 flex items-center justify-center mb-6">
                  <Layers className="h-5 w-5 text-foreground" />
                </div>
                <h3 className="font-display text-2xl mb-4">
                  Context injection
                </h3>
                <p className="text-muted-foreground leading-relaxed">
                  Muse pulls from your Foundation—positioning, proof points,
                  voice guidelines. It selects the right cohort. It understands
                  the campaign arc this asset belongs to.
                </p>
              </div>
            </div>

            {/* Step 3 */}
            <div className="flex flex-col md:flex-row gap-8 md:gap-16 items-start md:ml-48">
              <div className="md:w-32 flex-shrink-0">
                <span className="font-display text-7xl text-foreground/10">
                  03
                </span>
              </div>
              <div className="flex-1 max-w-xl">
                <div className="h-12 w-12 rounded-full bg-foreground/5 flex items-center justify-center mb-6">
                  <Sparkles className="h-5 w-5 text-foreground" />
                </div>
                <h3 className="font-display text-2xl mb-4">
                  On-brand generation
                </h3>
                <p className="text-muted-foreground leading-relaxed">
                  Multiple variants, each connected to your strategy. A/B
                  testing built in. Voice consistency guaranteed. Content that
                  sounds like you, not like everyone else.
                </p>
              </div>
            </div>

            {/* Step 4 */}
            <div className="flex flex-col md:flex-row gap-8 md:gap-16 items-start md:ml-24">
              <div className="md:w-32 flex-shrink-0">
                <span className="font-display text-7xl text-foreground/10">
                  04
                </span>
              </div>
              <div className="flex-1 max-w-xl">
                <div className="h-12 w-12 rounded-full bg-foreground/5 flex items-center justify-center mb-6">
                  <FileText className="h-5 w-5 text-foreground" />
                </div>
                <h3 className="font-display text-2xl mb-4">
                  Polish and deploy
                </h3>
                <p className="text-muted-foreground leading-relaxed">
                  Edit in our built-in text editor or canvas. Export as PDF,
                  copy to clipboard, or push directly to your channels.
                  Everything lives in your library, tagged and searchable.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Asset Types — Visual Grid */}
      <section className="py-24 lg:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="max-w-xl mb-16">
            <p className="text-[10px] font-semibold uppercase tracking-[0.3em] text-muted-foreground mb-4">
              The Factory
            </p>
            <h2 className="font-display text-4xl md:text-5xl font-normal tracking-tight">
              Every format,
              <br />
              one engine.
            </h2>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {[
              { name: 'Social Posts', icon: '📱' },
              { name: 'Email Copy', icon: '✉️' },
              { name: 'Landing Pages', icon: '🖥️' },
              { name: 'Headlines', icon: '📰' },
              { name: 'Taglines', icon: '✨' },
              { name: 'Ad Copy', icon: '📢' },
              { name: 'Product Names', icon: '🏷️' },
              { name: 'Blog Outlines', icon: '📝' },
            ].map((item) => (
              <div
                key={item.name}
                className="aspect-square rounded-2xl border border-foreground/10 flex flex-col items-center justify-center p-6 hover:border-foreground/30 transition-colors group"
              >
                <span className="text-3xl mb-4 grayscale group-hover:grayscale-0 transition-all">
                  {item.icon}
                </span>
                <span className="text-sm font-medium text-center">
                  {item.name}
                </span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Second Pull Quote */}
      <section className="border-y border-foreground/10">
        <div className="mx-auto max-w-7xl px-6 lg:px-8 py-20 lg:py-28">
          <blockquote className="max-w-3xl mx-auto text-center">
            <p className="font-display text-2xl md:text-3xl lg:text-4xl font-normal leading-tight text-muted-foreground">
              Stop <span className="text-foreground">editing AI output</span>{' '}
              for hours.
              <br />
              Start with content that&apos;s already on-brand.
            </p>
          </blockquote>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-24 lg:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="max-w-2xl mx-auto text-center">
            <h2 className="font-display text-4xl md:text-5xl lg:text-6xl font-normal tracking-tight mb-8">
              Your creative engine
              <br />
              awaits.
            </h2>
            <p className="text-lg text-muted-foreground mb-12">
              Connected to your strategy. Trained on your voice. Ready to
              create.
            </p>
            <Button
              asChild
              size="lg"
              className="h-14 px-10 text-base rounded-full group"
            >
              <Link href="/muse">
                Try Muse Free
                <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </Link>
            </Button>
          </div>
        </div>
      </section>
    </MarketingLayout>
  );
}
