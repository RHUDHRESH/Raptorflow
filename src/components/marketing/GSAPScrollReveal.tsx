'use client';

import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { ImagePlaceholder } from '@/components/ui/ImagePlaceholder';

gsap.registerPlugin(ScrollTrigger);

export function GSAPScrollReveal() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const imageRef = useRef<HTMLDivElement>(null);
  const textRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      // Pin the section while scrolling
      ScrollTrigger.create({
        trigger: sectionRef.current,
        start: 'top top',
        end: '+=200%',
        pin: true,
        pinSpacing: true,
      });

      // Image scale and rotation
      gsap.fromTo(
        imageRef.current,
        {
          scale: 0.6,
          rotation: -15,
          opacity: 0,
        },
        {
          scale: 1,
          rotation: 0,
          opacity: 1,
          scrollTrigger: {
            trigger: sectionRef.current,
            start: 'top top',
            end: '+=100%',
            scrub: true,
          },
        }
      );

      // Text reveal
      gsap.from('.reveal-text', {
        opacity: 0,
        y: 50,
        stagger: 0.2,
        scrollTrigger: {
          trigger: textRef.current,
          start: 'top 60%',
          end: 'top 20%',
          scrub: true,
        },
      });
    }, sectionRef);

    return () => ctx.revert();
  }, []);

  return (
    <section
      ref={sectionRef}
      className="relative h-screen flex items-center justify-center overflow-hidden bg-gradient-to-b from-muted/20 to-background"
    >
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          {/* Image */}
          <div ref={imageRef}>
            <ImagePlaceholder
              prompt="Product showcase: Isometric 3D view of multiple screens showing RaptorFlow dashboard in action. Floating UI elements, data flowing between modules, glowing connections. Futuristic, high-tech aesthetic with purple/pink neon highlights. Depth and dimension."
              aspectRatio="square"
              className="shadow-2xl"
              size="xl"
            />
          </div>

          {/* Text */}
          <div ref={textRef}>
            <div className="reveal-text">
              <h2 className="font-display text-5xl lg:text-6xl font-bold mb-6">
                Marketing that
                <br />
                <span className="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                  actually compounds
                </span>
              </h2>
            </div>
            <div className="reveal-text">
              <p className="text-xl text-muted-foreground mb-6 leading-relaxed">
                Every week builds on the last. Your positioning stays consistent.
                Your campaigns stack up. Results compound exponentially.
              </p>
            </div>
            <div className="reveal-text">
              <p className="text-lg text-muted-foreground leading-relaxed">
                No more starting from scratch every Monday. No more scattered tactics.
                Just systematic growth that gets easier over time.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
