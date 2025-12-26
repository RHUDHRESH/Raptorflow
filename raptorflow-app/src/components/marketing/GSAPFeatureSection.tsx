'use client';

import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { ImagePlaceholder } from '@/components/ui/ImagePlaceholder';

gsap.registerPlugin(ScrollTrigger);

const features = [
  {
    title: 'AI Positioning',
    description: 'Transform messy context into crystal-clear positioning that resonates with your ICP.',
    imagePrompt: 'Screenshot of AI positioning interface: Clean dashboard showing input fields for business context on left, AI-generated positioning framework on right with ICP profiles, value props, and messaging pillars. Modern UI with purple/pink gradients. Professional SaaS aesthetic.',
    color: 'from-blue-500 to-purple-600',
  },
  {
    title: '90-Day War Plans',
    description: 'Strategic campaigns that build momentum instead of random tactics.',
    imagePrompt: 'Kanban board view of 90-day marketing campaign: Three columns labeled "Month 1, 2, 3" with colorful cards representing campaigns. Each card shows metrics, status badges, and mini progress bars. Smooth gradients, modern calendar UI, timeline visualization.',
    color: 'from-purple-500 to-pink-600',
  },
  {
    title: 'Weekly Moves',
    description: 'Concrete marketing tasks that compound week over week.',
    imagePrompt: 'Weekly task dashboard: Grid of actionable move cards with checkboxes, due dates, and AI-generated content previews. Show mix of social posts, blog drafts, email campaigns. Clean task management UI with satisfying completion animations.',
    color: 'from-pink-500 to-red-500',
  },
];

export function GSAPFeatureSection() {
  const sectionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      // Fade in section title
      gsap.from('.section-title', {
        opacity: 0,
        y: 50,
        duration: 1,
        scrollTrigger: {
          trigger: '.section-title',
          start: 'top 80%',
        },
      });

      // Stagger feature cards
      gsap.from('.feature-card', {
        opacity: 0,
        y: 100,
        stagger: 0.2,
        duration: 1,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: '.features-grid',
          start: 'top 70%',
        },
      });

      // Parallax image effects
      document.querySelectorAll('.feature-image').forEach((img) => {
        gsap.to(img, {
          y: -50,
          scrollTrigger: {
            trigger: img,
            start: 'top bottom',
            end: 'bottom top',
            scrub: true,
          },
        });
      });

      // Hover animations
      document.querySelectorAll('.feature-card').forEach((card) => {
        const tl = gsap.timeline({ paused: true });
        tl.to(card, {
          scale: 1.05,
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
    <section ref={sectionRef} className="py-32 lg:py-40 relative overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-muted/20 via-background to-muted/20 -z-10" />

      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        {/* Section Header */}
        <div className="section-title text-center mb-20">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground mb-4">
            Core Features
          </p>
          <h2 className="font-display text-5xl lg:text-7xl font-bold tracking-tight mb-6 bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
            Built for founders who ship
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Every feature designed to turn strategy into execution
          </p>
        </div>

        {/* Features Grid */}
        <div className="features-grid space-y-32">
          {features.map((feature, index) => (
            <div
              key={feature.title}
              className={`feature-card grid lg:grid-cols-2 gap-12 items-center ${
                index % 2 === 1 ? 'lg:grid-flow-dense' : ''
              }`}
            >
              {/* Content */}
              <div className={index % 2 === 1 ? 'lg:col-start-2' : ''}>
                <div className="inline-block mb-4">
                  <div
                    className={`text-xs font-bold uppercase tracking-wider px-4 py-2 rounded-full bg-gradient-to-r ${feature.color} text-white`}
                  >
                    Feature #{index + 1}
                  </div>
                </div>
                <h3 className="font-display text-4xl lg:text-5xl font-bold mb-6">
                  {feature.title}
                </h3>
                <p className="text-xl text-muted-foreground leading-relaxed mb-8">
                  {feature.description}
                </p>

                {/* Stats */}
                <div className="grid grid-cols-3 gap-6">
                  <div>
                    <div className="text-3xl font-bold mb-1">10x</div>
                    <div className="text-sm text-muted-foreground">Faster</div>
                  </div>
                  <div>
                    <div className="text-3xl font-bold mb-1">90%</div>
                    <div className="text-sm text-muted-foreground">Clarity</div>
                  </div>
                  <div>
                    <div className="text-3xl font-bold mb-1">∞</div>
                    <div className="text-sm text-muted-foreground">Scale</div>
                  </div>
                </div>
              </div>

              {/* Image */}
              <div className={`feature-image ${index % 2 === 1 ? 'lg:col-start-1 lg:row-start-1' : ''}`}>
                <ImagePlaceholder
                  prompt={feature.imagePrompt}
                  aspectRatio="video"
                  className="shadow-2xl hover:shadow-3xl transition-shadow duration-300"
                  size="lg"
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
