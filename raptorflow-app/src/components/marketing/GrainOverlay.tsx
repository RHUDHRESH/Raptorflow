'use client';

// ============================================================================
// GRAIN OVERLAY - Subtle film grain texture
// ============================================================================

interface GrainOverlayProps {
  opacity?: number;
  className?: string;
}

export function GrainOverlay({
  opacity = 0.03,
  className = '',
}: GrainOverlayProps) {
  return (
    <div
      className={`pointer-events-none fixed inset-0 z-[9999] ${className}`}
      style={{ opacity }}
      aria-hidden="true"
    >
      <svg className="w-full h-full">
        <filter id="grain-filter">
          <feTurbulence
            type="fractalNoise"
            baseFrequency="0.8"
            numOctaves="4"
            stitchTiles="stitch"
          />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect
          width="100%"
          height="100%"
          filter="url(#grain-filter)"
          opacity="0.5"
        />
      </svg>
    </div>
  );
}

// ============================================================================
// NOISE TEXTURE - CSS-based noise overlay (lighter weight)
// ============================================================================

interface NoiseTextureProps {
  opacity?: number;
  className?: string;
}

export function NoiseTexture({
  opacity = 0.02,
  className = '',
}: NoiseTextureProps) {
  return (
    <div
      className={`pointer-events-none fixed inset-0 z-[9999] ${className}`}
      aria-hidden="true"
      style={{
        opacity,
        backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
        mixBlendMode: 'overlay',
      }}
    />
  );
}

// ============================================================================
// VIGNETTE OVERLAY - Subtle edge darkening
// ============================================================================

interface VignetteProps {
  intensity?: number;
  className?: string;
}

export function Vignette({ intensity = 0.3, className = '' }: VignetteProps) {
  return (
    <div
      className={`pointer-events-none fixed inset-0 z-[9998] ${className}`}
      aria-hidden="true"
      style={{
        background: `radial-gradient(ellipse at center, transparent 0%, transparent 50%, hsl(var(--background) / ${intensity}) 100%)`,
      }}
    />
  );
}

// ============================================================================
// SCANLINES - Retro CRT effect (use sparingly)
// ============================================================================

interface ScanlinesProps {
  opacity?: number;
  className?: string;
}

export function Scanlines({ opacity = 0.02, className = '' }: ScanlinesProps) {
  return (
    <div
      className={`pointer-events-none fixed inset-0 z-[9997] ${className}`}
      aria-hidden="true"
      style={{
        opacity,
        backgroundImage: `repeating-linear-gradient(
          0deg,
          transparent,
          transparent 1px,
          hsl(var(--foreground) / 0.1) 1px,
          hsl(var(--foreground) / 0.1) 2px
        )`,
        backgroundSize: '100% 4px',
      }}
    />
  );
}

// ============================================================================
// GRADIENT MESH - Beautiful mesh gradient background
// ============================================================================

interface GradientMeshProps {
  className?: string;
}

export function GradientMesh({ className = '' }: GradientMeshProps) {
  return (
    <div
      className={`pointer-events-none absolute inset-0 overflow-hidden ${className}`}
      aria-hidden="true"
    >
      {/* Primary gradient blob */}
      <div
        className="absolute -top-1/4 -left-1/4 w-1/2 h-1/2 rounded-full blur-3xl opacity-20"
        style={{
          background:
            'radial-gradient(circle, hsl(var(--foreground) / 0.15) 0%, transparent 70%)',
        }}
      />

      {/* Secondary gradient blob */}
      <div
        className="absolute -bottom-1/4 -right-1/4 w-1/2 h-1/2 rounded-full blur-3xl opacity-15"
        style={{
          background:
            'radial-gradient(circle, hsl(var(--muted-foreground) / 0.2) 0%, transparent 70%)',
        }}
      />

      {/* Accent gradient blob */}
      <div
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-2/3 h-2/3 rounded-full blur-3xl opacity-10"
        style={{
          background:
            'radial-gradient(circle, hsl(var(--accent) / 0.1) 0%, transparent 60%)',
        }}
      />
    </div>
  );
}

// ============================================================================
// SPOTLIGHT - Cursor-following spotlight effect
// ============================================================================

import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';

interface SpotlightProps {
  size?: number;
  intensity?: number;
  className?: string;
}

export function Spotlight({
  size = 400,
  intensity = 0.05,
  className = '',
}: SpotlightProps) {
  const spotlightRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const spotlight = spotlightRef.current;
    if (!spotlight) return;

    const prefersReducedMotion = window.matchMedia(
      '(prefers-reduced-motion: reduce)'
    ).matches;
    if (prefersReducedMotion) {
      spotlight.style.display = 'none';
      return;
    }

    const handleMouseMove = (e: MouseEvent) => {
      gsap.to(spotlight, {
        x: e.clientX - size / 2,
        y: e.clientY - size / 2,
        duration: 0.5,
        ease: 'power2.out',
      });
    };

    window.addEventListener('mousemove', handleMouseMove);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
    };
  }, [size]);

  return (
    <div
      ref={spotlightRef}
      className={`pointer-events-none fixed z-[1] ${className}`}
      aria-hidden="true"
      style={{
        width: size,
        height: size,
        background: `radial-gradient(circle, hsl(var(--foreground) / ${intensity}) 0%, transparent 70%)`,
        borderRadius: '50%',
        mixBlendMode: 'overlay',
        transform: 'translate(-50%, -50%)',
      }}
    />
  );
}
