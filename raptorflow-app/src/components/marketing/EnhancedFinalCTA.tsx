'use client';

import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { ArrowRight, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';

gsap.registerPlugin(ScrollTrigger);

import '@/styles/landing-animations.css';

export function EnhancedFinalCTA() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const cardRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      // Card entrance with dramatic tilt
      gsap.from(cardRef.current, {
        opacity: 0,
        y: 100,
        scale: 0.9,
        rotateX: 10,
        duration: 1.2,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: sectionRef.current,
          start: 'top 80%',
        },
      });

      // Text reveal
      gsap.from('.cta-headline-word', {
        opacity: 0,
        y: 60,
        stagger: 0.05,
        duration: 0.8,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: cardRef.current,
          start: 'top 70%',
        },
      });

      // Subtext
      gsap.from('.cta-subtext', {
        opacity: 0,
        y: 30,
        duration: 0.6,
        delay: 0.4,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: cardRef.current,
          start: 'top 70%',
        },
      });

      // Buttons
      gsap.from('.cta-buttons', {
        opacity: 0,
        y: 20,
        duration: 0.5,
        delay: 0.6,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: cardRef.current,
          start: 'top 70%',
        },
      });

      // Subtle floating for the card
      gsap.to(cardRef.current, {
        y: -10,
        duration: 4,
        ease: 'sine.inOut',
        repeat: -1,
        yoyo: true,
      });
    }, sectionRef);

    return () => ctx.revert();
  }, []);

  const headlineWords = ['Stop', 'guessing.', 'Start', 'shipping.'];

  return (
    <section
      ref={sectionRef}
      className="py-32 lg:py-40 relative overflow-hidden"
    >
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-background via-muted/20 to-muted/40 -z-10" />

      {/* Decorative orbs */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 rounded-full bg-gradient-to-br from-foreground/5 to-transparent blur-3xl -z-10" />
      <div className="absolute bottom-1/4 right-1/4 w-80 h-80 rounded-full bg-gradient-to-br from-foreground/3 to-transparent blur-3xl -z-10" />

      <div className="mx-auto max-w-5xl px-6 lg:px-8">
        {/* Main CTA Card - Tilted for dynamism */}
        <div
          ref={cardRef}
          className="tilted-card-right relative rounded-3xl bg-foreground text-background p-12 lg:p-20 depth-layer-hero overflow-hidden"
        >
          {/* Gradient mesh overlay */}
          <div className="absolute inset-0 opacity-10">
            <div className="absolute top-0 right-0 w-96 h-96 rounded-full bg-background blur-3xl" />
            <div className="absolute bottom-0 left-0 w-80 h-80 rounded-full bg-background blur-3xl" />
          </div>

          {/* Grid pattern */}
          <div className="absolute inset-0 opacity-[0.03]">
            <svg className="w-full h-full">
              <defs>
                <pattern
                  id="cta-grid"
                  width="40"
                  height="40"
                  patternUnits="userSpaceOnUse"
                >
                  <path
                    d="M 40 0 L 0 0 0 40"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1"
                  />
                </pattern>
              </defs>
              <rect width="100%" height="100%" fill="url(#cta-grid)" />
            </svg>
          </div>

          <div className="relative text-center">
            {/* Eyebrow */}
            <div className="mb-8 inline-flex items-center gap-2 px-4 py-2 rounded-full bg-background/10 border border-background/20">
              <Sparkles className="w-4 h-4" />
              <span className="text-sm font-medium">
                Ready to transform your marketing?
              </span>
            </div>

            {/* Headline */}
            <h2 className="font-display text-4xl lg:text-6xl xl:text-7xl font-semibold tracking-tight mb-8 overflow-hidden">
              {headlineWords.map((word, i) => (
                <span
                  key={i}
                  className={cn(
                    'cta-headline-word inline-block mr-[0.2em]',
                    i < 2 && 'opacity-70'
                  )}
                >
                  {word}
                </span>
              ))}
            </h2>

            {/* Subtext */}
            <p className="cta-subtext text-lg lg:text-xl opacity-70 mb-10 max-w-2xl mx-auto leading-relaxed">
              Join 500+ founders who replaced marketing chaos with a system that
              compounds. 10 minutes to clarity. Free to start.
            </p>

            {/* CTAs */}
            <div className="cta-buttons flex flex-col sm:flex-row items-center justify-center gap-4">
              <Button
                asChild
                size="lg"
                className="h-14 px-10 text-base rounded-xl bg-background text-foreground hover:bg-background/90 interactive-lift"
              >
                <Link
                  href="/login"
                  className="group inline-flex items-center gap-2"
                >
                  Start Free — No Credit Card
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </Link>
              </Button>
              <Button
                asChild
                variant="ghost"
                size="lg"
                className="h-14 px-8 text-base text-background hover:bg-background/10 hover:text-background"
              >
                <Link href="#demo">Watch 2-Min Demo</Link>
              </Button>
            </div>

            {/* Trust note */}
            <p className="mt-8 text-sm opacity-50">
              No BS. No 14-step onboarding. Just results.
            </p>
          </div>

          {/* Corner decoration */}
          <div className="absolute top-0 right-0 w-32 h-32">
            <svg viewBox="0 0 100 100" className="w-full h-full opacity-10">
              <circle cx="100" cy="0" r="80" fill="currentColor" />
            </svg>
          </div>
        </div>
      </div>
    </section>
  );
}
