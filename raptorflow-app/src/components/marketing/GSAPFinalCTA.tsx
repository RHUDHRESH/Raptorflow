'use client';

import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { ImagePlaceholder } from '@/components/ui/ImagePlaceholder';
import { ArrowRight, Sparkles } from 'lucide-react';

gsap.registerPlugin(ScrollTrigger);

export function GSAPFinalCTA() {
  const sectionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      // Background animation
      gsap.from('.cta-bg', {
        scale: 0.8,
        opacity: 0,
        duration: 1.5,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: sectionRef.current,
          start: 'top 60%',
        },
      });

      // Text reveal
      gsap.from('.cta-text', {
        opacity: 0,
        y: 50,
        stagger: 0.2,
        duration: 1,
        scrollTrigger: {
          trigger: sectionRef.current,
          start: 'top 50%',
        },
      });

      // Button animation
      gsap.from('.cta-button', {
        opacity: 0,
        scale: 0,
        duration: 0.8,
        ease: 'back.out(1.5)',
        scrollTrigger: {
          trigger: sectionRef.current,
          start: 'top 40%',
        },
      });

      // Floating animation for sparkles
      gsap.to('.floating-sparkle', {
        y: -20,
        duration: 2,
        ease: 'sine.inOut',
        stagger: 0.2,
        repeat: -1,
        yoyo: true,
      });
    }, sectionRef);

    return () => ctx.revert();
  }, []);

  return (
    <section
      ref={sectionRef}
      className="relative py-32 lg:py-40 overflow-hidden"
    >
      {/* Background */}
      <div className="cta-bg absolute inset-0 bg-gradient-to-br from-purple-600 via-pink-600 to-red-600">
        <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-20" />
      </div>

      {/* Floating sparkles */}
      {[...Array(12)].map((_, i) => (
        <Sparkles
          key={i}
          className="floating-sparkle absolute text-white/20"
          style={{
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
            width: `${16 + Math.random() * 16}px`,
            height: `${16 + Math.random() * 16}px`,
          }}
        />
      ))}

      <div className="relative z-10 mx-auto max-w-7xl px-6 lg:px-8">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          {/* Left: Image */}
          <div className="order-2 lg:order-1">
            <ImagePlaceholder
              prompt="Final CTA hero image: Celebration scene with confetti, rockets launching, success metrics dashboard showing exponential growth. 3D illustration style with vibrant colors. Energetic, exciting, success-focused imagery. Depth and motion."
              aspectRatio="square"
              className="shadow-2xl rounded-3xl"
              size="xl"
            />
          </div>

          {/* Right: Content */}
          <div className="order-1 lg:order-2 text-white">
            <div className="cta-text">
              <p className="text-sm font-semibold uppercase tracking-[0.2em] mb-6 text-white/80">
                Ready to Transform?
              </p>
            </div>
            
            <div className="cta-text">
              <h2 className="font-display text-5xl lg:text-7xl font-bold mb-6 leading-tight">
                Start shipping
                <br />
                marketing that
                <br />
                compounds
              </h2>
            </div>

            <div className="cta-text">
              <p className="text-xl mb-8 text-white/90 leading-relaxed max-w-lg">
                Join 500+ founders who turned their marketing chaos into a
                predictable revenue machine.
              </p>
            </div>

            <div className="cta-button flex flex-col sm:flex-row gap-4">
              <Button
                asChild
                size="lg"
                className="h-16 px-10 text-lg rounded-xl bg-white text-purple-600 hover:bg-white/90 font-semibold group"
              >
                <Link href="/login">
                  Get Started Free
                  <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </Link>
              </Button>
              <Button
                asChild
                size="lg"
                variant="outline"
                className="h-16 px-10 text-lg rounded-xl border-white/30 text-white hover:bg-white/10"
              >
                <Link href="#demo">Watch Demo</Link>
              </Button>
            </div>

            <div className="cta-text mt-10 flex items-center gap-6">
              <div className="flex -space-x-2">
                {[1, 2, 3, 4, 5].map((i) => (
                  <div
                    key={i}
                    className="w-10 h-10 rounded-full border-2 border-white bg-white/20"
                  />
                ))}
              </div>
              <div className="text-sm text-white/90">
                <p className="font-semibold">500+ founders</p>
                <p className="text-white/70">already shipping</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}