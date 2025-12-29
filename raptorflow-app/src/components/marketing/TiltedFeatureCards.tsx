'use client';

import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { ImagePlaceholder } from '@/components/ui/ImagePlaceholder';
import { cn } from '@/lib/utils';
import { ArrowRight } from 'lucide-react';

gsap.registerPlugin(ScrollTrigger);

import '@/styles/landing-animations.css';

const features = [
  {
    title: 'Foundation',
    subtitle: 'Know Your Market',
    description:
      'Define your positioning, ICPs, and competitive landscape in minutes. Every campaign decision flows from this single source of truth.',
    imagePrompt:
      'Clean ICP builder interface floating in 3D space. Avatar circles with demographic info, pain point tags, and behavior charts. Minimal design, zinc tones. The card appears to float with a soft shadow beneath. Modern marketing SaaS aesthetic.',
    tilt: 'left',
    accent: 'from-zinc-400/20 to-transparent',
  },
  {
    title: 'Muse',
    subtitle: 'AI Content Engine',
    description:
      'Generate on-brand content at scale. From LinkedIn posts to email sequences, Muse speaks your voice—backed by your positioning.',
    imagePrompt:
      'AI chat interface with conversation bubbles. One side shows user input, other shows AI-generated marketing copy suggestions. Glowing cursor effect. Modern, clean, conversational UI. Floating in isometric view with soft shadows.',
    tilt: 'right',
    accent: 'from-zinc-500/20 to-transparent',
  },
  {
    title: 'Campaigns',
    subtitle: '90-Day War Plans',
    description:
      'Strategic marketing arcs that compound. Plan your quarter, track momentum, and know exactly what to execute next.',
    imagePrompt:
      'Gantt-style 90-day campaign timeline. Horizontal bars in soft colors (zinc, platinum, subtle gold). Milestones marked with elegant dots. The chart appears to pop out of its container with depth. Clean, minimal calendar view.',
    tilt: 'left',
    accent: 'from-zinc-400/20 to-transparent',
  },
  {
    title: 'Moves',
    subtitle: 'Weekly Execution',
    description:
      'Seven moves per week. Consistent shipping that builds momentum. Never wonder "what should I post?" again.',
    imagePrompt:
      'Weekly task board interface with 7 cards representing daily moves. Each card shows a marketing action with status indicators. Clean kanban-style layout. Soft shadows, zinc/platinum palette. Premium productivity app aesthetic.',
    tilt: 'right',
    accent: 'from-zinc-500/20 to-transparent',
  },
];

export function TiltedFeatureCards() {
  const sectionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      // Section title
      gsap.from('.feature-section-title', {
        opacity: 0,
        y: 60,
        duration: 0.8,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: '.feature-section-title',
          start: 'top 85%',
        },
      });

      // Feature cards with stagger
      gsap.utils.toArray<HTMLElement>('.feature-card').forEach((card, i) => {
        const direction = i % 2 === 0 ? -1 : 1;

        gsap.from(card, {
          opacity: 0,
          x: direction * 80,
          rotationY: direction * 5,
          duration: 1,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: card,
            start: 'top 80%',
          },
        });

        // Image parallax inside card
        const image = card.querySelector('.feature-image');
        if (image) {
          gsap.to(image, {
            y: -30,
            scrollTrigger: {
              trigger: card,
              start: 'top bottom',
              end: 'bottom top',
              scrub: 1,
            },
          });
        }
      });
    }, sectionRef);

    return () => ctx.revert();
  }, []);

  return (
    <section ref={sectionRef} className="py-32 lg:py-40 overflow-hidden">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        {/* Section Header */}
        <div className="feature-section-title text-center mb-20 lg:mb-28">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground mb-4">
            The Complete System
          </p>
          <h2 className="font-display text-4xl lg:text-6xl font-semibold tracking-tight mb-6">
            Everything connects.
            <br />
            <span className="text-muted-foreground">Nothing wasted.</span>
          </h2>
        </div>

        {/* Feature Cards */}
        <div className="space-y-24 lg:space-y-32">
          {features.map((feature, index) => (
            <div
              key={feature.title}
              className={cn(
                'feature-card grid lg:grid-cols-2 gap-12 lg:gap-20 items-center',
                index % 2 === 1 && 'lg:flex-row-reverse'
              )}
            >
              {/* Content */}
              <div className={cn('space-y-6', index % 2 === 1 && 'lg:order-2')}>
                <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-muted/50 border border-border/30">
                  <span className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">
                    {feature.subtitle}
                  </span>
                </div>
                <h3 className="font-display text-3xl lg:text-5xl font-semibold tracking-tight">
                  {feature.title}
                </h3>
                <p className="text-lg text-muted-foreground leading-relaxed max-w-md">
                  {feature.description}
                </p>
                <button className="inline-flex items-center gap-2 text-sm font-medium text-foreground group">
                  Learn more
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </button>
              </div>

              {/* Image */}
              <div className={cn('relative', index % 2 === 1 && 'lg:order-1')}>
                {/* Tilted card container */}
                <div
                  className={cn(
                    'relative rounded-2xl overflow-hidden depth-layer-3 interactive-tilt',
                    feature.tilt === 'left'
                      ? 'tilted-card'
                      : 'tilted-card-right'
                  )}
                >
                  {/* Gradient overlay */}
                  <div
                    className={cn(
                      'absolute inset-0 bg-gradient-to-br opacity-50 -z-10',
                      feature.accent
                    )}
                  />

                  <div className="feature-image">
                    <ImagePlaceholder
                      prompt={feature.imagePrompt}
                      aspectRatio="video"
                      size="lg"
                    />
                  </div>
                </div>

                {/* Decorative dots */}
                <div className="absolute -top-4 -right-4 w-24 h-24 opacity-10">
                  <svg className="w-full h-full" viewBox="0 0 100 100">
                    {[...Array(25)].map((_, i) => (
                      <circle
                        key={i}
                        cx={(i % 5) * 25 + 12.5}
                        cy={Math.floor(i / 5) * 25 + 12.5}
                        r="2"
                        fill="currentColor"
                      />
                    ))}
                  </svg>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
