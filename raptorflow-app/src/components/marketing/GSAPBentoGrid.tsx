'use client';

import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { ImagePlaceholder } from '@/components/ui/ImagePlaceholder';
import { cn } from '@/lib/utils';

gsap.registerPlugin(ScrollTrigger);

const bentoItems = [
  {
    title: 'Foundation Module',
    description: 'Define your market positioning in minutes',
    imagePrompt: 'Clean interface showing ICP builder: Circular avatar placeholders with demographic info, pain points listed as tags, buying behavior graphs. Minimalist design, purple accents.',
    span: 'lg:col-span-2 lg:row-span-2',
    size: 'lg' as const,
  },
  {
    title: 'AI Content Engine',
    description: 'Generate on-brand content at scale',
    imagePrompt: 'AI writing assistant interface: Text editor with AI suggestions sidebar, tone selector, brand voice controls. Modern writing tool aesthetic.',
    span: 'lg:col-span-1 lg:row-span-1',
    size: 'md' as const,
  },
  {
    title: 'Analytics Dashboard',
    description: 'Track what matters',
    imagePrompt: 'Analytics dashboard: Clean charts showing campaign performance, engagement metrics, conversion funnels. Data visualization with gradients.',
    span: 'lg:col-span-1 lg:row-span-1',
    size: 'md' as const,
  },
  {
    title: 'Campaign Timeline',
    description: '90-day strategic view',
    imagePrompt: 'Gantt chart / timeline view: Horizontal bars showing overlapping campaigns across 3 months, milestones marked, color-coded by category.',
    span: 'lg:col-span-1 lg:row-span-1',
    size: 'md' as const,
  },
  {
    title: 'Team Collaboration',
    description: 'Real-time updates',
    imagePrompt: 'Team workspace: Avatar circles of team members, live cursors, comment threads, activity feed. Collaborative tool interface.',
    span: 'lg:col-span-1 lg:row-span-1',
    size: 'md' as const,
  },
  {
    title: 'Asset Library',
    description: 'All your marketing assets organized',
    imagePrompt: 'Media library grid: Thumbnails of images, videos, documents in organized folders. Clean file management UI with preview cards.',
    span: 'lg:col-span-2 lg:row-span-1',
    size: 'md' as const,
  },
];

export function GSAPBentoGrid() {
  const sectionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      // Title animation
      gsap.from('.bento-title', {
        opacity: 0,
        y: 50,
        duration: 1,
        scrollTrigger: {
          trigger: '.bento-title',
          start: 'top 80%',
        },
      });

      // Bento cards stagger
      gsap.from('.bento-card', {
        opacity: 0,
        scale: 0.8,
        stagger: {
          amount: 0.8,
          from: 'random',
        },
        duration: 0.8,
        ease: 'back.out(1.2)',
        scrollTrigger: {
          trigger: '.bento-grid',
          start: 'top 70%',
        },
      });

      // Hover effect setup
      document.querySelectorAll('.bento-card').forEach((card) => {
        const tl = gsap.timeline({ paused: true });
        tl.to(card, {
          y: -10,
          boxShadow: '0 20px 40px rgba(0,0,0,0.2)',
          duration: 0.3,
          ease: 'power2.out',
        });

        card.addEventListener('mouseenter', () => tl.play());
        card.addEventListener('mouseleave', () => tl.reverse());
      });
    }, sectionRef);

    return () => ctx.revert();
  }, []);

  return (
    <section
      ref={sectionRef}
      className="py-32 lg:py-40 relative overflow-hidden bg-gradient-to-b from-background to-muted/20"
    >
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        {/* Header */}
        <div className="bento-title text-center mb-16">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground mb-4">
            Complete Platform
          </p>
          <h2 className="font-display text-5xl lg:text-7xl font-bold tracking-tight mb-6">
            Everything you need
            <br />
            <span className="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              in one place
            </span>
          </h2>
        </div>

        {/* Bento Grid */}
        <div className="bento-grid grid grid-cols-1 lg:grid-cols-3 gap-6">
          {bentoItems.map((item, index) => (
            <div
              key={index}
              className={cn(
                'bento-card group relative overflow-hidden rounded-3xl border border-border bg-background/50 backdrop-blur-sm p-8',
                'hover:border-purple-500/50 transition-all duration-300',
                item.span
              )}
            >
              {/* Gradient overlay */}
              <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-pink-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

              {/* Content */}
              <div className="relative z-10">
                <h3 className="font-display text-2xl font-bold mb-2">
                  {item.title}
                </h3>
                <p className="text-muted-foreground mb-6">
                  {item.description}
                </p>

                {/* Image */}
                <ImagePlaceholder
                  prompt={item.imagePrompt}
                  aspectRatio={item.span.includes('row-span-2') ? 'portrait' : 'video'}
                  size={item.size}
                  className="mt-auto"
                />
              </div>

              {/* Decorative corner */}
              <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-purple-500/10 to-transparent rounded-bl-full opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}