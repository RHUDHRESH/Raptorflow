'use client';

import { motion, useScroll, useTransform } from 'framer-motion';
import { useRef } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { MagneticButton } from '@/components/ui/MagneticButton';
import { SplitText } from '@/components/ui/SplitText';
import { AbstractArtwork, FloatingDots, NoisTexture } from './AbstractArtwork';
import { ParticleField } from './VisualEffects';
import { cn } from '@/lib/utils';

export function EnhancedHero() {
  const ref = useRef(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ['start start', 'end start'],
  });

  const y = useTransform(scrollYProgress, [0, 1], ['0%', '50%']);
  const opacity = useTransform(scrollYProgress, [0, 0.5], [1, 0]);
  const scale = useTransform(scrollYProgress, [0, 1], [1, 0.8]);

  return (
    <section
      ref={ref}
      className="relative min-h-screen flex items-center justify-center overflow-hidden"
      data-magnetic
      data-cursor-text="Explore"
    >
      {/* Background Layers */}
      <div className="absolute inset-0 -z-30">
        <NoisTexture />
      </div>

      {/* Particle Background */}
      <div className="absolute inset-0 -z-20 opacity-30">
        <ParticleField
          particleCount={80}
          connectionDistance={150}
          mouseInteraction={true}
        />
      </div>

      {/* Abstract Artwork - Geometric */}
      <motion.div
        className="absolute top-1/4 right-0 w-1/3 h-1/3 text-foreground/5 -z-10"
        style={{ y, opacity }}
      >
        <AbstractArtwork variant="geometric" />
      </motion.div>

      {/* Abstract Artwork - Organic */}
      <motion.div
        className="absolute bottom-0 left-0 w-1/2 h-1/2 text-foreground/5 -z-10"
        style={{ y: useTransform(scrollYProgress, [0, 1], ['0%', '30%']) }}
      >
        <AbstractArtwork variant="organic" />
      </motion.div>

      {/* Floating Dots */}
      <FloatingDots className="text-foreground -z-10" />

      {/* Gradient Orbs */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 rounded-full bg-foreground/5 blur-3xl -z-10" />
      <div className="absolute bottom-1/4 right-1/4 w-80 h-80 rounded-full bg-muted-foreground/5 blur-3xl -z-10" />

      {/* Content */}
      <motion.div
        className="relative z-10 mx-auto max-w-7xl px-6 lg:px-8 py-24"
        style={{ scale, opacity }}
      >
        <div className="mx-auto max-w-5xl text-center">
          {/* Eyebrow */}
          <motion.div
            className="mb-8"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            <span className="inline-block px-4 py-1.5 rounded-full border border-border bg-background/50 backdrop-blur-sm">
              <span className="text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground">
                The Founder Marketing Operating System
              </span>
            </span>
          </motion.div>

          {/* Main Headline with Split Text */}
          <div className="mb-8 space-y-2">
            <h1 className="font-display text-7xl lg:text-9xl font-medium tracking-tight leading-none">
              <SplitText animation="blur" delay={0.4}>
                Marketing.
              </SplitText>
            </h1>
            <h1 className="font-display text-7xl lg:text-9xl font-medium tracking-tight leading-none text-muted-foreground">
              <SplitText animation="blur" delay={0.6} staggerDelay={0.03}>
                Finally under control.
              </SplitText>
            </h1>
          </div>

          {/* Subheadline */}
          <motion.p
            className="text-xl lg:text-2xl text-muted-foreground leading-relaxed mb-16 max-w-3xl mx-auto"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 1.2 }}
          >
            Turn messy business context into clear positioning and a 90-day
            marketing war plan—then ship weekly Moves that drive revenue.
          </motion.p>

          {/* CTA Buttons */}
          <motion.div
            className="flex flex-col sm:flex-row items-center justify-center gap-6"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 1.4 }}
          >
            <MagneticButton strength={0.4}>
              <Button
                asChild
                size="lg"
                className="h-16 px-12 text-lg rounded-2xl font-medium shadow-lg hover:shadow-xl transition-shadow"
                data-magnetic
                data-cursor-text="Start"
              >
                <Link href="/login">Get Started Free</Link>
              </Button>
            </MagneticButton>

            <MagneticButton strength={0.4}>
              <Button
                asChild
                variant="outline"
                size="lg"
                className="h-16 px-12 text-lg rounded-2xl font-medium bg-background/50 backdrop-blur-sm"
                data-magnetic
                data-cursor-text="Try"
              >
                <Link href="#try-it">Try It Now — No Signup</Link>
              </Button>
            </MagneticButton>
          </motion.div>

          {/* Trust Line */}
          <motion.p
            className="mt-12 text-sm text-muted-foreground"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 1.8 }}
          >
            No credit card required. Start in 2 minutes.
          </motion.p>

          {/* Scroll Indicator */}
          <motion.div
            className="mt-20"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 2 }}
          >
            <motion.div
              className="inline-flex flex-col items-center gap-2 text-muted-foreground"
              animate={{ y: [0, 8, 0] }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
                ease: 'easeInOut',
              }}
            >
              <span className="text-xs uppercase tracking-widest">Scroll</span>
              <svg
                width="20"
                height="20"
                viewBox="0 0 20 20"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M10 4V16M10 16L6 12M10 16L14 12"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </motion.div>
          </motion.div>
        </div>
      </motion.div>

      {/* Bottom Gradient Fade */}
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-background to-transparent" />
    </section>
  );
}
