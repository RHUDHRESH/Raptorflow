'use client';

import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { ImagePlaceholder } from '@/components/ui/ImagePlaceholder';

gsap.registerPlugin(ScrollTrigger);

const testimonials = [
  {
    quote:
      "RaptorFlow is the missing piece we didn't know we needed. Marketing finally makes sense.",
    author: 'Sarah Chen',
    role: 'CEO, TechStart',
    avatarPrompt:
      'Professional headshot: Female entrepreneur, 30s, confident smile, modern office background, natural lighting',
  },
  {
    quote:
      'From 5 disconnected tools to 1 unified system. Our marketing velocity increased 10x.',
    author: 'Marcus Rodriguez',
    role: 'Founder, GrowthLab',
    avatarPrompt:
      'Professional headshot: Male founder, early 30s, glasses, casual business attire, tech startup vibe',
  },
  {
    quote:
      'The AI positioning saved us months of trial and error. We found our voice in 10 minutes.',
    author: 'Emily Watson',
    role: 'CMO, Innovate Co',
    avatarPrompt:
      'Professional headshot: Female marketing executive, late 20s, creative industry aesthetic',
  },
  {
    quote:
      'Weekly Moves changed everything. We ship actual marketing now, not just strategy docs.',
    author: 'David Park',
    role: 'Head of Marketing, ScaleUp',
    avatarPrompt:
      'Professional headshot: Male marketing leader, mid 30s, professional but approachable',
  },
];

export function GSAPTestimonialWall() {
  const sectionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      // Title animation
      gsap.from('.testimonial-title', {
        opacity: 0,
        y: 50,
        duration: 1,
        scrollTrigger: {
          trigger: '.testimonial-title',
          start: 'top 80%',
        },
      });

      // Testimonial cards
      gsap.from('.testimonial-card', {
        opacity: 0,
        y: 100,
        stagger: 0.15,
        duration: 0.8,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: '.testimonial-grid',
          start: 'top 70%',
        },
      });

      // Hover effects
      document.querySelectorAll('.testimonial-card').forEach((card) => {
        const tl = gsap.timeline({ paused: true });
        tl.to(card, {
          scale: 1.05,
          y: -10,
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
      className="py-32 lg:py-40 relative overflow-hidden"
    >
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-b from-background via-purple-500/5 to-background -z-10" />

      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        {/* Header */}
        <div className="testimonial-title text-center mb-20">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground mb-4">
            Testimonials
          </p>
          <h2 className="font-display text-5xl lg:text-7xl font-bold tracking-tight mb-6">
            Founders love
            <br />
            <span className="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              RaptorFlow
            </span>
          </h2>
        </div>

        {/* Testimonial Grid */}
        <div className="testimonial-grid grid md:grid-cols-2 gap-8">
          {testimonials.map((testimonial, index) => (
            <div
              key={index}
              className="testimonial-card relative overflow-hidden rounded-3xl border border-border bg-background/50 backdrop-blur-sm p-8"
            >
              {/* Gradient overlay */}
              <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-pink-500/5" />

              {/* Content */}
              <div className="relative z-10">
                {/* Quote */}
                <div className="mb-8">
                  <svg
                    className="w-12 h-12 text-purple-500/20 mb-4"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path d="M14.017 21v-7.391c0-5.704 3.731-9.57 8.983-10.609l.995 2.151c-2.432.917-3.995 3.638-3.995 5.849h4v10h-9.983zm-14.017 0v-7.391c0-5.704 3.748-9.57 9-10.609l.996 2.151c-2.433.917-3.996 3.638-3.996 5.849h3.983v10h-9.983z" />
                  </svg>
                  <p className="text-xl font-medium leading-relaxed">
                    "{testimonial.quote}"
                  </p>
                </div>

                {/* Author */}
                <div className="flex items-center gap-4">
                  <ImagePlaceholder
                    prompt={testimonial.avatarPrompt}
                    aspectRatio="square"
                    className="w-16 h-16 rounded-full"
                    size="sm"
                  />
                  <div>
                    <p className="font-semibold">{testimonial.author}</p>
                    <p className="text-sm text-muted-foreground">
                      {testimonial.role}
                    </p>
                  </div>
                </div>
              </div>

              {/* Decorative corner */}
              <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-pink-500/10 to-transparent rounded-bl-full" />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
