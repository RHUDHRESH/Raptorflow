'use client';

import { motion, useInView } from 'framer-motion';
import { useRef, useState } from 'react';
import { TiltCard } from '@/components/ui/TiltCard';
import { SplitText } from '@/components/ui/SplitText';
import { cn } from '@/lib/utils';

interface Feature {
  title: string;
  description: string;
  icon: React.ReactNode;
  color: string;
}

const features: Feature[] = [
  {
    title: 'AI-Powered Positioning',
    description: 'Transform messy context into crystal-clear positioning that actually resonates.',
    icon: (
      <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
    ),
    color: 'from-blue-500/20 to-purple-500/20',
  },
  {
    title: '90-Day War Plans',
    description: 'Strategic campaigns that build on each other instead of random tactics.',
    icon: (
      <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
      </svg>
    ),
    color: 'from-green-500/20 to-emerald-500/20',
  },
  {
    title: 'Weekly Moves',
    description: 'Ship concrete marketing assets every week that drive real revenue.',
    icon: (
      <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
      </svg>
    ),
    color: 'from-orange-500/20 to-red-500/20',
  },
  {
    title: 'Unified System',
    description: 'One platform instead of juggling 5+ disconnected tools.',
    icon: (
      <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
      </svg>
    ),
    color: 'from-pink-500/20 to-rose-500/20',
  },
];

export function FeatureShowcase() {
  const [activeIndex, setActiveIndex] = useState(0);
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-10%' });

  return (
    <section ref={ref} className="py-32 lg:py-40 relative overflow-hidden">
      {/* Background Decoration */}
      <div className="absolute top-1/2 left-0 w-96 h-96 rounded-full bg-foreground/5 blur-3xl -translate-y-1/2" />
      <div className="absolute top-1/3 right-0 w-80 h-80 rounded-full bg-muted-foreground/5 blur-3xl" />

      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        {/* Header */}
        <motion.div
          className="mx-auto max-w-2xl text-center mb-20"
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8 }}
        >
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground mb-4">
            Why RaptorFlow
          </p>
          <h2 className="font-display text-5xl lg:text-6xl font-medium tracking-tight mb-6">
            <SplitText animation="blur" delay={0.2}>
              Marketing that actually works
            </SplitText>
          </h2>
          <p className="text-xl text-muted-foreground">
            Built for founders who are tired of guessing and want a system that compounds.
          </p>
        </motion.div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 gap-8 max-w-6xl mx-auto">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 40 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.8, delay: 0.1 * index }}
              onMouseEnter={() => setActiveIndex(index)}
            >
              <TiltCard intensity={6} className="h-full">
                <div
                  className={cn(
                    'relative h-full p-8 rounded-2xl border border-border bg-background/50 backdrop-blur-sm',
                    'hover:border-foreground/20 transition-all duration-500 group',
                    'overflow-hidden'
                  )}
                  data-magnetic
                  data-cursor-text="Learn"
                >
                  {/* Gradient Background */}
                  <div
                    className={cn(
                      'absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500',
                      'bg-gradient-to-br',
                      feature.color
                    )}
                  />

                  {/* Content */}
                  <div className="relative z-10">
                    {/* Icon */}
                    <div className="mb-6 inline-flex p-3 rounded-xl bg-foreground/5 group-hover:bg-foreground/10 transition-colors">
                      {feature.icon}
                    </div>

                    {/* Title */}
                    <h3 className="font-display text-2xl font-semibold mb-3 group-hover:text-foreground transition-colors">
                      {feature.title}
                    </h3>

                    {/* Description */}
                    <p className="text-muted-foreground leading-relaxed text-lg">
                      {feature.description}
                    </p>
                  </div>

                  {/* Decorative Corner */}
                  <div className="absolute top-0 right-0 w-32 h-32 opacity-0 group-hover:opacity-10 transition-opacity duration-500">
                    <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <circle cx="100" cy="0" r="100" fill="currentColor" />
                    </svg>
                  </div>
                </div>
              </TiltCard>
            </motion.div>
          ))}
        </div>

        {/* Bottom Decoration */}
        <motion.div
          className="mt-20 text-center"
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : {}}
          transition={{ duration: 0.8, delay: 0.6 }}
        >
          <div className="inline-flex items-center gap-2 text-sm text-muted-foreground">
            <span className="w-8 h-px bg-border" />
            <span>And so much more</span>
            <span className="w-8 h-px bg-border" />
          </div>
        </motion.div>
      </div>
    </section>
  );
}
