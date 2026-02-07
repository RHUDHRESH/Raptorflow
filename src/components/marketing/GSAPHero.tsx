'use client';

import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { ImagePlaceholder } from '@/components/ui/ImagePlaceholder';
import { ArrowRight } from 'lucide-react';

gsap.registerPlugin(ScrollTrigger);

export function GSAPHero() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const headlineRef = useRef<HTMLDivElement>(null);
  const imageRef = useRef<HTMLDivElement>(null);
  const ctaRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      // Headline animation
      gsap.from('.headline-word', {
        opacity: 0,
        y: 100,
        rotationX: -90,
        stagger: 0.1,
        duration: 1.2,
        ease: 'power4.out',
        delay: 0.3,
      });

      // Image reveal
      gsap.from(imageRef.current, {
        opacity: 0,
        scale: 0.8,
        duration: 1.5,
        ease: 'power3.out',
        delay: 0.8,
      });

      // Floating animation for image
      gsap.to(imageRef.current, {
        y: -20,
        duration: 2.5,
        ease: 'sine.inOut',
        repeat: -1,
        yoyo: true,
      });

      // CTA animation
      gsap.from(ctaRef.current, {
        opacity: 0,
        y: 50,
        duration: 1,
        ease: 'power3.out',
        delay: 1.2,
      });

      // Parallax scroll effect
      gsap.to(headlineRef.current, {
        y: 200,
        opacity: 0,
        scrollTrigger: {
          trigger: sectionRef.current,
          start: 'top top',
          end: 'bottom top',
          scrub: true,
        },
      });

      gsap.to(imageRef.current, {
        y: -100,
        scrollTrigger: {
          trigger: sectionRef.current,
          start: 'top top',
          end: 'bottom top',
          scrub: true,
        },
      });
    }, sectionRef);

    return () => ctx.revert();
  }, []);

  return (
    <section
      ref={sectionRef}
      className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-b from-background via-background to-muted/20"
    >
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        {[...Array(20)].map((_, i) => (
          <div
            key={i}
            className="absolute w-2 h-2 rounded-full bg-foreground/5"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animation: `float ${5 + Math.random() * 10}s infinite ease-in-out`,
              animationDelay: `${Math.random() * 5}s`,
            }}
          />
        ))}
      </div>

      <div className="mx-auto max-w-7xl px-6 lg:px-8 py-24 lg:py-32 relative z-10">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          {/* Left: Text Content */}
          <div>
            <div className="mb-6">
              <span className="inline-block px-4 py-1.5 rounded-full border border-border bg-background/50 backdrop-blur-sm text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground">
                AI-Powered Marketing OS
              </span>
            </div>

            <div ref={headlineRef} className="mb-8 overflow-hidden">
              <h1 className="font-display text-6xl lg:text-8xl font-bold tracking-tight leading-none">
                {['Marketing', 'that', 'compounds', 'weekly'].map((word, i) => (
                  <span
                    key={i}
                    className="headline-word inline-block mr-4 mb-2"
                    style={{
                      background: i === 0 ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' :
                                  i === 3 ? 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' : 'none',
                      WebkitBackgroundClip: i === 0 || i === 3 ? 'text' : 'none',
                      WebkitTextFillColor: i === 0 || i === 3 ? 'transparent' : 'inherit',
                    }}
                  >
                    {word}
                  </span>
                ))}
              </h1>
            </div>

            <p className="text-xl lg:text-2xl text-muted-foreground mb-12 max-w-xl leading-relaxed">
              From chaos to clarity to execution. RaptorFlow turns your messy marketing into a predictable revenue machine.
            </p>

            <div ref={ctaRef} className="flex flex-col sm:flex-row gap-4">
              <Button
                asChild
                size="lg"
                className="h-14 px-8 text-base rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
              >
                <Link href="/login" className="group">
                  Get Started Free
                  <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </Link>
              </Button>
              <Button
                asChild
                size="lg"
                variant="outline"
                className="h-14 px-8 text-base rounded-xl"
              >
                <Link href="#demo">Watch Demo</Link>
              </Button>
            </div>

            {/* Trust indicators */}
            <div className="mt-12 flex items-center gap-8">
              <div className="flex -space-x-2">
                {[1, 2, 3, 4].map((i) => (
                  <div
                    key={i}
                    className="w-10 h-10 rounded-full border-2 border-background bg-gradient-to-br from-purple-400 to-pink-400"
                  />
                ))}
              </div>
              <p className="text-sm text-muted-foreground">
                Trusted by <span className="font-semibold text-foreground">500+</span> founders
              </p>
            </div>
          </div>

          {/* Right: Hero Image */}
          <div ref={imageRef} className="relative">
            <ImagePlaceholder
              prompt="Hero image: Modern 3D dashboard mockup showing RaptorFlow interface with glowing purple and pink gradients. Multiple floating UI cards displaying campaign analytics, AI-generated content, and weekly moves. Isometric perspective with soft shadows. Ultra-modern, clean design with depth and dimension. Dark mode aesthetic with neon accents."
              aspectRatio="square"
              className="shadow-2xl"
              size="lg"
            />

            {/* Floating badges */}
            <div className="absolute -top-6 -left-6 bg-background/90 backdrop-blur-sm rounded-xl p-4 border border-border shadow-lg">
              <p className="text-sm font-semibold">🚀 10min Setup</p>
            </div>
            <div className="absolute -bottom-6 -right-6 bg-background/90 backdrop-blur-sm rounded-xl p-4 border border-border shadow-lg">
              <p className="text-sm font-semibold">✨ AI-Powered</p>
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes float {
          0%, 100% {
            transform: translateY(0);
          }
          50% {
            transform: translateY(-20px);
          }
        }
      `}</style>
    </section>
  );
}
