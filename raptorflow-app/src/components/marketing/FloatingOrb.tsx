'use client';

import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';

interface FloatingOrbProps {
  className?: string;
  size?: number;
  variant?: 'primary' | 'accent';
  parallaxSpeed?: number;
  morphDuration?: number;
}

export function FloatingOrb({
  className = '',
  size = 600,
  variant = 'primary',
  parallaxSpeed = 0.1,
  morphDuration = 8,
}: FloatingOrbProps) {
  const orbRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const orb = orbRef.current;
    if (!orb) return;

    const prefersReducedMotion = window.matchMedia(
      '(prefers-reduced-motion: reduce)'
    ).matches;
    if (prefersReducedMotion) return;

    // Breathing/morphing animation
    const morphTl = gsap.timeline({ repeat: -1, yoyo: true });
    morphTl.to(orb, {
      scale: 1.1,
      borderRadius: '60% 40% 70% 30%',
      duration: morphDuration,
      ease: 'sine.inOut',
    });
    morphTl.to(orb, {
      scale: 0.95,
      borderRadius: '40% 60% 30% 70%',
      duration: morphDuration,
      ease: 'sine.inOut',
    });

    // Mouse parallax effect
    const handleMouseMove = (e: MouseEvent) => {
      const { clientX, clientY } = e;
      const { innerWidth, innerHeight } = window;

      const xOffset = (clientX / innerWidth - 0.5) * 100 * parallaxSpeed;
      const yOffset = (clientY / innerHeight - 0.5) * 100 * parallaxSpeed;

      gsap.to(orb, {
        x: xOffset,
        y: yOffset,
        duration: 1.5,
        ease: 'power2.out',
      });
    };

    window.addEventListener('mousemove', handleMouseMove);

    return () => {
      morphTl.kill();
      window.removeEventListener('mousemove', handleMouseMove);
    };
  }, [parallaxSpeed, morphDuration]);

  const gradientClass =
    variant === 'primary' ? 'floating-orb--primary' : 'floating-orb--accent';

  return (
    <div
      ref={orbRef}
      className={`floating-orb ${gradientClass} ${className}`}
      style={{
        width: size,
        height: size,
      }}
    />
  );
}

// ============================================================================
// AMBIENT BACKGROUND - Multiple floating elements
// ============================================================================

interface AmbientBackgroundProps {
  className?: string;
}

export function AmbientBackground({ className = '' }: AmbientBackgroundProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const prefersReducedMotion = window.matchMedia(
      '(prefers-reduced-motion: reduce)'
    ).matches;
    if (prefersReducedMotion) return;

    const orbs = container.querySelectorAll('.ambient-orb');

    orbs.forEach((orb, index) => {
      // Each orb gets unique floating animation
      gsap.to(orb, {
        y: 'random(-30, 30)',
        x: 'random(-20, 20)',
        rotation: 'random(-5, 5)',
        duration: 4 + index,
        repeat: -1,
        yoyo: true,
        ease: 'sine.inOut',
        delay: index * 0.5,
      });
    });
  }, []);

  return (
    <div
      ref={containerRef}
      className={`absolute inset-0 overflow-hidden pointer-events-none ${className}`}
      aria-hidden="true"
    >
      {/* Large primary orb - top left */}
      <div
        className="ambient-orb absolute -top-32 -left-32 w-[600px] h-[600px] rounded-full opacity-20"
        style={{
          background:
            'radial-gradient(circle, hsl(var(--foreground) / 0.1) 0%, transparent 70%)',
          filter: 'blur(80px)',
        }}
      />

      {/* Medium accent orb - top right */}
      <div
        className="ambient-orb absolute top-20 -right-20 w-[400px] h-[400px] rounded-full opacity-15"
        style={{
          background:
            'radial-gradient(circle, hsl(var(--muted-foreground) / 0.15) 0%, transparent 70%)',
          filter: 'blur(60px)',
        }}
      />

      {/* Small orb - center */}
      <div
        className="ambient-orb absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] rounded-full opacity-10"
        style={{
          background:
            'radial-gradient(circle, hsl(var(--foreground) / 0.08) 0%, transparent 60%)',
          filter: 'blur(100px)',
        }}
      />

      {/* Subtle grid pattern */}
      <div
        className="absolute inset-0 opacity-[0.02]"
        style={{
          backgroundImage: `
            linear-gradient(hsl(var(--foreground)) 1px, transparent 1px),
            linear-gradient(90deg, hsl(var(--foreground)) 1px, transparent 1px)
          `,
          backgroundSize: '60px 60px',
        }}
      />
    </div>
  );
}

// ============================================================================
// GRADIENT LINE - Animated line decoration
// ============================================================================

interface GradientLineProps {
  className?: string;
  direction?: 'horizontal' | 'vertical';
}

export function GradientLine({
  className = '',
  direction = 'horizontal',
}: GradientLineProps) {
  const lineRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const line = lineRef.current;
    if (!line) return;

    const prefersReducedMotion = window.matchMedia(
      '(prefers-reduced-motion: reduce)'
    ).matches;
    if (prefersReducedMotion) {
      gsap.set(line, {
        scaleX: direction === 'horizontal' ? 1 : undefined,
        scaleY: direction === 'vertical' ? 1 : undefined,
      });
      return;
    }

    gsap.fromTo(
      line,
      {
        scaleX: direction === 'horizontal' ? 0 : 1,
        scaleY: direction === 'vertical' ? 0 : 1,
      },
      {
        scaleX: 1,
        scaleY: 1,
        duration: 1.2,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: line,
          start: 'top 85%',
        },
      }
    );
  }, [direction]);

  const isHorizontal = direction === 'horizontal';

  return (
    <div
      ref={lineRef}
      className={className}
      style={{
        height: isHorizontal ? '1px' : '100%',
        width: isHorizontal ? '100%' : '1px',
        background: `linear-gradient(${isHorizontal ? '90deg' : '180deg'},
          transparent 0%,
          hsl(var(--border)) 20%,
          hsl(var(--border)) 80%,
          transparent 100%
        )`,
        transformOrigin: isHorizontal ? 'left center' : 'center top',
      }}
    />
  );
}
