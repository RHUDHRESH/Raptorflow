'use client';

import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { cn } from '@/lib/utils';

gsap.registerPlugin(ScrollTrigger);

import '@/styles/landing-animations.css';

const stats = [
  {
    value: '10',
    unit: 'min',
    label: 'to build your 90-day plan',
    detail: 'From zero to execution',
  },
  {
    value: '7',
    unit: 'moves',
    label: 'shipped every week',
    detail: 'Consistent compound growth',
  },
  {
    value: '1',
    unit: 'system',
    label: 'instead of 5+ tools',
    detail: 'Everything connected',
  },
  {
    value: '500',
    unit: '+',
    label: 'founders shipping weekly',
    detail: 'Join the movement',
  },
];

export function FloatingStats() {
  const sectionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      // Section entrance
      gsap.from('.stats-headline', {
        opacity: 0,
        y: 40,
        duration: 0.8,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: '.stats-headline',
          start: 'top 85%',
        },
      });

      // Stats cards with stagger and count-up
      gsap.utils.toArray<HTMLElement>('.stat-card').forEach((card, i) => {
        // Card entrance
        gsap.from(card, {
          opacity: 0,
          y: 60,
          scale: 0.95,
          duration: 0.8,
          delay: i * 0.1,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: card,
            start: 'top 85%',
          },
        });

        // Number count-up
        const numberEl = card.querySelector('.stat-number');
        if (numberEl) {
          const endValue = parseInt(numberEl.getAttribute('data-value') || '0');
          const obj = { value: 0 };

          gsap.to(obj, {
            value: endValue,
            duration: 2,
            ease: 'power2.out',
            scrollTrigger: {
              trigger: card,
              start: 'top 80%',
            },
            onUpdate: () => {
              numberEl.textContent = Math.round(obj.value).toString();
            },
          });
        }
      });

      // Floating animation for cards
      gsap.utils.toArray<HTMLElement>('.stat-card').forEach((card, i) => {
        gsap.to(card, {
          y: -10 - (i % 2) * 5,
          duration: 2.5 + i * 0.3,
          ease: 'sine.inOut',
          repeat: -1,
          yoyo: true,
          delay: i * 0.2,
        });
      });
    }, sectionRef);

    return () => ctx.revert();
  }, []);

  return (
    <section
      ref={sectionRef}
      className="py-32 lg:py-40 bg-muted/30 relative overflow-hidden"
    >
      {/* Subtle background pattern */}
      <div className="absolute inset-0 opacity-[0.02]">
        <svg className="w-full h-full">
          <defs>
            <pattern
              id="stats-grid"
              width="80"
              height="80"
              patternUnits="userSpaceOnUse"
            >
              <circle cx="40" cy="40" r="1" fill="currentColor" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#stats-grid)" />
        </svg>
      </div>

      <div className="mx-auto max-w-7xl px-6 lg:px-8 relative">
        {/* Section Header */}
        <div className="stats-headline text-center mb-16 lg:mb-24">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground mb-4">
            By The Numbers
          </p>
          <h2 className="font-display text-4xl lg:text-6xl font-semibold tracking-tight">
            Built for <span className="text-muted-foreground">execution</span>
          </h2>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8">
          {stats.map((stat, index) => (
            <div
              key={stat.label}
              className={cn(
                'stat-card relative p-8 lg:p-10 rounded-2xl bg-background border border-border/50 depth-layer-2 overflow-hidden group',
                index % 2 === 0 ? 'tilted-card' : 'tilted-card-right'
              )}
            >
              {/* Gradient accent on hover */}
              <div className="absolute inset-0 bg-gradient-to-br from-foreground/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

              <div className="relative">
                {/* Giant number */}
                <div className="flex items-baseline gap-1 mb-3">
                  <span
                    className="stat-number font-display text-5xl lg:text-6xl font-bold tracking-tight"
                    data-value={stat.value}
                  >
                    0
                  </span>
                  <span className="text-2xl lg:text-3xl font-semibold text-muted-foreground">
                    {stat.unit}
                  </span>
                </div>

                {/* Label */}
                <p className="text-sm lg:text-base text-muted-foreground mb-2">
                  {stat.label}
                </p>

                {/* Detail */}
                <p className="text-xs text-muted-foreground/70 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                  {stat.detail}
                </p>
              </div>

              {/* Decorative corner */}
              <div className="absolute bottom-0 right-0 w-20 h-20 bg-gradient-to-tl from-muted/50 to-transparent rounded-tl-full opacity-50" />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
