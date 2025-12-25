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
import { TypingExperienceControls } from '@/components/ui/typing/TypingExperienceControls';

// GSAP Animation Components
import { AnimationProvider } from '@/components/providers/AnimationProvider';
import { HeroTextReveal, AnimatedHeadline } from '@/components/marketing/HeroTextReveal';
import { AmbientBackground, GradientLine } from '@/components/marketing/FloatingOrb';
import { MagneticButton, HoverLift } from '@/components/ui/MagneticButton';
import { SectionReveal, StaggerReveal, ParallaxSection } from '@/components/marketing/SectionReveal';
import { StatCard } from '@/components/marketing/NumberCounter';
import { QuoteReveal } from '@/components/marketing/QuoteReveal';
import { GrainOverlay, Spotlight } from '@/components/marketing/GrainOverlay';

// Advanced Spectacle Components
import { ScrollyStory, Marquee, DramaticReveal, TextScramble } from '@/components/marketing/ScrollStory';
import { ParticleField, Blob, Wave } from '@/components/marketing/VisualEffects';

// Stats data
const stats = [
  { value: 10, suffix: 'min', label: 'to build your 90-day plan' },
  { value: 1, suffix: 'system', label: 'instead of 5+ tools' },
  { value: 7, suffix: 'moves', label: 'shipped every week' },
];

// How it works steps
const steps = [
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
];

// Story steps for ScrollyStory
const storySteps = [
  {
    id: 'problem',
    highlight: 'The Problem',
    headline: 'Marketing feels like chaos',
    subheadline: '5+ tools. Random tactics. No clear strategy. Every week feels like starting over.',
  },
  {
    id: 'solution',
    highlight: 'The Solution',
    headline: 'One system to rule them all',
    subheadline: 'RaptorFlow connects your positioning, campaigns, and weekly execution into a single flow.',
  },
  {
    id: 'outcome',
    highlight: 'The Outcome',
    headline: 'Marketing that compounds',
    subheadline: 'Every week builds on the last. Results stack. Growth becomes predictable.',
  },
];

// Logos for marquee
const logoItems = [
  'Foundation', 'Cohorts', 'Campaigns', 'Moves', 'Muse', 'Matrix', 'Blackbox', 'Radar'
];

export default function LandingPage() {
  return (
    <AnimationProvider>
      <MarketingLayout>
        {/* Premium Overlays */}
        <GrainOverlay opacity={0.02} />
        <Spotlight size={600} intensity={0.03} />

        <TypingExperienceControls />

        {/* ============================================================
            HERO SECTION — Cinematic Reveal with Particles
            ============================================================ */}
        <section className="relative overflow-hidden min-h-screen flex items-center">
          {/* Particle Field Background */}
          <div className="absolute inset-0 -z-20 opacity-40">
            <ParticleField particleCount={60} connectionDistance={120} mouseInteraction={true} />
          </div>

          {/* Ambient Background */}
          <AmbientBackground className="-z-10" />

          {/* Animated Blob */}
          <div className="absolute top-20 right-0 -z-10 opacity-30">
            <Blob size={600} color="hsl(var(--foreground))" />
          </div>

          <div className="mx-auto max-w-7xl px-6 lg:px-8 py-24 lg:py-32">
            <div className="mx-auto max-w-4xl text-center">
              {/* Eyebrow with reveal */}
              <SectionReveal animation="fade-up" delay={0.1}>
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground mb-8">
                  The Founder Marketing Operating System
                </p>
              </SectionReveal>

              {/* Main Headline with cinematic text reveal */}
              <div className="mb-8">
                <AnimatedHeadline
                  lines={['Marketing.', 'Finally under control.']}
                  className="font-display text-6xl lg:text-8xl font-medium tracking-tight"
                  lineClassName="text-foreground [&:nth-child(2)]:text-muted-foreground"
                  delay={0.2}
                  stagger={0.25}
                />
              </div>

              {/* Subheadline with word reveal */}
              <SectionReveal animation="blur" delay={0.8}>
                <p className="text-xl lg:text-2xl text-muted-foreground leading-relaxed mb-12 max-w-2xl mx-auto">
                  Turn messy business context into clear positioning and a 90-day marketing war plan—then ship weekly Moves that drive revenue.
                </p>
              </SectionReveal>

              {/* CTAs with magnetic effect */}
              <SectionReveal animation="fade-up" delay={1.0}>
                <div className="flex flex-col sm:flex-row items-center justify-center gap-6">
                  <MagneticButton strength={0.3}>
                    <Button asChild size="lg" className="h-16 px-10 text-lg rounded-2xl font-medium">
                      <Link href="/login">Get Started Free</Link>
                    </Button>
                  </MagneticButton>
                  <MagneticButton strength={0.3}>
                    <Button asChild variant="outline" size="lg" className="h-16 px-10 text-lg rounded-2xl font-medium">
                      <Link href="#try-it">Try It Now — No Signup</Link>
                    </Button>
                  </MagneticButton>
                </div>
              </SectionReveal>

              {/* Trust line with scramble effect */}
              <SectionReveal animation="fade" delay={1.4}>
                <p className="mt-10 text-sm text-muted-foreground">
                  No credit card required. <TextScramble text="Start in 2 minutes." speed={25} />
                </p>
              </SectionReveal>
            </div>
          </div>

          {/* Wave decoration at bottom */}
          <div className="absolute bottom-0 left-0 right-0 h-24">
            <Wave className="w-full h-full" color="hsl(var(--foreground))" amplitude={15} frequency={0.015} />
          </div>
        </section>

        {/* ============================================================
            SCROLLY STORY — Narrative Scroll Experience
            ============================================================ */}
        <ScrollyStory steps={storySteps} className="bg-muted/20" />

        {/* ============================================================
            PAIN POINT QUOTE — Dramatic Reveal
            ============================================================ */}
        <DramaticReveal className="border-y border-border">
          <div className="mx-auto max-w-7xl px-6 lg:px-8 py-24">
            <QuoteReveal
              quote="If your marketing is confusing, you are losing—silently."
              className="mx-auto max-w-4xl"
            />
          </div>
        </DramaticReveal>

        {/* ============================================================
            MARQUEE — Infinite scroll modules
            ============================================================ */}
        <section className="py-8 border-b border-border overflow-hidden">
          <Marquee speed={40} direction="left">
            {logoItems.map((item) => (
              <div key={item} className="flex items-center gap-2 px-8">
                <span className="text-sm font-medium text-muted-foreground uppercase tracking-widest">
                  {item}
                </span>
                <span className="text-muted-foreground/30">•</span>
              </div>
            ))}
          </Marquee>
        </section>

        {/* ============================================================
            CHAOS TO CLARITY — Interactive Animation
            ============================================================ */}
        <section className="py-32 lg:py-40">
          <div className="mx-auto max-w-7xl px-6 lg:px-8">
            <SectionReveal animation="fade-up" className="mx-auto max-w-2xl text-center mb-16">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground mb-4">
                The Transformation
              </p>
              <h2 className="font-display text-5xl lg:text-6xl font-medium tracking-tight mb-6">
                Watch the chaos organize
              </h2>
              <p className="text-xl text-muted-foreground">
                Click to see what happens when you stop guessing and start systematizing.
              </p>
            </SectionReveal>
            <SectionReveal animation="scale" delay={0.2}>
              <ChaosToClarity />
            </SectionReveal>
          </div>
        </section>

        {/* ============================================================
            AI DEMO — Positioning Playground
            ============================================================ */}
        <section id="try-it" className="py-32 lg:py-40 border-y border-border bg-muted/30 relative overflow-hidden">
          {/* Background particle effect */}
          <div className="absolute inset-0 opacity-20">
            <ParticleField particleCount={30} connectionDistance={80} mouseInteraction={false} />
          </div>

          <div className="mx-auto max-w-7xl px-6 lg:px-8 relative z-10">
            <SectionReveal animation="fade-up" className="mx-auto max-w-2xl text-center mb-16">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground mb-4">
                Try It Now
              </p>
              <h2 className="font-display text-5xl lg:text-6xl font-medium tracking-tight mb-6">
                Positioning Playground
              </h2>
              <p className="text-xl text-muted-foreground">
                Describe your business. Get your positioning, ICP, and first Moves instantly.
              </p>
            </SectionReveal>
            <SectionReveal animation="fade-up" delay={0.2}>
              <PositioningPlayground />
            </SectionReveal>
          </div>
        </section>

        {/* ============================================================
            STATS SECTION — Animated Counters with Parallax
            ============================================================ */}
        <section className="py-24 lg:py-32 relative overflow-hidden">
          <ParallaxSection speed={0.2} className="absolute inset-0 -z-10">
            <div className="absolute top-0 left-1/4 w-96 h-96 rounded-full bg-foreground/5 blur-3xl" />
            <div className="absolute bottom-0 right-1/4 w-80 h-80 rounded-full bg-muted-foreground/5 blur-3xl" />
          </ParallaxSection>

          <div className="mx-auto max-w-7xl px-6 lg:px-8 relative z-10">
            <GradientLine className="mb-20" />
            <StaggerReveal className="grid grid-cols-1 md:grid-cols-3 gap-12 lg:gap-16" stagger={0.2}>
              {stats.map((stat, index) => (
                <StatCard
                  key={stat.label}
                  value={stat.value}
                  suffix={stat.suffix}
                  label={stat.label}
                  delay={index * 0.2}
                />
              ))}
            </StaggerReveal>
            <GradientLine className="mt-20" />
          </div>
        </section>

        {/* ============================================================
            SYSTEM FLOW — Connected Diagram
            ============================================================ */}
        <section className="py-32 lg:py-40 border-y border-border">
          <div className="mx-auto max-w-7xl px-6 lg:px-8">
            <SectionReveal animation="fade-up" className="mx-auto max-w-2xl text-center mb-16">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground mb-4">
                The System
              </p>
              <h2 className="font-display text-5xl lg:text-6xl font-medium tracking-tight mb-6">
                Everything connects
              </h2>
              <p className="text-xl text-muted-foreground">
                Not 8 separate tools. One unified system where every piece feeds the next.
              </p>
            </SectionReveal>
            <SectionReveal animation="scale" delay={0.2}>
              <SystemFlowDiagram />
            </SectionReveal>
          </div>
        </section>

        {/* ============================================================
            HOW IT WORKS — Staggered Steps with Hover Lift
            ============================================================ */}
        <section className="py-32 lg:py-40">
          <div className="mx-auto max-w-7xl px-6 lg:px-8">
            <SectionReveal animation="fade-up" className="mx-auto max-w-2xl text-center mb-20">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground mb-4">
                The Process
              </p>
              <h2 className="font-display text-5xl lg:text-6xl font-medium tracking-tight mb-6">
                Clarify. Build. Run.
              </h2>
              <p className="text-xl text-muted-foreground">
                Three steps to marketing that compounds instead of resetting every Monday.
              </p>
            </SectionReveal>

            <StaggerReveal
              className="grid lg:grid-cols-3 gap-12 max-w-5xl mx-auto"
              stagger={0.25}
              direction="up"
            >
              {steps.map((item) => (
                <HoverLift key={item.step} className="relative group" liftAmount={8}>
                  <div className="absolute -inset-4 rounded-2xl bg-muted/50 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                  <div className="relative">
                    <div className="text-7xl font-mono font-bold text-muted/20 mb-6 group-hover:text-muted/40 transition-colors">
                      {item.step}
                    </div>
                    <h3 className="text-2xl font-semibold mb-3">{item.title}</h3>
                    <p className="text-muted-foreground leading-relaxed text-lg">{item.description}</p>
                  </div>
                </HoverLift>
              ))}
            </StaggerReveal>
          </div>
        </section>

        {/* ============================================================
            CHAOS DIAGNOSTIC — Interactive Quiz
            ============================================================ */}
        <section className="py-32 lg:py-40 border-y border-border bg-muted/30">
          <div className="mx-auto max-w-7xl px-6 lg:px-8">
            <SectionReveal animation="fade-up" className="mx-auto max-w-2xl text-center mb-16">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground mb-4">
                Self-Assessment
              </p>
              <h2 className="font-display text-5xl lg:text-6xl font-medium tracking-tight mb-6">
                What is your Marketing Chaos Score?
              </h2>
              <p className="text-xl text-muted-foreground">
                6 questions. 60 seconds. Get your personalized diagnosis.
              </p>
            </SectionReveal>
            <SectionReveal animation="fade-up" delay={0.2}>
              <ChaosDiagnostic />
            </SectionReveal>
          </div>
        </section>

        {/* ============================================================
            MODULES SPECTACLE — Interactive Showcase
            ============================================================ */}
        <ModulesSpectacle />

        {/* ============================================================
            BEFORE/AFTER — Transformation Generator
            ============================================================ */}
        <section className="py-32 lg:py-40 border-y border-border bg-muted/30">
          <div className="mx-auto max-w-7xl px-6 lg:px-8">
            <SectionReveal animation="fade-up">
              <BeforeAfterGenerator />
            </SectionReveal>
          </div>
        </section>

        {/* ============================================================
            TESTIMONIAL — Dramatic Quote with Blur Reveal
            ============================================================ */}
        <DramaticReveal className="py-32 lg:py-40">
          <div className="mx-auto max-w-7xl px-6 lg:px-8">
            <div className="mx-auto max-w-4xl text-center">
              <blockquote>
                <p className="font-display text-4xl lg:text-5xl font-medium leading-relaxed text-foreground">
                  &quot;You should not have to guess your marketing.
                  <br />
                  <span className="text-muted-foreground">With RaptorFlow, you will not.&quot;</span>
                </p>
              </blockquote>
            </div>
          </div>
        </DramaticReveal>

        {/* ============================================================
            FINAL CTA — Dramatic Close with Particles
            ============================================================ */}
        <section className="border-t border-border bg-foreground text-background relative overflow-hidden min-h-[70vh] flex items-center">
          {/* Particle Background */}
          <div className="absolute inset-0 opacity-10">
            <ParticleField particleCount={40} connectionDistance={100} mouseInteraction={true} />
          </div>

          {/* Gradient overlay */}
          <div
            className="absolute inset-0 pointer-events-none"
            style={{
              background: 'radial-gradient(ellipse at center, transparent 0%, hsl(var(--foreground) / 0.3) 100%)',
            }}
          />

          <div className="mx-auto max-w-7xl px-6 lg:px-8 py-32 relative z-10 w-full">
            <div className="mx-auto max-w-3xl text-center">
              <SectionReveal animation="fade-up">
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-background/60 mb-8">
                  Ready to start?
                </p>
              </SectionReveal>
              <SectionReveal animation="blur" delay={0.2}>
                <h2 className="font-display text-5xl lg:text-7xl font-medium tracking-tight mb-8">
                  Stop trying marketing.
                  <br />
                  <span className="text-background/70">Start running a machine.</span>
                </h2>
              </SectionReveal>
              <SectionReveal animation="fade" delay={0.6}>
                <p className="text-xl text-background/60 mb-12 max-w-xl mx-auto">
                  Give us your messy context. We will turn it into a plan you can actually execute.
                </p>
              </SectionReveal>
              <SectionReveal animation="fade-up" delay={0.8}>
                <MagneticButton strength={0.35}>
                  <Button asChild size="lg" variant="secondary" className="h-16 px-12 text-lg rounded-2xl font-medium">
                    <Link href="/login">Get Started Free</Link>
                  </Button>
                </MagneticButton>
              </SectionReveal>
            </div>
          </div>
        </section>
      </MarketingLayout>
    </AnimationProvider>
  );
}
