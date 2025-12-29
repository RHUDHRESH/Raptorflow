'use client';

import Link from 'next/link';
import { MarketingLayout } from '@/components/marketing/MarketingLayout';
import { Button } from '@/components/ui/button';
import {
  ArrowRight,
  Activity,
  Shield,
  AlertTriangle,
  Zap,
  Eye,
  Power,
} from 'lucide-react';

/**
 * Matrix Product Page — Editorial Style
 * Industrial Command Center / Monochrome / Control Narrative
 */
export default function MatrixProductPage() {
  return (
    <MarketingLayout>
      {/* Hero — The Watchtower */}
      <section className="relative min-h-[80vh] flex items-center justify-center overflow-hidden">
        {/* Industrial Grid Pattern */}
        <div className="absolute inset-0 -z-10">
          {/* Grid lines */}
          <div className="absolute inset-0 opacity-[0.03]">
            {[...Array(12)].map((_, i) => (
              <div
                key={i}
                className="absolute h-full w-px bg-foreground"
                style={{ left: `${(i + 1) * (100 / 13)}%` }}
              />
            ))}
            {[...Array(8)].map((_, i) => (
              <div
                key={i}
                className="absolute w-full h-px bg-foreground"
                style={{ top: `${(i + 1) * (100 / 9)}%` }}
              />
            ))}
          </div>
          {/* Central focal point */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px]">
            <div className="absolute inset-0 rounded-full border border-foreground/5" />
            <div className="absolute inset-[100px] rounded-full border border-foreground/5" />
            <div className="absolute inset-[200px] rounded-full border border-foreground/5" />
          </div>
        </div>

        <div className="mx-auto max-w-7xl px-6 lg:px-8 py-24 lg:py-32">
          <div className="max-w-4xl">
            <p className="text-[10px] font-semibold uppercase tracking-[0.3em] text-muted-foreground mb-12">
              Command & Control
            </p>

            <h1 className="font-display text-6xl md:text-7xl lg:text-8xl font-normal tracking-tight text-foreground leading-[0.9] mb-8">
              See everything.
              <br />
              <span className="italic text-muted-foreground">Control</span>{' '}
              everything.
            </h1>

            <p className="text-xl md:text-2xl text-muted-foreground leading-relaxed max-w-2xl font-light mb-16">
              Matrix is your industrial-grade command center. Monitor agents,
              track costs, detect drift—and kill anything that isn&apos;t
              working.
            </p>

            <Button
              asChild
              size="lg"
              className="h-14 px-10 text-base rounded-full group"
            >
              <Link href="/matrix">
                Enter Matrix
                <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Status Indicators — Visual Bar */}
      <section className="border-y border-foreground/10 bg-foreground text-background py-8">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="flex flex-wrap justify-between items-center gap-8">
            <div className="flex items-center gap-3">
              <div className="h-3 w-3 rounded-full bg-green-400 animate-pulse" />
              <span className="font-mono text-sm">ALL SYSTEMS NOMINAL</span>
            </div>
            <div className="flex items-center gap-6 font-mono text-sm text-background/60">
              <span>
                AGENTS: <span className="text-background">7 ACTIVE</span>
              </span>
              <span>
                LATENCY: <span className="text-background">42ms</span>
              </span>
              <span>
                BURN: <span className="text-background">$2.14/day</span>
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* The Problem */}
      <section className="py-24 lg:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="grid lg:grid-cols-12 gap-16 items-start">
            <div className="lg:col-span-4">
              <p className="text-[10px] font-semibold uppercase tracking-[0.3em] text-muted-foreground mb-4">
                The Fog
              </p>
              <h2 className="font-display text-4xl md:text-5xl font-normal tracking-tight">
                Flying blind in
                <br />
                an AI world.
              </h2>
            </div>
            <div className="lg:col-span-7 lg:col-start-6">
              <div className="prose prose-lg text-muted-foreground space-y-6">
                <p className="text-xl leading-relaxed">
                  You&apos;ve deployed AI agents. They&apos;re generating
                  content, analyzing data, making decisions. But do you actually
                  know what they&apos;re doing?
                </p>
                <p className="text-lg leading-relaxed">
                  Marketing data scattered across twelve dashboards. Token costs
                  spiraling without warning. Models drifting off-message and you
                  find out from a customer complaint. Decisions made on vibes
                  because the real data is buried.
                </p>
                <p className="text-xl leading-relaxed font-medium text-foreground">
                  You need a command center, not another dashboard.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Core Capabilities */}
      <section className="border-y border-foreground/10 py-24 lg:py-32 bg-muted/20">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="max-w-xl mb-20">
            <p className="text-[10px] font-semibold uppercase tracking-[0.3em] text-muted-foreground mb-4">
              The Arsenal
            </p>
            <h2 className="font-display text-4xl md:text-5xl font-normal tracking-tight">
              Industrial-grade
              <br />
              control surfaces.
            </h2>
          </div>

          <div className="grid md:grid-cols-2 gap-12 lg:gap-20">
            {/* Capability 1 */}
            <div className="relative">
              <div className="absolute -left-8 top-0 w-px h-full bg-foreground/10" />
              <div className="h-14 w-14 rounded-full border border-foreground/20 flex items-center justify-center mb-8">
                <Activity className="h-6 w-6 text-foreground" />
              </div>
              <h3 className="font-display text-2xl mb-4">Agent Oversight</h3>
              <p className="text-muted-foreground leading-relaxed">
                Real-time visibility into every AI agent in your marketing
                stack. See what they&apos;re doing, what they&apos;re deciding,
                and how they&apos;re performing. One unified view.
              </p>
            </div>

            {/* Capability 2 */}
            <div className="relative">
              <div className="absolute -left-8 top-0 w-px h-full bg-foreground/10" />
              <div className="h-14 w-14 rounded-full border border-foreground/20 flex items-center justify-center mb-8">
                <Zap className="h-6 w-6 text-foreground" />
              </div>
              <h3 className="font-display text-2xl mb-4">Cost Intelligence</h3>
              <p className="text-muted-foreground leading-relaxed">
                Track token burn, inference costs, and ROI in real time. Know
                exactly what your AI is costing you—and whether it&apos;s worth
                it. Budget alerts before you overspend.
              </p>
            </div>

            {/* Capability 3 */}
            <div className="relative">
              <div className="absolute -left-8 top-0 w-px h-full bg-foreground/10" />
              <div className="h-14 w-14 rounded-full border border-foreground/20 flex items-center justify-center mb-8">
                <AlertTriangle className="h-6 w-6 text-foreground" />
              </div>
              <h3 className="font-display text-2xl mb-4">Drift Detection</h3>
              <p className="text-muted-foreground leading-relaxed">
                AI models drift. Messaging drifts. Data drifts. Matrix watches
                for deviations from your baseline and alerts you before
                customers notice. RAG status on everything.
              </p>
            </div>

            {/* Capability 4 */}
            <div className="relative">
              <div className="absolute -left-8 top-0 w-px h-full bg-foreground/10" />
              <div className="h-14 w-14 rounded-full border border-foreground/20 flex items-center justify-center mb-8">
                <Power className="h-6 w-6 text-foreground" />
              </div>
              <h3 className="font-display text-2xl mb-4">The Kill Switch</h3>
              <p className="text-muted-foreground leading-relaxed">
                When something goes wrong, you need to stop it. Instantly.
                One-click kill switch for any agent, any campaign, any process.
                Control that matches the speed of AI.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Pull Quote */}
      <section className="py-24 lg:py-28">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <blockquote className="max-w-4xl">
            <p className="font-display text-3xl md:text-4xl lg:text-5xl font-normal leading-tight">
              &ldquo;With AI, what you can&apos;t see{' '}
              <em className="not-italic text-muted-foreground">can</em> hurt
              you. Matrix makes the invisible visible.&rdquo;
            </p>
          </blockquote>
        </div>
      </section>

      {/* Metrics Preview */}
      <section className="border-y border-foreground/10 bg-foreground text-background py-24">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-12 text-center">
            <div>
              <div className="font-mono text-5xl lg:text-6xl font-light mb-2">
                P95
              </div>
              <div className="text-sm text-background/60 uppercase tracking-wider">
                Latency Tracking
              </div>
            </div>
            <div>
              <div className="font-mono text-5xl lg:text-6xl font-light mb-2">
                24/7
              </div>
              <div className="text-sm text-background/60 uppercase tracking-wider">
                Agent Monitoring
              </div>
            </div>
            <div>
              <div className="font-mono text-5xl lg:text-6xl font-light mb-2">
                $0.00
              </div>
              <div className="text-sm text-background/60 uppercase tracking-wider">
                Surprise Costs
              </div>
            </div>
            <div>
              <div className="font-mono text-5xl lg:text-6xl font-light mb-2">
                &lt;1s
              </div>
              <div className="text-sm text-background/60 uppercase tracking-wider">
                Kill Response
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Audit Trail Section */}
      <section className="py-24 lg:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div>
              <p className="text-[10px] font-semibold uppercase tracking-[0.3em] text-muted-foreground mb-4">
                Transparency
              </p>
              <h2 className="font-display text-4xl md:text-5xl font-normal tracking-tight mb-8">
                Every decision,
                <br />
                fully auditable.
              </h2>
              <p className="text-lg text-muted-foreground leading-relaxed mb-8">
                Deep inspection of raw agent inputs, tool calls, and LLM
                responses. Know not just what your AI decided, but why. Complete
                audit trail for compliance, debugging, and continuous
                improvement.
              </p>
              <div className="flex items-center gap-4">
                <div className="h-10 w-10 rounded-full bg-foreground flex items-center justify-center">
                  <Eye className="h-5 w-5 text-background" />
                </div>
                <span className="text-sm font-medium">
                  Full inference log exploration
                </span>
              </div>
            </div>

            {/* Visual representation */}
            <div className="bg-muted/30 rounded-2xl p-8 font-mono text-xs space-y-3 border border-foreground/5">
              <div className="text-muted-foreground">
                [14:32:01] Agent: muse_briefer
              </div>
              <div className="text-muted-foreground">
                [14:32:01] Input: &quot;Generate LinkedIn post for Q1
                launch&quot;
              </div>
              <div className="text-muted-foreground">
                [14:32:02] Context: Foundation.positioning +
                Cohort.early_founders
              </div>
              <div className="text-muted-foreground">
                [14:32:03] Tool: content_generator.create_post
              </div>
              <div className="text-foreground">
                [14:32:04] Output: &quot;Marketing. Finally under
                control...&quot;
              </div>
              <div className="text-green-600">
                [14:32:04] Status: SUCCESS | Tokens: 847 | Cost: $0.02
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-24 lg:py-32 border-t border-foreground/10">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="max-w-2xl mx-auto text-center">
            <h2 className="font-display text-4xl md:text-5xl lg:text-6xl font-normal tracking-tight mb-8">
              Take the
              <br />
              controls.
            </h2>
            <p className="text-lg text-muted-foreground mb-12">
              Industrial-grade oversight for your AI marketing ecosystem.
            </p>
            <Button
              asChild
              size="lg"
              className="h-14 px-10 text-base rounded-full group"
            >
              <Link href="/matrix">
                Enter Matrix
                <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </Link>
            </Button>
          </div>
        </div>
      </section>
    </MarketingLayout>
  );
}
